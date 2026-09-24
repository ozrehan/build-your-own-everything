---
title: "Time-Series Database"
category: "databases"
difficulty: "intermediate"
tags: [time-series, metrics, compression]
related: [columnar-storage-format, lsm-tree-storage, dashboard-metrics, metrics-monitor]
---

# Time-Series Database

A time-series database stores timestamped measurements — metrics, sensor readings, stock ticks — and answers "give me the p99 latency per minute for the last 30 days" in milliseconds. Building one teaches the two superpowers of the genre: ruthless timestamp/value compression and time-bucketed aggregation.

## Core concepts

- **Time-partitioned storage** — Data is physically organized by time (chunks per hour/day). Retention ("drop data older than 90 days") becomes deleting whole chunks, and range queries prune entire partitions without reading them.
- **Timestamp compression (delta-of-delta)** — Timestamps arrive at near-regular intervals, so storing the *delta of deltas* (e.g., Gorilla's encoding) shrinks 8-byte timestamps to a few bits each.
- **Value compression (XOR / Gorilla)** — Floating-point values change slowly; XOR-ing consecutive values produces mostly-zero bit patterns that compress dramatically. This one trick is why TSDBs store 10x more points per GB than naive formats.
- **Downsampling and rollups** — Precompute per-minute/hour aggregates (avg, max, p99) at ingest or via background jobs. Dashboards query the rollups, not the raw points — trading precision for speed.
- **Out-of-order and late data** — Real sensors deliver late or out-of-order points. The engine must decide: a small reorder buffer, or reject anything older than the watermark. This policy shapes the whole write path.
- **Tag-based data model** — A series is identified by (metric name + tag set), e.g. `http_latency{host=web1, region=eu}`. Queries select series by tag matchers, then aggregate over time — the Prometheus model.
- **Retention and continuous queries** — Raw points expire after N days while downsampled rollups live longer; continuous queries / recording rules compute the rollups incrementally.

## How it works

Each incoming point is routed to the in-memory chunk for its series (identified by metric + tags), where timestamps and values are appended using delta-of-delta and XOR compression. Chunks cover fixed time windows (e.g., 2 hours); when a window closes, the chunk is sealed, optionally re-encoded more aggressively, and flushed to disk indexed by series id and time range. Queries parse tag matchers to find matching series, load only the chunks overlapping the time range (partition pruning), decompress on the fly, and aggregate into time buckets (rate, avg, histogram quantiles). Background jobs downsample sealed chunks into rollup tables and enforce retention by dropping expired chunks wholesale.

## Build milestones

1. Build the write path: an in-memory map of series → append-only arrays of (timestamp, value); support out-of-order points within a small reorder window.
2. Add Gorilla-style compression: delta-of-delta timestamps and XOR float encoding; measure bytes/point before and after on a real dataset (e.g., a day of CPU metrics).
3. Implement time-partitioned chunk files on disk with a series index; support range queries with partition pruning and tag matchers.
4. Add aggregation: bucket points into fixed windows and compute avg/min/max/p99; add downsampling jobs that precompute hourly rollups from raw chunks.
5. Add retention policies (drop raw chunks after 7 days, keep rollups for a year), late-data handling policy, and a simple HTTP API + dashboard query endpoint.

## Best resources

- [TimescaleDB documentation](https://docs.timescale.com/) — hypertables (automatic time partitioning), compression, and continuous aggregates on top of Postgres; the best conceptual model.
- [Prometheus documentation](https://prometheus.io/docs/) — the tag-based data model, PromQL, and the TSDB storage format that popularized it.
- [InfluxDB documentation](https://docs.influxdata.com/influxdb/) — line protocol, retention policies, and continuous queries from the other major design lineage.
- [Time series database (Wikipedia)](https://en.wikipedia.org/wiki/Time_series_database) — the landscape: use cases, and how TSDBs differ from relational and NoSQL stores.
- [Gorilla: A Fast, Scalable, In-Memory Time Series Database (VLDB 2015)](https://doi.org/10.14778/2824032.2824078) — Facebook's paper; the delta-of-delta + XOR compression scheme every TSDB now uses.
- [Database Internals — Alex Petrov](https://www.databass.dev/) — storage-engine fundamentals that transfer directly: LSM-trees, compression, and partitioning.

## Stretch ideas

- Implement PromQL-style `rate()` and `histogram_quantile()` over your chunks and compare results against real Prometheus.
- Add anomaly detection: maintain per-series rolling baselines and alert when a bucket deviates by N sigma.
- Build a distributed version: shard series by hash of tag set across nodes (see sharding-strategy) with query fan-out.
