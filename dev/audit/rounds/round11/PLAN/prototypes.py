#!/usr/bin/env python3
"""Round 11 plan (P3): the architecture-score reading of each planned move's prototype edit.

Metric (one line): score.py:report(vector(fork tree), vector(fork tree + arm)), every counter on
(ARCHSCORE_ABLATE is refused). KEY: the vector vector.py:measure returns for the edited copy.

Each arm is an exact-text edit of a temporary copy of the package at the fork; the tree under test is
never written. An arm proves what the score reads for the move's shape, nothing about behaviour: the
fixer's failing test, mutation proof and the finder's harness are still owed (fixer.md).

  hub     coordinator._apply_comfort_weight publishes a replaced context instead of writing the shared
          OptimizationConfig in place (D7-s2-03's perturbation as a text edit)            ADR-003
  sysid   sysid.arm_from_config hands the switch to arm() instead of storing it on the collaborator's
          config each cycle                                                                ADR-003
  circ    the circulation pumps' write and its record move to one owner object; the coordinator's
          dict and its in-place store go (D16-s3-02's owner)                               ADR-004
  reach   boost reads the mode it was already told; diagnostics reads it from the #1739 view ADR-005
  tasks   async_shutdown stops clearing the task set its done-callbacks already empty      ADR-005
  clock   InputReader takes UTC from the standard library, not a function-scope Home Assistant import
                                                                                           ADR-002
  topk    tariff._smooth_topk_sum is one row of _smooth_topk_sum_batch                     ADR-006

The kernel's nine clone arms and its seven layer edges are D7-s1's own prototypes
(dev/audit/rounds/round11/D7/s1/m7_prototypes.py); this file does not repeat them.

Run (from the repository root; about 30 s per arm):
    python3 dev/audit/rounds/round11/PLAN/prototypes.py                    every arm alone, then combined
    python3 dev/audit/rounds/round11/PLAN/prototypes.py --only hub,circ    those arms alone
    python3 dev/audit/rounds/round11/PLAN/prototypes.py --only hub,circ --combined

Read at the fork 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 on 2026-11-18 (darwin arm64):
    hub    dS +5.4429 IMPROVES  hub_solve_writes 1 -> 0
    sysid  dS +2.2590 IMPROVES  shared_inplace_writes 3 -> 2
    circ   dS +2.2625 IMPROVES  shared_inplace_writes 3 -> 2, coord_footprint 2496 -> 2490
    reach  dS +1.5850 IMPROVES  coordinator_private_reach 2 -> 0
    tasks  dS +2.2590 IMPROVES  shared_inplace_writes 3 -> 2
    clock  dS +0.3479 IMPROVES  layer_violations 13 -> 10
    topk   dS +0.6964 IMPROVES  duplication_copies 18 -> 17
    all seven combined  dS +18.9616 IMPROVES, admissible (shared_inplace_writes 3 -> 0)
Writes only under a tempfile root.
"""
from __future__ import annotations

import os
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
FORK = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
PKG = "custom_components/heatpump_optimizer"
sys.path.insert(0, str(REPO / "tools" / "audit"))

from archscore import score, vector  # noqa: E402


def sub(root: Path, rel: str, old: str, new: str) -> None:
    """Replace ``old`` by ``new`` in ``rel``; the anchor must occur exactly once."""
    path = root / PKG / rel
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{rel}: anchor occurs {text.count(old)} times, not once: {old[:60]!r}")
    path.write_text(text.replace(old, new))


def cut(root: Path, rel: str, start: str, end: str, new: str, keep_end: bool) -> None:
    """Replace the text from ``start`` to ``end`` (``end`` kept when ``keep_end``) by ``new``."""
    path = root / PKG / rel
    text = path.read_text()
    a = text.index(start)
    b = text.index(end, a)
    path.write_text(text[:a] + new + text[b if keep_end else b + len(end):])


def hub(r: Path) -> None:
    sub(r, "coordinator.py",
        '        getattr(self, "_ctx", self)._opt_config.comfort_weight = self._comfort_weight()\n',
        "        ctx = self._ctx\n"
        "        self._ctx = replace(\n"
        "            ctx, _opt_config=replace(ctx._opt_config, comfort_weight=self._comfort_weight())\n"
        "        )\n")


def sysid(r: Path) -> None:
    sub(r, "sysid.py", "    ident.config.enabled = config.system_identification_enabled\n", "")
    sub(r, "sysid.py", "    armed = ident.arm(now, plant=plant, learner_samples=learner_samples, probe=probe)\n",
        "    armed = ident.arm(now, plant=plant, learner_samples=learner_samples, probe=probe,\n"
        "                      enabled=config.system_identification_enabled)\n")
    sub(r, "sysid.py",
        '        learner_samples: int = 0, probe: DrawRange | None = None,\n    ) -> bool:\n'
        '        """Arm an experiment',
        '        learner_samples: int = 0, probe: DrawRange | None = None, enabled: bool | None = None,\n'
        '    ) -> bool:\n        """Arm an experiment')
    sub(r, "sysid.py", "        if not self.config.enabled:\n",
        "        if not (self.config.enabled if enabled is None else enabled):\n")


def circ(r: Path) -> None:
    (r / PKG / "circulation.py").write_text(
        '"""The circulation pumps\' one owner: the write and the record of the write."""\n'
        "from __future__ import annotations\n\nimport logging\nfrom typing import Any\n\n"
        "_LOGGER = logging.getLogger(__name__)\n\n\n"
        "class CirculationPumps:\n"
        "    def __init__(self) -> None:\n"
        "        self.commanded: dict[str, bool] = {}\n\n"
        "    async def async_set(self, hass: Any, entity_id: str, on: bool, reason: str, *, off: bool) -> None:\n"
        "        previous = self.commanded.get(entity_id)\n"
        "        if off or (previous is not None and previous is on):\n"
        "            return\n"
        '        service = "turn_on" if on else "turn_off"\n'
        "        try:\n"
        '            await hass.services.async_call("homeassistant", service, {"entity_id": entity_id})\n'
        '            _LOGGER.info("Pump %s -> %s: %s", entity_id, service, reason)\n'
        "        except Exception as err:  # noqa: BLE001\n"
        '            _LOGGER.warning("Could not command pump %s: %s", entity_id, err)\n'
        "            return\n"
        "        self.commanded[entity_id] = on\n")
    cut(r, "coordinator.py", "        previous = self._pump_commanded.get(entity_id)\n",
        "        self._pump_commanded[entity_id] = on\n",
        "        await self._circulation.async_set(\n"
        "            self.hass, entity_id, on, reason, off=self._mode in (MODE_OFF,)\n"
        "        )\n", keep_end=False)
    sub(r, "coordinator.py", "        self._pump_commanded: dict[str, bool] = {}\n",
        "        self._circulation = CirculationPumps()\n")
    sub(r, "coordinator.py", "from . import boost\n", "from . import boost\nfrom .circulation import CirculationPumps\n")
    if "_pump_commanded" in (r / PKG / "coordinator.py").read_text():
        raise SystemExit("circ: a reader of the old dict is left")


def reach(r: Path) -> None:
    sub(r, "boost.py", '    return getattr(coord, "mode", None) == MODE_BOOST\n',
        "    return held_for(coord).mode_since is not None\n")
    sub(r, "diagnostics.py", '        "mode": getattr(coord, "mode", None),\n',
        '        "mode": state.mode if state else None,\n')
    sub(r, "coordinator.py", "    solve_failures: int | None = None\n    cop_scale: float | None = None\n",
        "    solve_failures: int | None = None\n    mode: str | None = None\n    cop_scale: float | None = None\n")
    sub(r, "coordinator.py", '            solve_failures=getattr(coord, "_solve_failures", None),\n',
        '            solve_failures=getattr(coord, "_solve_failures", None),\n'
        '            mode=getattr(coord, "_mode", None),\n')


def tasks(r: Path) -> None:
    sub(r, "coordinator.py", "        self._background_tasks.clear()\n", "")


def clock(r: Path) -> None:
    sub(r, "inputs.py",
        "        from homeassistant.util import dt as dt_util\n\n        utc_now: datetime = dt_util.utcnow()\n"
        "        return utc_now\n",
        "        return datetime.now(timezone.utc)\n")
    sub(r, "inputs.py", "from datetime import datetime, timedelta\n", "from datetime import datetime, timedelta, timezone\n")


def topk(r: Path) -> None:
    cut(r, "tariff.py",
        "    x = np.asarray(values, dtype=float)\n    if x.size == 0 or k <= 0:\n        return 0.0\n",
        "def _smooth_topk_sum_batch(",
        "    x = np.asarray(values, dtype=float)\n"
        "    return float(_smooth_topk_sum_batch(x[None, :], k, tau)[0])\n\n\n", keep_end=True)


ARMS = {"hub": hub, "sysid": sysid, "circ": circ, "reach": reach, "tasks": tasks, "clock": clock, "topk": topk}


def main(argv: list[str]) -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        raise SystemExit("ARCHSCORE_ABLATE is set: a gain that appears only without the counters did not happen")
    names = list(ARMS)
    if "--only" in argv:
        names = argv[argv.index("--only") + 1].split(",")
    runs = [names] if "--combined" in argv else [[n] for n in names] + ([names] if "--only" not in argv else [])
    with tempfile.TemporaryDirectory(prefix="r11-plan-") as tmp:
        fork = score.tree_of(FORK, Path(tmp) / "fork")
        base = vector.measure(fork)
        for i, run in enumerate(runs):
            tree = Path(tmp) / f"arm{i}"
            shutil.copytree(fork / "custom_components", tree / "custom_components")
            for name in run:
                ARMS[name](tree)
            for path in (tree / PKG).glob("*.py"):
                py_compile.compile(str(path), doraise=True)
            print("ARM", "+".join(run))
            print(score.report(base, vector.measure(tree)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
