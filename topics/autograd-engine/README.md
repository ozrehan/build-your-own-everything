---
title: "Autograd Engine"
category: "ai-ml"
difficulty: "intermediate"
tags: [autograd, backpropagation, deep-learning]
related: [neural-net-from-scratch, transformer-from-scratch, optimizer-zoo]
---

# Autograd Engine

An autograd engine records every arithmetic operation as a node in a computation graph, then walks the graph backwards applying the chain rule to get gradients automatically. Building one — a miniature PyTorch — is what makes reverse-mode automatic differentiation click: it's just a topological sort plus the chain rule.

## Core concepts

- **Computation graph** — A directed acyclic graph where each node is a value produced by an operation (add, multiply, tanh). Recording it during the forward pass is what makes "automatic" differentiation possible.
- **Reverse-mode autodiff** — Instead of differentiating symbolically, you compute each operation's local derivative and multiply gradients as you walk the graph backwards. One backward pass gives the gradient of a scalar output with respect to every input — ideal for neural nets with millions of parameters.
- **Topological ordering** — Gradients must flow from output to inputs in reverse order of computation. A depth-first traversal of the graph produces the correct order; getting this wrong silently produces wrong gradients.
- **Local gradients** — Each operation knows only its own derivative (e.g. `d(a*b)/da = b`). The chain rule composes these local pieces into the full gradient, which is why an autograd engine only needs a small set of primitive ops.
- **Gradient accumulation** — A value used by multiple downstream ops receives gradient contributions from each path; they must be summed, not overwritten. This is the `+=` in every `.backward()` implementation.
- **Broadcasting** — Element-wise ops on differently shaped arrays (like adding a bias vector to a matrix) need gradient "un-broadcasting": summing gradients back down to the original shape. A classic source of subtle bugs.

## How it works

You wrap numbers in a `Value` object that stores the data plus pointers to its parent values and the operation that created it. Every operator (`+`, `*`, `tanh`, `matmul`) is overloaded to build a new node and register a local backward closure. Calling `.backward()` on the final scalar runs a topological sort of the graph, seeds the output gradient with 1.0, then visits nodes in reverse order, invoking each closure to push gradients to parents, accumulating where paths merge. That accumulated gradient per parameter is exactly what gradient descent needs.

## Build milestones

1. Implement scalar-valued autograd: a `Value` class with `+`, `*`, `tanh`, and `backward()` using topological sort.
2. Verify correctness with numerical gradient checking on a small expression tree.
3. Extend to tensors (NumPy arrays): add `matmul`, broadcasting with gradient un-broadcasting, `sum`, and `mean`.
4. Build a tiny MLP on top of your engine and train it on a toy dataset — the same code should now look like miniature PyTorch.
5. Add niceties: `.zero_grad()`, a `Parameter` concept, no-grad inference mode, and ReLU/softmax.

## Best resources

- [micrograd](https://github.com/karpathy/micrograd) — Karpathy's ~150-line autograd engine; the definitive reference implementation to study and replicate.
- [Yes you should understand backprop](https://karpathy.ai/zero.html) — The essay that motivates building micrograd in the first place.
- [Automatic Differentiation in Machine Learning: a Survey](https://arxiv.org/abs/1502.05767) — The rigorous survey covering forward vs reverse mode and implementation strategies.
- [PyTorch: A Note on Automatic Differentiation](https://pytorch.org/docs/stable/notes/autograd.html) — How the real framework handles the graph, accumulation, and edge cases.
- [Calculus on Computational Graphs: Backpropagation](https://colah.github.io/posts/2015-08-Backprop/) — Chris Olah's visual walkthrough of derivatives on graphs.

## Stretch ideas

- Implement forward-mode autodiff too and benchmark both modes on a wide-shallow vs narrow-deep function to feel the complexity difference.
- Add higher-order gradients (gradient of a gradient) by making `backward()` itself build graph nodes — needed for things like meta-learning.
