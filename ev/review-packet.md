# Review packet #3622
head: 2aff0cc4fe1ea58c40c1113b300592211ee75d3f
base: 755b7f57675b2a56d8bf674b9b6846bdb184eb11

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=132946733587 success
arch-score / arch-score id=132958703847 success
arm id=132946446043 skipped
budget-raise-gate / budget-raise-gate id=132958657320 success
cancel-superseded id=132958693401 success
codeql id=132958690548 skipped
codeql / Analyze (actions) id=132946655046 success
codeql / Analyze (javascript-typescript) id=132946654941 success
codeql / Analyze (python) id=132946654884 success
gate id=132958655713 success
governance id=132958694884 skipped
governance / env-matrix id=132946654923 success
governance / instrument-self-tests id=132946654918 success
governance / policy-docs id=132946654875 success
governance / record id=132946656488 skipped
governance / wave-script id=132946654851 success
hassfest id=132958656457 skipped
hassfest / hassfest id=132946654828 success
kernel-points id=132958686503 skipped
pr-contract id=132958676297 skipped
pr-contract / pr-contract id=132958034235 success
prelude id=132958706264 success
refresh id=132958656239 success
sweep-self id=132958885791 skipped
tests id=132958655705 skipped
tests / arch-instrument id=132947073598 success
tests / briefs id=132946654927 success
tests / browser id=132947073562 success
tests / ci-ratchet id=132957820124 skipped
tests / claims-autofix id=132956193121 skipped
tests / closure-scope id=132946654894 success
tests / closures id=132947073638 success
tests / closures-autofix id=132955304476 skipped
tests / coverage id=132947073579 success
tests / coverage-ratchet id=132957818795 success
tests / fast (3.14) id=132947073592 success
tests / graders-head-copy id=132957818879 success
tests / lane-proofs id=132957818806 success
tests / mutation id=132946654902 success
tests / mutation-autofix id=132947167271 skipped
tests / mutation-pins id=132947166985 skipped
tests / nightly-ha id=132947074794 skipped
tests / nightly-status id=132946654854 success
tests / replay id=132947075355 skipped
tests / typing id=132947073570 success
validate id=132958692875 skipped
validate / validate-hacs id=132946654913 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 tools/audit/seat/plan_page.py --self-test
             `tools/audit/seat/plan_page.py` is in the tree at this head
  ok         python3 tools/audit/seat/plan_phases.py --check dev/programme/round11/phases.json
             `tools/audit/seat/plan_phases.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/plan_public.py --self-test
             `tools/audit/seat/plan_public.py` is in the tree at this head
  ok         python3 tools/audit/seat/state_docs.py --self-test
             `tools/audit/seat/state_docs.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_plan_page_mutants.py M0 <the phases-* names>
             `dev/audit/harnesses/r10_plan_page_mutants.py` is in the tree at this head

FIGURES: 5 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 2f08deea70..c31c28c6a2 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -5,7 +5,7 @@
   "_rule": "Tracked paths no dimension measures, each with its reason; check_scopes.py refuses a path in no universe and not here, an entry here that also names a covered path, and an entry that names nothing.",
   "dev/audit/{rounds,yardstick}/**": "evidence records of past rounds (reports, verdicts, the harnesses findings ran) and each round's objective record and start evaluation, which check_scopes.py --round reads: a finding re-measures one by its own harness, and a seat audits the mechanism, not the records it left (D11.md)",
   "dev/archive/**": "retired records and carries kept for history; no seat acts on them",
-  "dev/programme/{delivery,register,round9,round10,triage}/**": "delivery rows, the register, round notes and triage records: records of decisions the mechanism already made",
+  "dev/programme/{delivery,register,round9,round10,round11,triage}/**": "delivery rows, the register, round notes and triage records: records of decisions the mechanism already made",
   "docs/design/**": "dated design records of shipped features; the user docs D5 and D6 measure are what describes them now",
   "docs/site/fonts/**": "vendored font files and their SIL OFL licence texts; no behaviour and no claim",
   "tests/golden/**": "value-bearing golden fixtures, claimed and never re-derived by a finder (CLAUDE.md rule 3); the scripts that read them are in D3's and D11's universes",
@@ -524,7 +524,7 @@
   "static": {
    "dev/audit/{rounds,rca}/**": "round evidence and root-cause records: what a round or a seat found then, re-measured by its own harness, never re-verified as current text",
    "dev/archive/**": "retired records kept for history",
-   "dev/programme/{delivery,register,round9,round10,triage}/**": "delivery rows, the register, round notes and triage records: records of decisions already made",
+   "dev/programme/{delivery,register,round9,round10,round11,triage}/**": "delivery rows, the register, round notes and triage records: records of decisions already made",
    "dev/governance/decisions/**": "decision records, history of what was decided and why; the role contracts and rules they changed are measured",
    "docs/design/**": "dated design records of shipped features; the user docs that describe them now are measured",
    "{.claude,.cursor}/rules/**": "generated from dev/governance/rules/ by tools/policy/rules_sync.mjs, whose --check refuses drift; the source is measured",
diff --git a/dev/audit/harnesses/r10_plan_page_mutants.py b/dev/audit/harnesses/r10_plan_page_mutants.py
index 52acaf8a6e..9ee1aadf66 100644
--- a/dev/audit/harnesses/r10_plan_page_mutants.py
+++ b/dev/audit/harnesses/r10_plan_page_mutants.py
@@ -3,7 +3,8 @@
 
 Each mutant is one exact one-occurrence replacement in
 tools/audit/seat/plan_page.py, tools/plan/replan.py (the freshness rule the
-page shares) or tools/audit/seat/state_docs.py (which publishes the page).
+page shares), tools/audit/seat/state_docs.py (which publishes the page) or
+tools/audit/seat/plan_phases.py (the round's phases section the page draws).
 The driver applies one, runs `plan_page.py --self-test` (and the mutated
 file's own `--self-test` too, and every one for M0), restores
 the file byte for byte, and refuses to start on a file with uncommitted edits.
@@ -42,6 +43,7 @@ ROOT = repo_root(__file__)
 PAGE = "tools/audit/seat/plan_page.py"
 PLAN = "tools/plan/replan.py"
 STATE = "tools/audit/seat/state_docs.py"
+PHASES = "tools/audit/seat/plan_phases.py"
 sys.path.insert(0, str(Path(__file__).resolve().parent))
 import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
 
@@ -132,6 +134,47 @@ MUTANTS = [
     ("unavailable-no-figures", PAGE,
      "f'<div class=\"stat\"><b>—</b><span>{e(v)}</span></div>'",
      "f'<div class=\"stat\"><b>0</b><span>{e(v)}</span></div>'"),
+    # R11-PRE-PLAN-RENDER: one mutant per predicate of the phases file and section.
+    ("phases-unknown-status", PHASES, "    if st not in STATUSES:\n", "    if False:\n"),
+    ("phases-waiting-named", PHASES,
+     'if st == "waiting" and not str(x.get("waiting_on") or "").strip():', "if False:"),
+    ("phases-unknown-phase", PHASES,
+     "            bad.append(f\"{where}: unknown phase (one of {', '.join(order)})\")\n", ""),
+    ("phases-order", PHASES, "if order.index(pid) <= last:", "if False:"),
+    ("phases-iso-date", PHASES, "if ph.get(k) is not None and not _date_ok(ph[k]):", "if False:"),
+    ("phases-not-started-date", PHASES,
+     'if st == "not-started" and (ph.get("started") or ph.get("finished")):', "if False:"),
+    ("phases-finished-not-done", PHASES, 'if ph.get("finished") and st != "done":', "if False:"),
+    ("phases-forecast-basis", PHASES,
+     'if not (isinstance(fc, dict) and str(fc.get("basis") or "").strip()):',
+     "if not isinstance(fc, dict):"),
+    ("phases-unlisted-drawn", PHASES, "            for pid, title in PHASES]",
+     "            for pid, title in PHASES if pid in given]"),
+    ("phases-items-under-open", PHASES, 'if r.get("items") and r["status"] != "done":',
+     'if r.get("items"):'),
+    ("phases-waiting-label", PHASES,
+     "return f\"waiting on {x['waiting_on']}\" if st == \"waiting\" else STATUSES[st]",
+     "return STATUSES[st]"),
+    ("phases-forecast-basis-shown", PHASES,
+     "f'<div class=\"lanec\">{e(fc[\"basis\"])}</div>' if fc else", "'' if fc else"),
+    ("phases-unavailable", PHASES, "    if bad:\n        return (f'<section>",
+     "    if False:\n        return (f'<section>"),
+    ("phases-newest-round", PHASES, "return max(found)[1] if found else None",
+     "return min(found)[1] if found else None"),
+    ("phases-no-host-path", PHASES, "        return p.name\n", "        return str(p)\n"),
+    ("phases-drawn", PAGE,
+     '"phases": plan_phases.section(*phases, axis=time_axis(plan)) if phases else "",',
+     '"phases": "",'),
+    ("phases-shared-axis", PAGE, "plan_phases.section(*phases, axis=time_axis(plan))",
+     "plan_phases.section(*phases, axis=None)"),
+    ("phases-keep-groups-page", PAGE, '        "flow": flow_section(plan, rows, flow),',
+     '        "flow": "" if phases else flow_section(plan, rows, flow),'),
+    ("phases-cut-off-axis", PHASES, "if b < t0 or a > t_end:", "if False:"),
+    ("phases-cut-since", PHASES, "f'{_when(r[\"started\"])}</text>' if a < t0 else \"\")",
+     "f'{_when(r[\"started\"])}</text>' if False else \"\")"),
+    ("phases-forecast-past-axis", PHASES, "            if a > t_end:\n", "            if False:\n"),
+    ("phases-now-on-axis", PHASES, "    if t0 <= now <= t_end:\n", "    if True:\n"),
+    ("phases-discovered", PAGE, "pf = a.phases or plan_phases.discover(a.repo)", "pf = a.phases"),
 ]
 
 
@@ -143,7 +186,7 @@ def fail_name(line: str) -> str:
 
 def main(argv: list[str]) -> int:
     want = set(argv)
-    mutant_guard.arm([PAGE, PLAN, STATE])
+    mutant_guard.arm([PAGE, PLAN, STATE, PHASES])
     survived = 0
     for name, rel, old, new in MUTANTS:
         if want and name not in want:
diff --git a/dev/audit/harnesses/r11_plan_page_inventory.py b/dev/audit/harnesses/r11_plan_page_inventory.py
new file mode 100644
index 0000000000..1ecc14ad2f
--- /dev/null
+++ b/dev/audit/harnesses/r11_plan_page_inventory.py
@@ -0,0 +1,67 @@
+#!/usr/bin/env python3
+"""R11-PRE-PLAN-RENDER: what a plan page carries, as a set of structural items.
+
+    python3 dev/audit/harnesses/r11_plan_page_inventory.py BASE.html [OTHER.html ...]
+
+Prints the inventory of BASE: one line per item, kind and value, every digit
+run read as `#` so a figure that moved between two snapshots is the same item.
+The kinds: heading, table header row, legend entry, filter control, element
+id, class name, data attribute, event listener, link target shape, and a
+tooltip on a chart bar. For each OTHER it then prints `MISSING <item>` for
+every BASE item OTHER lacks, `ADDED <item>` for every item only OTHER has,
+and `RESULT other=<path> missing=<n> added=<n>`. Exit 1 when any OTHER misses
+an item. Null control: a page against itself prints missing=0 added=0.
+"""
+from __future__ import annotations
+
+import re
+import sys
+from pathlib import Path
+
+
+def _n(s: str) -> str:
+    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", s)).strip()
+
+
+def inventory(text: str) -> set:
+    items = set()
+    for lvl, h in re.findall(r"<h([123])[^>]*>(.*?)</h\1>", text, re.S):
+        items.add(f"heading h{lvl}: {_n(re.sub(r'<[^>]+>', '', h))}")
+    for head in re.findall(r"<thead>(.*?)</thead>", text, re.S):
+        items.add("table: " + " | ".join(_n(re.sub(r"<[^>]+>", "", c))
+                                         for c in re.findall(r"<th[^>]*>(.*?)</th>", head, re.S)))
+    for leg in re.findall(r'<div class="legend">(.*?)</div>', text, re.S):
+        for span in re.findall(r"<span>(.*?)</span>", leg, re.S):
+            items.add(f"legend: {_n(re.sub(r'<[^>]+>', '', span))}")
+    items |= {f"filter: {f}" for f in re.findall(r'data-f="([^"]+)"', text)}
+    items |= {f"id: {i}" for i in re.findall(r'<\w+[^>]*?\sid="([^"]+)"', text)}
+    items |= {f"class: {c}" for cs in re.findall(r'\sclass="([^"]+)"', text) for c in cs.split()}
+    items |= {f"data attribute: {d}" for d in re.findall(r"\s(data-[a-z-]+)=", text)}
+    items |= {f"listener: {ev}" for ev in re.findall(r"addEventListener\('([a-z]+)'", text)}
+    items |= {f"link: {_n(h)}" for h in re.findall(r'href="([^"]+)"', text)}
+    if re.search(r'<g class="grp"[^>]*>\s*<title>', text):
+        items.add("tooltip: chart bar title")
+    return items
+
+
+def main(argv: list) -> int:
+    if not argv:
+        print(__doc__)
+        return 2
+    base = inventory(Path(argv[0]).read_text(encoding="utf-8"))
+    for item in sorted(base):
+        print(item)
+    lost = 0
+    for other in argv[1:]:
+        inv = inventory(Path(other).read_text(encoding="utf-8"))
+        for item in sorted(base - inv):
+            print(f"MISSING {item}")
+        for item in sorted(inv - base):
+            print(f"ADDED {item}")
+        print(f"RESULT other={Path(other).name} missing={len(base - inv)} added={len(inv - base)}")
+        lost += len(base - inv)
+    return 1 if lost else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/programme/delivery/3622.md b/dev/programme/delivery/3622.md
new file mode 100644
index 0000000000..3bd7cc1291
--- /dev/null
+++ b/dev/programme/delivery/3622.md
@@ -0,0 +1 @@
+- [#3622](https://github.com/tvofi/heatpump_optimizer/pull/3622) — **open**, R11-PRE-PLAN-RENDER: r11 pre plan render (R11-PRE-PLAN-RENDER)
diff --git a/dev/programme/round11/phases.json b/dev/programme/round11/phases.json
new file mode 100644
index 0000000000..3ddf64c90b
--- /dev/null
+++ b/dev/programme/round11/phases.json
@@ -0,0 +1,131 @@
+{
+ "round": 11,
+ "as_of": "2026-11-15T13:00:00Z",
+ "phases": [
+  {
+   "phase": "round-start",
+   "status": "running",
+   "started": "2026-11-15T05:22:47Z",
+   "entry": "the prior round's final state comment on #201 (round 10 closed by the v10.0.0 tag, whose time is this phase's start)",
+   "exit": "a baseline SHA pinned after evaluator.md's evaluation, once every finder-critical group has merged",
+   "items": [
+    {
+     "name": "Pickup",
+     "status": "done"
+    },
+    {
+     "name": "Start evaluation (decision 0018)",
+     "status": "done",
+     "detail": "approved: eval/r11 02a48db2, review eval-review/r11-3 92991d2a"
+    },
+    {
+     "name": "Owner card rulings",
+     "status": "running",
+     "detail": "48 cards, 2 still to rule"
+    },
+    {
+     "name": "Round-10 objective record",
+     "status": "running",
+     "detail": "pull request #3611 open, in review"
+    },
+    {
+     "name": "Round-11 roster cutover",
+     "status": "waiting",
+     "waiting_on": "the roster edit queue",
+     "detail": "approved"
+    },
+    {
+     "name": "R11-PRE-FINDER-CONTRACT",
+     "status": "running",
+     "detail": "finder-critical; fixer running since 12:05Z"
+    },
+    {
+     "name": "R11-PRE-BRIEFS-CENSUS",
+     "status": "running",
+     "detail": "finder-critical; fixer running since 12:05Z"
+    },
+    {
+     "name": "R11-PRE-BRIEFS-TEXT",
+     "status": "running",
+     "detail": "finder-critical; fixer running since 12:05Z"
+    },
+    {
+     "name": "R11-PRE-OWNER-CRITERIA",
+     "status": "running",
+     "detail": "finder-critical; fixer running since 12:05Z"
+    },
+    {
+     "name": "R11-PRE-NEW-DIMENSIONS",
+     "status": "not-started",
+     "detail": "finder-critical; design first, not yet dispatched"
+    },
+    {
+     "name": "R11-PRE-ROUND-METRICS part 1",
+     "status": "running",
+     "detail": "finder-critical (recall and overlap); fixer running since 12:43Z"
+    },
+    {
+     "name": "Scopes proved",
+     "status": "not-started",
+     "detail": "finder-critical"
+    },
+    {
+     "name": "Baseline at a green main",
+     "status": "not-started",
+     "detail": "finder-critical"
+    },
+    {
+     "name": "Instrument groups",
+     "status": "running",
+     "detail": "in parallel, not gating finders: R11-PRE-MACHINERY-LIMITER, three S hotfixes, R11-PRE-TOOLCHAIN-PIN and R11-PRE-SHARED-FILES in design, R11-PRE-STANDING-SCRIPTS, RULINGS-FILE, RELAY-REBUILD, HANDOFF-BOOKKEEPING, ACK-COMPLETION, TOKEN-LEDGER, PLAN-RENDER"
+    },
+    {
+     "name": "Outside work",
+     "status": "running",
+     "detail": "in parallel, not gating finders: #3598 in review, #3602 in repair, #3529 open"
+    }
+   ]
+  },
+  {
+   "phase": "finders",
+   "status": "not-started",
+   "forecast": {
+    "start_from": "2026-11-16T08:00:00Z",
+    "start_to": "2026-11-16T20:00:00Z",
+    "basis": "the orchestrator's forecast at 2026-11-15 13:00Z, after the finder-critical groups"
+   },
+   "entry": "a baseline SHA pinned after evaluator.md's evaluation",
+   "exit": "every scope reported"
+  },
+  {
+   "phase": "verify-judge",
+   "status": "not-started",
+   "entry": "the finders' reports",
+   "exit": "every finding judged, classes swept"
+  },
+  {
+   "phase": "plan",
+   "status": "not-started",
+   "entry": "the judged register",
+   "exit": "Plan review: approve, then the owner's approval"
+  },
+  {
+   "phase": "fix-waves",
+   "status": "not-started",
+   "entry": "the approved plan; the roster lints clean",
+   "exit": "every group merged, one train batch at a time; row, handover and state docs current"
+  },
+  {
+   "phase": "stamps",
+   "status": "not-started",
+   "entry": "merges since the last tag",
+   "exit": "the tag pushed"
+  },
+  {
+   "phase": "closure",
+   "status": "not-started",
+   "entry": "every phase drained",
+   "exit": "the closure criteria of dev/audit/README.md hold"
+  }
+ ]
+}
diff --git a/tests/closure.py b/tests/closure.py
index bcd27818f9..0ef97cc923 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -644,6 +644,9 @@ INERT_EXCEPT = (
     # Also read by that self-test (the page renderer replan feeds): tools/audit/seat/
     # stays INERT, this file joins the recorded closure.
     "tools/audit/seat/plan_page.py",
+    # R11-PRE-PLAN-RENDER: plan_page.py imports the round's phases section, so
+    # the same self-test opens it; it joins the recorded closure beside it.
+    "tools/audit/seat/plan_phases.py",
     # R10-TICK-LEVELS P2: roster_sync.py (already a recorded read above) imports
     # the topic grammar's one owner in-process, so tests/entities.py's load of it
     # opens this file. CI's closures job 128825445404 was UNDER-SCOPED on it and
diff --git a/tests/closures.json b/tests/closures.json
index 57572416a4..f16c5f8215 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1981,6 +1981,7 @@
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/orchestrator_tick.py",
    "tools/audit/seat/plan_page.py",
+   "tools/audit/seat/plan_phases.py",
    "tools/audit/seat/plan_table.py",
    "tools/audit/seat/postmerge.py",
    "tools/audit/seat/pr_cap.py",
@@ -4125,6 +4126,7 @@
    "tools/audit/seat/owed_unactioned.py",
    "tools/audit/seat/plan_audit.py",
    "tools/audit/seat/plan_page.py",
+   "tools/audit/seat/plan_phases.py",
    "tools/audit/seat/plan_public.py",
    "tools/audit/seat/postmerge.py",
    "tools/audit/seat/pr_cap.py",
@@ -4460,6 +4462,7 @@
    "dev/audit/harnesses/r10_verdict_item_barrier.py",
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
+   "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
    "dev/audit/harnesses/r9_dbg2_selftest_price.py",
    "dev/audit/harnesses/r9_fr3_family_consumer.mjs",
diff --git a/tests/layout.json b/tests/layout.json
index 497917b883..9ba7369ebe 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -67,7 +67,7 @@
   },
   {
    "name": "dev/programme",
-   "why": "the fix programme record: the living handover, the plan of record, delivery rows, live carries, rosters, the register, proposal-triage rulings",
+   "why": "the fix programme record: the living handover, the plan of record, delivery rows, live carries, rosters, each round's phases file, the register, proposal-triage rulings",
    "globs": [
     "dev/programme/HANDOVER.md",
     "dev/programme/plan-*.md",
@@ -76,6 +76,7 @@
     "dev/programme/rosters/*.json",
     "dev/programme/round9/**",
     "dev/programme/round10/**",
+    "dev/programme/round*/phases.json",
     "dev/programme/register/*.md",
     "dev/programme/triage/*.md"
    ]
diff --git a/tools/audit/seat/instruments/plan_page.py.md b/tools/audit/seat/instruments/plan_page.py.md
index e9ec4e314e..7a2ac65631 100644
--- a/tools/audit/seat/instruments/plan_page.py.md
+++ b/tools/audit/seat/instruments/plan_page.py.md
@@ -33,3 +33,18 @@
   `plan-beat` row passes from the overlay's `train_log`); `--no-flow` draws no
   flow metrics. Its mutants are in
   `dev/audit/harnesses/r10_outside_intake_p2_mutants.py`.
+- Round phases (R11-PRE-PLAN-RENDER): above the group lanes the page draws
+  the round's phases file, `dev/programme/round<N>/phases.json` (`--phases
+  FILE`, else the checkout's highest-numbered one), through
+  `tools/audit/seat/plan_phases.py`: every playbook phase in the playbook's
+  order on the file's own time axis, with status, started, finished, the
+  planned window and its basis, entry and exit, and the open phases' items. A
+  phase the file omits is drawn not started; a date the file does not carry
+  is a dash. `plan_phases.py --check FILE` lints the file (unknown status or
+  phase, out of order, waiting on nothing named, a non-ISO date, a date on a
+  not-started phase, a finished date on a phase not done, a forecast with no
+  basis: exit 1); an invalid file draws PHASES UNAVAILABLE and leaves the rest
+  of the page standing. `plan_phases.py --phases FILE --html OUT` draws the
+  section alone as a page, for a round with no plan yet. The file is named on
+  the page by its checkout-relative path, never a host path. Its mutants are
+  the `phases-*` entries of `dev/audit/harnesses/r10_plan_page_mutants.py`.
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index db5c33befc..7852a30610 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -51,6 +51,11 @@ last segment against the tails of the roster's `resume.branch` values (with a
 `-pr` suffix dropped): `fix/r10-ci-layout-g` names R10-CI-LAYOUT only that way;
 failing both, by the one roster group id its title names.
 
+The round's phases (`plan_phases.py`, its file under `dev/programme/round<N>/`)
+are drawn above the group lanes: `--phases FILE`, else the checkout's newest
+round phases file; an invalid one is its section's PHASES UNAVAILABLE, never
+the page's.
+
 `--self-test` drives every arm from fixtures in a throwaway repository, and
 never reaches GitHub: the fetch is replaced by one that fails the test.
 """
@@ -77,6 +82,7 @@ import replan  # noqa: E402 -- the one owner of plan.json and its freshness
 sys.path.insert(0, str(_SEAT.parent))
 import merge_throughput as mt  # noqa: E402 -- the flow board's computations
 import bottleneck_check  # noqa: E402 -- the one owner of the alert thresholds
+import plan_phases  # noqa: E402 -- the round's phases file and its section
 
 SELF = "tools/audit/seat/plan_page.py"
 sys.path.insert(0, str(_SEAT.parents[1] / "policy"))
@@ -309,16 +315,21 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
 
 # ---------------------------------------------------------------------- svg
 
+def time_axis(plan: dict) -> tuple[dt.datetime, dt.datetime]:
+    """The plan's time axis, `(start, end)`: the swimlanes' and the phases'.
+    It runs to closure, which is the later of the round-close stamp and the
+    last post-closure step, so no stamp lies past it."""
+    return _t(plan["generated"]["start"]), max(
+        [_t(plan["summary"]["closure"])]
+        + [_t(plan["summary"]["post_closure_finish"])
+           for _ in [0] if plan["summary"].get("post_closure_finish")])
+
+
 def swimlanes(plan: dict, rows: list) -> tuple[str, int]:
     """The SVG chart on the plan's time axis; and how many critical-path links
     it draws (a link crossing more than one lane or two hours is left to the
     ◆ marks and the caption)."""
-    now = _t(plan["generated"]["start"])
-    # The axis runs to closure, which is the later of the round-close stamp and
-    # the last post-closure step, so no stamp lies past it.
-    end = max([_t(plan["summary"]["closure"])]
-              + [_t(plan["summary"]["post_closure_finish"])
-                 for _ in [0] if plan["summary"].get("post_closure_finish")])
+    now, end = time_axis(plan)
     slots = plan["generated"]["caps"]["slots"]
     span_h = max(1.0, (end - now).total_seconds() / 3600)
     W, LW, RH = 1180, 120, 24
@@ -632,8 +643,9 @@ def _when(s: str) -> str:
 
 
 def render(roster: dict, roster_src: str, plan: dict, snap: dict,
-           flow: dict | None = None) -> str:
-    """The page. Pure: every input is an argument."""
+           flow: dict | None = None, phases: tuple | None = None) -> str:
+    """The page. Pure: every input is an argument. `phases` is the round's
+    phases file as `(doc, violations, shown path)`, drawn above the lanes."""
     rows = build_rows(roster, plan, snap)
     svg, drawn = swimlanes(plan, rows)
     gen, summ = plan["generated"], plan["summary"]
@@ -695,6 +707,7 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
         "now": _t(gen["start"]).strftime("%d %b %H:%M"),
         "source": e(f'{roster_src} @ {gen["roster_blob"][:12]}'),
         "tracking": str(TRACKING_ISSUE), "open_iss": open_iss,
+        "phases": plan_phases.section(*phases, axis=time_axis(plan)) if phases else "",
         "issues_chart": issues_section(roster, plan, snap),
         "flow": flow_section(plan, rows, flow),
         "end": _t(summ["closure"]).strftime("%a %d %b %H:%M"),
@@ -784,6 +797,9 @@ def main(argv=None, fetch=fetch_github) -> int:
     p.add_argument("--train-log", default=None,
                    help="the live merge train's train.log, for the skip measure")
     p.add_argument("--no-flow", action="store_true", help="draw no flow metrics")
+    p.add_argument("--phases", default=None,
+                   help="the round's phases file; default: the checkout's newest "
+                        "dev/programme/round<N>/phases.json (plan_phases.discover)")
     p.add_argument("--self-test", action="store_true")
     a = p.parse_args(argv)
     if a.self_test:
@@ -810,7 +826,14 @@ def main(argv=None, fetch=fetch_github) -> int:
     snap = (json.loads(Path(a.github_snapshot).read_text(encoding="utf-8"))
             if a.github_snapshot else _fetch_or_offline(fetch, a.gh_repo))
     flow = None if a.no_flow else flow_metrics(a.repo, ref, path, roster, plan, a.train_log)
-    page = render(roster, f"{ref}:{path}", plan, snap, flow)
+    pf = a.phases or plan_phases.discover(a.repo)
+    phases = None
+    if pf:
+        doc, pbad = plan_phases.load(pf)
+        for b in pbad:
+            print(f"plan_page: phases {pf}: {b}", file=sys.stderr)
+        phases = (doc, pbad, plan_phases.shown(pf, a.repo))
+    page = render(roster, f"{ref}:{path}", plan, snap, flow, phases)
     Path(a.html).write_text(page, encoding="utf-8")
     print(f"wrote {a.html}: {len(roster_lib.groups_of(roster))} groups, "
           f"closure {plan['summary']['closure']}")
@@ -825,6 +848,7 @@ def _self_test() -> int:
     import tempfile
     sys.path.insert(0, str(_SEAT.parents[2] / "tests"))
     from throwaway_git import throwaway_git_environ, throwaway_git_init
+    import plan_public  # the public staging's privacy refusal, over a page with phases
     fails: list = []
     n = [0]
 
@@ -1316,6 +1340,64 @@ def _self_test() -> int:
                     "--github-snapshot", str(snapf)]
             check("a fresh plan renders (null control)",
                   main(argv, fetch=fetch_refused) == 0 and out.is_file())
+            check("null control: a checkout with no phases file draws no phases section",
+                  'id="phases"' not in out.read_text(encoding="utf-8")
+                  and "PHASES UNAVAILABLE" not in out.read_text(encoding="utf-8"))
+            out.unlink()
+            plan_phases.fixture_checks(check)
+            # The three cases of one page: groups and phases, phases only, groups only.
+            src = f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json"
+            fx = (plan_phases.fixture(), [], "dev/programme/round9/phases.json")
+            groups_only = render(roster, src, plan, snap)
+            both = render(roster, src, plan, snap, None, fx)
+            sec = plan_phases.section(*fx, axis=time_axis(plan))
+            check("groups and phases: the page is the groups-only page plus the phases section, "
+                  "every section, table and control of it kept",
+                  sec in both and both.replace(sec, "", 1) == groups_only,
+                  [ln for ln in both.replace(sec, "", 1).splitlines() if ln not in groups_only][:3])
+            check("groups and phases: the phases section sits above the swimlanes",
+                  0 <= both.find('id="phases"') < both.find("<h2>Swimlanes</h2>"))
+            ticks = [re.findall(r'<text x="([\d.]+)" y="14" class="tick">([^<]*)', x)[:4]
+                     for x in (sec, swimlanes(plan, build_rows(roster, plan, snap))[0])]
+            check("groups and phases: the phases are drawn on the swimlanes' own time axis",
+                  ticks[0] and ticks[0] == ticks[1], ticks)
+            check("null control, groups only: no phases section, nothing of the phases drawn",
+                  'id="phases"' not in groups_only and "PHASES UNAVAILABLE" not in groups_only)
+            empty = replan.build_plan({"groups": []}, json.loads(
+                (_SEAT.parents[1] / "plan" / "durations.json").read_text(encoding="utf-8")),
+                dict(replan.DEFAULT_CAPS), _t(plan["generated"]["start"]), "v1.0.0", "main",
+                "", round_n=9)
+            phases_only = render({"groups": []}, src, empty, snap, None, fx)
+            check("phases only (a round with no fix group yet): the page renders the phases "
+                  "and the group sections, with no group row",
+                  'id="phases"' in phases_only and "<h2>Swimlanes</h2>" in phases_only
+                  and '<tbody id="rows"></tbody>' in phases_only, phases_only[:200])
+            check("null control, phases only: the same empty roster with no phases file draws none",
+                  'id="phases"' not in render({"groups": []}, src, empty, snap))
+            pf = Path(td) / "outside" / "phases.json"
+            pf.parent.mkdir()
+            pf.write_text(json.dumps(plan_phases.fixture()), encoding="utf-8")
+            check("--phases FILE: the page draws the round's phases above the group lanes",
+                  main(argv + ["--phases", str(pf)], fetch=fetch_refused) == 0
+                  and 0 <= out.read_text(encoding="utf-8").find('id="phases"')
+                  < out.read_text(encoding="utf-8").find("<h2>Swimlanes</h2>"))
+            text = out.read_text(encoding="utf-8")
+            check("a page with phases names no host path: plan_public's privacy refusal passes",
+                  str(pf.parent) not in text and plan_public.refusal(text) is None,
+                  plan_public.refusal(text))
+            home = repo / "dev" / "programme" / "round9"
+            home.mkdir(parents=True)
+            (home / "phases.json").write_text(json.dumps(plan_phases.fixture()), encoding="utf-8")
+            main(argv, fetch=fetch_refused)
+            text = out.read_text(encoding="utf-8")
+            check("with no --phases, the checkout's newest round phases file is drawn",
+                  'id="phases"' in text and "dev/programme/round9/phases.json" in text, text[:300])
+            (home / "phases.json").write_text('{"round": 9, "phases": [{"phase": "x"}]}')
+            main(argv, fetch=fetch_refused)
+            text = out.read_text(encoding="utf-8")
+            check("an invalid phases file draws PHASES UNAVAILABLE; the group lanes still stand",
+                  "PHASES UNAVAILABLE" in text and "<h2>Swimlanes</h2>" in text, text[:300])
+            (home / "phases.json").unlink()
             out.unlink()
 
             def no_gh_binary(_repo):
@@ -1506,7 +1588,7 @@ td.st{min-width:11rem}
   <div class="stat end"><b>{{end}}</b><span>projected programme close</span></div>
 </div>
 
-{{issues_chart}}
+{{phases}}{{issues_chart}}
 {{flow}}
 <section>
   <h2>Swimlanes</h2>
diff --git a/tools/audit/seat/plan_phases.py b/tools/audit/seat/plan_phases.py
new file mode 100644
index 0000000000..c6d3cc52f2
--- /dev/null
+++ b/tools/audit/seat/plan_phases.py
@@ -0,0 +1,453 @@
+#!/usr/bin/env python3
+"""A round's phases: the linted input file and the plan page's phases section.
+
+    python3 tools/audit/seat/plan_phases.py --check dev/programme/round11/phases.json
+    python3 tools/audit/seat/plan_phases.py --phases FILE --html page.html
+
+The plan page draws a round's fix groups from the roster and plan.json, which
+exist only from the round's fifth phase. The phases file is where everything
+before and around them is recorded: one entry per phase of the playbook
+(`dev/audit/README.md`, "Running a round: the playbook" and "Round start"), in
+the order of `PHASES`. `plan_page.py` imports `section` and draws it above the
+group lanes; `--html` draws the section alone as a page, for a round with no
+plan yet.
+
+The file (JSON):
+
+    {"round": 11, "as_of": ISO, "note": str?,
+     "phases": [{"phase": one of PHASES, "status": one of STATUSES,
+                 "waiting_on": str (iff status waiting),
+                 "started": ISO?, "finished": ISO?,
+                 "forecast": {"start_from": ISO, "start_to": ISO, "basis": str}?,
+                 "entry": str?, "exit": str?,
+                 "items": [{"name": str, "status": one of STATUSES,
+                            "waiting_on": str?, "detail": str?}]?}]}
+
+REFUSALS (`violations`; `--check` exits 1): a status outside `STATUSES`; a
+phase outside `PHASES`, repeated, or out of the playbook's order; `waiting`
+with no `waiting_on`; a date that is not ISO-8601 UTC; a `started` or
+`finished` date on a not-started phase; a `finished` date on a phase not done;
+a forecast with no `basis` (a date with no plan behind it). A phase the file
+does not list is drawn "not started" with dashes, never omitted; the page
+prints no date or count the file does not carry. An invalid file is drawn as
+PHASES UNAVAILABLE with its first violation: the rest of the plan page stands.
+"""
+
+from __future__ import annotations
+
+import argparse
+import datetime as dt
+import html
+import json
+import re
+import sys
+import tempfile
+from pathlib import Path
+
+# The playbook's order (dev/audit/README.md): round start holds the pickup,
+# the start evaluation and the finder-critical groups; fix waves are the
+# roster's group lanes (playbook phases 5 to 10).
+PHASES = (
+    ("round-start", "Round start"),
+    ("finders", "Finders"),
+    ("verify-judge", "Verify, judge"),
+    ("plan", "Architect plan"),
+    ("fix-waves", "Fix waves"),
+    ("stamps", "Stamps"),
+    ("closure", "Closure"),
+)
+STATUSES = {"not-started": "not started", "running": "running",
+            "waiting": "waiting", "done": "done"}
+# The plan page's pill classes, so a phase reads in the page's own language.
+_PILL = {"not-started": "held", "running": "live", "waiting": "blocked", "done": "done"}
+_ISO = "%Y-%m-%dT%H:%M:%SZ"
+_FILE = re.compile(r"\Around(\d+)\Z")
+
+
+def _t(s: str) -> dt.datetime:
+    return dt.datetime.strptime(s, _ISO)
+
+
+def _date_ok(v) -> bool:
+    try:
+        _t(v)
+        return True
+    except (TypeError, ValueError):
+        return False
+
+
+def violations(doc) -> list:
+    """Every refusal the file earns, in reading order; empty when it is sound."""
+    if not isinstance(doc, dict):
+        return ["the file is not a JSON object"]
+    bad = []
+    if not isinstance(doc.get("round"), int):
+        bad.append("round: not an integer")
+    if not _date_ok(doc.get("as_of")):
+        bad.append(f"as_of: not ISO-8601 UTC ({doc.get('as_of')!r})")
+    order = [p for p, _ in PHASES]
+    last = -1
+    phases = doc.get("phases")
+    if not isinstance(phases, list):
+        return bad + ["phases: not a list"]
+    for i, ph in enumerate(phases):
+        pid = ph.get("phase") if isinstance(ph, dict) else None
+        where = f"phases[{i}] {pid}"
+        if pid not in order:
+            bad.append(f"{where}: unknown phase (one of {', '.join(order)})")
+            continue
+        if order.index(pid) <= last:
+            bad.append(f"{where}: out of the playbook's order, or repeated")
+        last = max(last, order.index(pid))
+        bad += _status_violations(where, ph)
+        st = ph.get("status")
+        for k in ("started", "finished"):
+            if ph.get(k) is not None and not _date_ok(ph[k]):
+                bad.append(f"{where}: {k} not ISO-8601 UTC ({ph[k]!r})")
+        if st == "not-started" and (ph.get("started") or ph.get("finished")):
+            bad.append(f"{where}: a date on a not-started phase (put a plan's date in forecast, with its basis)")
+        if ph.get("finished") and st != "done":
+            bad.append(f"{where}: finished on a phase not done")
+        fc = ph.get("forecast")
+        if fc is not None:
+            if not (isinstance(fc, dict) and str(fc.get("basis") or "").strip()):
+                bad.append(f"{where}: a forecast with no basis (a date with no plan behind it)")
+            elif not (_date_ok(fc.get("start_from")) and _date_ok(fc.get("start_to"))):
+                bad.append(f"{where}: forecast start_from/start_to not ISO-8601 UTC")
+        for j, it in enumerate(ph.get("items") or []):
+            if not (isinstance(it, dict) and str(it.get("name") or "").strip()):
+                bad.append(f"{where} items[{j}]: no name")
+                continue
+            bad += _status_violations(f"{where} item {it['name']}", it)
+    return bad
+
+
+def _status_violations(where: str, x: dict) -> list:
+    st = x.get("status")
+    if st not in STATUSES:
+        return [f"{where}: unknown status {st!r} (one of {', '.join(STATUSES)})"]
+    if st == "waiting" and not str(x.get("waiting_on") or "").strip():
+        return [f"{where}: waiting on nothing named (waiting_on)"]
+    return []
+
+
+def load(path: str | Path):
+    """(doc, violations) for a phases file; a file that does not parse is one violation."""
+    try:
+        doc = json.loads(Path(path).read_text(encoding="utf-8"))
+    except (OSError, ValueError) as exc:
+        return None, [f"{Path(path).name}: {type(exc).__name__}: {exc}"]
+    return doc, violations(doc)
+
+
+def discover(repo: str | Path) -> Path | None:
+    """The running round's phases file in a checkout: the highest-numbered
+    `dev/programme/round<N>/phases.json`, or None."""
+    found = []
+    for p in (Path(repo) / "dev" / "programme").glob("round*/phases.json"):
+        m = _FILE.match(p.parent.name)
+        if m:
+            found.append((int(m.group(1)), p))
+    return max(found)[1] if found else None
+
+
+# ------------------------------------------------------------------ drawing
+
+def _pill(st: str, label: str) -> str:
+    return f'<span class="pill {_PILL[st]}">{html.escape(label)}</span>'
+
+
+def _label(x: dict) -> str:
+    st = x["status"]
+    return f"waiting on {x['waiting_on']}" if st == "waiting" else STATUSES[st]
+
+
+def _when(s: str | None) -> str:
+    return _t(s).strftime("%a %d %b %H:%M") if s else "—"
+
+
+def rows_of(doc: dict) -> list:
+    """Every phase of the playbook, in its order: the file's entry, or a
+    not-started placeholder carrying nothing."""
+    given = {p["phase"]: p for p in doc.get("phases") or []}
+    return [dict(given.get(pid) or {"phase": pid, "status": "not-started"}, title=title)
+            for pid, title in PHASES]
+
+
+def timeline(doc: dict, rows: list, axis: tuple | None = None) -> str:
+    """The phases on a time axis. `axis` is the plan page's own `(start, end)`:
+    the swimlanes' geometry, scale and ticks, so a phase lines up with the
+    group lanes under it, and a phase reaching past either end is cut there
+    and says so. With no axis, the file's own: its earliest date to its
+    latest. A running bar ends at `as_of`, a forecast is a dashed window, a
+    phase with no date says so in its row."""
+    now = _t(doc["as_of"])
+    if axis:
+        t0, t1 = axis
+        span = max(3600.0, (t1 - t0).total_seconds())
+        W, LW, step = 1180, 120, 12
+    else:
+        pts = [now]
+        for r in rows:
+            pts += [_t(r[k]) for k in ("started", "finished") if r.get(k)]
+            fc = r.get("forecast")
+            if fc:
+                pts += [_t(fc["start_from"]), _t(fc["start_to"])]
+        t0, t1 = min(pts), max(pts)
+        span = max(3600.0, (t1 - t0).total_seconds()) * 1.04
+        W, LW = 1180, 230
+        step = 6 if span <= 3 * 86400 else 24
+    t_end = t0 + dt.timedelta(seconds=span)
+    RH = 26
+
+    def px(t):
+        return LW + (min(max(t, t0), t_end) - t0).total_seconds() / span * (W - LW - 20)
+
+    e, parts = html.escape, []
+    H = 22 + len(rows) * (RH + 6) + 6
+    h0 = t0 if axis else t0.replace(minute=0, second=0)
+    for k in range(0, int(span // 3600) + 2, step):
+        t = h0 + dt.timedelta(hours=k)
+        if t0 <= t <= t_end:
+            parts.append(f'<line x1="{px(t):.1f}" y1="20" x2="{px(t):.1f}" y2="{H}" class="grid"/>'
+                         f'<text x="{px(t):.1f}" y="14" class="tick">{t.strftime("%a %Hh")}</text>')
+
+    def note(y, text):
+        parts.append(f'<text x="{LW + 4}" y="{y + 17}" class="tick">{e(text)}</text>')
+    for i, r in enumerate(rows):
+        y = 22 + i * (RH + 6)
+        parts.append(f'<text x="10" y="{y + 17}" class="lanelab">{e(r["title"])}</text>')
+        cls = _PILL[r["status"]]
+        tip = f'{r["title"]}: {_label(r)}'
+        if r.get("started"):
+            a = _t(r["started"])
+            b = _t(r["finished"]) if r.get("finished") else now
+            if b < t0 or a > t_end:
+                note(y, f'{_label(r)}, {_when(r["started"])} to '
+                     f'{_when(r["finished"]) if r.get("finished") else "now"}, off this axis')
+            else:
+                w = max(px(b) - px(a), 4)
+                parts.append(f'<g class="phase"><title>{e(tip)}, started {_when(r["started"])}'
+                             f'{", finished " + _when(r["finished"]) if r.get("finished") else ", open"}</title>'
+                             f'<rect x="{px(a):.1f}" y="{y}" width="{w:.1f}" height="{RH}" rx="3" '
+                             f'class="bar {cls}{"" if r.get("finished") else " open"}"/>'
+                             + (f'<text x="{px(a) + 4:.1f}" y="{y + 17}" class="barlab">◂ since '
+                                f'{_when(r["started"])}</text>' if a < t0 else "") + "</g>")
+        fc = r.get("forecast")
+        if fc:
+            a, b = _t(fc["start_from"]), _t(fc["start_to"])
+            if a > t_end:
+                note(y, f'forecast start {_when(fc["start_from"])} to {_when(fc["start_to"])}, past this axis')
+            else:
+                parts.append(f'<g class="phase"><title>{e(r["title"])}: forecast start '
+                             f'{_when(fc["start_from"])} to {_when(fc["start_to"])} ({e(fc["basis"])})</title>'
+                             f'<rect x="{px(a):.1f}" y="{y}" width="{max(px(b) - px(a), 4):.1f}" '
+                             f'height="{RH}" rx="3" class="bar forecast"/>'
+                             f'<text x="{px(a) - 6:.1f}" y="{y + 17}" class="barlab" text-anchor="end">forecast start</text></g>')
+        if not r.get("started") and not fc:
+            note(y, f"{_label(r)} — no date")
+    if t0 <= now <= t_end:
+        parts.append(f'<line x1="{px(now):.1f}" y1="20" x2="{px(now):.1f}" y2="{H}" class="nowline"/>'
+                     f'<text x="{px(now) + 3:.1f}" y="{H - 2}" class="tick">as of</text>')
+    return (f'<svg viewBox="0 0 {W} {H + 4}" width="{W}" height="{H + 4}" role="img" '
+            f'aria-label="round phases">{"".join(parts)}</svg>')
+
+
+_CSS = """<style>
+.bar.done{fill:var(--done-bg);stroke:var(--done)}
+.bar.open{stroke-dasharray:6 2}
+.bar.forecast{fill:transparent;stroke:var(--muted);stroke-dasharray:3 3}
+.nowline{stroke:var(--accent);stroke-width:1.4}
+ul.items{margin:0;padding-left:1.1em;font-size:.86rem;columns:2 26rem;column-gap:28px}
+ul.items li{margin:2px 0;break-inside:avoid}
+</style>"""
+
+
+def section(doc, bad: list | None = None, where: str = "", axis: tuple | None = None) -> str:
+    """The phases section for the plan page: a timeline and one row per phase,
+    the running phases' items under them. `bad` (from `violations`) draws the
+    UNAVAILABLE section instead, naming the first refusal. `axis` is the plan
+    page's `(start, end)`: given, the timeline is drawn on it (`timeline`),
+    and the fix-waves row points at the group lanes, which are that phase."""
+    e = html.escape
+    if bad:
+        return (f'<section>\n  <h2>Round phases</h2>\n  <p><b>PHASES UNAVAILABLE — '
+                f'{len(bad)} violation(s) in {e(where)}: {e(bad[0])}</b></p>\n</section>\n')
+    rows = rows_of(doc)
+    trs = []
+    for r in rows:
+        fc = r.get("forecast")
+        planned = (f'start {_when(fc["start_from"])} to {_when(fc["start_to"])}'
+                   f'<div class="lanec">{e(fc["basis"])}</div>' if fc else "—")
+        items = ""
+        if r.get("items") and r["status"] != "done":
+            items = '<tr class="items"><td></td><td colspan="6"><ul class="items">' + "".join(
+                f'<li>{_pill(it["status"], _label(it))} <b>{e(it["name"])}</b>'
+                + (f' — {e(it["detail"])}' if it.get("detail") else "") + "</li>"
+                for it in r["items"]) + "</ul></td></tr>"
+        trs.append(
+            f'<tr data-phase="{e(r["phase"])}" data-st="{e(r["status"])}"><td class="g">{e(r["title"])}</td>'
+            f'<td class="st">{_pill(r["status"], _label(r))}</td>'
+            f'<td class="mono">{_when(r.get("started"))}</td><td class="mono">{_when(r.get("finished"))}</td>'
+            f'<td>{planned}</td><td class="d">{e(r.get("entry") or "—")}</td>'
+            f'<td class="d">{e(r.get("exit") or "—")}</td></tr>{items}')
+    note = f'<p class="note"><b>{e(doc["note"])}</b></p>' if doc.get("note") else ""
+    return (f'{_CSS}\n<section id="phases">\n  <h2>Round {doc["round"]} phases</h2>\n  {note}\n'
+            f'  <p class="note">State as of {_when(doc["as_of"])} UTC, read from the round\'s phases file '
+            f'({e(where)}); the phases are the playbook\'s, in its order (<code>dev/audit/README.md</code>). '
+            'A phase the file does not list is drawn not started. A dash is a date the file does not '
+            'carry, never a guess; a dashed outline is a forecast window with its basis.'
+            + (' The fix waves are the group lanes below, on the same time axis; the stamps are the '
+               'planned-stamps table.' if axis else '') + '</p>\n'
+            f'  <div class="scroll">{timeline(doc, rows, axis)}</div>\n'
+            '  <div class="scroll"><table><thead><tr><th>Phase</th><th>Status</th>'
+            '<th>Started (UTC)</th><th>Finished (UTC)</th><th>Planned</th><th>Entry</th><th>Exit</th>'
+            f'</tr></thead><tbody>{"".join(trs)}</tbody></table></div>\n</section>\n')
+
+
+def shown(path: str | Path, repo: str | Path) -> str:
+    """How the page names the file: relative to the checkout, else its bare
+    name -- a host path never reaches a public page (`plan_public.py`)."""
+    p = Path(path).resolve()
+    try:
+        return p.relative_to(Path(repo).resolve()).as_posix()
+    except ValueError:
+        return p.name
+
+
+# ---------------------------------------------------------------- self-test
+
+def fixture() -> dict:
+    """A round with each status on a phase and on an item, a forecast with
+    its basis, and two phases (fix waves, closure) the file does not list."""
+    return {"round": 9, "as_of": "2026-01-05T12:00:00Z", "phases": [
+        {"phase": "round-start", "status": "done", "started": "2026-01-01T00:00:00Z",
+         "finished": "2026-01-02T00:00:00Z", "entry": "ENTRY-RS", "exit": "EXIT-RS",
+         "items": [{"name": "ITEM-HIDDEN", "status": "done"}]},
+        {"phase": "finders", "status": "running", "started": "2026-01-02T00:00:00Z",
+         "items": [{"name": "ITEM-DONE", "status": "done"},
+                   {"name": "ITEM-RUN", "status": "running", "detail": "DETAIL-RUN"},
+                   {"name": "ITEM-WAIT", "status": "waiting", "waiting_on": "QUEUE-X"},
+                   {"name": "ITEM-NOT", "status": "not-started"}]},
+        {"phase": "verify-judge", "status": "waiting", "waiting_on": "THE-JUDGE"},
+        {"phase": "plan", "status": "not-started",
+         "forecast": {"start_from": "2026-01-06T08:00:00Z", "start_to": "2026-01-06T20:00:00Z",
+                      "basis": "BASIS-PLAN"}},
+        {"phase": "stamps", "status": "not-started"}]}
+
+
+def fixture_checks(check) -> None:
+    """The phases arms of plan_page.py's self-test, which runs them: each
+    refusal against the fixture it refuses, and the drawing;
+    `check(name, ok, got)`."""
+    import copy
+    doc = fixture()
+    check("phases: the fixture is sound (null control)", violations(doc) == [], violations(doc))
+
+    def refuses(mutate, why):
+        d = copy.deepcopy(doc)
+        mutate(d)
+        got = violations(d)
+        check(f"phases: refused, {why}", any(why in b for b in got), got)
+    ph = lambda d, i: d["phases"][i]  # noqa: E731
+    refuses(lambda d: ph(d, 1).update(status="started"), "unknown status")
+    refuses(lambda d: ph(d, 1)["items"][0].update(status="ok"), "unknown status")
+    refuses(lambda d: d["phases"].reverse(), "out of the playbook's order")
+    refuses(lambda d: d["phases"].insert(1, dict(ph(d, 0))), "out of the playbook's order")
+    refuses(lambda d: ph(d, 0).update(phase="intake"), "unknown phase")
+    refuses(lambda d: ph(d, 2).pop("waiting_on"), "waiting on nothing named")
+    refuses(lambda d: ph(d, 1)["items"][2].pop("waiting_on"), "waiting on nothing named")
+    refuses(lambda d: ph(d, 4).update(started="2026-01-07T00:00:00Z"), "a date on a not-started phase")
+    refuses(lambda d: ph(d, 3)["forecast"].pop("basis"), "a forecast with no basis")
+    refuses(lambda d: ph(d, 1).update(finished="2026-01-03T00:00:00Z"), "finished on a phase not done")
+    refuses(lambda d: ph(d, 1).update(started="2 Jan"), "not ISO-8601 UTC")
+    rows = rows_of(doc)
+    check("phases: every playbook phase is a row, in order; an unlisted one is not started",
+          [r["phase"] for r in rows] == [p for p, _ in PHASES]
+          and [r["status"] for r in rows if r["phase"] in ("fix-waves", "closure")]
+          == ["not-started"] * 2, [(r["phase"], r["status"]) for r in rows])
+    s = section(doc, [], "dev/programme/round9/phases.json")
+    tr = {m.group(1): m.group(0) for m in re.finditer(r'<tr data-phase="([a-z-]+)".*?</tr>', s, re.S)}
+    check("phases: the section draws a row per phase in the playbook's order",
+          list(tr) == [p for p, _ in PHASES], list(tr))
+    check("phases: a phase with no date prints dashes, never a date or a zero",
+          all(tr[p].count('<td class="mono">—</td>') == 2 and "<td>—</td>" in tr[p]
+              and not re.search(r"\d", re.sub(r"<[^>]+>|data-[a-z]+=\"[^\"]*\"", "", tr[p]))
+              for p in ("stamps", "fix-waves", "closure")),
+          {p: tr.get(p, "")[:200] for p in ("stamps", "fix-waves", "closure")})
+    check("phases: a waiting phase names what it waits on", "waiting on THE-JUDGE" in tr["verify-judge"],
+          tr["verify-judge"][:300])
+    check("phases: a forecast prints its window and its basis",
+          "Tue 06 Jan 08:00" in tr["plan"] and "BASIS-PLAN" in tr["plan"]
+          and 'class="bar forecast"' in s, tr["plan"][:300])
+    items = s.split('data-phase="finders"', 1)[1].split('data-phase="verify-judge"', 1)[0]
+    check("phases: the running phase's items are drawn under it, each with its status",
+          all(x in items for x in ("ITEM-DONE", "ITEM-RUN", "DETAIL-RUN", "waiting on QUEUE-X",
+                                   "ITEM-NOT")), items[:400])
+    check("phases: a done phase's items are not drawn", "ITEM-HIDDEN" not in s)
+    check("phases: entry and exit are the file's words", "ENTRY-RS" in s and "EXIT-RS" in s)
+    bad = section(None, ["X: unknown status"], "f.json")
+    check("phases: an invalid file draws PHASES UNAVAILABLE, no table, no date",
+          "PHASES UNAVAILABLE" in bad and "<table" not in bad and "X: unknown status" in bad, bad)
+    # On the plan page's axis: cut at its ends, and saying so.
+    t = dt.datetime
+    cut = timeline(doc, rows_of(doc), (t(2026, 1, 1, 12), t(2026, 1, 6, 0)))
+    check("phases: on an axis starting inside a phase, the bar is cut and names its start",
+          "◂ since Thu 01 Jan 00:00" in cut, re.findall(r"◂[^<]*", cut))
+    late = timeline(doc, rows_of(doc), (t(2026, 1, 3), t(2026, 1, 5, 6)))
+    check("phases: a phase wholly before the axis and a forecast past it are named, not drawn",
+          "done, Thu 01 Jan 00:00 to Fri 02 Jan 00:00, off this axis" in late
+          and "past this axis" in late and 'class="bar forecast"' not in late
+          and "as of" not in late, re.findall(r"[^>]*axis<", late))
+    check("phases: null control, an axis holding every date cuts and omits nothing",
+          "◂" not in (whole := timeline(doc, rows_of(doc), (t(2025, 12, 31), t(2026, 1, 8))))
+          and "axis<" not in whole and "as of" in whole)
+    with tempfile.TemporaryDirectory() as td:
+        for n in (9, 11, 10):
+            (Path(td) / f"dev/programme/round{n}").mkdir(parents=True)
+            (Path(td) / f"dev/programme/round{n}/phases.json").write_text("{}")
+        (Path(td) / "dev/programme/roundx").mkdir()
+        (Path(td) / "dev/programme/roundx/phases.json").write_text("{}")
+        found = discover(td)
+        check("phases: discovery takes the highest-numbered round's file",
+              found is not None and found.parent.name == "round11", found)
+        check("phases: a host path is shown by its bare name, a checkout path relative",
+              shown(found, "/elsewhere") == "phases.json"
+              and shown(found, td) == "dev/programme/round11/phases.json")
+    with tempfile.TemporaryDirectory() as td:
+        check("phases: null control, a checkout with no phases file discovers none",
+              discover(td) is None)
+
+
+def page(doc, bad: list, where: str) -> str:
+    """The section alone as a page, in the plan page's stylesheet."""
+    import plan_page  # noqa: PLC0415 -- the stylesheet's one owner; imports this module
+    style = re.search(r"<style>.*?</style>", plan_page._TEMPLATE, re.S).group(0)
+    title = f"Round {doc['round']} Plan" if doc and not bad else "Round Plan"
+    return ("<!doctype html>\n<meta charset=\"utf-8\">\n"
+            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
+            f"<title>{html.escape(title)}</title>\n{style}\n<main>\n<header><h1>{html.escape(title)}</h1></header>\n"
+            f"{section(doc, bad, where)}</main>\n")
+
+
+def main(argv=None) -> int:
+    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    p.add_argument("--check", metavar="FILE", help="lint a phases file; exit 1 on a violation")
+    p.add_argument("--phases", metavar="FILE")
+    p.add_argument("--html", metavar="OUT", help="with --phases: the section alone as a page")
+    a = p.parse_args(argv)
+    path = a.check or a.phases
+    if not path:
+        p.error("--check FILE or --phases FILE --html OUT")
+    doc, bad = load(path)
+    for b in bad:
+        print(f"plan_phases: {path}: {b}", file=sys.stderr)
+    if a.html:
+        Path(a.html).write_text(page(doc, bad, shown(path, Path.cwd())), encoding="utf-8")
+        print(f"wrote {a.html}")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    sys.path.insert(0, str(Path(__file__).resolve().parent))
+    sys.exit(main())

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
