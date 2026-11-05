# 0001 — One spec-driven workflow, with Superpowers execution

Date: 2026-11-05. Historical workflow scope only; personal installation and troubleshooting details have been removed. This decision does not establish current tool activation.

## Decision

Use one canonical project constitution and `specs/<feature>/{spec,plan,tasks}.md` set. Requirements and acceptance scenarios precede application logic. Superpowers is the proposed implementation/TDD/debugging/review layer, not a second planning system or runtime security boundary. Existing Sentinel product and execution plans plus the architecture review are design inputs; do not restart product discovery or ask the operator to repeat them.

RAPTOR-first evaluation is independent from development-agent tooling. Neither Superpowers nor Spec Kit is a hacking engine, worker sandbox or authorization service.

## Superpowers adoption conditions

Pinned upstream: `obra/superpowers@22f0b463e7a5e579904dd6211a520321035526f7`, manifest 7.0.2, MIT.

Tooling adoption requires independent review of the pinned registration path, skill-triggered scripts and warning categories. Do not disable scanning, update to an unreviewed revision, run upstream provider harnesses, replace built-in tools or restart services as incidental setup. Any exceptional action needs separate, narrowly scoped authority.

Verify package integrity, supported validation, registration and native skill loading before claiming activation. Record failed checks and distinguish filesystem preparation, process activation and fresh-session behavior; do not infer one from another. This historical decision supplies no current verification result.

Do not start the optional visual companion/branding telemetry or provider-backed evaluation scripts. No whole-repository safety or exploit-free claim follows from this scoped review.

## Spec Kit scope decision

Inspected upstream: `github/spec-kit@99d10403a2681981be98bd372fa412045180d105` (MIT). Adopt its spec/plan/task conventions; this historical decision supplies no current CLI or slash-command activation evidence.

The pinned native Hermes integration writes shared `~/.hermes/skills/speckit-*` files. Its documentation warns setup may replace another project's skills and teardown removes all global `speckit-*` directories, including edited ones. Source resolves `Path.home()` rather than a profile-aware destination. Therefore do not run native integration initialization/uninstall as an incidental project setup step. A future CLI adoption needs a scoped, reviewed installation/update/removal strategy; project conventions do not require those global writes.

## Verification expectations

After tooling acceptance, create the first application feature spec and test mapping, then work through RED/GREEN and an independent review. Planning or scaffolding alone does not satisfy S01. Publish changes through verified private GitHub targets; no automatic application merge.

## Primary references

- https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7
- https://github.com/github/spec-kit/blob/99d10403a2681981be98bd372fa412045180d105/docs/integrations/hermes.md
- https://github.com/github/spec-kit/blob/99d10403a2681981be98bd372fa412045180d105/src/specify_cli/integrations/hermes/__init__.py
- https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins
