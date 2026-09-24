---
title: "Virtual Memory and Paging"
category: "operating-systems"
difficulty: "advanced"
tags: [memory, paging, mmu]
related: [malloc-implementation, page-cache, mark-sweep-garbage-collector]
---

# Virtual Memory and Paging

Virtual memory gives every process its own private, contiguous address space while physical RAM is shared underneath — it is the foundation of memory protection, swapping, and memory-mapped files. Building a paging system yourself (page tables, a TLB, a fault handler) teaches you how the MMU translates addresses and why a segfault is really a failed page-table lookup.

## Core concepts

- **Virtual vs physical addresses** — Programs see virtual addresses; the MMU translates them to physical RAM locations via page tables. Two processes can use the same virtual address and land on different physical pages.
- **Pages and page tables** — Memory is split into fixed-size pages (usually 4KB). A multi-level page table (4 levels on x86-64) maps virtual page numbers to physical frame numbers plus permission bits.
- **The MMU and TLB** — The memory management unit walks page tables in hardware on every access; the translation lookaside buffer caches recent translations. A TLB miss costs a multi-level walk, which is why huge pages exist.
- **Page faults** — When translation fails (unmapped page, wrong permissions, swapped-out page), the CPU raises a page fault exception with the faulting address in CR2 (x86). The OS handler decides: grow the stack, load from disk, copy-on-write, or kill the process.
- **Copy-on-write** — `fork()` marks parent pages read-only and shared; the first write by either process triggers a fault that copies the page. This makes process creation nearly free.
- **Demand paging and swapping** — Pages are loaded from disk only on first access, and cold pages are evicted to swap when RAM fills. The page-replacement algorithm (LRU approximations like the clock algorithm) decides victims.
- **ASLR and the memory map** — Stack, heap, mmap regions, and libraries sit at randomized virtual addresses. Understanding the layout explains where your variables actually live.

## How it works

The OS builds a page-table tree for each process, where each entry maps one virtual page to a physical frame with present/read-write/user-executable bits, and points the CPU's CR3 register at the root. On every memory access the MMU walks the tables (or hits the TLB) to find the frame. When a walk fails, the CPU jumps to the page-fault handler, which reads the faulting address and error code: if the address belongs to a lazily-allocated region it allocates a frame and maps it; if the page was swapped out it reads it back from disk; if it's a copy-on-write page it duplicates the frame; otherwise the access is illegal and the process is killed with SIGSEGV. Changing CR3 on a context switch swaps the entire address space in one instruction.

## Build milestones

1. In a hobby kernel or emulator, build a 2-level page-table walker in software: given a virtual address, walk your tables and return the physical address — test with a hand-built table.
2. Implement 4-level x86-64 paging in a small kernel: identity-map the first megabytes, enable paging (set CR3, flip the PG bit), and keep running.
3. Write a page-fault handler that prints the faulting address from CR2 and the error code, distinguishing not-present vs protection-violation faults.
4. Add demand paging: lazily allocate physical frames on first touch of heap pages, with a bitmap frame allocator underneath.
5. Implement `fork()` with copy-on-write: mark pages read-only and shared, handle the write fault by copying the frame, and verify with a counter test.
6. Add swapping: evict cold pages to a disk-backed swap area using a clock-algorithm victim selector, and fault them back in on access.

## Best resources

- [OSTEP — Address Spaces and Paging](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf) — the clearest free explanation of paging mechanics and page-table structures.
- [OSTEP — Translation / TLBs](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-tlb.pdf) — how the TLB caches translations and why it matters for performance.
- [OSTEP — Beyond Physical Memory: Mechanisms](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys.pdf) — swapping, page faults, and replacement policies.
- [OSDev Wiki — Paging](https://wiki.osdev.org/Paging) — practical hobby-OS guide to setting up x86 paging with code sketches.
- [OSDev Wiki — Setting Up Long Mode](https://wiki.osdev.org/Setting_Up_Long_Mode) — building 4-level page tables to enter x86-64 long mode.
- [Intel 64 and IA-32 SDM, Volume 3A, Chapter 4](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) — the authoritative paging chapter.
- [What every programmer should know about memory (Ulrich Drepper)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf) — the classic deep dive on caches, TLBs, and virtual memory performance.

## Stretch ideas

- Implement huge pages (2MB/1GB) and benchmark TLB-miss reduction on a pointer-chasing workload.
- Add memory-mapped files: map a file's pages into the address space and let page faults drive the I/O.
