#!/usr/bin/env python3
"""Handoff-to-head lag, read from git alone (R10-RCA-RELAY-HANDOFF-STARVATION).

For every origin/handoff/<topic> whose pull-request branch (fix/<topic> or
fix/<topic>-pr) contains the handoff tip, the lag is the committer time of the
first commit on the branch's ancestry path from the tip to the head, less the
tip's own committer time. A handoff the head does not contain is `uncarried`.
Reads refs only; no REST. Exit 1 when any lag exceeds --limit minutes.

  python3 -I relay_handoff_lag.py [--repo DIR] [--limit MIN] [--since ISO]
"""
import argparse, subprocess, sys

def git(repo, *a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()

def lags(repo, since=0):
    rc, out = git(repo, "for-each-ref", "--format=%(refname:strip=4) %(objectname) %(committerdate:unix)",
                  "refs/remotes/origin/handoff")
    rows = []
    for line in out.splitlines():
        topic, hs, ht = line.split()
        if int(ht) < since:
            continue
        head = next((h for b in (f"fix/{topic}", f"fix/{topic}-pr")
                     for h in [git(repo, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{b}")[1]] if h), "")
        if not head:
            continue
        if git(repo, "merge-base", "--is-ancestor", hs, head)[0] != 0:
            rows.append((topic, hs[:9], None, "uncarried")); continue
        if hs == head:
            rows.append((topic, hs[:9], 0, "tip")); continue
        _, ts = git(repo, "log", "--ancestry-path", "--format=%ct %ae", f"{hs}..{head}")
        first = min((int(l.split()[0]), l.split()[1]) for l in ts.splitlines())
        rows.append((topic, hs[:9], (first[0] - int(ht)) / 60.0, first[1]))
    return rows

def self_test():
    """A synthetic origin: one handoff carried after 2 min (green), one after 40 min (red), one never."""
    import os, tempfile
    d = tempfile.mkdtemp(); env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    def g(*a, at=None):
        e = dict(env, **({"GIT_COMMITTER_DATE": f"@{at} +0000", "GIT_AUTHOR_DATE": f"@{at} +0000"} if at else {}))
        return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=e, check=True).stdout.strip()
    g("init", "-q", "-b", "main"); g("commit", "-q", "--allow-empty", "-m", "base", at=1000)
    for topic, wait in (("fast", 120), ("slow", 2400), ("never", None)):
        g("checkout", "-q", "-b", f"fix/{topic}", "main"); g("commit", "-q", "--allow-empty", "-m", "pr", at=1100)
        g("checkout", "-q", "-b", f"h/{topic}", f"fix/{topic}"); g("commit", "-q", "--allow-empty", "-m", "handoff", at=2000)
        hs = g("rev-parse", "HEAD")
        g("update-ref", f"refs/remotes/origin/handoff/{topic}", hs)
        if wait is None:
            g("update-ref", f"refs/remotes/origin/fix/{topic}", g("rev-parse", f"fix/{topic}")); continue
        g("checkout", "-q", f"fix/{topic}"); g("merge", "-q", "--no-ff", "-m", "carry", hs, at=2000 + wait)
        g("update-ref", f"refs/remotes/origin/fix/{topic}", g("rev-parse", "HEAD"))
    got = {t: (lag, who) for t, _, lag, who in lags(d)}
    assert round(got["fast"][0]) == 2 and round(got["slow"][0]) == 40, got
    assert got["never"][0] is None, got
    print("self-test ok: fast=2m (green), slow=40m (LATE at 15m), never=uncarried (not scored)")

if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test(); sys.exit(0)
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--limit", type=float, default=15)
    ap.add_argument("--since", type=int, default=0, help="unix time; older handoffs are ignored")
    a = ap.parse_args()
    bad = 0
    for topic, hs, lag, who in sorted(lags(a.repo, a.since), key=lambda r: -(r[2] or -1)):
        flag = lag is not None and lag > a.limit
        bad += flag
        print(f"{'LATE' if flag else 'ok  '} {topic} {hs} lag={'-' if lag is None else f'{lag:.0f}m'} {who}")
    print(f"late={bad} limit={a.limit}m"); sys.exit(1 if bad else 0)
