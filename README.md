# Vaultforge

A monorepo for projects, their specifications and the agent workflow that builds them.

The host gives direction, Eleven (the host's Hermes agent) maintains and merges, and
Claude Code on the web implements one issue per session and PR. How that works:
[docs/operating-model.md](docs/operating-model.md). Claude's instructions are in
[CLAUDE.md](CLAUDE.md); safety rules for every agent in [AGENTS.md](AGENTS.md).

- [Sentinel](projects/sentinel/README.md), the first project.

## Layout

```text
.claude/skills/   Claude skills: three Superpowers skills and nine Spec Kit skills
.specify/         Spec Kit scripts, templates and the constitution
specs/            feature packets: <NNN>-<project>-<feature>
projects/         product code and docs, one directory per project
docs/             the operating model
tools/            Eleven's PR poller, its tests and third-party licenses
```

Do not commit credentials, runtime databases or private infrastructure configuration.

**Status:** no Sentinel application logic, deployment or security gate is implemented yet.

Original Vaultforge material is licensed under Apache-2.0 ([LICENSE](LICENSE)); bundled
upstream assets keep their own licenses ([tools/README.md](tools/README.md)).
