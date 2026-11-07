/**
 * Authenticated producer trust classes (S01-002, S01-004).
 *
 * Trusted producer identity is assigned by the host at authenticated ingestion;
 * it is NEVER accepted from an agent-controlled payload field (execution plan §7).
 * The helper below models that boundary: an ingested payload that tries to carry
 * its own `authenticated_producer` is rejected, and the trusted class is supplied
 * separately by the authenticated transport.
 */
import { z } from "zod";

export const AuthenticatedProducer = z.enum([
  "scheduler",
  "worker",
  "model",
  "authority",
  "verifier",
  "supervisor",
]);
export type AuthenticatedProducer = z.infer<typeof AuthenticatedProducer>;

/**
 * Producer classes whose assertions establish privileged outcomes. A worker or
 * model payload can never self-assign one of these (S01-004). Authority receipts
 * establish authorization; the verifier establishes verified findings; the
 * supervisor reports facts measured outside the guest.
 */
export const TRUSTED_PRODUCERS: ReadonlySet<AuthenticatedProducer> = new Set([
  "authority",
  "verifier",
  "supervisor",
]);

export type IngestResult =
  | { ok: true; authenticated_producer: AuthenticatedProducer }
  | { ok: false; reason: "self_assigned_producer" | "unknown_producer" };

/**
 * Reject a payload that attempts to declare its own producer provenance, and
 * otherwise stamp it with the class the authenticated transport supplies.
 *
 * `hostAssigned` comes from the trusted ingest layer, not the payload. Shape
 * validation of the payload is not authentication; this function exists to make
 * the "never trust a payload-declared producer" rule executable and testable.
 */
export function rejectSelfAssignedProducer(
  payload: Record<string, unknown>,
  hostAssigned: AuthenticatedProducer,
): IngestResult {
  if ("authenticated_producer" in payload) {
    return { ok: false, reason: "self_assigned_producer" };
  }
  const assigned = AuthenticatedProducer.safeParse(hostAssigned);
  if (!assigned.success) {
    return { ok: false, reason: "unknown_producer" };
  }
  return { ok: true, authenticated_producer: assigned.data };
}
