#!/usr/bin/env python3
"""D3 round-3 mutant sampler.

Metric definition: the seeded, consequence-weighted sample of single-line
production mutations that the D3 pre-screen runs, one JSON record per mutant.

Run (from the repository root, nothing else is needed):

    PYTHONPATH=tests/hastub python3 tools/audit/round3/D3/mutant_pool.py \
        --seed 20260910 --n 34 --out tools/audit/round3/D3/mutants.json

Expected value: 34 mutants over <= 4 per module, pool size 3400 +- 400
(deterministic for a fixed seed and a fixed tree; exact for the baseline).
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
Machine: 8-core Apple M1, macOS 15 (Darwin 25.6.0), python3 3.11.5.

Every mutant is a single-line textual replacement recorded as
(file, line_no, old_line, new_line) so it re-applies byte-exactly.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import random
import re
from pathlib import Path

PROD = Path("custom_components/heatpump_optimizer")

# Consequence weights, by what a wrong answer in that module costs a user on
# Raspberry-Pi-class hardware.  5 = wrong money or wrong comfort silently.
MODULE_WEIGHT = {
    "optimizer.py": 5, "coordinator.py": 5, "thermal_model.py": 5,
    "price_model.py": 4, "tariff.py": 4, "grid_fee.py": 4,
    "sensor.py": 4, "services.py": 4, "config_flow.py": 4,
    "dhw_schedule.py": 3, "dhw_learning.py": 3, "dhw_draws.py": 3,
    "defrost.py": 3, "comfort_band.py": 3, "away.py": 3, "battery.py": 3,
    "wood_fuel.py": 3, "external_heat.py": 3, "freq_control.py": 3,
    "pump_mode.py": 3, "pump_signals.py": 3, "pump_schedule.py": 3,
    "power_guard.py": 3, "setpoint_check.py": 3, "mixing_valve.py": 3,
    "inputs.py": 2, "topology.py": 2, "sysid.py": 2, "accuracy.py": 2,
    "ledger.py": 2, "snapshots.py": 2, "narrative.py": 2, "presets.py": 2,
    "const.py": 2, "climate.py": 2, "switch.py": 2, "binary_sensor.py": 2,
    "boost.py": 2, "comfort_learning.py": 2, "manual_plan.py": 2,
    "open_meteo.py": 2, "frontend.py": 2, "__init__.py": 2,
    "curve_learning.py": 2, "drift.py": 2, "diagnosis.py": 2, "pv.py": 2,
    "wear.py": 2, "currency.py": 1, "entity.py": 1, "repairs.py": 1,
    "datetime.py": 1, "button.py": 1, "diagnostics.py": 1,
    "process_worker.py": 1,
}
DEFAULT_MODULE_WEIGHT = 2

# Kind weights: how directly the mutated construct decides a published number.
KIND_WEIGHT = {
    "CLAMP_DROP": 3,     # min()/max() safety clamp removed
    "GUARD_OFF": 3,      # `if <cond>:` forced False -- guard never fires
    "RAISE_DEL": 3,      # a validation raise deleted
    "RETURN_DEL": 2,     # an early return deleted
    "CONST": 2,          # a numeric literal changed
    "BOOLOP": 2,         # `and` <-> `or` on a condition line
}

_NUM = re.compile(r"(?<![\w.])(\d+\.\d+|\d+)(?![\w.])")


def _one_line(node, lines) -> bool:
    return getattr(node, "end_lineno", node.lineno) == node.lineno


def _indent(s: str) -> str:
    return s[: len(s) - len(s.lstrip())]


def candidates(path: Path):
    src = path.read_text()
    lines = src.splitlines()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    # Map: which lines are the *only* statement of a block body.
    sole = set()
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            body = getattr(node, field, None)
            if isinstance(body, list) and len(body) == 1:
                sole.add(body[0].lineno)

    for node in ast.walk(tree):
        ln = getattr(node, "lineno", None)
        if ln is None or ln > len(lines):
            continue
        line = lines[ln - 1]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # CLAMP_DROP: min(a, b) / max(a, b) on a single line -> first argument.
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("min", "max") and len(node.args) == 2
                and _one_line(node, lines)):
            seg = ast.get_source_segment(src, node)
            arg0 = ast.get_source_segment(src, node.args[0])
            if seg and arg0 and seg in line and line.count(seg) == 1:
                yield dict(kind="CLAMP_DROP", file=str(path), line=ln,
                           old=line, new=line.replace(seg, f"({arg0})"),
                           note=f"{node.func.id}() clamp dropped")

        # GUARD_OFF: `if <cond>:` on one line, with no else -> `if False:`.
        if (isinstance(node, ast.If) and _one_line(node.test, lines)
                and not node.orelse and stripped.startswith("if ")
                and stripped.endswith(":")):
            yield dict(kind="GUARD_OFF", file=str(path), line=ln,
                       old=line, new=_indent(line) + "if False:",
                       note="guard body never runs")

        # RAISE_DEL / RETURN_DEL: delete a one-line raise/return that is not
        # the sole statement of its block (deleting that would not parse).
        if isinstance(node, (ast.Raise, ast.Return)) and _one_line(node, lines):
            if ln in sole:
                continue
            kind = "RAISE_DEL" if isinstance(node, ast.Raise) else "RETURN_DEL"
            if kind == "RETURN_DEL" and getattr(node, "value", None) is None:
                continue
            yield dict(kind=kind, file=str(path), line=ln,
                       old=line, new=_indent(line) + "pass",
                       note=f"{kind.split('_')[0].lower()} removed")

        # BOOLOP: `and` -> `or` on a single-line boolean condition.
        if (isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)
                and _one_line(node, lines) and " and " in line
                and line.count(" and ") == 1):
            yield dict(kind="BOOLOP", file=str(path), line=ln,
                       old=line, new=line.replace(" and ", " or "),
                       note="conjunction weakened to a disjunction")

    # CONST: a module-level numeric assignment `NAME = <number>` -> x2 (or 1.0
    # when the value is 0).  Line-local, no AST walk needed beyond the tree.
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name) or not tgt.id.isupper():
            continue
        if not isinstance(node.value, ast.Constant):
            continue
        v = node.value.value
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        ln = node.lineno
        line = lines[ln - 1]
        m = _NUM.search(line.split("=", 1)[1]) if "=" in line else None
        if not m:
            continue
        new_val = "1.0" if v == 0 else repr(round(v * 2, 6) if isinstance(v, float) else v * 2)
        head, tail = line.split("=", 1)
        yield dict(kind="CONST", file=str(path), line=ln, old=line,
                   new=head + "=" + tail[: m.start()] + new_val + tail[m.end():],
                   note=f"{tgt.id} {v!r} -> {new_val}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--n", type=int, default=34)
    ap.add_argument("--per-module", type=int, default=4)
    ap.add_argument("--out", default="tools/audit/round3/D3/mutants.json")
    args = ap.parse_args()

    pool = []
    for path in sorted(PROD.glob("*.py")):
        for cand in candidates(path):
            mod = os.path.basename(cand["file"])
            cand["module"] = mod
            cand["module_weight"] = MODULE_WEIGHT.get(mod, DEFAULT_MODULE_WEIGHT)
            cand["kind_weight"] = KIND_WEIGHT[cand["kind"]]
            cand["weight"] = cand["module_weight"] * cand["kind_weight"]
            pool.append(cand)

    print(f"RESULT pool_size={len(pool)} candidates")
    by_kind = {}
    for c in pool:
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1
    for k in sorted(by_kind):
        print(f"RESULT pool_{k}={by_kind[k]} candidates")

    rng = random.Random(args.seed)
    chosen, per_mod, remaining = [], {}, list(pool)
    while remaining and len(chosen) < args.n:
        weights = [c["weight"] for c in remaining]
        pick = rng.choices(range(len(remaining)), weights=weights, k=1)[0]
        cand = remaining.pop(pick)
        mod = cand["module"]
        if per_mod.get(mod, 0) >= args.per_module:
            continue
        if any(c["file"] == cand["file"] and c["line"] == cand["line"] for c in chosen):
            continue
        per_mod[mod] = per_mod.get(mod, 0) + 1
        cand["id"] = f"M{len(chosen)+1:02d}"
        chosen.append(cand)

    print(f"RESULT sampled={len(chosen)} mutants")
    print(f"RESULT modules_touched={len(per_mod)} modules")
    Path(args.out).write_text(json.dumps(
        {"seed": args.seed, "n": args.n, "per_module": args.per_module,
         "pool_size": len(pool), "module_weight": MODULE_WEIGHT,
         "kind_weight": KIND_WEIGHT, "mutants": chosen}, indent=1))
    for c in chosen:
        print(f"  {c['id']}  {c['module']}:{c['line']}  {c['kind']}  w={c['weight']}  {c['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
