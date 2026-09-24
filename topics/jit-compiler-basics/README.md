---
title: "Build Your Own JIT Compiler (Basics)"
category: "programming-languages"
difficulty: "advanced"
tags: [compilers, performance, virtual-machines]
related: [bytecode-virtual-machine, mark-sweep-garbage-collector, assembler]
---

# Build Your Own JIT Compiler (Basics)

A just-in-time compiler watches your program run, finds the hot loops, and compiles them to native machine code on the fly — which is why JavaScript, Java, and Lua can rival C on numeric code. The core loop is simple to describe and thrilling to build: profile execution, compile the hot path, guard your assumptions, and bail back to the interpreter when a guard fails. Spencer Tipping's JIT tutorial builds a working JIT for a tiny language from first principles.

## Core concepts

- **Tiered execution** — start by interpreting, count loop iterations, and promote hot code to compiled tiers; most code never gets compiled, and that's fine.
- **Tracing vs. method JITs** — a tracing JIT records the actual path taken through a hot loop; a method JIT compiles whole functions. Traces are simpler to build first.
- **Type specialization and guards** — compile assuming `x` is an integer, and emit a guard that checks the assumption, exiting to the interpreter if it fails.
- **Inline caches** — cache a lookup's result at the call site keyed by the receiver's type; megamorphic sites fall back to the slow lookup.
- **Deoptimization** — when a guard fails, reconstruct interpreter state from the compiled frame and continue there; this safety net is what makes speculation sound.
- **Code cache management** — generated machine code lives in executable memory (allocated with `mmap` and `PROT_EXEC`); flushing and invalidation keep it coherent with the program.

## How it works

You begin with a bytecode interpreter augmented with execution counters on loops or opcodes. When a loop goes hot, the VM switches to recording mode and captures the linear trace of bytecodes executed — one path, no branches inside. The trace compiles to native code: integer arithmetic becomes a handful of x86-64 instructions, with guards at the entry and at every assumption (types, array bounds). Guard failures are side exits that spill registers back into interpreter state and resume the dispatch loop. The compiled trace lives in an executable code cache keyed by the loop's identity, so the next ten million iterations never touch the interpreter.

## Build milestones

1. Write a tiny bytecode interpreter for arithmetic loops with per-loop execution counters.
2. When a loop goes hot, record a linear trace of the bytecodes it executes (one path, no branches inside the trace).
3. Compile the trace to native code: hand-emit x86-64 for integer ops, or generate C and shell out to a compiler for your first version.
4. Add type guards on trace entry plus side exits that bail back to the interpreter; verify correctness on mixed-type programs.
5. Add an inline cache for one dynamic operation (a method call or property load) and measure the speedup on a benchmark loop.

## Best resources

- [JIT tutorial](https://github.com/spencertipping/jit-tutorial) — Spencer Tipping's from-first-principles tutorial building a working JIT for a tiny language.
- [Kaleidoscope: Adding JIT and Optimizer Support](https://releases.llvm.org/20.1.0/docs/tutorial/MyFirstLanguageFrontend/LangImpl04.html) — the LLVM tutorial chapter that plugs a real JIT (ORC) into a toy language.
- [LuaJIT (Wikipedia)](https://en.wikipedia.org/wiki/LuaJIT) — the canonical tracing JIT: how Mike Pall's design made a dynamic language fast.
- [LuaJIT internals documentation [pdf]](https://raw.githubusercontent.com/MethodicalAcceleratorDesign/MADdocs/master/luajit/luajit-doc.pdf) — bytecode format, trace recorder, and GC internals of a production JIT.

## Stretch ideas

- Compile traces with a real backend (DynASM, LLVM ORC, or Cranelift) instead of hand-emitted bytes.
- Implement on-stack replacement so a long-running loop can jump into compiled code mid-flight.
- Add a second optimization over your trace IR: loop-invariant code motion or simple constant propagation.
