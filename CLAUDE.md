# Vaultforge — Claude Code on the web

Read `AGENTS.md`, `.specify/memory/constitution.md`, `docs/claude-web-handoff.md`, the assigned issue and its canonical spec/plan/tasks. Read the project rules before project changes.

Claude Code **on the web** implements application code. Eleven prepares specifications, issues and review. Work only the first ready issue, open a PR with real evidence, and stop: no automatic merge or blocked-work continuation.

Sentinel lives under `projects/sentinel/`. Historical project-owned paths are relative to that directory; shared workflow/spec files stay at the root. Keep one canonical `specs/<NNN>-<project>-<feature>/` packet, not a second Superpowers planning tree.

## Native development skills

This repository carries five pinned Superpowers skills, not the full plugin:
- `test-driven-development`: load before implementing a feature or fix.
- `systematic-debugging`: load when tests fail or behavior is unexpected.
- `requesting-code-review`: load before handing off completed work; use its bundled reviewer prompt with a fresh general-purpose reviewer if available.
- `receiving-code-review`: load before acting on review feedback.
- `verification-before-completion`: load before claiming tests, work or acceptance passed.

Use the native Skill tool when available. Reading a file manually is only a documented fallback, not proof that native discovery worked. These unnamespaced skills live at `.claude/skills/<name>/SKILL.md`; do not invoke `superpowers:<name>` or assume plugin hooks exist. Use the nine official `speckit-*` skills for the existing spec/plan/task packet.

**Before application work:** follow `docs/claude-web-skill-smoke.md`. Report actual discovered names and exercise a benign skill. If discovery is unavailable, stop with that blocker; do not silently install a plugin or substitute an unlabeled manual read.

No startup installers, visual companions, telemetry, provider evaluation harnesses, global installers or permission bypasses. Bundled helper scripts are not automatically authorized to execute. Review necessity and effects before any explicit use. This setup does not authorize live product providers, targets or infrastructure changes.
