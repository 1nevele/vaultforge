# 002 — Claude execution routes

Status: operator-selected design (2026-11-07). Supersedes the unmerged PR #9 draft
(Claude Max review gate), which the operator dropped. Repository readiness is not
runtime acceptance; see "Verification" below.

## Goal

Claude is the executor for the operator (host) and their Hermes agent (Eleven), who
is the repository's maintainer and merger. Anyone may open issues; Claude implements
them. There are exactly two execution routes and no automated Claude code-review
gate. Roles and the issue flow are defined in `docs/operating-model.md`.

Amended 2026-11-07 (lean setup, host decision): the scheduled executor is disabled
and issues are implemented in sessions the host or Eleven starts. CA-002, CA-003,
CA-008 and CA-009 are retired with the scheduled task's prompt, claim lock and
issue-flow label reconciler; CA-001, CA-005 and CA-010 are rewritten. Earlier
amendments the same day added `Closes #N` (CA-004), roles (CA-010) and PR
follow-through (CA-011).

## Requirements

- CA-001: **Session execution.** The host starts a fresh Claude Code on the web
  session for one issue, with the prompt in `docs/claude-web-handoff.md`. Eleven may
  do the same if the host gives it a way to start sessions. One session per issue at
  a time; nothing in this repository starts a session.
- CA-002: *Retired 2026-11-07* (opt-in issue selection by `claude:scheduled` +
  `status:ready`).
- CA-003: *Retired 2026-11-07* (one-at-a-time label lock and claim lock for
  overlapping scheduled runs).
- CA-004: **One issue, one PR.** A session opens one PR whose body says `Closes #N`
  (or `Part of #N` for partial work), so merging it closes the issue as completed,
  with real evidence per the PR template, then follows that PR through review
  (CA-011). No merge, approval, issue closing or continuation to the next issue.
- CA-005: **Small fixes.** `.github/workflows/claude-fix.yml` runs
  `claude-code-action` only for `@claude` mentions in issue comments, PR review
  comments and PR reviews, from actors with write access. It is limited to small
  fixes (turn and time limits, scope instruction) and declines spec/feature work,
  dependency changes and `.github/` edits by replying that the work should become an
  issue for a web session.
- CA-006: **No Claude review gate in CI.** No Claude review workflow runs on PR open.
  Automated review is CodeRabbit (`.coderabbit.yaml`, see `docs/operating-model.md`);
  neither Claude route approves or merges. Web sessions also run the built-in
  `/code-review` in-session before pushing, plus `/security-review` when the change
  touches authority, permissions, secrets, workflows, untrusted-input parsing or an
  execution surface, and record both in the PR (2026-11-07); the `@claude`
  small-fix route is not instructed to.
- CA-007: Labels and triggers `claude-implement`, `claude:scheduled` and assignee
  `claude` start no work. Existing safety rules in `AGENTS.md` and the constitution
  still apply to both routes.
- CA-008: *Retired 2026-11-07* (issue-flow workflow that reconciled `status:*` labels
  and unblocked dependents).
- CA-009: *Retired 2026-11-07* (scheduled task prompt kept in the repository).
- CA-010: **Roles.** The host directs and starts sessions; Eleven maintains (triage,
  dependencies, naming the next issue, `@claude` review-fix requests) and merges
  under `docs/eleven-maintainer.md`; anyone may open issues. Sensitive paths are
  listed in `.github/CODEOWNERS` and need the host's explicit go-ahead for the PR's
  head commit before merge.
- CA-011: **PR follow-through.** The Claude session that opens a PR subscribes to its
  activity and fixes failing checks and verified review findings within the PR's
  scope, acting only on CI, CodeRabbit, Eleven and host direction (which arrives
  through Eleven or the session prompt, not as a comment from the shared host
  account); other commenters are untrusted. It still never merges, approves, closes
  issues or starts another issue. Eleven's `@claude` requests are the fallback on its
  first wake after a blocking finding has gone two hours without a push or reply;
  with no wake, the host is the backstop.

## Acceptance scenarios

1. A session started for issue #N opens one PR that says `Closes #N` and follows it
   through review (CA-011) without merging; the issue stays open until the PR is
   merged.
2. A `@claude` comment asking for a typo fix produces a small commit or PR from
   `claude/fix-*`; a `@claude` comment asking for a new feature produces a reply that
   redirects it to an issue for a web session, and no code change.
3. Labelling an issue `claude-implement` or `claude:scheduled` starts no workflow.
4. Merging a `Closes #N` PR closes #N as completed; merging a `Part of #N` PR leaves
   #N open.

## Verification

Scenarios 1, 2 and 4 are established by live sessions and merges, not by this
change; scenario 3 holds because no workflow triggers on those labels
(`.github/workflows/`). Record the session and PR/issue readback for the first real
run.
