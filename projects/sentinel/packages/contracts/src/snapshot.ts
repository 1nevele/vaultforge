/**
 * Mission projection snapshot and cursor (S01-002).
 *
 * The UI hydrates from a snapshot at a cursor and subscribes after it (product
 * plan: "Hydrate snapshot at cursor S, subscribe after S"). The cursor is a
 * projection sequence, not a timestamp — UI timestamps do not establish
 * ordering or causality.
 */
import { z } from "zod";
import { Generation, MissionId, SchemaVersionV1, Sequence } from "./common.js";
import type { EventEnvelope } from "./events.js";

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
    schema_version: SchemaVersionV1,
    status: MissionStatus,
    execution_generation: Generation,
    cursor: ProjectionCursor,
  })
  .strict();
export type MissionSnapshot = z.infer<typeof MissionSnapshot>;

export type CursorCheckResult =
  | { ok: true }
  | {
      ok: false;
      reason: "foreign_mission" | "already_in_snapshot" | "sequence_gap";
    };

/**
 * Check that an event is the next one to apply after a snapshot: same mission
 * and exactly one past the cursor. An event at or behind the cursor is already
 * reflected in the snapshot; one further ahead means events were missed and the
 * client must re-hydrate. Generation is deliberately not checked here: fencing
 * obsolete workers happens before an event is sequenced, so a sequenced event
 * from an older generation is part of the log and must still be applied.
 */
export function checkEventAfterSnapshot(
  snapshot: MissionSnapshot,
  event: EventEnvelope,
): CursorCheckResult {
  if (event.mission_id !== snapshot.mission_id) {
    return { ok: false, reason: "foreign_mission" };
  }
  const cursor = snapshot.cursor.projection_sequence;
  if (event.projection_sequence <= cursor) {
    return { ok: false, reason: "already_in_snapshot" };
  }
  if (event.projection_sequence !== cursor + 1) {
    return { ok: false, reason: "sequence_gap" };
  }
  return { ok: true };
}
