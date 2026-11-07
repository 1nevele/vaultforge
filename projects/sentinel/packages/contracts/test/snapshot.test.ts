import { describe, expect, test } from "vitest";
import { MissionSnapshot } from "../src/snapshot.js";

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
