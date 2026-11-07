import { describe, expect, test } from "vitest";
import { EvidenceRef } from "../src/evidence.js";

const validEvidence = {
  evidence_id: "ev-1",
  schema_version: "1.0.0",
  content_digest: "sha256:" + "e".repeat(64),
  media_type: "text/plain",
  size_bytes: 42,
};

describe("EvidenceRef (S01-002)", () => {
  test("accepts a content-addressed evidence reference with integrity metadata", () => {
    expect(EvidenceRef.parse(validEvidence).size_bytes).toBe(42);
  });

  test("rejects a negative size", () => {
    expect(
      EvidenceRef.safeParse({ ...validEvidence, size_bytes: -1 }).success,
    ).toBe(false);
  });

  test("rejects a mismatched/malformed content digest", () => {
    expect(
      EvidenceRef.safeParse({ ...validEvidence, content_digest: "sha256:zz" })
        .success,
    ).toBe(false);
  });

  test("rejects an unknown field", () => {
    expect(
      EvidenceRef.safeParse({ ...validEvidence, trusted: true }).success,
    ).toBe(false);
  });
});
