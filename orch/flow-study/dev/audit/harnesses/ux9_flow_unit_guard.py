#!/usr/bin/env python3
"""Mutation probes for the two flow-meter sites PR #2024 (R9-UX-9, #1956) added.

Sites, both in ``custom_components/heatpump_optimizer/inputs.py``:
- ``normalize_flow_kg_s GUARD_OFF b46fca00`` (``if unit is None:`` -> ``if False:``).
  The ``survivor_triage`` row
  ``tests/mutation_ledger/survivor_triage/inputs.py/normalize_flow_kg_s.GUARD_OFF.b46fca00.json``
  marks it ``equivalent`` on this probe's result.
- ``InputReader.read_flow_kg_s RETURN_DEL 69557675#2`` (the refusal arm's
  ``return reading`` -> ``pass``), pinned ``killed_by`` ``tests/features.py``
  from CI's measurement; this probe shows the features check that kills it.
Re-run it when ``normalize_flow_kg_s``, ``read_flow_kg_s``,
``FLOW_UNIT_TO_KG_S`` or the flow-meter block of ``tests/features.py`` changes.

Metric: (A) the number of failing checks when ``tests/features.py``'s own
flow-meter block (sliced verbatim from ``def _fm_reader`` to the first-reason
check, minus the two checks that need the coordinator and sensor fixtures)
runs in each tree; (B) the number of cases whose (value, problem, ok), by
``repr``, differ from the head's when the real ``normalize_flow_kg_s`` and
``InputReader.read_flow_kg_s`` are driven over 726 cases (20 units incl.
None, 'None', '', ' L/min ', 0, False and unknown ones, plus a state with no
unit attribute; 9 values and 13 states incl. nan, inf, -3, -1e-12 and
unavailable; ages 1 and 45 min). Trees, copied from the checkout:
- ``head``: unchanged;
- ``m278_guard_off``: the GUARD_OFF mutant;
- ``c278_control``: the perturbation for 278; the guard arm returns the raw
  value instead of None, so it differs exactly where the unit is None;
- ``m831_return_del``: the RETURN_DEL mutant;
- ``m831_return_del@8fb1b717-features``: the same mutant against
  ``tests/features.py`` as it was at 8fb1b717, before the check was extended
  (the null control for the new assertion).

Expected, as measured at ef115813 and on the merged trees after it:
    BLOCK head: rc=0 failing_checks=0
    BLOCK m278_guard_off: rc=0 failing_checks=0
    BLOCK c278_control: rc=0 failing_checks=0
    BLOCK m831_return_del: rc=0 failing_checks=2   (one check plus its summary line)
    BLOCK m831_return_del@8fb1b717-features: rc=0 failing_checks=0
    GRID m278_guard_off: cases=726 differing=0
    GRID c278_control: cases=726 differing=29   (every one a None unit)
    GRID m831_return_del: cases=726 differing=36

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/ux9_flow_unit_guard.py <out-dir>

It writes ``<variant>.block.txt`` and ``<variant>.grid.json`` into ``<out-dir>``.
"""

import json, os, shutil, subprocess, sys, tempfile
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


REPO = repo_root(__file__)

INP = "custom_components/heatpump_optimizer/inputs.py"
GUARD = "    if unit is None:\n        return None\n    factor = FLOW_UNIT_TO_KG_S"
REFUSE = ("                    \"unknown_unit\" if converted is None else \"implausible\"\n"
          "                )\n            return reading\n")
VARIANTS = {
    "head": [],
    # mutation_table GUARD_OFF: the test becomes `if False:`
    "m278_guard_off": [(GUARD, GUARD.replace("if unit is None:", "if False:"))],
    # boundary-only control for 278: the guard arm hands back the raw value,
    # so it differs from the fall-through exactly when unit is None
    "c278_control": [(GUARD, GUARD.replace("        return None\n", "        return value\n"))],
    # mutation_table RETURN_DEL: the statement becomes `pass`
    "m831_return_del": [(REFUSE, REFUSE.replace("            return reading\n", "            pass\n"))],
}
# the same 831 mutant against features.py at 8fb1b717, before this round's
# edit (git HEAD), the survival the `mutation` job reported
OLDTEST = {"m831_return_del@8fb1b717-features": "m831_return_del"}

FEATURE_BLOCK_DRIVER = r'''
import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from datetime import datetime
from harness import FakeHass, FakeState, Results, UTC, minutes_ago
NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
from heatpump_optimizer import const as _fb_const
from heatpump_optimizer import flow_meter as _fm
from heatpump_optimizer.inputs import InputReader as _fmReader
R = Results("flow")
src = open("tests/features.py").read()
start = src.index("def _fm_reader(")
end = src.index("sys.exit(R.close(\"FEATURE CHECKS\"))", start)
block = src[start:end]
# keep the reader helper and the reader-level checks; drop the two that need
# the coordinator/sensor fixtures defined earlier in features.py
cut0 = block.index("from heatpump_optimizer.sensor import CurrentPowerSensor")
cut1 = block.index("R.check(\n    \"an unknown flow unit is absent rather than guessed\"")
block = block[:cut0] + block[cut1:]
exec(compile(block, "features.py#flow-meter-block", "exec"))
print("RC", R.close("FLOW BLOCK"))
'''

GRID_DRIVER = r'''
import json, sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from datetime import datetime
from harness import FakeHass, FakeState, UTC, minutes_ago
from heatpump_optimizer import const
from heatpump_optimizer.inputs import InputReader, normalize_flow_kg_s
NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
UNITS = [None, "None", "none", "", " ", "L/min", " L/min ", "L/s", "L/h", "m³/h",
         "m³/s", "kg/s", "kg/min", "kg/h", "gal/min", "furlongs/fortnight", 0, 1.0,
         False, "NONE"]
VALUES = [0.0, -0.0, 1.0, 15.0, -3.0, 1e-12, 1e300, float("inf"), float("nan")]
rows = []
for u in UNITS:
    for v in VALUES:
        rows.append(["norm", repr(u), repr(v), repr(normalize_flow_kg_s(v, u))])
STATES = ["15.0", "0.0", "-0.0", "-3.0", "-1e-12", "1e300", "nan", "inf", "-inf",
          "unavailable", "unknown", "garbage", ""]
for u in UNITS + ["<no unit attr>"]:
    for st in STATES:
        for age in (1, 45):
            kw = {} if u == "<no unit attr>" else {"unit": u}
            hass = FakeHass({"sensor.flow": FakeState(st, last_updated=minutes_ago(age, NOW), **kw)})
            cfg = {const.CONF_FLOW_METER_ENTITY: "sensor.flow"}
            r = InputReader(hass, cfg, now=lambda: NOW).read_flow_kg_s(const.CONF_FLOW_METER_ENTITY)
            rows.append(["read", repr(u), st, age, repr(r.value), r.problem, r.ok])
print(json.dumps(rows))
'''

def build(variant, root):
    head = REPO
    old_features = variant in OLDTEST
    variant = OLDTEST.get(variant, variant)
    for d in ("custom_components", "tests"):
        shutil.copytree(head / d, Path(root) / d, ignore=shutil.ignore_patterns("__pycache__"))
    f = Path(root) / INP
    src = f.read_text()
    for old, new in VARIANTS[variant]:
        assert src.count(old) == 1, (variant, src.count(old))
        src = src.replace(old, new)
    f.write_text(src)
    if old_features:
        (Path(root) / "tests/features.py").write_text(subprocess.run(
            ["git", "show", "8fb1b717d83be7569ac43f91051dc01945799824:tests/features.py"], cwd=head,
            capture_output=True, text=True, check=True).stdout)

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
res = {}
for v in list(VARIANTS) + list(OLDTEST):
    with tempfile.TemporaryDirectory() as root:
        build(v, root)
        env = dict(os.environ, PYTHONPATH=f"{root}/tests/hastub")
        a = subprocess.run([sys.executable, "-c", FEATURE_BLOCK_DRIVER], cwd=root,
                           capture_output=True, text=True, env=env)
        b = subprocess.run([sys.executable, "-c", GRID_DRIVER], cwd=root,
                           capture_output=True, text=True, env=env)
        if b.returncode:
            print(v, "GRID FAILED", b.stderr[-3000:]); sys.exit(2)
        (out / f"{v}.block.txt").write_text(a.stdout + a.stderr)
        res[v] = json.loads(b.stdout.strip().splitlines()[-1])
        (out / f"{v}.grid.json").write_text(json.dumps(res[v], indent=0))
        fails = [l for l in a.stdout.splitlines() if "FAIL" in l]
        print(f"BLOCK {v}: rc={a.returncode} failing_checks={len(fails)}")
        for l in fails:
            print("   ", l.strip()[:200])
h = res["head"]
for v in res:
    if v == "head":
        continue
    rows = res[v]
    assert len(rows) == len(h)
    d = [(a, b) for a, b in zip(h, rows) if a != b]
    print(f"GRID {v}: cases={len(h)} differing={len(d)} "
          f"(units of the differing: {sorted({a[1] for a, b in d})})")
