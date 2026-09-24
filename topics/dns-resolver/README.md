---
title: "DNS Resolver"
category: "networking"
difficulty: "intermediate"
tags: [dns, protocol, udp]
related: [service-discovery, tls-handshake, packet-sniffer, cdn-edge-cache]
---

# DNS Resolver

Every name you type — every `curl`, every API call — starts with a DNS lookup, and almost nobody has seen the actual packets. Writing a resolver that speaks the DNS wire protocol and walks the hierarchy from the root servers yourself turns "the internet's phone book" from metaphor into mechanism.

## Core concepts

- **Names, labels, and zones** — `www.example.com` is three labels; each zone (like `example.com`) is administered by authoritative servers, and delegation happens through NS records pointing down the tree.
- **Record types** — A/AAAA map names to addresses, CNAME aliases one name to another, MX routes mail, NS delegates zones, TXT carries arbitrary data, SOA describes the zone itself. Your parser must handle each type's RDATA layout.
- **Wire format** — A 12-byte header (ID, flags, counts) followed by question, answer, authority, and additional sections. Names are length-prefixed labels, often with compression pointers (two high bits set) that jump elsewhere in the packet to save bytes.
- **Recursive vs iterative resolution** — A stub resolver asks a recursive resolver "just give me the answer"; the recursive resolver does the iterative work: ask a root, follow the referral, ask the TLD server, follow the referral, ask the authoritative server.
- **The delegation chain** — Resolution starts at one of the 13 root server identities, each step returning NS records plus "glue" A records for the next servers down. Following glue correctly is the subtle part.
- **Caching and TTL** — Every record carries a time-to-live; resolvers cache aggressively because the same names get asked constantly. Respecting TTLs (and never caching failures long) is what keeps DNS fast and correct.
- **UDP with TCP fallback** — Queries go over UDP for speed; if the response is truncated (TC bit set, common with DNSSEC), the client retries over TCP.

## How it works

1. You encode a query: header with a random 16-bit ID and the RD (recursion desired) flag, the question name as length-prefixed labels, QTYPE=A, QCLASS=IN.
2. For iterative resolution you send it to a root server IP, parse the response, and if there's no answer, extract the NS records and glue addresses from the authority/additional sections.
3. You repeat the query to one of those next servers, walking down root → TLD → authoritative until an answer (or NXDOMAIN) arrives, following CNAME chains as needed.
4. Answers are cached keyed by (name, type) with their TTLs; repeated lookups never hit the network until the TTL expires.

## Build milestones

1. Hand-craft a DNS query packet, send it over UDP to a public resolver, and decode the response's answer section by hand.
2. Handle name compression pointers and CNAME chains so real-world answers (which almost always use both) parse correctly.
3. Build an iterative resolver: start from a root server IP and follow referrals down to the authoritative answer without any recursion help.
4. Add a TTL-respecting cache, concurrent queries, and timeouts/retries for robustness.
5. Resolve `AAAA`, `MX`, and `TXT` records too, and add a CLI (`mydig example.com MX`) that prints answers like `dig`.

## Best resources

- [RFC 1034 — Domain Names: Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034) — the architecture: names, zones, delegation, and how resolution is supposed to work.
- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035) — the wire format, header flags, and record encodings your code implements.
- [RFC 8484 — DNS over HTTPS](https://www.rfc-editor.org/rfc/rfc8484) — how DNS is tunneled over HTTPS today; a great stretch target after UDP works.
- [Cloudflare Learning: What is DNS?](https://www.cloudflare.com/learning/dns/what-is-dns/) — a clear illustrated walkthrough of recursive vs authoritative servers.
- [Implement DNS in a Weekend](https://implement-dns.wizardzines.com/) — Julia Evans' guided tutorial for writing a DNS resolver from scratch, step by step.

## Stretch ideas

- Speak DNS-over-HTTPS (RFC 8484) or DNS-over-TLS (RFC 7858) and compare latency and privacy with plaintext DNS.
- Write a tiny authoritative server for your own zone and watch your resolver talk to it end to end.
