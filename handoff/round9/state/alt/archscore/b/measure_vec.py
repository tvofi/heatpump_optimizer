#!/usr/bin/env python3
"""One tree -> the full raw metric vector (structure rows + a3 metrics + size).

    python3 measure_vec.py ROOT   -> JSON on stdout

Structure rows: tests/structure.py at 7952d8f9 (the pinned measurer in ../a2/measurer),
re-pointed at ROOT with the hybrid seam map (current map, regex fallback for historic
names) so one measurer judges every tree. a3 rows: ../a3/metrics, each returning
{"value", "details"}; a metric that raises is recorded as None with its error.
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "a2"))
sys.path.insert(0, str(HERE.parent / "a3" / "metrics"))

A3 = ("hub_solve_writes", "shared_inplace_writes", "private_reach", "untyped_payload_keys",
      "xmodule_duplication", "import_cycles", "public_surface", "dead_by_reachability",
      "family_splits")


def pkg_loc(root: Path) -> int:
    P = root / "custom_components" / "heatpump_optimizer"
    return sum(sum(1 for ln in p.read_text().splitlines() if ln.strip())
               for p in sorted(P.rglob("*.py")))


def measure_vec(root: Path) -> dict:
    import measure_one  # a2's loader for the pinned structure.py
    out: dict = {}
    s = measure_one.structure_metrics(root)
    out.update({k: v for k, v in s.items() if not k.startswith("_structure_tb")})
    for name in A3:
        try:
            mod = __import__(name)
            r = mod.measure(root)
            out[name] = r["value"]
            if name == "public_surface":
                out["public_unused"] = r["details"]["unused"]
            if name == "import_cycles":
                out["import_cycle_modules"] = r["details"]["modules_in_import_time_cycles"]
        except Exception as err:  # recorded, never hidden
            out[name] = None
            out[f"_{name}_error"] = f"{type(err).__name__}: {err}"[:200]
    import subprocess
    r = subprocess.run([sys.executable, str(HERE.parent / "a1" / "probes.py"), str(root)],
                       capture_output=True, text=True)
    if r.returncode == 0:
        for k, v in json.loads(r.stdout).items():
            out[f"a1_{k}"] = v
    else:
        out["_a1_probes_error"] = r.stderr[-300:]
    out["pkg_loc"] = pkg_loc(root)
    return out


if __name__ == "__main__":
    print(json.dumps(measure_vec(Path(sys.argv[1]).resolve()), sort_keys=True))
