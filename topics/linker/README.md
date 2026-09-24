---
title: "Build Your Own Linker"
category: "programming-languages"
difficulty: "advanced"
tags: [low-level, systems, compilers]
related: [assembler, bytecode-virtual-machine, package-manager]
---

# Build Your Own Linker

A linker is the program that turns scattered object files into one runnable executable: it merges sections, assigns final addresses, and patches every cross-file reference. Every `gcc main.c util.c` invocation ends with a link step, and understanding it explains static vs. dynamic linking, shared libraries, and most mysterious "undefined reference" errors. Ian Lance Taylor's 20-part blog series walks the entire design, and John Levine's *Linkers & Loaders* is the canonical book.

## Core concepts

- **Object files as section bags** — `.o` files carry `.text`, `.data`, symbol tables, and relocation entries; the linker's input is structured data, not code.
- **Symbol resolution** — the linker merges all symbol tables; each undefined reference must match exactly one definition. Duplicates and missing symbols are link errors.
- **Relocation** — instructions referencing symbols contain placeholders; the linker patches them with final addresses once layout is fixed, guided by relocation entries.
- **Section merging and layout** — all `.text` sections concatenate into one segment; a linker script decides addresses, alignment, and ordering.
- **Static vs. dynamic linking** — static linking copies library code into the binary; dynamic linking leaves PLT/GOT stubs resolved at load time by `ld.so`, trading startup cost for shared memory.
- **The two views of ELF** — sections exist for the linker, segments for the loader; one file serves both masters through different header tables.

## How it works

The linker reads each object file's headers to find its sections, symbol table, and relocation tables. It merges same-named sections (all `.text` pieces become one), building a global symbol table and flagging duplicate or undefined symbols. Then it assigns final virtual addresses to every section, honoring alignment. Finally it walks every relocation entry — each naming an offset, a symbol, and a relocation type — and patches the placeholder bytes with the symbol's final address (absolute) or the computed distance (PC-relative). The result is written as an executable with program headers the kernel loader understands, or as a shared object with dynamic-linking metadata.

## Build milestones

1. Write an ELF reader: parse headers and list sections and symbols of a real `.o` file; verify your output against `readelf`.
2. Implement a static linker for your own assembler's object files: merge `.text`/`.data`, resolve symbols across two files, apply simple absolute relocations.
3. Add PC-relative relocations (call/jump patching) and link a multi-file "hello world".
4. Support archives (`.a`): extract only the members that resolve currently-undefined symbols, like real linkers do.
5. Implement basic dynamic linking: emit PLT/GOT entries and a `.dynamic` section — or write a tiny `ld.so`-style loader that resolves them at startup.

## Best resources

- [Linkers — Stephen Checkoway](https://checkoway.net/musings/linkers/) — a clear tutorial introduction to what linkers do and why object files look the way they do.
- [Linkers series — Ian Lance Taylor](https://www.airs.com/blog/archives/38/comment-page-1) — twenty blog posts from a gold-linker author covering every corner of real linker design.
- [Notes on the linker series](https://github.com/alfedotov/airs-notes) — community study notes summarizing Taylor's series post by post.
- [Object Files — Linkers & Loaders, ch. 3 [pdf]](http://www.staroceans.org/e-book/linkerAndLoader/linker03.pdf) — John Levine's canonical chapter on object file formats (mirror of the classic book).

## Stretch ideas

- Write a linker script language supporting custom section placement and symbol definitions.
- Implement link-time dead-code elimination (`--gc-sections` semantics) using reachability over the relocation graph.
- Add incremental linking: re-link only changed objects by caching section layouts.
