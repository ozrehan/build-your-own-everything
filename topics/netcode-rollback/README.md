---
title: "Rollback Netcode"
category: "games-graphics"
difficulty: "advanced"
tags: ["networking", "multiplayer", "netcode"]
related: [physics-engine, 2d-game-engine, save-system]
---

# Rollback Netcode
Rollback netcode makes online fighting and action games feel like offline play: it predicts what remote players will do and rewinds the simulation when the prediction was wrong. It is why modern fighting games can feel responsive across continents. Building it teaches you deterministic simulation and the real cost of the speed of light.

## Core concepts

- **Deterministic simulation**: Given the same inputs, every client must produce exactly the same game state — fixed-point math or careful float discipline, no random calls outside the shared RNG.
- **Input prediction**: When a remote player's input hasn't arrived yet, the game guesses (usually "repeat last input") and keeps simulating instead of stalling.
- **State snapshots**: The full game state is saved every frame into a ring buffer so the simulation can rewind to any recent frame.
- **Rollback and resimulation**: When the real remote input arrives and differs from the prediction, the game restores the snapshot from that frame and re-simulates forward to the present.
- **Input delay**: A small local input delay (1–3 frames) gives remote inputs time to arrive, drastically reducing mispredictions at the cost of slight local lag.
- **State serialization**: Snapshots must be fast to capture and restore — flat, memcpy-able state beats pointer-heavy structures.
- **Desync detection**: Checksums of state per frame, exchanged between peers, catch determinism bugs before they silently diverge.

## How it works

Each frame, both players' inputs are fed into the deterministic simulation and the resulting state is snapshotted. If a remote input is missing, the last known input is predicted. When the actual input packet arrives late, the netcode compares it to the prediction: on mismatch, it restores the state from the frame the input belonged to and re-simulates every frame up to the present with the corrected input. Players see a tiny visual correction instead of the whole game freezing to wait for packets.

## Build milestones

1. Make a tiny 2-player game simulation fully deterministic with serialized state snapshots.
2. Add local 2-player with a simulated network delay to feel the input problem.
3. Implement input prediction with "repeat last input" and a snapshot ring buffer.
4. Implement rollback: on late input arrival, restore and resimulate to the present.
5. Add configurable input delay, per-frame checksums, and desync logging.
6. Play over real UDP with packet loss simulation, then tune until corrections are invisible.

## Best resources

- [GGPO rollback research guide](https://github.com/endel/prediction-multiplayer-research/blob/HEAD/ggpo-rollback.md) — the concepts behind GGPO-style rollback netcode.
- [telegraph](https://github.com/lucasnate/telegraph) — a TypeScript GGPO-style rollback implementation to study.
- [lite-rollback](https://github.com/peshovurtoleta/lite-rollback) — a lightweight rollback netcode implementation.
- [rollback-netcode reference](https://github.com/kingpinged/rollback-netcode) — another reference implementation of rollback techniques.

## Stretch ideas

- Add spectator mode by streaming inputs and letting observers simulate deterministically.
- Implement save-state-based replays: record inputs, then replay the whole match from frame zero.
