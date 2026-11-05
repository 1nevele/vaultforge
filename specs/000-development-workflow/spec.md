# 000 — Specification-driven development workflow

Status: draft for review; implementation authorization is limited to tooling and documentation. User requested spec-driven work and consideration of Superpowers before application code.

## Objective

Create a reproducible, inspectable development workflow before Sentinel's first feature. Preserve existing product decisions and research rather than restart product brainstorming.

## Requirements

- WF-001: Every application feature has `spec.md`, `plan.md`, `tasks.md` and traceable acceptance scenarios before implementation.
- WF-002: Superpowers, if installed, uses a pinned reviewed upstream revision and native Hermes integration. A blocked scanner result requires review and explicit operator consent before an override. No silent global service restart.
- WF-003: One canonical spec/plan/task source; Superpowers execution and review consume it rather than maintaining a competing plan.
- WF-004: Root plus at most three active agents with exclusive ownership and independent review. Record real tests and unresolved gates in every handoff.
- WF-005: GitHub stays private; no secret, runtime data or homelab configuration is committed. Do not merge application work automatically.
- WF-006: RAPTOR-first evaluation remains a capability/containment question, not an unmeasured superiority claim or permission to scan.

## Acceptance scenarios

- AS-001 (WF-001/003): Given a new feature, when implementation is proposed, reviewers can locate its requirements, testable scenarios, plan and ordered tasks without duplicate conflicting instructions.
- AS-002 (WF-002): Given a blocked plugin installation, when no override is authorized, the plugin remains uninstalled/disabled and the precise blocker is recorded.
- AS-003 (WF-004): Given concurrent assignments, each lists owned paths, dependencies, tests and stop conditions; no shared-file edits overlap.
- AS-004 (WF-005): Given the first published repository, GitHub readback confirms private visibility and the published revision matches the local commit.
- AS-005 (WF-006): Given candidate engine evaluation, no engine installation or target traffic is required for the source-level decision note; runtime acceptance remains untested.

## Exclusions

No application implementation, live inference, sandbox launch, actual assessment, security-gate pass or automatic merge in this tooling slice. Do not claim full Spec Kit CLI or Superpowers activation when only conventions/source review exist.
