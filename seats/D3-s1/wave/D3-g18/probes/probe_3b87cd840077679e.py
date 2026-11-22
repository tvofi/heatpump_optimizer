#!/usr/bin/env python3
# Metric: over every catalog choice plus two unknown ids, the count of grid_fee.apply_catalog calls whose returned
#   config fields differ under the mutant, and (separately) the count whose DEBUG log text differs.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_3b87cd840077679e.py
# EXPECTED RESULT ids_tried=5 count
# EXPECTED RESULT differing_returns=0 count          (CATALOG_VERSION is read by no code path that writes config)
# EXPECTED RESULT differing_debug_text=2 count       ("Applying DSO catalog v1" -> "v2", one per real product)
# EXPECTED RESULT production_readers_of_constant=1 count  (grid_fee.py:497, the debug line; AST count of Name loads)
# EXPECTED RESULT null_delta_returns=0 count         (the baseline against itself)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.grid_fee:CATALOG_VERSION (grid_fee.py:445), read by apply_catalog (497).
# Perturbation: mutant 3b87cd840077679e, CATALOG_VERSION = 1 -> 2, applied in memory with
#   mock.patch.object(grid_fee, "CATALOG_VERSION", 2). Direction: only the DEBUG record's text moves.
# Inputs: "none", "ellevio_villa_effekt_2026", "goteborg_energi_effekt_2026", "not_a_dso", None.
# Null control: the baseline against itself; the reader count is taken from the AST of every production module.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import ast  # noqa: E402
import logging  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import grid_fee as gf  # noqa: E402


class Keep(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.msgs = []

    def emit(self, record):
        self.msgs.append(record.getMessage())


def call(pid, mutant):
    h = Keep()
    log = logging.getLogger(gf.__name__)
    log.addHandler(h)
    log.setLevel(logging.DEBUG)
    ctx = mock.patch.object(gf, "CATALOG_VERSION", 2) if mutant else mock.MagicMock()
    try:
        with ctx:
            out = gf.apply_catalog(pid)
    finally:
        log.removeHandler(h)
    return out, h.msgs


IDS = [gf.DSO_PRODUCT_NONE, *gf.SWEDEN_CATALOG, "not_a_dso", None]
dr = sum(1 for p in IDS if call(p, False)[0] != call(p, True)[0])
dt = sum(1 for p in IDS if call(p, False)[1] != call(p, True)[1])
null = sum(1 for p in IDS if call(p, False)[0] != call(p, False)[0])
readers = 0
for path in sorted((ROOT / "custom_components" / "heatpump_optimizer").rglob("*.py")):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Name) and node.id == "CATALOG_VERSION" and isinstance(node.ctx, ast.Load):
            readers += 1
        if isinstance(node, ast.Attribute) and node.attr == "CATALOG_VERSION":
            readers += 1
print(f"RESULT ids_tried={len(IDS)} count")
print(f"RESULT differing_returns={dr} count")
print(f"RESULT differing_debug_text={dt} count")
print(f"RESULT production_readers_of_constant={readers} count")
print(f"RESULT null_delta_returns={null} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
