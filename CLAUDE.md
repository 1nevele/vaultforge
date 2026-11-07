# Vaultforge — Claude Code on the web

Read `AGENTS.md`, `.specify/memory/constitution.md`, `docs/claude-web-handoff.md`, the assigned issue and its canonical spec/plan/tasks. Read the project rules before project changes.

Claude Code **on the web** implements application code. The operator (host) gives direction, CodeRabbit reviews PRs, and Eleven (their Hermes agent) only checks merge eligibility (`docs/eleven-maintainer.md`). There are two execution routes (`specs/002-vaultforge-claude-automation`):

- **Scheduled issue execution:** a Claude cloud scheduled task starts a fresh web session that takes the lowest-numbered open issue labelled both `claude:scheduled` and `status:ready`, labels it `status:in-progress`, opens a PR with real evidence, and stops. If any `claude:scheduled` issue is already `status:in-progress`, it does nothing. Issues without `claude:scheduled` are never picked up.
- **Small fixes:** `@claude` comments run `.github/workflows/claude-fix.yml` for small, self-contained fixes only.

No automatic merge, approval, issue closing or blocked-work continuation.

Sentinel lives under `projects/sentinel/`. Historical project-owned paths are relative to that directory; shared workflow/spec files stay at the root. Keep one canonical `specs/<NNN>-<project>-<feature>/` packet, not a second Superpowers planning tree.

## Native development skills

This repository carries three pinned Superpowers skills, not the full plugin:
- `verification-before-completion`: load before claiming tests, work or acceptance passed. Non-negotiable: run the command, read the output, then make the claim.
- `test-driven-development`: load before implementing behavior with real decisions in it (logic, ordering, boundary or authority rejection, security invariants, edge cases, adversarial inputs). Watch each such test fail before making it pass. Purely declarative code (schemas, config, glue) needs the schema plus a few adversarial tests, not test-first ritual.
- `systematic-debugging`: load when tests fail or behavior is unexpected.

Use the native Skill tool when available. Reading a file manually is only a documented fallback, not proof that native discovery worked. These unnamespaced skills live at `.claude/skills/<name>/SKILL.md`; do not invoke `superpowers:<name>` or assume plugin hooks exist. Use the nine official `speckit-*` skills for the existing spec/plan/task packet.

## Code review

Two layers: Claude reviews its own diff in-session before pushing, and CodeRabbit reviews the PR. There is no Superpowers review skill and no CI review job.

- **Before every push from a web session** (scheduled or interactive): run the built-in `/code-review` on the diff, and `/security-review` as well when the change touches authority, permissions, secrets, workflows, untrusted-input parsing or an execution surface. Fix blocking findings, or list each unfixed one with its reason in the PR's verification section, naming the reviewed commit.
- These reviewers run as subagents in a fresh context, but the authoring session triggers and reports them: the PR record is author-reported evidence. CodeRabbit is the independent reviewer whose approval counts (`docs/code-review.md`, `docs/eleven-maintainer.md`). Address CodeRabbit findings on the PR. Never approve or merge.
- The `@claude` small-fix workflow (`claude-fix.yml`) is exempt: it runs in GitHub Actions, where this review is not set up; CodeRabbit covers its PRs.
- The required reviewer is the built-in `code-review` skill; record that name in the PR. The operator may enable Anthropic plugins on their account (`security-guidance` for automatic diff/commit review, `claude-security` for deep scans). They are optional, supplement rather than replace `/code-review`, and are not committed to this repository. Confirm one actually loaded in the session before relying on or citing it.

**Before application work:** follow `docs/claude-web-skill-smoke.md`. Report actual discovered names and exercise a benign skill. If discovery is unavailable, stop with that blocker; do not silently install a plugin or substitute an unlabeled manual read.

No startup installers, visual companions, telemetry, provider evaluation harnesses, global installers or permission bypasses. Bundled helper scripts are not automatically authorized to execute. Review necessity and effects before any explicit use. This setup does not authorize live product providers, targets or infrastructure changes.
