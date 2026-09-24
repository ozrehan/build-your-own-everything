---
title: "Model Quantization"
category: "ai-ml"
difficulty: "advanced"
tags: [quantization, compression, inference]
related: [transformer-from-scratch, prompt-cache, optimizer-zoo]
---

# Model Quantization

Quantization shrinks models by storing weights in fewer bits — 8, 4, even 2 — so a 70B model fits on one GPU instead of four. Implementing it yourself, from naive rounding to GPTQ-style schemes, teaches the numerical reality behind "the 4-bit model": which bits matter, where precision is lost, and why some layers refuse to be quantized.

## Core concepts

- **Precision vs range** — FP32 → FP16 → INT8 → INT4: each step halves memory but narrows representable range. Quantization maps a float range onto integer buckets via scale and zero-point; the art is choosing the mapping so the error doesn't wreck the model.
- **Symmetric vs asymmetric** — Symmetric quantization centers buckets on zero (one scale); asymmetric adds a zero-point offset to use the full integer range for skewed distributions. Activations usually need asymmetric; weights often don't.
- **Per-tensor vs per-channel** — One scale for a whole tensor is simple but crude; per-channel (per-row) scales adapt to outlier channels. Outlier features in LLMs are the reason per-tensor quantization fails and per-channel succeeds.
- **Post-training quantization (PTQ)** — Quantize an already-trained model using a small calibration set, no retraining. GPTQ and AWQ made 4-bit PTQ nearly lossless for LLMs — the reason quantized open models work so well.
- **Quantization-aware training (QAT)** — Simulate quantization during training so the model adapts to the precision loss. More accurate than PTQ at very low bit-widths, but far more expensive — rarely worth it above 4 bits now.
- **KV-cache quantization** — Weights aren't the only memory hog: the KV cache for long contexts can exceed the model itself. Quantizing cached keys/values to 8 or 4 bits is the current frontier for long-context serving.

## How it works

Take a weight tensor, find its range (or per-channel ranges), and linearly map floats to integers: `q = round(x / scale) + zero_point`, storing scale/zero-point alongside. Dequantize on the fly during matmul (`x ≈ (q − zero_point) × scale`) or use integer kernels. GPTQ improves on naive rounding by quantizing columns sequentially and compensating: after quantizing one column, it updates the remaining weights using the inverse Hessian to cancel the introduced error. AWQ instead protects the ~1% of "salient" weights (identified via activation magnitudes) by scaling them up before quantization. Your build starts with naive per-channel INT8, measures perplexity degradation, then implements GPTQ's error compensation to recover it.

## Build milestones

1. Implement naive symmetric INT8 quantization of a small model's weights; measure size reduction and perplexity change.
2. Add asymmetric quantization and per-channel scales; identify which layers degrade most and why (outlier channels).
3. Implement GPTQ-style sequential quantization with Hessian-based error compensation on one transformer block; compare perplexity vs naive.
4. Quantize activations too (dynamic per-token scales); benchmark the full INT8 model's inference speed and memory.
5. Try 4-bit (NF4/GPTQ) quantization end to end; evaluate on a benchmark suite to quantify the accuracy cost of the memory win.

## Best resources

- [LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale](https://arxiv.org/abs/2208.07339) — Dettmers et al.; outlier-aware 8-bit inference that made big models runnable on single GPUs.
- [GPTQ: Accurate Post-Training Quantization for Generative Pretrained Transformers](https://arxiv.org/abs/2210.17323) — Frantar et al.; the one-shot 4-bit method with Hessian compensation.
- [AWQ: Activation-aware Weight Quantization](https://arxiv.org/abs/2306.00978) — Lin et al.; protecting salient weights via activation statistics, no retraining needed.
- [A Survey of Quantization Methods for Efficient Neural Network Inference](https://arxiv.org/abs/2103.13630) — Gholami et al.; the broad map of PTQ, QAT, and hardware considerations.
- [Hugging Face Optimum](https://github.com/huggingface/optimum) — The production toolkit (GPTQ, AWQ, bitsandbytes integrations); compare your implementation's output against it.

## Stretch ideas

- Implement KV-cache quantization in your from-scratch transformer and measure how far context length extends at fixed memory.
- Explore mixed-precision policies: automatically assign bit-widths per layer based on sensitivity analysis.
