# Vaultforge agent rules

## Ownership and entry points

Roles, labels and the issue flow are defined once in `docs/operating-model.md`: the host gives direction, Eleven maintains the repository and merges (`docs/eleven-maintainer.md`), Claude Code **on the web** implements, CodeRabbit reviews, and anyone may open issues. Do not replace Claude with local coding or a local Claude CLI session. Unaccepted local scaffolding is not an implementation baseline.

Read `.specify/memory/constitution.md`, `docs/development-workflow.md`, the assigned GitHub issue and its root `specs/<NNN>-<project>-<feature>/` packet. For Sentinel, read `projects/sentinel/AGENTS.md` and its plans/research. These rules supersede historical paths/executor instructions. Never initialize a second Git repository inside a project.

## Specification-driven delivery

- Requirements/acceptance scenarios → reviewed spec → plan → tasks → RED/GREEN implementation (test-first for behavioral logic, invariants and adversarial cases) → in-session `/code-review` before push → CodeRabbit PR review → verified PR.
- Keep one canonical root feature packet with project name in the directory; no competing Superpowers plan tree.
- Verify repository-provided skill discovery in the actual Claude web session. Hermes plugin activation is not web activation. Missing optional plugin support does not remove spec/TDD/review requirements.
- Maximum Lead plus three active agents that edit files (read-only reviewer subagents do not count); exclusive paths. Only the Claude lead edits shared manifests/lockfiles/contracts.
- Start dependent issues only after accepted prerequisites. Claude follows its assigned PR through CI and review; no Claude merge or whole-backlog continuation. Eleven merges under `docs/eleven-maintainer.md`; sensitive changes (`.github/CODEOWNERS` paths and the constitution's reserved categories) still require the host's explicit go-ahead.

## Safety and truthfulness

- No secrets, private host paths, infrastructure credentials, live provider spend, target operations, VM/network/account changes, public publication or destructive cleanup without applicable explicit authority.
- Do not disable scans or broaden permissions. Any exceptional tooling authorization must be separately scoped to the exact harness, revision and helper; it is not transferable.
- Do not launch visual companions, telemetry, upstream provider evals or diagnostic exports as setup side effects.
- Preserve original evidence and lineage. Hashes identify bytes, not truth; models cannot mint authorization or verified findings.
- Record real tests, skips and blockers. Demo/CI results do not establish live integration or containment.
- Read back external writes. Claim cloud dispatch only with an actual session handle and repository/task readback.
