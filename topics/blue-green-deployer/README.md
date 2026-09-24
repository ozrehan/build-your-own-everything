---
title: "Blue-Green Deployer"
category: "devops-infra"
difficulty: "intermediate"
tags: [deployment, devops, zero-downtime]
related: [tcp-load-balancer, feature-flag-service, ci-runner]
---

# Blue-Green Deployer

Deploying usually means replacing the running version in place and hoping. Blue-green deployment keeps two identical environments — blue (live) and green (idle) — deploys the new version to the idle one, verifies it, then flips the router to switch all traffic at once. Building one teaches you zero-downtime deployment mechanics: health-gated promotion, instant rollback (just flip back), and why the database is always the hard part.

## Core concepts

- **Two environments, one router** — blue and green are full copies of the production stack; a load balancer or reverse proxy decides which one receives traffic. The deploy target is always the idle environment, so users never see a half-updated system.
- **Smoke tests before promotion** — the new environment gets traffic only after automated checks pass: health endpoints, a synthetic transaction suite, maybe a slice of mirrored real traffic. Promotion is a decision, not a hope.
- **Instant rollback** — if the new version misbehaves after cutover, flipping the router back takes seconds and requires no rebuild. Rollback being trivial is the entire point; it changes the psychology of deploying.
- **The database problem** — code can be blue-green, but the database is shared. Safe pattern: make schema changes backward-compatible first (additive only — new nullable columns), deploy code that works with both schemas, then clean up. Destructive migrations break blue-green.
- **Canary vs blue-green** — canary shifts a percentage of traffic gradually; blue-green switches 100% at once after validation. Canary catches subtle issues with less blast radius; blue-green is simpler and rollback is cleaner. Real deployers offer both.
- **Immutable infrastructure** — never patch the live environment; always build a fresh one and switch. Immutability kills configuration drift and makes "what's running?" a question with a definitive answer.
- **Promotion gates** — manual approval steps, metric-based analysis (error rate below X for 5 minutes), or both. Gates turn deployment from a script into a controlled process with explicit go/no-go decisions.

## How it works

The deployer tracks which environment is live (via the router's config) and treats the other as the deploy target. A deployment has phases: (1) provision/build the new version into the idle environment — new containers, new config, migrations applied in backward-compatible form; (2) run health checks and smoke tests against the idle environment's private endpoint; (3) optionally warm it with mirrored production traffic; (4) on passing gates, atomically update the router to send 100% of traffic to the new environment; (5) keep the old environment warm for a cooldown period as the instant-rollback target, then tear it down or mark it idle.

State is a small state machine per deployment (provisioning → testing → promoting → live → retired) persisted so a crashed deployer can resume. Rollback is a single router update back to the previous environment, executable even mid-promotion. All router changes are versioned and logged, because the flip is the most consequential operation in the system.

## Build milestones

1. Build a deployer for a toy app with two directories (`blue/`, `green/`) and an nginx/haproxy config it rewrites to flip traffic; deploy = rsync new code to idle env + flip.
2. Add health-gated promotion: the deployer polls `/health` on the idle environment and runs a smoke-test script; promotion happens only if everything passes.
3. Implement the deployment state machine with persistence, cooldown (keep old env for 30 min), one-command rollback, and a CLI showing which env is live.
4. Add container-based environments (build fresh images per deploy), metric-based auto-promotion gates wired to your metrics monitor, and database migration safety checks that refuse destructive migrations.

## Best resources

- [Martin Fowler — BlueGreenDeployment](https://martinfowler.com/bliki/BlueGreenDeployment.html) — the original pattern description: why two environments, the router flip, and the database caveats, in a few dense pages.
- [Kubernetes Deployments documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) — rolling updates, readiness gates, and rollback semantics; the mainstream alternative strategy to compare against.
- [Argo Rollouts documentation](https://argo-rollouts.readthedocs.io/en/stable/) — blue-green and canary as Kubernetes-native controllers with analysis runs and automated promotion; the state of the art to study.
- [Martin Fowler — CanaryRelease](https://martinfowler.com/bliki/CanaryRelease.html) — the companion pattern to blue-green: gradual traffic shifting and how it differs in blast radius and rollback; read both to choose wisely.

## Stretch ideas

- Add canary support: shift traffic in 10% steps with automatic rollback if error rates spike, reusing your service mesh sidecar for weighted routing.
- Implement database migration guardrails: parse migration files and reject non-backward-compatible changes (dropped columns, renames) before deploy.
- Build deploy previews: spin up a green environment per pull request with its own URL, torn down on merge.
