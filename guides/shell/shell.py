#!/usr/bin/env python3
"""myshell - a tiny Unix shell (~150 lines, stdlib only).

Features: interactive prompt, external commands, builtins (cd, exit,
echo, pwd), single pipes (a | b), output redirection (> and >>),
~ expansion, and Ctrl-C never kills the shell.
"""

import os
import shlex
import signal
import sys


def split_pipeline(line):
    """Split on |, ignoring pipes inside quotes."""
    parts, cur, quote = [], [], None
    for ch in line:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            cur.append(ch)
        elif ch == "|":
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def parse_segment(seg):
    """shlex-split one pipeline stage; pull out > / >> redirection."""
    argv, redir, toks = [], None, shlex.split(seg, posix=True)
    i = 0
    while i < len(toks):
        if toks[i] in (">", ">>") and i + 1 < len(toks):
            redir = (toks[i], os.path.expanduser(toks[i + 1]))
            i += 2
        else:
            argv.append(os.path.expanduser(toks[i]))
            i += 1
    return argv, redir


def run_builtin(argv, out):
    """Run a builtin, writing to file object `out`. Returns True if handled."""
    cmd = argv[0]
    if cmd == "cd":
        try:
            os.chdir(os.path.expanduser(argv[1]) if len(argv) > 1
                     else os.path.expanduser("~"))
        except OSError as e:
            print(f"cd: {e}", file=sys.stderr)
        return True
    if cmd == "exit":
        raise SystemExit(0)
    if cmd == "pwd":
        out.write(os.getcwd() + "\n")
    elif cmd == "echo":
        out.write(" ".join(argv[1:]) + "\n")
    else:
        return False
    out.flush()  # children os._exit() without flushing stdio
    return True


def spawn(argv, redir, stdin_fd, stdout_fd):
    """Fork one pipeline stage; wire fds, exec (or run echo/pwd)."""
    pid = os.fork()
    if pid:
        return pid
    # --- child ---
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # children CAN be Ctrl-C'd
    try:
        if stdin_fd is not None:
            os.dup2(stdin_fd, 0)
        if stdout_fd is not None:
            os.dup2(stdout_fd, 1)
        if redir:
            flags = os.O_WRONLY | os.O_CREAT | \
                (os.O_TRUNC if redir[0] == ">" else os.O_APPEND)
            fd = os.open(redir[1], flags, 0o644)
            os.dup2(fd, 1)
            os.close(fd)
        for fd in range(3, 256):  # close inherited pipe ends
            try:
                os.close(fd)
            except OSError:
                pass
        if argv[0] in ("echo", "pwd"):
            run_builtin(argv, sys.stdout)
            os._exit(0)
        if argv[0] in ("cd", "exit"):
            print(f"myshell: {argv[0]}: not allowed in a pipeline",
                  file=sys.stderr)
            os._exit(1)
        os.execvp(argv[0], argv)
    except FileNotFoundError:
        print(f"myshell: command not found: {argv[0]}", file=sys.stderr)
    except OSError as e:
        print(f"myshell: {argv[0]}: {e}", file=sys.stderr)
    os._exit(127)


def run_line(line):
    stages = [(a, r) for a, r in
              (parse_segment(s) for s in split_pipeline(line)) if a]
    if not stages:
        return
    if len(stages) == 1 and stages[0][0][0] in ("cd", "exit", "pwd", "echo"):
        argv, redir = stages[0]  # builtin: cd/exit must affect THIS process
        if redir:
            with open(redir[1], "w" if redir[0] == ">" else "a") as f:
                run_builtin(argv, f)
        else:
            run_builtin(argv, sys.stdout)
        return
    # pipeline or single external command
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # shell survives Ctrl-C
    try:
        children, prev = [], None
        for i, (argv, redir) in enumerate(stages):
            rfd, wfd = os.pipe() if i < len(stages) - 1 else (None, None)
            children.append(spawn(argv, redir, prev, wfd))
            if prev is not None:
                os.close(prev)
            if wfd is not None:
                os.close(wfd)
            prev = rfd
        for pid in children:
            os.waitpid(pid, 0)
    finally:
        signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    while True:
        try:
            name = os.path.basename(os.getcwd()) or "/"
            line = input(f"\033[1;32m{name}\033[0m $ ")
        except KeyboardInterrupt:  # Ctrl-C at the prompt
            print()
            continue
        except EOFError:  # Ctrl-D
            print()
            break
        if not line.strip():
            continue
        try:
            run_line(line)
        except SystemExit:
            break
        except Exception as e:  # a bad line must never kill the shell
            print(f"myshell: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
