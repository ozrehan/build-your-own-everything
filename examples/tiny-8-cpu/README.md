# Example: Operating Systems — TINY-8 CPU

**[▶ Try it live](https://byoe-8bit-cpu.netlify.app)**

A complete working 8-bit CPU in one file: the **fetch → decode → execute** cycle,
4 registers, 32 bytes of RAM, and an assembly language you program in the browser.
Every OS boots on top of exactly this loop.

Example project for the [operating-systems learning path](../../topics/minimal-kernel/).

## The machine

- 8 instructions: `LOAD ADD SUB STORE LOADM CMP JMP/JZ/JNZ OUT HLT`
- 4 registers (R0–R3), zero-flag, program counter, 32 bytes RAM
- Two-pass assembler (labels → addresses), step/run/reset, adjustable clock speed

## What it teaches

| Part | Concept |
|---|---|
| `step()` | the fetch-decode-execute cycle every processor runs |
| `assemble()` | what an assembler does: labels, two passes |
| zero-flag + `JZ` | conditionals are just flags + jumps |
| `OUT` | memory-mapped I/O — how CPUs talk to devices |

## Exercises

1. Add a **stack** (`PUSH`/`POP`/`CALL`/`RET`) and write a recursive function.
2. Add **interrupts**: a timer that pauses the program periodically.
3. Write a tiny **monitor program** in TINY-8 assembly that reads "keystrokes".
