---
title: "Git Server"
category: "devops-infra"
difficulty: "intermediate"
tags: [git, server, version-control]
related: [ci-runner, secret-scanner, audit-logger]
---

# Git Server

GitHub is, at its core, a Git server with a nice UI: it speaks the Git wire protocols, stores bare repositories, and runs hooks on push. Building your own — HTTP smart protocol, SSH transport, auth, and push-triggered webhooks — teaches you how Git actually moves objects over the wire, what `git-receive-pack` does, and why hosting Git is mostly a solved protocol problem with an unsolved permissions problem.

## Core concepts

- **Bare repositories** — a repo with no working tree, just the `.git` contents (objects, refs). Servers store bare repos because there's nothing to check out; pushes update refs and add objects directly. `git init --bare` is the server's starting point.
- **Smart HTTP protocol** — the client GETs `/info/refs?service=git-upload-pack` for ref advertisement, then POSTs a "want/have" negotiation to `/git-upload-pack`. The server computes the minimal packfile of missing objects and streams it back. Stateless per request, which is why it load-balances trivially.
- **pkt-line framing** — Git's wire format: each line prefixed with a 4-hex-digit length. Both the ref advertisement and the pack negotiation are pkt-line streams; parsing them correctly is the first milestone of any Git server.
- **upload-pack vs receive-pack** — `git-upload-pack` serves fetches/clones (read path); `git-receive-pack` accepts pushes (write path). They share the negotiation machinery but the write path adds ref-update validation: fast-forward checks, hooks, and permissions.
- **Ref advertisement and negotiation** — the server lists all refs and their SHAs; the client replies with wants (objects it needs) and haves (objects it already has). The server walks the object graph to find the minimal set — this negotiation is what makes `git fetch` fast.
- **Hooks: pre-receive, update, post-receive** — scripts that run on push: validate (reject non-fast-forwards, enforce branch policies), then notify (trigger CI webhooks, update the UI). Hooks are the entire extensibility model of Git hosting.
- **Authentication and authorization** — HTTP Basic/token or SSH keys identify the user; per-repo ACLs decide read vs write. Git itself has no auth — the transport layer (your server) owns it entirely, which is why the SSH key management UX defines the product.

## How it works

Repositories live on disk as bare repos under a root directory. For HTTP, your server handles two endpoints per repo: `GET /<repo>/info/refs?service=git-upload-pack` runs `git-upload-pack --advertise-refs` semantics — or your own implementation — emitting the pkt-line ref advertisement with capabilities; `POST /<repo>/git-upload-pack` reads the client's want/have lines, computes the object set via graph traversal from the wants excluding haves, and streams a packfile response. For pushes, the receive-pack endpoint validates each ref update (old SHA must match current ref unless forced, enforced by policy), writes the new objects, updates refs atomically, then fires `post-receive` hooks.

SSH transport is simpler at the protocol level: the client runs `ssh git@host "git-upload-pack '/repo.git'"`, so your server just needs an SSH daemon that authenticates keys, maps the key to a user, checks repo permissions, and execs the pack command with stdio connected. A small management API handles repo creation, key registration, and ACLs; every push emits a webhook event (repo, ref, old/new SHA, pusher) that your CI runner consumes.

## Build milestones

1. Serve a bare repo over dumb HTTP (static files): `git clone http://localhost/repo.git` working from files your server serves. Then implement smart HTTP ref advertisement by shelling out to `git upload-pack`.
2. Write your own pkt-line parser and implement the want/have negotiation + packfile streaming without shelling out, for the fetch path.
3. Implement the push path: `git-receive-pack` handling with fast-forward validation, atomic ref updates, and `post-receive` hooks that POST a webhook payload.
4. Add SSH transport with key-based auth, per-repo read/write ACLs, a repo management API/UI, and wire push webhooks into your CI runner for end-to-end push-to-build.

## Best resources

- [Git HTTP transfer protocols](https://git-scm.com/docs/gitprotocol-http) — the smart/dumb HTTP protocol spec: ref discovery, negotiation, and packfile exchange. Your primary spec.
- [git-http-backend documentation](https://git-scm.com/docs/git-http-backend) — the reference CGI implementation; read it to understand the endpoint mapping and auth integration points.
- [Pro Git — Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) — packfiles, ref storage, and transfer internals; the object-model background your server needs.
- [Dulwich](https://www.dulwich.io/) — a pure-Python Git implementation including server-side protocol handling; the most readable real code for the wire protocol.
- [Gitea documentation](https://docs.gitea.com/) — the self-hosted Git platform: how repos, keys, hooks, and webhooks compose into a product; your feature checklist.
- [go-git](https://github.com/go-git/go-git) — pure-Go Git with pluggable transports; useful for embedding Git operations in your server without shelling out.

## Stretch ideas

- Implement protocol v2 (stateless, capability-advertised commands) for faster fetches on large repos.
- Add a pull-request model: refs under `refs/pull/N/head`, merge-base computation, and a merge API with conflict detection.
- Build a smart mirror: lazily fetch objects from upstream on demand so your server hosts thousands of forks without duplicating storage.
