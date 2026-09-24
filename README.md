# Build Your Own Everything

**Master programming by re-creating your favorite technologies from scratch.**

> *"What I cannot create, I do not understand." — Richard Feynman*

This repository is a hands-on collection for people who want to truly understand how software works: not by reading about it, but by building working versions of it with their own hands. It ships with **12 original, fully tested step-by-step guides** (Python, stdlib only — no dependencies) covering Git internals, HTTP servers, Redis, shells, regex engines, JSON parsers, Lisp interpreters, blockchains, template engines, DNS servers, static site generators, and load balancers — plus **200 topic learning paths** that explain what each technology is, how it works inside, and the concrete milestones to build it yourself — plus a **curated index of the best build-from-scratch tutorials** on the internet.

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](LICENSE)
[![CI](https://github.com/ozrehan/build-your-own-everything/actions/workflows/ci.yml/badge.svg)](https://github.com/ozrehan/build-your-own-everything/actions/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## Contents

- [Original Guides](#original-guides)
- [Learning Paths](#learning-paths)
- [Curated Tutorials](#curated-tutorials)
  - [Databases](#databases)
  - [Web Servers & Networking](#web-servers--networking)
  - [Programming Languages & Runtimes](#programming-languages--runtimes)
  - [DevOps & Infrastructure](#devops--infrastructure)
  - [Operating Systems](#operating-systems)
  - [Security & Cryptography](#security--cryptography)
  - [AI & Machine Learning](#ai--machine-learning)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

---

## Original Guides

Each guide is a complete, self-contained tutorial in `guides/<slug>/` with a clean commented solution (Python stdlib only) and a test suite you can run with `python3 test_*.py`.

| Guide | What you'll build |
|---|---|
| [Git](guides/git/) | A tiny Git: objects, trees, commits, `init`/`log` |
| [Web Server](guides/web-server/) | A raw-socket HTTP/1.1 static file server |
| [Redis](guides/redis/) | A RESP-speaking Redis clone with expiry |
| [Shell](guides/shell/) | A Unix shell: parsing, `fork`/`exec`, pipes, redirection |
| [Regex Engine](guides/regex-engine/) | A regex parser/matcher: quantifiers, alternation, groups, anchors, classes |
| [JSON Parser](guides/json-parser/) | A strict JSON parser and serializer |
| [Lisp Interpreter](guides/lisp-interpreter/) | Tokenizer, parser, evaluator, closures, recursion, REPL |
| [Blockchain](guides/blockchain/) | SHA-256 blocks, proof of work, chain validation |
| [Template Engine](guides/template-engine/) | Jinja-style variables, `if`, loops, comments |
| [DNS Server](guides/dns-server/) | An authoritative UDP DNS server with A records and NXDOMAIN |
| [Static Site Generator](guides/static-site-generator/) | Markdown rendering, layouts, index generation |
| [Load Balancer](guides/load-balancer/) | A round-robin HTTP reverse proxy |

Run any guide's tests, for example:

```bash
cd guides/git && python3 test_mygit.py
```

---

## Learning Paths

Beyond the full code guides above, [`topics/`](topics/) holds **200 bite-sized learning paths** — one per technology. Each path explains the core concepts for real, how the thing works inside, and an ordered set of build milestones from an evening-sized MVP to an impressive end state, plus verified resources and stretch ideas. Browse them all in the [Topics Index](topics/INDEX.md).

| Category | Topics | Examples |
|---|---|---|
| Programming Languages | 20 | [Tree-Walking Interpreter](topics/tree-walking-interpreter/), [Bytecode VM](topics/bytecode-virtual-machine/), [Mark-and-Sweep GC](topics/mark-sweep-garbage-collector/) |
| Databases | 20 | [B-Tree Index](topics/b-tree-index/), [LSM-Tree Storage](topics/lsm-tree-storage/), [Raft Consensus](topics/raft-consensus/) |
| Networking | 20 | [Userspace TCP/IP Stack](topics/tcp-ip-stack-userspace/), [QUIC Basics](topics/quic-basics/), [WebSocket Server](topics/websocket-server/) |
| Operating Systems | 20 | [Bootloader](topics/bootloader/), [Minimal Kernel](topics/minimal-kernel/), [Virtual Memory & Paging](topics/virtual-memory-paging/) |
| Web Development | 20 | [JavaScript Bundler](topics/js-bundler/), [OAuth2 Provider](topics/oauth2-provider/), [GraphQL Server](topics/graphql-server/) |
| DevOps & Infrastructure | 20 | [CI Runner](topics/ci-runner/), [Mini Terraform](topics/iac-mini-terraform/), [Distributed Tracer](topics/distributed-tracer/) |
| Security | 20 | [Password Hashing](topics/password-hashing/), [TLS Handshake](topics/tls-handshake/), [TOTP 2FA](topics/totp-2fa/) |
| AI & Machine Learning | 20 | [Neural Net from Scratch](topics/neural-net-from-scratch/), [Transformer from Scratch](topics/transformer-from-scratch/), [RAG Pipeline](topics/rag-pipeline/) |
| Games & Graphics | 20 | [Ray Tracer](topics/ray-tracer/), [Chess Engine](topics/chess-engine/), [CHIP-8 Emulator](topics/chip8-emulator/) |
| Distributed Systems & Data | 20 | [Mini MapReduce](topics/mapreduce-mini/), [Kademlia DHT](topics/dht-kademlia/), [CRDT Collaborative Text](topics/crdt-collaborative-text/) |

---

## Curated Tutorials

The best build-it-yourself tutorials from across the web, verified and organized by topic. A great starting point for further reading after finishing the original guides is the canonical mega-list: [**Build Your Own X**](https://github.com/codecrafters-io/build-your-own-x) by CodeCrafters.

### Databases

- **C**: [_Let's Build a Simple Database_](https://cstack.github.io/db_tutorial/parts/part2.html) — write a SQLite clone from scratch, part by part.
- **C**: [_Write a Hash Table_](https://github.com/jamesroutley/write-a-hash-table) — open-addressed, double-hashed hash table in ~200 lines.
- **Python**: [_Build Your Own Redis_](https://github.com/learnwithparam/build-your-own-redis-python) — 10 incremental steps: TCP echo → RESP → KV store → expiry → AOF → RDB → pub/sub → replication → event loop → benchmarks.
- **Go/Python**: [_Search Engine from Scratch — Part 1: The Inverted Index_](https://dev.to/mabd_dev/search-engine-from-scratch-part-1-the-inverted-index-243n) — tokenization, inverted indexes, and query ranking in a multi-part series.
- **Multiple**: [_500 Lines or Less_](https://github.com/aosabook/500lines) — the Architecture of Open Source Applications series: each chapter builds a real system (spreadsheet, web server, DB) in ≤500 lines.

### Web Servers & Networking

- **C**: [_Beej's Guide to Network Programming_](http://beej.us/guide/bgnet/) — the classic sockets tutorial; everything you need to speak TCP/IP in C.
- **C**: [_Let's Code a TCP/IP Stack_](http://www.saminiir.com/lets-code-tcp-ip-stack-1-ethernet-arp/) — implement Ethernet, ARP, IP, ICMP, UDP, and TCP on a virtual TAP device.
- **Python**: [_Implement DNS in a Weekend_](https://implement-dns.wizardzines.com/) — Julia Evans' guide to writing a real DNS resolver with `struct` and `socket`.
- **C**: [_FFmpeg and SDL Tutorial_](http://dranger.com/ffmpeg/ffmpegtutorial_all.html) — decode and play video by building a movie player on FFmpeg.

### Programming Languages & Runtimes

- **C**: [_Build Your Own Lisp_](https://buildyourownlisp.com/) — write a complete Lisp interpreter in C, from parsing to evaluation.
- **Python**: [_Let's Build a Simple Interpreter_](https://ruslanspivak.com/lsbasi-part1/) — Ruslan Spivak's multi-part series on building an interpreter from tokens to a full language.
- **Java/C**: [_Crafting Interpreters_](https://craftinginterpreters.com/) — Robert Nystrom's free book: a tree-walking interpreter (Java) and a bytecode VM (C) for the Lox language.
- **Haskell**: [_Write Yourself a Scheme in 48 Hours_](http://en.wikibooks.org/wiki/Write_Yourself_a_Scheme_in_48_Hours) — a Scheme interpreter in Haskell, from parser combinators to a REPL.
- **Python**: [_Write Yourself a Git_](https://wyag.thb.lt/) — reimplement Git's core commands (the "stupid content tracker") in Python.
- **C**: [_Build Your Own Text Editor_](https://viewsourcecode.org/snaptoken/kilo/01.setup.html) — the famous Kilo tutorial: a full terminal text editor in ~1000 lines of C.
- **JavaScript**: [_Build Your Own React_](https://pomb.us/build-your-own-react/) — Rodrigo Pombo's step-by-step React clone: createElement, fibers, reconciliation, hooks.
- **C**: [_Regular Expression Matching Can Be Simple And Fast_](https://swtch.com/~rsc/regexp/regexp1.html) — Russ Cox on Thompson NFA regex engines and why backtracking is slow.
- **C**: [_A Quick Tutorial on Implementing Malloc_](http://danluu.com/malloc-tutorial/) — Dan Luu's guide to writing `malloc`, `free`, `calloc`, and `realloc` on `sbrk`.

### DevOps & Infrastructure

- **Bash**: [_Bocker_](https://github.com/p8952/bocker) — Docker implemented in ~100 lines of Bash using namespaces, cgroups, and chroot.

### Operating Systems

- **Rust**: [_Writing an OS in Rust_](https://os.phil-opp.com/minimal-rust-kernel/) — Philipp Oppermann's series: boot a minimal 64-bit kernel and grow it into a real OS.
- **C/Assembly**: [_The Little Book About OS Development_](http://littleosbook.github.io/) — write a small x86 kernel: bootloader, paging, interrupts, and a basic shell.

### Security & Cryptography

- **Python**: [_Learn Blockchains by Building One_](https://hackernoon.com/learn-blockchains-by-building-one-117428612f46) — a minimal blockchain with mining, consensus, and transactions in ~50 lines.

### AI & Machine Learning

- **Python**: [_Let's build GPT: from scratch, in code_](https://www.youtube.com/watch?v=kCc8FmEb1nY) `[video]` — Andrej Karpathy codes a GPT from first principles: tokenization, attention, training.
- **Python**: [_GPT-2 from Scratch_](https://github.com/faiz61636/gpt2-from-scratch) — rebuild GPT-2's transformer architecture step by step in PyTorch-style Python.

> Found a great build-from-scratch tutorial that's missing? See [Contributing](#contributing).

---

## Contributing

Contributions are welcome! You can:

1. **Add a tutorial link** to the curated index above (one line, check the link works, put the best guides first).
2. **Add an original guide** to `guides/<slug>/` — a README tutorial, a clean stdlib-only solution, and a passing test suite.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide format and link conventions.

## Code of Conduct

Be kind, be constructive. Read the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is dedicated to the public domain under [CC0 1.0 Universal](LICENSE). Build anything with it.
