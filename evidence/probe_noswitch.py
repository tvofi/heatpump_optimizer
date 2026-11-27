import sys
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
from types import SimpleNamespace
from datetime import datetime, timezone
from harness import FakeHass, FakeState
from heatpump_optimizer import pump_arbiter as pa, frost_hold as fh
T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
def inp(out, switch):
    hass = FakeHass({switch: FakeState("on")} if switch else {})
    cfg = {"heat_pump_switch_entity": switch} if switch else {}
    return pa.ArbiterInputs(hass=hass, config=cfg, mode="auto", plan=None, plan_stale=False, entry_released=False,
        state=SimpleNamespace(outdoor_temperature=5.0), thermal=SimpleNamespace(params=SimpleNamespace(min_electrical_power=0.4)),
        params=None, action={}, measured_power_kw=None, disinfecting=False, outdoor_c=out)
for sw in ("switch.hp", None):
    for out in (-3.0, 5.0):
        held = pa.ArbiterState()
        v = fh.gate(held, lambda: inp(out, sw), False, T0)
        print(f"switch={sw!s:10} out={out:5} gate(False)->{v!r:6} frost_holding={held.frost_holding} holding={fh.holding(held, inp(out, sw))} ran_until={held.frost and held.frost.ran_until}")
print("-- end to end on a no-switch host (cycle's _write_supply runs gate before its switch check)")
for sw in (None, "switch.hp"):
    for enabled_cfg in ({}, ):
        class Host:
            def __init__(s): s.inp = inp(-3.0, sw)
            def arbiter_inputs(s): return s.inp
        h = Host()
        held = pa.state_for(h)
        fh.gate(held, h.arbiter_inputs, False, T0)
        from datetime import timedelta
        fr = fh.freeze_reason(h, T0 + timedelta(minutes=10))
        print(f"switch={sw!s:10} -3C idle OFF: frost_holding={held.frost_holding} _served(duty=None)->{pa._served(h, h.inp, None, T0)!r} freeze_reason->{fr!r}")
held = pa.ArbiterState()
print("null control, no switch +5C:", fh.gate(held, lambda: inp(5.0, None), False, T0), held.frost_holding)
