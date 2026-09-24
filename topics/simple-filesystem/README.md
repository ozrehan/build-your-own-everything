---
title: "Simple Filesystem"
category: "operating-systems"
difficulty: "intermediate"
tags: [filesystems, storage, disk]
related: [write-ahead-log, embedded-database, page-cache]
---

# Simple Filesystem

A filesystem turns a dumb array of disk blocks into named files and directories with permissions and persistence. Building one yourself — even on a flat file acting as a virtual disk — teaches you how inodes, allocation bitmaps, and directory entries work, and why crash consistency is the hardest part.

## Core concepts

- **Blocks and the superblock** — The disk is divided into fixed-size blocks; the superblock (usually block 0) describes the filesystem: block size, total blocks, where the inode table and bitmaps live.
- **Inodes** — A file's metadata (size, permissions, timestamps, pointers to data blocks) lives in an inode, separate from its name. Filenames live in directories; inodes are the files.
- **Direct vs indirect blocks** — An inode holds a few direct block pointers plus single/double/triple indirect pointers (pointers to blocks full of pointers), so small files are fast and large files are still possible.
- **Allocation bitmaps** — Free/used tracking for data blocks and inodes, typically one bit per block. Allocation is "find a free bit, flip it" — simple, but the bitmap itself must stay consistent.
- **Directories as files** — A directory is just a file whose data is a list of (inode number, name) entries. Creating a file means appending an entry and allocating an inode.
- **Journaling / crash consistency** — If the machine dies mid-write, the filesystem can be corrupt. Journaling (write-ahead log of metadata changes) lets it replay to a consistent state on mount; fsck-style scanning is the offline alternative.
- **The VFS layer** — Real kernels abstract filesystems behind a Virtual Filesystem interface so ext4, FAT, and your toy FS all answer the same `open/read/write` calls.

## How it works

You format a disk image by writing a superblock, zeroed inode and block bitmaps, an inode table, and a root directory. Creating a file allocates an inode (flip a bit in the inode bitmap), writes its metadata, and adds a directory entry mapping the name to that inode number. Writing data allocates data blocks (flip bits in the block bitmap), stores block numbers in the inode's direct/indirect pointers, and updates the size. Reading reverses the walk: name → directory entry → inode → block pointers → data. For crash safety, metadata updates go to a journal first: the change is written to the log and marked committed before the in-place structures are touched, so a crash can only lose the tail of the log, which is replayed or discarded on mount.

## Build milestones

1. Create a 10MB disk image file and a `mkfs` tool that writes a superblock, bitmaps, inode table, and empty root directory; add a `dump` tool that prints the superblock.
2. Implement `create`/`ls`: allocate inodes, append directory entries, and list the root directory by parsing it back.
3. Implement `write`/`read`/`cat` using direct block pointers only (files up to ~12 blocks); verify round-trip with checksums.
4. Add single and double indirect blocks so files can grow to megabytes; test with a 5MB file.
5. Implement `unlink` and free-space reuse: clear bitmap bits, and prove a deleted file's blocks get reallocated to a new file.
6. Add a simple journal: log metadata updates (inode writes, bitmap changes, directory appends) before applying them, replay on mount, and demonstrate recovery by crashing mid-write (kill -9 the writer).

## Best resources

- [OSTEP — File System Implementation](https://pages.cs.wisc.edu/~remzi/OSTEP/file-implementation.pdf) — inodes, allocation, and directory structures explained beautifully.
- [OSTEP — Crash Consistency: FSCK and Journaling](https://pages.cs.wisc.edu/~remzi/OSTEP/file-journaling.pdf) — why crashes corrupt filesystems and how journaling fixes it.
- [OSDev Wiki — File Systems](https://wiki.osdev.org/File_Systems) — overview of filesystem concepts with hobby-OS implementation pointers.
- [xv6 filesystem code](https://github.com/mit-pdos/xv6-public) — a complete, readable Unix-like filesystem (inode, bmap, logging) in a few hundred lines of C.
- [xv6 book — File system chapter](https://pdos.csail.mit.edu/6.828/2012/xv6/book-rev7.pdf) — the companion text explaining xv6's journaling and inode design.
- [The FAT specification (Microsoft)](https://download.microsoft.com/download/1/6/1/161ba512-40e2-4cc9-843a-923143f3456c/fatgen103.doc) — the official FAT spec; a great first real-world FS to implement against.

## Stretch ideas

- Make it mountable in Linux via FUSE so your filesystem works with real `ls`, `cp`, and `vim`.
- Add extents (contiguous block ranges) instead of per-block pointers and benchmark large-file throughput.
