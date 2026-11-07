import { describe, expect, test } from "vitest";
import { SchemaVersionV1 } from "../src/common.js";
import { Scope } from "../src/scope.js";
import { RuntimeActor } from "../src/actor.js";
import { CandidateSet } from "../src/candidates.js";
import { EvidenceRef } from "../src/evidence.js";
import { OperationRef, ReceiptRef, ReviewRef } from "../src/operation.js";
import { MissionRequest, TaskEnvelope } from "../src/mission.js";
import { EventEnvelope } from "../src/events.js";
import { TargetObservation } from "../src/targets.js";
import { DerivedInferenceRecord } from "../src/derived.js";
import { MissionSnapshot } from "../src/snapshot.js";

describe("SchemaVersionV1 fences the major version (S01-002)", () => {
  test.each(["1.0.0", "1.2.3"])("accepts v1 version %s", (v) => {
    expect(SchemaVersionV1.safeParse(v).success).toBe(true);
  });

  test.each(["2.0.0", "0.9.0", "10.0.0"])("rejects non-v1 version %s", (v) => {
    expect(SchemaVersionV1.safeParse(v).success).toBe(false);
  });
});

const records = {
  Scope,
  RuntimeActor,
  CandidateSet,
  EvidenceRef,
  OperationRef,
  ReviewRef,
  ReceiptRef,
  MissionRequest,
  TaskEnvelope,
  EventEnvelope,
  TargetObservation,
  DerivedInferenceRecord,
  MissionSnapshot,
};

describe("every v1 record rejects another major schema_version (S01-002)", () => {
  test.each(Object.entries(records))("%s rejects schema_version 2.0.0", (_, schema) => {
    const field = schema.shape.schema_version;
    expect(field.safeParse("1.0.0").success).toBe(true);
    expect(field.safeParse("2.0.0").success).toBe(false);
  });
});
