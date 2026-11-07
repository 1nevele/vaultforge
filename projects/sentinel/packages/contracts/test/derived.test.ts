import { describe, expect, test } from "vitest";
import { DerivedInferenceRecord } from "../src/derived.js";

const digest = (c: string) => "sha256:" + c.repeat(64);

const valid = {
  inference_id: "inf-1",
  mission_id: "m-1",
  execution_generation: 1,
  schema_version: "1.0.0",
  task_kind: "classify",
  provider: "scaledown",
  model_id: "classify-small",
  adapter_version: "1.0.0",
  rubric_schema_version: "1.0.0",
  data_policy_version: "1.0.0",
  source_artifact_hashes: [digest("1")],
  evidence_snapshot_hash: digest("2"),
  canonical_input_hash: digest("3"),
  rendered_provider_input_hash: digest("4"),
  score_semantics: "softmax-normalized label scores summing to 1.0",
  source_spans: [{ start: 0, end: 4, offset_unit: "utf8-byte" }],
  transformation_lineage: ["raw", "normalized"],
  completeness_flags: { truncated: false, partial: false },
  outcome: "completed",
};

describe("DerivedInferenceRecord v1 (S01-005)", () => {
  test("accepts an honest completed record with lineage and completeness", () => {
    expect(DerivedInferenceRecord.parse(valid).outcome).toBe("completed");
  });

  test("accepts an honest 'unknown' outcome", () => {
    expect(
      DerivedInferenceRecord.parse({ ...valid, outcome: "unknown" }).outcome,
    ).toBe("unknown");
  });

  test("rejects an outcome outside the closed set", () => {
    expect(
      DerivedInferenceRecord.safeParse({ ...valid, outcome: "verified" })
        .success,
    ).toBe(false);
  });

  test("rejects a record missing the rendered provider input hash", () => {
    const { rendered_provider_input_hash, ...rest } = valid;
    void rendered_provider_input_hash;
    expect(DerivedInferenceRecord.safeParse(rest).success).toBe(false);
  });

  test("rejects a span missing its offset unit (S01-005 span encoding)", () => {
    const bad = {
      ...valid,
      source_spans: [{ start: 0, end: 4 }],
    };
    expect(DerivedInferenceRecord.safeParse(bad).success).toBe(false);
  });

  test("rejects a forbidden 'verified' field — derived records cannot mint findings", () => {
    const bad = { ...valid, verified: true };
    expect(DerivedInferenceRecord.safeParse(bad).success).toBe(false);
  });

  test("rejects a span whose offset unit is not a known encoding", () => {
    const bad = {
      ...valid,
      source_spans: [{ start: 0, end: 4, offset_unit: "furlongs" }],
    };
    expect(DerivedInferenceRecord.safeParse(bad).success).toBe(false);
  });
});
