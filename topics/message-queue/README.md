---
title: "Message Queue"
category: "networking"
difficulty: "intermediate"
tags: [queue, messaging, async]
related: [pubsub-broker, stream-processor, notification-fanout, exactly-once-semantics]
---

# Message Queue

A message queue decouples producers from consumers in time: senders drop messages in and move on; workers pick them up at their own pace, with retries when things fail. Building one from scratch teaches the delivery guarantees, persistence, and failure modes that every "just use RabbitMQ" decision is secretly about.

## Core concepts

- **Producer/consumer decoupling** — Queues separate *when* work is created from *when* it's processed, absorbing bursts and letting producers and consumers scale and deploy independently.
- **Queues vs topics** — A queue delivers each message to exactly one consumer (work distribution); a topic/exchange fans out to many subscribers. Mixing them up is the most common messaging design error.
- **Delivery semantics** — At-most-once (may lose), at-least-once (may duplicate — the practical default), exactly-once (requires idempotent consumers or transactions; much harder than it sounds).
- **ACKs and redelivery** — Consumers acknowledge each message; unacked messages (crashed worker, timeout) go back to the queue after a visibility timeout. This single mechanism is what makes at-least-once work.
- **Durability** — Messages must survive broker restarts: append to a write-ahead log and fsync before acknowledging the producer. "Durable" without fsync is a lie told at high speed.
- **Dead-letter queues** — Messages that fail repeatedly (poison messages) get moved aside instead of blocking the queue forever; operators inspect and replay them later.
- **Backpressure** — When producers outrun consumers, the broker must push back (block, reject, or spill to disk) rather than grow memory until it dies.

## How it works

Producers connect over TCP and publish messages to named queues using a small framing protocol. The broker appends each message to a persistent log, then dispatches to connected consumers — tracking per-message state: queued → delivered (awaiting ACK) → acked, or back to queued when the visibility timeout fires without an ACK. Consumers that crash simply never ACK, so their messages are redelivered to someone else. A background sweeper enforces TTLs and routes exhausted messages to the dead-letter queue, and flow-control signals tell producers to slow down when depth grows.

## Build milestones

1. Build an in-memory FIFO queue over TCP with a tiny text protocol: one producer, one consumer, messages delivered in order.
2. Add ACKs and redelivery: unacknowledged messages return to the queue after a timeout (at-least-once delivery).
3. Make it durable: append messages to a file with fsync, replay the log on restart without losing or duplicating.
4. Support multiple named queues, competing consumers on one queue, and a dead-letter queue for poison messages.
5. Add delayed delivery and per-message TTLs, plus a stats endpoint showing depth, rates, and redelivery counts.

## Best resources

- [RabbitMQ Tutorials](https://www.rabbitmq.com/tutorials) — the classic six-tutorial progression (hello world → work queues → pub/sub → routing → topics → RPC) that maps exactly onto what you're building.
- [ZeroMQ: The Guide](https://zguide.zeromq.org/) — Pieter Hintjens' free book on messaging patterns; the chapters on reliability patterns are gold for queue design.
- [NATS documentation](https://docs.nats.io/) — core NATS (at-most-once) vs JetStream (persistent streams) shows the same queue idea at two delivery guarantees.
- [nats-server](https://github.com/nats-io/nats-server) — a clean, readable Go implementation of a messaging server to study once yours works.

## Stretch ideas

- Implement AMQP 0-9-1 wire-protocol compatibility for a subset (enough for a real RabbitMQ client library to connect).
- Add consumer groups with partition-key ordering and benchmark throughput against RabbitMQ on the same workload.
