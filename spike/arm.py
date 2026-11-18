#!/usr/bin/env python3
"""design/R11-ARCH-fabric-learner: the architecture-score reading of the whole cut (ADR-007's owed F).

An arm in the manner of dev/audit/rounds/round11/PLAN/prototypes.py (plan/r11, 819aa2e354b4), whose
sub/cut helpers and report it reuses: exact-text edits of a temporary copy of the package, the tree
under test never written. Parts, each readable alone:

  buffer   the buffer fold's gate arithmetic and envelope step            fold_buffer_cooling
  gains    the hourly gains fold                                           fold_internal_gains
  anchors  the anchor readings                                             heat_loss_anchors
  reanchor the re-anchor law's tail: gate, confidence, law, reset logs     reanchor_learned
  house    the house fold's Newton step                                    fold_house_heat_loss

Run from the repository root (the plan's prototypes.py exported beside this file, or --proto <path>):
    python3 arm.py --at <sha> [--only buffer,gains] [--each]
"""
from __future__ import annotations

import importlib.util
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tools" / "audit"))
argv = sys.argv
proto_path = Path(argv[argv.index("--proto") + 1]) if "--proto" in argv else HERE / "prototypes.py"
spec = importlib.util.spec_from_file_location("prototypes", proto_path)
proto = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proto)
sub, cut, PKG, score, vector = proto.sub, proto.cut, proto.PKG, proto.score, proto.vector

IMPORT_ANCHOR = "from . import boost\n"


def _module(r: Path) -> None:
    """The new module, and the names the coordinator keeps importable from it (once per tree)."""
    target = r / PKG / "fabric_learning.py"
    if target.exists():
        return
    shutil.copy(HERE / "fabric_learning.py", target)
    sub(r, "coordinator.py", IMPORT_ANCHOR,
        IMPORT_ANCHOR
        + "from .fabric_learning import (  # noqa: F401\n"
          "    HOUSE_LOSS_ALPHA, HOUSE_LOSS_MAX_STEP, HeatLossLearned, fold_buffer_cooling, fold_house_heat_loss,\n"
          "    fold_internal_gains, heat_loss_anchors, house_loss_confidence, reanchor_learned,\n"
          "    LEARNER_TRUST_REGION as _LEARNER_TRUST_REGION, house_loss_terms as _house_loss_terms,\n"
          "    learned_zone_temperature as _learned_zone_temperature, zone_capacity as _zone_capacity,\n"
          ")\n")
    for line in ("HOUSE_LOSS_ALPHA = 0.02\n", "HOUSE_LOSS_MAX_STEP = 0.05\n", "_LEARNER_TRUST_REGION = 0.5\n"):
        sub(r, "coordinator.py", "\n" + line, "\n")
    cut(r, "coordinator.py", "def house_loss_confidence(", "#: The confidence one EWMA", "", keep_end=True)
    cut(r, "coordinator.py", "def _house_loss_terms(", "def _restored_stores(", "", keep_end=True)


def buffer(r: Path) -> None:
    _module(r)
    cut(r, "coordinator.py", "        if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:\n",
        "        self._buffer_cooling_samples += 1\n",
        "        fold = fold_buffer_cooling(\n"
        "            self._buffer_cooling_rate, previous_temp, buffer_temp, dt_h, self._buffer_cooling_bounds()\n"
        "        )\n"
        "        if fold is None:\n            return\n"
        "        observed, rate = fold\n"
        "        self._apply_buffer_cooling_rate(rate)\n", keep_end=True)
    for name in ("ALPHA_DOWN", "ALPHA_UP", "MIN_SAMPLE_HOURS", "MAX_SAMPLE_HOURS", "MIN_DELTA"):
        cut(r, "coordinator.py", f"BUFFER_COOLING_{name} = ", "\n", "", keep_end=False)
    cut(r, "coordinator.py", "BUFFER_AMBIENT_TEMP = ", "\n", "", keep_end=False)


def gains(r: Path) -> None:
    _module(r)
    cut(r, "coordinator.py",
        "        if previous_time is None or dt_h <= 1e-6:\n            return\n        capacity = _zone_capacity(",
        "    def ",
        "        self._internal_gains_profile = fold_internal_gains(\n"
        "            self._internal_gains_profile, ctx._thermal_params, previous_time, residual, dt_h\n"
        "        )\n", keep_end=True)


def anchors(r: Path) -> None:
    _module(r)
    cut(r, "coordinator.py", "    def _house_heat_loss_anchor(self) -> float:\n", "    def _heat_loss_anchors(", "", keep_end=True)
    cut(r, "coordinator.py", "        return {\n            \"house_heat_loss_anchor\": round(self._house_heat_loss_anchor(), 6),\n",
        "    def _reanchor_house_heat_loss_scale(",
        "        return heat_loss_anchors(\n"
        "            ctx._thermal_params, ctx._config, heat_energy.meter_of(self).earned, self._lower_floor_loss_ratio\n"
        "        )\n\n", keep_end=True)


def reanchor(r: Path) -> None:
    _module(r)
    cut(r, "coordinator.py", "        live, ratio = self._heat_loss_anchors(), self._lower_floor_loss_ratio\n",
        "    async def _async_learn_buffer_cooling(",
        "        learned = reanchor_learned(\n"
        "            HeatLossLearned(self._house_heat_loss_scale, self._house_heat_loss_samples,\n"
        "                            self._lower_floor_loss_ratio, self._lower_floor_loss_samples),\n"
        "            (anchor, lower_then), stored.get(\"house_heat_loss_basis\"), self._heat_loss_anchors(),\n"
        "        )\n"
        "        if learned is None:\n"
        "            # Below the gate, or a pre-fix store with no anchor to re-express,\n"
        "            # which the caller adopts on its next save.\n"
        "            return swapped\n"
        "        self._house_heat_loss_samples, self._lower_floor_loss_samples = learned.scale_samples, learned.ratio_samples\n"
        "        self._apply_house_heat_loss_scale(learned.scale)\n"
        "        self._apply_lower_floor_loss_ratio(learned.ratio)\n"
        "        return True\n\n", keep_end=True)


def house(r: Path) -> None:
    _module(r)
    cut(r, "coordinator.py", "        base_u, capacity = _house_loss_terms(params)\n        step = learner_newton_step(\n            self._house_heat_loss_scale,\n",
        "        if step is None:\n            return clean\n        target_scale, new_scale = step\n        self._apply_house_heat_loss_scale(new_scale)\n",
        "        step = fold_house_heat_loss(self._house_heat_loss_scale, params, residual, delta_t, dt_h)\n", keep_end=True)


def module_only(r: Path) -> None:
    _module(r)


PARTS = {"module": module_only, "buffer": buffer, "gains": gains, "anchors": anchors, "reanchor": reanchor, "house": house}
WHOLE = ("buffer", "gains", "anchors", "reanchor", "house")


def main() -> int:
    at = argv[argv.index("--at") + 1]
    names = argv[argv.index("--only") + 1].split(",") if "--only" in argv else list(WHOLE)
    runs = [[n] for n in names] if "--each" in argv else [names]
    with tempfile.TemporaryDirectory(prefix="r11-fabric-") as tmp:
        base_tree = score.tree_of(at, Path(tmp) / "base")
        base = vector.measure(base_tree)
        for i, run in enumerate(runs):
            tree = Path(tmp) / f"arm{i}"
            shutil.copytree(base_tree / "custom_components", tree / "custom_components")
            for name in run:
                PARTS[name](tree)
            for path in (tree / PKG).glob("*.py"):
                py_compile.compile(str(path), doraise=True)
            if "--keep" in argv:
                shutil.copytree(tree, Path(argv[argv.index("--keep") + 1]) / "+".join(run))
            print("ARM", "+".join(run), "at", at)
            print(score.report(base, vector.measure(tree)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
