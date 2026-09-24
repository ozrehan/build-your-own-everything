# Contributing

Thanks for helping build the biggest hands-on collection of "build it from
scratch" guides on GitHub. There are two ways to contribute:

## 1. Add a tutorial link to the index

Found a great step-by-step guide for re-creating a technology from scratch?
Send a PR that adds it to the right category in `README.md`:

- One line, format: `* **Language**: _Title_ — link`
- Mark videos with `[video]`, PDFs with `[pdf]`
- Put the best/most complete guides first in each category
- Check the link works and isn't already listed

## 2. Add a guide to `guides/`

Original, tested tutorials live in `guides/<slug>/`. Each guide must have:

```
guides/<slug>/
├── README.md        # tutorial: what, how it works, run, test, exercises
├── <solution>.py    # clean, commented, stdlib-only (Python preferred)
└── test_<name>.py   # runnable via `python3 test_<name>.py`, must pass
```

Guide README template:

```md
# Build Your Own <X>
<one-line pitch>

## What you'll build
## How it works
## Run it
## Test it
## Stretch exercises
## Further reading
```

Rules for guides:

- **Stdlib only** — no pip installs, so anyone can run it anywhere.
- **~200 lines max** for the solution — small enough to read in one sitting.
- **Real tests** — `python3 test_*.py` must pass in CI.
- **Teach, don't just show** — the README must explain the key ideas,
  not just dump code.

## Fixing links

The link-checker workflow flags dead links. PRs fixing or replacing them
are always welcome — use `Fixes #<issue>` if one exists.

## Code of conduct

Be kind. Read `CODE_OF_CONDUCT.md`. Maintainers may remove contributions
that don't meet the quality bar, with an explanation.
