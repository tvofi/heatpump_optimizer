#!/usr/bin/env python3
"""Turn the pre-screen log into the D3 prescreened table and its two counts.

Metric definition: a script KILLS a mutant when its own verdict moves -- the
exit code differs from the same slot's unmutated run, a traceback appears, or
the reporter's summary line ("N of M ... CHECKS FAILED") reports a different
N.  A changed FAIL *detail* string is NOT a kill: tests/entities.py and
tests/features.py print `FAIL <name> [detail]` for their own deliberate
negative arms too, so a detail that moved is the arm reporting, not the gate
failing.

Run (from the repository root):

    python3 tools/audit/round3/D3/verdicts.py \
        tools/audit/round3/D3/prescreened.json

Writes tools/audit/round3/D3/PRESCREENED.md and prints the two counts.
Baseline SHA: ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SUMMARY = re.compile(r"(\d+) of (\d+) [A-Z ]+ FAILED")
ALLPASS = re.compile(r"ALL (\d+) [A-Z ]+ PASSED")
#: The two scripts that are not green on an unmutated SLOT.  A slot is a copy
#: with a fresh `git init` and no commit, so two git-dependent checks fail
#: there and only there:
#:   tests/entities.py   docs/HANDOVER.md's `updated-for:` commit is not an
#:                       ancestor of the slot's HEAD -- "1 of 1294 ENTITY
#:                       CHECKS FAILED", measured on all five tier-1 slots.
#:   tests/features.py   "the path that proceeds still stamps a resolvable
#:                       recorded_at (#363)" reads `unknown` -- "1 of 2136
#:                       FEATURE CHECKS FAILED", measured on all six tier-2
#:                       slots.
#: Both are counted, not name-matched, so a mutant that adds a failure still
#: moves the number.
SLOT_BASELINE_FAILED = {"tests/entities.py": 1, "tests/features.py": 1}


def summary_failed(tail: str) -> int | None:
    m = SUMMARY.search(tail)
    if m:
        return int(m.group(1))
    if ALLPASS.search(tail):
        return 0
    return None


def strict_kill(script: str, r: dict) -> tuple[bool, str]:
    base_rc = r.get("baseline_rc", 0)
    if r["rc"] != base_rc:
        return True, f"rc {base_rc} -> {r['rc']}"
    tail = r.get("tail", "") or ""
    if r.get("has_traceback") or "Traceback (most recent call last)" in tail:
        return True, "traceback"
    n = summary_failed(r.get("summary_line") or tail)
    if n is not None and n != SLOT_BASELINE_FAILED.get(script, 0):
        return True, f"{n} check(s) failed (baseline {SLOT_BASELINE_FAILED.get(script,0)})"
    if script.startswith("tests/env_drift.py") and r["rc"] != 0:
        return True, "golden payload moved"
    return False, ""


def main() -> int:
    data = json.loads(Path(sys.argv[1]).read_text())
    rows = data["prescreened"]
    out = []
    strict_survivors, loose_survivors = [], []
    for r in rows:
        killers, why = [], {}
        for x in r.get("ran", []):
            s = x["script"]
            k, reason = strict_kill(s, x)
            if k:
                killers.append(s)
                why[s] = reason
        r["strict_killed_by"] = killers
        r["strict_why"] = why
        r["strict_status"] = "KILLED" if killers else "SURVIVOR"
        if not killers:
            strict_survivors.append(r["id"])
        if r["status"] == "SURVIVOR":
            loose_survivors.append(r["id"])
        out.append(r)

    print(f"RESULT mutants_screened={len(rows)} mutants")
    print(f"RESULT survivors_strict={len(strict_survivors)} mutants "
          f"({','.join(strict_survivors)})")
    print(f"RESULT survivors_loose={len(loose_survivors)} mutants "
          f"({','.join(loose_survivors)})")
    drift_only = [r["id"] for r in out
                  if r["strict_status"] == "KILLED"
                  and r["strict_killed_by"] == ["tests/env_drift.py --all"]]
    print(f"RESULT killed_only_by_differential_gate={len(drift_only)} mutants "
          f"({','.join(drift_only)})")

    # Which scripts kill the same mutants: duplicated coverage.
    kills: dict[str, set[str]] = {}
    for r in out:
        for s in r["strict_killed_by"]:
            kills.setdefault(s, set()).add(r["id"])
    print("RESULT killers_by_script=" + json.dumps(
        {s: len(v) for s, v in sorted(kills.items())}))
    scripts = sorted(kills)
    for i, a in enumerate(scripts):
        for b in scripts[i + 1:]:
            inter = kills[a] & kills[b]
            if inter:
                print(f"  overlap {a} & {b}: {len(inter)} "
                      f"({len(inter)}/{len(kills[a])} of {a})")

    # Scripts a closure selected that no mutant in that module could move.
    sel_never: dict[str, set[str]] = {}
    for r in out:
        for x in r.get("ran", []):
            s = x["script"]
            sel_never.setdefault(s, set())
        for s in r.get("closure_scripts", []):
            sel_never.setdefault(s, set())
    for r in out:
        for s in r["strict_killed_by"]:
            sel_never[s].add(r["id"])
    ran_scripts = sorted({x["script"] for r in out for x in r.get("ran", [])})
    print("RESULT ran_but_never_killed=" + json.dumps(
        sorted(s for s in ran_scripts if not sel_never.get(s))))

    lines = ["# D3 round 3 — the prescreened table",
             "",
             f"Baseline `{data['baseline_sha']}`. "
             f"Seed 20260910, 34 mutants, <= 4 per module. "
             "A script kills a mutant when its own verdict moves (exit code, "
             "traceback, or its reporter's `N of M ... FAILED` count); a "
             "changed FAIL *detail* string is not a kill.",
             "",
             "| id | file:line | kind | patch (old -> new) | closure | scripts run | verdict |",
             "|---|---|---|---|---|---|---|"]
    for r in out:
        ran = ", ".join(f"`{x['script'].replace('tests/','')}`"
                        for x in r.get("ran", []))
        killers = ", ".join(f"`{s.replace('tests/','')}`"
                            for s in r["strict_killed_by"]) or "**nothing**"
        old = r["old"].strip().replace("|", "\\|")
        new = r["new"].strip().replace("|", "\\|")
        lines.append(
            f"| {r['id']} | `{r['file'].split('/')[-1]}:{r['line']}` | {r['kind']} "
            f"| `{old}` -> `{new}` | {len(r.get('closure_scripts', []))} scripts "
            f"| {ran} | {r['strict_status']}: killed by {killers} |")
    Path("tools/audit/round3/D3/PRESCREENED.md").write_text("\n".join(lines) + "\n")
    Path("tools/audit/round3/D3/prescreened_verdicts.json").write_text(
        json.dumps({"baseline_sha": data["baseline_sha"], "rows": out}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
