# Vaultforge agent rules

Roles and the flow of work are in `docs/operating-model.md`. Project rules live next to
the code (for Sentinel, `projects/sentinel/AGENTS.md`).

- No secrets, private host paths, credentials, live provider spend, target operations,
  infrastructure or account changes, publication or destructive cleanup without the
  host's explicit authority.
- Do not disable scans or broaden permissions.
- Preserve original evidence and its lineage; model output is not verified evidence.
- Report the tests you actually ran, what you skipped and what blocked you. CI or a demo
  does not prove live integration or containment.
- Read back what you write to external systems before claiming it happened.
- Never initialize a second Git repository inside a project.
