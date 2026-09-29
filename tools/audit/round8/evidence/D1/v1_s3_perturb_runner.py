"""D1 verifier v1: re-runs the finder's s3_openmeteo_hostile.py under the finder's
stated perturbation (_parse_block returns _EMPTY when block is not a dict),
applied in-process to the module object that harness imports; never on disk.
Command (tree root): PYTHONPATH=tests/hastub <thread pins> python3 tools/audit/round8/D1/v1_s3_perturb_runner.py
"""
import os, runpy, sys
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.getcwd())
from custom_components.heatpump_optimizer import open_meteo as om
orig = om._parse_block
def guarded(block, variable, max_value=om._MAX_PLAUSIBLE_GHI):
    if not isinstance(block, dict):
        return om._EMPTY
    return orig(block, variable, max_value)
om._parse_block = guarded
try:
    runpy.run_path("tools/audit/round8/D1/s3_openmeteo_hostile.py", run_name="__main__")
finally:
    om._parse_block = orig
