#!/usr/bin/env python3
"""D15-s2 harness, D15.M5 (timeline replay): the lane's judges over the bundle's
replay half, offenders per judge, and the verdict ``debug_replay.py`` prints.

``tests/replay.py:run_fixture`` returns offenders for every judge the lane
grades (``grade_ran``: each key of ``results`` must be empty);
``tools/replay/debug_replay.py:main`` prints five of them and its
``smoke_verdict`` reads four.

Metrics (one line each):
  judge_<name>: offenders ``run_fixture`` returns for that judge, the seeded
      replay as ``debug_replay.run_seeded`` runs it.
  lane_red_judges: judges with offenders (the lane's rule: any is red).
  debug_replay_verdict: ``pass``/``fail`` by ``debug_replay.main``'s own rule,
      re-applied to the same verdict (its printed keys and verdict keys are read
      off its source text below, so a change there moves this number).
  unreported_red_judges: lane-red judges ``debug_replay.main`` does not print.
  verdict_blind_red_judges: lane-red judges its ``smoke_verdict`` does not read.
Count key: the offenders the production entities' published records give
the lane's judge functions; nothing off the bundle's own text.

Run (from the export root):
    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round11/D15/s2/m5_judges.py --bundle B [--hours H]
    ... --from-hours F --hours H   # one chunk of the window (each chunk re-seeds)
    ... --offenders N    # print the first N offender lines per red judge (masked ids only)
Perturbation: --verdict-keys all  (debug_replay's verdict made to read every
judge run_fixture returns) -> verdict_blind_red_judges 0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: owner's macOS box (B8).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import contextlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components",
           ROOT / "tools" / "replay"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
import debug_replay  # noqa: E402


def debug_replay_keys() -> tuple[set[str], set[str]]:
    """(the judges main() prints, the judges its smoke_verdict reads), off its source."""
    tree = ast.parse(Path(debug_replay.__file__).read_text())
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    tuples = [n for n in ast.walk(main) if isinstance(n, ast.Tuple)
              and n.elts and all(isinstance(e, ast.Constant) and isinstance(e.value, str)
                                 for e in n.elts)]
    sets = [{e.value for e in t.elts} for t in tuples]
    printed = max(sets, key=len)
    verdict = min(sets, key=len)
    return printed, verdict


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    ap.add_argument("--hours", type=float, default=0.0, help="0: the whole replay half")
    ap.add_argument("--from-hours", type=float, default=0.0,
                    help="with --hours: the chunk starts this far into the window")
    ap.add_argument("--offenders", type=int, default=0)
    ap.add_argument("--verdict-keys", default="")
    ap.add_argument("--perturb", default="",
                    help="setpoint,constant: the two judge repairs, in memory")
    ap.add_argument("--save", type=Path, help="write the verdict JSON here (temp path)")
    a = ap.parse_args(argv)
    began = time.monotonic()
    bundle = debug_ingest.load_bundle(a.bundle)
    doc = bundle.get("replay") or {}
    if a.hours:
        start = datetime.fromisoformat(doc["window"]["start"]) + timedelta(hours=a.from_hours)
        doc = debug_replay.trim_replay(doc, start, start + timedelta(hours=a.hours))
    import replay as replay_mod
    if "setpoint" in a.perturb:
        # the action's setpoint sensor is a setpoint the config bounds supply,
        # as valve_target_recommendation is (replay.SETPOINT_KEYS)
        for key in ("current_setpoint", "optimal_setpoint"):
            replay_mod.SETPOINT_KEYS[key] = ("max_temperature", "min_temperature")
    if "constant" in a.perturb:
        # a published number that never moved over the window mirrors nothing
        real_frozen = replay_mod.frozen_offenders

        def moving_only(published, inputs):
            moved = {k: v for k, v in published.items()
                     if len({round(x, 6) for x in v if x is not None}) > 1}
            return real_frozen(moved, inputs)

        replay_mod.frozen_offenders = moving_only
    with contextlib.redirect_stderr(io.StringIO()):
        verdict = debug_replay.run_seeded(doc, bundle.get("stores") or None, None)
    if a.save:
        a.save.write_text(json.dumps(verdict, default=str))
    counts = verdict.get("counts") or {}
    printed, read = debug_replay_keys()
    if a.verdict_keys == "all":
        read = set(counts)
    red = {k for k, v in counts.items() if v}
    print(f"RESULT cycles={verdict.get('cycles')} unit=count")
    for k in sorted(counts):
        print(f"RESULT judge_{k}={counts[k]} unit=count")
    print(f"RESULT lane_red_judges={len(red)} unit=count names={','.join(sorted(red))}")
    dr = "fail" if any(counts.get(k) for k in read) else "pass"
    print(f"RESULT debug_replay_verdict={dr} unit=verdict")
    print(f"RESULT unreported_red_judges={len(red - printed)} unit=count names={','.join(sorted(red - printed))}")
    print(f"RESULT verdict_blind_red_judges={len(red - read)} unit=count names={','.join(sorted(red - read))}")
    if a.offenders:
        for k in sorted(red):
            for line in (verdict.get("results") or {}).get(k, [])[:a.offenders]:
                print(f"OFFENDER {k}: {line}")
    print(f"RESULT wall_s={time.monotonic() - began:.0f} unit=s provisional=true")
    print("RESULT thread_factor=1.000 unit=ratio (counts only)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print("RESULT swapins=n/a unit=count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
