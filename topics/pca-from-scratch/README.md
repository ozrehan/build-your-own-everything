---
title: "PCA from Scratch"
category: "ai-ml"
difficulty: "intermediate"
tags: [pca, dimensionality-reduction, linear-algebra]
related: [kmeans-clustering, embeddings-visualizer, dataset-pipeline]
---

# PCA from Scratch

Principal Component Analysis finds the directions in which your data varies the most, letting you compress hundreds of features into a few while keeping the signal. Deriving it yourself — from covariance matrix to eigendecomposition — turns linear algebra from abstract math into the single most useful unsupervised tool in the kit.

## Core concepts

- **Variance as information** — PCA assumes directions of high variance carry the signal and low-variance directions are mostly noise. Projecting onto the top principal components keeps the structure while discarding dimensions.
- **Covariance matrix** — The d×d matrix of pairwise feature covariances. Its eigenvectors are the principal directions; its eigenvalues say how much variance each direction explains. PCA is literally "eigendecompose this matrix".
- **SVD connection** — In practice you compute PCA via the Singular Value Decomposition of the centered data matrix, which is numerically stabler than forming the covariance matrix explicitly. Same result, better arithmetic.
- **Explained variance ratio** — Each eigenvalue divided by the total gives the fraction of variance its component captures. The cumulative curve tells you how many components to keep — the principled version of the elbow method.
- **Whitening** — Dividing each component by the square root of its eigenvalue gives unit-variance, uncorrelated features. Useful as preprocessing when downstream algorithms assume spherical data.
- **PCA's blind spots** — It's linear (can't unroll a Swiss roll — that's what UMAP/t-SNE are for) and variance isn't always signal (a high-variance nuisance feature will dominate the components). Standardizing features first is usually mandatory.

## How it works

Center the data (subtract each feature's mean), then compute the SVD of the centered matrix: `X = UΣVᵀ`. The columns of V are the principal components, ordered by decreasing singular values in Σ; the squared singular values (divided by n−1) are the explained variances. To reduce to k dimensions, project: `X_reduced = X_centered · V[:, :k]`. Reconstruction is the reverse multiplication, and the reconstruction error equals the discarded variance — which is why PCA is the optimal linear compressor in the least-squares sense.

## Build milestones

1. Implement PCA via eigendecomposition of the covariance matrix in NumPy; verify against scikit-learn on a small dataset.
2. Reimplement via SVD; compare numerical stability on an ill-conditioned dataset and confirm identical components.
3. Plot explained-variance curves and 2D projections of a real dataset (e.g. digits); color points by class to see structure emerge.
4. Build an eigenfaces demo: PCA on face images, then reconstruct faces from 50 components and visualize the top eigenfaces.
5. Use PCA as preprocessing: compare k-means clustering and a classifier's performance with and without PCA dimensionality reduction.

## Best resources

- [Principal component analysis (Wikipedia)](https://en.wikipedia.org/wiki/Principal_component_analysis) — Thorough reference on the derivation, SVD relationship, and limitations.
- [scikit-learn: Decompositions](https://scikit-learn.org/stable/modules/decomposition.html) — The user guide covering PCA, randomized PCA, and kernel PCA with guidance on when to use each.
- [In Depth: Principal Component Analysis](https://jakevdp.github.io/PythonDataScienceHandbook/05.09-principal-component-analysis.html) — Jake VanderPlas's hands-on chapter with the digits visualization.
- [A Tutorial on Principal Components Analysis (Lindsay Smith)](http://www.cs.otago.ac.nz/cosc453/student_tutorials/principal_components.pdf) — The classic gentle introduction, free PDF.
- [StatQuest: PCA](https://www.youtube.com/watch?v=_UVHneBUBW0) — Josh Starmer's famously clear video walkthrough of the intuition.

## Stretch ideas

- Implement kernel PCA (the kernel trick applied to PCA) and unroll the Swiss-roll dataset that linear PCA can't handle.
- Build incremental PCA for data too large for memory, processing it in batches with running mean/covariance updates.
