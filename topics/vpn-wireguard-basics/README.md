---
title: "VPN (WireGuard Basics)"
category: "networking"
difficulty: "intermediate"
tags: [vpn, wireguard, cryptography]
related: [nat-traversal, vpn-client, tls-handshake, packet-sniffer]
---

# VPN (WireGuard Basics)

WireGuard replaced sprawling VPN daemons with ~4,000 lines of principled cryptography: a TUN interface, a 1-RTT Noise handshake, and ChaCha20-Poly1305 transport. Rebuilding its core ideas yourself teaches modern applied crypto — key exchange, authenticated encryption, and replay protection — in a system small enough to fit in your head.

## Core concepts

- **TUN devices (layer 3)** — Unlike TAP (Ethernet frames), a TUN device hands your program raw IP packets. WireGuard is a layer-3 tunnel: IP packets go in one side, get encrypted into UDP datagrams, and come out decrypted on the other side.
- **Cryptokey routing** — WireGuard's elegant core: a table mapping each peer's public key to the IP ranges ("allowed IPs") it's permitted to send. Encryption and routing become the same lookup — no separate firewall rules needed.
- **Noise IK handshake** — A 1-round-trip key exchange: initiator sends an ephemeral key, responder replies, and both derive session keys. Static keys authenticate both sides like SSH keys; the handshake also provides identity hiding against passive observers.
- **ChaCha20-Poly1305 transport** — Every data packet is encrypted and authenticated with ChaCha20-Poly1305 using a per-packet nonce. Tampered or forged packets fail authentication and are silently dropped — no error oracle for attackers.
- **Perfect forward secrecy and rekeying** — Session keys rotate every couple of minutes via a chained key-derivation ratchet, so a later key compromise can't decrypt past traffic.
- **Roaming** — Peers are identified by key, not IP:port. When a client's endpoint changes (laptop moves networks), the server just updates its endpoint table on the next authenticated packet. This is why WireGuard survives network switches that kill OpenVPN sessions.
- **DoS resistance** — Handshake messages carry MACs (mac1 keyed by responder's public key, mac2 cookie mechanism under load) so the responder allocates zero state for unauthenticated packets — it can't be memory-exhausted by spoofed handshakes.

## How it works

1. Each peer generates a Curve25519 keypair; you configure peers with each other's public keys and allowed IP ranges, and bring up a TUN interface with a tunnel address.
2. When an IP packet arrives from the TUN device, cryptokey routing looks up which peer owns the destination range; if no session keys exist yet, the Noise IK handshake runs (one round trip over UDP).
3. The packet is encrypted with ChaCha20-Poly1305, wrapped in a WireGuard data message with a monotonically increasing nonce (replays are rejected), and sent as UDP to the peer's last-seen endpoint.
4. The receiver authenticates, decrypts, checks the source IP is within the sender's allowed IPs, and writes the plaintext IP packet back into its TUN device.

## Build milestones

1. Create a TUN interface, assign it an address, and read/write raw IP packets — ping through your program unencrypted.
2. Generate X25519 keypairs and implement a toy Noise-IK-style handshake between two peers using libsodium primitives.
3. Build the encrypted transport: encapsulate IP packets in UDP datagrams sealed with ChaCha20-Poly1305 and incrementing nonces.
4. Add a cryptokey routing table (public key ↔ allowed IPs), session-key rotation timers, and replay rejection.
5. Test two peers tunneling real traffic (e.g., `ping` and `curl`) through your implementation.

## Best resources

- [WireGuard](https://www.wireguard.com/) — the project's homepage: protocol overview, quickstart, and the reference implementations.
- [WireGuard whitepaper (NDSS 2017)](https://www.wireguard.com/papers/wireguard.pdf) — Jason Donenfeld's paper: the Noise handshake, cryptokey routing, and DoS-resistance design in full detail.
- [Noise Protocol Framework](https://noiseprotocol.org/) — the handshake framework WireGuard's IK pattern comes from; essential for understanding the key exchange.
- [libsodium documentation](https://doc.libsodium.org/) — the crypto library you'll build on: X25519, ChaCha20-Poly1305, BLAKE2, and key exchange helpers.

## Stretch ideas

- Add the mac1/mac2 cookie mechanism and benchmark handshake-flood resistance against your implementation.
- Implement roaming properly (endpoint learning from authenticated packets) and test a live handover between two Wi-Fi networks.
