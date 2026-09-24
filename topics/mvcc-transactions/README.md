---
title: "MVCC Transactions"
category: "databases"
difficulty: "advanced"
tags: [concurrency, transactions, isolation]
related: [write-ahead-log, crash-recovery-aries, distributed-lock, event-sourcing-bank]
---

# MVCC Transactions

MVCC (Multi-Version Concurrency Control) is how Postgres and friends let readers never block writers: instead of locking rows, every update creates a new *version* of the row, and each transaction sees a consistent snapshot of versions. Building it teaches the deepest idea in transaction processing — that isolation can come from versioning, not locking.

## Core concepts

- **Row versions, not in-place updates** — An `UPDATE` inserts a new version of the row and marks the old one as superseded; a `DELETE` marks the latest version dead. Readers pick the version visible to them; writers never block readers.
- **Transaction IDs and snapshots** — Each transaction gets an ID and a snapshot: the set of transactions committed before it started. A row version is visible if its creator committed before your snapshot and no later version did.
- **Visibility rules** — The precise predicate (creator committed, not deleted, or deleted by a transaction invisible to you) is the heart of MVCC. Getting it exactly right — including your own transaction's writes — is the main implementation challenge.
- **Isolation levels** — Read Committed (fresh snapshot per statement), Repeatable Read / Snapshot Isolation (one snapshot per transaction), Serializable (snapshot isolation plus predicate-locking or SSI conflict detection to kill anomalies).
- **Write-write conflicts** — Two concurrent transactions updating the same row: the second must wait or abort (first-committer-wins). MVCC removes read-write blocking but not write-write conflicts.
- **Vacuuming / garbage collection** — Dead row versions pile up and must be reclaimed once no active snapshot can see them. Postgres's `VACUUM`, or any MVCC GC, is a whole subsystem of its own.
- **Write skew and SSI** — Snapshot isolation still permits anomalies like write skew (two transactions each read a constraint the other then breaks). Serializable Snapshot Isolation detects dangerous read-write patterns and aborts one party.

## How it works

Every row version carries `xmin` (creating transaction) and `xmax` (deleting/superseding transaction). A transaction takes a snapshot at start: its own id plus the list of concurrently active transactions. To read, it scans versions newest-to-oldest and picks the first whose `xmin` committed before the snapshot began and whose `xmax` is either empty or belongs to a transaction not visible in the snapshot. Writes create new versions stamped with the writer's id and check for concurrent writers on the same row (first-committer-wins). On commit the transaction's id is marked committed in a shared status array, instantly making its versions visible to new snapshots. A background vacuum pass frees versions invisible to every active snapshot.

## Build milestones

1. Build a single-threaded versioned key/value store: `put` creates a new version chained to the old, `get` returns the latest committed version.
2. Add transaction ids, begin/commit/abort, and snapshot reads: each transaction sees versions committed before it started, plus its own writes.
3. Implement Read Committed (per-statement snapshots) and Repeatable Read (per-transaction snapshots); write tests showing a non-repeatable read in the former but not the latter.
4. Add write-write conflict detection (abort or block the second writer of the same key) and a vacuum pass that reclaims versions invisible to all active snapshots.
5. Implement Serializable via SSI-style dangerous-structure detection, with a classic write-skew test (e.g., two doctors both going off-call while the "at least one on call" invariant breaks) that aborts under Serializable but not under Snapshot Isolation.

## Best resources

- [PostgreSQL: Concurrency Control (MVCC intro)](https://www.postgresql.org/docs/current/mvcc-intro.html) — the official, precise description of snapshots, visibility, and row versions.
- [Multiversion concurrency control (Wikipedia)](https://en.wikipedia.org/wiki/Multiversion_concurrency_control) — the concept map: timestamps, snapshots, and which systems use it.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — chapters on concurrency control walk through tuple headers, hint bits, and vacuum mechanics.
- [MySQL: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/8.4/en/innodb-multi-versioning.html) — the other major MVCC implementation: undo logs and consistent reads, a useful contrast with Postgres.
- [ACID (Wikipedia)](https://en.wikipedia.org/wiki/ACID) — the properties MVCC exists to provide; the isolation-level definitions live here.
- [Readings in Database Systems (Red Book), 5th ed.](http://www.redbook.io/) — the "Weak Isolation and Distribution" chapter collects the snapshot-isolation papers.

## Stretch ideas

- Implement time-travel queries (`SELECT ... AS OF <timestamp>`) by keeping old versions addressable.
- Add predicate locking for true serializability and compare its abort rate against SSI on a contention benchmark.
- Make vacuum concurrent and incremental, and measure bloat under a sustained update workload.
