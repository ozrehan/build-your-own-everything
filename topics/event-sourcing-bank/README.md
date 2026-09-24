---
title: "Event Sourcing (Bank)"
category: "distributed-data"
difficulty: "intermediate"
tags: [event-sourcing, ddd, banking]
related: [cqrs-read-models, write-ahead-log, message-queue]
---

# Event Sourcing (Bank)

A bank ledger never erases a transaction — your balance is just the sum of everything that ever happened. Event sourcing applies that idea to software: store the immutable history of events (`Deposited $100`, `Withdrew $40`) instead of the current state, and derive state by replaying. Building a bank this way teaches you why "the log is the truth" changes debugging, auditing, and time travel.

## Core concepts

- **Events as the source of truth** — Instead of storing `balance = 60`, you store the facts that produced it. State becomes a cached interpretation of history, which means it can always be rebuilt, corrected, or reinterpreted.
- **Immutability** — Events are never updated or deleted; they are facts about the past. Corrections are new events (`WithdrawalReversed`), so the full story — including mistakes — is preserved, exactly like accounting.
- **Event store** — An append-only log partitioned into per-aggregate streams (one stream per bank account), each with a sequence number. Appends are the only write operation, which makes the store simple and fast.
- **Aggregate** — The consistency boundary: a bank account that validates commands ("withdraw $50") against its current state and emits events. Optimistic concurrency (expected version number on append) prevents two writers from corrupting one account.
- **Replay / rehydration** — Loading an aggregate means reading its event stream and folding events into state. This is also your migration story: change the fold logic and replay to get a new interpretation of the same history.
- **Snapshots** — For long-lived aggregates with thousands of events, periodically persist the folded state so replays start from the snapshot plus recent events instead of from account opening.
- **Projections** — Secondary views (monthly statements, fraud-detection feeds) built by subscribing to the event log. The bank's "current balances" table is just one projection among many.

## How it works

A `Withdraw` command arrives at the account aggregate, which loads its state by replaying its event stream (or snapshot + tail). The aggregate validates the command against business rules — sufficient funds, account open — and, if valid, appends a `FundsWithdrawn` event with the next expected sequence number to the account's stream. If another writer appended first, the version check fails and the command retries against fresh state. Readers never query the aggregate directly: projections subscribe to the global event log and maintain read models like "balances per account" or "all transactions this month." To answer "what was the balance on March 3rd?", replay the stream up to that date — time travel falls out of the design for free.

## Build milestones

1. Build the event store: an append-only log with per-account streams, sequence numbers, and optimistic concurrency (append fails if the expected version doesn't match).
2. Build the account aggregate: commands (`OpenAccount`, `Deposit`, `Withdraw`) validated against replayed state, emitting events; demonstrate two concurrent withdrawals where one correctly fails instead of overdrawing.
3. Add projections: a balances read model and a transaction-history read model, both updated by subscribing to the event log; show the write model and read models evolving independently.
4. Add snapshots and time travel: snapshot every 100 events, rebuild state from snapshot + tail, and implement "balance as of date X" by replaying to a cutoff.
5. Impressive end state: a working bank API (open/deposit/withdraw/transfer between accounts) where transfers emit events on both accounts atomically-ish via a saga, every state is rebuildable from the log, and an auditor endpoint can replay any account's full history.

## Best resources

- [Event Sourcing — Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html) — The definitive introduction: what it is, when it pays off, and the honest list of drawbacks.
- [EventStoreDB](https://www.eventstore.com/) — The database built for event sourcing; its docs teach streams, projections, and subscriptions as first-class concepts.
- [Event-driven architecture — Wikipedia](https://en.wikipedia.org/wiki/Event-driven_architecture) — The broader context: how event-sourced systems fit into event-driven design.
- [CQRS — Martin Fowler](https://martinfowler.com/bliki/CQRS.html) — Event sourcing's usual partner; explains why the write model and read models want to be separate things.

## Stretch ideas

- Implement a transfer saga with compensating events (`TransferFailed` → reverse the debit) and chaos-test it by killing the process mid-transfer.
- Add schema evolution: change an event's shape in version 2 and write an upcaster so old events still replay correctly.
