---
title: "HTTP/2 Framing"
category: "networking"
difficulty: "advanced"
tags: [http2, framing, multiplexing]
related: [http-protocol-deep-dive, quic-basics, grpc-service, websocket-server]
---

# HTTP/2 Framing

HTTP/2 keeps HTTP's semantics but replaces the text wire format with binary frames multiplexed over one connection — the fix for HTTP/1.1's head-of-line blocking and chatty handshakes. Implementing the framing layer yourself (frames, HPACK, flow control) teaches how protocols encode multiplexing, and it's the direct prerequisite for understanding gRPC and HTTP/3.

## Core concepts

- **Binary framing layer** — Everything is a frame: 9-byte header (24-bit length, 8-bit type, 8-bit flags, 31-bit stream ID) + payload. Text parsing bugs become impossible; a frame parser is a small state machine.
- **Streams and multiplexing** — Each request/response is a stream with an ID; frames from many streams interleave on one TCP connection. One connection per origin replaces HTTP/1.1's connection-per-request waste.
- **Frame types** — DATA (body bytes), HEADERS (HPACK-compressed headers), PRIORITY, RST_STREAM (abort one stream), SETTINGS (connection parameters), PUSH_PROMISE (server push), PING, GOAWAY (graceful shutdown), WINDOW_UPDATE, CONTINUATION.
- **HPACK header compression** — Headers are compressed with HPACK: indexed static/dynamic tables plus Huffman coding. The dynamic table is connection-scoped state both sides must keep in sync — the trickiest part to get right.
- **Flow control** — Two-level windows: per-stream and per-connection. Senders must not exceed the receiver's advertised window; WINDOW_UPDATE frames reopen it. This is backpressure built into the protocol.
- **Stream states** — Idle → open → half-closed → closed, with reserved states for server push. Sending a frame in the wrong state is a connection error — the state machine is the spec's core.
- **Prioritization** — Streams carry weights and dependencies forming a priority tree, letting browsers say "CSS before images". Widely implemented, rarely effective — a fun case study in spec vs reality.

## How it works

The connection starts with the HTTP/2 preface (magic string + SETTINGS frame); both sides exchange SETTINGS to agree on parameters like max frame size and header table size. Each request opens a stream: the client sends HEADERS (HPACK-encoded `:method`, `:path`, etc.) then DATA frames; the server replies with its own HEADERS+DATA on the same stream ID. Frames for different streams interleave freely, flow-control windows gate how much DATA can be in flight, and HPACK's dynamic table evolves as headers repeat. GOAWAY with the last-processed stream ID shuts down gracefully.

## Build milestones

1. Write a frame parser: read the 9-byte header, dispatch on type, and pretty-print frames from a real HTTP/2 session (capture with Wireshark or nghttp).
2. Implement the connection preface and SETTINGS exchange against a real server (e.g., nghttpd); keep the connection alive with PING.
3. Decode HEADERS with a minimal HPACK implementation: static table lookups, then indexed dynamic-table entries.
4. Build a client that opens multiple concurrent streams, interleaves requests, and reassembles each response — demonstrating multiplexing over one connection.
5. Add flow control: honor incoming WINDOW_UPDATEs, send your own, and handle RST_STREAM/GOAWAY gracefully.

## Best resources

- [RFC 9113 — HTTP/2](https://www.rfc-editor.org/rfc/rfc9113) — the protocol spec: framing, streams, and the state machine.
- [RFC 9114 — QPACK is the HTTP/3 variant; HPACK lives in RFC 7541](https://www.rfc-editor.org/rfc/rfc7541) — the HPACK compression spec: tables, indexing, and Huffman coding.
- [http2-explained (Daniel Stenberg)](https://daniel.haxx.se/http2/) — the beloved free book on HTTP/2's background and design.
- [nghttp2](https://nghttp2.org/) — the reference C implementation plus `nghttp`/`nghttpd` tools for generating test traffic.

## Stretch ideas

- Implement server push (PUSH_PROMISE) and measure whether it actually helps page-load time on your test site.
- Write a frame-level fuzzer that feeds malformed frames to your parser and to nghttpd, comparing error handling.
