---
title: "Phishing Simulator (Defensive Training)"
category: "security"
difficulty: "intermediate"
tags: [phishing, training, awareness]
related: [audit-logger, totp-2fa, security-headers-scanner]
---

# Phishing Simulator (Defensive Training)

A phishing simulator sends safe, clearly-labeled mock phishing emails to your own organization's users (with written authorization) to measure and improve their ability to spot real attacks. Building and running one teaches you how phishing works from the defender's side — and why training, not punishment, is what actually reduces click rates.

## Core concepts

- **Explicit authorization** — Simulations run only against your own organization with documented management approval, defined scope, and a clear policy; anything else is not a simulation.
- **No credential harvesting** — Defensive simulators track clicks and report-rate, but never collect or store real passwords; landing pages redirect to training, and any submitted data is discarded.
- **Phishing indicators** — The tells training teaches: mismatched sender domains, urgency language, unexpected attachments/links, and lookalike domains — your templates should model these realistically.
- **Report rate over click rate** — The metric that matters is how many users report the phish to security, not just how many clicked; a good program optimizes for reporting.
- **Training, not shaming** — Immediate, constructive micro-training on click ("here's what gave it away") beats punitive approaches, which just teach people to hide mistakes.
- **DMARC/SPF/DKIM** — The email authentication stack that lets your simulator's test domain (and your real domain) prove legitimacy, and lets you demonstrate spoofing defenses.
- **Program measurement** — Baseline click rate, then track improvement across campaigns; the goal is a downward trend and faster reporting times, campaign over campaign.

## How it works

A tool like GoPhish runs an admin web UI where you build a campaign from four pieces: an email template (the lure, with tracking pixel and personalized link), a landing page (clearly marked as a simulation, linking to training material), a sending profile (SMTP config for your test domain), and a target group (imported user list). When launched, it sends the emails, records opens/clicks/submits per user, and generates a report.

Your build work is the surrounding program: deploying GoPhish in an isolated lab, authoring realistic-but-safe templates based on real-world phish patterns, configuring your mail infrastructure so simulations don't get silently eaten by filters (or worse, leak outside scope), and building the metrics dashboard that turns raw events into a training program with trend lines.

## Build milestones

1. Deploy GoPhish in an isolated lab and run a first campaign against test mailboxes you control, end to end.
2. Author three safe templates modeled on common real lures (password-reset, HR notice, package delivery) with clear simulation labeling on the landing page.
3. Configure SPF/DKIM/DMARC on your test domain and verify how authentication results appear in the received headers.
4. Build a reporting dashboard: per-campaign click rate, report rate, time-to-report, and trend lines across campaigns — with no credential data stored anywhere.
5. Design the training loop: instant micro-training on click, monthly metrics review, and targeted follow-up for repeat clickers — documented as a reusable program playbook.

## Best resources

- [GoPhish](https://github.com/gophish/gophish) — The open-source phishing simulation framework; the standard tool for defensive exercises.
- [GoPhish Documentation](https://docs.getgophish.com) — Campaign setup, templates, landing pages, and API usage.
- [CISA — Avoiding Social Engineering and Phishing Attacks](https://www.cisa.gov/news-events/news/avoiding-social-engineering-and-phishing-attacks) — The government guidance your training content should align with.
- [Anti-Phishing Working Group (APWG)](https://apwg.org/) — Industry research and eCrime reports on current phishing trends to base scenarios on.

## Stretch ideas

- Add SMS/voice (vishing) simulation scenarios to the program, since attackers increasingly move off email.
- Build a "report phish" button workflow for your mail client and measure how it changes report rates vs. forwarding to IT.
