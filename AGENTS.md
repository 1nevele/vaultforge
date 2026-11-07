# Vaultforge agent rules

## Ownership and entry points

Claude Code **on the web** implements application code. For Sentinel, host gives direction, Claude owns development work and issue management within that direction, CodeRabbit reviews, and Eleven only checks merge eligibility, merges eligible PRs and notifies host under `docs/eleven-maintainer.md`. Eleven does not independently manage issues/specs, dispatch work or submit code reviews. Do not replace Claude with local coding or a local Claude CLI session. Unaccepted local scaffolding is not an implementation baseline.

Execution routes (`specs/002-vaultforge-claude-automation`): issues opted in with `claude:scheduled` plus `status:ready` run through the scheduled Claude cloud task, one at a time, locked by `status:in-progress` on a `claude:scheduled` issue; `@claude` comments run `.github/workflows/claude-fix.yml` for small fixes only. There is no automated code-review gate.

Read `.specify/memory/constitution.md`, `docs/development-workflow.md`, the assigned GitHub issue and its root `specs/<NNN>-<project>-<feature>/` packet. For Sentinel, read `projects/sentinel/AGENTS.md` and its plans/research. These rules supersede historical paths/executor instructions. Never initialize a second Git repository inside a project.

## Specification-driven delivery

- Requirements/acceptance scenarios → reviewed spec → plan → tasks → RED/GREEN implementation → independent spec/code review → verified PR.
- Keep one canonical root feature packet with project name in the directory; no competing Superpowers plan tree.
- Verify repository-provided skill discovery in the actual Claude web session. Hermes plugin activation is not web activation. Missing optional plugin support does not remove spec/TDD/review requirements.
- Maximum Lead plus three active agents; exclusive paths. Only the Claude lead edits shared manifests/lockfiles/contracts.
- Start dependent issues only after accepted prerequisites. Claude stops at the assigned PR; no Claude automatic merge or whole-backlog continuation. Eleven's bounded Sentinel maintainer authority is defined in `docs/eleven-maintainer.md`; sensitive changes still require host approval.

## Safety and truthfulness

- No secrets, private host paths, infrastructure credentials, live provider spend, target operations, VM/network/account changes, public publication or destructive cleanup without applicable explicit authority.
- Do not disable scans or broaden permissions. Any exceptional tooling authorization must be separately scoped to the exact harness, revision and helper; it is not transferable.
- Do not launch visual companions, telemetry, upstream provider evals or diagnostic exports as setup side effects.
- Preserve original evidence and lineage. Hashes identify bytes, not truth; models cannot mint authorization or verified findings.
- Record real tests, skips and blockers. Demo/CI results do not establish live integration or containment.
- Read back external writes. Claim cloud dispatch only with an actual session handle and repository/task readback.
