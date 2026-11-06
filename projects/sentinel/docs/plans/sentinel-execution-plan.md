# Sentinel — Executable Build Plan

Status: ready for implementation planning handoff; application implementation has not started.
Date: 31 October 2026.
Revision: 4, updated 1 November 2026 — existing sandbox/microVM evaluation and one client-neutral MCP boundary, without a dedicated Hermes/OpenClaw workstream.
Companion: [Product plan](sentinel-product-plan.md).
Machine-readable backlog: [Build backlog](sentinel-build-backlog.json).

## 1. What we are building

A laptop-hosted cyber command center for authorized offensive-security work, with a live agent graph, animated real message paths, a target map, inspectable commands/evidence, and an OpenCode client connected to the same missions.

Codex is the initial runtime candidate. Jev is included from the first real mission as the bounded tactical selector. Start with one active isolated worker and one mission. Evaluate an existing microVM sandbox first rather than building a VM manager. Broader assessments, Strix, protected verification, reporting, and engagement data-handling controls follow the first live vertical slice.

The completed HTML concept is a simulated design preview. It is not the live application or proof of containment. Do not copy its illustrative approval button into a privileged approval path without implementing the authority-owned review boundary.

## 2. Platform and preflight requirements — unverified

Apple Silicon/macOS support is a target requirement, not evidence of a tested host. Establish supported OS, CPU architecture, runtime and package-manager versions, available memory and VM/container prerequisites in the implementation environment. Pin compatible dependencies after checking their actual contracts. No workstation inventory or prior installation state is supplied by this plan.

Keep one active worker. A proposed benign-spike starting allocation is two virtual CPUs and 4 GiB RAM where configurable; this is an unverified test budget, not a measured capacity or minimum-host guarantee. Measure host headroom and peak usage before adopting supported resource limits.

Use supported account-status/configuration flows to establish prerequisites. Do not read or copy credential files for preflight. Use project-relative paths under the repository's ownership rules; do not depend on personal workspace folder conventions.

## 3. Worker backend decision: existing Docker and microVM systems

The backend is not selected yet. Feasibility planning does not authorize installing a backend or relaxing containment. Do not build a custom VMM or support every backend in the MVP.

| Candidate | Evaluation order and fit |
| --- | --- |
| Docker Sandboxes, local sbx CLI | First compatibility candidate. Its documented agent support includes Codex and OpenCode. Local sandboxes use separate microVM kernels, private Docker engines, and a host credential proxy. Test the required programmatic/event transport and offensive networking. |
| Ordinary Docker Desktop containers | Simple comparison/baseline. Containers share the Docker Desktop Linux VM kernel. Assess actual host integrations, daemon access, mounts, and network/reset behavior against the same required gates; a new container is not a fresh kernel. |
| Apple container | Alternative to examine if needed: OCI images run in lightweight VMs on Apple Silicon. Docker API/Strix compatibility, controls, and lifecycle need validation. Do not assume Docker CLI compatibility. |
| Lima/VZ with guest Docker | Conventional dedicated Linux VM fallback when existing agent sandboxes cannot support the tools/networking. More lifecycle integration to own, but no custom hypervisor. |
| Firecracker on a Linux worker | Later remote-Linux option. It requires Linux KVM and does not run directly on macOS. Do not add a nested Linux/KVM layer on the macOS target merely to use it. |

Proposed arrangement if the first candidate passes:

~~~text
Mac laptop
  command-center UI + mission service
  separately protected authority / inference custody
                  |
        existing sandbox launcher
          per-mission microVM
            Codex + shell/tool worker
            private Docker engine
              Strix containers when compatible
              disposable lab target
~~~

The sandbox product supplies the execution boundary. Sentinel owns mission authorization, limits, approvals, event records, and evidence. Reuse existing credential injection where it satisfies the tests; do not rebuild it by default. Confirm integration for Jev as well as Codex.

Docker Sandboxes is distinct from ordinary Docker Desktop containers. It can be installed as a standalone product; Docker Desktop is not an assumed prerequisite. The listed products are unverified compatibility candidates. Documented agent support alone does not establish Sentinel compatibility.

Inspect defaults: host workspace mounts, shared skills, SSH-agent forwarding, clipboard bridges, credential paths, and host-side MCP execution. Prefer a mountless mission workspace with explicitly imported sanitized inputs. Disable unneeded forwarding and shared state where supported; record any remaining bridges. Use authority-owned fixed configuration, excluding repository-defined host lifecycle/credential commands and untrusted host-side stdio MCP tools. The sbx documentation describes outbound TCP through host policy, ICMP blocked, and UDP disabled by default/experimental. Test raw scanning, target communication, Strix, and the later Kali/Tailscale route; do not promise that a coding sandbox supports a full pentest network. Only narrow, explicitly reviewed host MCP operations may cross the boundary.

Strix currently requires Docker, so test its actual release/image architecture early. A sandbox's private Docker engine may solve its nested execution requirement without a laptop Docker socket, but this must be demonstrated. Do not use a host socket or privileged outer container as an automatic compatibility fix.

For the target Apple Silicon/macOS platform, whose resource envelope is unverified, keep one active execution environment initially. Where allocation is configurable, start the benign spike at two virtual CPUs and 4 GiB RAM and measure actual use. A full Kali desktop is optional. Pin ARM64 images/binaries and record digests; do not silently depend on x86 emulation.

Sources: [Docker Sandboxes architecture](https://docs.docker.com/ai/sandboxes/architecture/), [supported agents](https://docs.docker.com/ai/sandboxes/agents/), [isolation controls](https://docs.docker.com/ai/sandboxes/security/isolation/), [default posture](https://docs.docker.com/ai/sandboxes/security/defaults/), [Apple container](https://github.com/apple/container), [Firecracker requirements](https://github.com/firecracker-microvm/firecracker/blob/main/docs/getting-started.md), [Lima VZ](https://lima-vm.io/docs/config/vmtype/vz/), [Docker Desktop VMM](https://docs.docker.com/desktop/features/vmm/), [Strix prerequisites](https://docs.strix.ai/quickstart).

## 4. Definition of the first live milestone

A mission submitted from OpenCode appears in the UI under the same mission ID. A real Codex runtime emits public activity, Jev selects an immutable permitted next action, and an isolated worker executes one benign lab operation. The UI animates only actual dispatched messages and observed execution events. It links the result to its transcript and evidence.

Close and reopen the UI; reconnect from an event cursor without repeating any action. Restart the mission service without resetting authority or budget. Cancel the mission; show Stopping until the supervisor confirms cessation and retain UNKNOWN for any ambiguous external effect.

Passing this milestone requires real runtime and Jev calls, authentic worker observations, containment tests, and the failure tests below. Fixture-only operation is a separately labeled demo and cannot pass it.

No external scanning, production access, autonomous merge, or unrestricted GitHub publication is part of this milestone. Use an owned, disposable lab and synthetic data.

## 5. Two different kinds of agents

The implementation team below builds Sentinel. It is separate from the agents displayed by the finished product.

The first product runtime comprises:
- One main runtime instance for planning and deeper investigation.
- Jev for selecting bounded next actions and escalation.
- One execution worker.
- A protected verification controller/stage once that feature is implemented.

A tool worker is labeled as a tool worker. Multiple role names do not prove separate processes or independent verification. Do not create a fictitious swarm to populate the UI.

## 6. Implementation team: root plus three active subagents

Maximum concurrency is four total agents, including the lead. Use inherited models/settings unless the user explicitly requests otherwise. The lead owns the critical path, contracts, and integration. Keep the same three work lanes through the first slice; use a freed slot for an independent reviewer later.

| Role | Exclusive initial ownership | Deliverables |
| --- | --- | --- |
| Lead / root integrator | Root manifests and lockfile; packages/contracts/; apps/authority/; shared fixtures; tests/security/; tests/e2e/; release decisions | Frozen contracts, narrow authority, integration, acceptance evidence, final handoff |
| Agent A: core and MCP integration | apps/mission-service/; packages/integrations/jev/; packages/integrations/mcp/; packages/evidence/; associated unit/integration tests | SQLite state, events/SSE, Jev, client-neutral Sentinel MCP server, evidence/report plumbing |
| Agent B: command-center interface | apps/web/ and its component/browser tests and presentation fixtures | Cyber UI, Team/Targets views, inspectors, finite event-driven animation, live transport, accessibility |
| Agent C: worker and runtime | packages/worker/; packages/integrations/codex/; packages/verification/; infra/vm/; associated runtime tests | VM/credential feasibility, supervisor, Codex, tool execution, later Strix and clean verification |

Treat these as ownership paths, not a requirement for one published package per directory. Create only the packages needed for the implementation. Extract abstractions when demonstrated by real consumers.

Subagent rules:
1. Each assignment names ticket IDs, allowed paths, inputs, outputs, dependencies, tests, and a stopping condition.
2. Only the lead changes shared contracts, root configuration, package versions, or lockfiles. Other agents request the exact change and explain the consumer requirement.
3. No two agents edit the same path concurrently. Use separate worktrees once the repository exists, or maintain explicit path ownership in a shared checkout. The lead chooses one integration method and records it.
4. A worktree is a collaboration mechanism, not a hostile-code sandbox.
5. Every handoff lists changed files, contract changes, commands actually run, observed results, remaining limitations, and unresolved blockers.
6. A dependent ticket starts only after its prerequisites are integrated and accepted, not merely after another agent says its code is written.
7. Reviewers do not approve their own security-sensitive implementation. Schedule a non-author or fresh reviewer in a freed slot; do not exceed the concurrency limit.
8. Keep independent work moving when a provider/VM prerequisite blocks one lane. Do not replace a failed live integration with an unlabeled mock.

## 7. Repository and contract baseline

Proposed source layout:

~~~text
sentinel/
  apps/
    web/
    mission-service/
    authority/
  packages/
    contracts/
    integrations/
      codex/
      jev/
      opencode/
    worker/
    evidence/
    verification/
  infra/vm/
  fixtures/
  tests/security/
  tests/e2e/
  docs/decisions/
  docs/acceptance/
~~~

Use React/TypeScript/Vite for the UI, React Flow for graphs, Motion for transitions, a small Node/TypeScript service, SQLite, and authenticated SSE. Pin versions after checking compatibility with the actual implementation toolchain. Do not upgrade the user's global tools as a side effect of bootstrapping.

Freeze a small versioned contract for:
- Mission request, immutable task envelope, scope, limits, and client request ID.
- Runtime actor instance and execution generation.
- Immutable candidate action set and selection.
- Canonical operation, material input/artifact digests, expected versions, approval, and receipt.
- Evidence reference and integrity metadata.
- Target observations and hypothesis/observed/verified relationships.
- Mission snapshot with projection cursor.
- Public event union and producer trust classification.
- Stop/steer requests and separate eventual outcomes.

Event envelope:
~~~text
event_id, mission_id, projection_sequence, schema_version,
actor_id, execution_generation, operation_id,
event_type, authenticated_producer,
correlation_id, causation_id, timestamp, payload_reference
~~~

Trusted producer identity is assigned at authenticated ingestion, never accepted from an agent-controlled payload field. Authority receipts alone establish authorization and privileged outcomes; the protected verifier alone establishes verified findings. A model saying "success" remains a model claim.

## 8. Dependency-ordered backlog

Statuses at handoff: S00 is done; S01 is ready; remaining implementation tickets are pending. Deferred items are not release prerequisites.

| ID | Owner | Depends on | Deliverable and acceptance |
| --- | --- | --- | --- |
| S00 | Lead | — | Capture agreed scope and design inputs; identify unverified platform requirements. This planning baseline is not application implementation. |
| S01 | Lead | S00 | Create repository/workspace, ownership instructions, pinned tooling, and contracts/fixtures. Schema validation and initial build/type checks pass; no real execution enabled. |
| S02 | Agent A | S01 | Durable mission core: migrations, one-active-mission scheduling, operation references, snapshots, bounded event queries, SSE, producer-authenticated receipt ingestion. Restart/reconnect/duplicate/gap tests preserve state and never redispatch actions. |
| S03 | Agent B | S01 | React command center against explicit demo fixtures. Team and Targets canvases, inspector, transcript/evidence view, pending review display, disconnected/denied/unknown states, finite motion, reduced motion. Demo/replay have no execution capability. |
| S03L | Agent B | S02, S03, S05 | Connect the UI to authenticated snapshots/SSE, cursor/gap recovery, generation handling, bounded live output, real stop/steer, inert evidence and canonical pending-review records. Hydration/reconnect do not animate old work or dispatch actions. Complete accessibility/performance checks. |
| S04 | Agent C | S01 | Existing-substrate feasibility spike: Docker Sandboxes first, Docker Desktop comparison, Lima fallback, other options only if needed. Record actual launch/mount/network/architecture/reset behavior, private event/control transport, and early Strix compatibility. Identify the supported inference path; final real-inference G1 testing belongs to S06 after S05. |
| S05 | Lead | S01 | Minimal separately protected authority/executor and trusted review CLI. Enforce task grants, generation, canonical content-bound commands, atomic claims, expiry/revocation, and narrow inference access. Prove OS/IPC ownership and rejection of scheduler/worker impersonation. |
| S06 | Agent C | S02, S04, S05 | Narrow adapter for the chosen existing sandbox launcher plus real Codex integration: start/resume/steer/interrupt, public event normalization, resource limits, stop versus destruction, and final G1 inference-custody test. Benign command, interrupted turn, restart, and direct bypass attempts have recorded outcomes. |
| S07 | Agent A | S02, S05 | Real Jev adapter for routing, next-action selection, and escalation. Validate immutable candidate IDs/versions, prerequisites, budget, abstention, provider errors, and stale decisions. Its choices cannot widen grants or skip mandatory verification. |
| S08 | Agent A | S02, S05 | Client-neutral Sentinel MCP server for submit/status/events/targets/evidence/steer/cancel. Durable mission handles, client-scoped content-bound idempotency, bounded cursor observations, explicit lifecycle semantics, and server-side authorization. Test the protocol independently and OpenCode as the first reference client. No approval/grant/secret/host-shell tool. |
| S09 | Lead integrates A/B/C | S03L, S06, S07, S08 | First real cross-interface mission and live command-center acceptance. Include one actual lab observation that creates/updates a target/service node linked to its producing command and evidence; registered scope is distinct from observed topology. Complete section 4 and G0–G6, recording actual and skipped checks. |
| S10 | Agent C with Lead integration | S09 | Protected verification in a freshly created separately controlled execution environment, after disposal of assessment state. The controller/harness authority stays outside the compromised assessment guest. Reproduce on a vulnerable baseline and immutable candidate; shared assessment daemons/caches/credentials cannot affect it. Forged reports or changed artifacts cannot create verified status. |
| S11 | Agent C | S10 | Strix adapter and guest Docker compatibility. Pin release/image digests, inspect actual capabilities/mounts, broker inference independently, and keep Strix's Docker daemon inside the worker boundary. Demonstrate one bounded controlled-lab finding and evidence. |
| S12 | Agent A | S10 | Incremental reproducible report and engagement data-handling controls: engagement/report clocks, screenshots/evidence checklist, per-mission sessions, download/data policy, export validation. Engagement tracking survives UI/controller restart; VM loss yields honest lost/unknown state. UI implementation is tracked separately as S12U. |
| S12U | Agent B | S12 | Implement report/evidence navigation, engagement/report clocks, completeness indicators, and lost-session state in the UI against the integrated report contract. The browser cannot restore authoritative outcomes from local storage. |
| S13 | Independent reviewer; Lead fixes/integrates | S11, S12U | Non-author adversarial review, reproducible acceptance run, operating guide, known limitations, and release-blocking issue closure. No "all passed" claim if real integrations were skipped. |
| S14 | Unassigned | S13 | Deferred: native desktop wrapper, additional model runtimes, concurrency, broad messaging integrations, or automatic repository publication after separate need/risk assessment. |

S11 and S12 can run in parallel after their stated prerequisites. The first live command center does not wait for Strix or engagement reporting. The first offensive-lab release includes protected verification; reporting readiness requires S12 and independent review, not a successful UI demo.

## 9. Execution waves

Wave 0 — establish facts and freeze interfaces.
Lead accepts S00, implements S01, records remaining runtime/auth/OS boundary questions, and dispatches the three role-specific briefs.

Wave 1 — parallel foundations.
Agent A implements S02. Agent B implements S03. Agent C runs S04. Lead implements S05 and reviews contract changes. This wave has four active agents including the lead.

Wave 2 — connect real components.
Agent C implements S06 after the feasibility and authority gates. Agent A implements S07 and S08 sequentially or in small non-overlapping increments. Agent B implements S03L to connect the same UI projection to live snapshots/SSE and adds the meaningful integration checks. Lead resolves integration issues and verifies producer provenance.

Wave 3 — first live milestone.
Lead runs S09 using the exact installed versions, then records the demo steps and acceptance evidence. Unsupported authentication, unsafe mounts, missing outer network enforcement, or authority isolation failures block real target execution while unrelated work continues.

Wave 4 — offensive workflow and reporting.
Agent C implements S10 then S11. Agent A implements S12 after verification contracts exist. Agent B implements S12U and performs non-author review where appropriate. Lead runs the protected acceptance and failure suite.

Wave 5 — independent release review.
Free an implementation slot before scheduling an independent reviewer for S13. Reproduce findings, fix material failures, rerun the affected checks, and deliver a working runbook. Do not add optional infrastructure to avoid completing the slice.

## 10. Security and truthfulness gates

| Gate | Required observation | What failure blocks |
| --- | --- | --- |
| G0: substrate | Selected existing ARM64 sandbox/container/VM actually boots, resets, and runs needed binaries; manifests/digests/mounts/network/protocol restrictions recorded; offensive-network compatibility matrix completed | Real worker launch |
| G1: inference custody | Runtime runs inside the VM using the selected supported inference path; no upstream/provider/GitHub/cloud/operator credentials in the worker; task proxy credential is narrow and revocable | That runtime integration |
| G2: containment | Deliberately compromised guest, including root, fails tested host-canary, management, cross-task, unauthorized network, IPv6/DNS, and scope-bypass attempts | Real target access |
| G3: authority ownership | Scheduler and worker cannot read authority secrets, change grants/approvals, impersonate human/verifier, or choose arbitrary supervisor mounts/images/network modes | Original compromised-orchestrator security claim and real-execution release |
| G4: approval | Authority-owned review retrieves actual canonical content; changed input/artifact/target/generation/expiry is rejected; concurrent consumption authorizes one logical operation | Sensitive operations |
| G5: local API/content | Authenticated HTTP/SSE, Host/Origin and cross-site request controls, bounded outputs, inert malicious content, no unapproved remote resource loads | Live client release |
| G6: failure/stop | Current-generation fencing, actual outer egress revocation, workload termination, UNKNOWN outcomes and safe reconciliation demonstrated during injected failures | Live mission acceptance |
| G7: verification | Protected reproduction/controller and a fresh execution boundary independent of assessment guest root; candidate and harness digests match; no assessment-controlled daemon/cache/credentials; bounded evidence/report reproducibility | Verified findings and offensive-lab acceptance |
| G8: independent review | Non-author review and repeatable integrated run; unresolved material issues listed and handled | Release/readiness claim |

Two processes under the same host UID with 0600 files are not the authority boundary. Implement distinct OS principals or real OS sandbox restrictions with protected storage/IPC. If that cannot be achieved, record the narrower trusted-coordinator threat model; do not silently claim the original compromised-orchestrator protection.

"Worker without upstream credentials" still allows a task-scoped broker credential. Do not call it credentialless or assume that authentication prevents the compromised holder from using its permitted capabilities.

Guest-root testing validates the tested configuration against the recorded attempts; it does not prove the hypervisor contains no exploitable vulnerability.

Do not automatically move credential-bearing Codex onto the laptop if inference brokering fails. That changes the trust model. Either find a supported integration or choose another runtime after recording the decision.

The authority-owned local review CLI is the simplest first sensitive-approval surface. The main UI can show pending review information and an operation reference. Its renderer does not mint authoritative approvals.

Authenticated guest telemetry proves which guest submitted it, not that the guest's claim is true. Reserve supervisor-observed for facts measured outside the guest, such as launch configuration, enforcement observations, and teardown. Guest command output is worker-reported evidence until checked by the protected verifier. Apply upstream-key custody and authority-owned atomic budget accounting to Jev too; its mission-service adapter must not hold a broad provider key.

Preserved Kali sessions are scoped to one mission and trust stage. They may survive UI/controller restarts while their environment lives, but cannot carry compromised writable state into clean verification. Stop/destroy old assessment state and launch a fresh verifier environment sequentially to retain the one-active-worker limit. A new container on an assessment-compromised shared kernel is insufficient for that independence claim.

When adapting an existing sandbox launcher, revalidate task generation before every launch/exec call: a convenience exec command may start a stopped sandbox. Test that late dispatch cannot revive a cancelled mission. Network-policy changes are not assumed to terminate established connections; verify actual stream/socket cessation during cancellation.

## 11. Live UI behavior that must be implemented

Use one projection with two separate capabilities:
- MissionDataSource: snapshot, events, evidence preview.
- LiveMissionCommands: submit/steer/cancel where authorized.

Demo and replay do not receive LiveMissionCommands. Missing live connectivity shows disconnected/error; it never silently loads a successful demo.

Hydrate snapshot at cursor S, subscribe after S, deduplicate by identity/sequence, and recover gaps with a fresh compatible snapshot. Reconnect/history hydration updates state without animating old handoffs as newly dispatched messages. Late old-generation events remain historical and cannot reactivate the current worker.

Animate only actual explicit message dispatch. Model output is not automatically a message to another agent. Show actual sender, recipient, public content, operation/evidence references, and observed outcome. Do not fabricate dialogue or expose private model reasoning as telemetry.

Keep animation queues bounded; skip decorative motion under load while preserving history. Start with at most four simultaneous packets. High-volume transcript output uses separate bounded chunks/cursors, not one graph event per token.

For the initial performance check, use four actors, 100 target nodes, 300 edges, and a 60-second burst of 50 small updates/second. Require the correct final projection, responsive selection, bounded queues, and no growing motion backlog. Record actual latency and memory on the target deployment platform rather than promising universal frame rates.

Maintain at least 12px technical labels, readable body text, keyboard/list alternatives to the graph, stable focus, word/symbol state labels, reduced motion, and normal-panel reflow at 320px. Graph panning may be local to the graph; ordinary forms and inspector text must not require horizontal page scrolling.

Stop is a requested transition until the supervisor confirms cessation. Connection loss is not cancellation. A model success claim is not an observed outcome. A candidate finding is not verified.

## 12. Meaningful verification suite

Implement tests as each boundary appears. Avoid tests that only mirror rendering code or add no independent assurance.

1. API/authority: tampered material parameters, changed script content with an unchanged command string, expired/revoked grants, 100 concurrent approval claims, stale generations, worker-as-human credentials, forged producer types.
2. Remote effects: process death before send/after acceptance/before persistence, dropped responses, overlapping recovery, and reconciliation. No blind repeat of UNKNOWN operations.
3. Worker: direct attacker-written clients, guest root, host canaries, metadata/private networks, alternate DNS/IPv6, guest Docker scope, children surviving parent termination, quotas, and outer deadline enforcement.
4. Clients: duplicate mission submissions, snapshot/event race, reconnect gaps/duplicates, slow consumers, closed/reopened UI, replay without execution, and stop/steer without authority expansion.
5. Jev: invalid/stale selections, confident wrong choices, untrusted content, provider failure, abstention, repeated low-value choices, and mandatory checks that selection cannot suppress.
6. Evidence: forged JUnit/SARIF/text claims, changed artifacts, malicious HTML/Markdown/terminal escapes, oversized outputs, unsafe paths/archives, and missing screenshots.
7. Verification: vulnerable baseline positive control, candidate retest, own-account/control behavior, immutable artifact matching, and verifier authentication.
8. Sessions: controller restart preserves a still-running mission VM; VM destruction loses live sessions, retains transcripts, invalidates authority, and never reuses writable state in a new mission.

Desired project commands to create during implementation:
~~~text
pnpm check
pnpm test
pnpm test:e2e
pnpm test:security
pnpm demo
pnpm dev
pnpm live:smoke
~~~

These commands do not exist yet. Unit/demo checks must run without provider credentials. Live smoke checks must declare missing prerequisites and cannot count a skipped provider/VM integration as a pass.

## 13. Provider access, external effects, and blockers

No real provider account/authentication or billable quota has been validated. Build offline-capable adapters and fixtures first. Before real calls, use the supported account setup and a configured spending ceiling. Never paste secrets into a plan, commit, event payload, or report.

The plan does not authorize arbitrary external scanning, new target scope, publication, production action, or unrestricted spend. Live target work uses registered owned-lab fixtures until the operator supplies an explicit target scope.

Missing credentials or a VM setup block only dependent real tests. Continue contracts, UI, persistence, MCP protocol tests, and failure fixtures. Report exactly what is missing; do not repeatedly ask for information that the environment or supported tools can provide.

Do not install a VM engine, change host network rules, create OS accounts, copy credentials, or modify the user's OpenCode configuration merely to finish this planning task. During implementation, prepare the concrete change, apply the session's authorization and applicable tool rules, and explain any unavoidable operator action.

No wall-clock implementation estimate is committed. Track completed acceptance gates and blockers instead of claiming a reliable schedule before the runtime/VM spike.

## 14. Handoff prompt for starting implementation

~~~text
Execute the Sentinel build plan and available canonical backlog.
Read the product plan and applicable AGENTS.md instructions first.
Start with S01 and preserve existing project artifacts.
Use one lead plus no more than three active subagents.
Assign exclusive paths and concrete acceptance checks before dispatch.
Keep root contracts/configuration/lockfile changes serialized.
Implement the command center and core against explicit demo data in parallel
with runtime/VM feasibility and authority work.
Do not enable real target execution until the applicable gates pass.
Keep Jev in the first real live mission.
Use supported credential setup and bounded spend; never copy host login files
into a worker or turn a missing provider into an unlabeled mock.
Continue independent work when a prerequisite is blocked.
Record actual tests, skipped checks, changed trust assumptions, and blockers.
Integrate and review each dependent slice before proceeding.
Finish with the cross-interface live demo and evidence-backed acceptance record.
~~~

This is a reusable handoff prompt, not a claim that execution has begun.

## 15. Work-package brief template

~~~text
Role:
Ticket IDs:
Read first:
Owned paths:
Frozen input contracts:
Required outputs:
Acceptance checks:
Out-of-scope files/actions:
Dependencies and current blockers:
Stop when:
Handoff: changed files, proposed contract changes, actual commands/results,
remaining limitations, security assumptions, and integration notes.
~~~

## 16. Client-neutral MCP contract

S08 builds one Sentinel MCP server. OpenCode is the first reference client; Hermes, OpenClaw, and other compatible clients use that same contract. Client setup may need transport/authentication configuration and a bounded interoperability check, not another backend or mission lifecycle. The unused, deferred Hermes-specific S15 ticket is removed.

Submission returns a durable mission handle promptly and accepts a client-generated idempotency key scoped to the authenticated client and canonical parameters. Reusing the key with changed parameters is an error. MCP protocol request IDs alone are not submission idempotency keys.

Expose bounded snapshots, cursor-based events, evidence references/previews, and explicit cursor-expiry/resynchronization behavior. Do not require clients to keep an MCP call or live stream open for the duration of a mission. Client disconnect, transport cancellation, and explicit mission cancellation are different events. Steering cannot expand scope; cancellation returns a stopping request and later supervisor-confirmed status.

Version schemas and negotiate supported capabilities. Authenticate clients and enforce authorization server-side. No client-supplied prose can establish human approval. Keep authority, retries, recovery, and canonical evidence in Sentinel. Client memories and generated skills are untrusted context; expose only approved data for that client/destination. Selecting an assistant as a worker runtime remains a separate sandboxed integration.

## 17. Completion and deferred scope

The first live milestone is complete only when S09 passes with real components and its required gates. Offensive-lab readiness additionally requires protected verification and actual tool compatibility. Engagement-reporting readiness requires reproducible reports, data-handling rules, recovery testing, and independent review.

Defer native packaging, multiple concurrent workers, alternative runtimes, client-specific messaging features, broad plugins/MCP catalogs, automated repository publication, production operations, OPA/SPIRE/Vault deployments, and distributed infrastructure until a concrete need emerges. Compatible assistants connect through the shared MCP boundary without a separate vendor-specific build workstream.

Source baselines: [Codex app-server](https://learn.chatgpt.com/docs/app-server), [OpenCode MCP](https://docs.opencode.ai/docs/mcp-servers/), [Jev primitives](https://docs.typesafe.ai/introduction). Recheck provider/runtime contracts when implementing the corresponding ticket.
