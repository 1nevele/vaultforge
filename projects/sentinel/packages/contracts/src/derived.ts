/**
 * Derived inference record v1 — the CDM contract (S01-005).
 *
 * A host-owned record of a constrained-decoding / model transformation. It is
 * NOT a provider-returned authority token (review §2). It records source and
 * evidence hashes, canonical and rendered provider input identity, adapter /
 * rubric / model / data-policy versions, score semantics, span encoding with an
 * explicit offset unit, transformation lineage, completeness flags, and an honest
 * outcome. It can never carry a `verified` field: hash identity is not truth, and
 * a derived record cannot manufacture a verified finding. `.strict()` enforces
 * that no such field (or any other) is smuggled in.
 */
import { z } from "zod";
import { MissionId, SchemaVersion, Sha256Digest } from "./common.js";

/** Offset unit must be explicit so a character vs byte ambiguity cannot hide. */
export const OffsetUnit = z.enum(["utf8-byte", "utf16-code-unit", "codepoint"]);
export type OffsetUnit = z.infer<typeof OffsetUnit>;

export const SourceSpan = z
  .object({
    start: z.number().int().nonnegative(),
    end: z.number().int().nonnegative(),
    offset_unit: OffsetUnit,
  })
  .strict()
  .refine((s) => s.end >= s.start, {
    message: "span end must be >= start",
    path: ["end"],
  });
export type SourceSpan = z.infer<typeof SourceSpan>;

export const DerivedOutcome = z.enum([
  "completed",
  "abstained",
  "failed",
  "unknown",
]);
export type DerivedOutcome = z.infer<typeof DerivedOutcome>;

export const CompletenessFlags = z
  .object({
    truncated: z.boolean(),
    partial: z.boolean(),
  })
  .strict();
export type CompletenessFlags = z.infer<typeof CompletenessFlags>;

export const DerivedInferenceRecord = z
  .object({
    inference_id: z.string().min(1),
    mission_id: MissionId,
    execution_generation: z.number().int().nonnegative(),
    schema_version: SchemaVersion,
    task_kind: z.enum(["classify", "extract", "summarize", "compress", "select"]),
    provider: z.string().min(1),
    model_id: z.string().min(1),
    adapter_version: SchemaVersion,
    rubric_schema_version: SchemaVersion,
    data_policy_version: SchemaVersion,
    source_artifact_hashes: z.array(Sha256Digest),
    evidence_snapshot_hash: Sha256Digest,
    canonical_input_hash: Sha256Digest,
    rendered_provider_input_hash: Sha256Digest,
    score_semantics: z.string().min(1),
    source_spans: z.array(SourceSpan),
    transformation_lineage: z.array(z.string().min(1)).min(1),
    completeness_flags: CompletenessFlags,
    outcome: DerivedOutcome,
  })
  .strict();
export type DerivedInferenceRecord = z.infer<typeof DerivedInferenceRecord>;
