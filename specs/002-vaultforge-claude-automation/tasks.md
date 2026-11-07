# 002 — Tasks

- [x] T001 Replace issue-implementation workflow with `@claude` small-fix workflow (CA-005, CA-007)
- [x] T002 Update root agent instructions and workflow docs (CA-001–CA-006)
- [x] T003 Create the Claude cloud scheduled task with the CA-001–CA-004 prompt (outside repo) — created "Vaultforge ready-issue executor", every 4 hours
- [ ] T004 Close PRs #9, #10, #11, #15 (done) and delete their branches (pending: needs operator; the executor session may push only its own branch)
- [ ] T005 Live acceptance: scenarios 1–5, with session handle and GitHub readback
- [x] T006 Issue flow: `tools/issue_flow.py` + `.github/workflows/issue-flow.yml` with offline tests (CA-008, scenarios 6–8)
- [x] T007 Commit the executor prompt as `docs/executor-prompt.md` (CA-009)
- [x] T008 One operating model (`docs/operating-model.md`), Eleven maintainer mandate, `.github/CODEOWNERS`; align root docs and remove risk-gate references (CA-010)
- [ ] T009 Host: copy `docs/executor-prompt.md` into the scheduled task after merge; decide on a non-admin identity for Eleven, `enforce_admins` and required code-owner review
- [ ] T010 Live acceptance of scenarios 6–12 on real PR merges and issue events, with run links
- [x] T011 Executor PRs use `Closes #N` (or `Part of #N`) so merging closes the issue (CA-004, scenario 9)
- [x] T012 Address independent review of 3567db9: state-based reconciliation (label history, plan-then-write, one concurrency group, abort on lookup failure), final-set planning (no empty status), every `#N` in Dependencies counts, merged-PR dependencies, `status:hold`, executor back-off and dependency check, CODEOWNERS and escalation wording (CA-008, scenarios 10–12)
- [x] T013 PR follow-through: Claude subscribes to the PRs it opens (CA-011)
