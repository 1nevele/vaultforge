# Vaultforge constitution

Version 0.3.0 · Updated 2026-11-07 · Scope: every project.

1. **Specs govern code.** One root `specs/<NNN>-<project>-<feature>/` packet per feature: requirements, acceptance, plan, tasks. Update material changes before code; never invent human sign-off.
2. **Clear executor.** Claude Code on the web implements application code. Claude also reviews its own diffs in-session before pushing; CodeRabbit reviews PRs and Eleven checks merge eligibility (`docs/eleven-maintainer.md`). Local tool activation or a GitHub issue is not cloud dispatch.
3. **Evidence before claims.** RED/GREEN/REFACTOR for behavioral logic, invariants and adversarial cases (declarative schemas/config need adversarial tests, not test-first ritual), and fresh-context reviewer agents (`/code-review`) before push, run after implementation agents finish. Those read-only reviewer subagents do not count toward §4's cap, which governs agents that edit files. Author-run review is evidence, not approval. Record commands, results, skips and blockers. Demo/CI is not live-integration or containment proof.
4. **Bounded collaboration.** Lead plus at most three active agents, exclusive paths, accepted prerequisites, serialized shared config/contracts. Stop at assigned PR; no automatic merge.
5. **Least authority.** Tooling is not product runtime. No copied credentials, host-service changes, permission bypass, target operations, provider spend or exports without applicable authority.
6. **Project isolation.** Product code/docs under projects/<name>. Share abstractions only when real consumers justify them; do not build a generic platform because this is a monorepo.
7. **Data integrity.** Preserve originals and transformation lineage. Model confidence/prose cannot create trusted outcomes. No committed secrets or runtime databases.
8. **Scoped tooling trust.** Pin sources and preserve licenses. Verify chosen harness. Do not transfer scan overrides across packages/harnesses or silently enable helpers/telemetry.
9. **Low operator overhead.** Resolve reversible choices within scope; escalate only material security, scope, cost or access issues. Reuse supplied plans instead of repeating product discovery.
