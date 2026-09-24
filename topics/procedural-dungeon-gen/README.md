---
title: "Procedural Dungeon Generator"
category: "games-graphics"
difficulty: "intermediate"
tags: ["procedural-generation", "dungeons", "algorithms"]
related: [a-star-pathfinding, ascii-roguelike, tilemap-editor]
---

# Procedural Dungeon Generator
A procedural dungeon generator creates a fresh, playable level every run — rooms, corridors, doors, and treasure placed by algorithm instead of by hand. It is the heart of roguelikes and the reason games like Binding of Isaac stay replayable. Building one teaches you randomness, graph layout, and constraint satisfaction.

## Core concepts

- **Seeded randomness**: A seed drives every random choice, so the same seed always yields the same dungeon — shareable, debuggable, and replayable.
- **Room placement**: Rectangles (or irregular shapes) are scattered and kept non-overlapping, often with a minimum size so rooms feel meaningful.
- **Corridor carving**: Corridors connect rooms using random walks, L-shaped hallways, or Delaunay triangulation plus a minimum spanning tree for guaranteed connectivity.
- **Connectivity guarantees**: A spanning tree over room centers ensures every room is reachable; extra corridors are added back as loops so the map isn't a boring tree.
- **Dead-end removal**: Maze-carved areas are pruned of dead ends (or kept deliberately for secrets) to control how the dungeon feels to explore.
- **Theming and content**: After layout, the generator places doors, enemies, loot, and traps according to difficulty curves — deeper rooms get deadlier content.
- **Cellular automata**: Caves and organic areas are grown with cellular automata rules (like Conway's Game of Life) and smoothed over several iterations.

## How it works

Start with a grid of solid rock. Place rooms at random non-overlapping positions. Grow a maze through the remaining rock with a random-walk carver, then connect each room to the maze with doors. Prune excess dead ends, and verify connectivity with a flood fill from the entrance — everything reachable is kept, stragglers are removed or reconnected. Finally, populate: spawn the player at the entrance, enemies and loot by depth, and the exit in the farthest room.

## Build milestones

1. Generate a grid of random non-overlapping rooms rendered as ASCII.
2. Connect rooms with L-shaped corridors and guarantee full connectivity.
3. Add maze carving between rooms (rooms-and-mazes style) plus dead-end pruning.
4. Place gameplay content: entrance, exit, enemies, treasure, and locked doors with keys.
5. Add difficulty scaling by depth and multiple dungeon themes or biomes.
6. Build a visualizer that animates generation step by step and lets you re-roll with a seed input.

## Best resources

- [Rooms and Mazes: A Procedural Dungeon Generator](https://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/) — Bob Nystrom's classic walkthrough of the full algorithm.
- [Dungeon Generation in Binding of Isaac](https://www.boristhebrave.com/2020/09/12/dungeon-generation-in-binding-of-isaac/) — analysis of a shipped game's generation rules.
- [Dungeon Generation in Enter the Gungeon](https://www.boristhebrave.com/2019/07/28/dungeon-generation-in-enter-the-gungeon/) — how Gungeon builds its levels.
- [Procedural Content Generation in Games, Chapter 3](https://www.pcgbook.com/chapter03.pdf) — the academic treatment of dungeon and level generation.

## Stretch ideas

- Generate quest structure alongside the map: the key is always placed before its locked door.
- Evolve the generator with player data, biasing layouts toward what players enjoy.
