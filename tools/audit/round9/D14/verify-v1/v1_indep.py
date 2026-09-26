#!/usr/bin/env python3
"""Round-9 D14 verifier V1: independent own-metric probes, one arm per finding.

Metric definitions (one line each; each arm prints its own RESULT lines):
  p1   legionella_raises[arm]  = LegionellaGuard.hours_since() calls that raise after async_load of a
       dhw_legionella store whose last_cycle/last_attempt carry the named awareness mix (arm both_aware = null)
  p6   horizon_hours_produced  = coordinator scenarios (golden.coordinator_scenarios, 5) whose
       _build_data_dict() payload holds the key 'horizon_hours'; boost_calls_on_real_coord = 1 if the real
       coordinator has the attribute boost.set_channel probes
  p2   derive_split_vs_canon   = configs of a 4-mode x 3-presence grid on which 'upper_floor_thermal_mass'
       in config_flow._derive_preset's output != ThermalParameters.from_config(saved).two_zone_enabled;
       wood_vs_canon = configs where topology.describe_setup(cfg)['wood']['present'] != wood_fuel.wood_furnace_on
  p8   eur_feed_on_sek_unit    = 1 when inputs.normalize_price_per_kwh(0.10,'EUR/kWh') returns 0.10 (code dropped),
       coordinator._audit_price_units raises no issue, and CurrentPriceSensor's unit is 'SEK/kWh'
  i4   p11_on_d14_axis / regex_admits = ledger ids absent from scopes.json D14 axis; my own id/class cases
       that the intake CLASS_GUESS + startsWith rule admits and finding.schema.json's pattern/enum refuses
  p7   grid_step0_off_min      = minutes between the first _utc_step_starts label built from
       coordinator._forecast_arrays' own (midnight, step_offset) and the 15-min floor of now, per half-hour
       instant on 2026-03-29 / 2026-10-25 Europe/Stockholm (null: 2026-03-22)
  rp   replay_tz_fixed         = 1 when tests/replay.py:_ts returns a fixed-offset tzinfo (not ZoneInfo), and
       wall_minus_utc_s        = (b-a) - (b.ts-a.ts) for two _ts instants straddling the spring transition
  s5   select_skips_deployment = 1 when closure.select([<hastub file>]) is scoped and does not run
       tests/deployment_shape.py; hastub_in_closure = count of tests/hastub files in its closure
  s5g  clip_lines_uncovered    = np.clip/np.minimum/np.maximum call lines in the package with no
       mutation_table.candidates() site on that line
  p4   re-aggregation of p4_seeds.py CELL lines (file arg): tgap misses, leave-one-out by profile
  p5   re-aggregation of P5_JSON rows (file arg): admitted with |err_log|>ln1.1; Spearman(|err|, hw) on gains

Command (repository root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v1/v1_indep.py --arm <arm> [file]
Expected at 1936d5ca (exact): p1 both_aware 0, naive_last 1, naive_attempt 1; p6 produced 0/5; p2 >0 split,
  wood 2; p8 1; i4 missing 1; p7 spring/autumn max 60, plain 0; rp fixed 1; s5 skips 1, hastub 0; s5g >0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 + round-9 evidence. Machine: cloud container, 4 cores,
CPython 3.14.0rc2, numpy 2.4.6. Counts only: timing not measured.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import sys
import time
sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
import asyncio
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

logging.disable(logging.CRITICAL)
T0P, T0T = time.process_time(), time.thread_time()
STO = ZoneInfo("Europe/Stockholm")


def tail():
    pc, tc = time.process_time() - T0P, time.thread_time() - T0T
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a")


def arm_p1():
    from harness import FakeEntry, FakeHass
    from homeassistant.helpers import storage
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    now = datetime(2026, 1, 15, 12, 0, tzinfo=STO)
    aware = (now - timedelta(days=3)).isoformat()
    naive = (now - timedelta(days=3)).replace(tzinfo=None).isoformat()
    cases = {"both_aware": (aware, aware), "naive_last": (naive, aware),
             "naive_attempt": (aware, naive), "both_naive": (naive, naive)}
    # real Home Assistant's as_utc reads a naive value as DEFAULT_TIME_ZONE; run both readings
    real_as_utc = lambda v: v if v.tzinfo == timezone.utc else (
        v.replace(tzinfo=STO) if v.tzinfo is None else v).astimezone(timezone.utc)
    for reading, fn in (("stub", dt_util.as_utc), ("ha_local", real_as_utc)):
        for name, (last, att) in cases.items():
            storage._DISK.clear()
            storage._DISK["heatpump_optimizer_test_entry_dhw_legionella"] = json.dumps(
                {"last_cycle": last, "last_attempt": att, "last_attempt_peak": 50.0})
            dt_util.freeze(now)
            orig = dt_util.as_utc
            dt_util.as_utc = fn
            try:
                coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"target_temperature": 21.0}))
                g = coord._legionella
                asyncio.run(g.async_load())
                raised = 0
                try:
                    g.hours_since()
                except Exception as e:  # noqa: BLE001
                    raised = 1
                    etype = type(e).__name__
                print(f"RESULT legionella_raises[{reading}:{name}]={raised} count"
                      + (f" ({etype})" if raised else ""))
            finally:
                dt_util.as_utc = orig


def arm_p6():
    import golden
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
    from harness import FakeEntry, FakeHass
    from homeassistant.util import dt as dt_util
    dt_util.freeze(golden.START)
    produced = 0
    scen = golden.coordinator_scenarios()
    for name, cfg in scen.items():
        data = golden._capture_coordinator(cfg)["data"]
        produced += "horizon_hours" in data
    print(f"RESULT horizon_hours_produced={produced}/{len(scen)} count")
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"target_temperature": 21.0}))
    print(f"RESULT boost_calls_on_real_coord={int(hasattr(c, 'boost_calls'))} count")
    import harness
    print(f"RESULT boost_calls_on_FakeCoordinator={int('boost_calls' in Path(harness.__file__).read_text())} count")


def arm_p2():
    from heatpump_optimizer import config_flow, const, topology, wood_fuel
    from heatpump_optimizer.thermal_model import ThermalParameters
    answers = {const.CONF_BUILDING_STRUCTURE: "timber_slab", const.CONF_BUILDING_ERA: "1980_2005",
               const.CONF_BUILDING_FOUNDATION: "none", const.CONF_HEATED_AREA: 120.0,
               const.CONF_UPPER_EMITTER: "radiators", const.CONF_LOWER_EMITTER: "floor"}
    modes = [None, const.TWO_ZONE_MODE_AUTO, const.TWO_ZONE_MODE_ON, const.TWO_ZONE_MODE_OFF]
    pres = {"none": {}, "upper": {const.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0},
            "lower": {const.CONF_LOWER_FLOOR_THERMAL_MASS: 7.0}}
    per_mode = {}
    total = 0
    for m in modes:
        for pn, p in pres.items():
            cur = dict(p)
            if m is not None:
                cur[const.CONF_TWO_ZONE_MODE] = m
            d = config_flow._derive_preset(dict(answers), dict(cur))
            canon = ThermalParameters.from_config({**cur, **answers, **d}).two_zone_enabled
            dis = (const.CONF_UPPER_FLOOR_THERMAL_MASS in d) != canon
            total += dis
            per_mode[str(m)] = per_mode.get(str(m), 0) + dis
            if dis:
                print(f"# disagree mode={m} presence={pn} split={const.CONF_UPPER_FLOOR_THERMAL_MASS in d} canon={canon}")
    print(f"RESULT derive_split_vs_canon={total}/12 count")
    for k, v in per_mode.items():
        print(f"RESULT derive_split_vs_canon[mode={k}]={v} count")
    wood = 0
    for cfg in ({const.CONF_VALVE_OUTLET_TEMP_ENTITY: "sensor.v"}, {const.CONF_DHW_WOOD_COIL_ENABLED: True},
                {const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.t"}, {}):
        shown = topology.describe_setup(dict(cfg))["wood"]["present"]
        canon = wood_fuel.wood_furnace_on(dict(cfg))
        wood += shown != canon
        print(f"# wood cfg={list(cfg)} shown={shown} canon={canon}")
    print(f"RESULT wood_vs_canon={wood}/4 count")


def arm_p8():
    from harness import FakeEntry, FakeHass, FakeState
    from heatpump_optimizer import coordinator as cm, inputs, sensor
    v = inputs.normalize_price_per_kwh(0.10, "EUR/kWh")
    hass = FakeHass()
    hass.config.currency = "SEK"
    hass.states.set("sensor.np", FakeState("0.10", attributes={"unit_of_measurement": "EUR/kWh"}))
    created = []
    orig = cm._create_issue
    cm._create_issue = lambda *a, **k: created.append(a[2] if len(a) > 2 else k)
    try:
        cm._audit_price_units(hass, {cm.CONF_PRICE_ENTITY: "sensor.np"})
    finally:
        cm._create_issue = orig
    coord = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data={"target_temperature": 21.0,
                                                                   cm.CONF_PRICE_ENTITY: "sensor.np"}))
    unit = sensor.CurrentPriceSensor(coord, FakeEntry()).native_unit_of_measurement
    print(f"# normalize={v} issues={created} unit={unit}")
    print(f"RESULT eur_feed_on_sek_unit={int(v == 0.10 and not created and unit == 'SEK/kWh')} count")
    # null: SEK feed on SEK instance publishes the correct label
    print(f"RESULT null_sek_feed_label_ok={int(inputs.normalize_price_per_kwh(0.10, 'SEK/kWh') == 0.10 and unit.startswith('SEK'))} count")


def arm_i4():
    ledger = [k for k in json.load(open("tools/audit/bugclasses.json")) if not k.startswith("_")]
    axis = json.load(open("tools/audit/scopes.json"))["D14"]["axis"]["class"]
    seats = {c for s in json.load(open("tools/audit/scopes.json"))["D14"]["seats"].values() for cell in s for c in cell["axis"]}
    print(f"RESULT ledger_not_on_axis={len(set(ledger) - set(axis))} count ({sorted(set(ledger) - set(axis))})")
    print(f"RESULT ledger_no_seat={len(set(ledger) - seats)} count")
    schema = json.load(open("tools/audit/finding.schema.json"))
    fnd = schema["definitions"]["finding"]["properties"]
    idpat = re.compile(fnd["id"]["pattern"])
    enum = set(fnd["class_guess"].get("enum", []))
    src = Path(".claude/workflows/audit-find.js").read_text()
    cg = re.compile(re.search(r"const CLASS_GUESS = /(.+)/\n", src).group(1))
    seat = "D14-s1"
    cases = [("D14-s1-03", "P13"), ("D14-s1-3", "P1"), ("D14-s1-003", "I2"), ("D14-s1-07", "I9"),
             ("D14-s1-08", "P1"), ("D14-s1-09", "new")]
    disagree = 0
    for fid, cls in cases:
        intake = fid.startswith(f"{seat}-") and bool(cg.match(cls))
        sch = bool(idpat.match(fid)) and cls in enum
        disagree += intake and not sch
    print(f"RESULT my_cases_intake_admits_schema_refuses={disagree}/{len(cases)} count")


def arm_p7():
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer import coordinator as cm
    captured = {}
    fake = SimpleNamespace(_opt_config=SimpleNamespace(n_steps=96))
    fake._ctx = fake
    fake._price_series = lambda n, mid, off: captured.update(mid=mid, off=off) or None
    for label, day in (("spring", (2026, 3, 29)), ("autumn", (2026, 10, 25)), ("plain", (2026, 3, 22))):
        worst = skewed = 0
        for k in range(48):
            utc0 = datetime(*day, tzinfo=STO).astimezone(timezone.utc)
            now = (utc0 + timedelta(minutes=30 * k)).astimezone(STO)
            now = now.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE) if dt_util.DEFAULT_TIME_ZONE else now
            cm.HeatPumpOptimizerCoordinator._forecast_arrays(fake, now)
            s0 = cm._utc_step_starts(captured["mid"], 1, captured["off"])[0]
            floor = now.timestamp() - (now.timestamp() % (cm.FORECAST_STEP_MINUTES * 60))
            off = abs(s0.timestamp() - floor) / 60.0
            worst = max(worst, off)
            skewed += off > 0
        print(f"RESULT grid_step0_off_min[{label}]={worst:.0f} minutes; skewed_instants={skewed}/48")


def arm_rp():
    import replay
    a = replay._ts("2026-03-29T01:00:00+01:00")
    b = a + timedelta(hours=3)
    print(f"RESULT replay_tz_fixed={int(not isinstance(a.tzinfo, ZoneInfo))} count ({type(a.tzinfo).__name__})")
    print(f"RESULT wall_minus_utc_s[fixed]={(b - a).total_seconds() - (b.timestamp() - a.timestamp()):.0f} s")
    az = a.astimezone(STO)
    bz = (az.astimezone(timezone.utc) + timedelta(hours=3)).astimezone(STO)
    print(f"RESULT wall_minus_utc_s[zoneinfo]={(bz - az).total_seconds() - (bz.timestamp() - az.timestamp()):.0f} s")


def arm_s5():
    import closure
    plan = closure.select(["tests/hastub/homeassistant/helpers/update_coordinator.py"])
    ran = "tests/deployment_shape.py" in plan.get("run", [])
    print(f"# mode={plan.get('mode')} run={len(plan.get('run', []))}")
    print(f"RESULT select_skips_deployment={int(plan.get('mode') == 'scoped' and not ran)} count")
    cl = json.load(open("tests/closures.json"))["closures"].get("tests/deployment_shape.py", {})
    files = cl.get("files", cl) if isinstance(cl, dict) else cl
    print(f"RESULT hastub_in_deployment_closure={sum(1 for f in files if str(f).startswith('tests/hastub'))} count")
    src = Path("tests/deployment_shape.py").read_text()
    print(f"RESULT deployment_spawns_driver={int('--driver' in src and 'subprocess' in src)} count")


def arm_s5g():
    import ast
    import mutation_table as mt
    pkg = Path("custom_components/heatpump_optimizer")
    unc = tot = 0
    for f in sorted(pkg.glob("*.py")):
        lines = {c["line"] for c in mt.candidates(f)}
        for n in ast.walk(ast.parse(f.read_text())):
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("clip", "minimum", "maximum")
                    and isinstance(n.func.value, ast.Name) and n.func.value.id in ("np", "numpy")):
                tot += 1
                unc += n.lineno not in lines
    print(f"RESULT np_clamp_calls={tot} count")
    print(f"RESULT np_clamp_lines_uncovered={unc} count")


def arm_p4(path):
    rows = []
    for ln in open(path):
        m = re.match(r"CELL (\S+)\s+flat=(\d).*tgap=(-?[\d.]+)%", ln)
        if m:
            rows.append((m.group(1), int(m.group(2)), float(m.group(3))))
    prod = [r for r in rows if r[1] == 0]
    miss = [r for r in rows if r[2] > 0.1]
    print(f"RESULT p4_calls={len(rows)} count; tgap_misses={len(miss)} count")
    print(f"RESULT p4_tgap_misses_price_arms={sum(1 for r in prod if r[2] > 0.1)}/{len(prod)} count")
    profs = sorted({r[0].split('|')[2] for r in prod})
    for p in profs:
        sub = [r for r in prod if r[0].split('|')[2] != p]
        print(f"RESULT p4_tgap_misses_drop[{p}]={sum(1 for r in sub if r[2] > 0.1)}/{len(sub)} count")


def arm_p5(path):
    import math
    rows = json.load(open(path))
    bar = math.log(1.10)
    over = [r for r in rows if r.get("admit") and abs(r.get("err_log") or 0) > bar]
    print(f"RESULT p5_admitted_over_bar_recount={len(over)} count")
    for p in sorted({r['preset'] for r in rows}):
        print(f"RESULT p5_over_bar_drop[{p}]={sum(1 for r in over if r['preset'] != p)} count")
    g = [r for r in rows if r["source"] == "gains" and r.get("hw") is not None and r.get("err_log") is not None]
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); rk = [0] * len(v)
        for i, j in enumerate(o): rk[j] = i
        return rk
    x, y = rank([abs(r["err_log"]) for r in g]), rank([r["hw"] for r in g])
    n = len(g); mx = sum(x) / n; my = sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sd = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    print(f"RESULT p5_spearman_abs_err_vs_hw_gains={cov / sd if sd else 0:.3f} (n={n})")
    for r in sorted(g, key=lambda r: (r['preset'], r['mag'])):
        print(f"# {r['preset']:12s} mag={r['mag']} err={100*r['err_log']:+.2f}% hw={r['hw']:.4f} admit={r['admit']}")


if __name__ == "__main__":
    arm = sys.argv[sys.argv.index("--arm") + 1]
    extra = [a for a in sys.argv[1:] if a not in ("--arm", arm)]
    globals()[f"arm_{arm}"](*extra)
    tail()
