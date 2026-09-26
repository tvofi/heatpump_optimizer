"""V3 (leads) independent recheck of D7-s1-71: grep-based, source-level confirmation (not
through l3_cold_water_default.py's own instrumentation) that the three named sites still spell
the cold-water default three ways, and whether every current production caller of
dhw_coil_draw_reduction passes inlet_temp explicitly (so the divergent default parameter is a
capability, not a live behavioural divergence today).

Metric: (a) 3 distinct default-spelling sites found by source grep; (b) of N production call
sites of dhw_coil_draw_reduction, how many omit inlet_temp (and so would read the un-migrated
default).
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  tools/audit/round9/D7/verify-v3-leads/v3_cold_water_default_recheck.py
Expected: spellings=3, coil_callers=3, coil_callers_passing_inlet=3, coil_callers_omitting=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import time

t0, th0 = time.process_time(), time.thread_time()

tm_src = open("custom_components/heatpump_optimizer/thermal_model.py").read()
opt_src = open("custom_components/heatpump_optimizer/optimizer.py").read()
cf_src = open("custom_components/heatpump_optimizer/config_flow.py").read()
const_src = open("custom_components/heatpump_optimizer/const.py").read()
whole = tm_src + opt_src + cf_src + const_src

spellings = 0
if re.search(r"dhw_inlet_temp:\s*float\s*=\s*10\.0", tm_src):
    spellings += 1  # bare literal field default (thermal_model.py)
if "DEFAULT_DHW_INLET_TEMP" in whole:
    spellings += 1  # const.py + config_flow.py / from_config path
if "DHW_COLD_WATER_TEMP" in whole:
    spellings += 1  # dhw_coil_draw_reduction's own default arg
print(f"RESULT spellings={spellings} count (bare literal / DEFAULT_DHW_INLET_TEMP / DHW_COLD_WATER_TEMP)")

# Every production call site of dhw_coil_draw_reduction, across both files it's defined/used in.
calls = []
for fname, src in (("optimizer.py", opt_src), ("thermal_model.py", tm_src)):
    for m in re.finditer(r"dhw_coil_draw_reduction\(([^)]*\)[^)]*\))", src):
        pass
# Simpler: find each call's arg-list text up to the matching close paren via a bounded scan.
def find_calls(src):
    out = []
    idx = 0
    while True:
        i = src.find("dhw_coil_draw_reduction(", idx)
        if i == -1:
            break
        # def line is a definition, not a call; skip it
        line_start = src.rfind("\n", 0, i) + 1
        if src[line_start:i].strip().startswith("def"):
            idx = i + 1
            continue
        depth = 0
        j = i + len("dhw_coil_draw_reduction(") - 1
        start = j
        while True:
            if src[j] == "(":
                depth += 1
            elif src[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(src[start:j + 1])
        idx = j + 1
    return out

all_calls = find_calls(opt_src) + find_calls(tm_src)
passing = [c for c in all_calls if "inlet_temp=" in c]
omitting = [c for c in all_calls if "inlet_temp=" not in c]
print(f"RESULT coil_callers={len(all_calls)} count")
print(f"RESULT coil_callers_passing_inlet={len(passing)} count")
print(f"RESULT coil_callers_omitting={len(omitting)} count sites={omitting}")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
