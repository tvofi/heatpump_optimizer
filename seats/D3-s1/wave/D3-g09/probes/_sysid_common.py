"""_run_system_identification arms shared by probe_425a9196b86265d0.py and probe_84797ff91697f6a7.py."""
import asyncio
import copy
import numpy as np
from unittest import mock
import _probe_lib as L

C = L.HeatPumpOptimizerCoordinator
M = L.coord_mod
PRICES = np.array([1.0, 0.8, 0.6, 0.9, 1.2, 1.4, 1.1, 0.7] * 12)


def run(c, fn=None, override=None):
    """One _run_system_identification(PRICES). The off-loop seam (coordinator._await_off_loop) is
    counted and run inline; `override` replaces the experiment's step answer when not None.
    Returns (off-loop dispatches, the adopted plan action, the experiment's vars after)."""
    dispatched = []

    async def inline(hass, fn_, *args):
        dispatched.append(fn_.__qualname__)
        state, ov = fn_(*args)
        return state, (override if override is not None else ov)

    async def go():
        with mock.patch.object(M, "_await_off_loop", inline):
            if fn is None:
                await c._run_system_identification(PRICES)
            else:
                with mock.patch.object(C, "_run_system_identification", fn):
                    await c._run_system_identification(PRICES)
    try:
        asyncio.run(go())
    except Exception as exc:
        return len(dispatched), f"raised {type(exc).__name__}: {exc}", None
    snap = {k: v for k, v in vars(c._sysid).items() if isinstance(v, (str, int, float, bool, type(None)))}
    return len(dispatched), dict(c._current_action), snap


def fresh(**cfg):
    c = L.coord(**cfg)
    c._current_action = {"power": 1.5, "dhw_power": 0.0, "mode": "auto"}
    return c


def scrub(action):
    """The action with values rounded, for a byte-for-byte arm comparison."""
    if not isinstance(action, dict):
        return action
    return {k: (round(v, 9) if isinstance(v, float) else v) for k, v in sorted(action.items())}


def force_phase(c, phase):
    c._sysid.phase = getattr(M.sysid, phase)
    return c


def deep(c):
    return copy.deepcopy(c)
