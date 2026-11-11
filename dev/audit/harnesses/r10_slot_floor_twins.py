"""R10-PUMP-MODEL census: every spelling of "the wall-clock step an instant falls in".

D7-s3-8x-slotfloor, and #2365's review. The optimizer's plan step covering now
is one concern -- the solve's anchor, the pump arbiter's ledger row and its
silent-window lookup all read it -- and `plan_step.plan_step_start` owns it, on
`plan_step.PLAN_STEP_MINUTES`. It used to be spelled three times:
`coordinator._solve_anchor` on `FORECAST_STEP_MINUTES`,
`pump_arbiter._step_start` on a literal 15, and `_observe` inline (ARCH2-s3
patch 02). The rule this census enumerates is the one the P2 owners block
registers as `slot_floor_rule` in `tests/entities.py`: a `//`/`%` BinOp whose
text names `.minute` -- a minute-field floor.

Metric: `disagreeing_probes` -- probes on which the driven seams do not return
the same `(isoformat, fold, POSIX timestamp)`. Key: the datetime each seam
returns (for `_observe`, the ledger row's ``start``, read through the
production function). 0 when the seams are one rule in their own anchors.
`folded_seams` names the driven table's entries the rule no longer returns, so
a fold is printed rather than dropped from the driven set.

**The census asserts its own precondition**: every seam the rule returns must be
DRIVEN or named EXEMPT with its reason, and a seam that is neither is reported
unclassified and the run exits 1. A census that skips a class of seams passes
the day a skipped seam gains a writer (fixer.md step 8).

Null controls: `--identity` drives the owner against itself (0), and
`--perturb` drops `_window_slot`'s fold restore in a copy (the metering
window's own precondition), which must move the count above 0. `--widen` is
the review's perturbation: the plan step widened to 30 minutes at the tree's
own width source (plan_step's constant, or coordinator's before it had one
owner). A seam carrying a width of its own then reads 15 where the rest read
30; one owner reads 0.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_slot_floor_twins.py \
        [--root DIR] [--identity|--perturb|--widen]

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
    "plan_step.plan_step_start",
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
    ap.add_argument("--widen", action="store_true")
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
    try:
        plan_step = importlib.import_module("heatpump_optimizer.plan_step")
    except ImportError:  # a tree from before the plan step had one owner
        plan_step = None
    # The plan step's width, read where this tree keeps it: plan_step's
    # constant, or coordinator's before it had one owner.
    width_home, width_name = (
        (plan_step, "PLAN_STEP_MINUTES") if plan_step is not None
        else (coord, "FORECAST_STEP_MINUTES")
    )
    if args.widen:
        # #2365's review perturbation: the plan step widened to 30 minutes at
        # its one width source. A seam on a width of its own reads 15 where the
        # others read 30.
        setattr(width_home, width_name, 30)
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

    owner = (plan_step.plan_step_start if plan_step is not None
             else arb._step_start)
    if args.identity:
        # The null control: the owner against itself. 0 says the comparison is
        # a comparison, not a reading that always differs.
        impls = {"owner": owner, "owner (copy)": owner}
    else:
        table = {
            "plan_step.plan_step_start": getattr(plan_step, "plan_step_start", None),
            "coordinator._solve_anchor": getattr(coord, "_solve_anchor", None),
            "pump_arbiter._step_start": getattr(arb, "_step_start", None),
            "pump_arbiter._observe": observed,
            "tariff._window_slot":
                lambda w: floor(w, int(getattr(width_home, width_name))),
        }
        # Driven = the table's drivers for the seams the rule still returns.
        # A table entry the rule no longer returns is a FOLD (the finding's own
        # `_observe` at the head) and is named, never dropped silently.
        impls = {k: v for k, v in table.items() if k in found}
        # The arbiter's ledger row is the floor's READER, driven whether or not
        # it still spells the floor itself: a fold that changed the key, or a
        # width the reader kept for itself, shows here.
        impls["pump_arbiter._observe (ledger row)"] = observed
        # The owner is absent, not folded, in a tree from before it existed.
        folded = sorted(k for k in table if k not in found
                        and not (k == "plan_step.plan_step_start" and plan_step is None))
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
