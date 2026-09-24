---
title: "Backup System"
category: "devops-infra"
difficulty: "intermediate"
tags: [backups, storage, recovery]
related: [cron-scheduler, merkle-trees, crash-recovery-aries]
---

# Backup System

Backups are the only feature you can't test in production until you need them — and then they must work perfectly. A backup system snapshots data, deduplicates it so daily backups don't cost 30x storage, encrypts it, and verifies restores. Building a mini-restic teaches you content-defined chunking, the real reason modern backups are fast and cheap, plus the operational discipline (3-2-1, restore drills) that separates backups from wishful thinking.

## Core concepts

- **Snapshots as immutable trees** — each backup is a Merkle tree: files hashed into blobs, directories as lists of (name, hash) pairs, the snapshot as the root hash. Identical files across snapshots share blobs automatically; a snapshot is just a new root pointing at mostly-old data.
- **Content-defined chunking** — instead of fixed 1MB blocks, a rolling hash (Rabin fingerprint) cuts chunk boundaries where the *content* dictates. Inserting one byte shifts only nearby chunks, so deduplication survives edits — this is the core trick behind restic and Borg.
- **Deduplication** — chunks are stored by hash; a chunk already present is never uploaded twice. Across machines and time, this typically cuts storage 5-20x, which is what makes frequent backups affordable.
- **Encryption by default** — AES-256-CTR + Poly1305 (or AES-GCM) with keys derived from a passphrase via Argon2. Encrypting before upload means the storage backend (S3, a friend's server) never sees plaintext — zero-trust backup.
- **Incremental vs differential vs full** — classic schemes trade restore complexity for backup speed; content-defined chunking makes the distinction nearly obsolete since every backup is effectively an incremental that *looks* like a full.
- **Retention policies (GFS)** — grandfather-father-son: keep daily snapshots for a week, weekly for a month, monthly for a year. `forget --prune` applies the policy and garbage-collects unreferenced chunks.
- **Restore verification** — a backup you haven't restored is a hope, not a backup. `check` verifies chunk hashes and index consistency; real confidence comes from automated restore drills into a scratch directory with diffing.

## How it works

A backup run walks the source tree, splitting each file into content-defined chunks via a rolling hash over a sliding window — when the low N bits of the fingerprint are zero, that's a boundary. Each chunk is hashed (SHA-256/BLAKE2), compressed, encrypted, and uploaded only if the backend doesn't already have that hash. File metadata and the chunk list form a blob; directory blobs reference file blobs; the snapshot blob references the root directory — a Merkle tree persisted as content-addressed JSON.

An index maps chunk IDs to their backend locations for fast lookup. `forget` selects snapshots to keep per the retention policy and prunes: it rebuilds the set of chunks referenced by surviving snapshots and deletes the rest (repacking partially-used pack files to reclaim space). `check` reads every referenced chunk, re-verifies hashes, and reports corruption. Restore walks the snapshot tree, fetches chunks, decrypts, and reassembles files — and because snapshots are complete trees, any snapshot restores independently.

## Build milestones

1. Build a snapshot tool: walk a directory, hash files into a Merkle tree stored as JSON, and restore any snapshot by its root hash. Verify with diff.
2. Add content-defined chunking with a rolling hash, content-addressed chunk storage with dedup, and compression.
3. Add encryption (passphrase → Argon2 → AES-GCM), backend abstraction (local disk + S3-compatible), and GFS retention with prune.
4. Implement `check` (full integrity verification), lock-free concurrent backups to the same repo, and automated restore drills that alert on failure.

## Best resources

- [restic documentation](https://restic.readthedocs.io/en/stable/) — the reference user-facing backup tool; commands, retention, and backend model your system mirrors.
- [restic design document](https://restic.readthedocs.io/en/stable/design.html) — the actual architecture: pack files, indexes, encryption, and the repository layout. Read this before writing code.
- [BorgBackup documentation](https://borgbackup.readthedocs.io/en/stable/) — the other great dedup backup tool; its internals on chunking and the files cache complement restic's design.
- [rclone documentation](https://rclone.org/) — "rsync for cloud storage" with 70+ backends; study its backend abstraction if you want your backup tool to support every storage target.

## Stretch ideas

- Add ransomware-resistant append-only mode: the backup credentials can write new snapshots but never delete old ones.
- Implement live database backups: coordinate with the DB (or use filesystem snapshots) for consistent backups of changing data.
- Build a backup health dashboard: last-successful age per host, dedup ratios, storage growth trends, and missed-backup alerts.
