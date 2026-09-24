---
title: "Mini MapReduce"
category: "distributed-data"
difficulty: "beginner"
tags: [mapreduce, big-data, parallel-computing]
related: [full-text-search-index, stream-processor, etl-pipeline]
---

# Mini MapReduce

MapReduce is the programming model that let Google process web-scale data on thousands of unreliable commodity machines. Building a small version yourself teaches you why the model is just map, shuffle, and reduce — and why that simplicity made it the foundation of the big-data era.

## Core concepts

- **Map** — A user function that takes one input record and emits zero or more key/value pairs (e.g. `(word, 1)` for each word in a line). Mappers run independently with no communication between them, which is what makes the computation trivially parallel.
- **Shuffle** — The framework phase that groups all intermediate pairs by key and delivers each key's values to a single reducer. This all-to-all data movement is the expensive part of every MapReduce job and the reason partitioning matters.
- **Reduce** — A user function that receives a key plus the list of all its values and emits final output (e.g. summing counts). Because all values for a key arrive together, reducers compute exact aggregates without talking to each other.
- **Input splits** — The input is chopped into chunks, each processed by one mapper. Splits are usually aligned with the underlying storage blocks so computation happens near the data, avoiding network transfer — the "data locality" idea.
- **Combiner** — An optional local mini-reducer that runs on the mapper's own output before the shuffle (e.g. pre-summing word counts per machine). It cuts shuffle traffic enormously and is safe whenever the reduce operation is associative.
- **Partitioner** — Decides which reducer receives each key (typically `hash(key) mod R`). A bad partitioner sends everything to one reducer and your "parallel" job becomes serial.
- **Fault tolerance** — Workers are stateless: if a mapper or reducer crashes, the master simply re-runs its task on another machine. Intermediate data is written to local disk and can be regenerated, so no checkpoints are needed.

## How it works

You write two functions and the framework does everything else. First, the input file is split into M pieces and each piece is handed to a mapper, which applies your map function and writes intermediate key/value pairs to its local disk, partitioned into R regions (one per reducer). Second, the shuffle: each reducer reads its partition from every mapper's disk, sorts the pairs by key so all values for a key are adjacent, and then calls your reduce function once per key, appending results to the output files. A master process tracks which tasks are done, reassigns failed ones, and handles stragglers by launching backup copies of slow tasks. The key insight: you never think about machines, networking, or failures — the model restricts what you can express so the runtime can parallelize and recover automatically.

## Build milestones

1. Build a single-process word counter: read a text file, map each line to `(word, 1)` pairs, group by key in a dictionary, and reduce by summing.
2. Add a real shuffle: write mapper output to partitioned files on disk, then have reducers read, sort, and aggregate — the same program, but with the disk-based data flow MapReduce actually uses.
3. Add multiple workers: spawn mapper/reducer processes that communicate over sockets or HTTP, with a tiny coordinator that assigns splits and tracks completion.
4. Add fault tolerance: kill a worker mid-job and have the coordinator detect the failure (missed heartbeat) and re-run its task elsewhere; verify the final counts are still exact.
5. Impressive end state: build an inverted index over a folder of documents (word → list of documents) using your mini-MapReduce, and benchmark it against a single-threaded version to see the speedup.

## Best resources

- [MapReduce — Wikipedia](https://en.wikipedia.org/wiki/MapReduce) — Clear overview of the model, the execution phases, and why the programming model restricts you on purpose.
- [MapReduce Tutorial — Apache Hadoop](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html) — The classic word-count walkthrough on real Hadoop; shows how maps, reduces, partitioners, and combiners fit together in practice.
- [Apache Hadoop](https://hadoop.apache.org/) — Home of the most famous MapReduce implementation; the docs explain HDFS, YARN, and the job lifecycle your mini version is imitating.
- [Apache Spark](https://spark.apache.org/) — Spark's RDD model is the spiritual successor to MapReduce; reading its docs shows what MapReduce got right and what it left on the table (in-memory iteration).

## Stretch ideas

- Implement speculative execution: when one mapper lags, launch a duplicate and take whichever finishes first, like the original Google paper describes.
- Add a combiner pass and measure how much shuffle traffic it saves on skewed data (e.g. a document where one word dominates).
