# Vaultforge constitution

Version 0.4.0 · Updated 2026-11-07 · Scope: every project.

**Temporary PoC amendment (host decision, 2026-11-07):** CodeRabbit is paused and
its approval is not required to merge. Its status and bot-only review artifacts do
not independently block merges; known defects/security concerns remain actionable.
The precise exception is in `docs/eleven-maintainer.md`. Fresh-context spec/code
review, real verification, required CI and head-specific host approval for sensitive
changes remain required. This overrides CodeRabbit role/approval requirements in
this constitution and other repository documents until the host re-enables it.

1. **Specs govern code.** One root `specs/<NNN>-<project>-<feature>/` packet per feature: requirements, acceptance, plan, tasks. Update material changes before code; never invent human sign-off.
2. **Clear roles.** The host gives direction and decides sensitive changes. Eleven maintains the repository and merges. Claude Code on the web implements application code. CodeRabbit reviews. Anyone may open issues. See `docs/operating-model.md`. Local tool activation or a GitHub issue is not cloud dispatch.
3. **Evidence before claims.** RED/GREEN/REFACTOR for behavioral logic, invariants and adversarial cases (declarative schemas/config need adversarial tests, not test-first ritual), and fresh-context reviewer agents (`/code-review`) before every push from a web session, run after implementation agents finish (the `@claude` small-fix workflow is exempt; CodeRabbit reviews its PRs, and while CodeRabbit is paused (PoC amendment), they need the fresh-context review the merge gate in `docs/eleven-maintainer.md` requires). Author-run review is evidence, not approval. Record commands, results, skips and blockers. Demo/CI is not live-integration or containment proof.
4. **Bounded collaboration.** Lead plus at most three active agents that edit files (read-only reviewer subagents do not count), exclusive paths, accepted prerequisites, serialized shared config/contracts. Claude works one assigned issue, follows its PR through review and never merges; merges follow the maintainer gates.
5. **Least authority.** Tooling is not product runtime. No copied credentials, host-service changes, permission bypass, target operations, provider spend or exports without applicable authority.
6. **Project isolation.** Product code/docs under projects/<name>. Share abstractions only when real consumers justify them; do not build a generic platform because this is a monorepo.
7. **Data integrity.** Preserve originals and transformation lineage. Model confidence/prose cannot create trusted outcomes. No committed secrets or runtime databases.
8. **Scoped tooling trust.** Pin sources and preserve licenses. Verify chosen harness. Do not transfer scan overrides across packages/harnesses or silently enable helpers/telemetry.
9. **Low operator overhead.** Resolve reversible choices within scope; escalate only material security, scope, cost or access issues. Reuse supplied plans instead of repeating product discovery.
