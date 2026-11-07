import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { describe, expect, test } from "vitest";
import { MissionRequest } from "../src/mission.js";
import { Scope } from "../src/scope.js";
import { DerivedInferenceRecord } from "../src/derived.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(here, "..", "..", "..", "fixtures");

function readFixture(name: string): unknown {
  return JSON.parse(readFileSync(join(fixturesDir, name), "utf8"));
}

function allFixtureText(): string {
  return readdirSync(fixturesDir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => readFileSync(join(fixturesDir, f), "utf8"))
    .join("\n");
}

describe("fixtures validate against their contracts (S01-006)", () => {
  test("valid mission request fixture parses", () => {
    expect(MissionRequest.safeParse(readFixture("mission-request.valid.json")).success).toBe(
      true,
    );
  });

  test("adversarial mission request fixture is rejected", () => {
    expect(
      MissionRequest.safeParse(readFixture("mission-request.forged-authority.json"))
        .success,
    ).toBe(false);
  });

  test("valid scope fixture parses", () => {
    expect(Scope.safeParse(readFixture("scope.valid.json")).success).toBe(true);
  });

  test("valid derived-inference fixture parses with an honest outcome", () => {
    expect(
      DerivedInferenceRecord.safeParse(readFixture("derived-inference.valid.json"))
        .success,
    ).toBe(true);
  });
});

describe("fixtures are synthetic and non-executing (S01-006)", () => {
  const text = allFixtureText();

  test("contain no http(s) URL / provider endpoint", () => {
    expect(/https?:\/\//i.test(text)).toBe(false);
  });

  test("contain no shell shebang or script marker", () => {
    expect(text.includes("#!")).toBe(false);
  });

  test("contain no PEM private-key block", () => {
    expect(/-----BEGIN [A-Z ]*PRIVATE KEY-----/.test(text)).toBe(false);
  });

  test("contain no obvious secret-token prefixes", () => {
    expect(/\b(sk-[a-z0-9]|ghp_[A-Za-z0-9]|AKIA[0-9A-Z]{8})/.test(text)).toBe(
      false,
    );
  });

  test("target hostnames use only non-resolvable reserved suffixes", () => {
    const scope = readFixture("scope.valid.json") as { targets: string[] };
    for (const t of scope.targets) {
      expect(/\.(synthetic|internal|invalid|test|example)(:\d+)?$/.test(t)).toBe(
        true,
      );
    }
  });
});
