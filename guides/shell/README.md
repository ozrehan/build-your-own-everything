# Build Your Own Shell

A tiny Unix shell in ~150 lines of Python. You'll learn how shells turn
what you type into running processes — parsing, `fork`/`exec`, pipes,
redirection, and signal handling.

## What you'll build

`shell.py` (stdlib only: `os`, `shlex`, `signal`, `subprocess`-free) with:

- Interactive prompt showing the current directory
- External commands via `fork` + `execvp` (PATH lookup works)
- Builtins: `cd`, `exit`, `echo`, `pwd`
- Single pipes: `cmd1 | cmd2` (quote-aware splitting)
- Output redirection: `>` and `>>`, plus `~` expansion
- Ctrl-C never kills the shell — it kills only the running child

## How it works

1. **Read.** `input()` shows a `dir$ ` prompt and reads a line. `shlex.split`
   tokenizes it respecting quotes.
2. **Parse.** The token list is scanned for `|` (pipe) and `>`/`>>`
   (redirection); builtins are detected first.
3. **Builtins.** `cd`/`exit` must run in the shell process itself (a child
   can't change the parent's directory). `echo`/`pwd` also work inside pipes.
4. **Fork/exec.** For external commands the shell `fork()`s; the child
   `dup2()`s pipe ends / redirect targets onto stdout, then `execvp()`s the
   program. The parent `wait()`s.
5. **Signals.** `SIGINT` is ignored in the shell while children run (children
   get the default disposition), and `KeyboardInterrupt` at the prompt just
   prints a fresh prompt.

## Run it

```sh
cd guides/shell
python3 shell.py
```

```sh
~/projects$ echo hello | tr a-z A-Z
HELLO
~/projects$ ls | wc -l
42
~/projects$ echo hi > out.txt
~/projects$ cd /tmp
/tmp$ exit
```

## Test it

```sh
python3 test_shell.py   # drives the shell via pipes: builtins, pipes, redirects
```

## Stretch exercises

1. Support multiple pipes: `a | b | c`.
2. Add input redirection `<` and `2>` stderr redirection.
3. Add job control: `cmd &` to background, `jobs` to list.

## Further reading

- [Tutorial - Write a Shell in C](https://brennan.io/2015/01/16/write-a-shell-in-c/) — the classic step-by-step
- [Let's build a shell! (C)](https://github.com/kamallanghanoja/shell) — minimal shell tutorial
- [Build Your Own Shell (Rust)](https://www.joshmcguigan.com/blog/build-your-own-shell/) — same concepts in Rust
