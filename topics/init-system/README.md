---
title: "Init System"
category: "operating-systems"
difficulty: "beginner"
tags: [init, pid1, services]
related: [process-orchestrator, cron-scheduler, container-runtime-basics]
---

# Init System

PID 1 — the init system — is the first process the kernel starts and the ancestor of everything: it mounts filesystems, launches services in dependency order, reaps orphaned children, and handles shutdown. Building a minimal init teaches you process supervision, runlevels/targets, and why systemd replaced SysV init.

## Core concepts

- **PID 1's special duties** — The kernel starts init as the first userspace process; it can never exit (a panic follows), it adopts orphaned processes, and it must reap zombies since nothing supervises it.
- **SysV init and runlevels** — The classic model: numbered runlevels (0=halt, 1=single-user, 3=multi-user, 6=reboot) with `/etc/rc.d` scripts run in alphanumeric order. Simple, but strictly sequential and slow.
- **Dependency-based boot** — Modern inits express "service B needs A" as a dependency graph and start independent services in parallel. This is the core idea systemd, Upstart, and runit variants share.
- **Supervision** — A supervisor keeps a service alive: fork, exec, watch for exit via SIGCHLD, restart on failure with backoff. daemontools/runit proved this model; systemd absorbed it.
- **Socket and D-Bus activation** — Instead of starting everything at boot, systemd can start a service on first connection (socket activation) or first D-Bus message — lazy startup that speeds boot and saves memory.
- **The shutdown path** — Init also orchestrates halt/reboot: send SIGTERM to all processes, wait, SIGKILL stragglers, unmount filesystems, then tell the kernel to power off. Getting this wrong corrupts disks.
- **Containers need init too** — A container's PID 1 has the same reaping problem; that's why tiny inits like `tini` and `dumb-init` exist as container entrypoints.

## How it works

The kernel finishes booting and execs `/sbin/init` as PID 1. Your init reads its configuration (service files describing commands, dependencies, and restart policies), builds a dependency graph, and topologically sorts it into a start order. It forks and execs each service, recording PIDs, and installs a SIGCHLD handler that reaps exits and applies restart policy (restart unless the exit was clean, with exponential backoff to avoid tight crash loops). It also adopts orphans automatically — any process whose parent dies is reparented to PID 1, so the reaper must `waitpid(-1, ...)` in a loop. On SIGTERM/SIGINT (or a `reboot` command), it walks services in reverse dependency order sending SIGTERM, escalates to SIGKILL after a timeout, syncs and unmounts, then invokes the `reboot()` syscall.

## Build milestones

1. Write a 100-line init: run as PID 1 in a VM or container, mount `/proc`, spawn a shell on the console, reap zombies in a SIGCHLD loop, and handle Ctrl-Alt-Del for reboot.
2. Add a service directory: for each `*.service` file (command + `After=` deps), topologically sort and start in order; log each service's output.
3. Implement supervision: restart crashed services with backoff, and add `myinit status` / `myinit stop <svc>` control via a Unix socket.
4. Parallelize startup: start dependency-satisfied services concurrently, measure boot time versus sequential, and handle the log interleaving.
5. Add socket activation: listen on a Unix socket for a service, spawn it on first connection, and pass the listening fd through.
6. Implement the shutdown path: on SIGTERM, stop services in reverse order (TERM → wait 5s → KILL), unmount filesystems, and reboot — test in QEMU.

## Best resources

- [systemd System and Service Manager](https://systemd.io/) — the project's docs explain targets, dependencies, and activation better than any tutorial.
- [systemd.service man page](https://www.freedesktop.org/software/systemd/man/systemd.service.html) — the unit file format; the best spec for what an init must express.
- [The systemd controversy essays (various)](https://www.freedesktop.org/wiki/Software/systemd/) — the project's own rationale for replacing SysV init.
- [runit documentation](http://smarden.org/runit/) — the minimal supervision-suite philosophy; a great model for a small init.
- [s6 supervision suite](https://skarnet.org/software/s6/) — a rigorous, well-documented take on supervision and readiness notification.
- [tini — a tiny init for containers](https://github.com/krallin/tini) — ~500 lines solving PID 1's reaping problem; perfect study-sized code.

## Stretch ideas

- Add cgroup-based resource limits per service, so one runaway service can't starve the others.
- Implement D-Bus-style readiness notification so dependents start only after a service signals it's actually ready.
