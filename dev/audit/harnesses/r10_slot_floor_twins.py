"""R10-PUMP-MODEL census: every spelling of "the wall-clock step an instant falls in".

D7-s3-8x-slotfloor. `pump_arbiter._step_start` owns the pump side's step start
(the arbiter ledger row, the silent-window lookup and the plan's step index),
and `_observe` spelled the same arithmetic inline until ARCH2-s3 patch 02. The
rule this census enumerates is the one the P2 owners block registers as
`slot_floor_rule` in `tests/entities.py`: a `//`/`%` BinOp whose text names
`.minute` -- a minute-field floor.

Metric: `disagreeing_probes` -- probes on which the driven seams do not return
the same `(isoformat, fold, POSIX timestamp)`. Key: the datetime each seam
returns (for `_observe`, the ledger row's ``start``, read through the
production function). 0 when the seams are one rule in their own anchors.
`folded_seams` names the driven table's entries the rule no longer returns --
at the head, `_observe`, the seam this finding folded -- so a fold is printed
rather than dropped from the driven set.

**The census asserts its own precondition**: every seam the rule returns must be
DRIVEN or named EXEMPT with its reason, and a seam that is neither is reported
unclassified and the run exits 1. A census that skips a class of seams passes
the day a skipped seam gains a writer (fixer.md step 8). So the baseline's
inline `_observe` is driven, and the count is 6 seams / 4 driven there against
5 / 3 at the head -- which is the finding's "implementations 4" and the fold's
"3", the owner among them.

Null controls: `--identity` drives the owner against itself (0), and
`--perturb` drops `_window_slot`'s fold restore in a copy (the metering
window's own precondition), which must move the count above 0.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_slot_floor_twins.py \
        [--root DIR] [--identity|--perturb]

Writes nothing; counts only, so contention-immune.
"""
from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import sys
import textwrap
import types
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

#: The seams the rule returns that this census drives, and how.
DRIVEN = (
    "coordinator._solve_anchor",
    "pump_arbiter._step_start",
    "pump_arbiter._observe",
    "tariff._window_slot",
)
#: Seams the rule returns that answer a different question, with why. Each is a
#: disposition of the same shape in tests/entities.py's P2 owners block.
EXEMPT = {
    "optimizer.HeatPumpOptimizer._window_offset_steps":
        "returns a step COUNT to the window boundary, not an instant",
    "price_model.PriceShapeModel.quarter_factor":
        "returns an index into a learned profile",
}
PROBES = [
    ("autumn 02:07 fold0", datetime(2026, 10, 25, 2, 7, tzinfo=ZoneInfo("Europe/Stockholm"), fold=0)),
    ("autumn 02:07 fold1", datetime(2026, 10, 25, 2, 7, tzinfo=ZoneInfo("Europe/Stockholm"), fold=1)),
    ("autumn 02:59:59.9 fold1", datetime(2026, 10, 25, 2, 59, 59, 900000,
                                         tzinfo=ZoneInfo("Europe/Stockholm"), fold=1)),
    ("spring gap 02:30", datetime(2026, 3, 29, 2, 30, tzinfo=ZoneInfo("Europe/Stockholm"))),
    ("spring 03:05", datetime(2026, 3, 29, 3, 5, tzinfo=ZoneInfo("Europe/Stockholm"))),
    ("12:07:33.123", datetime(2026, 1, 15, 12, 7, 33, 123000, tzinfo=ZoneInfo("Europe/Stockholm"))),
    ("12:15 edge", datetime(2026, 1, 15, 12, 15, tzinfo=ZoneInfo("Europe/Stockholm"))),
    ("23:59:59.999", datetime(2026, 1, 15, 23, 59, 59, 999000, tzinfo=ZoneInfo("Europe/Stockholm"))),
    ("naive 12:07", datetime(2026, 1, 15, 12, 7)),
    ("utc 12:07", datetime(2026, 1, 15, 12, 7, tzinfo=timezone.utc)),
]


def repo_root(start: str) -> Path:
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


def seams(pkg: Path) -> list[str]:
    """Every seam the rule returns, as ``<module>.<dotted def>`` labels."""
    out = []
    for path in sorted(pkg.glob("*.py")):
        for node, qual in _functions(ast.parse(path.read_text()), ""):
            inner = [g for g in ast.walk(node)
                     if g is not node and isinstance(g, (ast.FunctionDef, ast.AsyncFunctionDef))]
            own = set(ast.walk(node)) - {x for g in inner for x in ast.walk(g)}
            for n in own:
                if (isinstance(n, ast.BinOp) and isinstance(n.op, (ast.FloorDiv, ast.Mod))
                        and ".minute" in ast.unparse(n)):
                    out.append(f"{path.stem}.{qual}")
                    break
    return sorted(set(out))


def _functions(node: ast.AST, prefix: str):
    for child in ast.iter_child_nodes(node):
        name = prefix
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{prefix}.{child.name}" if prefix else child.name
            if not isinstance(child, ast.ClassDef):
                yield child, name
        yield from _functions(child, name)


def key(value) -> str:
    if not isinstance(value, datetime):
        return repr(value)
    return f"{value.isoformat()} fold={value.fold} ts={value.timestamp():.0f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="")
    ap.add_argument("--identity", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve() if args.root else repo_root(__file__)
    pkg = root / "custom_components" / "heatpump_optimizer"
    sys.path[:0] = [str(root / "custom_components"), str(root / "tests" / "hastub")]

    found = seams(pkg)
    print(f"RESULT seams={len(found)} count")
    for label in found:
        print("   ", label)
    unclassified = [s for s in found if s not in DRIVEN and s not in EXEMPT]
    for label in unclassified:
        print(f"  UNCLASSIFIED SEAM {label}: neither driven nor exempt -- "
              "add it to DRIVEN or to EXEMPT with its reason")

    arb = importlib.import_module("heatpump_optimizer.pump_arbiter")
    coord = importlib.import_module("heatpump_optimizer.coordinator")
    tariff = importlib.import_module("heatpump_optimizer.tariff")
    floor = tariff._window_slot
    if args.perturb:
        src = textwrap.dedent(inspect.getsource(tariff._window_slot)).replace(
            "slot = slot.replace(fold=when.fold)", "pass")
        ns = dict(vars(tariff))
        exec(compile(src, "<perturbed>", "exec"), ns)
        floor = ns["_window_slot"]

    def observed(when):
        """The ledger row's start, read through the production `_observe`."""
        held = arb.ArbiterState()
        inp = types.SimpleNamespace(
            config={}, state=types.SimpleNamespace(dhw_temperature=None),
            measured_power_kw=None,
        )
        arb._observe(held, inp, None, when)
        return held.step["start"] if held.step else None

    if args.identity:
        # The null control: the owner against itself. 0 says the comparison is
        # a comparison, not a reading that always differs.
        impls = {"pump_arbiter._step_start": arb._step_start,
                 "pump_arbiter._step_start (copy)": arb._step_start}
    else:
        table = {
            "coordinator._solve_anchor": coord._solve_anchor,
            "pump_arbiter._step_start": arb._step_start,
            "pump_arbiter._observe": observed,
            "tariff._window_slot": lambda w: floor(w, 15),
        }
        # Driven = the table's drivers for the seams the rule still returns.
        # A table entry the rule no longer returns is a FOLD (the finding's own
        # `_observe` at the head) and is named, never dropped silently.
        impls = {k: v for k, v in table.items() if k in found}
        folded = sorted(k for k in table if k not in found)
        print(f"RESULT folded_seams={len(folded)} count")
        for label in folded:
            print("    folded", label)
    disagree = []
    for label, when in PROBES:
        got = {}
        for name, fn in impls.items():
            try:
                got[name] = key(fn(when))
            except Exception as exc:  # noqa: BLE001 -- a raise is an answer
                got[name] = type(exc).__name__
        if len(set(got.values())) > 1:
            disagree.append(label)
            print(f"  DISAGREE {label}: "
                  + " | ".join(f"{k} -> {v}" for k, v in got.items()))
    print(f"RESULT driven={len(impls)} count")
    print(f"RESULT probes={len(PROBES)} count")
    print(f"RESULT disagreeing_probes={len(disagree)} count")
    print(f"RESULT disagreeing_probe_labels={','.join(disagree) or '-'}")
    print(f"RESULT unclassified_seams={len(unclassified)} count")
    return 1 if unclassified else 0


if __name__ == "__main__":
    sys.exit(main())
