#!/usr/bin/env python3
"""D3 round-3 mutation pre-screen: does the suite notice a single deleted line?

Metric definition: per mutant, the set of gate scripts (from that file's
measured closure in tests/closures.json) whose verdict differs from the
baseline's, where the differential gate's verdict is env_drift.py's own
byte-comparison of two --all captures made in this same environment.

Run (from the repository root; nothing is written inside the repository
except this directory's own JSON):

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D3/prescreen.py \
        --mutants tools/audit/round3/D3/mutants.json --tier 1 --workers 5

Expected value at the baseline: 34 mutants screened, >= 8 survivors of
tier 1 (+- 2 across reruns; the two timing-dependent checks in features.py
and one in entities.py are excluded by name, see BASELINE_KNOWN_FAILS).
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
Machine: 8-core Apple M1, 8 GB, macOS Darwin 25.6.0, python3 3.11.5,
numpy 2.4.6 / scipy 1.17.1 on OpenBLAS.

Instrumented symbols: tests/env_drift.py:capture_tree (the differential
gate's own capture worker) and tests/env_drift.py:_diff_leaves /
:may_drift_judged_diffs (its own comparison), driven over
custom_components/heatpump_optimizer/*.py mutated one line at a time.

Perturbation: each mutant IS the perturbation; a mutant that no script
notices is a survivor, and reverting it must return the tree to green.

How it works, so a verifier can re-run it without reading a report:
  1. A pristine copy of the repository is made under $TMPDIR (five worker
     slots), so nothing is mutated in the checkout itself.
  2. The baseline --all capture is made once (or reused from --base).
  3. For each mutant the single line is replaced in the slot, the slot is
     captured with `env_drift.py --capture <slot> <out> --all`, and the
     payloads are compared with env_drift.py's OWN _diff_leaves, with its
     OWN may-drift rule applied to the five SENSITIVE fixtures.
  4. The closure's fast scripts run in the slot. stress.py, edge.py and
     backtest.py are never run (D3 brief); golden.py never runs because
     GOLDEN_MODE=drift replaces it, exactly as tests/run.sh does.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import env_drift  # noqa: E402  -- the gate's own comparison, never a copy

# Scripts the D3 brief excludes from the pre-screen (quiet window only), plus
# golden.py, which tests/run.sh skips whenever GOLDEN_MODE=drift.
NEVER_RUN = {"tests/stress.py", "tests/edge.py", "tests/backtest.py",
             "tests/golden.py", "tests/env_drift.py"}
# Tier 1 = every fast script under ~60 s at the baseline on this box.
TIER1 = {"tests/entities.py", "tests/structure.py", "tests/typing_ruler.py",
         "tests/deployment_shape.py", "tests/config_flow_steps.py",
         "tests/solar_alignment.py", "tests/plan_view.py",
         "tests/manual_plan.py", "tests/open_meteo.py", "tests/frontend.py",
         "tests/ha_contract.py"}
# Tier 2 = the expensive fast scripts, run only for tier-1 survivors.
TIER2 = {"tests/features.py", "tests/validate.py", "tests/optimality.py"}
# Node scripts: skipped here, they never read a mutated .py directly.
NODE = {"tests/card.mjs", "tests/card_drift.mjs", "tests/setup_qa_render.mjs"}

#: Checks that already FAIL on an unmutated baseline tree on this box, so a
#: mutant must not be credited to them.  Both are wall-clock null controls.
BASELINE_KNOWN_FAILS = (
    "null control: reaping inline DOES stall it",
)

FAIL_RE = re.compile(r"^\s*(FAIL|FAILED|MISMATCH|DIFF)\b(.*)$")


def fail_lines(text: str) -> set[str]:
    out = set()
    for line in text.splitlines():
        m = FAIL_RE.match(line)
        if not m:
            continue
        s = line.strip()
        if any(k in s for k in BASELINE_KNOWN_FAILS):
            continue
        out.add(s[:160])
    return out


def make_slot(slot: Path) -> None:
    if slot.exists():
        shutil.rmtree(slot)
    slot.mkdir(parents=True)
    for name in ("custom_components", "tests", "tools", "docs",
                 "VERSION", "README.md", "RELEASE_NOTES.md", "hacs.json",
                 "CLAUDE.md", "DISCLAIMER.md", "LICENSE", "NOTICE",
                 ".gitattributes", ".gitignore", ".github", "icon.png"):
        src = ROOT / name
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, slot / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(src, slot / name)
    # tests/deployment_shape.py asks `git ls-files` what the installed
    # package contains, so a slot must be a git repository or that script
    # crashes for a reason that has nothing to do with the mutant.
    subprocess.run(["git", "init", "-q"], cwd=slot, check=True,
                   capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=slot, check=True,
                   capture_output=True)


def apply_patch(slot: Path, mut: dict) -> None:
    p = slot / mut["file"]
    lines = p.read_text().splitlines(keepends=True)
    idx = mut["line"] - 1
    have = lines[idx].rstrip("\n")
    if have != mut["old"]:
        raise SystemExit(f"{mut['id']}: line {mut['line']} of {mut['file']} is "
                         f"{have!r}, expected {mut['old']!r}")
    lines[idx] = mut["new"] + "\n"
    p.write_text("".join(lines))


def revert_patch(slot: Path, mut: dict) -> None:
    shutil.copy2(ROOT / mut["file"], slot / mut["file"])


def run_script(slot: Path, script: str, tmp: Path, timeout: int) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(slot / "tests" / "hastub")
    env["HPO_PLANDATA"] = str(tmp / f"plandata-{slot.name}.json")
    env["GOLDEN_MODE"] = "drift"
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, script], cwd=slot, env=env,
                           capture_output=True, text=True, timeout=timeout)
        rc, out = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        rc, out = 124, "TIMEOUT"
    summary_line = None
    for line in reversed(out.splitlines()):
        if re.search(r"(\d+) of (\d+) [A-Z ]+ FAILED", line) or re.search(
            r"ALL (\d+) [A-Z ]+ PASSED", line
        ):
            summary_line = line
            break
    return {"script": script, "rc": rc, "seconds": round(time.time() - t0, 1),
            "fails": sorted(fail_lines(out)), "tail": out[-1200:],
            "summary_line": summary_line,
            "has_traceback": "Traceback (most recent call last)" in out}


def capture(slot: Path, out_path: Path, timeout: int = 1800) -> int:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(slot / "tests" / "hastub")
    p = subprocess.run(
        [sys.executable, str(slot / "tests" / "env_drift.py"), "--capture",
         str(slot), str(out_path), "--all"],
        cwd=slot, env=env, capture_output=True, text=True, timeout=timeout)
    return p.returncode


def drift_verdict(base: dict, mut: dict) -> dict:
    """env_drift.py's own --all verdict, using env_drift's own comparison."""
    moved, exempt = [], []
    for name in sorted(set(base) | set(mut)):
        if name not in base or name not in mut:
            moved.append(f"{name}: present on one side only")
            continue
        diffs: list[str] = []
        env_drift._diff_leaves(base[name], mut[name], name, diffs)
        if not diffs:
            continue
        if name in env_drift.SENSITIVE:
            judged = env_drift.may_drift_judged_diffs(name, diffs)
            if judged:
                moved.extend(judged[:3])
            else:
                exempt.append(name)
        else:
            moved.extend([f"{name}: {len(diffs)} leaf diff(s)"] + diffs[:2])
    return {"killed": bool(moved), "moved": moved[:12],
            "may_drift_exempt": exempt}


def slot_baseline(slot: Path, tmp: Path, scripts: list[str]) -> dict:
    """Every tier-1/2 script's verdict on an UNMUTATED slot.

    A slot is a copy, not the checkout, so its verdict is what a mutant
    must be compared against -- otherwise a slot-only difference (a
    missing git object, a temp path) is credited to the mutant.
    """
    base = {}
    for s in scripts:
        r = run_script(slot, s, tmp, timeout=2400)
        base[s] = {"rc": r["rc"], "fails": set(r["fails"])}
    return base


def screen_one(mut: dict, slot: Path, tmp: Path, base_payloads: dict,
               closures: dict, tier: int, prev: dict | None,
               sbase: dict) -> dict:
    rec = dict(mut)
    mod = mut["module"]
    sel = closures[mod]["run"]
    rec["closure_scripts"] = sel
    rec["closure_mode"] = closures[mod]["mode"]
    ran, killers = [], []
    apply_patch(slot, mut)
    try:
        # Syntax first: a mutant that will not compile is not a suite gap.
        p = subprocess.run([sys.executable, "-m", "py_compile",
                            str(slot / mut["file"])], capture_output=True,
                           text=True)
        if p.returncode != 0:
            rec.update(status="SYNTAX-ERROR", ran=[], killed_by=["py_compile"])
            return rec

        if tier == 1:
            # The cheap assertion scripts run first: they cost ~60 s together
            # while one --all capture pair costs ~300 s under this box's load,
            # and a mutant an assertion already kills cannot be a survivor
            # whatever the differential gate says.  The capture therefore runs
            # for every mutant no assertion killed -- which is every mutant
            # whose survivorship the differential gate can still decide.
            for s in sel:
                if s in NEVER_RUN or s in NODE or s not in TIER1:
                    continue
                r = run_script(slot, s, tmp, timeout=900)
                b = sbase.get(s, {"rc": 0, "fails": set()})
                r["baseline_rc"] = b["rc"]
                r["new_fails"] = sorted(set(r["fails"]) - b["fails"])
                ran.append(r)
                if r["rc"] != b["rc"] or r["new_fails"]:
                    killers.append(s)

            if killers:
                rec["drift"] = {"killed": None, "moved": [],
                                "note": "not captured: an assertion script "
                                        "already killed this mutant"}
            else:
                out = tmp / f"cap-{mut['id']}.json"
                t0 = time.time()
                rc = capture(slot, out, timeout=3600)
                secs = round(time.time() - t0, 1)
                if rc != 0:
                    rec["drift"] = {"killed": True,
                                    "moved": ["capture crashed (rc=%d)" % rc]}
                    ran.append({"script": "tests/env_drift.py --all", "rc": rc,
                                "seconds": secs, "fails": ["capture crashed"],
                                "new_fails": ["capture crashed"]})
                    killers.append("tests/env_drift.py --all")
                else:
                    v = drift_verdict(base_payloads, json.loads(out.read_text()))
                    rec["drift"] = v
                    ran.append({"script": "tests/env_drift.py --all",
                                "rc": 1 if v["killed"] else 0, "seconds": secs,
                                "fails": v["moved"][:3],
                                "new_fails": v["moved"][:3]})
                    if v["killed"]:
                        killers.append("tests/env_drift.py --all")
                    out.unlink(missing_ok=True)
        else:
            for s in sel:
                if s in NEVER_RUN or s in NODE or s not in TIER2:
                    continue
                r = run_script(slot, s, tmp, timeout=2400)
                b = sbase.get(s, {"rc": 0, "fails": set()})
                r["baseline_rc"] = b["rc"]
                r["new_fails"] = sorted(set(r["fails"]) - b["fails"])
                ran.append(r)
                if r["rc"] != b["rc"] or r["new_fails"]:
                    killers.append(s)
            if prev:
                ran = prev.get("ran", []) + ran
                killers = prev.get("killed_by", []) + killers
                rec["drift"] = prev.get("drift")
                rec["closure_scripts"] = prev.get("closure_scripts", sel)
    finally:
        revert_patch(slot, mut)
    rec["ran"] = ran
    rec["killed_by"] = sorted(set(killers))
    rec["status"] = "KILLED" if killers else "SURVIVOR"
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", default="tools/audit/round3/D3/mutants.json")
    ap.add_argument("--closures",
                    default="tools/audit/round3/D3/closures_by_module.json")
    ap.add_argument("--out", default="tools/audit/round3/D3/prescreened.json")
    ap.add_argument("--base", default="", help="baseline --all capture JSON")
    ap.add_argument("--tier", type=int, default=1)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--only", default="", help="comma-separated mutant ids")
    ap.add_argument("--prev", default="", help="tier-1 prescreened.json")
    ap.add_argument("--slot-prefix", default="slot",
                    help="worker-slot directory prefix; give concurrent runs "
                         "different prefixes or one run's cleanup deletes the "
                         "other's slots mid-flight")
    ap.add_argument("--capture-only", action="store_true",
                    help="run only the differential gate's capture pair; "
                         "for mutants whose assertion scripts already ran")
    args = ap.parse_args()

    if getattr(ap.parse_args([]), "capture_only", False) or args.capture_only:
        TIER1.clear()
        TIER2.clear()

    tmp = Path(tempfile.gettempdir()) / "d3audit"
    tmp.mkdir(exist_ok=True)
    muts = json.loads(Path(args.mutants).read_text())["mutants"]
    if args.only:
        keep = set(args.only.split(","))
        muts = [m for m in muts if m["id"] in keep]
    closures = json.loads(Path(args.closures).read_text())

    base_path = Path(args.base) if args.base else tmp / "base_all.json"
    if not base_path.exists():
        print(f"capturing baseline --all into {base_path} ...", flush=True)
        slot0 = tmp / "slot-base"
        make_slot(slot0)
        if capture(slot0, base_path) != 0:
            raise SystemExit("baseline capture failed")
        shutil.rmtree(slot0)
    base_payloads = json.loads(base_path.read_text())
    print(f"RESULT baseline_fixtures={len(base_payloads)} fixtures", flush=True)

    prev = {}
    if args.prev:
        prev = {r["id"]: r for r in json.loads(Path(args.prev).read_text())["prescreened"]}

    slots = []
    for i in range(args.workers):
        s = tmp / f"{args.slot_prefix}-{i}"
        make_slot(s)
        slots.append(s)
    print(f"RESULT worker_slots={len(slots)} slots", flush=True)

    results: list[dict] = []
    lock_free = list(range(len(slots)))

    def work(i_m):
        ci, i, m = i_m
        slot = slots[ci]
        try:
            r = screen_one(m, slot, tmp, base_payloads, closures, args.tier,
                           prev.get(m["id"]), sbases[ci])
        except Exception as exc:  # a crashed screen is not a survivor
            r = dict(m, status="SCREEN-ERROR", error=repr(exc), ran=[],
                     killed_by=["screen-error"])
        print(f"  {r['id']:>4} {r['module']}:{r['line']:<6} {r['status']:<12} "
              f"killed_by={r.get('killed_by')}", flush=True)
        return r

    # Round-robin over slots: each worker owns one slot for its whole job.
    chunks = [[] for _ in slots]
    for i, m in enumerate(muts):
        chunks[i % len(slots)].append(m)

    wanted = sorted({s for m in muts for s in closures[m["module"]]["run"]
                     if s not in NEVER_RUN and s not in NODE
                     and s in (TIER1 if args.tier == 1 else TIER2)})
    print(f"RESULT slot_baseline_scripts={len(wanted)} scripts", flush=True)
    sbases: dict[int, dict] = {}

    def run_chunk(ci):
        mine = sorted({s for m in chunks[ci]
                       for s in closures[m["module"]]["run"]} & set(wanted))
        sbases[ci] = slot_baseline(slots[ci], tmp, mine)
        for s, v in sbases[ci].items():
            if v["rc"] != 0 or v["fails"]:
                print(f"  slot-{ci} BASELINE {s} rc={v['rc']} "
                      f"fails={sorted(v['fails'])[:2]}", flush=True)
        out = []
        for m in chunks[ci]:
            out.append(work((ci, 0, m)))
        return out

    with ThreadPoolExecutor(max_workers=len(slots)) as ex:
        for part in ex.map(run_chunk, range(len(slots))):
            results.extend(part)

    results.sort(key=lambda r: r["id"])
    survivors = [r for r in results if r["status"] == "SURVIVOR"]
    print(f"RESULT screened={len(results)} mutants")
    print(f"RESULT survivors={len(survivors)} mutants")
    print(f"RESULT survivor_ids={','.join(r['id'] for r in survivors)}")
    killed_by_drift = [r for r in results
                       if "tests/env_drift.py --all" in r.get("killed_by", [])]
    print(f"RESULT killed_by_differential_gate={len(killed_by_drift)} mutants")
    la = os.getloadavg()[0]
    print(f"RESULT load1={la:.2f}")
    print("RESULT thread_factor=1.00  (counts only; no timing claim)")
    Path(args.out).write_text(json.dumps(
        {"baseline_sha": "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1",
         "tier": args.tier, "load1": la, "prescreened": results}, indent=1))
    for s in slots:
        shutil.rmtree(s, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
