---
title: "Embeddings Visualizer"
category: "ai-ml"
difficulty: "beginner"
tags: [embeddings, visualization, nlp]
related: [transformer-from-scratch, rag-pipeline, vector-search-hnsw]
---

# Embeddings Visualizer

Word and sentence embeddings place meaning into geometry: similar things end up near each other in a high-dimensional vector space. Building a visualizer — projecting hundreds of dimensions down to an interactive 2D map — makes the abstract idea of "semantic similarity" something you can literally see and poke at.

## Core concepts

- **Distributional hypothesis** — "You shall know a word by the company it keeps." Embeddings learn from co-occurrence: words appearing in similar contexts get similar vectors, no dictionary required.
- **Word2Vec** — Trains by predicting neighbors (skip-gram) or a word from its neighbors (CBOW). The famous king − man + woman ≈ queen arithmetic falls out of the geometry it learns.
- **Cosine similarity** — The standard way to measure closeness between embeddings: the cosine of the angle between vectors, ignoring magnitude. Nearest-neighbor search over cosine similarity is the backbone of semantic search.
- **Dimensionality reduction** — PCA preserves global variance linearly; t-SNE and UMAP preserve local neighborhoods nonlinearly, producing the clustered "islands" you see in embedding plots. The choice changes the story the picture tells.
- **Analogies and bias** — Vector arithmetic reveals both the power (capital-country relations) and the problems (gendered occupation associations) baked into the training corpus. Embeddings are a mirror of their data.
- **Contextual vs static embeddings** — Word2Vec gives one vector per word; transformer models give one vector per word *in context* ("bank" as river vs money). Visualizing both shows why contextual models won.

## How it works

You load pretrained vectors (Word2Vec, GloVe, or sentence embeddings from a transformer), pick a vocabulary subset, and compute pairwise cosine similarities. A reduction algorithm (PCA for a quick linear view, UMAP/t-SNE for neighborhood structure) maps the vectors to 2D coordinates, which you render as an interactive scatter plot — hover to see the word, click to see nearest neighbors. The pipeline is: embed → reduce → plot → explore, and the exploration step (querying analogies, inspecting clusters) is where the learning happens.

## Build milestones

1. Load pretrained GloVe vectors; write a nearest-neighbor lookup by cosine similarity and test it on a few words.
2. Implement the classic analogy solver (`king - man + woman`) and evaluate it on a small analogy test set.
3. Add PCA projection and a static matplotlib scatter plot colored by word category (animals, capitals, verbs…).
4. Build an interactive web visualizer: search a word, highlight its neighbors, toggle between PCA/UMAP projections.
5. Add sentence embeddings from a transformer model; compare static vs contextual embeddings on polysemous words like "bank" or "crane".

## Best resources

- [Efficient Estimation of Word Representations (word2vec)](https://arxiv.org/abs/1301.3781) — The Mikolov et al. paper that started the embedding era.
- [GloVe: Global Vectors for Word Representation](https://arxiv.org/abs/1406.1078) — Pennington et al.'s count-based alternative; also ships great pretrained vectors to play with.
- [TensorFlow Embedding Projector](https://projector.tensorflow.org/) — The reference interactive embedding visualizer; study its UX before building yours.
- [Word Embeddings (TensorFlow guide)](https://www.tensorflow.org/text/guide/word_embeddings) — Hands-on tutorial for training your own embeddings from scratch.
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings) — How modern API embeddings work: use cases, similarity search, and evaluation.
- [How to Use t-SNE Effectively (Distill)](https://distill.pub/2016/misread-tsne/) — Essential reading before you trust any 2D embedding plot; t-SNE lies in predictable ways.

## Stretch ideas

- Visualize how embeddings shift during training: checkpoint a model every epoch and animate the clusters forming.
- Build a tiny semantic search engine on your embeddings and evaluate it against keyword search on a small document set.
