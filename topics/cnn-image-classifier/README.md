---
title: "CNN Image Classifier"
category: "ai-ml"
difficulty: "intermediate"
tags: [cnn, computer-vision, classification]
related: [neural-net-from-scratch, optimizer-zoo, dataset-pipeline]
---

# CNN Image Classifier

A convolutional network learns its own visual features — edges, textures, object parts — by sliding small learned filters across the image and stacking the results. Building one from convolution up (before touching a framework's `nn.Conv2d`) shows why CNNs need orders of magnitude less data than dense networks on images.

## Core concepts

- **Convolution** — Each filter is a small weight matrix slid across the image, computing dot products at every position. The same weights are reused everywhere, which is what makes CNNs translation-equivariant: a cat detector works wherever the cat is.
- **Feature maps** — The output of one filter across the whole image. Early layers learn Gabor-like edge detectors; deeper layers compose them into textures, parts, and eventually object-level concepts.
- **Pooling** — Downsampling (usually max-pooling) that shrinks feature maps, giving slight translation invariance and cutting computation. Modern architectures often replace it with strided convolutions.
- **Receptive field** — How much of the input image influences one output neuron. It grows with depth, which is why deep layers "see" whole objects while early layers see only edges.
- **Padding and stride** — Padding controls whether the output keeps the input's spatial size; stride controls the step size of the sliding window and is the main lever for downsampling.
- **Data augmentation** — Random crops, flips, and color jitter artificially expand the training set. On small image datasets it routinely matters more than architecture tweaks.
- **Transfer learning** — Features learned on ImageNet transfer surprisingly well to other vision tasks; fine-tuning a pretrained backbone beats training from scratch on small datasets almost every time.

## How it works

An image (height × width × channels) passes through alternating convolution+ReLU blocks and downsampling: each convolution learns K filters that detect K patterns at every location, producing K feature maps. After several blocks, the spatial maps are flattened (or globally average-pooled) into a vector and fed to a small dense classifier with softmax. Training is standard cross-entropy + backprop — the convolution backward pass is itself a convolution (with flipped filters), which is elegant once you see it. Inference is just the forward pass; the whole model is a few megabytes of filter weights.

## Build milestones

1. Implement 2D convolution from scratch in NumPy (no framework conv ops) and verify against a known filter like Sobel edge detection.
2. Build a tiny CNN (2 conv blocks + dense head) in PyTorch and train it on MNIST to 99%+.
3. Move to CIFAR-10: add data augmentation, batch normalization, and a deeper architecture (VGG-style); hit 85%+.
4. Implement a ResNet-style residual block and train a small ResNet; compare training stability and accuracy against the plain stack.
5. Visualize what the network learned: plot first-layer filters and generate class-activation maps (Grad-CAM) for test images.

## Best resources

- [CS231n: Convolutional Networks](https://cs231n.github.io/convolutional-networks/) — Stanford's notes: the canonical explanation of conv arithmetic, padding, and stride.
- [ImageNet Classification with Deep CNNs (AlexNet)](https://arxiv.org/abs/1206.9571) — The 2012 paper that started the deep learning boom; surprisingly readable.
- [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385) — ResNet: residual connections that made 100+ layer networks trainable.
- [PyTorch CIFAR-10 Tutorial](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html) — The official end-to-end training tutorial; a perfect starting skeleton.
- [fast.ai Practical Deep Learning](https://course.fast.ai/) — Free course that gets you training strong image classifiers in the first lessons.
- [Feature Visualization (Distill)](https://distill.pub/2017/feature-visualization/) — How researchers visualize what individual neurons and layers detect.

## Stretch ideas

- Implement depthwise-separable convolutions (MobileNet-style) and measure the accuracy-vs-parameters tradeoff against your ResNet.
- Train an object detector head (bounding-box regression on top of your backbone) on a small detection dataset.
