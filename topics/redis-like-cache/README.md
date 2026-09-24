---
title: "Redis-Like Cache"
category: "databases"
difficulty: "beginner"
tags: [caching, key-value, in-memory]
related: [connection-pooler, rate-limiter, message-queue, page-cache]
---

# Redis-Like Cache

A Redis-like cache is an in-memory key/value server speaking the RESP protocol: sub-millisecond reads, rich data structures, and optional persistence. Building one teaches event-driven networking, hash-table engineering, and the data-structure tricks (lists, sets, sorted sets) that make Redis more than a hash map.

## Core concepts

- **RESP (REdis Serialization Protocol)** — The simple text-based wire protocol: `*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n`. Implementing a parser for it means real `redis-cli` can talk to your server.
- **Single-threaded event loop** — Redis handles tens of thousands of connections on one thread with epoll/kqueue and non-blocking I/O. No locks, no context-switch storms — the design lesson is that I/O, not CPU, is the bottleneck.
- **Data structures, not just strings** — Lists (queues), sets, sorted sets (leaderboards via skiplists), hashes, streams. Each has purpose-built encodings; the server is a data-structure toolkit behind a network API.
- **Compact encodings** — Small hashes/lists use ziplists (now listpacks): contiguous memory instead of pointers. Memory efficiency at millions of keys is an engineering discipline of its own.
- **Expiry and eviction** — Keys carry TTLs checked lazily (on access) plus active sampling; when memory fills, policies like allkeys-lru or volatile-ttl choose victims. Caching is defined by what you throw away.
- **Persistence options** — RDB snapshots (fork + copy-on-write dump) vs. AOF (append every write, rewrite in background). The durability/latency tradeoff in miniature.
- **Pipelining** — Batching many commands per round trip. A huge fraction of real Redis performance comes from clients pipelining, not from server cleverness.

## How it works

The server runs a single-threaded event loop: it accepts TCP connections, reads bytes into per-connection buffers, and parses RESP commands. Each command dispatches to a handler that operates on in-memory structures — a global hash table mapping keys to objects, where each object has a type tag and encoding. Strings are reference-counted SDS buffers; sorted sets layer a skiplist over a hash table for O(log n) range queries by score plus O(1) member lookup. Expired keys are reclaimed by a mix of lazy checks on access and periodic random sampling of the keyspace. Writes optionally append to an AOF file (fsync policy configurable) while a background fork writes RDB snapshots using the OS's copy-on-write. Replies are serialized back to RESP and flushed by the event loop.

## Build milestones

1. Build a TCP server with a RESP parser and implement `SET`/`GET`/`DEL`/`EXISTS` on an in-memory hash table; verify with real `redis-cli`.
2. Add expiry: `EXPIRE`/`TTL`, lazy expiration on access, and periodic active expiry sampling; add `KEYS`/`SCAN` iteration.
3. Implement lists (`LPUSH`/`RPOP`/`LRANGE`), sets (`SADD`/`SMEMBERS`), and hashes (`HSET`/`HGETALL`) with compact encodings for small collections.
4. Implement sorted sets with a skiplist (`ZADD`, `ZRANGE`, `ZRANK`) and build a leaderboard demo; add pipelining support and benchmark it.
5. Add persistence: RDB-style snapshots and an AOF log with rewrite; implement one eviction policy (allkeys-lru) with a memory cap and test under pressure.

## Best resources

- [Redis documentation](https://redis.io/docs/) — commands reference, data types, persistence, and eviction policies from the source.
- [Redis source code](https://github.com/redis/redis) — famously readable C; `dict.c`, `t_zset.c`, and `ae.c` (event loop) are the curriculum.
- [memcached](https://memcached.org/) — the simpler, multithreaded alternative; comparing its slab allocator and LRU with Redis sharpens the design lessons.
- [Cache replacement policies (Wikipedia)](https://en.wikipedia.org/wiki/Cache_replacement_policies) — LRU, LFU, and friends: the theory behind eviction.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — the page cache and storage chapters explain what sits beneath an in-memory store.
- [CMU 15-445/645 Intro to Database Systems](https://15445.courses.cs.cmu.edu/) — buffer pool management lectures are the database version of cache eviction.

## Stretch ideas

- Implement Redis Streams (`XADD`/`XREAD`) and build a tiny message queue on top (see message-queue).
- Add Lua scripting (`EVAL`) with a sandboxed interpreter for atomic multi-key operations.
- Cluster it: hash-slot sharding across instances with client-side redirection (see sharding-strategy).
