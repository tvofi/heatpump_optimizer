#!/usr/bin/env python3
"""Round-1 B5 harness: the five D10 findings, measured on the tree it runs in.

    #180 action-setup             services registered by async_setup, once
    #181 runtime-data             the coordinator on entry.runtime_data
    #182 unique-config-entry      a true duplicate aborts, a second pump passes
    #183 docs-removal-instructions a Removal section under Installation
    #184 parallel-updates         PARALLEL_UPDATES on every platform

Run from the repository root of the tree to measure (the baseline in a
worktree of the merge base, the fix on the branch):

    PYTHONPATH=tests/hastub python tools/audit/round1/B5/harness.py

It never cds, writes nothing, and needs no network. Every check is guarded
so the same file measures a tree that predates the fix (no async_setup, no
runtime_data, no AbortFlow in the stub) and reports the pre-fix number
rather than crashing.

RESULT lines, with the expected value on each side (tolerance 0 -- these
are counts, not timings):

    services_after_async_setup        services in the registry after the
                                      domain's async_setup with no entry.
                                      before 0 (no async_setup), after 11
    service_registrations_two_entries async_register calls over async_setup
                                      plus two entries' setup.
                                      before 22 (11 per entry), after 11
    services_after_last_unload        services left once both entries are
                                      unloaded. before 0, after 11
    hass_data_domain_reads            static count of hass.data[DOMAIN],
                                      hass.data.get(DOMAIN ...) and
                                      hass.data.setdefault(DOMAIN ...) in
                                      custom_components/heatpump_optimizer.
                                      before 24, after 0
    platforms_from_runtime_data       platforms whose async_setup_entry finds
                                      its coordinator on entry.runtime_data
                                      with hass.data empty. before 0, after 5
    duplicate_flow_aborted            1 if the initial flow, run twice with
                                      the same first screen, aborts the
                                      second time as already_configured.
                                      before 0, after 1
    distinct_flow_proceeds            1 if the same account with a different
                                      heat-pump switch proceeds to the
                                      temperature step. before 1, after 1
                                      (the null control: multi-entry stays)
    parallel_updates_declared         platform modules declaring
                                      PARALLEL_UPDATES. before 0, after 5
    removal_section_present           1 if README.md has "### Removal"
                                      between "## Installation" and
                                      "## Quick start". before 0, after 1
    thread_factor / load1 / swapins   machine state at the end, per the
                                      harness contract (no timing RESULT
                                      here, so the 1.05 / 1.5 gates do not
                                      apply; printed for completeness)

Baseline: origin/main at the branch's merge base (c398fc8 when first
measured; the PR body names the exact SHAs). Machine: the 8-core M1 audit
box; the numbers are counts and reproduce anywhere.

Instrumented symbols: hass.services.async_register (counted through a
FakeServices subclass), heatpump_optimizer.async_setup / async_setup_entry /
async_unload_entry, each platform's async_setup_entry,
HeatPumpOptimizerConfigFlow.async_step_user (with validate_tibber_token
swapped for a stub verdict, the same idiom tests/entities.py uses).

Perturbations, one production line each, and the RESULT that moves:
    delete `_async_register_services(hass)` from async_setup
        -> services_after_async_setup 11 -> 0, services_after_last_unload
           11 -> 0, service_registrations_two_entries 11 -> 0
    delete `entry.runtime_data = coordinator` in async_setup_entry
        -> platforms_from_runtime_data is unaffected (it sets runtime_data
           itself) but the three service metrics report -1: setup no longer
           completes, which is the honest reading
    delete `self._abort_if_unique_id_configured()` in async_step_user
        -> duplicate_flow_aborted 1 -> 0, distinct_flow_proceeds stays 1
    delete one platform's `PARALLEL_UPDATES = ...`
        -> parallel_updates_declared 5 -> 4
    delete the README's "### Removal" section
        -> removal_section_present 1 -> 0
"""
from __future__ import annotations

import os

# The thread pin, before anything that could import numpy (the coordinator
# does). Copied from tests/stress.py; without it a threaded BLAS inflates
# process CPU time by the thread factor.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_var, "1")

import asyncio  # noqa: E402
import glob  # noqa: E402
import re  # noqa: E402
import resource  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass, FakeServices  # noqa: E402

import heatpump_optimizer as integ  # noqa: E402
from heatpump_optimizer import binary_sensor, button, climate, config_flow, const, sensor, switch  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

PLATFORMS = (sensor, binary_sensor, button, climate, switch)
DATA = {const.CONF_TIBBER_TOKEN: "x", const.CONF_WEATHER_ENTITY: "weather.home"}
DOMAIN = const.DOMAIN


def result(name: str, value, unit: str = "count") -> None:
    print(f"RESULT {name}={value} {unit}")


def _state(name: str):
    """A ConfigEntryState member, or None on a stub that predates it."""
    try:
        from homeassistant.config_entries import ConfigEntryState
    except ImportError:
        return None
    return getattr(ConfigEntryState, name, None)


class CountingServices(FakeServices):
    """The honest registry, plus a count of registration calls."""

    def __init__(self) -> None:
        super().__init__()
        self.registrations = 0

    def async_register(self, *args, **kwargs):
        self.registrations += 1
        return super().async_register(*args, **kwargs)


def _entry(entry_id: str) -> FakeEntry:
    entry = FakeEntry(data=dict(DATA))
    entry.entry_id = entry_id  # the pre-fix FakeEntry has no keyword for it
    return entry


def _registry(hass) -> dict:
    return dict(hass.services.async_services().get(DOMAIN, {}))


async def _setup_domain(hass) -> bool:
    """What async_setup_component does: the domain's async_setup, if any."""
    setup = getattr(integ, "async_setup", None)
    if setup is None:
        return False
    return bool(await setup(hass, {}))


async def _setup_entry(hass, entry) -> bool:
    """What ConfigEntry.async_setup does, on either tree."""
    if entry not in hass.config_entries.entries:
        hass.config_entries.entries.append(entry)
    ok = await integ.async_setup_entry(hass, entry)
    if ok and _state("LOADED") is not None:
        entry.state = _state("LOADED")
    return ok


async def _unload_entry(hass, entry) -> bool:
    """What ConfigEntry.async_unload does (2024.6+): runtime_data goes too."""
    ok = await integ.async_unload_entry(hass, entry)
    if ok:
        if hasattr(entry, "runtime_data"):
            delattr(entry, "runtime_data")
        if _state("NOT_LOADED") is not None:
            entry.state = _state("NOT_LOADED")
    return ok


# ---------------------------------------------------------------- #180 ----
async def measure_services() -> tuple[int, int, int]:
    hass = FakeHass()
    hass.services = CountingServices()
    await _setup_domain(hass)
    after_setup = len(_registry(hass))
    first, second = _entry("b5_first"), _entry("b5_second")
    try:
        await _setup_entry(hass, first)
        await _setup_entry(hass, second)
        registrations = hass.services.registrations
        await _unload_entry(hass, first)
        await _unload_entry(hass, second)
        after_unload = len(_registry(hass))
    except Exception as err:  # noqa: BLE001 - a perturbed tree may not set up
        print(f"note: entry lifecycle failed: {type(err).__name__}: {err}")
        return after_setup, -1, -1
    return after_setup, registrations, after_unload


# ---------------------------------------------------------------- #181 ----
def count_hass_data_domain_reads() -> int:
    pattern = re.compile(r"hass\.data(?:\[DOMAIN\]|\.get\(DOMAIN\b|\.setdefault\(DOMAIN\b)")
    total = 0
    for path in sorted(glob.glob("custom_components/heatpump_optimizer/*.py")):
        with open(path, encoding="utf-8") as handle:
            total += len(pattern.findall(handle.read()))
    return total


async def measure_platforms() -> int:
    found = 0
    for module in PLATFORMS:
        hass = FakeHass()
        entry = _entry("b5_platform")
        entry.runtime_data = HeatPumpOptimizerCoordinator(hass, entry)
        added: list = []
        try:
            await module.async_setup_entry(hass, entry, added.extend)
        except Exception:  # noqa: BLE001 - the pre-fix platform reads hass.data
            continue
        if added:
            found += 1
    return found


# ---------------------------------------------------------------- #182 ----
async def _accept_any_token(hass, token) -> str:
    return "ok"


def _run_user_step(flow, answers) -> dict:
    try:
        return asyncio.run(flow.async_step_user(dict(answers)))
    except Exception as err:  # noqa: BLE001 - AbortFlow on the fixed tree
        reason = getattr(err, "reason", None)
        if reason is None:
            raise
        return {"type": "abort", "reason": reason}


def measure_flow() -> tuple[int, int]:
    first_screen = {
        "name": "Heat Pump Optimizer",
        const.CONF_TIBBER_TOKEN: "tok-a",
        const.CONF_WEATHER_ENTITY: "weather.home",
        const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_a",
    }
    real = config_flow.validate_tibber_token
    config_flow.validate_tibber_token = _accept_any_token
    try:
        hass = FakeHass()

        def flow():
            handler = config_flow.HeatPumpOptimizerConfigFlow()
            handler.hass = hass
            return handler

        first = flow()
        first_result = _run_user_step(first, first_screen)
        # What the flow manager does when the first flow finishes: an entry
        # holding the flow's unique id (None on the pre-fix tree).
        existing = FakeEntry(data=dict(first_screen))
        existing.entry_id = "b5_existing"
        existing.unique_id = getattr(first, "unique_id", None)
        hass.config_entries.entries.append(existing)

        second_result = _run_user_step(flow(), first_screen)
        duplicate_aborted = int(
            first_result.get("type") == "form"
            and second_result.get("type") == "abort"
            and second_result.get("reason") == "already_configured"
        )
        other_result = _run_user_step(
            flow(), {**first_screen, const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.pump_b"}
        )
        distinct_proceeds = int(
            other_result.get("type") == "form"
            and other_result.get("step_id") == "temperature"
        )
    finally:
        config_flow.validate_tibber_token = real
    return duplicate_aborted, distinct_proceeds


# ---------------------------------------------------------------- #184 ----
def count_parallel_updates() -> int:
    return sum(1 for module in PLATFORMS if hasattr(module, "PARALLEL_UPDATES"))


# ---------------------------------------------------------------- #183 ----
def removal_section_present() -> int:
    with open("README.md", encoding="utf-8") as handle:
        readme = handle.read()
    try:
        install = readme.index("## Installation")
        quick = readme.index("## Quick start")
    except ValueError:
        return 0
    return int(re.search(r"^### Removal$", readme[install:quick], re.M) is not None)


def main() -> None:
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    print(f"HEAD {head or '?'}")
    process_start, thread_start = time.process_time(), time.thread_time()

    after_setup, registrations, after_unload = asyncio.run(measure_services())
    result("services_after_async_setup", after_setup)
    result("service_registrations_two_entries", registrations)
    result("services_after_last_unload", after_unload)
    result("hass_data_domain_reads", count_hass_data_domain_reads())
    result("platforms_from_runtime_data", asyncio.run(measure_platforms()))
    duplicate_aborted, distinct_proceeds = measure_flow()
    result("duplicate_flow_aborted", duplicate_aborted, "bool")
    result("distinct_flow_proceeds", distinct_proceeds, "bool")
    result("parallel_updates_declared", count_parallel_updates())
    result("removal_section_present", removal_section_present(), "bool")

    process_cpu = time.process_time() - process_start
    thread_cpu = time.thread_time() - thread_start
    result("thread_factor", f"{process_cpu / thread_cpu:.3f}" if thread_cpu else "nan", "ratio")
    result("load1", f"{os.getloadavg()[0]:.2f}", "load")
    result("swapins", resource.getrusage(resource.RUSAGE_SELF).ru_nswap, "count")


if __name__ == "__main__":
    main()
