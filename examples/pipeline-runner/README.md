# Example: DevOps — Pipeline Runner

**[▶ Try it live](https://byoe-pipeline.netlify.app)**

A miniature CI system in one file: **parse → schedule → execute → report**.
Edit the pipeline YAML, hit run, and watch stages stream logs like GitHub Actions.

Example project for the [devops learning path](../../topics/ci-runner/).

## What it teaches

- **Pipeline parsing**: YAML-ish stages become an execution plan.
- **Stage lifecycle**: queued → running → passed/failed, with timings.
- **Fail-fast semantics**: a non-zero exit stops the pipeline — the core idea of CI.
- **Log streaming**: timestamped per-command output, like a real runner.

Try the **FAIL DEMO** button to watch a red pipeline halt before deploy.

## Exercises

1. Run **independent stages in parallel** (fan-out/fan-in).
2. Add **caching**: skip `install` if the lockfile hash is unchanged.
3. Add **artifacts**: pass a build output from one stage to the next.
