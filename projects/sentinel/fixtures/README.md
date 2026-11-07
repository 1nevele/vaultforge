# Sentinel contract fixtures

**Synthetic and explicitly non-executing (S01-006).**

These JSON files are hand-written examples used only by the offline contract
tests in `packages/contracts/test/`. They exist to exercise schema
validation — valid shapes that must parse, and adversarial shapes that must be
rejected.

They are **not** live data and carry **no execution capability**:

- No secrets, API keys, tokens or credentials.
- No URLs (of any scheme) or provider endpoints.
- No shell, script, or command content.
- Hostnames use only the reserved top-level names `.test`, `.example` and
  `.invalid` (RFC 2606 / RFC 6761), which never resolve to a real host.
- Digests (`sha256:…`) are placeholder byte strings, not real content hashes of
  anything sensitive.

A test (`test/fixtures.test.ts`) scans every fixture and fails if any of the
above is violated, so the inert property is enforced, not just asserted in prose.

| Fixture | Purpose |
| --- | --- |
| `mission-request.valid.json` | A valid synthetic mission request. |
| `mission-request.forged-authority.json` | Carries a forged top-level `authenticated_producer`; must be rejected. |
| `scope.valid.json` | A valid registered scope + limits. |
| `derived-inference.valid.json` | An honest derived-inference record with an `unknown` outcome. |
