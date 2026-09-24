---
title: "VPN Client"
category: "security"
difficulty: "advanced"
tags: [vpn, networking, tunneling]
related: [vpn-wireguard-basics, tls-handshake, nat-traversal]
---

# VPN Client

A VPN client builds an encrypted tunnel from your device to a trusted endpoint, so traffic crossing hostile networks (coffee-shop Wi-Fi, ISPs) is confidential and authenticated. Building one yourself — the handshake, the tunnel interface, the crypto — teaches you exactly what commercial VPN apps are doing under the hood.

## Core concepts

- **Tunneling** — Encapsulating packets of one protocol inside another: your original IP packet becomes the encrypted payload of an outer UDP packet addressed to the VPN server.
- **TUN/TAP interfaces** — Virtual network interfaces the OS treats like real NICs; your client reads plaintext packets from the TUN device, encrypts them, and sends them down the tunnel.
- **Handshake and key exchange** — The initial authenticated exchange (Noise protocol in WireGuard, TLS in OpenVPN) that establishes session keys and proves the server's identity before any data flows.
- **Perfect forward secrecy** — Session keys are ephemeral and rotated, so a later key compromise doesn't decrypt previously captured tunnel traffic.
- **Split vs. full tunnel** — Full tunnel routes all traffic through the VPN; split tunnel routes only selected subnets, leaving the rest direct — a tradeoff between privacy and performance.
- **Kill switch** — Firewall rules that block all non-VPN traffic, so if the tunnel drops, packets can't silently leak onto the raw network.
- **Authentication of the server** — The client must verify it's talking to the real VPN server (via pre-shared keys or certificates); without this, the "encrypted" tunnel may terminate at an attacker's box.

## How it works

Using WireGuard as the model: each side has a static Curve25519 keypair, and peers are identified by public key. The handshake is a 1-RTT Noise_IK exchange — the initiator sends an ephemeral public key encrypted to the responder's static key, the responder replies with its own ephemeral, and both derive symmetric session keys via HKDF. After that, data packets are just ChaCha20-Poly1305-encrypted IP packets with a small header, sent over UDP; keys rotate every couple of minutes via a lightweight re-handshake.

Your client creates a TUN interface, assigns it an address, installs routes directing traffic into it, and runs the crypto loop: read packet from TUN → encrypt with current sending key → UDP to server, and the reverse for inbound. Building this against a real WireGuard server (or two of your own endpoints) makes tunneling, routing, and key rotation completely concrete.

## Build milestones

1. Build a toy UDP tunnel: TUN interface on each end, plaintext packets forwarded between them, verifying ping works through the tunnel.
2. Add the WireGuard handshake: implement Noise_IK with X25519, HKDF, and ChaCha20-Poly1305 to derive session keys with a peer.
3. Add data-plane encryption: encrypt/decrypt tunnel packets with rotating keys and anti-replay counters.
4. Add routing control: full-tunnel default route plus a kill-switch firewall rule that blocks leaks if the tunnel dies.
5. Interoperate with the real WireGuard implementation: handshake your client against a standard wg server.

## Best resources

- [WireGuard whitepaper](https://www.wireguard.com/papers/wireguard.pdf) — The protocol spec: Noise handshake, key rotation, and design rationale, all in one tight paper.
- [WireGuard Quick Start](https://www.wireguard.com/quickstart/) — Practical setup of interfaces, keys, and peers; the lab companion to the paper.
- [RFC 7296 — IKEv2](https://www.rfc-editor.org/rfc/rfc7296) — The key-exchange protocol behind IPsec VPNs; read after WireGuard to compare approaches.
- [OpenVPN source](https://github.com/OpenVPN/openvpn) — The TLS-based VPN approach; study its auth and tunnel setup as the alternative design.

## Stretch ideas

- Add a WireGuard-compatible roaming: keep the tunnel alive across network changes (Wi-Fi to cellular) using the protocol's built-in mobility.
- Build a minimal VPN server with multi-user key management, per-peer bandwidth accounting, and config generation.
