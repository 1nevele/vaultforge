# 002 — Plan

1. Replace `.github/workflows/claude-implement.yml` with `claude-fix.yml`: `@claude`
   comment/review triggers only, per-thread concurrency, `--max-turns 15`, 20-minute
   timeout, scope-limiting system prompt, `id-token: write` (from closed PR #15).
2. Update `CLAUDE.md`, `AGENTS.md`, `docs/claude-web-handoff.md` and
   `docs/code-review.md` to describe the two routes, the label lock and the absence
   of an automated review gate.
3. Create the cloud scheduled task (outside the repository) with a standalone prompt
   implementing CA-001–CA-004. Record its name and schedule in the handoff doc, not
   its internal identifiers.
4. Repository cleanup: close superseded PRs #9, #10, #11, #15 and delete their
   branches. PR #9's review tooling stays recoverable from the closed PR.
