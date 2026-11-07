# Vaultforge — Claude Code on the web

Read `AGENTS.md`, `.specify/memory/constitution.md`, `docs/claude-web-handoff.md`, the assigned issue and its canonical spec/plan/tasks. Read the project rules before project changes.

Claude Code **on the web** implements application code; it is the executor for the operator and Eleven (their Hermes agent), who prepare specifications, issues and review. There are two execution routes (`specs/002-vaultforge-claude-automation`):

- **Scheduled issue execution:** a Claude cloud scheduled task starts a fresh web session that takes the lowest-numbered open issue labelled both `claude:scheduled` and `status:ready`, labels it `status:in-progress`, opens a PR with real evidence, and stops. If any `claude:scheduled` issue is already `status:in-progress`, it does nothing. Issues without `claude:scheduled` are never picked up.
- **Small fixes:** `@claude` comments run `.github/workflows/claude-fix.yml` for small, self-contained fixes only.

No automatic merge, approval, issue closing or blocked-work continuation.

Sentinel lives under `projects/sentinel/`. Historical project-owned paths are relative to that directory; shared workflow/spec files stay at the root. Keep one canonical `specs/<NNN>-<project>-<feature>/` packet, not a second Superpowers planning tree.

## Lead and subagents

The lead session runs Opus at high effort (`.claude/settings.json`) and delegates bounded work to project subagents in `.claude/agents/`: `scout` (read-only research, Haiku), `implementer` (one tasks.md item, test-first, assigned paths only, Haiku), `verifier` (runs checks, read-only, Haiku) and `reviewer` (independent review, Sonnet). At most three subagents run at once, matching AGENTS.md. Give each a narrow brief; do not pass a `model` override when delegating; keep shared manifests, lockfiles, contracts, specs and integration with the lead.

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
