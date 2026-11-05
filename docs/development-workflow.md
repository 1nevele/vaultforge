# Development workflow and tooling review

As of 2026-11-05. Scope: Sentinel development, not worker execution.

## Proposed division

Spec Kit provides the specification structure; Superpowers provides implementation, test-first debugging and independent review. Existing product/execution plans and research are inputs. There is one canonical feature spec/plan/task set, not parallel planning trees.

## Historical Superpowers review scope

Upstream inspected: obra/superpowers, commit `22f0b463e7a5e579904dd6211a520321035526f7`, MIT, Hermes manifest 7.0.2.

Review native registration/bootstrap and skill-triggered script surfaces at the pin. Review examples, migration scripts, test harnesses and optional helpers as executable content, not merely documentation. A scoped source review is not whole-package security assurance or proof of activation.

Do not disable scans, force a blocked installation, copy plugins manually or restart services as setup side effects. Any exceptional tooling action requires separately scoped authority. Optional visual companions, telemetry and provider-backed harnesses are not authorized by adopting this workflow.

## Spec Kit status

Inspected github/spec-kit commit `99d10403a2681981be98bd372fa412045180d105` (MIT). Repository conventions are adopted in `.specify/memory/` and `specs/`. This historical document does not establish CLI or native integration activation; verify actual commands before claiming availability. Tool installation should remain local/pinned rather than silently changing global Python or Node packages.

## Review gates

Spec completeness → scoped implementation plan → failing behavioral test → minimal implementation → passing checks → independent specification compliance and code review → PR evidence. Never claim application tests or CI pass when only configuration exists.

## Primary references

- https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7
- https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/.hermes-plugin/plugin.yaml
- https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/.hermes-plugin/__init__.py
- https://github.com/github/spec-kit/tree/99d10403a2681981be98bd372fa412045180d105
- https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
