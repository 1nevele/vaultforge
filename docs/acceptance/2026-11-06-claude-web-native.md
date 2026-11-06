# Claude-web native repository setup acceptance

Date: 2026-11-06. Scope: Vaultforge development assets and handoff only.

## Configuration adopted

- Private repository remains `1nevele/vaultforge`; publication history is privacy-sanitized. Sentinel plans, research and project rules live under `projects/sentinel/`.
- Five Superpowers native skills at `22f0b463e7a5e579904dd6211a520321035526f7`: test-driven development, systematic debugging, requesting/receiving review, and verification before completion. Twelve files include the required supporting resources. This is not the complete plugin.
- Nine official Claude Spec Kit skills and committed scripts/templates/metadata were generated from `99d10403a2681981be98bd372fa412045180d105`, integration `claude`, events disabled. Twenty-eight generated files are recorded, excluding the custom project constitution.
- Both MIT licenses, complete adopted-file hashes and exact text adaptations are in `tools/provenance.json`. The repository lock now identifies `claude-code-web`, not historical Hermes activation.
- No startup download/install hook, automatic plugin settings, browser companion, diagnostic framework or new global integration. No Sentinel application code or local dependency scaffold is published by this setup.

## Historical offline observations — not rerun by this note

The original record listed these repository checks; results below describe only that historical setup, not the sanitized publication tree:

```bash
python -B -m unittest discover -s tools/tests -v
for script in .specify/scripts/bash/*.sh; do bash -n "$script" || exit; done
SPECIFY_FEATURE_DIRECTORY=specs/001-sentinel-foundation \
SPECIFY_FEATURE_NO_PERSIST=1 \
.specify/scripts/bash/check-prerequisites.sh --paths-only --json
git diff --check
git diff --cached --check
```

- Ten setup checks passed. These cover inventory, hashes, safe manifest paths, native names, supporting resources, official skill-manifest hashes, entry-point paths and no automatic bootstrap/plugin configuration. They do not prove Claude execution/compliance.
- Bash syntax checks passed; S01 feature resolution returned the existing spec and expected future plan/tasks paths without creating persistent feature context.
- Parent independently verified each of twelve adopted Superpowers source hashes against the pinned checkout, replayed every recorded adaptation and compared exact output bytes. All twenty-eight official generated files matched their scratch-generation originals.
- Plan/research/decision artifacts have since been privacy-sanitized. Earlier relocation byte-identity comparisons are superseded and do not verify the sanitized content.
- A disposable source copy without global skills passed all ten setup checks. Appending bytes to a copied skill failed integrity checking; replacing a copied skill with a symlink failed safe-path checking. Restoring it returned all ten checks to passing.
- Spec Kit's real `--require-tasks --include-tasks --json` check exited 1 because S01 `plan.md` does not exist yet. This is the expected negative prerequisite result, not successful application analysis. No plan/tasks were fabricated to hide it.

## Scope of asset adaptations

The provenance record describes the bounded native namespace, canonical-path and excluded-workflow adaptations. Those records identify asset bytes; they do not prove cloud activation or model compliance. Personal setup and troubleshooting history is not retained here.

## Independent review

A separate non-author read-only review found no material local-setup blocker. The reviewer independently ran all ten setup checks, Bash syntax checks and process-scoped feature resolution; replayed the twelve Superpowers asset adaptations against pinned upstream; checked both license byte identities; and inspected the official generated integration. Parent reran the ten checks after review: all passed. This is conditional repository-readiness review only, not approval of untested Claude-web behavior.

## Real Claude-web check: BLOCKED / NOT EXERCISED

No successful Claude-web session or native skill discovery/loading is established by this historical record. Account access and activation must be checked separately. Do not install host packages, reconfigure accounts/tools, access provider keys or substitute local execution merely to conceal a failed prerequisite.

The bounded test and evidence requirements are in `docs/claude-web-skill-smoke.md`. `cloud_session_tested` remains false in the lock and provenance. A future ordinary repository cloud session must actually discover/invoke the intended skills before S01 implementation starts.

## Publication history

Publication history was privacy-sanitized; earlier revision and file-hash readbacks are superseded and are not proof of current repository state. Fresh verification is required before publication.

Issue readiness is not a Claude session. S01 is the bounded starting assignment; dependent work remains blocked on accepted prerequisites.

No application tests, product providers/targets, sandbox/inference custody, containment, OS authority or G0–G8 product gate was exercised or passed by these checks. Missing original preview/backlog inputs remain explicit in the workflow documentation.
