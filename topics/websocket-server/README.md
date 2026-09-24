---
title: "WebSocket Server"
category: "networking"
difficulty: "intermediate"
tags: [websocket, realtime, protocol]
related: [websocket-chat, http-protocol-deep-dive, pubsub-broker, netcode-rollback]
---

# WebSocket Server

WebSockets upgrade an ordinary HTTP connection into a persistent, bidirectional, message-oriented channel — the foundation of chat apps, live dashboards, and multiplayer games. Implementing the handshake and framing yourself demystifies the "magic" and shows exactly what libraries like Socket.IO add on top.

## Core concepts

- **HTTP Upgrade handshake** — The client sends a normal HTTP request with `Upgrade: websocket` and `Connection: Upgrade`; the server answers `101 Switching Protocols`. After that, HTTP is gone — the socket speaks WebSocket frames.
- **Sec-WebSocket-Accept** — The server proves it understood the handshake by hashing the client's `Sec-WebSocket-Key` with the magic GUID `258EAFA5-E914-47DA-95CA-C5AB0DC85B11` (SHA-1, then base64). It's not security, just a protocol-version check.
- **Frame format** — Every message is wrapped in frames: a FIN bit, a 4-bit opcode, a mask bit, a 7/16/64-bit payload length, an optional 4-byte masking key, then payload. Parsing this bit-level format is the core of the project.
- **Masking** — Client-to-server frames MUST be masked with a random 32-bit key (XORed per byte) to prevent cache-poisoning attacks through misbehaving proxies; server-to-client frames are never masked.
- **Opcodes** — `0x1` text, `0x2` binary, `0x8` close, `0x9` ping, `0xA` pong, `0x0` continuation. Control frames (close/ping/pong) can arrive between fragments of a data message.
- **Fragmentation** — A large message may be split across frames (first frame has the opcode, the rest use continuation `0x0`, last has FIN). Your server must reassemble before delivering.
- **Ping/pong heartbeats** — Either side can ping; the peer must pong promptly. This is how servers detect dead connections and keep idle NAT mappings alive.

## How it works

1. Your TCP server reads the client's HTTP upgrade request, extracts `Sec-WebSocket-Key`, computes the accept hash, and replies with `101 Switching Protocols`.
2. From then on you read frames: parse the 2-byte header, read the extended length if present, read the 4-byte mask, unmask the payload byte-by-byte.
3. To send, you build frames yourself — FIN + opcode `0x1`, no mask bit, length encoding — and write them to the socket.
4. You handle control frames inline (reply pong to ping, echo close and tear down), reassemble fragmented messages, and route complete messages to your application logic, e.g. broadcasting chat lines to all connected clients.

## Build milestones

1. Accept a TCP connection, complete the HTTP upgrade handshake, and verify it with `new WebSocket()` in a browser console.
2. Parse incoming masked text frames and print messages; handle the 16-bit and 64-bit extended length forms.
3. Send unmasked frames back to build an echo server; confirm round-trip in the browser.
4. Implement ping/pong, the close handshake, and fragmented-message reassembly.
5. Run many concurrent clients with a broadcast loop — a working multi-user chat room over raw sockets.

## Best resources

- [RFC 6455 — The WebSocket Protocol](https://www.rfc-editor.org/rfc/rfc6455) — the complete spec: handshake, framing, masking, and close semantics.
- [MDN: The WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) — how the client side behaves, which is what your server must satisfy.
- [MDN: Writing a WebSocket server](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_server) — a walkthrough of the handshake and framing in multiple languages.
- [High Performance Browser Networking: WebSocket](https://hpbn.co/websocket/) — why WebSockets exist, framing overhead, and performance characteristics.
- [Socket.IO docs](https://socket.io/docs/v4/) — shows what a full-featured layer (rooms, fallbacks, reconnection) adds over raw WebSockets.
- [Autobahn Testsuite](https://github.com/crossbario/autobahn-testsuite) — the standard compliance test suite; run your server against it to find framing bugs.

## Stretch ideas

- Add `permessage-deflate` compression negotiation and measure the bandwidth win on JSON payloads.
- Layer TLS (wss) in front and add subprotocol negotiation (`Sec-WebSocket-Protocol`) for versioned APIs.
