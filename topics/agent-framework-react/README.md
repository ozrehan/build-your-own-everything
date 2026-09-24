---
title: "ReAct Agent Framework"
category: "ai-ml"
difficulty: "intermediate"
tags: [agents, react, tool-use]
related: [q-learning-agent, rag-pipeline, eval-harness-llm, prompt-cache]
---

# ReAct Agent Framework

A ReAct agent loops through Thought → Action → Observation: the LLM reasons about what to do, calls a tool (search, calculator, code runner), reads the result, and repeats until it can answer. Building this loop yourself — the prompt format, the tool registry, the parsing — shows that "agents" are mostly careful prompt engineering wrapped around an LLM API, not a new kind of model.

## Core concepts

- **The ReAct loop** — Interleaving reasoning traces with actions lets the model plan, gather information, and adjust. The "Thought:" lines aren't just for show: they measurably improve tool-use accuracy by forcing explicit planning.
- **Tools as functions** — Each tool is a name, a description, and a JSON schema for its arguments. The LLM only ever outputs text; your framework parses the action, validates arguments against the schema, executes, and feeds back the observation.
- **Function calling** — Modern APIs natively support tool use: the model emits structured tool calls instead of you parsing "Action:" text. More reliable than prompt parsing, but the loop architecture is identical underneath.
- **Observation handling** — Tool outputs must be truncated, formatted, and sometimes summarized before re-entering the context. Unbounded observations blow the context window; badly formatted ones confuse the model.
- **Stopping conditions** — Max iterations, "Final Answer" detection, repeated-action detection (the model stuck in a loop calling the same tool). A production agent needs all three; a demo needs at least the first.
- **Planning vs reacting** — ReAct is purely reactive (one step at a time). Alternatives like plan-then-execute generate a full plan upfront. Reacting handles surprises better; planning is cheaper and more predictable. Most real systems mix both.

## How it works

You maintain a message history starting with a system prompt that describes the available tools and the Thought/Action/Observation format. Each iteration: send the history to the LLM, parse its response — either a tool call (name + JSON args) or a final answer. If it's a tool call, look it up in the registry, execute it with a timeout, append the result as an observation, and loop. If it's a final answer (or max iterations hit), return. Error handling is load-bearing: malformed tool calls, tool exceptions, and timeouts all become observations the model can recover from, which is what makes the loop robust instead of brittle.

## Build milestones

1. Build the core loop with two hardcoded tools (calculator, web search stub): prompt template, action parsing via regex, observation feedback.
2. Add a proper tool registry: decorators to register functions with JSON schemas, automatic argument validation, timeouts.
3. Switch to native function calling with a real LLM API; compare reliability against your regex-parsed version.
4. Add guardrails: max iterations, loop detection (same action 3× → break), observation truncation, and a token-budget tracker.
5. Build a genuinely useful agent (e.g. a research assistant that searches, fetches pages, and writes a cited summary) and evaluate it on 10 tasks.

## Best resources

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — The Yao et al. paper that defined the pattern; includes the prompt templates.
- [Chain-of-Thought Prompting Elicits Reasoning](https://arxiv.org/abs/2201.11903) — The reasoning-trace idea ReAct builds on; essential background.
- [Building Effective Agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic's engineering guide: when to use workflows vs agents, and patterns that work in production.
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview) — The graph-based framework for stateful agents; study its ReAct implementation as a reference.
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) — How native tool use works: schemas, parallel calls, and structured outputs.

## Stretch ideas

- Implement multi-agent collaboration: a planner agent that delegates to specialist sub-agents with different tool sets.
- Add persistent memory (a vector store of past observations) so the agent accumulates knowledge across tasks.
