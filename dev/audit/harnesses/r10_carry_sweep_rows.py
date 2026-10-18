#!/usr/bin/env python3
"""Round-10 carry sweep: which recorded findings carry_audit.py refuses (O11's instrument).

Written by the O11 fixer (carry-forward enforcement). Two measurements, both over
the PR text GitHub holds, through tools/audit/carry_audit.py's own
audit:

  rows39   the finding sweep's UNCARRIED rows that live in PR text (33 of its 39;
           the other six are ledger-only L14-L16, issues L20/L21 and roster
           drift L18, which carry_audit.py sweep --issues and two
           --roster-ref read). A row is CAUGHT when a finding item of one of
           its pull requests contains its key text.
  last20   the null control: the last 20 merged non-record pull requests at
           2026-10-18, every finding item set against the sweep rows from those
           pull requests (all statuses). Prints the rows hit and missed and
           every hit on no row, so the comparison is of sets, not totals.

A row's key is a regex over the item text; the sweep's REPORT.md lists P23 under
#2316, but its text is in #2320's body, which is where this keys it. The sweep's
rows are a snapshot (origin/main 64b1f82a3): re-derive the rows, never carry the
figures. Run from a worktree root; --from-dir D reads D/bodies/<n>.md
and D/comments/<n>.json instead of gh api:

    python3 dev/audit/harnesses/r10_carry_sweep_rows.py rows39 [--from-dir D]
    python3 dev/audit/harnesses/r10_carry_sweep_rows.py last20 [--from-dir D]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "audit"))
import carry_audit as ca  # noqa: E402

# (row, pull requests, key regex)
ROWS39 = [
    ('L02', '2345', 'dom_stub'),
    ('L03', '2366', 'agreement lane reads the branch'),
    ('L04', '2360', 'started_at|2 \\* med|twice'),
    ('L05', '2341', 'recorded rather than propagated'),
    ('P02', '2281', 'RosterNotFound'),
    ('P05', '2282', 're-books'),
    ('P06', '2282', 'inspect'),
    ('P07', '2282', 'calibration pin'),
    ('P08', '2283', 'openSetupSlot`?, is unpinned'),
    ('P12', '2284', 'non-kernel'),
    ('P13', '2285,2365', '_bounded|_plateau_aware_day_max|catch-?up'),
    ('P16', '2305', 'pinned by .?mutation-autofix'),
    ('P18', '2311', 'under-fire'),
    ('P19', '2311', 'C15 and C16'),
    ('P23', '2320', 'handoff_push'),
    ('P28', '2323', 'isinstance\\(e, dict\\)'),
    ('P33', '2336', 'float \\| None'),
    ('P35', '2340', 'rule A'),
    ('P37', '2341', 'line cap of 61'),
    ('P38', '2344', 'one-shot driver'),
    ('P40', '2346', 'committed figure'),
    ('P41', '2346', 'placeLabel'),
    ('P45', '2347', 'displace_schedule index|claim file'),
    ('P46', '2347', 'max_class_loc|docstring line'),
    ('P48', '2351', 'hass=None'),
    ('P51', '2366', 'wip-sync'),
    ('P52', '2368', 'may-drift'),
    ('P54', '2373', 'sys\\.path\\.insert'),
    ('P55', '2373', 'step 3f'),
    ('P56', '2373', '--only'),
    ('P57', '2375', 'exit code|exit 1'),
    ('P61', '2339', 'next week'),
    ('F-POL', '2345,2347,2365,2366,2368,2373,2374', 'harness_headers|dev/audit/harnesses'),
]
LAST20 = [2351, 2376, 2345, 2371, 2380, 2366, 2377, 2374, 2360, 2356,
          2347, 2320, 2346, 2352, 2349, 2344, 2340, 2348, 2342, 2341]
ROWS20 = [
    ('L02', '2345', 'dom_stub'),
    ('L03', '2366', 'agreement lane reads the branch'),
    ('L04', '2360', '2x threshold|started_at'),
    ('L05', '2341', 'recorded rather than propagated'),
    ('L06', '2371', 'private_cross_module.{0,40}rename|pure private'),
    ('L08', '2374', 'd15_restart_gaps'),
    ('L09', '2376', 'line 1741'),
    ('L10', '2376', 'section 5 holds'),
    ('L12', '2376', 'predictor still prints|route line says|Not blocking. It is message text'),
    ('P11', '2345', "R10-DEEPLINK-HANDLERS's brief|census's refusals"),
    ('P24', '2320', 'C19 is defeated|Private crossings outside|GOOD case .a3_private'),
    ('P25', '2320', 'TYPE_CHECKING exclusion'),
    ('P26', '2320', 'R10-CONFIGFLOW-PAGES'),
    ('P27', '2320', 'Two residual body errors'),
    ('P34', '2340', 'dead_members|R10-ARCHSCORE-COVERAGE. \\('),
    ('P35', '2340', 'rule A'),
    ('P36', '2341', '#2267'),
    ('P37', '2341', 'line cap of 61'),
    ('P38', '2344', 'one-shot|step 3 requires re-executing'),
    ('P39', '2344', 'attribute-bound'),
    ('P40', '2346', 'committed page figures'),
    ('P41', '2346', 'placeLabel'),
    ('P42', '2346', 'finite_inline'),
    ('P43', '2346', 'dead-definition'),
    ('P44', '2347', 'envelope-score|R10-SCORES'),
    ('P45', '2347', 'owed to the record'),
    ('P46', '2347', 'max_class_loc'),
    ('P47', '2349', 'composed-proof|coverage-ratchet'),
    ('P48', '2351', 'hass=None|flow-unit clearing'),
    ('P49', '2351', 'forget_held call in async_shutdown'),
    ('P51', '2366', 'wip-sync'),
    ('P53', '2371', 'REASON_IDLE|reviewer M7'),
    ('P69', '2371', 'utc_shift'),
    ('P71', '2380', 'D8-s1-01'),
    ('F-POL', '2374,2345,2347,2366', 'harness_headers|step 18|fixer.md: cost: three review rounds|fixer.md: unenforced: round 1'),
]


def hits_of(prs, from_dir, dests, cache={}):
    for n in prs:
        if n not in cache:
            body, com = ca.read_pr(n, ca.REPO, from_dir)
            cache[n] = ca.audit(body, com, dests)["rows"]
    return cache


def main(argv):
    mode = argv[0] if argv else "rows39"
    from_dir = argv[argv.index("--from-dir") + 1] if "--from-dir" in argv else None
    dests = ca.load_dests(ROOT, "origin/main")
    table = ROWS39 if mode == "rows39" else ROWS20
    prs = sorted({int(x) for _, p, _ in table for x in p.split(",")} | (set(LAST20) if mode == "last20" else set()))
    cache = hits_of(prs, from_dir, dests)
    hit = {}
    for rid, p, rx in table:
        for n in [int(x) for x in p.split(",")]:
            for r in cache[n]:
                if re.search(rx, r["text"], re.I | re.S):
                    hit.setdefault(rid, (n, r["where"], r["id"]))
                    r.setdefault("row", rid)
    for rid, _, _ in table:
        print(f"{rid}	{'CAUGHT' if rid in hit else 'missed'}	{hit.get(rid, '')}")
    print(f"RESULT rows_caught={len(hit)} of={len(table)}")
    if mode == "last20":
        allhits = [(n, r) for n in LAST20 for r in cache[n]]
        extra = [(n, r) for n, r in allhits if "row" not in r]
        for n, r in extra:
            print(f"EXTRA #{n} {r['where']} item {r['id']} [{r['why']}]: {re.sub(r'\s+', ' ', r['text'])[:110]}")
        print(f"RESULT last20_hits={len(allhits)} on_a_row={len(allhits) - len(extra)} on_no_row={len(extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
