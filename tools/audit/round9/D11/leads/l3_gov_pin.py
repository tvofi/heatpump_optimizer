"""l3_gov_pin: does entities.py's GOV pin see a governance job outside governance.yml?

Metric (one line): probe cells -- one new job appended to a workflow file that the GOV set's own
derivation rule (governance_cost.py comment: governance.yml, `briefs`, pr-contract.yml,
budget-raise-gate.yml) or D13's re-derivation (budget-raise-gate-rerun.yml) counts as governance --
in which the entities.py GOV pin still PASSES; key = the pin's boolean, executed from entities.py's
own source text (the slice from `def _workflow_job_ids` to the R.check that follows `_GOV_JOBS`),
against a temp copy of .github/workflows.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/leads/l3_gov_pin.py [--perturb all-files]
Expected: escaping_cells=3 of 3 (exact); positive control governance.yml cell: pin fails 1 of 1;
          live_gov_missing=1 (rerun-stale-verdict, a governance job no GOV member names);
          --perturb all-files (the pin's `_workflow_job_ids(_DS_GOV)` widened, in memory, to the
          union over the derivation rule's files) -> escaping_cells=0 (the rerun cell also needs
          GOV to name the file: reported separately as rerun_cell_escapes).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: shared 4-core Linux leads box, venv314.
Instrumented symbols: tests/entities.py GOV pin (check 'the governance-cost GOV set names only jobs
the workflow files define'), tools/audit/round4/D11/governance_cost.py:GOV.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re, shutil, sys, tempfile, time
from pathlib import Path
t0p, t0t = time.process_time(), time.thread_time()
PERTURB = "--perturb" in sys.argv and sys.argv[sys.argv.index("--perturb") + 1] == "all-files"
ROOT = Path.cwd()
src = (ROOT / "tests/entities.py").read_text()
a = src.index("def _workflow_job_ids(")
b = src.index("_GOV_JOBS = _workflow_job_ids(_DS_GOV)")
end = src.index("\n)\n", b) + 3
SLICE = src[a:end]
if PERTURB:
    widened = SLICE.replace(
        "_GOV_JOBS = _workflow_job_ids(_DS_GOV)",
        "_GOV_JOBS = set().union(*(_workflow_job_ids(Path('.github/workflows', f).read_text()) for f in "
        "('governance.yml', 'pr-contract.yml', 'budget-raise-gate.yml', 'budget-raise-gate-rerun.yml')))")
    assert widened != SLICE
    SLICE = widened


class _R:
    def __init__(self):
        self.results = []

    def check(self, name, ok, detail=""):
        self.results.append((name, bool(ok)))


def run_pin(tmp):
    """Execute the pin slice with cwd = a temp tree carrying the probe workflows."""
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        R = _R()
        g = {"re": re, "Path": Path, "R": R, "__name__": "l3_gov_pin_slice",
             "_DS_GOV": Path(".github/workflows/governance.yml").read_text()}
        exec(compile(SLICE, str(ROOT / "tests/entities.py"), "exec"), g)
        return R.results[0][1], g["_GOV_MOD"].GOV, g["_ALL_JOB_IDS"]
    finally:
        os.chdir(cwd)


def tree_with(extra_file=None):
    tmp = Path(tempfile.mkdtemp(prefix="l3gov-"))
    shutil.copytree(ROOT / ".github/workflows", tmp / ".github/workflows")
    (tmp / "tools/audit/round4/D11").mkdir(parents=True)
    for f in ("governance_cost.py", "d11lib.py"):
        shutil.copy(ROOT / "tools/audit/round4/D11" / f, tmp / "tools/audit/round4/D11" / f)
    if extra_file:
        p = tmp / ".github/workflows" / extra_file
        p.write_text(p.read_text().rstrip("\n") + "\n  l3-probe-job:\n    runs-on: ubuntu-latest\n    steps:\n      - run: 'true'\n")
    return tmp


ok0, GOV, ALL = run_pin(tree_with())
print(f"baseline pin passes={ok0}")
missing = sorted(j for f in ("budget-raise-gate-rerun.yml",)
                 for j in re.findall(r"^  ([A-Za-z][\w-]*):", (ROOT / ".github/workflows" / f).read_text().split("\njobs:\n")[-1], re.M)
                 if j not in GOV)
escape = 0
cells = ("pr-contract.yml", "budget-raise-gate.yml", "budget-raise-gate-rerun.yml")
rerun_escapes = 0
for f in cells:
    ok, _, _ = run_pin(tree_with(f))
    escape += ok
    if f == "budget-raise-gate-rerun.yml":
        rerun_escapes = int(ok)
    print(f"cell new job in {f:30s} pin_passes={ok}")
ctl_ok, _, _ = run_pin(tree_with("governance.yml"))
print(f"control new job in governance.yml pin_passes={ctl_ok}")
print(f"RESULT baseline_pin_passes={int(ok0)}")
print(f"RESULT escaping_cells={escape} of {len(cells)} count")
print(f"RESULT rerun_cell_escapes={rerun_escapes}")
print(f"RESULT positive_control_pin_fails={int(not ctl_ok)} of 1 count")
print(f"RESULT live_gov_missing={len(missing)} count ({','.join(missing)})")
print(f"RESULT perturbed={int(PERTURB)}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:  # noqa: BLE001
    sw = -1
print(f"RESULT swapins={sw}")
