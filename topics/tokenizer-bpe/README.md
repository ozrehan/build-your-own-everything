---
title: "BPE Tokenizer"
category: "ai-ml"
difficulty: "intermediate"
tags: [tokenization, nlp, bpe]
related: [transformer-from-scratch, rnn-text-generator, dataset-pipeline]
---

# BPE Tokenizer

Byte-Pair Encoding turns raw text into the integer sequences models actually consume: it starts from characters and repeatedly merges the most frequent adjacent pair until the vocabulary reaches a target size. Implementing it yourself reveals why "token" is a slippery concept — and why tokenizers quietly shape everything downstream, from cost to model behavior.

## Core concepts

- **Why subwords** — Pure word tokenizers explode in vocabulary size and choke on unseen words; pure character tokenizers make sequences painfully long. Subword methods like BPE split the difference: common words stay whole, rare words decompose into pieces.
- **Merge rules** — The trained artifact is an ordered list of merges (e.g. `e + r → er`). Encoding applies them greedily in priority order, which makes tokenization deterministic for a fixed vocabulary.
- **Pre-tokenization** — Before BPE runs, text is split into chunks (by whitespace, or with a regex like GPT-2's that keeps contractions and punctuation separate). This step decides what merges are even allowed to form.
- **Byte-level BPE** — Modern tokenizers operate on UTF-8 bytes rather than characters, so any string — any language, any emoji — can be represented with no out-of-vocabulary tokens, at the cost of sometimes splitting characters mid-way.
- **Special tokens** — Reserved IDs for `<bos>`, `<eos>`, padding, and masking that the model treats structurally rather than linguistically. Mismatching them between tokenizer and model silently corrupts training.
- **Detokenization** — Decoding isn't just concatenation: byte-level tokens need byte decoding, and word-boundary markers (like GPT-2's `Ġ` for space) must be translated back to real spaces.

## How it works

Training: split a corpus into words with frequencies, start with a vocabulary of individual bytes/characters, then loop — count every adjacent symbol pair across the corpus, merge the most frequent pair into a new token, rewrite the corpus with the merge — until the vocabulary hits the target size, saving the ordered merge list. Encoding: pre-tokenize the input text, split each chunk into base symbols, then apply the saved merges in order until no more apply, mapping final tokens to IDs. Decoding reverses the ID map and handles byte/space reconstruction.

## Build milestones

1. Write a naive BPE trainer on a small text file: word frequencies → pair counting → merges, printing the vocabulary as it grows.
2. Implement the encoder: apply merge rules in priority order and convert tokens to integer IDs.
3. Implement the decoder with correct space/byte handling; verify perfect round-trips on tricky inputs (emoji, code, mixed scripts).
4. Train on a real corpus at a realistic vocab size (e.g. 8k–32k) and compare token counts vs a word-level baseline to see the compression.
5. Add a regex pre-tokenizer and special-token handling; benchmark encode/decode throughput.

## Best resources

- [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — The Sennrich et al. paper that introduced BPE to NLP; the algorithm fits on one page.
- [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) — Karpathy implements byte-level BPE from scratch, including the regex pre-tokenizer.
- [tiktoken](https://github.com/openai/tiktoken) — OpenAI's fast BPE implementation; read it to see how the naive algorithm gets productionized.
- [tokenizers (Hugging Face)](https://github.com/huggingface/tokenizers) — The Rust-backed library behind most open models; great for comparing your output token-for-token.
- [Summary of the tokenizers](https://huggingface.co/docs/transformers/v4.47.1/tokenizer_summary) — HF's conceptual guide to BPE, WordPiece, and Unigram with worked examples.
- [Tokenizers: Components](https://huggingface.co/docs/tokenizers/en/components) — How models, pre-tokenizers, and decoders compose in a real tokenizer pipeline.

## Stretch ideas

- Implement WordPiece (likelihood-based merges) and Unigram (probabilistic, pruned vocabulary) on the same corpus and compare tokenizations side by side.
- Train tokenizers on code vs prose vs another language and measure how vocabulary specialization changes tokens-per-word and model context usage.
