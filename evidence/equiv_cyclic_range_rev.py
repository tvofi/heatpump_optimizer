"""Behaviour equivalence for patch 07: grid_fee.parse_month_range / parse_day_range before and after.

Metric: mismatches = tokens (every ordered pair of every month and weekday spelling joined by '-',
every single spelling, and 6 malformed tokens) whose result -- the frozenset, or the exception
type and message -- differs between the baseline module and the patched module.

Perturbation: --break flips the patched owner's wrap (drops the last value of a wrapping range);
mismatches must then be > 0.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/equiv_cyclic_range.py [--break]
Expected: tokens=522, mismatches=0 (tolerance 0); with --break mismatches > 0.
Baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef. Machine: the seat's macOS box.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util  # noqa: E402
import itertools  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
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


REPO = Path(os.environ["EQ_REPO"])
BASE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"
PATCH = Path(__file__).resolve().parent / "patches" / "07_cyclic_range.patch"


def load(path: Path, name: str):
    pkg = types.ModuleType(name)
    pkg.__path__ = [str(path.parent)]
    sys.modules[name] = pkg
    spec = importlib.util.spec_from_file_location(f"{name}.grid_fee", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def answer(fn, tok):
    try:
        return sorted(fn(tok))
    except Exception as exc:  # noqa: BLE001
        return f"{type(exc).__name__}: {exc}"


def main() -> int:
    t0, c0 = time.time(), time.process_time()
    root = Path(tempfile.mkdtemp(prefix="arch-s2-eq-"))
    try:
        sys.path.insert(0, str(REPO / "tools" / "audit"))
        base = Path(os.environ["EQ_BASE"])
        head = root / "head"
        shutil.copytree(Path(os.environ["EQ_HEAD"]) / "custom_components", head / "custom_components")
        rel = Path("custom_components/heatpump_optimizer/grid_fee.py")
        if "--break" in sys.argv:
            f = head / rel
            txt = f.read_text(); assert "range((end - start) % size + 1)" in txt; f.write_text(txt.replace("range((end - start) % size + 1)", "range((end - start) % size)"))
        b = load(base / rel, "hpo_base")
        h = load(head / rel, "hpo_head")
        toks = []
        for names in (b._MONTHS, b._DAYS):
            toks += [f"{x}-{y}" for x, y in itertools.product(names, names)] + list(names)
        toks += ["", "foo", "jan-foo", "mon-", " Nov - Mar ", "MÅN-fre"]
        bad = 0
        for fn in ("parse_month_range", "parse_day_range"):
            for tok in toks:
                if answer(getattr(b, fn), tok) != answer(getattr(h, fn), tok):
                    bad += 1
        print(f"RESULT tokens={len(toks)} count")
        print(f"RESULT mismatches={bad} count")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
