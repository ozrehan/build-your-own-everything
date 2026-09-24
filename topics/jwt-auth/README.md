---
title: "JWT Authentication"
category: "web-development"
difficulty: "beginner"
tags: [jwt, auth, tokens]
related: [oauth2-provider, password-hashing, totp-2fa, rest-api-client]
---

# JWT Authentication

JSON Web Tokens are signed, self-contained credentials: the server issues a token after login, and the client sends it with each request so the server can verify identity without a session lookup. Building JWT auth yourself — signing, verification, refresh rotation — teaches stateless authentication, its real trade-offs versus sessions, and the classic mistakes (like trusting the `alg` header).

## Core concepts

- **Token structure: header.payload.signature** — Three base64url segments: the header names the algorithm, the payload carries claims, and the signature is HMAC/RSA over the first two, so tampering is detectable.
- **Claims** — Standard fields like `sub` (user id), `exp` (expiry), `iat` (issued at), and `iss` (issuer); application claims like `role` go in the same payload.
- **Stateless verification** — The server verifies the signature with its key and trusts the claims — no database lookup — which is why JWTs scale horizontally but can't be individually revoked without extra state.
- **Access vs refresh tokens** — Short-lived access tokens (minutes) sent with API calls; long-lived refresh tokens (days) stored securely and used only to mint new access tokens, limiting the blast radius of a leak.
- **Storage: httpOnly cookies vs localStorage** — Cookies with `HttpOnly`/`Secure`/`SameSite` resist XSS theft but need CSRF protection; localStorage is CSRF-immune but any XSS can steal the token.
- **The `alg: none` attack** — A historic vulnerability class where verifiers accepted attacker-chosen algorithms; always pin the expected algorithm and never trust the token's own `alg` header.
- **Key management and rotation** — Signing keys must be strong secrets (or RSA key pairs with `kid` headers); rotation means accepting old keys briefly while issuing with the new one.
- **Revocation strategies** — True stateless JWTs can't be revoked; practical systems use short expiries plus a denylist, token versioning (`jti` + stored version), or refresh-token rotation to detect theft.

## How it works

1. User logs in with credentials; the server verifies the password hash and issues a short-lived access JWT and a refresh token.
2. The client stores them (httpOnly cookie or memory) and sends the access token as `Authorization: Bearer <token>` on API calls.
3. The server's auth middleware verifies the signature, checks `exp`/issuer/audience, and attaches the user to the request — no session store hit.
4. When the access token expires, the client calls the refresh endpoint; the server validates the refresh token (rotating it) and issues a new pair.

## Build milestones

1. Hand-roll HS256 JWT creation/verification (base64url + HMAC, no library) with `exp` checking — the core in an evening.
2. Add login/register with bcrypt password hashing, issuing access + refresh tokens.
3. Add auth middleware protecting routes, role claims, and token refresh with rotation.
4. Add logout/revocation via a `jti` denylist (Redis or in-memory) and demonstrate the stateless trade-off.
5. Graduate to RS256 with key rotation via `kid`, and httpOnly cookie transport with CSRF tokens.

## Best resources

- [RFC 7519 — JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519) — the short, readable spec defining claims and structure.
- [jwt.io](https://jwt.io/) — paste a token to inspect it; the debugger and library list make the format click instantly.
- [jose — JavaScript JOSE library](https://github.com/panva/jose) — the reference implementation to study (and use) once your hand-rolled version works.
- [MDN — HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) — the `HttpOnly`/`Secure`/`SameSite` attributes that decide how safely you can store tokens.
- [OWASP — JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) — the security checklist: algorithm pinning, expiry, key storage.

## Stretch ideas

- Implement sliding sessions with refresh-token reuse detection (alarm on token replay).
- Add a JWKS endpoint so multiple services can verify tokens with your public keys.
