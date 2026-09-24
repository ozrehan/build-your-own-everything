---
title: "B-Tree Index"
category: "databases"
difficulty: "intermediate"
tags: [indexing, data-structures, storage-engines]
related: [lsm-tree-storage, secondary-indexing, write-ahead-log, embedded-database]
---

# B-Tree Index

A B-tree is the self-balancing tree structure that lets a database find any row among billions in a handful of disk reads. Building one yourself teaches the single most-used idea in storage engineering: how to keep data ordered on disk while making inserts, lookups, and range scans all fast at once.

## Core concepts

- **Ordered pages instead of a flat file** — A B-tree stores sorted key/value pairs in fixed-size pages (typically 4–16 KB). Because each page is ordered and pages link to each other in order, both point lookups and range scans are natural operations.
- **Fan-out and tree height** — With hundreds of keys per page, a 3-level tree can address hundreds of millions of keys. That is why the core guarantee matters: lookups cost O(log n) disk reads, and n grows exponentially per level.
- **Node split** — When an insert overflows a leaf page, the page splits in two and the middle key is pushed up to the parent. This local surgery is what keeps the tree balanced without ever rebuilding it.
- **Node merge / redistribution** — When deletes empty a page below half-full, it merges with a sibling or borrows keys from one. Without this, the tree would slowly degrade into sparse, half-empty pages.
- **B+ tree variant** — Real databases use B+ trees: all values live in the leaves, leaves are linked into a doubly-linked list, and internal nodes hold only separator keys. Range scans just walk the leaf list.
- **Clustering vs. covering indexes** — A clustered index stores the row itself in the leaves; a secondary index stores the key plus a pointer (rowid/page id) to the heap row. That pointer lookup is why a covering index (all query columns in the key) can skip the table entirely.
- **Page layout and slotted pages** — Inside a page, a small directory of (key offset, length) slots lets keys be variable-length while the page stays compact. Understanding this layout is the bridge from "tree in memory" to "tree on disk".

## How it works

A B-tree lookup starts at the root page and binary-searches its sorted keys to choose the child pointer for the target key, repeating until it reaches a leaf. An insert follows the same path, adds the key to the leaf, and if the leaf overflows it splits the page, promoting the median key upward — splits can cascade to the root, growing the tree by one level. Deletes remove the key and may trigger merges. Because every leaf sits at the same depth and each page is at least half full, the tree stays balanced and every operation touches only O(log n) pages.

## Build milestones

1. Build an in-memory B-tree in any language: insert, point lookup, and in-order iteration, with node split on overflow. Test with 100k random keys and assert sorted iteration.
2. Add deletion with redistribution and merging, plus a page-size parameter; print tree height and average fill factor to see balancing work.
3. Persist it: store fixed-size pages in a single file, address pages by page id, keep a small header page with the root id, and use slotted-page layout for variable-length keys.
4. Add a free-page list and crash-safe writes (write the new page, then update the parent pointer — or reuse the WAL from the write-ahead-log topic) so the file survives `kill -9`.
5. Build a secondary index on top of a toy table: store (key, rowid) pairs, implement range scans and a "covering index" fast path, and benchmark point vs. range queries against a full table scan.

## Best resources

- [B-tree (Wikipedia)](https://en.wikipedia.org/wiki/B-tree) — the canonical definition: invariants, split/merge rules, and the B+ tree variant explained precisely.
- [Let's Build a Simple Database — cstack](https://cstack.github.io/db_tutorial/) — a hands-on C tutorial that builds a persistent B-tree page by page; the closest thing to this topic's blueprint.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — full lecture course with slides and videos; the tree-index lectures are the clearest free treatment of B+ trees.
- [Use The Index, Luke!](https://use-the-index-luke.com/) — Markus Winand's free book on how B-tree indexes actually behave in queries: access vs. filter predicates, composite column order, and why.
- [PostgreSQL: Indexes](https://www.postgresql.org/docs/current/indexes.html) — the official docs on B-tree vs. hash vs. GiST vs. GIN, and how the planner chooses an index.
- [The Case for Learned Index Structures](https://arxiv.org/abs/1712.01208) — the Kraska et al. paper that challenged B-trees with learned models; great for understanding what B-trees assume.

## Stretch ideas

- Implement prefix compression of keys within a page (like real B-trees do) and measure the space savings on string keys.
- Add optimistic latch coupling (lock the parent, then the child) to make the tree safe for concurrent readers and writers.
- Build an R-tree variant for spatial data on the same page abstraction and compare range-query behavior.
