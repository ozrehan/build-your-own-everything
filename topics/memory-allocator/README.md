---
title: "Build Your Own Memory Allocator"
category: "programming-languages"
difficulty: "intermediate"
tags: [memory-management, systems, low-level]
related: [mark-sweep-garbage-collector, actor-model-concurrency, bytecode-virtual-machine]
---

# Build Your Own Memory Allocator

Every `malloc` call runs a small, clever algorithm: your memory allocator decides where each block lives, splits and merges free space, and does it all fast enough that programs never notice. Writing one — typically by implementing `malloc` and `free` yourself over `sbrk` or `mmap` — teaches you fragmentation, free lists, and the real cost of allocation. Dan Luu's malloc tutorial builds a working allocator in a single sitting.

## Core concepts

- **The heap as a managed resource** — the allocator owns a region of memory (requested from the OS via `sbrk`/`mmap`) and subdivides it; the OS only ever sees large requests.
- **Headers and footers** — each block carries metadata (size, free/used flag); boundary tags let `free` coalesce with neighboring blocks in O(1).
- **Free lists** — freed blocks link into a list; first-fit, best-fit, and next-fit are the classic placement policies with different fragmentation profiles.
- **Splitting and coalescing** — carve exact-size pieces from bigger blocks on allocate; merge adjacent free blocks on free, or fragmentation eventually wins.
- **Alignment** — every returned pointer must satisfy the platform's alignment (16 bytes on x86-64); headers are sized and padded accordingly.
- **Size classes** — production allocators segregate blocks by size class so common allocations are O(1) and fragmentation stays bounded.

## How it works

The allocator requests memory from the OS in large chunks and carves them into blocks, each prefixed with a header recording its size and status. `malloc(size)` rounds the request up for alignment and header space, scans the free list for the first (or best) fitting block, splits off any large remainder back onto the free list, and returns a pointer past the header. `free(ptr)` reads the header, marks the block free, and coalesces it with adjacent free neighbors using boundary tags. Larger requests bypass the heap and go straight to `mmap`; `calloc` and `realloc` are thin layers on top of these two primitives.

## Build milestones

1. Write a bump allocator: `my_malloc` hands out memory from a growing arena with no `free`; measure how far a test program gets.
2. Add headers and a first-fit free list; implement `my_free` with coalescing; run an allocate/free stress test and check for leaks.
3. Handle alignment, zero-size requests, and large allocations via `mmap`; add `calloc` and `realloc` on top.
4. Add size classes (e.g. eight buckets) with per-class free lists; benchmark against the system malloc on a mixed workload.
5. Add thread safety — a global lock first, then per-thread caches — and measure contention.

## Best resources

- [Malloc tutorial](http://danluu.com/malloc-tutorial/) — Dan Luu's walkthrough: build a working malloc/free over `sbrk` in one sitting.
- [malloc-tutorial repo](https://github.com/danluu/malloc-tutorial/blob/master/Makefile) — the tutorial's companion code and build setup.
- [memory-allocator](https://github.com/shega1992/memory-allocator) — a from-scratch allocator implementation to compare your design against.
- [Malloc — UIUC coursebook [pdf]](https://github.com/cs341-illinois/coursebook/raw/refs/heads/pdf_deploy/malloc.pdf) — the University of Illinois systems course chapter on dynamic memory allocation.
- [Malloc internals walkthrough [video]](https://www.youtube.com/watch?v=NGjRX7VEGGU) — a video walkthrough of allocator internals and design trade-offs.

## Stretch ideas

- Implement a debugging mode: red zones, fill patterns on alloc/free, and leak reports — a valgrind-lite for your heap.
- Write a fragmentation benchmark and compare first-fit vs. best-fit vs. size classes quantitatively.
- Replace the global lock with lock-free per-thread caches and measure scaling up to eight threads.
