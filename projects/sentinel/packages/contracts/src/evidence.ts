/**
 * Evidence reference and integrity metadata (S01-002).
 *
 * Evidence is content-addressed: the digest identifies the exact bytes. The
 * reference carries integrity/metadata only; the bytes themselves live outside
 * the event envelope (product plan: "Store large or sensitive payloads outside
 * the event envelope"). A reference is not a verified finding.
 */
import { z } from "zod";
import { SchemaVersionV1, Sha256Digest } from "./common.js";

export const EvidenceRef = z
  .object({
    evidence_id: z.string().min(1),
    schema_version: SchemaVersionV1,
    content_digest: Sha256Digest,
    media_type: z.string().min(1),
    size_bytes: z.number().int().nonnegative(),
  })
  .strict();
export type EvidenceRef = z.infer<typeof EvidenceRef>;

export type EvidenceContentResult =
  | { ok: true }
  | { ok: false; reason: "digest_mismatch" | "size_mismatch" };

/**
 * Check observed bytes against an evidence reference (S01-002 "reject digest
 * mismatches"). The caller hashes the bytes it actually holds; a reference whose
 * declared digest or size disagrees with them is rejected.
 */
export function checkEvidenceContent(
  ref: EvidenceRef,
  observed: { digest: Sha256Digest; size_bytes: number },
): EvidenceContentResult {
  if (observed.digest !== ref.content_digest) {
    return { ok: false, reason: "digest_mismatch" };
  }
  if (observed.size_bytes !== ref.size_bytes) {
    return { ok: false, reason: "size_mismatch" };
  }
  return { ok: true };
}
