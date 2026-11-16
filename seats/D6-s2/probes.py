#!/usr/bin/env python3
"""D6-s2 round 11: executed probes behind the strings.json / blueprint / governance claims of seat D6-s2.

Metric (per probe, one line each):
  wood_packing_ratio    count of wood types whose loose/packed useful kWh per m3, read through
                        wood_fuel:useful_kwh_m3, is not 0.60 +-0.005 (strings.json: "loose ... billed at
                        0.60 of packed"). Key: the value useful_kwh_m3 returns. Expected 1 (birch) +-0.
  flow_unit_lmin        ratio of const:FLOW_UNIT_TO_KG_S["L/min"] to the physical 0.998/60 kg/s per L/min
                        (strings.json: a flow sensor "in L/min" lets the integration read the heat).
                        Key: the factor the production table delivers. Expected 0.01667 (1/60) +-1e-4.
  station_potable       const:COMBI_TANK_PRESETS["external_station"].potable_volume_l, litres
                        (strings.json: "0 for a fresh-water station"). Expected 150 +-0.
  return_gate           pump_arbiter:_gate_floor_c for space_setpoint_unit "return", degC (strings.json:
                        "the gate that means off is 25 degC for a flow target and 20 degC for a return
                        target"). Key: the value _gate_floor_c returns. Expected 30.0 +-0.
  observe_writes        pump_arbiter:_arbitrate in duty mode "observe", optimizer mode auto, pump on:
                        number of _command calls (strings.json: "Observe writes none either").
                        Key: calls reaching pump_arbiter._command. Expected 1 +-0.
  gov_paths             backticked repository paths in dev/governance/{dimensions,dimensions/criteria,roles}/*.md
                        that resolve to no file or directory of the tree under test. Expected 2 +-0.

Run (repository root of the export):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s2/probes.py [--probe NAME] [--perturb]
--perturb applies each probe's named one-line production change in memory (never on disk) and the
number must move as stated in REPORT.md.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 as exported to $HOME/audit-r11-baseline (see REPORT.md:
the export's production files differ from that SHA's blobs). Machine: box B2, Linux x86_64, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
_T0P, _T0T = time.process_time(), time.thread_time()

import harness  # noqa: E402,F401  (stub wiring: hastub + package path)
from heatpump_optimizer import const, wood_fuel, pump_arbiter  # noqa: E402

GOV_GLOBS = ("dev/governance/dimensions/*.md", "dev/governance/dimensions/criteria/*.md",
             "dev/governance/roles/*.md")
PATHLIKE = re.compile(r"`([A-Za-z0-9_.~/-]+/[A-Za-z0-9_.-]+\.(?:py|mjs|js|sh|json|md|yaml|yml|txt|tsv))`")


def wood_packing_ratio(perturb=False):
    table = dict(wood_fuel.WOOD_KWH_M3)
    if perturb:  # one-line edit: birch row {"packed": 1900.0, "loose": 1140.0}
        wood_fuel.WOOD_KWH_M3 = {**table, "birch": {"packed": 1900.0, "loose": 1140.0}}
    try:
        off = []
        for t in wood_fuel.WOOD_KWH_M3:
            r = wood_fuel.useful_kwh_m3(t, "loose", 100.0) / wood_fuel.useful_kwh_m3(t, "packed", 100.0)
            print(f"   {t}: loose/packed = {r:.4f}")
            if abs(r - 0.60) > 0.005:
                off.append(t)
        return len(off), "types", ",".join(off)
    finally:
        wood_fuel.WOOD_KWH_M3 = table


def flow_unit_lmin(perturb=False):
    table = dict(const.FLOW_UNIT_TO_KG_S)
    if perturb:  # one-line edit: "L/min": WATER_KG_PER_L / 60.0
        const.FLOW_UNIT_TO_KG_S["L/min"] = const.WATER_KG_PER_L / 60.0
    try:
        got = const.FLOW_UNIT_TO_KG_S["L/min"]
        phys = 0.998 / 60.0
        # the heat 10 L/min across 5 K carries, as production's factor converts it
        kw = 10.0 * got * const.WATER_CP_KJ_PER_KG_K * 5.0
        print(f"   factor={got:.6g} kg/s per L/min, physical={phys:.6g}; 10 L/min x 5 K reads {kw:.3f} kW (physical 3.479)")
        return round(got / phys, 5), "ratio", f"{kw:.3f} kW"
    finally:
        const.FLOW_UNIT_TO_KG_S.clear(); const.FLOW_UNIT_TO_KG_S.update(table)


def station_potable(perturb=False):
    presets = dict(const.COMBI_TANK_PRESETS)
    if perturb:  # one-line edit: "external_station": CombiTankPreset(0.75, 0.0)
        const.COMBI_TANK_PRESETS["external_station"] = const.CombiTankPreset(0.75, 0.0)
    try:
        p = const.COMBI_TANK_PRESETS["external_station"]
        print(f"   external_station effectiveness={p.effectiveness} potable_volume_l={p.potable_volume_l}")
        return p.potable_volume_l, "L", f"eps={p.effectiveness}"
    finally:
        const.COMBI_TANK_PRESETS.clear(); const.COMBI_TANK_PRESETS.update(presets)


def observe_writes(perturb=False):
    """Drive pump_arbiter._arbitrate in observe mode with every side seam stubbed; count _command."""
    pa = pump_arbiter
    calls = {"command": 0, "adopt": 0, "night": 0}
    saved = {}

    async def _cmd(*a, **k):
        calls["command"] += 1

    async def _adopt(*a, **k):
        calls["adopt"] += 1

    async def _night(*a, **k):
        calls["night"] += 1

    async def _anoop(*a, **k):
        return None

    stubs = {
        "_command": _cmd, "_adopt": _adopt, "_write_night_schedule": _night, "_persist": _anoop,
        "hold": lambda *a, **k: None, "_step_duty": lambda *a, **k: "space",
        "_observe": lambda *a, **k: None, "_served": lambda *a, **k: "space",
        "desired": lambda *a, **k: None, "_switch_context": lambda *a, **k: None,
        "_pump_off": lambda inp, held: False,
    }
    for k, v in stubs.items():
        saved[k] = getattr(pa, k)
        setattr(pa, k, v)
    saved_boost = (pa.boost.release_blocked, pa.boost.held_for, pa.boost.persist)
    saved_ds = (pa.duty_switch.note_pass, pa.duty_switch.record_for)
    pa.boost.release_blocked = lambda *a, **k: False
    pa.boost.held_for = lambda *a, **k: None
    pa.boost.persist = _anoop
    pa.duty_switch.note_pass = _anoop
    pa.duty_switch.record_for = lambda *a, **k: None
    orig_arb = pa._arbitrate
    if perturb:  # one-line edit: `if mode != DUTY_CONTROL or _pump_off(inp, held):`
        import inspect, textwrap
        src = textwrap.dedent(inspect.getsource(orig_arb)).replace(
            "    if _pump_off(inp, held):\n        return",
            "    if mode != DUTY_CONTROL or _pump_off(inp, held):\n        return")
        ns = {}
        exec(compile(src, pa.__file__, "exec"), pa.__dict__, ns)
        pa._arbitrate = ns["_arbitrate"]
    try:
        held = pa.ArbiterState()
        inp = SimpleNamespace(mode="auto", config={const.CONF_PUMP_DUTY_MODE: "observe"} if hasattr(const, "CONF_PUMP_DUTY_MODE") else {},
                              hass=None, plan=None, plan_stale=False, entry_released=False)
        coord = SimpleNamespace(hass=None, entry=None)
        now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
        asyncio.run(pa._arbitrate(coord, held, inp, "observe", now))
        print(f"   observe pass: _command={calls['command']} _adopt={calls['adopt']} night_schedule={calls['night']}")
        return calls["command"], "calls", f"adopt={calls['adopt']} night={calls['night']}"
    finally:
        pa._arbitrate = orig_arb
        for k, v in saved.items():
            setattr(pa, k, v)
        pa.boost.release_blocked, pa.boost.held_for, pa.boost.persist = saved_boost
        pa.duty_switch.note_pass, pa.duty_switch.record_for = saved_ds


def return_gate(perturb=False):
    pa = pump_arbiter
    orig = pa._as_target
    if perturb:  # one-line edit: `return supply_c - RETURN_SUPPLY_OFFSET_K if _return_unit(config) else supply_c`
        pa._as_target = lambda config, supply_c: supply_c - pa.RETURN_SUPPLY_OFFSET_K if pa._return_unit(config) else supply_c
    try:
        ret = pa._gate_floor_c({const.CONF_SPACE_SETPOINT_UNIT: "return"})
        flow = pa._gate_floor_c({})
        print(f"   gate: flow target {flow} degC, return target {ret} degC")
        return ret, "degC", f"flow={flow}"
    finally:
        pa._as_target = orig


def _tree():
    out = set()
    for r, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if d != ".git"]
        rel = os.path.relpath(r, ROOT)
        if rel != ".":
            out.add(rel)
        out.update(os.path.normpath(os.path.join(rel, f)) for f in fs)
    return out


def gov_paths(perturb=False, verbose=True):
    """Backticked paths (with a directory part) in the governance briefs/roles resolving to nothing."""
    tree = _tree()
    if perturb:  # creating the decisions at the cited path: the count goes to zero
        tree |= {"docs/decisions/0010-merge-commits-on-main.md", "docs/decisions/0011-app-authored-identity.md"}
    bad = []
    for g in GOV_GLOBS:
        for f in sorted(ROOT.glob(g)):
            txt = f.read_text(encoding="utf-8")
            for m in PATHLIKE.finditer(txt):
                p = m.group(1)
                rel = str(f.relative_to(ROOT))
                cands = [p, os.path.normpath(os.path.join(os.path.dirname(rel), p))]
                # a placeholder path (`k/SKILL.md`: k is a variable the sentence defines) is no reference
                if p.startswith(("~", "/")) or re.match(r"^[a-z]/", p) or any(c in tree for c in cands):
                    continue
                # a path written relative to a known root (tools/audit/seat, tests, dev/governance/*)
                if any(t.endswith("/" + p) for t in tree):
                    continue
                bad.append((rel, txt.count("\n", 0, m.start()) + 1, p))
    if verbose:
        for b in bad:
            print("   unresolved %s:%d %s" % b)
    return len(bad), "paths", ";".join(f"{a}:{b}" for a, b, _ in bad)


PROBES = {f.__name__: f for f in (wood_packing_ratio, flow_unit_lmin, station_potable, observe_writes, return_gate, gov_paths)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", choices=sorted(PROBES))
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    for name, fn in PROBES.items():
        if a.probe and name != a.probe:
            continue
        v, unit, note = fn(a.perturb)
        print(f"RESULT {name}{'_perturbed' if a.perturb else ''}={v} {unit}  # {note}")
    pt, tt = time.process_time() - _T0P, time.thread_time() - _T0T
    print(f"RESULT thread_factor={pt / tt if tt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except (OSError, IndexError):
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
