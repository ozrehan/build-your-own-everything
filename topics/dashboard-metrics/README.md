---
title: "Dashboard Metrics"
category: "distributed-data"
difficulty: "beginner"
tags: [metrics, monitoring, observability]
related: [log-aggregator, metrics-monitor, distributed-tracer]
---

# Dashboard Metrics

"How many requests per second are we serving, and is the p99 latency okay?" Every production system answers this with metrics: numbers scraped, aggregated, and graphed on dashboards. Building the pipeline yourself — instrumentation, storage, querying, alerting — teaches you what those graphs actually mean and why averages lie.

## Core concepts

- **Counters** — Monotonically increasing values (requests served, bytes sent). The fundamental metric type; rates are derived by differencing over time. Never use a counter for something that can go down.
- **Gauges** — Point-in-time values that go up and down (queue depth, active connections, temperature). Simple, but averaging a gauge across time can mislead if the sampling is uneven.
- **Histograms / summaries** — Distributions of observations (request latencies). Histograms bucket values so you can compute quantiles later; this is how you get p50/p99 without storing every sample.
- **Why averages lie** — A 100ms average latency can hide 1% of users waiting 10 seconds. Percentiles (p99) describe the experience of actual users; dashboards that only show means are hiding the tail.
- **Pull vs push collection** — Prometheus scrapes targets on an interval (pull: targets just expose `/metrics`); StatsD-style systems have apps push datagrams. Pull simplifies discovery and failure detection; push suits ephemeral jobs.
- **Time-series storage** — Metrics are (timestamp, labels, value) streams. Specialized TSDBs compress them brutally (delta-of-delta encoding, Gorilla-style) because the data is append-only and numeric — a general database would drown.
- **Labels / cardinality** — Key-value tags on every series (`method="GET", status="500"`). Labels make metrics sliceable — and dangerous: a label with a million values (user IDs) creates a million series and melts the TSDB. Cardinality budgeting is a core ops skill.

## How it works

Your application instruments code with a metrics library: increment a counter per request, observe latency into a histogram, set gauges for queue depth — each metric carrying labels. An exporter (or the app itself) serves these at an HTTP endpoint in a text format. Prometheus scrapes the endpoint every 15 seconds, appending samples to its TSDB with aggressive compression. A query language (PromQL) computes rates, ratios, and quantiles over time ranges: `rate(http_requests_total[5m])` or `histogram_quantile(0.99, ...)`. Grafana renders query results as dashboards, and an alert manager evaluates threshold rules ("p99 latency > 500ms for 10 minutes") and pages someone. Retention policies downsample old data so a year of history fits in reasonable disk.

## Build milestones

1. Build instrumentation: a tiny metrics library with counters, gauges, and histograms; instrument a toy web server and expose `/metrics` in Prometheus text format.
2. Build the scraper + TSDB: poll the endpoint every 15s, store (timestamp, labels, value) series in append-only segment files with delta encoding; verify the compression ratio vs raw floats.
3. Build a query engine: implement `rate()` over a time window and histogram quantile computation, served over a small HTTP API.
4. Build dashboards and alerts: a simple web UI graphing queries over time, plus alert rules evaluated on each scrape ("error rate > 1% for 5m") that log/page.
5. Impressive end state: instrument 3+ services, run a load test with an injected latency spike on one endpoint, and watch your dashboard show the p99 spike while the mean barely moves — with an alert firing, and a cardinality guard rejecting a mislabeled metric before it melts storage.

## Best resources

- [Prometheus](https://prometheus.io/) — The dominant open-source metrics system; its docs define the data model (counters, gauges, histograms, labels) the whole industry now uses.
- [Prometheus: introduction and overview](https://prometheus.io/docs/introduction/overview/) — The architecture doc: pull-based scraping, the TSDB, PromQL, and alerting, in one clear page.
- [Grafana](https://grafana.com/) — The dashboard layer; its docs teach visualization thinking — what to graph, how to template dashboards, and how alerts flow.
- [OpenTelemetry](https://opentelemetry.io/) — The vendor-neutral instrumentation standard for metrics, traces, and logs; the right way to instrument code so you're not locked to one backend.

## Stretch ideas

- Implement downsampling/rollups: keep raw 15s data for a week, 5-minute rollups for a month, hourly for a year — and query transparently across tiers.
- Add anomaly-based alerting: alert on sudden changes in the rate of change rather than static thresholds, cutting false pages.
