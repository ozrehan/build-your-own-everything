---
title: "Decision Tree"
category: "ai-ml"
difficulty: "beginner"
tags: [decision-trees, classification, supervised-learning]
related: [q-learning-agent, dataset-pipeline, recommender-collaborative]
---

# Decision Tree

A decision tree classifies by asking a sequence of yes/no questions about the features — "is income > 50k?", "is age < 30?" — learned greedily from data. Implementing the splitting logic yourself makes impurity measures concrete, and explains both why single trees overfit and why forests of them are so powerful.

## Core concepts

- **Recursive splitting** — Training picks the feature and threshold that best separates the data, splits into two child nodes, and recurses. The result is a set of nested if-else rules that partition feature space into rectangles.
- **Impurity measures** — Gini impurity and entropy quantify how mixed a node's labels are. The split criterion maximizes impurity *reduction* (information gain): the best question is the one that makes the children purest.
- **Greedy construction** — At each node the algorithm picks the locally best split without lookahead. This is fast but myopic — a globally optimal tree is NP-hard, which is why greedy heuristics rule in practice.
- **Overfitting and pruning** — An unconstrained tree will grow until every leaf is pure, memorizing noise. Limiting depth, requiring minimum samples per leaf, or pruning back branches trades training accuracy for generalization.
- **Feature importance** — Summing each feature's total impurity reduction across the tree gives a built-in importance ranking — one reason trees remain popular where interpretability matters.
- **From trees to forests** — A single tree is high-variance (small data changes → different tree). Random forests average hundreds of trees trained on bootstrapped samples with random feature subsets, which is why they "just work" on tabular data.

## How it works

For each node, evaluate every feature and candidate threshold, computing the weighted impurity of the resulting children; pick the split with the largest information gain. Recurse on each child until a stopping rule fires (max depth, min samples, or pure node), then store the majority class (or mean, for regression) at the leaf. Prediction is a walk down the tree following the stored thresholds. The whole algorithm is maybe 100 lines — the subtlety is all in choosing splits efficiently (sorting features once, scanning thresholds) and stopping at the right time.

## Build milestones

1. Implement Gini impurity and a brute-force best-split search; train a depth-2 tree on a 2D dataset and plot the decision boundary.
2. Complete the recursive tree builder with stopping criteria; evaluate train vs test accuracy on a real tabular dataset.
3. Add pruning (max depth, min samples per leaf, cost-complexity); plot accuracy vs depth to find the overfitting knee.
4. Extend to regression (variance reduction as the criterion) and multi-class classification.
5. Implement a random forest on top of your tree (bootstrap sampling + feature subsampling) and measure the accuracy jump over a single tree.

## Best resources

- [Decision tree learning (Wikipedia)](https://en.wikipedia.org/wiki/Decision_tree_learning) — Clear reference for ID3/C4.5/CART, impurity measures, and pruning.
- [scikit-learn: Decision Trees](https://scikit-learn.org/stable/modules/tree.html) — The user guide covers the exact algorithm variants, parameters, and practical tips.
- [Random forests (Wikipedia)](https://en.wikipedia.org/wiki/Random_forest) — How bagging and feature randomness turn weak trees into a strong ensemble.
- [The Elements of Statistical Learning](https://hastie.su.domains/Papers/ESLII.pdf) — Hastie et al.'s free classic; chapters 9–10 give the rigorous treatment of trees and ensembles.
- [XGBoost Documentation](https://xgboost.readthedocs.io/en/stable/) — The gradient-boosted-tree library that dominates tabular competitions; read after your forest works.

## Stretch ideas

- Implement gradient-boosted trees (fit each new tree to the residuals of the ensemble) and compare against your random forest.
- Build a tree visualizer that renders the learned splits as an interactive diagram with per-node sample counts.
