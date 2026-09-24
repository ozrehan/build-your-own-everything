#!/usr/bin/env python3
"""mygit - a tiny reimplementation of Git's core, in ~150 lines.

Commands:
  mygit init                 create a .mygit repo here
  mygit hash-object [-w] FILE  hash a file as a blob (-w saves it)
  mygit cat-file -p SHA        print an object
  mygit write-tree            snapshot the working dir -> tree SHA
  mygit commit-tree TREE -m MSG  create a commit, move main to it
  mygit log                  show commit history

Objects are zlib-compressed exactly like real Git, so real `git`
can read anything mygit writes (try: git --git-dir=.mygit cat-file -p SHA).
"""

import hashlib
import os
import sys
import time
import zlib

GITDIR = ".mygit"


def find_root():
    d = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(d, GITDIR)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            sys.exit("not a mygit repo (no .mygit found)")
        d = parent


def obj_path(root, sha):
    return os.path.join(root, GITDIR, "objects", sha[:2], sha[2:])


def write_object(root, otype, data):
    header = f"{otype} {len(data)}\0".encode() + data
    sha = hashlib.sha1(header).hexdigest()
    path = obj_path(root, sha)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(zlib.compress(header))
    return sha


def read_object(root, sha):
    # accept short SHAs like real git
    if len(sha) < 40:
        d = os.path.join(root, GITDIR, "objects", sha[:2])
        if not os.path.isdir(d):
            sys.exit(f"unknown object {sha}")
        matches = [f for f in os.listdir(d) if f.startswith(sha[2:])]
        if len(matches) != 1:
            sys.exit(f"ambiguous or unknown object {sha}")
        sha = sha[:2] + matches[0]
    with open(obj_path(root, sha), "rb") as f:
        raw = zlib.decompress(f.read())
    hdr, _, data = raw.partition(b"\0")
    otype, size = hdr.decode().split(" ")
    assert int(size) == len(data), "corrupt object"
    return otype, data, sha


def head_ref(root):
    with open(os.path.join(root, GITDIR, "HEAD")) as f:
        return f.read().strip().split(" ", 1)[1]  # ref: refs/heads/main


def ref_sha(root, ref):
    p = os.path.join(root, GITDIR, ref)
    return open(p).read().strip() if os.path.exists(p) else None


def cmd_init(args):
    root = os.path.abspath(args[0]) if args else os.getcwd()
    gd = os.path.join(root, GITDIR)
    os.makedirs(os.path.join(gd, "objects"), exist_ok=True)
    os.makedirs(os.path.join(gd, "refs", "heads"), exist_ok=True)
    with open(os.path.join(gd, "HEAD"), "w") as f:
        f.write("ref: refs/heads/main\n")
    print(f"initialized empty mygit repo in {gd}")


def cmd_hash_object(args):
    root = find_root()
    write = "-w" in args
    path = args[-1]
    with open(path, "rb") as f:
        data = f.read()
    sha = write_object(root, "blob", data) if write else \
        hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    print(sha)


def cmd_cat_file(args):
    root = find_root()
    otype, data, sha = read_object(root, args[-1])
    if otype == "tree":
        out = []
        i = 0
        while i < len(data):
            j = data.index(b"\0", i)
            mode, name = data[i:j].decode().split(" ", 1)
            esha = data[j + 1:j + 21].hex()
            etype, _, _ = read_object(root, esha)
            out.append(f"{mode} {etype} {esha}  {name}")
            i = j + 21
        print("\n".join(out))
    else:
        sys.stdout.write(data.decode(errors="replace"))


def write_tree_for(root, path):
    entries = []
    for name in sorted(os.listdir(path)):
        if name == GITDIR:
            continue
        full = os.path.join(path, name)
        if os.path.isdir(full):
            sha = write_tree_for(root, full)
            entries.append((b"40000", name.encode(), bytes.fromhex(sha)))
        else:
            with open(full, "rb") as f:
                sha = write_object(root, "blob", f.read())
            entries.append((b"100644", name.encode(), bytes.fromhex(sha)))
    data = b"".join(m + b" " + n + b"\0" + s for m, n, s in entries)
    return write_object(root, "tree", data)


def cmd_write_tree(args):
    root = find_root()
    print(write_tree_for(root, root))


def cmd_commit_tree(args):
    root = find_root()
    tree = args[0]
    msg = args[args.index("-m") + 1] if "-m" in args else ""
    ref = head_ref(root)
    parent = ref_sha(root, ref)
    now = int(time.time())
    ident = f"Rehan <rehan@local> {now} +0530"
    body = f"tree {tree}\n"
    if parent:
        body += f"parent {parent}\n"
    body += f"author {ident}\ncommitter {ident}\n\n{msg}\n"
    sha = write_object(root, "commit", body.encode())
    refp = os.path.join(root, GITDIR, ref)
    os.makedirs(os.path.dirname(refp), exist_ok=True)
    with open(refp, "w") as f:
        f.write(sha + "\n")
    print(sha)


def cmd_log(args):
    root = find_root()
    sha = ref_sha(root, head_ref(root))
    if not sha:
        print("no commits yet")
        return
    while sha:
        otype, data, sha = read_object(root, sha)
        lines = data.decode().split("\n")
        msg = "\n".join(lines[lines.index("") + 1:]).strip()
        print(f"commit {sha}\n    {msg}\n")
        parent = [l.split(" ")[1] for l in lines if l.startswith("parent ")]
        sha = parent[0] if parent else None


COMMANDS = {
    "init": cmd_init,
    "hash-object": cmd_hash_object,
    "cat-file": cmd_cat_file,
    "write-tree": cmd_write_tree,
    "commit-tree": cmd_commit_tree,
    "log": cmd_log,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit("usage: mygit {init|hash-object|cat-file|write-tree|commit-tree|log} ...")
    COMMANDS[sys.argv[1]](sys.argv[2:])
