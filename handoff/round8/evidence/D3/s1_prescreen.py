#!/usr/bin/env python3
"""s1_prescreen.py -- D3 seat s1: seeded, weighted mutant pool over coordinator.py,
optimizer.py, thermal_model.py, sysid.py, pre-screened against each mutant's
MEASURED closure (tests/closures.json) plus env_drift.py --all <baseline>.

Metric: per mutant, the verdict KILLED(<script>/<check>) or LIVES, where a script
kills when its exit status differs from the UNMUTATED tree's or its `N of M ...
FAILED` count rises (tests/mutation_table.py's rule; FAIL-line text is NOT
compared, because entities.py's negative-control rails print run-varying detail).
The unmutated baseline is run with the production file restored. Key: the
scripts' own verdicts on the delivered production behaviour.

Mutants come from tests/mutation_table.py:candidates() (the gate's six
operators), restricted to sites with no recorded disposition in
tests/mutation_budgets.json, sampled without replacement by weight
(KIND_W x consequence class, below), SEED fixed, at most PER_MODULE per module.

Scripts per mutant: the closure's scripts minus stress.py, edge.py, backtest.py
(D3 brief step 2), minus golden.py (its default mode IS the env_drift step) and
card_drift.mjs (it compares two card sources over ONE payload, so it cannot see
a Python mutant; the gate also skips it when GOLDEN_REF is HEAD), cheapest
recorded seconds first; card.mjs runs right after plan_view.py (payload order);
tools/audit/round8/D3/s1_envdrift.py (env_drift --all <baseline>) runs last,
under `flock /home/claude/audit-r8/envdrift.lock`. First kill stops a mutant
unless --no-stop.

The production file is restored in a finally block (and on SIGTERM); the tree is
byte-identical afterwards (checked and printed as RESULT restored=1).

Commands (tree root, thread pin set by the harness itself):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_prescreen.py --list
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_prescreen.py --run 1,2,3
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_prescreen.py --run 0 (null: no mutation)
Expected: --list is exact and reproducible (seed); --run 0 LIVES everywhere.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud
container shared with ~13 seats (wall numbers provisional).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import contextlib
import ast
import hashlib
import json
import random
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

BASE_SHA = "cdf82daabcfe3777d98b31489f36df5555ec9d82"
SEED = 20260923
PER_MODULE = 4
MODULES = ["coordinator", "optimizer", "thermal_model", "sysid"]
KIND_W = {"GUARD_OFF": 3.0, "CLAMP_DROP": 3.0, "BOOLOP": 2.0, "RAISE_DEL": 2.0,
          "RETURN_DEL": 1.5, "CONST": 2.0}
# consequence classes by line text: money/comfort/safety terms up, logging and
# diagnostics down. First matching class wins.
CLASSES = [
    ("log", 0.1, re.compile(r"_LOGGER|\blog\w*\(|warning\(|debug\(|narrat|diagnos", re.I)),
    ("money_comfort", 3.0, re.compile(r"price|cost|tariff|fee|comfort|setpoint|target|"
                                      r"indoor|t_in|legion|dhw|tank|cop|power|kw|"
                                      r"flow|lift|bound|floor|ceil|limit|clip|clamp", re.I)),
    ("state_model", 2.0, re.compile(r"stale|valid|finite|nan|none|fit|learn|sysid|"
                                    r"horizon|slot|step|tau|ua|capacity", re.I)),
    ("other", 1.0, re.compile(r".")),
]
SKIP_SCRIPTS = {"tests/stress.py", "tests/edge.py", "tests/backtest.py",
                "tests/golden.py", "tests/card_drift.mjs", "tests/env_drift.py"}
OUT = ROOT / "tools/audit/round8/D3/s1_prescreen.jsonl"
TMP = Path("/home/claude/audit-r8/tmp/D3-s1")
_FAIL = re.compile(r"^\s*FAIL\s+(.+?)\s*$", re.M)


def weight(m):
    for name, w, rx in CLASSES:
        if rx.search(m["old"]):
            return name, KIND_W[m["kind"]] * w


def pool():
    budgets = json.loads((ROOT / "tests/mutation_budgets.json").read_text())
    disp = mt.dispositions(budgets)
    rng = random.Random(SEED)
    out = []
    for mod in MODULES:
        path = ROOT / f"custom_components/heatpump_optimizer/{mod}.py"
        cands = [c for c in mt.candidates(path)
                 if not mt.disposition_matches(disp.get(mt.triage_key(c)), c)]
        cands.sort(key=lambda c: (c["line"], c["kind"]))
        picked = []
        while len(picked) < PER_MODULE and cands:
            ws = [weight(c)[1] for c in cands]
            c = rng.choices(cands, weights=ws, k=1)[0]
            cands.remove(c)
            cls, w = weight(c)
            c = dict(c, cls=cls, w=w)
            picked.append(c)
        out.extend(sorted(picked, key=lambda c: c["line"]))
    for i, m in enumerate(out, 1):
        m["id"] = i
    return out


def closure_scripts(rel):
    raw = json.loads((ROOT / "tests/closures.json").read_text())
    cl, rec = raw["closures"], raw["recorded"]
    s = [k for k, v in cl.items() if rel in v and k not in SKIP_SCRIPTS]
    s.sort(key=lambda k: rec.get(k, {}).get("seconds", 999))
    # payload order: plan_view.py before card.mjs
    if "tests/card.mjs" in s:
        s.remove("tests/card.mjs")
        s.insert(s.index("tests/plan_view.py") + 1 if "tests/plan_view.py" in s else 0,
                 "tests/card.mjs")
    return s + ["ENVDRIFT"]


def run(script, timeout=2400):
    env = dict(os.environ, PYTHONPATH="tests/hastub",
               TMPDIR=str(TMP), HPO_PLANDATA=str(TMP / "plandata"))
    if script == "ENVDRIFT":
        env.pop("HPO_PLANDATA", None)  # HPO_* is hashed into the drift cache key
        env["LC_CTYPE"] = "C.UTF-8"
        cmd = ["flock", "/home/claude/audit-r8/envdrift.lock", sys.executable,
               "tools/audit/round8/D3/s1_envdrift.py", BASE_SHA]
    elif script.endswith(".mjs"):
        cmd = ["node", script]
    else:
        cmd = [sys.executable, script]
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=timeout)
        rc, so, se = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        rc, so, se = 124, "", "TIMEOUT"
    if script == "ENVDRIFT":
        (TMP / f"envdrift_last_{int(time.time())}.log").write_text(so + "\n--stderr--\n" + se)
    hits = mt._FAILED.findall(so)
    fails = sorted(set(_FAIL.findall(so)))
    tail = [ln for ln in (so + "\n" + se).splitlines() if ln.strip()][-3:]
    return dict(rc=rc, failed=int(hits[-1][0]) if hits else 0, fails=fails,
                seconds=round(time.monotonic() - t0, 1), tail=tail)


BASEFILE = TMP / "s1_baseline_runs.json"


def baseline(script, unmutated):
    cache = json.loads(BASEFILE.read_text()) if BASEFILE.exists() else {}
    if script not in cache:
        with unmutated():
            cache[script] = run(script)
        BASEFILE.write_text(json.dumps(cache, indent=1))
    return cache[script]


def _names(fails):
    # check id only: detail text after two spaces carries run-varying payload
    return {f.split("  ")[0] for f in fails}


def killed(script, r, unmutated):
    """tests/mutation_table.py's rule: rc differs from the UNMUTATED tree's, or
    the `N of M ... FAILED` count rises. The baseline is always taken with the
    production file restored (`unmutated` is a context manager)."""
    if r["rc"] == 0 and script != "tests/entities.py":
        return None  # green under the mutant; recorded baseline rc=0 (closures.json)
    b = baseline(script, unmutated)
    new = sorted(_names(r["fails"]) - _names(b["fails"]))
    if r["rc"] != b["rc"]:
        return f"rc {b['rc']}->{r['rc']}: " + ("; ".join(new[:3]) or " | ".join(r["tail"]))
    if r["failed"] > b["failed"]:
        return f"failed {b['failed']}->{r['failed']}: " + "; ".join(new[:3])
    return None


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", default="")
    ap.add_argument("--no-stop", action="store_true")
    ap.add_argument("--no-envdrift", action="store_true",
                    help="stage 1: closure scripts only; survivors get ENVDRIFT via --only ENVDRIFT")
    ap.add_argument("--only", default="", help="comma list of scripts to run instead of the closure")
    a = ap.parse_args()
    TMP.mkdir(parents=True, exist_ok=True)
    P = pool()
    if a.list or not a.run:
        print(f"seed={SEED} per_module={PER_MODULE} KIND_W={KIND_W} "
              f"classes={[(n, w) for n, w, _ in CLASSES]}")
        for m in P:
            print(f"M{m['id']:02d} {m['file'].split('/')[-1]}:{m['line']} {m['kind']} "
                  f"cls={m['cls']} w={m['w']:.2f} | {m['old'].strip()[:90]}")
        print(f"RESULT pool_size={len(P)} count")
        return 0
    ids = [int(x) for x in a.run.split(",")]
    for mid in ids:
        if mid == 0:
            m = dict(id=0, file="custom_components/heatpump_optimizer/sysid.py",
                     line=0, kind="NULL", old="", new="")
        else:
            m = next(x for x in P if x["id"] == mid)
        path = ROOT / m["file"]
        before = sha(path)
        original = path.read_text()
        rec = dict(id=mid, file=m["file"], line=m["line"], kind=m["kind"],
                   old=m["old"], new=m["new"], scripts=[], verdict="LIVES")
        state = {"text": original}

        @contextlib.contextmanager
        def unmutated():
            path.write_text(original)
            try:
                yield
            finally:
                path.write_text(state["text"])

        try:
            if mid:
                lines = original.splitlines(True)
                assert lines[m["line"] - 1].rstrip("\n") == m["old"], "moved"
                lines[m["line"] - 1] = m["new"] + "\n"
                mutated = "".join(lines)
                ast.parse(mutated)
                path.write_text(mutated)
                state["text"] = mutated
            scripts = a.only.split(",") if a.only else closure_scripts(m["file"])
            if a.no_envdrift:
                scripts = [x for x in scripts if x != "ENVDRIFT"]
            for s in scripts:
                r = run(s)
                k = killed(s, r, unmutated) if s != "ENVDRIFT" else (
                    None if r["rc"] == 0 else "env_drift: " + " | ".join(r["tail"]))
                rec["scripts"].append(dict(script=s, rc=r["rc"], failed=r["failed"],
                                           seconds=r["seconds"], kill=k))
                print(f"  M{mid:02d} {s}: rc={r['rc']} {r['seconds']}s {'KILL ' + k if k else 'pass'}",
                      flush=True)
                if k:
                    rec["verdict"] = f"KILLED by {s}"
                    if not a.no_stop:
                        break
        finally:
            path.write_text(original)
            rec["restored"] = int(sha(path) == before)
        with OUT.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"RESULT M{mid:02d}_verdict={rec['verdict']}")
        print(f"RESULT M{mid:02d}_restored={rec['restored']}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    sys.exit(main())
