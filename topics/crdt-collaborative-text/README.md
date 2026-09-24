---
title: "CRDT Collaborative Text"
category: "distributed-data"
difficulty: "advanced"
tags: [crdt, collaboration, distributed-systems]
related: [gossip-protocol, distributed-lock, websocket-chat]
---

# CRDT Collaborative Text

Google Docs lets two people type in the same paragraph with no server arbitrating every keystroke. CRDTs (Conflict-free Replicated Data Types) are the math that makes this possible: data structures where any two replicas that have seen the same updates always converge to the same state, with no coordination. Building a collaborative text editor on CRDTs teaches you how to get strong guarantees without consensus.

## Core concepts

- **Strong eventual consistency** — Replicas may diverge temporarily, but once they have exchanged all updates they are guaranteed identical — without any leader, lock, or merge step. Convergence is a property of the data structure, not of a protocol.
- **Commutativity** — The core trick: every update is designed so that applying updates in different orders yields the same result (like addition). If operations commute, replicas never need to agree on an order.
- **Operation-based (CmRDT) vs state-based (CvRDT)** — Op-based CRDTs broadcast each operation (e.g. "insert X at position P") and require reliable, exactly-once delivery; state-based CRDTs broadcast the whole state and merge it with a function that is associative, commutative, and idempotent, tolerating duplicates and loss.
- **Tombstones** — In a text CRDT, deleting a character can't remove it from history, because a concurrent insert elsewhere might reference it. Deleted characters become invisible "tombstones" that must be retained so merges stay correct.
- **Causal order / vector clocks** — Operations carry enough metadata to know what the author had seen when they typed. This lets replicas apply operations only when their dependencies are present, keeping the document structure sane.
- **RGA / Yjs-style list CRDTs** — Replicated Growable Array assigns every character a unique ID and links it to its left neighbor; concurrent inserts at the same spot are ordered deterministically by ID. This is the design behind Yjs, the most-used collaborative editing library.
- **Convergence vs intention preservation** — Convergence (same final text) is guaranteed by the CRDT; preserving what each user *meant* (their insert lands where their cursor was, relative to text they could see) is the harder UX property good editors chase.

## How it works

Every character ever typed gets a globally unique ID (e.g. `clientID:counter`) and is stored as a node linked to the character that was to its left when it was inserted. An insert is just "add node X after node Y"; a delete marks node X as a tombstone. Because nodes are never truly removed and links only reference IDs — never array indices — two users inserting at the "same position" simply create two nodes after the same left neighbor, and every replica orders the tie the same way (e.g. by ID). Merging is then just set union: collect all nodes from both replicas, sort them by the deterministic traversal order, skip tombstones. Any pair of replicas that exchange their node sets converge to identical documents, regardless of network order, duplicates, or partitions.

## Build milestones

1. Build a single-user text buffer where every character is a node `{id, char, leftId, deleted}` and rendering walks the linked structure — no CRDT yet, just the data model.
2. Add a second replica in the same process: apply inserts on replica A, serialize the operations, apply them on replica B, and verify both render the same text.
3. Simulate concurrency: have both replicas insert at the same position without exchanging updates first, then sync, and verify they converge to identical (if interleaved) text on both sides.
4. Add deletes with tombstones and test the nasty cases: delete a character concurrently with an insert after it; delete the same character twice; sync in scrambled order with duplicates.
5. Impressive end state: two real browser windows editing the same document over WebSockets through a dumb relay server that stores nothing — kill and restart the relay mid-session and watch the documents stay consistent.

## Best resources

- [Conflict-free replicated data type — Wikipedia](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type) — The canonical overview: state-based vs op-based, the math properties required, and the standard CRDT catalog.
- [crdt.tech](https://crdt.tech/) — The community hub: papers, talks, and implementations, including the original Shapiro et al. CRDT paper that started it all.
- [Yjs](https://yjs.dev/) — The production CRDT library behind countless collaborative editors; its docs and source are the best practical reference for a list CRDT done right.
- [Automerge](https://automerge.org/) — A JSON-like CRDT with excellent documentation on how op-based CRDTs handle richer data than plain text.

## Stretch ideas

- Add undo/redo that works across replicas — surprisingly hard, because "undo my insert" must not resurrect characters others intentionally deleted.
- Implement garbage collection of tombstones using version vectors, so a long-lived document stops growing forever.
