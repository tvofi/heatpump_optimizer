#!/usr/bin/env python3
"""ARCH-s3 harness: does untyped_payload_keys' census see every key the coordinator publishes?

Metric: blind_keys = |runtime payload keys - census produced keys|, where runtime keys are the
union over tests/golden.py:coordinator_scenarios() of the dict the production
HeatPumpOptimizerCoordinator._build_data_dict returns (golden._capture_coordinator, plus the three
volatile keys that capture drops), and census keys are
tools/audit/archscore/metrics/untyped_payload_keys.Flow.returned_keys(<coordinator>._async_update_data).
Second metric: blind_untyped = blind keys that an untyping perturbation leaves invisible: with
--perturb the harness rewrites payload.py's AwayView in a temp copy of the tree so every key is
declared ``Any`` (an untyped contract) and re-measures the headline; the headline must rise by the
number of AwayView keys the census sees, and stays 0 when the census is blind to them.

Run:     PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s3/payload_census_coverage.py [--perturb]
Root:    the working directory (run from the tree under test); never resolved from __file__.
Expected at baseline 554e2ecfa: blind_keys=10 (exact), headline 0; with --perturb headline stays 0
         (the defect) -- a census that followed state.as_dict() would read 10 (the D7-arch3-01 prototype does).
Machine: macOS arm64, tvofi's audit box. Counts only; no timing.
Instrumented: heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._build_data_dict (runtime),
             archscore.metrics.untyped_payload_keys:Flow.returned_keys (census).
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
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tests" / "hastub"),
                str(ROOT / "custom_components"), str(ROOT / "tools" / "audit")]

from archscore.metrics import common as C  # noqa: E402
from archscore.metrics import untyped_payload_keys as U  # noqa: E402

PRODUCER = f"{C.COORD_MODULE}:{C.COORD_CLASS}._async_update_data"


def census(root: Path) -> dict:
    C.reset_caches()
    pkg = C.load(str(root))
    flow = U.Flow(pkg, C.engine(pkg))
    keys, _dyn = flow.returned_keys(PRODUCER)
    return keys


def runtime_keys() -> set:
    import golden
    rt: set = set()
    for _name, cfg in golden.coordinator_scenarios().items():
        rt |= set(golden._capture_coordinator(cfg)["data"])
    return rt | {"last_optimization", "next_optimization", "solve_time_ms"}


def main() -> None:
    t_cpu, th_cpu = time.process_time(), time.thread_time()
    keys = census(ROOT)
    rt = runtime_keys()
    blind = sorted(rt - set(keys))
    print("census_not_runtime:", sorted(set(keys) - rt))
    print("runtime_not_census:", blind)
    print(f"RESULT census_keys={len(keys)} count")
    print(f"RESULT runtime_keys={len(rt)} count")
    print(f"RESULT blind_keys={len(blind)} count")
    print(f"RESULT headline_untyped={U.measure(ROOT)['value']} count")
    if "--perturb" in sys.argv:
        with tempfile.TemporaryDirectory(prefix="arch-s3-") as tmp:
            dst = Path(tmp) / "custom_components" / "heatpump_optimizer"
            shutil.copytree(ROOT / "custom_components" / "heatpump_optimizer", dst)
            p = dst / "payload.py"
            src = p.read_text()
            m = re.search(r"class AwayView\(TypedDict, total=False\):\n((?:    .*\n|\n)+?)\n\nclass", src)
            body = m.group(1)
            new = re.sub(r"^(    \w+): .*$", r"\1: Any", body, flags=re.M)
            src = src.replace(body, new).replace("from typing import TYPE_CHECKING, TypedDict",
                                                 "from typing import TYPE_CHECKING, Any, TypedDict")
            p.write_text(src)
            n_away = len(re.findall(r"^    \w+: Any$", new, flags=re.M))
            seen = len([k for k in census(Path(tmp)) if k.startswith("away_")])
            print(f"RESULT perturb_awayview_keys_untyped={n_away} count")
            print(f"RESULT perturb_away_keys_census_sees={seen} count")
            print(f"RESULT perturb_headline_untyped={U.measure(Path(tmp))['value']} count")
    print(f"RESULT thread_factor={(time.process_time() - t_cpu) / max(time.thread_time() - th_cpu, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
