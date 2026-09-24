---
title: "RNN Text Generator"
category: "ai-ml"
difficulty: "intermediate"
tags: [rnn, nlp, text-generation]
related: [tokenizer-bpe, transformer-from-scratch, dataset-pipeline]
---

# RNN Text Generator

A recurrent network reads text one token at a time, updating a hidden state that acts as memory, and predicts the next token from that state. Training one to write Shakespeare or code is the classic pre-transformer rite of passage — and it teaches sequential modeling, teacher forcing, and sampling in a way that makes transformers' design choices obvious.

## Core concepts

- **Hidden state as memory** — The RNN's state vector is updated each step (`h_t = f(h_{t-1}, x_t)`), so it must compress the entire history into fixed size. This bottleneck is both the idea's power and its fundamental limit.
- **Teacher forcing** — During training you feed the *true* previous token at each step rather than the model's own prediction, which stabilizes training but creates exposure bias: the model never learns to recover from its own mistakes.
- **Vanishing gradients** — Backpropagating through many time steps multiplies the same weight matrix repeatedly, so gradients shrink (or explode) exponentially. This is why plain RNNs can't learn long-range dependencies.
- **LSTM** — Adds a cell state plus input/forget/output gates that learn what to remember and what to discard, giving gradients a protected highway through time. The forget gate turned out to be the most important part.
- **GRU** — A streamlined LSTM with two gates (reset and update) and no separate cell state; roughly as capable with fewer parameters, and often the pragmatic choice.
- **Sampling strategies** — Generation quality depends heavily on decoding: greedy argmax is repetitive, pure sampling is chaotic, and temperature / top-k / top-p sampling interpolate between them.

## How it works

Characters (or tokens) are embedded into vectors and fed sequentially into the recurrent cell, which updates its hidden state each step. A linear head maps each hidden state to logits over the vocabulary, and the model is trained with cross-entropy to predict the next token at every position — all positions trained in parallel via teacher forcing. To generate, you seed the state with a prompt, sample a token from the output distribution, feed it back as the next input, and repeat. The hidden state carries the "memory" of everything generated so far.

## Build milestones

1. Build a character-level bigram/trigram baseline first — a surprisingly strong reference point that makes the RNN's gains measurable.
2. Implement a vanilla RNN cell from scratch in NumPy; train it on a tiny corpus and watch gradients vanish on long sequences.
3. Move to PyTorch: train a char-level LSTM on Shakespeare; generate samples at various temperatures and compare quality.
4. Add a GRU variant and an embedding layer; benchmark LSTM vs GRU vs n-gram on validation perplexity.
5. Train on a larger corpus (e.g. code or lyrics) with top-k/top-p sampling; build a small CLI that completes prompts interactively.

## Best resources

- [The Unreasonable Effectiveness of Recurrent Neural Networks](http://karpathy.github.io/2015/05/21/rnn-effectiveness/) — Karpathy's legendary post; char-RNNs writing Shakespeare and LaTeX.
- [Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — Chris Olah's visual, gate-by-gate explanation of how LSTMs work.
- [Attention and Augmented RNNs (Distill)](https://distill.pub/2016/augmented-rnns/) — Where RNNs meet attention; the bridge to the transformer era.
- [PyTorch Char-RNN Generation Tutorial](https://pytorch.org/tutorials/intermediate/char_rnn_generation_tutorial.html) — Official tutorial for training a name/surname generator with a char RNN.
- [Learning to Forget (GRU paper)](https://arxiv.org/abs/1412.3555) — Cho et al.'s paper introducing gated recurrent units for machine translation.

## Stretch ideas

- Implement a seq2seq model with attention (encoder-decoder) for a toy translation task and compare against the plain char-RNN.
- Add beam search decoding and measure how it changes generation quality vs greedy/temperature sampling.
