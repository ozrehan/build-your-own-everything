# Example: Networking — Journey of a URL

**[▶ Try it live](https://byoe-net-journey.netlify.app)**

Type any URL and watch what *really* happens when you press enter —
packets flying through **DNS → TCP handshake → TLS handshake → HTTP**, animated.

Example project for the [networking learning path](../../topics/tcp-ip-stack-userspace/).

## What it teaches

| Phase | Packets | Concept |
|---|---|---|
| DNS | query → answer | name resolution, caching |
| TCP | SYN → SYN-ACK → ACK | 3-way handshake, sequence numbers |
| TLS | ClientHello → certificate → key exchange | encrypted tunnel negotiation |
| HTTP | GET → 200 OK | the actual request, inside the tunnel |

## Exercises

1. Add a **packet sniffer view** showing raw bytes of each packet.
2. Simulate **packet loss**: drop the SYN and show the retransmit timer firing.
3. Animate what changes with **QUIC** (fewer round trips — see the `quic-basics` topic).
