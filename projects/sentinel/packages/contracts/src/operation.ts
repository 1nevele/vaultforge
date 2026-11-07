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
import { OperationId, SchemaVersion, Sha256Digest, Timestamp } from "./common.js";

export const OperationRef = z
  .object({
    operation_id: OperationId,
    schema_version: SchemaVersion,
    command_digest: Sha256Digest,
    script_digest: Sha256Digest,
    expected_actor_generation: z.number().int().nonnegative(),
    expires_at: Timestamp,
  })
  .strict();
export type OperationRef = z.infer<typeof OperationRef>;

export const ReviewRef = z
  .object({
    review_id: z.string().min(1),
    schema_version: SchemaVersion,
    operation_id: OperationId,
    operation_digest: Sha256Digest,
    expires_at: Timestamp,
  })
  .strict();
export type ReviewRef = z.infer<typeof ReviewRef>;

export const ReceiptRef = z
  .object({
    receipt_id: z.string().min(1),
    schema_version: SchemaVersion,
    operation_id: OperationId,
    operation_digest: Sha256Digest,
    issued_at: Timestamp,
  })
  .strict();
export type ReceiptRef = z.infer<typeof ReceiptRef>;
