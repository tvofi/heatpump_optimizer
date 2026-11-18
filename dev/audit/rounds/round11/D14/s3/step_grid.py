#!/usr/bin/env python3
"""D14-s3 (round 11): N-step-grid detector over every number field the flows build.

Drives ``tests/golden.py:capture_config_flow`` -- the live config and options
flow builders (``heatpump_optimizer.config_flow``), every page, seeded the way
the golden fixture records them -- and walks every ``NumberSelector`` it
fingerprints. A field with a numeric ``step`` is judged on the browser's own
rule for ``<input type=number>`` (the step base is ``min``):

  default_off_grid  (default - min) / step is not an integer (1e-9 relative)
  max_off_grid      (max - min) / step is not an integer (the top unreachable
                    by the spinner)
  min_off_zero_grid min / step is not an integer (the detector idea's
                    ``(min - base) % step`` with base 0)

Metric: fields per rule; count key: the selector config and default the
production builder delivered. Perturbation (``--perturb``): every captured
default is shifted by step/2 before judging -> default_off_grid goes up.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s3/step_grid.py
Expected at 92d38ecb6: see REPORT.md. Machine: box B7, 4 vCPU. Tolerance: exact.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import ast
import sys
import time
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components"):
    sys.path.insert(0, str(_p))


def lit(v):
    try:
        return ast.literal_eval(v) if isinstance(v, str) else v
    except (ValueError, SyntaxError):
        return v


def on_grid(x: float, base: float, step: float) -> bool:
    k = (x - base) / step
    return abs(k - round(k)) <= 1e-9 * max(1.0, abs(k))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0 = time.monotonic()
    import asyncio
    import json
    import golden
    flow = golden.capture_config_flow()
    # The replay arm: every options page rendered for each replay fixture's
    # stored entry (a real install's options, tests/replay/*.json), where
    # ``config_flow._fit_stored_values`` may widen a bound to a stored value.
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.config_flow import HeatPumpOptimizerOptionsFlow as Flow
    for fx in sorted((ROOT / "tests" / "replay").glob("*.json")):
        entry = json.loads(fx.read_text())["entry"]
        f = Flow(FakeEntry(data=dict(entry["data"]), options=dict(entry["options"])))
        f.hass = FakeHass()
        for step in Flow._MENU_LABELS:
            try:
                res = asyncio.run(getattr(f, f"async_step_{step}")())
            except Exception as err:  # noqa: BLE001 - a page that will not render is reported
                print(f"  {fx.name} {step}: {type(err).__name__}: {err}")
                continue
            flow[f"{fx.stem}:{step}"] = golden.schema_fingerprint(res.get("data_schema"))
    fields = []

    def walk(page, node, name=None):
        if isinstance(node, dict):
            if node.get("selector") == "NumberSelector":
                fields.append((page, name, {k: lit(v) for k, v in node["config"].items()},
                               lit(node.get("default"))))
                return
            for k, v in node.items():
                walk(page, v, k)

    for page, node in flow.items():
        walk(page, node)
    hits = {"default_off_grid": [], "max_off_grid": [], "min_off_zero_grid": []}
    judged = 0
    for page, name, cfg, default in fields:
        step = cfg.get("step")
        if not isinstance(step, (int, float)) or step <= 0:
            continue
        judged += 1
        lo, hi = cfg.get("min"), cfg.get("max")
        tag = f"{page}.{name} mode={cfg.get('mode')} min={lo} max={hi} step={step} default={default}"
        if isinstance(default, (int, float)) and isinstance(lo, (int, float)):
            d = default + (step / 2 if a.perturb else 0.0)
            if not on_grid(d, lo, step):
                hits["default_off_grid"].append(tag)
        if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and not on_grid(hi, lo, step):
            hits["max_off_grid"].append(tag)
        if isinstance(lo, (int, float)) and not on_grid(lo, 0.0, step):
            hits["min_off_zero_grid"].append(tag)
    print(f"{len(fields)} number fields over {len(flow)} pages; {judged} with a numeric step")
    for rule, rows in hits.items():
        for r in sorted(set(rows)):
            print(f"  {rule}: {r}")
        print(f"RESULT {rule}={len(set(rows))} count")
    print(f"RESULT number_fields={len(fields)} count")
    print(f"RESULT judged_fields={judged} count")
    print(f"RESULT wall_s={time.monotonic() - t0:.1f} s (provisional)")
    pc, tc = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(pc / tc) if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + str(sum(int(l.split()[1]) for l in open("/proc/vmstat")
                                      if l.startswith("pswpin"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
