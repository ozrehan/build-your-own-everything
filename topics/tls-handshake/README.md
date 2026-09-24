---
title: "TLS Handshake"
category: "security"
difficulty: "advanced"
tags: [tls, networking, cryptography]
related: [certificate-authority, vpn-client, http-protocol-deep-dive]
---

# TLS Handshake

The TLS handshake is the few-millisecond negotiation that turns a raw TCP connection into an authenticated, encrypted channel before any HTTP is spoken. Reimplementing it yourself — parsing ClientHello, doing the key exchange, deriving session keys — is the single best way to truly understand what "the padlock" is actually doing.

## Core concepts

- **ClientHello / ServerHello** — The opening messages where the client advertises supported TLS versions, cipher suites, and a random nonce, and the server picks one combination both sides support.
- **Key exchange** — The mechanism (ECDHE in modern TLS) by which both sides derive the same session keys without ever transmitting them, using ephemeral Diffie-Hellman so each session gets fresh keys.
- **Forward secrecy** — The property that compromising a server's long-term private key does not let an attacker decrypt past captured traffic, because session keys were never derived from that key.
- **Certificate authentication** — The server proves its identity by presenting an X.509 certificate chain the client validates up to a trusted root; without this step, encryption alone cannot stop a man-in-the-middle.
- **Cipher suite negotiation** — The agreed combination of key exchange, authentication, bulk cipher, and MAC (e.g., TLS_AES_128_GCM_SHA256), which defines exactly how data will be protected.
- **Session resumption** — Skipping the full handshake on reconnect using session tickets or pre-shared keys (PSK), cutting latency and CPU cost for repeat visits.
- **TLS 1.3 vs 1.2** — 1.3 collapses the handshake to one round trip, removes legacy primitives (RSA key transport, CBC cipher suites), and encrypts the certificate, fixing whole classes of 1.2-era attacks.

## How it works

In TLS 1.3, the client sends a ClientHello containing a random nonce, its supported cipher suites, and — crucially — its ephemeral Diffie-Hellman public share up front, guessing the group the server will pick. The server responds with ServerHello (its own DH share, chosen cipher suite), then immediately sends its encrypted certificate and a Finished message whose MAC is computed over the whole transcript with keys derived from the shared secret. The client validates the certificate chain, verifies the transcript MAC, and both sides now hold identical traffic keys.

From the shared DH secret, both sides run HKDF (a key-derivation function) to stretch it into distinct keys: one for encrypting the handshake itself, then separate client→server and server→client application keys, with fresh keys derived per record batch. Every byte of application data afterwards is encrypted with AEAD (authenticated encryption), so tampering is detected and ordering is protected.

## Build milestones

1. Write a parser that decodes a captured ClientHello/ServerHello from a pcap into its fields (version, random, session ID, cipher suites, extensions).
2. Implement the TLS 1.3 key schedule: take an X25519 shared secret and derive handshake and application traffic keys with HKDF exactly per the RFC.
3. Build a minimal TLS 1.3 client that completes a handshake against a real server (e.g., example.com) and decrypts the server's certificate message.
4. Add certificate chain validation: parse X.509, check signatures up to a trusted root, verify hostname and expiry.
5. Send an HTTP request over your own encrypted records and read the response — a from-scratch HTTPS fetch with no TLS library.

## Best resources

- [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446.html) — The authoritative spec; dense but the key schedule sections are precise and complete.
- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/) — Every byte of a real TLS 1.3 handshake explained with diagrams; the best visual companion to the RFC.
- [RFC 5246 — TLS Version 1.2](https://www.rfc-editor.org/rfc/rfc5246) — Worth reading after 1.3 to understand what changed and why (and what still runs in the wild).
- [What is SSL/TLS? — Cloudflare Learning Center](https://www.cloudflare.com/learning/ssl/what-is-ssl/) — A plain-language overview of certificates, handshakes, and how TLS fits into the web stack.
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) — Shows which protocol versions and cipher suites are considered modern/intermediate/old, with generated configs.

## Stretch ideas

- Implement session resumption with PSK tickets and measure the latency savings on reconnects.
- Add a packet-dissector mode that takes a pcap and prints a human-readable transcript of every TLS record.
