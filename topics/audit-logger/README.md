---
title: "Audit Logger"
category: "security"
difficulty: "beginner"
tags: [logging, compliance, forensics]
related: [intrusion-detection, honeypot, log-aggregator]
---

# Audit Logger

An audit logger records who did what, when — logins, permission changes, data access — in a tamper-evident trail that survives long enough to matter. Building one teaches you the difference between debug logs and security evidence, and why "we'll check the logs" only works if someone designed the logs for that purpose.

## Core concepts

- **Audit trail vs. debug log** — Audit logs answer "who did what to which resource and when" for security and compliance; debug logs answer "why did the code break." Different audiences, different retention, different integrity needs.
- **Tamper evidence** — Hash-chaining log entries (each entry includes the hash of the previous) so that deleting or editing a past entry breaks the chain detectably; append-only storage completes the picture.
- **What to log** — Authentication events, authorization decisions, privilege changes, sensitive data access, and configuration changes — plus the actor, timestamp (UTC, synchronized), source IP, and outcome.
- **What NOT to log** — Passwords, session tokens, full credit-card numbers, and other secrets; logs get copied to many systems, so anything sensitive in them becomes a breach amplifier.
- **Log injection** — Attackers embedding newlines or fake entries in user input that ends up in logs; sanitize or structure (JSON) log fields so the log can't be made to lie.
- **Centralized collection** — Forwarding logs off the host promptly (syslog, agents) so an attacker who compromises the machine can't erase the record of how they got in.
- **Retention and rotation** — Keeping logs long enough for incident response and compliance (often months to years) while managing volume through rotation, compression, and tiered storage.

## How it works

A minimal audit logger is a small library your application calls at security-relevant moments: `audit.log(actor="alice", action="login", result="success", ip="...")`. Each event is serialized as structured JSON with a UTC timestamp, appended to a hash-chained log file (each record stores `prev_hash`), and forwarded to a central collector over TLS. A separate verifier can replay the chain and confirm no entry was altered or removed.

The design lessons are in the details you'll hit immediately: clock sync matters (use UTC everywhere), high-volume events need sampling or aggregation policies, and the forwarder needs local buffering so logs survive network outages. Your first build can be a Python library + file backend + chain verifier, which already captures 80% of the concept.

## Build milestones

1. Build an audit event library: structured JSON events (actor, action, resource, result, timestamp, IP) emitted from a demo app's login and admin actions.
2. Add hash-chained append-only storage and a verifier that detects any tampering with historical entries.
3. Add log injection defenses: structured encoding of all fields and tests proving crafted usernames can't forge entries.
4. Add reliable forwarding: buffer locally, ship to a central collector over TLS, and survive collector outages without losing events.
5. Build the review side: a query CLI (filter by actor/action/time) and an alert rule (e.g., 5 failed logins → alert) over the collected logs.

## Best resources

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) — What to log, what not to log, and how to protect logs; the practical baseline.
- [NIST SP 800-92 — Guide to Computer Security Log Management](https://csrc.nist.gov/pubs/sp/800/92/final) — The standard reference on log management infrastructure: generation, protection, and retention.
- [Linux Audit documentation](https://github.com/linux-audit/audit-documentation) — The kernel-level audit framework: syscall auditing, rules, and log formats.
- [RFC 5424 — The Syslog Protocol](https://www.rfc-editor.org/rfc/rfc5424) — The structured syslog format your forwarder will likely speak.

## Stretch ideas

- Add anomaly alerting on the audit stream: impossible-travel logins, privilege escalations outside change windows, dormant-account activity.
- Implement signed log checkpoints: periodically anchor the chain hash somewhere external (even a gist) so tampering with the whole file is detectable.
