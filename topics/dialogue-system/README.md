---
title: "Dialogue System"
category: "games-graphics"
difficulty: "beginner"
tags: ["dialogue", "narrative", "scripting"]
related: [save-system, ui-toolkit, ascii-roguelike]
---

# Dialogue System
A dialogue system runs conversations in games: branching lines, player choices, and story state that remembers what you said. From visual novels to RPG bark systems, it turns static text into an interactive narrative engine. Building one teaches you scripting languages and state machines.

## Core concepts

- **Dialogue scripting language**: A writer-friendly format (like Ink or Yarn) with lines, choices, and logic — separate from code so writers can work independently.
- **Nodes and choices**: Conversations are graphs of nodes; choices are edges the player picks between, leading to different branches.
- **Variables and conditions**: Story state (met the king? has the key?) gates which lines and choices appear, making dialogue reactive.
- **Localization**: Every line needs a stable ID so translations can be swapped per language without touching logic.
- **Typewriter effect**: Text reveals character by character with skip-on-input — the signature feel of game dialogue.
- **Speaker metadata**: Names, portraits, and voice cues attach to lines so the UI can present who's talking.
- **Save integration**: Dialogue progress (visited nodes, set variables) must persist in the save system or choices won't stick.

## How it works

Writers author dialogue in a script file with lines, choices, and conditional logic. At build time (or load time) the script compiles into a runtime model of nodes and edges. In game, the dialogue runner starts at a node, displays its lines with the typewriter effect, and presents choices; the player's pick jumps to the next node while setting story variables. Conditions on lines and choices are evaluated against those variables, so the conversation adapts to everything the player has done.

## Build milestones

1. Display a single line of dialogue with a typewriter effect and click-to-continue.
2. Add a simple script format with speaker names and sequential lines.
3. Implement player choices that branch to different lines.
4. Add story variables and conditional lines/choices (e.g. different greeting if you've met before).
5. Integrate an existing language (Ink or Yarn Spinner) as the scripting backend.
6. Add localization IDs, voice-over hooks, and a dialogue editor preview tool.

## Best resources

- [Ink](https://github.com/syynth/ink) — inkle's narrative scripting language for branching dialogue.
- [Yarn Spinner](https://yarnspinner.dev/) — a friendly dialogue scripting language for games.
- [Yarn Spinner docs](https://docs.yarnspinner.dev/) — full documentation for writing and running Yarn dialogue.
- [YarnSpinner-Unity](https://github.com/YarnSpinnerTool/YarnSpinner-Unity) — Unity integration showing how a dialogue runner wires into a game.

## Stretch ideas

- Add a visual node-graph editor for authoring conversations instead of text files.
- Implement procedural barks: NPCs commenting on world events from templated lines.
