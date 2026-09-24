---
title: "Build Your Own Mark-Sweep Garbage Collector"
category: "programming-languages"
difficulty: "advanced"
tags: [garbage-collection, memory-management, runtimes]
related: [bytecode-virtual-machine, memory-allocator, jit-compiler-basics]
---

# Build Your Own Mark-Sweep Garbage Collector

A mark-sweep garbage collector finds memory your program can no longer reach and reclaims it automatically, so programmers never call `free`. It works in two phases — mark everything reachable from the roots, then sweep away the rest — and it is the collection algorithm every language implementer should build first. Bob Nystrom's "Baby's First Garbage Collector" implements a precise mark-sweep collector in about a hundred lines of C.

## Core concepts

- **Roots** — the pointer set the collector starts from: the VM stack, global variables, registers. Anything not reachable from a root is garbage by definition.
- **The mark phase (tracing)** — a depth-first walk from the roots flips an `is_marked` bit on each object; the tri-color abstraction (white/grey/black) describes the same walk more generally.
- **The sweep phase** — a linear scan of the heap frees every unmarked object and unmarks the survivors in the same pass.
- **Precise vs. conservative** — a precise collector knows exactly which words are pointers via object headers or tags; a conservative collector (like Boehm's) treats any word that *could* be a pointer as one, and never moves objects.
- **Fragmentation** — freed blocks return to a free list; splitting and coalescing blocks keeps allocation working, but fragmentation is the long-term tax mark-sweep pays.
- **Write barriers and generations** — production collectors add barriers to track old-to-young pointers and collect the young generation more often; your first collector can stay single-generation.

## How it works

Every heap object gets a header with a mark bit, and all allocated objects link into a list the collector can traverse. Collection triggers when allocated bytes pass a threshold. Marking starts from the roots — for a VM, that means walking the value stack, call frames, globals, and the compiler's temporary roots — following every pointer with an explicit grey stack rather than C recursion (deep object graphs would overflow the C stack). Sweeping then walks the object list: unmarked objects are unlinked and freed, marked ones get their bit cleared for the next cycle. Two testing tricks make this tractable: a stress mode that collects on *every* allocation, and logging that prints each collection's before/after heap size so leaks show up immediately.

## Build milestones

1. Define the object model: heap objects with a mark bit threaded on a singly linked list of all allocations; start with manual free so you can watch leaks happen.
2. Implement roots and marking: mark from a root set (a stack of values, globals), following pointers recursively at first.
3. Implement the sweep: free unmarked objects, unmark survivors; add a stress-test flag that collects on every allocation to shake out marking bugs.
4. Replace recursive marking with an explicit grey stack; add an allocation threshold that grows after each collection to amortize GC cost.
5. Wire the collector into a real host — a tree-walking interpreter or bytecode VM — and watch heap size stabilize under a loop that allocates garbage.

## Best resources

- [Baby's First Garbage Collector](https://journal.stuffwithstuff.com/2013/12/08/babys-first-garbage-collector/) — Bob Nystrom's classic: a precise mark-sweep GC in ~100 lines of C, with clear explanation of roots, marking, and sweeping.
- [The Garbage Collection Handbook](https://gchandbook.org/) — the companion site to Jones, Hosking & Moss's book; the definitive reference once you outgrow the basics.
- [bfgc](https://github.com/isaacazuelos/bfgc) — a small mark-sweep collector in C in the "baby's first GC" tradition; good for comparing implementation choices.
- [garbage_collector](https://github.com/inmisin/garbage_collector) — another compact GC implementation to study alongside your own.
- [Crafting Interpreters — Table of Contents](https://craftinginterpreters.com/contents.html) — Chapter 26, "Garbage Collection," integrates mark-sweep into the clox VM: grey stack, string interning, and weak references.

## Stretch ideas

- Add generational collection: a nursery with copying collection for young objects plus your mark-sweep old generation.
- Implement finalizers or weak references and think carefully through their ordering hazards during the sweep.
- Benchmark pause times under allocation-heavy workloads, then add incremental marking to smooth the worst pauses.
