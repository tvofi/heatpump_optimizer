#!/usr/bin/env python3
"""R10-PLAN-ARTIFACT: each behaviour plan_page.py's self-test pins dies alone.

Each mutant is one exact one-occurrence replacement in
tools/audit/seat/plan_page.py, tools/plan/replan.py (the freshness rule the
page shares) or tools/audit/seat/state_docs.py (which publishes the page).
The driver applies one, runs `plan_page.py --self-test` (and the mutated
file's own `--self-test` too, and every one for M0), restores
the file byte for byte, and refuses to start on a file with uncommitted edits.
Metric, one line per mutant:

  RESULT mutant=<name> rc=<rc> fails=<n> verdict=killed|SURVIVED|CRASHED

then the FAIL lines. A mutant that kills only by crashing (no FAIL line) is
CRASHED, not killed. Null control: M0, nothing replaced, must print rc=0
fails=0; a replacement whose text is not found exactly once aborts.

    python3 dev/audit/harnesses/r10_plan_page_mutants.py [NAME ...]
"""
from __future__ import annotations

import re
import subprocess
import sys
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


ROOT = repo_root(__file__)
PAGE = "tools/audit/seat/plan_page.py"
PLAN = "tools/plan/replan.py"
STATE = "tools/audit/seat/state_docs.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant

MUTANTS = [
    ("M0", PAGE, None, None),
    ("live", PAGE, "elif _stage(entry) in replan.LIVE_STAGES:", "elif False:"),
    ("blocked", PAGE, "elif blk and not part:", "elif False:"),
    ("partial", PAGE, "if m and m.group(1) in G:", "if False:"),
    ("blocked-by-less-done", PAGE,
     "blk = [a for a in entry.get(\"after\") or [] if a in G and a not in done]",
     "blk = [a for a in entry.get(\"after\") or [] if a in G]"),
    ("pr-by-merge-commit", PAGE,
     "if sha.startswith(commit) or commit.startswith(sha[:len(commit)]):", "if False:"),
    ("pr-by-branch", PAGE, "            by_group[g] = p[\"number\"]", "            pass"),
    ("pr-sha8-fallback", PAGE, "label, pr = f\"merged at {commit[:8]}\", \"merged\"",
     "label, pr = \"folded into another group (no merge of its own)\", \"merged\""),
    ("branch-tail-fallback", PAGE,
     "return tails.get(tail) or tails.get(tail.replace(\"-pr\", \"\"))", "return None"),
    ("title-fallback", PAGE,
     "return named.pop() if len(named) == 1 else None", "return None"),
    ("closed-strike", PAGE, "(\"\" if is_open else \" closed\")", "\"\""),
    ("tracking-excluded", PAGE,
     "if i[\"state\"] == \"OPEN\" and i[\"number\"] != TRACKING_ISSUE)",
     "if i[\"state\"] == \"OPEN\")"),
    ("page-refuses-stale", PAGE, "    if stale:\n        bad.append", "    if False:\n        bad.append"),
    ("freshness-rule", PLAN, "if have != want:", "if False:"),
    ("stamp-on-axis", PAGE,
     "end = max([_t(plan[\"summary\"][\"closure\"])] + [_t(s[\"at\"]) for s in plan[\"stamps\"]])",
     "end = _t(plan[\"summary\"][\"closure\"])"),
    # Round 2: the fix review's survivors B to E (probe/rev-2558-e98d4b97).
    # B moved with its rule (2026-11-01): `replan.check_plan` refuses a plan
    # recording no model, which the page reads through C, so the page's own
    # duplicate refusal was deleted and the mutant targets the one owner.
    ("B-model-record-refusal", PLAN,
     "        bad.append(\"model: the plan records no duration model (generated.model)\")",
     "        pass"),
    ("C-check_plan-refusal", PAGE, "bad = replan.check_plan(plan)", "bad = []"),
    ("D-caption-drawn-count", PAGE, "f\"start, ETA and wave. {drawn} of",
     "f\"start, ETA and wave. {max(0, len(chain) - 1) - drawn} of"),
    ("E-explicit-ref-wins", PLAN, "    ref = ref or gen.get(\"roster_ref\") or \"\"",
     "    ref = gen.get(\"roster_ref\") or ref or \"\""),
    # R10-PLAN-PRIO: the Tier column is the plan's computed dispatch priority.
    ("tier-column", PAGE,
     '{r["tier"] if r["tier"] is not None else "—"}', '"—"'),
    # R10-ORCH-PLANPAGE: the scratch generator's five defects (orch-machinery
    # DESIGN.md S8, 6.7), each mutant restoring its pre-fix shape.
    ("defect-1-hardcoded-override", PAGE,
     "    G = roster_lib.groups_of(roster)\n    PG = plan[\"groups\"]",
     "    G = roster_lib.groups_of(roster)\n    G.update({g: {**G[g], \"resume\": "
     "{\"stage\": \"not-started\"}} for g in list(G)[:1]})\n    PG = plan[\"groups\"]"),
    ("defect-2-scratch-graph", PAGE,
     "blk = [a for a in entry.get(\"after\") or [] if a in G and a not in done]",
     "blk = [a for a in {\"R9-READY\": [\"R9-LIVE\"]}.get(g, entry.get(\"after\") or [])"
     " if a in G and a not in done]"),
    ("defect-3-count-wrong-set", PAGE,
     "open_iss = (\"—\" if snap.get(\"offline\") else str(sum(",
     "open_iss = (\"—\" if snap.get(\"offline\") else str(len(snap[\"issues\"]) - 1 + 0 * sum("),
    ("defect-4-sha8-as-pr", PAGE,
     "label, pr = f\"merged at {commit[:8]}\", \"merged\"",
     "label, pr = f\"merged at {commit[:8]}\", f\"#{commit[:8]}\""),
    ("defect-5-absorbed-as-done", PAGE,
     "            st = \"held\"\n", "            st = \"done\"\n"),
    ("held-label", PAGE,
     "label = _stage(entry) + (f\" into {short(into)}\" if into else \"\") + sfx",
     "label = \"delivered\" + sfx"),
    ("unavailable-page-written", PAGE,
     "    Path(html_out).write_text(unavailable_page(what), encoding=\"utf-8\")\n",
     "    pass\n"),
    ("state-page-published", STATE, "        return {page_path: text}, None",
     "        return {}, None"),
    ("state-keeps-last-good", STATE,
     "    return ({} if held else {page_path: text}), why",
     "    return {page_path: text}, why"),
    ("state-unavailable-where-none", STATE,
     "    return ({} if held else {page_path: text}), why", "    return {}, why"),
    ("state-unread-exits-1", STATE, "rc = 1 if unread else 0", "rc = 0"),
    ("state-crash-guard", STATE,
     'if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:', "if False:"),
    ("unavailable-no-figures", PAGE,
     "f'<div class=\"stat\"><b>—</b><span>{e(v)}</span></div>'",
     "f'<div class=\"stat\"><b>0</b><span>{e(v)}</span></div>'"),
]


def fail_name(line: str) -> str:
    """A self-test FAIL line without its `(got: ...)` evidence tail; the one
    grammar of that line, shared with r10_plan_issues_chart_mutants.py."""
    return re.sub(r"\(got: .*", "", line)


def main(argv: list[str]) -> int:
    want = set(argv)
    mutant_guard.arm([PAGE, PLAN, STATE])
    survived = 0
    for name, rel, old, new in MUTANTS:
        if want and name not in want:
            continue
        path = ROOT / rel
        orig = path.read_bytes()
        try:
            if old is not None:
                text = orig.decode()
                if text.count(old) != 1:
                    print(f"abort: {name}: {old!r} occurs {text.count(old)} times in {rel}")
                    return 2
                path.write_text(text.replace(old, new), encoding="utf-8")
            runs = [subprocess.run([sys.executable, "-I", str(ROOT / s), "--self-test"],
                                   capture_output=True, text=True)
                    for s in (PAGE, PLAN, STATE) if s == PAGE or s == rel or old is None]
        finally:
            path.write_bytes(orig)
        fails = [ln for r in runs for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
        # state_docs.py reports its failures on one line, comma-joined.
        fails += [f"FAIL {ln}" for r in runs for ln in r.stdout.splitlines()
                  if re.match(r"\d+ self-test check\(s\) failed: ", ln)]
        rc = max(r.returncode for r in runs)
        if name == "M0":
            verdict = "null" if rc == 0 and not fails else "SURVIVED"
        elif fails and rc:
            verdict = "killed"
        elif rc:
            verdict = "CRASHED"
        else:
            verdict = "SURVIVED"
        survived += verdict in ("SURVIVED", "CRASHED")
        print(f"RESULT mutant={name} rc={rc} fails={len(fails)} verdict={verdict}")
        for ln in fails:
            print("   ", fail_name(ln))
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
