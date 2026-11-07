/**
 * Target observations and hypothesis/observed/verified relationships (S01-002).
 *
 * Suspected and verified are kept distinct (product plan: "Suspected and
 * verified edges have distinct labels and styles"). A `verified` relationship is
 * only valid when the producer is the `verifier` trust class — a worker or model
 * cannot mint a verified finding (S01-004; review R5). Verification itself is out
 * of scope for S01; this only enforces that the claim cannot be self-assigned.
 */
import { z } from "zod";
import { AuthenticatedProducer } from "./producers.js";
import { SchemaVersion, Sha256Digest } from "./common.js";

export const TargetRelationship = z.enum([
  "hypothesis",
  "observed",
  "verified",
]);
export type TargetRelationship = z.infer<typeof TargetRelationship>;

export const TargetObservation = z
  .object({
    observation_id: z.string().min(1),
    schema_version: SchemaVersion,
    node: z.string().min(1),
    // Same field name as EventEnvelope and the key rejectSelfAssignedProducer
    // inspects, so the single ingest guard covers this record's producer channel
    // too — not only the verified→verifier refine below (S01-004).
    authenticated_producer: AuthenticatedProducer,
    relationship: TargetRelationship,
    evidence_ref: Sha256Digest,
  })
  .strict()
  .refine(
    (o) =>
      o.relationship !== "verified" || o.authenticated_producer === "verifier",
    {
      message: "only the verifier producer may assert a verified relationship",
      path: ["relationship"],
    },
  );
export type TargetObservation = z.infer<typeof TargetObservation>;
