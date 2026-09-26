"""V3 (leads) independent recheck of D5-s2-51: does the source itself still say what the
finder's harness measured, read directly rather than through dataflow_comments.py's instrumentation?

Metric: (a) grep hit for the two cited sentences at their claimed sites; (b) a static read of
coordinator._warm_seeded confirming it copies result.power_schedule with no index shift.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  tools/audit/round9/D5/verify-v3-leads/v3_dataflow_comments_recheck.py
Expected: both_sentences_present=2 of 2; warm_seeded_shifts=0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import time

t0, th0 = time.process_time(), time.thread_time()

opt_src = open("custom_components/heatpump_optimizer/optimizer.py").read()
coord_src = open("custom_components/heatpump_optimizer/coordinator.py").read()

hits = 0
if "the same problem one step later" in opt_src:
    hits += 1
if "model stashes the series on itself for the terminal-cost term" in opt_src:
    hits += 1
print(f"RESULT both_sentences_present={hits} of 2")

# _warm_seeded: does it shift by elapsed steps, or copy verbatim at offset 0?
m = re.search(r"def _warm_seeded\(.*?\n(?:.*\n)*?    return optimizer\n", coord_src)
body = m.group(0) if m else ""
copies_verbatim = "result.power_schedule" in body and "np.asarray" in body
shifts = bool(re.search(r"power_schedule\[[^\]]*:\s*\]", body)) or "elapsed" in body
print(f"RESULT warm_seeded_copies_verbatim={int(copies_verbatim)}")
print(f"RESULT warm_seeded_shifts={int(shifts)}")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
