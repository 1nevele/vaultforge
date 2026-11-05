# Sentinel: adversarial architecture review and CDM integration

**Architecture review · 5 November 2026**

**Scope:** the supplied product plan and execution plan, revision 4. Deep STORM-style research: five analytical perspectives, three parallel research agents plus parent synthesis. This reviews a proposed system, not deployed code. Severity below means consequence **if an unresolved design assumption ships**, not an observed vulnerability. External facts have numbered citations; proposed controls, priorities and architectural deductions are identified as recommendations or analysis.

## Executive decision

**Keep the product direction and most of the architecture. Do not start by replacing Jev or expanding the worker fleet. Add CDMs as an evidence-processing capability, and resolve the execution-authority model before promising secure autonomy.**

The plans already address many failures often missed in agent designs: independently protected authority, authenticated producer ownership, immutable action candidates, content-bound approvals, UNKNOWN effects, real cancellation, a separate verifier environment, and replay without execution. These are strengths of the supplied documents—not controls this review discovered were absent.

The biggest remaining problem is a tension between **a deliberately compromised worker with target-network access** and **authority approval of every sensitive operation**. Destination filtering constrains where packets go; it does not establish which logical operation those packets perform. Docker documents destination-controlled TCP proxying, not application-level authorization of every assessment effect[18]. **Analysis:** unless effects are mediated outside the compromised worker, task-level scope containment is the defensible claim; complete per-operation approval is not.

Three other decision-changing findings:

- **Docker Sandboxes remains a candidate, not a validated pentest substrate.** Its documented egress proxies TCP, blocks ICMP, and leaves UDP experimental/disabled by default. A successful HTTP probe cannot establish raw-scan or VPN fidelity[18].
- **CDM compatibility has a concrete trap.** ScaleDown advertises a Jev-shaped Decisions endpoint, but documents that only `state.text` and `state.document` are read. A naive replacement can omit separately supplied candidate, scope or evidence state[13].
- **Fresh verification is not enough.** NIST warns that multiple tools can reproduce the same false positive[27]. Recommendation: require an independent outcome oracle and reset baseline/candidate target state, not merely a new scanner VM.

**Recommended first workload:** one owned disposable web-service fixture, HTTP/TCP-connect effects, no pivot/VPN, Jev selecting frozen candidates, a CDM producing source-linked advisory output, and no model-generated authorization. Broader network tooling follows measured compatibility—not the other way around.

## 1. Highest-priority holes and how to close them

### R1 — P0: target access can bypass exact-operation approvals

**Plan location:** execution §§7,10,12; product security controls. **Affected gates:** G2–G4, G6.

The plan correctly expects guest root to be hostile and demands direct-client bypass tests. The unresolved case is not an out-of-scope destination: it is a **prohibited effect against an otherwise allowed destination**. Network-policy matching in the documented candidate authorizes destinations, not the meaning of arbitrary requests[18].

**Analysis:** if the guest can send traffic directly, it can construct requests without going through the scheduler's command journal. A reviewed command hash does not constrain attacker-written clients. Broad target egress and complete operation mediation are different security models.

**Recommendation:** explicitly choose, per playbook:

- **Task-contained workspace:** authorize a bounded set of testing effects for the task; admit that hostile worker activity within that envelope may not have individual command approval or complete command telemetry.
- **Brokered sensitive effects:** require the protected executor/protocol gateway to perform specific immutable operations. The worker has no parallel direct route. This supports narrower operation approval, but limits arbitrary shell/network tooling.

Do not call a guest-side wrapper an enforcement boundary against guest root. Add an owned-fixture test: direct attacker client, allowed IP/port, disallowed application effect. Either block it externally or document that the task grant includes that effect. This test should precede a strong “all tools mediated” claim.

### R2 — P0: backend selection lacks a required packet-semantics contract

**Plan location:** S04/S06. **Affected gates:** G0, G2, G6.

Docker documents a private in-VM Docker engine, but all outbound TCP passes through host proxying; external ICMP is blocked and UDP is experimental[18]. The plan already identifies this concern. The missing step is deciding which semantics the MVP actually requires **before** selecting the backend.

**Recommendation:** mark each capability required, optional or unsupported: HTTP, TCP connect, raw SYN behavior, UDP, ICMP, browser callbacks, VPN transport, traffic inside tunnels, reverse connections and DNS. Validate required behaviors with fixture-side observations, not only guest output. A ping between two containers inside the VM does not demonstrate external ICMP.

Counterpoint: if the first workload only needs HTTP/TCP connect, these restrictions can be an intentional safety/capability trade-off. Retain sbx first in the spike; reject it only for demonstrated requirements it cannot meet. Never fix compatibility by exposing a host Docker socket.

### R3 — P0: key custody is not constrained inference or permitted disclosure

**Plan location:** S05–S07, proposed CDM adapter. **Affected gates:** G1, G3, G6.

Docker's credential mechanism injects credentials onto matching requests. Its docs say service secrets are global by default and describe OAuth passthrough as an explicit escape from masking[19]. These features are not automatically the narrow Sentinel broker promised by the plan.

**Analysis:** a worker can abuse permitted request authority without learning an upstream key. An approved inference endpoint is also a route for transmitting context. Adding a CDM adds another destination and transformation chain; “local-first” is not a confidentiality guarantee for hosted inference.

**Recommendation:** define one authority-owned inference contract covering task/audience, provider/account/model, exact endpoint/method/schema, permitted provider features, input/output limits, concurrency, deadline, destination policy and request provenance. Disable parallel default credential-injection paths. Do not assume prompt wording establishes a data boundary; OWASP explicitly separates prompt formatting from tool-boundary enforcement[5].

Reserve bounded spend **before** forwarding across Codex, Jev, CDM and later Strix. Retain reservations for uncertain billable outcomes until reconciled; do not refund merely because a response was lost. Specify treatment of provider-side uploads, caches, sessions and background work. Local stop cannot retract already disclosed data or guarantee reversal of billing. These are proposed accounting/data-flow requirements, not measured provider behavior.

### R4 — P0: callbacks can move execution out of the worker

**Plan location:** S04–S06. **Affected gates:** G1–G4.

Current Codex app-server docs include commands outside its **thread sandbox** and dynamic tools executed by the app-server client[22]. Docker also documents local stdio MCP execution on the host[17]. This does not prove escape from an outer VM: it identifies where placement must be checked.

**Recommendation:** map every RPC and reverse request to its executing principal. Keep execution-capable callbacks in the worker trust domain; never let a privileged host adapter become an arbitrary tool runner. Maintain a narrow method/field/reply allowlist, reject policy/model/cwd overrides, and fail explicitly on unsupported permission requests. Do not forward public MCP calls directly into app-server RPC.

Add malicious dynamic-tool/reverse-request fixtures. Assert no privileged subprocess, persistent permission grant, or host-side stdio execution occurs. The existing prohibition on approval/grant MCP tools should remain; another broad “confirmation” tool would weaken it.

### R5 — P0 for offensive readiness: the verifier needs an oracle and clean targets

**Plan location:** specify before S09; implement S10. **Affected gate:** G7.

The fresh independently controlled verifier environment is already in the plan. NIST distinguishes validation from discovery and notes that comparison tools may share false positives; it also warns that active testing can disrupt systems[27].

**Recommendation:** define the exact independently observed effect that confirms each finding class. An assessor-written script, screenshot, exit code or scanner agreement remains a lead, not the oracle. Run supplied reproducers as adversarial code without authority over expected results or evidence storage.

Reset **target-side** state separately for baseline and candidate: databases, accounts, caches and external services where relevant. A new verifier VM does not reset a remote target. Add a functional control so a candidate that disables the service is not credited as a repair.

Report confirmed, refuted-with-evidence, inconclusive, blocked/skipped and unsupported separately. “Did not reproduce” must not automatically mean “safe.” Test shared-state contamination, forged success, wrong target, timeout, correlated scanner errors and functionality-breaking fixes.

### R6 — P1: MCP's protocol profile must be pinned, not assumed

**Plan location:** S01/S08/S09. **Affected gates:** G5, G6.

The primary site's `latest` redirect resolved during this review to **2026-07-28**. That profile uses per-request metadata rather than the legacy initialization handshake; its HTTP transport does not support Last-Event-ID resumption and treats closing an SSE response as cancellation of that request[24][25]. This is not evidence that the selected OpenCode version supports that profile.

**Recommendation:** pin and test the actual OpenCode/server/SDK compatibility matrix. Support a named legacy profile if necessary; do not claim newest-profile interoperability without testing. Keep browser SSE and MCP transport as separate contracts.

Durably accept a mission and return its handle promptly. Cancellation of a status/events request stops observation, not an already accepted mission. Mission cancellation remains a separate durable operation. Retain application-level event cursors regardless of transport replay.

Authorize every handle read/replay/cancel. HTTP auth is per request; the tools spec explicitly distinguishes a handle's identity from authority[23][26]. Derive durable client identity from trusted authentication, not token bytes, connection ID or self-reported client metadata. Test token renewal, revoked access, cross-client handles and lost submit acknowledgements.

### R7 — P1: durability and canonical identity need executable policy

**Plan location:** S01/S02/S05. **Affected gates:** G3, G4, G6.

SQLite remains a reasonable choice. Its WAL docs describe a WAL-reset corruption bug fixed in 3.51.3 and selected backports; the actual linked library must be inventoried rather than inferred from an npm package version[1]. WAL `synchronous=NORMAL` can lose committed transactions across power loss/system crash, unlike ordinary application-crash recovery[2].

**Recommendation:** pin a supported patched SQLite build, record actual runtime version/settings, and specify durability for authority consumption/budget commits. Test disk-full, failed commit, busy/checkpoint pressure, power-loss assumptions, backup/restore and outbox redelivery. Independent authority and mission stores do not share one magical atomic transaction.

RFC 8785 supplies precise JSON canonicalization rules, including duplicate-name rejection and numeric/string constraints; it does not freeze filesystem dependencies[3]. Bind operations to executable/script bytes, relevant environment, cwd, dependency/artifact versions and target identity—not just a command string. Define canonicalization version and Unicode/number behavior.

AWS's idempotency guidance emphasizes caller intent and atomic token/mutation recording[4]. Keep the plan's client-scoped idempotency, then specify retention, deliberate identical reruns, cancel tombstones and late dispatch. Restoring an old backup must not resurrect consumed approvals. Treat restored authority state as requiring a new execution epoch and reconciliation, not transparent continuation.

### R8 — P1 now, P0 when enabled: tunnels can hide final scope

**Plan location:** S04/S06; later Kali/Tailscale work. **Affected gates:** G2, G6.

Docker's documented policy acts on proxied destinations[18]. OWASP's SSRF guidance separately warns that domain allowlisting alone does not prevent DNS rebinding and calls for connection-time address validation and redirect controls[6].

**Analysis:** authorizing an encrypted relay does not necessarily authorize—or even reveal—the final destination behind it.

**Recommendation:** forbid generic pivots in the first slice. Later, enforce task scope after decryption at a controlled gateway, or explicitly acknowledge a broader trust assumption. Test one allowed and one forbidden target behind the same allowed tunnel endpoint. Also bind resolution/retries/redirects and IPv4/IPv6 to the effective scope; include established-flow cessation at revocation.

### R9 — P1: fresh VM does not mean fresh host integrations or patched images

**Plan location:** S04/S05/S10/S13. **Affected gates:** G0–G3, G7.

Docker documents host-side MCP and clipboard output; its security text is inconsistent about shared-skills mount defaults, so runtime inspection is needed[17][18]. Its security announcements explicitly warn that updating the sbx CLI does not update existing sandboxes[20]. Lima's own threat-model material describes a default read-only home mount; a flexible fallback is not automatically a hardened profile[21].

**Recommendation:** read back effective mounts, helper/kit configuration, shared skills, clipboard paths, host services and credential-helper execution. Disable unnecessary bridges. Check selected host/VMM/template/image versions against current advisories, and refresh images/trust stores deliberately. Do not label an installed CLI “patched enough” in isolation.

For Lima, require a specific reviewed mountless profile and repeat the same gates. For later Strix, prove the selected Docker daemon is guest-private, pin ARM64 artifacts, and exercise its browser/scanner workload. Measure host-enforced memory/disk/process limits and cancellation responsiveness on the target Apple Silicon/macOS platform with an explicitly recorded resource envelope. These are unverified requirements, not measured performance results.

### R10 — P1: engagement data handling needs explicit destination rules

**Plan location:** S12/S13. **Affected readiness:** engagement reporting and evidence export.

**Recommendation:** bind target-copying, hosted-inference disclosure, verifier inputs and messaging exports to the engagement's explicit scope and destination policy. Disable uncertain flows pending authorization; an allowed tool or provider does not independently authorize data disclosure. This is a proposed product requirement, not a compliance or verification claim.

## 2. Incorporating CDMs without creating a second authority

### What CDM means here

This review interprets CDM as **Constrained Decoding Model**, consistent with ScaleDown's current classification/structured-decision documentation. Classify scores labels; Extract performs extraction and routes enum/oneOf fields into classification[10][16]. Summarize produces an abstractive rewrite; Compress transforms context[11][12]. **Analysis:** these are distinct mechanisms, and a constrained answer vocabulary is not a guarantee of factual correctness.

**Recommended role split:**

- **Codex:** open-ended planning/investigation inside the worker.
- **Jev:** bounded tactical selection from immutable candidates, as already planned.
- **CDM Classify:** advisory telemetry/observation taxonomy and routing hints.
- **Extract:** source-linked candidate facts from bounded text; deterministic parsers first for structured scanner output.
- **Summarize:** operator briefs explicitly labeled as derived summaries.
- **Compress:** optional retrieval/context optimization only after ablation tests. Never the authoritative representation of grants, approvals, scope, command bytes, budgets or evidence.
- **Authority/verifier:** unchanged. Neither classification nor confidence can mint approval or verified status.

These are recommended assignments, not measured model rankings.

### Concrete Jev compatibility hazard

ScaleDown describes its Decisions API as Jev-shaped while documenting that only `state.text`/`state.document` are read[13]. **Recommendation:** keep provider-specific adapters and test canonical state rendering. Do not replace an API base URL and assume separate scope, candidates and evidence fields survive. Bind the original structured snapshot and the exact rendered provider input by hash; reject unsupported shapes.

Jev's docs warn that “none of the above” may work poorly and distinguish its confidence statistic from probability of correctness[14][15]. Recommendation: controller-enforced empty/invalid candidate handling, explicit abstention, and tested applicability logic—not confidence as a substitute for authorization or an untested extra label.

### Add a small derived-inference contract

Proposed host-owned record, not a provider-returned authority token:

```text
DerivedInferenceRecord v1
  inference_id, mission_id, execution_generation
  task_kind, provider, model_id, resolved_version_if_available
  adapter_version, rubric_schema_version, data_policy_version
  source_artifact_hashes, evidence_snapshot_hash
  canonical_input_hash, rendered_provider_input_hash
  candidate_set_hash (selection tasks only)
  authority_reservation_id, request_id, deadline
  raw_response_ref, normalized_result_ref
  score_semantics, source_spans_with_encoding_and_offset_unit
  transformation_lineage, completeness_flags
  outcome: completed | abstained | failed | unknown
```

The trusted adapter assigns provenance and producer classification; worker-supplied fields cannot self-upgrade trust. Preserve immutable original evidence separately from raw provider replies and normalized derived records. Client-facing projections must be bounded/redacted and independently authorized.

For literal spans, validate against the exact referenced bytes. For inferred labels, record that they are inferred even if accompanied by an extracted justification. Hash identity is not truth.

### Extraction has completeness traps worth testing immediately

The current Extract reference documents scalar limits of 30 distinct values and nested/array limits of 200 items. Mixed nested/scalar schemas make scalar fields single-valued; extraction thresholds do not apply uniformly to classification or nested/array paths. Its offset wording mixes character and byte terminology[16].

**Recommendation:** test Unicode, truncation, cardinality, empty evidence and schema mixing before using extraction to populate a supposedly complete target/IOC inventory. Missing extraction is not evidence of absence. A follow-up justification span does not independently establish an inferred label's truth. Preserve a completeness/unsupported state rather than silently producing an authoritative-looking map.

## 3. Model evaluation and adoption sequence

**Recommended benchmark:** held-out, adjudicated cyber observations, split by source/incident/time rather than near-duplicate chunks. Include contradictions, negation, stale evidence, unseen classes, prompt injection, no valid action, all actions prohibited and confidently wrong examples. This is a proposed dataset—not a benchmark run in this review.

Keep six evaluations separate:

1. **Schema:** malformed outputs, unknown IDs, nonfinite distributions, extra/missing questions.
2. **Evidence fidelity:** exact span matches, offset encoding, unsupported inference and completeness.
3. **Classification/selection:** per-class errors, valid-candidate inclusion, candidate-order/ID sensitivity and abstention risk–coverage.
4. **Probability:** reliability, Brier/log loss and calibration on Sentinel data; do not equate a concentrated distribution with correctness[15].
5. **Transformation:** raw-only versus extracted/summarized/compressed context; measure lost exceptions, identifiers, attribution and downstream decision errors—not just token savings. Summarization is abstractive and “lossless in intent” compression is a vendor characterization, not an established Sentinel property[11][12].
6. **Enforcement/operations:** injected instructions, stale generations, replay, cross-task tokens, budget races, provider errors, timeout and revoked access. Model quality cannot compensate for dispatch outside the frozen permitted set.

Adopt in stages: offline fixtures → live CDM shadow classification on approved synthetic observations → source-linked extraction → reviewed operational use. Keep raw-only baselines. Do not make a cheap model a fallback that silently changes evidence quality, provider destination or authority. No accuracy, latency, savings or superiority claim is justified by this source review alone.

## 4. Proposed changes to the execution backlog

These amend acceptance criteria; they do not rewrite the original files or invent the missing JSON backlog.

- **S01 — Lead:** freeze threat-model tiers, effect classes, canonical bytes, provenance/derived-inference schema, provider policy and verification outcome taxonomy. Resolve R1 explicitly.
- **S02 — Agent A:** add durability settings/version evidence, acceptance-point/idempotency retention, restore epochs, outbox failure and authorization-after-replay tests.
- **S04 — Agent C:** decide the first workload before backend selection; publish required/optional/unsupported protocol matrix, fixture-side captures, effective host-bridge inventory and private-Docker/ARM64 feasibility.
- **S05 — Lead:** specify target-effect mediation and the complete inference broker contract, including data destinations and atomic aggregate budget reservations. Prove alternate credential routes fail closed.
- **S06 — Agent C:** pin app-server schemas and callback-placement allowlist. Test hostile reverse requests, current-generation launch fencing and queued/streaming revocation.
- **S07 — Agent A:** retain real Jev. Add explicit applicability/abstention and candidate rendering tests, probability semantics and provider-specific state validation.
- **Add S07C — Agent A, after S02/S05:** a narrow `packages/integrations/cdm/` adapter, immutable derivation records, offline adversarial fixtures and approved synthetic shadow calls. Only Lead changes shared contracts/dependencies/lockfile. No new general-purpose model gateway platform.
- **S08 — Agent A:** pin actual MCP/OpenCode profile; test lost acknowledgements, cancelled observations, token renewal, revoked replay and cross-client access. No raw app-server forwarding.
- **S09 — Lead:** demonstrate real Jev plus one actual CDM-derived observation if CDM inclusion is an acceptance goal; label it model-derived, not verified. Record missing provider prerequisites as blockers, never a mocked pass. Core S09 and a CDM-extended S09 should have explicit separate completion labels if delivered incrementally.
- **S10 — Agent C:** implement independent oracle, trusted capture and separately reset baseline/candidate target state. Do not wait until implementation to define this interface.
- **S12/S12U — A/B:** include uncertainty, derivation lineage, completeness and destination-policy indicators in reporting/UI; enforce engagement-specific collection and export restrictions.
- **S13 — Independent reviewer:** test R1 bypass semantics, broker escape paths, target-state contamination, malicious callbacks and restore rollback—not only the happy-path demo.

Preserve the existing root-plus-three concurrency limit and exclusive ownership. Do not turn this research into permission to install a VMM, create OS users, alter networking or copy credentials.

## 5. Decision-changing unknowns and research limits

Before a real-execution release, resolve: task-level versus exact-operation containment; required network semantics; actual supported Codex inference path; permitted provider destinations/data handling; independently owned macOS authority/IPC deployment; actual MCP client profile; measurable verifier oracles; and the target platform's unverified resource envelope. These are implementation gates, not questions the operator must answer to receive this report.

**Method:** deep STORM-style adaptation, not execution of Stanford's STORM package. Five source-grounded perspectives used adaptive Q&A: authority/data flow; durability/recovery; model mechanics; substrate feasibility; integration/verification. Three delegated lanes each completed three rounds; the parent completed two three-round perspectives, revised the outline, reconciled overlap and audited sources. All agents used the inherited `gpt-6.1-sol` model; no alternative model or paid service was selected.

The final report cites primary documentation and research guidance, not independent performance benchmarks. Vendor documentation establishes interfaces and claims, not cyber accuracy or exploit-free isolation. Consequential compatibility facts were read back from saved sources; the parent independently re-fetched the CDM state-field exception, latest MCP redirect and Codex documentation. The bibliography and evidence checks are mechanical support, not proof that every inference is correct.

No Sentinel repository/code, Mac runtime, sandbox, credentials, provider API, target network, model quality or cost was tested. The linked machine-readable backlog, previews and AGENTS instructions were not provided. Public source retrieval does not verify deployment compatibility. Original documents and system configuration were not modified.

**Bottom line:** Sentinel is worth building as a bounded, evidence-first command center. CDMs fit best as observable typed transformations—not extra autonomous authority. The next engineering milestone should settle the allowed-effect boundary and demonstrate a deliberately narrow real workflow, not widen the number of agents, tools or platforms.

## Sources

[1] https://www.sqlite.org/wal.html — SQLite Write-Ahead Logging
    > "3.51.3 (2026-03-13) and later."
[2] https://sqlite.org/pragma.html — SQLite PRAGMA reference
    > "committed in WAL mode with synchronous=NORMAL might roll back following a power loss or system crash."
[3] https://www.rfc-editor.org/rfc/rfc8785.html — RFC 8785: JSON Canonicalization Scheme
    > "JSON objects MUST NOT exhibit duplicate property names."
[4] https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs — AWS Builders Library: Making retries safe with idempotent APIs
    > "all mutating operations related to servicing the request"
[5] https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html — OWASP LLM Prompt Injection Prevention Cheat Sheet
    > "These examples illustrate formatting only."
[6] https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html — OWASP Server-Side Request Forgery Prevention Cheat Sheet
    > "Domain allowlisting alone does not prevent DNS rebinding."
[10] https://docs.scaledown.ai/api-reference/classify-overview.md — Classify overview
    > "Scores are softmax-normalised across all labels so they sum to 1.0"
[11] https://docs.scaledown.ai/api-reference/summarize-overview.md — Summarize overview
    > "condenses text into a shorter, fluent rewrite in the model's own words."
[12] https://docs.scaledown.ai/api-reference/compress-overview.md — Compress overview
    > "The compression is lossless in intent"
[13] https://docs.scaledown.ai/api-reference/decisions-overview.md — Decisions overview
    > "Only `state.text` / `state.document` are read"
[14] https://docs.typesafe.ai/primitives/choice.md — Choice — TypeSafe docs
    > "A `none of the above` option may not work well in many use cases."
[15] https://docs.typesafe.ai/confidence.md — Confidence — TypeSafe docs
    > "which is different from the probability that the selected answer is correct."
[16] https://docs.scaledown.ai/api-reference/extract.md — Extract API reference
    > "Character offsets (`start`, `end`) refer to byte positions in the original `text` string."
[17] https://docs.docker.com/ai/sandboxes/security — Docker Sandboxes — Security model
    > "local stdio MCP servers run on the host, not inside the sandbox VM."
[18] https://docs.docker.com/ai/sandboxes/security/isolation — Docker Sandboxes — Isolation layers
    > "Processes in a local sandbox can write text to your host clipboard"
[19] https://docs.docker.com/ai/sandboxes/configuration/credentials — Docker Sandboxes — Manage credentials
    > "A kit can set OAuth passthrough: true to opt out of sentinel masking."
[20] https://docs.docker.com/security/security-announcements — Docker security announcements
    > "Updating the sbx CLI alone doesn't update existing sandboxes."
[21] https://raw.githubusercontent.com/lima-vm/lima/master/.oss-scanner/threat_model.md — Lima project threat model and supporting project security/template material
    > "The default template mounts the user's home directory read-only."
[22] https://learn.chatgpt.com/docs/app-server — Codex App Server
    > "This runs outside the sandbox with full access and doesn’t inherit the thread sandbox policy."
[23] https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization — MCP Authorization 2026-07-28
    > "authorization MUST be included in every HTTP request from client to server."
[24] https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http — MCP Streamable HTTP 2026-07-28
    > "Closing the SSE response stream MUST be treated by the server as cancellation of that request."
[25] https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning — MCP Versioning 2026-07-28
    > "There is no negotiation handshake."
[26] https://modelcontextprotocol.io/specification/2026-07-28/server/tools — MCP Tools 2026-07-28
    > "a handle is a name, not a capability."
[27] https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf — NIST SP 800-115 (September 2008)
    > "comparison tools can often produce similar results—including the same false positives."
