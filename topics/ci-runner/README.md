---
title: "CI Runner"
category: "devops-infra"
difficulty: "intermediate"
tags: [ci-cd, pipelines, automation]
related: [git-server, cron-scheduler, artifact-registry]
---

# CI Runner

Every push to a Git repo triggers invisible labor: checkout, install dependencies, run tests, build artifacts, deploy. A CI runner is the agent that does that labor — it picks up jobs from a queue, executes them in a clean environment, and reports results back. Building one demystifies the entire CI/CD world, because the "magic" of GitHub Actions or Jenkins is really just a queue, a worker loop, and logs streamed over a pipe.

## Core concepts

- **Pipeline as a DAG** — a pipeline is a directed acyclic graph of steps: each step runs a shell command in order, and steps can depend on each other's outputs. Parsing a YAML workflow file into this graph is half the job of a CI system.
- **Job queue and workers** — the server holds pending jobs; runners are workers that long-poll (or receive webhooks) for work, execute it, and post back status. This producer/consumer split is what lets one control plane drive hundreds of machines.
- **Ephemeral, isolated execution environments** — every job runs in a fresh container or VM so leftover state from a previous job can't poison the next. Reproducibility comes from destroying the environment after each run.
- **Artifacts and caching** — steps share data by uploading artifacts (test reports, built binaries) to object storage between steps; dependency caches survive between runs keyed by a hash of the lockfile, trading disk for speed.
- **Secrets masking** — secrets are injected as environment variables and any occurrence in logs is redacted before streaming. This single feature is why CI configs can be public while credentials stay private.
- **Webhooks and idempotency** — a push event arrives as an HTTP POST from the Git host; the server must handle duplicate and out-of-order deliveries without running the same job twice, so each run gets a unique id derived from commit + pipeline definition.
- **Exit codes and failure semantics** — a step fails when its process exits non-zero; `continue-on-error`, `if: failure()`, and step conditionals turn raw exit codes into a workflow language for retries and cleanup.

## How it works

The control plane receives a webhook from the Git host with the repo and commit SHA. It fetches the pipeline definition (e.g. `.ci.yml`), expands matrix jobs and conditionals, and pushes each job onto a FIFO queue persisted in a database so nothing is lost on restart. Each runner loops: claim a job (atomically marking it `running`), clone the repo at the pinned SHA, set up the environment (restore cache, export secrets), then execute steps in order, streaming each step's stdout/stderr line-by-line back to the server over a persistent connection.

Streaming is the interesting bit: the runner tags each log line with step and timestamp and sends it in chunks; the server appends to a log file and fans out to the web UI, so you watch builds in real time. When all steps finish, the runner uploads artifacts, stores cache entries, and reports the final status. The scheduler then evaluates the DAG — downstream jobs run only if their dependencies succeeded — until the pipeline completes or fails.

## Build milestones

1. Build a single-file runner that reads a YAML pipeline (steps as shell commands), clones a repo at a given SHA, runs the steps sequentially, and prints pass/fail with exit codes.
2. Split into server + runner: the server stores job definitions and exposes an HTTP API; the runner long-polls for jobs, executes them, and POSTs back status. Support webhook-triggered runs from a real Git push.
3. Add real-time log streaming (chunked POST or WebSocket), per-step status, artifact upload to local disk/S3, and dependency caching keyed by lockfile hash.
4. Support matrix builds (fan-out N jobs from one definition), `needs:` dependencies between jobs, and timeout/kill of runaway jobs. Run the whole thing as a self-hosted alternative on your own server.

## Best resources

- [GitHub Actions documentation](https://docs.github.com/en/actions) — the canonical reference for workflow syntax, events, expressions, and runners; the best mental model for what a CI system must implement.
- [GitLab CI/CD documentation](https://docs.gitlab.com/ee/ci/) — excellent pipeline architecture docs, including runners, artifacts, caching, and DAG pipelines.
- [Tekton Pipelines documentation](https://tekton.dev/docs/pipelines/) — a Kubernetes-native, container-per-step pipeline engine; great for seeing how steps become pods and results become files.
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html) — the classic essay on why CI exists and what practices (fast builds, single source repo, everyone commits daily) make it work.
- [Buildkite Agent documentation](https://buildkite.com/docs/agent/v3) — how a polling job runner, artifact upload, and agent hooks work in a hybrid SaaS/self-hosted setup.

## Stretch ideas

- Implement self-hosted autoscaling runners: spawn ephemeral containers per job and destroy them after, like GitHub's ephemeral runner mode.
- Add a pluggable "checks" API so external tools can post annotations onto specific lines of a diff, like real CI status checks.
- Build pipeline visualization: render the DAG with per-step timing, and detect the critical path to tell users which step dominates build time.
