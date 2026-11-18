#!/usr/bin/env python3
"""Probes for the N-uncleared-issue seams: each FAILS (exit 1) while its seam
is an instance. Run from repo root: PYTHONPATH=tests/hastub:. python3 <this> <probe>.
Probes: worker_fallback (behavioural), solve_failures, grid_fee, switch_lost (structural)."""
from __future__ import annotations
import ast, sys
from pathlib import Path
from types import SimpleNamespace

PKG = Path("custom_components/heatpump_optimizer")


def _tree(name):
    return ast.parse((PKG / name).read_text())


def _func(t, name):
    return next(n for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def worker_fallback():
    """A fresh process (empty latch) with the persisted notice restored: one healthy solve must clear it."""
    from custom_components.heatpump_optimizer import coordinator as c
    c._WORKER_FALLBACK_CAUSES.clear()
    hass = SimpleNamespace(issues=[(c.DOMAIN, "solve_worker_fallback", {"is_persistent": True})], data={})
    c._clear_worker_fallback(hass, "entry")
    left = sum(1 for i in hass.issues if i[1] == "solve_worker_fallback")
    print(f"solve_worker_fallback left after a fresh-process healthy solve: {left}")
    return left == 0


def solve_failures():
    """The success-path delete of the persistent solve_failures notice must not hang on the in-memory counter."""
    t = _tree("coordinator.py")
    f = _func(t, "async_run_optimization")
    gated = 0
    for st in ast.walk(f):
        if isinstance(st, ast.If) and "_solve_failures" in ast.unparse(st.test):
            if any(isinstance(n, ast.Call) and "solve_failures" in ast.unparse(n) and "delete" in ast.unparse(n.func) for b in st.body for n in ast.walk(b)):
                gated += 1
    saved = "\"solve_failures\"" in ast.unparse(_func(t, "_async_save_state")) if any(
        isinstance(n, ast.FunctionDef) and n.name == "_async_save_state" for n in ast.walk(t)) else False
    restored = "_solve_failures" in "".join(ast.unparse(n) for n in ast.walk(t) if isinstance(n, ast.Assign) and "stored" in ast.unparse(n.value) and "_solve_failures" in ast.unparse(n.targets[0]))
    print(f"solve_failures clear gated on in-memory counter: {gated}; counter restored from store: {restored}")
    return gated == 0 or restored


def grid_fee():
    """The persistent grid_fee_* notices must have a clear path when the fee layer goes inactive."""
    t = _tree("coordinator.py")
    callers = [f for f in ast.walk(t) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
               and any(isinstance(n, ast.Call) and ast.unparse(n.func).endswith("._fee_series") for n in ast.walk(f))]
    ungated = 0
    for f in callers:
        for n in ast.walk(f):
            if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("._fee_series"):
                encl = [s for s in ast.walk(f) if isinstance(s, ast.If) and any(m is n for b in s.body for m in ast.walk(b))]
                if not any("active" in ast.unparse(s.test) for s in encl):
                    ungated += 1
    other = sum(1 for n in ast.walk(t) if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("._audit_grid_fee")
                ) - 1  # the one inside _fee_series
    print(f"_fee_series calls not behind schedule.active: {ungated}; other _audit_grid_fee callers: {other}")
    return ungated + other > 0


def switch_lost():
    """Some path must clear dhw_disinfection_switch_lost_<entity> (e.g. once the switch reads off)."""
    hits = 0
    for p in PKG.rglob("*.py"):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.Call) and any(k in ast.unparse(n.func) for k in ("delete_issue", "clear_issue")) \
                    and "switch_lost" in ast.unparse(n):
                hits += 1
    print(f"clear sites for dhw_disinfection_switch_lost_*: {hits}")
    return hits > 0


if __name__ == "__main__":
    ok = globals()[sys.argv[1]]()
    print("PASS" if ok else "FAIL (instance)")
    sys.exit(0 if ok else 1)
