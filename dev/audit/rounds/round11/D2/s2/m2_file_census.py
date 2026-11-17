"""D2.M2 file axis: every production module in the seat's scope, classified for COP/derate content.

Not a finding harness (it hooks no production symbol): it is the coverage record that each of
the 95 files in `check_scopes.py --seat D2-s2` was run through the step's method -- locate
every COP law, derate, capacity cap and priced-formula input; a file that IMPLEMENTS one is
driven by an executed identity harness (m2_cop_laws.py, m2_capacity_envelope.py,
m2_priced_surface.py), a file that only CALLS the single-sourced law inherits those identities,
and a file with neither has nothing for D2.M2 to measure.
Metric: law_impl_files = files containing the COP law's own constants (0.025 slope, 273.15
Carnot offset) or a derate formula; expected 1 (thermal_model.py) for the law, exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s2/m2_file_census.py
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B5.
"""
import glob
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

LAW = re.compile(r"273\.15\s*[-+)]|0\.025\s*\*|carnot_(?:ref|flow)\b")
DERATE = re.compile(r"def (?:derate_from_duty|partload_factor|_partload_derate|flow_lift_factor|_cop_law|_batch_cop|factor)\b")
CAP = re.compile(r"_capacity_caps|_fold_capacity_envelope|CAPACITY_FLOOR_FRACTION|power_caps_extra|power_cap_breach_c")
PRICED = re.compile(r"declared_modulation|levels_clamped|compressor_modulation|space_setpoint_unit|flow_curve_cop|cop_flow_carnot")
CALLS = re.compile(r"compute_cop(?:_dhw)?\(|marginal_cop\(|heat_per_cop_kw\(|power_for_heat_per_cop_kw\(|partload_factor\(|\.factor\(")
HARNESS = {"law": "m2_cop_laws.py", "capacity": "m2_capacity_envelope.py", "priced": "m2_priced_surface.py"}

files = sorted(glob.glob("custom_components/heatpump_optimizer/*.py"))
counts = {}
law_impl = 0
for f in files:
    s = open(f, encoding="utf-8").read()
    law = len(LAW.findall(s)) + (len(DERATE.findall(s)) if os.path.basename(f) in ("thermal_model.py", "defrost.py") else 0)
    cap, pri, calls = len(CAP.findall(s)), len(PRICED.findall(s)), len(CALLS.findall(s))
    kinds = [k for k, n in (("law", law), ("capacity", cap), ("priced", pri)) if n]
    cls = "+".join(kinds) if kinds else ("consumer" if calls else "none")
    if law and LAW.search(s):
        law_impl += 1
    counts[cls] = counts.get(cls, 0) + 1
    via = ",".join(HARNESS[k] for k in kinds) or ("inherits law identities" if calls else "-")
    print(f"FILE {f}\tclass={cls}\tlaw={law}\tcap={cap}\tpriced={pri}\tcalls={calls}\tvia={via}")
C.result("files", len(files), "count")
C.result("law_impl_files", law_impl, "count")
for k, v in sorted(counts.items()):
    C.result(f"class.{k}", v, "count")
C.trailer()
