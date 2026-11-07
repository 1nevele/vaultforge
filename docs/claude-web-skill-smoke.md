# Claude-web native skill smoke check

Status: **not exercised in Claude Code on the web**. Filesystem checks are separate evidence. This check must precede S01 application implementation; successful manual reading is not native discovery.

## Session and limits

Use a fresh **ordinary repository cloud session** for private `1nevele/vaultforge`, with the published setup revision. Do not use a cloud thread inside a Claude project: that surface does not load repository skills. Do not change Claude account settings, network policies, permissions or global packages to make this pass.

This is a bounded development-skill check, not authorization for live Sentinel inference, targets, workers or infrastructure. Stop after the result; the implementation assignment is separate. Starting a Claude session uses the operator's account/quota and requires access through the supported surface.

## Paste-ready check

```text
In this ordinary repository cloud session, do not implement application code.
Read CLAUDE.md and docs/development-workflow.md.
Report the repository, checkout revision and actual skill discovery source.

1. Enumerate the native skills actually exposed to your Skill tool. Expect
   three unnamespaced Superpowers skills and nine speckit-* skills, and confirm
   the built-in code-review skill (and security-review) is exposed, since
   CLAUDE.md requires it before every push. Distinguish actual tool discovery
   from a filesystem listing or startup capability claim.
2. Invoke verification-before-completion using the native Skill tool. Cite its
   resolved name/source and summarize its evidence-before-claims rule. Do not
   run a product command or fabricate a completion claim for this check.
3. Invoke speckit-analyze natively with read-only S01 feature context:
   SPECIFY_FEATURE_DIRECTORY=specs/001-sentinel-foundation
   SPECIFY_FEATURE_NO_PERSIST=1
   Its missing S01 plan/tasks are expected at this stage. Report that exact
   prerequisite result; do not create them, edit files, call providers or start
   implementation just to make analysis pass. Do not invoke its suggested next
   skills automatically.
4. Report discovered/loaded/blocked separately, and stop. No plugin install,
   account change, helper execution, secret access, target operation or merge.
   If native skill invocation is unavailable, record BLOCKED, not a manual-read
   substitute or a passing result.
```

## Evidence to retain

Record session/task handle, account-authorized repository access, checkout SHA, exact native skill names/sources, actual invocation results and all prompts/blockers. Do not retain secrets or private session transcripts wholesale. The negative Spec Kit prerequisite result is expected; it proves neither application readiness nor successful full analysis. A passed discovery check does not prove the full Superpowers plugin, hooks, model adherence or Sentinel security gates.

Current handoff state is **repository setup prepared**, not cloud task submitted or application implementation started.
