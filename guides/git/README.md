# Build Your Own Git

Reimplement Git's core — objects, trees, and commits — in ~150 lines of Python.
By the end you'll understand exactly what happens when you run `git commit`.

## What you'll build

`mygit.py`, a tiny Git that supports:

- `init` — create a `.mygit` repository
- `hash-object [-w]` — hash a file into a blob object
- `cat-file -p <sha>` — pretty-print any object
- `write-tree` — snapshot the working directory as a tree object
- `commit-tree <tree> -m <msg>` — create a commit, move `main` forward
- `log` — walk the commit history

Objects are zlib-compressed **exactly like real Git**, so real `git` can read
anything `mygit` writes:

```sh
git --git-dir=.mygit cat-file -p <sha>
```

## How it works

1. **Objects.** Every blob/tree/commit is stored as `<type> <size>\0<content>`,
   zlib-compressed, at `.mygit/objects/ab/cdef...` (first 2 SHA-1 hex chars
   become the directory). `hash_object()` does the hashing + writing.
2. **Blobs.** `hash-object -w` reads a file and stores it as a blob. No
   filename is kept — the name lives in the tree.
3. **Trees.** `write-tree` walks the working directory, hashes every file as a
   blob, and writes one tree object listing `mode name sha` entries, sorted.
4. **Commits.** `commit-tree` writes a commit object (`tree <sha>`, optional
   `parent <sha>`, author, message) and updates the `refs/heads/main` ref.
5. **Log.** `log` starts at `main` and follows `parent` lines back.

## Run it

```sh
cd guides/git
python3 mygit.py init
echo "hello git" > a.txt
python3 mygit.py hash-object -w a.txt
TREE=$(python3 mygit.py write-tree)
python3 mygit.py commit-tree $TREE -m "first commit"
python3 mygit.py log
```

## Test it

```sh
python3 test_mygit.py   # exercises the full workflow in a temp dir
```

## Stretch exercises

1. Add `status` — compare working directory against the last commit's tree.
2. Add branching: `branch <name>` and `checkout <name>` (just move refs around).
3. Implement the packfile format so `mygit` repos can be cloned.

## Further reading

- [Write yourself a Git!](https://wyag.thb.lt) — the classic from-scratch Git book
- [ugit: Learn Git Internals by Building Git Yourself](https://www.leshenko.net) — video series building a Git in Python
- [Gitlet](https://gitlet.maryrosecook.com) — build Git in JavaScript
