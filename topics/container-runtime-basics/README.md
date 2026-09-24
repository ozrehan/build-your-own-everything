---
title: "Container Runtime Basics"
category: "operating-systems"
difficulty: "intermediate"
tags: [containers, namespaces, cgroups]
related: [chroot-sandbox, init-system, sandbox-executor]
---

# Container Runtime Basics

A container is not a VM and not magic: it's an ordinary Linux process running with restricted views of the system (namespaces) and restricted resources (cgroups). Building a minimal container runtime yourself — `clone()` a process into new namespaces, set up its root filesystem, limit its memory — demystifies Docker completely.

## Core concepts

- **Namespaces** — The kernel feature behind containers: PID, mount, network, UTS (hostname), IPC, user, and cgroup namespaces each give a process its own isolated view of one global resource. `unshare()`/`clone()` create them.
- **chroot and pivot_root** — `chroot()` changes a process's root directory; `pivot_root()` is the stronger primitive container runtimes use to fully replace the root filesystem so the old root can be unmounted.
- **cgroups** — Control groups limit and account resources: memory caps, CPU shares, block I/O weight, and the freezer. cgroup v2 unified the hierarchy under `/sys/fs/cgroup`.
- **Overlay filesystems** — Containers layer a writable upper dir over a read-only image via overlayfs, so each container gets cheap copy-on-write storage sharing the base image.
- **The OCI specs** — `runtime-spec` defines the config.json contract (namespaces, mounts, cgroups, process to run) and `image-spec` defines image layout. runc implements the runtime side; your toy runtime can too.
- **Seccomp and capabilities** — Defense in depth: seccomp-bpf filters which syscalls a container may make, and dropping Linux capabilities (e.g. CAP_SYS_ADMIN) removes specific root powers without losing root entirely.
- **runc and containerd** — The real stack: containerd manages lifecycle and images, runc is the low-level runtime that actually creates the namespaces and execs the process. Reading runc's `libcontainer` is the masterclass.

## How it works

Your runtime reads a config (rootfs path, command, resource limits), then `clone()`s a child with flags like `CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET | CLONE_NEWUTS`. In the child, it mounts the container's rootfs, `pivot_root()`s into it, mounts `/proc` and `/sys` fresh inside the new mount namespace, sets the hostname, writes cgroup limits (e.g. `memory.max`) for the child's cgroup, drops capabilities, installs a seccomp filter, and finally `exec()`s the target binary as PID 1 of its new PID namespace. The parent monitors the child and cleans up cgroups on exit. From inside, the process believes it is alone on its own machine; from outside, it's just a process you can `ps` and `kill`.

## Build milestones

1. Write a 50-line "container" in C or Go: `unshare(CLONE_NEWUTS)` then `sethostname()` — prove the host's hostname is unchanged while the child sees its own.
2. Add mount + PID namespaces: `pivot_root` into a minimal rootfs (busybox), mount a fresh `/proc`, and run a shell as container PID 1.
3. Add a veth pair + network namespace: give the container its own IP, NAT it through the host, and `ping` out from inside.
4. Enforce limits with cgroup v2: cap memory at 64MB and CPU weight, then run a memory hog inside and watch the OOM killer strike only the container.
5. Apply a seccomp-bpf filter blocking dangerous syscalls (e.g. `mount`, `reboot`) and drop all capabilities except the minimum — verify escape attempts fail.
6. Implement an OCI-runtime-spec-compatible `config.json` reader so your runtime can launch any OCI bundle; compare behavior against `runc run`.

## Best resources

- [Linux namespaces man page](https://man7.org/linux/man-pages/man7/namespaces.7.html) — the authoritative reference for all seven namespace types.
- [cgroups v2 documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html) — the official guide to the unified hierarchy, controllers, and delegation.
- [Containers from scratch (Liz Rice)](https://www.youtube.com/watch?v=8fi7uSYlOdc&pp=ugUEEgJlbg%3D%3D) — classic talk building a container runtime live in Go; short and illuminating.
- [runc source code](https://github.com/opencontainers/runc) — the reference OCI runtime; `libcontainer` shows exactly how namespaces, cgroups, and seccomp fit together.
- [OCI runtime specification](https://github.com/opencontainers/runtime-spec) — the config.json contract your runtime can target.
- [pivot_root man page](https://man7.org/linux/man-pages/man2/pivot_root.2.html) — the precise semantics of the rootfs switch, with its famous quirks.


## Stretch ideas

- Add image support: unpack an OCI image tarball into an overlayfs upper/lower stack as the container rootfs.
- Implement checkpoint/restore of your container with CRIU and migrate it between two hosts.
