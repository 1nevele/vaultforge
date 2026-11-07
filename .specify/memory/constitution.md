# Vaultforge constitution

Version 0.5.0 · Updated 2026-11-07 · Scope: every project.

Principles only. Roles, review and the issue flow, including temporary decisions such
as the current CodeRabbit pause, are defined once in `docs/operating-model.md`.

1. **Specs govern code.** One root `specs/<NNN>-<project>-<feature>/` packet per feature: requirements, acceptance, plan, tasks. Update material changes before code; never invent human sign-off.
2. **Clear roles.** The host gives direction and decides sensitive changes. Eleven maintains the repository and merges. Claude Code on the web implements application code. PR review, including temporary host decisions about it, is defined in `docs/operating-model.md`. Anyone may open issues. Local tool activation or a GitHub issue is not cloud dispatch.
3. **Evidence before claims.** RED/GREEN/REFACTOR for behavioral logic, invariants and adversarial cases (declarative schemas/config need adversarial tests, not test-first ritual), and fresh-context reviewer agents (`/code-review`) before every push from a web session, run after implementation agents finish (scope and exemptions: `docs/operating-model.md`). Author-run review is evidence, not approval. Record commands, results, skips and blockers. Demo/CI is not live-integration or containment proof.
4. **Bounded collaboration.** Lead plus at most three active agents that edit files (read-only reviewer subagents do not count), exclusive paths, accepted prerequisites, serialized shared config/contracts. Claude works one assigned issue, follows its PR through review and never merges; merges follow the maintainer gates.
5. **Least authority.** Tooling is not product runtime. No copied credentials, host-service changes, permission bypass, target operations, provider spend or exports without applicable authority.
6. **Project isolation.** Product code/docs under projects/<name>. Share abstractions only when real consumers justify them; do not build a generic platform because this is a monorepo.
7. **Data integrity.** Preserve originals and transformation lineage. Model confidence/prose cannot create trusted outcomes. No committed secrets or runtime databases.
8. **Scoped tooling trust.** Pin sources and preserve licenses. Verify chosen harness. Do not transfer scan overrides across packages/harnesses or silently enable helpers/telemetry.
9. **Low operator overhead.** Resolve reversible choices within scope; escalate only material security, scope, cost or access issues. Reuse supplied plans instead of repeating product discovery.
