---
title: "Rate Limiter"
category: "networking"
difficulty: "beginner"
tags: [rate-limiting, api, algorithms]
related: [tcp-load-balancer, cdn-edge-cache, status-page]
---

# Rate Limiter

A rate limiter decides who gets served and who gets a `429 Too Many Requests` — it's what keeps one abusive client from taking down your API. The classic algorithms (token bucket, leaky bucket, sliding window) are small, beautiful, and directly reusable, making this the highest concepts-per-line project on the list.

## Core concepts

- **Why limit** — Rate limiting protects shared resources from abuse, accidents, and cost explosions; it's also how APIs tier free vs paid usage. The policy is a product decision; the algorithm is engineering.
- **Token bucket** — Tokens refill at a fixed rate into a bucket of capacity N; each request spends one. Bursts up to N are allowed, sustained rate is capped. The most widely deployed algorithm (and the most intuitive).
- **Leaky bucket** — Requests enter a queue that drains at a fixed rate; overflow is rejected. Smooths bursts into a steady flow — great for protecting downstream systems that can't handle spikes.
- **Fixed vs sliding window** — Counting requests per fixed minute has a boundary flaw (2× the limit across a boundary); a sliding window log or sliding-window counter fixes it at the cost of more state.
- **Limiting keys** — Limits apply per API key, per IP, per user, or per endpoint — choosing the key is choosing what "fair" means, and getting it wrong punishes everyone behind one NAT.
- **Headers and 429s** — Good limiters tell clients the rules: `X-RateLimit-Limit/Remaining/Reset` and `Retry-After` on `429`. Clients that can read these back off gracefully instead of hammering.
- **Distributed limiting** — One process can count in memory; a fleet needs shared state (Redis `INCR` with TTL, or Redis Cell's `CL.THROTTLE`). Clock skew and race conditions make exactness expensive — most systems accept approximate.

## How it works

Each request is mapped to a limiting key; the limiter looks up that key's bucket state (tokens, timestamps, or counters), applies the algorithm's math against the current time, and either allows the request (updating state) or rejects it with 429 plus `Retry-After`. State lives in memory for a single instance or in Redis for a fleet; a middleware wrapper applies the check to every request before it reaches your handlers, and response headers advertise the client's remaining quota.

## Build milestones

1. Implement a token bucket in memory as HTTP middleware: allow bursts, enforce sustained rate, return 429 with `Retry-After`.
2. Add a leaky bucket variant and a sliding-window counter; compare their burst behavior under a simulated traffic spike.
3. Support multiple limiting keys (per API key, per IP, per route) with different policies each.
4. Move state to Redis for a distributed limiter and test correctness with two instances hammering the same key.
5. Emit proper `X-RateLimit-*` headers and build a small dashboard showing rejection rates per key.

## Best resources

- [Redis rate limiting patterns](https://redis.io/docs/manual/patterns/rate-limiter/) — the canonical INCR+TTL patterns and their tradeoffs, straight from the Redis docs.
- [Stripe: Rate limiters](https://stripe.com/blog/rate-limiters) — how Stripe built distributed rate limiting; the best real-world design writeup.
- [Cloudflare: Rate limiting](https://www.cloudflare.com/learning/bots/how-rate-limiting-works/) — what limiting looks like at CDN scale, including per-IP vs per-key thinking.
- [IETF RateLimit header fields (draft)](https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-08.html) — the standardizing `RateLimit-*` response headers; implement these.

## Stretch ideas

- Implement the GCRA (Generic Cell Rate Algorithm) — the theoretically cleanest limiter — and prove it equivalent to a token bucket.
- Add adaptive limiting that tightens automatically when backend latency degrades (AIMD-style, like TCP congestion control).
