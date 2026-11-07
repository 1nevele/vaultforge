"""Deterministic risk gate: a required check that blocks merge on high-risk diffs.

CodeRabbit's auto-approval is a blanket on/off switch with no risk awareness.
This script supplies the missing risk tier: it fails (blocking, required-check
status) for any PR whose diff touches sensitive paths or is large, regardless
of what CodeRabbit or any other reviewer says. Low/medium risk PRs still need
their normal required approval; this only ever adds a block, never a bypass.
"""
import json
import os
import subprocess
import sys

SENSITIVE = ('.github/workflows/', '.github/claude-review/', '.claude/',
             '.specify/memory/', 'specs/002-vaultforge-claude-automation/')
SENSITIVE_FILES = {
    'AGENTS.md', 'CLAUDE.md', 'CODEOWNERS', '.github/CODEOWNERS', 'docs/CODEOWNERS',
    '.coderabbit.yaml', 'tools/claude_review.py', 'tools/tests/test_claude_review.py',
    'tools/risk_gate.py', 'tools/tests/test_risk_gate.py',
}
CODE_EXTENSIONS = ('.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.rb', '.java', '.sh', '.json', '.toml')


def compute_risk(paths, additions, deletions):
    total = additions + deletions
    if any(p in SENSITIVE_FILES or p.startswith(SENSITIVE) for p in paths) or total > 200:
        return 'high'
    if total > 40 or any(p.lower().endswith(CODE_EXTENSIONS) for p in paths):
        return 'medium'
    return 'low'


def collect_paths(files):
    """Paths to classify: each file's path plus a rename's source path."""
    paths = [f['filename'] for f in files]
    paths.extend(f['previous_filename'] for f in files if f.get('previous_filename'))
    return paths


def decide(risk):
    """Exit code for the required check: only 'high' blocks."""
    return 1 if risk == 'high' else 0


def main():
    number = os.environ['PR_NUMBER']
    pages_text = subprocess.check_output(
        ['gh', 'api', f'repos/1nevele/vaultforge/pulls/{number}/files?per_page=100', '--paginate'],
        text=True, timeout=90)
    decoder = json.JSONDecoder()
    files, remaining = [], pages_text.lstrip()
    while remaining:
        page, end = decoder.raw_decode(remaining)
        files.extend(page)
        remaining = remaining[end:].lstrip()
    paths = collect_paths(files)
    additions = sum(f['additions'] for f in files)
    deletions = sum(f['deletions'] for f in files)
    risk = compute_risk(paths, additions, deletions)
    print(f'risk={risk} files={len(files)} additions={additions} deletions={deletions}')
    if risk == 'high':
        print('BLOCKED: high-risk diff requires explicit human review before merge.')
    sys.exit(decide(risk))


if __name__ == '__main__':
    main()
