---
title: "Certificate Authority"
category: "security"
difficulty: "advanced"
tags: [pki, x509, tls]
related: [tls-handshake, secrets-vault, oauth2-provider]
---

# Certificate Authority

A certificate authority is the trust anchor of the web: it signs certificates that bind a public key to a domain name, letting browsers trust millions of sites through a handful of roots. Running your own private CA teaches you exactly what those signatures mean, how chains validate, and why the whole system hinges on careful key custody.

## Core concepts

- **X.509 certificates** — The standard data format binding a subject (domain), public key, validity period, and extensions, all signed by an issuer; everything in web PKI is an X.509 cert.
- **Chain of trust** — Leaf cert → intermediate CA → root CA: clients verify each signature up the chain to a root they already trust, which is why intermediates exist (roots stay offline and rarely sign directly).
- **Certificate Signing Request (CSR)** — The applicant generates its own keypair and sends the CA only the public key plus identity info; the private key never leaves the applicant.
- **Root key custody** — The root private key is the crown jewel: kept offline, often in an HSM with multi-person ceremony, because its compromise invalidates every certificate beneath it.
- **Revocation (CRL/OCSP)** — Mechanisms for invalidating certificates before expiry; historically unreliable in browsers, which is why short-lived certificates (Let's Encrypt's 90 days) are now preferred.
- **Certificate Transparency** — Public append-only logs of every issued certificate, so domain owners can detect mis-issued certs for their domains — the accountability layer for CAs.
- **ACME protocol** — The automated protocol (RFC 8555) Let's Encrypt uses to prove domain control and issue certificates with zero human involvement.

## How it works

You start by generating a root keypair and self-signing a root certificate (a cert where issuer equals subject). To issue a server certificate, you create an intermediate CA: the root signs the intermediate's certificate, and the intermediate does the day-to-day signing so the root key can go back offline. A server generates its own keypair, sends you a CSR, and you sign a leaf certificate binding its public key to its hostname with a validity period and the right extensions (key usage, SANs).

Clients validate by walking the chain: check each signature, check expiry, check the hostname matches a Subject Alternative Name, check the chain ends at a trusted root, and (in modern setups) check Certificate Transparency logs. Building this with OpenSSL or a small Go program makes abstract PKI concepts — "what does 'trusted' even mean?" — completely concrete.

## Build milestones

1. Create a root CA with OpenSSL: self-signed root cert, then an intermediate signed by the root.
2. Issue a leaf certificate from a CSR for a local test domain, install it in a test web server, and trust your root in a test browser profile.
3. Write a chain validator that parses the certs and verifies signatures, expiry, and hostname matching by hand.
4. Build a tiny ACME-like auto-issuance flow: prove control of a test domain via an HTTP challenge, then issue and renew certs automatically.
5. Implement revocation: publish a CRL, run a mini OCSP responder, and verify clients reject a revoked cert.

## Best resources

- [RFC 5280 — Internet X.509 PKI Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280) — The definitive spec for certificate fields, chain validation, and revocation.
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/) — How automated issuance, ACME challenges, and short-lived certs work in production.
- [step-ca by smallstep](https://github.com/smallstep/certificates) — A clean open-source private CA in Go; the best codebase to study for real CA operations.
- [Mozilla CA Certificate Policy](https://www.mozilla.org/en-US/about/governance/policies/security-group/certs/policy/) — The rules a public CA must follow to stay in browser trust stores, including audit and incident requirements.

## Stretch ideas

- Add Certificate Transparency: submit your issued certs to a test CT log and build a monitor that alerts on certs issued for your domains.
- Implement mutual TLS (client certificates) for a service mesh-style setup where every service authenticates with its own cert.
