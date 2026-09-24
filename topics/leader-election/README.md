---
title: "Leader Election"
category: "distributed-data"
difficulty: "advanced"
tags: [consensus, coordination, fault-tolerance]
related: [raft-consensus, distributed-lock, gossip-protocol]
---

# Leader Election

Every distributed system has jobs only one node may do — accept writes, run the scheduler, hold the primary lease. Leader election is how a cluster agrees on who that node is, and re-agrees when it dies. Building it teaches you the core dance of distributed consensus: terms, votes, quorums, and why "just pick the lowest ID" falls apart.

## Core concepts

- **Term / epoch** — A monotonically increasing number identifying each election round. Terms let nodes ignore stale messages from old elections — a candidate from term 5 cannot disrupt a leader already reigning in term 7.
- **Quorum / majority** — A candidate becomes leader only with votes from a majority of nodes. Majorities of any two elections overlap in at least one node, which is what prevents two leaders in the same term.
- **Randomized election timeouts** — If all followers notice a dead leader simultaneously and all vote for themselves, nobody wins. Randomizing the timeout before starting an election makes split votes rare and elections converge quickly.
- **Split vote** — When two candidates each get a minority of votes, no leader emerges and a new term begins. Real algorithms either randomize (Raft) or rank candidates (Paxos-style) to escape this.
- **Heartbeat / lease** — The leader continuously proves it is alive; followers start an election only after missing several heartbeats. The timeout must be comfortably larger than network jitter to avoid flapping.
- **Safety vs liveness** — Safety ("never two leaders in one term") must hold always; liveness ("eventually someone leads") only needs to hold when the network behaves. Good algorithms never trade safety for speed.
- **Log replication tie-in** — In Raft, election isn't standalone: a candidate must have a log at least as up-to-date as the voters', which guarantees the new leader has every committed entry.

## How it works

Every node starts as a follower with a randomized election timer. If the timer fires without hearing from a leader, the node increments its term, votes for itself, and sends RequestVote RPCs to everyone. A node grants its vote if the candidate's term is newer and its log is at least as complete, and only one vote per term. A candidate that collects a majority becomes leader and immediately starts sending heartbeats (empty AppendEntries) to assert authority and suppress new elections. If a follower hears from a leader with a higher term, it steps down. If the leader dies, heartbeats stop, timers fire, and the cycle repeats — typically electing a replacement within a few hundred milliseconds.

## Build milestones

1. Build the skeleton: N processes over TCP/HTTP with the three states (follower, candidate, leader) and a heartbeat loop; watch one node become leader and the rest stay followers.
2. Add randomized election timeouts and demonstrate clean re-election: kill the leader process and time how long the cluster takes to elect a successor.
3. Add terms: make candidates increment a term on each election and have nodes reject/ignore messages from older terms; test with a partitioned old leader rejoining and trying to assert authority.
4. Add the log check: give each node a fake log, require candidates to be at least as up-to-date as voters, and show a stale node failing to win an election.
5. Impressive end state: run a 5-node cluster, partition it 3-vs-2 with firewall rules, and prove the majority side keeps a single leader while the minority side cannot elect one — then heal the partition and watch it reconverge with no split brain.

## Best resources

- [Raft](https://raft.github.io/) — The project's home page: the original paper, the interactive visualization, and links to every serious implementation.
- [Raft (algorithm) — Wikipedia](https://en.wikipedia.org/wiki/Raft_(algorithm)) — A compact, accurate walkthrough of leader election, log replication, and the safety argument.
- [The Raft dissertation (PDF)](https://raft.github.io/raft.pdf) — Diego Ongaro's thesis: the full story including cluster membership changes and the proof sketches, free to read.
- [Apache ZooKeeper](https://zookeeper.apache.org/) — The production coordination service whose Zab protocol solves the same problem; its recipes show what leader election unlocks (locks, queues, barriers).

## Stretch ideas

- Implement Raft's joint-consensus membership change so you can add/remove nodes without downtime — the part most toy implementations skip.
- Add a replicated state machine on top: the leader replicates a log of commands and every node applies them, turning your election into a real consensus system.
