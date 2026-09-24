---
title: "Layer-7 Routing"
category: "networking"
difficulty: "intermediate"
tags: [proxy, routing, http]
related: [tcp-load-balancer, service-mesh-sidecar, service-discovery, grpc-service]
---

# Layer-7 Routing

A layer-7 router (reverse proxy / ingress) reads the actual HTTP request — host, path, headers — and decides which backend service should handle it. It's the traffic cop in front of every microservice deployment, and building one teaches you how routing, TLS termination, and resilience policies compose in production systems like Envoy and Traefik.

## Core concepts

- **Reverse proxy vs forward proxy** — A forward proxy serves clients reaching outward; a reverse proxy sits in front of servers, presenting one address while fanning out to many backends. L7 routers are reverse proxies that inspect HTTP semantics.
- **Host/path/header routing** — The routing table matches `Host: api.example.com` or path prefixes like `/v2/` (or headers, cookies, query params) to backend pools. Rule order and specificity determine which rule wins on overlap.
- **TLS termination** — The router holds the certificates and decrypts HTTPS, then forwards plain HTTP to backends. This centralizes certificate management and lets backends stay simple.
- **Request rewriting** — Stripping path prefixes, adding `X-Forwarded-For` / `X-Forwarded-Proto`, and injecting trace headers. Done wrong, rewriting causes redirect loops and broken absolute URLs.
- **Retries, timeouts, and circuit breaking** — A router retries idempotent requests on different backends, enforces per-route timeouts so one slow backend can't pile up connections, and trips circuit breakers to stop hammering a failing service.
- **Middleware chains** — Auth, rate limiting, compression, and logging compose as ordered middleware around the routing core — the same pattern every web framework uses.
- **Dynamic configuration** — Real routers watch a service registry or config file and update routes without restarting or dropping connections; your router should reload its table on signal or file watch.

## How it works

Your server accepts client connections and parses each HTTP request. It evaluates the routing rules in order — first matching host, then longest path prefix, then header conditions — to pick a backend pool. It selects one backend (round-robin or least-connections), opens (or reuses) a connection to it, forwards the request with adjusted headers (`X-Forwarded-For`, possibly a rewritten path), then streams the backend's response back to the client. Around this core sit health checks that prune dead backends, retry logic for failed attempts, and middleware for cross-cutting concerns.

## Build milestones

1. Build an HTTP reverse proxy that forwards every request to a single backend and streams the response back untouched.
2. Add a routing table: route by `Host` header and by path prefix to different backends; return 404 for no match.
3. Implement header manipulation (`X-Forwarded-For`, `X-Forwarded-Proto`) and path-prefix stripping/rewriting.
4. Add active health checks, retries with backoff on 5xx/connection errors, and per-route timeouts.
5. Support hot config reload (SIGHUP or file watch) without dropping in-flight connections, plus access logging.

## Best resources

- [Envoy documentation](https://www.envoyproxy.io/docs) — the reference architecture for modern L7 routing: listeners, routes, clusters, retries, and circuit breakers.
- [Traefik documentation](https://doc.traefik.io/traefik/) — routers, middlewares, and providers; the clearest mental model of rule-based routing.
- [NGINX reverse proxy guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) — the classic admin-guide walkthrough of proxying, header passing, and buffering.
- [Caddy documentation](https://caddyserver.com/docs/) — a simpler take on the same ideas, with excellent explanations of reverse-proxy directives.
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110) — Host-based routing, forwarding headers, and intermediary behavior are all specified here.

## Stretch ideas

- Terminate TLS with automatic certificate loading and route gRPC (HTTP/2 with trailers) alongside plain HTTP/1.1.
- Add weighted traffic splitting for canary deploys and a small admin UI showing live route tables and backend health.
