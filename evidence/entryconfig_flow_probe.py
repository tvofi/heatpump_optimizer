"""Reviewer probe: does the flow-meter estimate still fire when the config is
main's EntryConfig rather than the plain dict the branch was written against?

The resolution merge brought main's R9-EG-B11 typed config into the same tree as
this branch's flow_meter reads; both sides edited coordinator.py and the region
merged clean, so nothing in the merge itself proves the call still works.

 arms:
  A  EntryConfig carrying the flow key, no power/frequency signal -> kW estimate
  B  the same mapping as a plain dict -> must equal A (null control on the type)
  C  EntryConfig WITHOUT the flow key -> None (the branch's own null control)
  D  EntryConfig with the flow key AND a power entity -> None (outranked)
  E  probe_install(EntryConfig) directly -> the reads thermal_model makes
"""
import sys

sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests")

from heatpump_optimizer import const, flow_meter  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402
from heatpump_optimizer.thermal_model import probe_install  # noqa: E402


class _Reading:
    ok = True
    value = 0.05


class _Reader:
    def read_flow_kg_s(self, key):
        return _Reading()


FLOW = {const.CONF_FLOW_METER_ENTITY: "sensor.water_flow"}
WITH_POWER = {**FLOW, const.CONF_POWER_ENTITY: "sensor.hp_power"}


def kw(cfg):
    return flow_meter.read_heat_output_kw(_Reader(), cfg, temps=(45.0, 35.0))


ec_flow = EntryConfig.from_mapping(dict(FLOW))
ec_plain = EntryConfig.from_mapping({})
ec_power = EntryConfig.from_mapping(dict(WITH_POWER))
dict_flow = dict(FLOW)

expected = 0.05 * const.WATER_CP_KJ_PER_KG_K * 10.0
a, b, c, d = kw(ec_flow), kw(dict_flow), kw(ec_plain), kw(ec_power)
cap = probe_install(ec_flow)

print(f"RESULT A_entryconfig_flow={a} expected={expected}")
print(f"RESULT B_dict_flow={b}")
print(f"RESULT C_entryconfig_noflowkey={c}")
print(f"RESULT D_entryconfig_with_power={d}")
print(f"RESULT E_probe_install_writes={sorted(cap.writes)} measured_power={cap.measured_power} frequency={cap.frequency}")
print(f"RESULT get_undeclared={ec_flow.get(const.CONF_FLOW_METER_ENTITY)!r} "
      f"get_missing_default={ec_flow.get('no_such_key', 'D')!r} in_cfg={'flow_meter_entity' in ec_flow} len={len(ec_flow)}")
print(f"VERDICT A={'PASS' if a == expected else 'FAIL'} B={'PASS' if b == a else 'FAIL'} "
      f"C={'PASS' if c is None else 'FAIL'} D={'PASS' if d is None else 'FAIL'}")
