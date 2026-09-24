---
title: "Dataset Pipeline"
category: "ai-ml"
difficulty: "intermediate"
tags: [data-engineering, datasets, etl]
related: [tokenizer-bpe, cnn-image-classifier, rnn-text-generator]
---

# Dataset Pipeline

A dataset pipeline turns raw files into the shuffled, batched, prefetched tensors training loops consume — and it's where most real ML projects actually fail. Building one yourself (streaming, sharding, deterministic shuffling, augmentation) teaches the unglamorous truth: data plumbing determines training speed and reproducibility more than model code does.

## Core concepts

- **ETL for ML** — Extract (read raw files), Transform (clean, tokenize, normalize, augment), Load (serve batches to the trainer). Unlike analytics ETL, the transform stage runs every epoch and must be fast enough to keep the GPU fed.
- **Streaming vs materialized** — Materializing processed data to disk (TFRecord, Parquet, Arrow) costs storage but makes training I/O-bound-proof; streaming processes on the fly, saving disk at the cost of repeated CPU work. Large-scale training almost always materializes.
- **Shuffling done right** — True random shuffling of a 1TB dataset is impossible; pipelines shuffle within a buffer plus shard the data across workers. Understanding the shuffle buffer size vs randomness tradeoff prevents subtle training biases.
- **Sharding for distributed training** — Each worker reads a disjoint shard so no example is seen twice per epoch. Deterministic sharding + per-worker seeds keeps multi-GPU runs reproducible.
- **Prefetching and parallelism** — Overlap data loading with training: while the GPU trains on batch N, CPUs prepare batch N+1. Without prefetching, even a fast model starves waiting on I/O — the most common silent performance bug.
- **Versioning and lineage** — Datasets change; models trained on different data aren't comparable. Hashing inputs, pinning pipeline code versions, and logging the exact transform config make experiments reproducible.

## How it works

Raw files are scanned into a manifest (paths + labels + hashes), then a reader stage decodes them in parallel workers. A transform chain applies deterministic preprocessing (resize, tokenize) and stochastic augmentation (crop, flip, dropout noise) with seeded RNGs. Examples flow into a shuffle buffer, get batched (dropping or padding the ragged remainder), and are prefetched into a queue the training loop drains. Checkpoints save the RNG state and read position so interrupted runs resume mid-epoch. The whole thing is a producer-consumer system; your job is keeping the consumer (GPU) never waiting.

## Build milestones

1. Build a minimal pipeline: walk a directory of images, decode, resize, batch with NumPy; train a tiny model on it.
2. Add parallel workers, a shuffle buffer, and prefetching; benchmark images/sec with each optimization toggled to see what actually matters.
3. Implement deterministic mode: seeded shuffling and augmentation, resumable iteration, and a data hash logged per run.
4. Add a materialization step: preprocess once into an efficient on-disk format (Arrow/Parquet), then train from that; compare epoch times.
5. Shard the dataset across simulated workers with disjoint, deterministic splits; verify no overlap and identical results across runs.

## Best resources

- [Hugging Face Datasets](https://github.com/huggingface/datasets) — The standard library for loading, processing, and streaming ML datasets; study its Arrow-backed design.
- [Hugging Face Datasets Docs](https://huggingface.co/docs/datasets) — Streaming, caching, and distributed processing patterns from the reference implementation.
- [tf.data: Build TensorFlow input pipelines](https://www.tensorflow.org/guide/data) — The canonical guide to performant pipelines: parallel map, prefetch, interleave.
- [tf.data performance guide](https://www.tensorflow.org/guide/data_performance) — The optimization checklist: caching, vectorized mapping, and autotuning, with benchmarks.
- [PyTorch Data Loading (DataLoader)](https://pytorch.org/docs/stable/data.html) — Workers, samplers, and custom datasets in the PyTorch ecosystem.
- [WebDataset](https://github.com/webdataset/webdataset) — Tar-shard streaming format for huge datasets; the pragmatic alternative to heavyweight infrastructure.

## Stretch ideas

- Build a data-quality monitor: per-batch statistics (label distribution, image brightness, text length) with alerts on distribution shift.
- Implement online active learning: score unlabeled examples by model uncertainty and prioritize labeling the most informative ones.
