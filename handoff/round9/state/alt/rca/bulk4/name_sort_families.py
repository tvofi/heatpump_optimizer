#!/usr/bin/env python3
"""N-name-sort enumerator (RCA-BULK-4).

Metric (one line): over every entity name the shipped catalogue publishes
(translations/{en,sv}.json -> entity.<platform>.<translation_key>.name, all
platforms in one list, the way the entity registry's default view sorts),
count the families whose members do NOT form one contiguous run in the
name sort.

Family definitions (all derived, none hand-listed):
  KEY   -- first underscore token of the translation_key, >= 2 members,
           across platforms.  The translation_key is the one in-code family
           declaration: entity_id = <platform>.heat_pump_optimizer_<key>
           (sensor.py:304, binary_sensor.py:82, button.py:77) and #1227 /
           #1333 renamed keys precisely so that a family shares this token.
  TRAIL -- last word of the English name (the #797 "trailing noun" partition,
           reference only: the owner declined renames for it at #797).

Sort keys: en = casefold(); sv = casefold() with the Swedish alphabet tail
(a-ring < a-umlaut < o-umlaut after z), approximating Intl.Collator('sv').

Usage:
  name_sort_families.py <git-sha|WORKTREE> [--null] [--perturb NAME=>NEW]
    --null     : replace every name by its translation_key (all KEY families
                 contiguous by construction) -> must print 0
    --perturb  : rename one English and Swedish member in memory
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2] / "main"
CAT = "custom_components/heatpump_optimizer/translations/{}.json"

SV_TAIL = str.maketrans({"å": "z\u0001", "ä": "z\u0002", "ö": "z\u0003"})


def load(sha: str, lang: str) -> dict:
    if sha == "WORKTREE":
        return json.loads((REPO / CAT.format(lang)).read_text())["entity"]
    out = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{sha}:{CAT.format(lang)}"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)["entity"]


def sort_key(lang: str):
    if lang == "sv":
        return lambda n: n.casefold().translate(SV_TAIL)
    return lambda n: n.casefold()


def runs(order: list, members: set) -> int:
    pos = [i for i, row in enumerate(order) if row in members]
    if len(pos) < 2:
        return 0
    return 1 + sum(1 for a, b in zip(pos, pos[1:]) if b != a + 1)


def families(rows, how):
    fam: dict[str, set] = {}
    for plat, key, en, _sv in rows:
        tok = key.split("_")[0] if how == "KEY" else en.split()[-1].strip("()").casefold()
        fam.setdefault(tok, set()).add((plat, key))
    return {k: v for k, v in fam.items() if len(v) >= 2}


def measure(rows, how, lang, verbose=True):
    idx = 2 if lang == "en" else 3
    order = [(p, k) for p, k, *_ in sorted(rows, key=lambda r: sort_key(lang)(r[idx]))]
    split = []
    for tok, members in sorted(families(rows, how).items()):
        r = runs(order, members)
        if r > 1:
            names = sorted(row[idx] for row in rows if (row[0], row[1]) in members)
            split.append((tok, r, len(members), names))
    if verbose:
        for tok, r, n, names in split:
            print(f"  SPLIT {how}/{lang} {tok!r}: {n} members in {r} runs: {names}")
    return len(split), sum(r - 1 for _, r, _, _ in split)


def main(argv):
    sha = argv[1]
    en, sv = load(sha, "en"), load(sha, "sv")
    rows = [
        (plat, key, body["name"], sv.get(plat, {}).get(key, {}).get("name", "~" + key))
        for plat, ents in en.items() for key, body in ents.items()
    ]
    if "--null" in argv:
        rows = [(p, k, k, k) for p, k, _e, _s in rows]
    if "--perturb" in argv:
        old, new = argv[argv.index("--perturb") + 1].split("=>")
        rows = [(p, k, new if e == old else e, s) for p, k, e, s in rows]
    print(f"# {sha}: {len(rows)} published entity names")
    for how in ("KEY", "TRAIL"):
        for lang in ("en", "sv"):
            fams, extra = measure(rows, how, lang, verbose=(how == "KEY"))
            nf = len(families(rows, how))
            print(f"RESULT {how.lower()}_families_split_{lang}={fams} "
                  f"(of {nf} families; extra_runs={extra})")


if __name__ == "__main__":
    main(sys.argv)
