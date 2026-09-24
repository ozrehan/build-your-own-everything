---
title: "LSM-Tree Storage Engine"
category: "databases"
difficulty: "advanced"
tags: [storage-engines, indexing, write-amplification]
related: [b-tree-index, write-ahead-log, columnar-storage-format, embedded-database]
---

# LSM-Tree Storage Engine

An LSM-tree (Log-Structured Merge-tree) is the storage engine behind Cassandra, RocksDB, and Bigtable: it turns random writes into sequential ones, which is why write-heavy databases use it instead of B-trees. Building one teaches how databases trade read cost for write speed, and what compaction really is.

## Core concepts

- **Memtable** — An in-memory sorted structure (usually a skiplist or balanced tree) that absorbs all writes. Reads check it first, so recently written data is always visible even though it is not on disk yet.
- **Immutable memtable and flush** — When the memtable fills, it is frozen and written to disk as a sorted file (an SSTable), while a fresh memtable takes over. Writes never block on disk seeks — only on sequential flushes.
- **SSTable (Sorted String Table)** — An immutable, sorted file of key/value pairs with an index block for binary search. Immutability is the whole trick: files are never modified in place, only created and deleted.
- **Compaction** — A background process that merges overlapping SSTables into fewer, larger ones, discarding overwritten and deleted keys. It bounds read amplification at the cost of write amplification (rewriting data multiple times).
- **Levels and size-tiered vs. leveled compaction** — Leveled compaction (RocksDB) keeps one sorted run per level with levels growing ~10x; size-tiered (Cassandra) merges same-sized files. The choice trades write amplification against read amplification.
- **Bloom filters** — A tiny probabilistic structure per SSTable that answers "is this key definitely not here?" — letting point lookups skip most files without reading them.
- **Tombstones** — Deletes are written as special markers that flow through compaction; the old value is only physically removed once the tombstone has merged past every file containing it.

## How it works

Every write goes to the write-ahead log and the memtable. When the memtable reaches its size limit it is frozen, flushed to disk as an immutable sorted SSTable, and the log segment is discarded. Reads merge results across the memtable and all SSTables, newest first, so the latest value for a key wins. In the background, compaction repeatedly merges overlapping SSTables level by level, dropping superseded values and tombstoned keys, which keeps the number of files — and thus read cost — bounded. The engine is a pipeline: fast sequential writes up front, paid for later by background merge work.

## Build milestones

1. Build the memtable as a skiplist (or sorted map) with put/get/delete, plus a simple WAL file so it survives restarts.
2. Add freeze-and-flush: when the memtable exceeds N keys, write it to an immutable sorted file and start a new one; reads merge the memtable with all on-disk files.
3. Add a manifest file tracking the live SSTable set, plus per-file Bloom filters so point lookups skip files quickly.
4. Implement leveled compaction: merge overlapping files from level L into level L+1, dropping overwritten keys and resolved tombstones; expose read/write amplification metrics.
5. Add range iterators that merge-sort across levels, snapshot reads (read at a sequence number), and a benchmark comparing write throughput against a naive B-tree or hash file.

## Best resources

- [Log-structured merge-tree (Wikipedia)](https://en.wikipedia.org/wiki/Log-structured_merge-tree) — the original O'Neil et al. design: components, rolling merge, and the read/write cost model.
- [LevelDB](https://github.com/google/leveldb) — Google's small, readable LSM implementation; the best codebase to study the core loop.
- [RocksDB](https://github.com/facebook/rocksdb) — the production LSM engine (Facebook/Meta); its wiki and code show leveled compaction, column families, and tuning in the real world.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — the book's storage-engine half is essentially a guided tour of B-trees vs. LSM-trees with real implementation detail.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — lectures on LSM storage, compaction policies, and the LSM vs. B-tree tradeoff.
- [Readings in Database Systems (Red Book), 5th ed.](http://www.redbook.io/) — the "Techniques Everyone Should Know" chapter collects the classic storage papers.

## Stretch ideas

- Implement tiered (universal) compaction alongside leveled and benchmark write vs. read amplification on the same workload.
- Add compression (Snappy/LZ4) per SSTable block and measure the size/latency tradeoff.
- Build secondary indexes as separate LSM-trees and explore how tombstones complicate index maintenance.
