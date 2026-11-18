"""V2 probe for D7-arch2-11 and D7-arch2-08: does a non-finite value a coercer passes reach a decision?

Metric (D7-arch2-11): silent_cap = quiet_windows.silent_cap_kw(config, get_state, p_max) and
  compose_caps = the per-step ceiling quiet_windows.compose returns over one silent window, for a
  heat-pump power entity reading each probe state. p_max=6.0 kW, silent_mode_power_fraction=0.7
  (fraction cap 4.2 kW; capacity floor 0.6*p_max=3.6 kW).
  inf_reaches_cap = 1 if any returned cap/ceiling is non-finite; inf_changes_decision = 1 if the
  '1e400' answer differs from the refusal arm ('unknown').
Null control: state 'unknown' (every parser refuses) -> fraction cap 4.2; and an absurd FINITE
  state '1e6' kW -> shows whether the inf answer differs from an ordinary over-range reading.
Perturbation: in memory, quiet_windows._power_entity_kw wrapped to refuse a non-finite kW (the
  inputs-style policy); the '1e400' arm must then equal the 'unknown' arm.
Metric (D7-arch2-08): pump_arbiter._finite_or_none passes NaN/inf; drive its only consumer
  pump_arbiter._step_kw -> thermal_model.flow_setpoint_for_level and report whether the written
  flow set-point is finite (nan_reaches_flow).
Run (from a tree root): PYTHONPATH=tests/hastub python3 \
    dev/audit/rounds/round10/catchup/arch-s2/probe_coercion_reach.py
Expected at baseline 554e2ecfa: inf_reaches_cap=0, inf_changes_decision=1 (cap 6.0 = no cap vs 4.2),
  inf equals the 1e6 arm; perturbed 1e400 == unknown; nan_reaches_flow=0.
Baseline SHA 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef (production identical to d749c986d). Machine:
shared macOS 8-core box; counts only. Imports the working tree's package read-only.
"""
import math, os, sys, types
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
sys.path.insert(0, str(REPO / "custom_components"))
import numpy as np
from heatpump_optimizer import quiet_windows as qw, pump_arbiter as pa, thermal_model as tm
from heatpump_optimizer.const import (CONF_POWER_ENTITY, CONF_QUIET_SILENT_WINDOWS,
                                      CONF_SILENT_MODE_FRACTION, CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY)

P_MAX = 6.0
START = datetime(2026, 1, 5, 0, 0)
CFG = {CONF_POWER_ENTITY: "sensor.p", CONF_SILENT_MODE_FRACTION: 0.7,
       CONF_QUIET_SILENT_WINDOWS: "00:00-06:00", CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.silent"}

def state(s):
    return types.SimpleNamespace(state=s, attributes={"unit_of_measurement": "kW"})

def arm(s):
    gs = lambda eid: state(s) if eid == "sensor.p" else None
    cap = qw.silent_cap_kw(CFG, gs, P_MAX)
    try:
        comp = qw.compose(None, CFG, gs, START, 8, 1.0, P_MAX)
        caps = None if comp.caps is None else [round(float(x), 3) for x in comp.caps]
    except Exception as exc:  # noqa: BLE001
        caps = type(exc).__name__
    return cap, caps

PROBES = ["unknown", "3", "1e6", "1e400", "inf"]
def table(tag):
    out = {}
    for s in PROBES:
        out[s] = arm(s)
        print(f"  [{tag}] state={s!r:10} silent_cap_kw={out[s][0]!r:6} compose_caps={out[s][1]}")
    return out

print(f"RESULT load1={os.getloadavg()[0]:.2f}")
base = table("baseline")
nonfinite = any((c is not None and not math.isfinite(c)) for c, _ in base.values()) or any(
    isinstance(v, list) and any(not math.isfinite(x) for x in v) for _, v in base.values())
print(f"RESULT inf_reaches_cap={int(nonfinite)} bool")
print(f"RESULT inf_changes_decision={int(base['1e400'] != base['unknown'])} bool")
print(f"RESULT inf_equals_finite_absurd={int(base['1e400'] == base['1e6'])} bool")

orig = qw._power_entity_kw
def refusing(pid, gs):
    kw = orig(pid, gs)
    return kw if kw is not None and math.isfinite(kw) else None
qw._power_entity_kw = refusing
pert = table("perturbed")
qw._power_entity_kw = orig
print(f"RESULT perturbed_1e400_equals_unknown={int(pert['1e400'] == pert['unknown'])} bool")

# D7-arch2-08: pump_arbiter._finite_or_none -> _step_kw -> flow_setpoint_for_level
now = datetime(2026, 1, 5, 12, 7, tzinfo=timezone.utc)
for bad in (float("nan"), float("inf"), np.float64("nan")):
    res = types.SimpleNamespace(timestamps=[now - timedelta(minutes=7)], power_schedule=[bad])
    kw = pa._step_kw(res, now)
    flow = tm.flow_setpoint_for_level(kw, 1.0, 6.0, 45.0, 30.0)
    print(f"  _step_kw({bad!r})={kw!r} -> flow_setpoint_for_level={flow!r}")
    print(f"RESULT nan_reaches_flow[{bad!r}]={int(not math.isfinite(flow))} bool")
