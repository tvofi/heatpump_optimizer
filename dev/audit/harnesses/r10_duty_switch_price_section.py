#!/usr/bin/env python3
"""Run R10-DUTY-SWITCH-PLANNER-PRICE's section of ``tests/features.py`` alone, and its mutants.

WHY IT EXISTS. ``tests/features.py`` has no section filter, and the mutation
proof of the group (the leg rule's leaf, the switch term, the lost running
time, the banned candidate, the learner's count cap and its read for the
planner) runs the section once per mutant. This cuts the section out of the
script at its two markers, binds the six names the script had bound by then,
and runs it. It executes the tree's own text: a check edited in
``tests/features.py`` is the check run here.

It refuses (exit 2) when a marker is missing or the section holds no check,
so a moved marker cannot read as a pass.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py --mutants [name ...]

``--mutants`` copies the package and ``tests/`` to a private directory per
mutant, applies one edit there (the tree is never written), runs the section
on the copy and prints the checks that went red. An unmutated copy runs
first as the control and must pass. A mutant whose pattern is not found
exactly once, or that turns no check red, is printed as such and the exit
code is 1. The coordinator's one argument is outside the section (its check
sits beside #1512's in the lifecycle part of the script) and is proven by a
whole run of ``tests/features.py``.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(os.environ.get("DSP_SECTION_ROOT") or __file__)
START = "from types import SimpleNamespace as _DspNS"
END = '\nsys.exit(R.close("FEATURE CHECKS"))'
PRELUDE = """
from datetime import datetime, timedelta
import numpy as np
from harness import Results, UTC
from profiles import solve_inputs
R = Results("R10-DUTY-SWITCH-PLANNER-PRICE's section of tests/features.py")
"""
PKG = "custom_components/heatpump_optimizer/"

#: name, file, the text to find exactly once, its replacement.
MUTANTS: list[tuple[str, str, str, str]] = [
    ("optimizer: a candidate is tried with no requirement to hold it to", PKG + "optimizer.py",
     "if kept_requirement is None or not duty_legs.switch_weight(", "if not duty_legs.switch_weight("),
    ("optimizer: a candidate pass that raises is not caught", PKG + "optimizer.py",
     "    except Exception as err:  # noqa: BLE001 - a candidate is optional", "    except KeyError as err:  # a candidate is optional"),
    ("learner: no count cap", PKG + "duty_switch.py",
     "        if self.n > N_CAP:\n", "        if False:\n"),
    ("learner: the cap scales the stops alone", PKG + "duty_switch.py",
     "self.k, self.kept_w = self.k * scale, self.kept_w * scale", "self.k = self.k * scale"),
    ("learner: the cap is three times the on-threshold", PKG + "duty_switch.py",
     "N_CAP = 2.0 * N_ON", "N_CAP = 3.0 * N_ON"),
    ("learner: the read ignores the latch", PKG + "duty_switch.py",
     "read = [d if d.usable else Direction() for", "read = [d for"),
    ("learner: the read swaps the directions", PKG + "duty_switch.py",
     "return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
     "return (read[1].p, read[0].p), (read[1].median_off_s or 0.0, read[0].median_off_s or 0.0)"),
    ("learner: the read hands the off time of the other direction", PKG + "duty_switch.py",
     "(read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
     "(read[1].median_off_s or 0.0, read[0].median_off_s or 0.0)"),
    ("leaf: the hot-water-to-heating switch reads the other direction", PKG + "duty_legs.py",
     "(before == DHW) & (after == SPACE),\n        p_ds,", "(before == DHW) & (after == SPACE),\n        p_sd,"),
    ("leaf: the switch weight takes the larger neighbouring draw", PKG + "duty_legs.py",
     "np.minimum(level[_BEFORE], level[_AFTER])", "np.maximum(level[_BEFORE], level[_AFTER])"),
    ("leaf: the in-step weight draws the smaller circuit, not the combined draw", PKG + "duty_legs.py",
     "np.where(two, p_ds * level, 0.0)",
     "np.where(two, p_ds * np.minimum(space, np.asarray(dhw_kw, dtype=float)), 0.0)"),
    ("leaf: the weight is not divided by the maximum draw", PKG + "duty_legs.py",
     "axis=1)) / p_max", "axis=1))"),
    ("leaf: a small hot-water share no longer collapses to heating", PKG + "duty_legs.py",
     "to_space = both & (dhw_min < SPLIT_MIN_MINUTES)", "to_space = both & (dhw_min > SPLIT_MIN_MINUTES)"),
    ("leaf: a small heating share no longer collapses to hot water", PKG + "duty_legs.py",
     "~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)",
     "~to_space & (step_minutes - dhw_min > SPLIT_MIN_MINUTES)"),
    ("leaf: the leg classification ignores the duty floor", PKG + "duty_legs.py",
     "_runs(space, floor), _runs(dhw, floor)", "_runs(space, None), _runs(dhw, None)"),
    # The leaf's own zero-pair return is a shortcut, not a rule: dropping its
    # zero-pair clause (`if p_max <= 0:`) was run and turns no check red,
    # because zero probabilities already weigh zero. The rule is the two below.
    ("leaf: the zero-pair early return fires when either direction is unpriced", PKG + "duty_legs.py",
     "if (p_ds <= 0 and p_sd <= 0) or p_max <= 0:", "if (p_ds <= 0 or p_sd <= 0) or p_max <= 0:"),
    ("leaf: a pump with no maximum draw is not returned early", PKG + "duty_legs.py",
     "if (p_ds <= 0 and p_sd <= 0) or p_max <= 0:", "if p_ds <= 0 and p_sd <= 0:"),
    ("leaf: the early return is one entry per step, not per row", PKG + "duty_legs.py",
     "return np.zeros(space.shape[0])", "return np.zeros(space.shape[1])"),
    ("optimizer: no priced direction still returns a pair", PKG + "optimizer.py",
     "return stops if max(stops) > 0 else None", "return stops"),
    ("leaf: the charged step is the hot-water block's last step", PKG + "duty_legs.py",
     "charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)",
     "charged[:-1] |= (last[:-1] == DHW) & (first[1:] == SPACE)"),
    ("leaf: the delivered draw is keyed on the clamped install", PKG + "duty_legs.py",
     "    if floor is None:\n        return space_kw", "    if floor is not None:\n        return space_kw"),
    ("leaf: the delivered draw loses only the space share", PKG + "duty_legs.py",
     "(1.0 - avail) * (space_kw + dhw_kw)", "(1.0 - avail) * space_kw"),
    ("optimizer: the switch term is handed the delivered draw", PKG + "optimizer.py",
     "switch_cost(space_power, dhw_plan_power)", "switch_cost(heat_power, dhw_plan_power)"),
    ("optimizer: the simulation is handed the shipped draw", PKG + "optimizer.py",
     "_space_traj(heat_power, buffer_exo_kw)", "_space_traj(space_power, buffer_exo_kw)"),
    ("optimizer: the energy cost is handed the shipped draw", PKG + "optimizer.py",
     "drawn = combined if heat_power is space_power else heat_power + dhw_plan_power",
     "drawn = combined"),
    ("optimizer: the publication drops the solve's availability vector", PKG + "optimizer.py",
     "heat_space = optimal_space if self._space_avail is None else duty_legs",
     "heat_space = optimal_space if True else duty_legs"),
    ("planner: the placement ban is not OR'd into forced_off", PKG + "dhw_planner.py",
     "return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)",
     "return forced_off"),
    ("optimizer: a candidate short of its requirement is adopted", PKG + "optimizer.py",
     "            and first_short(plan.schedule, requirement, unheld)[1] is None\n",
     "            and True\n"),
    ("optimizer: a candidate with hot water on a banned step is adopted", PKG + "optimizer.py",
     "            not np.any(plan.schedule[ban & ~forced_on] > 0)\n", "            True\n"),
    ("optimizer: the candidate is adopted on a higher score", PKG + "optimizer.py",
     "if score < base - 1e-9:", "if score > base - 1e-9:"),
    ("leaf: the lost share is not capped at one", PKG + "duty_legs.py",
     "return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
     "return stop_probability[0] * off_seconds[0] / (step_minutes * 60.0)"),
    ("leaf: the lost share ignores the stop probability", PKG + "duty_legs.py",
     "min(1.0, stop_probability[0] * off_seconds[0] /", "min(1.0, off_seconds[0] /"),
    # The fix reviewer's three survivors at ee89d50b2b (R5, R9, R11), its texts.
    ("optimizer: the co-optimisation headroom ignores the availability vector", PKG + "optimizer.py",
     "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, None, _duty_floor(self))"),
    ("optimizer: the availability vector is classified with no duty floor", PKG + "optimizer.py",
     "return duty_legs.availability(space, tank, lost, _duty_floor(opt))",
     "return duty_legs.availability(space, tank, lost, None)"),
    ("optimizer: the candidate pass runs on a combi store", PKG + "optimizer.py",
     "or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
     "or not opt.config.cycling_cost > 0:"),
    ("optimizer: the co-optimisation headroom is handed no duty floor", PKG + "optimizer.py",
     "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, self._space_avail, None)"),
    ("arbiter: the share serves the legs in reverse order", PKG + "pump_arbiter.py",
     "return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
     "return legs[-1][0] if (now - result.timestamps[i]) < first_ends else legs[0][0]"),
]


def run_section(root: Path) -> int:
    text = (root / "tests" / "features.py").read_text()
    if text.count(START) != 1 or text.count(END) != 1:
        print("REFUSED: a section marker is missing or repeated in tests/features.py")
        return 2
    section = text[text.index(START):text.index(END)]
    sys.path[:0] = [str(root / "tests"), str(root / "custom_components")]
    scope: dict = {"__name__": "duty_switch_price_section"}
    exec(compile(PRELUDE + section, "tests/features.py[duty-switch-price]", "exec"), scope)
    results = scope["R"]
    if not results.checks:
        print("REFUSED: the section ran no check")
        return 2
    return results.close("DUTY-SWITCH PLANNER-PRICE SECTION CHECKS")


def _copy_run(edit: tuple[str, str, str] | None) -> tuple[int | None, list[str]]:
    """The section's exit code and red check names on a private copy, ``None`` when the pattern is not there once."""
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp)
        for part in ("custom_components", "tests"):
            shutil.copytree(ROOT / part, copy / part, ignore=shutil.ignore_patterns("__pycache__", "golden"))
        if edit is not None:
            path, old, new = edit
            text = (copy / path).read_text()
            if text.count(old) != 1:
                return None, []
            (copy / path).write_text(text.replace(old, new))
        env = {**os.environ, "DSP_SECTION_ROOT": str(copy / "custom_components"),
               "PYTHONPATH": str(copy / "tests" / "hastub"), "PYTHONDONTWRITEBYTECODE": "1"}
        out = subprocess.run([sys.executable, __file__], cwd=copy, env=env, capture_output=True, text=True)
        red = [line[7:].split("  [")[0] for line in out.stdout.splitlines() if line.startswith("  FAIL ")]
        if "SECTION CHECKS" not in out.stdout:  # a traceback exits 1 too, and closes nothing
            red.append(f"the section stopped: {(out.stderr.strip().splitlines() or ['no output'])[-1]}")
        return out.returncode, red


def run_mutants(names: list[str]) -> int:
    code, red = _copy_run(None)
    print(f"== control, no edit: exit {code}, {len(red)} red")
    if code != 0:
        print("\n".join(f"     {name}" for name in red))
        return 1
    bad = 0
    for name, path, old, new in MUTANTS:
        if names and name not in names:
            continue
        code, red = _copy_run((path, old, new))
        verdict = "PATTERN NOT FOUND ONCE" if code is None else f"{len(red)} red" if red else "SURVIVED"
        bad += not red
        print(f"== {name}: {verdict}")
        print("\n".join(f"     {check}" for check in red), end="\n" if red else "")
    print(f"RESULT mutants_not_killed={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(run_mutants(sys.argv[2:]) if sys.argv[1:2] == ["--mutants"] else run_section(ROOT))
