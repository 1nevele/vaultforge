# 001 — Tasks: Sentinel offline contract foundation (S01)

Dependency-ordered. Each task is RED→GREEN where it adds behavior. IDs trace to
`spec.md` requirements S01-001…S01-007. `[x]` is only set after the verification
command was actually run and observed (verification-before-completion).

## Setup

- [x] T001 (S01-001) Create `projects/sentinel/` workspace: `package.json`,
  `pnpm-workspace.yaml`, `tsconfig.base.json`, pinned devDeps
  (typescript 5.9.3, vitest 5.0.5, zod 4.6.6, @types/node 22.20.5), `packageManager`
  pinned. `pnpm install` produces a committed lockfile. No global installs.
- [x] T002 (S01-001) Create `packages/contracts/` package.json + tsconfig (extends
  base, `strict: true`), vitest config, and `pnpm` scripts: `typecheck`, `build`,
  `test`. Confirm empty `tsc --noEmit` and `vitest run` succeed on a trivial module.

## Contracts (TDD: test first, then schema)

- [x] T003 (S01-002) `common.ts`: branded `SchemaVersion`, `Sha256Digest`,
  `MissionId`, `OperationId`, `ActorId`, `EventId`, opaque `CandidateId`, cursor types.
  RED: reject malformed version `"1.0"`, bad digest `"sha256:xyz"`; GREEN: accept
  `"1.0.0"`, `"sha256:"+64hex`.
- [x] T004 (S01-002,004) `producers.ts`: closed `AuthenticatedProducer` enum
  (`scheduler|worker|model|authority|verifier|supervisor`) + trust-class helpers.
  RED: a payload object carrying its own `authenticated_producer: "authority"` is
  rejected by `rejectSelfAssignedProducer`; GREEN: host-assigned producer passed as a
  separate argument is accepted.
- [x] T005 (S01-002) `mission.ts`: `MissionRequest` + immutable `TaskEnvelope` with
  client request id. RED: extra authority field rejected (`.strict`), malformed
  version rejected; GREEN: valid synthetic request round-trips and preserves the
  versioned value (spec scenario 1).
- [x] T006 (S01-002) `scope.ts`: registered `Scope` + `Limits` (protocols, testing
  effects, time/cost caps). RED: unknown effect / negative limit rejected; GREEN:
  valid scope accepted. Note: scope shape is registration data, not authorization.
- [x] T007 (S01-002) `actor.ts`: `RuntimeActor` + `ExecutionGeneration` (monotonic).
  RED: non-integer / negative generation rejected; GREEN: valid actor accepted.
- [x] T008 (S01-003) `candidates.ts`: immutable `CandidateSet` (versioned, frozen),
  `Selection` (opaque id | abstention), and `resolveSelection`. RED: unknown id,
  stale generation, stale set version each rejected with a typed reason; selection
  never yields parameters. GREEN: in-snapshot id resolves to that opaque id; explicit
  abstention resolves to abstention (spec scenario 3).
- [x] T009 (S01-002) `operation.ts`: canonical `OperationRef`, `ReviewRef`,
  `ReceiptRef` bound by content digest + expected versions + expiry. RED: malformed
  digest / missing expiry rejected; `checkOperationBinding` rejects an operation id or
  canonical digest mismatch (T022); GREEN: valid refs accepted. Shape is not approval.
- [x] T010 (S01-002) `evidence.ts`: `EvidenceRef` + integrity metadata
  (content-addressed digest, size, media type). RED: malformed digest rejected;
  `checkEvidenceContent` rejects observed digest/size mismatch (T022); GREEN: valid
  ref accepted.
- [x] T011 (S01-002) `targets.ts`: `TargetObservation` with
  hypothesis/observed/verified relationship labels kept distinct. RED: a record
  asserting `verified` without a verifier producer is rejected; GREEN: observed /
  hypothesis records accepted. (Verification itself is out of scope.)
- [x] T012 (S01-002,004) `events.ts`: event envelope
  (`event_id, mission_id, projection_sequence, schema_version, actor_id,
  execution_generation, operation_id, event_type, authenticated_producer,
  correlation_id, causation_id, timestamp, payload_reference`) + public event union.
  RED: event whose `event_type` is not owned by its producer rejected; unknown extra
  field rejected. GREEN: valid authority-receipt event accepted.
- [x] T013 (S01-002) `snapshot.ts`: `MissionSnapshot` + `ProjectionCursor`. RED:
  negative cursor rejected; `checkEventAfterSnapshot` rejects an event behind or
  ahead of the cursor, from another mission or from an older generation (T022);
  GREEN: valid snapshot+cursor accepted.
- [x] T014 (S01-005) `derived.ts`: `DerivedInferenceRecord` v1. RED: missing
  canonical/rendered input hash, missing span offset unit, or a forbidden `verified`
  field rejected; `outcome` outside `completed|abstained|failed|unknown` rejected.
  GREEN: honest `failed`/`unknown` record with lineage + completeness accepted
  (spec S01-005).
- [x] T015 `index.ts`: `CONTRACTS_SCHEMA_VERSION` constant + re-exports. Typecheck
  passes.

## Fixtures

- [x] T016 (S01-006) `fixtures/` synthetic JSON for the mission request (valid and
  forged-authority), scope and derived-inference contracts, plus `README.md`
  declaring them synthetic and non-executing. Other contracts' valid/adversarial
  cases live in their unit tests; shared adversarial fixtures for later lanes
  (stale selection, producer-spoofed event, self-verified target) are deferred. RED/assert: a test
  scans fixtures and fails if any contains a script, secret-shaped token, resolvable
  host, or provider endpoint (no execution surface).

## Verification + handoff

- [x] T017 (S01-007) Run and record: `pnpm --dir projects/sentinel install
  --frozen-lockfile`, `typecheck`, `build`, `test` with observed counts; re-run the
  repository-level offline checks. Confirm fresh-checkout reproducibility; no provider
  credentials used.
- [x] T018 (S01-007) Add the pinned `sentinel-contracts` CI job. Label it a setup/unit
  gate, not G0–G8.
- [x] T019 (S01-007) Independent spec/code review via `requesting-code-review` with a
  fresh reviewer; record findings + resolutions.
- [x] T020 Open the S01 PR: changed paths, requirement→test map, commands + observed
  RED/GREEN, skipped gates, trust assumptions, blockers. Stop; no merge, no self-close,
  no unlock of #2–#5. (PR #21.)
- [x] T021 (S01-002, S01-003, S01-005, S01-006) Address CodeRabbit review of PR #21,
  RED first: unique `candidate_id` per `CandidateSet`; canonical `SchemaVersion` (no
  leading zeros); shared `Generation`/`Sequence` brands on every generation/sequence
  field (type-level test); Z-only `Timestamp` pinned by test; issue-path assertions
  and span/lineage boundary tests for `DerivedInferenceRecord`; fixture host scan
  over every host-bearing value in every fixture. Shape-vs-semantics boundary notes on
  `RuntimeActor`, `Scope.targets` and `DerivedInferenceRecord`. Declined: rejecting
  `completed` + truncated/partial records (an honest disclosure, not an
  inconsistency), span-to-artifact binding (spans carry no artifact reference) and
  arbitrary string length limits (no spec limit); recorded as downstream boundary
  duties.
- [x] T022 (S01-002, S01-005, S01-006) Address the independent re-review of PR #21,
  RED first: `checkOperationBinding`, `checkEvidenceContent` and
  `checkEventAfterSnapshot` implement the mismatch/cursor checks T009, T010 and T013
  claimed; `SchemaVersionV1` makes every record's `schema_version` reject other major
  versions; `SourceSpan.artifact_hash` must name one of a non-empty
  `source_artifact_hashes` (reverses T021's span decline); `operation.*` events need a
  non-null `operation_id`; `candidate_set_version` uses the `Generation` brand;
  forged-key tests assert `unrecognized_keys`; `failed`/`abstained` outcomes accepted;
  fixture scan covers `node`/`url`/`domain`/`ip` keys and URLs of any scheme, and
  fixture hosts use only RFC 2606 names. Deferred: readonly/frozen candidate sets,
  distinct brand for adapter/rubric/policy versions, whitespace/control-character
  ids, scope coherence (duplicates, effect-vs-protocol), `packageManager` hash pin.

## Requirement → task map

| Req | Tasks |
| --- | --- |
| S01-001 | T001, T002 |
| S01-002 | T003, T005–T013 |
| S01-003 | T008 |
| S01-004 | T004, T012 |
| S01-005 | T014 |
| S01-006 | T016 |
| S01-007 | T017–T020 |
| Review | T021, T022 |
