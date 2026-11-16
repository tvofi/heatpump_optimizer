#!/usr/bin/env python3
"""D5.M3 settings-table harness: the Default column of docs/configuration.md's options-page
tables against the default the options flow actually offers.

Metric: table rows of docs/configuration.md under "## Changing settings later" whose Setting cell
equals an options-flow field's English label (translations/en.json options.step.<page> data and
sections), and of those, the rows whose stated default (first number, or on/off) differs from
config_flow._OPTION_FIELDS' `default` for that field. Rows whose Default cell is not a literal
(the setup value, none, empty, a time list) are counted as not comparable.
Key: the default the production registry holds (config_flow:_OPTION_FIELDS[i].default), never
the doc's number.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/defaults_table.py [--perturb KEY=VALUE ...]
  --perturb KEY=VALUE  the registry default of KEY replaced in memory (e.g.
                       dhw_legionella_interval_days=7): the matching row's mismatch moves to zero.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: the RESULT lines, exact (counts).
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, sys, time
from pathlib import Path

sys.path.insert(0, "custom_components")
import heatpump_optimizer.config_flow as cf  # noqa: E402

EN = json.loads(Path("custom_components/heatpump_optimizer/translations/en.json").read_text())


def label_map():
    out = {}
    for step, s in EN["options"]["step"].items():
        data = dict(s.get("data", {}))
        for sec in s.get("sections", {}).values():
            data.update(sec.get("data", {}))
        for k, v in data.items():
            out.setdefault(v.strip().lower(), []).append((step, k))
    return out


def main():
    pert = {}
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--perturb":
            k, _, v = args[i + 1].partition("=")
            pert[k] = v
    fields = {(f.step, f.key): f.default for f in cf._OPTION_FIELDS}
    for (st, k) in list(fields):
        if k in pert:
            fields[(st, k)] = type(fields[(st, k)])(pert[k]) if not isinstance(fields[(st, k)], bool) else pert[k] == "True"
    labels = label_map()
    text = Path("docs/configuration.md").read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(text) if l.startswith("## Changing settings later"))
    end = next(i for i, l in enumerate(text) if l.startswith("## The hydronic layout catalog"))
    rows = matched = comparable = ranged = 0
    bad, rbad = [], []
    widgets = {(f.step, f.key): f.widget for f in cf._OPTION_FIELDS}
    for n in range(start, end):
        l = text[n]
        if not l.startswith("|") or l.startswith("|---"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("Setting", "Page", "First menu", "Advanced settings"):
            continue
        rows += 1
        hits = labels.get(re.sub(r"\s*\([^)]*\)$", "", cells[0]).strip().lower()) or labels.get(cells[0].lower())
        if not hits:
            continue
        cands = [(st, k) for st, k in hits if (st, k) in fields]
        if not cands:
            continue
        matched += 1
        widget = widgets.get(cands[0])
        cfg = getattr(widget, "config", None) or {}
        rm = re.match(r"^(-?\d+(?:\.\d+)?)\s*[–-]\s*(-?\d+(?:\.\d+)?)", re.sub(r"(?<=\d)[   ](?=\d{3})", "", cells[2])) if len(cells) > 3 else None
        if rm and "min" in cfg and "max" in cfg:
            ranged += 1
            if (float(rm.group(1)), float(rm.group(2))) != (float(cfg["min"]), float(cfg["max"])):
                rbad.append(f"docs/configuration.md:{n + 1} {cells[0]!r}: doc range {cells[2]!r} vs {cands[0][1]} selector {cfg['min']}..{cfg['max']}")
        dflt = cells[1]
        code = fields[cands[0]]
        if isinstance(code, bool):
            if dflt.lower() not in ("on", "off"):
                continue
            stated = dflt.lower() == "on"
        else:
            m = re.match(r"^`?(-?\d+(?:\.\d+)?)", re.sub(r"(?<=\d)[ \u202f\u00a0](?=\d{3})", "", dflt))
            if not m or not isinstance(code, (int, float)):
                continue
            stated = float(m.group(1))
        comparable += 1
        same = (stated == code) if isinstance(code, bool) else abs(stated - float(code)) < 1e-9
        if not same:
            bad.append(f"docs/configuration.md:{n + 1} {cells[0]!r}: doc {dflt!r} vs {cands[0][0]}.{cands[0][1]} default {code!r}")
    print(f"RESULT table_rows={rows} rows")
    print(f"RESULT rows_matched_to_field={matched} rows")
    print(f"RESULT rows_comparable={comparable} rows")
    print(f"RESULT default_mismatches={len(bad)} rows")
    for b in bad:
        print(f"   BAD {b}")
    print(f"RESULT rows_with_range={ranged} rows")
    print(f"RESULT range_mismatches={len(rbad)} rows")
    for b in rbad:
        print(f"   RANGE {b}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
