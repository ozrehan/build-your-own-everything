---
title: "Workflow Engine"
category: "distributed-data"
difficulty: "advanced"
tags: [workflows, orchestration, durable-execution]
related: [cron-scheduler, etl-pipeline, message-queue]
---

# Workflow Engine

"Charge the card, then book the flight, then email the ticket — and if step 2 fails after step 1 succeeded, refund." Multi-step processes that must survive crashes, retries, and human-speed delays are workflows, and the engine that runs them durably is one of the most useful systems you can build. Doing it yourself teaches you event sourcing, deterministic replay, and why "just use a queue and hope" breaks down.

## Core concepts

- **Durable execution** — The engine's promise: your workflow code can sleep for days, crash mid-step, and resume exactly where it left off. Progress is persisted, not held in memory.
- **Activities** — The side-effecting steps (charge card, send email) executed as separate, retryable units. Keeping side effects in activities — not in workflow code — is what makes replay safe.
- **Deterministic replay** — Workflow code itself must be deterministic: on recovery, the engine re-runs it from the start, and recorded activity results are fed back instead of re-executed. A random number or `now()` in workflow code breaks this contract.
- **Event-sourced history** — Every workflow's execution is an append-only history of events (activity scheduled, activity completed, timer fired). State is derived by replay; the history is the truth, exactly like event sourcing.
- **Timers as events** — "Sleep 30 days" isn't a thread sleeping — it's a timer event persisted in history, and the workflow wakes when the timer fires, even if every worker restarted in between.
- **Idempotent activities** — Because a crashed activity may have actually completed, activities must be safe to retry: idempotency keys on the charge API, dedupe on the email send. The engine guarantees at-least-once execution of activities.
- **Versioning / patching** — Workflows live for months; code changes underneath them. Engines need a story for running old histories against new code (version markers, patch APIs), or a deploy breaks in-flight workflows.

## How it works

You write workflow code in a normal language, calling activities and timers through the SDK. The SDK doesn't execute directly — it records each call as an intent. The engine persists a history: `WorkflowStarted`, `ActivityScheduled(charge-card)`, and when the activity worker completes it, `ActivityCompleted(result)`. If the workflow worker crashes, a new one loads the history and replays the workflow function: every SDK call that already has a recorded result returns that result instead of re-running. New intents (a timer, the next activity) are appended as fresh events. The workflow is thus a deterministic fold over its own history — crash-safe, migratable between workers, and fully auditable.

## Build milestones

1. Build the history model: define event types (started, activity scheduled/completed/failed, timer fired) and a workflow function that, given a history, deterministically decides the next action.
2. Add an activity worker: a separate process that polls for scheduled activities, executes them with retries and timeouts, and reports results back into the history.
3. Implement replay recovery: kill the workflow worker mid-run, restart it, and show it resuming from history without re-executing completed activities.
4. Add durable timers and signals: "wait 24h or until the user approves" — persist the timer, survive restarts, and let external events (signals) wake the workflow early.
5. Impressive end state: an order-processing workflow (reserve inventory → charge → ship → notify, with compensation on failure) running across two worker processes, with a UI showing live history, the ability to kill -9 workers mid-flight without losing a single order, and versioned workflow code handling old and new histories.

## Best resources

- [Temporal](https://temporal.io/) — The leading open-source durable execution platform; its concepts docs are the clearest explanation of workflows vs activities anywhere.
- [Temporal Documentation](https://docs.temporal.io/) — Deep dives on event histories, replay determinism, versioning, and failure handling — the playbook for your implementation.
- [temporalio/temporal (GitHub)](https://github.com/temporalio/temporal) — The actual server source; invaluable when your engine's edge cases need a reference implementation.
- [Apache Airflow](https://airflow.apache.org/) — The DAG-based predecessor: great for understanding task orchestration, and a useful contrast for why durable *code* beats static DAGs for long-running processes.

## Stretch ideas

- Implement the saga/compensation pattern: each activity registers an undo action, and workflow failure triggers compensations in reverse order.
- Add workflow versioning with patch markers so you can deploy new workflow code while month-old workflow instances are still running.
