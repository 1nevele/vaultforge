# Sentinel implementation rules

Read docs/plans/, docs/development-workflow.md, .specify/memory/constitution.md and the current feature spec/plan/tasks before changes. This is tooling/specification work; no application, runtime, target access, authority deployment or security gate has passed.

Spec-driven development is required: review requirements and acceptance scenarios, then plan/tasks, then test-first implementation. Use one canonical spec/plan/task source. Tooling activation is not established by this historical document. Do not force blocked installations, disable scans or imply unverified activation. Any exception requires separately scoped explicit authority.

- Maximum four active agents including Lead; explicit exclusive paths.
- Lead alone changes root configuration, package versions, lockfile, packages/contracts/, authority, shared fixtures and acceptance tests.
- Agent A owns mission-service, Jev/CDM/MCP and evidence integrations; B owns web; C owns worker/runtime and substrate feasibility. Start dependent work only after accepted contracts.
- Use tests-first RED/GREEN cycles. Record actual commands and blockers. No claimed passes for skipped integrations.
- Models choose frozen IDs and produce untrusted derived data. Never grant authorization or verified findings from model output.
- RAPTOR is the first tool-engine candidate to evaluate, not an approved runtime. Strix remains an alternative. Neither owns mission lifecycle or grants.
- No arbitrary target execution, credential copying, infrastructure/network changes, global tooling upgrade, automatic merge, public publication, or real provider spend.
- Validate shape separately from authentication/authorization. No pure TypeScript function establishes an OS or network boundary.
- Keep raw observations separate from derived summaries; hashes establish identity, not truth.
- No secrets, runtime databases, local absolute paths, or private infrastructure details in commits. CI uses no provider credentials.
- Read back every GitHub write. Independent review before application-code publication; do not equate CI with containment.
