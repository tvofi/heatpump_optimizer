#!/usr/bin/env python3
"""D7-03 harness: which persisted learners ingest a contaminated interval.

METRIC (one line): ingests[learner][arm] = the number of times a learner
object's own ingest method is called when the coordinator runs one interval's
learner pass while contamination signal `arm` is asserted; a learner that
ingests where HeatPumpOptimizerCoordinator._learning_frozen would have returned
a reason is un-gated.

RUN (from the repository root, nothing else):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/learner_freeze_matrix.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5). Counts only:
    contaminated_arms                  = 5 exactly
    ungated_learners                   = 2 exactly  (freq_map, start_counter)
    ungated_learner_names              = freq_map|start_counter
    gated_learners                     = 2 exactly  (accuracy, cop_scale)
    gated_learner_names                = accuracy|cop_scale
    arms_with_freeze_reason            = 5 exactly  (positive control: every
                                         contaminated arm DOES make
                                         _learning_frozen return a reason)
    freq_map_ingests_contaminated      = 5 exactly  (of 5 arms)
    start_counter_ingests_contaminated = 5 exactly  (of 5 arms)
    accuracy_ingests_contaminated      = 0 exactly  CONTROL
    cop_scale_ingests_contaminated     = 0 exactly  CONTROL
    clean_arm_ingests_freq_map         = 2 exactly  (positive control)
    clean_arm_ingests_accuracy         = 1 exactly  (positive control)
    clean_arm_ingests_cop_scale        = 1 exactly  (positive control)
    freq_map_cooling_ingests           = 2 exactly
    defrost / defrost_inferred         = 0 on EVERY arm including clean: this
                                         rig does not open a defrost window, so
                                         the derate is NOT exercised here and
                                         this harness says nothing about it.
    perturb_gated_freq_map_ingests_contaminated = 0 (must fall from 5)
    perturb_gated_clean_arm_ingests_freq_map    = 2 (must NOT fall)

WHAT IT SHOWS
    coordinator._learning_frozen is the project's single freeze predicate. Its
    docstring says "Fail closed... a learner that trains on a flatline or on
    heat it did not supply corrupts a parameter that is persisted to disk", and
    five callers consult it. The FREQUENCY MAP is persisted and rolled back
    with exactly those learners -- coordinator._apply_learner_payloads resets
    `self._freq_map = FrequencyMap()` in the same block as the curve learner and
    the solar aperture, with the comment "T7: the frequency map rolls back with
    its fellow learners" -- but coordinator._observe_frequency consults
    _learning_frozen nowhere. Its only guards are `_measured_power is None` and
    `_immersion_active`. The same is true of the compressor start counter in
    coordinator._observe_compressor_start, which prices wear into the ledger.

    The cooling arm is the one that matters most: pump_signals reports the heat
    pump running in COOLING mode, _learning_frozen returns that as a freeze
    reason, every gated learner stops -- and the frequency map keeps folding
    kW-per-Hz pairs measured in reverse-cycle operation into the map that
    coordinator._command_frequency later writes to the compressor while heating.

PERTURBATION (the judge's): in coordinator.py, _observe_frequency's fold
    `self._freq_map.observe(...)` -- add `if self._learning_frozen(
    CONF_POWER_ENTITY) is not None: return` immediately before it (one line).
    DIRECTION: freq_map_ingests_contaminated must fall from 5 to 0 while
    clean_arm_ingests_freq_map stays 2. The harness performs this mutation
    itself in a COPY of the tree under a private temp directory and never edits
    the tree under audit. Pass --no-mutate to skip that arm.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402
from pathlib import Path  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-5.0", unit="°C"),
    "sensor.hp_power": FakeState("2000", unit="W"),
    "sensor.freq": FakeState("55", unit="Hz"),
}
CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "power_entity": "sensor.hp_power",
    "compressor_freq_entity": "sensor.freq",
}

#: Every contamination signal _learning_frozen recognises, by the coordinator
#: state that asserts it. "clean" is the positive control.
ARMS = ("clean", "external_heat", "open_window", "pump_offline", "pump_fault",
        "pump_cooling")
CONTAMINATED = tuple(a for a in ARMS if a != "clean")

#: learner name -> (owning object attribute, ingest method name)
LEARNERS = {
    "freq_map": ("_freq_map", "observe"),
    "start_counter": ("_start_counter", "observe"),
    "accuracy": ("_accuracy", "record"),
    "defrost": ("_defrost", "observe_duty"),
    "defrost_inferred": ("_defrost", "observe"),
    "cop_scale": (None, "_apply_cop_scale"),
}


def build() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=CFG))


def apply_arm(coord: HeatPumpOptimizerCoordinator, arm: str) -> str | None:
    """Assert one contamination signal through the coordinator's own state."""
    if arm == "external_heat":
        coord._external_heat_active = True
    elif arm == "open_window":
        coord._vent_cusum.tripped = True
    elif arm in ("pump_offline", "pump_fault", "pump_cooling"):
        reason = {
            "pump_offline": "heat_pump_offline",
            "pump_fault": "heat_pump_fault",
            "pump_cooling": "heat_pump_cooling",
        }[arm]
        # pump_signals owns the reason; set it the way _learning_frozen reads it.
        object.__setattr__(coord._pump_signals, "freeze_reason", reason)
    return coord._learning_frozen("power_entity", "outdoor_temp_entity")


def instrument(coord: HeatPumpOptimizerCoordinator) -> dict[str, int]:
    """Count calls into each learner's own ingest method (instance-level wrap)."""
    counts = {name: 0 for name in LEARNERS}

    def wrap(owner, method, key):
        original = getattr(owner, method)

        def counted(*a, **kw):
            counts[key] += 1
            return original(*a, **kw)

        setattr(owner, method, counted)

    for key, (attr, method) in LEARNERS.items():
        owner = coord if attr is None else getattr(coord, attr)
        wrap(owner, method, key)
    return counts


def run_interval(coord: HeatPumpOptimizerCoordinator) -> None:
    """One interval's learner pass, through the coordinator's own entry points."""
    now = dt_util.now()
    coord._measured_power = 2.0
    coord._current_action = {
        "power": 2.0,
        "dhw_power": 0.0,
        "heat_pump_on": True,
        "power_normalized": 0.33,
    }
    # Arm a prediction 30 minutes old so the settle branch runs, then settle it.
    coord._record_accuracy()
    coord._pending_prediction["when"] = now - timedelta(minutes=30)
    coord._pending_prediction["predicted_temp"] = 21.0
    coord._pending_prediction["outdoor"] = -5.0
    coord._pending_prediction["power"] = 2.0
    coord._record_accuracy()
    coord._learn_measured_cop()


def measure(arm: str) -> tuple[dict[str, int], str | None]:
    coord = build()
    frozen = apply_arm(coord, arm)
    counts = instrument(coord)
    run_interval(coord)
    return counts, frozen


def mutated_arm(root: Path) -> dict[str, int]:
    """Gate the frequency fold on _learning_frozen in a COPY, re-measure."""
    with tempfile.TemporaryDirectory(prefix="d7-freeze-") as tmp:
        dst = Path(tmp) / "tree"
        subprocess.run(
            ["rsync", "-a", "--exclude", "__pycache__",
             "--exclude", ".abacus.donotdelete", f"{root}/", f"{dst}/"],
            check=True,
        )
        target = dst / "custom_components/heatpump_optimizer/coordinator.py"
        text = target.read_text(encoding="utf-8")
        needle = (
            "        if self._measured_power is None or self._immersion_active:\n"
            "            return\n"
            "        self._freq_map.observe(\n"
        )
        if needle not in text:
            return {"error": -1}
        target.write_text(
            text.replace(
                needle,
                "        if self._measured_power is None or self._immersion_active:\n"
                "            return\n"
                "        if self._learning_frozen(CONF_POWER_ENTITY) is not None:\n"
                "            return  # D7 spot mutation\n"
                "        self._freq_map.observe(\n",
            ),
            encoding="utf-8",
        )
        rel = Path(__file__).resolve().relative_to(root.resolve())
        env = dict(os.environ, PYTHONPATH="tests/hastub", HPO_PLANDATA=tmp)
        out = subprocess.run(
            [sys.executable, str(rel), "--child"], cwd=dst, env=env,
            capture_output=True, text=True,
        )
        got: dict[str, int] = {}
        for line in out.stdout.splitlines():
            if line.startswith("RESULT freq_map_ingests_contaminated="):
                got["contaminated"] = int(line.split("=")[1].split()[0])
            if line.startswith("RESULT clean_arm_ingests_freq_map="):
                got["clean"] = int(line.split("=")[1].split()[0])
        if not got:
            sys.stderr.write(out.stdout[-2000:] + out.stderr[-2000:])
        return got


def thread_factor() -> float:
    m = np.random.default_rng(0).standard_normal((300, 300))
    t0, w0 = time.process_time(), time.thread_time()
    for _ in range(6):
        m @ m
    t1, w1 = time.process_time(), time.thread_time()
    dt, dw = t1 - t0, w1 - w0
    return float(dt / dw) if dw > 1e-9 else 1.0


def main() -> int:
    child = "--child" in sys.argv
    table: dict[str, dict[str, int]] = {}
    frozen_reason: dict[str, str | None] = {}
    for arm in ARMS:
        counts, frozen = measure(arm)
        table[arm] = counts
        frozen_reason[arm] = frozen

    if not child:
        names = list(LEARNERS)
        print("\nINGESTS per learner per arm (one interval each)")
        print(f"  {'arm':<15} {'_learning_frozen':<22} " + " ".join(
            f"{n:>17}" for n in names))
        for arm in ARMS:
            print(
                f"  {arm:<15} {str(frozen_reason[arm]):<22} "
                + " ".join(f"{table[arm][n]:>17}" for n in names)
            )

    contaminated_totals = {
        n: sum(1 for a in CONTAMINATED if table[a][n] > 0) for n in LEARNERS
    }
    ungated = [n for n, v in contaminated_totals.items() if v == len(CONTAMINATED)]
    gated = [
        n
        for n, v in contaminated_totals.items()
        if v == 0 and table["clean"][n] > 0
    ]

    print()
    print(f"RESULT contaminated_arms={len(CONTAMINATED)} count")
    for n in LEARNERS:
        print(f"RESULT {n}_ingests_contaminated={contaminated_totals[n]} count")
        print(f"RESULT clean_arm_ingests_{n}={table['clean'][n]} count")
    print(f"RESULT freq_map_cooling_ingests={table['pump_cooling']['freq_map']} count")
    print(f"RESULT ungated_learners={len(ungated)} count")
    print(f"RESULT ungated_learner_names={'|'.join(sorted(ungated)) or 'none'} names")
    print(f"RESULT gated_learners={len(gated)} count")
    print(f"RESULT gated_learner_names={'|'.join(sorted(gated)) or 'none'} names")
    print(
        f"RESULT arms_with_freeze_reason="
        f"{sum(1 for a in CONTAMINATED if frozen_reason[a] is not None)} count"
    )

    if not child and "--no-mutate" not in sys.argv:
        got = mutated_arm(Path.cwd())
        print(
            "RESULT perturb_gated_freq_map_ingests_contaminated="
            f"{got.get('contaminated', -1)} count"
        )
        print(
            f"RESULT perturb_gated_clean_arm_ingests_freq_map="
            f"{got.get('clean', -1)} count"
        )

    print(f"RESULT thread_factor={thread_factor():.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT threads_alive={threading.active_count()} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
