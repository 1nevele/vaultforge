"""Executor claim lock on a git branch (specs/002 CA-003).

The tip of `claude/executor-lock` on `origin` is the lock. It is a commit with an
empty tree whose message is `held <token>` or `free <token>`. Every change is a new
child of the tip just read, pushed without force, so the remote accepts it only if
the tip has not moved since: the push is the compare-and-swap. Two runs that read
the same tip cannot both win.

A held lock whose committer date is older than the stale limit was left by a run
that crashed, and the next acquire breaks it the same way. A tip that is neither
`held` nor `free` counts as held until it is stale, so a stray push fails closed.

Usage, from a clone with push access (exit 0 success, 3 refused, 1 error, 2 usage):
    python3 tools/executor_lock.py acquire [--stale-minutes N]   # prints the token
    python3 tools/executor_lock.py check TOKEN
    python3 tools/executor_lock.py release TOKEN
"""
import os
import re
import secrets
import subprocess
import sys
import time

BRANCH = 'claude/executor-lock'
REMOTE = 'origin'
STALE_MINUTES = 30
_LOCAL = 'refs/executor-lock/tip'
_MESSAGE = re.compile(r'^(held|free) ([0-9a-f]{32})$')
_IDENTITY = ('-c', 'user.name=Vaultforge executor lock',
             '-c', 'user.email=executor-lock@users.noreply.github.com')


class LockError(RuntimeError):
    """Git failed for a reason other than losing the race."""


def _git(cwd, *args, env=None, check=True):
    result = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, input='',
                            env={**os.environ, **(env or {})}, timeout=120)
    if check and result.returncode != 0:
        raise LockError(f'git {args[0]} failed: {result.stderr.strip()[:300]}')
    return result


def fetch_tip(cwd):
    """The remote lock tip as {'sha', 'state', 'token', 'time'}, or None if absent."""
    listed = _git(cwd, 'ls-remote', REMOTE, f'refs/heads/{BRANCH}').stdout.split()
    if not listed:
        return None
    _git(cwd, 'fetch', '-q', '--no-tags', REMOTE, f'+refs/heads/{BRANCH}:{_LOCAL}')
    sha, stamp, message = _git(cwd, 'log', '-1', '--format=%H%n%ct%n%s', _LOCAL).stdout.split('\n', 2)
    match = _MESSAGE.match(message.strip())
    return {'sha': sha, 'time': int(stamp),
            'state': match.group(1) if match else None,
            'token': match.group(2) if match else None}


def _push(cwd, tip, message, env=None):
    """Push a child of `tip` with `message`; True if it landed, False if the tip moved."""
    tree = _git(cwd, 'hash-object', '-t', 'tree', '-w', '--stdin').stdout.strip()
    parent = ['-p', tip['sha']] if tip else []
    commit = _git(cwd, *_IDENTITY, 'commit-tree', tree, *parent, '-m', message,
                  env=env).stdout.strip()
    pushed = _git(cwd, 'push', '--porcelain', REMOTE, f'{commit}:refs/heads/{BRANCH}',
                  check=False)
    if pushed.returncode == 0:
        return True
    if any(line.startswith('!\t') for line in pushed.stdout.splitlines()):
        return False  # rejected: someone else moved the tip first
    raise LockError(f'git push failed: {(pushed.stderr or pushed.stdout).strip()[:300]}')


def try_claim(cwd, tip, env=None):
    """Claim the lock as a child of `tip` (None: create the branch). Token or None."""
    token = secrets.token_hex(16)
    return token if _push(cwd, tip, f'held {token}', env=env) else None


def _is_held(tip, stale_minutes):
    if tip is None or tip['state'] == 'free':
        return False
    return time.time() - tip['time'] < stale_minutes * 60


def acquire(cwd, env=None, stale_minutes=STALE_MINUTES):
    """Take the lock if it is free or stale. Returns the new token, or None if held."""
    tip = fetch_tip(cwd)
    if _is_held(tip, stale_minutes):
        return None
    return try_claim(cwd, tip, env=env)


def current_token(cwd):
    """The token holding the lock right now, if any (stale or not)."""
    tip = fetch_tip(cwd)
    return tip['token'] if tip and tip['state'] == 'held' else None


def check(cwd, token):
    """True while `token` is still the holder."""
    return current_token(cwd) == token


def release(cwd, token):
    """Free the lock if `token` still holds it. False if it does not (nothing changed)."""
    tip = fetch_tip(cwd)
    if not tip or tip['state'] != 'held' or tip['token'] != token:
        return False
    return _push(cwd, tip, f'free {token}')


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    cwd = os.getcwd()
    try:
        if args[:1] == ['acquire'] and len(args) in (1, 3) and args[1:2] in ([], ['--stale-minutes']):
            stale = int(args[2]) if len(args) == 3 else STALE_MINUTES
            token = acquire(cwd, stale_minutes=stale)
            if token is None:
                print('executor_lock: held by another run', file=sys.stderr)
                return 3
            print(token)
            return 0
        if args[:1] in (['check'], ['release']) and len(args) == 2:
            ok = (check if args[0] == 'check' else release)(cwd, args[1])
            return 0 if ok else 3
    except (LockError, ValueError) as error:
        print(f'executor_lock: {error}', file=sys.stderr)
        return 1
    print(__doc__.split('Usage', 1)[1].strip(), file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
