# Sentinel

Local-first cyber command center for authorized lab security work.

**Status: specification and development-tooling setup. No application or worker execution is implemented.**

## Working method

Requirements → spec review → implementation plan → dependency-ordered tasks → failing tests → implementation → independent spec/code review → verified pull request.

- Project principles: [.specify/memory/constitution.md](.specify/memory/constitution.md).
- First slice: [specs/000-development-workflow/spec.md](specs/000-development-workflow/spec.md).
- Plan and task status: [plan](specs/000-development-workflow/plan.md), [tasks](specs/000-development-workflow/tasks.md).
- Development tools and limitations: [docs/development-workflow.md](docs/development-workflow.md).
- Implementation guidance: [AGENTS.md](AGENTS.md).

Jev remains the bounded selector; CDMs are advisory evidence transformations. RAPTOR is the first tool-engine candidate to evaluate, not a selected or validated backend. Strix remains an alternative. Neither engine owns mission state or authorization.

No targets, provider credentials, VM engines or host-network changes are configured. A passing development check will not establish containment. Private repository; no open-source license has been chosen for Sentinel.
