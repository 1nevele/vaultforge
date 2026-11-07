/**
 * Evidence reference and integrity metadata (S01-002).
 *
 * Evidence is content-addressed: the digest identifies the exact bytes. The
 * reference carries integrity/metadata only; the bytes themselves live outside
 * the event envelope (product plan: "Store large or sensitive payloads outside
 * the event envelope"). A reference is not a verified finding.
 */
import { z } from "zod";
import { SchemaVersion, Sha256Digest } from "./common.js";

export const EvidenceRef = z
  .object({
    evidence_id: z.string().min(1),
    schema_version: SchemaVersion,
    content_digest: Sha256Digest,
    media_type: z.string().min(1),
    size_bytes: z.number().int().nonnegative(),
  })
  .strict();
export type EvidenceRef = z.infer<typeof EvidenceRef>;
