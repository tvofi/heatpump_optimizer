"""V3 (leads) independent, STATIC recheck of D7-s3-72 (whose own harness is dynamic: a runtime
descriptor tracing 4 golden solves). Static grep across the whole tracked tree for any non-writer
reference to the four named _step_* members, plus a look at whether the writer method itself
ever reads one back (which the dynamic trace, run only over 4 named golden scenarios, could
miss if that read only fires on a code path those 4 scenarios never take).

Metric: for each of the 4 named members, count of files outside thermal_model.py mentioning
`.<member>` (grep, whole tree) -- confirms "0 loads outside thermal_model.py" statically, not
just over the 4 traced solves. Also flags any self-referential read of the member INSIDE
thermal_model.py itself (`self.<member>` appearing on the right-hand side of an expression,
i.e. not only as an assignment target), since that changes whether "no production consumer
reads it" is exactly true or only true of external consumers.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  tools/audit/round9/D7/verify-v3-leads/v3_write_only_scratch_static_recheck.py
Expected: external_refs=0 for all 4 members; self_read_lines>0 for _step_wood_refused (the
simulate_step multi-substep mean, `wood_refused += self._step_wood_refused`), 0 for the other 3.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import time

t0, th0 = time.process_time(), time.thread_time()

MEMBERS = ["_step_dhw_refused", "_step_dhw_floor_injected", "_step_dhw_draw_kw", "_step_wood_refused"]

tm_path = "custom_components/heatpump_optimizer/thermal_model.py"
tm_src = open(tm_path).read()

all_py = []
for root, dirs, files in os.walk("custom_components"):
    if "__pycache__" in root:
        continue
    for fn in files:
        if fn.endswith(".py"):
            all_py.append(os.path.join(root, fn))

for m in MEMBERS:
    external_refs = 0
    for f in all_py:
        if os.path.abspath(f) == os.path.abspath(tm_path):
            continue
        src = open(f).read()
        if f".{m}" in src:
            external_refs += 1
    # Self-read: `self.<m>` used where it is NOT the assignment target, i.e. appears
    # after an operator/on the RHS, or as an operand of `+=` (which is both a read and
    # a write).
    self_read_lines = []
    for i, line in enumerate(tm_src.splitlines(), 1):
        if f"self.{m}" not in line:
            continue
        # A plain `self.X = ...` (not +=, not on the RHS) is a pure write.
        stripped = line.strip()
        if re.match(rf"^self\.{m}\s*=\s*[^=]", stripped) and stripped.count(f"self.{m}") == 1:
            continue
        self_read_lines.append((i, stripped))
    print(f"member={m} external_refs={external_refs} self_read_lines={len(self_read_lines)} {self_read_lines}")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
