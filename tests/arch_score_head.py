#!/usr/bin/env python3
"""The architecture score still measures today's tree (R9-EG-A1).

tests/arch_score.py measures a pinned tree and stored history, so it cannot notice the instrument
going blind on the tree it is run against: a coordinator renamed, a role the engine no longer finds, a
module the metrics cannot parse. This is that check, and it is the only part that reads the working tree
-- so it is its own script, and a change to the integration selects it and not the calibration.

  * every score metric and every tripwire is a number on this tree;
  * a tree compared with itself reads NULL, and the report names no metric;
  * the coordinator class the metrics key on is the one ``tests/structure.py`` keys on;
  * nothing the scheduled solve or the what-if reaches writes the coordinator's three hubs,
    except the event-driven producers SOLVE_PATH_HUB_WRITERS names (#1736).

    PYTHONPATH=tests/hastub python3 tests/arch_score_head.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from harness import Results  # noqa: E402

from archscore import counters, score, vector  # noqa: E402
from archscore.metrics import common, hub_solve_writes  # noqa: E402

R = Results("architecture score on today's tree (R9-EG-A1)")

#: #1736: a solve plans from one record built on the loop, so the hub writes
#: hub_solve_writes still finds on the solve path are the learners its tail
#: runs, each moving configured state at the event that changed it (RCA-1736
#: section 3), keyed (writer, hub.field). A site outside this table is a
#: solve-scoped value written into shared configuration: #1736's class.
SOLVE_PATH_HUB_WRITERS = {
    ("coordinator:HeatPumpOptimizerCoordinator._apply_comfort_weight",
     "_opt_config.comfort_weight"):
        "the quiet-period learner in the solve's tail moved the learned weight",
    ("coordinator:HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale",
     "_thermal_params.house_heat_loss_scale"):
        "a finished system identification adopts its fitted scale",
}
#: The planted write the control adds as async_run_optimization's first statement.
_PLANT_AT = '        ctx = getattr(self, "_ctx", self)\n        _LOGGER.info("Running heat pump optimization'
_PLANT = '        ctx._opt_config.peak_count = 3\n'


def hub_writers(root: Path) -> set[tuple[str, str]]:
    """(writer, hub.field) for every hub write the solve roots reach in ``root``."""
    with tempfile.TemporaryDirectory(prefix="archscore-hubs-") as tmp:
        flat = Path(tmp)
        counters.flatten(root, flat, inline=True)
        pkg = common.load(str(flat))
        eng = common.engine(pkg)
        out: set[tuple[str, str]] = set()
        for r in hub_solve_writes.ROOTS:
            q = f"{common.COORD_MODULE}:{common.COORD_CLASS}.{r}"
            if q in pkg.funcs:
                out |= {(x[4], f"{x[2]}.{x[3]}") for x in hub_solve_writes._sites(eng, q)}
        return out


def planted_writers() -> tuple[bool, set[tuple[str, str]]]:
    """The positive control: today's package with one hub write planted at the
    top of async_run_optimization. ``(planted, writers)``."""
    with tempfile.TemporaryDirectory(prefix="archscore-plant-") as tmp:
        root = Path(tmp)
        shutil.copytree(ROOT / counters.PKG, root / counters.PKG,
                        ignore=shutil.ignore_patterns("__pycache__"))
        coord = root / counters.PKG / "coordinator.py"
        text = coord.read_text()
        at = text.find(_PLANT_AT)
        if at < 0:
            return False, set()
        cut = at + len('        ctx = getattr(self, "_ctx", self)\n')
        coord.write_text(text[:cut] + _PLANT + text[cut:])
        return True, hub_writers(root)


def main() -> int:
    here = vector.measure(ROOT)
    missing = [m for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY) if not isinstance(here.get(m), int)]
    R.check("every score metric and tripwire measures on today's tree", not missing,
            f"no value for {missing}; errors {[v for k, v in here.items() if k.endswith('_error')]}")
    R.check("a tree against itself reads NULL", score.delta(here, here)["verdict"] == "NULL")
    R.check("a tree against itself reports no metric moved",
            score.report(here, here).count("\n") == 0, score.report(here, here))
    structure = vector.load_structure(ROOT)
    R.check("the metrics and tests/structure.py key on the same coordinator class",
            common.COORD_CLASS == structure.COORDINATOR_CLASS_NAME,
            f"{common.COORD_CLASS} vs {structure.COORDINATOR_CLASS_NAME}")
    writers = hub_writers(ROOT)
    R.check("nothing the solve reaches writes a hub but its event-driven producers (#1736)",
            writers <= set(SOLVE_PATH_HUB_WRITERS),
            f"unlisted: {sorted(writers - set(SOLVE_PATH_HUB_WRITERS))}: put the value in "
            "the solve's record, or list the producer with the event that moves it")
    planted, seen = planted_writers()
    R.check("the hub check refuses a write planted at the top of the solve, and lists only it",
            planted and seen - set(SOLVE_PATH_HUB_WRITERS) == {
                ("coordinator:HeatPumpOptimizerCoordinator.async_run_optimization",
                 "_opt_config.peak_count")},
            f"planted={planted}; unlisted {sorted(seen - set(SOLVE_PATH_HUB_WRITERS))}")
    R.check("every listed producer is still reached, so the table holds no stale row",
            set(SOLVE_PATH_HUB_WRITERS) <= writers,
            f"stale: {sorted(set(SOLVE_PATH_HUB_WRITERS) - writers)}")
    return R.close("ARCHITECTURE SCORE HEAD CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
