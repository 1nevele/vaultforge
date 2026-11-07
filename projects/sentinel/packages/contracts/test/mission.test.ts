import { describe, expect, test } from "vitest";
import { MissionRequest, TaskEnvelope } from "../src/mission.js";

const validTask = {
  task_id: "t-1",
  schema_version: "1.0.0",
  objective: "enumerate the synthetic lab web service",
  workflow_template: "web-service-recon",
  scope_ref: "sha256:" + "b".repeat(64),
};

const validRequest = {
  mission_id: "m-1",
  schema_version: "1.0.0",
  client_request_id: "cr-1",
  task: validTask,
  submitted_at: "2026-11-07T00:00:00.000Z",
};

describe("MissionRequest (S01-002)", () => {
  test("accepts a valid synthetic request and preserves the versioned value (scenario 1)", () => {
    const parsed = MissionRequest.parse(validRequest);
    expect(parsed.schema_version).toBe("1.0.0");
    expect(parsed.task.task_id).toBe("t-1");
  });

  test("rejects an unknown top-level authority-bearing field (scenario: forged extra field)", () => {
    const forged = { ...validRequest, authenticated_producer: "authority" };
    expect(MissionRequest.safeParse(forged).success).toBe(false);
  });

  test("rejects an unknown field nested in the task envelope", () => {
    const forged = { ...validRequest, task: { ...validTask, grant: "all" } };
    expect(MissionRequest.safeParse(forged).success).toBe(false);
  });

  test("rejects a malformed schema version", () => {
    const bad = { ...validRequest, schema_version: "1.0" };
    expect(MissionRequest.safeParse(bad).success).toBe(false);
  });
});

describe("TaskEnvelope (S01-002)", () => {
  test("accepts a valid task envelope", () => {
    expect(TaskEnvelope.parse(validTask).workflow_template).toBe(
      "web-service-recon",
    );
  });

  test("rejects a missing objective", () => {
    const { objective, ...rest } = validTask;
    void objective;
    expect(TaskEnvelope.safeParse(rest).success).toBe(false);
  });
});
