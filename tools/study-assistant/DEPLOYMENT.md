# Deploy on the Intel NUC

The NUC deployment runs the study app as a Docker container. Caddy serves it at
`https://study.192-168-1-22.sslip.io` using the existing homelab certificate
authority. The app joins Caddy's Docker network and the existing private Ollama
network; Ollama is not published to the LAN.

## Start or update

From the repository root on the NUC:

```bash
docker compose -f compose.deploy.yml up -d --build
```

The `workbench-index` volume keeps the generated retrieval index across app
rebuilds. After changing Markdown content, regenerate it inside the running
container:

```bash
docker compose -f compose.deploy.yml exec systems-workbench \
  python3 tools/study-assistant/study_assistant.py build
```

The deployment uses `nomic-embed-text` for semantic retrieval and
`qwen2.5:3b` for answers. Pull either model in the existing `shelf-ollama`
container if it is missing:

```bash
docker exec shelf-ollama ollama pull nomic-embed-text
docker exec shelf-ollama ollama pull qwen2.5:3b
```

Seatline is part of this same repository and runs as a companion container. It
is available at `https://study.192-168-1-22.sslip.io/seatline/`; it does not
need a separate hostname or certificate. Start it from the repository root:

```bash
docker compose -f examples/seatline/compose.nuc.yml up -d --build
```

## Caddy route

The existing Caddy container must share the `reverse-proxy_default` network.
Its Caddyfile needs this site block:

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

The NUC's Caddy has its admin API disabled, so restart `reverse-proxy` after
changing the Caddyfile. Devices that do not trust the homelab CA can install it
from `http://pakhi.local/ca.crt`.
