import { describe, expect, test } from "vitest";
import { Scope, Limits, TestingEffect } from "../src/scope.js";

const validScope = {
  scope_id: "s-1",
  schema_version: "1.0.0",
  targets: ["lab.internal.synthetic"],
  protocols: ["http", "tcp-connect"],
  effects: ["http-request", "tcp-connect"],
  limits: {
    max_wall_clock_seconds: 3600,
    max_cost_units: 100,
    max_concurrent_workers: 1,
  },
};

describe("Scope (S01-002)", () => {
  test("accepts a valid registered scope", () => {
    const parsed = Scope.parse(validScope);
    expect(parsed.protocols).toContain("http");
  });

  test("rejects an unknown testing effect", () => {
    const bad = { ...validScope, effects: ["launch-nukes"] };
    expect(Scope.safeParse(bad).success).toBe(false);
  });

  test("rejects an unknown extra field (shape is registration data, not authority)", () => {
    const bad = { ...validScope, approved: true };
    expect(Scope.safeParse(bad).success).toBe(false);
  });

  test("rejects an empty target list", () => {
    const bad = { ...validScope, targets: [] };
    expect(Scope.safeParse(bad).success).toBe(false);
  });
});

describe("Limits (S01-002)", () => {
  test("rejects a negative wall-clock limit", () => {
    expect(
      Limits.safeParse({
        max_wall_clock_seconds: -1,
        max_cost_units: 1,
        max_concurrent_workers: 1,
      }).success,
    ).toBe(false);
  });

  test("rejects zero concurrent workers (one active worker is the floor)", () => {
    expect(
      Limits.safeParse({
        max_wall_clock_seconds: 1,
        max_cost_units: 1,
        max_concurrent_workers: 0,
      }).success,
    ).toBe(false);
  });
});

describe("TestingEffect (S01-002)", () => {
  test("is a closed enum", () => {
    expect(TestingEffect.safeParse("udp-flood").success).toBe(false);
    expect(TestingEffect.parse("http-request")).toBe("http-request");
  });
});
