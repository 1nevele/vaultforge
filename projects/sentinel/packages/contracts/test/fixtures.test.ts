import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { describe, expect, test } from "vitest";
import { MissionRequest } from "../src/mission.js";
import { Scope } from "../src/scope.js";
import { DerivedInferenceRecord } from "../src/derived.js";
import { hostBearingValues } from "./fixture-scan.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(here, "..", "..", "..", "fixtures");

function readFixture(name: string): unknown {
  return JSON.parse(readFileSync(join(fixturesDir, name), "utf8"));
}

function allFixtures(): Array<[string, unknown]> {
  return readdirSync(fixturesDir)
    .filter((f) => f.endsWith(".json"))
    .map((f): [string, unknown] => [f, readFixture(f)]);
}

// RFC 2606 / RFC 6761 names that never resolve to a real host.
const RESERVED_HOST = /\.(test|example|invalid)(:\d+)?$/;

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

  test("adversarial mission request fixture is rejected for its forged producer", () => {
    const r = MissionRequest.safeParse(
      readFixture("mission-request.forged-authority.json"),
    );
    expect(r.success).toBe(false);
    if (!r.success) {
      expect(r.error.issues).toEqual([
        expect.objectContaining({
          code: "unrecognized_keys",
          keys: ["authenticated_producer"],
        }),
      ]);
    }
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

  test("contain no URL of any scheme / provider endpoint", () => {
    expect(/\b[a-z][a-z0-9+.-]*:\/\//i.test(text)).toBe(false);
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

  test("every host-bearing value in every fixture uses a reserved suffix", () => {
    const hosts = allFixtures().flatMap(([name, json]) =>
      hostBearingValues(json).map((h) => `${name}: ${h}`),
    );
    expect(hosts.length).toBeGreaterThan(0);
    const unreserved = hosts.filter((h) => !RESERVED_HOST.test(h));
    expect(unreserved).toEqual([]);
  });
});

describe("hostBearingValues finds hosts anywhere in a fixture", () => {
  test("collects nested scope targets inside a mission request", () => {
    const missionLike = {
      mission: { scope: { targets: ["a.synthetic", "b.example.com"] } },
    };
    expect(hostBearingValues(missionLike)).toEqual([
      "a.synthetic",
      "b.example.com",
    ]);
  });

  test("collects single host and endpoint fields and array items", () => {
    const json = {
      observations: [{ host: "lab.test" }, { endpoint: "x.invalid:8443" }],
    };
    expect(hostBearingValues(json)).toEqual(["lab.test", "x.invalid:8443"]);
  });

  test("collects node, url, domain and ip fields", () => {
    const json = { node: "n.test", url: "u.test", domain: "d.test", ip: "192.0.2.1" };
    expect(hostBearingValues(json)).toEqual(["n.test", "u.test", "d.test", "192.0.2.1"]);
  });

  test("ignores strings under unrelated keys", () => {
    expect(hostBearingValues({ label: "real.example.com" })).toEqual([]);
  });
});
