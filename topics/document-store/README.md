---
title: "Document Store"
category: "databases"
difficulty: "intermediate"
tags: [nosql, json, schema-flexibility]
related: [b-tree-index, secondary-indexing, mvcc-transactions, full-text-search-index]
---

# Document Store

A document store (MongoDB, CouchDB) keeps data as self-describing JSON-like documents instead of rows, so each record can have a different shape without schema migrations. Building one teaches schema-flexible storage, document path indexing, and the replication story that made NoSQL famous.

## Core concepts

- **BSON / binary JSON** — Documents are stored as length-prefixed binary JSON: fast to scan, with types (dates, ObjectIds, binary) that plain JSON lacks. Understanding the encoding explains both its flexibility and its storage overhead.
- **Collections without schemas** — A collection holds documents that merely *tend* to share a shape. The application owns the schema, which removes migrations but pushes validation and consistency discipline outward.
- **Embedded vs. referenced** — One-to-few relationships embed as subdocuments (one read fetches all); one-to-many/many-to-many use references (ids pointing at other documents). This denormalization decision is the core data-modeling skill.
- **Dot-path queries and indexes** — Queries address nested fields (`address.city`), and secondary indexes can be built on those paths — including multikey indexes that expand one index entry per array element.
- **Aggregation pipeline** — Stages (`$match`, `$group`, `$sort`, `$lookup`) compose into a data-processing pipeline executed inside the database. It's MapReduce's friendlier descendant and a query planner target in its own right.
- **Replica sets and elections** — The classic NoSQL HA story: a primary takes writes, secondaries replicate the oplog, and an election promotes a new primary on failure. (See read-replicas-replication and raft-consensus.)
- **MVCC-ish concurrency** — Document-level locking / multi-version storage lets concurrent writers touch different documents without blocking; WiredTiger's MVCC is why modern MongoDB handles mixed workloads.

## How it works

Writes arrive as documents, get an `_id`, and are stored in a collection file (often a B-tree or LSM-tree keyed by `_id`) with each document serialized as BSON. Secondary indexes are B-trees keyed by the indexed field's value (expanding arrays into multiple entries for multikey indexes) pointing back to document locations. A query planner parses the filter document, picks the most selective usable index (or falls back to collection scan), fetches matching documents, and runs the aggregation pipeline stages over them. Every mutation is also appended to an operation log (oplog); secondaries tail the oplog to stay in sync, and elections use it to pick the most up-to-date new primary.

## Build milestones

1. Build a JSON document collection on disk: insert/find by `_id`, BSON-ish binary encoding, and a simple filter language (`{age: {$gt: 30}}`).
2. Add secondary indexes on dot paths (`address.city`), including multikey indexes over arrays; implement index selection in a tiny planner.
3. Implement an aggregation pipeline: `$match`, `$project`, `$group` (with `$sum`/`$avg`), `$sort`, `$limit`, executed as chained iterators.
4. Add an oplog and a replication follower that tails it; implement primary election on failure with a simple voting protocol.
5. Add schema validation rules per collection, text search over string fields, and a MongoDB-wire-protocol-compatible server so real drivers can connect.

## Best resources

- [MongoDB Manual](https://www.mongodb.com/docs/manual/) — the definitive reference: data modeling (embed vs. reference), indexing, aggregation, and replication.
- [Apache CouchDB](https://couchdb.apache.org/) — the other classic document store; its MVCC-per-document and replication protocol are beautifully documented.
- [Document-oriented database (Wikipedia)](https://en.wikipedia.org/wiki/Document-oriented_database) — the concept, history, and comparison with relational and key/value models.
- [SQLite JSON1 extension](https://sqlite.org/json1.html) — how a relational engine does document queries natively; a great study in hybrid design.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — storage engines and replication chapters that explain what's under the document API.
- [Designing Data-Intensive Applications — Martin Kleppmann](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) — the data-modeling and replication chapters put document stores in context.

## Stretch ideas

- Implement change streams: a tailable cursor over the oplog that pushes document changes to subscribers.
- Add multi-document ACID transactions with snapshot isolation and compare performance to single-document atomicity.
- Build a schema-inference tool that samples a collection and proposes the "implicit schema" with field type histograms.
