---
title: "Stream Processor"
category: "distributed-data"
difficulty: "intermediate"
tags: [stream-processing, real-time, event-driven]
related: [message-queue, exactly-once-semantics, dashboard-metrics]
---

# Stream Processor

Batch jobs answer questions about yesterday; stream processors answer questions about right now — fraud detection, live dashboards, per-user sessionization. Building one teaches you the two hard problems of streaming: what "time" means when events arrive late, and how to keep state correct when machines fail mid-stream.

## Core concepts

- **Event time vs processing time** — Event time is when the thing actually happened (embedded in the event); processing time is when your system sees it. Mixing them up is the source of nearly every streaming bug, because networks delay and reorder events.
- **Watermarks** — A watermark is the system's best guess that "no events older than time T will arrive." It lets a streaming job close a time window and emit results while tolerating late data up to a bound.
- **Windows** — Bounded chunks of an unbounded stream: tumbling (non-overlapping, e.g. every minute), sliding (overlapping), and session windows (grouped by gaps of inactivity). Almost every streaming query is "aggregate something per window."
- **State** — Running aggregates (counts, sums, session tables) that live inside the processor between events. State must survive crashes, which means it has to be checkpointed, not just kept in memory.
- **Checkpoints / savepoints** — Periodic snapshots of operator state plus the input positions (offsets) consumed so far. On failure the job restarts from the last checkpoint instead of from the beginning of time.
- **At-least-once vs exactly-once** — Without care, a crash between "emit result" and "checkpoint" causes duplicates. True exactly-once requires the sink to participate (idempotent writes or transactions), not just the processor.
- **Backpressure** — When input arrives faster than the job can process, the system must slow the source rather than buffer unboundedly and run out of memory. A real streaming engine propagates pressure upstream automatically.

## How it works

Events flow from a log (like Kafka partitions) into operators arranged as a dataflow graph. Each operator holds keyed state — e.g. "per-user click counts" — and processes events in event-time order as far as watermarks allow. Periodically, the system injects checkpoint barriers into the stream; when a barrier has passed through every operator, each one snapshots its state and records how far it has read, giving a globally consistent recovery point. Windows are just a special case of state: a tumbling 1-minute window buffers events per key until the watermark passes the window end, then fires the aggregate downstream. Sinks write results with idempotent keys or two-phase commits so a replayed checkpoint doesn't double-count.

## Build milestones

1. Build a single-threaded event pipeline: read JSON events from a file, maintain per-key counts in a dictionary, and print results — a stream processor with no distribution, just the core loop.
2. Add tumbling windows on event time: parse timestamps from events, bucket them into 1-minute windows, and emit each window's aggregate when you decide it is complete.
3. Add watermarks and late-data handling: track the max event time seen, close windows when the watermark passes them, and route late events to a side output instead of silently corrupting results.
4. Add durable state with checkpoints: snapshot your per-key state and input offset to disk every N events; kill the process mid-run and resume exactly where it left off.
5. Impressive end state: run two parallel workers splitting keys by hash (like real partitioned streaming), each checkpointing independently, with a sink that deduplicates on replay so end-to-end results are exactly-once.

## Best resources

- [Stream processing — Wikipedia](https://en.wikipedia.org/wiki/Stream_processing) — Good grounding in the concepts: windows, state, and how streaming differs from batch.
- [Apache Flink](https://flink.apache.org/) — The reference open-source stream processor; its documentation is the best practical explanation of watermarks, checkpoints, and exactly-once.
- [Kafka Streams documentation](https://kafka.apache.org/documentation/streams/) — Shows the "streaming as a library" approach and how tables, joins, and state stores map onto Kafka topics.
- [Apache Kafka](https://kafka.apache.org/) — The durable event log most stream processors read from; understanding partitions and offsets is prerequisite to understanding streaming recovery.

## Stretch ideas

- Implement session windows (group events by user with a 30-minute inactivity gap) and compare their state cost against tumbling windows.
- Add a simple SQL layer: parse `SELECT count(*) FROM events WINDOW TUMBLING(1 MINUTE)` and compile it to your operator graph.
