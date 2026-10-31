#!/usr/bin/env python3
"""Seatline: a small, runnable ticket reservation reference application."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("SEATLINE_DB", APP_DIR / "data" / "seatline.sqlite3"))
HOST = os.environ.get("SEATLINE_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8090"))
HOLD_SECONDS = int(os.environ.get("SEATLINE_HOLD_SECONDS", "300"))
MAX_BODY = 16_384
CACHE_SECONDS = 3
_cache_lock = threading.Lock()
_event_cache: tuple[float, list[dict]] | None = None


class Problem(Exception):
    def __init__(self, status: int, message: str):
        self.status, self.message = status, message


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def now() -> int:
    return int(time.time())


def init_db() -> None:
    db = connect()
    try:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, venue TEXT NOT NULL,
                city TEXT NOT NULL, starts_at TEXT NOT NULL, capacity INTEGER NOT NULL,
                sold INTEGER NOT NULL DEFAULT 0, price_cents INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS holds (
                id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES events(id),
                quantity INTEGER NOT NULL, status TEXT NOT NULL,
                expires_at INTEGER NOT NULL, request_key TEXT NOT NULL UNIQUE,
                created_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS holds_inventory_idx ON holds(event_id,status,expires_at);
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY, hold_id TEXT NOT NULL UNIQUE REFERENCES holds(id),
                event_id TEXT NOT NULL REFERENCES events(id), quantity INTEGER NOT NULL,
                total_cents INTEGER NOT NULL, status TEXT NOT NULL,
                request_key TEXT NOT NULL UNIQUE, created_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS orders_created_idx ON orders(created_at DESC);
            CREATE TABLE IF NOT EXISTS outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL, payload TEXT NOT NULL,
                created_at INTEGER NOT NULL, processed_at INTEGER
            );
            CREATE INDEX IF NOT EXISTS outbox_pending_idx ON outbox(processed_at,id);
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL UNIQUE,
                message TEXT NOT NULL, created_at INTEGER NOT NULL
            );
        """)
        if db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
            samples = [
                ("evt-summit", "Distributed Systems Summit", "Jio World Convention Centre", "Mumbai", "09:30", 48, 41, 8900),
                ("evt-design", "Designing Reliable Products", "NESCO Centre", "Mumbai", "13:00", 36, 23, 5900),
                ("evt-night", "The Queue Is the Dancefloor", "antiSOCIAL", "Mumbai", "20:00", 60, 52, 2400),
            ]
            date = (datetime.now(timezone.utc).date() + timedelta(days=14)).isoformat()
            db.executemany("INSERT INTO events VALUES (?,?,?,?,?,?,?,?)", [
                (i, title, venue, city, f"{date}T{clock}:00Z", capacity, sold, price)
                for i, title, venue, city, clock, capacity, sold, price in samples
            ])
    finally:
        db.close()


def invalidate_events() -> None:
    global _event_cache
    with _cache_lock:
        _event_cache = None


def list_events(query: str = "") -> list[dict]:
    global _event_cache
    q = query.strip().lower()
    with _cache_lock:
        if not q and _event_cache and _event_cache[0] > time.monotonic():
            return _event_cache[1]
    db = connect()
    try:
        rows = db.execute("""
            SELECT e.*, COALESCE(SUM(CASE WHEN h.status='active' AND h.expires_at>? THEN h.quantity ELSE 0 END),0) AS held
            FROM events e LEFT JOIN holds h ON h.event_id=e.id
            WHERE (?='' OR lower(e.title || ' ' || e.venue || ' ' || e.city) LIKE ?)
            GROUP BY e.id ORDER BY e.starts_at
        """, (now(), q, f"%{q}%")).fetchall()
    finally:
        db.close()
    result = [{
        "id": r["id"], "title": r["title"], "venue": r["venue"], "city": r["city"],
        "starts_at": r["starts_at"], "capacity": r["capacity"], "sold": r["sold"],
        "held": r["held"], "remaining": max(0, r["capacity"] - r["sold"] - r["held"]),
        "price_cents": r["price_cents"],
    } for r in rows]
    if not q:
        with _cache_lock:
            _event_cache = (time.monotonic() + CACHE_SECONDS, result)
    return result


def list_orders() -> list[dict]:
    db = connect()
    try:
        rows = db.execute("""
            SELECT o.*, e.title, n.created_at AS notified_at
            FROM orders o JOIN events e ON e.id=o.event_id
            LEFT JOIN notifications n ON n.order_id=o.id
            ORDER BY o.created_at DESC LIMIT 30
        """).fetchall()
        return [{k: r[k] for k in r.keys()} for r in rows]
    finally:
        db.close()


def create_hold(event_id: str, quantity: int, request_key: str) -> dict:
    if not request_key or len(request_key) > 120:
        raise Problem(400, "An idempotency key is required.")
    if not 1 <= quantity <= 8:
        raise Problem(400, "Choose between 1 and 8 tickets per reservation.")
    db = connect()
    try:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT * FROM holds WHERE request_key=?", (request_key,)).fetchone()
        if previous:
            db.commit()
            return dict(previous)
        event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        if not event:
            raise Problem(404, "That event could not be found.")
        timestamp = now()
        held = db.execute("SELECT COALESCE(SUM(quantity),0) FROM holds WHERE event_id=? AND status='active' AND expires_at>?", (event_id, timestamp)).fetchone()[0]
        remaining = event["capacity"] - event["sold"] - held
        if quantity > remaining:
            raise Problem(409, f"Only {max(0, remaining)} ticket(s) remain. No seats were reserved.")
        hold_id, expires = "hld_" + uuid.uuid4().hex[:12], timestamp + HOLD_SECONDS
        db.execute("INSERT INTO holds VALUES (?,?,?,?,?,?,?)", (hold_id, event_id, quantity, "active", expires, request_key, timestamp))
        db.commit()
        invalidate_events()
        return {"id": hold_id, "event_id": event_id, "quantity": quantity, "status": "active", "expires_at": expires}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def checkout(hold_id: str, request_key: str) -> dict:
    if not request_key or len(request_key) > 120:
        raise Problem(400, "An idempotency key is required.")
    db = connect()
    try:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT * FROM orders WHERE request_key=?", (request_key,)).fetchone()
        if previous:
            db.commit()
            return dict(previous)
        hold = db.execute("SELECT * FROM holds WHERE id=?", (hold_id,)).fetchone()
        if not hold:
            raise Problem(404, "Reservation not found.")
        if hold["status"] != "active" or hold["expires_at"] <= now():
            raise Problem(409, "This reservation expired or was already checked out. Please choose seats again.")
        event = db.execute("SELECT * FROM events WHERE id=?", (hold["event_id"],)).fetchone()
        timestamp, order_id = now(), "ord_" + uuid.uuid4().hex[:12]
        total = hold["quantity"] * event["price_cents"]
        db.execute("UPDATE holds SET status='checked_out' WHERE id=? AND status='active'", (hold_id,))
        db.execute("UPDATE events SET sold=sold+? WHERE id=?", (hold["quantity"], event["id"]))
        db.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?)", (order_id, hold_id, event["id"], hold["quantity"], total, "confirmed", request_key, timestamp))
        payload = json.dumps({"order_id": order_id, "event_id": event["id"], "quantity": hold["quantity"]})
        db.execute("INSERT INTO outbox(event_type,aggregate_id,payload,created_at) VALUES(?,?,?,?)", ("order.confirmed", order_id, payload, timestamp))
        db.commit()
        invalidate_events()
        return {"id": order_id, "hold_id": hold_id, "event_id": event["id"], "quantity": hold["quantity"], "total_cents": total, "status": "confirmed", "request_key": request_key, "created_at": timestamp}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def replay_notification(order_id: str) -> None:
    db = connect()
    try:
        order = db.execute("SELECT id,event_id,quantity FROM orders WHERE id=?", (order_id,)).fetchone()
        if not order:
            raise Problem(404, "Order not found.")
        payload = json.dumps({"order_id": order_id, "event_id": order["event_id"], "quantity": order["quantity"]})
        db.execute("INSERT INTO outbox(event_type,aggregate_id,payload,created_at) VALUES(?,?,?,?)", ("order.confirmed", order_id, payload, now()))
    finally:
        db.close()


def run_race_lab() -> dict:
    """Run two simultaneous holds against one disposable seat and clean up."""
    event_id = "lab_" + uuid.uuid4().hex[:12]
    request_keys = ["lab_" + uuid.uuid4().hex for _ in range(2)]
    db = connect()
    try:
        starts = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        db.execute("INSERT INTO events(id,title,venue,city,starts_at,capacity,sold,price_cents) VALUES(?,?,?,?,?,?,?,?)",
                   (event_id, "Concurrency lab · disposable seat", "Isolated test venue", "Lab", starts, 1, 0, 100))
    finally:
        db.close()

    gate = threading.Barrier(2)
    def attempt(request_key: str) -> dict:
        request_id = uuid.uuid4().hex[:12]
        gate.wait()
        try:
            hold = create_hold(event_id, 1, request_key)
            result = {"status": 201, "outcome": "seat held", "hold_id": hold["id"], "request_id": request_id}
        except Problem as exc:
            result = {"status": exc.status, "outcome": exc.message, "request_id": request_id}
        print(json.dumps({"level": "info", "component": "concurrency-lab", **result}), flush=True)
        return result

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            attempts = list(pool.map(attempt, request_keys))
        return {"attempts": attempts, "event_id": event_id}
    finally:
        # The event is private to this run. Remove only its test holds and event.
        db = connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM holds WHERE event_id=?", (event_id,))
            db.execute("DELETE FROM events WHERE id=?", (event_id,))
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        invalidate_events()


def outbox_worker() -> None:
    """At-least-once delivery; notification order_id is the idempotency key."""
    while True:
        db = connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            timestamp = now()
            db.execute("UPDATE holds SET status='expired' WHERE status='active' AND expires_at<=?", (timestamp,))
            pending = db.execute("SELECT * FROM outbox WHERE processed_at IS NULL ORDER BY id LIMIT 20").fetchall()
            for item in pending:
                payload = json.loads(item["payload"])
                db.execute("INSERT OR IGNORE INTO notifications(order_id,message,created_at) VALUES(?,?,?)", (
                    payload["order_id"], f"Your order for {payload['quantity']} ticket(s) is confirmed.", timestamp))
                db.execute("UPDATE outbox SET processed_at=? WHERE id=?", (timestamp, item["id"]))
            db.commit()
            if pending:
                invalidate_events()
        except Exception as exc:
            db.rollback()
            print(json.dumps({"level": "error", "component": "outbox-worker", "error": str(exc)}), flush=True)
        finally:
            db.close()
        time.sleep(1)


class Handler(BaseHTTPRequestHandler):
    server_version = "Seatline/0.1"

    def send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Request-ID", self.request_id)
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise Problem(400, "Invalid request size.")
        if size < 1 or size > MAX_BODY:
            raise Problem(413, "Request body is empty or too large.")
        try:
            value = json.loads(self.rfile.read(size))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise Problem(400, "Send a valid JSON request.")
        if not isinstance(value, dict):
            raise Problem(400, "Send a JSON object.")
        return value

    def do_GET(self) -> None:  # noqa: N802
        self.request_id = self.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = (APP_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/api/events":
            query = parse_qs(parsed.query).get("q", [""])[0][:100]
            self.send_json(200, {"events": list_events(query), "cached_for_seconds": CACHE_SECONDS if not query else 0})
        elif parsed.path == "/api/orders":
            self.send_json(200, {"orders": list_orders()})
        elif parsed.path == "/api/health":
            db = connect()
            try: db.execute("SELECT 1").fetchone()
            finally: db.close()
            self.send_json(200, {"ok": True, "service": "seatline", "request_id": self.request_id})
        else:
            self.send_json(404, {"error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802
        self.request_id = self.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        try:
            data = self.read_json()
            if self.path == "/api/holds":
                hold = create_hold(str(data.get("event_id", "")), int(data.get("quantity", 0)), str(data.get("idempotency_key", "")))
                self.send_json(201, {"hold": hold, "request_id": self.request_id})
            elif self.path == "/api/checkout":
                order = checkout(str(data.get("hold_id", "")), str(data.get("idempotency_key", "")))
                self.send_json(201, {"order": order, "request_id": self.request_id})
            elif self.path == "/api/labs/race":
                self.send_json(200, {"scenario": "last-seat-race", **run_race_lab(), "request_id": self.request_id})
            elif self.path.startswith("/api/orders/") and self.path.endswith("/replay"):
                order_id = self.path.removeprefix("/api/orders/").removesuffix("/replay").strip("/")
                replay_notification(order_id)
                self.send_json(202, {"queued": True, "message": "A duplicate delivery was queued; the consumer deduplicates by order ID."})
            else:
                self.send_json(404, {"error": "Not found."})
        except Problem as exc:
            self.send_json(exc.status, {"error": exc.message, "request_id": self.request_id})
        except (ValueError, TypeError):
            self.send_json(400, {"error": "Invalid field value.", "request_id": self.request_id})
        except sqlite3.IntegrityError:
            self.send_json(409, {"error": "That idempotency key conflicts with an existing operation.", "request_id": self.request_id})

    def log_message(self, fmt: str, *args: object) -> None:
        print(json.dumps({"level": "info", "component": "http", "client": self.client_address[0],
                          "request_id": getattr(self, "request_id", ""), "message": fmt % args}), flush=True)


def main() -> None:
    init_db()
    threading.Thread(target=outbox_worker, name="outbox-worker", daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.daemon_threads = True
    print(json.dumps({"level": "info", "message": "Seatline listening", "host": HOST, "port": PORT, "database": str(DB_PATH)}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
