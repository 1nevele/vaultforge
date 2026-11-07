# 002 — Tasks

- [x] T001 Replace issue-implementation workflow with `@claude` small-fix workflow (CA-005, CA-007)
- [x] T002 Update root agent instructions and workflow docs (CA-001–CA-006)
- [x] T003 Create the Claude cloud scheduled task with the CA-001–CA-004 prompt (outside repo) — created "Vaultforge ready-issue executor", every 4 hours
- [ ] T004 Close PRs #9, #10, #11, #15 (done) and delete their branches (pending: needs operator; the executor session may push only its own branch)
- [x] T006 Create the event-triggered task "Vaultforge issue-opened executor" (outside repo, no schedule) with the same rules plus a triggering-issue early exit and a post-claim concurrency check
- [ ] T007 Operator: add the GitHub "Issue opened" trigger and the repository to that task at claude.ai/code/routines (cannot be done from a cloud session)
- [ ] T005 Live acceptance: scenarios 1–5, with session handle and GitHub readback
