"""Reviewer probe: is an over-limit part-load derate ever silently read as 0?"""
import sys
from custom_components.heatpump_optimizer import config_flow as cf
from custom_components.heatpump_optimizer import const as c
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters, partload_derate_limit

stored = {c.CONF_HEAT_PUMP_MIN_POWER: 1.0, c.CONF_HEAT_PUMP_MAX_POWER: 5.0,
          c.CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: 0.4}
print("RESULT stored 1-5 kW d=0.4 limit %.4f read %r" % (
    partload_derate_limit(1.0, 5.0), ThermalParameters.from_config(stored).cop_partload_derate))
saved = {c.CONF_HEAT_PUMP_MAX_POWER: 2.0}   # pre-fill suggests capacity/COP
merged = {**stored, **saved}
lim = partload_derate_limit(1.0, 2.0)
read = ThermalParameters.from_config(merged).cop_partload_derate
page = cf._partload_errors(saved, stored)
pre = cf._prefill_errors(saved, stored)
print("RESULT thermal_model page, max 5->2 (limit %.4f): errors %r" % (lim, page))
print("RESULT pre-fill save, max 5->2: errors %r; model reads derate %r" % (pre, read))
silent = (not pre) and read == 0.0 and stored[c.CONF_HEAT_PUMP_COP_PARTLOAD_DERATE] >= lim
# null control: a derate under the narrowed limit is kept by both
ok = {**stored, c.CONF_HEAT_PUMP_COP_PARTLOAD_DERATE: 0.3}
print("RESULT null d=0.3 max 5->2: pre-fill errors %r page errors %r read %r" % (
    cf._prefill_errors(saved, ok), cf._partload_errors(saved, ok),
    ThermalParameters.from_config({**ok, **saved}).cop_partload_derate))
print("RESULT silent over-limit read-as-0 via pre-fill:", "YES" if silent else "no")
sys.exit(1 if silent else 0)
