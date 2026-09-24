# Example: Distributed Systems — Raft Visualizer

**[▶ Try it live](https://byoe-raft.netlify.app)**

The consensus algorithm inside etcd, Consul, and Kubernetes — animated.
Watch **leader election** and **log replication**, then **kill the leader mid-write**
and see the cluster recover without losing committed data.

Example project for the [distributed-systems learning path](../../topics/raft-consensus/).

## What it teaches

- **Leader election**: randomized timeouts → candidate → majority vote (3/5).
- **Why majorities are safe**: two leaders can't both win a majority in one term.
- **Log replication**: leader appends → followers ack → commit on majority.
- **Failure recovery**: missed heartbeats trigger a new election automatically.

## Try

1. Write `x=1`, then **kill the leader** before it commits — the write is lost (correct!).
2. Write `x=2`, wait for COMMITTED, then kill the leader — the value survives.
3. Exercise: add **persistent logs** so a revived node rejoins with its history.
