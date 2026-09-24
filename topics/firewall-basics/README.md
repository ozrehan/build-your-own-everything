---
title: "Firewall Basics"
category: "security"
difficulty: "beginner"
tags: [networking, iptables, packet-filtering]
related: [port-scanner, vpn-client, tcp-ip-stack-userspace]
---

# Firewall Basics

A firewall is a gatekeeper that inspects every packet entering or leaving a machine and decides, rule by rule, whether it may pass. Writing your own rulesets — and eventually your own packet filter — teaches you exactly how operating systems see network traffic and what "blocked" really means at the packet level.

## Core concepts

- **Packet filtering** — Decisions made on packet headers alone (source/destination IP, port, protocol, TCP flags) without understanding the application data inside.
- **Stateful inspection** — Tracking connection state (NEW, ESTABLISHED, RELATED) so you can allow return traffic for connections you initiated while blocking unsolicited inbound packets.
- **Default-deny policy** — The practice of dropping everything not explicitly allowed, which is far safer than trying to enumerate everything bad; your ruleset is a whitelist.
- **Chains and tables** — In Linux netfilter, packets traverse ordered rule chains (INPUT, OUTPUT, FORWARD) grouped by table (filter, nat, mangle); the first matching rule wins.
- **NAT (masquerading)** — Rewriting source addresses so many private hosts share one public IP, which also implicitly drops unsolicited inbound traffic since no mapping exists.
- **Rule ordering** — Because evaluation stops at the first match, a broad ALLOW placed before a narrow DROP silently nullifies the DROP; ordering bugs are the classic firewall misconfiguration.
- **Logging vs. dropping** — Logging rejected packets gives you visibility into scans and misconfigurations, but unbounded logging on a port under attack can fill disks and cost CPU.

## How it works

On Linux, every packet passes through the netfilter hooks in the kernel. Your ruleset, installed via iptables or nftables, is evaluated top to bottom in the relevant chain: each rule is a match condition (e.g., "TCP destination port 22") plus a verdict (ACCEPT, DROP, REJECT, LOG). The conntrack subsystem watches packets flow and builds a state table, so a rule like "allow ESTABLISHED,RELATED" can permit the server's replies to your outbound web request without opening any inbound port.

A minimal secure host firewall is just a handful of rules: allow loopback, allow established traffic, allow SSH from your IP, drop everything else. Building one by hand and then probing it with a port scanner shows you immediately which rules leak — for example, why allowing all ICMP or forgetting the conntrack rule breaks real traffic.

## Build milestones

1. Write an iptables/nftables ruleset for a fresh VM: default-deny, allow SSH + established traffic, and verify with a port scan from outside.
2. Add NAT/masquerading so a private subnet reaches the internet through your firewall box, and observe conntrack entries as connections flow.
3. Implement rate limiting on SSH (e.g., max 3 new connections per minute per IP) and log dropped packets to see scans in real time.
4. Build a userspace packet filter in Python using raw sockets or nfqueue that implements ACCEPT/DROP decisions on headers.
5. Write a ruleset linter that detects shadowing (unreachable rules), overly broad allows, and missing default-deny.

## Best resources

- [nftables Wiki](https://wiki.nftables.org/) — The official docs for the modern Linux firewall framework, with rule examples and concepts.
- [Iptables Essentials — DigitalOcean](https://www.digitalocean.com/community/tutorials/iptables-essentials-common-firewall-rules-and-commands) — The classic hands-on tutorial for common rules and commands.
- [Netfilter Packet Filtering HOWTO](https://www.netfilter.org/documentation/HOWTO/packet-filtering-HOWTO.html) — Rusty Russell's original deep-dive into how iptables chains and tables work.
- [Ubuntu UFW Community Help](https://help.ubuntu.com/community/UFW) — The friendlier frontend to iptables; great for a first ruleset before going raw.
- [What is a firewall? — Cloudflare Learning Center](https://www.cloudflare.com/learning/network-layer/what-is-a-firewall/) — A clear primer on types of firewalls and where they sit in a network.

## Stretch ideas

- Build a tiny stateful firewall in eBPF/XDP that drops packets in the kernel before they reach the network stack, and benchmark the throughput difference.
- Add geo-blocking or threat-feed ingestion that auto-generates drop rules from a blocklist.
