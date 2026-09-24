---
title: "Sharding Strategy"
category: "databases"
difficulty: "advanced"
tags: [partitioning, scalability, distributed-systems]
related: [read-replicas-replication, dht-kademlia, raft-consensus, gossip-protocol]
---

# Sharding Strategy

Sharding splits one logical database across many machines so no single node holds all the data or all the traffic. Building it teaches the hardest part of scaling databases: choosing the split key, and living with everything that choice breaks — especially cross-shard queries and transactions.

## Core concepts

- **Shard key selection** — The field whose value decides placement (e.g., `user_id`). A good key spreads writes evenly and keeps common queries single-shard; a bad key creates hotspots or forces scatter-gather for every query.
- **Range vs. hash partitioning** — Range sharding keeps adjacent keys together (good for range scans, bad for hotspots on sequential ids); hash sharding spreads load evenly (kills range scans, which become scatter-gather).
- **Consistent hashing** — Hash the key onto a ring of nodes so adding/removing a node moves only ~1/n of the data. The foundation of Dynamo/Cassandra-style partitioning.
- **Virtual nodes (vnodes)** — Split each physical node into many virtual ring positions for even distribution and smooth rebalancing. Without vnodes, random ring placement leaves some nodes overloaded.
- **Scatter-gather queries** — A query without the shard key fans out to all shards and merges results. Works, but latency becomes the slowest shard's latency and cross-shard joins/aggregations get expensive fast.
- **Cross-shard transactions** — ACID across shards needs two-phase commit (2PC) with a coordinator — slow and failure-prone. Real systems either avoid cross-shard writes in the data model or accept the cost.
- **Rebalancing and resharding** — Splitting a hot shard or adding nodes means moving data while serving traffic: range migration with dual-write or catch-up phases, done without downtime.

## How it works

Every key is mapped to a shard by the partitioning function: `shard = hash(shard_key) mod N` for hash sharding, or a range map (kept in a routing table or config service) for range sharding. A router/proxy layer (like Vitess's vtgate) parses each query, extracts the shard key if present, and sends the query to exactly one shard; without a shard key it fans out to all shards and merges. Each shard is itself replicated (see read-replicas-replication) for fault tolerance. When a shard outgrows its node, the system splits its key range, copies data to the new shard while dual-writing new updates, then atomically flips routing. The whole art is in the shard key: it determines data distribution, query patterns, and which operations stay cheap.

## Build milestones

1. Build a hash-sharded key/value store: N shard processes, a client library computing `hash(key) mod N`, and single-key get/put routed correctly.
2. Add range sharding with a routing table service; support range scans within one shard and measure the hotspot when keys are sequential ids.
3. Implement a query router that parses simple filters, routes shard-key queries to one shard, and scatter-gathers the rest with result merging.
4. Add per-shard replication (one follower each) and implement resharding: split a shard's range and migrate data with zero-downtime dual-write.
5. Implement cross-shard transactions with 2PC for the rare multi-shard write, and benchmark its latency/failure modes vs. single-shard writes.

## Best resources

- [Shard (database architecture) (Wikipedia)](https://en.wikipedia.org/wiki/Shard_(database_architecture)) — partitioning methods, advantages, and the classic drawbacks.
- [Vitess](https://vitess.io/) — the production sharding proxy for MySQL (born at YouTube); its docs explain vtgate routing, resharding, and VSchema.
- [MongoDB: Sharding](https://www.mongodb.com/docs/manual/sharding/) — the official guide to shard keys, zones, and balancer behavior.
- [Designing Data-Intensive Applications — Martin Kleppmann](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) — chapter 6 is the definitive partitioning treatment: skew, hotspots, rebalancing.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — partitioning and distributed-systems chapters with implementation detail.
- [Dynamo: Amazon's Highly Available Key-Value Store (SOSP 2007)](http://www.redbook.io/) — consistent hashing, vnodes, and quorum replication; in the Red Book's distribution chapter.

## Stretch ideas

- Implement consistent hashing with vnodes and simulate node addition/removal, measuring data movement vs. naive mod-N.
- Add a shard-key advisor: analyze a query log and recommend the key minimizing scatter-gather.
- Build geo-sharding: pin shards to regions for data locality and measure cross-region query cost.
