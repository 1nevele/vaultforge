import { describe, expect, test } from "vitest";
import { EvidenceRef, checkEvidenceContent } from "../src/evidence.js";
import { Sha256Digest } from "../src/common.js";

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

  test("rejects a malformed content digest", () => {
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

describe("checkEvidenceContent: digest/size mismatch (S01-002)", () => {
  const ref = EvidenceRef.parse({
    evidence_id: "ev-1",
    schema_version: "1.0.0",
    content_digest: "sha256:" + "a".repeat(64),
    media_type: "text/plain",
    size_bytes: 12,
  });

  test("accepts bytes whose observed digest and size match the reference", () => {
    expect(checkEvidenceContent(ref, { digest: Sha256Digest.parse("sha256:" + "a".repeat(64)), size_bytes: 12 })).toEqual({ ok: true });
  });

  test("rejects bytes whose observed digest differs", () => {
    expect(checkEvidenceContent(ref, { digest: Sha256Digest.parse("sha256:" + "b".repeat(64)), size_bytes: 12 })).toEqual({
      ok: false,
      reason: "digest_mismatch",
    });
  });

  test("rejects bytes whose observed size differs", () => {
    expect(checkEvidenceContent(ref, { digest: Sha256Digest.parse("sha256:" + "a".repeat(64)), size_bytes: 13 })).toEqual({
      ok: false,
      reason: "size_mismatch",
    });
  });
});
