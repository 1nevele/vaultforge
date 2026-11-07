import { describe, expect, test } from "vitest";
import {
  CandidateSet,
  Selection,
  resolveSelection,
} from "../src/candidates.js";

const snapshot = CandidateSet.parse({
  candidate_set_version: 7,
  execution_generation: 3,
  schema_version: "1.0.0",
  candidates: [
    { candidate_id: "c-1", label: "enumerate services" },
    { candidate_id: "c-2", label: "fetch banner" },
  ],
});

describe("CandidateSet (S01-003)", () => {
  test("accepts a frozen, versioned candidate set", () => {
    expect(snapshot.candidates).toHaveLength(2);
  });

  test("rejects an unknown field (no inlined parameters)", () => {
    expect(
      CandidateSet.safeParse({
        ...snapshot,
        candidates: [{ candidate_id: "c-1", label: "x", command: "rm -rf /" }],
      }).success,
    ).toBe(false);
  });
});

describe("CandidateSet opaque ids are unique (S01-003)", () => {
  test("rejects a snapshot with a duplicate candidate_id", () => {
    const r = CandidateSet.safeParse({
      ...snapshot,
      candidates: [
        { candidate_id: "c-1", label: "enumerate services" },
        { candidate_id: "c-1", label: "fetch banner" },
      ],
    });
    expect(r.success).toBe(false);
    if (!r.success) expect(r.error.issues[0]?.path).toEqual(["candidates"]);
  });
});

describe("resolveSelection (S01-003)", () => {
  const base = { candidate_set_version: 7, execution_generation: 3 };

  test("resolves an in-snapshot id to that opaque id (scenario 3)", () => {
    const sel = Selection.parse({ kind: "choose", candidate_id: "c-2", ...base });
    const r = resolveSelection(snapshot, sel);
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.candidate_id).toBe("c-2");
  });

  test("resolves an explicit abstention", () => {
    const sel = Selection.parse({ kind: "abstain", ...base });
    const r = resolveSelection(snapshot, sel);
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.candidate_id).toBeNull();
  });

  test("rejects an unknown candidate id", () => {
    const sel = Selection.parse({ kind: "choose", candidate_id: "c-9", ...base });
    const r = resolveSelection(snapshot, sel);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toBe("unknown_candidate");
  });

  test("rejects a stale execution generation", () => {
    const sel = Selection.parse({
      kind: "choose",
      candidate_id: "c-1",
      candidate_set_version: 7,
      execution_generation: 2,
    });
    const r = resolveSelection(snapshot, sel);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toBe("stale_generation");
  });

  test("rejects a stale candidate set version", () => {
    const sel = Selection.parse({
      kind: "choose",
      candidate_id: "c-1",
      candidate_set_version: 6,
      execution_generation: 3,
    });
    const r = resolveSelection(snapshot, sel);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toBe("stale_candidate_set");
  });

  test("a resolved selection never yields executable parameters", () => {
    const sel = Selection.parse({ kind: "choose", candidate_id: "c-1", ...base });
    const r = resolveSelection(snapshot, sel);
    expect(r.ok).toBe(true);
    if (r.ok) expect(Object.keys(r)).toEqual(["ok", "candidate_id"]);
  });
});
