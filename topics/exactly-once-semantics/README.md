---
title: "Exactly-Once Semantics"
category: "distributed-data"
difficulty: "advanced"
tags: [streaming, kafka, delivery-guarantees]
related: [stream-processor, message-queue, workflow-engine]
---

# Exactly-Once Semantics

"At-most-once" loses data; "at-least-once" duplicates it; "exactly-once" — each record affecting the result precisely once, even across crashes — is the holy grail of stream processing. Building it teaches you why the guarantee is really a contract between producer, processor, and sink, and why idempotence plus transactions are the only honest way to get there.

## Core concepts

- **The three delivery semantics** — At-most-once (may lose, never duplicate), at-least-once (never lose, may duplicate), exactly-once (the effect happens once). Most systems genuinely offer the first two; the third requires coordination across the whole pipeline.
- **Idempotent producer** — The broker deduplicates retried sends using a producer ID + sequence number per partition. A network timeout no longer risks a duplicate write, because the broker recognizes "I've seen sequence 42 from producer 7."
- **Transactions across partitions** — The producer can atomically commit a batch spanning multiple partitions (plus consumer offsets): either all of it is visible or none is. This is what makes "read → process → write" atomic.
- **End-to-end vs processing-only** — Exactly-once *within* the stream processor is achievable; exactly-once *end-to-end* additionally requires the sink to cooperate (idempotent writes or transactional sinks). A non-idempotent sink reintroduces duplicates no matter what the processor does.
- **The offset-commit atomicity problem** — The classic failure: process record, write result, crash before committing the offset → on restart the record is reprocessed and the result written twice. Transactions solve it by committing the offset and the output atomically.
- **Fencing zombie writers** — After a failover, the old producer might still be alive and writing. Epoch fencing (broker rejects writes from an older producer epoch) ensures only the current generation's writes land — the same idea as fencing tokens in distributed locks.
- **The cost** — Transactions add latency (commit markers, fencing) and throughput overhead. Many teams discover at-least-once plus idempotent sinks is cheaper and sufficient — exactly-once is a tool, not a virtue.

## How it works

Each producer gets a unique producer ID and epoch from the broker, and tags every batch with a sequence number; the broker keeps the last sequence per (producer, partition) and drops duplicates. For a stream processor doing read-process-write, the flow is: begin transaction, consume a batch of input, compute results, send results to output partitions, send the input offsets to the transaction, commit. The commit is atomic — downstream consumers with `read_committed` isolation see either the whole batch's outputs and offset advances, or nothing. On crash, the processor restarts, its new epoch fences the zombie, it re-reads from the last committed offset, and the idempotent producer plus transaction markers guarantee no record's effect is applied twice.

## Build milestones

1. Build the failure demo: a naive consumer that processes, writes results to a file, then commits offsets — kill it between write and commit and show the duplicate on restart.
2. Add an idempotent producer: sequence numbers per partition, broker-side dedup table, and proof that retried sends don't duplicate.
3. Add transactions: begin/commit/abort spanning multiple output partitions plus offset commits; show a crashed-then-recovered run producing exactly the same output file as a clean run.
4. Add zombie fencing: start a second producer instance with the same ID, bump the epoch, and show the old instance's writes being rejected by the broker.
5. Impressive end state: a mini stream processor (word counts over an input log) with transactional read-process-write into an output log, chaos-tested with random kills — output verified byte-identical to a failure-free run, with latency/throughput numbers showing what the guarantee costs.

## Best resources

- [Exactly-once Semantics Are Possible: Here's How Kafka Does It — Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/) — Written by the engineers who built it: idempotent producer, transactions, and the real costs, explained clearly.
- [KIP-98: Exactly Once Delivery and Transactional Messaging](https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging) — The original design proposal; the best deep technical reference for the protocol mechanics.
- [Message Delivery Semantics — Apache Kafka docs](https://kafka.apache.org/documentation/#semantics) — The official definitions of at-most/at-least/exactly-once and exactly where each guarantee is won or lost.
- [Idempotence Is Not a Medical Condition — Pat Helland (ACM)](https://dl.acm.org/doi/10.1145/2160718.2160734) — The classic essay on why idempotence is the fundamental building block, and why "exactly once" is often the wrong goal.

## Stretch ideas

- Implement a transactional sink to an external database (write results + offsets in one DB transaction) and prove end-to-end exactly-once across system boundaries.
- Benchmark the overhead: measure throughput and p99 latency with transactions on vs off, and find the batch size where the cost becomes acceptable.
