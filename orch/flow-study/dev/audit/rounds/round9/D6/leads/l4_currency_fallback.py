"""L4 lead (raised by D14-s2) for D6-s1 / D6.M1 -- the documented SEK fallback under real Home Assistant.

Claim under test: README.md ("`CUR` is your Home Assistant instance currency (SEK when the instance
  has none ...)") and currency.py's docstring/FALLBACK_CURRENCY: an instance with no currency
  labels money in SEK.
Metric (one line): fallback_reached = HA core versions (of 2: hacs.json's minimum 2025.2.0 and the
  newest wheel pip resolves) for which currency.resolve_currency, handed an instance whose
  Config.currency is HA core's own constructor default, returns FALLBACK_CURRENCY.
  The default is read from the wheel's homeassistant/core_config.py by AST (Config.__init__'s
  `self.currency` assignment), never assumed. Count key: resolve_currency's return value.
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/leads/l4_currency_fallback.py [--perturb] [--wheels DIR]
  Needs network for `pip download --no-deps` into a mktemp root, or --wheels DIR holding the wheels.
Perturbation (--perturb): currency.resolve_currency replaced in memory by `lambda hass:
  FALLBACK_CURRENCY` (the fallback made unconditional). Expected: fallback_reached 0 -> 2 (up).
Null control: the same call on the test stub's instance (tests/harness.py FakeHass), which pins
  currency "SEK" itself -- the only place the SEK label can come from.
Expected: fallback_reached=0 of 2 (2025.2.0 and 2026.2.3 both default 'EUR'); --perturb 2 of 2. Exact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container.
Instrumented: currency:resolve_currency; HA core homeassistant/core_config.py:Config.__init__ (read).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import glob
import subprocess
import sys
import tempfile
import time
import zipfile
from types import SimpleNamespace
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass  # noqa: E402
from heatpump_optimizer import currency  # noqa: E402

if "--perturb" in sys.argv:
    currency.resolve_currency = lambda hass: currency.FALLBACK_CURRENCY


def wheels():
    if "--wheels" in sys.argv:
        d = sys.argv[sys.argv.index("--wheels") + 1]
    else:
        d = tempfile.mkdtemp(prefix="l4_ha_")
        for spec in ("homeassistant==2025.2.0", "homeassistant"):
            subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "-q", "-d", d, spec],
                           check=True)
    return sorted(glob.glob(os.path.join(d, "homeassistant-*.whl")))


def core_default(whl):
    src = zipfile.ZipFile(whl).read("homeassistant/core_config.py").decode()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ClassDef) and node.name == "Config":
            for fn in node.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == "__init__":
                    for st in ast.walk(fn):
                        tgt = getattr(st, "target", None) or (getattr(st, "targets", [None]) or [None])[0]
                        if (isinstance(tgt, ast.Attribute) and tgt.attr == "currency"
                                and isinstance(getattr(st, "value", None), ast.Constant)):
                            return st.value.value
    raise RuntimeError(f"no Config.__init__ currency default in {whl}")


def main():
    t0, th0 = time.process_time(), time.thread_time()
    ws = wheels()
    reached = 0
    for w in ws:
        default = core_default(w)
        got = currency.resolve_currency(SimpleNamespace(config=SimpleNamespace(currency=default)))
        reached += int(got == currency.FALLBACK_CURRENCY)
        print(f"HA {os.path.basename(w)} Config.currency default={default!r} -> resolve_currency={got!r}")
    stub = currency.resolve_currency(FakeHass({}))
    print(f"RESULT ha_versions={len(ws)} count")
    print(f"RESULT fallback_reached={reached} of {len(ws)}")
    print(f"RESULT stub_resolves_to={stub} (null control: the stub pins it)")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
