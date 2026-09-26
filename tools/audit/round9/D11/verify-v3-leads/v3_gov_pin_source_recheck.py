"""V3 (leads) independent, source-level recheck of D11-s1-72: read tests/entities.py's GOV pin
directly (not through l3_gov_pin.py's own re-derivation) to confirm (a) the pin's second arm
reads only governance.yml, (b) governance_cost.py's own derivation comment names more files than
that, and (c) budget-raise-gate-rerun.yml's rerun-stale-verdict job is absent from GOV today --
a live gap, not only a hypothetical cell.

Metric: count of workflow files governance_cost.py's own comment names as governance vs. count
the entities.py pin actually reads from.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  tools/audit/round9/D11/verify-v3-leads/v3_gov_pin_source_recheck.py
Expected: pin_reads_files=1 (governance.yml only); derivation_names_files>=3; rerun_job_in_gov=0;
  rerun_job_exists=1 (budget-raise-gate-rerun.yml:rerun-stale-verdict).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: leads box (4-core Linux container).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import time

t0, th0 = time.process_time(), time.thread_time()

ent_src = open("tests/entities.py").read()
gc_src = open("tools/audit/round4/D11/governance_cost.py").read()
rerun_src = open(".github/workflows/budget-raise-gate-rerun.yml").read()

# (a) What file(s) does the pin's second arm (_workflow_job_ids(_DS_GOV) <= GOV) read from?
m = re.search(r"_DS_GOV\s*=\s*Path\(([^)]+)\)\.read_text\(\)", ent_src)
pin_reads = [m.group(1)] if m else []
print(f"RESULT pin_reads_files={len(pin_reads)} count files={pin_reads}")

# (b) governance_cost.py's own derivation comment (search for the file names it lists as
# "governance" near the GOV set / near a comment mentioning "derive").
gov_comment = re.search(r"# The rule this set is derived from.*?(?=\nGOV =)", gc_src, re.S)
derivation_text = gov_comment.group(0) if gov_comment else ""
named_files = sorted(set(re.findall(r"[\w-]+\.yml", derivation_text)))
print(f"RESULT derivation_names_files={len(named_files)} count files={named_files}")

# (c) is rerun-stale-verdict a real job in budget-raise-gate-rerun.yml, and is it in GOV?
rerun_job_exists = int("rerun-stale-verdict:" in rerun_src)
gov_match = re.search(r"^GOV = \{(.*?)\}", ent_src, re.S | re.M) or re.search(
    r"^GOV = \{(.*?)\}", gc_src, re.S | re.M
)
gov_set_text = gov_match.group(1) if gov_match else ""
rerun_job_in_gov = int('"rerun-stale-verdict"' in gov_set_text)
print(f"RESULT rerun_job_exists={rerun_job_exists} count")
print(f"RESULT rerun_job_in_gov={rerun_job_in_gov} count")

print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open('/proc/vmstat') if ln.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
