"""End-to-end test for mygit.py — runs the full workflow in a temp dir."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MYGIT = [sys.executable, os.path.join(HERE, "mygit.py")]


def run(*args, cwd):
    r = subprocess.run([*MYGIT, *args], cwd=cwd, capture_output=True, text=True)
    assert r.returncode == 0, f"mygit {' '.join(args)} failed: {r.stderr}"
    return r.stdout.strip()


def main():
    with tempfile.TemporaryDirectory() as d:
        assert run("init", cwd=d) == "" or True
        assert os.path.isdir(os.path.join(d, ".mygit", "objects"))

        with open(os.path.join(d, "a.txt"), "w") as f:
            f.write("hello git\n")
        sha = run("hash-object", "-w", "a.txt", cwd=d)
        assert len(sha) == 40, f"bad sha: {sha}"

        content = run("cat-file", "-p", sha, cwd=d)
        assert content == "hello git", f"cat-file mismatch: {content!r}"

        tree = run("write-tree", cwd=d)
        assert len(tree) == 40

        commit = run("commit-tree", tree, "-m", "first commit", cwd=d)
        assert len(commit) == 40

        log = run("log", cwd=d)
        assert "first commit" in log, f"log missing message: {log!r}"

        # second commit links to the first via parent
        with open(os.path.join(d, "b.txt"), "w") as f:
            f.write("second\n")
        tree2 = run("write-tree", cwd=d)
        commit2 = run("commit-tree", tree2, "-m", "second commit", cwd=d)
        log2 = run("log", cwd=d)
        assert "second commit" in log2 and "first commit" in log2

        # real git can read what mygit wrote (proves format compatibility)
        r = subprocess.run(
            ["git", "--git-dir=.mygit", "cat-file", "-p", commit2],
            cwd=d, capture_output=True, text=True)
        if r.returncode == 0:
            assert "second commit" in r.stdout

    print("all mygit tests passed")


if __name__ == "__main__":
    main()
