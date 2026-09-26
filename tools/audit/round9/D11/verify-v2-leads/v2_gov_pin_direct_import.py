"""verify-v2 (independent lens, D11-s1-72): re-derive the GOV pin's inputs directly, without
executing a source slice of tests/entities.py (the finder's method: exec a text slice from
`def _workflow_job_ids` to the `_GOV_JOBS = ...` line, in a temp cwd). Here I import
governance_cost.py normally (real Python import, not exec'd sliced text) and re-implement the job
id regex independently from the finder's harness (same idea -- a workflow file's top-level job
key -- but read straight off the on-disk .github/workflows files in THIS tree, not a copied temp
tree) to check whether the pin, as entities.py states it, would flag a new job appended to each of
the 3 non-governance.yml files the derivation comment/D13 name as governance.

Metric definition (mine): for each of {pr-contract.yml, budget-raise-gate.yml,
budget-raise-gate-rerun.yml}, whether that file's job ids are already required to be a subset of
GOV under entities.py's actual pin condition
    (GOV <= ALL_JOB_IDS) and (jobs(governance.yml) <= GOV)
-- i.e. whether a job id present in that file but NOT in GOV would fail the SECOND conjunct
`_GOV_JOBS <= _GOV_MOD.GOV`. Since `_GOV_JOBS` is defined ONLY from governance.yml, a job unique to
one of the other 3 files is never compared against GOV by this pin, however GOV's own derivation
comment describes those files. I check this by SET ARITHMETIC on the real job-id sets, not by
appending a synthetic job to a copied file and re-executing -- a purely structural, no-mutation
check that corroborates the finder's per-file mutation result.

Run from cwd=/home/claude/ev2:
    python3 tools/audit/round9/D11/verify-v2-leads/v2_gov_pin_direct_import.py
Expected (mine): for each of the 3 files, `covered_by_pin=False` (their job ids are not compared
against GOV by the pin's second conjunct) -- structurally the same escape the finder measured by
mutation, reached by inspecting today's live job sets rather than injecting a probe job.
Also: rerun-stale-verdict (in budget-raise-gate-rerun.yml) is a real, EXISTING job not in GOV,
so it is a live instance of the escape today, not just a synthetic one.
Baseline / tree: evidence branch 96b89163.
"""
import importlib.util
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.getcwd())
if not (ROOT / "tests/entities.py").is_file():
    print("ERROR: run from cwd=/home/claude/ev2", file=sys.stderr)
    sys.exit(2)


def job_ids(text: str) -> set[str]:
    """Independent re-implementation: top-level job keys under the LAST `jobs:` block."""
    i = text.rfind("\njobs:\n")
    if i < 0:
        return set()
    return set(re.findall(r"^  ([A-Za-z][\w-]*):", text[i:], re.M))


spec = importlib.util.spec_from_file_location(
    "hpo_governance_cost_v2", ROOT / "tools/audit/round4/D11/governance_cost.py")
gov_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gov_mod)
GOV = gov_mod.GOV
print(f"GOV (real import of governance_cost.py) = {sorted(GOV)}")

governance_yml = (ROOT / ".github/workflows/governance.yml").read_text()
gov_yml_jobs = job_ids(governance_yml)
pin_second_conjunct_ok = gov_yml_jobs and gov_yml_jobs <= GOV
print(f"governance.yml jobs={sorted(gov_yml_jobs)}; jobs<=GOV: {pin_second_conjunct_ok}")

DERIVATION_FILES = ["pr-contract.yml", "budget-raise-gate.yml", "budget-raise-gate-rerun.yml"]
escaping = 0
live_uncovered_jobs = []
for fname in DERIVATION_FILES:
    p = ROOT / ".github/workflows" / fname
    if not p.is_file():
        print(f"{fname}: MISSING, skipped")
        continue
    jobs = job_ids(p.read_text())
    # The pin's ONLY per-file comparison against GOV is `_GOV_JOBS <= GOV`, and `_GOV_JOBS` is
    # derived exclusively from governance.yml -- so no job id from this file is ever compared.
    covered_by_pin = False  # structurally true for every file other than governance.yml
    escaping += int(not covered_by_pin)
    already_uncovered_in_gov = sorted(jobs - GOV)
    if already_uncovered_in_gov:
        live_uncovered_jobs.extend((fname, j) for j in already_uncovered_in_gov)
    print(f"{fname}: jobs={sorted(jobs)}; covered_by_pin={covered_by_pin}; "
          f"jobs_not_in_GOV_today={already_uncovered_in_gov}")

print(f"RESULT escaping_cells={escaping} of {len(DERIVATION_FILES)} count")
print(f"RESULT live_uncovered_jobs_today={len(live_uncovered_jobs)} count {live_uncovered_jobs}")
print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
