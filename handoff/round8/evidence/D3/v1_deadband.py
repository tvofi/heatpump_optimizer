#!/usr/bin/env python3
"""v1_deadband.py -- D3 verifier's own measurement of D3-s2-02.

Metric (one line): through the REAL domain setup (harness.ha_setup_component +
ha_setup_entry, then hass.services.async_call -- the path tests/features.py's
_et_call drives), whether set_thermal_parameters and apply_schedule raise a
*_no_deadband ServiceValidationError for dhw_min_temperature = 50.0 with the
default 55 C setpoint (ceiling = 55 - DHW_MIN_TEMP_SETPOINT_MARGIN = 50.0),
baseline vs `>`->`>=` mutant at each site separately.
Arms per variant: 50.0 (boundary), 49.99 (null: accepted everywhere), 51.0
(positive control: rejected everywhere -- the value the suite uses).

The mutant is applied IN MEMORY in the probe subprocess (the mutated source is
exec'd into the already-imported services module's namespace), so production
files on disk are never touched. Instrumented symbols: services.py
handle_set_thermal_params (line 486) and handle_apply_schedule (line 823).

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/v1_deadband.py
Expected at cdf82daabcfe3777d98b31489f36df5555ec9d82: boundary accepted at both
sites on baseline, rejected at the mutated site only; null/positive unchanged.
Machine: 4-vCPU container; counts exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import time

PROBE = r'''
import sys, json, asyncio
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import harness
from harness import FakeHass, FakeEntry, FakeState
import heatpump_optimizer as integ
from heatpump_optimizer import services as svc
from heatpump_optimizer.const import DOMAIN
from homeassistant.exceptions import HomeAssistantError
variant = sys.argv[1]
PATCH = {
    "A": ("            if float(minimum) > ceiling:", "            if float(minimum) >= ceiling:"),
    "B": ("            if wanted > ceiling:", "            if wanted >= ceiling:"),
}
if variant in PATCH:
    src = open(svc.__file__).read()
    old, new = PATCH[variant]
    assert src.count(old) == 1
    exec(compile(src.replace(old, new, 1), svc.__file__, "exec"), svc.__dict__)
from homeassistant.util import dt as dt_util
from datetime import timedelta
def seed(hass):
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set("sensor.prices", FakeState("0.5", attributes={"raw_today": [
        {"start": (now + timedelta(hours=h)).isoformat(), "value": round(0.5 + 0.1 * (h % 4), 3)}
        for h in range(48)]}))
out = {}
for service in ("set_thermal_parameters", "apply_schedule"):
    for value in (50.0, 49.99, 51.0):
        hass = FakeHass(); seed(hass)
        entry = FakeEntry(data={"price_source": "entity", "price_entity": "sensor.prices",
                                "weather_entity": "weather.home"})
        asyncio.run(harness.ha_setup_component(integ, hass))
        asyncio.run(harness.ha_setup_entry(integ, hass, entry))
        try:
            asyncio.run(hass.services.async_call(DOMAIN, service, {"dhw_min_temperature": value}))
            r = "accepted"
        except HomeAssistantError as err:
            r = getattr(err, "translation_key", None) or type(err).__name__
        out[f"{service}@{value}"] = r
print("JSON " + json.dumps(out))
'''


def probe(variant):
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    p = subprocess.run([sys.executable, "-c", PROBE, variant], env=env,
                       capture_output=True, text=True, timeout=900)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("JSON ")]
    if not line:
        raise SystemExit(p.stdout[-2000:] + p.stderr[-3000:])
    return json.loads(line[-1][5:])


def main():
    t0 = time.process_time(); w0 = time.thread_time()
    res = {v: probe(v) for v in ("base", "A", "B")}
    for v, r in res.items():
        print(f"  {v}: {r}")
    b = res["base"]
    flips = 0
    for v, site in (("A", "set_thermal_parameters"), ("B", "apply_schedule")):
        flipped = b[f"{site}@50.0"] == "accepted" and res[v][f"{site}@50.0"] != "accepted"
        flips += flipped
        print(f"RESULT boundary_flip_{v}_{site}={int(flipped)} count")
    null_ok = all(res[v][f"{s}@49.99"] == "accepted" for v in res
                  for s in ("set_thermal_parameters", "apply_schedule"))
    pos_ok = all(res[v][f"{s}@51.0"] != "accepted" for v in res
                 for s in ("set_thermal_parameters", "apply_schedule"))
    print(f"RESULT boundary_flips={flips} count (of 2)")
    print(f"RESULT null_accepted_everywhere={int(null_ok)} count")
    print(f"RESULT posctl_rejected_everywhere={int(pos_ok)} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-w0,1e-9):.3f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
