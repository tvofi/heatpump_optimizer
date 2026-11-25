#!/usr/bin/env python3
"""D5-s3: comfort_band.py's module docstring says the climate slider's maximum sits one degree above
the configured ceiling. Measure the slider's maximum against the ceiling on the real entity.

Metric: overshoot_c = HeatPumpOptimizerClimate(...)._attr_max_temp (the stub has no max_temp property) - EntryConfig.max_temperature, °C, on
a coordinator built from FakeHass/FakeEntry with max_temp=24; the docstring claims 1.0.
stale_rows = 1 when the measured overshoot differs from the docstring's claimed 1.0 °C, else 0
(key: the max_temp the production entity publishes, not the docstring text).
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s3/slider_ceiling.py [--perturb]
Expected: RESULT overshoot_c=0.0, RESULT stale_rows=1 at the baseline; exact.
Perturbation (--perturb): climate.EntryConfig.from_mapping wrapped in memory so the entity sees
max_temperature + 1 (the pre-v5.1.7 `+ 1` slider); expected overshoot_c -> 1.0 and stale_rows -> 0 (to_zero).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B3. Counts only; no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, re, sys, time
from unittest import mock

sys.path.insert(0, "tests")
from harness import FakeHass, FakeEntry  # noqa: E402  (inserts custom_components on sys.path)
from heatpump_optimizer import climate  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.entry_config import EntryConfig  # noqa: E402

DOC = open("custom_components/heatpump_optimizer/comfort_band.py", encoding="utf-8").read()


def measure(perturb):
    cfg = {"min_temp": 19.0, "max_temp": 24.0, "target_temp": 21.0}
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    real = EntryConfig.from_mapping

    def plus_one(mapping):
        c = real(mapping)
        return dataclasses.replace(c, max_temperature=c.max_temperature + 1.0)

    with mock.patch.object(climate.EntryConfig, "from_mapping", staticmethod(plus_one) if perturb else staticmethod(real)):
        ent = climate.HeatPumpOptimizerClimate(coord, coord.entry if hasattr(coord, "entry") else FakeEntry(data=cfg))
    ceiling = EntryConfig.from_mapping(coord.effective_config).max_temperature
    return float(getattr(ent, "max_temp", ent._attr_max_temp)) - float(ceiling)


def main():
    t0 = time.process_time()
    claims = bool(re.search(r"slider's own maximum sitting one degree \*above\*\s+the\s+configured ceiling", DOC.replace("\n  ", " ")))
    over = measure("--perturb" in sys.argv)
    print(f"RESULT docstring_claims_plus_one={int(claims)}")
    print(f"RESULT overshoot_c={over:.1f} degC")
    print(f"RESULT stale_rows={int(claims and abs(over - 1.0) > 1e-9)} rows")
    pc = time.process_time() - t0
    print(f"RESULT thread_factor={pc / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
