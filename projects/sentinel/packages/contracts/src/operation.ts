/**
 * Canonical operation, review and receipt references (S01-002).
 *
 * Operations are bound to the executable/script bytes (digests), the expected
 * actor generation and an explicit expiry — not to a bare command string
 * (review R7: "Bind operations to executable/script bytes ... not just a command
 * string"). These are references; a passing shape is NOT an approval. Only an
 * authority-issued receipt (established at an authenticated boundary, outside
 * this contract package) authorizes an operation.
 */
import { z } from "zod";
import {
  Generation,
  OperationId,
  SchemaVersionV1,
  Sha256Digest,
  Timestamp,
} from "./common.js";

export const OperationRef = z
  .object({
    operation_id: OperationId,
    schema_version: SchemaVersionV1,
    command_digest: Sha256Digest,
    script_digest: Sha256Digest,
    expected_actor_generation: Generation,
    expires_at: Timestamp,
  })
  .strict();
export type OperationRef = z.infer<typeof OperationRef>;

export const ReviewRef = z
  .object({
    review_id: z.string().min(1),
    schema_version: SchemaVersionV1,
    operation_id: OperationId,
    operation_digest: Sha256Digest,
    expires_at: Timestamp,
  })
  .strict();
export type ReviewRef = z.infer<typeof ReviewRef>;

export const ReceiptRef = z
  .object({
    receipt_id: z.string().min(1),
    schema_version: SchemaVersionV1,
    operation_id: OperationId,
    operation_digest: Sha256Digest,
    issued_at: Timestamp,
  })
  .strict();
export type ReceiptRef = z.infer<typeof ReceiptRef>;

export type OperationBindingResult =
  | { ok: true }
  | { ok: false; reason: "operation_id_mismatch" | "operation_digest_mismatch" };

/**
 * Check that a review or receipt references exactly the operation it claims:
 * same operation id and same canonical operation digest (S01-002 "reject
 * identifier/digest mismatches"). The expected digest is computed by the host
 * over the canonical operation; this helper only compares. Passing it is NOT an
 * approval — authority is established outside this package.
 */
export function checkOperationBinding(
  expectedOperationId: string,
  expectedOperationDigest: string,
  ref: ReviewRef | ReceiptRef,
): OperationBindingResult {
  if (ref.operation_id !== expectedOperationId) {
    return { ok: false, reason: "operation_id_mismatch" };
  }
  if (ref.operation_digest !== expectedOperationDigest) {
    return { ok: false, reason: "operation_digest_mismatch" };
  }
  return { ok: true };
}
