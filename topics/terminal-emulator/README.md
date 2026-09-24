---
title: "Terminal Emulator"
category: "operating-systems"
difficulty: "intermediate"
tags: [terminal, pty, ansi]
related: [device-driver-uart, markdown-renderer, ipc-pipes-sockets]
---

# Terminal Emulator

A terminal emulator is the window your shell lives in: it draws a character grid, interprets ANSI escape sequences, and bridges keystrokes to a pseudoterminal. Building one teaches you the surprisingly deep stack under every terminal window — ptys, termios, escape codes, and the line discipline.

## Core concepts

- **The pty pair** — A pseudoterminal is a master/slave device pair: the shell runs on the slave side thinking it's a real terminal, while your emulator reads/writes the master side. `posix_openpt()` + `grantpt()` + `unlockpt()` create them.
- **The line discipline** — The kernel layer between keystrokes and programs: it buffers a line, handles backspace (erase), Ctrl-C (SIGINT), Ctrl-Z (suspend), and echo — in "canonical" mode. Raw mode (what vim uses) bypasses it.
- **termios** — The `struct termios` settings controlling all of the above: input flags, output processing, control chars, local modes (ICANON, ECHO). `stty` is just a CLI for termios.
- **ANSI escape sequences** — The control language: `\x1b[<row>;<col>H` moves the cursor, `\x1b[31m` sets red, `\x1b[2J` clears the screen. ECMA-48 standardizes them; xterm's docs are the de facto reference.
- **The alternate screen** — Full-screen apps (vim, less) switch to a separate buffer with `\x1b[?1049h` and restore on exit — that's why quitting vim brings your shell history back.
- **Scrollback and the grid** — The emulator keeps a grid of cells (character + attributes) plus scrollback history; rendering is just painting changed cells, the ancestor of all retained-mode UIs.
- **Unicode, wide chars, and ambiguous width** — CJK characters occupy two cells, combining marks occupy zero, and emoji are a minefield. Correct width handling (`wcwidth`) separates toy terminals from real ones.

## How it works

Your emulator opens a pty master, forks, and the child calls `setsid()`, opens the slave as its controlling terminal, duplicates it onto stdin/stdout/stderr, and execs the shell. The parent (your emulator) runs an event loop: bytes arriving from the pty master are fed to an escape-sequence parser — a small state machine (ground, escape, CSI, parameters) — which updates the cell grid (write chars, move cursor, change colors, scroll). Changed regions are repainted to the window. Keystrokes go the other way: the emulator translates GUI key events into bytes (including escape-prefixed sequences for arrows, e.g. `\x1b[A`) and writes them to the master; the kernel line discipline delivers them to the shell. Window resizes send SIGWINCH to the foreground process group so full-screen apps redraw.

## Build milestones

1. Build the pty plumbing: open a pty pair, spawn `/bin/sh` on the slave, and relay bytes between the master and your own stdin/stdout — a working (ugly) terminal in ~100 lines.
2. Add raw-mode input handling on your side and correct Ctrl-C/Ctrl-D behavior through the line discipline.
3. Write the escape-sequence state machine: handle cursor movement, colors (SGR), and clear-screen; test against `vim` and `htop`.
4. Render to a real window (SDL, or a web canvas): a monospace cell grid, cursor, and damage-based repainting.
5. Implement the alternate screen buffer and scrollback (10k lines), with Shift+PageUp navigation.
6. Handle SIGWINCH-driven resizes, UTF-8 decoding, and `wcwidth`-correct double-width characters — then run `ncurses` test programs as torture tests.

## Best resources

- [The TTY Demystified (Linus Åkesson)](https://www.linusakesson.net/programming/tty/index.php) — the single best explanation of ptys, the line discipline, and job control.
- [XTerm Control Sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html) — the de facto reference for every escape sequence your parser must handle.
- [ECMA-48 standard](https://ecma-international.org/publications-and-standards/standards/ecma-48/) — the official standard behind ANSI escape codes.
- [pty(7) man page](https://man7.org/linux/man-pages/man7/pty.7.html) — pseudoterminal semantics and the openpt/grantpt API.
- [termios(3) man page](https://man7.org/linux/man-pages/man3/termios.3.html) — every flag controlling canonical/raw mode, echo, and signals.
- [Build your own terminal (st — suckless)](https://st.suckless.org/) — the minimal real terminal emulator; ~5000 lines of readable C to study.
- [VT100.net](https://vt100.net/) — historical DEC documentation for the terminal all emulators descend from.

## Stretch ideas

- Add sixel or Kitty graphics protocol support to display images inline in the terminal.
- Implement tmux-style multiplexing: multiple pty sessions, detach/reattach, and window splitting in your emulator.
