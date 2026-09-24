---
title: "CQRS Read Models"
category: "distributed-data"
difficulty: "intermediate"
tags: [cqrs, read-models, architecture]
related: [event-sourcing-bank, document-store, full-text-search-index]
---

# CQRS Read Models

The data shape that makes writes safe (normalized, validated, one aggregate at a time) is rarely the shape that makes reads fast (denormalized, pre-joined, query-specific). CQRS — Command Query Responsibility Segregation — splits them: one model takes commands, separate models serve queries. Building the read-model side teaches you how projections turn an event log into query-optimized views.

## Core concepts

- **Command vs query separation** — Commands change state and can fail validation; queries just return data and never do. Once separated, each side can be optimized, scaled, and even stored differently without compromise.
- **Read model / projection** — A data structure purpose-built for one query pattern, maintained by folding events as they arrive: "orders per customer per month" is a table you update on every `OrderPlaced`, not a query you compute at request time.
- **Eventual consistency between models** — The read model lags the write model by the projection delay (milliseconds, usually). Your UI must tolerate "I just saved it, why don't I see it?" — the fundamental UX tradeoff of CQRS.
- **Multiple specialized models** — One event log can feed many read models: a relational table for the admin dashboard, a search index for product search, a cache for the hot homepage query. Each is disposable and rebuildable.
- **Replay to rebuild** — Because read models are pure functions of the event history, you can delete one and rebuild it from scratch — or build a brand-new model for a query nobody anticipated, over the full history.
- **Idempotent projection handlers** — A projector may see the same event twice (retries, replays). Handlers must be safe to re-run — e.g. keyed upserts rather than blind increments — or rebuilds will corrupt the model.
- **Query-side scaling** — Read models are just data, so they scale like any database: replicas, caches, even different engines per model, while the write side stays small and authoritative.

## How it works

The write side appends events to the log and does nothing else. Each read model runs a projector: a subscriber that reads the log from a stored checkpoint, applies each event to its own storage (SQL tables, a search index, an in-memory cache), and advances the checkpoint. A projector for "customer order summaries" handles `OrderPlaced` by upserting a row keyed by `(customer_id, month)` and handles `OrderCancelled` by adjusting it. Queries hit these precomputed models directly — no joins across aggregates at request time, no touching the write model. When a new reporting need appears, you write a new projector, replay history into it, and it catches up to live tail within minutes.

## Build milestones

1. Build one projector: subscribe to an event log (from your event-sourcing bank or a fake one) and maintain a "balances" table in SQLite; serve balance queries from it instead of replaying.
2. Add a second, different read model over the same events — e.g. a "largest transactions this week" list — proving one log feeds many models.
3. Handle the consistency gap: write an API that returns the write-side version with each command, and have the UI poll the read model until it catches up (read-your-writes without blocking).
4. Make projectors idempotent and rebuildable: add a checkpoint per projector, simulate duplicate delivery, then delete a read model and rebuild it by replaying from event zero.
5. Impressive end state: three read models (SQL balances, full-text searchable transaction descriptions, and a cached "top customers" leaderboard) all fed by one event log, with a dashboard showing each projector's lag in real time.

## Best resources

- [CQRS — Martin Fowler](https://martinfowler.com/bliki/CQRS.html) — The original bliki post: what CQRS is, what it isn't, and when the complexity is worth it.
- [CQRS Pattern — Microsoft Architecture](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) — The cloud architecture guide's treatment, with concrete guidance on splitting command and query stores.
- [EventStoreDB](https://www.eventstore.com/) — Its projections feature is literally CQRS read models as a database primitive; the docs show the pattern in its native habitat.
- [Event Sourcing — Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html) — The companion pattern: CQRS read models are most powerful when the write side is an event log.

## Stretch ideas

- Build a read model in a genuinely different engine (e.g. Elasticsearch-style inverted index) to feel why "one model per query shape" beats "one database for everything."
- Implement a "projector lag SLO" monitor that pages you when any read model falls more than N seconds behind the log.
