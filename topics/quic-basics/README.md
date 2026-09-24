---
title: "QUIC Basics"
category: "networking"
difficulty: "advanced"
tags: [quic, udp, http3]
related: [http2-framing, tls-handshake, http-protocol-deep-dive, tcp-ip-stack-userspace]
---

# QUIC Basics

QUIC rebuilds TCP+TLS as a user-space protocol on top of UDP: encrypted-by-default, 1-RTT handshakes, and independent streams with no head-of-line blocking. It's what HTTP/3 runs on, and implementing even a slice of it teaches you why thirty years of TCP ossification made a clean-slate transport necessary.

## Core concepts

- **Why UDP** — Middleboxes and OS kernels made TCP unfixable: new TCP options get stripped, and kernel upgrades take years. QUIC puts everything in userspace over UDP so the transport can evolve like an app.
- **Packet number spaces** — QUIC keeps three separate packet-number spaces (Initial, Handshake, Application Data), each with its own encryption keys and loss recovery. This separation is what lets the handshake and data use different crypto cleanly.
- **Integrated TLS 1.3 handshake** — The QUIC handshake *is* a TLS 1.3 handshake carried in QUIC packets: 1-RTT to establish, optional 0-RTT resumption for repeat connections. There's no separate TCP-then-TLS phase.
- **Connection IDs and migration** — Connections are identified by connection IDs, not the 4-tuple. Your phone can switch from Wi-Fi to cellular mid-connection and QUIC just keeps going — impossible for TCP.
- **Streams without head-of-line blocking** — Like HTTP/2's streams but at the transport layer: loss on one stream doesn't stall the others, because retransmission and ordering are per-stream while the packet layer stays shared.
- **Loss detection and congestion control** — QUIC reimplements TCP's machinery (RACK-style loss detection, CUBIC/BBR congestion control) in userspace with better signals: no retransmission ambiguity, richer ACK frames, explicit ECN.
- **Version negotiation** — Endpoints that disagree on the QUIC version fall back gracefully via version-negotiation packets, so the protocol can keep evolving on the wire.

## How it works

A client sends an Initial packet (long header, destination connection ID, TLS ClientHello inside CRYPTO frames). The server may reply with a Retry for address validation, then both sides complete the TLS 1.3 handshake across the Initial and Handshake packet-number spaces, deriving 1-RTT keys. From there, short-header packets carry STREAM frames — each an independent byte stream with its own offsets — plus ACK frames, all encrypted with keys derived from the TLS handshake. Loss is detected per packet-number space and retransmitted data gets new packet numbers, eliminating TCP's retransmission ambiguity.

## Build milestones

1. Parse a captured QUIC Initial packet by hand: long header, connection IDs, and QUIC's variable-length integer encoding.
2. Run a QUIC echo server with quic-go or quiche; open multiple streams and observe that stalling one doesn't block the others (compare with TCP).
3. Demonstrate connection migration: change the client's source port mid-connection and watch the session survive.
4. Measure handshake latency for fresh vs resumed (0-RTT) connections and compare against TCP+TLS 1.3.
5. Capture a session and analyze it with qlog/Wireshark to see packet number spaces, ACK ranges, and loss recovery in action.

## Best resources

- [RFC 9000 — QUIC: A UDP-Based Multiplexed and Secure Transport](https://www.rfc-editor.org/rfc/rfc9000) — the transport spec: packets, streams, migration, and loss recovery.
- [RFC 9001 — Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001) — how the TLS 1.3 handshake is embedded and how packet protection keys are derived.
- [The Road to QUIC (Cloudflare)](https://blog.cloudflare.com/the-road-to-quic/) — the motivations and design tradeoffs, explained by the team that deployed it at scale.
- [quiche](https://github.com/cloudflare/quiche) — Cloudflare's Rust QUIC/HTTP3 implementation with a low-level packet API; ideal for experiments.
- [QUIC Working Group](https://quicwg.org/) — the IETF working group's hub: drafts, implementations, and interop test resources.
- [quic-go](https://github.com/quic-go/quic-go) — a pure-Go QUIC implementation with a friendly API for building clients and servers quickly.

## Stretch ideas

- Implement a minimal Initial-packet crafter and complete a handshake against a real server using only your code and a TLS library.
- Add qlog logging to your client and build a small visualization of stream multiplexing under packet loss.
