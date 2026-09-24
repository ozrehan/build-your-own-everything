---
title: "Write-Ahead Log"
category: "databases"
difficulty: "intermediate"
tags: [durability, recovery, storage-engines]
related: [crash-recovery-aries, b-tree-index, lsm-tree-storage, event-sourcing-bank]
---

# Write-Ahead Log

The write-ahead log (WAL) is the reason a database can promise your data survives a power cut: every change is appended to a sequential log on disk *before* the data pages are touched. Building one teaches the central durability trick of all storage engines — and why sequential writes beat random writes.

## Core concepts

- **Write-ahead rule** — A data page may only be written to its home location after the log records describing the change are durably on disk. Crash at any point and the log still tells the full story.
- **Sequential vs. random I/O** — Appending to a log is sequential; updating scattered data pages is random. The WAL converts the latency-critical path of every write into a fast sequential append.
- **Log sequence numbers (LSNs)** — Every log record gets a monotonically increasing LSN. Pages stamp the LSN of their last applied change, which lets recovery know exactly which log records a page is missing.
- **Checkpoints** — A checkpoint records how far recovery must replay by flushing dirty pages and noting the position. It bounds recovery time: replay starts at the last checkpoint, not at the beginning of time.
- **Redo and undo records** — Redo information re-applies a change that was lost; undo information reverses a change from a transaction that never committed. ARIES-style physiological logging records both per page.
- **Group commit** — Batching multiple transactions' log flushes into one fsync amortizes the most expensive operation in the system. Throughput jumps; per-transaction latency barely moves.
- **Log truncation** — Once checkpoints guarantee old records are no longer needed for recovery, log segments are recycled. Without truncation the log grows forever.

## How it works

On every write, the engine formats a log record (transaction id, page id, before/after images, LSN), appends it to an in-memory log buffer, and on commit flushes the buffer through `fsync` so the record is durable. The data pages themselves are updated in the buffer pool whenever convenient — possibly long after commit. After a crash, recovery reads the last checkpoint, then replays the log forward (redo): any change whose LSN is newer than the page's stamped LSN is re-applied. Finally it rolls back any transaction that had no commit record. The invariant that makes it all work: the log always describes a superset of what's on the data pages.

## Build milestones

1. Build a single-threaded key/value store with an append-only log file: every `put` appends a record; on startup, replay the whole file to rebuild state.
2. Add LSNs, a log buffer with explicit flush, and `fsync` on commit; demonstrate durability by `kill -9`-ing mid-workload and verifying no committed write is lost.
3. Separate the log from the data: keep data pages in memory, write them to a "data file" lazily, and implement redo-only recovery using page LSNs.
4. Add checkpoints (flush dirty pages, write a checkpoint record, truncate old log segments) and group commit; benchmark transactions/sec with and without group commit.
5. Add undo records and rollback of uncommitted transactions at recovery, turning the log into a full ARIES-style redo/undo log.

## Best resources

- [Write-ahead logging (Wikipedia)](https://en.wikipedia.org/wiki/Write-ahead_logging) — the concept, the write-ahead rule, and ARIES context in one page.
- [Write-Ahead Logging in SQLite](https://www.sqlite.org/wal.html) — SQLite's WAL mode documented end to end: frames, checkpoints, and recovery. The clearest real-world WAL doc.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — its WAL chapter covers record format, checkpoints, and full-page writes with internals depth.
- [PostgreSQL: Reliability and the Write-Ahead Log](https://www.postgresql.org/docs/current/wal-intro.html) — the official explanation of why Postgres can survive OS crashes.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — the storage building-blocks chapters treat the WAL as a first-class structure with implementation notes.
- [ARIES: Algorithms for Recovery and Isolation Exploiting Semantics (Wikipedia)](https://en.wikipedia.org/wiki/Algorithms_for_Recovery_and_Isolation_Exploiting_Semantics) — where WAL discipline meets the full recovery algorithm.

## Stretch ideas

- Implement log shipping: stream the WAL to a second process that replays it, giving you a hot standby (see read-replicas-replication).
- Add checksums per log record and demonstrate detecting (and skipping) a torn/corrupted tail after a simulated crash.
- Benchmark fsync latency vs. throughput and implement adaptive group commit that tunes batch size to load.
