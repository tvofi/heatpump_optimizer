#!/usr/bin/env python3
"""ARCH-s3 harness: which spellings of "no type" does untyped_payload_keys' counter C1 read as untyped?

Metric: for each spelling S, the headline untyped_payload_keys.measure(tree)["value"] on a temp copy
of the tree where every field of payload.py's ``EnergyTotals`` slice (6 keys, all seen by the
census at baseline) is declared ``S``. A spelling that states no type must read 6; one that reads
0 is a way to "type" a payload key that the score credits and nothing about the contract checks.
The control spellings: ``float`` (the real type) must read 0, bare ``Any`` must read 6.

Run:     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/payload_any_spellings.py
Root:    the working directory; the tree is copied to a private temp dir, never edited in place.
Expected at baseline 554e2ecfa: float 0, Any 6, object 6, NotRequired[Any] 6; Any | None 0,
         Optional[Any] 0, "Any" 0, an alias _Untyped = Any 0 (the four C1 gaps).
Machine: macOS arm64, tvofi's audit box. Counts only.
Instrumented: archscore.metrics.untyped_payload_keys:is_any (counter C1) via measure().
Perturbation: the census itself -- setting is_any to ``lambda a: False`` (ARCHSCORE_ABLATE=C1's
         switch) makes the Any row read 0 too, so the Any/object rows are live.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import re  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tools" / "audit")]
from archscore.metrics import common as C  # noqa: E402
from archscore.metrics import untyped_payload_keys as U  # noqa: E402

SPELLINGS = {
    "float": "float",
    "Any": "Any",
    "object": "object",
    "NotRequired_Any": "NotRequired[Any]",
    "Any_or_None": "Any | None",
    "Optional_Any": "Optional[Any]",
    "string_Any": '"Any"',
    "alias_Any": "_Untyped",
}
IMPORTS = "from typing import TYPE_CHECKING, Any, NotRequired, Optional, TypedDict\n_Untyped = Any\n"


def headline(tmp: Path, spelling: str) -> int:
    tree = tmp / spelling.replace(" ", "")[:20].replace('"', "q").replace("|", "_").replace("[", "_").replace("]", "_")
    dst = tree / "custom_components" / "heatpump_optimizer"
    shutil.copytree(ROOT / "custom_components" / "heatpump_optimizer", dst)
    p = dst / "payload.py"
    src = p.read_text()
    m = re.search(r"class EnergyTotals\(TypedDict, total=False\):\n((?:    .*\n)+)", src)
    body = m.group(1)
    src = src.replace(body, re.sub(r"^(    \w+): .*$", rf"\1: {spelling}", body, flags=re.M))
    src = src.replace("from typing import TYPE_CHECKING, TypedDict\n", IMPORTS)
    p.write_text(src)
    C.reset_caches()
    return U.measure(tree)["value"]


def main() -> None:
    t_cpu, th_cpu = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch-s3-any-") as tmp:
        tmp = Path(tmp)
        C.reset_caches()
        print(f"RESULT baseline_headline={U.measure(ROOT)['value']} count")
        for name, spelling in SPELLINGS.items():
            print(f"RESULT untyped_with_{name}={headline(tmp, spelling)} count")
        keep = U.is_any
        U.is_any = lambda a: False
        try:
            print(f"RESULT ablated_C1_untyped_with_Any={headline(tmp / 'ablate', 'Any')} count")
        finally:
            U.is_any = keep
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th_cpu, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
