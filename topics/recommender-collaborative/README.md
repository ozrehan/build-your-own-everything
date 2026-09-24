---
title: "Collaborative Recommender"
category: "ai-ml"
difficulty: "intermediate"
tags: [recommender-systems, collaborative-filtering, matrix-factorization]
related: [embeddings-visualizer, dataset-pipeline, eval-harness-llm]
---

# Collaborative Recommender

Collaborative filtering recommends items based on patterns across users: "people who liked what you liked also liked this." Implementing matrix factorization yourself — learning latent user and item vectors whose dot products predict ratings — reveals that recommendation is secretly an embedding problem, closely related to word2vec.

## Core concepts

- **User-item matrix** — Ratings arranged as a sparse matrix: rows are users, columns are items, and 99% of entries are missing. The entire field is about filling in the blanks sensibly.
- **Latent factors** — Matrix factorization learns a low-dimensional vector per user and per item such that their dot product approximates the known ratings. The dimensions end up encoding genres, tastes, and styles — discovered, never labeled.
- **User-based vs item-based** — Classical neighborhood methods predict from similar users' ratings or similar items' ratings. Item-based (this item is like items you rated highly) won in practice because item similarities are more stable than user similarities.
- **Implicit feedback** — Clicks, views, and purchases (not star ratings) dominate real systems. Implicit data has no negatives — a missing entry means "didn't see it", not "disliked it" — which changes the loss function entirely.
- **Cold start** — New users and new items have no history, so pure collaborative filtering can't handle them. Real systems blend in content-based features (genres, text) as a fallback.
- **Ranking vs rating prediction** — Predicting a 4.2 vs 4.3 star rating is less useful than getting the top-10 ordering right. Modern evaluation uses ranking metrics (precision@k, NDCG), and training often optimizes pairwise ranking losses directly.

## How it works

Factorize the sparse rating matrix R ≈ U·Vᵀ by minimizing squared error over *observed* entries only, plus L2 regularization on the factors. Optimize with SGD or alternating least squares: each step nudges a user vector toward the item vectors they rated highly (scaled by the rating error). Add user/item bias terms to capture that some users rate generously and some items are universally liked. For implicit feedback, switch to a ranking loss (like BPR) that trains the model to score observed interactions above unobserved ones. Recommendations for a user are the highest-scoring unrated items by dot product.

## Build milestones

1. Load the MovieLens 100k dataset; build the sparse user-item matrix and compute baseline predictors (global mean, user/item biases).
2. Implement SGD matrix factorization with biases; beat the bias baseline on RMSE for held-out ratings.
3. Add train/test splitting by time (not random — avoid leaking the future) and evaluate with ranking metrics (precision@10, NDCG).
4. Implement item-based kNN collaborative filtering; compare its recommendations qualitatively against matrix factorization for a few users.
5. Handle implicit feedback: binarize ratings to "interacted", train with a ranking loss, and build a top-N recommendation API for a user.

## Best resources

- [Google ML: Recommendation Systems](https://developers.google.com/machine-learning/recommendation) — Google's course covering both retrieval and ranking stages of production recommenders.
- [Netflix Prize (Wikipedia)](https://en.wikipedia.org/wiki/Netflix_Prize) — The million-dollar competition that made matrix factorization famous; great history and context.
- [Collaborative Filtering for Implicit Feedback Datasets](https://arxiv.org/abs/0811.3949) — Hu, Koren & Volinsky's ALS paper; the standard approach for click/purchase data.
- [Surprise](http://surpriselib.com/) — The Python library for explicit-feedback recommenders; compare your factorization against its SVD implementation.
- [MovieLens Datasets](https://grouplens.org/datasets/movielens/) — The canonical public rating datasets, from 100k to 25M interactions.

## Stretch ideas

- Build the two-stage production pattern: a fast candidate-retrieval model plus a heavier ranking model with more features.
- Add content-based side features (movie genres, text embeddings of descriptions) to make a hybrid that handles cold-start items.
