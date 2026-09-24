---
title: "Connection Pooler"
category: "databases"
difficulty: "intermediate"
tags: [postgres, proxy, performance]
related: [redis-like-cache, rate-limiter, tcp-load-balancer, message-queue]
---

# Connection Pooler

A connection pooler (PgBouncer, Pgpool) sits between your app and the database, multiplexing thousands of cheap client connections onto a handful of real database connections. Building one teaches proxy protocol mechanics, why Postgres connections are expensive, and the session-vs-transaction pooling tradeoff.

## Core concepts

- **Why connections are expensive** — A Postgres backend is a full OS process (~5–10 MB+ each); at thousands of connections the database spends its time context-switching instead of querying. The pooler exists because the cost is per-connection, not per-query.
- **Postgres wire protocol** — Startup handshake, authentication (MD5/SCRAM), simple vs. extended query protocol, Parse/Bind/Execute messages. A pooler must speak this fluently in both directions.
- **Session vs. transaction vs. statement pooling** — Session: one server connection per client for its whole life (safe, little benefit). Transaction: reassign the server connection after each transaction (the sweet spot; breaks session state). Statement: per query (breaks multi-statement transactions entirely).
- **Session state hazards** — `SET` options, prepared statements, advisory locks, temp tables, `LISTEN/NOTIFY` all assume a stable connection. Transaction pooling must reset or forbid them — this is where poolers earn their complexity.
- **Multiplexing** — Many idle clients share few server connections; a client only holds a server connection while its transaction runs. 10,000 app connections → 100 database connections is a typical ratio.
- **Health checks and failover** — The pooler tracks which backends are alive, drains connections to a failing primary, and can reroute to a standby — making it the natural place for failover logic.
- **Prepared statement handling** — Named prepared statements are per-connection state, which conflicts with transaction pooling. Solutions: rewrite to unnamed statements, or pin clients to connections.

## How it works

Clients connect to the pooler as if it were Postgres: it performs the startup/auth handshake itself (validating against its own user list or passing through). When a client begins a transaction (or sends a query, in statement mode), the pooler checks out an idle server connection from the pool — or queues the client if the pool is exhausted — and proxies bytes between the two sockets. On `COMMIT`/`ROLLBACK` the server connection is reset (issuing `DISCARD ALL` or the equivalent to clear session state) and returned to the idle pool for the next client. A background janitor reaps stale connections, runs health checks against each backend, and maintains per-database/per-user pool limits. Because it never parses SQL deeply, the pooler stays fast: it's a smart byte-pipe with connection lifecycle management.

## Build milestones

1. Build a dumb TCP proxy for Postgres: accept client connections, open one server connection each, and blindly forward bytes both ways; verify `psql` works through it.
2. Implement the startup and auth handshake yourself (parse StartupMessage, handle SCRAM or trust auth) so the pooler terminates client connections.
3. Add session pooling: a fixed pool of server connections handed out per client session, with queuing when exhausted and per-user/database limits.
4. Upgrade to transaction pooling: detect transaction boundaries, return connections to the pool on commit/rollback, and reset session state (`DISCARD ALL`); document what breaks (prepared statements, advisory locks).
5. Add backend health checks, graceful drain on config reload, and metrics (wait queue depth, checkout latency); load-test 1,000 idle clients against 20 server connections.

## Best resources

- [PgBouncer](https://www.pgbouncer.org/) — the reference implementation; its docs on pooling modes are the definitive guide to the tradeoffs.
- [PgBouncer source](https://github.com/pgbouncer/pgbouncer) — compact, readable C; the way it manages connection state machines is the curriculum.
- [PostgreSQL: Connection settings](https://www.postgresql.org/docs/current/runtime-config-connection.html) — `max_connections` and friends: why the database can't just accept more connections itself.
- [ProxySQL](https://www.proxysql.com/) — the MySQL-side equivalent; its query-routing rules show what a pooler can grow into.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — the process model and protocol chapters explain exactly what a backend connection costs.
- [Designing Data-Intensive Applications — Martin Kleppmann](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) — the chapters on partitioning and replication cover the proxy layer's role.

## Stretch ideas

- Add read/write splitting: route `SELECT`s to replicas and writes to the primary by sniffing the extended-protocol messages.
- Implement query-level caching in the pooler for a narrow class of safe queries, with invalidation hooks.
- Add SCRAM authentication passthrough without ever seeing the plaintext password.
