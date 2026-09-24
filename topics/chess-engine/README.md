---
title: "Chess Engine"
category: "games-graphics"
difficulty: "advanced"
tags: ["chess", "ai", "search"]
related: [a-star-pathfinding, ascii-roguelike, ui-toolkit]
---

# Chess Engine
A chess engine is a program that plays chess: it represents the board, generates legal moves, and searches millions of positions to pick the best one. It is the purest form of game AI — no graphics tricks, just search and evaluation. Building even a weak engine teaches you data structures, pruning, and optimization like nothing else.

## Core concepts

- **Board representation**: Bitboards (64-bit integers, one per piece type) make move generation blazing fast with bitwise operations; simpler mailbox arrays are easier to start with.
- **Move generation**: Every legal move for a position must be generated exactly, including castling, en passant, and promotion — bugs here silently corrupt the search.
- **Minimax with alpha-beta pruning**: The engine assumes both sides play optimally; alpha-beta pruning skips branches that can't change the outcome, searching far deeper in the same time.
- **Evaluation function**: A heuristic score (material + piece-square tables + king safety) estimates who's winning without searching to checkmate.
- **Iterative deepening**: Search depth 1, then 2, then 3... so the engine always has a best move ready when its time runs out.
- **Transposition tables**: A hash map of previously searched positions avoids recomputing them when the same position arises via different move orders.
- **UCI protocol**: The Universal Chess Interface is a text protocol letting any engine talk to any chess GUI — implement it and your engine can play in real apps.

## How it works

The engine receives a position (FEN string) and a time limit over UCI. It runs iterative deepening: at each depth, a negamax search with alpha-beta pruning explores moves ordered by likely quality (captures first), using the transposition table to cut repeats. Leaf nodes are scored by the evaluation function, scores propagate up assuming optimal play, and the best move at the deepest completed depth is returned as `bestmove`.

## Build milestones

1. Represent a board and generate legal moves for all pieces, validated against known perft counts.
2. Add minimax search with a simple material-only evaluation that beats random play.
3. Implement alpha-beta pruning and move ordering; measure nodes-per-second.
4. Add iterative deepening, quiescence search (to avoid horizon-effect blunders), and piece-square tables.
5. Implement the UCI protocol so the engine plays in a real GUI like Arena or Cute Chess.
6. Tune with a transposition table and null-move pruning, then test against other engines.

## Best resources

- [Simple Chess AI, Step by Step](https://www.freecodecamp.org/news/simple-chess-ai-step-by-step-1d55a9266977) — building a minimax/alpha-beta chess AI from scratch.
- [Sunfish](https://github.com/thomasahle/sunfish) — a tiny but complete Python chess engine to study.
- [UCI Protocol — Shredder Chess](https://www.shredderchess.com/chess-features/uci-universal-chess-interface.html) — what the Universal Chess Interface is and why engines use it.
- [UCI specification](https://github.com/andersfylling/uci/blob/HEAD/description.md) — the full text of the UCI protocol spec for implementing engine<->GUI communication.

## Stretch ideas

- Train a tiny neural-network evaluation function on self-play games.
- Add an opening book and endgame tablebase support.
