#!/usr/bin/env python3
"""Prototype countermeasure for N-name-sort (RCA-BULK-4 section 5).

One declared family per entity, one generic check. The declaration is the
translation_key's lead token (what entity_id is already built from) plus an
explicit OVERRIDES map -- in production this map would live beside the
keys (const.py), so moving an entity between families is a visible edit to
one table, not a silent edit to a test's hand-list. ALLOW names the
families the owner has accepted as split (today: never decided; the two
live splits are listed so the demonstration isolates each instance).

Check: every declared family with >= 2 members is ONE contiguous run in
the en and sv name sorts over the whole roster. Anchors refuse a vacuous
pass (empty roster, no families).

  family_check.py <sha|WORKTREE> [--overrides r9] [--allow a,b] [--null]
exit 0 PASS, 1 FAIL
"""
from __future__ import annotations

import sys

from name_sort_families import load, runs, sort_key

OVERRIDE_SETS = {
    "none": {},
    # The declaration #1733 would have had to write (the families it fixed).
    "r9": {
        ("button", "diagnose_last_interval"): "prediction",
        ("sensor", "cost_total_heating"): "lifetime",
        ("sensor", "space_heating_cost"): "lifetime",
        ("sensor", "space_heating_energy"): "lifetime",
        ("sensor", "total_energy"): "lifetime",
    },
}


def main(argv):
    sha = argv[1]
    ov = OVERRIDE_SETS[argv[argv.index("--overrides") + 1]] if "--overrides" in argv else {}
    allow = set(argv[argv.index("--allow") + 1].split(",")) if "--allow" in argv else set()
    en, sv = load(sha, "en"), load(sha, "sv")
    rows = [(p, k, b["name"], sv.get(p, {}).get(k, {}).get("name", "~" + k))
            for p, e in en.items() for k, b in e.items()]
    if "--null" in argv:  # every name led by its declared family -> all contiguous
        lead = lambda p, k: ov.get((p, k), k.split("_")[0])
        rows = [(p, k, f"{lead(p, k)} {k}", f"{lead(p, k)} {k}") for p, k, _e, _s in rows]
    fam: dict[str, set] = {}
    for p, k, _e, _s in rows:
        fam.setdefault(ov.get((p, k), k.split("_")[0]), set()).add((p, k))
    fam = {t: m for t, m in fam.items() if len(m) >= 2}
    bad = []
    if len(rows) < 60 or len(fam) < 10:
        bad.append(f"ANCHOR roster={len(rows)} families={len(fam)}")
    for lang, idx in (("en", 2), ("sv", 3)):
        order = [(p, k) for p, k, *_ in sorted(rows, key=lambda r: sort_key(lang)(r[idx]))]
        for t, m in sorted(fam.items()):
            r = runs(order, m)
            if r > 1 and t not in allow:
                names = sorted(row[idx] for row in rows if (row[0], row[1]) in m)
                bad.append(f"{lang} {t!r} {r} runs: {names}")
    for b in bad:
        print("  FAIL", b)
    print(f"{sha}: {'FAIL' if bad else 'PASS'} ({len(rows)} names, {len(fam)} families, "
          f"overrides={len(ov)}, allow={sorted(allow)})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
