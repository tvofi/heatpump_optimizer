#!/usr/bin/env python3
"""Independent fix-review probe for PR #2526 (gate-lease priority + slot lifetime).

Reviewer-authored instrument, not the fixer's. Drives the public functions
directly; prints one RESULT line per assertion. Run:

    python3 probe.py <worktree>

Where <worktree> is a detached checkout at the head under review.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

WT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
ROWS = []


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


g = load("gate_lock_review", WT / "tests" / "gate_lock.py")
sys.path.insert(0, str(WT / "tools" / "pr"))
sys.path.insert(0, str(WT / "tools" / "audit" / "seat"))
gp = load("gate_priority_review", WT / "tools" / "pr" / "gate_priority.py")


def check(name, ok, detail=""):
    ROWS.append(ok)
    print(f"RESULT {'PASS' if ok else 'FAIL'} | {name} | {detail}")


def dead_pid():
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


# ---------------------------------------------------------------- slot lifetime
def plant_slot(lockdir, *, pid, expired):
    pool = g.pool_dir(lockdir)
    g._ensure_lock_dir(pool)
    now = datetime.now(UTC)
    taken = now - timedelta(seconds=600)
    exp = (now - timedelta(seconds=1)) if expired else (now + timedelta(seconds=600))
    # Owner(label, expires_at, taken_at, pid) -- expiry is the SECOND field.
    g.Owner("holder", exp, taken, pid).write(g._slot_path(pool, 0))


def try_take(lockdir, who="fifth", slots=1):
    try:
        g.take_slot(who, lock_dir=lockdir, slots=slots, lease_seconds=60, wait=False)
        return True
    except BlockingIOError:
        return False


with tempfile.TemporaryDirectory() as td:
    base = Path(td)
    # 1. live holder past lease is KEPT
    d = base / "live"
    plant_slot(d, pid=os.getpid(), expired=True)
    check("live holder past lease keeps its slot", try_take(d) is False)

    # 2. dead holder past lease reclaimed at once
    d = base / "dead"
    plant_slot(d, pid=dead_pid(), expired=True)
    check("dead holder past lease reclaimed", try_take(d) is True)

    # 3. dead holder BEFORE expiry reclaimed at once (no wait for the lease)
    d = base / "deadfresh"
    plant_slot(d, pid=dead_pid(), expired=False)
    check("dead holder reclaimed before its lease expiry", try_take(d) is True)

    # 4. no-pid expired freed; no-pid fresh respected
    d = base / "nopid"
    plant_slot(d, pid=None, expired=True)
    freed = try_take(d)
    d = base / "nopidfresh"
    plant_slot(d, pid=None, expired=False)
    kept = try_take(d) is False
    check("no-pid expired freed, no-pid fresh respected", freed and kept,
          f"freed={freed} fresh_kept={kept}")

    # 5. status witnesses: past-lease and unleased, both driven
    d = base / "status"
    plant_slot(d, pid=os.getpid(), expired=True)
    g.mark_unleased("prepr-x", lock_dir=d, pid=os.getpid())
    s = g.slots_status(lock_dir=d, slots=1)
    ok = s["past_lease"] == ["0:holder"] and s["unleased"] == ["prepr-x"]
    check("slot-status counts a live past-lease holder and an unleased run", ok,
          f"past_lease={s['past_lease']} unleased={s['unleased']}")
    g.clear_unleased("prepr-x", lock_dir=d)
    s2 = g.slots_status(lock_dir=d, slots=1)
    check("clear_unleased empties the count", s2["unleased"] == [], f"unleased={s2['unleased']}")
    g.mark_unleased("prepr-dead", lock_dir=d, pid=dead_pid())
    s3 = g.slots_status(lock_dir=d, slots=1)
    check("a dead unleased marker is pruned", s3["unleased"] == [], f"unleased={s3['unleased']}")

    # 6. a taker records a pid even when the caller names none
    d = base / "recorded"
    g.take_slot("auto", lock_dir=d, slots=1, lease_seconds=60, wait=False)
    o = g._read_at(g._slot_path(g.pool_dir(d), 0))
    check("take_slot with no owner_pid records this process", o is not None and o.pid == os.getpid(),
          f"pid={None if o is None else o.pid}")

# ---------------------------------------------------------------- priority queue
with tempfile.TemporaryDirectory() as td:
    d = Path(td) / "q"
    now = datetime.now(UTC)
    g._ensure_lock_dir(d)

    def ticket(n, who, prio, age):
        (d / f"{g.TICKET_PREFIX}{n:012d}").write_text(
            f"label={who}\npid={os.getpid()}\n"
            f"expires_at={(now + timedelta(seconds=9000)).isoformat()}\n"
            f"priority={prio}\nqueued_at={(now - timedelta(seconds=age)).isoformat()}\n")

    ticket(1, "normal", 0, g.PRIORITY_AGING_SECONDS + 1)
    ticket(2, "urgent", 2, 5)
    check("aging promotes an aged normal past a younger urgent",
          [w.label for w in g._queue(d, now=now)] == ["normal", "urgent"])
    # null control one second short
    d2 = Path(td) / "q2"
    g._ensure_lock_dir(d2)
    (d2 / f"{g.TICKET_PREFIX}{1:012d}").write_text(
        f"label=normal\npid={os.getpid()}\nexpires_at={(now + timedelta(seconds=9000)).isoformat()}\n"
        f"priority=0\nqueued_at={(now - timedelta(seconds=g.PRIORITY_AGING_SECONDS - 1)).isoformat()}\n")
    (d2 / f"{g.TICKET_PREFIX}{2:012d}").write_text(
        f"label=urgent\npid={os.getpid()}\nexpires_at={(now + timedelta(seconds=9000)).isoformat()}\n"
        f"priority=2\nqueued_at={(now - timedelta(seconds=5)).isoformat()}\n")
    check("null control: below the window priority still orders",
          [w.label for w in g._queue(d2, now=now)] == ["urgent", "normal"])
    # malformed parsing
    parsed = [g._read_priority(v) for v in (None, "", "junk", "9", "-4", "2.5", " 1 ")]
    check("malformed/out-of-range priorities parse to 0 or clamp",
          parsed == [0, 0, 0, 2, 0, 0, 1], f"parsed={parsed}")
    # rewrite keeps priority + queued_at
    d3 = Path(td) / "q3"
    p1 = g._enqueue(d3, "w", None, priority=2)
    first = g._fields(p1.read_text())
    p2 = g._enqueue(d3, "w", p1, priority=2)
    second = g._fields(p2.read_text())
    check("rewrite keeps priority and queued_at",
          p2 == p1 and first.get("priority") == "2" and first.get("queued_at") == second.get("queued_at"))

# ---------------------------------------------------------------- derivation
live_ref = None
r = subprocess.run(["git", "-C", str(WT), "for-each-ref", "--format=%(refname)",
                    "refs/remotes/origin/handoff/audit-r10-roster"],
                   capture_output=True, text=True)
if r.returncode == 0 and r.stdout.strip():
    live_ref = r.stdout.strip().splitlines()[0]

with tempfile.TemporaryDirectory() as td:
    d = Path(td)
    # channels that need no git: env > marker
    (d / gp.MARKER_NAME).write_text("1\n")
    check("marker answers when no env and no git",
          gp.priority_for_branch("b", repo=str(d), fetch=False, env={}) == 1)
    check("env overrides marker",
          gp.priority_for_branch("b", repo=str(d), fetch=False,
                                 env={gp.PRIORITY_ENV: "2"}) == 2)
    check("malformed env is skipped, not fatal (marker answers)",
          gp.priority_for_branch("b", repo=str(d), fetch=False,
                                 env={gp.PRIORITY_ENV: "junk"}) == 1)
    (d / gp.MARKER_NAME).write_text("not-an-int\n")
    check("malformed marker with no git resolves to 0, no crash",
          gp.priority_for_branch("b", repo=str(d), fetch=False, env={}) == 0)
    (d / gp.MARKER_NAME).unlink()
    # nonexistent repo -> 0, no crash
    check("nonexistent repo resolves to 0, no crash",
          gp.priority_for_branch("b", repo=str(d / "nope"), fetch=True, env={}) == 0)

# derived against the live roster ref, read only (no fetch)
if live_ref:
    check("live: listed group -> 1",
          gp.derived_priority("handoff/r10-sav-reasons", repo=str(WT),
                              ref=live_ref, fetch=False) == 1)
    check("live: unlisted/unmapped branch -> 0",
          gp.derived_priority("handoff/r10-gate-priority", repo=str(WT),
                              ref=live_ref, fetch=False) == 0)
    check("live: ref lacking the file -> 0",
          gp.derived_priority("handoff/r10-sav-reasons", repo=str(WT),
                              ref="origin/main", fetch=False) == 0)
    check("live: nonexistent ref -> 0",
          gp.derived_priority("handoff/r10-sav-reasons", repo=str(WT),
                              ref="refs/review/does-not-exist", fetch=False) == 0)
    # malformed env with a listed branch: the env is skipped and the DERIVED
    # answer (1) is returned -- record the actual behaviour.
    got = gp.priority_for_branch("handoff/r10-sav-reasons", repo=str(WT),
                                 ref=live_ref, fetch=False,
                                 env={gp.PRIORITY_ENV: "junk"})
    check("malformed env on a listed branch falls through to derived 1 (documented skip)",
          got == 1, f"got={got}")

# throwaway repo: malformed / empty critical-path file -> 0
with tempfile.TemporaryDirectory() as td:
    repo = Path(td) / "repo"
    (repo / "dev" / "programme" / "rosters").mkdir(parents=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "p", "GIT_AUTHOR_EMAIL": "p@x",
           "GIT_COMMITTER_NAME": "p", "GIT_COMMITTER_EMAIL": "p@x",
           "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}

    def git(*a):
        subprocess.run(["git", "-C", str(repo), *a], check=True, env=env,
                       capture_output=True)

    git("init", "-q", "-b", "main")
    (repo / "dev/programme/rosters/wave-r10-groups.json").write_text(
        json.dumps({"groups": [{"group": "R10-CRIT", "resume": {"branch": "handoff/r10-crit"}}]}))
    cp = repo / "dev/programme/rosters/critical-path.json"
    cp.write_text(json.dumps({"at": "x", "critical": ["R10-CRIT"]}))
    git("add", "-A"); git("commit", "-q", "-m", "ok")
    good = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, env=env).stdout.strip()
    check("throwaway: listed -> 1", gp.derived_priority("handoff/r10-crit", repo=str(repo),
                                                        ref=good, fetch=False) == 1)
    for label, text in (("empty list", '{"critical": []}'),
                        ("non-list", '{"critical": "R10-CRIT"}'),
                        ("non-string item", '{"critical": [1]}'),
                        ("not json", "not json"),
                        ("no critical key", '{"at": "x"}')):
        cp.write_text(text)
        git("add", "-A"); git("commit", "-q", "-m", label)
        sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                             capture_output=True, text=True, env=env).stdout.strip()
        check(f"throwaway: {label} -> 0",
              gp.derived_priority("handoff/r10-crit", repo=str(repo), ref=sha, fetch=False) == 0)

# constants arithmetic
check("aging window between the pool floor and the lease",
      g.SLOT_MIN_SECONDS < g.PRIORITY_AGING_SECONDS < g.LEASE_SECONDS,
      f"{g.SLOT_MIN_SECONDS} < {g.PRIORITY_AGING_SECONDS} < {g.LEASE_SECONDS}")
check("PRIORITY_MAX is 2 (aging lands at the top band)", g.PRIORITY_MAX == 2,
      f"PRIORITY_MAX={g.PRIORITY_MAX}")

print(f"SUMMARY {sum(1 for r in ROWS if r)}/{len(ROWS)} checks passed")
sys.exit(0 if all(ROWS) else 1)
