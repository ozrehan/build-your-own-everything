---
title: "Security Headers Scanner"
category: "security"
difficulty: "beginner"
tags: [http, headers, web-security]
related: [waf-rules, vulnerability-scanner, http-protocol-deep-dive]
---

# Security Headers Scanner

HTTP security headers are one-line server configurations that switch on browser-side protections against XSS, clickjacking, and downgrade attacks. Building a scanner that grades any site's headers teaches you what each header actually does — and how many production sites ship without them.

## Core concepts

- **Content-Security-Policy (CSP)** — A whitelist of where scripts, styles, and other resources may load from; the single strongest mitigation against XSS when written strictly.
- **Strict-Transport-Security (HSTS)** — Tells browsers to only ever use HTTPS for this domain (for a declared period), defeating SSL-stripping downgrade attacks.
- **X-Frame-Options / frame-ancestors** — Controls whether the page can be embedded in an iframe, which is what stops clickjacking attacks.
- **X-Content-Type-Options: nosniff** — Stops browsers from "sniffing" a response's content type, blocking attacks that smuggle scripts inside innocent-looking files.
- **Referrer-Policy and Permissions-Policy** — Limit what information leaks in Referer headers and which powerful browser features (camera, geolocation) a page may use.
- **Cookie flags** — `Secure`, `HttpOnly`, and `SameSite` on Set-Cookie: respectively, HTTPS-only transmission, no JavaScript access, and CSRF protection.
- **Grading vs. reality** — A scanner grades what's observable, but headers interact: a strict CSP can compensate for missing X-XSS-Protection (which is deprecated anyway), so good scanners explain, not just score.

## How it works

The scanner is beautifully simple: make an HTTPS request to the target, read the response headers (and Set-Cookie flags), and evaluate each against a checklist. HSTS present with a long max-age and includeSubDomains? Good. CSP present but `unsafe-inline` allowed? Flag it as weak, and explain why. Missing X-Frame-Options and no frame-ancestors in CSP? Flag clickjacking risk.

Your first build can be a 100-line script that prints a per-header pass/warn/fail table. The learning happens when you run it against real sites: you'll find banks with no CSP, CDNs stripping headers, and redirect chains where the headers only exist on the final hop — each one a real-world lesson in how defense-in-depth fails at the seams.

## Build milestones

1. Write a scanner that fetches a URL's headers and reports presence/absence of the 8 core security headers with one-line explanations.
2. Add value analysis: parse CSP directives and flag `unsafe-inline`, `*`, and missing object-src; check HSTS max-age and includeSubDomains.
3. Add cookie analysis: parse Set-Cookie and flag missing Secure/HttpOnly/SameSite flags.
4. Follow redirect chains and report headers at each hop, flagging downgrades from HTTPS to HTTP.
5. Add grading (A+–F like securityheaders.com) with a remediation section generating the exact header values to add for each failure.

## Best resources

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/) — The reference for which headers to set and what values to use.
- [Content-Security-Policy — MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy) — The definitive CSP directive reference with examples.
- [securityheaders.com](https://securityheaders.com/) — Scott Helme's scanner; compare your grades against it to calibrate.
- [Mozilla Observatory](https://observatory.mozilla.org/) — Broader scanner covering headers, TLS, and more; good for seeing what a full assessment looks like.

## Stretch ideas

- Add CSP violation-report collection: an endpoint that receives browsers' violation reports and turns them into a dashboard of blocked attacks.
- Build a CSP generator: crawl your own site's resources and propose a strict nonce-based policy that doesn't break it.
