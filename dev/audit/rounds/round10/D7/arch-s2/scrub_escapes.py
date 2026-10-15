"""Published entity properties that escape the finite scrub (entity.HeatPumpOptimizerEntity.__init_subclass__).

Metric: escapes = (entity class, published property name) pairs, over every concrete
HeatPumpOptimizerEntity subclass the platforms define, whose RESOLVED property (``getattr(cls, name)``,
through the MRO) has an fget not marked ``_finite_scrubbed`` -- i.e. Home Assistant would read a value
the scrub never saw. Key: the property object Home Assistant resolves on the class.
Perturbation: --patch patches/01_payload_value_mixin.patch (a mixin whose runtime base is ``object``
supplies native_value) must raise the count; patch 09 (the scrub resolves through the MRO) must
bring it back to 0.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/scrub_escapes.py [--patch P ...]
Expected at baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef: escapes=0; with patch 01 alone: 17.
Machine: the seat's macOS box; counts only. Writes only under a tempfile.mkdtemp root.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import importlib  # noqa: E402
import inspect  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

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


REPO = repo_root(__file__)
BASE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"
PLATFORMS = ("sensor", "binary_sensor", "climate", "button", "switch", "datetime")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append", default=[], type=Path)
    a = ap.parse_args()
    t0, c0 = time.time(), time.process_time()
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore.score import tree_of
    root = Path(tempfile.mkdtemp(prefix="arch-s2-scrub-"))
    try:
        tree = tree_of(BASE, root / "t")
        for p in a.patch:
            subprocess.run(["patch", "-p1", "-s", "-d", str(tree), "-i", str(p.resolve())], check=True)
        sys.path.insert(0, str(tree / "custom_components"))
        entity = importlib.import_module("heatpump_optimizer.entity")
        base = entity.HeatPumpOptimizerEntity
        classes = set()
        for plat in PLATFORMS:
            mod = importlib.import_module(f"heatpump_optimizer.{plat}")
            for _n, cls in inspect.getmembers(mod, inspect.isclass):
                if issubclass(cls, base) and cls is not base:
                    classes.add(cls)
        escapes = []
        for cls in sorted(classes, key=lambda c: (c.__module__, c.__name__)):
            for name in base._PUBLISHED:
                prop = getattr(cls, name, None)
                if isinstance(prop, property) and prop.fget is not None \
                        and not getattr(prop.fget, "_finite_scrubbed", False):
                    owner = next(k.__name__ for k in cls.__mro__ if name in vars(k))
                    if owner in ("Entity", "SensorEntity", "ClimateEntity", "BinarySensorEntity",
                                 "ButtonEntity", "SwitchEntity", "DateTimeEntity", "CoordinatorEntity"):
                        continue  # Home Assistant's own default, which reads _attr_* the integration set
                    escapes.append(f"{cls.__module__.rsplit('.', 1)[-1]}.{cls.__name__}.{name} (from {owner})")
        print(f"RESULT entity_classes={len(classes)} count")
        print(f"RESULT escapes={len(escapes)} count")
        for e in escapes:
            print("  ", e)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
