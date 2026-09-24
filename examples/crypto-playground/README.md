# Example: Security — Crypto Playground

**[▶ Try it live](https://byoe-crypto.netlify.app)**

The primitives inside every login system, run locally in your browser:
**password hashing with salt** (SHA-256), **classical ciphers** (Caesar, Vigenère),
and a **brute-force cracker**.

Example project for the [security learning path](../../topics/password-hashing/).

## What it teaches

| Tab | Concept |
|---|---|
| Password hashing | same password + different salt → different hash; why rainbow tables fail |
| Ciphers | substitution, key spaces, encrypt/decrypt symmetry |
| Crack it | brute-forcing all 25 Caesar shifts — then compare with AES-256's 2²⁵⁶ keys |

## Exercises

1. Implement **bcrypt-style key stretching**: hash 10,000 rounds and feel the slowness.
2. Add a **frequency-analysis** cracker that breaks Caesar without brute force.
3. Build a **Diffie-Hellman key exchange** demo (see the `tls-handshake` topic).
