"""V2 probe for D7-arch2-01: does a mixin-supplied published property escape the finite scrub?

Metric (two numbers):
  mixin_supplied = (entity class, published name) pairs, over every class in the six platform
      modules that subclasses HeatPumpOptimizerEntity, whose MRO-resolved property is DEFINED on a
      package class that is NOT itself a HeatPumpOptimizerEntity subclass (a runtime-object mixin).
      Unlike scrub_escapes.py it does not look at the _finite_scrubbed mark; it asks only whether
      the shape the finding describes exists at baseline.
  nan_published = live NaN injection: a synthetic runtime-object mixin whose native_value returns
      float('nan') is mixed into a fresh HeatPumpOptimizerEntity subclass; reads instance.native_value.
      1 = NaN reaches the property HA reads (unscrubbed), 0 = scrubbed to None.
Null control: the same NaN-returning native_value defined on the entity class itself -> must read
  None (scrubbed), nan_published_null = 0.
Perturbation: --patch <file> (e.g. patches/00_scrub_resolves_mro.patch) applied to a temp tree;
  nan_published must go 1 -> 0 under patch 00.
Run (from a tree root): PYTHONPATH=tests/hastub python3 \
    dev/audit/rounds/round10/catchup/arch-s2/probe_scrub_mixin.py [--patch P ...]
Expected at baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef: mixin_supplied=0, nan_published=1,
nan_published_null=0; with patch 00: nan_published=0. Machine: shared macOS 8-core box; counts only.
"""
import argparse, importlib, inspect, math, os, shutil, subprocess, sys, tempfile
from pathlib import Path

def repo_root(start):
    here = Path(start).resolve().parent
    m = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for c in (here, *here.parents):
        if (c / m).is_file():
            return c
    raise RuntimeError("no root")

REPO = repo_root(__file__)
BASE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"
PLATFORMS = ("sensor", "binary_sensor", "climate", "button", "switch", "datetime")

ap = argparse.ArgumentParser(); ap.add_argument("--patch", action="append", default=[], type=Path)
a = ap.parse_args()
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore.score import tree_of
root = Path(tempfile.mkdtemp(prefix="cv-arch-s2-probe-"))
try:
    tree = tree_of(BASE, root / "t")
    for p in a.patch:
        subprocess.run(["patch", "-p1", "-s", "-d", str(tree), "-i", str(p.resolve())], check=True)
    sys.path.insert(0, str(tree / "custom_components"))
    ent = importlib.import_module("heatpump_optimizer.entity")
    B = ent.HeatPumpOptimizerEntity
    pairs, runtime_object_mixins = [], set()
    for plat in PLATFORMS:
        mod = importlib.import_module(f"heatpump_optimizer.{plat}")
        for _n, cls in inspect.getmembers(mod, inspect.isclass):
            if not cls.__module__.startswith("heatpump_optimizer"):
                continue
            if not issubclass(cls, B):
                runtime_object_mixins.add(f"{cls.__module__}.{cls.__name__}")
                continue
            for name in B._PUBLISHED:
                owner = next((k for k in cls.__mro__ if name in vars(k)), None)
                if owner is None or not owner.__module__.startswith("heatpump_optimizer"):
                    continue
                if not issubclass(owner, B):
                    pairs.append(f"{cls.__name__}.{name} from {owner.__name__}")
    print(f"RESULT runtime_object_mixins={len(runtime_object_mixins)} count  {sorted(runtime_object_mixins)}")
    print(f"RESULT mixin_supplied={len(pairs)} count")
    for p in pairs: print("  ", p)

    # Probe classes claim a package module: patch 00 skips owners outside the package, so a
    # __main__-defined class would be exempt for a reason unrelated to the mixin shape.
    class NanMixin:  # runtime base object, as sensor._SensorMixinBase is outside TYPE_CHECKING
        __module__ = "heatpump_optimizer.sensor"
        @property
        def native_value(self):
            return float("nan")
    class Probe(NanMixin, B):
        __module__ = "heatpump_optimizer.sensor"
    class NullProbe(B):
        __module__ = "heatpump_optimizer.sensor"
        @property
        def native_value(self):
            return float("nan")
    def read(cls):
        inst = cls.__new__(cls)
        v = cls.native_value.__get__(inst)
        return v
    class OutsideProbe(B):  # defined outside the package (a test module's subclass)
        @property
        def native_value(self):
            return float("nan")
    v1, v0, vo = read(Probe), read(NullProbe), read(OutsideProbe)
    print(f"RESULT nan_published_outside_pkg={int(isinstance(vo, float) and math.isnan(vo))} bool  (value={vo!r})")
    print(f"RESULT nan_published={int(isinstance(v1, float) and math.isnan(v1))} bool  (value={v1!r})")
    print(f"RESULT nan_published_null={int(isinstance(v0, float) and math.isnan(v0))} bool  (value={v0!r})")
finally:
    shutil.rmtree(root, ignore_errors=True)
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
