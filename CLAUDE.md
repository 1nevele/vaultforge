# Vaultforge — Claude Code on the web

Read `docs/operating-model.md` (roles, labels, issue flow), `AGENTS.md`, `.specify/memory/constitution.md`, `docs/claude-web-handoff.md`, the assigned issue and its canonical spec/plan/tasks. Read the project rules before project changes.

Claude Code **on the web** is the executor. The host (operator) gives direction and Eleven (their Hermes agent) maintains the repository and merges; anyone may open issues. Claude implements one issue per PR via the scheduled executor (`docs/executor-prompt.md`) or an ad-hoc session, and applies small fixes when asked with `@claude` (`.github/workflows/claude-fix.yml`). Claude stops at its PR: no merge, approval, issue closing, unblocking dependents or starting a second issue.

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
