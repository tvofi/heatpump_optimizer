#!/usr/bin/env python3
"""D7-s1 / D7.M5 companion: doc paragraph and owning module per train item.

Metric (one line): per item, the number of user-facing doc files (README.md,
docs/*.md except audit/backlog/plan/delivery records) carrying a paragraph
that matches the item's pattern, and the number of production modules that
DEFINE (def/class/assign at top level) the item's core symbols.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/s1/train_docs.py
Expected at 1936d5ca: exact counts as printed (static; no timing).
Machine: cloud container (linux), baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import ast  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
PKG = ROOT / "custom_components/heatpump_optimizer"
ITEMS = {
    "batched gradient": (r"batched (finite-difference )?gradient|_batch_fd_gradient", ["_batch_fd_gradient", "simulate_trajectory_batch"]),
    "bounds gate": (r"_bounds_supported_by_batch|bounds gate", ["_bounds_supported_by_batch"]),
    "weekly windows": (r"weekly window|weekdays 0\d:\d\d", ["parse_weekly_windows", "windows_for_day"]),
    "topology catalogue": (r"topolog(y|ies)", ["LAYOUTS", "Layout", "layout_edges"]),
    "wood variant": (r"wood[- ]tank|wood-while-usable|wood heat", ["wood_fuel_from_coordinator"]),
    "coil variant": (r"\bcoil\b", ["dhw_coil_active"]),
    "DHW confidence": (r"(dhw|hot[- ]water).{0,60}confidence|confidence band|expected[- ]error band", ["_dhw_confidence_band"]),
    "Tuya": (r"\btuya", ["_TUYA_HEAT_PUMP", "_TUYA_LOCAL"]),
    "re-anchor law": (r"re-?anchor|reconfigur.{0,200}(learn|heat[- ]loss)", ["house_loss_confidence", "_reanchor_house_heat_loss_scale"]),
    "card collaborators": (r"collaborator", ["PlanSource", "HistorySource"]),
}
SKIP = re.compile(r"audit|backlog|plan-|delivery|HANDOVER|decisions/|superpowers/")


def doc_files() -> list[Path]:
    out = [ROOT / "README.md"]
    out += [p for p in sorted((ROOT / "docs").rglob("*.md")) if not SKIP.search(str(p.relative_to(ROOT)))]
    return out


def definers(symbols: list[str]) -> set[str]:
    hits = set()
    for path in sorted(PKG.rglob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            name = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = node.name
            if isinstance(node, ast.Assign):
                name = next((t.id for t in node.targets if isinstance(t, ast.Name)), None)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                name = node.target.id
            if name in symbols:
                hits.add(path.name)
    for path in sorted(PKG.rglob("*.js")):
        if any(re.search(rf"^class {s}\b", path.read_text(), re.M) for s in symbols):
            hits.add(path.name)
    return hits


def main() -> int:
    c0, t0 = time.process_time(), time.thread_time()
    docs = doc_files()
    for item, (pat, syms) in ITEMS.items():
        rx = re.compile(pat, re.I)
        with_para = [d.relative_to(ROOT).as_posix() for d in docs
                     if any(rx.search(par) for par in d.read_text().split("\n\n"))]
        own = sorted(definers(syms))
        key = re.sub(r"\W+", "_", item)
        print(f"  {item}: docs={with_para[:4]}{'...' if len(with_para) > 4 else ''} owners={own}")
        print(f"RESULT {key}_doc_files={len(with_para)} count")
        print(f"RESULT {key}_owner_modules={len(own)} count")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
