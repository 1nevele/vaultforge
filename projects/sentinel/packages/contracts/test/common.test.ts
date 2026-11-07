import { describe, expect, test } from "vitest";
import {
  SchemaVersion,
  Sha256Digest,
  MissionId,
  CandidateId,
  Timestamp,
} from "../src/common.js";

describe("SchemaVersion (S01-002)", () => {
  test("accepts a well-formed MAJOR.MINOR.PATCH version", () => {
    expect(SchemaVersion.parse("1.0.0")).toBe("1.0.0");
  });

  test("rejects a malformed two-part version", () => {
    expect(SchemaVersion.safeParse("1.0").success).toBe(false);
  });

  test("rejects a non-numeric version", () => {
    expect(SchemaVersion.safeParse("v1.0.0").success).toBe(false);
  });
});

describe("Sha256Digest (S01-002)", () => {
  const good = "sha256:" + "a".repeat(64);

  test("accepts sha256:<64 lowercase hex>", () => {
    expect(Sha256Digest.parse(good)).toBe(good);
  });

  test("rejects a short digest", () => {
    expect(Sha256Digest.safeParse("sha256:xyz").success).toBe(false);
  });

  test("rejects a digest with no algorithm prefix", () => {
    expect(Sha256Digest.safeParse("a".repeat(64)).success).toBe(false);
  });

  test("rejects uppercase hex (non-canonical)", () => {
    expect(Sha256Digest.safeParse("sha256:" + "A".repeat(64)).success).toBe(false);
  });
});

describe("branded ids (S01-002)", () => {
  test("accept non-empty strings", () => {
    expect(MissionId.parse("m-1")).toBe("m-1");
    expect(CandidateId.parse("c-1")).toBe("c-1");
  });

  test("reject empty strings", () => {
    expect(MissionId.safeParse("").success).toBe(false);
    expect(CandidateId.safeParse("").success).toBe(false);
  });
});

describe("Timestamp (S01-002)", () => {
  test("accepts an RFC3339/ISO-8601 UTC instant", () => {
    expect(Timestamp.parse("2026-11-07T00:00:00.000Z")).toBe(
      "2026-11-07T00:00:00.000Z",
    );
  });

  test("rejects a non-timestamp string", () => {
    expect(Timestamp.safeParse("yesterday").success).toBe(false);
  });
});
