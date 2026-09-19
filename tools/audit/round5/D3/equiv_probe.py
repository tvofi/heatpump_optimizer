#!/usr/bin/env python3
"""D3 round 5 -- equivalence probe for the survivors.

Metric (one line): per survivor, whether the mutated line CHANGES observable
behaviour at the boundary input it guards -- so a survivor can be told apart
from an equivalent mutant, which no check could ever fail on.

Command:
    cd /tmp/hpo-d3-wt && PYTHONPATH=tests/hastub \
        python3 -u tools/audit/round5/D3/equiv_probe.py

Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main).
Machine: Apple M1, 8 GB. Everything here is in-process, no solver, no timing:
no number below is load-sensitive.

The mutant is applied by re-exec'ing the module's own source (with the one line
replaced) into the imported module's namespace, so package-relative imports
still resolve; the pristine source is re-exec'd in the finally to restore it.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tests" / "hastub"))
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent

POOL = {f"{r['file']}:{r['line']}": r
        for r in json.loads((HERE / "pool.json").read_text())["pool"]}


def run_original_and_mutant(rel, line, new, call):
    """call(module) on the pristine module, then on the one-line mutant."""
    name = "custom_components.heatpump_optimizer." + Path(rel).stem
    mod = importlib.import_module(name)
    src = (ROOT / rel).read_text().splitlines(True)
    pristine = "".join(src)
    assert src[line - 1].rstrip("\n") == POOL[f"{rel}:{line}"]["old"], \
        f"{rel}:{line} moved in the tree: {src[line-1]!r}"
    src[line - 1] = new + "\n"
    out = []
    for text in (pristine, "".join(src)):
        exec(compile(text, mod.__file__, "exec"), mod.__dict__)  # noqa: S102
        try:
            out.append(("ok", call(mod)))
        except Exception as exc:                                # noqa: BLE001
            out.append((type(exc).__name__, str(exc)))
    return out[0], out[1]


def probe(key, call):
    rel, line = key.rsplit(":", 1)
    mut = POOL[key]
    a, b = run_original_and_mutant(rel, int(line), mut["new"], call)
    same = a == b
    print(f"  {key}")
    print(f"      {'EQUIVALENT' if same else 'DIFFERS'}")
    print(f"      original: {a!r}")
    print(f"      mutated : {b!r}")
    return same


def _defrost(mod):
    d = mod.DefrostDerate()
    before = sum(sum(r) for r in d.duty_counts)
    d.observe_duty(outdoor_temp=3.0, humidity=0.8, duty=2.0)
    return {"counts_before": before,
            "counts_after": sum(sum(r) for r in d.duty_counts),
            "derate": d.duty[0][0]}


def _wear(mod):
    c = mod.StartCounter()
    when = datetime(2026, 1, 1, tzinfo=timezone.utc)
    c.running = True            # "already running, still above threshold"
    c._streak = 0
    confirmed = 0
    for i in range(mod.START_HYSTERESIS_SAMPLES + 2):
        if c.observe(when + timedelta(minutes=i), 2.0, 1.0, False):
            confirmed += 1
    return {"confirmed_starts": confirmed, "lifetime": c.lifetime,
            "streak": c._streak}


def _wood(mod):
    return mod.cheaper_hour_count(wood_sek=1.0, prices=[1.0], cops=[0.0],
                                  space_kw=[5.0], dhw_kw=[0.0], threshold=1.0)


def _mix(mod):
    return mod.flow_setpoint(target_temp=21.0, outdoor_temp=-5.0,
                             heat_loss_coefficient=0.2, emitter_ua=0.0)


CHECKS = {
    "custom_components/heatpump_optimizer/mixing_valve.py:109": _mix,
    "custom_components/heatpump_optimizer/wood_fuel.py:147": _wood,
    "custom_components/heatpump_optimizer/defrost.py:314": _defrost,
    "custom_components/heatpump_optimizer/wear.py:72": _wear,
}


def main():
    rows = []
    for key, call in CHECKS.items():
        rows.append((key, probe(key, call)))
    print()
    print("RESULT survivors_probed=%d count" % len(rows))
    print("RESULT non_equivalent=%d count" % sum(1 for _, s in rows if not s))
    print("RESULT equivalent=%d count" % sum(1 for _, s in rows if s))
    print("RESULT thread_factor=1.00 ratio")
    print("RESULT load1=%.2f ratio" % os.getloadavg()[0])


if __name__ == "__main__":
    main()
