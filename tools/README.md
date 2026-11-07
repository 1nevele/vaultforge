# Tools

- `sentinel_maintainer_gate.py`: Eleven's PR poller, which wakes Eleven only when a PR
  changes (`docs/operating-model.md`). Tested by `tests/test_sentinel_maintainer_gate.py`.
- `licenses/`: the unmodified MIT licenses of the bundled upstream assets:
  - Superpowers, `obra/superpowers@22f0b463e7a5e579904dd6211a520321035526f7`: the
    `test-driven-development`, `systematic-debugging` and
    `verification-before-completion` skills in `.claude/skills/`, with `superpowers:`
    namespaces removed;
  - Spec Kit, `github/spec-kit@99d10403a2681981be98bd372fa412045180d105`: the nine
    `speckit-*` skills and `.specify/`.

Run the tests from the repository root:

```bash
python -B -m unittest discover -s tools/tests -v
```
