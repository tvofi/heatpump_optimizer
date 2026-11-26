"""Probe helper: the production thermal_model.py with ONE line replaced, loaded as a scratch module
(in memory; the tree is never written). load(line, old, new) -> (baseline_module, mutant_module)."""
import os, sys, types
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from pathlib import Path
# Probes read a pristine baseline export (git archive of the baseline sha), never the gate's tree, which
# carries a mutant while a gate runs. PROBE_ROOT overrides; default ~/probe-tree.
ROOT = Path(os.environ.get("PROBE_ROOT", os.path.expanduser("~/probe-tree")))
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), ROOT
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import thermal_model as base  # noqa: E402

def load(line, old, new):
    lines = Path(base.__file__).read_text().split("\n")
    assert lines[line - 1].strip() == old.strip(), (lines[line - 1], old)
    ind = lines[line - 1][: len(lines[line - 1]) - len(lines[line - 1].lstrip())]
    lines[line - 1] = ind + new.strip()
    name = "custom_components.heatpump_optimizer.thermal_model_mut"
    mod = types.ModuleType(name)
    mod.__file__ = base.__file__
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = mod  # dataclasses need it registered
    exec(compile("\n".join(lines), base.__file__, "exec"), mod.__dict__)
    return base, mod
