---
title: "Cron Scheduler"
category: "devops-infra"
difficulty: "beginner"
tags: [cron, scheduling, automation]
related: [process-orchestrator, ci-runner, backup-system]
---

# Cron Scheduler

`0 2 * * * /backup.sh` — five fields that have run the world's batch jobs for forty years. A cron scheduler reads schedule expressions, wakes up at the right moments, and executes commands reliably. Building one teaches you time-based scheduling from the ground up: parsing cron expressions, computing next fire times across timezones and DST, and the surprisingly deep problem of "run this exactly once even if the machine restarts".

## Core concepts

- **Cron expression syntax** — five (or six, with seconds) fields: minute, hour, day-of-month, month, day-of-week. `*/15` means "every 15", `1-5` ranges, `MON-FRI` names, and day-of-month vs day-of-week is OR, not AND — the classic gotcha.
- **Next-fire-time computation** — given "now" and an expression, find the next matching datetime by walking fields from largest to smallest, rolling over on overflow. Timezone-aware scheduling must handle DST gaps (2:30am doesn't exist on spring-forward) and folds (it happens twice on fall-back).
- **At-least-once vs exactly-once execution** — if the scheduler restarts mid-job, should the job re-run? Cron's answer is at-least-once with no memory: missed runs during downtime are simply skipped, which is why jobs must be idempotent.
- **Misfire handling** — when a scheduled time passes without execution (scheduler was down, system was asleep), policies decide: fire immediately on recovery, skip, or fire-and-continue. Quartz's misfire instructions are the canonical treatment.
- **Concurrency control** — what if a job takes longer than its interval? Options: allow overlap, skip if still running (with a lock), or queue. The wrong default here causes the legendary "900 backup processes" incident.
- **Distributed cron and leader election** — with multiple scheduler instances, only one may fire each job. A distributed lock (or leader election) around the fire moment prevents duplicate execution across the fleet.
- **Observability of scheduled work** — every run needs a recorded outcome: started, finished, exit code, duration, next scheduled time. Without a run history, "did the 2am job run?" is unanswerable — the reason cron's silent failures are infamous.

## How it works

The scheduler loads job definitions (command, schedule expression, timezone, concurrency policy) into memory and computes each job's next fire time. A single timer thread sleeps until the nearest fire time — waking once per minute is the classic cron approach; a priority queue of upcoming firings is more precise. When a fire time arrives, the scheduler checks the concurrency policy (acquire a lock; skip if held and policy says so), then spawns the job as a child process, capturing its output and exit code.

Each run is recorded in a history store with its scheduled time, actual start, end, and status. If the process is still running when the next fire time arrives, the policy decides: overlap, skip, or wait. On restart, the scheduler recomputes next fire times from "now" (skipping anything missed during downtime, per the misfire policy) and resumes. For distributed setups, firing is wrapped in a lock acquisition against etcd/Redis so only one instance executes.

## Build milestones

1. Write a cron expression parser (5 fields, ranges, steps, lists, names) plus a `next_fire_time(expr, from)` function, tested against known edge cases including DST transitions.
2. Build the scheduler loop: load jobs from a YAML file, fire commands as child processes at the right times, capture output/exit codes, and keep a run history you can query.
3. Add concurrency policies (skip-if-running via lock files), misfire handling on restart, and email/webhook notifications on failure.
4. Implement distributed mode: multiple scheduler instances with a Redis/etcd lock so each job fires exactly once, plus a web UI showing upcoming runs and past history.

## Best resources

- [crontab(5) man page](https://man7.org/linux/man-pages/man5/crontab.5.html) — the authoritative reference for cron field syntax, special strings (`@daily`), and environment handling.
- [systemd.timer man page](https://www.freedesktop.org/software/systemd/man/systemd.timer.html) — the modern alternative: calendar expressions, monotonic timers, `Persistent=true` for catch-up runs, and accuracy tradeoffs.
- [robfig/cron](https://github.com/robfig/cron) — the standard Go cron library; its parser and scheduler are small enough to read end-to-end and directly inform your design.
- [Quartz Scheduler tutorial](https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/) — jobs, triggers, job stores, clustering, and misfire instructions; the enterprise-grade treatment of everything in this guide.

## Stretch ideas

- Add calendar-aware scheduling: skip holidays, run on "last business day of month", with a pluggable calendar provider.
- Implement job dependencies: build a DAG of jobs where downstream jobs fire only after upstream jobs succeed, like a mini-Airflow.
- Add runaway detection: kill jobs exceeding their historical p99 duration and alert, catching the "hung backup" class of failures.
