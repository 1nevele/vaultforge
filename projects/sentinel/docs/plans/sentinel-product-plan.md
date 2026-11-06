# Sentinel — Local Cyber Command Center

Planning baseline: 31 October 2026. This is a product and implementation plan, not a deployed system.
Updated 1 November 2026: Sentinel exposes a client-neutral MCP server; OpenCode is the first interoperability test client. Hermes, OpenClaw, and other compatible clients need no dedicated platform workstream.

Implementation handoff: [Executable build plan](sentinel-execution-plan.md) and [dependency backlog](sentinel-build-backlog.json).

## Product objective

Build a local-first offensive-security assistant with an operator-controlled interface, OpenCode access, and an animated cyber command center. Initial use cases are authorized lab assessments and development/remediation workflows.

The selected visual direction is a cyber command center with an agent graph, animated message paths, and a target map. Apple Silicon/macOS is a target platform requirement, not a verified deployment. The supported host resource envelope must be measured during feasibility testing. Choose an existing worker backend through a feasibility spike: Docker Sandboxes microVMs first, ordinary Docker Desktop as a comparison, and Lima/VZ with guest Docker as a fallback; Apple container is another Mac-native option if needed. A full Kali desktop and a custom VM manager are not prerequisites. Keep one active execution environment, test tool architecture and offensive networking, and validate actual containment before real target access. See the execution plan for the current candidate matrix.

The first reasoning runtime may be Codex. Jev remains part of the initial product for bounded tactical choices. Kimi or another runtime can be evaluated later. Model selection must not own authorization, mission state, or evidence.

Local-first means local interface, mission state, and evidence. Hosted model inference can still transmit explicitly permitted context to the selected providers. It does not mean the models run on the laptop.

## Initial product experience

The operator creates a mission with a target scope, workflow template, time/cost limits, and approved data destinations. A mission created through OpenCode appears in the same graphical workspace. The operator can inspect either interface without creating another job or losing context.

The central Team view displays real runtime actors and tool workers, their current states, and actual dispatched messages. A Targets view displays hosts, services, observed relationships, hypotheses, and verified results. Findings open their evidence; evidence opens the originating command and execution record.

The visual style uses a near-black/navy workspace, cyan/teal activity accents, restrained amber for waiting, red for denied/failed states, monospaced technical labels, and readable ordinary text. Color is always accompanied by a state label or symbol. Motion is purposeful, interruptible, and supports reduced motion.

Do not invent a large swarm for visual effect. Start with one main agent, Jev, one execution worker, and a verification stage. A tool worker is labeled as a tool worker. Several logical roles may use the same model, but the UI must identify actual runtime instances and avoid implying independent verification where it does not exist.

## Five interface areas

1. Mission control: task description, current activity, public agent messages, scope, budget, and stop control.
2. Team graph: actor states, handoffs, queued work, selected Jev decisions, and inspectable communication.
3. Target map: observed topology, candidate paths, hypotheses, and evidence-backed results. Suspected and verified edges have distinct labels and styles.
4. Execution and evidence: command transcript, tool output, screenshots, findings, and a growing report. Untrusted output is inert text or safely rendered content.
5. Review queue: exact proposed operations, material parameters, immutable content references, expiry, and human decisions. An agent's prose is supplementary. High-impact approval occurs in an authority-owned review surface or local CLI that displays the canonical command and its immutable hash. The main mission UI can request review; its renderer cannot relabel a command or manufacture approval.

Use a side inspector rather than presenting every detail permanently. The normal workflow should not require reading implementation vocabulary. A visible scope indicator and worker-connection state remain available during execution.

## Animation contract

Animations project persisted events. They never create execution state.

| Observed event | Visual behavior |
| --- | --- |
| Actor started | Its node changes from queued to active |
| Message dispatched | A packet moves between the actual sender and recipient; selecting it opens the public message |
| Tool dispatch accepted | The worker activates and the linked transcript opens |
| Execution observation received | A result appears with the producer and evidence reference |
| Target discovered | A labeled node enters the target map |
| Candidate finding recorded | A hypothesis marker appears; it is not marked verified |
| Independent reproduction confirmed | The finding changes to verified and links its evidence |
| Approval requested | The action enters a waiting state with a review item |
| Operation denied | A denied marker and reason appear; no successful-action animation runs |
| Connection lost | A disconnected/stale label replaces the previous live status |
| Cancellation requested | The mission shows stopping until the supervisor confirms cessation |

Show actual messages and explicitly labeled agent summaries. Do not fabricate conversations or claim to display private model reasoning. Replay mode is visibly distinct from live mode and cannot issue execution commands. Replaying a message event never repeats its tool action.

## System architecture

```text
Laptop
  Browser UI ------------------+
                               +--> Sentinel mission service
  OpenCode --> Sentinel MCP ---+       state, scheduler, event projections
                                         |
                                 Authority/executor service
                                 grants, approvals, operations,
                                 provider/GitHub credential custody
                                         |
                                 Constrained sandbox launcher
                                         |
                                Disposable Linux/Kali VM
                                agent runtime, shell/tools,
                                Strix where useful

  Protected inference path --> approved model provider/account
  Bounded evidence ingress --> local evidence store
```

These are responsibility and privilege boundaries, not a requirement for seven microservices. The authority service needs independently owned state and a process identity inaccessible to the scheduler and workers. Separate processes under the same host UID do not establish this boundary; validate distinct OS principals or enforced OS sandbox/IPC controls. The mission service cannot create or enlarge grants. The supervisor accepts fixed execution templates, not arbitrary host commands, mounts, or networking.

Use one active execution attempt initially. Fresh verification must not trust development-writable tests, caches, or summaries. Its controller/harness authority remains outside the compromised assessment guest, and verification uses a fresh independently controlled execution environment with no shared assessment daemon, credentials, or writable state. Disposable targets, where used, have restricted egress and synthetic credentials.

## OpenCode integration

Implement a small Sentinel MCP server as the initial integration. Proposed tool names are design choices, not existing commands:

- `sentinel_submit_mission`: create a request using a registered template and scope reference.
- `sentinel_get_status`: return a compact mission snapshot.
- `sentinel_get_events`: retrieve bounded events after a cursor.
- `sentinel_get_targets`: retrieve the current observed target state.
- `sentinel_get_evidence`: retrieve a bounded permitted evidence preview.
- `sentinel_steer_mission`: add operator guidance without changing authority.
- `sentinel_cancel_mission`: stop future work and request teardown.

Do not expose self-approval, arbitrary grants, credential reads, policy editing, or laptop shell execution through these tools. Mission submission uses preauthorized templates or produces a pending request for the human interface. It cannot authorize a new target merely because the tool text says the user approved it.

OpenCode supports local and remote MCP servers. Its SDK is a separate option if deeper session integration becomes necessary. Start with MCP so OpenCode is another client, not a second mission scheduler. If OpenCode later becomes the worker engine, run that engine behind the same execution boundary and let Sentinel remain the workflow owner.

An unrestricted OpenCode process on the laptop retains whatever host tools and credentials it already has. Sentinel's MCP permissions do not sandbox those unrelated capabilities. The security claim covers Sentinel-managed agents and operations.

References: [OpenCode MCP](https://docs.opencode.ai/docs/mcp-servers/), [OpenCode SDK](https://docs.opencode.ai/docs/sdk/).

## Client-neutral assistant access

Build one versioned Sentinel MCP server. OpenCode is the initial reference client; Hermes, OpenClaw, or another compatible client can use the same tools after transport/authentication configuration and a small interoperability check. Do not add client-specific mission engines or adapter packages by default.

Submission returns a durable mission ID promptly. Require a client-scoped idempotency key bound to canonical parameters; reject reuse with changed parameters. Provide bounded status, cursor-based events, and evidence previews so clients do not require a permanent stream. Client disconnection or an MCP timeout does not cancel a mission. Explicit cancellation requests stopping; steering cannot expand authority.

Authenticate clients and enforce their permissions server-side. No client can approve sensitive actions, create grants, read broker secrets, or select unrestricted host execution. Sentinel owns execution, retries, recovery, and authoritative evidence. Client memory and tool output remain untrusted context; expose only data approved for that client and destination.

Using an assistant framework as the actual sandboxed worker is a separate runtime decision, not a consequence of connecting its MCP client.

## Initial Codex integration

Prototype a narrow runtime adapter around Codex app-server. Its documented purpose includes persistent conversations, streamed events, interruptions, and approvals, which match this interface. Keep the adapter small: start, resume, send/steer, receive public events, and interrupt.

Use a supervised private transport; do not expose the runtime management API directly to the browser or LAN. Pin the runtime/protocol version and contract-test the actual installed schema. Some app-server features and transports are experimental.

The first integration spike must prove runtime placement inside the worker, inference access without broad credentials in that worker, mediation of all relevant tools, event capture, cancellation, and recovery. Do not mount the laptop's login or credential directories into the VM. If the selected authentication/runtime combination cannot satisfy the boundary, change the integration rather than silently weakening it.

The mission store remains authoritative across model/runtime changes. Do not assume native Codex, Kimi, or OpenCode session formats are interchangeable.

References: [Codex platform integration choices](https://developers.openai.com/blog/codex-as-a-platform), [Codex app-server](https://learn.chatgpt.com/docs/app-server).

## Jev's role

Jev is the tactical selector between observations and the next bounded action. It can classify a mission, rank investigations, choose a reviewed playbook, request evidence, switch approach, or escalate to the main agent.

Code constructs immutable candidate action records and computes counters, budgets, deadlines, and prerequisites. Jev selects an action ID or abstains. The executor retrieves the actual parameters and revalidates current scope, task generation, approval, and budget before dispatch.

Begin with three decisions: mission routing, next-playbook selection, and escalation. Use a compact task-specific state. Log the selected option, candidate-set version, returned distribution, latency, and outcome; label explanatory summaries as model-reported. No Jev decision can suppress mandatory evidence, verification, alerts, or authorization.

## State, events, and recovery

SQLite is sufficient initially. Persist mission state, operations, and events with schema migrations. The authoritative grant/approval store is owned by the authority service, not shared read/write with the scheduler.

Use an ordinary durable event table and transactional event publication; do not introduce Kafka, Redis, a separate event store, or full event sourcing. UI state can be rebuilt from snapshots and an event cursor.

A proposed event envelope contains:

```text
event_id, mission_id, sequence, schema_version,
actor_id, execution_generation, operation_id,
event_type, producer, timestamp,
correlation_id, causation_id, payload_reference
```

Distinguish model-reported claims from supervisor-observed execution and independently verified findings. Authenticate producers and enforce event-type ownership: only authority receipts establish authorization and privileged-operation outcomes; only the protected verifier establishes verified findings. Each authoritative state owner publishes from its own transactional outbox, with idempotent ingestion into the mission service's projection. The scheduler cannot promote its own claim into trusted evidence. Projection sequence gives display order; explicit causation and producer records establish relationships. UI timestamps do not establish causality. Store large or sensitive payloads outside the event envelope and send redacted, bounded projections to clients.

Serve the UI from the local service's origin. Use authenticated HTTP for commands and server-sent events for observations. Reconnect using a sequence cursor; deduplicate events. A slow/closed UI must never block a mission or consume unbounded backend memory. Throttle high-frequency output and retain the full bounded transcript separately.

Every external effect has a durable command record and may enter UNKNOWN on a lost response. No blind retry. Use execution generations to fence obsolete workers. Cancellation blocks new authority, revokes networking, terminates execution, then reconciles any already transmitted operations. Closing the UI does not cancel the mission; explicit stop does.

Use a VM lifecycle scoped to one mission. Kali sessions can survive UI and coordinator restarts while that VM remains alive; loss or destruction of the VM does not preserve live shells or connections. Persist their transcripts and reconcile uncertain actions as UNKNOWN. Never reuse a previous mission's sessions, credentials, or writable state for a new mission.

## Security controls required in the first working slice

- Disposable worker with no upstream provider, GitHub, cloud, or operator credentials, laptop home mount, SSH agent, host Docker socket, or shared writable task caches. A task-scoped broker credential remains a credential and must be narrow and revocable.
- Outer default-deny network controls and explicit permitted destinations; target scope must include protocols and testing effects.
- Separately owned grants and exact-operation approvals, checked again at dispatch.
- Fixed provider/account/model routing and server-side spending limits.
- Loopback-only local service, authenticated APIs/event streams, Host/Origin validation, appropriate CSRF protection, and restrictive CORS/CSP.
- Separate human and worker credentials; a worker token cannot approve operations.
- Safe evidence parsing/rendering, no active report HTML, no automatic external image loading, no automatic execution of reproduction text.
- Supervisor-confirmed cancellation, hard deadlines, disk/PID/resource quotas, and failure-closed operation journaling.
- Honest UI states for failed, disconnected, unknown, denied, and unverified outcomes.

Host root and the trusted operator account remain part of the local deployment's trust assumptions. A local UI is not automatically isolated from malicious websites or compromised same-user software.

## Initial implementation stack

| Area | Choice |
| --- | --- |
| UI | React, TypeScript, Vite |
| Agent/target graph | React Flow with custom nodes and event-correlated edges |
| Animation | Motion for React plus small SVG/CSS packet transitions |
| Backend | Node.js/TypeScript, Fastify, explicit schemas |
| State | SQLite and local content-addressed evidence blobs |
| Live UI updates | Authenticated SSE with sequence cursors |
| OpenCode integration | Small local Sentinel MCP server |
| Main runtime | Codex adapter first, conditional on integration spike |
| Tactical decisions | Jev |
| Tools | Existing ARM64 sandbox backend selected by compatibility tests; private guest Docker where required; Kali toolset as needed |
| Desktop packaging | Browser-hosted locally first; Tauri wrapper after the workflow works |

React Flow and Motion supply graph and animation primitives. There is no demonstrated need for a game engine, Three.js, a 3D world, or a custom renderer. Select the VM engine after confirming laptop OS, CPU architecture, available RAM, image compatibility, and reset/network behavior. Do not assume Linux-only microVM tooling runs natively on every laptop.

References: [React Flow](https://reactflow.dev/learn), [Motion](https://motion.dev/docs/react), [Tauri](https://v2.tauri.app/start/).

## Delivery milestones and exit criteria

### 1. Reviewable interaction concept

Create the command-center shell, actor graph, target view, message/evidence inspector, and a clearly labeled simulated mission. Demonstrate finite animated handoffs, waiting, denial, and evidence arrival. This is the current planning preview; it does not run tools.

Exit: the operator can assess the visual direction and understand who is acting, on what, and why an action is waiting.

### 2. Integration and containment spike

Prove the chosen Codex/runtime integration and the actual local VM execution boundary. Validate credential custody, fixed worker provisioning, network enforcement, event capture, interrupt/restart behavior, and a single benign tool execution. Pin versions.

Exit: deliberate worker compromise cannot reach host credentials or another scope; the UI shows observed execution, not invented activity.

### 3. First real mission across both interfaces

Connect the UI and OpenCode MCP client to one mission service. Add task envelopes, operation journal, Jev's first bounded decisions, tool transcripts, evidence storage, and cancellation. Keep one active job.

Exit: start a scoped lab mission from OpenCode, inspect and steer it in the UI, close/reopen the UI, and stop it with confirmed worker teardown. No duplicate execution or lost evidence.

### 4. Offensive lab workflow

Add reviewed playbooks, target observations, candidate findings, selected Strix runs, protected reproductions, and incremental report generation. Simulate wrong Jev choices, malicious tool output, target scope escape, and restart uncertainty.

Exit: a controlled vulnerable lab produces an evidence-backed finding, a verified result, and a reproducible report. A fabricated success cannot close a finding.

### 5. Engagement reporting and broader hardening

Add engagement/report deadlines, evidence completeness checks, screenshot workflow, mission-scoped Kali sessions, data-handling restrictions, and controlled-lab evaluations. Validate connectivity, recovery, permitted data collection and approved export destinations.

Exit: complete a bounded controlled-lab engagement with complete evidence, accurate resumed state, bounded cost, and zero scope violations. Success is measured against independent lab outcomes, not agent claims.

Only then add multiple concurrent workers, alternative model adapters, automatic GitHub publication, richer communication integrations, or native desktop packaging as needed.

## Engagement data handling

Require reproducible documentation, explicit target-file collection rules and destination approval. Distinguish required evidence capture from arbitrary target-file collection. Do not send evidence to unapproved messaging channels or memory systems.

## Components deferred

Client-specific messaging features, generic plugin marketplaces, broad MCP catalogs, PostgreSQL, distributed workflow engines, OPA deployment, SPIRE deployment, a new Vault deployment, multi-user tenancy, unrestricted autonomous delegation, production deployment, and 3D rendering are not prerequisites. Compatible assistants connect through the shared MCP server.

Jev is not deferred. The visual command center is not deferred. Both participate in the first useful vertical slice, with animations driven by the same persisted events used for audit and recovery.

## Decisions still open

1. Existing sandbox backend, outer networking, and ARM64 tool/image compatibility on the target Apple Silicon/macOS platform, whose supported resource envelope remains unverified. Docker Sandboxes is the first feasibility candidate, not a validated selection.
2. Codex authentication and inference-proxy compatibility under the actual worker boundary.
3. Exact initial lab target class and reviewed playbooks.
4. Provider accounts, permitted data flows, and spending ceilings.
5. When native desktop packaging becomes useful enough to justify it.
6. Whether OpenCode eventually remains a client or also supplies a worker engine.

Do not block the interface concept on those choices. Do block real execution on proving the containment and credential boundaries.
