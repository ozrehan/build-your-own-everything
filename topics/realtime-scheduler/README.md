---
title: "Real-Time Scheduler"
category: "operating-systems"
difficulty: "advanced"
tags: [scheduling, real-time, rtos]
related: [cpu-scheduler, interrupt-handling, userspace-threads]
---

# Real-Time Scheduler

A real-time scheduler doesn't optimize for throughput — it guarantees deadlines: a task that must run every 10ms will, provably, run every 10ms. Building one (even simulated) teaches you rate-monotonic analysis, priority inversion, and the difference between "fast" and "predictable" that defines embedded and safety-critical systems.

## Core concepts

- **Hard vs soft real-time** — Hard: missing a deadline is a system failure (airbag, pacemaker). Soft: misses degrade quality (video frame drops). Firm: late results are useless but not catastrophic. The category dictates the math.
- **Periodic task model** — Tasks are characterized by period (T), worst-case execution time (C), and deadline (D, often = T). Schedulability analysis asks: can this task set provably meet all deadlines?
- **Rate-monotonic scheduling (RMS)** — Fixed priorities by rate: shorter period = higher priority. The Liu & Layland bound says a task set is schedulable if total utilization ≤ n(2^(1/n) − 1) (≈69% for many tasks) — sufficient but not necessary.
- **Earliest-deadline-first (EDF)** — Dynamic priorities: whoever's deadline is nearest runs first. Optimal on uniprocessors (schedulable up to 100% utilization) but harder to implement and less predictable under overload.
- **Priority inversion and inheritance** — A high-priority task blocked on a mutex held by a low-priority task can miss its deadline; priority inheritance (temporarily boosting the holder) is the classic fix, and getting it wrong famously affected the Mars Pathfinder.
- **Determinism over throughput** — RTOS schedulers are O(1), use static allocation, disable paging, and bound interrupt latency. Jitter (variation in timing), not average speed, is the enemy.
- **Linux's realtime classes** — `SCHED_FIFO`, `SCHED_RR` (fixed priorities 1–99, preempt everything including CFS), and `SCHED_DEADLINE` (EDF with runtime/period/deadline parameters) bring real-time to Linux, especially with the PREEMPT_RT patch set.

## How it works

You model each task with its period, deadline, and measured worst-case execution time. An RMS scheduler assigns static priorities (shortest period first) and the dispatcher always runs the highest-priority ready task, preempting on each timer tick or task release. Before deployment you run schedulability analysis — utilization bound or exact response-time analysis — to prove deadlines hold. Shared resources use priority-inheritance mutexes so inversion is bounded and analyzable. At runtime the scheduler is deliberately dumb and fast: no fairness, no load balancing, just "highest priority ready task runs now," with admission control refusing new tasks that would break the guarantee. On Linux you get this via `sched_setscheduler` with `SCHED_DEADLINE`, specifying runtime, deadline, and period per thread, and the kernel enforces the EDF math.

## Build milestones

1. Write a discrete-event simulator: periodic tasks with (C, T), an RMS scheduler, and a timeline plot showing a schedule — then find a task set that misses a deadline.
2. Implement the Liu & Layland utilization test and exact response-time analysis; verify your simulator agrees with the theory.
3. Build a real preemptive RMS scheduler on a microcontroller or in userspace with timer signals, running LED-blink/sensor-style periodic tasks.
4. Add priority-inheritance mutexes: construct the classic inversion scenario, measure the unbounded blocking, then show inheritance bounds it.
5. Implement EDF and compare against RMS on the same task sets — find cases where EDF schedules what RMS cannot.
6. On Linux with PREEMPT_RT (or a Pi), run `SCHED_DEADLINE` threads with `sched_setattr`, measure worst-case jitter with cyclictest-style logging under load.

## Best resources

- [Liu & Layland, "Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment" (1973)](https://ieeexplore.ieee.org/document/1015769) — the founding paper: RMS and the utilization bound.
- [Implications of classical scheduling results for real-time systems (Stankovic et al.)](http://retis.sssup.it/~giorgio/paps/1995/IEEEcomputer95.pdf) — a survey of classical scheduling results and their real-time implications, by Buttazzo's group.
- [sched(7) man page](https://man7.org/linux/man-pages/man7/sched.7.html) — Linux scheduling policies including the realtime classes.
- [sched_setattr(2) / SCHED_DEADLINE docs](https://www.kernel.org/doc/html/latest/scheduler/sched-deadline.html) — the kernel's EDF scheduler documentation.
- [PREEMPT_RT documentation](https://wiki.linuxfoundation.org/realtime/documentation/technical_basics) — the realtime Linux patch set and its latency guarantees.
- [Mars Pathfinder priority inversion account](https://www.cs.unc.edu/~anderson/teach/comp790/papers/mars_pathfinder_long_version.html) — the famous real-world priority inversion bug and its fix.
- [FreeRTOS kernel](https://www.freertos.org/) — the most widely used RTOS; small enough to read the scheduler source directly.

## Stretch ideas

- Implement mixed-criticality scheduling: guarantee hard tasks while best-effort tasks use slack time.
- Build a schedulability analyzer tool that takes a task set and outputs RMS/EDF feasibility plus a Gantt chart.
