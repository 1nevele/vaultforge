# 001 — Plan: Sentinel offline contract foundation (S01)

Status: implementation plan for Claude Code on the web. Derives from `spec.md`, the
Sentinel execution plan (§§7,10,12), the product plan and the 2026-11-05 architecture
review. No human sign-off on a detailed API beyond this packet is implied.

## Scope

Build the smallest **offline** TypeScript contract + fixture foundation under
`projects/sentinel/packages/contracts/`. Validation only: parse/normalize/reject
untrusted shapes. No runtime, no network, no provider calls, no execution surface.
This slice freezes interfaces that S02–S05 integrate against; it does not implement
them.

## Toolchain (detected, then pinned)

Detected in the actual Claude web environment: Node `v22.23.4`, pnpm `10.28.0`
(Corepack-managed), x86_64 Ubuntu 24.04. The cloud host is **not** the unverified
Apple Silicon/macOS deployment target (product plan §2); nothing here depends on the
deployment platform.

Pinned, exact versions (chosen as mature, mutually compatible, not bleeding-edge):

| Dependency | Version | Rationale |
| --- | --- | --- |
| TypeScript | `5.9.3` | Stable; strict mode; avoids the just-released 7.x ecosystem churn. |
| vitest | `5.0.5` | Current stable line; engines allow Node 22.12+. |
| zod | `4.6.6` | Runtime schema validation with strict/branded types; one minor behind newest. |
| @types/node | `22.20.5` | Matches the Node 22 runtime. |

No global installs, no `-g`, no upgrade of the host toolchain. `packageManager` is
pinned in `package.json` so Corepack resolves the same pnpm. Lockfile committed.

## Architecture

One package, no premature splitting (constitution §6; execution plan §6 "create only
the packages needed"):

```text
projects/sentinel/
  package.json                 # pnpm workspace root for the project
  pnpm-workspace.yaml
  tsconfig.base.json
  packages/contracts/
    package.json
    tsconfig.json
    src/
      common.ts                # branded primitives: digests, versions, ids, hashes
      producers.ts             # authenticated producer trust classes (S01-002/004)
      mission.ts               # mission request + immutable task envelope (S01-002)
      scope.ts                 # registered scope + limits (S01-002)
      actor.ts                 # runtime actor instance + execution generation (S01-002)
      candidates.ts            # immutable candidate set + selection/abstention (S01-003)
      operation.ts             # canonical operation / review / receipt refs (S01-002)
      evidence.ts              # evidence reference + integrity metadata (S01-002)
      targets.ts               # target observations + hypothesis relations (S01-002)
      events.ts                # public event envelope + producer union (S01-002/004)
      snapshot.ts              # mission projection snapshot + cursor (S01-002)
      derived.ts               # DerivedInferenceRecord v1 (CDM) (S01-005)
      index.ts                 # version constant + re-exports
    test/
      <one *.test.ts per module, RED/GREEN mapped to S01-00x>
  fixtures/
    README.md                  # states fixtures are synthetic + non-executing
    *.json                     # synthetic valid + adversarial inputs (S01-006)
```

## Design decisions

1. **Validation is not authority.** Every schema doc comment repeats: shape
   validation is not authentication, grant approval or execution authority
   (spec S01-003; review R1). Contracts carry no code that performs an effect.
2. **Branded identifiers.** Digests, schema versions, ids and hashes are zod
   branded strings with explicit format checks (semver-ish `MAJOR.MINOR.PATCH`;
   `sha256:<64 hex>`), so a plain string cannot be passed where an identity is
   required. Rejects malformed versions and identifier/digest mismatches (S01-002).
3. **`.strict()` everywhere.** Objects reject unknown keys, so an untrusted payload
   cannot smuggle an authority-bearing extra field (S01-002, S01-004).
4. **Producer trust assigned, never accepted.** `authenticated_producer` is a closed
   enum. A helper `rejectSelfAssignedProducer` proves a worker/model-ingested payload
   claiming `authority`/`verifier`/`supervisor` provenance is rejected at the ingest
   boundary (S01-004; review R3/§7). The trusted class is applied by the host at
   authenticated ingestion, modeled here as a separate function input, not a payload
   field.
5. **Selection normalization.** `resolveSelection(snapshot, selection)` returns the
   opaque candidate id, or an abstention, or a typed rejection for: unknown id, stale
   `execution_generation`, stale `candidate_set_version`. It never invents executable
   parameters (S01-003; review on Jev candidate rendering).
6. **Derived records are honest.** `DerivedInferenceRecord` requires source/evidence
   hashes, canonical + rendered input hashes, adapter/rubric/model versions, score
   semantics, span encoding + offset unit, completeness flags, lineage, and an
   `outcome` of `completed|abstained|failed|unknown`. Derived records cannot carry a
   `verified` field; verification is out of scope for S01 (S01-005; review §2).
7. **Fixtures synthetic + inert.** JSON only, no scripts, no secrets, no hostnames
   that resolve, no provider endpoints. A test asserts fixtures contain no execution
   surface (S01-006).

## Verification strategy (RED → GREEN)

Each requirement maps to named tests. TDD: write a failing test referencing the
behavior, then the schema, then confirm GREEN. Offline-only; runs with no provider
credentials and no network (spec scenario 4).

Project commands (new, scoped to the project — not the deferred product commands in
execution plan §12):

```bash
pnpm --dir projects/sentinel install --frozen-lockfile
pnpm --dir projects/sentinel typecheck   # tsc --noEmit, strict
pnpm --dir projects/sentinel build       # tsc emit to dist/
pnpm --dir projects/sentinel test         # vitest run
```

Repository-level offline checks (`docs/development-workflow.md`) remain unchanged and
must still pass.

## CI

Add a `sentinel-contracts` job to `.github/workflows/repository-checks.yml` (pinned
`actions/checkout` and `actions/setup-node` by SHA, `persist-credentials: false`,
`corepack enable`, `--frozen-lockfile`, then typecheck + build + test). This is a
setup/unit gate, explicitly **not** a G0–G8 security or live-integration gate
(spec S01-007; execution plan §10). Editing this workflow is a CI-policy change, so
the PR needs the host's explicit go-ahead before Eleven merges it.

## Ownership and serialization

Claude lead owns: the project manifests, `pnpm-workspace.yaml`, the contracts package,
fixtures, and the one serialized edit to the root CI workflow. No other lane runs in
this slice, so there is no concurrent path contention. Later lanes request shared
changes rather than racing them (constitution §4).

## Out of scope / explicit non-goals

No mission service, scheduler, SSE, SQLite, authority service, Jev/Codex/CDM adapters,
MCP server, UI, VM/worker, or any network/provider/target code. No `pnpm dev`, no
`demo`. Missing live prerequisites stay blocked, not mocked (execution plan §13).

## Stop condition

Open one PR for S01 with changed paths, the requirement→test map, the exact commands
run and observed RED/GREEN output, independent review notes, skipped gates and
blockers. Do not merge, self-close #1, or unlock #2–#5.
