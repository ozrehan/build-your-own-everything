---
title: "Secret Scanner"
category: "security"
difficulty: "beginner"
tags: [git, credentials, devsecops]
related: [git-server, secrets-vault, audit-logger]
---

# Secret Scanner

A secret scanner hunts through code and git history for accidentally committed credentials — API keys, tokens, private keys — before attackers find them. Building one teaches you how secrets leak, why "I deleted it from the repo" doesn't work, and how detection fits into a safe development workflow.

## Core concepts

- **Entropy analysis** — Random-looking strings (long, high Shannon entropy, mixed character sets) are strong signals of keys and tokens, even without knowing the exact format.
- **Pattern matching** — Regexes for known secret formats (`AKIA...` AWS keys, `ghp_...` GitHub tokens, PEM headers); precise but must be updated as providers change formats.
- **Git history is forever** — Deleting a secret from the working tree doesn't remove it from history; anyone who cloned the repo still has it, which is why leaked secrets must be revoked, not just removed.
- **Pre-commit vs. CI scanning** — Pre-commit hooks catch secrets before they're committed; CI scans catch what slipped through and scan full history. You want both.
- **Allowlisting and baselines** — Test fixtures and fake keys trigger detectors; a usable scanner needs per-repo allowlists and a baseline so new findings stand out from known noise.
- **Remediation workflow** — The correct response to a finding is: revoke/rotate the credential first, then purge history (filter-repo/BFG), then add the pattern to prevention — in that order.
- **Provider partnerships** — Platforms like GitHub partner with secret issuers so that when a known-format token appears in a public repo, the issuer is notified automatically.

## How it works

A scanner like Gitleaks walks every commit in a repository (or staged changes, in pre-commit mode) and runs each file's contents through two engines: regex rules for known secret formats, and a generic entropy detector for anything that looks like a random token. Matches are reported with file, line, commit, and author — and critically, the scanner exits non-zero in CI so the pipeline fails.

Your first build can be a Python script that clones a test repo, iterates commits with pygit2 or git log, and flags lines matching a handful of regexes plus high-entropy strings. The lesson lands when you run it against a repo where you deliberately committed a fake key three commits ago and "deleted" it: the scanner still finds it, which is exactly why rotation matters more than deletion.

## Build milestones

1. Write a scanner that walks a repo's full history and flags lines matching regexes for 5 common secret formats (AWS keys, GitHub tokens, PEM blocks, Slack tokens, generic passwords in config).
2. Add entropy-based detection for unknown formats, with a minimum-length and charset heuristic to control noise.
3. Add a baseline/allowlist file so known test fixtures don't re-alert on every run.
4. Wire it as a pre-commit hook and a CI step that fails the build on new findings.
5. Build the remediation helper: given a finding, generate the exact commands to rotate the credential and purge it from history with git filter-repo.

## Best resources

- [Gitleaks](https://github.com/gitleaks/gitleaks) — Fast, configurable secret scanner; its default ruleset is a great study in pattern design.
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) — Scans git history plus verifies found secrets against live APIs to confirm they're real.
- [GitHub Secret Scanning docs](https://docs.github.com/en/code-security/secret-scanning) — How push protection and partner alerts work at platform scale.
- [Yelp detect-secrets](https://github.com/Yelp/detect-secrets) — Baseline-oriented scanner with pre-commit integration; good model for the baseline workflow.

## Stretch ideas

- Add live verification: for matched tokens, check validity against the provider's API (in a safe read-only way) to separate real leaks from test data.
- Build a secret-sprawl dashboard across all your repos showing findings by age, so old leaks get rotated first.
