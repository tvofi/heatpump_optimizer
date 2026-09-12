#!/usr/bin/env python3
"""D3 round 4 -- the mutant pool: consequence-weighted, seeded, capped at 4/module.

METRIC: the sampled set of single-line DELETION mutants of production code,
drawn without replacement with probability proportional to a module's
consequence weight, seed 20260912, at most 4 per module.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/mutant_pool_r4.py --n 36 > /dev/null

EXPECTED: 36 mutants over 12 modules, deterministic for a given seed; the
pool JSON is written to tools/audit/round4/D3/pool.json.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0 (darwin), python 3.11

This file generates candidates only; it executes no production code and has no
timing RESULT, so it carries no thread pin.
"""
from __future__ import annotations

import argparse
import ast
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PKG = "custom_components/heatpump_optimizer/"

# Consequence weights. The scale is COMMON.md's severity ladder read forwards:
# 5 = a wrong line here moves money or comfort silently; 4 = a safety or
# health guard, or the loop that publishes every value; 3 = a user-visible
# published value, a service, or config validation; 2 = a feature module whose
# failure is bounded; 1 = presentation and plumbing.
WEIGHTS = {
    "optimizer.py": 5, "thermal_model.py": 5, "price_model.py": 5,
    "tariff.py": 5, "grid_fee.py": 5,
    "coordinator.py": 4, "legionella.py": 4, "defrost.py": 4,
    "power_guard.py": 4, "setpoint_check.py": 4, "dhw_schedule.py": 4,
    "mixing_valve.py": 4, "wood_fuel.py": 4,
    "sensor.py": 3, "services.py": 3, "config_flow.py": 3, "inputs.py": 3,
    "manual_plan.py": 3, "topology.py": 3, "climate.py": 3, "battery.py": 3,
    "pv.py": 3, "external_heat.py": 3,
    "away.py": 2, "boost.py": 2, "comfort_band.py": 2,
    "comfort_learning.py": 2, "curve_learning.py": 2, "dhw_learning.py": 2,
    "drift.py": 2, "freq_control.py": 2, "pump_mode.py": 2,
    "pump_schedule.py": 2, "pump_signals.py": 2, "snapshots.py": 2,
    "sysid.py": 2, "wear.py": 2, "accuracy.py": 2, "ledger.py": 2,
    "diagnosis.py": 2, "presets.py": 2, "dhw_draws.py": 2, "currency.py": 2,
    "narrative.py": 1, "frontend.py": 1, "binary_sensor.py": 1,
    "button.py": 1, "switch.py": 1, "datetime.py": 1, "diagnostics.py": 1,
    "entity.py": 1, "repairs.py": 1, "process_worker.py": 1,
    "open_meteo.py": 1, "__init__.py": 1,
}
# const.py is deliberately out of the pool: every deletion of a module-level
# constant assignment is an ImportError in every driver, so it measures the
# import graph rather than the suite.
EXCLUDED = {"const.py"}


def _indent(s: str) -> str:
    return s[: len(s) - len(s.lstrip())]


def _one_line(node) -> bool:
    end = getattr(node, "end_lineno", None)
    return end is not None and end == node.lineno


def candidates(path: Path, rel: str):
    """Single-line DELETION mutants: the guard off, the clamp dropped, the
    statement replaced by `pass` at the same indent."""
    src = path.read_text()
    lines = src.splitlines()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    # Lines inside `if TYPE_CHECKING:` are not executed at runtime.
    skip: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            t = node.test
            name = getattr(t, "id", None) or getattr(t, "attr", None)
            if name == "TYPE_CHECKING":
                for i in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                    skip.add(i)
    for node in ast.walk(tree):
        ln = getattr(node, "lineno", None)
        if ln is None or ln > len(lines) or ln in skip:
            continue
        line = lines[ln - 1]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # (a) the clamp, deleted: min(a, b) -> (a)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("min", "max") and len(node.args) == 2
                and _one_line(node)):
            seg = ast.get_source_segment(src, node)
            arg0 = ast.get_source_segment(src, node.args[0])
            if seg and arg0 and seg in line and line.count(seg) == 1:
                yield dict(op="CLAMP_DROP", file=rel, line=ln, old=line,
                           new=line.replace(seg, f"({arg0})"),
                           what=f"drop the {node.func.id}() clamp")
        # (b) the guard, deleted: everything it guards stops happening
        if (isinstance(node, ast.If) and _one_line(node.test)
                and not node.orelse and stripped.startswith("if ")
                and stripped.endswith(":")):
            yield dict(op="GUARD_OFF", file=rel, line=ln, old=line,
                       new=_indent(line) + "if False:",
                       what="delete the guarded block (condition never taken)")
        # (c) the statement, deleted
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.Raise, ast.Return,
                             ast.Expr, ast.Continue, ast.Break)) and _one_line(node):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                continue  # a docstring
            if isinstance(node, ast.Return) and getattr(node, "value", None) is None:
                continue  # `return` alone: `pass` is the same thing
            if not stripped or stripped.startswith(("@", "def ", "class ")):
                continue
            if getattr(node, "col_offset", 0) == 0:
                continue  # module level: import-time, not behaviour
            yield dict(op="STMT_DEL", file=rel, line=ln, old=line,
                       new=_indent(line) + "pass",
                       what="delete the statement")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=36)
    ap.add_argument("--per-module", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260912)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "pool.json"))
    args = ap.parse_args()

    pkg = ROOT / PKG
    by_module: dict[str, list[dict]] = {}
    for path in sorted(pkg.rglob("*.py")):
        name = str(path.relative_to(pkg))
        if name in EXCLUDED or name not in WEIGHTS:
            continue
        rel = PKG + name
        got = list(candidates(path, rel))
        if got:
            by_module[name] = got

    rng = random.Random(args.seed)
    # Allocation, not a bare weighted draw. A uniform draw over module weights
    # under-samples the five modules that carry money and comfort simply
    # because there are fifty other modules: the five weight-5 modules would
    # have drawn 1.3 slots each out of 36. Slots are therefore allocated
    # proportional to weight SQUARED (5:4:3:2:1 -> 25:16:9:4:1), by largest
    # remainder, capped at --per-module, with the seeded RNG breaking ties and
    # choosing the lines. Recorded here so the allocation is auditable.
    share = {m: WEIGHTS[m] ** 2 for m in by_module}
    total = sum(share.values())
    exact = {m: args.n * share[m] / total for m in by_module}
    alloc = {m: min(args.per_module, min(int(exact[m]), len(by_module[m])))
             for m in by_module}
    order = sorted(by_module, key=lambda m: (-(exact[m] - int(exact[m])), -share[m], m))
    rng.shuffle(order)
    order.sort(key=lambda m: -(exact[m] - int(exact[m])))
    i = 0
    while sum(alloc.values()) < args.n and i < 10 * len(order):
        m = order[i % len(order)]
        if alloc[m] < min(args.per_module, len(by_module[m])):
            alloc[m] += 1
        i += 1

    chosen: list[dict] = []
    for mod in sorted(by_module, key=lambda m: (-WEIGHTS[m], m)):
        k = alloc[mod]
        if not k:
            continue
        # Stratified by operator inside the module. The brief names guards --
        # `if`, `min`/`max`/`clip` -- first, and an unstratified draw gives
        # them 4 of 36 because plain statements outnumber them ~5:1 in the
        # candidate list. Half of each module's slots (rounded up) go to the
        # guard/clamp stratum when it has that many.
        guards = [c for c in by_module[mod] if c["op"] in ("GUARD_OFF", "CLAMP_DROP")]
        stmts = [c for c in by_module[mod] if c["op"] == "STMT_DEL"]
        want_g = min(len(guards), (k + 1) // 2)
        picks = rng.sample(guards, want_g) + rng.sample(stmts, min(len(stmts), k - want_g))
        if len(picks) < k:
            rest = [c for c in by_module[mod] if c not in picks]
            picks += rng.sample(rest, min(len(rest), k - len(picks)))
        for mut in picks:
            mut = dict(mut)
            mut["weight"] = WEIGHTS[mod]
            mut["weight_sq_share"] = round(share[mod] / total, 5)
            mut["slots_for_module"] = k
            chosen.append(mut)
    rng.shuffle(chosen)
    for n, mut in enumerate(chosen, 1):
        mut["id"] = f"M{n:02d}"

    out = {
        "seed": args.seed, "n": len(chosen), "per_module": args.per_module,
        "baseline_sha": "7dd68dd327fe3dbfb09f3bd0fe38910c58877697",
        "weights": WEIGHTS, "excluded": sorted(EXCLUDED),
        "allocation_rule": "slots proportional to weight**2, largest remainder, cap per_module",
        "pool_sizes": {m: len(v) for m, v in sorted(by_module.items())},
        "mutants": chosen,
    }
    Path(args.out).write_text(json.dumps(out, indent=1) + "\n")
    print(f"RESULT mutants={len(chosen)} count")
    print(f"RESULT modules={len(set(m['file'] for m in chosen))} count")
    print(f"RESULT candidate_lines={sum(len(v) for v in by_module.values())} count")
    for m in chosen:
        print(f"  {m['id']} w={m['weight']} {m['op']:10s} "
              f"{m['file'][len(PKG):]}:{m['line']}  {m['old'].strip()[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
