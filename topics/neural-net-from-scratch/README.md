---
title: "Neural Net from Scratch"
category: "ai-ml"
difficulty: "beginner"
tags: [neural-networks, backprop, numpy]
related: [autograd-engine, optimizer-zoo, decision-tree]
---

# Neural Net from Scratch

A neural network is just layers of weighted sums followed by nonlinearities, trained by nudging each weight in the direction that reduces error. Building one yourself — with only NumPy, no framework — turns backpropagation from a scary formula into a mechanical procedure you can trace by hand.

## Core concepts

- **Perceptron** — A single neuron computes a weighted sum of its inputs plus a bias, then passes it through an activation function. Everything deep learning does is this idea stacked deeper.
- **Activation functions** — Nonlinearities like ReLU, sigmoid, and tanh let networks model curved decision boundaries; without them, any stack of layers collapses into a single linear function.
- **Forward pass** — Data flows input → hidden layers → output, producing a prediction. Every intermediate value ("activation") must be kept around, because the backward pass needs it.
- **Loss function** — A single number (mean squared error, cross-entropy) that measures how wrong the prediction is. Training is just minimizing this number with respect to the weights.
- **Backpropagation** — The chain rule from calculus applied layer by layer: starting from the loss, you compute how much each weight contributed to the error, working backwards through the network.
- **Gradient descent** — Update each weight by stepping a small amount (the learning rate) in the opposite direction of its gradient. Repeat thousands of times and the loss goes down.
- **Overfitting** — A network that memorizes training data instead of learning patterns. Splitting off a validation set is how you detect it; regularization is how you fight it.

## How it works

You initialize small random weights, feed an input forward through matrix multiplications and activations, and compare the output to the target with a loss function. Then you walk backwards: for each layer, compute the gradient of the loss with respect to that layer's inputs and weights using the chain rule, and update the weights by `w -= lr * grad`. Do this over many examples (in mini-batches for efficiency) and the network gradually carves out the decision boundary. There is no magic — just the chain rule, arithmetic, and repetition.

## Build milestones

1. Build a single-neuron perceptron in NumPy that learns a linear decision boundary on 2D synthetic data.
2. Add a hidden layer with ReLU and implement the full forward/backward pass by hand — verify your gradients with numerical gradient checking.
3. Train a 2-layer network on the XOR problem, then on the digits dataset from scikit-learn; plot loss over time.
4. Add mini-batch training, learning-rate scheduling, and a validation split to reach 95%+ on a real dataset.
5. Implement softmax + cross-entropy, L2 regularization, and dropout — compare training curves with and without them.

## Best resources

- [Neural Networks and Deep Learning](http://neuralnetworksanddeeplearning.com/) — Michael Nielsen's free book; the clearest explanation of backprop anywhere.
- [Yes you should understand backprop](https://karpathy.ai/zero.html) — Karpathy's famous essay demystifying backpropagation with tiny code.
- [CS231n: Neural Networks Part 1](https://cs231n.github.io/neural-networks-1/) — Stanford's notes on modeling one neuron and setting up the architecture.
- [TensorFlow Playground](https://playground.tensorflow.org/) — Interactive visualization of how layers, activations, and learning rates shape decision boundaries.
- [3Blue1Brown: Neural Networks](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) — Visual intuition for gradients and backprop before you touch code.
- [Google Machine Learning Crash Course](https://developers.google.com/machine-learning/crash-course) — Free Google course with exercises on training neural nets.

## Stretch ideas

- Implement your own tiny framework on top of the network (layers as objects, a Trainer class) and re-train everything through it.
- Train on a harder dataset like Fashion-MNIST and experiment with width/depth to see how capacity changes the result.
