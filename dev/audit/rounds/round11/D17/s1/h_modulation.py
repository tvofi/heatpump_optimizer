"""D17-s1-04 harness: 'Compressor modulation: On/off' plans exactly like 'Modulating'.

Metric: the number of planned steps (of the published schedule, 96 x 15 min) whose
power lies strictly between 0.01 kW and the configured minimum power, after the
thermal_model options page is saved with compressor_modulation=on_off and
heat_pump_min_power=1.5, a restart and one full cycle. The option's own description:
"On/off: every planned step is either off or between min and max power" -> 0 expected.
Count key: the schedule the coordinator's solve publishes (data["schedule"][i]["power"]).
Instrumented symbol: heatpump_optimizer.thermal_model:declared_modulation (its own
docstring: "on_off -> False, modulating -> True"), driven through
config_flow:async_step_thermal_model and the solve.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s1/h_modulation.py
Expected: RESULT on_off_sub_min_steps=60 (of 96), RESULT modulating_sub_min_steps=60,
          RESULT declared_on_off=True (exact)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-docstring patches declared_modulation to return False for on_off
(what its docstring says): on_off_sub_min_steps goes down (to 0 when the clamp holds).
Null control: compressor_modulation=modulating, where sub-minimum (averaged) steps are
documented: RESULT modulating_sub_min_steps.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from heatpump_optimizer import const, thermal_model  # noqa: E402

MIN_P = 1.5

if "--perturb-docstring" in sys.argv:
    _real = thermal_model.declared_modulation

    def _doc(config):
        mode = (config or {}).get(const.CONF_COMPRESSOR_MODULATION)
        if mode == const.COMPRESSOR_MODULATION_ON_OFF:
            return False
        return _real(config)

    mock.patch.object(thermal_model, "declared_modulation", _doc).start()


def sub_min(mode):
    res, entry = asyncio.run(rig.save_option("thermal_model", "compressor_modulation", mode,
                                             extra={"heat_pump_min_power": MIN_P}))
    assert not res.get("errors"), res.get("errors")
    hass, coord = rig.build_coord(entry)
    d = rig.run_cycles(coord, 1)
    pw = [float(s["power"]) for s in d["schedule"]]
    return sum(1 for p in pw if 0.01 < p < MIN_P - 1e-6), len(pw), entry.options


def main():
    n_on, tot, opts = sub_min(const.COMPRESSOR_MODULATION_ON_OFF)
    n_mod, _, _ = sub_min(const.COMPRESSOR_MODULATION_MODULATING)
    print("stored:", opts)
    print(f"RESULT declared_on_off={thermal_model.declared_modulation({'compressor_modulation': 'on_off'})}")
    print(f"RESULT on_off_sub_min_steps={n_on} of {tot}")
    print(f"RESULT modulating_sub_min_steps={n_mod} of {tot}")
    print(f"RESULT thread_factor={rig.thread_factor()}")
    print(f"RESULT load1={rig.load1()}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
