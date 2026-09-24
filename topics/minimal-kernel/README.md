---
title: "Minimal Kernel"
category: "operating-systems"
difficulty: "intermediate"
tags: [kernel, x86-64, freestanding]
related: [bootloader, syscall-interface, interrupt-handling]
---

# Minimal Kernel

A kernel is the privileged core of an operating system that owns the hardware and hands it out to programs. Building a minimal one — just boot, print to screen, and loop forever — teaches you what an OS actually is underneath the libraries: freestanding C, a hand-made stack, and the CPU running your code with no one beneath you.

## Core concepts

- **Freestanding C** — Kernel code runs without the C standard library: no `printf`, no `malloc`, no OS syscalls to lean on. You write your own string functions and manage every byte yourself.
- **The entry point** — After the bootloader jumps to the kernel, you must set up a stack pointer and call your C `kmain`. The bootloader-kernel contract (registers, memory layout) is defined by you or by a spec like Multiboot.
- **Ring 0 vs ring 3** — The CPU runs code at privilege levels; the kernel lives in ring 0 (full hardware access) while user programs run in ring 3 (restricted). This boundary is the reason syscalls exist.
- **The VGA text buffer** — On x86, video memory at 0xB8000 lets you print characters by writing bytes directly — the classic "hello from my kernel" with no driver at all.
- **The GDT and IDT** — The Global Descriptor Table defines memory segments and the Interrupt Descriptor Table maps hardware/software interrupts to handler functions. Both must exist before interrupts can be enabled safely.
- **Panic and fault handling** — With no OS beneath you, a null dereference or divide-by-zero is a CPU exception you must catch and handle — usually by printing registers and halting. This is where `panic()` comes from.
- **Linker scripts** — A kernel is not a normal executable: you write a linker script to place sections at exact physical addresses (e.g. code at 0x100000) that the bootloader expects.

## How it works

The bootloader loads the kernel image to a fixed physical address and jumps to its entry point with the CPU in 32-bit protected or 64-bit long mode and a stack you've pointed at free memory. The entry assembly stub zeroes the BSS segment, sets up segment registers and the GDT, then calls the C kernel main. Your C code then installs an interrupt descriptor table, initializes a simple physical memory allocator (often just a bump allocator over the firmware memory map), sets up serial/VGA output for debugging, enables interrupts, and either starts the first user process or idles. Every later subsystem — scheduling, paging, syscalls — hooks into this skeleton.

## Build milestones

1. Boot a freestanding C `kmain` that writes "hello" to the VGA text buffer at 0xB8000 and halts — in QEMU, using a GRUB/Multiboot bootloader so you skip writing your own loader first.
2. Add a serial port (COM1) logger and a minimal `printf` (support `%d`, `%s`, `%x`) so you can debug without VGA.
3. Install an IDT with handlers for CPU exceptions (divide-by-zero, page fault, GPF) that print the faulting address and register dump, then halt.
4. Parse the Multiboot memory map and implement a physical page-frame allocator (bitmap or stack-based) with `alloc_page`/`free_page`.
5. Add a programmable interval timer (PIT) interrupt that increments a tick counter and prints it — your first preemptive hardware heartbeat.
6. Load a static user-space program as a flat binary, switch to ring 3, and implement your first syscall so the program can print back to the kernel.

## Best resources

- [OSDev Wiki — Bare Bones](https://wiki.osdev.org/Bare_Bones) — the canonical first-kernel walkthrough using GRUB and Multiboot.
- [os-tutorial by cfenollosa](https://github.com/cfenollosa/os-tutorial) — builds a bootloader and minimal kernel chapter by chapter on GitHub.
- [The little book about OS development](https://littleosbook.github.io/) — free short book on a minimal x86 kernel from boot to userspace concepts.
- [linux-insides by 0xAX](https://github.com/0xAX/linux-insides) — deep dive into how the real Linux kernel boots and initializes, chapter by chapter.
- [James Molloy's kernel development tutorials (OSDev mirror)](http://wiki.osdev.org/User:Lionel/James_Molloy%27s_Kernel_Development_Tutorials) — classic tutorial series on a multitasking hobby kernel (original site is down; mirrored on the OSDev wiki).
- [Intel 64 and IA-32 Software Developer Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) — the ground truth for modes, segmentation, and interrupts.

## Stretch ideas

- Replace the flat user binary with a real ELF loader so you can run programs compiled with a normal toolchain.
- Implement SMP support: wake the application processors with the APIC and give each CPU its own stack and scheduler.
