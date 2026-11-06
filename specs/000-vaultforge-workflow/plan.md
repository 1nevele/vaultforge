# Vaultforge Monorepo Setup Plan

**Goal:** Prepare the publication-ready monorepo and actual Claude-web skill/issue handoff without application coding.
**Architecture:** Preserve design lineage, but supersede original repository-identity preservation with the authorized fresh-repository migration in VF-001. Keep the original private and publish only reviewed sanitized history in the fresh destination; Sentinel product artifacts under projects/sentinel; one shared root spec/agent workflow. Pin upstream tooling without global Hermes integration.
**Spec:** spec.md.

## Ordered work

- [x] Inspect actual repo identity/privacy, collision-free name, tracked/untracked state and primary tooling docs.
- [x] Preserve the original privately under a separate name; create the fresh destination; sanitize all reachable history before publishing there; update origin. This replaces the original identity-preserving rename step. Exclude unaccepted local scaffold; do not delete unrelated local artifacts.
- [x] Configure five pinned native Superpowers skills and nine official Claude Spec Kit skills, licenses and provenance; no full-plugin behavior claimed.
- [x] Write root/project agent rules and a draft offline-foundation specification.
- [x] Create/read back a tracker plus S01–S05 issues with scope, dependencies, tests and stop conditions.
- [x] Exercise offline checks and independent setup review; fix material findings. Fresh sanitized-tree verification on 2026-11-06 passed all ten workflow tests, Bash syntax/feature-context checks, actionlint, official CodeRabbit schema validation and Gitleaks scans. GitHub Actions passed both main-push and PR checks. Real Claude-web discovery remains untested; CodeRabbit installation/first review and final publication settings require separate live verification.
- [ ] Verify authorized repository identity, visibility, sanitized revision and consequential file hashes. Publication history was privacy-sanitized; earlier revision and file-hash readbacks are superseded and are not proof of current repository state. Fresh verification is required before publication.

## Review focus

Fresh checkout without global skills; namespace/invocation mismatch; unsafe relative paths; broken monorepo links; unsupported cloud-activation assumptions; accidental local scaffold/secrets publication. Actual cloud dispatch is a separate observed state.

No competing implementation-plan tree and no local application execution. Claude web implements future feature issues and stops at a reviewed PR.
