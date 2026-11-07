import { describe, expect, test } from "vitest";
import { MissionSnapshot, checkEventAfterSnapshot } from "../src/snapshot.js";
import { EventEnvelope } from "../src/events.js";

const valid = {
  mission_id: "m-1",
  schema_version: "1.0.0",
  status: "running",
  execution_generation: 2,
  cursor: { projection_sequence: 10 },
};

describe("MissionSnapshot (S01-002)", () => {
  test("accepts a valid snapshot with a projection cursor", () => {
    expect(MissionSnapshot.parse(valid).cursor.projection_sequence).toBe(10);
  });

  test("rejects an unknown mission status", () => {
    expect(
      MissionSnapshot.safeParse({ ...valid, status: "owned" }).success,
    ).toBe(false);
  });

  test("rejects a negative cursor sequence", () => {
    expect(
      MissionSnapshot.safeParse({
        ...valid,
        cursor: { projection_sequence: -1 },
      }).success,
    ).toBe(false);
  });

  test("rejects an unknown field", () => {
    expect(MissionSnapshot.safeParse({ ...valid, live: true }).success).toBe(
      false,
    );
  });
});

describe("checkEventAfterSnapshot: cursor behind/ahead (S01-002)", () => {
  const snapshot = MissionSnapshot.parse(valid);
  const event = (overrides: Record<string, unknown>) =>
    EventEnvelope.parse({
      event_id: "e-11",
      mission_id: "m-1",
      projection_sequence: 11,
      schema_version: "1.0.0",
      actor_id: "a-1",
      execution_generation: 2,
      operation_id: null,
      authenticated_producer: "worker",
      event_type: "execution.observation",
      correlation_id: "corr-1",
      causation_id: "cause-1",
      timestamp: "2026-11-07T00:00:00.000Z",
      payload_reference: "sha256:" + "a".repeat(64),
      ...overrides,
    });

  test("accepts the next event after the cursor", () => {
    expect(checkEventAfterSnapshot(snapshot, event({}))).toEqual({ ok: true });
  });

  test("rejects an event already covered by the snapshot (behind the cursor)", () => {
    expect(checkEventAfterSnapshot(snapshot, event({ projection_sequence: 10 }))).toEqual({
      ok: false,
      reason: "already_in_snapshot",
    });
  });

  test("rejects an event that skips ahead of the cursor (gap)", () => {
    expect(checkEventAfterSnapshot(snapshot, event({ projection_sequence: 13 }))).toEqual({
      ok: false,
      reason: "sequence_gap",
    });
  });

  test("rejects an event from another mission", () => {
    expect(checkEventAfterSnapshot(snapshot, event({ mission_id: "m-2" }))).toEqual({
      ok: false,
      reason: "foreign_mission",
    });
  });

  test("applies a sequenced event from an older generation (fencing is the writer's job)", () => {
    expect(checkEventAfterSnapshot(snapshot, event({ execution_generation: 1 }))).toEqual({
      ok: true,
    });
  });
});
