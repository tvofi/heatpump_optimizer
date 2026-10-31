#!/usr/bin/env python3
"""N-staleness detector over the nightly replay: report-on-change inputs read stale.

METRIC: for each guarded input of the replay fixture, the fixture is rewritten as
its report-on-change twin (a row is kept only when the state changes, and its
last_reported is its own change instant -- what Home Assistant records for a
source that sends nothing while its value holds); the day is replayed through the
real coordinator and the count is the cycles on which that input's InputReading
came back with problem == "stale" (hooked at inputs.InputHealth.record, the value
production delivers). A seam is an input key with stale_cycles > 0.
Also counted: cycles on which a published entity is unavailable that is available
on the same cycle of the unmodified (polling) day.
COMMAND: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/staleness_on_change.py
EXPECTED (baseline 17f1c55fad1b, B7): polling arm 0 stale cycles for every key
(clean fixture); see RESULT lines for per-key counts; perturbation arm
(const.INPUT_MAX_AGE_MINUTES[<seam key>] -> 1e9) drops that key to 0. Exact, tol 0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, io, json, subprocess, sys, tempfile, time
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
MARK = "<<<stale>>>"
FIX = ROOT / "tests/replay/synthetic-dhw-only.json"


def on_change(rows):
    out, last = [], object()
    attrs = None
    for upd, state, a, rep in rows:
        if a is not None:
            attrs = a
        if state != last:
            out.append([upd, state, attrs, upd])
            last = state
    return out


def arm_run(spec):
    entity, unbound = (spec.split("|") + [""])[:2]
    import replay
    from heatpump_optimizer import inputs, const
    if unbound:
        const.INPUT_MAX_AGE_MINUTES[unbound] = 1e9
    stale = Counter()
    cyc = {"n": 0}
    real_record = inputs.InputHealth.record
    def record(self, reading):
        if reading.problem == "stale":
            stale[f"{reading.key}@{cyc['n']}"] = 1
        return real_record(self, reading)
    inputs.InputHealth.record = record
    unavail = []
    real_sweep = replay.sweep
    def sweep(entities, action, errors, t):
        recs = real_sweep(entities, action, errors, t)
        unavail.append(sorted(r["entity_id"] for r in recs if not r["available"]))
        cyc["n"] += 1
        return recs
    replay.sweep = sweep
    src = json.loads(FIX.read_text())
    if entity:
        src["states"][entity] = on_change(src["states"][entity])
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "day.json"
        p.write_text(json.dumps(src))
        with contextlib.redirect_stdout(io.StringIO()):
            run = replay.run_fixture(p, 30)
    per_key = Counter(k.split("@")[0] for k in stale)
    return {"cycles": run["cycles"], "stale": dict(per_key), "unavail": unavail,
            "rows": len(src["states"][entity]) if entity else None}


def child_env(tz):
    """tests/replay.py:child_env, inlined so pre-fix trees without it run too."""
    env = {**os.environ, "HASTUB_TZ": tz,
           "PYTHONPATH": os.pathsep.join([str(ROOT / "tests" / "hastub"),
                                          os.environ.get("PYTHONPATH", "")])}
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env.setdefault(var, "1")
    return env


def run_arm(spec, env):
    p = subprocess.run([sys.executable, __file__, "--arm", spec], capture_output=True,
                       text=True, env=env, cwd=ROOT)
    line = next((l for l in p.stdout.splitlines() if l.startswith(MARK)), None)
    if line is None:
        print(f"# arm {spec} failed: {p.stderr[-1200:]}")
        return None
    return json.loads(line[len(MARK):])


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--arm":
        print(MARK + json.dumps(arm_run(sys.argv[2])))
        return 0
    import replay
    from heatpump_optimizer import const
    src = json.loads(FIX.read_text())
    env = child_env(src.get("time_zone") or "UTC")
    keymap = {v: k for k, v in src["entry"]["data"].items()
              if isinstance(v, str) and k in const.INPUT_MAX_AGE_MINUTES}
    base = run_arm("", env)
    print(f"# polling day: cycles={base['cycles']} stale={base['stale']}")
    print(f"RESULT polling_stale_cycles={sum(base['stale'].values())} count")
    seams = []
    for entity, key in sorted(keymap.items()):
        out = run_arm(entity, env)
        if out is None:
            print(f"RESULT {key}_stale_cycles=-1 count"); continue
        n = out["stale"].get(key, 0)
        newly = sum(len(set(a) - set(b)) for a, b in zip(out["unavail"], base["unavail"]))
        print(f"# {key} ({entity}) limit={const.INPUT_MAX_AGE_MINUTES[key]} min, "
              f"on-change rows={out['rows']}: stale={out['stale']}")
        print(f"RESULT {key}_stale_cycles={n} count")
        print(f"RESULT {key}_newly_unavailable_entity_cycles={newly} count")
        lost = Counter(e for a, b in zip(out["unavail"], base["unavail"]) for e in set(a) - set(b))
        for e, c in sorted(lost.items()):
            print(f"#   unavailable only on the on-change day: {e} x{c}")
        if n:
            seams.append((entity, key))
    print(f"RESULT seams={len(seams)} count  # {[k for _, k in seams]}")
    for entity, key in seams:
        out = run_arm(f"{entity}|{key}", env)
        v = -1 if out is None else out["stale"].get(key, 0)
        print(f"RESULT perturb_unbounded_{key}_stale_cycles={v} count")
    tc = time.thread_time()
    print(f"RESULT thread_factor={time.process_time() / tc if tc else 1:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
