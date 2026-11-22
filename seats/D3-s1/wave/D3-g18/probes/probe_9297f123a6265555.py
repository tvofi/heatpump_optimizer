#!/usr/bin/env python3
# Metric: WARNING records the heatpump_optimizer.grid_fee logger emits when the config flow's grid-fee step
#   finishes (config_flow._apply_dso_catalog -> grid_fee.apply_catalog) with the DSO product left at its "none"
#   choice, absent, or empty; and how many of those submits come back with different stored fields.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_9297f123a6265555.py
# EXPECTED RESULT warnings_baseline=0 count
# EXPECTED RESULT warnings_mutant=3 count          ("Unknown DSO catalog product none|None|; not writing", one per submit)
# EXPECTED RESULT differing_stored_fields=0 count  (the return is None either way: nothing is written)
# EXPECTED RESULT null_delta_warnings=0 count      (a real catalog product: both arms write the row, no warning)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g18 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: heatpump_optimizer.grid_fee:apply_catalog, line 483
#   `if not product_id or product_id == DSO_PRODUCT_NONE:`, driven through config_flow._apply_dso_catalog (2067),
#   the `finish` of the grid-fee step (config_flow.py:3919).
# Perturbation: mutant 9297f123a6265555, the guard -> `if False:`, applied in memory (apply_catalog is recompiled
#   from its own source and patched onto grid_fee for the mutant arm). Direction: warnings up by one per submit
#   whose product is "none" (the default choice), absent or empty; stored fields unchanged.
# Inputs: submits with dso_product "none", absent, "" (moving), and "goteborg_energi_effekt_2026" (null arm).
# Null control: a real catalog product id, which both arms resolve and write with no warning.
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
import inspect  # noqa: E402
import logging  # noqa: E402
import textwrap  # noqa: E402
from unittest import mock  # noqa: E402

from heatpump_optimizer import config_flow as cf  # noqa: E402
from heatpump_optimizer import grid_fee as gf  # noqa: E402

OLD = "if not product_id or product_id == DSO_PRODUCT_NONE:"
SRC = textwrap.dedent(inspect.getsource(gf.apply_catalog))
assert SRC.count(OLD) == 1, "anchor line moved"
NS = dict(gf.__dict__)
exec(compile(SRC.replace(OLD, "if False:", 1), gf.__file__, "exec"), NS)
MUT = NS["apply_catalog"]


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


def submit(product, mutant):
    h = Count()
    log = logging.getLogger(gf.__name__)
    log.addHandler(h)
    log.setLevel(logging.DEBUG)
    cleaned = {"grid_fee_mode": "none"}
    if product is not ...:
        cleaned[cf.CONF_DSO_PRODUCT] = product
    ctx = mock.patch.object(gf, "apply_catalog", MUT) if mutant else mock.MagicMock()
    try:
        with ctx:
            out = cf._apply_dso_catalog(dict(cleaned), {})
    finally:
        log.removeHandler(h)
    return h.n, out


MOVING = (gf.DSO_PRODUCT_NONE, ..., "")
wb = sum(submit(p, False)[0] for p in MOVING)
wm = sum(submit(p, True)[0] for p in MOVING)
diff = sum(1 for p in MOVING if submit(p, False)[1] != submit(p, True)[1])
real = "goteborg_energi_effekt_2026"
nb, ob = submit(real, False)
nm, om = submit(real, True)
print(f"RESULT warnings_baseline={wb} count")
print(f"RESULT warnings_mutant={wm} count")
print(f"RESULT differing_stored_fields={diff} count")
print(f"RESULT null_delta_warnings={abs(nm - nb) + int(ob != om)} count")

import resource as _resource  # noqa: E402
import time as _time  # noqa: E402

print(f"RESULT thread_factor={_time.process_time() / max(_time.thread_time(), 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={_resource.getrusage(_resource.RUSAGE_SELF).ru_nswap} count")
