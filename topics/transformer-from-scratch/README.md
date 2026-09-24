---
title: "Transformer from Scratch"
category: "ai-ml"
difficulty: "advanced"
tags: [transformers, attention, llm]
related: [tokenizer-bpe, autograd-engine, rnn-text-generator, prompt-cache]
---

# Transformer from Scratch

The Transformer replaced recurrence with self-attention: every token directly looks at every other token, weighted by learned relevance. Reimplementing a GPT-style decoder yourself — attention, residuals, layer norm, the whole training loop — is how the architecture stops being a diagram and becomes machinery you truly own.

## Core concepts

- **Self-attention** — For each token, compute query/key/value projections; attention scores are `softmax(QK^T / sqrt(d))`, used to take a weighted average of values. It's a content-addressable lookup: tokens pull information from wherever it's relevant in the sequence.
- **Multi-head attention** — Running several attention mechanisms in parallel lets different heads specialize (one tracks syntax, another tracks long-range references). Their outputs are concatenated and re-projected.
- **Positional encoding** — Attention is permutation-invariant, so position must be injected: sinusoidal encodings in the original paper, learned or rotary (RoPE) embeddings in modern models.
- **Causal masking** — In a decoder, token *i* may only attend to tokens ≤ *i*, enforced by masking future positions with −∞ before the softmax. This single mask is what makes autoregressive generation possible.
- **Residual connections + layer norm** — Each sub-layer adds its input back (`x + Sublayer(x)`) and normalizes, which keeps gradients flowing through dozens of layers without vanishing.
- **Feed-forward block** — After attention, each position independently passes through a two-layer MLP (usually 4× wider inside) that does most of the model's "thinking" and stores factual knowledge.
- **Next-token prediction** — Training minimizes cross-entropy between the model's predicted distribution and the actual next token. That's the entire objective behind GPT — everything else is scale.

## How it works

Token IDs are embedded into vectors and given positional information. Each transformer block runs masked multi-head self-attention (letting every position gather context from its past), adds the residual, normalizes, then runs the position-wise MLP, adds the residual again, and normalizes. After N blocks, a final linear layer projects to vocabulary size and a softmax gives next-token probabilities. You train by feeding text, shifting targets by one position, and minimizing cross-entropy with Adam. Generation is a loop: sample a token, append it, repeat — with the KV cache storing past keys/values so you don't recompute the whole prefix each step.

## Build milestones

1. Implement single-head causal self-attention in NumPy and verify the masking math on a tiny sequence.
2. Build a full decoder block (multi-head attention, MLP, layer norm, residuals) in PyTorch; overfit it on a single paragraph until loss → 0.
3. Train a character-level mini-GPT on a small corpus (e.g. Shakespeare); generate text and observe it learning spelling before words before style.
4. Scale up: BPE tokenizer, larger model, proper train/val split, learning-rate warmup and cosine decay.
5. Add generation features: temperature, top-k/top-p sampling, and a KV cache; benchmark tokens/sec with and without the cache.

## Best resources

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — The original 2017 paper; short, readable, and the source of truth for the architecture.
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — Jay Alammar's visual walkthrough of every component, the best conceptual companion.
- [Let's build GPT: from scratch, in code, spelled out](https://www.youtube.com/watch?v=kCc8FmEb1nY) — Karpathy builds a working GPT live; follow along and type every line.
- [nanoGPT](https://github.com/karpathy/nanoGPT) — The minimal-but-real training codebase the video builds toward; study its structure.
- [Attention? Attention!](https://lilianweng.github.io/posts/2018-06-24-attention/) — Lilian Weng's deep dive into attention variants and their math.
- [Neural Networks: Zero to Hero](https://github.com/karpathy/nn-zero-to-hero) — The full lecture series and code this project sits inside.

## Stretch ideas

- Implement RoPE positional embeddings and grouped-query attention, the two upgrades that define modern open models.
- Train a tiny encoder (BERT-style) with masked-language modeling on the same corpus and compare its representations to your decoder's.
