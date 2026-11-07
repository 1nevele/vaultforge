# Development tooling assets

These are repository preparation assets, not Sentinel application code.

- `provenance.json`: pinned upstream identities, complete adopted/generated asset hashes, exact Superpowers text adaptations and license hashes.
- `licenses/`: unmodified upstream MIT licenses.
- `issue_flow.py`: the issue-flow label reconciler run by `.github/workflows/issue-flow.yml` (specs/002 CA-008, `docs/operating-model.md`); tested offline by `tests/test_issue_flow.py`.
- `sentinel_maintainer_gate.py`: Eleven's PR-only wake gate (`docs/eleven-maintainer.md`); tested by `tests/test_sentinel_maintainer_gate.py`.
- `tests/test_workflow_setup.py`: offline inventory, integrity, safe-path, namespace/resource and current-configuration acceptance checks. They do not test Claude's skill loader or prove the model follows a skill.

Run from the repository root:

```bash
python -B -m unittest discover -s tools/tests -v
```

No runtime installer, startup download hook or vendored VMM is supplied. See `docs/development-workflow.md` and `docs/claude-web-skill-smoke.md` for supported scope and the separate real-executor discovery gate.

## Updating assets

Do not edit a pin or refresh hashes merely to silence a failure. Review the proposed upstream revision and license; generate Spec Kit in a separate scratch project with the documented pinned official integration; preserve the project constitution. Reapply only the documented native-namespace/excluded-skill adaptations and inspect the diff. Validate source hashes against the exact upstream Git tree, replay declared adaptations, then validate output hashes and complete inventory. Commit changed provenance and actual verification evidence together.

Generated metadata records preparation-time versions and timestamps; it does not establish the cloud runtime version. This repository does not install the Specify CLI in Claude's cloud environment. Native skill prompts call the committed Bash scripts directly. Optional workflow CLI dispatch requires a separately reviewed installation if needed later.
