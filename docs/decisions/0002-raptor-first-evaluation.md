# 0002 — RAPTOR-first feasibility evaluation

Date: 2026-11-05. Status: evaluation order only; **no engine selected; no integration proven**.

## Decision and evidence boundary

Evaluate `gadievron/raptor` before `usestrix/strix`, respecting the requested preference. Keep Strix as the application-testing comparator, not a presumed inferior fallback. This is fit-based prioritisation, not benchmark superiority. Sentinel remains one active worker behind a private backend; external authority owns grants and providers, Jev selects immutable candidates, and CDM output remains advisory derived evidence.

Pinned public HTTPS snapshots:

- RAPTOR: `e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd`.
- Strix: `851743adcf989a3afcc469fc0379f9fceea4e4b5`.

Verified here means retrieved documentation or statically inspected code, **not measured behaviour**. No installation, upstream-code execution, scanning, target access, credentials, or homelab access occurred. ARM64 execution, image manifests, dependency resolution, memory use, cancellation and broker compatibility remain untested.

## Fit and integration surface

**RAPTOR:** its documented workflows connect source analysis, SCA, binary investigation, fuzzing and patch proposals; `/web` also covers running applications. This breadth makes it a plausible source/binary research candidate, not exclusively DAST[1]. Python requires `>=3.12,<4.0`; optional groups include binary, browser and provider dependencies[3]. Interactive use depends on Claude Code; standalone mechanical workflows do not, and standalone LLM analysis can use configured providers[1]. The Claude Code adapter invokes a subprocess transport, so that route adds a separately supervised runtime and account boundary[5]. The development toolchain alone establishes none of these runtime prerequisites.

Inspect the CLI/file boundary first, not an assumed service API: `raptor.py` dispatches workflow modes, including SCA through a separate shim[20]. Shell slash commands are not a Sentinel RPC contract. Define and version an adapter envelope for exit status, evidence paths, partial results and errors; do not embed internal Python modules as a stable SDK without a separate compatibility test.

**Strix:** documented local runs accept source directories and deployed applications, with noninteractive mode and run-directory outputs[8]. Thus source-aware and DAST workloads overlap RAPTOR; neither is universally better. Its Python `>=3.12` package uses OpenAI Agents/LiteLLM rather than declaring Claude Code as its engine prerequisite[10]. Local CLI supervision is the candidate interface. MCP configuration makes Strix an MCP **client** of stdio/HTTP servers; that is not evidence of a Sentinel-facing engine server[14]. Do not confuse the separately documented cloud API with local private-backend integration.

## Licensing and platform feasibility

RAPTOR's actual LICENSE is MIT: retain copyright/permission notices; warranty is disclaimed[2]. This resolves the earlier metadata `NOASSERTION`, not every dependency's terms. Bundled notices retain separate licences; CodeQL has its own permitted-use and redistribution restrictions[19][17]. Start without CodeQL or redistribution until the exact dependency/image inventory is reviewed.

Strix's actual Apache-2.0 text includes copyright/patent grants, patent-litigation termination, licence/notice retention and modification notices on redistribution; it does not grant trademark rights[9]. Neither repository licence licenses every bundled tool or provider service. These are source observations, not legal clearance.

RAPTOR documents Linux isolation and macOS Seatbelt, but macOS lacks Linux PID/mount namespaces and uses coarser controls[18]. Its container recipe also skips unavailable `rr`; recipe portability is not proof of full tool parity[4]. Strix's Dockerfile has ARM64 branches for several downloads, including Gitleaks, Trivy and Caido; this does not prove a published ARM64 image or complete Apple Silicon functionality[11]. Apple Silicon/macOS support is an unverified target requirement; native compatibility and resource measurements are required. Linux inspection cannot certify that platform. Begin with minimal source tooling, not the full browser/binary stack.

## Authority, credentials and supervision

RAPTOR documents launcher-held provider keys and socket-based workers, but direct Python CLI invocations hold keys in-process[22]. Its dispatcher is **not** Sentinel's external authority. Prove keyless broker routing and disable ambient provider selection before adding inference. Its sandbox documentation explicitly distinguishes process-tree supervision from confinement and recommends a disposable outer environment[18]. Require both isolation and externally enforced process cleanup.

Strix's Docker client adds `NET_ADMIN`/`NET_RAW` and host-gateway access; manifest-dependent branches can add `SYS_ADMIN` with unconfined AppArmor. Resource caps are opt-in, and bind mounts default writable unless explicitly specified[13]. Those defaults are not acceptable Sentinel policy without containment changes. MCP omission exposes all server tools, and connection failures can be skipped; explicitly allowlist tools and fail required dependencies closed[14].

Neither engine's autonomy, prompts, sandbox or model permissions can issue Sentinel grants. Do not expose a host Docker socket, operator HOME, privileged MCP subprocess, or direct target/provider bypass. Report any required bypass as a failed fit criterion, not an integration workaround.

## Requirements for the later selection spec

Before application code, the lead must confirm the applicable specification, test-first implementation and independent-review workflow; this note does not verify tooling activation. The later spec SHALL: (R1) separate source, binary and HTTP/DAST capability profiles; (R2) pin engine, dependencies and image digests with licence inventory; (R3) require authority-owned grants/provider routing and prohibit ambient secrets; (R4) enforce one worker, immutable inputs and versioned evidence/error schemas; (R5) require independent containment, resource, cancellation and bypass tests; (R6) record native ARM64 compatibility, measured resource requirements and unsupported features; (R7) retain RAPTOR-first ordering without selecting an engine until acceptance evidence is reviewed. No application implementation is authorised by this note.

## Future benign spike: executable tests and gates

**Not executed now.** After separate approval and pre-provisioning of pinned, disposable workers, run these commands through the future adapter, never directly on the operator host. No adapter is supplied by this note.

1. Interface smoke: RAPTOR `python3 raptor.py --help`; comparator `strix --help`. Capture exit status/stdout/stderr and enforce a 30-second deadline. Pass: bounded completion, no login, image download, provider call or config mutation outside disposable storage.
2. Fixture evidence: RAPTOR `python3 raptor.py sca --repo "$FIXTURE" --no-llm` on an owned minimal dependency fixture, with network denied[1]. Pass: structured artefacts or explicit blocked/partial status; immutable input hashes unchanged. Missing advisory data must not become a clean-security claim.
3. Isolation probes, through the same engine tool path: `python3 -c 'open("/sentinel-canary").read()'` and `python3 -c 'open("/fixture/forbidden","w").write("x")'`. Pass: denied; outer supervisor verifies canary and read-only fixture unchanged. Use synthetic canaries only.
4. Lifecycle probe: `python3 -c 'import subprocess,time; subprocess.Popen(["sleep","300"]); time.sleep(300)'`. Cancel after two seconds; independently assert no descendants/containers remain within five seconds. Disconnect/restart must not rerun it.
5. Broker gate: approved local mock provider/HTTP-health fixture only. Attempt missing, expired and wrong-task grants; require zero fixture-side effects. One valid grant permits only its frozen request, with external audit and spend reservation. Test direct-client bypass independently.

Pass only with one active worker, explicit unsupported states, attributable evidence and native ARM64 success. Start with the original plan's proposed two vCPUs and 4-GiB allocation where configurable, measure host headroom and peak usage, and revise limits only through the selection spec. Otherwise document the blocker and evaluate Strix against the same gates. Finding quality requires a later independently labelled corpus; this note makes no accuracy ranking.

## Sources

[1] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/README.md — raptor/README.md
[2] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/LICENSE — raptor/LICENSE
[3] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/pyproject.toml — raptor/pyproject.toml
[4] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/.devcontainer/Dockerfile — raptor/.devcontainer/Dockerfile
[5] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/core/llm/cc_adapter.py — raptor/core/llm/cc_adapter.py
[8] https://raw.githubusercontent.com/usestrix/strix/851743adcf989a3afcc469fc0379f9fceea4e4b5/README.md — strix/README.md
[9] https://raw.githubusercontent.com/usestrix/strix/851743adcf989a3afcc469fc0379f9fceea4e4b5/LICENSE — strix/LICENSE
[10] https://raw.githubusercontent.com/usestrix/strix/851743adcf989a3afcc469fc0379f9fceea4e4b5/pyproject.toml — strix/pyproject.toml
[11] https://raw.githubusercontent.com/usestrix/strix/851743adcf989a3afcc469fc0379f9fceea4e4b5/containers/Dockerfile — strix/containers/Dockerfile
[13] https://raw.githubusercontent.com/usestrix/strix/851743adcf989a3afcc469fc0379f9fceea4e4b5/strix/runtime/docker_client.py — strix/strix/runtime/docker_client.py
[14] https://raw.githubusercontent.com/usestrix/strix/851743adcf989a3afcc469fc0379f9fceea4e4b5/docs/integrations/mcp.mdx — strix/docs/integrations/mcp.mdx
[17] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/docs/dependencies.md — docs/dependencies.md
[18] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/docs/sandbox.md — docs/sandbox.md
[19] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/THIRD_PARTY_NOTICES.md — THIRD_PARTY_NOTICES.md
[20] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/raptor.py — raptor.py
[22] https://raw.githubusercontent.com/gadievron/raptor/e7063e5e7b7802ec980274dd37e4bcb3e1a86fdd/docs/llm.md — docs/llm.md
