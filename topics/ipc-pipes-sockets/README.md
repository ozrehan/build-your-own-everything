---
title: "IPC: Pipes and Sockets"
category: "operating-systems"
difficulty: "beginner"
tags: [ipc, pipes, sockets]
related: [message-queue, websocket-server, unix-signals]
---

# IPC: Pipes and Sockets

Inter-process communication is how separate programs talk: pipes give you a one-way byte stream between parent and child, and sockets generalize that to any two endpoints, local or across the network. Building with both teaches you file-descriptor passing, buffering, blocking semantics, and the exact boundary where local IPC becomes networking.

## Core concepts

- **Everything is a file descriptor** — Pipes, sockets, and files all present as fds, so `read`/`write`/`select`/`poll` work uniformly. This is the Unix design insight that makes IPC composable with everything else.
- **Anonymous pipes** — `pipe()` returns two fds; typically the parent forks and each side closes one end. Data written to one end is readable from the other, in order, with kernel buffering in between.
- **FIFOs (named pipes)** — `mkfifo` creates a pipe with a filesystem name so unrelated processes can rendezvous on it. Same byte-stream semantics, no parent-child relationship needed.
- **Blocking, capacity, and atomicity** — A pipe has a finite buffer (64KB default on Linux). Writers block when full, readers block when empty; writes under `PIPE_BUF` (4KB) are atomic, which is how shell pipelines avoid interleaving.
- **Unix domain sockets** — Sockets bound to a filesystem path (or abstract namespace) for same-machine IPC: bidirectional, with datagram or stream modes, and the unique ability to pass file descriptors between processes.
- **Socket pairs** — `socketpair()` creates a connected, bidirectional pair of Unix sockets — like `pipe()` but full-duplex, the standard primitive for parent-child control channels.
- **Multiplexing with poll/epoll** — One thread watches many fds for readability/writability. This is the foundation of every event loop, from nginx to Node.js.

## How it works

`pipe()` asks the kernel to allocate a circular buffer and two file descriptors pointing at its ends. When process A writes, the kernel copies bytes into the buffer and wakes any reader blocked in `read()`; when the buffer is full, the writer sleeps until space frees. A Unix domain socket instead goes through the socket layer: `socket()` creates the endpoint, `bind()` attaches an address, `listen()`/`accept()` (or `connect()`) establish the channel, and data flows through socket buffers with the same blocking semantics. Passing an fd over a Unix socket uses ancillary data (`SCM_RIGHTS`): the kernel duplicates the open file description into the receiving process's fd table — the only way to hand a live fd to another process.

## Build milestones

1. Write a parent/child pair using `pipe()` + `fork()`: child sends numbers, parent sums them; then reverse roles to feel the one-way limitation.
2. Build a shell-style pipeline runner: parse `cmd1 | cmd2 | cmd3`, wire each stage with pipes, and exec the commands — you've built the core of a shell.
3. Create a FIFO-based chat: two unrelated terminals exchange messages through a named pipe; observe blocking open semantics.
4. Implement a request/reply server over Unix domain sockets with `SOCK_STREAM`, handling multiple sequential clients.
5. Pass an open file descriptor from one process to another with `SCM_RIGHTS` — have the receiver read a file it never opened.
6. Write a single-threaded echo server using `epoll` over many socketpair/socket clients; benchmark connections per second versus a thread-per-client version.

## Best resources

- [Beej's Guide to Unix IPC](https://beej.us/guide/bgipc/html/) — the friendliest complete tutorial on pipes, FIFOs, message queues, and shared memory.
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/html/) — sockets from first principles; the Unix-domain sections apply directly to local IPC.
- [pipe(7) man page](https://man7.org/linux/man-pages/man7/pipe.7.html) — pipe capacity, atomicity guarantees, and blocking behavior, precisely documented.
- [unix(7) man page](https://man7.org/linux/man-pages/man7/unix.7.html) — Unix domain sockets, including fd passing with SCM_RIGHTS.
- [The Linux Programming Interface, Ch. 43–44 (Kerrisk)](https://man7.org/tlpi/) — the book's site; chapters 43–61 are the definitive IPC reference.
- [epoll man page](https://man7.org/linux/man-pages/man7/epoll.7.html) — the event-notification interface behind high-performance multiplexing.

## Stretch ideas

- Implement a tiny RPC: marshal function calls over a Unix socket with a length-prefixed framing protocol.
- Build a zero-copy transfer path with `splice()`/`tee()` moving data between pipes and sockets without userspace copies.
