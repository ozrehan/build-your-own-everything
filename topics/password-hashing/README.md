---
title: "Password Hashing"
category: "security"
difficulty: "intermediate"
tags: [cryptography, authentication, key-derivation]
related: [totp-2fa, secrets-vault, jwt-auth]
---

# Password Hashing

Storing passwords means never storing the password itself — you store a one-way hash that can verify a login without ever being reversible. Building your own password hasher teaches the difference between a hash, a salt, and a real password key-derivation function, and why "just SHA-256 it" is a breach waiting to happen.

## Core concepts

- **Cryptographic salt** — A unique random value mixed into each password before hashing, so identical passwords produce different hashes and precomputed rainbow tables become useless.
- **Key stretching / work factor** — Deliberately making hashing slow (thousands of iterations or megabytes of memory) so that an attacker who steals the database can only try a few guesses per second, while a real login barely notices the delay.
- **Memory-hard functions** — Algorithms like Argon2 and scrypt that force attackers to use large amounts of RAM per guess, which defeats GPU and ASIC cracking rigs that excel at parallel cheap computation.
- **Rainbow tables** — Giant precomputed tables mapping hashes back to common passwords; salts killed them, and work factors make the tables too expensive to build for each salt anyway.
- **Pepper** — An additional secret value stored separately from the database (e.g., in app config or an HSM); if only the database leaks, peppered hashes stay safe even against offline cracking.
- **Adaptive hashing** — Designing the scheme so the work factor can be raised over time as hardware gets faster, and re-hashing users transparently on their next login.
- **Timing-safe comparison** — Comparing hashes with constant-time functions so attackers cannot guess a hash byte-by-byte by measuring how long a comparison takes.

## How it works

When a user registers, you generate a random salt (16+ bytes), run the password through a key-derivation function like Argon2id with a chosen work factor, and store the salt, parameters, and resulting hash in one encoded string (e.g., the PHC string format). At login you re-run the same function with the stored salt and compare the result in constant time.

The security comes from asymmetry: verifying one password takes ~100ms of server CPU and a chunk of memory — trivial for a login flow, but it caps an offline attacker who stole your database at roughly ten guesses per second per core. Fast hashes like SHA-256 or MD5, in contrast, let that same attacker try billions of guesses per second on a single GPU, which is why they must never be used for passwords no matter how many times you iterate them.

## Build milestones

1. Build a registration/login demo that hashes with SHA-256 and a fixed salt — then crack it yourself with a wordlist to see exactly why it fails.
2. Add per-user random salts and store salt, iterations, and hash in a standard encoded format; verify with constant-time comparison.
3. Swap the primitive for a real KDF: use bcrypt (via a library) with a tunable cost factor, and benchmark login latency vs. cost.
4. Implement parameter upgrade: on successful login, detect outdated parameters and transparently re-hash with stronger ones.
5. Add pepper support loaded from an environment variable, plus a pepper-rotation path that re-hashes on login.

## Best resources

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) — The definitive current guidance on algorithms, parameters, and migration; start here.
- [NIST SP 800-63B Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html) — The federal standard for authentication, covering memorized secrets, verifiers, and throttling.
- [Password Hashing Competition](https://www.password-hashing.net/) — The competition that selected Argon2; explains why memory-hardness won.
- [Argon2 RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html) — The formal spec for Argon2, the current best-practice password hash.
- [scrypt paper by Colin Percival](https://www.tarsnap.com/scrypt/scrypt.pdf) — The original paper on memory-hard KDFs and why ASIC resistance matters.
- [bcrypt and the OpenBSD crypt scheme](https://www.openwall.com/crypt/) — Background on bcrypt, the adaptive hash that dominated password storage for two decades.

## Stretch ideas

- Build a tiny offline cracker (wordlist + rules) and benchmark guesses/sec against your own hashes at different work factors to feel the cost asymmetry.
- Implement a migration tool that upgrades a legacy MD5/SHA-1 password database to Argon2id without forcing a password reset.
