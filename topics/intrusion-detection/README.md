---
title: "Intrusion Detection"
category: "security"
difficulty: "intermediate"
tags: [ids, monitoring, threat-detection]
related: [packet-sniffer, audit-logger, honeypot]
---

# Intrusion Detection

An intrusion detection system watches network traffic or host activity and raises alerts when something looks like an attack. Building your own — even a simple signature matcher over packet captures — teaches you how defenders actually spot port scans, exploit attempts, and malware beacons hiding in ordinary traffic.

## Core concepts

- **Signature-based detection** — Matching traffic against known-bad patterns (a Snort rule for a specific exploit string); precise and low-noise, but blind to anything new.
- **Anomaly-based detection** — Learning what "normal" looks like (traffic volumes, login times) and flagging deviations; catches novel attacks but needs tuning to avoid alert floods.
- **NIDS vs. HIDS** — Network IDS (Snort, Suricata, Zeek) watches packets on the wire and sees everything crossing a segment; host IDS (OSSEC, Wazuh agents) watches logs and file integrity on one machine and sees what encryption hides.
- **Rules and signatures** — Declarative detection logic, e.g., "alert on TCP to port 445 containing this SMB exploit byte pattern"; the entire craft is writing rules with high signal and low false positives.
- **Alert fatigue** — The operational reality that a noisy IDS gets ignored; tuning thresholds, suppressions, and severity levels is as important as detection coverage.
- **Network Security Monitoring (NSM)** — The philosophy that you collect full packet data and metadata so you can investigate after an alert, not just detect — detection tells you where to look, data tells you what happened.
- **Evasion techniques** — Attackers fragment packets, use slow scans, or encrypt payloads to dodge signatures; understanding evasion is why defenders layer multiple detection methods.

## How it works

A typical NIDS like Snort or Suricata sniffs packets off an interface (or a mirrored switch port), reassembles TCP streams, and runs each stream through a rule engine. Rules specify protocol, ports, and content matches — for example, "TCP destination port 80, payload contains `union select` case-insensitively" — and fire an alert with a classification and priority when they match. Zeek takes a different approach: instead of just alerting, it logs rich structured metadata about every connection, DNS query, and file transfer, which analysts query during investigations.

In practice you layer these: signatures catch the known-bad, anomaly baselines catch the weird, and full packet/metadata retention lets a human confirm. Your first build will be a small Python sniffer that applies a handful of hand-written rules to live traffic and prints alerts — and you'll immediately discover how noisy the real internet is.

## Build milestones

1. Write a packet sniffer that reassembles TCP streams and alerts on a hardcoded list of suspicious strings (e.g., SQLi keywords in HTTP requests).
2. Add a rule format (YAML or Snort-like one-liners) with protocol/port/content matching, so detections are data, not code.
3. Build a port-scan detector using connection-attempt counting per source IP over a sliding time window, with tunable thresholds.
4. Add alert deduplication and severity levels, plus a JSON log of every alert for later analysis.
5. Deploy your detector on a mirrored port or test VM, run a lab vulnerability scan against it, and tune rules until scan traffic is caught with minimal false positives.

## Best resources

- [Snort — Network Intrusion Detection](https://www.snort.org/) — The classic open-source NIDS; its rule documentation teaches signature writing better than any textbook.
- [Suricata — Open Source IDS/IPS](https://suricata.io/) — Multi-threaded modern NIDS with excellent rule and output documentation.
- [Zeek — Network Security Monitor](https://zeek.org/) — The metadata-first approach: learn its logging model to understand investigation-driven monitoring.
- [Security Onion](https://securityonion.net/) — A full NSM distribution bundling Snort/Suricata, Zeek, and ELK; great for seeing how the pieces fit together.
- [TaoSecurity Blog](https://taosecurity.blogspot.com/) — Richard Bejtlich's long-running blog on network security monitoring practice and philosophy.

## Stretch ideas

- Add a simple anomaly detector: baseline bytes-per-host per hour and alert on 3-sigma deviations, then compare its alert volume against your signature rules.
- Feed your alerts into an ELK/OpenSearch dashboard with a timeline view for investigating a simulated compromise.
