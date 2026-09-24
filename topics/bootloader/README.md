---
title: "Bootloader"
category: "operating-systems"
difficulty: "intermediate"
tags: [boot, x86, firmware]
related: [minimal-kernel, assembler, elf-loader]
---

# Bootloader

A bootloader is the first software that runs when a computer powers on: it bridges the firmware (BIOS/UEFI) and your operating system, loading a kernel into memory and handing it control. Building one yourself teaches you exactly how a machine goes from a blank CPU to running code — real mode, memory maps, and the first bytes of an OS.

## Core concepts

- **POST and firmware** — On power-up, firmware runs self-tests and hardware init, then finds a boot device and loads the first sector of code. A bootloader has to know what the firmware promises it and what it doesn't.
- **Real mode (x86)** — The CPU starts in 16-bit real mode with 20-bit segmented addressing and no memory protection. Your bootloader's first instructions execute in this limited environment before switching to protected or long mode.
- **The boot sector** — On legacy BIOS systems, the first 512 bytes of a disk (ending with the 0x55AA magic signature) are loaded to address 0x7C00 and executed. Those 510 bytes of usable code define stage 1.
- **Multistage booting** — Because 512 bytes is tiny, real bootloaders load in stages: stage 1 loads a bigger stage 2 from disk, which does the heavy lifting like filesystem parsing and decompression.
- **Memory map (E820)** — The firmware provides a map of which physical memory regions are usable RAM versus reserved hardware. A kernel must ask for this before the firmware is gone.
- **A20 line and GDT** — Enabling the A20 address line lets the CPU address memory above 1MB, and setting up a Global Descriptor Table is required to leave real mode for 32-bit protected mode.
- **BIOS interrupts (INT 0x13)** — The simplest way to read disk sectors in real mode is calling firmware services via software interrupts. A bootloader leans on these before the OS has its own drivers.

## How it works

On a legacy BIOS boot, firmware loads the 512-byte boot sector to 0x7C00 and jumps to it. The bootloader's stage 1 uses BIOS services to read additional sectors (stage 2) from disk into memory, then jumps to them. Stage 2 typically parses a filesystem (or a raw kernel image at a known location), loads the kernel ELF or binary to a fixed physical address, collects the memory map, switches the CPU into protected/long mode, sets up a stack, and jumps to the kernel's entry point. On UEFI systems the flow is friendlier: firmware loads a PE-format bootloader application from a FAT-formatted EFI partition, giving it a full API for memory allocation and disk access before calling ExitBootServices() and jumping to the kernel.

## Build milestones

1. Write a 512-byte boot sector in x86 assembly that prints a message via BIOS interrupts (INT 0x10) and hangs — boot it in QEMU with `qemu-system-i386`.
2. Extend stage 1 to read sector 2 from disk with INT 0x13 and jump to it; stage 2 prints its own message to prove the handoff worked.
3. Query the E820 memory map and print the usable regions, then enable the A20 line and switch to 32-bit protected mode with a minimal GDT.
4. Build a two-stage bootloader that loads a flat binary kernel image to 0x100000 (1MB) and jumps to it with a valid stack.
5. Add FAT32 parsing to stage 2 so the kernel is loaded by filename instead of fixed sectors — your bootloader now survives a disk defragment.
6. Write a UEFI application variant: parse the memory map via UEFI boot services, call ExitBootServices(), and jump to a 64-bit kernel in long mode.

## Best resources

- [OSDev Wiki](https://wiki.osdev.org/Main_Page) — the canonical OS-dev reference; start with "Bootloader", "Bare Bones", and "Rolling Your Own Bootloader".
- [os-tutorial by cfenollosa](https://github.com/cfenollosa/os-tutorial) — a hands-on GitHub repo building a bootloader and tiny kernel from zero, with clear chapters.
- [The little book about OS development](https://littleosbook.github.io/) — short free book walking through a minimal x86 OS from boot sector to kernel.
- [Intel 64 and IA-32 Software Developer Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) — the authoritative CPU reference; Volume 3A covers modes and system programming.
- [UEFI Specification](https://uefi.org/specifications) — the official spec for the modern boot interface, including boot services and the memory map.

## Stretch ideas

- Add a boot menu with a timeout and multiple kernel choices, reading configuration from disk.
- Implement password protection or signature verification of the kernel image before jumping to it (a toy secure boot).
