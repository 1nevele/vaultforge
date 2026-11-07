# Vaultforge operating model

This is the single source of truth for who does what and how work moves through the
repository. Other documents link here instead of restating it; if one disagrees, this
file wins and the other is a bug. Safety rules stay in `AGENTS.md` and the
constitution.

## Roles

| Role | Who | Owns |
| --- | --- | --- |
| **Host** | The operator (GitHub `46tsoh`) | Direction and priorities; approval of sensitive changes; exceptions and escalations. |
| **Eleven** | The operator's Hermes agent (GitHub `1nevele`) | Maintainer and merger: issue triage and labels, dependency and lock upkeep, queuing work for Claude, driving review feedback back to Claude, merging eligible PRs, closing finished issues, notifying the host. Mandate details: [eleven-maintainer.md](eleven-maintainer.md). |
| **Claude** | Claude Code on the web (scheduled task and ad-hoc sessions); `claude-fix.yml` for `@claude` | Executor: implements one issue per PR with real evidence, and applies small fixes on request. Never approves or merges. |
| **CodeRabbit** | `coderabbitai[bot]` | Automated PR review; its approving review on the current head is the routine approval. |
| **CI** | `Repository checks` | Required checks (`Workflow setup`, `Secret scan`, plus project jobs such as `Sentinel contracts (offline)`). |

The host, Eleven and Claude may all open issues. Claude's GitHub actions run through
the host's GitHub connection, so they also appear as `46tsoh`; a GitHub review or label
from `46tsoh` therefore cannot prove a host decision. Host approval of a sensitive
change is given to Eleven in conversation and recorded by Eleven on the PR.

## Labels

| Label | Meaning |
| --- | --- |
| `status:ready` | Specified and unblocked; may be picked up. |
| `status:in-progress` | Claimed. On a `claude:scheduled` issue this is the executor lock. |
| `status:blocked` | Waiting on declared dependencies or on a manual block. |
| `claude:scheduled` | Opt-in for the scheduled executor. Issues without it are never picked up. |
| `project:<name>`, `type:tracking` | Classification only. |

An issue carries at most one `status:*` label; a closed issue carries none.
`claude-implement` is retired and starts nothing.

### Dependencies

Declare dependencies in the issue body, either as `Blocked by #N` / `Depends on #N`
lines under a `## Dependencies` heading, or as a `Depends-on: #N, #M` line anywhere.
References elsewhere in the body (for example a tracker checklist) are not
dependencies. A dependency is satisfied only when that issue is closed as
**completed**; closing it as not planned leaves dependents blocked for a decision.

### Automated label upkeep

`.github/workflows/issue-flow.yml` (`tools/issue_flow.py`) runs on issue events, daily
and on demand. It changes `status:*` labels only:

- a newly added status label replaces the other status labels; otherwise
  in-progress beats blocked beats ready;
- closing an issue removes its status labels, which releases the executor lock;
- a `status:blocked` issue whose declared dependencies are all completed becomes
  `status:ready`; a block with no declared dependency is manual and left alone;
- a `status:ready` issue with an open dependency becomes `status:blocked`.

It never closes, assigns, comments, dispatches Claude or runs pull-request code.

## Flow of one issue

1. **Create.** Anyone opens an issue with scope, `## Dependencies`, owned paths,
   acceptance and stop conditions, and a link to (or the request to create) its
   `specs/<NNN>-<project>-<feature>/` packet.
2. **Queue.** Eleven (or the host) triages it: project label, dependencies, and
   `status:ready` or `status:blocked`. Adding `claude:scheduled` queues it for the
   executor; do that only for work inside the host's current direction.
3. **Claim.** The scheduled executor ([executor-prompt.md](executor-prompt.md)) runs
   on its schedule. If no `claude:scheduled` issue is `status:in-progress`, it takes
   the lowest-numbered open `claude:scheduled` + `status:ready` issue, labels it
   `status:in-progress`, implements it, opens one PR with `Closes #N`, and stops.
4. **Review.** CI and CodeRabbit run. If CodeRabbit requests changes or a check fails,
   Eleven asks Claude for a fix with an `@claude` comment on the PR quoting the
   findings to address (at most two rounds per PR), or escalates.
5. **Merge.** When the PR meets the merge gates in
   [eleven-maintainer.md](eleven-maintainer.md), Eleven squash-merges the exact head.
6. **Close.** Merging the PR closes the issue as completed through GitHub's
   `Closes #N` keyword, with no extra step. Issue flow then clears the lock and
   unblocks dependents, and the next scheduled run proceeds. Eleven checks the result
   and notifies the host. A PR that delivers only part of an issue says
   `Part of #N` instead, and the issue stays open.
7. **Abandon.** If a PR is abandoned, Eleven closes it and sets the issue back to
   `status:ready` (retry) or `status:blocked` (needs a decision); either releases the
   lock.

Only one `claude:scheduled` issue is in progress at a time, from claim until close or
reset. Claude stops at its PR; it never merges, approves, closes issues, unblocks
dependents or starts a second issue.

### Closing keywords

| PR body | On merge |
| --- | --- |
| `Closes #N` | Issue #N is closed as completed; dependents may unblock. |
| `Part of #N` | Nothing; #N stays open and keeps its status. |

GitHub only honours `Closes` when the PR merges into `main`. An issue closed this way
can be reopened if the work turns out incomplete; reopening does not re-block
dependents that already moved to `status:ready`.

## Escalate to the host

Eleven notifies the host and waits for direction when:

- a PR touches a path in `.github/CODEOWNERS` (governance, CI, tooling trust, Sentinel
  trust boundaries), or any category the constitution reserves for the host
  (security authority, sandbox boundaries, secrets, deployment, spend, destructive
  migrations, publication, infrastructure, review/CI policy);
- two `@claude` fix rounds have not cleared the blocking findings, or Claude and
  CodeRabbit disagree on a finding;
- a merge conflict or failing check is beyond a small fix;
- Claude reports a blocker on an issue (missing access, failed skill discovery,
  ambiguous spec);
- a dependency was closed as not planned, or the next work is outside current
  direction.

## Known gaps

- Eleven's GitHub account owns the repository and main's `enforce_admins` is off, so
  repository settings do not enforce Eleven's limits; they rest on its mandate. A
  separate non-admin identity for Eleven and re-enabled admin enforcement would close
  this. Changing either is a host decision.
- `.github/CODEOWNERS` names the sensitive paths and requests reviews. "Require review
  from Code Owners" is not turned on; that setting is a host decision.
- The scheduled task's live prompt is stored in the host's claude.ai account. Keep it
  identical to [executor-prompt.md](executor-prompt.md).
