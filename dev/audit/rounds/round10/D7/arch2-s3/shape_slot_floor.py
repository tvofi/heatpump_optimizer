"""Shape: 'the 15-minute slot a datetime falls in' -- every implementation, driven on shared probes.

Seam rule (AST, printed): a function in the package that calls ``<x>.replace(minute=<expr>)`` where
<expr> contains ``//`` or ``%`` (a minute-field floor), plus ``tariff._window_slot`` (the
midnight-anchored floor). Counted per site, so an inline copy of a helper counts.

Driven: ``tariff._window_slot(when, 15)``, ``coordinator._solve_anchor(when)`` and
``pump_arbiter._step_start(when)``. The inline floor in ``pump_arbiter._observe`` is the same
expression as ``_step_start`` byte for byte (printed), so it is not driven separately.

Metric: disagreeing_probes = probes on which the driven implementations do not return the same
(isoformat, fold, POSIX timestamp). Probes: Europe/Stockholm across the autumn repeated hour (both
folds), the spring gap, slot edges, sub-second stamps, a naive stamp and a UTC stamp. Key: the
datetime each production function returns.

Perturbation: --perturb drops the fold restore from ``_window_slot`` in this process (it is
re-bound to a copy without the ``slot.replace(fold=when.fold)`` line); the autumn fold=1 probe
must then disagree (count rises from the baseline value).

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/shape_slot_floor.py [--root DIR] [--perturb]

Counts only; contention-immune. Writes nothing.
"""
import argparse
import ast
import importlib
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


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


REPO = repo_root(__file__)
TZ = ZoneInfo("Europe/Stockholm")
PROBES = [
    ("autumn 02:07 fold0", datetime(2026, 10, 25, 2, 7, tzinfo=TZ, fold=0)),
    ("autumn 02:07 fold1", datetime(2026, 10, 25, 2, 7, tzinfo=TZ, fold=1)),
    ("autumn 02:59:59.9 fold1", datetime(2026, 10, 25, 2, 59, 59, 900000, tzinfo=TZ, fold=1)),
    ("spring gap 02:30", datetime(2026, 3, 29, 2, 30, tzinfo=TZ)),
    ("spring 03:05", datetime(2026, 3, 29, 3, 5, tzinfo=TZ)),
    ("12:07:33.123", datetime(2026, 1, 15, 12, 7, 33, 123000, tzinfo=TZ)),
    ("12:15 edge", datetime(2026, 1, 15, 12, 15, tzinfo=TZ)),
    ("23:59:59.999", datetime(2026, 1, 15, 23, 59, 59, 999000, tzinfo=TZ)),
    ("naive 12:07", datetime(2026, 1, 15, 12, 7)),
    ("utc 12:07", datetime(2026, 1, 15, 12, 7, tzinfo=timezone.utc)),
]


def seams(pkg: Path) -> list[str]:
    out = []
    for p in sorted(pkg.glob("*.py")):
        tree = ast.parse(p.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for c in ast.walk(fn):
                if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "replace"
                        and any(k.arg == "minute" and any(isinstance(n, ast.BinOp) and isinstance(n.op, (ast.FloorDiv, ast.Mod))
                                                          for n in ast.walk(k.value)) for k in c.keywords)):
                    out.append(f"{p.stem}.{fn.name}:{c.lineno}  {ast.unparse(c)[:90]}")
            if fn.name == "_window_slot":
                out.append(f"{p.stem}.{fn.name}:{fn.lineno}  (midnight + timedelta, fold restored)")
    return out


def key(d: datetime) -> str:
    return f"{d.isoformat()} fold={d.fold} ts={d.timestamp():.0f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    sys.path.insert(0, str(root / "custom_components"))
    rows = seams(root / "custom_components" / "heatpump_optimizer")
    print(f"RESULT implementations={len(rows)} count")
    for r in rows:
        print("   ", r)
    tariff = importlib.import_module("heatpump_optimizer.tariff")
    coord = importlib.import_module("heatpump_optimizer.coordinator")
    arb = importlib.import_module("heatpump_optimizer.pump_arbiter")
    floor = getattr(tariff, "slot_floor", None) or getattr(tariff, "_window_slot")
    if a.perturb:
        import inspect
        src = textwrap.dedent(inspect.getsource(tariff._window_slot)).replace(
            "slot = slot.replace(fold=when.fold)", "pass")
        ns = dict(vars(tariff))
        exec(compile(src, "<perturbed>", "exec"), ns)
        floor = ns["_window_slot"]
    impls = {
        "tariff._window_slot(.,15)": lambda w: floor(w, 15),
        "coordinator._solve_anchor": coord._solve_anchor,
        "pump_arbiter._step_start": arb._step_start,
    }
    dis = []
    for label, when in PROBES:
        got = {}
        for name, fn in impls.items():
            try:
                got[name] = key(fn(when))
            except Exception as exc:  # noqa: BLE001 -- a raise is an answer
                got[name] = type(exc).__name__
        if len(set(got.values())) > 1:
            dis.append(label)
            print(f"  DISAGREE {label}: " + " | ".join(f"{k} -> {v}" for k, v in got.items()))
    print(f"RESULT driven={len(impls)} count")
    print(f"RESULT probes={len(PROBES)} count")
    print(f"RESULT disagreeing_probes={len(dis)} count")
    print(f"RESULT disagreeing_probe_labels={','.join(dis) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
