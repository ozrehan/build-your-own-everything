---
title: "Userspace Threads"
category: "operating-systems"
difficulty: "intermediate"
tags: [threads, concurrency, context-switch]
related: [cpu-scheduler, actor-model-concurrency, chip8-emulator]
---

# Userspace Threads

Userspace threads (fibers, coroutines, green threads) are concurrency without the kernel: your library switches between stacks by saving and restoring registers itself. Building them teaches you exactly what a context switch is, how stacks work, and why async/await runtimes like Go's goroutines and Tokio exist.

## Core concepts

- **What a thread really is** — A stack plus saved register state (program counter, stack pointer, callee-saved registers). Switching threads = saving one register set and loading another. The kernel does this; you can too.
- **Cooperative vs preemptive** — Userspace threads usually yield voluntarily (`yield()`), avoiding preemption complexity. Preemptive userspace scheduling needs timer signals and is much trickier to get right.
- **Context-switch primitives** — `setjmp`/`longjmp`, POSIX `ucontext` (deprecated but instructive), or hand-written assembly swapping registers. Modern runtimes use assembly; start with `ucontext` or `setjmp`.
- **Per-thread stacks** — Each thread needs its own stack (e.g. 64KB–8MB from `mmap` or `malloc`), with a guard page at the bottom to catch overflows as segfaults instead of silent corruption.
- **The scheduler loop** — A ready queue of thread control blocks; `yield()` saves the current context and jumps to the scheduler, which picks the next thread and restores it. This is the same shape as a kernel scheduler.
- **Blocking is the hard part** — A blocking syscall (like `read`) blocks the whole OS thread and every userspace thread on it. Real runtimes solve this with non-blocking I/O + event loops, or a pool of OS threads.
- **M:N threading** — Many userspace threads multiplexed onto N kernel threads: the Go/Tokio model. It combines cheap thread creation with true parallelism, at the cost of a sophisticated runtime.

## How it works

You allocate a stack per thread and initialize a context pointing at the thread's start function. The scheduler keeps a queue of runnable contexts. When a thread calls `yield()`, it saves its registers into its thread control block and transfers control to the scheduler's context; the scheduler dequeues the next thread and restores its registers, resuming exactly where that thread last yielded. Because switching never enters the kernel, a context switch costs tens of nanoseconds versus microseconds for kernel threads — which is why you can spawn a million goroutines but not a million pthreads. The catch: any thread that blocks in a syscall freezes its underlying OS thread, so the runtime must either intercept blocking calls or dedicate OS threads for them.

## Build milestones

1. Implement two coroutines with `setjmp`/`longjmp` ping-ponging values back and forth — the smallest possible context switch. Note they share a single stack; true per-thread stacks need `ucontext` or manual stack-pointer switching, which you build in step 2.
2. Build a cooperative thread library: `thread_create(fn)`, `thread_yield()`, round-robin scheduler, each thread on its own `malloc`'d 64KB stack (use `ucontext` or raw stack-pointer switching).
3. Add `thread_sleep` and channel-style message passing between threads so they can coordinate without busy-waiting.
4. Add guard pages with `mprotect` and demonstrate a stack overflow being caught cleanly.
5. Make blocking I/O work: wrap reads in non-blocking mode + a `poll()`-based event loop in the scheduler, so one thread's socket read doesn't stall the others.
6. Go M:N: run the scheduler on 4 pthreads with work-stealing queues, and benchmark a million spawned threads versus pthreads.

## Best resources

- [OSTEP — Threads introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf) — what threads are and why concurrency is hard, from the free OS textbook.
- [ucontext man pages](https://man7.org/linux/man-pages/man3/makecontext.3.html) — the classic (deprecated but educational) userspace context API.
- [A portable userspace thread library walkthrough](https://www.gnu.org/software/pth/) — GNU Pth, a real cooperative threading library; its docs explain the design space.
- [Goroutine scheduler design (Go)](https://go.dev/src/runtime/HACKING.md) — how Go's M:N scheduler actually works, from the runtime hackers' guide.
- [Tokio internals](https://tokio.rs/tokio/tutorial) — the async runtime's tutorial shows the userspace-scheduling mindset in Rust.
- [Protothreads (Adam Dunkels)](https://dunkels.com/adam/pt/) — stackless coroutines in pure C; a beautiful minimal take on the idea.

## Stretch ideas

- Implement `async`/`await`-style syntax on top of your threads with a small preprocessor or macro layer.
- Add thread-local storage and demonstrate why it needs compiler/runtime cooperation.
