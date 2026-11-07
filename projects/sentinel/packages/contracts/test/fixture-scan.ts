/**
 * Test-only helper: collect every host-bearing string in a parsed JSON value,
 * however deeply nested, so the inertness check covers all fixtures rather than
 * one known file (CodeRabbit #21 review).
 */
const HOST_KEY =
  /^(targets?|hosts?|hostnames?|nodes?|addresses?|endpoints?|urls?|domains?|ips?)$/i;

function strings(value: unknown): string[] {
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) return value.flatMap(strings);
  return [];
}

export function hostBearingValues(value: unknown): string[] {
  if (Array.isArray(value)) return value.flatMap(hostBearingValues);
  if (value === null || typeof value !== "object") return [];
  return Object.entries(value).flatMap(([key, child]) =>
    HOST_KEY.test(key) ? strings(child) : hostBearingValues(child),
  );
}
