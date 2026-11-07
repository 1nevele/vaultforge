/**
 * Registered scope and limits (S01-002).
 *
 * Scope is registration data describing where and what testing effects are in
 * bounds. It is NOT authorization: a dispatch path must still check grants,
 * generation and approval (spec S01-003; review R1 task-vs-operation mediation).
 * The effect/protocol enums are closed so an unknown capability is rejected
 * rather than silently permitted.
 */
import { z } from "zod";
import { SchemaVersionV1 } from "./common.js";

/** Closed set of testing effects the first slice is willing to describe. */
export const TestingEffect = z.enum([
  "http-request",
  "tcp-connect",
  "dns-lookup",
]);
export type TestingEffect = z.infer<typeof TestingEffect>;

export const Protocol = z.enum(["http", "https", "tcp-connect", "dns"]);
export type Protocol = z.infer<typeof Protocol>;

export const Limits = z
  .object({
    max_wall_clock_seconds: z.number().int().positive(),
    max_cost_units: z.number().nonnegative(),
    max_concurrent_workers: z.number().int().positive(),
  })
  .strict();
export type Limits = z.infer<typeof Limits>;

export const Scope = z
  .object({
    scope_id: z.string().min(1),
    schema_version: SchemaVersionV1,
    // Shape-only in S01. A target grammar (hostname/CIDR, no URLs or
    // credentials) is deferred to a later slice and must be enforced before any
    // dispatch path consumes `targets`.
    targets: z.array(z.string().min(1)).min(1),
    protocols: z.array(Protocol).min(1),
    effects: z.array(TestingEffect).min(1),
    limits: Limits,
  })
  .strict();
export type Scope = z.infer<typeof Scope>;
