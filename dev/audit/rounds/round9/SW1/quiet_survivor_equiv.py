#!/usr/bin/env python3
"""R9-SW-1: the quiet-window mutants manual_plan.py left alive.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/SW1/quiet_survivor_equiv.py

Each survivor is the operator's own mutant from ``candidates()``. Head and
mutant are called on one grid. The control is a tie-only edit that must
move on at least one case the mutant does not, or the grid never reached
the arm and the equivalence is not shown.
"""
import ast
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path[:0] = ["tests", "custom_components"]
import mutation_table as mt  # noqa: E402
from heatpump_optimizer import quiet_windows as qw  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_POWER_ENTITY,
    CONF_QUIET_OFF_WINDOWS,
    CONF_QUIET_SILENT_WINDOWS,
    CONF_SILENT_MODE_FRACTION,
)

START = datetime(2026, 1, 15, tzinfo=timezone.utc)


class _St:
    def __init__(self, state, unit="W"):
        self.state = state
        self.attributes = {} if unit is None else {"unit_of_measurement": unit}


def _gs(mapping):
    def get_state(entity_id):
        if not isinstance(entity_id, str):
            raise TypeError(entity_id)
        return mapping.get(entity_id)
    return get_state


def _same(a, b) -> bool:
    if isinstance(a, BaseException) or isinstance(b, BaseException):
        return type(a) is type(b)
    if hasattr(a, "caps") or hasattr(b, "caps"):
        def eq(x, y):
            if x is None or y is None:
                return x is y
            return bool(np.array_equal(x, y))
        return (
            eq(a.caps, b.caps) and eq(a.off_steps, b.off_steps)
            and eq(a.actions, b.actions) and a.silent_dropped == b.silent_dropped
        )
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return isinstance(a, np.ndarray) and isinstance(b, np.ndarray) and bool(np.array_equal(a, b))
    return a == b


def _call(fn, args):
    try:
        return fn(*args)
    except Exception as err:  # noqa: BLE001 — the mutant's own exception is the result
        return err


def _build(text: str, name: str):
    fn = next(n for n in ast.parse(text).body
              if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(vars(qw))
    exec(compile(ast.Module([fn], []), qw.__file__, "exec"), ns)
    return ns[name]


def _replaced(src: str, line: int, new: str) -> str:
    lines = src.splitlines()
    lines[line - 1] = new if new.endswith("\n") else new
    # keep the mutant's own indentation, which `new` already carries
    return "\n".join(lines) + "\n"


CASES = {
    "_parse_spec_pair": [
        ("", ""), ("", "08:00-09:00"), ("08:00-09:00", ""),
        ("garbage", "08:00-09:00"), (None, None), ("weekdays 08:00-09:00", ""),
    ],
    "_power_entity_kw": [
        ("s", lambda e: None),
        ("s", _gs({"s": _St("0", "W")})),
        ("s", _gs({"s": _St("-3", "W")})),
        ("s", _gs({"s": _St("3500", "W")})),
        ("s", _gs({"s": _St("3500", "furlong")})),
        ("s", _gs({"s": _St("offline", "W")})),
    ],
    "compose": [
        (None, {}, _gs({}), START, 4, 0.25, 5.0),
        (np.full(4, 4.0), {}, _gs({}), START, 4, 0.25, 5.0),
        (None, {CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.n",
                CONF_QUIET_SILENT_WINDOWS: "03:00-04:00",
                CONF_SILENT_MODE_FRACTION: 0.7}, _gs({}), START, 4, 0.25, 5.0),
        (None, {CONF_QUIET_OFF_WINDOWS: "00:00-00:15"}, _gs({}), START, 4, 0.25, 5.0),
        (None, {CONF_QUIET_SILENT_WINDOWS: "", CONF_QUIET_OFF_WINDOWS: ""},
         _gs({}), START, 4, 0.25, 5.0),
        (None, {CONF_QUIET_SILENT_WINDOWS: "03:00-04:00"}, _gs({}), START, 0, 0.25, 5.0),
    ],
    "measured_ceiling_kw": [
        ({}, None, 5.0),
        ({CONF_POWER_ENTITY: "s"}, _gs({}), 5.0),
        ({CONF_POWER_ENTITY: "s"}, _gs({"s": _St("0", "W")}), 5.0),
        ({}, _gs({}), 0.0),
        ({CONF_COMPRESSOR_FREQ_SENSOR: "h"}, _gs({"h": _St("0", None)}), 5.0),
        ({CONF_POWER_ENTITY: "s"}, _gs({"s": _St("3500", "W")}), 5.0),
    ],
    "step_actions": [
        (START, -1, 0.25, "01:00-02:00", ""),
        (START, 0, 0.25, "01:00-02:00", ""),
        (START, 4, 0.25, "", ""),
        (START, 8, 0.25, "00:00-01:00", "02:00-02:15"),
        (START, 4, 0.25, "not-a-window", ""),
    ],
}

# Tie-only edits: they change the result exactly where the operator's two
# arms could have disagreed, and nowhere the mutant already moves.
CONTROLS = {
    "_parse_spec_pair GUARD_OFF d061db3d":
        "        if not spec:\n            out.append(([(0.0, 0.25)], None))\n            continue",
    "_power_entity_kw CMP_BOUND 18712c03":
        "    return kw if kw is not None and kw >= 0.0 else 0.0",
    "_power_entity_kw CMP_BOUND ff9edf11":
        "    if value < 0.0:\n        return 0.0",
    "_power_entity_kw GUARD_OFF ff9edf11":
        "    if value <= 0.0:\n        return 0.0",
    "compose GUARD_OFF 306af9f6":
        "    if actions is None:\n        return QuietCompose(caps_extra, None, None, True)",
    "compose GUARD_OFF 5ddd0985":
        "    if not silent_spec and not off_spec:\n        return QuietCompose(caps_extra, None, None, True)",
    "measured_ceiling_kw RETURN_DEL da9e8e97":
        "    return 0.0",
    "step_actions CMP_BOUND 6f152d50":
        "    if n_steps < 0 or n_steps == 0:\n        return np.array([9])",
}


def main() -> int:
    src = Path(qw.__file__).read_text()
    sites = [s for s in mt.inventory() if s["file"].endswith("quiet_windows.py")]
    by = {}
    for s in sites:
        by.setdefault(s["anchor"], []).append(s)
    failed = 0
    for anchor, control in CONTROLS.items():
        group = next(v for k, v in by.items() if k.endswith(anchor))
        assert len(group) == 1, (anchor, len(group))
        site = group[0]
        fname = site["anchor"].split(":")[1].split(" ")[0].rsplit(".", 1)[-1]
        head = _build(src, fname)
        mutant = _build(_replaced(src, site["line"], site["new"]), fname)
        # The control replaces the whole guarded statement. Indentation is
        # the line's own, so a multi-line control is written over the one line
        # only when it is a single replacement; multi-line controls below are
        # spliced as the new text of that one source line's slot by expanding.
        ctl_lines = src.splitlines()
        ctl_lines[site["line"] - 1:site["line"]] = control.split("\n")
        control_fn = _build("\n".join(ctl_lines) + "\n", fname)
        cases = diff = ctl = 0
        for args in CASES[fname]:
            cases += 1
            a, b, c = _call(head, args), _call(mutant, args), _call(control_fn, args)
            diff += not _same(a, b)
            ctl += not _same(a, c)
        ok = diff == 0 and ctl > 0
        failed += not ok
        print(f"RESULT {anchor.split(':')[-1]} cases={cases} "
              f"mutant_differs={diff} control_differs={ctl} "
              f"{'equivalent' if ok else 'NOT-SHOWN'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
