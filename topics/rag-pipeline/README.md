---
title: "RAG Pipeline"
category: "ai-ml"
difficulty: "intermediate"
tags: [rag, retrieval, llm]
related: [vector-search-hnsw, embeddings-visualizer, transformer-from-scratch, eval-harness-llm]
---

# RAG Pipeline

Retrieval-Augmented Generation grounds an LLM's answers in your own documents: chunk the docs, embed them, retrieve the relevant chunks at query time, and stuff them into the prompt. Building the full pipeline yourself — chunking, indexing, retrieval, generation — demystifies the architecture behind nearly every production "chat with your docs" product.

## Core concepts

- **Chunking** — Documents are split into retrievable pieces. Chunk size and overlap are the highest-leverage knobs in the whole system: too big and retrieval is imprecise, too small and chunks lose the context needed to answer.
- **Embedding index** — Each chunk is embedded into a vector and stored in a vector index (see HNSW). At query time the question is embedded the same way and nearest neighbors become the retrieved context.
- **Dense vs sparse retrieval** — Dense (embedding) retrieval captures semantic similarity ("car" matches "automobile"); sparse (BM25/keyword) retrieval captures exact terms and rare names. Hybrid systems that combine both usually beat either alone.
- **Reranking** — A cheap first-stage retriever fetches many candidates; a heavier cross-encoder model then scores query+chunk pairs precisely and keeps the best few. This two-stage pattern is the standard quality lever.
- **Context stuffing** — Retrieved chunks are concatenated into the prompt with the question. Prompt budget is finite, so ranking quality directly determines what the model gets to see.
- **Grounded generation** — The LLM answers *from* the retrieved context rather than its weights, which reduces hallucination — but only if you prompt it to cite and refuse when the context lacks the answer. The model will happily invent otherwise.

## How it works

Offline: documents → chunked → embedded → stored in a vector index alongside metadata. Online: the user query is embedded, the index returns the top-k chunks (optionally reranked), and those chunks plus a "answer using only this context" instruction form the LLM prompt. The model generates the answer, ideally with citations to the chunks used. Evaluation closes the loop: for a set of test questions with known answers, you measure retrieval recall (was the right chunk fetched?) and answer correctness separately, because they fail independently.

## Build milestones

1. Build the naive pipeline: chunk text files by fixed size, embed with an API or local model, brute-force cosine search, prompt an LLM with the top-3 chunks.
2. Add proper chunking (sentence-aware with overlap) and metadata filtering; measure how chunk size changes answer quality on 10 test questions.
3. Swap brute-force search for an HNSW index; add BM25 hybrid retrieval with score fusion.
4. Add a reranking stage and citation-style prompts ("answer only from the context, cite chunk numbers"); handle the "not in the documents" refusal case.
5. Build an eval set of 30+ question/answer pairs; compute retrieval recall@k and answer accuracy, then iterate on chunking to move the numbers.

## Best resources

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) — The original Lewis et al. paper that named and formalized RAG.
- [Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906) — Karpukhin et al.'s bi-encoder retriever; the dense-retrieval half of every RAG system.
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook) — Practical notebooks on embeddings, retrieval, and RAG patterns that actually run.
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook) — Recipes including contextual retrieval and long-context RAG techniques.
- [LangChain Documentation](https://docs.langchain.com) — The standard framework's guides for building and tuning retrieval pipelines.
- [LlamaIndex Documentation](https://docs.llamaindex.ai/) — A data-framework alternative focused specifically on indexing and retrieval for LLMs.

## Stretch ideas

- Implement contextual retrieval (embedding each chunk with a generated summary of its document) and measure the recall lift.
- Add query rewriting / HyDE (generate a hypothetical answer, embed *that*) and compare retrieval quality against raw queries.
