---
title: "Embedded Database"
category: "databases"
difficulty: "intermediate"
tags: [sqlite, storage-engines, zero-ops]
related: [b-tree-index, lsm-tree-storage, write-ahead-log, sql-parser]
---

# Embedded Database

An embedded database (SQLite, DuckDB) is a full SQL engine that runs *inside* your process — no server, no network, just a library and a file. Building one teaches the complete database pipeline end to end: parsing, planning, B-tree storage, and transactions, all small enough to hold in your head.

## Core concepts

- **Library, not server** — The engine links into your application; "connections" are function calls. This removes the network, auth, and process management — and forces the engine to be crash-safe as a library.
- **Single-file format** — The entire database (schema, tables, indexes) lives in one cross-platform file with a fixed header. Portability and backup become "copy the file".
- **B-tree for everything** — SQLite stores tables as B-trees keyed by rowid and indexes as B-trees keyed by indexed columns. One page format, one tree implementation, the whole database.
- **Pager and the buffer pool** — The pager mediates between B-tree pages and the file: caching, read/write, and the journaling that makes commits atomic. It's the OS-facing half of the engine.
- **Rollback journal vs. WAL mode** — Journal mode copies original pages aside before writing (rollback on crash); WAL mode (see write-ahead-log) appends changes and checkpoints. Two durability strategies, one pager.
- **Virtual machine (VDBE)** — SQLite compiles SQL to bytecode for a small register-based VM. A bytecode layer decouples the planner from storage and makes the executor testable in isolation.
- **Zero-configuration reliability** — No setup, no tuning, no DBA — yet it must never corrupt data. The famous SQLite test suite (100% branch coverage, simulated I/O failures) is part of the design philosophy.

## How it works

A SQL string enters the parser (SQLite uses the Lemon parser generator) producing an AST; the code generator walks the AST emitting VDBE bytecode — a sequence of operations like `OpenRead`, `Column`, `Filter`, `ResultRow` over virtual cursors. Each cursor is backed by a B-tree: the pager fetches 4 KB pages from the file into the page cache, and B-tree code navigates them. Writes go through the pager too: in journal mode, original pages are copied to the rollback journal before modification; on commit the journal is deleted (or the WAL is fsync'd and checkpointed). A transaction is just a bytecode program whose page modifications are made atomic by the pager — the entire engine is parser → bytecode → pager → file.

## Build milestones

1. Build the storage core: a pager with fixed-size pages, a page cache, and a B-tree (table keyed by integer rowid) persisted in a single file; support insert and full scan.
2. Add a second B-tree type for secondary indexes and a rollback journal so commits are atomic across crashes (test with `kill -9`).
3. Write a SQL subset parser (`CREATE TABLE`, `INSERT`, `SELECT ... WHERE`, simple expressions) and a direct AST-to-cursor executor.
4. Add a bytecode VM layer: compile queries to a small op set, implement `EXPLAIN` showing the bytecode, and rewrite the executor on top of it.
5. Add WAL mode, `UPDATE`/`DELETE`, transactions with savepoints, and a torture test: random crash injection during a workload with integrity verification after every restart.

## Best resources

- [Let's Build a Simple Database — cstack](https://cstack.github.io/db_tutorial/) — the canonical hands-on guide: B-tree, pager, and SQL-ish frontend in C, built incrementally.
- [SQLite documentation](https://sqlite.org/docs.html) — architecture docs, the WAL page, atomic commit, and file format specs from the reference implementation.
- [SQLite: How SQLite Is Tested](https://sqlite.org/testing.html) — the testing philosophy (100% branch coverage, simulated crashes); essential reading for "never corrupt data".
- [The Architecture of Open Source Applications: SQLite](https://aosabook.org/en/v1/sqlite.html) — a compact architectural tour of the whole engine.
- [DuckDB](https://duckdb.org/) — the analytical embedded DB; its docs show how the same embedded idea serves OLAP with vectorized execution.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — the storage and execution lectures map directly onto your pager and VM.

## Stretch ideas

- Implement the SQLite file format itself well enough that the real `sqlite3` CLI can open your database files.
- Add an in-process analytical extension: columnar mini-batches and vectorized aggregation inside the VM.
- Fuzz the parser and pager with randomized crash injection and drive corruption bugs to zero.
