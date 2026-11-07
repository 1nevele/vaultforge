# 002 — Claude execution routes

Status: operator-selected design (2026-11-07). Supersedes the unmerged PR #9 draft
(Claude Max review gate), which the operator dropped. Repository readiness is not
runtime acceptance; see "Verification" below.

## Goal

Claude is the executor for the operator and their Hermes agent (Eleven). Humans and
Eleven prepare specs and issues; Claude implements them. There are exactly two
execution routes and no automated Claude code-review gate.

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
  starting work. The operator or Eleven removes that label after accepting, merging
  or abandoning the PR. A stale label blocks later runs; it is never cleared by the
  scheduled run itself.
- CA-004: **Stop at the PR.** A run opens one PR referencing (not closing) the issue,
  with real evidence per the PR template, then stops. No merge, approval, issue
  closing, unblocking of dependent issues or continuation to the next issue.
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

## Acceptance scenarios

1. With no issue labelled both `claude:scheduled` and `status:ready`, a scheduled run
   exits and changes nothing, even if other `status:ready` issues exist.
2. With a `claude:scheduled` issue already `status:in-progress`, a scheduled run exits
   and changes nothing.
3. With one ready issue, a scheduled run labels it in progress, opens one PR that
   references it, and stops; the issue stays open.
4. A `@claude` comment asking for a typo fix produces a small commit or PR from
   `claude/fix-*`; a `@claude` comment asking for a new feature produces a reply that
   redirects to a scheduled issue and no code change.
5. Labelling an issue `claude-implement` starts no workflow.

## Verification

Scenarios 1–5 require live runs and are not established by this change. Record the
scheduled task's session handle and the PR/issue readback for the first real run.
