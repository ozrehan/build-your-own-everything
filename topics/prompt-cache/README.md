---
title: "Prompt Cache"
category: "ai-ml"
difficulty: "advanced"
tags: [caching, inference, kv-cache]
related: [transformer-from-scratch, agent-framework-react, model-quantization]
---

# Prompt Cache

Every LLM request reprocesses the entire prompt — but when the prefix is identical across requests (system prompt, few-shot examples, long documents), its key/value states can be cached and reused. Building a caching layer yourself, from KV-cache mechanics to prefix-aware routing, teaches the optimization that quietly cut production LLM costs by up to 90%.

## Core concepts

- **KV cache** — During generation, each token's key and value vectors are stored so future tokens don't recompute them. Without it, generating token N would cost O(N²); with it, each new token costs O(N). It's the reason long generations are feasible at all.
- **Prefix caching** — The KV cache for a prompt prefix depends only on that prefix's tokens. Two requests sharing the first 5,000 tokens can share the cached states for those tokens — the second request only computes the new suffix.
- **Cache breakpoints** — Providers let you mark where cacheable segments end (Anthropic's `cache_control`, OpenAI's automatic 1024-token thresholds). Everything before the breakpoint is the cache key; a single changed byte invalidates it.
- **Static-first prompt ordering** — Because caching is prefix-based, prompt structure now affects cost: stable content (system prompt, tool definitions, documents) goes first, dynamic content (timestamps, user query) goes last. Reordering is free money.
- **TTL and eviction** — Cached prefixes expire after inactivity (minutes, typically) and compete for GPU memory. High-QPS workloads hit cache naturally; low-volume ones may never benefit — caching is a throughput game.
- **Semantic caching** — A different layer: cache *responses* keyed by query similarity, so "what's the refund policy?" and "tell me about refunds" hit the same entry. Exact-prefix caching saves compute; semantic caching saves entire LLM calls.

## How it works

At the provider level, you structure requests with explicit breakpoints and stable prefixes; the provider hashes the prefix, looks up stored KV states, and on a hit skips the prefill computation (billing only a discounted read). At the application level, you add a semantic cache in front: embed the incoming query, look up near-duplicates in a vector store above a similarity threshold, and return the stored response directly. Your build ties both together: prompt templates designed for maximal stable prefixes, a local cache (Redis/SQLite) for exact and semantic hits, and instrumentation showing hit rate, latency saved, and dollars saved per request.

## Build milestones

1. Implement a KV-cache demo in your from-scratch transformer: generate with and without caching, measure the tokens/sec difference as context grows.
2. Build an exact-match response cache (SQLite: prompt hash → response) in front of an LLM API; add TTLs and measure hit rate on repeated queries.
3. Restructure prompts for prefix caching: move stable content first, mark breakpoints, and verify cache hits via the provider's usage fields.
4. Add semantic caching: embed queries, threshold on cosine similarity, and handle the false-positive risk (similar question, different answer).
5. Build a dashboard: hit rate, p50/p99 latency with vs without cache, and estimated cost savings over a week of real traffic.

## Best resources

- [Anthropic: Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — The canonical docs: breakpoints, minimum sizes, TTLs, and pricing mechanics.
- [OpenAI: Prompt Caching Guide](https://platform.openai.com/docs/guides/prompt-caching) — OpenAI's automatic prefix caching: thresholds, eligible models, and discount structure.
- [Efficient Memory Management for LLM Serving with PagedAttention](https://arxiv.org/abs/2309.06180) — The vLLM paper; how serving systems manage KV cache memory at scale.
- [Google Gemini: Context Caching](https://ai.google.dev/gemini-api/docs/caching) — Explicit cached-content objects with TTLs; a different API shape for the same idea.
- [GPTCache](https://github.com/zilliztech/gptcache) — The open-source semantic cache for LLM responses; study its modular embedding/similarity design.

## Stretch ideas

- Implement cache-aware routing: direct requests to the server most likely to hold their prefix (consistent hashing on the prompt prefix).
- Combine prompt caching with speculative decoding and measure the compounded latency win.
