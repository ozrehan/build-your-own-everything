---
title: "Build Your Own Actor-Model Concurrency"
category: "programming-languages"
difficulty: "intermediate"
tags: [concurrency, runtimes, systems]
related: [memory-allocator, bytecode-virtual-machine, repl-design]
---

# Build Your Own Actor-Model Concurrency

The actor model structures concurrent programs as isolated actors that communicate only by sending asynchronous messages — no shared memory, no locks, and no data races by construction. It's the foundation of Erlang's legendary reliability at Ericsson and of Elixir and Akka. Building a small actor runtime yourself — spawn, send, selective receive, supervision — makes the "let it crash" philosophy concrete instead of aspirational.

## Core concepts

- **Actors as isolated processes** — each actor owns private state and a mailbox; message passing is the only interaction, so there's no shared mutable state to corrupt.
- **Asynchronous send** — `Pid ! Msg` never blocks; the sender continues immediately, decoupling throughput from the receiver's speed.
- **Mailbox plus selective receive** — incoming messages queue in the mailbox; `receive` scans for the first message matching a pattern, leaving the rest queued.
- **Supervision trees** — actors link into a hierarchy; when a child crashes, its supervisor restarts it (one-for-one or one-for-all strategies). This is "let it crash" engineering.
- **Location transparency** — a pid works identically locally or across the network; distribution becomes a deployment detail rather than a rewrite.
- **Backpressure and bounded mailboxes** — unbounded queues hide overload until memory dies; real systems bound mailboxes and slow or shed producers.

## How it works

The runtime is a scheduler over lightweight processes: each actor is a closure (or stack) plus a message queue. `spawn` creates an actor and returns its pid; `send` enqueues a message in the target's mailbox and marks it runnable; `receive` scans the mailbox for the first message matching one of its patterns, suspending the actor if none matches yet. Links propagate exit signals: when an actor dies, linked processes get a message they can trap or crash on, and supervisors use this to restart children per their strategy. A preemptive scheduler — reduction counting is the classic Erlang approach — guarantees one busy actor can't starve the rest.

## Build milestones

1. Build a single-threaded runtime: spawn actors as closures with mailboxes, implement `send`/`receive` with pattern matching, and get ping-pong working.
2. Add a preemptive scheduler (reduction counting or time-slicing) so one busy actor can't starve others; demonstrate with a spinner plus an echo actor.
3. Implement links, monitors, and exit signals; build a supervisor that restarts crashed children with a one-for-one strategy.
4. Add selective receive with timeouts (`after` clauses) and registered names; implement a small request/reply abstraction in the gen_server style.
5. Go concurrent: run the scheduler on multiple OS threads with lock-free mailbox queues, or add distribution over TCP with location-transparent pids.

## Best resources

- [Erlang: Concurrent Programming](https://www.erlang.org/docs/27/system/conc_prog) — the official docs on processes, message passing, and the concurrency primitives your runtime must implement.
- [Erlang: Getting Started — Concurrency](http://erlang.org/documentation/doc-6.0/doc/getting_started/conc_prog.html) — the classic tutorial introduction: spawn, send, and receive with examples.
- [Erlang Programming/Processes — Wikibooks](https://en.wikibooks.org/wiki/Erlang_Programming%2FProcesses) — a worked walkthrough of processes and message diagrams, including a process-chain example.
- [Concurrent Programming in Erlang [pdf]](https://github.com/MuhamedHabib/ebooks/raw/refs/heads/master/concurrent_programming_erlang.pdf) — Armstrong and Virding's book text (mirrored): the original exposition of the actor model as Erlang practices it.

## Stretch ideas

- Implement hot code reloading: swap an actor's behavior module without dropping its mailbox.
- Add distributed node connections Erlang-style and measure message latency across machines.
- Build a tiny OTP on your runtime: supervisor, gen_server, and application behaviors as libraries.
