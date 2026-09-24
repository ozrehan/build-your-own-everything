---
title: "BGP Announcer"
category: "networking"
difficulty: "intermediate"
tags: [bgp, routing, internet]
related: [dns-resolver, firewall-basics, status-page, metrics-monitor]
---

# BGP Announcer

BGP is the protocol that stitches the internet together — routers in 70,000+ autonomous systems use it to tell each other which IP ranges live where. Announcing a prefix yourself (even in a lab) teaches you how global routing really works, and why a single misconfigured announcement can redirect a country's traffic.

## Core concepts

- **Autonomous Systems and prefixes** — The internet is a federation of networks (ASes), each identified by an ASN, each originating IP prefixes like `203.0.113.0/24`. BGP's job is distributing "AS X can reach prefix Y" claims.
- **eBGP vs iBGP** — External BGP runs between different ASes (the internet's glue); internal BGP distributes those routes inside one AS. The distinction changes loop-prevention rules and next-hop handling.
- **BGP messages** — Four types: OPEN (start a session, exchange ASN/hold time/capabilities), UPDATE (announce or withdraw prefixes with path attributes), NOTIFICATION (errors, tears the session down), KEEPALIVE (heartbeat). That's the whole protocol.
- **Path attributes** — Every announcement carries ORIGIN, AS_PATH (the list of ASes the route traversed — BGP's loop prevention), and NEXT_HOP, plus optional ones like communities (opaque tags operators use for policy).
- **Best-path selection** — Routers receiving multiple announcements for one prefix pick a winner through a deterministic preference cascade (local-pref, AS path length, origin, MED…). Understanding it explains why traffic takes the paths it does.
- **Announcement vs withdrawal** — An UPDATE either advertises reachability or withdraws it. Withdrawing a more-specific prefix instantly reroutes traffic — the mechanism behind both failover and hijacks.
- **Looking glasses and collectors** — Public route collectors (RIPE RIS, RouteViews) archive global BGP state; you can watch your lab announcement propagate (or, defensively, watch for someone announcing *your* space).

## How it works

1. Your speaker opens TCP port 179 to a peer, sends an OPEN message with your ASN, hold time, and capabilities (e.g., multiprotocol extensions), and completes the handshake with KEEPALIVEs.
2. To announce, you build an UPDATE: the NLRI (your prefix) plus path attributes — AS_PATH containing your ASN, NEXT_HOP set to your address, ORIGIN=IGP.
3. The peer installs it, re-advertises to its own peers with your ASN prepended to AS_PATH, and the announcement ripples outward.
4. To withdraw, you send an UPDATE listing the prefix in the withdrawn-routes field; peers purge it and reconverge. Health-check-driven announce/withdraw is the standard anycast failover pattern.

## Build milestones

1. Establish a BGP session against a local BIRD or FRR peer: exchange OPEN messages and keep it alive with KEEPALIVEs.
2. Craft and send an UPDATE announcing a test prefix; confirm it appears in the peer's routing table.
3. Withdraw the prefix and parse incoming UPDATEs, printing AS_PATHs of routes your peer sends you.
4. Drive announcements from a script with ExaBGP: announce on health-check pass, withdraw on failure — a working anycast failover demo.
5. Add BGP communities to your announcements and observe how the peer's policy treats tagged vs untagged routes.

## Best resources

- [RFC 4271 — BGP-4](https://www.rfc-editor.org/rfc/rfc4271) — the protocol spec: message formats, the state machine, and path attributes.
- [ExaBGP](https://github.com/Exa-Networks/exabgp) — the programmable BGP speaker: it handles the state machine and encoding while your scripts decide what to announce.
- [GoBGP](https://github.com/osrg/gobgp) — a full-featured Go BGP daemon with CLI and gRPC API; great for standing up the peer your announcer talks to.
- [Hurricane Electric BGP Toolkit](https://bgp.he.net/) — look up any ASN or prefix to see real AS paths; invaluable for sanity-checking what your announcements should look like.

## Stretch ideas

- Build a container lab with three ASes and practice traffic engineering with AS_PATH prepending and communities.
- Write a defensive monitor that watches a prefix you care about and alerts if its origin ASN ever changes (hijack detection).
