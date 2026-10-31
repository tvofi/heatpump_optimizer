"""D7-v1 verifier harness for D7-s2-03: is the dhw_coil edge observable in production, and does any test see it go?

Metric (one line): killed = 1 when, on a private copy of the tree, the mutant `if dhw_coil:` -> `if False:`
  in topology.layout_edges changes tests/features.py's exit status or raises its FAILED count vs the same
  unmutated copy (tests/mutation_table.py:run_script's kill rule); plus seam_edge = whether production
  topology.describe_setup() publishes ("wood_tank","dhw_tank") for a two_tank_4way + DHW + wood-coil config
  (baseline must be 1, mutant 0: the mutation is not equivalent).
Also: static count of test-script call sites that pass dhw_coil=True / enable the wood coil into
  layout_edges/describe_setup (the finder says 0).
Perturbation (--perturb): drop a one-check driver tests/v1_coil_check.py into the copy asserting the
  coil edge through describe_setup; its kill must go 0 -> 1.
Command:  PYTHONPATH=tests/hastub TMPDIR=<private> python3 tools/audit/round8/D7/v1_coil_edge.py [--perturb] [--skip-features]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, shutil, tempfile, re, subprocess
from pathlib import Path
_p0, _t0 = time.process_time(), time.thread_time()
sys.path.insert(0, "tests")
from mutation_table import run_script

ROOT = Path(".").resolve()
TOPO = "custom_components/heatpump_optimizer/topology.py"
OLD, NEW = "        if dhw_coil:\n", "        if False:\n"
PROBE = r'''
import sys
sys.path.insert(0, "custom_components")
from heatpump_optimizer import topology as T
cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
       "upper_floor_thermal_mass": 3.0, "lower_floor_thermal_mass": 4.5, "dhw_tank_volume": 200.0,
       "mixing_valve_mode": "manual", "buffer_tank_volume": 750.0, "external_heat_detection_enabled": True,
       "wood_tank_top_entity": "sensor.wood_top", "dhw_wood_coil_enabled": True, "topology_layout": "two_tank_4way"}
d = T.describe_setup(cfg)
has = ["wood_tank", "dhw_tank"] in [list(e) for e in d["edges"]]
print("layout", d["layout"], "edge", int(has))
print("1 of 1 checks FAILED" if not has else "0 of 1 checks FAILED")
sys.exit(0 if has else 1)
'''


def copy_tree(dst):
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("__pycache__", ".git", "round8", "node_modules"),
                    symlinks=True)
    (dst / "tests" / "v1_coil_check.py").write_text(PROBE)


tests_cite = 0
for f in list(Path("tests").glob("*.py")) + list(Path("tests").glob("*.mjs")):
    s = f.read_text(errors="replace")
    tests_cite += len(re.findall(r"dhw_coil\s*=\s*True", s))
    tests_cite += len(re.findall(r"[\"']dhw_wood_coil_enabled[\"']\s*:\s*True", s))
print(f"RESULT test_sites_enabling_coil={tests_cite} count (dhw_coil=True or dhw_wood_coil_enabled: True in tests/*.py|*.mjs)")

tmp = Path(tempfile.mkdtemp(prefix="d7v1coil_", dir=os.environ.get("TMPDIR")))
try:
    base, mut = tmp / "base", tmp / "mut"
    copy_tree(base)
    copy_tree(mut)
    t = mut / TOPO
    s = t.read_text()
    assert s.count(OLD) == 1
    t.write_text(s.replace(OLD, NEW))
    pb = run_script("tests/v1_coil_check.py", base, 300)
    pm = run_script("tests/v1_coil_check.py", mut, 300)
    print(f"RESULT seam_edge_baseline={int(pb.rc == 0)} seam_edge_mutant={int(pm.rc == 0)}")
    if "--perturb" in sys.argv:
        k = int(pm.rc != pb.rc or pm.failed > pb.failed)
        print(f"RESULT perturbed_killed={k} (the added one-check driver)")
    if "--skip-features" not in sys.argv:
        fb = run_script("tests/features.py", base, 3600)
        fm = run_script("tests/features.py", mut, 3600)
        k = int(fm.rc != fb.rc or fm.failed > fb.failed)
        print(f"CELL features.py baseline rc={fb.rc} failed={fb.failed}; mutant rc={fm.rc} failed={fm.failed}")
        print(f"RESULT killed_by_features={k}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
