---
title: "WebSocket Chat App"
category: "web-development"
difficulty: "intermediate"
tags: [websocket, realtime, chat]
related: [websocket-server, webrtc-video-chat, jwt-auth, notification-fanout]
---

# WebSocket Chat App

A WebSocket chat app keeps a persistent two-way connection between browser and server so messages arrive instantly, no polling needed. Building one — handshake, rooms, presence, reconnection — teaches real-time system fundamentals: connection lifecycle, message framing, and how to scale stateful servers.

## Core concepts

- **The WebSocket handshake** — An HTTP request with `Upgrade: websocket` and a `Sec-WebSocket-Key`; the server answers `101 Switching Protocols` and the TCP connection becomes a message-oriented channel.
- **Frames and masking** — Messages travel as frames with opcodes (text, binary, ping, close); clients must mask payloads (a simple XOR) — a protocol requirement your server must enforce.
- **Rooms and pub/sub** — The server tracks which sockets belong to which room and fans each message out to room members; rooms are just sets of connections with join/leave semantics.
- **Presence** — Tracking who's online via heartbeat pings and disconnect cleanup; presence state is ephemeral and must tolerate abrupt disconnects.
- **Reconnection and message replay** — Networks drop; clients should reconnect with backoff and the server should replay missed messages using per-room sequence numbers.
- **Horizontal scaling problem** — With multiple server instances, a socket on server A can't reach a room member on server B — solved with a shared pub/sub backbone (Redis) between instances.
- **Backpressure** — If a client can't keep up, the server must bound per-socket queues and eventually drop or disconnect slow consumers instead of buffering forever.
- **Socket.IO vs raw WebSockets** — Socket.IO adds rooms, auto-reconnect, and fallbacks on top of WebSocket; building raw first teaches what the abstraction buys you.

## How it works

1. The browser opens a WebSocket to your server; the handshake upgrades the HTTP connection.
2. The client sends a `join` message; the server adds the socket to the room's set and broadcasts presence updates.
3. Chat messages are framed, broadcast to room members, persisted with sequence numbers, and acked.
4. On disconnect the server cleans up presence; the client reconnects with backoff and requests missed messages since its last sequence number.

## Build milestones

1. A raw WebSocket echo server (Node `ws` or hand-rolled handshake) plus a browser page that sends/receives — live in an evening.
2. Add rooms: join/leave, room-scoped broadcast, and a simple message protocol (JSON with `type` fields).
3. Add usernames, presence (who's online), typing indicators, and message history from SQLite.
4. Add reconnection with exponential backoff, sequence-number-based replay of missed messages, and heartbeats.
5. Scale: put Redis pub/sub between two server instances and load-balance sockets across them.

## Best resources

- [RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455) — the protocol spec: handshake, framing, masking, close codes.
- [WebSocket API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) — the browser-side API reference.
- [ws — Node WebSocket library](https://github.com/websockets/ws) — the standard server library; readable source for frame handling.
- [Socket.IO docs](https://socket.io/docs/v4/) — rooms, namespaces, and fallbacks; the pragmatic production layer.
- [Writing WebSocket servers — MDN](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers) — the server-side companion to the client API docs: handshake details, frame parsing, and masking, in one place.

## Stretch ideas

- Add end-to-end encrypted DMs using per-conversation keys exchanged out of band.
- Implement message reactions and threaded replies with an efficient fan-out design.
