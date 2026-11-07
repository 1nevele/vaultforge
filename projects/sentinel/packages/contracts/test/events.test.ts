import { describe, expect, expectTypeOf, test } from "vitest";
import {
  EventEnvelope,
  EVENT_TYPE_OWNERS,
  type EventEnvelope as EventEnvelopeType,
  type EventType,
} from "../src/events.js";

const base = {
  event_id: "e-1",
  mission_id: "m-1",
  projection_sequence: 0,
  schema_version: "1.0.0",
  actor_id: "a-1",
  execution_generation: 0,
  operation_id: "op-1",
  authenticated_producer: "authority",
  event_type: "operation.receipt.issued",
  correlation_id: "corr-1",
  causation_id: "cause-1",
  timestamp: "2026-11-07T00:00:00.000Z",
  payload_reference: "sha256:" + "a".repeat(64),
};

describe("EventEnvelope (S01-002)", () => {
  test("accepts a valid authority-receipt event whose producer owns the type", () => {
    expect(EventEnvelope.parse(base).event_type).toBe(
      "operation.receipt.issued",
    );
  });

  test("rejects an unknown extra field", () => {
    expect(EventEnvelope.safeParse({ ...base, forged: 1 }).success).toBe(false);
  });

  test("rejects an event whose producer does not own the event type (S01-004)", () => {
    const spoofed = {
      ...base,
      authenticated_producer: "worker",
      event_type: "operation.receipt.issued",
    };
    expect(EventEnvelope.safeParse(spoofed).success).toBe(false);
  });

  test("rejects an unknown event type", () => {
    expect(
      EventEnvelope.safeParse({ ...base, event_type: "mission.pwned" }).success,
    ).toBe(false);
  });

  test("allows a nullable operation_id for non-operation events", () => {
    const ev = {
      ...base,
      authenticated_producer: "supervisor",
      event_type: "actor.started",
      operation_id: null,
    };
    expect(EventEnvelope.parse(ev).operation_id).toBeNull();
  });

  test("EVENT_TYPE_OWNERS maps a verified-finding event to the verifier only", () => {
    expect(EVENT_TYPE_OWNERS["finding.verified"]).toBe("verifier");
  });

  test("the frozen event_type is the precise union, not widened to string", () => {
    // Compile-time assertion (checked by `pnpm typecheck`): the inferred field
    // type must be the EventType union, so downstream exhaustiveness holds.
    expectTypeOf<EventEnvelopeType["event_type"]>().toEqualTypeOf<EventType>();
    expectTypeOf<EventType>().not.toEqualTypeOf<string>();
  });
});
