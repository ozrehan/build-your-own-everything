---
title: "Port Scanner"
category: "networking"
difficulty: "beginner"
tags: [scanning, tcp, security]
related: [packet-sniffer, firewall-basics, vulnerability-scanner, tcp-ip-stack-userspace]
---

# Port Scanner

A port scanner asks a host "which doors are open?" by probing its TCP and UDP ports and interpreting the replies. It's the first tool in every network inventory and security assessment — and writing one teaches TCP handshakes, raw sockets, and the difference between what a firewall shows and what's really there. (Scan only hosts you own or have permission to test.)

## Core concepts

- **TCP connect scan** — The polite scan: complete the full three-way handshake per port. Needs no privileges, always works — but it's slow and gets logged everywhere.
- **SYN (half-open) scan** — Send SYN, read the reply, never complete the handshake: SYN/ACK means open, RST means closed. Fast and stealthy, but needs raw-socket privileges (root).
- **FIN/NULL/Xmas scans** — Send packets with unusual flag combos; RFC 793 says closed ports must RST them while open ports stay silent. They slip past simple stateless firewalls but fail against Windows stacks (which RST everything).
- **UDP scanning** — Send empty UDP datagrams: an ICMP "port unreachable" means closed, silence means open-or-filtered. Slow and ambiguous — which is why UDP services hide so well.
- **Port states** — Open, closed, filtered (firewall dropped the probe), unfiltered, and open|filtered. A good scanner reports states, not just "open ports", because filtered tells its own story.
- **Timing and parallelism** — Scanning 65k ports serially takes forever; real scanners parallelize probes, adapt timeouts to measured RTT, and randomize order to dodge rate-based detection.
- **Banner grabbing** — After finding an open port, read the service's greeting (or send a probe) to identify what's actually listening — the step that turns port lists into asset inventories.

## How it works

For a connect scan, you attempt a TCP `connect()` to each target port with a short timeout: success means open, refused means closed, timeout means filtered. For a SYN scan, you craft raw SYN packets (IP_HDRINCL or AF_PACKET), then sniff replies: a SYN/ACK flags the port open (you immediately RST to avoid completing the handshake), an RST flags it closed, and silence after retries flags it filtered. Results feed a state table per host, and a final pass banners open ports to fingerprint services.

## Build milestones

1. Write a TCP connect scanner in Python: probe a list of ports with timeouts and report open vs closed.
2. Add banner grabbing — read the first response bytes (or send an HTTP/SSH probe) to identify services on open ports.
3. Implement a raw-socket SYN scan: craft SYN packets, interpret SYN/ACK vs RST replies, and RST open ports to stay half-open.
4. Parallelize with a thread pool or async I/O, add adaptive timeouts, randomized port order, and a top-1000 ports list.
5. Produce an Nmap-style report: per-host port states, service guesses, and scan timing statistics.

## Best resources

- [Nmap: Port Scanning Techniques](https://nmap.org/book/man-port-scanning-techniques.html) — the definitive reference for every scan type: what it sends, what replies mean, and when each fails.
- [Nmap](https://nmap.org/) — the standard itself; study its output format and timing options to calibrate your own scanner.
- [masscan](https://github.com/robertdavidgraham/masscan) — the fastest port scanner ever written; its design notes teach asynchronous transmit/receive at line rate.
- [ZMap](https://zmap.io/) — internet-wide scanning research project; the papers explain stateless scanning and address randomization.
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) — sockets and raw-socket programming fundamentals your scanner is built on.

## Stretch ideas

- Add basic OS fingerprinting by probing TCP/IP stack quirks (initial window size, TTL, option order) and matching against a signature table.
- Implement UDP scanning with ICMP-unreachable handling and rate limiting, then compare coverage against your TCP results on a test host.
