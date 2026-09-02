#!/usr/bin/env python3
"""D7 step 6 -- spot mutations for "this year's train": does a gate script fail when the addition is deleted?

Metric (one line): per addition, the export tree is COPIED to a private temp dir, ONE textual
mutation (MUTATIONS below: an exact anchor asserted to occur exactly once -> a replacement
that deletes the mechanism) is applied to the copy, and the gate scripts named for it run
there; detected = 1 when any script's exit status or its count of ``FAIL`` check lines rises
above the same script's value on an UNMUTATED copy run by the identical procedure first
(golden.py: the count of "DIFF <scenario>" lines; 34/55 differ at baseline on this box).
Also per addition: the count of docs/*.md + README.md files mentioning its doc anchor.
Each copy carries a one-line stub RELEASE_NOTES.md ("## v<VERSION>") because the export
deliberately omits that file and tests/entities.py:4360 aborts without it; the stub only
lets the entity checks after that line run. NOTHING in the export itself is edited.

Run:      PYTHONPATH=tests/hastub python tools/audit/round2/D7/train_mutations.py [--jobs 2] [--only id,id]
Expected: RESULT detected_<id> in {0,1} (exact, baseline c398fc84eec25fc44b60d74aae05b9a2da205884);
          ~12 min wall at --jobs 2 on the shared box (features.py ~28 s per copy).
Machine:  8-core Apple M1, 8 GB, shared audit box. Counts only; no timing is reported.
Instrumented symbol: per row (see MUTATIONS[*]["symbol"]).
Perturbation: for a row with detected=0, add a check to tests/features.py that drives the
          symbol (e.g. assert _bounds_supported_by_batch(uniform bounds) is True) -> detected
          moves UP to 1; for a row with detected=1, delete that check -> may move DOWN.
Writes:   tools/audit/round2/D7/train_mutations.json and a private temp root only.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "train_mutations.json"
PY = sys.executable
NODE = shutil.which("node")
PKG = "custom_components/heatpump_optimizer"
CARD = f"{PKG}/www/heatpump-optimizer-card.js"

PY_SCRIPTS = ["tests/features.py", "tests/entities.py", "tests/golden.py"]
CARD_SCRIPTS = ["tests/plan_view.py", "node tests/card.mjs", "tests/frontend.py"]

MUTATIONS = [
    {
        "id": "batched_gradient_gate_off",
        "addition": "batched gradient (#97) and its bounds gate (D9-01)",
        "module": f"{PKG}/optimizer.py", "symbol": "optimizer:_bounds_supported_by_batch",
        "doc_anchor": r"simulate_trajectory_batch|batched",
        "file": f"{PKG}/optimizer.py",
        "old": "    if not bounds:\n        return False\n    for lo, hi in bounds:\n        if not (np.isfinite(lo) and np.isfinite(hi)):",
        "new": "    return False  # D7 mutation: the batched jac never serves a solve\n    if not bounds:\n        return False\n    for lo, hi in bounds:\n        if not (np.isfinite(lo) and np.isfinite(hi)):",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "bounds_gate_zero_range_admitted",
        "addition": "the bounds gate's zero-range carve-out (D9-01)",
        "module": f"{PKG}/optimizer.py", "symbol": "optimizer:_bounds_supported_by_batch",
        "doc_anchor": r"zero-range|lo == hi|bounds gate",
        "file": f"{PKG}/optimizer.py",
        "old": "        if lo >= hi:\n            return False\n    return True",
        "new": "        if lo > hi:  # D7 mutation: zero-range bounds admitted to the batch\n            return False\n    return True",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "drift_cusum_never_trips",
        "addition": "the drift detector primitive (drift.py Cusum, T4a) behind the open-window, COP-health and drift gates",
        "module": f"{PKG}/drift.py", "symbol": "drift:Cusum.update",
        "doc_anchor": r"CUSUM|drift\.py",
        "file": f"{PKG}/drift.py",
        "old": "        if not self.tripped and self.stat >= self.threshold:\n            self.tripped = True",
        "new": "        if False:  # D7 mutation: the detector never trips\n            self.tripped = True",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "weekly_windows_off",
        "addition": "weekly DHW windows (weekdays/weekend selectors)",
        "module": f"{PKG}/dhw_schedule.py", "symbol": "dhw_schedule:windows_for_day",
        "doc_anchor": r"weekdays|weekend",
        "file": f"{PKG}/dhw_schedule.py",
        "old": "    if weekly is None or weekday is None:\n        return fallback\n    return weekly[max(0, min(6, int(weekday)))]",
        "new": "    return fallback  # D7 mutation: every day gets the flat fallback\n    if weekly is None or weekday is None:\n        return fallback\n    return weekly[max(0, min(6, int(weekday)))]",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "topology_catalogue_never_matches",
        "addition": "the topology catalogue (topology.py LAYOUTS / match_layout)",
        "module": f"{PKG}/topology.py", "symbol": "topology:match_layout",
        "doc_anchor": r"topology",
        "file": f"{PKG}/topology.py",
        "old": "        if expected == target and LAYOUTS[key].selectable:\n            return key, \"\"",
        "new": "        if False and LAYOUTS[key].selectable:  # D7 mutation: no drawing ever matches\n            return key, \"\"",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "wood_share_zero",
        "addition": "the wood two-tank variant (thermal_model.wood_share priority law, #40)",
        "module": f"{PKG}/thermal_model.py", "symbol": "thermal_model:wood_share",
        "doc_anchor": r"wood",
        "file": f"{PKG}/thermal_model.py",
        "old": "    if wood_temp >= flow_set:\n        return 1.0\n    if hp_temp > flow_set:\n        f_w = (hp_temp - flow_set) / (hp_temp - wood_temp)",
        "new": "    return 0.0  # D7 mutation: the valve never draws from the wood tank\n    if wood_temp >= flow_set:\n        return 1.0\n    if hp_temp > flow_set:\n        f_w = (hp_temp - flow_set) / (hp_temp - wood_temp)",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "coil_reduction_off",
        "addition": "the DHW wood-coil variant (thermal_model.dhw_coil_draw_reduction, v3.15.1)",
        "module": f"{PKG}/thermal_model.py", "symbol": "thermal_model:dhw_coil_draw_reduction",
        "doc_anchor": r"coil",
        "file": f"{PKG}/thermal_model.py",
        "old": "    if draw_kw <= 0.0:\n        return draw_kw, 0.0\n    t_in = inlet_temp + DHW_WOOD_COIL_EFFECTIVENESS * max(",
        "new": "    return draw_kw, 0.0  # D7 mutation: the coil preheats nothing\n    if draw_kw <= 0.0:\n        return draw_kw, 0.0\n    t_in = inlet_temp + DHW_WOOD_COIL_EFFECTIVENESS * max(",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "dhw_confidence_band_off",
        "addition": "the DHW confidence band (v5.2.0, coordinator._dhw_confidence_band)",
        "module": f"{PKG}/coordinator.py", "symbol": "coordinator:HeatPumpOptimizerCoordinator._dhw_confidence_band",
        "doc_anchor": r"confidence band|dhw_temp_lo|dhw_band",
        "file": f"{PKG}/coordinator.py",
        "old": "        n = len(dhw_temp)\n        if not self._dhw_accuracy.has_lead_history():\n            return [None] * n, [None] * n",
        "new": "        n = len(dhw_temp)\n        if True:  # D7 mutation: the band is never published\n            return [None] * n, [None] * n",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "pump_signals_freeze_off",
        "addition": "the Tuya heat-pump signals (v5.3.0 pump_signals.read: the offline/fault/cooling learner freeze)",
        "module": f"{PKG}/pump_signals.py", "symbol": "pump_signals:read",
        "doc_anchor": r"pump_offline|pump_fault|freeze_reason|Tuya",
        "file": f"{PKG}/pump_signals.py",
        "old": "        freeze_reason=freeze,\n    )",
        "new": "        freeze_reason=None,  # D7 mutation: the signals never freeze the learners\n    )",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "reanchor_law_off",
        "addition": "the re-anchor law (#86, coordinator._reanchor_house_heat_loss_scale)",
        "module": f"{PKG}/coordinator.py", "symbol": "coordinator:HeatPumpOptimizerCoordinator._reanchor_house_heat_loss_scale",
        "doc_anchor": r"re-anchor|reanchor",
        "file": f"{PKG}/coordinator.py",
        "old": "        if anchor is None:\n            # A pre-fix store carries no anchor: nothing to re-express,",
        "new": "        return False  # D7 mutation: the stored scale is never re-expressed\n        if anchor is None:\n            # A pre-fix store carries no anchor: nothing to re-express,",
        "scripts": PY_SCRIPTS,
    },
    {
        "id": "card_collaborator_lane_editor_removed",
        "addition": "the card collaborators (PR 5b LaneEditor of the decomposition program, #136)",
        "module": CARD, "symbol": "heatpump-optimizer-card.js:LaneEditor",
        "doc_anchor": r"LaneEditor|collaborator",
        "file": CARD,
        "old": "class LaneEditor {",
        "new": "class LaneEditor_D7_removed {",
        "scripts": CARD_SCRIPTS,
    },
]

INFRA = [
    {"id": "drift_gate_env_drift", "addition": "the drift gate (tests/env_drift.py, CI GOLDEN_MODE=drift)",
     "module": "tests/env_drift.py", "doc_anchor": r"env_drift|GOLDEN_MODE|drift mode",
     "note": "needs `git worktree add`: not executable in a git-less export; no test tests the gate"},
    {"id": "scoped_gate", "addition": "the scoped gate (tests/run.sh GATE_SCOPE=auto, tests/closure.py, closures.json)",
     "module": "tests/closure.py", "doc_anchor": r"GATE_SCOPE|closures\.json|scoped",
     "note": "probed below: `closure.py select` with and without closures.json"},
    {"id": "stress_budgets", "addition": "the stress solve-time budgets (tests/stress.py Calibration / SOLVE_BUDGET_RATIO)",
     "module": "tests/stress.py", "doc_anchor": r"budget",
     "note": "a timing guard; needs the quiet box and runs alone -- not mutated here"},
]

# Results.check prints "  FAIL <name>"; golden.py prints "  DIFF <scenario>" per changed scenario
# (34 of 55 differ at baseline on this box -- fixtures were recorded elsewhere -- so the golden
# net is the COUNT rising above the unmutated copy's, not the exit status).
FAIL_RE = re.compile(r"^\s*(FAIL|MISMATCH|DIFF)\b", re.M)


def docs_mentions(anchor: str) -> int:
    rx = re.compile(anchor, re.I)
    n = 0
    for p in list((ROOT / "docs").glob("*.md")) + [ROOT / "README.md"]:
        if rx.search(p.read_text(errors="replace")):
            n += 1
    return n


def tests_mentions(anchor: str) -> int:
    rx = re.compile(anchor, re.I)
    return sum(1 for p in (ROOT / "tests").glob("*.*")
               if p.suffix in (".py", ".mjs", ".sh") and rx.search(p.read_text(errors="replace")))


def make_copy(dst: Path) -> None:
    shutil.copytree(
        ROOT, dst,
        ignore=shutil.ignore_patterns("tools", ".git", "__pycache__", "*.pyc", ".pytest_cache"),
    )
    version = (ROOT / "VERSION").read_text().strip()
    (dst / "RELEASE_NOTES.md").write_text(f"## v{version}\n\n- D7 audit stub: the export omits this file.\n")


def apply(dst: Path, mut: dict) -> None:
    p = dst / mut["file"]
    src = p.read_text()
    n = src.count(mut["old"])
    if n != 1:
        raise SystemExit(f"{mut['id']}: anchor occurs {n} times in {mut['file']}, expected 1")
    p.write_text(src.replace(mut["old"], mut["new"]))


def run_scripts(dst: Path, scripts: list[str]) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub"
    env["HPO_PLANDATA"] = str(dst / "plandata.json")
    # HASTUB_TZ is dst_checks.py's variable (features.py sets it for that subprocess itself);
    # exporting it to every script makes features.py abort on a naive/aware datetime subtraction.
    env.pop("HASTUB_TZ", None)
    out = {}
    for s in scripts:
        if s.startswith("node "):
            if NODE is None:
                out[s] = {"exit": None, "fails": None, "note": "node not on PATH"}
                continue
            cmd = [NODE, s.split()[1], str(dst / "plandata.json")]
        else:
            cmd = [PY, s]
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=dst, env=env, capture_output=True, text=True, timeout=1500)
            text = r.stdout + r.stderr
            out[s] = {"exit": r.returncode, "fails": len(FAIL_RE.findall(text)),
                      "tail": text.strip().splitlines()[-1][:160] if text.strip() else "",
                      "secs": round(time.time() - t0, 1)}
        except subprocess.TimeoutExpired:
            out[s] = {"exit": -1, "fails": None, "tail": "timeout", "secs": round(time.time() - t0, 1)}
    return out


def one(tmp: Path, mut: dict | None) -> dict:
    mid = mut["id"] if mut else "baseline"
    dst = tmp / mid
    make_copy(dst)
    if mut:
        apply(dst, mut)
    scripts = mut["scripts"] if mut else sorted(set(PY_SCRIPTS + CARD_SCRIPTS), key=(PY_SCRIPTS + CARD_SCRIPTS).index)
    res = run_scripts(dst, scripts)
    shutil.rmtree(dst, ignore_errors=True)
    return {"id": mid, "scripts": res}


def probe_scoped_gate(tmp: Path) -> dict:
    """Does the scoped gate select fewer scripts for an optimizer change than for a closures-less tree?"""
    dst = tmp / "scoped_probe"
    make_copy(dst)
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub"
    res = {}
    for label, remove in (("with_closures", False), ("without_closures", True)):
        if remove:
            (dst / "tests" / "closures.json").unlink()
        work = dst / f"work_{label}"
        work.mkdir()
        r = subprocess.run([PY, "tests/closure.py", "select", "--files",
                            f"{PKG}/optimizer.py", "--workdir", str(work)],
                           cwd=dst, env=env, capture_output=True, text=True)
        text = r.stdout + r.stderr
        res[label] = {"exit": r.returncode, "head": text.strip().splitlines()[:12]}
    shutil.rmtree(dst, ignore_errors=True)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    muts = [m for m in MUTATIONS if not only or m["id"] in only]
    tmp = Path(os.environ.get("D7_TMP") or tempfile.mkdtemp(prefix="d7mut-"))
    tmp.mkdir(parents=True, exist_ok=True)
    print(f"=== D7 spot mutations (copies under {tmp}) ===")
    base = one(tmp, None)
    print("baseline:", json.dumps(base["scripts"], indent=None)[:600])
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(lambda m: one(tmp, m), muts))
    rows = []
    for m, r in zip(muts, results):
        detected = 0
        for s, v in r["scripts"].items():
            b = base["scripts"].get(s, {})
            if v.get("exit") is None or b.get("exit") is None:
                continue
            if v["exit"] > b["exit"] or (v.get("fails") or 0) > (b.get("fails") or 0):
                detected = 1
        rows.append({"id": m["id"], "addition": m["addition"], "module": m["module"],
                     "symbol": m["symbol"], "detected": detected,
                     "docs_files": docs_mentions(m["doc_anchor"]),
                     "test_files": tests_mentions(m["doc_anchor"]),
                     "scripts": r["scripts"]})
    infra_rows = []
    for i in INFRA:
        infra_rows.append({**i, "docs_files": docs_mentions(i["doc_anchor"]),
                           "test_files": tests_mentions(i["doc_anchor"])})
    scoped = probe_scoped_gate(tmp) if (not only or "scoped_gate" in only) else {}

    print(f"\n{'id':40} {'det':>3} {'docs':>4} {'tests':>5}  per-script exit/fails")
    for r in rows:
        per = " ".join(f"{Path(s.split()[-1]).name}={v.get('exit')}/{v.get('fails')}" for s, v in r["scripts"].items())
        print(f"{r['id']:40} {r['detected']:3d} {r['docs_files']:4d} {r['test_files']:5d}  {per}")
    for i in infra_rows:
        print(f"{i['id']:40} {'n/a':>3} {i['docs_files']:4d} {i['test_files']:5d}  {i['note']}")
    if scoped:
        print("\nscoped gate probe:")
        for k, v in scoped.items():
            print(f"  {k}: exit={v['exit']}")
            for line in v["head"]:
                print(f"      {line}")

    for r in rows:
        print(f"RESULT detected_{r['id']}={r['detected']} count")
        print(f"RESULT docs_files_{r['id']}={r['docs_files']} count")
    print(f"RESULT additions_mutated={len(rows)} count")
    print(f"RESULT additions_detected={sum(r['detected'] for r in rows)} count")
    print(f"RESULT additions_undetected={sum(1 for r in rows if not r['detected'])} count")
    print(f"RESULT additions_without_doc_file={sum(1 for r in rows if r['docs_files'] == 0)} count")
    print("RESULT thread_factor=1.0")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    OUT.write_text(json.dumps({"baseline": base, "rows": rows, "infra": infra_rows,
                               "scoped_gate_probe": scoped, "tmp": str(tmp)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
