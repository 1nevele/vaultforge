# Vaultforge Monorepo Setup Plan

**Goal:** Prepare the private monorepo and actual Claude-web skill/issue handoff without application coding.
**Architecture:** Preserve repository identity and design lineage; publication history is subject to privacy sanitation; Sentinel product artifacts under projects/sentinel; one shared root spec/agent workflow. Pin upstream tooling without global Hermes integration.
**Spec:** spec.md.

## Ordered work

- [x] Inspect actual repo identity/privacy, collision-free name, tracked/untracked state and primary tooling docs.
- [x] Rename remote/update origin; move Sentinel artifacts with history. Exclude unaccepted local scaffold from publication; do not delete unrelated local artifacts.
- [x] Configure five pinned native Superpowers skills and nine official Claude Spec Kit skills, licenses and provenance; no full-plugin behavior claimed.
- [x] Write root/project agent rules and a draft offline-foundation specification.
- [x] Create/read back a tracker plus S01–S05 issues with scope, dependencies, tests and stop conditions.
- [x] Exercise offline checks and independent setup review; fix material findings. No material local blocker remains; real Claude-web discovery is separately untested.
- [ ] Publish explicit setup paths; verify private repo identity/revision and consequential file hashes.

## Review focus

Fresh checkout without global skills; namespace/invocation mismatch; unsafe relative paths; broken monorepo links; unsupported cloud-activation assumptions; accidental local scaffold/secrets publication. Actual cloud dispatch is a separate observed state.

No competing implementation-plan tree and no local application execution. Claude web implements future feature issues and stops at a reviewed PR.
