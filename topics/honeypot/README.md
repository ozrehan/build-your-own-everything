---
title: "Honeypot"
category: "security"
difficulty: "intermediate"
tags: [deception, monitoring, threat-intel]
related: [intrusion-detection, audit-logger, firewall-basics]
---

# Honeypot

A honeypot is a decoy system — a fake SSH server, a fake login page — that has no legitimate users, so every interaction with it is suspicious by definition. Building one teaches you how attackers actually behave on the wire: their scanning patterns, their credential lists, and their post-login commands.

## Core concepts

- **Low vs. high interaction** — Low-interaction honeypots emulate just enough of a service to log probes (cheap, safe); high-interaction ones run real systems attackers can fully compromise (rich intel, real risk of abuse).
- **Deception as detection** — Because no legitimate user ever touches a honeypot, its signal-to-noise ratio is near perfect: an alert from it means something is actively probing you.
- **Attacker TTPs** — Tactics, techniques, and procedures: the credential pairs, commands, and malware download URLs attackers try, which you capture verbatim in honeypot logs and feed into blocklists.
- **Containment** — A honeypot must never become a launchpad: outbound connections are blocked or rate-limited, and high-interaction systems run isolated with snapshots for reset.
- **Fingerprinting risk** — Attackers probe for honeypot tells (fake banners, limited command sets); part of the craft is making the decoy convincing without running anything truly exploitable.
- **Legal and ethical boundaries** — Deploy only on infrastructure you own or are authorized to use, log minimally and transparently, and never use captured credentials against third parties.
- **Threat intelligence output** — The real product of a honeypot is data: attacker IPs, payload hashes, and C2 URLs that feed your IDS rules and firewall blocklists.

## How it works

A low-interaction SSH honeypot like Cowrie listens on port 22 and implements just enough of the SSH protocol to complete a handshake and present a fake shell. Every login attempt — username, password, source IP — is logged. If the attacker "succeeds," they get a simulated filesystem and shell where every command they type (downloading malware via wget, running crypto miners) is recorded and the downloaded files are safely captured for analysis.

Because nothing on the honeypot is real, there's no user traffic to filter out. You point your IDS at its logs and suddenly you have a live feed of what the internet's background radiation is trying right now: which passwords are in this week's botnet dictionaries, which CVEs are being mass-scanned, and what the current malware droppers look like.

## Build milestones

1. Build a fake SSH server in Python (using paramiko or raw sockets) that logs every login attempt's username, password, and IP to a file.
2. Add a fake shell with a handful of convincing commands (ls, whoami, wget) that logs everything typed and safely captures "downloaded" files without executing them.
3. Harden containment: block all outbound traffic from the honeypot except DNS, and run it in an isolated VM or container with no route to your LAN.
4. Add a dashboard that shows top attacker IPs, top credential pairs, and a live tail of sessions.
5. Feed the collected attacker IPs and payload URLs into your firewall blocklist and IDS rules automatically.

## Best resources

- [Cowrie SSH/Telnet Honeypot](https://github.com/cowrie/cowrie) — The standard medium-interaction SSH honeypot; study its fake filesystem and logging to learn the craft.
- [T-Pot — Multi-Honeypot Platform](https://github.com/telekom-security/tpotce) — A turnkey platform running dozens of honeypots with ELK dashboards; shows how honeypot data becomes intel.
- [The Honeynet Project](https://www.honeynet.org/) — The research community behind honeypot science, with papers on deployment and attacker analysis.
- [Modern Honey Network](https://github.com/pwnlandia/mhn) — Server framework for deploying and managing multiple honeypots centrally.

## Stretch ideas

- Build a fake web login honeypot that captures credential-stuffing attempts against your brand's lookalike pages, and analyze which password lists attackers reuse.
- Correlate honeypot hits with your IDS alerts to measure how much of your alert volume is opportunistic internet scanning vs. targeted activity.
