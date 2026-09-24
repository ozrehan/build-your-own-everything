---
title: "ASCII Roguelike"
category: "games-graphics"
difficulty: "beginner"
tags: ["roguelike", "ascii", "turn-based"]
related: [procedural-dungeon-gen, a-star-pathfinding, dialogue-system]
---

# ASCII Roguelike
An ASCII roguelike is a dungeon crawler rendered entirely in text characters: `@` is you, `g` is a goblin, `#` is a wall. No art budget needed — just game design. It is the ideal first complete game: procedural dungeons, turn-based combat, permadeath, and emergent stories from simple interacting systems.

## Core concepts

- **Grid-based world**: The dungeon is a 2D array of tiles; entities occupy cells, and everything from movement to line-of-sight operates on the grid.
- **Turn-based loop**: The game waits for player input, then every entity takes a turn in order. No real-time pressure — complexity comes from decisions, not reflexes.
- **Field of view**: Shadowcasting reveals only tiles visible from the player; explored-but-unseen areas stay dim in memory, creating tension and discovery.
- **Entities and components**: Player, monsters, and items share an entity model with health, attack, and AI components; data-driven design keeps content easy to add.
- **Combat**: Bump-to-attack keeps input simple — walking into an enemy attacks it. Damage formulas, armor, and status effects add depth.
- **Procedural generation**: Each run generates a new dungeon with monsters and loot scaled by depth, making every playthrough different.
- **Permadeath**: Death ends the run permanently. It makes every decision matter and every victory memorable.

## How it works

The main loop renders the dungeon grid as characters, waits for a keypress, and then processes a full turn: the player moves or attacks, then each monster takes its AI turn (wander, chase via pathfinding, or attack if adjacent). Field of view is recomputed after movement, items can be picked up and used, and descending stairs generates a deeper, harder level. If the player's health hits zero, the run ends and a new seeded dungeon begins.

## Build milestones

1. Render a static dungeon room in ASCII and move `@` around with arrow keys.
2. Add walls that block movement, a procedurally generated multi-room dungeon, and stairs.
3. Implement field of view with shadowcasting and explored-vs-visible tile rendering.
4. Add monsters with simple AI (chase when visible, wander otherwise) and bump combat.
5. Add items (potions, weapons), an inventory screen, and permadeath with a game-over screen.
6. Polish into a complete game: multiple enemy types, a final boss, high-score tracking, and save-compatible seeded runs.

## Best resources

- [Roguelike Tutorial, part 2](https://rogueliketutorials.com/tutorials/tcod/v2/part-2/) — the classic step-by-step roguelike tutorial series.
- [roguelike_tutorial_v2](https://github.com/azimuth73/roguelike_tutorial_v2) — a complete implementation of the tutorial to study.
- [rogueday notes](https://github.com/nigeltc/rogueday) — notes from working through a roguelike tutorial.
- [libtcod](https://github.com/libtcod) — the roguelike development library: field of view, pathfinding, and console rendering.
- [Roguelike Celebration](https://www.roguelike.club/) — the community conference with talks on procedural generation and roguelike design.

## Stretch ideas

- Add a magic system with scrolls, wands, and area-of-effect spells.
- Implement monster factions so enemies fight each other, creating emergent stories.
