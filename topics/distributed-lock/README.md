---
title: "Distributed Lock"
category: "distributed-data"
difficulty: "intermediate"
tags: [distributed-systems, coordination, redis]
related: [leader-election, raft-consensus, distributed-tracer]
---

# Distributed Lock

When three servers all think they're the one allowed to run the nightly billing job, you need a lock that lives outside any single machine. Building a distributed lock teaches you the uncomfortable truth of distributed systems: a lock is only as good as your assumptions about clocks, pauses, and network delays.

## Core concepts

- **Mutual exclusion** — The lock's one job: at most one holder at a time. Everything else — TTLs, fencing, consensus — exists because this simple property is surprisingly hard to guarantee across machines.
- **Lease with TTL** — The standard trick: acquiring a lock sets a key with an expiry, so a crashed holder's lock eventually releases itself. The TTL must be long enough for the work but short enough that a crash doesn't stall the system for ages.
- **SET NX** — Redis's `SET key value NX EX ttl` (set only if not exists, with expiry) is the atomic primitive most distributed locks are built on: one command that both checks and acquires, so no race exists between the two steps.
- **Fencing tokens** — A monotonically increasing number handed to each lock holder, which the holder must present to the storage system with every write; storage rejects writes from stale tokens. This is the only real fix for a paused process that wakes up after its lease expired.
- **The GC-pause hazard** — A process can be frozen for seconds (garbage collection, VM suspension) between acquiring a lock and acting on it. By the time it wakes, its lease has expired and someone else holds the lock — now two processes believe they are the exclusive holder.
- **Redlock** — Redis's multi-node algorithm: acquire the lock on a majority of independent Redis instances and subtract acquisition time from the TTL. Controversial because it is heavier than single-node locking but still vulnerable to the clock/pausing problems it was meant to solve.
- **Consensus-based locks** — ZooKeeper/Curator and etcd implement locks on top of consensus (Zab/Raft), giving real safety guarantees at the cost of a heavier coordination service. When correctness truly depends on the lock, this is the recommended path.

## How it works

The client generates a unique token and sends `SET lock-name token NX EX 30` to Redis. If the key didn't exist, the client holds the lock for 30 seconds and must finish its work — and release the lock with a Lua script that deletes the key only if the stored token still matches its own (so it never deletes someone else's lock). A background thread can extend the TTL while work continues. For the fencing-token variant, a separate counter increments on every acquisition; the client includes the token with each write to the protected resource, and the resource's storage layer rejects any write whose token is older than the latest one it has seen — so even a zombie holder with an expired lease cannot corrupt data.

## Build milestones

1. Build the basic lock: a client that acquires with `SET NX EX`, does fake work, and releases with an atomic check-and-delete Lua script against a single Redis.
2. Demonstrate the failure mode: simulate a long GC pause (sleep past the TTL while holding the lock) and show two clients both believing they hold it — then add fencing tokens and show the stale write being rejected.
3. Add lock renewal: a watchdog thread that extends the TTL while the holder is alive, and verify a killed holder's lock expires on time.
4. Implement Redlock across 3–5 Redis instances: acquire on a majority, measure the effective TTL, and handle the case where some instances are down.
5. Impressive end state: build a tiny leader-guarded job runner — N workers compete for a lock, exactly one runs the "billing job" writing fenced records to a log, and you can kill -STOP a worker mid-run to prove no duplicate billing occurs.

## Best resources

- [How to do distributed locking — Martin Kleppmann](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — The essential critique: why TTL locks fail under process pauses and why fencing tokens are the real answer. Read this before trusting any lock.
- [Apache Curator](https://curator.apache.org/) — ZooKeeper-based recipes including inter-process locks built on consensus; the correct tool when the lock protects correctness.
- [Redis](https://redis.io/) — The `SET NX EX` pattern and Lua-scripted release live here; the official docs cover the distributed lock pattern and its caveats.
- [Raft](https://raft.github.io/) — Understanding consensus explains why ZooKeeper/etcd locks are safe in a way Redis locks are not.

## Stretch ideas

- Model your lock in TLA+ and check whether mutual exclusion holds when you inject arbitrary process pauses.
- Build a lock-service comparison harness: measure acquisition latency and behavior under partitions for single-Redis, Redlock, and a consensus-based lock.
