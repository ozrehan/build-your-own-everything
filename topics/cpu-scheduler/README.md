---
title: "CPU Scheduler"
category: "operating-systems"
difficulty: "intermediate"
tags: [scheduling, processes, kernel]
related: [userspace-threads, realtime-scheduler, process-orchestrator]
---

# CPU Scheduler

A CPU scheduler decides which runnable task gets the CPU and for how long — it is the piece of the kernel that creates the illusion that dozens of programs run simultaneously. Building one yourself (even in userspace on top of timers) teaches you how fairness, priority, preemption, and context switching actually work.

## Core concepts

- **Process vs thread** — A process owns an address space and resources; a thread is a schedulable unit of execution inside one. The scheduler mostly thinks in threads, even when we casually say "processes".
- **Context switch** — Saving one task's registers, stack pointer, and program counter and restoring another's. This is the atomic unit of "switching programs" and its cost bounds how often you can schedule.
- **Preemption** — The timer interrupt forcibly takes the CPU away from a running task at the end of its time slice. Without preemption (cooperative scheduling), one buggy task can hang the whole system.
- **Ready queue and runqueue** — The data structure holding tasks waiting for CPU. Its design (single queue, per-CPU queues, priority arrays, red-black tree) is the heart of scheduler performance.
- **Scheduling policies** — Round-robin (fair slices in turn), priority scheduling (important tasks first, with aging to avoid starvation), and CFS-style proportional fairness (Linux's default: everyone gets CPU in proportion to weight, tracked by virtual runtime).
- **Starvation and priority inversion** — A low-priority task that never runs is starvation; a high-priority task blocked behind a low-priority one holding a lock is priority inversion. Real schedulers must defend against both.
- **Load balancing** — On multicore machines, per-CPU runqueues must periodically rebalance so one core isn't idle while another has ten runnable tasks.

## How it works

Each task has a state (running, ready, blocked) and a control block storing its registers and scheduling metadata. A periodic timer interrupt invokes the scheduler: it saves the current task's context, picks the next task from the ready queue according to its policy (e.g. the lowest virtual-runtime task in CFS, or the highest-priority non-empty queue in a priority scheduler), restores that task's context, and resumes it. When a task blocks on I/O or a lock, it voluntarily yields and the scheduler picks someone else immediately instead of waiting for the timer. The whole design balances three goals — throughput, latency, and fairness — which fundamentally trade off against each other.

## Build milestones

1. Build a cooperative scheduler in userspace: tasks are functions that call `yield()`, implemented with `ucontext` or manual stack switching; round-robin through them.
2. Add priorities with multiple queues and aging so low-priority tasks eventually run — demonstrate starvation without aging first, then fix it.
3. Make it preemptive: use `SIGALRM`/`setitimer` to fire a timer interrupt that force-switches tasks mid-computation (careful with signal-safe code).
4. Implement a CFS-like scheduler: track each task's virtual runtime weighted by nice value, always run the task with the smallest vruntime, and verify fairness with a workload test.
5. Add blocking: tasks that wait on a pipe/lock sleep instead of spinning, and are woken by the I/O completion — measure the throughput difference.
6. Extend to multicore: per-CPU runqueues with periodic load balancing, and benchmark scaling versus a single global queue with a lock.

## Best resources

- [Operating Systems: Three Easy Pieces — CPU Scheduling](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf) — the classic free textbook chapter; clear, rigorous, and the best starting point.
- [OSTEP — Multi-level Feedback Queue](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched-mlfq.pdf) — how real schedulers learn task behavior with multiple priority queues.
- [Linux kernel scheduler documentation](https://www.kernel.org/doc/html/latest/scheduler/index.html) — the official docs on CFS, realtime, and deadline scheduling internals.
- [Completely fair process scheduling in Linux (OpenSource.com)](https://opensource.com/article/19/2/fair-scheduling-linux) — an accessible explainer of CFS and virtual runtime.
- [OSDev Wiki — Scheduling Algorithms](https://wiki.osdev.org/Scheduling_Algorithms) — a survey of algorithms with hobby-OS implementation notes.
- [The Linux Scheduler: a Decade of Wasted Cores (Lozi et al., EuroSys 2016)](https://doi.org/10.1145/2901318.2901326) — a real paper showing how scheduler bugs waste multicore performance.

## Stretch ideas

- Implement SCHED_DEADLINE-style earliest-deadline-first scheduling and test it with periodic real-time tasks.
- Add scheduler statistics (wait time, turnaround, context-switch rate) and plot how policy changes affect them.
