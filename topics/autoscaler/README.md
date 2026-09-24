---
title: "Autoscaler"
category: "devops-infra"
difficulty: "intermediate"
tags: [scaling, kubernetes, devops]
related: [metrics-monitor, process-orchestrator, tcp-load-balancer]
---

# Autoscaler

Traffic doubles at 9am; your service should double its capacity without a human being paged. An autoscaler watches metrics (CPU, request latency, queue depth) and adjusts replica counts up and down automatically. Building one teaches you control theory applied to infrastructure: the scaling algorithm, cooldowns to prevent flapping, and why scaling on the wrong metric causes spectacular oscillation.

## Core concepts

- **Horizontal vs vertical scaling** — horizontal adds more instances (replicas); vertical gives existing instances more CPU/RAM. Horizontal is the default for stateless services; vertical suits databases and single-threaded workloads. Good systems do both at different layers.
- **The scaling algorithm** — Kubernetes HPA's core: `desired = ceil(current * (currentMetric / targetMetric))`. If CPU is at 80% and target is 50%, you need ~1.6x replicas. Simple, proportional, and wrong in edge cases — which is why the rest of this list exists.
- **Cooldowns and stabilization** — scale-up should be fast, scale-down slow. After any scaling action, a cooldown (e.g. 5 min for down, 0-1 min for up) ignores further signals; downscale stabilization takes the max recommendation over a window. Without this, metrics noise causes flapping.
- **Choosing the right metric** — CPU is a lagging, noisy proxy for user pain; request queue depth or p99 latency often scales better. Custom metrics (queue length, active connections) beat resource metrics for most real workloads.
- **Min/max bounds and safety rails** — always clamp: a minimum for availability (never scale to zero unless designed for it), a maximum for cost and downstream protection. A runaway scaler without a max is how you get a $50k cloud bill.
- **Predictive vs reactive** — reactive scaling responds to current load (with unavoidable lag: new instances take minutes to warm); predictive scaling uses historical patterns or schedules (scale up before the 9am rush). The best systems blend both.
- **Cluster autoscaling vs pod autoscaling** — pod autoscalers change replica counts; cluster autoscalers add/remove whole nodes when pods can't be scheduled. They must coordinate, or they fight: pods scale up, nodes scale up, then both scale down in a loop.

## How it works

The autoscaler's control loop ticks every N seconds (15s in Kubernetes). Each tick it fetches the configured metrics for the target workload — from the metrics API for CPU/memory or a custom metrics adapter for application metrics like queue depth. It computes desired replicas with the proportional formula, applies per-metric results (taking the max across metrics — scale for the most constrained resource), then clamps to min/max bounds.

Before acting, it consults the stabilization logic: for scale-down, it looks back over the stabilization window and uses the highest recent recommendation, preventing a single quiet minute from killing half your fleet; for scale-up it generally acts immediately but respects the scale-up cooldown. If the decision differs from current replicas, it patches the workload's replica count and records the event. A separate cluster-level loop watches for unschedulable pods (scale nodes up) and underutilized nodes (cordon, drain, terminate — scale down), with its own longer cooldowns since node operations take minutes.

## Build milestones

1. Build a workload simulator (fake service with adjustable load) and a control loop that polls its CPU metric and adjusts replica count with the proportional formula, clamped to min/max.
2. Add scale-down stabilization windows, separate up/down cooldowns, and multi-metric support (take the max recommendation across CPU and queue depth).
3. Wire it to real metrics: point your autoscaler at your metrics monitor, scaling an actual containerized service on custom metrics.
4. Implement predictive scaling from historical data (yesterday's 9am pattern) and a cluster-level node scaler that adds/removes VMs based on pending pods.

## Best resources

- [Kubernetes Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) — the algorithm, stabilization windows, scaling policies, and multi-metric behavior; the spec your scaler implements.
- [KEDA documentation](https://keda.sh/) — event-driven autoscaling on 60+ scalers (queues, streams, cron); the best reference for custom-metric scaling done right.
- [Kubernetes Cluster Autoscaler](https://github.com/kubernetes/autoscaler) — node-level scaling: scale-up on unschedulable pods, scale-down of underutilized nodes; study its cooldowns and expander strategies.
- [Tirmazi et al. — Borg: The Next Generation (2020)](https://research.google/pubs/borg-the-next-generation/) — Google's longitudinal study of Borg including Autopilot vertical autoscaling in production; the empirical grounding for what actually works at scale.

## Stretch ideas

- Add cost-aware scaling: choose instance types and scale targets to minimize $/request, not just to meet latency SLOs.
- Implement scale-to-zero with fast cold starts for batch/event workloads, including request buffering during scale-up.
- Build a scaling simulator: replay historical traffic against different algorithms and cooldowns to tune policy without risking production.
