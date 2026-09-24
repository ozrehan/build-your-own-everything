---
title: "Test Runner Framework"
category: "web-development"
difficulty: "intermediate"
tags: [testing, runner, assertions]
related: [js-bundler, dev-server-hmr, fuzzer, ci-runner]
---

# Test Runner Framework

A test runner discovers test files, executes them in isolation, and reports pass/fail with useful diffs — the engine behind Jest, Vitest, and Mocha. Building a minimal one (file discovery, `describe`/`it`, assertions, mocking) teaches how test isolation, async handling, and module mocking actually work, and why test runners are secretly complex programs.

## Core concepts

- **Test discovery** — Globbing for `*.test.js` / `*.spec.js` files and loading them; the runner must distinguish test files from helpers without executing everything.
- **`describe`/`it` registration** — Test files don't run tests immediately; they register suites and cases into a tree during a collection phase, which the runner then executes — enabling `--only`, filtering, and ordering.
- **Isolation** — Each test file gets a fresh module registry (and often a fresh environment) so state doesn't leak between files; in-process isolation via module cache busting vs worker processes is a core design choice.
- **Async test handling** — Tests signal completion via returned promises, `done` callbacks, or async functions; the runner must await them and time out hangs.
- **Hooks** — `beforeEach`/`afterEach`/`beforeAll`/`afterAll` run around tests in nesting order; getting hook ordering and error propagation right is subtle.
- **Assertion library** — `expect(x).toBe(y)` with deep equality, pretty diffs on failure, and asymmetric matchers (`expect.any(Number)`) — the diff output is what makes failures debuggable.
- **Mocking and spies** — Replacing module functions or timers (`vi.fn()`, fake timers) so tests control dependencies and time; module mocking requires hooking the module loader.
- **Reporters and watch mode** — Output formats (spec, TAP, JSON) plus file-watching re-runs; watch mode needs dependency-graph-aware re-running of only affected tests.

## How it works

1. The CLI globs test files, loads each in an isolated context, and collects the `describe`/`it` tree without running test bodies.
2. The runner walks the tree: for each test it runs applicable `beforeEach` hooks, awaits the test function (promise-aware), runs `afterEach`, and captures assertion failures.
3. Failures are formatted with diffs and stack traces; results aggregate into a summary with exit code 0/1.
4. In watch mode, a file watcher maps changed files to affected tests via the import graph and re-runs only those.

## Build milestones

1. A CLI that loads `*.test.js` files and runs exported test functions with a tiny `assert` — passing/failing output in an evening.
2. Add `describe`/`it`/`beforeEach` with the collect-then-run two-phase architecture and nested suites.
3. Add async support (promise tests, timeouts), a real `expect` with deep equality and diff output.
4. Add per-file isolation (fresh module registry), simple function spies, and fake timers.
5. Add watch mode with dependency-graph-aware re-runs and a TAP reporter.

## Best resources

- [Jest docs](https://jestjs.io/docs/getting-started) — the reference test framework; its architecture docs explain the worker-based design.
- [Vitest docs](https://vitest.dev/) — the modern Vite-native runner; excellent docs on mocking, snapshots, and watch mode.
- [Mocha docs](https://mochajs.org/) — the classic `describe`/`it` interface and hook semantics, clearly specified.
- [Node.js test runner](https://nodejs.org/docs/latest/api/test.html) — Node's built-in `node:test`; a minimal real implementation to study.
- [AVA docs](https://github.com/avajs/ava) — shows the concurrent-test-file, worker-process isolation model taken to its logical end.

## Stretch ideas

- Implement snapshot testing with serialized output and `--update-snapshots`.
- Add code coverage via V8's built-in coverage or AST instrumentation.
