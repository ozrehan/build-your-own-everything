---
title: "Pub/Sub Broker"
category: "networking"
difficulty: "intermediate"
tags: [pubsub, messaging, realtime]
related: [message-queue, websocket-server, notification-fanout, crdt-collaborative-text]
---

# Pub/Sub Broker

A pub/sub broker routes messages by topic: publishers fire into named channels, and every subscriber gets a copy — nobody knows about anybody else. It's the backbone of chat systems, live updates, and IoT telemetry, and building one teaches fan-out, wildcard matching, and the delivery guarantees that separate toys from infrastructure.

## Core concepts

- **Topics and subscriptions** — Publishers send to topic names like `sensors/kitchen/temp`; subscribers register interest and receive matching messages. Neither side addresses the other directly — the broker is the rendezvous point.
- **Fan-out** — One published message becomes N deliveries. The broker's core loop is a fast topic→subscriber lookup plus per-subscriber queues; slow subscribers must never block fast ones.
- **Wildcard matching** — MQTT-style `+` (single level) and `#` (multi-level) let one subscription cover `sensors/+/temp`. Efficient matching (trie over topic levels) matters once you have thousands of subscriptions.
- **Retained messages** — The broker keeps the last message per topic and delivers it immediately to new subscribers — how late joiners get current state (like "last known temperature") without waiting.
- **QoS levels** — MQTT's 0 (fire and forget), 1 (at-least-once with ACKs), and 2 (exactly-once via 4-step handshake). Each level is a different state machine per message per subscriber.
- **Presence** — Tracking who's online/offline (MQTT's Last Will lets a client declare a message published automatically on unexpected disconnect) turns a broker into a presence system.
- **Slow-subscriber backpressure** — A subscriber that can't keep up forces a choice: buffer unboundedly (OOM), drop messages, or disconnect it. Every production broker picks one explicitly.

## How it works

Clients connect and send SUBSCRIBE/UNSUBSCRIBE/PUBLISH commands over your wire protocol. The broker maintains a topic trie mapping to subscriber lists; on PUBLISH it walks the trie (including wildcard matches), appends the message to each matched subscriber's outbound queue, and a per-connection writer loop flushes those queues. QoS 1 adds per-message ACK tracking with redelivery timers; retained topics store the latest payload for instant delivery to new subscribers; heartbeats detect dead connections so their subscriptions can be cleaned up.

## Build milestones

1. Build a TCP broker with a text protocol (SUB/UNSUB/PUB); fan out published messages to all matching subscribers.
2. Add MQTT-style topic wildcards (`+`/`#`) with a trie-based matcher and retained messages for late joiners.
3. Implement QoS 1: per-message ACKs, redelivery on timeout, and session resume across reconnects.
4. Add a WebSocket gateway so browser clients can publish/subscribe, plus presence tracking (who's online per topic).
5. Persist subscriptions and retained messages so the broker survives restarts without losing state.

## Best resources

- [MQTT.org](https://mqtt.org/) — the home of MQTT, the dominant pub/sub wire protocol; start with the spec overview and FAQ.
- [NATS publish-subscribe guide](https://docs.nats.io/concepts/pub-sub-basics) — how subject-based messaging, wildcards, and queue groups work in a modern broker.
- [Redis Pub/Sub documentation](https://redis.io/docs/manual/pubsub/) — channels, pattern subscriptions, and sharded pub/sub; the simplest production reference.
- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) — the HTTP-native way to push topic updates to browsers; a great gateway transport for your broker.

## Stretch ideas

- Implement the MQTT 3.1.1 CONNECT/PUBLISH/SUBSCRIBE wire subset so real MQTT clients (mosquitto_pub/sub) work against your broker.
- Cluster two brokers with gossip-based subscription sync and measure fan-out latency across the cluster.
