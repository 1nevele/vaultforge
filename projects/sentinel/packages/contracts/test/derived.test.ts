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

/** Paths of every validation issue, so a test cannot pass for the wrong reason. */
function rejectedPaths(input: unknown): PropertyKey[][] {
  const r = DerivedInferenceRecord.safeParse(input);
  if (r.success) return [];
  return r.error.issues.map((i) => i.path);
}

const withSpan = (span: unknown) => ({ ...valid, source_spans: [span] });

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
    expect(rejectedPaths({ ...valid, outcome: "verified" })).toEqual([
      ["outcome"],
    ]);
  });

  test("rejects a record missing the rendered provider input hash", () => {
    const { rendered_provider_input_hash, ...rest } = valid;
    void rendered_provider_input_hash;
    expect(rejectedPaths(rest)).toEqual([["rendered_provider_input_hash"]]);
  });

  test("rejects a span missing its offset unit (S01-005 span encoding)", () => {
    const bad = {
      ...valid,
      source_spans: [{ start: 0, end: 4 }],
    };
    expect(rejectedPaths(bad)).toEqual([["source_spans", 0, "offset_unit"]]);
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

describe("SourceSpan and lineage boundaries (S01-005)", () => {
  test("rejects a negative start offset", () => {
    expect(
      rejectedPaths(withSpan({ start: -1, end: 4, offset_unit: "utf8-byte" })),
    ).toEqual([["source_spans", 0, "start"]]);
  });

  test("rejects a non-integer end offset", () => {
    expect(
      rejectedPaths(withSpan({ start: 0, end: 4.5, offset_unit: "utf8-byte" })),
    ).toEqual([["source_spans", 0, "end"]]);
  });

  test("rejects a span whose end precedes its start", () => {
    expect(
      rejectedPaths(withSpan({ start: 5, end: 4, offset_unit: "utf8-byte" })),
    ).toEqual([["source_spans", 0, "end"]]);
  });

  test("accepts an empty span (start === end)", () => {
    expect(
      rejectedPaths(withSpan({ start: 4, end: 4, offset_unit: "codepoint" })),
    ).toEqual([]);
  });

  test("rejects an empty transformation lineage", () => {
    expect(rejectedPaths({ ...valid, transformation_lineage: [] })).toEqual([
      ["transformation_lineage"],
    ]);
  });
});
