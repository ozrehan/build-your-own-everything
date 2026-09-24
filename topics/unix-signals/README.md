---
title: "Unix Signals"
category: "operating-systems"
difficulty: "beginner"
tags: [unix, signals, posix]
related: [interrupt-handling, ipc-pipes-sockets, process-orchestrator]
---

# Unix Signals

Signals are the kernel's async notification system: numbered messages like SIGTERM, SIGSEGV, and SIGCHLD that interrupt a process to report events. Building signal-aware programs teaches you how Unix handles the asynchronous world — Ctrl-C, child termination, timers — and why signal handlers have such strict rules.

## Core concepts

- **Signals as software interrupts** — Like hardware interrupts for processes: the kernel suspends normal execution and runs a handler. `kill -l` lists the ~30 standard signals and their default actions.
- **Default actions** — Each signal has one: terminate (SIGTERM), terminate with core dump (SIGSEGV), ignore (SIGCHLD), stop (SIGSTOP), or continue (SIGCONT). A handler overrides the default where allowed.
- **Catching vs ignoring vs blocking** — `sigaction()` installs a handler; `SIG_IGN` discards; `sigprocmask()` blocks delivery until unblocked, queuing standard signals (merging duplicates) while blocked.
- **Async-signal safety** — A handler can run at any instruction, even mid-`malloc`. Only async-signal-safe functions (see `signal-safety(7)`) may be called inside — `printf` and `malloc` are forbidden, which is why handlers set a flag and return.
- **Reliable signals with sigaction** — Old `signal()` had racy semantics (handler reset, interrupted syscalls). `sigaction()` with `SA_RESTART` gives well-defined behavior; know the difference.
- **SIGCHLD and reaping** — When a child dies the parent gets SIGCHLD; the handler (or main loop) must `waitpid()` to reap the zombie. This is the core of every process supervisor.
- **Uncatchable signals** — SIGKILL and SIGSTOP cannot be caught, blocked, or ignored — the kernel's guarantee that a runaway process can always be stopped. That's why `kill -9` is the last resort.

## How it works

When an event occurs (you press Ctrl-C → the terminal driver sends SIGINT to the foreground group; a child exits → SIGCHLD to the parent), the kernel marks the signal pending on the target process. At the next return from kernel to userspace — after a syscall or interrupt — the kernel checks pending unblocked signals before resuming. If a handler is installed, it pushes a frame onto the user's stack and jumps to the handler; on return, the `sigreturn` syscall restores the original context and resumes the interrupted code. Blocked signals wait in the pending set; standard signals merge (one SIGUSR1 pending no matter how many were sent), while queued real-time signals (SIGRTMIN+n) each carry a value via `sigqueue()`.

## Build milestones

1. Write a program that installs a SIGINT handler with `sigaction()` printing a message via `write()` (signal-safe) — contrast with the broken `signal()` version.
2. Implement graceful shutdown: block SIGTERM during critical sections with `sigprocmask()`, handle it by setting a `volatile sig_atomic_t` flag, and exit the main loop cleanly.
3. Build a mini supervisor: fork workers, catch SIGCHLD, reap with `waitpid(-1, &status, WNOHANG)` in a loop, and restart crashed workers — log each event.
4. Use `setitimer` + SIGALRM to build a watchdog: reset the timer on heartbeat, and have the handler abort if the main loop stalls.
5. Demonstrate the async-signal-safety rule: call `printf` in a handler under load and observe corruption, then fix it with the self-pipe trick (write a byte to a pipe, handle it in the event loop).
6. Send real-time signals with `sigqueue()` carrying integer payloads between two processes, and show they queue without merging.

## Best resources

- [signal(7) man page](https://man7.org/linux/man-pages/man7/signal.7.html) — the complete signal reference: numbers, defaults, and semantics.
- [signal-safety(7) man page](https://man7.org/linux/man-pages/man7/signal-safety.7.html) — exactly which functions are safe in handlers.
- [sigaction(2) man page](https://man7.org/linux/man-pages/man2/sigaction.2.html) — the correct API and its flags (SA_RESTART, SA_SIGINFO).
- [Beej's Guide to Unix IPC — Signals section](https://beej.us/guide/bgipc/html/multi/signals.html) — approachable introduction with working examples.
- [The Linux Programming Interface, Ch. 20–22 (Kerrisk)](https://man7.org/tlpi/) — the definitive chapters on signal concepts, handlers, and advanced topics.
- [Handling signals the right way (self-pipe trick)](http://cr.yp.to/docs/selfpipe.html) — Dan Bernstein's classic explanation of the self-pipe pattern.

## Stretch ideas

- Implement job control: a tiny shell handling SIGTSTP/SIGCONT, foreground/background process groups like bash.
- Build a signal-based profiler: sample the program counter with SIGPROF on a timer and aggregate a histogram.
