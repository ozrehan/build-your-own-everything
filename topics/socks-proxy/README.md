---
title: "SOCKS Proxy"
category: "networking"
difficulty: "beginner"
tags: [socks, proxy, tunneling]
related: [vpn-wireguard-basics, nat-traversal, packet-sniffer]
---

# SOCKS Proxy

SOCKS is the universal TCP (and UDP) relay: a client asks the proxy to "connect me to host:port" and the proxy shuttles bytes, never caring whether it's HTTP, SSH, or a game protocol. It's simpler than HTTP proxies, which makes it the perfect first proxy — and the foundation of SSH tunneling and Tor's local interface.

## Core concepts

- **Circuit-level proxying** — SOCKS operates at the session layer: it relays opaque byte streams without parsing application protocols. One proxy handles everything TCP — the opposite of an HTTP proxy's request/response model.
- **SOCKS5 handshake** — Client offers auth methods, server picks one (usually "no auth" or username/password), then the client sends a CONNECT request with the target address. Three small steps and you're tunneling.
- **Address types** — Requests carry IPv4, IPv6, or a domain name. Domain-name support is the killer feature: the *proxy* resolves DNS, so clients never leak DNS queries locally (crucial for privacy tools).
- **UDP ASSOCIATE** — SOCKS5's UDP mode: after a TCP control connection, UDP datagrams get wrapped with a small header and relayed. Essential for DNS-over-SOCKS and any UDP application.
- **BIND for inbound** — The rarely-used reverse mode: the proxy listens on a port and forwards inbound connections back to the client (FTP active mode's trick).
- **Authentication** — Username/password auth (RFC 1929) is the standard; GSSAPI exists for Kerberos shops. Most private proxies are just "a secret password on a port".
- **Proxy chains** — SOCKS proxies compose: client → proxy A → proxy B → target. Each hop only knows its neighbors — the same layering idea Tor extends with encryption.

## How it works

The server listens on (typically) port 1080. Each client connection starts with method negotiation (client lists auth methods, server selects), then a request: CONNECT + address type + target host/port. The server dials the target, replies with success/failure, and then enters a byte-shuttling loop — two `io.Copy` directions until either side closes. For UDP ASSOCIATE, the server allocates a UDP relay socket, wraps each datagram with the SOCKS UDP header, and forwards them, enforcing that datagrams come from the client that established the association.

## Build milestones

1. Implement the SOCKS5 handshake: method negotiation (no-auth) and CONNECT requests with IPv4 targets.
2. Add the relay loop: dial the target, reply success, and shuttle bytes both ways until close.
3. Support domain-name and IPv6 address types (resolve on the proxy side) and proper error replies.
4. Add username/password authentication and per-client connection logging.
5. Implement UDP ASSOCIATE and test DNS queries tunneled through your proxy.

## Best resources

- [RFC 1928 — SOCKS Protocol Version 5](https://www.rfc-editor.org/rfc/rfc1928) — the whole protocol in 9 pages: handshake, requests, replies, and UDP.
- [RFC 1929 — Username/Password Authentication for SOCKS V5](https://www.rfc-editor.org/rfc/rfc1929) — the standard auth sub-protocol.
- [microsocks](https://github.com/rofl0r/microsocks) — a tiny, readable multithreaded SOCKS5 implementation; perfect reference code.
- [Dante](https://www.inet.no/dante/) — the venerable full-featured SOCKS server; study its config model for access rules.

## Stretch ideas

- Chain two of your proxies and verify end-to-end connectivity; add access-control rules (allow/deny by destination).
- Build a TUN-to-SOCKS adapter that routes all of a machine's TCP traffic through your proxy transparently.
