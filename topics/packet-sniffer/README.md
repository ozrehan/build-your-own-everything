---
title: "Packet Sniffer"
category: "networking"
difficulty: "intermediate"
tags: [packets, pcap, debugging]
related: [port-scanner, tcp-ip-stack-userspace, tls-handshake, dns-resolver]
---

# Packet Sniffer

A packet sniffer captures raw traffic off the wire and decodes it layer by layer — it's tcpdump/Wireshark from scratch. Building one turns every protocol you've read about into something you can watch live, and it makes you fluent in the byte-level reality of Ethernet, IP, TCP, and DNS.

## Core concepts

- **Promiscuous mode and AF_PACKET** — Normally the NIC drops frames not addressed to you; promiscuous mode (or a raw `AF_PACKET` socket) hands your program everything the interface sees. On switched networks you mostly see your own traffic plus broadcasts.
- **Link-layer decoding** — Every capture starts with Ethernet: destination/source MACs and the EtherType that says what comes next (IPv4, IPv6, ARP). VLAN tags insert an extra 4 bytes you must skip correctly.
- **IP header parsing** — Version, header length, total length, TTL, protocol number, and the source/destination addresses. The protocol field (6=TCP, 17=UDP, 1=ICMP) routes you to the next parser.
- **TCP segment decoding** — Ports, sequence/ack numbers, flags (SYN/ACK/FIN/RST), window size. Reading flags in a live handshake is the moment TCP finally clicks.
- **BPF filters** — Berkeley Packet Filter expressions (`tcp port 80`, `host 1.2.3.4`) compiled to bytecode that runs in the kernel, so you only pay for packets you care about. Writing filters by hand teaches the bytecode VM.
- **Stream reassembly** — Following one TCP conversation means tracking sequence numbers, handling retransmissions and out-of-order segments — the hard part that separates packet printers from protocol analyzers.
- **pcap format** — The standard capture file format (global header + per-packet records with timestamps). Writing pcap files lets Wireshark open your captures for deeper analysis.

## How it works

You open a raw socket (or libpcap handle) on an interface, optionally install a BPF filter, and receive frames in a capture loop. Each frame is decoded by a chain of parsers: Ethernet → (VLAN) → IP → TCP/UDP/ICMP → application decoders (DNS, HTTP). A flow table keyed by 5-tuple tracks TCP streams for reassembly; a display layer prints per-packet summaries and per-flow statistics, and an optional pcap writer persists captures for later analysis in Wireshark.

## Build milestones

1. Capture frames with a raw socket and print a hexdump plus parsed Ethernet and IPv4 headers.
2. Decode TCP and UDP headers; print one summary line per packet (src → dst, ports, flags, length) like a minimal tcpdump.
3. Add DNS decoding: parse queries and responses on port 53 to show names being resolved live.
4. Implement TCP stream reassembly — follow one connection's data stream across segments in order.
5. Support BPF-style filters and write captures to pcap files that Wireshark can open.

## Best resources

- [tcpdump](https://www.tcpdump.org/) — the reference capture tool; its man page doubles as a BPF filter tutorial.
- [Wireshark](https://www.wireshark.org/) — the graphical analyzer; use it to verify your parser against ground truth on the same capture.
- [libpcap](https://www.tcpdump.org/#latest-release) — the portable capture library (and its BPF compiler) that every serious sniffer builds on.
- [Scapy](https://scapy.net/) — the Python packet-crafting library; excellent for generating test traffic to feed your sniffer.
- [Practical Packet Analysis (Chris Sanders)](https://www.chrissanders.org/practical-packet-analysis-3rd-edition/) — the book-length guide to reading captures, protocol by protocol.

## Stretch ideas

- Add TLS ClientHello parsing to extract SNI hostnames — the classic "what sites is this machine visiting" view.
- Build a live bandwidth-by-host dashboard that aggregates your captures into per-host traffic statistics.
