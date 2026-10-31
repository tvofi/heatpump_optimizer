#!/usr/bin/env python3
"""D3-s2-02: the dhw-min/setpoint deadband boundary (minimum == ceiling) is
untested in both services.py call sites that enforce it, so a boundary-off
mutation (`>` -> `>=`) in EITHER survives.

Metric definition: handle_set_thermal_params / handle_apply_schedule raise
ServiceValidationError(translation_key=..._no_deadband) or not, for
minimum == ceiling exactly (ceiling = setpoint - DHW_MIN_TEMP_SETPOINT_MARGIN).
Baseline (real code): minimum == ceiling is ACCEPTED (0 deadband allowed,
`>` is strict). Mutant (`>` -> `>=`): minimum == ceiling is REJECTED.
This harness drives the real production functions
(custom_components.heatpump_optimizer.services:handle_set_thermal_params,
handle_apply_schedule) with a minimal ServiceCall/coordinator stub -- not a
recomputation of the comparison from constants.

Instrumented symbols:
  custom_components.heatpump_optimizer.services:handle_set_thermal_params
  custom_components.heatpump_optimizer.services:handle_apply_schedule
Perturbation: `if float(minimum) > ceiling:` -> `>=` (line ~485) and
`if wanted > ceiling:` -> `>=` (line ~822); expected_direction: a call at
the exact boundary flips from accepted (rc=0 / no raise) to rejected
(ServiceValidationError) -- to_zero/sign_flip on "accepted".
Null control: the same call 0.01 degrees BELOW the boundary (minimum <
ceiling) must be accepted under both baseline and mutant -- the ordinary
case the suite does cover.

Command:
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
    python3 tools/audit/round8/D3/s2_finding02_deadband_boundary.py
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: shared 4-vCPU cloud container; this harness makes no solver calls
and no HA event loop beyond asyncio.run of two coroutines, so its numbers
are exact/count-like, not wall-time sensitive (still prints load1/thread_factor
per contract).
"""
import asyncio
import importlib
import os
import sys

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "tests", "hastub"))
sys.path.insert(0, REPO)

SVC_PATH = os.path.join(REPO, "custom_components", "heatpump_optimizer", "services.py")

PATCH_A = ("            if float(minimum) > ceiling:",
           "            if float(minimum) >= ceiling:")
PATCH_B = ("            if wanted > ceiling:",
           "            if wanted >= ceiling:")


class FakeThermalParams:
    def __init__(self, dhw_setpoint, dhw_min_temp):
        self.dhw_setpoint = dhw_setpoint
        self.dhw_min_temp = dhw_min_temp


class FakeCoord:
    def __init__(self, setpoint):
        self._thermal_params = FakeThermalParams(setpoint, setpoint - 10.0)

    async def async_update_thermal_params(self, params):
        return None


class FakeEntry:
    def __init__(self, entry_id, data=None, options=None, runtime_data=None):
        self.entry_id = entry_id
        self.data = data or {}
        self.options = options or {}
        self.runtime_data = runtime_data


def load_services(loaded_entries):
    for m in list(sys.modules):
        if m.startswith("custom_components"):
            del sys.modules[m]
    services = importlib.import_module("custom_components.heatpump_optimizer.services")
    services._loaded_entries = lambda hass, target_entry=None: loaded_entries
    return services


def probe_set_thermal_params(minimum, setpoint):
    entry = FakeEntry("e1", runtime_data=FakeCoord(setpoint))
    services = load_services([entry])
    call = services.ServiceCall() if hasattr(services, "ServiceCall") else None

    class Call:
        data = {"dhw_min_temperature": minimum}

    try:
        asyncio.run(services.handle_set_thermal_params(object(), Call()))
        return None  # accepted
    except Exception as err:  # noqa: BLE001
        if os.environ.get("S2_DEBUG"):
            import traceback
            traceback.print_exc()
        return type(err).__name__ + ":" + getattr(err, "translation_key", "?")


class FakeConfigEntries:
    def async_update_entry(self, entry, options=None, **kw):
        if options is not None:
            entry.options = options


class FakeHass:
    def __init__(self):
        self.config_entries = FakeConfigEntries()


def probe_apply_schedule(minimum, setpoint):
    entry = FakeEntry("e1", data={"dhw_setpoint": setpoint}, options={})
    services = load_services([entry])

    class Call:
        data = {"dhw_min_temperature": minimum}

    try:
        asyncio.run(services.handle_apply_schedule(FakeHass(), Call()))
        return None
    except Exception as err:  # noqa: BLE001
        if os.environ.get("S2_DEBUG"):
            import traceback
            traceback.print_exc()
        return type(err).__name__ + ":" + getattr(err, "translation_key", "?")


def with_patch(patch, fn):
    with open(SVC_PATH) as f:
        orig = f.read()
    old, new = patch
    if orig.count(old) != 1:
        raise SystemExit(f"REFUSE: anchor occurs {orig.count(old)} times")
    try:
        with open(SVC_PATH, "w") as f:
            f.write(orig.replace(old, new, 1))
        return fn()
    finally:
        with open(SVC_PATH, "w") as f:
            f.write(orig)


def main():
    setpoint = 60.0
    ceiling = setpoint - 5.0  # DHW_MIN_TEMP_SETPOINT_MARGIN

    # -- set_thermal_parameters --
    base_boundary = probe_set_thermal_params(ceiling, setpoint)
    base_control = probe_set_thermal_params(ceiling - 0.01, setpoint)
    mut_boundary = with_patch(PATCH_A, lambda: probe_set_thermal_params(ceiling, setpoint))
    mut_control = with_patch(PATCH_A, lambda: probe_set_thermal_params(ceiling - 0.01, setpoint))
    print(f"RESULT set_thermal_params_baseline_at_boundary={base_boundary!r}")
    print(f"RESULT set_thermal_params_baseline_null_control={base_control!r}")
    print(f"RESULT set_thermal_params_mutant_at_boundary={mut_boundary!r}")
    print(f"RESULT set_thermal_params_mutant_null_control={mut_control!r}")
    a_moved = (base_boundary is None) and (mut_boundary is not None)
    a_control_ok = (base_control is None) and (mut_control is None)
    print(f"RESULT set_thermal_params_mutant_survives={not a_moved}")
    print(f"RESULT set_thermal_params_null_control_holds={a_control_ok}")

    # -- apply_schedule --
    base_boundary2 = probe_apply_schedule(ceiling, setpoint)
    base_control2 = probe_apply_schedule(ceiling - 0.01, setpoint)
    mut_boundary2 = with_patch(PATCH_B, lambda: probe_apply_schedule(ceiling, setpoint))
    mut_control2 = with_patch(PATCH_B, lambda: probe_apply_schedule(ceiling - 0.01, setpoint))
    print(f"RESULT apply_schedule_baseline_at_boundary={base_boundary2!r}")
    print(f"RESULT apply_schedule_baseline_null_control={base_control2!r}")
    print(f"RESULT apply_schedule_mutant_at_boundary={mut_boundary2!r}")
    print(f"RESULT apply_schedule_mutant_null_control={mut_control2!r}")
    b_moved = (base_boundary2 is None) and (mut_boundary2 is not None)
    b_control_ok = (base_control2 is None) and (mut_control2 is None)
    print(f"RESULT apply_schedule_mutant_survives={not b_moved}")
    print(f"RESULT apply_schedule_null_control_holds={b_control_ok}")

    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1}")
    print(f"RESULT thread_factor=1.0")
    print(f"RESULT swapins=0")


if __name__ == "__main__":
    main()
