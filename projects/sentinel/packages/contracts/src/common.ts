/**
 * Shared primitive schemas for Sentinel contracts (S01-002).
 *
 * These are branded, format-checked strings. Shape validation here is NOT
 * authentication, grant approval or execution authority (spec S01-003). A value
 * passing one of these schemas means only that its bytes are well-formed.
 */
import { z } from "zod";

/**
 * Schema version: MAJOR.MINOR.PATCH, digits only, no leading zeros, so one
 * version has exactly one accepted encoding (same canonical-form rule as
 * Sha256Digest).
 */
export const SchemaVersion = z
  .string()
  .regex(/^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/, "expected MAJOR.MINOR.PATCH")
  .brand<"SchemaVersion">();
export type SchemaVersion = z.infer<typeof SchemaVersion>;

/**
 * Content-addressed digest: `sha256:` followed by exactly 64 lowercase hex
 * characters. Uppercase is rejected so the encoded form is canonical and two
 * encodings of the same bytes cannot disagree (spec S01-002: reject digest
 * mismatches).
 */
export const Sha256Digest = z
  .string()
  .regex(/^sha256:[0-9a-f]{64}$/, "expected sha256:<64 lowercase hex>")
  .brand<"Sha256Digest">();
export type Sha256Digest = z.infer<typeof Sha256Digest>;

/** A non-empty identifier, branded per domain so ids are not interchangeable. */
const brandedId = <B extends string>(brand: B) =>
  z.string().min(1).brand<B>();

export const MissionId = brandedId("MissionId");
export type MissionId = z.infer<typeof MissionId>;

export const TaskId = brandedId("TaskId");
export type TaskId = z.infer<typeof TaskId>;

export const ActorId = brandedId("ActorId");
export type ActorId = z.infer<typeof ActorId>;

export const OperationId = brandedId("OperationId");
export type OperationId = z.infer<typeof OperationId>;

export const EventId = brandedId("EventId");
export type EventId = z.infer<typeof EventId>;

/** Opaque candidate identifier. Opaque: carries no executable parameters. */
export const CandidateId = brandedId("CandidateId");
export type CandidateId = z.infer<typeof CandidateId>;

export const ClientRequestId = brandedId("ClientRequestId");
export type ClientRequestId = z.infer<typeof ClientRequestId>;

/**
 * RFC3339 / ISO-8601 instant in UTC with a `Z` suffix only; explicit offsets
 * such as `+00:00` are rejected so one instant has one encoding. Display/order
 * aid only; not a causality source.
 */
export const Timestamp = z
  .string()
  .datetime({ offset: false })
  .brand<"Timestamp">();
export type Timestamp = z.infer<typeof Timestamp>;

/**
 * Monotonic non-negative integer used to fence obsolete workers (execution
 * generation) and to version frozen candidate sets. A stale value must be
 * rejected by consumers, not silently accepted.
 */
export const Generation = z.number().int().nonnegative().brand<"Generation">();
export type Generation = z.infer<typeof Generation>;

/** Projection sequence: monotonic non-negative integer. */
export const Sequence = z.number().int().nonnegative().brand<"Sequence">();
export type Sequence = z.infer<typeof Sequence>;
