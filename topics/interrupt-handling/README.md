---
title: "Interrupt Handling"
category: "operating-systems"
difficulty: "advanced"
tags: [interrupts, hardware, x86]
related: [device-driver-uart, minimal-kernel, unix-signals]
---

# Interrupt Handling

Interrupts are how hardware gets the CPU's attention: a device raises a line, the CPU suspends what it's doing and jumps to a handler. Building interrupt handling yourself — descriptor tables, the PIC/APIC, top/bottom halves — teaches you the mechanism behind every keystroke, packet, and timer tick the OS processes.

## Core concepts

- **Interrupts vs exceptions vs traps** — Interrupts come from hardware asynchronously (keyboard, timer); exceptions are synchronous CPU faults (divide-by-zero, page fault); traps are deliberate (syscall). All funnel through descriptor tables but with different semantics.
- **The IDT (Interrupt Descriptor Table)** — On x86, a 256-entry table mapping vector numbers to handler addresses with privilege levels. `lidt` installs it; the CPU consults it on every interrupt/exception.
- **PIC vs APIC** — The legacy 8259 PIC routes 15 IRQs with a master/slave cascade and needs an end-of-interrupt (EOI) ack. Modern systems use the APIC: per-CPU local APICs plus an I/O APIC, supporting 24+ IRQs, IPIs, and MSI.
- **Interrupt context constraints** — Handlers run with interrupts disabled (or at raised IRQL), on a special stack, and can't sleep. They must be fast: acknowledge the device, stash data, defer the rest.
- **Top halves and bottom halves** — The top half (hard IRQ handler) does the minimum; the bottom half (softirq, tasklet, workqueue) does the heavy processing later with interrupts enabled. This split is why high packet rates don't livelock the kernel.
- **Interrupt affinity and MSI** — IRQs can be pinned to specific CPUs (`/proc/irq/N/smp_affinity`), and MSI/MSI-X lets PCI devices write directly to LAPIC registers instead of sharing legacy lines — no more IRQ conflicts.
- **NMI and the unmaskable** — Non-maskable interrupts can't be disabled; they're reserved for catastrophic events (hardware failure, watchdog). If your NMI handler runs, something is deeply wrong.

## How it works

When a device signals an interrupt, the (I/O) APIC delivers it to a CPU's local APIC, which vectors through the IDT: the CPU pushes flags, CS, and RIP onto the interrupt stack, clears the interrupt flag, and jumps to the handler address from the IDT entry. Your handler (written in assembly for the entry stub, then C) saves registers, identifies the device, reads/clears its status, copies data into a ring buffer, sends EOI to the APIC, and schedules a bottom half for the rest before `iret`-ing back to the interrupted code. On Linux the flow is `do_IRQ` → driver IRQ handler (top half) → softirq/tasklet → workqueue, with `/proc/interrupts` showing per-CPU counts. Miss the EOI or forget to clear the device's interrupt source and the line stays asserted — the classic interrupt storm.

## Build milestones

1. In a hobby kernel, install an IDT with a divide-by-zero handler: trigger it deliberately and print a register dump — your first synchronous exception.
2. Remap the 8259 PIC (it's at the wrong vectors by default, colliding with CPU exceptions) and handle the PIT timer tick: print a counter at 100Hz.
3. Handle the keyboard IRQ: read scancodes from port 0x60, translate to ASCII, and echo — with proper EOI to both PICs.
4. Split into top/bottom halves: the IRQ handler only enqueues scancodes; a deferred task processes them with interrupts enabled.
5. Bring up the APIC: disable the PIC, enumerate via ACPI MADT, route IRQs through the I/O APIC, and handle timer interrupts from the local APIC.
6. Implement MSI for a PCI device in QEMU (e.g. e1000): no legacy IRQ line, per-vector handlers, and verify with per-CPU counts.

## Best resources

- [OSDev Wiki — Interrupts](https://wiki.osdev.org/Interrupts) — the practical starting point: IDT setup and exception handlers.
- [OSDev Wiki — 8259 PIC](https://wiki.osdev.org/8259_PIC) — remapping and programming the legacy interrupt controller.
- [OSDev Wiki — APIC](https://wiki.osdev.org/APIC) — local APIC, I/O APIC, and the modern interrupt path.
- [Linux kernel: IRQ subsystem docs](https://www.kernel.org/doc/html/latest/core-api/irq/index.html) — how Linux abstracts controllers, handlers, and affinity.
- [Intel SDM Volume 3A, Chapter 6](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) — interrupt and exception handling, authoritative and precise.
- [Understanding the Linux Kernel, Ch. 4 (Bovet & Cesati)](https://www.oreilly.com/library/view/understanding-the-linux/0596005652/) — the classic chapter on interrupts and deferred work.

## Stretch ideas

- Write an interrupt latency benchmark: timestamp in the handler vs the event, and measure jitter under load.
- Implement interrupt threading (like PREEMPT_RT's threaded IRQs) where handlers run as schedulable threads.
