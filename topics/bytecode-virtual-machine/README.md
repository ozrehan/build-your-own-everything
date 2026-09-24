---
title: "Build Your Own Bytecode Virtual Machine"
category: "programming-languages"
difficulty: "intermediate"
tags: [interpreters, virtual-machines, compilers]
related: [tree-walking-interpreter, jit-compiler-basics, mark-sweep-garbage-collector]
---

# Build Your Own Bytecode Virtual Machine

A bytecode virtual machine compiles source code to a compact stream of numeric instructions, then executes them with a simple stack-based loop — the same architecture behind the JVM, CPython, and Lua. Compiling once and interpreting the dense bytecode is typically an order of magnitude faster than walking a syntax tree, because dispatch happens on single bytes instead of polymorphic node objects. *Crafting Interpreters* Part III builds exactly this: clox, a complete bytecode VM in C with closures and garbage collection.

## Core concepts

- **Bytecode as a portable ISA** — opcodes are small integers and operands live in a constant pool; the compiled chunk is plain data you can serialize, inspect, and disassemble.
- **The stack machine** — values are pushed and popped on an operand stack rather than held in registers; most instructions are zero-address (`OP_ADD` pops two values and pushes one), which keeps the compiler trivial.
- **The dispatch loop** — a tight loop reads an opcode and jumps to its handler via `switch` or computed goto; instruction dispatch is the VM's hot path and its dominant cost.
- **Single-pass Pratt compiler** — expressions compile straight to bytecode using a precedence table, with no AST ever built, which keeps memory usage small and compilation fast.
- **Call frames** — each function call pushes a frame holding the function, instruction pointer, and stack base; locals are stack slots addressed relative to the frame.
- **Upvalues for closures** — a local captured by a nested function is heap-allocated as an upvalue so it outlives its stack frame; the VM tracks open vs. closed upvalues.

## How it works

The compiler translates source to a chunk: a byte array of opcodes interleaved with operand bytes, plus a constant table and line-number info for errors. The VM runs a fetch-decode-execute loop over the chunk, manipulating the value stack: `OP_CONSTANT` pushes a constant, `OP_ADD` pops two numbers and pushes their sum, `OP_JUMP_IF_FALSE` patches control flow. Function calls allocate a call frame pointing at a fresh stack window; when the frame's instruction pointer hits `OP_RETURN`, the frame pops and the return value lands on the caller's stack. A disassembler that prints chunks in human-readable form is not optional tooling — it is how you debug the compiler.

## Build milestones

1. Implement the chunk representation (code bytes, constants, line info) plus a disassembler, and a VM loop executing constants and arithmetic.
2. Write the Pratt compiler: expressions with precedence compiling directly to bytecode, plus global variables.
3. Compile locals and lexical scoping to stack slots; implement `if`/`while` via jump emission and backpatching.
4. Add functions: call frames, arity checks, native functions, and closures with upvalues.
5. Integrate a mark-sweep garbage collector (grey stack, string interning, hash tables) so the VM manages memory itself.

## Best resources

- [Crafting Interpreters](https://craftinginterpreters.com/) — Part III builds clox, a bytecode VM in C: chunks, a Pratt compiler, closures, and GC, all from scratch.
- [clox in C](https://github.com/kwakker35/clox) — a complete C implementation following the book's VM chapters; useful for diffing against your own.
- [Lox interpreter implementations](https://github.com/chrisjose7/lox-interpreter) — another book-following implementation to compare design choices with.
- [Crafting Interpreters implementations](https://github.com/ngendah/crafting-interpreters) — a further implementation of both the tree-walker and the VM for reference.
- [LuaJIT (Wikipedia)](https://en.wikipedia.org/wiki/LuaJIT) — the production-grade example of a bytecode VM with a tracing JIT on top; shows where this architecture leads.
- [LuaJIT internals documentation [pdf]](https://raw.githubusercontent.com/MethodicalAcceleratorDesign/MADdocs/master/luajit/luajit-doc.pdf) — deep dive into a real bytecode VM's design: bytecode format, GC, and FFI.

## Stretch ideas

- Add a peephole optimizer (constant folding, jump threading) and benchmark a numeric workload before and after.
- Implement classes and methods, or a module system, on top of the VM's function and upvalue machinery.
- Try a register-based instruction set and measure its dispatch cost against your stack machine.
