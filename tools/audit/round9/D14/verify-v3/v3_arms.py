#!/usr/bin/env python3
"""Round-9 D14 verifier V3 (reach and class): independent measurements, one arm per finding.

Metric (one line per arm; each arm prints its own RESULT lines):
  p7grid   -- D14-s4-01: instants on a DST day (Europe/Stockholm, real zoneinfo, NOT the hastub
              clock) where production coordinator:HeatPumpOptimizerCoordinator._forecast_arrays
              hands _price_series a (midnight, step_offset) whose step-0 UTC instant differs from
              now floored to 15 min in UTC; control arms: same instants with tz=UTC and with a
              fixed-offset tzinfo (0 expected).
  p1leg    -- D14-s1-01: coordinator._build_data_dict / legionella calls that raise on the real-HA
              clock shape (HASTUB_TZ set => dt_util.now() aware ZoneInfo, as upstream) after
              LegionellaGuard.async_load reads a store holding a naive ISO timestamp in one leaf;
              control: every leaf aware.
  p2preset -- D14-s2-01: house_thermal_mass that production config_flow._derive_preset derives on
              two reachable entry shapes, divided by what it derives when two_zone follows
              ThermalParameters.from_config(...).two_zone_enabled.
  p8cur    -- D14-s2-02: the unit label vs the feed's money code for a price entity whose unit is
              EUR/kWh on an instance whose hass.config.currency is SEK (production
              inputs.normalize_price_per_kwh, currency.resolve_currency, coordinator._audit_price_units).
  p5grid   -- D14-s3-03: a magnitude grid of undeclared free heat (kW) the finder did not run
              (0.3, 0.5, 0.6, 1.0, 1.2) driven through the finder's plant driver; the smallest
              undeclared kW at which adoption_decision admits |UA err| > bar, per preset.
  closure  -- D14-s5-01: for every tracked tests/hastub/**.py file, whether production
              tests/closure.py:select([file]) is scoped with tests/deployment_shape.py skipped.
  i4       -- D14-s2-03: ledger class ids absent from scopes.json's D14 axis, read directly.
  p6       -- D14-s1-02: AST count of assignments to .horizon_hours / horizon_hours= keyword in
              the package, and of 'horizon_hours' string keys written in coordinator.py.
Command (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v3/v3_arms.py <arm>
  (p1leg re-execs itself with HASTUB_TZ=Europe/Stockholm)
Expected: counts, exact (no BLAS dependence except p5grid, +-1 cell).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence).
Machine: cloud container G3-V3, 4 cores, Linux, CPython 3.14.0rc2 (/home/claude/venv).
Perturbation per arm: p7grid tz=UTC / fixed offset (must fall to 0); p1leg all-aware store (0);
p2preset canonical predicate (ratio 1.0); closure --union folds hastub into deployment_shape's
closure in memory (must fall to 0).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402,F401

_T0 = (time.process_time(), time.thread_time())


def _tail():
    pc, tc = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


# --------------------------------------------------------------------------- p7grid
def arm_p7grid():
    from heatpump_optimizer import coordinator as cm
    step_min = cm.FORECAST_STEP_MINUTES
    days = {"spring2025": "2025-03-30", "autumn2025": "2025-10-26", "spring2026": "2026-03-29",
            "autumn2026": "2026-10-25", "spring2027": "2027-03-28", "autumn2027": "2027-10-31",
            "plain": "2026-03-22"}
    tzs = {"zoneinfo": ZoneInfo("Europe/Stockholm"), "utc": ZoneInfo("UTC"),
           "fixed+01": timezone(timedelta(hours=1))}

    class Self:
        _opt_config = SimpleNamespace(n_steps=96)

        def _price_series(self, n, midnight, offset):
            self.cap = (midnight, offset)
            return None

    fn = cm.HeatPumpOptimizerCoordinator._forecast_arrays
    for tzname, tz in tzs.items():
        total_bad = total = 0
        for label, day in days.items():
            y, m, d = map(int, day.split("-"))
            # every 15 min of the local day, walked in UTC so each instant is real
            start = datetime(y, m, d, tzinfo=tz).astimezone(timezone.utc)
            bad = n = 0
            skew_max = 0.0
            t = start
            while t.astimezone(tz).date() == datetime(y, m, d).date():
                now = t.astimezone(tz)
                s = Self()
                fn(s, now)
                midnight, off = s.cap
                first = cm._utc_step_starts(midnight, 1, off)[0]
                ts = now.timestamp()
                truth = ts - (ts % (step_min * 60))
                skew = (first.timestamp() - truth) / 60.0
                n += 1
                if abs(skew) > 1e-6:
                    bad += 1
                    skew_max = max(skew_max, abs(skew))
                t += timedelta(minutes=step_min)
            total_bad += bad
            total += n
            print(f"RESULT p7grid[{tzname}][{label}]={bad}_of_{n} instants skew_max={skew_max:.0f} min")
        print(f"RESULT p7grid_total[{tzname}]={total_bad}_of_{total} instants")


# --------------------------------------------------------------------------- p1leg
def arm_p1leg():
    if os.environ.get("HASTUB_TZ") != "Europe/Stockholm":
        env = dict(os.environ, HASTUB_TZ="Europe/Stockholm")
        return subprocess.call([sys.executable, __file__, "p1leg"], env=env)
    import traceback
    from harness import FakeEntry, FakeHass
    import golden
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    cfg = dict(golden.coordinator_scenarios()["coord_dhw"])
    cfg["dhw_legionella_enabled"] = True
    tz = ZoneInfo("Europe/Stockholm")
    aware = datetime(2026, 1, 14, 20, 0, tzinfo=tz).isoformat()
    naive = "2026-01-14T20:00:00"
    cases = {
        "control_all_aware": {"last_cycle": aware, "last_attempt": aware},
        "naive_last_cycle+aware_attempt": {"last_cycle": naive, "last_attempt": aware},
        "aware_last_cycle+naive_attempt": {"last_cycle": aware, "last_attempt": naive},
        "naive_last_cycle_only": {"last_cycle": naive},
        "naive_both": {"last_cycle": naive, "last_attempt": naive},
    }
    now_aware = type(dt_util.now()).__name__, dt_util.now().tzinfo is not None
    print(f"# dt_util.now() aware under HASTUB_TZ: {now_aware[1]}")
    raised = 0
    for name, stored in cases.items():
        hass = FakeHass()
        coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
        leg = coord._legionella

        async def _load(stored=stored):
            return dict(stored)
        leg.store.async_load = _load
        leg.async_save = (lambda: asyncio.sleep(0))
        asyncio.run(leg.async_load())
        fails = []
        for label, call in (("hours_since", leg.hours_since), ("due_in_hours", leg.due_in_hours),
                            ("_build_data_dict", coord._build_data_dict)):
            try:
                call()
            except Exception as err:  # noqa: BLE001
                tb = traceback.extract_tb(err.__traceback__)[-1]
                fails.append(f"{label}:{type(err).__name__}@{Path(tb.filename).name}:{tb.lineno}")
        if fails and not name.startswith("control"):
            raised += 1
        print(f"RESULT p1leg[{name}]={len(fails)} raising_calls {' '.join(fails)}")
    print(f"RESULT p1leg_raising_cases={raised}_of_{len(cases) - 1}")


# --------------------------------------------------------------------------- p2preset
def arm_p2preset():
    from heatpump_optimizer import config_flow as cf, const
    from heatpump_optimizer.thermal_model import ThermalParameters
    import inspect
    import textwrap
    answers = {const.CONF_BUILDING_STRUCTURE: "wood", const.CONF_BUILDING_ERA: "1976_1990",
               const.CONF_BUILDING_FOUNDATION: "slab", const.CONF_HEATED_AREA: 150.0}
    for k in list(answers):
        pass
    src = textwrap.dedent(inspect.getsource(cf._derive_preset))
    old = "two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),"
    assert src.count(old) == 1
    ns: dict = {}
    exec(compile(src.replace(old, "two_zone=ThermalParameters.from_config(dict(current)).two_zone_enabled,"),
                 cf.__file__, "exec"), dict(cf.__dict__, ThermalParameters=ThermalParameters), ns)
    canon = ns["_derive_preset"]
    shapes = {
        "mode_off+upper_key(entry.data survivor)": {const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_OFF,
                                                    const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0},
        "mode_on+no_upper_key": {const.CONF_TWO_ZONE_MODE: const.TWO_ZONE_MODE_ON},
        "auto+lower_key_only": {const.CONF_LOWER_FLOOR_THERMAL_MASS: 3.0},
        "control_auto+upper_key": {const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0},
        "control_auto+no_keys": {},
    }
    disagree = 0
    for name, cur in shapes.items():
        a = cf._derive_preset(dict(answers), cur)
        b = canon(dict(answers), cur)
        ha, hb = a.get("house_thermal_mass"), b.get("house_thermal_mass")
        ratio = (ha / hb) if (ha and hb) else float("nan")
        diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        if diff and not name.startswith("control"):
            disagree += 1
        print(f"RESULT p2preset[{name}] house_mass_ratio={ratio:.3f} keys_differing={len(diff)} {diff[:4]}")
    print(f"RESULT p2preset_disagree={disagree}_of_3 reachable shapes")


# --------------------------------------------------------------------------- p8cur
def arm_p8cur():
    from harness import FakeHass, FakeState
    from heatpump_optimizer import inputs, currency, coordinator as cm, const
    hass = FakeHass({"sensor.nordpool": FakeState("0.10", attributes={"unit_of_measurement": "EUR/kWh"})})
    hass.config.currency = "SEK"
    v = inputs.normalize_price_per_kwh(0.10, "EUR/kWh")
    label = currency.resolve_currency(hass)
    issues = []
    import homeassistant.helpers.issue_registry as ir
    orig = cm._create_issue
    cm._create_issue = lambda *a, **k: issues.append(a[2] if len(a) > 2 else k)
    try:
        cm._audit_price_units(hass, {const.CONF_PRICE_ENTITY: "sensor.nordpool"})
    finally:
        cm._create_issue = orig
    print(f"RESULT p8cur_value_after_normalize={v} (feed 0.10 EUR/kWh)")
    print(f"RESULT p8cur_label={label} mismatch={int(label != 'EUR')}")
    print(f"RESULT p8cur_repair_issues_raised={len(issues)}")
    lit = sum(1 for l in Path(cm.__file__).with_name("config_flow.py").read_text().splitlines()
              if "'SEK/m" in l or '"SEK/m' in l)
    print(f"RESULT p8cur_literal_SEK_units_in_config_flow={lit}")


# --------------------------------------------------------------------------- p5grid
def arm_p5grid():
    sys.path.insert(0, "tools/audit/round9/D14/s3")
    import p5_gate as G
    bar = float(G.S.UA_ADOPTION_HALFWIDTH_BAR)
    for name in ("typical_slab", "heavy_old"):
        p = G.preset(name)
        first_bad = None
        for mag in (0.3, 0.5, 0.6, 1.0, 1.2):
            r = G.drive(p, "gains", mag)
            err = r.get("err_log")
            adm = r.get("admit")
            hw = r.get("hw")
            over = err is not None and abs(err) > bar
            if adm and over and first_bad is None:
                first_bad = mag
            e = f"{(np.exp(err) - 1) * 100:+.2f}%" if err is not None else "na"
            print(f"CELL {name} gains mag={mag} admit={int(bool(adm))} err={e} hw={hw} why={r.get('why') or r.get('reason')}")
        print(f"RESULT p5grid_first_undeclared_kW_admitted_over_bar[{name}]={first_bad}")


# --------------------------------------------------------------------------- closure
def arm_closure():
    import closure
    files = subprocess.run(["git", "ls-files", "tests/hastub"], capture_output=True, text=True).stdout.split()
    files = [f for f in files if f.endswith(".py")]
    skipped = 0
    modes = {}
    for f in files:
        plan = closure.select([f])
        modes[plan["mode"]] = modes.get(plan["mode"], 0) + 1
        if plan["mode"] != "full" and "tests/deployment_shape.py" not in plan["run"]:
            skipped += 1
    print(f"RESULT closure_hastub_py_files={len(files)} count modes={modes}")
    print(f"RESULT closure_hastub_edit_skips_deployment_shape={skipped} count")
    # perturbation: every hastub file folded into deployment_shape's closure, in memory
    data = json.loads(closure.CLOSURES.read_text())
    data["closures"]["tests/deployment_shape.py"] = sorted(set(data["closures"]["tests/deployment_shape.py"]) | set(files))
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "closures.json"
    tmp.write_text(json.dumps(data))
    orig = closure.CLOSURES
    closure.CLOSURES = tmp
    try:
        sk = sum(1 for f in files if (lambda p: p["mode"] != "full" and "tests/deployment_shape.py" not in p["run"])(closure.select([f])))
    finally:
        closure.CLOSURES = orig
    print(f"RESULT closure_hastub_edit_skips_deployment_shape[perturbed:union]={sk} count")


# --------------------------------------------------------------------------- i4
def arm_i4():
    ledger = {k for k in json.loads(Path("tools/audit/bugclasses.json").read_text()) if not k.startswith("_")}
    scopes = json.loads(Path("tools/audit/scopes.json").read_text())
    found = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and o in ledger:
            found.add(o)
    walk(scopes.get("D14", scopes))
    print(f"RESULT i4_ledger_ids={len(ledger)} count")
    print(f"RESULT i4_ledger_ids_absent_from_scopes_D14={len(ledger - found)} count {sorted(ledger - found)}")


# --------------------------------------------------------------------------- p6
def arm_p6():
    pkg = Path("custom_components/heatpump_optimizer")
    assigns = kw = 0
    for f in pkg.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                tg = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in tg:
                    if isinstance(t, ast.Attribute) and t.attr == "horizon_hours":
                        assigns += 1
                    if isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and t.slice.value == "horizon_hours":
                        assigns += 1
            if isinstance(node, ast.keyword) and node.arg == "horizon_hours":
                kw += 1
            if isinstance(node, ast.Dict):
                for k in node.keys:
                    if isinstance(k, ast.Constant) and k.value == "horizon_hours" and f.name != "sensor.py":
                        assigns += 1
    print(f"RESULT p6_horizon_hours_writes={assigns} count (attr/subscript/dict-key outside sensor.py)")
    print(f"RESULT p6_horizon_hours_kwargs={kw} count")


# --------------------------------------------------------------------------- guards
def arm_guards():
    """D14-s5-02, own definition: (a) ast.If whose test spans >1 line and whose body's last
    statement is return/raise/continue/break; (b) np.clip(...) calls. Each counted uncovered when
    production tests/mutation_table.py:candidates yields no GUARD_OFF (a) / CLAMP_DROP (b) on it."""
    import mutation_table as mt
    pkg = Path("custom_components/heatpump_optimizer")
    exits = (ast.Return, ast.Raise, ast.Continue, ast.Break)
    a_tot = a_unc = b_tot = b_unc = 0
    for f in sorted(pkg.glob("*.py")):
        cands = list(mt.candidates(f.resolve()))
        g = {c["line"] for c in cands if c["kind"] == "GUARD_OFF"}
        cl = {c["line"] for c in cands if c["kind"] == "CLAMP_DROP"}
        for node in ast.walk(ast.parse(f.read_text())):
            if isinstance(node, ast.If) and node.test.end_lineno > node.test.lineno \
                    and isinstance(node.body[-1], exits):
                a_tot += 1
                a_unc += node.lineno not in g
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "clip" and isinstance(node.func.value, ast.Name) \
                    and node.func.value.id == "np":
                b_tot += 1
                b_unc += node.lineno not in cl
    print(f"RESULT guards_multiline_exit_if={a_tot} count uncovered={a_unc}")
    print(f"RESULT guards_np_clip={b_tot} count uncovered={b_unc}")


# --------------------------------------------------------------------------- p4alt
def arm_p4alt():
    """D14-s3-02, own definition: the finder's quick grid (8 cells) with the 'tight' arm at a
    MODERATE stop (ftol 1e-9, gtol 1e-7, maxiter 3000) instead of 1e-12/1e-9: if the shipped
    point is non-stationary, a 1000x tighter ftol than production's 1e-6 already moves it."""
    sys.path.insert(0, "tools/audit/round9/D14/s3")
    import p4_seeds as P4
    P4.TIGHT.clear()
    P4.TIGHT.update(ftol=1e-9, gtol=1e-7, maxiter=3000, maxfun=200000)
    sys.argv = [sys.argv[0], "--cells", "quick"]
    return P4.main()


if __name__ == "__main__":
    arm = sys.argv[1]
    rc = globals()[f"arm_{arm}"]()
    if not (arm == "p1leg" and os.environ.get("HASTUB_TZ") != "Europe/Stockholm"):
        _tail()
    sys.exit(rc or 0)
