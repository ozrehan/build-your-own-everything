---
title: "chroot Sandbox"
category: "operating-systems"
difficulty: "beginner"
tags: [sandbox, chroot, security]
related: [container-runtime-basics, sandbox-executor, firewall-basics]
---

# chroot Sandbox

`chroot` changes a process's view of the filesystem so `/` points somewhere else — the oldest, simplest Unix sandboxing primitive. Building a chroot jail yourself teaches you how filesystem isolation works, what it takes to make a jail actually usable (libraries, devices, DNS), and exactly where chroot's security guarantees end.

## Core concepts

- **What chroot does** — `chroot("/jail")` makes that directory the process's new root; absolute paths resolve inside it, and the old filesystem becomes unreachable by name. It's per-process, inherited across fork.
- **Building a usable jail** — A program needs its libraries (`ldd` shows them), config files, and device nodes (`/dev/null`, `/dev/urandom`). Assembling these is the fiddly real work of jailing.
- **chroot is not a security boundary** — Root inside a chroot can often escape (e.g. via `mknod` device creation, or chroot-again tricks with open directory fds). It's filesystem isolation, not a security container — the man page says so.
- **Escapes and mitigations** — Classic escape: open a fd to `/`, chroot to a subdirectory, `fchdir` back out, then chroot again. Mitigations: drop root immediately after chroot, and layer namespaces/seccomp on top.
- **User namespaces as the fix** — With a user namespace, an unprivileged user gets a fake root that can chroot safely — this is how modern sandboxes let untrusted users build jails.
- **Where chroot still shines** — Build systems (mock, pbuilder), FTP servers, package builds, and recovery environments all use chroot for filesystem isolation where full containers are overkill.
- **From chroot to containers** — Add mount, PID, and network namespaces plus cgroups to a chroot and you have reinvented the container. The lineage is direct.

## How it works

You create a directory tree containing everything the jailed program needs: copy the binary, use `ldd` to find its shared libraries and copy those preserving paths, create minimal `/dev` nodes, and add `/etc/resolv.conf` and `/etc/passwd` if networking or user lookups are needed. A small launcher (which must start as root, or in a user namespace) calls `chroot()` into the tree, `chdir("/")`, drops privileges to an unprivileged uid/gid, and `exec()`s the target. Inside, the process sees only the jail; outside, it's an ordinary process. For defense in depth you add `seccomp` to restrict syscalls and a mount namespace with the jail mounted read-only where possible — at which point you've built a credible sandbox from 1979's primitive plus modern helpers.

## Build milestones

1. Build a minimal jail by hand: copy `/bin/sh` and its `ldd` libraries into `~/jail`, then `sudo chroot ~/jail /bin/sh` — explore what's missing and fix it iteratively.
2. Write a `jail` launcher in C/Python: takes a program + args, sets up the chroot, drops to `nobody`, and execs — no root shell escapes possible after the drop.
3. Automate jail construction: a script that takes any binary, resolves its full library closure with `ldd`, and populates the jail tree.
4. Demonstrate the classic chroot escape as root inside the jail (in a VM!), then fix your launcher by dropping privileges and show the escape now fails.
5. Harden with a user namespace so unprivileged users can create jails, plus a seccomp filter blocking `mount`, `ptrace`, and `reboot` inside.
6. Run a real untrusted workload: execute user-submitted scripts in fresh per-run jails with CPU/memory limits via cgroups, and report resource usage.

## Best resources

- [chroot(2) man page](https://man7.org/linux/man-pages/man2/chroot.2.html) — the syscall semantics, including the documented security limitations.
- [How to break out of a chroot() cell (unixwiz.net mirror)](http://www.unixwiz.net/techtips/mirror/chroot-break.html) — the classic writeup of chroot escape techniques.
- [user_namespaces(7) man page](https://man7.org/linux/man-pages/man7/user_namespaces.7.html) — how unprivileged users get safe chroot-equivalent isolation.
- [An introduction to Linux container primitives (Red Hat)](https://www.redhat.com/en/blog/introduction-linux-container-primitives-cgroups-namespaces-and-selinux) — places chroot in the lineage toward full containers.
- [Firejail documentation](https://firejail.wordpress.com/documentation/) — a real-world sandboxing tool built on namespaces, seccomp, and chroot concepts.
- [The Chromium sandbox design docs](https://chromium.googlesource.com/chromium/src/+show/HEAD/docs/design/sandbox.md) — how a production browser layers sandboxing primitives.

## Stretch ideas

- Make the jail network-isolated with its own network namespace and a filtered veth uplink.
- Add an audit mode that `strace`s the jailed program and reports every syscall outside an allowlist.
