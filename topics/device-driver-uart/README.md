---
title: "UART Device Driver"
category: "operating-systems"
difficulty: "intermediate"
tags: [drivers, uart, serial]
related: [interrupt-handling, minimal-kernel, terminal-emulator]
---

# UART Device Driver

A UART (serial port) is the simplest real hardware a kernel can talk to: a few I/O registers that send and receive bytes one at a time. Writing a UART driver is the traditional first device driver because it teaches memory-mapped/port I/O, polling vs interrupts, and ring buffers — and it gives your kernel a debug console that works when everything else is broken.

## Core concepts

- **Port I/O vs memory-mapped I/O** — x86 devices are often driven with `in`/`out` instructions on a separate 16-bit port address space (COM1 lives at 0x3F8). ARM typically maps device registers into normal memory instead.
- **The 16550 register set** — A PC UART exposes ~8 registers at consecutive ports: transmit/receive data, interrupt enable, FIFO control, line control (baud, parity, stop bits), and line status. The datasheet is the whole API.
- **Baud rate and the divisor latch** — Setting the DLAB bit repurposes the data registers to accept a clock divisor; 115200 baud with a 1.8432MHz clock means divisor 1. Getting this wrong produces garbage characters.
- **Polling vs interrupts** — Polling spins on the "transmit buffer empty" status bit — simple but wasteful. Interrupt-driven I/O lets the UART raise an IRQ when it needs service, freeing the CPU.
- **Ring buffers** — The standard decoupling structure: the interrupt handler pushes received bytes into a circular buffer, and `read()` pops them. Head/tail indices with wraparound handle the producer/consumer race.
- **Flow control** — Hardware (RTS/CTS lines) or software (XON/XOFF characters) signaling so a fast sender doesn't overrun a slow receiver's FIFO.
- **Why serial is the debug lifeline** — Serial output needs no interrupts, no DMA, no complex init: a few port writes and bytes appear on the host terminal. That's why kernels print panics to serial first.

## How it works

At boot the driver initializes the UART: disable interrupts, set DLAB and write the baud divisor, configure 8 data bits / no parity / 1 stop bit, enable FIFOs, then re-enable interrupts. Transmitting polls the line-status register until the transmit-holding-register-empty bit is set, then writes the byte to the data port. Receiving via interrupt: the UART raises IRQ4 when a byte arrives; the handler reads the interrupt-identification register to confirm, drains the receive FIFO into a ring buffer, and returns. A `read()` syscall blocks on a wait queue until the ring buffer is non-empty, copies bytes out, and the whole path from keystroke to program works without busy-waiting.

## Build milestones

1. Write a polled `serial_putc` using `outb` to COM1 (0x3F8): init the UART at 38400 baud, 8N1, and print "hello" — view it with QEMU's `-serial stdio`.
2. Add `serial_getc` (polled receive) and a tiny echo loop: type in the QEMU terminal, see characters come back.
3. Convert receive to interrupts: route IRQ4 through your IDT/PIC, write the handler to fill a 256-byte ring buffer, and make echo work without polling.
4. Add blocking `read()` semantics: the syscall sleeps on a wait queue when the ring buffer is empty and is woken by the interrupt handler.
5. Implement `printf`-style formatted output with a lock so concurrent kernel threads don't interleave characters.
6. Add transmit interrupts with a TX ring buffer (for throughput) and hardware flow control (RTS/CTS) handling.

## Best resources

- [OSDev Wiki — Serial Ports](https://wiki.osdev.org/Serial_Ports) — register-level guide to programming the 16550 UART, the standard reference.
- [OSDev Wiki — UART](https://wiki.osdev.org/UART) — broader UART concepts and programming notes.
- [Linux serial driver (8250.c)](https://github.com/torvalds/linux/blob/master/drivers/tty/serial/8250/8250_port.c) — how the real Linux driver handles the same hardware.
- [Baking Pi — Operating Systems Development (Cambridge course overview)](https://community.element14.com/learn/publications/w/documents/10385/learn-how-to-develop-an-operating-system-with-the-raspberry-pi) — the classic Raspberry Pi bare-metal UART tutorial for the ARM memory-mapped side.

## Stretch ideas

- Write the same driver for a memory-mapped ARM PL011 UART on QEMU's `virt` board and compare the two approaches.
- Implement a SLIP or minimal PPP layer over serial to get IP packets across your UART.
