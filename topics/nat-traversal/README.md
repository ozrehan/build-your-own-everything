---
title: "NAT Traversal"
category: "networking"
difficulty: "intermediate"
tags: [nat, stun, p2p]
related: [vpn-wireguard-basics, webrtc-video-chat, dht-kademlia, p2p-file-sharing]
---

# NAT Traversal

Two machines behind home routers can't just connect to each other — neither has a public address the other can dial. NAT traversal (STUN, hole punching, ICE) is the bag of tricks that makes peer-to-peer calls, games, and VPNs work anyway. Building it yourself reveals why "just connect" is one of networking's hardest problems.

## Core concepts

- **NAT mappings** — When your machine sends a UDP packet out, the NAT creates a temporary public `ip:port` mapping and rewrites the packet. Return traffic to that mapping gets forwarded back inside. The mapping is the only door in.
- **NAT behavior types** — Full-cone NATs accept packets from anyone once a mapping exists; restricted/port-restricted NATs only accept from addresses you've contacted; symmetric NATs create a *different* mapping per destination, which defeats naive hole punching.
- **STUN** — A simple protocol that answers "what does my address look like from the internet?" You send a Binding Request to a public STUN server; it replies with the XOR-MAPPED-ADDRESS — the public `ip:port` your NAT assigned you.
- **Hole punching** — Both peers send UDP packets to each other's public addresses *simultaneously*. Each NAT sees an outbound packet first and opens the mapping, so the inbound packet from the peer looks like a reply and is let through.
- **ICE** — The full framework: gather candidates (host addresses, STUN-discovered reflexive addresses, TURN relay addresses), exchange them via a signaling channel, then run connectivity checks on every pair and nominate the best working one.
- **TURN relay fallback** — When both sides sit behind symmetric NATs and punching fails, traffic relays through a public server. It always works and always costs bandwidth — which is why it's the last resort.
- **Signaling channel** — Peers need *some* way to exchange candidates before they can talk directly — a websocket, a central server, even copy-pasted text. Signaling is out-of-band by design.

## How it works

1. Each peer opens a UDP socket and asks a STUN server for its reflexive (public) address, collecting a candidate list: local LAN addresses plus the STUN-discovered address.
2. Peers swap candidate lists through the signaling channel.
3. Both sides start sending probe packets to every candidate pair at once — these outbound packets punch holes in their own NATs while doubling as connectivity checks.
4. The first pair that gets a successful round trip wins; both sides switch their data path to it. If nothing works after a timeout, they fall back to relaying through TURN.

## Build milestones

1. Write a STUN client: send a Binding Request to a public STUN server and parse the XOR-MAPPED-ADDRESS from the response.
2. Set up a tiny signaling server (websocket or HTTP); have two NATed peers exchange their reflexive addresses and observe what each side sees.
3. Implement UDP hole punching: both peers send to each other's public endpoints simultaneously and establish a direct channel.
4. Build mini-ICE: gather host + server-reflexive candidates, run connectivity checks across pairs, nominate the best path automatically.
5. Add a relay fallback mode and measure when punching succeeds vs fails across different NAT setups.

## Best resources

- [How NAT traversal works (Tailscale)](https://tailscale.com/blog/how-nat-traversal-works/) — the best illustrated explainer of NAT mappings, STUN, and hole punching; read this first.
- [RFC 8489 — STUN](https://www.rfc-editor.org/rfc/rfc8489) — the current STUN spec: message format, XOR-mapped addresses, and authentication.
- [RFC 8445 — ICE](https://www.rfc-editor.org/rfc/rfc8445) — candidate gathering, connectivity checks, and nomination; the full traversal framework.
- [RFC 5766 — TURN](https://www.rfc-editor.org/rfc/rfc5766) — the relay protocol of last resort: allocations, permissions, and channel bindings.

## Stretch ideas

- Classify your own NAT's behavior (full-cone vs symmetric) empirically by probing mapping stability across destinations.
- Implement simultaneous-open TCP hole punching, which is far fussier than UDP, and document where it breaks.
