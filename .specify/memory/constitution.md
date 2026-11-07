# Vaultforge constitution

Version 1.0.0 · Updated 2026-11-07 · Scope: every project.

1. **Specs for features.** Each product feature has one `specs/<NNN>-<project>-<feature>/`
   packet (requirements, acceptance, plan, tasks), updated before material code changes.
   Process changes edit `docs/operating-model.md` instead. Never invent human sign-off.
2. **Clear roles.** The host directs, Eleven maintains and merges, Claude implements;
   see `docs/operating-model.md`. Claude never merges or approves.
3. **Evidence before claims.** Real tests, test-first for logic and security invariants;
   `/code-review` before every push; report what ran, what was skipped and what blocked.
4. **Least authority.** No secrets, provider spend, live targets, infrastructure changes
   or exports without explicit host authority. Pin tool sources and keep their licenses.
5. **Project isolation.** Product code under `projects/<name>/`; share code only when a
   second real consumer needs it.
6. **Data integrity.** Preserve originals and lineage. Model output cannot create trusted
   outcomes. No committed secrets or runtime databases.
7. **Stay lean.** Decide reversible choices within scope; escalate only security, scope,
   cost or access questions.
