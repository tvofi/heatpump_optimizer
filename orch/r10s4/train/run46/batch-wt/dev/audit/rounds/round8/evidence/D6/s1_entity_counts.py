#!/usr/bin/env python3
"""
Metric: counts real entities instantiated through the real async_setup_entry
for the sensor, binary_sensor and button platforms (tests/entities.py:collect),
and compares them against README.md's stated headcounts ("Sensors (59 total)",
"Binary Sensors (5 total)", "Buttons (4 total)").
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D6/s1_entity_counts.py
Expected: prints RESULT lines; run from the tree root.
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: cloud 4-vCPU container (see BASELINE.md); counts are exact (not
timing), so contention-immune.
Perturbation: comment out one sensor class's registration in sensor.py's
async_setup_entry (or set an entity's default-disabled condition to always
skip) and the printed count must drop by exactly the number of entities that
registration adds.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import re
import sys
import time
import resource

sys.path.insert(0, "tests")
sys.path.insert(0, "tests/hastub")

t0 = time.process_time()

# entities.py runs its whole check suite (1700+ checks) at import time and
# calls sys.exit() at the end (tools/audit/README.md's trap list). We only
# need the collect() helper and DATA fixture it defines earlier in the
# module, so neutralise sys.exit for the duration of the import.
_real_exit = sys.exit
sys.exit = lambda *a, **k: None
try:
    import entities as E
finally:
    sys.exit = _real_exit
from heatpump_optimizer import sensor, binary_sensor, button

_hass, coord, _data = E._honest_coordinator()
sensors = E.collect(sensor, coordinator=coord)
binsens = E.collect(binary_sensor, coordinator=coord)
buttons = E.collect(button, coordinator=coord)

n_sensor = len(sensors)
n_binary = len(binsens)
n_button = len(buttons)

# Parse README's claimed counts.
readme = open("README.md", encoding="utf-8").read()
def claimed(label):
    m = re.search(rf"### {label} \((\d+) total\)", readme)
    return int(m.group(1)) if m else None

c_sensor = claimed("Sensors")
c_binary = claimed(r"Binary Sensors")
c_button = claimed("Buttons")

t1 = time.process_time()
thread_cpu = t1 - t0  # single-threaded script; process==thread here

print(f"RESULT sensor_count_actual={n_sensor} entities")
print(f"RESULT sensor_count_claimed={c_sensor} entities")
print(f"RESULT binary_sensor_count_actual={n_binary} entities")
print(f"RESULT binary_sensor_count_claimed={c_binary} entities")
print(f"RESULT button_count_actual={n_button} entities")
print(f"RESULT button_count_claimed={c_button} entities")
print(f"RESULT sensor_delta={n_sensor - (c_sensor or 0)} entities")
print(f"RESULT binary_sensor_delta={n_binary - (c_binary or 0)} entities")
print(f"RESULT button_delta={n_button - (c_button or 0)} entities")

load1 = os.getloadavg()[0]
print(f"RESULT load1={load1} load")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
