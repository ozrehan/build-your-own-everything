---
title: "Metrics Monitor"
category: "devops-infra"
difficulty: "intermediate"
tags: [monitoring, metrics, observability]
related: [dashboard-metrics, log-aggregator, status-page]
---

# Metrics Monitor

"Is the site slow, or is it just me?" Metrics monitoring answers that with numbers: a system that scrapes numeric time series (request latency, CPU, error counts) from your services, stores them, and lets you query, graph, and alert on them. Building a mini-Prometheus — exposition format, scraper, TSDB, query language, alerting rules — teaches you the pull-based monitoring model that now dominates infrastructure observability.

## Core concepts

- **Metrics vs logs vs traces** — metrics are aggregated numbers over time (cheap, great for dashboards and alerts); logs are discrete events (rich detail, expensive); traces follow single requests. A monitor specializes in the first and references the others.
- **Pull-based scraping** — instead of services pushing data, the monitor polls an HTTP `/metrics` endpoint on each target. This makes discovery simple (any HTTP server qualifies), failures obvious (a failed scrape is itself a signal), and backpressure natural.
- **Exposition format** — the text protocol of `# HELP`, `# TYPE`, and `metric_name{label="value"} 123` lines. Labels turn one metric name into thousands of series (per-pod, per-endpoint); label design is the core skill of the whole discipline.
- **Metric types: counter, gauge, histogram** — counters only increase (requests served), gauges go up and down (queue depth), histograms bucket observations (latency distribution). Choosing wrong — e.g. averaging a counter — is the classic monitoring bug.
- **Time-series storage** — samples are `(timestamp, value)` pairs compressed in chunks (delta-of-delta encoding like Prometheus's TSDB). High-cardinality labels explode storage, which is why cardinality budgets matter.
- **Alerting rules and silences** — PromQL-style expressions evaluated on a schedule (`rate(errors[5m]) > 0.05`) produce alerts that are deduplicated, grouped by label, and routed; silences and inhibition rules keep paging humane.
- **Service discovery** — targets come and go (containers, autoscaling), so the scraper watches a discovery source (DNS, file, Kubernetes API) and re-resolves the target list continuously rather than using a static config.

## How it works

Each instrumented service exposes `/metrics` in the exposition format. The monitor's discovery component maintains the target list; the scraper fans out HTTP GETs on an interval (e.g. every 15s), parses the text, and appends samples to the TSDB: an in-memory head for recent data (a few hours) plus immutable compressed chunks flushed to disk, indexed by metric name and label set.

The query engine evaluates expressions over time ranges by loading the relevant chunks and applying operators — `rate()` differentiates counters per second, `sum by (job)` aggregates across labels, comparisons filter series. A rule evaluator runs alerting rules on a tick, and firing alerts go to a notifier that groups by labels, deduplicates repeats, and sends to channels (email, Slack, PagerDuty) respecting silences. The UI graphs query results and shows target health: which scrapes are failing and why.

## Build milestones

1. Build an instrumented demo app exposing `/metrics` in Prometheus text format (a counter and a histogram), plus a scraper that polls it and prints the parsed series.
2. Add a minimal TSDB: append samples in memory, flush compressed chunks to disk, and support `GET /api/v1/query?query=...` for instant queries over label matchers.
3. Implement `rate()`, `sum by`, and comparison operators; add alerting rules evaluated every 30s with a simple webhook notifier.
4. Add file-based service discovery, a retention/compaction policy for old chunks, and a small dashboard UI with graphs — then point it at a real service for a week and tune your alerts.

## Best resources

- [Prometheus documentation — overview](https://prometheus.io/docs/introduction/overview/) — the architecture doc for the whole model: scraping, TSDB, PromQL, alerting. Your spec.
- [Prometheus exposition formats](https://prometheus.io/docs/instrumenting/exposition_formats/) — the exact text format, metric types, and escaping rules your scraper and demo app must implement.
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — the four golden signals (latency, traffic, errors, saturation) and why you alert on symptoms, not causes.
- [Brendan Gregg — The USE Method](http://www.brendangregg.com/usemethod.html) — utilization/saturation/errors per resource; the checklist that tells you which metrics to collect on every box.
- [Tom Wilkie — The RED Method](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/) — rate/errors/duration per service; the request-scoped counterpart to USE, and the basis of most service dashboards.

## Stretch ideas

- Implement remote-write: ship samples to a long-term store and add downsampling (5m/1h rollups) so a year of data stays queryable.
- Add anomaly detection: baseline each series with a rolling median/MAD and alert on deviation instead of static thresholds.
- Build exemplar support: attach trace IDs to histogram buckets so a latency spike links straight to the offending trace.
