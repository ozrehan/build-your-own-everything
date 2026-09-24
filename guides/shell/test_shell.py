"""Test for shell.py — drives the shell with piped stdin, checks stdout."""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def run_shell(script, cwd=None):
    p = subprocess.run(
        [sys.executable, os.path.join(HERE, "shell.py")],
        input=script, capture_output=True, text=True, cwd=cwd, timeout=20)
    return p.stdout, p.stderr, p.returncode


def main():
    with tempfile.TemporaryDirectory() as d:
        out, err, code = run_shell("echo hello\nexit\n", cwd=d)
        assert "hello" in out, f"echo failed: {out!r}"
        assert code == 0

        out, _, _ = run_shell("pwd\nexit\n", cwd=d)
        assert d in out or os.path.basename(d) in out, f"pwd failed: {out!r}"

        out, _, _ = run_shell("echo foo | tr a-z A-Z\nexit\n", cwd=d)
        assert "FOO" in out, f"pipe failed: {out!r}"

        out, _, _ = run_shell("echo bar > out.txt\nexit\n", cwd=d)
        with open(os.path.join(d, "out.txt")) as f:
            assert f.read().strip() == "bar", "redirect failed"

        out, _, _ = run_shell("echo one >> out.txt\nexit\n", cwd=d)
        with open(os.path.join(d, "out.txt")) as f:
            assert f.read().strip().split() == ["bar", "one"], "append failed"

        out, _, _ = run_shell("cd /tmp\npwd\nexit\n", cwd=d)
        assert "/tmp" in out, f"cd failed: {out!r}"

        out, err, _ = run_shell("definitely-not-a-real-cmd-xyz\nexit\n", cwd=d)
        assert "not found" in err or "not found" in out, "unknown cmd silent"

        # a failing line must not kill the shell
        out, _, code = run_shell("definitely-not-a-real-cmd-xyz\necho alive\nexit\n", cwd=d)
        assert "alive" in out and code == 0, "shell died on bad command"

    print("all shell tests passed")


if __name__ == "__main__":
    main()
