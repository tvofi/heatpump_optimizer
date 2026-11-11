#!/usr/bin/env python3
"""Fix seat #930's re-derivation harness for D3-S1 (non-wrapping month ranges).

The committed d3_own_S1.py is the panel's record and stays as written; this is
the same harness mechanism re-anchored for the fix seat, with exactly two
adaptations, both deliberate:

1. LINE 106 -> 113. #967 (764405d) and #968 (b9f31c5) added lines above the
   guard after the audit baseline 7dd68dd. d3_own_common's mutant() asserts
   the stripped line CONTENT, so a wrong anchor hard-fails rather than
   mutating something else; at 67499b1 `if start <= end:` (parse_month_range)
   is line 113. Any future run re-verifies the anchor by that assertion.
2. The probe adds a catalog round-trip arm -- every SWEDEN_CATALOG row parses
   whole and apply_catalog writes the row's own rules string back -- as the
   null control the fix must not disturb (#968 pins it byte-identical).

EXPECTED at the audit merge base 67499b1 (before the fix; executed by the fix
seat with a byte-identical mechanism): the probe returns Mar-Sep = 7 months
base vs 12 under the mutant, Nov-Mar unchanged, catalog writeback true in both
arms, and killed_by=none -- features.py, entities.py and config_flow_steps.py
all rc=0/failed=0 under the mutant. At the fix head: killed_by=tests/features.py
(rc 0->1, failed 0->3, exactly the three new #930 checks), everything else
identical, catalog writeback still true in both arms.

RUN (from a worktree root of this branch; mutates ONLY the scratch worktree
../audit-r4-verify-D3-1-scratch, restored and SHA-256-verified):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/d3_own_S1_fix930.py

BASELINE: merge base 67499b1 (unfixed) and fix head, both executed by the fix
seat; the header EXPECTED values above are keyed to those two SHAs.
MACHINE: 8-core Apple M1, macOS 25.6.0, python 3.11, threads pinned to 1.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tools/audit/round4/D3")
from d3_own_common import (arms, ensure_scratch, heavy_neighbours, load1,
                           swapins, thread_factor)

REL = "custom_components/heatpump_optimizer/grid_fee.py"
LINE, OLD, NEW = 113, "if start <= end:", "if False:"

PROBE = r"""
import json
from custom_components.heatpump_optimizer import grid_fee as gf
catalog = {}
for key, row in gf.SWEDEN_CATALOG.items():
    applied = gf.apply_catalog(key)
    catalog[key] = {
        "rules_len": len(gf.parse_rules(row["grid_fee_rules"])),
        "writeback_ok": bool(
            applied is not None
            and applied[gf.CONF_GRID_FEE_RULES] == row["grid_fee_rules"]
        ),
    }
print(json.dumps({
    "Mar-Sep": sorted(gf.parse_month_range("Mar-Sep")),
    "Nov-Mar": sorted(gf.parse_month_range("Nov-Mar")),
    "Jul":     sorted(gf.parse_month_range("Jul")),
    "catalog": catalog,
}))
"""


def main() -> int:
    print(f"D3-S1 fix-930 re-derivation — mutant {REL}:{LINE} {OLD!r} -> {NEW!r}")
    print(f"heavy neighbours (stress.py/run.sh procs): {heavy_neighbours()}")
    ensure_scratch()  # baseline() reads SCRATCH before run_driver() creates it
    out = arms(
        REL, LINE, OLD, NEW,
        scripts=["tests/features.py", "tests/entities.py",
                 "tests/config_flow_steps.py"],
        finding="S1",
        probes={"code": PROBE},
    )
    b = out["probes"]["base"]["value"]
    m = out["probes"]["mut"]["value"]
    n_mar_sep_base = len(b["Mar-Sep"])
    n_mar_sep_mut = len(m["Mar-Sep"])
    for script, rec in out["scripts"].items():
        base, mut = rec["base"], rec["mut"]
        if mut is None:
            print(f"RESULT S1_{script.replace('/', '_')}_verdict=void")
            continue
        print(f"RESULT S1_{script.replace('/', '_')}_rc={base['rc']}->{mut['rc']} delta_rc")
        print(f"RESULT S1_{script.replace('/', '_')}_failed={base['failed']}->{mut['failed']} count")
    print(f"RESULT S1_mar_sep_months_base={n_mar_sep_base} months")
    print(f"RESULT S1_mar_sep_months_mut={n_mar_sep_mut} months")
    print(f"RESULT S1_nov_mar_unchanged={b['Nov-Mar'] == m['Nov-Mar']} bool")
    print(f"RESULT S1_catalog_writeback_base={all(r['writeback_ok'] and r['rules_len'] >= 1 for r in b['catalog'].values())} bool")
    print(f"RESULT S1_catalog_writeback_mut={all(r['writeback_ok'] and r['rules_len'] >= 1 for r in m['catalog'].values())} bool")
    print(f"RESULT S1_killed_by={out['killed_by'] or 'none'} script")
    print(f"RESULT thread_factor={thread_factor()}")
    print(f"RESULT load1={load1():.2f}")
    print(f"RESULT swapins={swapins()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
