# Claude-only Review and Merge Implementation Plan

> **For agentic workers:** Use the repository's canonical specification-driven workflow and independent implementation/review gates. This plan is a local design draft, not a deployed pipeline.

**Goal:** Max-backed Claude review followed by machine-validated independent approval and native squash auto-merge, plus verified Claude web execution.

**Architecture:** A trusted controller prepares inert PR input for fresh isolated Claude inference. A separate validator and approving identity accept only an explicit complete verdict for authoritative current PR/head/base/policy metadata. A dedicated gate identity prevents arbitrary PR workflows from minting a passing merge gate. No PR-code execution occurs in credential-bearing jobs.

**Tech stack:** GitHub Actions/API, official Claude action pinned to `115e0b2c49222c831de6748ccdf365bb8d3ea9a3`, Claude Max OAuth, deterministic Python validation/tests, dedicated limited GitHub gate App.

**Spec:** `specs/002-vaultforge-claude-automation/spec.md`

## Global constraints

- Satisfy CA-001 through CA-012; preserve public Vaultforge/private-history separation.
- No API key or extra-usage billing; use `CLAUDE_CODE_OAUTH_TOKEN` without logging it.
- Keep automatic approval/merging disabled until all live activation tests pass.
- The Claude App installation is now verified on Vaultforge only; Max account linkage and subscription secret remain absent. The source auditor's earlier no-App assumption is superseded by installation readback, not by any runtime claim.
- Preserve current CI and main approval protections during bootstrap. No administrator/direct-main bypass.
- This is infrastructure setup, not authorization for local application implementation or whole-backlog dispatch.

## Review focus and blocking design questions

1. Project/local Claude settings, hooks, MCP, plugins, runtime preloads and symlinks must never execute from PR content. No-tools inference over controller-prepared inert data is the initial candidate; actual isolation must be demonstrated.
2. `GITHUB_TOKEN` approval/check authority cannot enter the inference job. An explicitly supplied read-only `github_token` is required rather than defaulting to a potentially write-capable Claude App token.
3. A required check bound only to the GitHub Actions App does not identify its producing workflow. Use a dedicated gate App whose credentials cannot be read by arbitrary PR workflows. Environment branch restrictions or a separate controller must be exercised before claiming that boundary.
4. Head/base/policy/nonce freshness and exact workflow provenance must be checked independently of model output. Strict checks alone do not prove a base cannot change between validation and merge; the accepted freshness contract and enforcement mechanism remain unresolved.
5. Clean AI findings are probabilistic evidence. No claim of prompt-injection immunity or complete code correctness. Real product gates are still required for application merging.

## Task 1: Pin inference inputs and implement deterministic validation

**Files:** trusted controller implementation and tests under `tools/claude_review/` and `tools/tests/`; trusted policy/schema under `.github/claude-review/`.

**Consumes:** authoritative repository ID, PR number, head/base SHA and ref, policy revision, unique run nonce and complete paginated diff/blob inventory.
**Produces:** an immutable input tuple, a review-input digest, and a parsed verdict accepted only for that tuple.

- [ ] Define the exact JSON schema and validator interfaces after resolving the freshness contract; require explicit verdict, findings, complete coverage and all tuple fields. Unknown fields fail closed.
- [ ] Write and observe failing tests for approve/reject, absent/malformed/truncated output, unknown fields, incomplete pagination/coverage, error/quota/timeout, wrong repo/PR/head/base/policy/nonce and replay/sibling-PR evidence.
- [ ] Implement only the deterministic validator and data preparation; no inference or credentials in unit tests.
- [ ] Run all tests and existing offline checks. Fixtures are validator evidence only, not a real Claude review.
- [ ] Independent spec/security/code review before publishing implementation.

## Task 2: Prove Max-backed isolated inference

**Consumes:** Task 1 trusted inert inputs and the protected Max subscription secret.
**Produces:** a fresh real Claude result, isolated from PR configuration and write credentials, plus observed action/session metadata.

- [ ] Authenticate Max through the native supported token flow; verify secret presence, never token contents.
- [ ] Pin the action and CLI/runtime dependencies. Official output is `structured_output` (singular); schema is supplied through `--json-schema` in `claude_args`.
- [ ] Run from trusted/empty configuration with no PR checkout at workspace root, no PR executable setup and no restored caches. Do not rely only on `allowedTools`.
- [ ] Show negative tests for malicious `CLAUDE.md`, SessionStart hooks, nested settings, MCP/plugin files, runtime preload, symlinks and attempts to read approval/merge secrets.
- [ ] Exercise one real passing and one deliberately failing Claude review. Confirm no skipped/absent review can become approval.

## Task 3: Isolate gate credentials and submit independent approval

**Consumes:** trusted controller metadata, validated current verdict and exact CI workflow/run/job provenance.
**Produces:** dedicated-App required gate plus GitHub Actions approval with exact `commit_id`, both read back remotely.

- [ ] Establish a dedicated minimal check-writing gate App/controller credential boundary. Restrict installation to Vaultforge; ensure arbitrary PR workflows cannot use its credential.
- [ ] Enable GitHub Actions review approvals only as part of this verified activation task, not as a speculative prerequisite.
- [ ] In a separate non-Claude job, revalidate tuple and eligible PR author/latest pusher, then submit approval as a distinct identity.
- [ ] Verify actual approving actor, commit and protection eligibility for `claude[bot]` and `1nevele` authors. Unknown authors/pushers or self-approval stay blocked.
- [ ] Test forged artifacts/comments/statuses, duplicate check names, wrong App/workflow, skipped CI, rerun/replay, new head/base, retarget and force-push.
- [ ] Test the bootstrap route without using admin bypass or weakening existing protection. The bootstrap remains an explicit acceptance problem until exercised.

## Task 4: Activate native merge only after negative tests

**Consumes:** observed gate App ID/check name, eligible approval and preserved real CI.
**Produces:** protected native auto-merge and a genuinely merged test PR, with negative cases demonstrably blocked.

- [ ] Update AGENTS.md, CLAUDE.md, constitution/review policy and relevant handoff artifacts through the accepted infrastructure PR route; do not leave contradictory stop-at-PR/no-auto-merge instructions.
- [ ] Bind the observed gate to its dedicated App; retain current CI, strict update checks, stale-review dismissal, latest-push approval, conversation resolution and no force push/deletion.
- [ ] Enable native automatic squash merge without direct merge or administrative bypass.
- [ ] Verify all negative cases block; then exercise a real eligible PR and read back merged SHA/time and resulting main checks.
- [ ] Keep gate/controller/credential-policy changes outside self-authorizing automatic eligibility.

## Task 5: Verify web execution and notification delivery

- [ ] Complete Max web account sign-in and GitHub linkage; current Cloudflare verification blocks Eleven's browser. No archives, proxy relays or copied cookies substitute for authentication.
- [ ] Verify selected repository/branch and run the published benign cloud skill smoke check in a fresh real session. Capture a genuine session handle and actual skill-discovery results.
- [ ] Verify Discord notification authority. Prefer the native GitHub-compatible webhook when Manage Webhooks is granted; do not silently add a costly model-polled schedule.
- [ ] Test actual PR/review/merge delivery and read the exact target message; no secret or private-archive payloads.
- [ ] Only after readiness, submit the bounded S01 assignment from #6/#1, verify its web task handle/repository/assignment, and stop at that assignment's boundary.

## Source verification

Parent verified official action `action.yml:169–184,334–336`, `base-action/src/run-claude-sdk.ts:236–295`, and `docs/security.md:23–64` against the cloned immutable revision. This confirms OAuth/structured-output support and upstream trust warnings, not the proposed pipeline's runtime safety. Additional settings/token concerns were independently audited; implementation must test them before acceptance.

## Current status

No pipeline code, approval/merge-setting changes, extra billing or web execution has been activated. Local specification and this plan are preparatory artifacts only. Max subscription token and web-account linkage are owner-action prerequisites already communicated.
