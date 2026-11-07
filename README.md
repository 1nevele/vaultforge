# Vaultforge

A monorepo for projects, shared agent workflows and specifications.

Original Vaultforge material is licensed under Apache-2.0; see [LICENSE](LICENSE).
Bundled upstream assets retain their [own licenses](tools/README.md).

## Development ownership

**The host gives direction, Eleven (the host's Hermes agent) maintains and merges, and Claude Code on the web implements.** Anyone may open issues; review and the rest are in the operating model. The scheduled executor lives in the host's claude.ai account; nothing in this repository starts a cloud session.

- [Operating model: roles, labels and issue flow](docs/operating-model.md).
- [Claude entry point](CLAUDE.md) and [monorepo rules](AGENTS.md).
- [Development workflow](docs/development-workflow.md).
- [CI, branch protection, licensing and publication policy](docs/code-review.md).
- [Monorepo setup specification](specs/000-vaultforge-workflow/spec.md).
- [Claude-web handoff](docs/claude-web-handoff.md).
- [Required real-session skill smoke check](docs/claude-web-skill-smoke.md).
- [Sentinel project](projects/sentinel/README.md).

## Layout

```text
.claude/                   repository-local Claude skills/configuration
.specify/                  shared specification toolkit and constitution
specs/                     feature packets: <NNN>-<project>-<feature>
projects/
  sentinel/                Sentinel's plans, research, project rules and future code
docs/                      shared workflow, handoff and setup evidence
tools/                     pinned development assets, provenance and offline checks
```

Keep one canonical spec/plan/task set per feature. Shared tooling is not a production runtime dependency. Repository-private is not secret-safe: do not commit credentials, runtime databases or private infrastructure configuration.

**Status:** monorepo/tooling setup only; no Sentinel application logic, worker deployment, assessment or product security gate is implemented or passed. Activation in another harness is not proof of Claude-web activation.
