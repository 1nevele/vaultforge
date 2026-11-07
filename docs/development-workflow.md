# Vaultforge development workflow

Updated 2026-11-06. Scope: repository preparation and Claude Code **on the web**, not Sentinel execution.

## One workflow

Spec Kit owns one canonical root `specs/<NNN>-<project>-<feature>/{spec,plan,tasks}.md` packet. Existing product plans and research are inputs, not a reason to restart discovery. Superpowers supplies bounded TDD/debugging/verification guidance; it does not create another plan hierarchy. Code review uses the built-in `/code-review` in-session before push (`CLAUDE.md`). Root instructions and project safety rules take precedence over examples in upstream skills.

Eleven prepares specifications, issues and review. Claude Code on the web implements application code. Start S01 (#1), produce a PR with independent review and real tests, then stop. S02–S05 remain blocked on accepted/integrated S01.

## Adopted repository assets

- **Superpowers:** `obra/superpowers@22f0b463e7a5e579904dd6211a520321035526f7` (7.0.2, MIT). Three native, unnamespaced project skills: `test-driven-development`, `systematic-debugging`, `verification-before-completion`. Supporting resources are included. `requesting-code-review` and `receiving-code-review` were retired on 2026-11-07 in favour of the built-in `/code-review`. This is a subset, **not** the complete plugin or its hooks.
- **Spec Kit:** `github/spec-kit@99d10403a2681981be98bd372fa412045180d105` (generator 1.3.2.dev0, MIT). Official Claude integration generated with `specify init <scratch-project> --integration claude --ignore-agent-tools --non-interactive --integration-options="--events false"`. Its nine native `speckit-*` skills, scripts and templates are committed, preserving the custom constitution. Generation used an isolated preparation environment; no cloud or global CLI installation is implied.
- `tools/provenance.json` records source pins, source/output hashes, exact text adaptations, generated-file hashes and licenses. `development-tools.lock.json` describes this executor, not the earlier Hermes installation.
- Superpowers text changes remove included `superpowers:` skill namespaces and replace one reference to an excluded skill-authoring workflow with the explicit cloud smoke-check boundary. No plugin code, automatic hooks, browser companion or diagnostics framework is adopted.

## Cloud loading and readiness

The documented target is an **ordinary repository cloud session**, not a cloud thread inside a Claude project. Claude's cloud documentation supports committed `.claude/skills/`; it does not install repository `enabledPlugins` automatically. Account-enabled skills are a separate option, not a dependency of this setup.

Static hashes and filesystem checks prove repository assets, not model compliance, native discovery or full-plugin behavior. Run the bounded [cloud skill smoke check](claude-web-skill-smoke.md) in a fresh target session before application implementation. Preserve an explicit unavailable/unknown result rather than silently installing plugins or treating a manual file read as native discovery.

There are no repository startup installers or automatic plugin settings. Bundled debugging resources may contain example shell commands or helper scripts: inspect their effects and obtain applicable task authority before explicit use. Do not run optional upstream provider tests, visuals, exports or global setup. This repository does not change the operator's Claude account or Hermes profile.

## Offline checks

```bash
python -B -m unittest discover -s tools/tests -v
for script in .specify/scripts/bash/*.sh; do bash -n "$script" || exit; done
SPECIFY_FEATURE_DIRECTORY=specs/001-sentinel-foundation \
SPECIFY_FEATURE_NO_PERSIST=1 \
.specify/scripts/bash/check-prerequisites.sh --paths-only --json
```

These are setup checks, not application tests or product containment gates. Feature context is process-scoped; do not commit `.specify/feature.json`. No application package manager, provider key or target is needed for these checks.

## History and limits

Historical workflow scope is recorded in [decision 0001](decisions/0001-development-workflow.md) and its dated acceptance note. Those documents do not establish current activation, authorize helpers or transfer exceptional tooling permissions. This change adopts no new global integration.

Missing supplied artifacts remain explicit: the original HTML preview and `sentinel-build-backlog.json` were not provided. The preserved product/execution plans retain their original references; GitHub issues and root specs are the current handoff, not a fabricated replacement for those missing files.

## Source references

- Claude cloud configuration: https://code.claude.com/docs/en/cloud-environments
- Claude skills and project-thread caveats: https://code.claude.com/docs/en/skills
- Spec Kit pinned integration: https://github.com/github/spec-kit/blob/99d10403a2681981be98bd372fa412045180d105/docs/integrations/claude.md
- Superpowers pinned source: https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7
- Maintainer-reported cloud setup example (not independently reproduced): https://github.com/rudolfjs/agent-extensions/commit/4367c887d5fb344daf7ec5256e82011d2299a1ab
