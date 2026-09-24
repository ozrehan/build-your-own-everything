---
title: "Status Page"
category: "devops-infra"
difficulty: "beginner"
tags: [monitoring, uptime, incidents]
related: [metrics-monitor, log-aggregator, notification-fanout]
---

# Status Page

When your service goes down, users don't check your logs — they check your status page. A status page combines automated health checks (is the API up? what's the p99?) with human-written incident updates on a public page, plus subscriber notifications. Building one teaches you the two halves of incident communication: the probing infrastructure that detects problems, and the editorial workflow that keeps users informed without causing panic.

## Core concepts

- **Components, not just "up/down"** — a status page lists components (API, Website, Database, Email delivery) each with its own status. Granularity matters: "API degraded, website fine" is actionable; a single red banner is not.
- **Incident lifecycle** — investigating → identified → monitoring → resolved. Each transition is a public update with a timestamp. The discipline of updating at every transition is what builds trust; silence during an outage destroys it.
- **Active probing vs passive metrics** — status pages typically run synthetic checks (HTTP probes from multiple regions every minute) rather than trusting internal metrics, because the page must reflect the *user's* experience, including DNS and CDN failures your dashboards can't see.
- **Uptime math and SLAs** — "99.9% uptime" means 43 minutes of downtime per month. Computing it requires defining what counts (scheduled maintenance usually excluded) and handling partial degradation honestly — the credibility of the page rests on this math.
- **Subscriber notifications** — users subscribe per-component via email, SMS, webhook, or RSS; incident updates fan out automatically. Subscription granularity ("notify me only about the API") is what makes notifications useful instead of noise.
- **Incident communication templates** — pre-written shells ("We are investigating reports of <symptom> affecting <component>...") so responders aren't composing prose under pressure. Atlassian's templates are the industry reference.
- **Postmortems and history** — past incidents stay visible with timelines and postmortem links. A status page that hides history looks dishonest; one that shows resolved incidents with honest write-ups builds long-term trust.

## How it works

A prober fleet runs on a schedule (every 30-60s): for each component, it issues synthetic checks — HTTP requests to endpoints, TCP connects, DNS lookups — from one or more regions, recording latency and success. Results feed a rolling window that computes current status (operational / degraded / outage) per component using thresholds (e.g. 3 consecutive failures = outage) to avoid flapping on single blips.

The incident workflow is human-driven: an on-call engineer creates an incident, selects affected components and severity, and posts updates through the lifecycle; each update is timestamped, rendered on the public page, and fanned out to subscribers of those components via their chosen channels. Uptime percentages are computed from the probe history per component per day, and a separate scheduled-maintenance flow lets teams announce upcoming downtime in advance. Everything — probes, incidents, updates — is append-only history.

## Build milestones

1. Build a prober: check a list of HTTP endpoints every minute from your machine, store results in SQLite, and render a simple public page showing current status per component.
2. Add incident management: create/update/resolve incidents with templated messages, per-component status overrides, and a public timeline of past incidents.
3. Implement subscriber notifications (email + webhook) per component, multi-region probing (run probers in 2+ locations and require agreement for "outage"), and uptime percentage computation.
4. Add scheduled maintenance announcements, a public API (so other tools can post incidents), RSS feeds, and status badges embeddable in other sites' READMEs.

## Best resources

- [Atlassian — Incident communication templates](https://www.atlassian.com/incident-management/postmortem/templates) — the industry-standard templates and postmortem format; the editorial half of your status page.
- [Cachet](https://cachethq.io/) — the leading open-source status page; its component/incident/metric model is the reference data model to copy.
- [Uptime Kuma](https://github.com/louislam/uptime-kuma) — a self-hosted prober with 90+ monitor types and a clean UI; study its check scheduling and notification integrations.
- [Better Stack — Status pages](https://betterstack.com/status-pages) — modern hosted status pages with incident automation; good for seeing how probing, on-call, and public comms integrate.

## Stretch ideas

- Add automatic incident creation: when probers detect an outage, draft an incident (human confirms the messaging before it goes public).
- Implement status-page-as-code: define components and checks in YAML, versioned in Git, with the page generated from it.
- Build a public API compatibility layer so existing uptime tools can push metrics into your page, like hosted providers' metric integrations.
