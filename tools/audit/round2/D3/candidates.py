#!/usr/bin/env python3
"""D3 round 2 -- enumerate and sample deletion mutants over the production tree.

Metric: none (this is the sampler, not a measurement); it produces the
mutant pool and the seeded sample that tools/audit/round2/D3/prescreen.py
pre-screens.

Run from the repository root:

    PYTHONPATH=tests/hastub .venv/bin/python tools/audit/round2/D3/candidates.py \
        --seed 20260902 --n 36 --per-module 4 --out tools/audit/round2/D3

Baseline: c398fc84eec25fc44b60d74aae05b9a2da205884, 8-core Apple M1.

Site kinds and the deletion each one gets:
  guard_return   an `if` with no else whose body is only a bail-out
                 (return/raise/continue/break, optionally after one logging
                 call) -> the whole `if` block is deleted (guard never fires)
  clamp          min()/max()/np.clip()/np.minimum()/np.maximum() ->
                 replaced by its value argument (the bound is gone)
  except_handler `except X:` whose body does not re-raise -> `except ():`
                 (the handler never catches; the exception propagates)
  payload_key    `d["key"] = ...` inside a *_view / _build_data_dict /
                 extra_state_attributes function -> line deleted
  reason_code    `<list>.append("literal")` -> line deleted
  general_if     any other `if` with no else and a short body -> block deleted

Weights: module weight (consequence for a Pi-class user: money/comfort path
5, published values and config 3, learners 2, wording 1) x kind weight
(guard_return 3, clamp 3, except_handler 2, payload_key 2, reason_code 2,
general_if 1). Sampling is weighted without replacement, at most
--per-module sites per module, with numpy's default_rng(seed).
"""
from __future__ import annotations

import argparse
import ast
import difflib
import json
import os
import py_compile
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
PROD = ROOT / "custom_components" / "heatpump_optimizer"

MODULE_WEIGHT = {
    "optimizer.py": 5, "thermal_model.py": 5, "coordinator.py": 5,
    "tariff.py": 4, "grid_fee.py": 4, "dhw_schedule.py": 4, "inputs.py": 4,
    "power_guard.py": 4,
    "price_model.py": 3, "ledger.py": 3, "dhw_draws.py": 3, "external_heat.py": 3,
    "defrost.py": 3, "freq_control.py": 3, "pump_signals.py": 3,
    "pump_schedule.py": 3, "pump_mode.py": 3, "mixing_valve.py": 3,
    "comfort_band.py": 3, "away.py": 3, "manual_plan.py": 3,
    "config_flow.py": 3, "sensor.py": 3, "climate.py": 3, "__init__.py": 3,
    "comfort_learning.py": 2, "curve_learning.py": 2, "drift.py": 2,
    "accuracy.py": 2, "battery.py": 2, "pv.py": 2, "sysid.py": 2, "wear.py": 2,
    "snapshots.py": 2, "topology.py": 2, "presets.py": 2, "binary_sensor.py": 2,
    "switch.py": 2, "frontend.py": 2, "open_meteo.py": 2,
    "diagnosis.py": 1, "narrative.py": 1, "button.py": 1, "const.py": 1,
    "currency.py": 1,
}
KIND_WEIGHT = {
    "guard_return": 3, "clamp": 3, "except_handler": 2, "payload_key": 2,
    "reason_code": 2, "general_if": 1,
}
BAILOUT = (ast.Return, ast.Raise, ast.Continue, ast.Break)
CLAMP_NAMES = {"min", "max"}
CLAMP_ATTRS = {"clip", "minimum", "maximum"}


def _is_log_call(stmt: ast.stmt) -> bool:
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        return False
    f = stmt.value.func
    return isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and \
        f.value.id in ("_LOGGER", "LOGGER", "logger", "log")


def _seg(src: str, node: ast.AST) -> str:
    return ast.get_source_segment(src, node) or ""


def _contains(node: ast.AST, kinds) -> bool:
    return any(isinstance(n, kinds) for n in ast.walk(node))


class Enumerator(ast.NodeVisitor):
    def __init__(self, module: str, src: str) -> None:
        self.module = module
        self.src = src
        self.lines = src.splitlines(keepends=True)
        self.sites: list[dict] = []
        self.func_stack: list[str] = []

    def _add(self, kind: str, node: ast.AST, repl: dict, note: str = "") -> None:
        self.sites.append({
            "module": self.module, "kind": kind,
            "line": node.lineno, "end_line": node.end_lineno,
            "func": ".".join(self.func_stack) or "<module>",
            "text": _seg(self.src, node).splitlines()[0][:120],
            "repl": repl, "note": note,
        })

    def visit_FunctionDef(self, node):
        self.func_stack.append(node.name)
        self.generic_visit(node)
        self.func_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.func_stack.append(node.name)
        self.generic_visit(node)
        self.func_stack.pop()

    def visit_If(self, node: ast.If):
        test = _seg(self.src, node.test)
        if test in ("TYPE_CHECKING", '__name__ == "__main__"') or not self.func_stack:
            self.generic_visit(node)
            return
        if not node.orelse:
            body = node.body
            tail = body[-1]
            head = body[:-1]
            if isinstance(tail, BAILOUT) and (not head or (len(head) == 1 and _is_log_call(head[0]))):
                self._add("guard_return", node,
                          {"op": "delete_lines", "start": node.lineno, "end": node.end_lineno})
            elif len(body) <= 3 and not _contains(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._add("general_if", node,
                          {"op": "delete_lines", "start": node.lineno, "end": node.end_lineno})
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        f = node.func
        name = None
        if isinstance(f, ast.Name) and f.id in CLAMP_NAMES:
            name = f.id
        elif isinstance(f, ast.Attribute) and f.attr in CLAMP_ATTRS and \
                isinstance(f.value, ast.Name) and f.value.id == "np":
            name = "np." + f.attr
        if name and self.func_stack and len(node.args) >= 2 and not node.keywords and \
                not any(isinstance(a, ast.Starred) for a in node.args) and \
                node.lineno == node.end_lineno:
            args = node.args
            if name == "np.clip":
                value = args[0]
            else:
                non_const = [a for a in args if not isinstance(a, ast.Constant)]
                if len(non_const) == 1:
                    value = non_const[0]
                elif len(args) == 2 and all(isinstance(a, ast.Constant) for a in args):
                    value = None
                else:
                    value = args[0]
            if value is not None:
                self._add("clamp", node, {
                    "op": "replace_span",
                    "line": node.lineno, "col": node.col_offset, "end_col": node.end_col_offset,
                    "new": _seg(self.src, value),
                }, note=name)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is not None and self.func_stack and not _contains(node, ast.Raise) \
                and node.type.lineno == node.type.end_lineno == node.lineno:
            self._add("except_handler", node, {
                "op": "replace_span", "line": node.lineno,
                "col": node.type.col_offset, "end_col": node.type.end_col_offset, "new": "()",
            }, note=_seg(self.src, node.type))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        fn = self.func_stack[-1] if self.func_stack else ""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript) and \
                isinstance(node.targets[0].slice, ast.Constant) and \
                isinstance(node.targets[0].slice.value, str) and \
                node.lineno == node.end_lineno and \
                (fn.endswith("_view") or fn in ("_build_data_dict", "extra_state_attributes",
                                                "as_dict", "to_dict", "payload") or "payload" in fn):
            self._add("payload_key", node,
                      {"op": "delete_lines", "start": node.lineno, "end": node.end_lineno})
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr):
        v = node.value
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and v.func.attr == "append" \
                and len(v.args) == 1 and isinstance(v.args[0], ast.Constant) \
                and isinstance(v.args[0].value, str) and node.lineno == node.end_lineno and self.func_stack:
            self._add("reason_code", node,
                      {"op": "delete_lines", "start": node.lineno, "end": node.end_lineno})
        self.generic_visit(node)


def apply_repl(src: str, repl: dict) -> str:
    lines = src.splitlines(keepends=True)
    if repl["op"] == "delete_lines":
        s, e = repl["start"] - 1, repl["end"]
        out = lines[:s] + lines[e:]
        return "".join(out)
    if repl["op"] == "replace_span":
        i = repl["line"] - 1
        line = lines[i]
        lines[i] = line[:repl["col"]] + repl["new"] + line[repl["end_col"]:]
        return "".join(lines)
    raise ValueError(repl["op"])


def compiles(text: str) -> bool:
    try:
        compile(text, "<mutant>", "exec")
        return True
    except SyntaxError:
        return False


def mutate(src: str, repl: dict) -> str | None:
    """Apply the deletion; if an emptied block breaks the syntax, put `pass` there."""
    out = apply_repl(src, repl)
    if compiles(out):
        return out
    if repl["op"] == "delete_lines":
        lines = src.splitlines(keepends=True)
        first = lines[repl["start"] - 1]
        indent = first[: len(first) - len(first.lstrip())]
        s, e = repl["start"] - 1, repl["end"]
        out = "".join(lines[:s] + [indent + "pass\n"] + lines[e:])
        if compiles(out):
            return out
    return None


def enumerate_sites() -> list[dict]:
    sites = []
    for path in sorted(PROD.glob("*.py")):
        src = path.read_text()
        tree = ast.parse(src)
        en = Enumerator(path.name, src)
        en.visit(tree)
        sites.extend(en.sites)
    for i, s in enumerate(sites):
        s["site_id"] = i
        s["weight"] = MODULE_WEIGHT.get(s["module"], 1) * KIND_WEIGHT[s["kind"]]
    return sites


def sample(sites: list[dict], seed: int, n: int, per_module: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    w = np.array([s["weight"] for s in sites], dtype=float)
    picked: list[dict] = []
    per: dict[str, int] = {}
    alive = np.ones(len(sites), dtype=bool)
    tried = 0
    while len(picked) < n and alive.any():
        p = w * alive
        p = p / p.sum()
        i = int(rng.choice(len(sites), p=p))
        alive[i] = False
        tried += 1
        s = sites[i]
        if per.get(s["module"], 0) >= per_module:
            continue
        src = (PROD / s["module"]).read_text()
        out = mutate(src, s["repl"])
        if out is None or out == src:
            s["rejected"] = "does not compile / no-op"
            continue
        per[s["module"]] = per.get(s["module"], 0) + 1
        s = dict(s)
        s["draw"] = tried
        s["patch"] = "".join(difflib.unified_diff(
            src.splitlines(keepends=True), out.splitlines(keepends=True),
            fromfile="a/custom_components/heatpump_optimizer/" + s["module"],
            tofile="b/custom_components/heatpump_optimizer/" + s["module"],
        ))
        picked.append(s)
    return picked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--n", type=int, default=36)
    ap.add_argument("--per-module", type=int, default=4)
    ap.add_argument("--out", default=str(Path(__file__).parent))
    args = ap.parse_args()
    sites = enumerate_sites()
    picked = sample(sites, args.seed, args.n, args.per_module)
    out = Path(args.out)
    (out / "mutants").mkdir(parents=True, exist_ok=True)
    by_kind: dict[str, int] = {}
    by_mod: dict[str, int] = {}
    for s in sites:
        by_kind[s["kind"]] = by_kind.get(s["kind"], 0) + 1
        by_mod[s["module"]] = by_mod.get(s["module"], 0) + 1
    pool = {"seed": args.seed, "n_sites": len(sites), "by_kind": by_kind, "by_module": by_mod,
            "module_weight": MODULE_WEIGHT, "kind_weight": KIND_WEIGHT,
            "sites": [{k: v for k, v in s.items() if k != "patch"} for s in sites]}
    (out / "pool.json").write_text(json.dumps(pool, indent=1))
    manifest = []
    for k, s in enumerate(picked, 1):
        mid = f"M{k:02d}"
        (out / "mutants" / f"{mid}.patch").write_text(s["patch"])
        rec = {k2: v for k2, v in s.items() if k2 != "patch"}
        rec["id"] = mid
        manifest.append(rec)
        print(f"{mid} {s['module']}:{s['line']} {s['kind']:14s} w={s['weight']:2d} "
              f"{s['func']}: {s['text'][:70]}")
    (out / "sample.json").write_text(json.dumps(manifest, indent=1))
    print(f"RESULT n_sites={len(sites)} count")
    print(f"RESULT n_sampled={len(picked)} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
