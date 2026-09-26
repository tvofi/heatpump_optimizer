"""D14-s2 / class P2 -- one configuration fact decided twice: a seam re-derives a
presence-inferred fact from a proxy key instead of calling its canonical predicate.

Metric (one line): boundary configurations on which a production seam's delivered
  decision disagrees with the canonical predicate evaluated on the same config.
Count key: what the seam DELIVERS -- _derive_preset's derived dict (whether it
  carries the two-zone split, i.e. 'upper_floor_thermal_mass'), modbus_prefill
  .infer's suggestion dict -- against ThermalParameters.from_config(...)
  .two_zone_enabled on the config that seam's output is saved into. A fix may route
  the seam through the canonical predicate or through any equivalent; the count
  only reads the delivered output.

Canonical facts and their predicates (the proxy keys are EXTRACTED from the
predicate bodies by AST, not carried):
  two_zone_enabled  thermal_model.ThermalParameters.from_config (mode key + presence)
  dhw_enabled       thermal_model._dhw_enabled_from_config
  wood_furnace_on   wood_fuel.wood_furnace_on / wood_furnace_inferred

Command (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s2/p2_facts.py
  ... --seams [--ref <git ref>]   static enumeration (the seam rule); --ref reads
      the package at that commit (positive control: 3602b6ca^, the R7-D12-01 pre-fix)
  ... --selftest                  clean fixture (0) and one-line re-introduction (1)
Expected (baseline 1936d5ca), exact:
  derive_preset_disagree=20 of 40 cells; prefill_refused_or_missed=20 of 40;
  wood_picture_vs_model_disagree=2 of 21 (topology.describe_setup vs
  wood_fuel.wood_furnace_on). All three are 0 under the perturbation (each proxy
  read replaced in memory by its canonical predicate). Null control: on the 20
  cells where upper-key presence and the canonical verdict coincide, 0.
  Seam rule at baseline: 2 decision seams of two_zone_enabled, 11 of dhw_enabled,
  16 of wood_furnace_on (dispositioned in REPORT.md); at 3602b6ca^ two_zone is 3
  (the R7-D12-01 flow-target guard re-found). --selftest: clean 0, re-introduced 1.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: cloud container B8,
  4 cores, 15 GB, CPython 3.14.0rc2. Counts only: no timing.
Instrumented symbols: heatpump_optimizer.config_flow:_derive_preset,
  heatpump_optimizer.modbus_prefill:infer, heatpump_optimizer.config_flow:_prefill_errors,
  heatpump_optimizer.thermal_model:ThermalParameters.from_config.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import inspect
import itertools
import subprocess
import sys
import textwrap
import time
from pathlib import Path

sys.path.insert(0, "tests")
_P0, _T0 = time.process_time(), time.thread_time()
import harness  # noqa: E402,F401  (puts the package on sys.path)

from heatpump_optimizer import config_flow, const, modbus_prefill, thermal_model, wood_fuel  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

PKG = "custom_components/heatpump_optimizer"


# ------------------------------------------------------------------ static seam rule
def _conf_names(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id.startswith("CONF_"):
            out.add(n.id)
        elif isinstance(n, ast.Attribute) and n.attr.startswith("CONF_"):
            out.add(n.attr)
    return out


def canonical_facts(read):
    """{fact: (canonical function names, proxy CONF_ names)} extracted from the predicates."""
    tm = ast.parse(read(f"{PKG}/thermal_model.py"))
    wf = ast.parse(read(f"{PKG}/wood_fuel.py"))
    facts = {}
    for n in ast.walk(tm):
        if isinstance(n, ast.If):
            txt = ast.unparse(n)
            if "values['two_zone_enabled']" in txt and "CONF_TWO_ZONE_MODE" not in txt:
                facts.setdefault("two_zone_enabled", set()).update(_conf_names(n))
        if isinstance(n, ast.Assign) and "two_zone_mode" in ast.unparse(n.targets[0]):
            facts.setdefault("two_zone_enabled", set()).update(_conf_names(n.value))
        if isinstance(n, ast.FunctionDef) and n.name == "_dhw_enabled_from_config":
            facts["dhw_enabled"] = _conf_names(n)
    for n in ast.walk(wf):
        if isinstance(n, ast.FunctionDef) and n.name in ("wood_furnace_on", "wood_furnace_inferred"):
            facts.setdefault("wood_furnace_on", set()).update(_conf_names(n))
    canon = {"two_zone_enabled": {"from_config"}, "dhw_enabled": {"_dhw_enabled_from_config"},
             "wood_furnace_on": {"wood_furnace_on", "wood_furnace_inferred", "wood_fuel_ready"}}
    return {k: (canon[k], v) for k, v in facts.items()}


DECIDE = (ast.If, ast.IfExp, ast.While, ast.BoolOp, ast.Assert)


def _is_read(n):
    """`x.get(K...)`, `x[K]` (load), or `K in x`; returns the CONF_ name or None."""
    def key(e):
        if isinstance(e, ast.Name) and e.id.startswith("CONF_"):
            return e.id
        if isinstance(e, ast.Attribute) and e.attr.startswith("CONF_"):
            return e.attr
        return None
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args:
        return key(n.args[0])
    if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Load):
        return key(n.slice)
    if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], (ast.In, ast.NotIn)):
        return key(n.left)
    return None


def scan(read, files):
    facts = canonical_facts(read)
    seams = []
    for f in files:
        try:
            tree = ast.parse(read(f))
        except SyntaxError:
            continue
        parents = {}
        for p in ast.walk(tree):
            for c in ast.iter_child_nodes(p):
                parents[c] = p
        for n in ast.walk(tree):
            k = _is_read(n)
            if not k:
                continue
            # enclosing function and decision context
            fn, decides, cur = None, False, n
            while cur in parents:
                par = parents[cur]
                if isinstance(par, (ast.If, ast.IfExp, ast.While, ast.Assert)) and cur is par.test:
                    decides = True
                if isinstance(par, (ast.BoolOp, ast.UnaryOp)) and not decides:
                    decides = decides or isinstance(par, ast.BoolOp) or isinstance(par.op, ast.Not)
                if isinstance(par, ast.Call) and getattr(par.func, "id", None) == "bool":
                    decides = True
                if isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    fn = getattr(par, "name", "<lambda>")
                    break
                cur = par
            for fact, (canon, keys) in facts.items():
                if k in keys and decides and fn not in canon and not f.endswith("/const.py"):
                    seams.append((fact, f, n.lineno, fn, k))
    return facts, seams


def read_at(ref):
    if ref is None:
        return lambda p: Path(p).read_text(), sorted(str(p) for p in Path(PKG).glob("*.py"))
    files = subprocess.run(["git", "ls-tree", "--name-only", f"{ref}:{PKG}"], capture_output=True, text=True, check=True).stdout.split()
    return (lambda p: subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True, text=True, check=True).stdout,
            [f"{PKG}/{f}" for f in files if f.endswith(".py")])


# ------------------------------------------------------------------ dynamic probes
MASS_KEYS = [const.CONF_UPPER_FLOOR_THERMAL_MASS, const.CONF_LOWER_FLOOR_THERMAL_MASS,
             const.CONF_INTER_ZONE_TRANSFER, const.CONF_RADIATOR_POWER_FRACTION]
MODES = [None, const.TWO_ZONE_MODE_AUTO, const.TWO_ZONE_MODE_ON, const.TWO_ZONE_MODE_OFF, "bogus"]
# presence patterns: none, upper only, upper=0.0 (falsy but present), lower only,
# inter-zone only, radiator fraction only, upper+lower, all four.
PRESENCE = [(), ((0, 4.0),), ((0, 0.0),), ((1, 8.0),), ((2, 0.3),), ((3, 0.5),), ((0, 4.0), (1, 8.0)),
            ((0, 4.0), (1, 8.0), (2, 0.3), (3, 0.5))]
ANSWERS = {const.CONF_BUILDING_STRUCTURE: "timber_slab", const.CONF_BUILDING_ERA: "1980_2005",
           const.CONF_BUILDING_FOUNDATION: "none", const.CONF_HEATED_AREA: 150.0,
           const.CONF_UPPER_EMITTER: "radiators", const.CONF_LOWER_EMITTER: "radiators",
           const.CONF_BUILDING_PRESET_ENABLED: True}
SNAP = {"r4109": ("sensor.gchv_r4109", "0", 1.0)}  # water temperature control


def grid():
    for mode, pres in itertools.product(MODES, PRESENCE):
        cfg = {}
        if mode is not None:
            cfg[const.CONF_TWO_ZONE_MODE] = mode
        for i, v in pres:
            cfg[MASS_KEYS[i]] = v
        yield cfg


def probe(derive_preset, infer):
    cells = d_dis = p_bad = agree_cells = agree_bad = 0
    mass_err = []
    rows = []
    for cur in grid():
        cells += 1
        canon_now = ThermalParameters.from_config(dict(cur)).two_zone_enabled
        derived = derive_preset(dict(ANSWERS), dict(cur))
        saved = {**cur, **ANSWERS, **derived}
        canon_saved = ThermalParameters.from_config(saved).two_zone_enabled
        split = "upper_floor_thermal_mass" in derived
        dis = split != canon_saved
        d_dis += dis
        sugg = infer(SNAP, dict(cur))
        flow = sugg.get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND) == "flow"
        refused = bool(config_flow._prefill_errors(dict(sugg), dict(cur)).get(const.CONF_MIXING_VALVE_WRITE_TARGET_KIND))
        missed = canon_now and not flow
        bad = (flow and refused) or missed
        p_bad += bad
        # null-control subset: presence of the upper key agrees with the canonical verdict
        presence = bool(cur.get(const.CONF_UPPER_FLOOR_THERMAL_MASS))
        if presence == canon_now:
            agree_cells += 1
            agree_bad += dis or bad
        if dis:
            ref = config_flow.presets.derive(config_flow.presets.BuildingPreset(
                structure="timber_slab", era="1980_2005", foundation="none", heated_area_m2=150.0,
                upper_emitter="radiators", lower_emitter="radiators",
                upper_area_ratio=float(cur.get(const.CONF_UPPER_FLOOR_AREA_RATIO, const.DEFAULT_UPPER_FLOOR_AREA_RATIO)),
                two_zone=canon_saved))
            mass_err.append(derived["house_thermal_mass"] / ref["house_thermal_mass"])
        rows.append((cur, canon_now, canon_saved, split, flow, refused, missed))
    return cells, d_dis, p_bad, agree_cells, agree_bad, mass_err, rows


WOOD_KEYS = [const.CONF_WOOD_TANK_TOP_ENTITY, const.CONF_WOOD_TANK_BOTTOM_ENTITY, const.CONF_DHW_WOOD_COIL_ENABLED,
             const.CONF_EXTERNAL_HEAT_ENABLED, const.CONF_EXTERNAL_HEAT_ENTITY, const.CONF_VALVE_OUTLET_TEMP_ENTITY]


def wood_grid():
    for flag in (None, True, False):
        for k in [None] + WOOD_KEYS:
            cfg = {}
            if flag is not None:
                cfg[const.CONF_WOOD_FURNACE_ENABLED] = flag
            if k is not None:
                cfg[k] = True if k in (const.CONF_DHW_WOOD_COIL_ENABLED, const.CONF_EXTERNAL_HEAT_ENABLED) else "sensor.x"
            yield cfg


def wood_probe(describe):
    cells = dis = 0
    rows = []
    for cfg in wood_grid():
        cells += 1
        shown = describe(dict(cfg))["wood"]["present"]
        canon = wood_fuel.wood_furnace_on(dict(cfg))
        dis += shown != canon
        if shown != canon:
            rows.append((cfg, shown, canon))
    return cells, dis, rows


def perturbed(fn, old, new):
    """The production function recompiled in its own module with one line replaced."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert old in src, (fn.__name__, old)
    ns = dict(fn.__globals__)
    ns["ThermalParameters"] = ThermalParameters
    ns["wood_furnace_on"] = wood_fuel.wood_furnace_on
    exec(compile(src.replace(old, new), inspect.getsourcefile(fn), "exec"), ns)
    return ns[fn.__name__]


def selftest():
    clean = textwrap.dedent('''
        from .thermal_model import ThermalParameters
        def a(cfg):
            if ThermalParameters.from_config(cfg).two_zone_enabled:
                return 1
            return cfg.get(CONF_UPPER_FLOOR_THERMAL_MASS, 0.0)
    ''')
    dirty = clean.replace("if ThermalParameters.from_config(cfg).two_zone_enabled:", "if cfg.get(CONF_UPPER_FLOOR_THERMAL_MASS):")
    real = lambda p: Path(p).read_text()  # noqa: E731
    for name, text in (("clean", clean), ("reintroduced", dirty)):
        rd = lambda p, _t=text: _t if p == "fixture.py" else real(p)  # noqa: E731
        _, s = scan(rd, ["fixture.py"])
        print(f"RESULT selftest_seams[{name}]={len(s)} count")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    if "--seams" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
        rd, files = read_at(ref)
        facts, seams = scan(rd, files)
        for fact, (canon, keys) in facts.items():
            print(f"FACT {fact}: canonical {sorted(canon)} proxies {sorted(keys)}")
        for s in seams:
            print(f"SEAM {s[0]} {s[1]}:{s[2]} in {s[3]} reads {s[4]}")
        for fact in facts:
            print(f"RESULT seams[{fact}@{ref or 'worktree'}]={sum(1 for s in seams if s[0] == fact)} count")
        return
    cells, dd, pb, ac, ab, err, rows = probe(config_flow._derive_preset, modbus_prefill.infer)
    for r in rows:
        if (r[3] != r[2]) or (r[4] and r[5]) or r[6]:
            print("CELL", r)
    print(f"RESULT cells={cells} count")
    print(f"RESULT derive_preset_disagree={dd} count")
    print(f"RESULT prefill_refused_or_missed={pb} count")
    print(f"RESULT null_control_cells={ac} count")
    print(f"RESULT null_control_disagree={ab} count")
    if err:
        print(f"RESULT house_mass_ratio_min={min(err):.3f} ratio")
        print(f"RESULT house_mass_ratio_max={max(err):.3f} ratio")
    dp = perturbed(config_flow._derive_preset, "two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),",
                   "two_zone=ThermalParameters.from_config(dict(current)).two_zone_enabled,")
    ip = perturbed(modbus_prefill.infer, "found = {**_hot_water(snap), **_plant(snap, current)}",
                   "found = {**_hot_water(snap), **_plant_p(snap, current)}")
    pl = perturbed(modbus_prefill._plant, "if water and current.get(CONF_UPPER_FLOOR_THERMAL_MASS)",
                   "if water and ThermalParameters.from_config(dict(current)).two_zone_enabled")
    ip.__globals__["_plant_p"] = pl
    _, dd2, pb2, _, _, _, _ = probe(dp, ip)
    print(f"RESULT derive_preset_disagree[perturbed]={dd2} count")
    print(f"RESULT prefill_refused_or_missed[perturbed]={pb2} count")
    from heatpump_optimizer import topology
    wc, wd, wrows = wood_probe(topology.describe_setup)
    for r in wrows:
        print("WOODCELL", r)
    print(f"RESULT wood_cells={wc} count")
    print(f"RESULT wood_picture_vs_model_disagree={wd} count")
    dsp = perturbed(topology.describe_setup, "wood = _wood_tank_shown(config)", "wood = wood_furnace_on(config)")
    _, wd2, _ = wood_probe(dsp)
    print(f"RESULT wood_picture_vs_model_disagree[perturbed]={wd2} count")
    pc, tc = time.process_time() - _P0, time.thread_time() - _T0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = [l for l in Path("/proc/vmstat").read_text().splitlines() if l.startswith("pswpin")]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 'n/a'}")


if __name__ == "__main__":
    main()
