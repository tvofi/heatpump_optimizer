#!/usr/bin/env python3
"""R10-ORCH-PLANPAGE: each rule of the measured size model dies alone.

Each mutant is one exact one-occurrence replacement in
tools/plan/size_durations.py, the instrument that measures replan.py's
duration model from merged pull requests (replan.py's own model, admission
and priority mutants live in its self-test's mutation table). The driver
applies one, runs `size_durations.py --self-test`, restores the file byte
for byte, and refuses to start on a file with uncommitted edits. Metric, one
line per mutant:

  RESULT mutant=<name> rc=<rc> fails=<n> verdict=killed|SURVIVED|CRASHED

then the FAIL lines. A mutant that kills only by crashing (no FAIL line) is
CRASHED, not killed. Null control: M0, nothing replaced, must print rc=0
fails=0; a replacement whose text is not found exactly once aborts.

    python3 dev/audit/harnesses/r10_plan_durations_mutants.py [NAME ...]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
SIZES = "tools/plan/size_durations.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill and refuses a leftover mutant

MUTANTS = [
    ("M0", None, None),
    ("shared-branch-maps", "        if SHARED_BRANCH.search(p[\"head_ref\"]):\n            continue",
     "        if False:\n            continue"),
    ("roster-pointer", "        out[g] |= {n for n in nums if n in by_num}", "        pass"),
    ("merge-commit-pointer",
     "            out[g] |= {p[\"number\"] for p in prs if p[\"merge_commit\"].startswith(commit[:12])}",
     "            pass"),
    ("verdict-dedupe", "        if m and (m.group(1), m.group(2)[:7]) not in seen:", "        if m:"),
    ("dispatch-stamp-start", "        start, src = min(starts + [(s, \"dispatched\") for s in stamps])",
     "        start, src = min(starts)"),
    ("active-not-span", "            \"hours\": active_hours(spans),",
     "            \"hours\": round((finish - start).total_seconds() / 3600.0, 2),"),
    ("not-answered", "            if NOT_ANSWERED.search(sentence) or forward and not ANSWERED.search(sentence):",
     "            if forward and not ANSWERED.search(sentence):"),
    ("forward-needs-done", "            if NOT_ANSWERED.search(sentence) or forward and not ANSWERED.search(sentence):",
     "            if NOT_ANSWERED.search(sentence):"),
    ("percentile-linear", "    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)", "    return xs[lo]"),
    ("theil-sen", "    return round(max(0.0, pctl(slopes, 50)), 2) if slopes else 0.0",
     "    return round(max(0.0, sum(slopes) / len(slopes)), 2) if slopes else 0.0"),
    ("rounds-priced-out",
     "    adj = [dict(r, hours=max(0.0, r[\"hours\"] - slope * (r[\"rounds\"] - 1))) for r in rows]",
     "    adj = list(rows)"),
    ("min-cell", "                 if sum(1 for r in rs if r[\"class\"] == c) >= MIN_CELL}",
     "                 if sum(1 for r in rs if r[\"class\"] == c) >= 1}"),
    ("monotone-lift", "        if prev is not None and h < prev[1]:", "        if False:"),
    ("part-capacity-p90",
     "    hours, per = round(pctl([p[\"hours\"] for p in parts], percentile), 1), round(pctl(citing, 90), 1)",
     "    hours, per = round(pctl([p[\"hours\"] for p in parts], percentile), 1), round(pctl(citing, 50), 1)"),
    ("held-open-index", "        open_ = [i for i in range(1, len(carry) + 1) if i not in cited]",
     "        open_ = list(range(1, len(carry) + 1))"),
    ("future-groups-only",
     "            and (e.get(\"resume\") or {}).get(\"stage\") != \"carries-open\"}", "}"),
    ("boilerplate", "            boiler = len(seen.get(key, ())) >= 3", "            boiler = False"),
    ("pnums-subset", "                    if (pnums and pnums <= set(P_NUMBER.findall(other))) or (",
     "                    if (pnums and pnums & set(P_NUMBER.findall(other))) or ("),
    ("forward-overlap",
     "                                _words(carry[i - 1][:400]) & _words(item)) >= FORWARD_OVERLAP:",
     "                                _words(carry[i - 1][:400]) & _words(item)) >= 0:"),
]


def main(argv: list[str]) -> int:
    want = set(argv)
    mutant_guard.arm([SIZES])
    survived = 0
    path = ROOT / SIZES
    for name, old, new in MUTANTS:
        if want and name not in want:
            continue
        orig = path.read_bytes()
        try:
            if old is not None:
                text = orig.decode()
                if text.count(old) != 1:
                    print(f"abort: {name}: {old!r} occurs {text.count(old)} times in {SIZES}")
                    return 2
                path.write_text(text.replace(old, new), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(path), "--self-test"],
                               capture_output=True, text=True)
        finally:
            path.write_bytes(orig)
        fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
        if name == "M0":
            verdict = "null" if r.returncode == 0 and not fails else "SURVIVED"
        elif fails and r.returncode:
            verdict = "killed"
        elif r.returncode:
            verdict = "CRASHED"
        else:
            verdict = "SURVIVED"
        survived += verdict in ("SURVIVED", "CRASHED")
        print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)} verdict={verdict}")
        for ln in fails:
            print("   ", ln)
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
