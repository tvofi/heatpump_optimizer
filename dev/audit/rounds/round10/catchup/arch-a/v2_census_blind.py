#!/usr/bin/env python3
"""arch-a V2 (round 10 catch-up verify, D7-s1-83): spellings of an in-place thermal-parameter
write that the finder did not plant, read by the hub census on the working tree given.

Metric: per plant, hub_solve_writes(planted tree) - hub_solve_writes(unplanted tree); seen = >0.
Count key: the metric's own (file, line, hub, field) sites.
Instrumented symbols: tools/audit/archscore/metrics/hub_solve_writes.py:measure over
        coordinator:HeatPumpOptimizerCoordinator._update_current_state (anchor: the humidity write)
        and legionella:LegionellaGuard (anchor: the dhw_legionella_temp read at line ~191).
Command:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/arch-a/v2_census_blind.py --kind main|proto
          run from the root of the tree under test (main = unpatched, proto = P1 applied); the
          package is copied to a temp dir per plant, the tree itself is never written.
Null control: control_* plants (the plain hub spelling) must read seen=True on both trees, else
          the plant site is unreached and the arm measures nothing.
Expected (d749c986d, darwin): main -- every plant seen; proto -- setattr_live_model,
          two_hop_live_model, learner_reader_from_coord, guard_reader_in_guard NOT seen.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tools" / "audit"))
from archscore.metrics import hub_solve_writes as h  # noqa: E402

PKG = "custom_components/heatpump_optimizer"
ANCHOR = {
    "main": {"C": "        ctx._thermal_params.ambient_humidity = self._current_humidity()\n",
             "L": "        target = float(self._params.dhw_legionella_temp)\n"},
    "proto": {"C": "        _publish_params(self, ambient_humidity=self._current_humidity())\n",
              "L": "        target = float(self._params().dhw_legionella_temp)\n"},
}
PLANTS = {
    "main": {
        "control_coord": ("C", "        ctx._thermal_params.cop_scale = 1.0\n"),
        "setattr_live_model": ("C", '        setattr(self._thermal_model.params, "cop_scale", 1.0)\n'),
        "two_hop_live_model": ("C", "        _m = self._thermal_model\n        _m.params.cop_scale = 1.0\n"),
        "learner_reader_from_coord": ("C", "        self._dhw_learner._params.cop_scale = 1.0\n"),
        "guard_reader_in_guard": ("L", "        self._params.dhw_legionella_enabled = True\n"),
    },
    "proto": {
        "control_coord": ("C", "        ctx = getattr(self, '_ctx', self)\n        ctx._thermal_params.cop_scale = 1.0\n"),
        "setattr_live_model": ("C", '        setattr(self._thermal_model.params, "cop_scale", 1.0)\n'),
        "two_hop_live_model": ("C", "        _m = self._thermal_model\n        _m.params.cop_scale = 1.0\n"),
        "learner_reader_from_coord": ("C", "        self._dhw_learner._params().cop_scale = 1.0\n"),
        "guard_reader_in_guard": ("L", "        self._params().dhw_legionella_enabled = True\n"),
    },
}
FILES = {"C": "coordinator.py", "L": "legionella.py"}


def copy_tree(dst: Path) -> Path:
    shutil.copytree(ROOT / PKG, dst / PKG)
    return dst


def main(argv: list[str]) -> int:
    kind = argv[argv.index("--kind") + 1] if "--kind" in argv else ""
    if kind not in PLANTS:
        print(__doc__)
        return 2
    with tempfile.TemporaryDirectory(prefix="archa-census-") as tmp:
        base = h.measure(copy_tree(Path(tmp) / "base"))["value"]
        print(f"RESULT kind={kind} base hub_solve_writes={base} count")
        for name, (key, line) in PLANTS[kind].items():
            d = copy_tree(Path(tmp) / name)
            f = d / PKG / FILES[key]
            text = f.read_text()
            anchor = ANCHOR[kind][key]
            if text.count(anchor) != 1:
                print(f"RESULT kind={kind} {name} anchor_count={text.count(anchor)} (skipped)")
                continue
            f.write_text(text.replace(anchor, anchor + line))
            v = h.measure(d)["value"]
            print(f"RESULT kind={kind} {name} hub_solve_writes={v} count seen={v > base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
