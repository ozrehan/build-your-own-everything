---
title: "Secondary Indexing"
category: "databases"
difficulty: "intermediate"
tags: [indexing, query-optimization, access-paths]
related: [b-tree-index, full-text-search-index, sql-parser, query-planner-optimizer]
---

# Secondary Indexing

Secondary indexes are how a database answers "find by email" without scanning the table: auxiliary structures keyed by non-primary columns. Building them teaches index maintenance on writes, the covering-index optimization, and why every index is a tradeoff paid on every `INSERT`.

## Core concepts

- **Primary vs. secondary** — The primary index defines row storage order (clustered) or the rowid lookup; secondary indexes are separate structures mapping indexed values → row locations. A table can have one primary and many secondaries.
- **Index maintenance cost** — Every `INSERT`/`UPDATE`/`DELETE` must update every secondary index on affected columns. Indexes speed reads and tax writes — the fundamental tradeoff behind "don't over-index".
- **Covering indexes** — If the index key contains all columns the query needs, the engine never touches the table (index-only scan). INCLUDE columns / index-organized payloads exist precisely for this.
- **Composite indexes and leftmost prefix** — An index on `(a, b, c)` serves queries on `a`, `(a,b)`, `(a,b,c)` — but not on `b` alone. Column order should follow predicate shape: equality columns first, then at most one range column.
- **Index types beyond B-tree** — Hash (equality only), GiST/SP-GiST (extensible: geometry, ranges), GIN (inverted: full text, arrays, JSON), BRIN (block ranges for naturally ordered data like timestamps), bitmap (low-cardinality analytics).
- **Partial and expression indexes** — Index only rows matching a predicate (`WHERE active`) or the result of an expression (`lower(email)`). Smaller, faster, and exactly matched to the queries that need them.
- **Index selection by the planner** — The optimizer estimates selectivity per index (via statistics) and picks the cheapest access path — or no index at all. Understanding this is what `EXPLAIN` is for.

## How it works

A secondary index is typically a B-tree whose keys are `(indexed_column_values, row_pointer)` — the row pointer breaks ties and locates the heap row. On insert, the engine computes each indexed expression and inserts entries into every affected index inside the same transaction; on update it deletes stale entries and inserts new ones; deletes remove entries. A query planner consults table statistics to estimate each candidate index's selectivity, then chooses: full scan, one index scan plus heap fetch, bitmap heap scan (collect row pointers from multiple indexes, then fetch rows in physical order), or an index-only scan when the index covers the query. Unique indexes add a constraint check on insert — a duplicate key aborts the transaction.

## Build milestones

1. On top of a heap table with rowids, build one secondary B-tree index on a column; implement point lookup and range scan returning rowids, then heap fetch.
2. Add automatic index maintenance: inserts/updates/deletes keep the index consistent; write a torture test comparing indexed vs. scanned results on random workloads.
3. Implement composite indexes with leftmost-prefix matching and a tiny planner rule that picks the best index for a given `WHERE` clause.
4. Add covering indexes (payload columns in the leaf) with index-only scans, plus unique indexes with duplicate rejection.
5. Implement two exotic types — a GIN-style inverted index for array/JSON containment and a BRIN-style block-range index for timestamp columns — and benchmark each against B-tree on its home turf.

## Best resources

- [Use The Index, Luke!](https://use-the-index-luke.com/) — the single best resource on this topic: anatomy of an index, composite order, and execution plans, free online.
- [PostgreSQL: Indexes](https://www.postgresql.org/docs/current/indexes.html) — B-tree, hash, GiST, SP-GiST, GIN, BRIN: what each is for, with examples.
- [Database index (Wikipedia)](https://en.wikipedia.org/wiki/Database_index) — the taxonomy: clustered vs. non-clustered, index types, and their tradeoffs.
- [SQLite Query Planner](https://sqlite.org/queryplanner.html) — how a real engine picks indexes, including automatic indexes and skip-scan.
- [The Internals of PostgreSQL — Hironobu Suzuki](https://www.interdb.jp/pg/index.html) — index access methods at the internals level: page layout, WAL logging of index changes.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — index lectures covering B+ trees, hashing, and index selection.

## Stretch ideas

- Implement index advisor tooling: given a query log, recommend indexes and estimate their write overhead.
- Add online index builds: create an index on a live table without blocking writes (snapshot + catch-up phases).
- Build a learned index (piecewise-linear model over sorted keys) and compare lookup speed against your B-tree.
