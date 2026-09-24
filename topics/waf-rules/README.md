---
title: "WAF Rules"
category: "security"
difficulty: "intermediate"
tags: [waf, appsec, http]
related: [vulnerability-scanner, security-headers-scanner, http-protocol-deep-dive]
---

# WAF Rules

A Web Application Firewall sits in front of your app and inspects HTTP requests against a ruleset, blocking SQL injection, XSS, and other attack patterns before they reach your code. Writing your own rules teaches you how attacks actually look on the wire — and why a WAF is a complement to secure code, never a substitute.

## Core concepts

- **Positive vs. negative security model** — Negative model blocks known-bad patterns (signatures); positive model allows only known-good input shapes. Negative is easier to deploy, positive is stronger but needs per-app tuning.
- **Rule chaining and scoring** — Modern rulesets (like the OWASP Core Rule Set) assign anomaly scores per matched rule and block when the total crosses a threshold, instead of blocking on any single match — which slashes false positives.
- **Paranoia levels** — Tiered rule strictness: level 1 blocks obvious attacks with minimal false positives, higher levels catch subtler attacks but need tuning for your app's legitimate traffic.
- **Request parsing** — A WAF must decode the request exactly like your backend does (URL decoding, multipart bodies, JSON); mismatches between WAF parsing and app parsing are a classic bypass vector.
- **False positives and tuning** — Legitimate traffic (a blog post about SQL, a password containing `<script>`) triggers rules; production WAF work is mostly writing exclusions, not rules.
- **Virtual patching** — Deploying a WAF rule to block exploitation of a known CVE while you wait for the real patch — a key incident-response use case.
- **WAF bypass techniques** — Attackers use encoding tricks, case variation, and parser differentials to slip past signatures; studying bypasses (defensively, on your own apps) is how you write robust rules.

## How it works

A WAF like ModSecurity with the OWASP Core Rule Set processes each request in phases: parse headers, args, and body (decoding transformations like URL-decoding and comment-stripping first), then run the ruleset. Each rule is a match condition — a regex against an argument, a check for a known attack string — that adds to an anomaly score when it hits. If the inbound score exceeds the threshold (default 5 for CRS), the request is blocked with a 403; the response can be scored and inspected on the way out too.

Building a miniature version — a reverse proxy in Python or Go that applies a dozen hand-written regex rules to query strings and bodies — shows you both the power (it really does stop basic SQLi probes) and the limits (one encoding trick and naive regexes fall over). That tension is the entire WAF discipline.

## Build milestones

1. Build a reverse proxy that logs full requests and applies 5 hand-written block rules (SQLi keywords, `<script>`, path traversal) to query strings.
2. Add request-body inspection with decoding transformations (URL-decode, lowercase) applied before matching, and watch bypass attempts fail.
3. Implement anomaly scoring: rules add points, block at a threshold, so single weak signals don't cause false positives.
4. Deploy ModSecurity + OWASP CRS in front of your own test app, run an attack lab against it, and tune paranoia level and exclusions.
5. Write a virtual patch: a custom rule that blocks exploitation of a specific CVE in your test app until you deploy the real fix.

## Best resources

- [OWASP Core Rule Set (CRS)](https://coreruleset.org/) — The community standard WAF ruleset; its documentation teaches rule writing, scoring, and tuning.
- [ModSecurity](https://github.com/owasp-modsecurity/ModSecurity) — The open-source WAF engine; study its SecRules language and processing phases.
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) — The risk list your rules should map to; keeps your ruleset focused on what matters.
- [AWS WAF Documentation](https://docs.aws.amazon.com/waf/) — Managed-WAF perspective: managed rule groups, rate-based rules, and logging.

## Stretch ideas

- Build a positive-security-model WAF: learn your app's normal request shapes for a week, then alert on anything structurally new.
- Add a shadow/block mode toggle with full request logging so you can measure false-positive rates before enforcing.
