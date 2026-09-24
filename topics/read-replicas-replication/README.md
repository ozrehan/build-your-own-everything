---
title: "Read Replicas and Replication"
category: "databases"
difficulty: "intermediate"
tags: [replication, high-availability, distributed-systems]
related: [write-ahead-log, raft-consensus, sharding-strategy, leader-election]
---

# Read Replicas and Replication

Replication keeps copies of your data on multiple machines so reads scale out and the database survives a server dying. Building it teaches the fundamental distributed-systems tradeoff: how far behind a replica may lag, and what breaks when the primary disappears.

## Core concepts

- **Single-leader replication** — One primary takes all writes; replicas apply the primary's change stream. Simple to reason about, and the default in Postgres, MySQL, and MongoDB.
- **The replication log** — The primary's WAL (or logical change stream) is the transport: replicas replay it in order. Physical replication ships byte-level changes; logical replication ships row-level changes and allows version/schema flexibility.
- **Asynchronous vs. synchronous** — Async replicas may lag (fast, risk of data loss on failover); sync replicas acknowledge before commit returns (durable, slower, availability risk if a replica is down). Semi-sync is the common middle ground.
- **Replication lag** — The delay between a commit on the primary and its visibility on a replica. Monitoring lag is operational core: too much lag means stale reads and painful failovers.
- **Read-your-writes consistency** — A client that writes then reads may hit a lagging replica and not see its own write. Fixes: route post-write reads to the primary, or track a replica's applied position per session.
- **Failover and split-brain** — Promoting a replica requires fencing the old primary (it might just be partitioned, not dead). Without fencing, two primaries accept divergent writes — the classic split-brain.
- **Multi-leader and leaderless** — Writes to any node (multi-leader: MySQL Galera; leaderless: Cassandra/Dynamo with quorum reads/writes). Higher write availability, but conflict resolution becomes the hard problem.

## How it works

The primary writes every change to its WAL and streams log records to each replica over a persistent connection. Replicas replay the records in commit order against their own data files and continuously report how far they've applied (their LSN position). Read queries are load-balanced across replicas; a proxy can enforce read-your-writes by remembering each client's last write LSN and only routing to replicas that have applied past it. When the primary fails, a failover manager picks the most caught-up replica, fences the old primary (STONITH — "shoot the other node in the head" — or a consensus-backed lease), replays any remaining log, and promotes it. Clients reconnect to the new primary and replication re-forms around it.

## Build milestones

1. Build WAL shipping: a primary that streams its write-ahead log over TCP to a follower process that replays it into an identical store; verify byte-identical state.
2. Add async replication with lag metrics (primary LSN vs. replica applied LSN) and a read proxy that spreads queries across replicas.
3. Implement read-your-writes routing: track each client's last write LSN and steer its reads to sufficiently caught-up replicas (or the primary).
4. Add semi-synchronous replication (commit waits for one replica ack) and measure the latency/durability tradeoff vs. pure async under a kill-the-primary test.
5. Implement automatic failover: health checks, fencing of the old primary, election of the most caught-up replica, and client redirection — then chaos-test it.

## Best resources

- [PostgreSQL: High Availability, Load Balancing, and Replication](https://www.postgresql.org/docs/current/warm-standby.html) — streaming replication, slots, and failover in the official docs.
- [MySQL: Replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html) — the other canonical implementation: binary log, GTIDs, and group replication.
- [Database replication (Wikipedia)](https://en.wikipedia.org/wiki/Database_replication) — models (single/multi-leader, leaderless), consistency, and conflict handling.
- [Designing Data-Intensive Applications — Martin Kleppmann](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) — chapters 5–7 are the definitive treatment of replication, lag, and failover.
- [The dangers of replication and a solution (Gray et al., SIGMOD 1996)](http://www.redbook.io/) — the classic paper on why async multi-master replication is dangerous; in the Red Book's replication chapter.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — replication and consensus chapters with implementation-level detail.

## Stretch ideas

- Implement logical (row-based) replication with schema mapping so replicas can run a different engine version.
- Add cascading replication (replicas of replicas) and measure lag amplification down the chain.
- Build conflict detection for multi-leader writes using vector clocks or last-writer-wins with per-field resolution.
