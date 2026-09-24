---
title: "OAuth2 Provider"
category: "web-development"
difficulty: "advanced"
tags: [oauth2, security, identity]
related: [jwt-auth, password-hashing, totp-2fa, rest-api-client]
---

# OAuth2 Provider

An OAuth2 provider is the authorization server: it issues tokens that let third-party apps act on a user's behalf without ever seeing their password ("Log in with …"). Building the provider side — authorization endpoints, code exchange, token issuance — teaches the security model deeply, including exactly which attacks each parameter (state, PKCE, redirect validation) defends against.

## Core concepts

- **Roles: resource owner, client, authorization server, resource server** — The user owns the data, the client app wants access, your provider authenticates the user and issues tokens, and the resource server validates them.
- **Authorization code flow** — The secure core flow: user is redirected to the provider, approves scopes, and the client receives a one-time code that it exchanges (server-to-server, with its secret) for tokens.
- **PKCE** — Proof Key for Code Exchange: the client sends a hash of a random verifier with the authorization request and the verifier at token exchange, preventing code interception — required for public clients (SPAs, mobile).
- **Scopes** — Granular permissions (`read:profile`, `write:posts`) the user consents to; access tokens carry them and resource servers enforce them.
- **Redirect URI validation** — The provider must match the redirect URI exactly against pre-registered values; lax matching enables token theft via open redirectors.
- **Refresh tokens** — Long-lived credentials that mint new short-lived access tokens, stored securely server-side and rotated on use to detect theft.
- **State parameter** — A client-generated random value round-tripped through the authorization request to bind the callback to the original request and prevent CSRF login attacks.
- **OpenID Connect layer** — An identity layer on top of OAuth2: an `id_token` (JWT) with standardized claims (`sub`, `email`) plus a `userinfo` endpoint, which is what "Log in with Google" actually uses.

## How it works

1. The client redirects the user to `/authorize` with `client_id`, `redirect_uri`, `scope`, `state`, and PKCE challenge.
2. Your provider authenticates the user (its own login), shows a consent screen listing scopes, and redirects back with a short-lived authorization code.
3. The client POSTs the code to `/token` (with client secret and PKCE verifier); the provider validates everything and returns access + refresh tokens.
4. Resource servers validate access tokens (by introspection or JWT signature) and enforce scopes on each request.

## Build milestones

1. Client registration (store `client_id`, hashed secret, registered redirect URIs) and a `/authorize` endpoint that issues codes after a mock user login.
2. Add the `/token` endpoint: validate code, client auth, and PKCE verifier; issue signed access tokens and rotating refresh tokens.
3. Add a consent screen showing requested scopes, exact redirect-URI matching, and the `state` parameter round-trip.
4. Add token introspection/revocation endpoints and scope enforcement middleware for a sample resource server.
5. Layer OpenID Connect: `id_token` JWT issuance, `userinfo` endpoint, and discovery document (`/.well-known/openid-configuration`).

## Best resources

- [RFC 6749 — OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749) — the normative spec; dense but the flow diagrams are definitive.
- [OAuth 2.0 Simplified — Aaron Parecki](https://aaronparecki.com/oauth-2-simplified/) — the best plain-English guide to the flows, from an OAuth working-group contributor.
- [RFC 7636 — PKCE](https://datatracker.ietf.org/doc/html/rfc7636) — the short spec for the code-challenge mechanism every public client needs.
- [OAuth 2.0 Security Best Current Practice](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics) — the IETF's current guidance on what not to do (retire implicit flow, use PKCE, etc.).
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html) — the identity layer spec: ID tokens, claims, and the userinfo endpoint.

## Stretch ideas

- Implement the device authorization grant (TV/CLI login via user code) end to end.
- Add step-up authentication: require fresh MFA for high-risk scopes at the consent screen.
