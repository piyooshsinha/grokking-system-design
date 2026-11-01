# Seatline — the reference application

Seatline is a small ticket reservation app that makes the design decisions in
Systems Workbench concrete. A reader can search events, reserve a limited number
of seats, check out, and watch an asynchronous confirmation arrive. The
**Replay delivery** action deliberately delivers the same event twice so the
consumer's deduplication behavior is visible.

This is a teaching system, not a production ticketing service. Payment is
simulated. The first version uses one Python process and SQLite so the complete
request path is easy to follow; its limits are called out below rather than
hidden behind a stack of services.

## Run it

With Python 3.10 or newer:

```bash
cd examples/seatline
python3 app.py
```

Open `http://127.0.0.1:8090`. The demo database is created at
`examples/seatline/data/seatline.sqlite3` and is seeded on its first run. Remove
that file to reset the sample data. Change the hold duration with
`SEATLINE_HOLD_SECONDS`.

Or run the same app in Docker from this directory:

```bash
docker compose up --build
```

The Compose setup stores SQLite data in a named volume and publishes port 8090.
Open `http://127.0.0.1:8090` after the container starts.

On the Intel NUC, Seatline runs from this repository and shares the Workbench
domain. Caddy serves it at
`https://study.192-168-1-22.sslip.io/seatline/`; the Workbench stays at the
root URL. Start it from the repository root with:

```bash
docker compose -f examples/seatline/compose.nuc.yml up -d --build
```

Add the path route to the existing Workbench site block in the Caddyfile.
`handle_path` removes `/seatline` before forwarding, and Seatline prefixes its
API calls so they stay under the same URL:

```caddyfile
https://study.192-168-1-22.sslip.io {
    tls internal
    @seatlineRoot path /seatline
    redir @seatlineRoot /seatline/ 308
    handle_path /seatline/* {
        reverse_proxy seatline:8090
    }
    handle {
        reverse_proxy systems-workbench:8000
    }
}
```

The NUC's Caddy admin API is disabled, so restart its `reverse-proxy` container
after changing the Caddyfile. Both apps now use the same Workbench hostname and
TLS certificate. Devices that do not trust the homelab CA can install it from
`http://pakhi.local/ca.crt`.

## Follow the request

For a staged learning path with code links, runnable experiments, and slow or unavailable dependency scenarios, open the [Seatline end-to-end walkthrough](../../guides/seatline-end-to-end.md).


```mermaid
sequenceDiagram
    actor Buyer
    participant API as Seatline API
    participant DB as SQLite transaction
    participant Outbox as Outbox worker
    Buyer->>API: Search events
    API->>DB: Read catalog (short cache)
    Buyer->>API: Hold seats + idempotency key
    API->>DB: BEGIN IMMEDIATE; check available capacity
    DB-->>API: Hold expires in five minutes
    Buyer->>API: Checkout + idempotency key
    API->>DB: Confirm order and insert outbox event
    Outbox->>DB: Deliver event; dedupe by order ID
    DB-->>Buyer: Order shows notification delivered
```

| Study idea | Where to see it in code | What to try |
|---|---|---|
| Capacity invariant and contention | `app.py:create_hold`, `run_race_lab`, `BEGIN IMMEDIATE` · [transactions and databases](../../fundamentals/databases.md) | Run “Race for the last seat”. The isolated event is removed after the two simultaneous attempts finish. |
| Leases and expiration | `holds.expires_at`, `outbox_worker` · [idempotency and retries](../../patterns/idempotency.md) | Set `SEATLINE_HOLD_SECONDS=15`, hold seats, then wait for them to return. |
| Idempotency | `holds.request_key`, `orders.request_key`, `checkout` · [idempotency](../../patterns/idempotency.md) | Confirm a reservation; the UI retries checkout using the same key and shows that both responses identify one order. |
| Transactional outbox | `checkout`, `outbox` table · [outbox pattern](../../patterns/outbox-pattern.md) | Confirm an order and observe that its notification is delivered asynchronously. |
| At-least-once delivery and deduplication | `replay_notification`, `outbox_worker`, unique notification `order_id` · [message queues](../../patterns/message-queues.md) | Replay a notification; the delivery is processed but no duplicate notification is created. |
| Caching and search | `list_events`, three-second in-process cache · [caching](../../patterns/caching.md) | Search the catalog, then reserve a seat and see the cached inventory invalidate. |
| Indexes and query shape | `holds_inventory_idx`, `orders_created_idx` · [database design](../../fundamentals/databases.md) | Inspect the SQL used to compute available seats and list recent orders. |
| Request tracing and health | `Handler`, request trace panel, `/api/health`, `X-Request-ID` · [metrics and monitoring](../../questions/design-metrics-monitoring.md) | Follow a request ID from the UI into the server logs. |

The app's request-flow strip highlights each stage. Lesson links jump to the
corresponding system-design pages in the study app. The guided failure lab
makes two behaviors repeatable: it races two buyers against one disposable
seat, and checkout retries the same request key to show the original order
being returned. The request trace lists recent HTTP calls with their status and
request ID. Replaying a delivery from Recent orders exercises the outbox
consumer's deduplication.

## Start with SCOPE

Before reading the implementation, use the [SCOPE method](../../guides/scope-method.md)
on this promise: **a confirmed ticket must have exactly one buyer, even when
requests retry or arrive at the same time.** Start with one event's remaining
capacity, draw the hold and checkout writes, then probe a lost response, a
crashed worker, and an unavailable replica. The code demonstrates the first
two in a single-process baseline; the later steps are evolution exercises.

## Evolving the design

The single-process baseline keeps the end-to-end behavior readable. Future
chapters can replace one boundary at a time and preserve the same user flow:

1. Replace SQLite with PostgreSQL and compare row locks, conditional updates,
   and isolation levels under concurrent holds.
2. Replace the in-process catalog cache with Redis; add cache-aside, TTL,
   invalidation, and stale-read exercises.
3. Move the outbox worker to a durable broker and demonstrate consumer groups,
   retries, dead-letter handling, and backpressure.
4. Add a read model and live order updates, then compare polling, SSE, and
   WebSockets.
5. Introduce multiple inventory partitions and replicas to explore hot keys,
   sharding, quorum choices, regional failure, and reconciliation.

This progression keeps the example coherent: the same event purchase gives the
reader a concrete way to compare each design, while the code only claims the
guarantees it actually implements. There is no real payment provider, account
system, distributed cache, external message broker, or cross-region deployment
in this first slice.
