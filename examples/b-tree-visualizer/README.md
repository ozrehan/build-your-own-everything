# Example: Databases — B-Tree Visualizer

**[▶ Try it live](https://byoe-btree.netlify.app)**

The index structure inside Postgres, MySQL, and SQLite — animated.
Insert keys and watch nodes **split**, the exact moment a database grows a new level.

Example project for the [databases learning path](../../topics/b-tree-index/).

## What it teaches

- **Node splits**: when a node overflows, the middle key is pushed up — splits can
  cascade all the way to the root, growing the tree one level.
- **O(log n) search**: every search walks a single root-to-leaf path.
- **Self-balancing**: insert keys in order or shuffled — the tree stays balanced either way.

The implementation is a real B-tree (order m=4), ~120 lines, in `index.html`.

## Try

1. Insert 1–20 in order (worst case), reset, then insert shuffled. Compare heights.
2. Search for a key and count the levels walked.
3. Exercise: add **deletion** with node merging (the harder half of B-trees).
