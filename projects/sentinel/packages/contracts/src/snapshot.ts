/**
 * Mission projection snapshot and cursor (S01-002).
 *
 * The UI hydrates from a snapshot at a cursor and subscribes after it (product
 * plan: "Hydrate snapshot at cursor S, subscribe after S"). The cursor is a
 * projection sequence, not a timestamp — UI timestamps do not establish
 * ordering or causality.
 */
import { z } from "zod";
import { Generation, MissionId, SchemaVersion, Sequence } from "./common.js";

export const MissionStatus = z.enum([
  "pending",
  "running",
  "stopping",
  "stopped",
  "failed",
  "unknown",
]);
export type MissionStatus = z.infer<typeof MissionStatus>;

export const ProjectionCursor = z
  .object({
    projection_sequence: Sequence,
  })
  .strict();
export type ProjectionCursor = z.infer<typeof ProjectionCursor>;

export const MissionSnapshot = z
  .object({
    mission_id: MissionId,
    schema_version: SchemaVersion,
    status: MissionStatus,
    execution_generation: Generation,
    cursor: ProjectionCursor,
  })
  .strict();
export type MissionSnapshot = z.infer<typeof MissionSnapshot>;
