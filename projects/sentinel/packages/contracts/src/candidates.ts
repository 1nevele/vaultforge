/**
 * Immutable candidate set and selection (S01-003).
 *
 * Code constructs the frozen candidate snapshot; the selector returns an opaque
 * id or abstains. `resolveSelection` resolves ONLY to an opaque id present in the
 * host-frozen snapshot, or an abstention, and rejects a stale generation, a stale
 * set version or an unknown id. It never invents or returns executable parameters
 * (product plan: "Jev selects an action ID or abstains"; review Jev hazard).
 */
import { z } from "zod";
import { CandidateId, Generation, SchemaVersionV1 } from "./common.js";

/** A candidate carries an opaque id and a human label — never a command. */
export const Candidate = z
  .object({
    candidate_id: CandidateId,
    label: z.string().min(1),
  })
  .strict();
export type Candidate = z.infer<typeof Candidate>;

export const CandidateSet = z
  .object({
    candidate_set_version: Generation,
    execution_generation: Generation,
    schema_version: SchemaVersionV1,
    candidates: z.array(Candidate),
  })
  .strict()
  .refine(
    (s) =>
      new Set(s.candidates.map((c) => c.candidate_id)).size ===
      s.candidates.length,
    // A duplicated opaque id would make a selection ambiguous.
    { message: "candidate_id values must be unique", path: ["candidates"] },
  );
export type CandidateSet = z.infer<typeof CandidateSet>;

/** A selection names the set + generation it was made against, so staleness is detectable. */
export const Selection = z.discriminatedUnion("kind", [
  z
    .object({
      kind: z.literal("choose"),
      candidate_id: CandidateId,
      candidate_set_version: Generation,
      execution_generation: Generation,
    })
    .strict(),
  z
    .object({
      kind: z.literal("abstain"),
      candidate_set_version: Generation,
      execution_generation: Generation,
    })
    .strict(),
]);
export type Selection = z.infer<typeof Selection>;

export type SelectionResolution =
  | { ok: true; candidate_id: CandidateId | null }
  | {
      ok: false;
      reason:
        | "stale_generation"
        | "stale_candidate_set"
        | "unknown_candidate";
    };

/**
 * Resolve a selection against the frozen snapshot. Staleness is checked before
 * membership so an out-of-date decision never resolves, even if the id happens to
 * still exist.
 */
export function resolveSelection(
  snapshot: CandidateSet,
  selection: Selection,
): SelectionResolution {
  if (selection.execution_generation !== snapshot.execution_generation) {
    return { ok: false, reason: "stale_generation" };
  }
  if (selection.candidate_set_version !== snapshot.candidate_set_version) {
    return { ok: false, reason: "stale_candidate_set" };
  }
  if (selection.kind === "abstain") {
    return { ok: true, candidate_id: null };
  }
  const found = snapshot.candidates.some(
    (c) => c.candidate_id === selection.candidate_id,
  );
  if (!found) {
    return { ok: false, reason: "unknown_candidate" };
  }
  return { ok: true, candidate_id: selection.candidate_id };
}
