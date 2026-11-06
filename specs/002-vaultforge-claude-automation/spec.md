# Claude-only automated review and web execution

Status: local draft; operator selected Claude-only zero-human-review merging and Claude Max authentication. Technical design review, account linking and runtime acceptance remain pending. This draft is not a claim of human approval of implementation details.

## Goal

Use the operator's Claude Max subscription for independent PR review and Claude Code web execution in `1nevele/vaultforge`, with machine-enforced approval/merge rules and Discord notifications. Do not use CodeRabbit or introduce paid API billing.

## Requirements

- CA-001: Claude Code on the web remains the application implementation executor. Eleven prepares specifications, issues, authorized infrastructure setup and independent verification. Do not substitute a local application implementation.
- CA-002: Authenticate reviews with the documented `CLAUDE_CODE_OAUTH_TOKEN` repository secret backed by Claude Max. Never put the credential in repository files, prompts, artifacts, logs or Discord. No separately billed API key or extra-usage activation.
- CA-003: Restrict the official Claude GitHub App installation to the public Vaultforge repository; exclude retained private history. Installation and account linkage are separate acceptance conditions.
- CA-004: Review in a fresh Claude context with specification and test-evidence checks, using structured output. The reviewed repository, PR, head SHA and base SHA must be explicit and validated against current GitHub state.
- CA-005: Missing credentials, skipped review, absent or malformed output, incomplete coverage, model/action failure, timeout, blocking findings or changed head/base must prevent approval and merging.
- CA-006: A separate deterministic job validates review evidence and submits approval as an identity other than the PR author and latest pusher. The model has no approval or merge credentials. Validate GitHub eligibility rather than assuming a bot review counts.
- CA-007: Main retains the existing independent-approval and CI requirements during bootstrap. Activate automatic squash-merging only after positive and negative live tests establish the replacement gate. No administrator bypass, force-push or direct-main workaround.
- CA-008: Treat PR code, instructions, titles, comments and artifacts as untrusted. Privileged jobs do not execute PR code or load PR-supplied hooks/plugins/settings. Workflow/gate modifications must not be able to certify themselves. Fork PRs do not receive credentials or privileged execution.
- CA-009: Preserve existing Workflow setup and Secret scan checks. Application test/type/lint/build checks are added with application code; setup checks are not application or containment assurance.
- CA-010: Report actual PR/review/merge outcomes in Discord channel `1568388040433340541`, without secrets, blanket mentions or retained-private-repository disclosures. Never represent a test/ping as a real merge event.
- CA-011: Before application work, exercise repository skill discovery in a fresh real Claude web session using the published smoke-check instructions; record the session handle, repository, branch and actual result.
- CA-012: After readiness verification, dispatch only the first ready bounded assignment from issue #6/#1 and its canonical `specs/001-sentinel-foundation` packet. No automatic whole-backlog continuation, provider/target operations or application deployment.

## Acceptance scenarios

1. Valid clean latest-commit review plus actual required CI produces an eligible independent approval and automatic squash-merge, with an observable Discord notification.
2. A deliberately failing review produces no approval or merge; fixing the change requires a new real review.
3. A push or base change after review invalidates evidence; an old verdict never approves new bytes.
4. Missing authentication, invalid JSON/schema, model failure, skipped review and missing evidence all fail closed.
5. A PR touching the gate, inserting instructions, or forging an artifact/status cannot obtain authority from its own changes.
6. Claude App installation access readback names only Vaultforge; a real Max-backed review demonstrates authentication without exposing the token.
7. A real fresh Claude web session discovers the selected committed skills and returns the documented smoke-check result before the first application assignment starts.

## Verified discovery and blockers

- Official action source inspected at immutable revision `115e0b2c49222c831de6748ccdf365bb8d3ea9a3`; inspection is not runtime verification.
- GitHub App installation `179414669` was created and read back with selected-repository access only to `1nevele/vaultforge` (repository ID `1448718197`). This does not establish linkage to the operator's Claude Max account.
- GitHub Actions now has `CLAUDE_CODE_OAUTH_TOKEN`. Secret presence is verified, not secret contents. Max-backed runtime authentication remains to be exercised. Claude CLI is not installed on Eleven's execution machine.
- Claude web access from Eleven's browser is currently stopped by Cloudflare human verification, including after use of the normal verification control. No bypass or alternate account is authorized.
- GitHub currently has auto-merge disabled and Actions review approvals disabled. Both existing required checks and the one-independent-approval policy are unchanged.
- CodeRabbit App is removed. Repository cleanup PR #8 remains open. PR #7 also remains open; no merge is claimed.

## Non-goals

No CodeRabbit replacement subscription, managed Team/Enterprise review purchase, unbounded fix loop, extra-usage billing, product runtime/provider selection, live security-target access, secret migration from Hermes, or activation claims without real execution.
