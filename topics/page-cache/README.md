---
title: "Page Cache"
category: "operating-systems"
difficulty: "intermediate"
tags: [caching, memory, io]
related: [virtual-memory-paging, simple-filesystem, redis-like-cache]
---

# Page Cache

The page cache is the OS's transparent disk cache: file data lives in RAM in page-sized chunks, so repeated reads never touch the disk and writes return instantly. Building a page-cache model yourself teaches you write-back vs write-through, eviction, readahead, and why "free RAM" on Linux is mostly cache.

## Core concepts

- **Pages as the cache unit** — The cache stores file contents in page-sized (4KB) frames indexed by (inode, offset). This unifies beautifully with virtual memory: an mmap'd file and the page cache are the same pages.
- **Write-back vs write-through** — Write-back: writes go to cache and return immediately; dirty pages flush to disk later (fast, risks data loss). Write-through: every write hits disk before returning (safe, slow). Linux is write-back by default.
- **Dirty pages and writeback** — Modified cached pages are marked dirty; kernel threads (writeback) flush them based on age (`dirty_expire_centisecs`) and memory pressure. `fsync()` forces one file's dirty pages out now.
- **Eviction under pressure** — When RAM fills, the kernel reclaims clean pages first (just drop them) and writes back dirty ones. Linux uses an LRU approximation with active/inactive lists, split per memory zone.
- **Readahead** — The kernel detects sequential reads and prefetches upcoming pages, turning many small reads into fewer large disk I/Os. This is why `cat` of a big file is fast.
- **Drop caches and observability** — `/proc/meminfo`'s `Cached`/`Dirty`/`Writeback` lines show the cache live; `echo 3 > /proc/sys/vm/drop_caches` clears it for benchmarking cold-cache behavior.
- **Unified buffer cache** — Modern Unix merged the old block buffer cache into the page cache: there's one cache for file data, and even raw block devices are accessed through it.

## How it works

Every file read first looks up (inode, page-offset) in the page cache's radix tree. On a hit, data is copied from the cached page — no disk I/O at all. On a miss, the filesystem allocates a page, submits a disk read, and inserts the page on completion; readahead may fetch neighbors speculatively. Writes copy into cached pages and mark them dirty, returning immediately — the application perceives disk speed as memory speed. Independently, writeback threads scan for dirty pages older than the expiry threshold or when dirty memory exceeds `dirty_ratio`, and submit them to the block layer. When the allocator needs RAM, the reclaim path walks the inactive LRU list: clean file pages are freed instantly, dirty ones are written back first. `mmap()` maps these same pages directly into the process address space, so a write through the mapping dirties the identical page a `read()` would see.

## Build milestones

1. Build a userspace page-cache simulator: fixed number of 4KB frames, (file, offset) → frame index, LRU eviction; replay a trace and report hit rate.
2. Add write-back semantics: dirty bits, a background flusher thread with an age threshold, and crash simulation showing unwritten dirty data loss.
3. Implement readahead: detect sequential access patterns and prefetch; measure the hit-rate change on sequential vs random traces.
4. Model Linux's two-list (active/inactive) LRU approximation and compare its hit rate against true LRU on the same traces.
5. Write a real measurement tool: use `mincore()` to report which pages of a file are cached, and correlate with `/proc/meminfo` Dirty/Writeback counters during a copy.
6. Demonstrate mmap-cache unity: mmap a file, modify it through the mapping, and show `read()` sees the change without any write syscall — same page, two views.

## Best resources

- [Linux kernel: page cache documentation](https://www.kernel.org/doc/html/latest/admin-guide/mm/concepts.html) — the official overview of page cache, reclaim, and writeback concepts.
- [OSTEP — Locality and the Page Cache](https://pages.cs.wisc.edu/~remzi/OSTEP/file-intro.pdf) — how caching fits into the filesystem stack.
- [Writeback tuning documentation](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/vm.html) — every `dirty_*` knob explained; the practical control surface.
- [mincore(2) man page](https://man7.org/linux/man-pages/man2/mincore.2.html) — query which pages of a mapping are resident; your observability tool.
- [What every programmer should know about memory (Drepper)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf) — caches at every level, including the page cache's role.
- [Linux Memory Management wiki](https://www.kernel.org/doc/html/latest/mm/index.html) — the kernel's memory management docs hub.

## Stretch ideas

- Implement `fadvise`-style hints (sequential, random, willneed, dontneed) in your simulator and show workloads that benefit.
- Build a FUSE filesystem that exposes cache statistics per file as virtual files.
