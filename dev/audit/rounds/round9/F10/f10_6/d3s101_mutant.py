#!/usr/bin/env python3
"""F10.6's one in-memory mutant: CMP_BOUND on D3-s1-01's line.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/F10/f10_6/d3s101_mutant.py

Takes the mutant `candidates(..., LISTED)` generates for the lower bound of
coordinator.py's `_dhw_inlet_c` plausibility test, compiles that function from
the mutated and the unmutated module text, and calls both on a fresh inlet
probe reading. coordinator.py imports numpy, which this seat lacks, so the
function is compiled alone and bound to the production helpers it calls
(inputs.py's age_of, temperature_c, state_unit; the hastub dt_util). The
boundary reading -5.0 separates the two; 0.0 and 35.0 are the null controls,
on which the lower-bound mutant must agree with production.
"""
import __future__
import ast
import sys
import types
from datetime import timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

pkg = types.ModuleType("hpo_pkg")
pkg.__path__ = [str(mt.PRODUCTION)]
sys.modules["hpo_pkg"] = pkg
from hpo_pkg import inputs  # noqa: E402

COORD = mt.PRODUCTION / "coordinator.py"
src = COORD.read_text()
muts = [m for m in mt.candidates(COORD, mt.LISTED) if m["kind"] == "CMP_BOUND"
        and "-5.0 <= value <= 35.0" in m["old"] and "-5.0 < value" in m["new"]]
assert len(muts) == 1, f"expected one lower-bound mutant, got {len(muts)}"
mut = muts[0]
lines = src.splitlines(True)
lines[mut["line"] - 1] = mut["new"] + "\n"


def compiled(text: str):
    fn = next(n for n in ast.parse(text).body
              if isinstance(n, ast.FunctionDef) and n.name == "_dhw_inlet_c")
    ns = dict(age_of=inputs.age_of, temperature_c=inputs.temperature_c,
              state_unit=inputs.state_unit, dt_util=dt_util,
              timedelta=timedelta, Any=Any, HomeAssistant=Any,
              DHW_INLET_MAX_AGE_MINUTES=24.0 * 60.0)
    exec(compile(ast.Module([fn], []), str(COORD), "exec",
                 flags=__future__.annotations.compiler_flag), ns)
    return ns["_dhw_inlet_c"]


class _State:
    def __init__(self, v: str):
        now = dt_util.utcnow()
        self.state, self.attributes = v, {"unit_of_measurement": "°C"}
        self.last_updated = self.last_changed = self.last_reported = now


class _Hass:
    def __init__(self, v: str):
        self.states = types.SimpleNamespace(get=lambda _e: _State(v))


prod, mutant = compiled(src), compiled("".join(lines))
print(f"MUTANT {mt.triage_key(mut)}: {mut['new'].strip()}")
for v in ("-5.0", "0.0", "35.0"):
    a, b = prod(_Hass(v), "sensor.inlet"), mutant(_Hass(v), "sensor.inlet")
    print(f"RESULT reading={v} production={a} mutant={b} "
          f"{'DIFFERS' if a != b else 'same'}")
