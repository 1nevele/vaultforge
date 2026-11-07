import { describe, expect, test } from "vitest";
import { TargetObservation } from "../src/targets.js";

const base = {
  observation_id: "obs-1",
  schema_version: "1.0.0",
  node: "lab.internal.synthetic:8080",
  authenticated_producer: "worker",
  evidence_ref: "sha256:" + "f".repeat(64),
};

describe("TargetObservation (S01-002)", () => {
  test("accepts a worker-reported observed relationship", () => {
    const o = TargetObservation.parse({ ...base, relationship: "observed" });
    expect(o.relationship).toBe("observed");
  });

  test("names the producer channel 'authenticated_producer', matching the ingest guard (S01-004)", () => {
    // The field must share its name with EventEnvelope and with the key that
    // rejectSelfAssignedProducer inspects, so one guard covers this record too.
    const o = TargetObservation.parse({ ...base, relationship: "observed" });
    expect(o.authenticated_producer).toBe("worker");
  });

  test("accepts a hypothesis marker from a model producer", () => {
    const o = TargetObservation.parse({
      ...base,
      authenticated_producer: "model",
      relationship: "hypothesis",
    });
    expect(o.relationship).toBe("hypothesis");
  });

  test("rejects a 'verified' relationship from a non-verifier producer (S01-004)", () => {
    expect(
      TargetObservation.safeParse({
        ...base,
        authenticated_producer: "worker",
        relationship: "verified",
      }).success,
    ).toBe(false);
  });

  test("accepts 'verified' only when the producer is the verifier", () => {
    const o = TargetObservation.parse({
      ...base,
      authenticated_producer: "verifier",
      relationship: "verified",
    });
    expect(o.authenticated_producer).toBe("verifier");
  });

  test("rejects an unknown relationship label", () => {
    expect(
      TargetObservation.safeParse({ ...base, relationship: "pwned" }).success,
    ).toBe(false);
  });
});
