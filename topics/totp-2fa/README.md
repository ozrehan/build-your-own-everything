---
title: "TOTP Two-Factor Auth"
category: "security"
difficulty: "beginner"
tags: [authentication, mfa, otp]
related: [password-hashing, jwt-auth, oauth2-provider]
---

# TOTP Two-Factor Auth

TOTP is the six-digit code in your authenticator app that changes every 30 seconds. Building your own generator and verifier teaches you how time-based one-time passwords work under the hood — and why a second factor defeats the vast majority of password-based attacks even when the password itself is stolen.

## Core concepts

- **Shared secret** — A random key exchanged once (via QR code) between server and authenticator app; both sides use it to independently compute the same code, so it must be stored securely server-side.
- **Time steps** — The current Unix time divided into 30-second windows; the code is a function of the secret and the window number, which is why both devices need roughly accurate clocks.
- **HMAC-based OTP (HOTP)** — The underlying primitive from RFC 4226: HMAC-SHA1 of a counter with the secret, truncated to 6–8 digits; TOTP just replaces the counter with a time step.
- **Clock skew tolerance** — Accepting the previous and next time window as well as the current one, so users with slightly drifting clocks aren't locked out (at the cost of a slightly larger attack window).
- **Replay protection** — A code is valid for its window, so the server should reject a code that was already used within that window to stop simple replay.
- **Backup codes** — One-time recovery codes issued at enrollment for when the device is lost; they must be hashed like passwords, since each one is a full authentication bypass.
- **Why not SMS** — SMS codes can be intercepted via SIM swapping and SS7 attacks; TOTP's offline computation has no network path for an attacker to intercept.

## How it works

At enrollment, the server generates a random secret, stores it encrypted, and shows it to the user as a QR code (an `otpauth://` URI). The authenticator app scans it and starts computing: for each 30-second window, it takes the window number as an 8-byte counter, computes HMAC-SHA1 with the secret, then truncates the 20-byte result to 6 digits via the RFC's dynamic truncation (take the last nibble as an offset, grab 4 bytes, mod 10^6).

When the user logs in, they type the current code; the server runs the same computation for the current window (plus one window of skew each way) and compares. No network call, no SMS — just synchronized math. Your first build can be a 50-line script that generates codes from a secret and verifies them, which demystifies the whole "magic number" experience.

## Build milestones

1. Write a TOTP generator: base32-decode a secret, compute HMAC-SHA1 over the time counter, apply dynamic truncation, and print the 6-digit code.
2. Verify your output matches Google Authenticator / any TOTP app for the same secret — the interop moment.
3. Build a verifier with configurable clock-skew tolerance and replay protection (remember used codes per window).
4. Add enrollment: generate secrets, render provisioning QR codes, and store secrets encrypted at rest.
5. Add hashed backup codes and an account-recovery flow that doesn't weaken the second factor.

## Best resources

- [RFC 6238 — TOTP: Time-Based One-Time Password Algorithm](https://www.rfc-editor.org/rfc/rfc6238) — The spec; short, precise, and directly implementable.
- [RFC 4226 — HOTP: HMAC-Based One-Time Password Algorithm](https://www.rfc-editor.org/rfc/rfc4226) — The counter-based foundation TOTP builds on, including the truncation algorithm.
- [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) — Practical guidance on deploying MFA: enrollment, recovery, and what to avoid.
- [Google Authenticator (open source)](https://github.com/google/google-authenticator) — Reference implementations and the PAM module; useful for cross-checking your codes.

## Stretch ideas

- Implement WebAuthn/FIDO2 passkeys next and compare the UX and phishing-resistance against TOTP in a write-up.
- Build a small admin dashboard showing MFA adoption rates and failed second-factor attempts over time.
