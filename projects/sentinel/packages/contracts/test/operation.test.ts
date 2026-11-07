import { describe, expect, test } from "vitest";
import {
  OperationRef,
  ReviewRef,
  ReceiptRef,
  checkOperationBinding,
} from "../src/operation.js";

const digest = "sha256:" + "c".repeat(64);
const scriptDigest = "sha256:" + "d".repeat(64);

const validOp = {
  operation_id: "op-1",
  schema_version: "1.0.0",
  command_digest: digest,
  script_digest: scriptDigest,
  expected_actor_generation: 3,
  expires_at: "2026-11-07T01:00:00.000Z",
};

describe("OperationRef (S01-002)", () => {
  test("accepts a canonical operation reference bound by digest + expiry", () => {
    expect(OperationRef.parse(validOp).operation_id).toBe("op-1");
  });

  test("rejects a malformed command digest", () => {
    expect(
      OperationRef.safeParse({ ...validOp, command_digest: "sha256:nope" })
        .success,
    ).toBe(false);
  });

  test("rejects a missing expiry (no open-ended approval)", () => {
    const { expires_at, ...rest } = validOp;
    void expires_at;
    expect(OperationRef.safeParse(rest).success).toBe(false);
  });

  test("rejects an unknown field", () => {
    expect(
      OperationRef.safeParse({ ...validOp, approved: true }).success,
    ).toBe(false);
  });
});

describe("ReviewRef (S01-002)", () => {
  test("binds a review to an operation and canonical content; shape is not approval", () => {
    const review = ReviewRef.parse({
      review_id: "rv-1",
      schema_version: "1.0.0",
      operation_id: "op-1",
      operation_digest: digest,
      expires_at: "2026-11-07T01:00:00.000Z",
    });
    expect(review.operation_id).toBe("op-1");
  });
});

describe("ReceiptRef (S01-002)", () => {
  test("a receipt references the reviewed operation and its canonical digest", () => {
    const receipt = ReceiptRef.parse({
      receipt_id: "rc-1",
      schema_version: "1.0.0",
      operation_id: "op-1",
      operation_digest: digest,
      issued_at: "2026-11-07T00:30:00.000Z",
    });
    expect(receipt.receipt_id).toBe("rc-1");
  });

  test("rejects a receipt whose digest is malformed", () => {
    expect(
      ReceiptRef.safeParse({
        receipt_id: "rc-1",
        schema_version: "1.0.0",
        operation_id: "op-1",
        operation_digest: "not-a-digest",
        issued_at: "2026-11-07T00:30:00.000Z",
      }).success,
    ).toBe(false);
  });
});

describe("checkOperationBinding: identifier/digest mismatch (S01-002)", () => {
  const opDigest = "sha256:" + "e".repeat(64);
  const expected = { operation_id: "op-1", operation_digest: opDigest };
  const review = ReviewRef.parse({
    review_id: "rev-1",
    schema_version: "1.0.0",
    operation_id: "op-1",
    operation_digest: opDigest,
    expires_at: "2026-11-07T01:00:00.000Z",
  });
  const receipt = ReceiptRef.parse({
    receipt_id: "rcpt-1",
    schema_version: "1.0.0",
    operation_id: "op-1",
    operation_digest: opDigest,
    issued_at: "2026-11-07T00:30:00.000Z",
  });

  test("accepts a review and receipt bound to the same operation id and digest", () => {
    expect(checkOperationBinding(OperationRef.parse(validOp).operation_id, opDigest, review)).toEqual({ ok: true });
    expect(checkOperationBinding(expected.operation_id, expected.operation_digest, receipt)).toEqual({ ok: true });
  });

  test("rejects a reference to a different operation id", () => {
    const foreign = ReceiptRef.parse({ ...receipt, operation_id: "op-2" });
    expect(checkOperationBinding(expected.operation_id, expected.operation_digest, foreign)).toEqual({
      ok: false,
      reason: "operation_id_mismatch",
    });
  });

  test("rejects a reference whose canonical digest differs", () => {
    const tampered = ReviewRef.parse({ ...review, operation_digest: "sha256:" + "f".repeat(64) });
    expect(checkOperationBinding(expected.operation_id, expected.operation_digest, tampered)).toEqual({
      ok: false,
      reason: "operation_digest_mismatch",
    });
  });
});
