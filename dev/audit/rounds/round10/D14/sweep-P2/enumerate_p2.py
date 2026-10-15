"""Class P2 enumerator (round 10, D14 method steps 3-4): one fact, several local copies.

P2's property: a fact the package uses at several places has ONE owner the other places
call; no place decides it with its own copy of the rule. The round-10 findings in the
class are seven fact-families. This script lists every seam of each family across the
whole package (not only the judged sites), each from a static AST rule widened from the
finding's own seam_rule:

  F1 run_threshold   a numeric literal 0.05/0.1 compared against a power/draw value, or a
                     `threshold` default of that literal, instead of MIN_RUNNING_DRAW_KW
                     (D8-s1-01)
  F2 learner_gate    a learner fold (`.observe(`/`.fold(` on a coordinator learner) whose
                     enclosing function does not refuse on `_learning_frozen(...)` itself
                     (D7-s2-01)
  F3 cop_law_fork    a function that branches on `cop_flow_carnot`, i.e. holds its own
                     choice of COP law (D2-s2-01)
  F4 entry_resolve   a service handler that returns before it resolves its entry_id
                     through `_loaded_entries`/`_loaded_coordinators`/`_manual_targets`
                     (D10-s1-51)
  F5 clone           an archscore gapped clone class (C3 census), each a rule written
                     more than once (D7-s2-52..56, D7-s2-59)
  F6 hour_clock      a function that rounds hour*60 and reduces by 24*60 (D7-s2-57)
  F7 scrub_mixin     a package class defining a published entity property while not
                     descending from HeatPumpOptimizerEntity, so `__init_subclass__`
                     cannot scrub it (D7-s2-51, latent at baseline)

    python3 enumerate_p2.py                 # the working tree's package
    python3 enumerate_p2.py --fixture       # null control: a clean synthetic package
    python3 enumerate_p2.py --perturb       # one one-line re-introduction per family
                                            # on a temp copy; prints before/after counts
    python3 enumerate_p2.py --json          # seams as JSON
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
PKG = REPO / "custom_components" / "heatpump_optimizer"

POWERISH = re.compile(r"power|draw|raw_space|raw_dhw|_kw\b|\bkw\b|p_max|commanded", re.I)
RUN_LITERALS = (0.05, 0.1)
FOLD_ATTRS = {"observe", "fold"}
GATE_TOKEN = "_learning_frozen("
RESOLVERS = {"_loaded_entries", "_loaded_coordinators", "_manual_targets"}
PUBLISHED = ("native_value", "extra_state_attributes", "is_on", "current_temperature",
             "target_temperature", "hvac_action", "native_min_value", "native_max_value")


def _trees(pkg: Path):
    for p in sorted(pkg.glob("*.py")):
        yield p, ast.parse(p.read_text())


def _parents(tree):
    par = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            par[c] = n
    return par


def _enclosing_fn(node, par):
    while node in par:
        node = par[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node
    return None


def f1_run_threshold(pkg):
    out = []
    for p, tree in _trees(pkg):
        par = _parents(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(
                    n.ops[0], (ast.Gt, ast.GtE, ast.Lt, ast.LtE)):
                sides = [n.left, n.comparators[0]]
                lits = [s for s in sides if isinstance(s, ast.Constant) and s.value in RUN_LITERALS]
                other = [s for s in sides if s not in lits]
                if lits and other and POWERISH.search(ast.unparse(other[0])):
                    fn = _enclosing_fn(n, par)
                    out.append((p.stem, fn.name if fn else "<module>", n.lineno, ast.unparse(n)))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = n.args.args + n.args.kwonlyargs
                defs = [None] * (len(n.args.args) - len(n.args.defaults)) + list(n.args.defaults) + list(n.args.kw_defaults)
                for a, d in zip(args, defs):
                    if a.arg == "threshold" and isinstance(d, ast.Constant) and d.value in RUN_LITERALS:
                        out.append((p.stem, n.name, n.lineno, f"threshold={d.value}"))
    return out


def f2_learner_gate(pkg):
    out = []
    p = pkg / "coordinator.py"
    tree = ast.parse(p.read_text())
    par = _parents(tree)
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in FOLD_ATTRS):
            recv = ast.unparse(n.func.value)
            if not re.match(r"(self|coord)\._|draw_range$", recv):
                continue
            fn = _enclosing_fn(n, par)
            body = ast.unparse(fn) if fn else ""
            if GATE_TOKEN not in body:
                out.append(("coordinator", fn.name if fn else "<module>", n.lineno, f"{recv}.{n.func.attr}"))
    return out


def f3_cop_law_fork(pkg):
    out = []
    for p, tree in _trees(pkg):
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            inner = [g for g in ast.walk(fn) if g is not fn and isinstance(g, (ast.FunctionDef, ast.AsyncFunctionDef))]
            own = set(ast.walk(fn)) - {x for g in inner for x in ast.walk(g)}
            for n in own:
                if isinstance(n, (ast.If, ast.IfExp)) and "cop_flow_carnot" in ast.unparse(n.test):
                    out.append((p.stem, fn.name, fn.lineno, ast.unparse(n.test)[:80]))
                    break
    return out


def f4_entry_resolve(pkg):
    out = []
    p = pkg / "services.py"
    if not p.exists():
        return out
    tree = ast.parse(p.read_text())
    for fn in tree.body:
        if not (isinstance(fn, ast.AsyncFunctionDef) and fn.name.startswith("handle_")):
            continue
        first = None
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in RESOLVERS:
                first = n.lineno if first is None else min(first, n.lineno)
        if first is None:
            continue  # the handler resolves no entry at all
        for n in ast.walk(fn):
            if isinstance(n, ast.Return) and n.lineno < first and not any(
                    isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in RESOLVERS
                    for c in ast.walk(n)):
                out.append(("services", fn.name, n.lineno, ast.unparse(n)[:80]))
    return out


def f5_clone(pkg):
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore import counters as K  # noqa: E402
    from archscore import vector  # noqa: E402
    root = pkg.parent.parent
    with tempfile.TemporaryDirectory() as tmp:
        flat = Path(tmp)
        K.flatten(root, flat, inline=True)
        S = vector.load_structure(flat)
        trees = [(q, ast.parse(q.read_text())) for q in sorted(S.PACKAGE_DIR.glob("*.py"))]
        groups = K.gapped_clones(S, trees)
    out = []
    for g in sorted(groups, key=lambda g: (-len(g), g)):
        head = g[0]
        members = " | ".join(f"{r.split('/')[-1].removesuffix('.py')}:{f}:{ln}" for r, f, ln in g)
        out.append((head[0].split("/")[-1].removesuffix(".py"), head[1], head[2], f"[{len(g)}] {members}"))
    return out


def _is_clock(fn) -> bool:
    has_round = has_day = False
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "round" and n.args:
            a = n.args[0]
            if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Mult) and any(
                    isinstance(x, ast.Constant) and x.value in (60, 60.0) for x in (a.left, a.right)):
                has_round = True
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult) and ast.unparse(n) == "24 * 60":
            has_day = True
    return has_round and has_day


def f6_hour_clock(pkg):
    out = []
    for p, tree in _trees(pkg):
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_clock(fn):
                inner = [g for g in ast.walk(fn) if g is not fn and isinstance(g, ast.FunctionDef) and _is_clock(g)]
                if not inner:
                    out.append((p.stem, fn.name, fn.lineno, "round(h*60) % (24*60)"))
    return out


def f7_scrub_mixin(pkg):
    classes = {}
    for p, tree in _trees(pkg):
        for c in tree.body:
            if isinstance(c, ast.ClassDef):
                classes[c.name] = (p.stem, c, [ast.unparse(b).split(".")[-1].split("[")[0] for b in c.bases])

    def descends(name, seen=()):
        if name == "HeatPumpOptimizerEntity":
            return True
        if name not in classes or name in seen:
            return False
        return any(descends(b, seen + (name,)) for b in classes[name][2])

    def is_entityish(name, seen=()):
        # a class HA treats as an entity: it (transitively) names an HA entity base
        if name in seen:
            return False
        if name not in classes:
            return name.endswith("Entity")
        return any(is_entityish(b, seen + (name,)) for b in classes[name][2])

    out = []
    for name, (stem, c, bases) in classes.items():
        props = [f.name for f in c.body if isinstance(f, ast.FunctionDef) and f.name in PUBLISHED
                 and any(ast.unparse(d) == "property" for d in f.decorator_list)]
        used_as_base = any(name in b and descends(o) for o, (_s, _c, b) in classes.items())
        if props and not descends(name) and (is_entityish(name) or used_as_base):
            # a mixin, or an entity outside the base: either way the scrub cannot see it
            out.append((stem, name, c.lineno, ",".join(props) + (" (entity)" if is_entityish(name) else " (mixin)")))
    return out


FAMILIES = {
    "F1_run_threshold": f1_run_threshold,
    "F2_learner_gate": f2_learner_gate,
    "F3_cop_law_fork": f3_cop_law_fork,
    "F4_entry_resolve": f4_entry_resolve,
    "F5_clone": f5_clone,
    "F6_hour_clock": f6_hour_clock,
    "F7_scrub_mixin": f7_scrub_mixin,
}


def enumerate_all(pkg):
    return {k: f(pkg) for k, f in FAMILIES.items()}


# ---- null control: a clean package where every fact has one owner -----------------------

CLEAN = {
    "manifest.json": "{}",
    "thermal_model.py": (
        "MIN_RUNNING_DRAW_KW = 0.1\n"
        "def is_running(space_kw, dhw_kw):\n    return space_kw + dhw_kw > MIN_RUNNING_DRAW_KW\n"
        "def compute_cop(params, t):\n    return law(params, t)\n"
        "def compute_cop_dhw(params, t):\n    return law(params, t)\n"
        "def law(params, t):\n    return 3.0 + 0.0 * t\n"
    ),
    "coordinator.py": (
        "from .thermal_model import MIN_RUNNING_DRAW_KW\n"
        "class HeatPumpOptimizerCoordinator:\n"
        "    def _observe_frequency(self):\n"
        "        if self._learning_frozen('power') is not None:\n            return\n"
        "        self._freq_map.observe(1.0)\n"
        "    def _plan_slots(self, power, threshold=MIN_RUNNING_DRAW_KW):\n"
        "        return [p > threshold for p in power]\n"
    ),
    "services.py": (
        "def _loaded_entries(hass, eid):\n    return [eid]\n"
        "async def handle_apply_schedule(hass, call):\n"
        "    targets = _loaded_entries(hass, call.data.get('entry_id'))\n"
        "    if not call.data:\n        return {'updated': {}}\n"
        "    return {'updated': targets}\n"
    ),
    "clock.py": "def wall_clock(h):\n    return int(h) % 24\n",
    "entity.py": (
        "class HeatPumpOptimizerEntity:\n    pass\n"
        "class Mixin(HeatPumpOptimizerEntity):\n"
        "    @property\n    def native_value(self):\n        return 1\n"
    ),
}


def _write_clean(root: Path) -> Path:
    pkg = root / "custom_components" / "heatpump_optimizer"
    pkg.mkdir(parents=True)
    for name, text in CLEAN.items():
        (pkg / name).write_text(text)
    return pkg


# ---- perturbation: one line re-introduces one seam per family ------------------------------

PERTURB = {
    # (file, old, new): each is a one-line edit on a temp copy
    "F1_run_threshold": ("optimizer.py", "power: np.ndarray, threshold: float = MIN_RUNNING_DRAW_KW",
                         "power: np.ndarray, threshold: float = 0.05"),
    "F2_learner_gate": ("coordinator.py", "    if coord._learning_frozen(CONF_OUTDOOR_TEMP_ENTITY) is not None:\n",
                        "    if False:\n"),
    "F3_cop_law_fork": ("thermal_model.py", "        if self.params.cop_flow_carnot:\n            # #1530",
                        "        if self.params.cop_flow_carnot:\n            # #1530"),  # replaced below
    "F4_entry_resolve": ("services.py", "    targets = _loaded_entries(hass, target_entry)\n",
                         "    if not data: return {}\n    targets = _loaded_entries(hass, target_entry)\n"),
    "F6_hour_clock": ("grid_fee.py", "\n\ndef ", "\n\ndef _p2_perturb_clock(h):\n    m = round(h * 60) % (24 * 60)\n    return m\n\n\ndef "),
    # a sensor takes native_value from a mixin outside the entity base (arch-s2 patch 01's shape)
    "F7_scrub_mixin": ("sensor.py", "\n\nclass ",
                       "\n\nclass _P2Mixin:\n    @property\n    def native_value(self): return float('nan')\n"
                       "class _P2Sensor(_P2Mixin, HeatPumpOptimizerEntity): pass\n\n\nclass "),
}


def _perturb(family: str):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copytree(PKG.parent.parent, root, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".git", "tests", "dev", "docs", "node_modules", "__pycache__"))
        shutil.copytree(REPO / "tools", root / "tools", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
        pkg = root / "custom_components" / "heatpump_optimizer"
        before = len(FAMILIES[family](pkg))
        if family == "F3_cop_law_fork":
            # one line: compute_cop_space_alt re-reads the flag with its own law
            f = pkg / "thermal_model.py"
            f.write_text(f.read_text() + "\n\ndef _p2_perturb_cop(p, t):\n    return 3.0 if p.cop_flow_carnot else 2.5\n")
        elif family == "F5_clone":
            # a second copy of a rule that has one today: thermal_model._flow_curve_values
            f = pkg / "thermal_model.py"
            src = f.read_text()
            tree = ast.parse(src)
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_flow_curve_values")
            seg = ast.get_source_segment(src, fn).replace("def _flow_curve_values", "def _p2_perturb_curve", 1)
            f.write_text(src + "\n\n" + seg + "\n")
        else:
            fname, old, new = PERTURB[family]
            f = pkg / fname
            src = f.read_text()
            assert old in src, (family, old)
            f.write_text(src.replace(old, new, 1))
        after = len(FAMILIES[family](pkg))
    return before, after


# positive control: every judged finding's site, as (family, substring of a seam line)
POSITIVE = {
    "D8-s1-01": [("F1_run_threshold", "coordinator:_build_plan_views"), ("F1_run_threshold", "coordinator:_plan_slots"),
                 ("F1_run_threshold", "sensor:native_value")],
    "D7-s2-01": [("F2_learner_gate", "coordinator:_observe_frequency")],
    "D2-s2-01": [("F3_cop_law_fork", "thermal_model:compute_cop_dhw")],
    "D10-s1-51": [("F4_entry_resolve", "services:handle_apply_schedule")],
    "D7-s2-52": [("F5_clone", "[11] sensor:native_value:543"), ("F5_clone", "[4] sensor:native_value:478")],
    "D7-s2-53": [("F5_clone", "[5] sensor:native_value:2463"), ("F5_clone", "sensor:native_value:2776")],
    "D7-s2-54": [("F5_clone", "climate:extra_state_attributes:231")],
    "D7-s2-55": [("F5_clone", "config_flow:_options_suggested_numeric")],
    "D7-s2-56": [("F5_clone", "config_flow:async_step_building"), ("F5_clone", "config_flow:async_step_grid:"),
                 ("F5_clone", "config_flow:async_step_grid_connection")],
    "D7-s2-57": [("F6_hour_clock", "dhw_draws:_fmt"), ("F6_hour_clock", "dhw_schedule:fmt"),
                 ("F6_hour_clock", "pump_arbiter:_night_clock"), ("F6_hour_clock", "quiet_windows:_gchv_at"),
                 ("F6_hour_clock", "quiet_windows:_fmt")],
    "D7-s2-59": [("F5_clone", "grid_fee:parse_day_range")],
    # D7-s2-51 is latent at baseline (escapes 0); its control is --perturb F7 (arch-s2 patch 01's shape)
}


def main(argv):
    if "--control" in argv:
        res = enumerate_all(PKG)
        lines = {k: [f"{s[0]}:{s[1]}:{s[2]}  {s[3]}" for s in v] for k, v in res.items()}
        missed = 0
        for fid, wants in POSITIVE.items():
            for fam, sub in wants:
                hit = any(sub in ln for ln in lines[fam])
                missed += not hit
                print(f"{'HIT ' if hit else 'MISS'} {fid} {fam} {sub}")
        print(f"RESULT control.findings={len(POSITIVE)} count")
        print(f"RESULT control.missed_sites={missed} count")
        return 0
    as_json = "--json" in argv
    if "--fixture" in argv:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = _write_clean(Path(tmp))
            shutil.copytree(REPO / "tools", Path(tmp) / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            res = {k: f(pkg) for k, f in FAMILIES.items()}
        for k, v in res.items():
            print(f"RESULT fixture.{k}={len(v)} count")
        print(f"RESULT fixture.total={sum(len(v) for v in res.values())} count")
        return 0
    if "--perturb" in argv:
        for fam in FAMILIES:
            b, a = _perturb(fam)
            print(f"RESULT perturb.{fam} before={b} after={a} moved={a - b}")
        return 0
    res = enumerate_all(PKG)
    if as_json:
        print(json.dumps({k: [list(s) for s in v] for k, v in res.items()}, indent=1))
        return 0
    for k, v in res.items():
        for s in v:
            print(f"SEAM {k} {s[0]}:{s[1]}:{s[2]}  {s[3]}")
    for k, v in res.items():
        print(f"RESULT {k}={len(v)} count")
    print(f"RESULT seams_total={sum(len(v) for v in res.values())} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
