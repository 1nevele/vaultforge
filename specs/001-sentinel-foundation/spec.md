# 001 — Sentinel offline contract foundation (S01)

Status: draft handoff for Claude Code on the web. Derives from the original plans and architecture review; no human sign-off on an unshown detailed API is implied.

## Objective

Build the smallest offline TypeScript contract/fixture foundation under projects/sentinel so later service, UI and worker lanes integrate against reviewed interfaces. No execution capability.

## Requirements and scenarios

- S01-001: Pin tooling compatible with the actual Claude web environment, not unverified deployment assumptions or unaccepted scaffolding. Reproducible fresh-checkout install, typecheck, build and tests; no global upgrades.
- S01-002: Version strict contracts for mission request/task envelope, registered scope/limits, actor/generation, immutable candidates/selection, canonical operation/review/receipt references, evidence, target observations, projection snapshot and public event producer classes. Reject malformed versions, authority-bearing extra fields and identifier/digest mismatches.
- S01-003: Selection resolves only an opaque ID in the host-frozen candidate snapshot or explicit abstention. Reject stale generation/set and unknown IDs. Shape validation is not authentication, grant approval or execution authority.
- S01-004: Untrusted model/worker ingestion cannot self-assign supervisor/authority/verifier provenance. Authenticated host identity and privileged dispatch remain distinct future boundaries.
- S01-005: CDM derivations carry source/evidence hashes, canonical/rendered input identity, adapter/rubric/model versions, score semantics, span encoding/offset unit, completeness/lineage and honest failed/unknown outcomes. Derived records never manufacture verified findings.
- S01-006: Fixtures are synthetic and explicitly non-executing. No secrets, provider calls, backend install, target request, approval bypass or host-shell/MCP execution surface.
- S01-007: Link requirements to actual RED/GREEN tests and independent spec/code review. CI/unit fixtures are not G0–G8 evidence.

Given a valid synthetic mission request, validation preserves the versioned value. Given forged/extra authority fields, validation rejects them. Given a stale or foreign candidate selection, normalization rejects rather than inventing executable parameters. Given missing provider/VM prerequisites, offline tests still run and no live acceptance is falsely passed.

## Ownership

Claude lead owns project manifests, contracts under projects/sentinel/packages/contracts/, shared fixtures/security tests, and serialized root config/lockfile changes needed for this slice. Avoid empty packages or a generic monorepo platform. Later lanes request shared changes instead of racing them.

## Stopping condition

Before code, refine/review this spec, create plan.md/tasks.md and exact interface/test mapping in this same packet. Implement S01 only. Open a PR with changed paths, actual commands/results, independent review and remaining gates; stop. Do not merge, self-close the issue or automatically unlock dependent issues. The historical linked backlog JSON was not provided and is not an existing implementation artifact.
