---
title: "Optimizer Zoo"
category: "ai-ml"
difficulty: "intermediate"
tags: [optimization, gradient-descent, training]
related: [neural-net-from-scratch, autograd-engine, cnn-image-classifier]
---

# Optimizer Zoo

An optimizer is the rule that turns gradients into weight updates — and the differences between SGD, momentum, Adam, and friends are small formulas with outsized effects on training. Implementing the whole zoo on one shared interface, then racing them on the same problems, teaches you what each one is actually doing to the loss landscape.

## Core concepts

- **SGD with momentum** — Keeps a running average of past gradients (the "velocity") and steps along it instead of the raw noisy gradient. This damps oscillation in steep directions and accelerates along consistent ones.
- **Nesterov momentum** — A refinement that evaluates the gradient at the *lookahead* position (where momentum is taking you) rather than the current one — a corrective peek that reduces overshoot.
- **Adaptive learning rates** — AdaGrad, RMSprop, and Adam scale each parameter's step by its historical gradient magnitude, so rarely-updated parameters get bigger steps and frequently-updated ones get smaller steps. This matters enormously for sparse features like word embeddings.
- **Adam** — Combines momentum (first moment) with RMSprop-style scaling (second moment), plus bias correction for the early steps when the running averages are still warming up. The default choice for transformers, though not always the best final performer.
- **AdamW** — Decouples weight decay from the adaptive scaling: instead of folding L2 regularization into the gradient (where Adam's normalization distorts it), it decays the weights directly. The version you actually want when a paper says "Adam".
- **Learning-rate schedules** — Warmup (ramping up to avoid early instability) plus decay (cosine or linear cooldown) routinely matter as much as the optimizer choice itself. The schedule and optimizer must be evaluated together.

## How it works

Every optimizer maintains some per-parameter state — plain SGD keeps none, momentum keeps a velocity vector, Adam keeps first and second moment estimates. Each step: receive the gradient from backprop, update the state (e.g. `m = β1·m + (1−β1)·g`, `v = β2·v + (1−β2)·g²`), apply bias correction (`m̂ = m / (1−β1^t)`), then compute the update (`θ -= lr · m̂ / (sqrt(v̂) + ε)`) and optionally apply decoupled weight decay. Implementing them behind one `step(params, grads)` interface makes A/B comparisons trivial — and reveals how few lines separate these famous algorithms.

## Build milestones

1. Implement vanilla SGD and SGD-with-momentum from scratch; visualize their trajectories on a 2D quadratic with an elongated valley.
2. Add AdaGrad, RMSprop, and Adam behind a common interface; reproduce the classic "beaker" pathologies each one fixes.
3. Race all optimizers training the same small MLP; plot loss vs step and loss vs wall-clock to see the speed/stability tradeoffs.
4. Implement AdamW and learning-rate warmup + cosine decay; confirm the combo trains a tiny transformer more stably than Adam alone.
5. Add gradient clipping and compare final generalization (not just training loss) across optimizers — the fastest trainer isn't always the best model.

## Best resources

- [An overview of gradient descent optimization algorithms](https://ruder.io/optimizing-gradient-descent/) — Sebastian Ruder's definitive tour from SGD through Adam, with the math and the intuition.
- [Why Momentum Really Works](https://distill.pub/2017/momentum/) — Distill's interactive essay on what momentum is actually doing to the dynamics; corrects the naive "rolling ball" story.
- [Adam: A Method for Stochastic Optimization](https://arxiv.org/abs/1412.6980) — The original Kingma & Ba paper; short and worth reading once you've implemented it.
- [Decoupled Weight Decay Regularization (AdamW)](https://arxiv.org/abs/1711.05101) — Loshchilov & Hutter's fix that explains why "Adam with weight decay" was subtly wrong.
- [torch.optim documentation](https://pytorch.org/docs/stable/optim.html) — The reference for exact update rules, defaults, and edge-case behavior of every production optimizer.
- [Deep Learning Book, Chapter 8: Optimization](https://www.deeplearningbook.org/contents/optimization.html) — Goodfellow et al.'s rigorous treatment of the theory behind the zoo.

## Stretch ideas

- Implement a second-order method (L-BFGS) or a modern adaptive one (Lion, Sophia) and test whether the hype survives your benchmark.
- Build an optimizer visualizer that animates trajectories on real 2D loss surfaces sliced out of a trained network.
