#!/usr/bin/env python3
"""ARCH2-s1 (round 10, D7): does hub_solve_writes still see an in-place write to the parameters?

The gaming check for P1. P1 removes the 15 _thermal_params sites by replacing each in-place edit
with a published snapshot; a fair drop needs the census to keep seeing a NEW in-place write after
it, through every spelling a consumer holds. Each probe plants one write into a copy of the tree
and reads the census.

Metric: hub_solve_writes on the tree with one planted line, against the same tree without it;
        seen = the planted tree reads one more site.
Count key: distinct (file, line, hub, field) sites, the metric's own key.
Instrumented symbols: archscore.metrics.hub_solve_writes:measure over
        coordinator:HeatPumpOptimizerCoordinator._update_current_state (the planted coordinator lines)
        and dhw_learning:DhwProfileLearner.apply_cooling_rate (the planted learner line).
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s1/census_probe.py --tree main|proto
          main   the baseline tree (git object BASELINE), spellings a consumer holds there
          proto  the baseline with P1_thermal_params_single_owner.patch, spellings it holds there
Perturbation: none beyond the plant; control_hub_direct must read seen=True on both trees (a probe
          that cannot see the plain spelling measures nothing).
Expected (baseline 9061fbd3d710): main -- every probe seen; proto -- control and local alias seen,
          via_live_model / via_reader (learner and guard) NOT seen: the census derives aliases
          from constructor arguments only, so P1's reader callables and its attribute rebind of the
          live model are outside it. That is an instrument hole P1 opens, reported, not hidden.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from archscore import score  # noqa: E402
from archscore.metrics import hub_solve_writes as h  # noqa: E402

BASELINE = "9061fbd3d710d5894b7083d8a58b8203f9e7aa97"
PATCH = HERE / "P1_thermal_params_single_owner.patch"
PKG = "custom_components/heatpump_optimizer"
TREES = {
    "main": {
        "C": "        ctx._thermal_params.ambient_humidity = self._current_humidity()\n",
        "D": "        self._params.dhw_cooling_rate = self.cooling_rate\n",
        "probes": {
            "control_hub_direct": ("C", '        getattr(self, "_ctx", self)._thermal_params.cop_scale = 1.0\n'),
            "via_live_model": ("C", "        self._thermal_model.params.cop_scale = 1.0\n"),
            "via_guard_reader": ("C", "        self._legionella._params.dhw_legionella_temp = 1.0\n"),
            "via_learner_reader": ("D", "        self._params.dhw_setpoint = 1.0\n"),
            "via_local_alias": ("C", "        _p = self._thermal_params\n        _p.cop_scale = 1.0\n"),
        },
    },
    "proto": {
        "C": "        _publish_params(self, ambient_humidity=self._current_humidity())\n",
        "D": "        self._publish(dhw_cooling_rate=self.cooling_rate)\n",
        "probes": {
            "control_hub_direct": ("C", '        getattr(self, "_ctx", self)._thermal_params.cop_scale = 1.0\n'),
            "via_live_model": ("C", "        self._thermal_model.params.cop_scale = 1.0\n"),
            "via_guard_reader": ("C", "        self._legionella._params().dhw_legionella_temp = 1.0\n"),
            "via_learner_reader": ("D", "        self._params().dhw_setpoint = 1.0\n"),
            "via_local_alias": ("C", "        _p = self._thermal_params\n        _p.cop_scale = 1.0\n"),
        },
    },
}
FILES = {"C": "coordinator.py", "D": "dhw_learning.py"}


def tree(into: Path, proto: bool) -> Path:
    into.mkdir()
    score.tree_of(BASELINE, into)
    if proto:
        subprocess.run(["git", "apply", "--include=custom_components/*", "--whitespace=nowarn", str(PATCH)],
                       cwd=into, check=True)
    return into


def main(argv: list[str]) -> int:
    if "--tree" not in argv or argv[argv.index("--tree") + 1] not in TREES:
        print(__doc__)
        return 2
    which = argv[argv.index("--tree") + 1]
    spec = TREES[which]
    with tempfile.TemporaryDirectory(prefix="arch2s1-census-") as tmp:
        base = h.measure(tree(Path(tmp) / "base", which == "proto"))["value"]
        print(f"RESULT tree={which} base hub_solve_writes={base} count")
        for name, (key, line) in spec["probes"].items():
            d = tree(Path(tmp) / name, which == "proto")
            f = d / PKG / FILES[key]
            text = f.read_text()
            assert text.count(spec[key]) == 1, (which, name)
            f.write_text(text.replace(spec[key], spec[key] + line))
            v = h.measure(d)["value"]
            print(f"RESULT tree={which} {name} hub_solve_writes={v} count seen={v > base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
