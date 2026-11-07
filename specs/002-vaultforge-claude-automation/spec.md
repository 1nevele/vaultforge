# 002 — Claude execution routes

Status: operator-selected design (2026-11-07). Supersedes the unmerged PR #9 draft
(Claude Max review gate), which the operator dropped. Repository readiness is not
runtime acceptance; see "Verification" below.

## Goal

Claude is the executor for the operator (host) and their Hermes agent (Eleven), who
is the repository's maintainer and merger. Anyone may open issues; Claude implements
them. There are exactly two execution routes and no automated Claude code-review
gate. Roles and the issue flow are summarized in `docs/operating-model.md`.

Amended 2026-11-07: CA-003 lock release, CA-004 `Closes #N` on executor PRs, CA-008
issue flow, CA-009 executor prompt in the repository, CA-010 roles, CA-011 PR
follow-through.

## Requirements

- CA-001: **Scheduled issue execution.** A Claude cloud scheduled task (configured
  in the operator's claude.ai account, not in this repository) periodically starts a
  fresh Claude Code on the web session for `1nevele/vaultforge`. Each run executes
  at most one issue, following `docs/claude-web-handoff.md`.
- CA-002: **Issue selection (opt-in).** Only issues labelled `claude:scheduled` are
  eligible. A run picks the lowest-numbered open issue labelled both
  `claude:scheduled` and `status:ready`, and not labelled `status:blocked` or
  `status:in-progress`. If none exists, the run exits without changes. A
  `status:ready` issue without `claude:scheduled` is never picked up.
- CA-003: **One at a time.** If any open issue is labelled both `claude:scheduled`
  and `status:in-progress`, the run exits without changes. A run labels its issue `status:in-progress` before
  starting work. Merging the issue's `Closes #N` PR closes it and releases the lock;
  if the PR is abandoned or merged as `Part of #N`, Eleven (or the host) adds
  `status:ready` (plus `status:hold` if it needs a decision). CA-008 then removes the
  stale `status:in-progress`. A stale label blocks later runs;
  it is never cleared by the scheduled run itself.
- CA-004: **One issue, one PR.** A run opens one PR whose body says `Closes #N` (or
  `Part of #N` for partial work), so merging it closes the issue as completed,
  with real evidence per the PR template, then follows that PR through review
  (CA-011). No merge, approval, issue closing, unblocking of dependent issues or
  continuation to the next issue.
- CA-005: **Small fixes.** `.github/workflows/claude-fix.yml` runs
  `claude-code-action` only for `@claude` mentions in issue comments, PR review
  comments and PR reviews, from actors with write access. It is limited to small
  fixes (turn and time limits, scope instruction) and declines spec/feature work,
  dependency changes and `.github/` edits by pointing to a scheduled issue
  (`claude:scheduled` + `status:ready`).
- CA-006: **No Claude review gate.** No Claude review workflow runs on PR open.
  Automated review is CodeRabbit (`.coderabbit.yaml`, see `docs/code-review.md`);
  neither Claude route approves or merges.
- CA-007: Labels and triggers `claude-implement` / assignee `claude` no longer start
  work. Existing safety rules in `AGENTS.md` and the constitution still apply to both
  routes.
- CA-008: **Issue flow.** `.github/workflows/issue-flow.yml` runs
  `tools/issue_flow.py` on issue events, daily and on demand, one run at a time, with
  an issues-scoped token. Each run reads current labels, label history and dependency
  states, plans every open issue (and a just-closed one), and writes only if every
  lookup succeeded. It edits `status:*` labels only:
  - an open issue keeps one of ready / in-progress / blocked: the most recently
    added (label history), otherwise in-progress > blocked > ready;
  - a closed issue keeps none;
  - dependencies are every `#N`, same-repository `owner/repo#N` or issue/PR URL in
    the `## Dependencies` section (to the next same-or-higher heading) or on a
    `Depends-on:` line, outside code fences and HTML comments; one is satisfied
    when it is an issue closed as completed or a merged PR; a reference to another
    repository is never satisfied;
  - `status:blocked` becomes `status:ready` when all declared dependencies are
    satisfied, `status:ready` becomes `status:blocked` while one is not, and a block
    with no declared dependency is left alone;
  - `status:hold` is a flag the executor skips; the reconciler keeps it and still
    manages the held issue's status label;
  - labels the workflow added itself do not count as most recently added.
  It never closes, assigns, comments, dispatches or runs PR code.
- CA-009: **Executor prompt in the repository.** `docs/executor-prompt.md` is the
  reviewed source of the scheduled task's prompt. The host copies merged changes into
  the scheduled task; merging does not update the live task.
- CA-010: **Roles.** The host directs; Eleven maintains (triage, labels,
  dependencies, queuing, `@claude` review-fix requests, lock release) and merges under
  `docs/eleven-maintainer.md`; anyone may open issues. Sensitive paths are listed in
  `.github/CODEOWNERS` and need the host's explicit go-ahead for the PR's head commit
  before merge.
- CA-011: **PR follow-through.** The Claude session that opens a PR subscribes to its
  activity and fixes failing checks and verified review findings within the PR's
  scope, acting only on CI, CodeRabbit, Eleven and the host (other commenters are
  untrusted). It still never merges, approves, closes issues or starts another
  issue. Eleven's `@claude` requests are the fallback when a blocking finding has had
  no push or reply for two hours.

## Acceptance scenarios

1. With no issue labelled both `claude:scheduled` and `status:ready`, a scheduled run
   exits and changes nothing, even if other `status:ready` issues exist.
2. With a `claude:scheduled` issue already `status:in-progress`, a scheduled run exits
   and changes nothing.
3. With one ready issue, a scheduled run labels it in progress, opens one PR that
   says `Closes #N`, and follows it through review (CA-011) without merging; the issue
   stays open until the PR is merged.
4. A `@claude` comment asking for a typo fix produces a small commit or PR from
   `claude/fix-*`; a `@claude` comment asking for a new feature produces a reply that
   redirects to a scheduled issue and no code change.
5. Labelling an issue `claude-implement` starts no workflow.
6. Adding `status:in-progress` to a `status:ready` issue leaves only
   `status:in-progress`; later adding `status:ready` to it releases the lock, judged
   by label history rather than by which event triggered the run.
7. Closing an issue as completed removes its status labels, and each open
   `status:blocked` issue whose declared dependencies are now all completed becomes
   `status:ready`; one with any open dependency, or closed as not planned, stays
   blocked.
8. A consistent issue set produces no label changes.
9. Merging a `Closes #N` PR closes #N as completed, and scenario 7 follows; merging a
   `Part of #N` PR leaves #N open with its labels.
10. The executor never picks a `status:hold` issue; removing the hold returns the
    issue to the queue with the status the rules give it.
11. If a dependency lookup fails for any reason other than "not found", the run writes
    no labels.
12. No reconciliation ever leaves an open issue that had a status label without one.

## Verification

Scenarios 1–5 require live runs and are not established by this change. Scenarios
6–8 and 10–12 are covered offline by `tools/tests/test_issue_flow.py`; their live behaviour, and
scenario 9 (GitHub's closing keyword), are established by the first real PR merge and
issue events after merge. Record the
scheduled task's session handle and the PR/issue readback for the first real run.
