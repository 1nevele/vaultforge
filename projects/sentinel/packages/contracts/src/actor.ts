/**
 * Runtime actor instance and execution generation (S01-002).
 *
 * The execution generation fences obsolete workers: a late event from an older
 * generation must not reactivate the current worker (product plan: "Use
 * execution generations to fence obsolete workers"). Roles are a closed set so
 * the UI cannot be told an actor is a producer class it is not.
 */
import { z } from "zod";
import { ActorId, Generation, SchemaVersionV1 } from "./common.js";

export const ActorRole = z.enum([
  "runtime",
  "selector",
  "worker",
  "supervisor",
  "verifier",
]);
export type ActorRole = z.infer<typeof ActorRole>;

/**
 * A parsed RuntimeActor proves only shape. It does not authenticate the caller or
 * establish that it holds `role`: privileged roles must be assigned host-side at
 * an authenticated boundary, never trusted from untrusted input (S01-004).
 */
export const RuntimeActor = z
  .object({
    actor_id: ActorId,
    schema_version: SchemaVersionV1,
    role: ActorRole,
    execution_generation: Generation,
  })
  .strict();
export type RuntimeActor = z.infer<typeof RuntimeActor>;
