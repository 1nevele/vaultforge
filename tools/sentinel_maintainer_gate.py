"""PR-only merge/notification gate. No network data is operational authority.

The scheduler evaluates the JSON wakeAgent field before creating an AI session.
A run acknowledges only its exact pending snapshot, so failures are retryable and
new activity cannot be swallowed by acknowledging a later live snapshot.
"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import subprocess

REPOSITORY = '1nevele/vaultforge'
EMPTY = {'prs': {}}


def api_records(path, query):
    result = subprocess.run(
        ['gh', 'api', '--paginate', f'repos/{REPOSITORY}/{path}', '--jq', query],
        check=True, capture_output=True, text=True, timeout=60,
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def ordered(records):
    return sorted(records, key=canonical)


def fetch_snapshot(api=api_records):
    pulls = api('pulls?state=open&per_page=100',
                '.[] | {number,head:.head.sha,base:.base.sha,draft}')
    snapshot = {'prs': {}}
    for pull in pulls:
        number, sha = pull['number'], pull['head']
        review = api(f'pulls/{number}/reviews?per_page=100',
                     '.[] | {id,state,commit_id,user:.user.login}')
        comments = api(f'issues/{number}/comments?per_page=100',
                       '.[] | {id,updated_at,user:.user.login}')
        inline = api(f'pulls/{number}/comments?per_page=100',
                     '.[] | {id,updated_at,user:.user.login}')
        checks = api(f'commits/{sha}/check-runs?per_page=100',
                     '.check_runs[] | {id,name,status,conclusion}')
        statuses = api(f'commits/{sha}/status?per_page=100',
                       '.statuses[] | {context,state,updated_at}')
        snapshot['prs'][str(number)] = {
            **pull,
            'reviews': ordered(r for r in review if r['user'] != '1nevele'),
            'comments': ordered(r for r in comments if r['user'] != '1nevele'),
            'inline_comments': ordered(r for r in inline if r['user'] != '1nevele'),
            'checks': ordered(checks), 'statuses': ordered(statuses),
        }
    return snapshot


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


@contextmanager
def state_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.lock').open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        yield


def read_state(path):
    return json.loads(path.read_text()) if path.exists() else {'acked': EMPTY}


def write_state(path, state):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as handle:
        handle.write(canonical(state))
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def poll(path, fetch):
    try:
        # Explicitly discard legacy issue fingerprints: issue changes cannot
        # wake the narrowed merge/notification role, including during migration.
        snapshot = {'prs': fetch()['prs']}
        with state_lock(path):
            state = read_state(path)
            if snapshot == {'prs': state.get('acked', EMPTY).get('prs', {})}:
                return {'wakeAgent': False, 'status': 'unchanged'}
            event_id = hashlib.sha256(canonical(snapshot).encode()).hexdigest()
            state['pending'] = {'event_id': event_id, 'snapshot': snapshot}
            write_state(path, state)
            return {'wakeAgent': True, 'event_id': event_id,
                    'open_pr_count': len(snapshot['prs'])}
    except Exception as exc:
        return {'wakeAgent': False, 'status': 'lookup_or_state_failed',
                'error_type': type(exc).__name__}


def acknowledge(path, event_id):
    with state_lock(path):
        state = read_state(path)
        pending = state.get('pending', {})
        if pending.get('event_id') != event_id:
            raise ValueError('Acknowledgement does not match the pending event')
        write_state(path, {'acked': pending['snapshot']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    home = Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes')))
    parser.add_argument('--state', type=Path,
                        default=home / 'sentinel-maintainer' / 'activity-state.json')
    parser.add_argument('--ack', metavar='EVENT_ID')
    args = parser.parse_args()
    if args.ack:
        acknowledge(args.state, args.ack)
        print(canonical({'acknowledged': args.ack}))
    else:
        payload = poll(args.state, fetch_snapshot)
        # Keep fail-closed errors inspectable without leaking raw API stderr.
        try:
            with state_lock(args.state):
                write_state(args.state.with_name('gate-status.json'), payload)
        except OSError:
            payload = {'wakeAgent': False, 'status': 'status_write_failed'}
        print(canonical(payload))


if __name__ == '__main__':
    main()
