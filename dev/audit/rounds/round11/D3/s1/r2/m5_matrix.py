#!/usr/bin/env python3
"""D3-s1 M5 (b): the kill-overlap matrix, with no early stop.

prescreen.py's fast drive plus its `complete` drive run every closure driver
of tests/mutation_table.py's default set on a mutant. The gate runs more:
edge.py, backtest.py and stress.py (dropped from the pre-screen by the brief),
and the node card scripts (card.mjs after plan_view.py writes the payload it
reads, card_drift.mjs <ref>); golden.py is the non-drift path. This harness
drives those EXTRA scripts on each matrix mutant, no early stop, and `table`
merges them with the prescreen/complete rows into one (mutant x script) matrix:
K killed, s survived, r reach-skipped (the traced baseline never executes the
line), - not in the script's closure, ? not driven.

Metric: per script, mutants killed; per mutant, killers; duplicate kills
(mutants killed by >=2 scripts) and sole kills (a script is the only killer).
Kill rule: tests/mutation_table.py:killed (red AND more failing checks than the
same script's unmutated run on this tree).
Instrumented symbol: mutation_table.killed / failing_count over each driven
production line (tests/mutation_table.py inventory site or R10 sample line).
Perturbation: `drive --null` drives the comment-only null control
(mutation_table.null_for) through the same scripts: it must be killed by none.

Run (seat worktree root, PYTHONPATH=tests/hastub):
  python3 dev/audit/rounds/round11/D3/s1/r2/m5_matrix.py baseline
  python3 dev/audit/rounds/round11/D3/s1/r2/m5_matrix.py drive --keys FILE [--no-stress] [--null]
  python3 dev/audit/rounds/round11/D3/s1/r2/m5_matrix.py table --keys FILE
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64, shared.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "dev/audit/rounds/round11/D3/s1")
import mutation_table as mt  # noqa: E402
import prescreen as ps  # noqa: E402

HERE = Path(__file__).resolve().parent
S1 = HERE.parent
STATE = S1 / "state"
OUT = STATE / "results" / "matrix_extra"
BASE = STATE / "matrix_base.json"
REF = "HEAD^1"
EXTRA = ["tests/edge.py", "tests/backtest.py", "tests/golden.py",
         "tests/card.mjs", "tests/card_drift.mjs", "tests/stress.py"]
TREE = Path(tempfile.gettempdir()) / "d3s1-workers" / "w8"
LOCK_LABEL = "D3-s1-r11"


def tree() -> Path:
    if not (TREE / ".git").exists():
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(TREE), "HEAD"],
                       cwd=mt.ROOT, check=True)
    return TREE


def cmd_for(s: str):
    node = shutil.which("node") or "node"
    if s == "tests/card_drift.mjs":
        return [node, s, REF], {}
    if s.endswith(".mjs"):
        return [node, s], {}
    if s in ("tests/stress.py", "tests/golden.py"):
        return [sys.executable, s], {"GOLDEN_REF": REF}
    return [sys.executable, s], {}


def run(s: str, t: Path, timeout: int = 7200) -> mt.ScriptRun:
    cmd, extra = cmd_for(s)
    env = {**os.environ, "PYTHONPATH": "tests/hastub", **extra}
    t0 = time.monotonic()
    lease = s == "tests/stress.py"
    if lease:
        subprocess.run([sys.executable, "tests/gate_lock.py", "take", "--label", LOCK_LABEL],
                       cwd=mt.ROOT, capture_output=True)
    try:
        if s.endswith(".mjs"):
            # the card scripts read the payload plan_view.py writes from this tree
            subprocess.run([sys.executable, "tests/plan_view.py"], cwd=t, env=env,
                           capture_output=True, timeout=timeout)
        p = subprocess.run(cmd, cwd=t, env=env, capture_output=True, text=True, timeout=timeout)
        r = mt.ScriptRun(p.returncode, 0, time.monotonic() - t0, p.stdout, p.stderr)
        return r._replace(failed=mt.failing_count(r))
    except subprocess.TimeoutExpired:
        return mt.ScriptRun(mt.TIMEOUT_RC, 0, time.monotonic() - t0, "", "timeout", True)
    finally:
        if lease:
            subprocess.run([sys.executable, "tests/gate_lock.py", "release", "--label", LOCK_LABEL],
                           cwd=mt.ROOT, capture_output=True)


def cmd_baseline(a) -> int:
    t = tree()
    base = json.loads(BASE.read_text()) if BASE.exists() else {}
    for s in EXTRA:
        if s in base or (a.no_stress and s == "tests/stress.py"):
            continue
        r = run(s, t)
        base[s] = ps.to_json(r)
        BASE.write_text(json.dumps(base))
        print(f"BASELINE {s} rc={r.rc} failed={r.failed} wall={r.seconds:.1f}s", flush=True)
    return 0


def mutants(keys_file: str) -> list[tuple[str, dict]]:
    want = [k.strip() for k in Path(keys_file).read_text().split() if k.strip()]
    found = {}
    for sub in ("complete", "pre", "c2", "c3c6"):
        for p in (STATE / "results" / sub).glob("*.json"):
            if p.stem in want and p.stem not in found:
                found[p.stem] = json.loads(p.read_text())["mutant"]
    return [(k, found[k]) for k in want if k in found]


def cmd_drive(a) -> int:
    t = tree()
    base = json.loads(BASE.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    clos = mt.load_closures()
    todo = mutants(a.keys) if not a.null else [
        ("null", mt.null_for([{"file": r} for r in ps.RELS]))]
    for k, m in todo:
        dest = OUT / (k + ".json")
        prior = json.loads(dest.read_text()) if dest.exists() else {"mutant": m, "runs": {}}
        path = t / m["file"]
        original = path.read_text()
        lines = original.splitlines(True)
        assert lines[m["line"] - 1].rstrip("\n") == m["old"], m
        lines[m["line"] - 1] = m["new"] + "\n"
        try:
            path.write_text("".join(lines))
            for s in EXTRA:
                if s in prior["runs"] or s not in base:
                    continue
                if (STATE / "STOP").exists():
                    return 0
                if m["file"] not in clos.get(s, ()):
                    prior["runs"][s] = {"not_in_closure": True}
                    continue
                r = run(s, t)
                j = ps.to_json(r)
                j["killed"] = mt.killed(s, r, ps.from_json(base[s]))
                prior["runs"][s] = j
                dest.write_text(json.dumps(prior))
                print(f"{k} {s} killed={j['killed']} rc={r.rc} wall={r.seconds:.1f}s", flush=True)
        finally:
            path.write_text(original)
    return 0


def cmd_table(a) -> int:
    rows = {}
    for k, m in mutants(a.keys):
        cells = {}
        comp = STATE / "results" / "complete" / (k + ".json")
        src = None
        if comp.exists():
            src = json.loads(comp.read_text())
        else:
            for sub in ("pre", "c2", "c3c6", "full"):
                p = STATE / "results" / sub / (k + ".json")
                if p.exists():
                    src = json.loads(p.read_text())
                    break
        if src:
            for s in src.get("skipped", []):
                cells[s] = "r"
            for s, j in src["runs"].items():
                cells[s] = "K" if j.get("killed") else "s"
            for s in src.get("deferred_slow", []) + src.get("relaxed_skipped", []):
                cells.setdefault(s, "?")
        ex = OUT / (k + ".json")
        if ex.exists():
            for s, j in json.loads(ex.read_text())["runs"].items():
                cells[s] = "-" if j.get("not_in_closure") else ("K" if j.get("killed") else "s")
        rows[k] = (m, cells)
    scripts = sorted({s for _, c in rows.values() for s in c})
    kills = Counter()
    sole = Counter()
    dup = 0
    unknown = 0
    for k, (m, c) in rows.items():
        ks = [s for s in scripts if c.get(s) == "K"]
        unknown += sum(1 for s in scripts if c.get(s) in (None, "?"))
        for s in ks:
            kills[s] += 1
        if len(ks) >= 2:
            dup += 1
        if len(ks) == 1:
            sole[ks[0]] += 1
        print(f"{k}\t{m['file'].rsplit('/', 1)[-1]}:{m['line']}\t{m['kind']}\t"
              + "".join(c.get(s, "?") for s in scripts) + "\t" + ",".join(ks))
    print("scripts: " + " ".join(f"{i}={s.rsplit('/', 1)[-1]}" for i, s in enumerate(scripts)))
    for s in scripts:
        print(f"RESULT kills[{s}]={kills[s]} sole={sole[s]}")
    print(f"RESULT mutants={len(rows)} duplicate_killed={dup} undriven_cells={unknown}")
    print(f"RESULT scripts_with_no_sole_kill={sum(1 for s in scripts if not sole[s])}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("baseline", "drive", "table"))
    ap.add_argument("--keys")
    ap.add_argument("--no-stress", action="store_true")
    ap.add_argument("--null", action="store_true")
    a = ap.parse_args()
    rc = {"baseline": cmd_baseline, "drive": cmd_drive, "table": cmd_table}[a.cmd](a)
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return rc


if __name__ == "__main__":
    sys.exit(main())
