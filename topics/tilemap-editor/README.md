---
title: "Tilemap Editor"
category: "games-graphics"
difficulty: "intermediate"
tags: ["tilemaps", "level-design", "tools"]
related: [2d-game-engine, procedural-dungeon-gen, ui-toolkit, sprite-animation]
---

# Tilemap Editor
A tilemap editor is the tool level designers use to paint 2D game worlds: pick tiles from a palette and stamp them onto a grid. Every 2D RPG, platformer, and strategy game level is built this way. Writing your own editor teaches you tools programming — the unglamorous half of game development.

## Core concepts

- **Tiles and tilesets**: Levels are built from small square images; a tileset packs them into one texture, each tile referenced by an ID.
- **Layers**: Ground, decoration, and collision live on separate layers so art and logic stay independent and render in the right order.
- **Map formats**: TMX (Tiled's XML) and JSON store tile IDs per layer plus metadata; your game loads this file at runtime.
- **Autotiling**: Bitmask rules pick the right edge/corner tile automatically as you paint, so walls and terrain connect seamlessly.
- **Object layers**: Non-grid entities — spawn points, triggers, NPCs — are placed as objects with positions and custom properties.
- **Undo/redo**: Every edit is a command on a stack; tools live or die by reliable undo.
- **Camera and viewport**: Pan, zoom, and grid snapping make large maps editable; the editor renders only the visible region.

## How it works

The editor loads a tileset image and slices it into tiles. The map is a 2D array of tile IDs per layer. Painting tools (brush, fill, eraser, rectangle) write IDs into the array under the cursor; the renderer draws the visible tiles each frame. Selecting a tile in the palette changes the active brush. Saving serializes layers, tileset references, and objects to TMX or JSON, which the game then loads and renders with the same tile size.

## Build milestones

1. Display a tileset palette and paint tiles onto a grid with a brush tool.
2. Add multiple layers, eraser, flood fill, and save/load to JSON.
3. Implement undo/redo, pan/zoom camera, and rectangular selection.
4. Add autotiling rules so terrain edges connect automatically while painting.
5. Support object layers for spawn points and triggers with editable properties.
6. Export to the TMX format (compatible with the real Tiled editor) and build a runtime loader that renders your maps in a game.

## Best resources

- [Tiled Map Editor](https://www.mapeditor.org/) — the reference open-source tilemap editor; study its features and formats.
- [gl-tiled](https://github.com/lemueldls/gl-tiled) — a WebGL renderer for Tiled maps, useful for the runtime side.
- [Tiled Editor Workflow for Phaser](https://github.com/yakoub-ai/phaser4-gamedev/blob/HEAD/skills/phaser-tilemap/references/tiled-workflow.md) — step-by-step guide to authoring maps in Tiled.
- [Tiled forum: tilemap source code](https://discourse.mapeditor.org/t/where-can-i-find-tilemap-source-code/4066/2) — discussion of TMX/JSON map formats and editing them.

## Stretch ideas

- Add collaborative editing so two designers can paint the same map over the network.
- Implement isometric and hexagonal map rendering alongside orthogonal.
