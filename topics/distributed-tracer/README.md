---
title: "Distributed Tracer"
category: "devops-infra"
difficulty: "advanced"
tags: [tracing, observability, opentelemetry]
related: [log-aggregator, metrics-monitor, service-mesh-sidecar]
---

# Distributed Tracer

A slow request crosses five services, and each one's logs look fine. A distributed tracer stitches those hops into one picture: a tree of spans showing exactly where the milliseconds went. Building one — instrumentation SDK, context propagation, a collector, and a waterfall UI — teaches you the hardest part of observability: joining causally related events across process boundaries with nothing but IDs passed in headers.

## Core concepts

- **Traces, spans, and parentage** — a trace is one end-to-end operation with a shared `trace_id`; each unit of work (HTTP handler, DB query) is a span with its own `span_id`, a `parent_span_id`, start/end timestamps, and attributes. The spans form a causal tree.
- **Context propagation** — the trace context travels across process boundaries in headers (W3C `traceparent`: `version-trace_id-parent_span_id-flags`). Every client library must inject it on egress and extract it on ingress, or the tree breaks.
- **Sampling** — you cannot store every trace at scale. Head-based sampling decides at trace start (e.g. keep 1%, always keep errors); tail-based sampling decides after seeing the whole trace (keep all slow/error traces). The choice determines what questions you can answer later.
- **Instrumentation: manual vs automatic** — manual SDK calls (`tracer.start_span("db.query")`) give precise control; auto-instrumentation (bytecode weaving, monkey-patching HTTP clients) covers everything with zero code changes but needs per-framework plugins.
- **Collector pipeline** — agents on each host batch spans and forward to collectors that validate, tail-sample, and write to storage. Batching and backpressure handling are what keep tracing overhead under ~1% CPU.
- **Span storage and indexing** — spans are indexed by trace ID (for retrieval) and by service/operation/duration (for search: "slowest traces for /checkout yesterday"). Columnar stores work well; retention is short because traces are huge.
- **Critical path analysis** — the waterfall UI isn't just pretty: the critical path (the chain of spans whose durations sum to the total) is what actually determines latency, and async spans off that path are noise for performance work.

## How it works

An instrumented service creates a root span for each incoming request, generating a random 128-bit `trace_id` (or extracting one from the `traceparent` header). Child spans are created for downstream calls; before each outbound HTTP/gRPC call, the SDK injects the current trace and span IDs into headers. Each span records its timing and attributes, and on completion is handed to a batching exporter that ships spans to the collector over OTLP/gRPC.

The collector receives batches, applies tail-sampling policies (keep errors, keep p99-latency traces, drop the rest), and writes spans to storage indexed by trace ID. The query API fetches all spans for a trace ID, reconstructs the tree by parent links, computes each span's self-time (duration minus children), and renders the waterfall. A service-map view aggregates parent→child service pairs across traces to show the real dependency graph.

## Build milestones

1. Build an SDK in one language: `start_span`/`end_span`, W3C `traceparent` inject/extract on HTTP calls, and a stdout exporter. Trace a request across two services and print the tree.
2. Add a collector service that receives OTLP-style batches over HTTP, stores spans in SQLite indexed by trace ID, and serves a waterfall UI for any trace.
3. Implement head-based sampling (probabilistic + always-sample-errors), batching with flush-on-interval/size, and auto-instrumentation for one HTTP framework.
4. Add tail-based sampling, a trace search API (by service, operation, min duration), and a service dependency map — then measure the overhead your SDK adds per request.

## Best resources

- [OpenTelemetry documentation](https://opentelemetry.io/docs/) — the standard for traces, metrics, and logs: data model, context propagation, SDK and collector architecture. Your primary spec.
- [Sigelman et al. — Dapper (2010)](https://research.google/pubs/pub36356/) — Google's paper that invented distributed tracing: annotations, sampling, and the famous "keep overhead negligible" design constraints.
- [Jaeger documentation](https://www.jaegertracing.io/docs/) — the CNCF tracer: agent/collector/query architecture, storage backends, and adaptive sampling; the reference implementation to study.
- [W3C Trace Context](https://www.w3.org/TR/trace-context/) — the `traceparent`/`tracestate` header spec; short, precise, and exactly what your propagation code must implement.
- [Zipkin](https://zipkin.io/) — the original open-source tracer from Twitter; its data model docs are the clearest explanation of span structure anywhere.

## Stretch ideas

- Implement continuous profiling correlation: attach profile IDs to spans so a slow span links to the CPU flame graph of that exact moment.
- Build span-to-logs correlation: inject trace/span IDs into your log aggregator so each log line links to its trace and vice versa.
- Add trace-derived RED metrics: compute per-service rate/error/duration dashboards purely from span data, no separate metrics pipeline needed.
