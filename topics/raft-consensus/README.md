---
title: "Raft Consensus"
category: "databases"
difficulty: "advanced"
tags: [consensus, distributed-systems, replication]
related: [leader-election, distributed-lock, gossip-protocol, read-replicas-replication]
---

# Raft Consensus

Raft is the algorithm that lets a cluster of machines agree on a single sequence of operations even when some machines fail — it's what makes etcd, Consul, and CockroachDB possible. Building it teaches the core distributed-systems skill: reasoning about majorities, terms, and exactly what "committed" means.

## Core concepts

- **Leader, followers, candidates** — At any time each node is in one of three states. The leader takes all client writes; followers replicate; candidates campaign during elections. All complexity lives in the transitions.
- **Terms** — Time is divided into numbered terms; each term has at most one leader. Terms let nodes detect stale leaders ("your term 3 < my term 5, step down") and are the basis of all safety arguments.
- **Leader election** — Followers start elections after randomized timeouts without hearing from a leader. A candidate wins with a majority of votes; randomization prevents split votes from recurring forever.
- **Log replication** — The leader appends client commands to its log and replicates entries via AppendEntries RPCs; followers apply entries to their state machines in order. The log is the single source of truth.
- **Commit index and majorities** — An entry is *committed* once a majority has stored it. Committed means durable: any future leader must contain it (this is the property the election rules enforce).
- **Election safety via up-to-date logs** — A candidate only wins votes from nodes whose logs are at most as up-to-date as its own, guaranteeing the new leader has every committed entry. This one rule is why Raft works.
- **Membership changes** — Adding/removing nodes uses joint consensus (old + new majorities overlap) so two leaders can never be elected during the transition.

## How it works

Nodes start as followers. If a follower hears nothing for its randomized election timeout, it becomes a candidate, increments its term, votes for itself, and requests votes; it becomes leader on receiving a majority, but only from nodes whose logs it is at least as up-to-date as. The leader then serves clients: each write is appended to the leader's log and sent to followers in AppendEntries RPCs; once a majority acknowledges an entry, the leader advances its commit index, applies the entry to its state machine, and replies to the client. Followers learn the commit index from subsequent RPCs and apply entries in order. If a follower's log diverges (missing or extra entries from an old leader), the leader decrements its next-index for that follower and retries until logs match — the consistency check that heals partitions. Heartbeats double as the replication RPC, so steady state is just periodic AppendEntries.

## Build milestones

1. Implement the basics: three states, randomized election timeouts, RequestVote RPCs over TCP/HTTP, and stable leader election in a 3-node cluster. Test by killing the leader and watching re-election.
2. Add log replication: leader appends client writes, replicates via AppendEntries, tracks match indexes, and advances the commit index on majority ack. Build a replicated key/value state machine on top.
3. Implement the log consistency check (prevLogIndex/prevLogTerm) and conflict resolution by decrementing nextIndex; test with partitions that create divergent logs.
4. Add persistence: write current term, voted-for, and the log to disk before replying to RPCs, so a restarted node rejoins correctly; test crash-recovery of followers and leaders.
5. Implement snapshotting (compact the log, install snapshots on lagging followers) and single-node membership change via joint consensus; run a Jepsen-style partition test suite.

## Best resources

- [Raft official site](https://raft.github.io/) — the paper, the famous interactive visualization, and talks; start with the visualization.
- [In Search of an Understandable Consensus Algorithm (Ongaro & Ousterhout)](https://raft.github.io/raft.pdf) — the original paper; unusually readable, and the safety arguments are worth working through.
- [Raft (algorithm) (Wikipedia)](https://en.wikipedia.org/wiki/Raft_(algorithm)) — a compact reference for the RPCs, state transitions, and safety properties.
- [etcd](https://etcd.io/) — the production Raft-based key/value store (Kubernetes' brain); its docs and code show Raft operating real systems.
- [Paxos (computer science) (Wikipedia)](https://en.wikipedia.org/wiki/Paxos_(computer_science)) — Raft's predecessor; understanding what Raft simplified teaches why the design choices matter.
- [Designing Data-Intensive Applications — Martin Kleppmann](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) — chapter 9 puts consensus in the broader replication landscape.

## Stretch ideas

- Implement the pre-vote extension and demonstrate it preventing disruptive re-elections when a partitioned node rejoins.
- Add linearizable reads (ReadIndex / lease-based) so reads don't have to go through the log.
- Build a Raft-backed distributed lock service (see distributed-lock) with fencing tokens.
