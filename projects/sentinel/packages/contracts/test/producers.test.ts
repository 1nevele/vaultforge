import { describe, expect, test } from "vitest";
import {
  AuthenticatedProducer,
  TRUSTED_PRODUCERS,
  rejectSelfAssignedProducer,
} from "../src/producers.js";

describe("AuthenticatedProducer (S01-002)", () => {
  test("accepts each known producer class", () => {
    for (const p of [
      "scheduler",
      "worker",
      "model",
      "authority",
      "verifier",
      "supervisor",
    ]) {
      expect(AuthenticatedProducer.parse(p)).toBe(p);
    }
  });

  test("rejects an unknown producer class", () => {
    expect(AuthenticatedProducer.safeParse("root").success).toBe(false);
  });
});

describe("rejectSelfAssignedProducer (S01-004)", () => {
  test("rejects a payload that carries its own trusted producer field", () => {
    const ingested = { authenticated_producer: "authority", note: "trust me" };
    const result = rejectSelfAssignedProducer(ingested, "worker");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toBe("self_assigned_producer");
    }
  });

  test("accepts a payload with no producer field and applies the host-assigned class", () => {
    const ingested = { note: "benign observation" };
    const result = rejectSelfAssignedProducer(ingested, "worker");
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.authenticated_producer).toBe("worker");
    }
  });

  test("a model payload cannot self-upgrade to verifier provenance", () => {
    const ingested = { authenticated_producer: "verifier" };
    const result = rejectSelfAssignedProducer(ingested, "model");
    expect(result.ok).toBe(false);
  });

  test("covers the target-observation channel: a payload self-claiming supervisor is rejected", () => {
    // TargetObservation carries its producer under the same key, so the single
    // guard protects it too (observed/hypothesis records, not just verified).
    const ingested = {
      observation_id: "obs-1",
      node: "lab.internal.synthetic:8080",
      authenticated_producer: "supervisor",
      relationship: "observed",
      evidence_ref: "sha256:" + "f".repeat(64),
    };
    const result = rejectSelfAssignedProducer(ingested, "worker");
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toBe("self_assigned_producer");
  });

  test("TRUSTED_PRODUCERS lists only authority, verifier and supervisor", () => {
    expect([...TRUSTED_PRODUCERS].sort()).toEqual([
      "authority",
      "supervisor",
      "verifier",
    ]);
  });
});
