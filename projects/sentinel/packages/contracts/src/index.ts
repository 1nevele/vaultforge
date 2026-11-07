/**
 * @sentinel/contracts — versioned offline schemas for the Sentinel foundation (S01).
 *
 * Validation only. Nothing here authenticates a caller, approves a grant, or
 * performs an effect. Consumers (mission service, authority, UI, worker — all
 * future slices) import these to parse and reject untrusted shapes at their
 * boundaries.
 */
export const CONTRACTS_SCHEMA_VERSION = "1.0.0" as const;

export * from "./common.js";
export * from "./producers.js";
export * from "./mission.js";
export * from "./scope.js";
export * from "./actor.js";
export * from "./candidates.js";
export * from "./operation.js";
export * from "./evidence.js";
export * from "./targets.js";
export * from "./events.js";
export * from "./snapshot.js";
export * from "./derived.js";
