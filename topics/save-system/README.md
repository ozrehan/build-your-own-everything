---
title: "Save System"
category: "games-graphics"
difficulty: "beginner"
tags: ["persistence", "serialization", "game-data"]
related: [dialogue-system, procedural-dungeon-gen, chip8-emulator]
---

# Save System
A save system preserves a player's progress — position, inventory, quest flags — to disk and restores it later. It sounds simple until version 2 of your game has to load version 1's saves. Building one teaches you serialization, data versioning, and which state is actually worth keeping.

## Core concepts

- **Serialization**: Converting in-memory game state into bytes (JSON, binary, or a custom format) that can be written to a file and read back later.
- **Save slots**: Multiple named slots plus an autosave slot let players keep parallel playthroughs and recover from crashes.
- **What to save vs recompute**: Save player stats, inventory, and world flags; recompute transient things like particle positions and enemy AI state on load.
- **Versioning and migration**: A version number in every save file lets the loader upgrade old formats — add a migration step per version, never break old saves silently.
- **Checksums**: A hash stored alongside the data detects corrupted or tampered save files before they crash the game.
- **Atomic writes**: Write to a temp file then rename, so a crash mid-save never leaves a half-written file as the only copy.
- **Autosave triggers**: Save on zone transitions, quest completion, timed intervals, and quit — never only on player request.

## How it works

When saving, the game walks its world collecting each saveable object's state into a plain data structure (position, health, inventory IDs, quest flags), tags it with a format version and checksum, serializes it to JSON or binary, and writes it atomically to the slot file. On load, the file is read, the checksum verified, migrations applied if the version is old, and objects are reconstructed: the player is placed, inventory restored, and world flags reapplied so doors stay opened and bosses stay dead.

## Build milestones

1. Serialize a player struct (position, health, level) to JSON and load it back.
2. Add multiple save slots with timestamps and a save/load menu UI.
3. Save a small world: entity list, inventory, and quest flags — skipping transient state.
4. Implement versioning with a migration that upgrades v1 saves to v2.
5. Add atomic writes, checksums, and autosave on zone change plus quit.
6. Support cloud-style conflict handling: detect a newer save and prompt before overwriting.

## Best resources

- [Save System Design skill](https://github.com/xyrces/godot-ecs-gamedev-playbook/blob/HEAD/skills/save_system_design/SKILL.md) — a full save architecture: serializers, version migrator, autosave scheduler.
- [Saving System Upgrade: BinaryFormatter to Json.NET](https://community.gamedev.tv/t/saving-system-upgrade-replacing-binaryformatter-with-json-net/174046) — GameDev.tv walkthrough of evolving a real save system.
- [Unity Save & Load System notes](https://github.com/yinhk-gamedev/unity-learn/blob/HEAD/Save%20&%20Load%20System/README.md) — JSON serialization patterns for game saves.
- [Serialization in Unity](https://DEV.to/marufhow/serialization-in-unity-2bmc) — the serialization fundamentals behind any save system.

## Stretch ideas

- Add screenshot thumbnails to each save slot for easy identification.
- Implement cross-device sync by uploading saves to a simple backend.
