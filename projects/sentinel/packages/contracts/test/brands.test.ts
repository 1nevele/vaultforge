import { describe, expectTypeOf, test } from "vitest";
import type { Generation, Sequence } from "../src/common.js";
import type { CandidateSet, Selection } from "../src/candidates.js";
import type { MissionSnapshot, ProjectionCursor } from "../src/snapshot.js";
import type { EventEnvelope } from "../src/events.js";
import type { DerivedInferenceRecord } from "../src/derived.js";
import type { OperationRef } from "../src/operation.js";

// Fencing values must carry the shared brands, so an unbranded number cannot be
// passed where a fenced generation/sequence is expected (CodeRabbit #21 review).
describe("generation and sequence fields use the shared brands (S01-002)", () => {
  test("execution_generation is a branded Generation everywhere", () => {
    expectTypeOf<CandidateSet["execution_generation"]>().toEqualTypeOf<Generation>();
    expectTypeOf<Selection["execution_generation"]>().toEqualTypeOf<Generation>();
    expectTypeOf<MissionSnapshot["execution_generation"]>().toEqualTypeOf<Generation>();
    expectTypeOf<EventEnvelope["execution_generation"]>().toEqualTypeOf<Generation>();
    expectTypeOf<DerivedInferenceRecord["execution_generation"]>().toEqualTypeOf<Generation>();
    expectTypeOf<OperationRef["expected_actor_generation"]>().toEqualTypeOf<Generation>();
  });

  test("projection_sequence is a branded Sequence everywhere", () => {
    expectTypeOf<ProjectionCursor["projection_sequence"]>().toEqualTypeOf<Sequence>();
    expectTypeOf<EventEnvelope["projection_sequence"]>().toEqualTypeOf<Sequence>();
  });
});
