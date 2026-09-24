---
title: "Process Orchestrator"
category: "devops-infra"
difficulty: "intermediate"
tags: [processes, supervision, orchestration]
related: [init-system, cron-scheduler, metrics-monitor]
---

# Process Orchestrator

systemd, supervisord, and PM2 all answer one question: how do you keep a set of long-running processes alive, ordered, and observable? A process orchestrator (supervisor) starts processes from a config file, restarts them when they die, captures their logs, and shuts them down cleanly. Building one is a masterclass in Unix process management — fork, signals, exit codes, and the double-fork dance are the entire curriculum.

## Core concepts

- **Supervision trees** — processes are organized in a tree where a supervisor watches its children; if a child dies unexpectedly, the supervisor restarts it according to a policy. Erlang/OTP formalized this, and systemd units are the same idea in a flatter form.
- **Restart policies and backoff** — `always`, `on-failure`, `unless-stopped`, combined with exponential backoff, prevent a crashing process from spinning the CPU in a tight restart loop (the "flapping" problem).
- **Signals as the control plane** — `SIGTERM` asks a process to shut down gracefully, `SIGKILL` ends it unconditionally, `SIGHUP` conventionally means "reload config". A supervisor must forward signals and implement a kill escalation: TERM, wait, then KILL.
- **Reaping zombies** — when a child exits, the parent must `waitpid()` to collect its exit status, or it becomes a zombie. A supervisor is typically the subreaper (`PR_SET_CHILD_SUBREAPER`) so orphaned grandchildren still get reaped.
- **Startup ordering and readiness** — `After=`/`Requires=` express dependency order, but order isn't readiness: real systems wait on a health check (open port, HTTP endpoint, "ready" file) before starting dependents, otherwise races are guaranteed.
- **Stdout/stderr capture and log rotation** — the supervisor's children inherit pipes from the supervisor, which timestamps, prefixes, and rotates log files; this is why `journalctl` and supervisord logs exist instead of everyone writing their own rotation.
- **Idempotent converge loop** — like Terraform for processes: read desired config, compare against actual running state, and take minimal actions (start missing, stop extra, restart changed). Re-running the loop with no changes must be a no-op.

## How it works

The orchestrator reads a declarative config (TOML/YAML or unit files) describing each service: command, working directory, environment, restart policy, dependencies, health check. On start it topologically sorts services by dependency, then for each one forks a child: the child calls `setsid()` to detach, redirects stdio to pipes owned by the supervisor, applies resource limits, and `exec()`s the target binary.

The supervisor's main loop is an event loop around `SIGCHLD` (a child changed state) plus timers. When a child exits, the loop reaps it with `waitpid`, logs the exit code, consults the restart policy and backoff timer, and relaunches. Health checks run on a separate timer; a service that stops passing checks is treated as failed and restarted. Shutdown reverses the dependency order: send `SIGTERM`, wait the grace period, escalate to `SIGKILL`, then reap.

## Build milestones

1. Build a supervisor that reads a TOML config of services, starts each with `fork`+`exec`, reaps exits with `waitpid`, and restarts them with exponential backoff. Capture stdout to per-service log files.
2. Add graceful shutdown (TERM → wait 10s → KILL), signal forwarding, `SIGHUP` config reload without restarting healthy services, and a CLI (`start|stop|restart|status`).
3. Add dependency ordering, TCP/HTTP health checks as the readiness gate, and log rotation by size/time.
4. Implement the converge loop with hot config diffing (restart only services whose config changed), resource limits via cgroups, and a socket-based status API that a dashboard can poll.

## Best resources

- [systemd.service man page](https://www.freedesktop.org/software/systemd/man/systemd.service.html) — the definitive reference for restart policies, dependencies, and sandboxing options; the spec your orchestrator reimplements.
- [Supervisor documentation](http://supervisord.org/) — the classic Python process supervisor; its architecture (XML-RPC API, event listeners, process states) maps directly onto a hand-built design.
- [HashiCorp Nomad documentation](https://developer.hashicorp.com/nomad/docs) — a cluster-level orchestrator; its task driver and rescheduling model shows how process supervision scales to many machines.
- [Erlang/OTP Supervision Principles](https://www.erlang.org/doc/design_principles/sup_princ.html) — the original supervision-tree theory: restart strategies (`one_for_one`, `rest_for_one`) and why supervisors should do nothing but supervise.
- [PM2 documentation](https://pm2.keymetrics.io/docs/usage/quick-start/) — a widely used Node process manager; good for seeing the CLI/status/log UX a supervisor needs.

## Stretch ideas

- Add bin-packing across machines: a scheduler that places services on nodes by CPU/memory requests, the first step toward a mini-Kubernetes.
- Implement rolling restarts with health-gated batches for zero-downtime deploys of multi-instance services.
- Add an event bus: emit structured events (start, crash, OOM) that webhooks or alerting integrations can subscribe to.
