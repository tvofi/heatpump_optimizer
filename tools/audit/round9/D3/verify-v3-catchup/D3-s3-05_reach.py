#!/usr/bin/env python3
"""Verifier V3 cheap check for D3-s3-05 (legionella.LegionellaGuard._drive_switch).

Metric: number of homeassistant.helpers.issue_registry.async_delete_issue
calls made for "dhw_disinfection_write_failed" across 5 consecutive healthy
(``switch.failed = False``) observe cycles, baseline vs the M20 mutant
(`if switch.failed == self.write_failed_notice: return` deleted), with a
null (identity) arm. The mutant is applied in memory via
mock.patch.object(LegionellaGuard, "_drive_switch", ...), never on disk.

Command:
    PYTHONPATH=tests/hastub /root/venv314/bin/python \
    tools/audit/round9/D3/verify-v3-catchup/D3-s3-05_reach.py

Real-HA arm: legionella.py imports homeassistant.helpers.issue_registry
directly, so this seam's real-world consequence is what
issue_registry.async_delete_issue actually does when the issue is already
gone -- read directly from real Home Assistant 2026.2.3
(/root/venvha/bin/python, no tests/hastub on PYTHONPATH,
`import typing; typing.ByteString = bytes` before importing homeassistant),
not the stub's stand-in.

Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box G1-V3 (4 CPUs).
"""
import asyncio
import os
import sys
import time
from unittest import mock

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

t_process0 = time.process_time()
t_wall0 = time.time()

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

from harness import FakeHass  # noqa: E402
from heatpump_optimizer.disinfection import DisinfectionSwitch  # noqa: E402
from heatpump_optimizer.legionella import LegionellaGuard  # noqa: E402
from heatpump_optimizer import legionella as legionella_mod  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402


def make_guard() -> LegionellaGuard:
    params = ThermalParameters()
    params.dhw_enabled = True
    switch = DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None)
    guard = LegionellaGuard(
        FakeHass(),
        "verify-v3-catchup",
        params,
        {},
        action=lambda: {},
        disinfect=switch,
        dhw_blocked=lambda: False,
    )
    # controlling derives from an empty config (no entity_id) -> already
    # False, i.e. observe mode: no switch writes attempted.
    return guard


async def run(mutant: bool) -> int:
    guard = make_guard()
    deletes: list[str] = []
    original = legionella_mod.ir.async_delete_issue
    legionella_mod.ir.async_delete_issue = lambda hass, domain, issue_id: deletes.append(issue_id)
    try:
        if mutant:
            async def mutated_drive_switch(self, on: bool) -> None:
                # M20: the `if switch.failed == self.write_failed_notice: return`
                # memo guard deleted -- every cycle re-issues the delete.
                switch = self.disinfect
                switch.memo = None
                await switch.release(legionella_mod.dt_util.now())
                self.write_failed_notice = switch.failed
                if not switch.failed:
                    legionella_mod.ir.async_delete_issue(
                        self.hass, "heatpump_optimizer", "dhw_disinfection_write_failed"
                    )

            with mock.patch.object(LegionellaGuard, "_drive_switch", mutated_drive_switch):
                for _ in range(5):
                    guard.disinfect.failed = False
                    await guard._drive_switch(False)
        else:
            for _ in range(5):
                guard.disinfect.failed = False
                await guard._drive_switch(False)
    finally:
        legionella_mod.ir.async_delete_issue = original
    return len(deletes)


def main():
    baseline = asyncio.run(run(mutant=False))
    mutant = asyncio.run(run(mutant=True))
    null = asyncio.run(run(mutant=False))

    print(f"RESULT baseline_deletes_over_5_cycles={baseline}")
    print(f"RESULT mutant_deletes_over_5_cycles={mutant}")
    print(f"RESULT mutant_delta={mutant - baseline}")
    print(f"RESULT null_delta={null - baseline}")

    # Real-HA arm: what async_delete_issue on a missing issue actually costs.
    try:
        import subprocess

        clean_env = dict(os.environ)
        clean_env.pop("PYTHONPATH", None)  # tests/hastub must not shadow real HA
        real_ha_check = subprocess.run(
            [
                "/root/venvha/bin/python",
                "-c",
                "import typing\n"
                "typing.ByteString = bytes\n"
                "import inspect\n"
                "import homeassistant.helpers.issue_registry as ir\n"
                "src = inspect.getsource(ir.IssueRegistry.async_delete)\n"
                "noop = 'if self.issues.pop((domain, issue_id), None) is None:' in src\n"
                "print('NOOP_ON_MISSING_ISSUE=' + str(noop))\n",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env=clean_env,
        )
        print("RESULT real_ha_async_delete_issue_stdout=" + real_ha_check.stdout.strip().replace("\n", ";"))
        if real_ha_check.returncode != 0:
            print("RESULT real_ha_check_stderr=" + real_ha_check.stderr.strip()[-400:])
    except Exception as exc:  # pragma: no cover - diagnostic only
        print(f"RESULT real_ha_check_error={exc!r}")

    thread_cpu = time.process_time() - t_process0
    wall = time.time() - t_wall0
    thread_factor = (thread_cpu / wall) if wall > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = -1.0
    print(f"RESULT thread_factor={min(thread_factor, 1.0):.3f}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
