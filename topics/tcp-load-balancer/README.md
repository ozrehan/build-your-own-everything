---
title: "TCP Load Balancer"
category: "networking"
difficulty: "intermediate"
tags: [load-balancing, tcp, proxy]
related: [layer7-routing, service-discovery, rate-limiter, status-page]
---

# TCP Load Balancer

A TCP (layer-4) load balancer accepts client connections and spreads them across backend servers without understanding the application protocol — it's how HAProxy and cloud LBs handle millions of connections. Building one teaches you connection proxying, scheduling algorithms, and what "high availability" actually costs in code.

## Core concepts

- **L4 vs L7 balancing** — L4 balancers route on IP/port only and never parse application data, so they work for any TCP protocol with minimal overhead; L7 balancers parse HTTP and can route on URLs but cost more per connection.
- **Round-robin** — Connections go to backends in rotation. Dead simple and fair when connections are uniform, but blind to backend load or connection duration.
- **Least-connections** — Each new connection goes to the backend with the fewest active connections. Adapts to uneven load but needs accurate per-backend counters.
- **IP hash / consistent hashing** — Hash the client IP to pick a backend so the same client sticks to the same server. Minimizes reshuffling when backends come and go, at the cost of potentially uneven distribution.
- **Active health checks** — The balancer periodically dials each backend (or hits a health endpoint); failures remove the backend from rotation until it recovers. Without this, one dead server black-holes its share of traffic.
- **Connection draining** — When a backend is removed, existing connections finish naturally while no new ones are assigned — the difference between graceful deploys and dropped requests.
- **The C10K problem** — Handling ten thousand concurrent connections forced the shift from thread-per-connection to event-driven I/O; your balancer's architecture (epoll/async) is the answer to it.

## How it works

The balancer listens on a public port. For each accepted client connection it runs the scheduling algorithm to pick a healthy backend, opens a TCP connection to that backend, then splices the two sockets together — bytes flow client→backend and backend→client until either side closes, at which point both are torn down and counters updated. A background loop health-checks backends and maintains the pool; stats (connections per backend, failures) are exposed for observability.

## Build milestones

1. Build a TCP proxy: accept a client, dial one backend, and shuttle bytes both ways until close.
2. Add a backend pool with pluggable algorithms: round-robin, least-connections, and IP-hash.
3. Implement active health checks — remove dead backends from rotation and re-add them on recovery — plus passive failure detection on dial errors.
4. Add graceful connection draining, per-backend stats, and a small status endpoint showing pool health.
5. Handle the thundering-herd basics: connection limits per backend and staggered health-check intervals.

## Best resources

- [HAProxy](https://www.haproxy.org/) — the reference open-source TCP/HTTP load balancer; study its configuration model and balancing algorithms.
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) — sockets, `select`/`poll`, and the I/O fundamentals your proxy loop is built on.
- [The C10K Problem](http://www.kegel.com/c10k.html) — Dan Kegel's classic essay on why event-driven servers exist; required context for balancer design.
- [Envoy documentation](https://www.envoyproxy.io/docs) — the clearest modern treatment of load-balancing algorithms, health checking, and outlier detection.

## Stretch ideas

- Implement the PROXY protocol so backends can see the real client IP, or do TLS passthrough routed on SNI without decrypting.
- Add Maglev-style consistent hashing and measure how little traffic moves when you add or remove a backend.
