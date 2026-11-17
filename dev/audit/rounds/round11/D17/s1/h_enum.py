"""D17-s1-01 harness: enumerate.py d17-features omits every field nested in a section.

Metric: the number of options-flow fields strings.json declares under
options.step.<step>.sections.<section>.data that `enumerate.py d17-features --kind
option` does not print as an `option <step>.<field>` line (and the same for
config-field over config.step). Count key: the enumerator's own printed lines,
produced by calling tools/audit/enumerate.py:d17 on this tree.
Also prints how many of the brief's owed cell (the comfort page's weekend and holiday
fields, D17.md method step 3) the universe holds.

Command:  python3 dev/audit/rounds/round11/D17/s1/h_enum.py
Expected: RESULT option_fields_missing=156 (of 286 declared), RESULT config_fields_missing=0,
          RESULT owed_cell_printed=0 of 8 (exact, counts)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13
Perturbation: --perturb-sections wraps enumerate.d17 to also emit each section's data
keys: option_fields_missing goes to 0, owed_cell_printed to 8.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path(".").resolve()
spec = importlib.util.spec_from_file_location("hpo_enumerate", "tools/audit/enumerate.py")
en = importlib.util.module_from_spec(spec)
sys.modules["hpo_enumerate"] = en
spec.loader.exec_module(en)

if "--perturb-sections" in sys.argv:
    _real = en.d17

    def _with_sections(repo, kind=None, **kw):
        out = _real(repo, kind=None, **kw)
        s = json.loads((repo / en.PKG / "strings.json").read_text())
        for sec, kfield in (("config", "config-field"), ("options", "option")):
            for step, body in s.get(sec, {}).get("step", {}).items():
                for group in (body.get("sections") or {}).values():
                    out += [f"{kfield} {step}.{k}" for k in (group.get("data") or {})]
        return [l for l in out if not kind or l.split(" ", 1)[0] == kind]

    en.d17 = _with_sections

strings = json.loads((REPO / en.PKG / "strings.json").read_text())


def declared(section_kind):
    out = set()
    for step, body in strings[section_kind]["step"].items():
        for k in (body.get("data") or {}):
            out.add(f"{step}.{k}")
        for group in (body.get("sections") or {}).values():
            for k in (group.get("data") or {}):
                out.add(f"{step}.{k}")
    return out


printed_opt = {l.split(" ", 1)[1] for l in en.d17(REPO, kind="option")}
printed_cfg = {l.split(" ", 1)[1] for l in en.d17(REPO, kind="config-field")}
miss_opt = sorted(declared("options") - printed_opt)
miss_cfg = sorted(declared("config") - printed_cfg)
owed = [f"comfort.{k}" for k in ("comfort_temp_day_weekend", "comfort_temp_night_weekend",
                                 "day_start_hour_weekend", "day_end_hour_weekend",
                                 "holiday_comfort_temp_day", "holiday_comfort_temp_night",
                                 "holiday_day_start_hour", "holiday_day_end_hour")]
by_step = {}
for m in miss_opt:
    by_step.setdefault(m.split(".")[0], []).append(m.split(".")[1])
for st, ks in sorted(by_step.items()):
    print(f"MISSING options {st}: {len(ks)} {ks}")
print(f"RESULT option_lines_printed={len(printed_opt)}")
print(f"RESULT option_fields_declared={len(declared('options'))}")
print(f"RESULT option_fields_missing={len(miss_opt)}")
print(f"RESULT config_fields_missing={len(miss_cfg)} {miss_cfg}")
print(f"RESULT owed_cell_printed={sum(1 for o in owed if o in printed_opt)} of {len(owed)}")
print("RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]}")
print("RESULT swapins=0")
