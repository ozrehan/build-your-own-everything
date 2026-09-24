---
title: "Chaos Monkey Lite"
category: "devops-infra"
difficulty: "beginner"
tags: [chaos-engineering, resilience, testing]
related: [status-page, metrics-monitor, process-orchestrator]
---

# Chaos Monkey Lite

Netflix's Chaos Monkey randomly kills production servers — on purpose. The idea: if failures are constant and small, your system learns to survive them, and engineers stop fearing deploys. Chaos engineering is the discipline of running controlled failure experiments to find weaknesses before real outages do. Building a lite version (random process kills, network latency injection, disk-fill drills) teaches you the resilience patterns — retries, bulkheads, graceful degradation — that separate systems that survive from systems that page.

## Core concepts

- **Hypothesis-driven experiments** — chaos isn't random destruction; each experiment states a hypothesis ("killing one API instance won't raise p99 above 500ms") and a blast radius. You run it, measure, and either confirm resilience or find a bug. No hypothesis, no experiment.
- **Blast radius control** — experiments are scoped by service, percentage of instances, time window, and automatic abort conditions. The discipline is in the guardrails: a chaos tool without an abort button is just sabotage.
- **Steady-state definition** — before breaking things, define "normal": error rate < 0.1%, p99 < 300ms. The experiment's job is to prove the system returns to steady state. Without a baseline, you can't tell if the experiment did anything.
- **Failure injection types** — process kills (crash), network latency/packet loss (degraded dependency), disk fill and CPU hog (resource exhaustion), DNS failures (dependency disappearance). Each exposes a different class of missing resilience.
- **Game days** — scheduled, team-wide chaos sessions where everyone watches dashboards together. The social practice matters as much as the tooling: game days train the incident-response muscle and surface tribal knowledge.
- **Principles of Chaos Engineering** — the field's founding document: build a hypothesis around steady state, vary real-world events, run experiments in production, automate continuously, minimize blast radius. Worth reading in full.
- **Resilience patterns it validates** — timeouts, retries with backoff, circuit breakers, bulkheads (isolating failure domains), graceful degradation, and fast startup (so replacements come up quickly). Chaos finds which ones you forgot.

## How it works

The chaos controller reads an experiment schedule: which fault to inject, against which targets, when, and with what abort conditions. At the scheduled time it selects targets (e.g. randomly pick 1 of N API containers, or 10% of instances in a service group), verifies preconditions (steady-state metrics look normal, no ongoing incident, not in a freeze window), and injects the fault — SIGKILL a process, add 500ms latency via `tc`, fill a disk with a sparse file, or blackhole an egress IP with iptables.

During the experiment window it watches the abort conditions (error rate, latency SLOs from your metrics monitor); if any breach, it halts injection and restores immediately. After the window it removes the fault, waits for steady state to return, and records the result: hypothesis confirmed or violated, with links to the metrics. A weekly report shows experiment history and which services keep failing — that's your resilience roadmap.

## Build milestones

1. Build a "kill monkey": on a schedule, randomly SIGKILL one instance of a demo multi-instance service; verify the load balancer reroutes and no requests fail.
2. Add network faults: inject latency and packet loss with `tc`/`iptables` on a dependency, and confirm your service's timeouts and retries handle it.
3. Implement the experiment framework: hypothesis + steady-state checks + abort conditions wired to your metrics monitor, with a schedule and audit log of every injection.
4. Add game-day mode (coordinated multi-fault scenarios), automatic weekly reports of resilience gaps, and resource-exhaustion faults (CPU hog, disk fill).

## Best resources

- [Netflix Chaos Monkey](https://github.com/Netflix/chaosmonkey) — the original: how termination experiments are scheduled, scoped, and made safe in production.
- [Principles of Chaos Engineering](https://principlesofchaos.org/) — the field's manifesto: steady-state hypothesis, real-world events, production experiments, minimized blast radius. Short and essential.
- [LitmusChaos](https://litmuschaos.io/) — the CNCF chaos framework: experiment CRDs, probes for steady-state validation, and chaos result reporting; the modern reference architecture.
- [Jepsen](https://jepsen.io/) — Kyle Kingsbury's distributed-systems correctness testing; the rigorous extreme of failure injection, with analyses that read like detective stories.

## Stretch ideas

- Build a "dependency down" simulator: run your entire stack against mocked failures of each external dependency and generate a resilience scorecard.
- Add automatic experiment generation: mine past incidents for their failure mode and auto-create a chaos experiment that would have caught each one.
- Implement chaos in CI: run a short fault-injection suite against every pull request's preview environment before merge.
