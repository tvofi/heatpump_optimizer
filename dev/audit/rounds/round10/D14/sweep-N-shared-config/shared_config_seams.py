#!/usr/bin/env python3
"""Round-10 D14 class sweep, N-shared-config: every seam where state the
coordinator shares (with an in-flight cycle across an await, with the
entities it publishes to, or with a solve thread) is written in place or
adopted without a re-check.

Four families, one per finding seam_rule in the class:
  A  executor-await adoption (D1-s1-02): an ``await`` of an off-loop call
     (_await_optimize / _await_off_loop / _await_process /
     async_add_executor_job) inside an async function that, later in the same
     body, writes ``self.<attr>`` / ``coord.<attr>`` or calls an adopt/publish
     helper -- the result is adopted after the loop may have moved.
  B  hub in-place writes reachable from a solve root (D7-arch1-01):
     archscore.metrics.hub_solve_writes sites.
  C  shared in-place writes outside the owner / inside coordinator async
     methods (D7-arch1-02, -03): archscore.metrics.shared_inplace_writes sites.
  D  module-level runtime channels (D7-arch3-04): a ``global`` rebinding,
     ``setattr`` on a module-level or imported function/object, or a store /
     mutator call on a module-level name, inside a function body.

Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-shared-config/shared_config_seams.py [--root DIR] [--json]
          --null           run on a clean fixture package (expected 0 in every family)
          --perturb FAM    the clean fixture plus ONE re-introduced line of family FAM (expected 1 in FAM)
Positive control: at the round's baseline the output contains every judged
          finding site (printed as POSITIVE lines, each must say found=1).
Root: the worktree (resolved from this file, five parents up) unless --root.
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tools" / "audit"))

PKG = "custom_components/heatpump_optimizer"
OFFLOOP = {"_await_optimize", "_await_off_loop", "_await_process", "async_add_executor_job"}
ADOPT = ("adopt", "publish", "async_set_updated_data", "async_update_listeners")
MUT = {"append", "extend", "insert", "pop", "popitem", "clear", "update",
       "setdefault", "add", "discard", "remove"}


def _callee(c: ast.Call) -> str:
    f = c.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")


def family_a(pkg: Path) -> list[str]:
    out = []
    for p in sorted(pkg.glob("*.py")):
        t = ast.parse(p.read_text())
        for fn in ast.walk(t):
            if not isinstance(fn, ast.AsyncFunctionDef):
                continue
            awaits = [n for n in ast.walk(fn) if isinstance(n, ast.Await)
                      and isinstance(n.value, ast.Call) and _callee(n.value) in OFFLOOP]
            for aw in awaits:
                later = False
                for n in ast.walk(fn):
                    if getattr(n, "lineno", 0) <= aw.lineno:
                        continue
                    if isinstance(n, (ast.Assign, ast.AugAssign)):
                        for tg in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                            b = tg
                            while isinstance(b, (ast.Attribute, ast.Subscript)):
                                b = b.value
                            if isinstance(b, ast.Name) and b.id in ("self", "coord", "coordinator") \
                                    and isinstance(tg, (ast.Attribute, ast.Subscript)):
                                later = True
                    if isinstance(n, ast.Call):
                        nm = _callee(n)
                        if any(k in nm for k in ADOPT) or (nm == "update" and isinstance(n.func, ast.Attribute)
                                and isinstance(n.func.value, ast.Call) and _callee(n.func.value) == "vars"):
                            later = True
                if later:
                    out.append(f"{p.name}:{aw.lineno} {fn.name} awaits {_callee(aw.value)} then adopts")
    return out


def family_d(pkg: Path) -> list[str]:
    out = []
    for p in sorted(pkg.glob("*.py")):
        t = ast.parse(p.read_text())
        modnames = set()
        for n in t.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                modnames.add(n.name)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                modnames.update((a.asname or a.name).split(".")[0] for a in n.names)
            elif isinstance(n, (ast.Assign, ast.AnnAssign)):
                for tg in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                    if isinstance(tg, ast.Name):
                        modnames.add(tg.id)
        for fn in sorted((n for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))),
                         key=lambda n: n.lineno):
            local = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
            for n in ast.walk(fn):
                if isinstance(n, (ast.Assign, ast.AnnAssign)) and fn.name:
                    for tg in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                        if isinstance(tg, ast.Name):
                            local.add(tg.id)
            shared = modnames - local
            for n in ast.walk(fn):
                if isinstance(n, ast.Global):
                    out.append(f"{p.name}:{n.lineno} {fn.name} global {','.join(n.names)}")
                elif isinstance(n, ast.Call):
                    f = n.func
                    if isinstance(f, ast.Name) and f.id == "setattr" and n.args \
                            and isinstance(n.args[0], ast.Name) and n.args[0].id in shared:
                        out.append(f"{p.name}:{n.lineno} {fn.name} setattr {n.args[0].id}")
                    elif isinstance(f, ast.Attribute) and f.attr in MUT and isinstance(f.value, ast.Name) \
                            and f.value.id in shared and f.value.id.isupper() is not None \
                            and f.value.id.startswith("_") and f.value.id.lstrip("_")[:1].isupper():
                        out.append(f"{p.name}:{n.lineno} {fn.name} mutates {f.value.id}.{f.attr}")
                elif isinstance(n, (ast.Assign, ast.AugAssign)):
                    for tg in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                        if isinstance(tg, (ast.Attribute, ast.Subscript)) and isinstance(tg.value, ast.Name) \
                                and tg.value.id in shared and tg.value.id not in ("self", "cls"):
                            out.append(f"{p.name}:{n.lineno} {fn.name} stores {ast.unparse(tg)}")
    # A nested def is walked from its parent too: keep each site once, on its
    # innermost function (the latest-starting one, which sorts last here).
    inner = {}
    for o in out:
        f, rest = o.split(" ", 1)
        name, what = rest.split(" ", 1)
        inner[(f, what)] = o
    return sorted(set(inner.values()))


def families_bc(root: Path) -> tuple[list[str], list[str]]:
    from archscore.metrics import hub_solve_writes as H, shared_inplace_writes as S
    try:
        b = H.measure(root)["details"]["sites"]
    except Exception as err:  # a fixture with no solve root
        b = [] if "coord" in str(err).lower() or isinstance(err, KeyError) else (_ for _ in ()).throw(err)
    s = S.measure(root)["details"]
    return list(b), list(s["sites"]) + list(s["borrow_restore"])


CLEAN = '''
import asyncio
from dataclasses import replace

def helper(x, floor=None):
    return x > (floor or 0.0)

class HeatPumpOptimizerCoordinator:
    def __init__(self, hass):
        self.hass = hass
        self._current_state = None
        self._result = None

    async def _async_update_data(self):
        state = replace(self._current_state, room_temperature=20.0)
        self._current_state = state
        r = await self.hass.async_add_executor_job(helper, 1.0, 0.5)
        return {"r": r}

    async def async_run_optimization(self):
        r = await self.hass.async_add_executor_job(helper, 1.0)
        return r
'''

PERTURB = {
    "A": ("        return r\n", "        self._result = r\n        return r\n"),
    "B": ("        self._current_state = state\n", "        self._current_state = state\n        self._current_state.room_temperature = 21.0\n"),
    "C": ("        self._current_state = state\n", "        self._current_state = state\n        self._away.override_active = True\n"),
    "D": ("    return x > (floor or 0.0)\n", "    return x > (floor or 0.0)\n\ndef step(p):\n    setattr(helper, 'floor', p)\n"),
}


def fixture(perturb: str | None) -> Path:
    d = Path(tempfile.mkdtemp(prefix="nsc-fixture-"))
    pkg = d / PKG
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    src = CLEAN
    if perturb:
        a, b = PERTURB[perturb]
        assert a in src
        src = src.replace(a, b, 1)
    (pkg / "coordinator.py").write_text(src)
    return d


POSITIVE = {
    "D1-s1-02": ("A", "async_run_optimization awaits _await_optimize"),
    "D7-s1-51": ("B", "_current_state."),
    "D7-s1-52": ("C", "_away_state"),
    "D7-s1-53": ("C", "_flow_bias .heat_output_kw"),
    "D7-s3-54": ("D", "setattr planned_draw_runs"),
}


def main() -> None:
    args = sys.argv[1:]
    root = ROOT
    if "--root" in args:
        root = Path(args[args.index("--root") + 1]).resolve()
    if "--null" in args:
        root = fixture(None)
    if "--perturb" in args:
        root = fixture(args[args.index("--perturb") + 1])
    pkg = root / PKG
    fam = {"A": family_a(pkg), "D": family_d(pkg)}
    fam["B"], fam["C"] = families_bc(root)
    if "--json" in args:
        print(json.dumps(fam, indent=1))
        return
    for k in "ABCD":
        for s in fam[k]:
            print(f"SEAM {k} {s}")
    for fid, (k, needle) in POSITIVE.items():
        print(f"POSITIVE {fid} family={k} found={int(any(needle in s for s in fam[k]))}")
    for k in "ABCD":
        print(f"RESULT family_{k}={len(fam[k])} count")
    print(f"RESULT seams_total={sum(len(v) for v in fam.values())} count")


if __name__ == "__main__":
    main()
