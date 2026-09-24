---
title: "LLM Eval Harness"
category: "ai-ml"
difficulty: "intermediate"
tags: [evaluation, llm, benchmarking]
related: [rag-pipeline, transformer-from-scratch, prompt-cache]
---

# LLM Eval Harness

An eval harness turns "the model feels smarter" into numbers: a set of tasks, a runner that prompts the model, and scorers that grade the outputs. Building one yourself teaches the uncomfortable truth of LLM evaluation — that benchmark design (prompt format, few-shot examples, scoring rule) often matters more than the model being tested.

## Core concepts

- **Tasks as the unit of evaluation** — Each eval is a dataset of (input, expected output) pairs plus a scoring function: multiple-choice accuracy, exact match, or a rubric. A harness is just infrastructure for running many of these uniformly.
- **Logprob vs generation scoring** — Multiple-choice tasks can be scored by comparing token probabilities (fast, deterministic); open-ended tasks need actual generation plus grading (slow, noisy). The choice changes both cost and what you're measuring.
- **Few-shot prompting** — Including example Q&A pairs in the prompt dramatically changes scores, so harnesses standardize the number and selection of shots. Comparing a 0-shot score to a 5-shot score is comparing different tests.
- **LLM-as-judge** — A stronger model grades outputs against a rubric. It's the pragmatic choice for open-ended tasks, but it introduces judge bias (verbosity preference, self-preference) that you must calibrate for.
- **Contamination** — If the model saw the test set during training, the score is meaningless. Deduplicating evals against training data and using held-out or dynamic benchmarks is an active research problem, not a solved one.
- **Statistical significance** — A 1% benchmark gap on 200 examples is noise. Good harnesses report confidence intervals and standard errors; without them you're reading tea leaves.

## How it works

You define a task: a loader that yields prompts, a template that formats each example (system prompt, few-shot examples, the question), and a scorer (regex/exact match, logprob comparison, or judge model call). The runner iterates over examples, calls the model API with retries and rate limiting, caches responses so reruns are cheap, applies the scorer, and aggregates into metrics with error bars. A report layer diffs two models side by side. The architecture is deliberately boring — the interesting work is all in task design and scoring validity.

## Build milestones

1. Build a minimal runner: 20 hand-written Q&A pairs, exact-match scoring, a results table. Run it against any LLM API.
2. Add multiple-choice logprob-style scoring (or generation + answer extraction) and few-shot prompt templates as configuration.
3. Implement response caching (SQLite) and parallel requests with rate limiting; reruns should be free and fast.
4. Add an LLM-as-judge scorer with a written rubric; measure judge agreement against your own grades on 30 samples.
5. Implement a diff mode: run two models/prompts on the same tasks and report per-task deltas with confidence intervals.

## Best resources

- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) — The community-standard harness; study its task-config format before designing your own.
- [openai/evals](https://github.com/openai/evals) — OpenAI's eval framework and registry; good examples of eval YAML definitions.
- [HELM (Holistic Evaluation of Language Models)](https://crfm.stanford.edu/helm/) — Stanford's broad-coverage benchmark suite; the state of the art in "evaluate everything" methodology.
- [Holistic Evaluation of Language Models (paper)](https://arxiv.org/abs/2211.09110) — The paper behind HELM; excellent on metrics, scenarios, and what "holistic" should mean.
- [Hugging Face Evaluate](https://github.com/huggingface/evaluate) — The library of standard metrics (BLEU, ROUGE, exact match) your scorers will build on.
- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) — The foundational study of using LLMs as evaluators, including their biases.

## Stretch ideas

- Build a contamination checker: n-gram overlap analysis between your eval sets and a model's known training corpora.
- Add regression gating for prompts: run the harness in CI so prompt changes can't silently degrade quality.
