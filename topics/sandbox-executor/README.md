---
title: "Sandboxed Code Executor"
category: "security"
difficulty: "advanced"
tags: [sandboxing, isolation, containers]
related: [chroot-sandbox, container-runtime-basics, malware-analysis-sandbox]
---

# Sandboxed Code Executor

A sandboxed code executor runs untrusted programs — user-submitted code, plugins, build scripts — with strict limits on what they can touch. Building one teaches you the OS isolation primitives (namespaces, seccomp, cgroups) that underpin containers, and how thin the line is between "contained" and "escaped."

## Core concepts

- **Linux namespaces** — Kernel primitives that give a process its own view of PIDs, mounts, network, users, and IPC; the foundation of container isolation.
- **seccomp-bpf** — A Berkeley Packet Filter program attached to a process that whitelists which syscalls it may invoke (and with which arguments); the main defense against kernel exploitation from inside the sandbox.
- **cgroups** — Limits on CPU, memory, disk I/O, and process count that stop a sandboxed program from starving the host or fork-bombing it.
- **Filesystem isolation** — A minimal read-only root (via chroot or mount namespace + pivot_root) so the sandbox can't read host secrets or write to host binaries.
- **Capability dropping** — Stripping Linux capabilities (CAP_SYS_ADMIN and friends) and running as an unprivileged UID so even a compromised sandbox process has little power.
- **Escape surface** — The ways sandboxes fail: kernel bugs reachable through allowed syscalls, misconfigured mounts, /proc leaks, and shared namespaces; sandboxing is risk reduction, not a proof.
- **Defense in depth** — Real executors layer namespaces + seccomp + cgroups + read-only FS + network blocking, because any single layer has known bypasses.

## How it works

When your executor receives a program, it spawns a child process that first applies restrictions to itself: unshare into new mount/PID/network namespaces, pivot to a minimal root filesystem, install a seccomp filter allowing only the syscalls the workload needs (read, write, exit, mmap…), join a cgroup with memory/CPU caps, drop all capabilities, and set an alarm timeout. Only then does it exec the untrusted binary.

The parent watches from outside: it captures stdout/stderr through pipes, enforces a wall-clock timeout by killing the cgroup, and reads back the exit status. The key insight you gain by building this is how much of "isolation" is just careful process setup — there is no magic sandbox syscall, only the disciplined combination of these primitives.

## Build milestones

1. Build a runner that executes a program with a wall-clock timeout and captures output — no isolation yet, just the harness.
2. Add filesystem isolation: chroot into a minimal root with only the needed libraries, running as a nobody user.
3. Add namespaces (mount, PID, network off) via unshare/clone, so the sandbox can't see host processes or the network.
4. Add a seccomp-bpf whitelist filter for the syscalls your workload needs, and test that a shellcode-style exploit attempt gets killed.
5. Add cgroup limits (memory, CPU, pids) and a read-only root; then attempt to break out of your own sandbox in a lab and fix what you find.

## Best resources

- [nsjail by Google](https://github.com/google/nsjail) — A small, readable sandbox using namespaces + seccomp; the best reference implementation to study.
- [gVisor](https://gvisor.dev/) — Google's userspace kernel that intercepts syscalls; shows the stronger end of the sandboxing spectrum.
- [Firecracker microVMs](https://github.com/firecracker-microvm/firecracker) — When process isolation isn't enough: real VM-level isolation with KVM.
- [namespaces(7) man page](https://man7.org/linux/man-pages/man7/namespaces.7.html) — The authoritative reference on each namespace type.
- [seccomp(2) man page](https://man7.org/linux/man-pages/man2/seccomp.2.html) — How seccomp filters are installed and how BPF programs are structured.

## Stretch ideas

- Build a multi-tenant code-runner service (like an online judge) with per-submission isolation, resource accounting, and result caching.
- Add syscall auditing: log every blocked syscall attempt to detect exploit probes against your sandbox.
