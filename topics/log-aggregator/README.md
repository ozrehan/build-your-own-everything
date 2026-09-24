---
title: "Log Aggregator"
category: "devops-infra"
difficulty: "intermediate"
tags: [logging, observability, elk]
related: [metrics-monitor, distributed-tracer, status-page]
---

# Log Aggregator

When you have fifty containers on ten machines, `tail -f` stops working. A log aggregator collects log lines from every host and container, parses them into structured records, indexes them centrally, and gives you a search UI — "show me all 500s from the payments service in the last hour". Building a mini-ELK/Loki teaches you the pipeline every observability vendor runs: ship, parse, index, retain.

## Core concepts

- **Structured logging** — emitting JSON (`{"level":"error","service":"api","latency_ms":412}`) instead of free text turns logs into queryable records. The single highest-leverage logging decision a team can make.
- **Shipping: agents vs direct** — a lightweight agent (Fluentd/Fluent Bit style) runs on each host, tails files or reads container stdout, and forwards over the network with batching, retries, and disk buffering for outages. Apps stay dumb; agents handle delivery.
- **Parsing and enrichment** — grok/regex or JSON parsers extract fields (timestamp, level, request ID) at ingest; enrichment adds host, container, and Kubernetes metadata. Parsing at ingest makes queries fast; parsing at query time keeps ingest cheap — the central tradeoff.
- **Indexing strategies** — full-text inverted indexes (Elasticsearch) make arbitrary string search fast but are storage-hungry; label-only indexes (Loki) index just metadata and scan compressed chunks for the rest, trading query speed for 10x lower cost.
- **Retention and rotation** — logs are append-only and voluminous, so hot/warm/cold tiers move old data to cheaper storage and eventually delete it. Retention policy is a cost decision disguised as an engineering one.
- **Backpressure and durability** — when the central store is slow, agents must buffer to disk and shed load gracefully rather than OOMing or dropping silently. At-least-once delivery with idempotent writes is the standard guarantee.
- **Correlation IDs** — a request ID stamped on every log line across services lets you reconstruct one request's journey by filtering on a single value — the poor man's distributed trace, and often enough.

## How it works

On each host, an agent tails log sources (files via inotify, or the container runtime's log driver) and batches lines into chunks. Each chunk is parsed: timestamp normalized, JSON extracted, labels attached (hostname, container name, service), and shipped over HTTP/gRPC to the ingester with retries and a local disk buffer for when the backend is unreachable.

The ingester validates, optionally applies a sampling policy for high-volume debug logs, and writes to storage: an index entry (timestamp + labels + a pointer) plus the compressed log chunk. Queries arrive with a label selector and time range; the querier finds matching chunks, decompresses, applies line filters (substring or regex) and field predicates, and streams results back newest-first. A retention sweeper deletes chunks older than the policy.

## Build milestones

1. Build a shipper: tail a log file, parse JSON lines, and POST batches to a collector that appends them to per-day files on disk.
2. Add label extraction and a query API: `GET /query?service=api&level=error&since=1h` returning matching lines newest-first, with substring filtering.
3. Implement the agent model: run the shipper on multiple "hosts", add disk buffering with retry, gzip compression of stored chunks, and a retention sweeper.
4. Build a simple inverted index over tokens for full-text search, add a web UI with live tailing, and benchmark ingest throughput — then compare your storage per GB against Loki's design doc.

## Best resources

- [Fluentd documentation](https://docs.fluentd.org/) — the canonical log shipper: input/filter/output plugin model, buffering, and retry semantics; the architecture your agent copies.
- [Grafana Loki documentation](https://grafana.com/docs/loki/latest/) — the label-indexed, low-cost approach to log aggregation; read its architecture to understand the index-vs-scan tradeoff.
- [Jay Kreps — The Log](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) — the foundational essay on the append-only log as the unifying abstraction behind databases, replication, and stream processing.
- [Elastic Common Schema](https://www.elastic.co/guide/en/ecs/current/index.html) — a standardized field naming scheme (`http.response.status_code`, `service.name`); shows what "structured" means at scale.
- [Graylog documentation](https://go2docs.graylog.org/) — extractors, streams, and pipeline rules; a practical tour of parsing and routing features a mature aggregator needs.

## Stretch ideas

- Add log-based alerting: evaluate queries on a schedule and fire alerts on patterns (e.g. >10 auth failures/minute from one IP).
- Implement trace-aware querying: join log lines with trace IDs from your distributed tracer to jump from a log line to its full trace.
- Build anomaly detection on log volume: alert when a service's error rate deviates from its weekly baseline.
