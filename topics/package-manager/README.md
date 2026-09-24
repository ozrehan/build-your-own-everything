---
title: "Build Your Own Package Manager"
category: "programming-languages"
difficulty: "intermediate"
tags: [developer-tools, systems, networking]
related: [linker, transpiler, repl-design]
---

# Build Your Own Package Manager

A package manager is a dependency solver with a network client: it reads version constraints, finds a set of package versions that satisfy them all, downloads the artifacts, and lays them out reproducibly. npm, Cargo, and pip all share this architecture, and the hard part — version solving — is a beautiful search problem that PubGrub solved elegantly. Building a miniature one teaches you lockfiles, registries, and why installs sometimes fail with inscrutable errors.

## Core concepts

- **Manifests and version constraints** — `package.json` and `Cargo.toml` declare dependencies as ranges (`^1.2`, `>=2.0,<3`); semantic versioning gives those ranges meaning.
- **Version solving** — finding mutually compatible versions is NP-complete in general; PubGrub-style conflict-driven search with backjumping solves real cases fast and explains failures clearly.
- **Lockfiles** — the solver's output pinned to exact versions plus content hashes; installing from a lockfile is deterministic, which is what makes CI reproducible.
- **The registry protocol** — package metadata (versions, dependencies, tarball URLs, hashes) is fetched over HTTP; integrity is verified by hash before unpacking.
- **Layout and isolation** — where packages live (`node_modules` nesting vs. Cargo's shared store) determines duplication and phantom-dependency behavior.
- **Caching and offline use** — a content-addressed cache makes repeat installs instant and lets builds work offline; invalidation is by hash, not by time.

## How it works

The client parses the manifest into a root dependency list, then asks the registry for each package's metadata: available versions, each version's dependencies, and tarball hashes. The solver — unit propagation over incompatibilities, decision making on the most constrained package, conflict learning when a dead end appears — searches for one version per package satisfying every constraint, producing either a solution or a human-readable explanation of the conflict. The solution is written to a lockfile with exact versions and hashes; then tarballs download into a content-addressed cache, hashes are verified, and packages unpack into the install layout with receipts recording what went where.

## Build milestones

1. Define a manifest format and a fake local registry (a directory of versioned tarballs with metadata); implement installing exact versions with hash verification.
2. Add semver range parsing and a naive backtracking solver; watch it explode on a diamond dependency, then fix it.
3. Implement PubGrub-style solving — incompatibilities, unit propagation, decision making — following Weizenbaum's article; produce readable conflict explanations.
4. Add lockfile generation plus a `ci`-style deterministic install from the lockfile, backed by a content-addressed download cache.
5. Build a real network registry client: fetch metadata over HTTP with retries and timeouts, support `update` vs. locked installs, and publish a package to your fake registry.

## Best resources

- [npm CLI documentation](https://docs.npmjs.com/cli/v11/commands/npm/) — the reference for npm's commands, config, and how the registry client behaves.
- [package.json reference](https://github.com/npm/cli/blob/HEAD/docs/lib/content/configuring-npm/package-json.md) — the manifest format: dependency ranges, overrides, and publishing fields.
- [The Cargo Book](https://github.com/rust-lang/cargo/blob/HEAD/doc/book/src/index.md) — Cargo's documentation: manifests, lockfiles, workspaces, and the publish workflow done well.
- [cargo man page](https://github.com/rust-lang/cargo/blob/HEAD/doc/man/cargo.md) — the command reference showing what surface a mature package manager exposes.
- [PubGrub: Next-Generation Version Solving](https://nex3.medium.com/pubgrub-2fb6470504f) — Natalie Weizenbaum's article explaining conflict-driven version solving with worked examples.
- [PubGrub solver spec walkthrough](https://github.com/dsimunic/elm-wrap/blob/HEAD/doc/pubgrub-solver-spec.md) — a step-by-step trace of the PubGrub algorithm resolving a real dependency conflict.

## Stretch ideas

- Add vulnerability auditing: match locked versions against an advisory database and suggest minimal upgrades.
- Implement workspace/monorepo support with local path dependencies.
- Build `why` and `tree` commands that explain how each package entered the dependency graph.
