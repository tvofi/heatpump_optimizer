#!/usr/bin/env python3
"""D6-s3-02: en.json says loose firewood "is billed at 0.60 of packed"; the
production energy table the wood price is computed from does not hold that
for every wood type.

Metric (one line): wood types for which
useful_kwh_m3(type, "loose", e) / useful_kwh_m3(type, "packed", e) differs from
the 0.60 the options text (options.step.building.sections.wood
.data_description.wood_packing) states, by more than 1e-9.
Key: the ratio is read from the value the production seam delivers
(`wood_fuel.useful_kwh_m3`, which `wood_sek_per_kwh` and every wood price
derive from), never from en.json alone.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s3/wood_packing_ratio.py [--perturb]

Expected on the export audited (box B3, linux; see the provenance note):
    RESULT types_off_claim=1 count            (birch: loose/packed = 1.667; exact)
    RESULT birch_packed_kwh_m3=1140, birch_loose_kwh_m3=1900  (exact)
    RESULT pine_ratio=0.600, mixed_ratio=0.600 (null control: the other two types hold the claim)
    RESULT packed_birch_sek_per_kwh=1.4035 at 1200 SEK/m3, 75 %  (the published wood price;
                                               0.8421 if packed birch held 1900 kWh/m3 as
                                               tests/features.py's "birch packed is 1900 kWh/m3" pins)
--perturb (in memory: birch's two entries exchanged) -> types_off_claim=0.

Provenance: the export's wood_fuel.py differs from commit
92d38ecb640bd462f2e19c0814d0f0b7df1ee692 on exactly this row (the commit holds
packed 1900 / loose 1140). The finding is measured on the export the seat was
told to audit; the judge decides which tree it binds.

Instrumented symbol: heatpump_optimizer.wood_fuel:useful_kwh_m3 (table WOOD_KWH_M3),
consumer heatpump_optimizer.wood_fuel:wood_sek_per_kwh.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import pathlib  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from unittest import mock  # noqa: E402

ROOT = pathlib.Path.cwd()
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "custom_components")]

from heatpump_optimizer import wood_fuel  # noqa: E402

EN = json.loads((ROOT / "custom_components/heatpump_optimizer/translations/en.json").read_text())


def claimed_ratio():
    text = EN["options"]["step"]["building"]["sections"]["wood"]["data_description"]["wood_packing"]
    m = re.search(r"billed at (\d+(?:\.\d+)?) of packed", text)
    assert m, text
    return float(m.group(1))


def main():
    perturb = "--perturb" in sys.argv
    t0p, t0t = time.process_time(), time.thread_time()
    claim = claimed_ratio()
    table = {k: dict(v) for k, v in wood_fuel.WOOD_KWH_M3.items()}
    if perturb:
        b = table["birch"]
        table["birch"] = {"packed": b["loose"], "loose": b["packed"]}
    with mock.patch.dict(wood_fuel.WOOD_KWH_M3, table):
        off = 0
        for wtype in sorted(wood_fuel.WOOD_KWH_M3):
            packed = wood_fuel.useful_kwh_m3(wtype, "packed", 100.0)
            loose = wood_fuel.useful_kwh_m3(wtype, "loose", 100.0)
            ratio = loose / packed
            off += abs(ratio - claim) > 1e-9
            print(f"RESULT {wtype}_packed_kwh_m3={packed:g} kWh/m3")
            print(f"RESULT {wtype}_loose_kwh_m3={loose:g} kWh/m3")
            print(f"RESULT {wtype}_ratio={ratio:.3f}")
        price = wood_fuel.wood_sek_per_kwh(1200.0, "birch", "packed", 75.0)
    print(f"RESULT claimed_ratio={claim:g}")
    print(f"RESULT types_off_claim={off} count")
    print(f"RESULT packed_birch_sek_per_kwh={price:.4f} SEK/kWh")
    print(f"RESULT perturbed={int(perturb)}")
    dp, dt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={dp / dt if dt > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        swap = next(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except (OSError, StopIteration):
        swap = -1
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()
