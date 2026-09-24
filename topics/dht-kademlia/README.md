---
title: "Kademlia DHT"
category: "distributed-data"
difficulty: "advanced"
tags: [dht, p2p, xor-metric]
related: [p2p-file-sharing, gossip-protocol, merkle-trees]
---

# Kademlia DHT

A distributed hash table lets millions of untrusted peers store and find data with no server — it's how BitTorrent finds peers without a tracker. Kademlia is the DHT that won: its elegant XOR distance metric makes routing provably efficient and naturally resilient. Building one teaches you how structure emerges from a clever choice of geometry.

## Core concepts

- **XOR distance metric** — Distance between two 160-bit IDs is their bitwise XOR, interpreted as a number. XOR is symmetric (unlike Chord's circular distance), so every query a node forwards also teaches it about nodes in exactly the region it routes to — routing tables improve as a side effect of use.
- **k-buckets** — Each node keeps, for each prefix-length i, up to k contacts whose IDs share its first i bits but differ at bit i+1. Near buckets are full and fresh; far buckets are sparse — you need fine-grained knowledge of your neighborhood and only coarse knowledge of distant space.
- **Node IDs as keys** — Both nodes and data keys live in the same 160-bit space (usually SHA-1/SHA-256 hashes). A key's "home" is the set of nodes closest to it, so lookup is just routing toward an ID.
- **Iterative lookup** — To find a key, a node asks the α (typically 3) closest nodes it knows, takes the best answers, and repeats with the new closest set until nobody returns anyone closer. Parallel queries mean one slow or dead node never stalls a lookup.
- **k (replication factor)** — Data is stored on the k closest nodes (k=20 in BitTorrent's DHT), so the data survives nodes churning out. The bucket size and replication factor being the same k is no coincidence — buckets already track the k closest nodes you know.
- **Churn resistance** — Nodes constantly join and leave, so Kademlia prefers long-lived contacts in buckets (they're statistically likely to stay) and republishes data periodically. The protocol assumes instability and routes around it.
- **Sybil considerations** — Anyone can mint IDs, so an attacker can cluster fake nodes near a target key. Real deployments add ID constraints or trust mechanisms; the base protocol is correct but not attack-proof.

## How it works

Give your node a random 160-bit ID and a routing table of k-buckets. To join, contact one bootstrap node and look up your own ID — the responses populate your buckets. To store a value, find the k closest nodes to `hash(key)` via iterative lookup and send each a STORE. To retrieve, run the same lookup; the first node that has the value returns it (and you opportunistically cache it at the closest node that didn't have it, speeding future lookups). Bucket maintenance is passive: any message from a node is a chance to refresh its bucket entry, preferring to keep old, long-lived contacts over newcomers. Lookups converge in O(log n) hops because each iteration moves to nodes sharing a longer prefix with the target.

## Build milestones

1. Implement the XOR metric and k-buckets in a single process: insert fake node IDs, verify bucket splitting, and that "k closest to X" queries work.
2. Build iterative lookup between real processes over UDP: node A looks up a key held by node C via intermediate node B, with α=3 parallel queries.
3. Add STORE/FIND_VALUE RPCs and the join procedure (bootstrap → lookup own ID → populate buckets); demonstrate a 10-node network where any node can store and any node can retrieve.
4. Add churn handling: random nodes join/leave, data is republished periodically, and lookups still succeed — measure hop count vs network size to see the logarithmic scaling.
5. Impressive end state: a trackerless mini-torrent — publish "file X is at peer Y" records into your DHT and have a downloader find peers purely through Kademlia lookups, with nodes churning throughout.

## Best resources

- [Kademlia — Wikipedia](https://en.wikipedia.org/wiki/Kademlia) — Solid overview of the XOR metric, k-buckets, and the four RPCs (PING, STORE, FIND_NODE, FIND_VALUE).
- [Kademlia: A Peer-to-Peer Information System Based on the XOR Metric (PDF)](http://www.cs.cornell.edu/people/egs/cs6460-spring10/kademlia.pdf) — The original Maymounkov–Mazières paper; short, readable, and the proofs explain *why* the design works.
- [Distributed hash table — Wikipedia](https://en.wikipedia.org/wiki/Distributed_hash_table) — Places Kademlia among Chord, Pastry, and CAN so you understand what design choices it was competing with.
- [BEP 5: DHT Protocol](http://www.bittorrent.org/beps/bep_0005.html) — How BitTorrent actually wires Kademlia up in the real world (message formats, token security for announces).

## Stretch ideas

- Implement S/Kademlia's constrained ID generation to raise the cost of Sybil attacks near a target key.
- Add iterative-lookup parallelism tuning: measure how α trades latency against bandwidth under churn.
