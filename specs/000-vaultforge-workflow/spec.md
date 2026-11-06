# 000 — Vaultforge monorepo and Claude-web workflow

Status: requested tooling/repository setup; no application implementation in this feature. User approved Vaultforge as the monorepo, Sentinel as a project, and the repository-native Claude Code web setup. Implementation uses five pinned Superpowers skills plus nine official generated Spec Kit skills, not a full Superpowers plugin. Actual cloud discovery remains a separate gate.

## Requirements

- VF-001: The original identity-preserving private rename requirement is superseded by the operator-authorized publication migration: retain the original privately as `1nevele/vaultforge-private-history` and use a fresh `1nevele/vaultforge` with privacy-sanitized history. Verify distinct repository identities and keep the original private; public visibility applies only to the reviewed fresh repository.
- VF-002: Preserve Sentinel plans/research under projects/sentinel. No accidental local application/dependency scaffold is published.
- VF-003: Provide actual pinned repository-local Superpowers/Spec Kit artifacts and supported Claude configuration, including licenses/provenance. Do not depend on global Hermes skills or confuse repo readiness with cloud activation.
- VF-004: One canonical root feature packet; project prefix in its directory. Root CLAUDE/AGENTS files identify executor/scope.
- VF-005: Create scoped dependency-linked GitHub issues and one ready starting assignment. Do not imply issues launch a cloud session.
- VF-006: Exercise offline checks, independent setup review and exact GitHub readback. Actual cloud session remains separately untested until exercised.

## Acceptance

- AS-001: Read back distinct source/archive and fresh destination repository IDs, verify the source remains private, verify only the authorized destination visibility changes, and confirm local origin targets the fresh repository. The original same-ID rename acceptance is superseded by VF-001.
- AS-002: Relocated artifacts exist; no app scaffold, secrets or runtime data enter the commit.
- AS-003: Validate pinned identities/licenses/required files/safe paths from a clean checkout. No global native Hermes integration; any required CLI/bootstrap is explicit and verified separately.
- AS-004: Claude entry point and canonical specs resolve without stale paths or contradictory ownership.
- AS-005: Verify every created issue body/dependency/status; only S01 ready, later initial-wave work blocked on accepted S01.
- AS-006: Record independent review, actual checks and untested Claude-web activation boundary.

## Exclusions

No application code, target access, provider calls, VM/network/account changes, diagnostic exports, visual companion or broad permission bypass. No cloud-dispatch claim without session evidence.
