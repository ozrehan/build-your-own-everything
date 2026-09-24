---
title: "malloc Implementation"
category: "operating-systems"
difficulty: "intermediate"
tags: [memory, allocation, heap]
related: [memory-allocator, virtual-memory-paging, mark-sweep-garbage-collector]
---

# malloc Implementation

`malloc` turns a raw stretch of memory from the OS into right-sized, reusable blocks for your program — and `free` must recycle them without corruption. Writing your own allocator teaches you free lists, fragmentation, alignment, and why real allocators (dlmalloc, jemalloc, tcmalloc) look the way they do.

## Core concepts

- **sbrk/mmap as the raw source** — The allocator gets memory from the OS via `sbrk()` (grow the heap) or anonymous `mmap()`. Everything above that is your allocator's own bookkeeping.
- **Block headers and metadata** — Each allocated chunk carries a hidden header (size, free/used flag) just before the pointer you return. `free()` finds the header by subtracting — which is why freeing a bad pointer corrupts everything.
- **Free lists** — Freed blocks are linked into a list for reuse. An implicit list walks headers linearly; an explicit list stores next/prev pointers inside the free blocks themselves.
- **Fit strategies** — First-fit (take the first big-enough block), best-fit (smallest sufficient block), next-fit. Each trades search time against fragmentation; none dominates everywhere.
- **Splitting and coalescing** — Split a large free block when serving a small request; merge adjacent free blocks on `free()` (using boundary tags/footers) to fight external fragmentation.
- **Size classes and bins** — Production allocators round requests into size classes and keep per-class free lists, making common sizes O(1). dlmalloc's bins and tcmalloc's thread caches are refinements of this idea.
- **Alignment** — Returned pointers must satisfy the platform's alignment (16 bytes on x86-64) or SIMD and struct access break. Headers are sized and padded to preserve it.

## How it works

Your `malloc(size)` rounds the request up (header + alignment), searches the free list for a fitting block, splits off any large remainder back into the list, marks the block used, and returns a pointer past the header. If nothing fits, it extends the heap with `sbrk()` (or `mmap()` for huge requests) and carves from the fresh memory. `free(ptr)` reads the header, marks the block free, and coalesces with neighboring free blocks by checking boundary tags — footers at each block's end that let you find the previous block's header in O(1). Fragmentation is the eternal enemy: internal (wasted padding inside blocks) versus external (free memory chopped into unusable slivers), measured by running allocation traces and comparing peak heap to live bytes.

## Build milestones

1. Write a bump allocator: `my_malloc` hands out memory from a static 1MB arena, `my_free` is a no-op — use it to feel why reuse matters.
2. Add a real free list with first-fit search, block splitting, and `sbrk()`-backed heap growth; pass a smoke test of interleaved malloc/free.
3. Implement coalescing with boundary tags (header + footer), then demonstrate the before/after with a fragmentation-inducing workload.
4. Add size-segregated bins (e.g. 8 size classes up to 512 bytes + a general list) and measure the speedup on a small-object benchmark.
5. Route large requests (>128KB) to anonymous `mmap()` and release them with `munmap()` on free, like real allocators do.
6. Write a drop-in `malloc.so` via `LD_PRELOAD` overriding glibc's malloc, run a real program under it, and compare peak RSS against the system allocator.

## Best resources

- [Doug Lea's malloc documentation](https://www.cs.tufts.edu/~nr/cs257/archive/doug-lea/malloc.html) — the design notes behind dlmalloc, the ancestor of glibc's allocator; essential reading.
- [glibc malloc internals wiki](https://sourceware.org/glibc/wiki/MallocInternals) — how the production allocator organizes chunks, bins, and arenas.
- [Memory Allocator 101 — write a simple memory allocator (Arjun Sreedharan)](https://arjunsreedharan.org/post/148675821737/memory-allocators-101-write-a-simple-memory) — a short, correct first-fit implementation tutorial.
- [jemalloc paper/design](https://jemalloc.net/) — the modern production allocator's design docs; read after you have your own working.
- [tcmalloc documentation](https://github.com/google/tcmalloc/blob/HEAD/docs/design.md) — Google's thread-caching allocator design, the contrasting approach to jemalloc.

## Stretch ideas

- Add per-thread caches to eliminate lock contention and benchmark a multithreaded workload.
- Implement a debugging mode with red zones, fill patterns, and double-free detection, then run it against a buggy program.
