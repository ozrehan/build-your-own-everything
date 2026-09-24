---
title: "Build Your Own Assembler"
category: "programming-languages"
difficulty: "intermediate"
tags: [low-level, systems, compilers]
related: [linker, bytecode-virtual-machine, formal-grammars-ebnf]
---

# Build Your Own Assembler

An assembler is the simplest real compiler: it translates human-readable mnemonics like `mov rax, 1` into the exact bytes the CPU executes. Writing one demystifies machine code completely — instruction encodings, addressing modes, and object files stop being magic and become table lookups. The classic design is the two-pass assembler: pass one collects labels into a symbol table, pass two emits bytes, and forward references just work.

## Core concepts

- **Mnemonics to opcodes** — an opcode table maps each mnemonic plus operand shape to its byte encoding; most of an assembler is table-driven.
- **Two passes solve forward references** — pass one assigns addresses and records labels; pass two emits code with every label address known.
- **The symbol table** — labels map to addresses, built in pass one and consulted in pass two; duplicate and undefined labels are assembler errors.
- **The location counter** — the running address that advances by each instruction's size; directives like `org` and alignment manipulate it.
- **Instruction encoding** — x86 uses prefixes, opcode, ModR/M, SIB, displacement, and immediate bytes; even a tiny subset teaches you how CPUs decode.
- **Object file emission** — beyond raw bytes, real assemblers emit relocatable object files (ELF/Mach-O) with sections, symbols, and relocations for the linker.

## How it works

Each source line tokenizes into an optional label, a mnemonic, and operands. Pass one walks the lines maintaining the location counter: labels get entered into the symbol table with the current address, and the counter advances by the instruction's size (looked up in the opcode table by mnemonic and operand kinds) or by data directives. Pass two walks the lines again, this time encoding each instruction — opcode byte, ModR/M, immediates — and resolving label operands through the now-complete symbol table. The output is either a flat binary or a relocatable object file; a listing file showing addresses beside source lines is how you verify the encoding.

## Build milestones

1. Define a tiny instruction set (8–12 instructions) with fixed-width encoding; assemble straight-line code to raw bytes and run it in an emulator.
2. Add labels and jumps: pass one builds the symbol table, pass two resolves addresses; test forward and backward jumps.
3. Add data directives (`.word`, `.asciiz`) and a location counter with alignment handling.
4. Implement a two-pass assembler for a useful subset of a real architecture (x86-64 or RISC-V), using the NASM manual or instruction reference for encodings.
5. Emit a real relocatable object file (ELF `.o`) with `.text`, a symbol table, and relocations; link it with the system linker.

## Best resources

- [NASM documentation](https://www.nasm.us/xdoc/2.16.03/html/nasmdoc0.html) — the Netwide Assembler manual: syntax, directives, macros, and output formats.
- [Programming from the Ground Up](https://github.com/billsix/programmingFromTheGroundUp) — Jonathan Bartlett's book teaching x86 assembly and how assemblers see the machine.
- [x86 instruction reference](https://www.felixcloutier.com/x86/no-longer-updated) — the complete x86/x64 instruction encoding reference you'll consult constantly.
- [Assembler tutorial (Phoenix docs)](https://github.com/hansolovkarlsson/phoenix/blob/HEAD/docs/tutorial-assembler.md) — a worked tutorial on why assembly needs two passes, with the failed one-pass attempt shown first.

## Stretch ideas

- Add macro processing (textual macros with parameters) as a pass-zero before assembly.
- Write a disassembler for your instruction set and round-trip test: assemble → disassemble → assemble.
- Target a second architecture and factor all machine-dependent parts behind a clean interface.
