# Claude-only automation tasks and evidence

## Milestone A: isolated review verification (no approval/merge)

- [x] Inspect the official action at immutable source revision recorded in spec/plan.
- [x] Write validator contract tests first and observe 16 missing-implementation failures.
- [x] Implement fail-closed identity, freshness, result and complete-file coverage validation; all original validator tests pass.
- [x] Exercise real GitHub input preparation for PR #8. An older gh CLI rejected `--slurp`; add a failing concatenated-pagination test, implement portable decoding, then rerun the whole suite: 27 tests pass.
- [x] Prepare complete real PR #8 before/after input without checking out or executing its code.
- [ ] Exercise the pinned official base action with Max OAuth, a new no-tools context, empty MCP configuration and user-only settings sources.
- [ ] Read back the actual structured verdict, reviewed head, model session and producing workflow run.
- [ ] Exercise real reject/incomplete/stale cases. Fixture validation is not live model evidence.
- [ ] Independent review of the whole infrastructure branch.

## Milestone B: approval and merge authority

- [ ] Resolve and demonstrate non-spoofable gate identity/credential isolation.
- [ ] Move review authentication to trusted-controller-only scope before enabling automatic untrusted PR processing; do not remove the existing secret before a replacement is verified.
- [ ] Exercise independent approval eligibility and exact-head readback.
- [ ] Prove native strict freshness and gate-policy changes cannot self-authorize.
- [ ] Update standing policy consistently, retain CI, then activate native auto-merge only after all negative cases block.

## Milestone C: execution and delivery

- [ ] Verify real Max web-account GitHub linkage and fresh web skill discovery.
- [ ] Dispatch only the bounded S01 handoff after readiness evidence exists.
- [ ] Exercise actual PR/review/merge Discord notifications.

## Rulings

- Use the existing dedicated preparation clone on `ci/claude-max-review`; do not create another implementation environment or alter application code.
- The initial verification uses explicit `workflow_dispatch` on the existing registered workflow path, selected branch/revision and chosen PR. It has read-only GitHub permissions and no approval/merge authority. This is an acceptance test, not automatic processing or a production gate.
- Use the official lower-level base action only as an inference primitive, with caller-owned inert input isolation. Its completion is never interpreted as approval; the separate validator rejects non-clean or stale results.
- The canonical packet remains this spec/plan/tasks set. No competing plan tree is introduced.
