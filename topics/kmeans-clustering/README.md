---
title: "K-Means Clustering"
category: "ai-ml"
difficulty: "beginner"
tags: [clustering, unsupervised-learning, k-means]
related: [pca-from-scratch, embeddings-visualizer, dataset-pipeline]
---

# K-Means Clustering

K-means groups data into k clusters by alternating between assigning each point to its nearest centroid and moving each centroid to its cluster's mean. It's the simplest unsupervised learning algorithm that actually works — and implementing it exposes the assumptions hiding inside "just cluster it": spherical clusters, known k, and sensitivity to initialization.

## Core concepts

- **The two-step loop** — Assignment: each point joins its nearest centroid. Update: each centroid becomes the mean of its members. Repeat until assignments stop changing. Each step provably reduces the within-cluster variance, so the algorithm always converges — to a *local* optimum.
- **The k-means objective** — Minimize the sum of squared distances from points to their assigned centroid. Simple, but finding the global optimum is NP-hard, which is why initialization and restarts matter.
- **k-means++ initialization** — Picking the first centroid randomly, then each subsequent one with probability proportional to its squared distance from existing centroids, spreads seeds sensibly. It provably improves the expected result and is the default everywhere.
- **Choosing k** — The elbow method (plot objective vs k, look for the bend), silhouette scores, and domain knowledge. There is no principled automatic answer — k is a modeling decision, not a discoverable truth.
- **Assumptions baked in** — K-means assumes roughly spherical, equally-sized clusters and is sensitive to feature scaling (always standardize first). Feed it elongated or nested clusters and it fails in instructive ways.
- **Local optima** — Different initializations give different final clusterings. The standard fix is multiple restarts, keeping the run with the lowest objective — cheap and effective.

## How it works

Initialize k centroids (k-means++), then iterate: compute the distance from every point to every centroid (a single vectorized matrix operation), assign each point to the nearest, and recompute each centroid as the mean of its assigned points. Stop when assignments stabilize or a max iteration count hits. That's the entire algorithm — Lloyd's method in about 20 lines of NumPy. The interesting engineering is all around it: vectorizing the distance computation, handling empty clusters, and running restarts in parallel.

## Build milestones

1. Implement Lloyd's algorithm in NumPy with random initialization; cluster a 2D blob dataset and plot the result.
2. Add k-means++ seeding; compare final objective values across 20 random vs k-means++ runs.
3. Implement the elbow method and silhouette score; use them to pick k on a dataset where the answer isn't obvious.
4. Apply it to a real task: color quantization (reduce an image to 16 colors) or document clustering on TF-IDF vectors.
5. Break it on purpose: run it on moons/circles data and on unscaled features, then fix what you can (scaling, restarts) and document what you can't.

## Best resources

- [K-means clustering (Wikipedia)](https://en.wikipedia.org/wiki/K-means_clustering) — The algorithm, its variants, and known limitations in one place.
- [scikit-learn: Clustering](https://scikit-learn.org/stable/modules/clustering.html) — The user guide comparing k-means against DBSCAN, hierarchical, and other methods.
- [scikit-learn KMeans API](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) — The reference implementation's parameters and their effects.
- [k-means++: The Advantages of Careful Seeding](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf) — Arthur & Vassilvitskii's short paper; the seeding trick with proofs.
- [Google ML: Clustering](https://developers.google.com/machine-learning/clustering) — Google's crash-course module with intuitive explanations and exercises.

## Stretch ideas

- Implement k-medoids (centroids must be actual data points) and Gaussian mixture models (soft assignments via EM) on the same datasets to see the generalization ladder.
- Build an interactive demo where users draw 2D points and watch the centroids converge step by step.
