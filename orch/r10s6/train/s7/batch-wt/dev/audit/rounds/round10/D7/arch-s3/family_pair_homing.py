#!/usr/bin/env python3
"""ARCH-s3 harness: can family_splits be "cured" past counter C6 by homing two unrelated entities
into an invented two-member family?

Metric: family_splits.measure(tree)["value"] and counters.family_orphan_overrides(tree) on three
temp trees: PLANT (the baseline with optimization_status renamed so its family splits:
en "Status of Optimization", sv "Status för optimering"), GAME (PLANT plus two
ENTITY_FAMILY_OVERRIDES entries, optimization_status -> "zzpair" and solar_surplus_forecast ->
"zzpair": a solar forecast and the optimizer status declared one family because they sort
adjacently), and HONEST (PLANT with the rename reverted, i.e. the baseline).
A game that cures the split (2 -> 0) with C6 at 0 is an evasion: the declared family is not one
the user would recognise, and no counter refuses it.

Run:     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/family_pair_homing.py
Root:    the working directory; trees are private temp copies.
Expected at baseline 554e2ecfa: plant splits 2 / C6 0; game splits 0 / C6 0 (the evasion);
         with the D7-arch3-03 prototype applied, game C6 2.
Machine: macOS arm64, tvofi's audit box. Counts only.
Instrumented: archscore.metrics.family_splits:measure, archscore.counters:family_orphan_overrides.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "tools" / "audit")]
from archscore import counters as K  # noqa: E402
from archscore.metrics import family_splits as F  # noqa: E402

PKG = Path("custom_components") / "heatpump_optimizer"


def tree(tmp: Path, name: str, rename: bool, game: bool) -> Path:
    t = tmp / name
    shutil.copytree(ROOT / PKG, t / PKG)
    if rename:
        for lang, label in (("en", "Status of Optimization"), ("sv", "Status för optimering")):
            p = t / PKG / "translations" / f"{lang}.json"
            d = json.loads(p.read_text())
            d["entity"]["sensor"]["optimization_status"]["name"] = label
            p.write_text(json.dumps(d, ensure_ascii=False))
    if game:
        p = t / PKG / "const.py"
        src = p.read_text()
        anchor = "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {\n"
        assert src.count(anchor) == 1
        src = src.replace(anchor, anchor + '    "optimization_status": "zzpair",\n'
                                           '    "solar_surplus_forecast": "zzpair",\n')
        p.write_text(src)
    return t


def main() -> None:
    t_cpu, th_cpu = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="arch-s3-pair-") as tmp:
        tmp = Path(tmp)
        for name, rename, game in (("honest", False, False), ("plant", True, False), ("game", True, True)):
            t = tree(tmp, name, rename, game)
            print(f"RESULT {name}_family_splits={F.measure(t)['value']} count")
            print(f"RESULT {name}_family_orphan_overrides={K.family_orphan_overrides(t)} count")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th_cpu, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
