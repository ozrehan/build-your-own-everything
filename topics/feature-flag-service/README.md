---
title: "Feature Flag Service"
category: "devops-infra"
difficulty: "beginner"
tags: [feature-flags, deployment, experimentation]
related: [blue-green-deployer, config-management, status-page]
---

# Feature Flag Service

Deploying code and releasing a feature are different events — feature flags are what separates them. A flag service lets you wrap new code in `if (flags.isEnabled("new-checkout", user))`, then turn it on for 1% of users, your team, or everyone, without redeploying. Building one teaches you evaluation semantics (targeting rules, rollouts, bucketing), the client SDK design, and why flags are a deployment-safety tool first and an A/B testing tool second.

## Core concepts

- **Kill switches** — the original and most important use: a flag that instantly disables a misbehaving feature in production. Every flag should be designed so "off" is the safe state; this alone justifies the whole system.
- **Targeting rules** — ordered rules evaluated top-down: "team@company.com → on", "country == DE → off", "default → 10% rollout". First match wins. Rule ordering and explicit defaults prevent the "who actually sees this?" confusion.
- **Percentage rollouts and sticky bucketing** — a user is hashed (`hash(flag_key + user_id) % 100`) to a bucket 0-99; rollout to N% enables buckets below N. The hash makes assignment stable across requests and deploys — the same user always gets the same experience.
- **Flag evaluation performance** — flags are checked in hot request paths, so evaluation must be microseconds: flags cached in memory, refreshed on a background interval, with a local default if the service is unreachable. Never block a request on the flag service.
- **Flag lifecycle and tech debt** — flags are meant to be temporary; permanent flags become invisible configuration. Real systems track flag age, owner, and stale-flag reports — "this flag hasn't changed in 18 months, can we remove it?"
- **Audit trail** — who turned what on, when, and to whom. Flag changes are production changes; the audit log is what lets you answer "what changed at 2:14am?" during an incident.
- **Experimentation vs operational flags** — operational flags (kill switches, rollouts) need instant propagation and simple semantics; experimentation flags need consistent bucketing and exposure logging for statistical analysis. One system serves both, but the requirements differ.

## How it works

Flag definitions live in the service's store: each flag has a default value, an ordered list of targeting rules (attribute conditions → value or rollout percentage), and metadata (owner, created date). SDKs in each application fetch all flag definitions on startup and poll for changes every N seconds (or receive SSE/push updates), keeping an in-memory copy.

Evaluation is pure and local: `isEnabled("new-checkout", context)` walks the rules in order, evaluating conditions against the provided context (user ID, email, country, plan tier). For percentage rules it computes the sticky hash of flag key + context key and compares against the threshold. Results are returned in microseconds with no network call. Flag change events are exposed to the application (for cache invalidation or logging), and every change made through the admin UI/API is appended to the audit log with the actor and timestamp.

## Build milestones

1. Build an in-memory flag evaluator: flags with on/off state and percentage rollouts using sticky hashing, tested for stable bucketing across evaluations.
2. Add a service with a REST API (CRUD flags, targeting rules with attribute conditions), SDK polling with local caching, and safe defaults when the service is down.
3. Build an admin UI showing all flags, their current rollout state, and an audit log of every change with actor and timestamp.
4. Add rule types (email domain, country, gradual rollout schedules), webhook notifications on flag changes, and a stale-flag report flagging flags untouched for 90+ days.

## Best resources

- [Martin Fowler — Feature Toggles](https://martinfowler.com/articles/feature-toggles.html) — the definitive taxonomy: release toggles vs experiment toggles vs ops toggles vs permission toggles, and how to manage their lifecycles.
- [OpenFeature](https://openfeature.dev/) — the CNCF standard API for feature flagging; design your SDK against it and you learn the industry's agreed evaluation semantics.
- [Unleash](https://www.getunleash.io/) — the leading open-source flag service; its activation strategies and constraint model are the reference implementation to study.
- [LaunchDarkly documentation](https://docs.launchdarkly.com/home/) — targeting rules, percentage rollouts, and flag prerequisites from the commercial pioneer; excellent for edge cases in evaluation order.

## Stretch ideas

- Add scheduled rollouts: "ramp from 5% to 100% over 7 days" with automatic progression and pause-on-alert integration with your metrics monitor.
- Implement flag prerequisites: flag B can only evaluate true if flag A is on, enabling safe multi-flag feature launches.
- Build exposure logging for experiments: log every flag evaluation with context hash so data teams can compute experiment results without extra instrumentation.
