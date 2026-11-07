/**
 * Mission request and immutable task envelope (S01-002).
 *
 * `.strict()` rejects unknown keys so an untrusted submission cannot smuggle an
 * authority-bearing field (e.g. a self-declared producer or grant). Validation
 * preserves the versioned value; it does not authorize the mission.
 */
import { z } from "zod";
import {
  ClientRequestId,
  MissionId,
  SchemaVersion,
  Sha256Digest,
  TaskId,
  Timestamp,
} from "./common.js";

/**
 * Immutable description of the work. `scope_ref` binds by content digest to a
 * registered Scope; the envelope never inlines mutable authority.
 */
export const TaskEnvelope = z
  .object({
    task_id: TaskId,
    schema_version: SchemaVersion,
    objective: z.string().min(1),
    workflow_template: z.string().min(1),
    scope_ref: Sha256Digest,
  })
  .strict();
export type TaskEnvelope = z.infer<typeof TaskEnvelope>;

export const MissionRequest = z
  .object({
    mission_id: MissionId,
    schema_version: SchemaVersion,
    client_request_id: ClientRequestId,
    task: TaskEnvelope,
    submitted_at: Timestamp,
  })
  .strict();
export type MissionRequest = z.infer<typeof MissionRequest>;
