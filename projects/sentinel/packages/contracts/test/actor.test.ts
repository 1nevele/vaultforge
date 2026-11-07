import { describe, expect, test } from "vitest";
import { RuntimeActor } from "../src/actor.js";

const validActor = {
  actor_id: "a-1",
  schema_version: "1.0.0",
  role: "runtime",
  execution_generation: 0,
};

describe("RuntimeActor (S01-002)", () => {
  test("accepts a valid actor at generation 0", () => {
    expect(RuntimeActor.parse(validActor).execution_generation).toBe(0);
  });

  test("rejects a negative execution generation", () => {
    expect(
      RuntimeActor.safeParse({ ...validActor, execution_generation: -1 }).success,
    ).toBe(false);
  });

  test("rejects a non-integer execution generation", () => {
    expect(
      RuntimeActor.safeParse({ ...validActor, execution_generation: 1.5 })
        .success,
    ).toBe(false);
  });

  test("rejects an unknown role", () => {
    expect(
      RuntimeActor.safeParse({ ...validActor, role: "god-mode" }).success,
    ).toBe(false);
  });
});
