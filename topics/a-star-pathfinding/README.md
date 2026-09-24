---
title: "A* Pathfinding"
category: "games-graphics"
difficulty: "intermediate"
tags: ["pathfinding", "algorithms", "ai"]
related: [procedural-dungeon-gen, ascii-roguelike, tilemap-editor]
---

# A* Pathfinding
A* is the workhorse pathfinding algorithm of games: given a grid or graph, it finds the shortest route from start to goal efficiently. Enemies chasing the player, units moving across an RTS map, and NPCs navigating dungeons all rely on it. Implementing it yourself makes graphs, heuristics, and priority queues click.

## Core concepts

- **Graph representation**: The world becomes nodes (grid cells, waypoints) connected by edges with movement costs; A* searches this graph, not the raw geometry.
- **g-cost and h-cost**: g is the exact cost from the start to a node; h is the heuristic estimate from the node to the goal. Their sum f = g + h orders exploration.
- **Heuristics**: Manhattan distance for 4-directional grids, Euclidean or octile for 8-directional. The heuristic must never overestimate (admissible) or the path may not be optimal.
- **Open and closed sets**: The open set (a priority queue keyed by f) holds frontier nodes; the closed set remembers visited nodes so they are never processed twice.
- **Movement weights**: Terrain costs (mud slower than road) are folded into g-cost, letting paths prefer good terrain without special cases.
- **Path smoothing**: Raw grid paths zigzag; line-of-sight checks or string-pulling remove unnecessary waypoints for natural movement.
- **Hierarchical and flow-field variants**: For huge maps or hundreds of agents, hierarchical A* or flow fields amortize the search cost.

## How it works

Push the start node into the open set with g = 0. Repeatedly pop the node with the lowest f, move it to the closed set, and examine its neighbors: for each unvisited neighbor, compute its g through the current node and push it with its f score, remembering the parent that produced the better path. When the goal is popped, follow parent pointers back to the start to recover the shortest path. If the open set empties, no path exists.

## Build milestones

1. Implement A* on a small hardcoded grid and print the found path as ASCII.
2. Add an interactive grid where you paint walls and watch the search expand.
3. Support 8-directional movement, terrain weights, and an admissible heuristic.
4. Add path smoothing so agents cut corners naturally instead of zigzagging.
5. Handle dynamic obstacles by replanning, and profile with a binary-heap open set.
6. Scale up: hierarchical regions or a flow field so hundreds of agents path at once.

## Best resources

- [A* Pathfinding (E01) by Sebastian Lague](http://youtube.com/watch?v=-L-WgKMFuhE) — clear visual explanation of the algorithm and its data structures.
- [SebLague/Pathfinding](https://github.com/SebLague/Pathfinding) — the project repo accompanying the video series.
- [A* tutorial series notes: weights](https://stevelilley.com/2019/12/10/sebastian-lague-a-tutorial-series-weights-pt-06/) — notes on movement penalties and terrain costs.
- [A* tutorial series notes: path smoothing](https://stevelilley.com/2019/12/14/sebastian-lague-a-tutorial-series-path-smoothing-pt-08-and-pt-09/) — notes on smoothing raw grid paths.
- [A* reference project](https://github.com/paulbreuler/Pathfinding) — a standalone A* implementation to study and compare against.

## Stretch ideas

- Implement Jump Point Search for dramatically faster grid pathfinding.
- Add cooperative pathfinding so multiple agents avoid colliding with each other.
