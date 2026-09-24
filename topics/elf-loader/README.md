---
title: "ELF Loader"
category: "operating-systems"
difficulty: "intermediate"
tags: [elf, binaries, linker]
related: [linker, bootloader, minimal-kernel]
---

# ELF Loader

ELF is the binary format of Unix: the loader parses its headers, maps loadable segments into memory with the right permissions, and jumps to the entry point. Writing an ELF loader teaches you how executables are structured, what the linker actually produced, and the machinery behind every program launch.

## Core concepts

- **ELF header and magic** — Every ELF starts with `0x7F 'E' 'L' 'F'`, plus class (32/64-bit), endianness, and type (executable, shared object, relocatable). Validating the magic is the loader's first job.
- **Program headers (segments)** — `PT_LOAD` segments describe what to map: file offset, virtual address, sizes, and R/W/X flags. The loader `mmap`s each at its virtual address — this is what "loading a program" literally is.
- **Sections vs segments** — Sections (`.text`, `.data`, `.bss`) are the linker's view for tools like `readelf`; segments are the loader's view at runtime. A running program needs only segments.
- **BSS and zero-fill** — `.bss` (uninitialized globals) occupies no file space: `memsz > filesz` in the segment header tells the loader to zero-fill the tail. This is why large zero arrays don't bloat binaries.
- **The entry point** — `e_entry` is the virtual address where execution begins (usually `_start`, not `main`). The loader jumps there after setting up the stack with argc/argv/envp.
- **Dynamic linking** — Dynamically linked binaries have a `PT_INTERP` segment naming the loader (`/lib64/ld-linux-x86-64.so.2`) and relocation tables; the dynamic linker maps shared libraries and patches addresses before `main` runs.
- **Position-independent executables (PIE)** — Modern binaries are `ET_DYN`: the loader picks a random base address (ASLR) and adds it to every virtual address. Static addresses in your loader must become base + offset.

## How it works

The loader opens the file, reads and validates the ELF header, then iterates the program header table. For each `PT_LOAD` segment it allocates memory at the segment's virtual address (aligned to page boundaries), copies `filesz` bytes from the file offset, and zeroes the remaining `memsz - filesz` for BSS. It applies the segment flags as page protections (R/W/X), sets up the initial stack with argc, argv, envp, and the auxiliary vector, then jumps to `e_entry`. For dynamic binaries the kernel actually maps the `PT_INTERP` interpreter first and jumps to *its* entry point; the interpreter then loads the main binary and its `DT_NEEDED` libraries, performs relocations, calls initializers, and finally transfers control to the program.

## Build milestones

1. Write an ELF parser: read a compiled "hello world", validate the magic, and print all program headers with `readelf -l` as your answer key.
2. Load a statically linked binary: map its `PT_LOAD` segments into memory with correct permissions, zero the BSS, and jump to `e_entry` — print from the guest program to prove it ran.
3. Set up the initial stack properly (argc/argv/envp/auxv per the ABI) so the loaded program can read its arguments and environment.
4. Support PIE: load an `ET_DYN` executable at a random base, relocating all virtual addresses — verify ASLR changes the base each run.
5. Handle `PT_INTERP`: map the dynamic linker and jump to it, letting it do relocations for a dynamically linked "hello world".
6. Implement minimal relocation yourself: parse `.rela.dyn`, apply `R_X86_64_RELATIVE` relocations, and load a dynamic binary without invoking the system ld.so.

## Best resources

- [elf(5) man page](https://man7.org/linux/man-pages/man5/elf.5.html) — the structure reference: headers, program headers, sections.
- [OSDev Wiki — ELF](https://wiki.osdev.org/ELF) — loading ELF in a hobby OS, with the segment-mapping logic spelled out.
- [OSDev Wiki — ELF Tutorial](https://wiki.osdev.org/ELF_Tutorial) — a hands-on companion to the ELF article.
- [Linkers and Loaders (John Levine)](https://www.iecc.com/linker/) — the full book free online; chapters 3 and 8 cover ELF and loading deeply.
- [A Whirlwind Tutorial on Creating Really Teensy ELF Executables](http://www.muppetlabs.com/~breadbox/software/tiny/teensy.html) — hand-crafting minimal ELFs teaches the format like nothing else.
- [The ELF specification (SCO)](https://refspecs.linuxfoundation.org/elf/elf.pdf) — the original System V ABI document defining ELF.

## Stretch ideas

- Write a static binary rewriter: parse an ELF, inject a new segment that prints a message, and redirect the entry point through it.
- Implement lazy PLT binding so function calls resolve on first use, and measure the startup cost.
