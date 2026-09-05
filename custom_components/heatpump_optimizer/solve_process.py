"""Run CPU-heavy solves in a child process (#290 #199).

The default Home Assistant executor is a thread pool. A solve holds the GIL
for hundreds of milliseconds at a time, starving the event loop and every
other integration's executor work on the same interpreter. These workers run
in a dedicated ``ProcessPoolExecutor`` so the solve's GIL is not shared.
"""
from __future__ import annotations

import asyncio
import inspect
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime
from typing import Any, Callable, TypeVar

import numpy as np

from . import diagnosis
from .optimizer import HeatPumpOptimizer, OptimizationResult
from .thermal_model import ThermalModel, ThermalParameters, ThermalState

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T")

_pool: ProcessPoolExecutor | None = None


def _pool_executor() -> ProcessPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ProcessPoolExecutor(max_workers=1)
    return _pool


def shutdown_solve_pool() -> None:
    """Release the shared pool on coordinator shutdown."""
    global _pool
    if _pool is not None:
        _pool.shutdown(wait=False, cancel_futures=True)
        _pool = None


def _use_process_pool() -> bool:
    """Production default; tests/hastub runs inline unless forced on."""
    flag = os.environ.get("HPO_SOLVE_PROCESS")
    if flag == "0":
        return False
    if flag == "1":
        return True
    return not any("tests/hastub" in entry for entry in sys.path)


def _call_bound(
    func: Callable[..., T], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> T:
    """Invoke ``func`` after binding defaults (picklable process-pool shim)."""
    bound = inspect.signature(func).bind(*args, **kwargs)
    bound.apply_defaults()
    return func(*bound.args, **bound.kwargs)


async def async_run_solve_job(
    hass: Any, func: Callable[..., T], /, *args: Any, **kwargs: Any
) -> T:
    """Dispatch a picklable worker: process pool in production, hass in tests."""
    if not _use_process_pool():
        if kwargs:
            return await hass.async_add_executor_job(lambda: func(*args, **kwargs))
        return await hass.async_add_executor_job(func, *args)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _pool_executor(), _call_bound, func, args, kwargs
    )


def worker_pid() -> int:
    """Null worker for gate tests: proves dispatch left the parent process."""
    return os.getpid()


def run_optimize_worker(
    optimizer: HeatPumpOptimizer,
    state: ThermalState,
    prices: np.ndarray,
    outdoor_temps: np.ndarray,
    wind_speeds: np.ndarray,
    precipitation: np.ndarray,
    solar_radiation: np.ndarray,
    solve_now: datetime,
    price_known: np.ndarray,
    pv_surplus: np.ndarray,
    price_sigma: np.ndarray,
    space_pins: np.ndarray | None = None,
    dhw_pins: np.ndarray | None = None,
    external_heat: np.ndarray | None = None,
    caps_extra: np.ndarray | None = None,
    humidity: np.ndarray | None = None,
    min_temp_margins: np.ndarray | None = None,
    min_temp_floors: np.ndarray | None = None,
    space_blocked: bool = False,
    dhw_blocked: bool = False,
) -> OptimizationResult:
    """Top-level worker for scheduled and what-if MPC solves."""
    return optimizer.optimize(
        state,
        prices,
        outdoor_temps,
        wind_speeds,
        precipitation,
        solar_radiation,
        solve_now,
        price_known,
        pv_surplus,
        space_pins,
        dhw_pins,
        external_heat,
        price_sigma,
        caps_extra,
        humidity,
        min_temp_margins=min_temp_margins,
        min_temp_floors=min_temp_floors,
        space_blocked=space_blocked,
        dhw_blocked=dhw_blocked,
    )


def run_interval_diagnosis(
    thermal_params: ThermalParameters,
    record: dict[str, Any],
) -> dict[str, Any] | None:
    """Top-level worker for interval residual attribution (#52)."""
    try:
        scratch_model = ThermalModel(replace(thermal_params))
        report = diagnosis.attribute(
            scratch_model,
            record["state"],
            dict(record["planned"], dt_hours=record["dt_hours"]),
            record["realised"],
            record["actual"],
        )
    except Exception as err:  # noqa: BLE001 - never break ops for insight
        _LOGGER.debug("Interval diagnosis failed: %s", err)
        return None
    if report is not None:
        report["interval_end"] = record["when"]
    return report
