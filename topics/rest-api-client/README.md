---
title: "REST API Client"
category: "web-development"
difficulty: "beginner"
tags: [rest, http, client]
related: [jwt-auth, oauth2-provider, http-protocol-deep-dive, form-validation-library]
---

# REST API Client

A REST API client is a wrapper around HTTP that turns endpoints into typed functions with retries, auth headers, caching, and sane error handling. Building one teaches HTTP semantics (methods, status codes, idempotency), the interceptor pattern, and every resilience feature — timeouts, retries with backoff, pagination — that raw `fetch` leaves to you.

## Core concepts

- **Resource-oriented design** — URLs name resources (`/users/42/orders`), HTTP methods name operations (GET/POST/PUT/PATCH/DELETE); a good client maps these to methods like `client.users.get(42)`.
- **Interceptors** — Middleware that runs on every request/response: attach auth tokens, log, transform errors — the extension point that makes one client serve a whole app.
- **Timeouts and AbortController** — Every request needs a deadline; `AbortController` cancels in-flight requests (route changes, debounced search) so stale responses never win.
- **Retries with backoff** — Transient failures (429, 503, network blips) deserve retries with exponential backoff and jitter; non-idempotent POSTs need idempotency keys before they're safe to retry.
- **Error taxonomy** — Distinguish network errors, timeouts, 4xx (client's fault — don't retry), and 5xx (maybe retry); normalize them into one error type with status, body, and retryability.
- **Pagination strategies** — Offset/limit, cursor-based, and Link-header pagination each need different client iteration helpers; cursor pagination is the robust default.
- **Caching and deduplication** — GET responses cached by URL+params with TTLs, and concurrent identical requests deduplicated into one flight — the two features that cut API load dramatically.
- **Request/response transforms** — camelCase↔snake_case key conversion, date-string→Date parsing, and envelope unwrapping (`{ data: ... }`) keep API quirks out of app code.

## How it works

1. You define a client with a base URL and default headers; resource methods build URLs and call a core `request()` function.
2. `request()` runs request interceptors, performs `fetch` with timeout/abort, then runs response interceptors.
3. Failures go through the retry policy (backoff for retryable statuses, immediate throw for 4xx) and are normalized into typed errors.
4. GETs check the cache/dedup layer first; paginated helpers iterate pages behind an async-generator interface.

## Build milestones

1. A thin `fetch` wrapper with base URL, JSON handling, and typed errors — useful in an evening.
2. Add interceptors (auth header injection, logging), timeouts via AbortController, and request cancellation.
3. Add retries with exponential backoff + jitter, honoring `Retry-After`, and an idempotency-key option for POSTs.
4. Add a GET cache with TTL and stale-while-revalidate, plus in-flight request deduplication.
5. Add pagination helpers (cursor + offset), key-case transforms, and auto-refresh of expired auth tokens on 401.

## Best resources

- [Fetch API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API) — the underlying primitive: Request, Response, Headers, AbortController.
- [Axios docs](https://axios-http.com/docs/intro) — the reference API-client design: instances, interceptors, cancellation, transforms.
- [ky on GitHub](https://github.com/sindresorhus/ky) — a tiny, elegant fetch wrapper; excellent source to study for hooks and retry design.
- [undici on GitHub](https://github.com/nodejs/undici) — Node's HTTP client internals: pooling, pipelining, and why connection reuse matters.
- [REST API Tutorial — HTTP methods](https://restfulapi.net/http-methods/) — a clear reference for method semantics and idempotency.

## Stretch ideas

- Generate the client from an OpenAPI spec, including TypeScript types.
- Add offline request queueing with replay, like a service worker for mutations.
