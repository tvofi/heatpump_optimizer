"""Shared in-memory mutation helper for the D3-g46-h probes (no production file is written)."""
import os, sys, inspect, textwrap
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
_here = Path(__file__).resolve()
ROOT = Path(os.environ["PROBE_ROOT"]) if os.environ.get("PROBE_ROOT") else next(c for c in _here.parents if (c / "custom_components/heatpump_optimizer/manifest.json").is_file())
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import thermal_model as tm  # noqa: E402


def mutant(name, old, new):
    """Recompile module-level function `name` with the single line `old` replaced by `new`
    (exactly one occurrence, indentation kept), in the module's own namespace."""
    src = inspect.getsource(getattr(tm, name))
    assert src.count(old) == 1, (name, old, src.count(old))
    ns = tm.__dict__
    exec(compile(src.replace(old, new), f"<mutant {name}>", "exec"), ns, loc := {})
    return loc[name]
