---
title: "Syscall Interface"
category: "operating-systems"
difficulty: "intermediate"
tags: [kernel, abi, system-calls]
related: [minimal-kernel, interrupt-handling, device-driver-uart]
---

# Syscall Interface

System calls are the controlled doorway between user programs and the kernel — the only way a normal program can read files, allocate memory, or talk to hardware. Building a syscall interface yourself teaches you how privilege transitions work, how arguments cross the user/kernel boundary safely, and why every OS has an ABI contract.

## Core concepts

- **The privilege boundary** — User code runs in ring 3 and cannot touch hardware or kernel memory directly. A syscall is a deliberate, CPU-assisted trap into ring 0 that switches stacks and privilege level.
- **Trap mechanisms** — Classic x86 used software interrupt `int 0x80`; modern CPUs use fast `syscall`/`sysenter` instructions that jump to a kernel entry point via a model-specific register (LSTAR), skipping interrupt overhead.
- **The syscall number table** — Each syscall has a number (in `rax` on x86-64); the kernel dispatches through a table of function pointers. Linux's table lives in `arch/x86/entry/syscalls/` and its ABI is frozen forever.
- **Argument passing** — Arguments arrive in registers (`rdi, rsi, rdx, r10, r8, r9` on Linux x86-64) and the return value in `rax`, with negative values encoding `-errno`. The kernel must validate every pointer before dereferencing it.
- **copy_to_user / copy_from_user** — The kernel cannot trust user pointers: they may be unmapped, or change under it (TOCTOU). These helpers safely copy with fault handling, returning how many bytes failed.
- **vdso and vsyscall** — Some "syscalls" like `gettimeofday` need no privilege at all; the kernel maps a shared library page (vdso) into every process so they run entirely in userspace.
- **Strace as a teacher** — `strace` shows every syscall a program makes. Reading `strace` output is the fastest way to learn what the syscall interface really looks like in practice.

## How it works

A C library wrapper (e.g. glibc's `read()`) places the syscall number in `rax` and arguments in the ABI registers, then executes the `syscall` instruction. The CPU switches to ring 0, swaps to the kernel stack, and jumps to the entry point recorded in the LSTAR MSR. The kernel's entry assembly saves all registers, uses `rax` to index the syscall dispatch table, and calls the handler — e.g. `sys_read`, which validates the file descriptor, copies data from the file into a kernel buffer, then `copy_to_user()` into the caller's buffer. The handler's return value goes back into `rax`, the CPU executes `sysret` to drop back to ring 3, and glibc converts negative returns into `errno`. A bad pointer anywhere in this path is caught by the fault handler instead of crashing the kernel.

## Build milestones

1. In a hobby kernel, implement one syscall (`sys_write` to a serial console) dispatched via `int 0x80` or the `syscall` instruction with a number table.
2. Write a userspace test program in freestanding C (no libc) that invokes your syscalls with inline assembly, verifying arguments arrive intact.
3. Add `sys_read`, `sys_open`, `sys_close` backed by a tiny in-memory file table, so a user program can open and echo a file.
4. Implement safe `copy_from_user`/`copy_to_user` using the page-fault handler: probe the user buffer first and return `-EFAULT` instead of crashing on a bad pointer.
5. Add `sys_fork`/`sys_exec` (or `spawn`): duplicate the address space, reset to a new entry point, and run two user programs that communicate through a pipe.
6. Write a mini-`strace`: intercept your syscalls at the dispatch table and log number, arguments, and return values for every call a program makes.

## Best resources

- [Linux syscalls man page](https://man7.org/linux/man-pages/man2/syscalls.2.html) — the complete syscall list with notes on each.
- [OSDev Wiki — System Calls](https://wiki.osdev.org/System_Calls) — practical guide to implementing syscalls in a hobby OS, both `int 0x80` and `syscall`.
- [The Definitive Guide to Linux System Calls (PackageCloud blog)](https://blog.packagecloud.io/the-definitive-guide-to-linux-system-calls) — a thorough walkthrough of the whole path from libc to kernel.
- [Linux kernel: entry_64.S](https://github.com/torvalds/linux/blob/master/arch/x86/entry/entry_64.S) — the actual syscall entry assembly; dense but definitive.


## Stretch ideas

- Implement `seccomp`-style filtering: a per-process allowlist of syscall numbers enforced at dispatch time.
- Add a vdso page exporting a fast `gettimeofday` that never enters the kernel.
