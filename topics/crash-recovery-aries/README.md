---
title: "Crash Recovery (ARIES)"
category: "databases"
difficulty: "advanced"
tags: [recovery, wal, transactions]
related: [write-ahead-log, mvcc-transactions, event-sourcing-bank, backup-system]
---

# Crash Recovery (ARIES)

ARIES is the recovery algorithm behind DB2, SQL Server, and Postgres's crash recovery: after a power failure, it replays the write-ahead log to restore exactly the committed state — no lost commits, no partial transactions. Building it teaches the three-pass discipline (Analysis, Redo, Undo) that makes restartable recovery possible.

## Core concepts

- **The three passes** — Analysis (figure out what was in flight and what pages were dirty), Redo (repeat history: re-apply every logged change), Undo (roll back losers). In that order, always.
- **Log Sequence Numbers (LSNs)** — Every log record has an LSN; every data page stamps the LSN of its last update (pageLSN). Redo skips any record with LSN ≤ pageLSN — the idempotence that makes repeated recovery safe.
- **Repeating history** — Redo re-applies *all* updates, including those of transactions that never committed. This seems wasteful, but it restores the exact pre-crash state so Undo can then cleanly reverse the losers.
- **Compensation Log Records (CLRs)** — Undo actions are themselves logged as CLRs pointing to the next record to undo. If the system crashes *during* recovery, restart just continues — CLRs are never undone, so undo is idempotent.
- **Dirty Page Table and fuzzy checkpoints** — Checkpoints record dirty pages and their first-dirty LSN (recLSN) *without* flushing them. Redo starts at the minimum recLSN — bounded work, zero quiesce.
- **Transaction Table** — The checkpoint also records active transactions and their last LSN, so Analysis knows exactly which transactions are losers without scanning the whole log.
- **Steal / no-force** — ARIES assumes the buffer manager may write uncommitted pages (steal) and need not flush at commit (no-force). These are the realistic policies; the algorithm's job is to make them safe.

## How it works

During normal operation, every update writes a log record (with undo and redo info) and the page's pageLSN advances; checkpoints periodically write the Transaction Table and Dirty Page Table. After a crash, **Analysis** scans forward from the last checkpoint, rebuilding both tables and identifying loser transactions (active at crash). **Redo** starts at the smallest recLSN in the Dirty Page Table and re-applies every update and CLR whose LSN exceeds the page's pageLSN — reconstructing the exact pre-crash buffer state. **Undo** processes losers backwards from their last LSN: each update is reversed (writing a CLR chained to the record's predecessor), CLRs are skipped via their undo-next pointers, until every loser is fully rolled back. Because redo is idempotent and undo is logged, crashing mid-recovery just restarts the same three passes.

## Build milestones

1. Build a paged key/value store with a WAL carrying undo+redo records and pageLSNs; implement naive whole-log redo recovery.
2. Add the Analysis pass: checkpoint records with Transaction Table and Dirty Page Table; recovery starts from the last checkpoint instead of log start.
3. Implement the Redo pass with pageLSN comparison (skip already-applied records) and verify idempotence by crashing *during* redo and recovering again.
4. Implement the Undo pass with CLRs and undo-next chaining; test rolling back multi-page transactions and verify CLRs are never undone on repeated crashes.
5. Add fuzzy checkpoints (no page flushing at checkpoint time), media-recovery hooks (restore from backup + replay log tail), and a randomized crash-injection test suite that verifies ACID after every restart.

## Best resources

- [ARIES (Wikipedia)](https://en.wikipedia.org/wiki/Algorithms_for_Recovery_and_Isolation_Exploiting_Semantics) — the three principles (WAL, repeating history, logging undo) and the algorithm's structure.
- [ARIES: A Transaction Recovery Method (Mohan et al., 1992)](https://ipads.se.sjtu.edu.cn/courses/csdi/2020/materials/lec10/ARIES.pdf) — the original paper; the definitive reference for LSNs, CLRs, and the three passes.
- [SQLite: Atomic Commit](https://www.sqlite.org/atomiccommit.html) — how SQLite achieves atomic commits and recovery; the clearest small-scale treatment of the same problems.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — WAL, checkpoints, and crash recovery chapters showing ARIES ideas in a real engine.
- [Write-ahead logging (Wikipedia)](https://en.wikipedia.org/wiki/Write-ahead_logging) — the logging discipline ARIES is built on.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — recovery lectures walk through ARIES with worked examples.

## Stretch ideas

- Implement savepoints / partial rollback using the same CLR machinery, exposing nested transaction abort.
- Add parallel recovery: partition the redo pass by page ranges across threads and measure restart time on large logs.
- Build a log-structured "time travel" debugger: replay the WAL to reconstruct the database at any historical LSN.
