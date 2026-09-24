---
title: "Userspace TCP/IP Stack"
category: "networking"
difficulty: "advanced"
tags: [tcp, ip, tuntap]
related: [packet-sniffer, port-scanner, nat-traversal, vpn-wireguard-basics]
---

# Userspace TCP/IP Stack

A userspace TCP/IP stack reimplements the kernel's networking — Ethernet, ARP, IP, ICMP, and TCP — as an ordinary program that reads raw packets from a virtual network interface. Building one forces you to confront every field of every header, and it's the single fastest way to truly understand what happens between `connect()` and the wire.

## Core concepts

- **TUN/TAP devices** — Virtual network interfaces created by the kernel. A TAP device hands your program raw Ethernet frames to read and write, so your program becomes the network stack for that interface, exactly how VPN clients work.
- **ARP (Address Resolution Protocol)** — Maps IP addresses to MAC addresses on a local network. Your stack must answer "who has this IP?" requests before anyone can send it a single IP packet.
- **IPv4 header and checksum** — Every packet carries version, length, TTL, protocol, and source/destination addresses plus a header checksum. Getting the checksum wrong means silent packet drops, which is why it's the classic first bug.
- **TCP state machine** — Connections move through LISTEN → SYN_RCVD → ESTABLISHED → FIN_WAIT → CLOSED and a dozen more states. Each incoming segment is legal only in certain states; the state machine is the heart of TCP.
- **Sequence and acknowledgment numbers** — TCP numbers every byte, not every packet. ACKs say "I've received everything up to byte N", which is what makes retransmission and reordering possible.
- **Retransmission and RTO** — If an ACK doesn't arrive in time, the sender resends. The retransmission timeout adapts to measured round-trip time (Jacobson's algorithm); too aggressive and you flood, too lazy and you stall.
- **Sliding window and flow control** — The receiver advertises how much buffer space it has, and the sender never has more than that unacknowledged. This one mechanism prevents fast senders from overwhelming slow receivers.
- **Socket API shim** — Advanced stacks (like level-ip) intercept libc's `socket`/`connect` calls via `LD_PRELOAD` so unmodified programs like `curl` run on your stack instead of the kernel's.

## How it works

1. You create a TAP device (`ip tuntap add dev tap0 mode tap`) and give it an address; the kernel now delivers every frame sent to that interface to your program's file descriptor.
2. Your main loop reads raw Ethernet frames, dispatches on EtherType: ARP frames go to your ARP handler (learn mappings, answer requests for your IP), IPv4 frames go to IP parsing (verify checksum, check destination).
3. ICMP echo requests get echo replies; TCP segments go to the TCP engine, which looks up the connection by the 4-tuple (src IP, src port, dst IP, dst port) and drives the state machine: SYN in LISTEN → send SYN/ACK → wait for ACK → ESTABLISHED.
4. In ESTABLISHED, incoming data segments are ACKed and reassembled in sequence-number order; outgoing data is segmented, checksummed, and queued for retransmission until ACKed. FIN initiates the closing handshake.

## Build milestones

1. Open a TAP device, read raw Ethernet frames, and print parsed IPv4/ICMP header fields for each packet you see.
2. Answer ARP requests for your stack's IP and reply to ICMP echo requests — `ping` your stack successfully.
3. Implement the TCP three-way handshake so `nc` can complete a connection to a listening port on your stack.
4. Add data transfer: sequence numbers, ACKs, in-order reassembly, and a retransmission timer for lost segments.
5. Implement graceful close (FIN handshake) and RST handling for refused ports, then run a real HTTP request through it.
6. Stretch: `LD_PRELOAD` shim that redirects a real program's socket calls into your stack.

## Best resources

- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/) — the classic sockets/TAP-level tutorial; essential background for the syscalls your stack sits on.
- [level-ip](https://github.com/saminiir/level-ip) — a complete, readable userspace TCP/IP stack in C built as a learning project; the reference implementation for this exact build.
- [Let's Code a TCP/IP Stack (part 1: Ethernet & ARP)](http://www.saminiir.com/lets-code-tcp-ip-stack-1-ethernet-arp) — first of a 5-part blog series walking through level-ip's construction, from ARP through TCP retransmission.
- [RFC 793 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc793) — the original TCP spec; dense but it's the ground truth for the state machine and header format.
- [RFC 791 — Internet Protocol](https://www.rfc-editor.org/rfc/rfc791) — the IPv4 spec; short enough to read end to end and worth doing once.
- [Linux TUN/TAP documentation](https://www.kernel.org/doc/html/latest/networking/tuntap.html) — how the virtual interface your stack reads from actually works.

## Stretch ideas

- Add UDP and a minimal DNS client running entirely on your stack, so `gethostbyname` never touches the kernel.
- Implement TCP congestion control (slow start + congestion avoidance) and watch throughput change under loss with `tc netem`.
