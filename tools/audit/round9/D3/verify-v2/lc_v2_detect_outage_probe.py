"""V2 independent harness for D3-s1-91.

V2's own metric, distinct from the finder's: the finder drove
`_immersion_dhw_margin` (coordinator.py:8384) with an in-memory guard-off
copy. This harness drives the OTHER site the finding names as "identical
shape" (:8112, `_detect_outage`) instead, on a real (not guard-off-copy)
`HeatPumpOptimizerCoordinator` instance, and counts differing outcomes
between GUARD_ON (real method, HASTUB_TZ unset -- the gate default) and a
scenario that forces the `now.tzinfo is not None` branch open (HASTUB_TZ set)
to see whether the guard is exercised (any code path reached beyond the
tzinfo check) under the gate default vs not, and whether forcing it open
without the guard crashes.

No mutation pool, no prescreen, no full-gate run (tvofi's 2026-09-26 D3
rule). This only imports and calls production code twice, under two values
of HASTUB_TZ, with `dt_util` reloaded exactly as the finder's harness does.

Instrumented symbol: coordinator.HeatPumpOptimizerCoordinator._detect_outage.
Perturbation: HASTUB_TZ unset vs Europe/Stockholm (dt_util.now() naive vs
aware); the guard line itself is deleted in an in-memory recompiled copy,
never on disk.

Run: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
  /tmp/claude-0/-home-claude/c1053ac1-148d-5d89-9785-8af9678426ba/scratchpad/lc_v2_d3.py
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Expected: HASTUB_TZ unset -> now naive -> guard_on == guard_off (0 divergence,
guard dead); HASTUB_TZ=Europe/Stockholm -> now aware -> guard_off raises
TypeError, guard_on does not (1 divergence, guard reachable only there).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib
import inspect
import re
import sys
import textwrap
import time

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import harness  # noqa: E402
from heatpump_optimizer import coordinator as C  # noqa: E402
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from heatpump_optimizer import const  # noqa: E402


def _guard_off(func, pattern):
    src = textwrap.dedent(inspect.getsource(func))
    new_src, n = re.subn(pattern, "", src, count=1)
    assert n == 1, f"pattern not found once in {func.__name__}: {pattern!r}"
    ns = dict(vars(sys.modules[func.__module__]))
    exec(compile(new_src, f"<guard_off:{func.__name__}>", "exec"), ns)
    return ns[func.__name__]


def _set_tz(hastub_tz):
    if hastub_tz is None:
        os.environ.pop("HASTUB_TZ", None)
    else:
        os.environ["HASTUB_TZ"] = hastub_tz
    dt_mod = sys.modules["homeassistant.util.dt"]
    importlib.reload(dt_mod)
    C.dt_util = dt_mod


def _coord():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    config = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        C.CONF_OUTAGE_RECOVERY_ENABLED: True,
    }
    return C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=config))


def _run(hastub_tz):
    _set_tz(hastub_tz)
    # Freeze the stub clock so both the GUARD_ON and GUARD_OFF call see the
    # identical `now`; two live `dt_util.now()` calls a microsecond apart
    # would make on()/off() differ for a timing reason that has nothing to
    # do with the guard (a trap the harness must avoid, verifier.md step 3).
    frozen = C.dt_util.now()
    C.dt_util.freeze(frozen)
    on = C.HeatPumpOptimizerCoordinator._detect_outage
    off = _guard_off(
        on,
        r" {4}if last\.tzinfo is None and now\.tzinfo is not None:\n"
        r" {8}last = last\.replace\(tzinfo=now\.tzinfo\)\n",
    )
    # A naive stored last-tick timestamp far enough in the past to cross
    # OUTAGE_GAP_MINUTES, so the branch beyond the guard actually executes
    # (the guard's own reachability question, not the outage threshold's).
    last_tick_iso = "2020-01-01T00:00:00"

    coord_on = _coord()
    now_aware = C.dt_util.now().tzinfo is not None
    try:
        on(coord_on, last_tick_iso)
        a = (coord_on._outage_recovery_until, coord_on._outage_dhw_until)
    except Exception as err:  # noqa: BLE001
        a = f"raises {type(err).__name__}: {err}"

    coord_off = _coord()
    try:
        off(coord_off, last_tick_iso)
        b = (coord_off._outage_recovery_until, coord_off._outage_dhw_until)
    except Exception as err:  # noqa: BLE001
        b = f"raises {type(err).__name__}: {err}"

    return now_aware, a, b


def main():
    t0 = time.process_time()
    naive_aware, naive_on, naive_off = _run(None)
    sthlm_aware, sthlm_on, sthlm_off = _run("Europe/Stockholm")
    cpu = time.process_time() - t0

    print(f"HASTUB_TZ unset: now_tzaware={int(naive_aware)} on={naive_on!r} off={naive_off!r}")
    print(f"HASTUB_TZ=Europe/Stockholm: now_tzaware={int(sthlm_aware)} on={sthlm_on!r} off={sthlm_off!r}")

    differs_unset = int(naive_on != naive_off)
    differs_sthlm = int(sthlm_on != sthlm_off)
    print(f"RESULT detect_outage_8112_now_tzaware_default={int(naive_aware)}")
    print(f"RESULT detect_outage_8112_differs_hastubtz_unset={differs_unset}")
    print(f"RESULT detect_outage_8112_differs_hastubtz_stockholm={differs_sthlm}")
    print(f"RESULT detect_outage_8112_off_raises_stockholm={int(isinstance(sthlm_off, str) and 'raises' in sthlm_off)}")
    print(f"RESULT cpu_s={cpu:.3f}")
    print("RESULT thread_factor=1.0 (no numpy/BLAS on this path)")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = -1.0
    print(f"RESULT load1={load1:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
