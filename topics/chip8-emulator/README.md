---
title: "CHIP-8 Emulator"
category: "games-graphics"
difficulty: "beginner"
tags: ["emulation", "retro", "cpu"]
related: [audio-synthesizer, save-system, ascii-roguelike]
---

# CHIP-8 Emulator
CHIP-8 is a tiny interpreted language from the 1970s that ran simple games on 8-bit microcomputers. Writing an emulator for it is the classic first emulation project: only 35 opcodes, 4KB of memory, and a 64×32 monochrome display. You will learn fetch-decode-execute, timers, and input — the skeleton of every emulator.

## Core concepts

- **Memory map**: 4KB of RAM; the first 512 bytes are reserved for the interpreter, so programs load at address 0x200. A built-in font set lives in low memory.
- **Registers**: Sixteen 8-bit general registers V0–VF (VF doubles as a flag for carries and collisions), plus a 16-bit index register I and program counter PC.
- **Fetch-decode-execute**: Each cycle reads two bytes at PC, decodes the 16-bit opcode, executes it, and advances PC — the heartbeat of the virtual CPU.
- **Stack**: Subroutine calls (2NNN) push the return address; returns (00EE) pop it. A 16-level stack is plenty.
- **Display**: A 64×32 monochrome framebuffer drawn with XOR sprites; drawing sets VF to 1 on pixel collision, which games use for hit detection.
- **Timers**: Delay and sound timers tick down at 60Hz independently of the CPU; the sound timer buzzes while nonzero.
- **Keypad**: A 16-key hex keypad (0–F) mapped to a modern keyboard; opcodes can wait for or skip on key presses.

## How it works

Load the ROM into memory at 0x200 and set PC there. In a loop running a few hundred cycles per second: fetch the two bytes at PC, decode the opcode's nibbles (its first hex digit selects the instruction family), and execute — arithmetic on registers, jumps, sprite draws to the framebuffer, keypad checks. Decrement both timers at 60Hz, render the framebuffer to a window, and play a beep while the sound timer is active.

## Build milestones

1. Set up memory, registers, and a fetch-decode-execute loop that can run no-op cycles.
2. Implement the flow and register opcodes (jumps, calls, loads, arithmetic) and load a ROM.
3. Add the 64×32 XOR sprite display and render it to a window.
4. Implement timers, the hex keypad, and the sound beep; run the IBM logo ROM.
5. Handle quirks (shift and memory-increment behaviors differ between original and SUPER-CHIP).
6. Get Pong and Space Invaders fully playable with save states and adjustable CPU speed.

## Best resources

- [Write a CHIP-8 Emulator — Tobias Langhoff](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/) — a thorough modern guide to the whole system.
- [CHIP-8 Emulator — Austin Morlan](https://austinmorlan.com/posts/chip8_emulator/) — clean C++ tutorial building an emulator step by step.
- [chip-8 reference implementation](https://github.com/alaaarmoush/chip-8) — a complete implementation to compare your opcode handling against.
- [Cowgod's CHIP-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) — the canonical opcode and hardware reference.

## Stretch ideas

- Add SUPER-CHIP extensions (128×64 resolution, scrolling opcodes) and a debugger with breakpoints.
- Reimplement the emulator in a second language and run the same ROM test suite against both.
