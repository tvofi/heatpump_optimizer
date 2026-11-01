# Review packet #3054
head: 361be3cd6cdc6a594b542956403220efdd4f0803
base: 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124722069904 neutral
arch-score / arch-score id=124721897558 success
arm id=124721812138 skipped
budget-raise-gate / budget-raise-gate id=124721897469 success
cancel-superseded id=124721812588 success
codeql / Analyze (actions) id=124721897434 success
codeql / Analyze (javascript-typescript) id=124721897428 success
codeql / Analyze (python) id=124721897527 in_progress
governance / delivery-status id=124721897456 success
governance / delivery-status-publish id=124721898297 skipped
governance / env-matrix id=124721897505 in_progress
governance / instrument-self-tests id=124721897458 in_progress
governance / policy-docs id=124721897533 in_progress
governance / record id=124721898250 skipped
governance / wave-script id=124721897525 success
hassfest / hassfest id=124721897415 success
kernel-points id=124721898701 skipped
prelude id=124721812654 in_progress
refresh id=124721812454 success
tests / arch-instrument id=124722006442 success
tests / briefs id=124721897443 success
tests / browser id=124722006448 in_progress
tests / closure-scope id=124721897482 success
tests / closures id=124722006516 in_progress
tests / coverage id=124722006528 in_progress
tests / fast (3.14) id=124722006517 in_progress
tests / mutation id=124721897487 success
tests / mutation-autofix id=124722063165 skipped
tests / mutation-pins id=124722062475 skipped
tests / nightly-ha id=124722007574 skipped
tests / nightly-status id=124721897476 success
tests / replay id=124722007839 skipped
tests / typing id=124722006484 success
validate / validate-hacs id=124721897431 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 14f2b3f6: #2505
NOTE body item 675e3fea: #2505
NOTE body item 2dc1b88f: R10-ORCH-LEDGER
NOTE body item ab6a9661: #2505
NOTE body item ba9e34f2: R10-ORCH-LEDGER
NOTE body item cdba48a9: #2505
CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs <roster>
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         GATE_SCOPE=auto bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/closure.py select
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff a7dd7f50d
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/audit/archscore/score.py --diff a7dd7f50d HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 10 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3054.md b/dev/programme/delivery/3054.md
new file mode 100644
index 000000000..edfb4aa6e
--- /dev/null
+++ b/dev/programme/delivery/3054.md
@@ -0,0 +1 @@
+- [#3054](https://github.com/tvofi/heatpump_optimizer/pull/3054) — **open**, R10-ORCH-ROSTER-SCHEMA (part 2): roster schema carries (R10-ORCH-ROSTER-SCHEMA)
diff --git a/tools/audit/carry_audit.py b/tools/audit/carry_audit.py
index d004c6b1f..e1d3a7765 100644
--- a/tools/audit/carry_audit.py
+++ b/tools/audit/carry_audit.py
@@ -6,6 +6,7 @@
     python3 -I tools/audit/carry_audit.py sweep (--prs N,N | --last N) [--from-dir DIR] [--issues]
                                          [--ledger FILE]
     python3 -I tools/audit/carry_audit.py owners REGEX [REGEX ...] [--ledger FILE]
+    python3 -I tools/audit/carry_audit.py roster [--open-issues FILE]
     python3 -I tools/audit/carry_audit.py --self-test
   (before the subcommand: --repo O/R, --briefs-dir DIR, --roster-ref REF, repeatable)
 
@@ -62,7 +63,13 @@ two `--roster-ref`, every carry or brief text the first holds and the second
 lacks (a roster PR cut from the second reverts it without a conflict); and
 `--ledger`, every orchestrator-ledger line saying `FINDING:` or `LESSON:`
 with no `Carry:` (the ledger's work-queue OWED lines are tasks, not read).
-`owners` is the sweep's owner-corpus search. EXIT 0 when every finding item
+`owners` is the sweep's owner-corpus search. `roster` is #2733's offline
+routing check over the roster alone: every pending carry on a done or
+absorbed group (STRANDED, by `roster_lib.pending_carries`; a carry a closed
+group held at `roster_lib.CARRY_CUTOVER` is legacy and exempt) and, given
+`--open-issues FILE`, every open issue but #201 that no live group lists
+(ISSUE-STRANDED when only closed groups do, ISSUE-UNLISTED when none does);
+`CARRY-ROSTER:` is its summary line. EXIT 0 when every finding item
 is routed to a valid destination; `CARRY-AUDIT:` is the summary line;
 `--self-test` prints `carry_audit self-test: N checks, 0 failed`. Reads only:
 `gh api` GETs, `git show`/`ls-tree`; nothing is written.
@@ -507,6 +514,53 @@ def ledger_unrouted(text: str) -> list[str]:
             if LEDGER_FINDING.search(ln) and not carry_dests(ln)]
 
 
+# --------------------------------------------------------------- the roster
+#: The one issue every seat writes to and no group owns (the round's log).
+LOG_ISSUE = 201
+
+
+def open_issue_numbers(text: str) -> set[int]:
+    """Open issue numbers from a JSON list: numbers, or gh's issue objects
+    (`gh issue list --json number`, or the REST list, whose pull requests carry
+    a `pull_request` key and are dropped)."""
+    out = set()
+    for x in json.loads(text):
+        if isinstance(x, int):
+            out.add(x)
+        elif isinstance(x, dict) and "pull_request" not in x and isinstance(x.get("number"), int):
+            out.add(x["number"])
+    return out
+
+
+def roster_report(roster: dict, legacy: dict, open_issues: set[int] | None) -> list[str]:
+    """#2733's invariants 1 and 3, offline. STRANDED: a pending carry
+    (`roster_lib.pending_carries`, the predicate set-stage and roster_sync
+    close a group by) on a group in `roster_lib.CARRY_CLOSED`. With an issue
+    list: ISSUE-STRANDED, an open issue only closed groups list; ISSUE-UNLISTED,
+    one no group lists. #201 is the log and is never reported. Without a list
+    the issue arm says nothing: absence is not a measurement."""
+    out = []
+    for gid, stage, i, text in roster_lib.stranded(roster, legacy):
+        into = (roster_lib.groups_of(roster)[gid].get("resume") or {}).get("absorbed_into")
+        where = f"absorbed into {into}" if stage == "absorbed" and into else stage
+        out.append(f"STRANDED {gid} ({where}) carry[{i}]: {text[:90]!r}")
+    if open_issues is None:
+        return out
+    listing: dict[int, list[tuple[str, bool]]] = {}
+    for gid, g in roster_lib.groups_of(roster).items():
+        live = (g.get("resume") or {}).get("stage") not in roster_lib.CARRY_CLOSED
+        for n in set(g.get("issues") or []) | set(g.get("fixes") or []):
+            listing.setdefault(n, []).append((gid, live))
+    for n in sorted(open_issues - {LOG_ISSUE}):
+        by = listing.get(n, [])
+        if not by:
+            out.append(f"ISSUE-UNLISTED #{n}")
+        elif not any(live for _, live in by):
+            out.append(f"ISSUE-STRANDED #{n} listed only by closed group(s): "
+                       + ", ".join(gid for gid, _ in by))
+    return out
+
+
 # ---------------------------------------------------------------- the owners
 def owner_corpus(repo: Path = ROOT, ref: str | None = None, briefs_dir: str | None = None,
                  ledger: str | None = None) -> list[tuple[str, str]]:
@@ -554,6 +608,9 @@ def main(argv: list[str]) -> int:
     o = sub.add_parser("owners")
     o.add_argument("pattern", nargs="+")
     o.add_argument("--ledger")
+    ro = sub.add_parser("roster")
+    ro.add_argument("--open-issues", help="a JSON list of the open issues "
+                    "(gh issue list --state open --json number)")
     a = p.parse_args(argv)
     ref = a.roster_ref[0] if a.roster_ref else None
     try:
@@ -565,6 +622,25 @@ def main(argv: list[str]) -> int:
             dests = load_dests(ROOT, ref, a.briefs_dir, gh_issue_state(a.repo))
             body, comments = read_pr(a.n, a.repo, None)
             return report(audit(body, comments, dests), f"#{a.n} ")
+        if a.cmd == "roster":
+            repo = str(ROOT)
+            rel = roster_lib.roster_path(repo, ref)
+            roster = (roster_lib.show_roster(repo, ref, rel) if ref
+                      else roster_lib.load_roster_file(str(ROOT / rel)))
+            legacy = roster_lib.read_legacy(repo, rel)
+            issues = (open_issue_numbers(Path(a.open_issues).read_text())
+                      if a.open_issues else None)
+            lines = roster_report(roster, legacy, issues)
+            for line in lines:
+                print(line)
+            cut = roster_lib.CARRY_CUTOVER.get(rel)
+            print(f"CARRY-ROSTER: {rel} at {ref or 'the tree'}; cut-over "
+                  f"{cut[:12] if cut else 'none'} ({sum(map(len, legacy.values()))} legacy "
+                  f"carries); {sum(ln.startswith('STRANDED') for ln in lines)} stranded "
+                  "carry(ies); issues "
+                  + (f"{len(issues)} open, {sum(ln.startswith('ISSUE') for ln in lines)} unrouted"
+                     if issues is not None else "not measured (no --open-issues)"))
+            return 1 if lines else 0
         if a.cmd == "owners":
             corpus = owner_corpus(ROOT, ref, a.briefs_dir, a.ledger)
             for pat in a.pattern:
@@ -1094,6 +1170,38 @@ def _self_test() -> int:
     check("carry_dests stops at prose", carry_dests("Carry: R10-LIVE because it owns x") == ["R10-LIVE"])
     check("carry_dests reads dismissed whole", carry_dests("Carry: dismissed: host load")
           == ["dismissed:host load"])
+    # THE ROSTER ARM (#2733 invariants 1 and 3; carries 23, 24, 26, 27). A
+    # pending carry on a closed group is STRANDED; an open issue no live group
+    # lists is reported, #201 never. Pure: the CLI only reads the roster, its
+    # cut-over and an issue list into it.
+    rr = {"groups": [
+        {"group": "S-DONE", "issues": [2733], "fixes": [], "resume": {"stage": "done"},
+         "carry": ["legacy owed", "owed after", "paid [implemented: 0123abcd]"]},
+        {"group": "S-ABS", "issues": [], "fixes": [], "carry": ["folded"],
+         "resume": {"stage": "absorbed", "absorbed_into": "S-LIVE"}},
+        {"group": "S-PAID", "issues": [2855], "fixes": [], "resume": {"stage": "done"},
+         "carry": ["x [dismissed: a duplicate]"]},
+        {"group": "S-LIVE", "issues": [2429], "fixes": [2500], "resume": {"stage": "carries-open"},
+         "carry": ["live owed"]},
+    ]}
+    lines = roster_report(rr, {"S-DONE": frozenset({"legacy owed"})}, {201, 2429, 2500, 2733, 2855, 2875})
+    stranded_l = [ln for ln in lines if ln.startswith("STRANDED")]
+    check("roster: a pending post-cut-over carry on a done group is STRANDED, with its index",
+          any(ln.startswith("STRANDED S-DONE (done) carry[1]") for ln in stranded_l))
+    check("roster: a carry on an absorbed group is STRANDED and names absorbed_into",
+          any(ln.startswith("STRANDED S-ABS (absorbed into S-LIVE) carry[0]") for ln in stranded_l))
+    check("roster (null): a legacy carry, a marked carry and an open group's carry are not STRANDED",
+          len(stranded_l) == 2)
+    check("roster: an open issue listed only by done groups is reported with them",
+          "ISSUE-STRANDED #2733 listed only by closed group(s): S-DONE" in lines
+          and "ISSUE-STRANDED #2855 listed only by closed group(s): S-PAID" in lines)
+    check("roster: an open issue no group lists is reported", "ISSUE-UNLISTED #2875" in lines)
+    check("roster (null): an issue a live group lists, in issues or fixes, and #201 are not reported",
+          not [ln for ln in lines if re.search(r"#(2429|2500|201)\b", ln)])
+    check("roster: with no issue list the issue arm reports nothing, never a guess",
+          not [ln for ln in roster_report(rr, {}, None) if ln.startswith("ISSUE")])
+    check("roster: open_issues reads gh's JSON, numbers or objects, and drops pull requests",
+          open_issue_numbers('[1, {"number": 2}, {"number": 3, "pull_request": {}}]') == {1, 2})
     print(f"carry_audit self-test: {passed + failed} checks, {failed} failed")
     tmp.cleanup()
     return 1 if failed else 0
diff --git a/tools/audit/seat/r10_roster_ops_mutants.py b/tools/audit/seat/r10_roster_ops_mutants.py
index eaae79b9b..bf0d4cc23 100644
--- a/tools/audit/seat/r10_roster_ops_mutants.py
+++ b/tools/audit/seat/r10_roster_ops_mutants.py
@@ -3,9 +3,10 @@
 
 Metric, one line per plant: `RESULT mutant=<name> rc=<rc> fails=<n>`, then the
 failing check names. Each plant is one exact one-occurrence replacement in
-tools/audit/seat/roster_edit.py; the driver applies it, runs
-`roster_edit.py --self-test`, and restores the file byte for byte. It refuses
-to start when the file differs from HEAD, so a restore cannot overwrite work.
+tools/audit/seat/roster_edit.py, or in the file a three-part plant names
+(`parts`); the driver applies it, runs that file's `--self-test`, and
+restores it byte for byte. It refuses to start when any target differs from
+HEAD, so a restore cannot overwrite work.
 Expected: every plant rc=1 with fails>=1 -- a FAIL line, not a crash (a
 crash is rc=1 with fails=0 and prints its tail).
 
@@ -27,6 +28,24 @@ Plants, one per refusal of the two ops and per round-trip property:
   T1-T5  the triage gate (decision 0015): the uncited proposal arm, a
          non-ACCEPT verdict passing, a missing batch read as an empty one, the gate's call
          in write_roster, and added_texts blind to appended carries.
+  K1-K9  the carry ledger (#2733): mark-carry's refusals (K1 a carry already
+         marked, K2 an unknown mark, K3 implemented without a sha, K4 the
+         whole moved arm, K5 a move to itself, K6 dismissed with no reason),
+         set-stage bypassing the shared closing rule (K7), the cut-over not
+         read (K8), and set-resume --field stage bypassing it (K9); a move
+         to a closed group (K10), a value holding `]` (K11), and an
+         unreadable cut-over read as no legacy by set-stage (K12).
+  L1-L6  roster_lib's predicate, under roster_lib.py --self-test: marks
+         ignored (L1), legacy ignored (L2), every group's carries legacy at
+         the cut-over (L3), absorbed not closed (L4), closing never
+         downgrades (L5), a mark read anywhere in the text (L6).
+  Y1-Y4  roster_sync: the merge bypassing the shared rule (Y1), an
+         unreadable cut-over read as no legacy (Y2), the write path's
+         re-derive without the legacy set (Y3), and apply_plan writing the
+         stage without it (Y4).
+  R1-R5  carry_audit's roster arm: closed-only issues unreported (R1),
+         unlisted issues unreported (R2), #201 reported (R3), absorbed_into
+         unnamed (R4), pull requests read as issues (R5).
   S1-S7  the vocabulary barrier (R10-ORCH-ROSTER-SCHEMA): each of the three
          stage-writing ops losing its classification check (S1 set-stage, S2
          set-resume --field stage, S3 append-group), append-group losing the
@@ -53,6 +72,11 @@ from pathlib import Path
 
 ROOT = Path(__file__).resolve().parents[3]
 TARGET = "tools/audit/seat/roster_edit.py"
+DROP = '    del g["carry"][_carry_index(g, index, match, "drop-carry")]\n'
+LIB, SYNC, AUDIT = ("tools/audit/seat/roster_lib.py",
+                    "tools/audit/seat/roster_sync.py", "tools/audit/carry_audit.py")
+_MARK_LINE = next((ln for ln in (ROOT / LIB).read_text().splitlines()
+                   if ln.startswith("_CARRY_MARK = ")), "_CARRY_MARK missing")
 DETACHED = ('g = next((x for x in roster.get("groups", []) '
             'if x.get("group") == group), {})')
 
@@ -67,21 +91,20 @@ PLANTS = {
            f'    {DETACHED}\n    after = [] if spec'),
     "A7": ('    g["after"] = after\n',
            '    g.pop("after", None)\n    g["after"] = after\n'),
-    "C1": ('    if not carry:\n        raise Refuse(f"drop-carry: {group} carries nothing")',
-           '    if False:\n        raise Refuse(f"drop-carry: {group} carries nothing")'),
+    "C1": ('    if not carry:\n        raise Refuse(f"{op}: {group} carries nothing")',
+           '    if False:\n        raise Refuse(f"{op}: {group} carries nothing")'),
     "C2": ("if match in c]\n", "if match in c] or [0]\n"),
     "C3": ("        if len(hits) > 1:\n", "        if False:\n"),
-    "C4": ("        if not 0 <= i < len(carry):\n",
-           "        if not i < len(carry):\n"),
-    "C5": ("            i = int(index)\n",
-           '            i = int(index) if index.lstrip("-").isdigit() else 0\n'),
-    "C6": ("    del carry[i]\n",
-           '    del carry[i]\n    if not carry:\n        del g["carry"]\n'),
-    "C7": ("    del carry[i]\n", "    del carry[i - 1]\n"),
-    "C8": ('    g = _need(roster, group)\n    carry = g.get("carry")',
-           f'    {DETACHED}\n    carry = g.get("carry")'),
+    "C4": ("    if not 0 <= i < len(carry):\n",
+           "    if not i < len(carry):\n"),
+    "C5": ("        i = int(index)\n",
+           '        i = int(index) if index.lstrip("-").isdigit() else 0\n'),
+    "C6": (DROP, DROP + '    if not g["carry"]:\n        del g["carry"]\n'),
+    "C7": (DROP, DROP.replace(')]', ') - 1]')),
+    "C8": ('    g = _need(roster, group)\n    del g["carry"]',
+           f'    {DETACHED}\n    g.setdefault("carry", [])\n    del g["carry"]'),
     "P1": ('p.error("drop-carry takes an index or --match, not both")', "pass"),
-    "P2": ('p.error("drop-carry needs an index or --match")', "pass"),
+    "P2": ('p.error(f"{a.op} needs an index or --match")', "pass"),
     "P3": ('p.error("--match is a drop-carry flag")', "pass"),
     "D1": ("return json.dumps(roster, indent=1)",
            "return json.dumps(roster, indent=2)"),
@@ -109,11 +132,70 @@ PLANTS = {
            "    if True:  # S6\n        return None\n"),
     "S7": ("        op_append_group(roster, value, rel, sizes)\n",
            "        op_append_group(roster, value)  # S7\n"),
+    "K1": ('    if roster_lib.carry_mark(g["carry"][i]):\n', "    if False:  # K1\n"),
+    "K2": ("    if kind not in roster_lib.CARRY_MARKS:\n", "    if False:  # K2\n"),
+    "K3": ('    if kind == "implemented" and not SHA_RE.match(arg):\n',
+           "    if False:  # K3\n"),
+    "K4": ('    if kind == "moved":\n', "    if False:  # K4\n"),
+    "K5": ("        if arg == group:\n", "        if False:  # K5\n"),
+    "K6": ('    if kind == "dismissed" and not arg:\n', "    if False:  # K6\n"),
+    "K7": ('["stage"] = _closing(g, stage, legacy, "set-stage")\n',
+           '["stage"] = stage  # K7\n'),
+    "K8": ("                    legacy = roster_lib.read_legacy(a.worktree, rel)\n",
+           "                    legacy = {}  # K8\n"),
+    "K9": ('        value = _closing(g, value, legacy, "set-resume")\n',
+           "        pass  # K9\n"),
+    "K10": ("        if stage in roster_lib.CARRY_CLOSED:\n",
+            "        if False:  # K10\n"),
+    "K11": ('    if "]" in arg:\n', "    if False:  # K11\n"),
+    "K12": ('raise Refuse(f"the carry cut-over is unreadable, so no "\n'
+            '                                 f"stage is written: {e}")',
+            "legacy = {}  # K12"),
+    "L1": (LIB, "            if carry_mark(c) is None and c not in held]\n",
+           "            if c not in held]  # L1\n"),
+    "L2": (LIB, "            if carry_mark(c) is None and c not in held]\n",
+           "            if carry_mark(c) is None]  # L2\n"),
+    "L3": (LIB, '            if (g.get("resume") or {}).get("stage") in CARRY_CLOSED}\n',
+           "            }  # L3\n"),
+    "L4": (LIB, 'CARRY_CLOSED = DONE_STAGES + ("absorbed",)\n',
+           "CARRY_CLOSED = DONE_STAGES  # L4\n"),
+    "L5": (LIB, '    return ("carries-open" if pending else "done"), pending\n',
+           '    return "done", pending  # L5\n'),
+    # L6 reads the mark's grammar from roster_lib's own line: a second
+    # spelling of it here would be the grammar written twice (agreement.mjs).
+    "L6": (LIB, _MARK_LINE, _MARK_LINE.replace('\\Z")', '")') + "  # L6"),
+    "Y1": (SYNC, '        closed, _ = roster_lib.closing_stage(g, "done", legacy or {})\n',
+           '        closed = "done"  # Y1\n'),
+    "Y2": (SYNC, '            raise Refuse(f"the carry cut-over is unreadable: {e}")\n',
+           "            legacy = {}  # Y2\n"),
+    "Y3": (SYNC, "            changes, _, transitions = derive(roster, prs, legacy)\n",
+           "            changes, _, transitions = derive(roster, prs)  # Y3\n"),
+    "Y4": (SYNC, "        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit,\n"
+                 "                                 legacy=legacy)\n",
+           "        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit)"
+           "  # Y4\n"),
+    "R1": (AUDIT, "        elif not any(live for _, live in by):\n",
+           "        elif False:  # R1\n"),
+    "R2": (AUDIT, "        if not by:\n", "        if False:  # R2\n"),
+    "R3": (AUDIT, "    for n in sorted(open_issues - {LOG_ISSUE}):\n",
+           "    for n in sorted(open_issues):  # R3\n"),
+    "R4": (AUDIT, '        where = f"absorbed into {into}" if stage == "absorbed" and into else stage\n',
+           "        where = stage  # R4\n"),
+    "R5": (AUDIT, '        elif isinstance(x, dict) and "pull_request" not in x and isinstance(x.get("number"), int):\n',
+           '        elif isinstance(x, dict) and isinstance(x.get("number"), int):  # R5\n'),
 }
 
 
-def target_self_test():
-    r = subprocess.run([sys.executable, TARGET, "--self-test"], cwd=ROOT,
+def parts(name):
+    """(target, old, new) of a plant: roster_edit.py unless the plant names
+    its file. Every target is a Python tool whose `--self-test` prints FAIL
+    lines, so one driver reads them all."""
+    plant = PLANTS[name]
+    return plant if len(plant) == 3 else (TARGET,) + plant
+
+
+def target_self_test(target=TARGET):
+    r = subprocess.run([sys.executable, target, "--self-test"], cwd=ROOT,
                        capture_output=True, text=True)
     fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
     return r.returncode, fails, (r.stdout + r.stderr).strip().splitlines()[-3:]
@@ -141,12 +223,13 @@ def self_test():
         passed, failed = passed + ok, failed + (not ok)
         print(f"  {'ok  ' if ok else 'FAIL'} {name}")
 
-    text = (ROOT / TARGET).read_text()
-    for name, (old, new) in PLANTS.items():
-        ck(f"{name}: anchor occurs once in {TARGET}", text.count(old) == 1)
+    for name in PLANTS:
+        target, old, new = parts(name)
+        text = (ROOT / target).read_text()
+        ck(f"{name}: anchor occurs once in {target}", text.count(old) == 1)
         ck(f"{name}: the plant changes the text", new != old)
         try:
-            compile(text.replace(old, new), TARGET, "exec")
+            compile(text.replace(old, new), target, "exec")
             ok = True
         except SyntaxError:
             ok = False
@@ -178,38 +261,41 @@ def self_test():
 
 
 def main(argv):
-    path = ROOT / TARGET
     if argv == ["--self-test"]:
         return self_test()
-    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", TARGET],
+    targets = sorted({parts(n)[0] for n in PLANTS})
+    if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *targets],
                       cwd=ROOT).returncode != 0:
-        print(f"refusing: {TARGET} differs from HEAD", file=sys.stderr)
+        print(f"refusing: one of {targets} differs from HEAD", file=sys.stderr)
         return 2
     if argv == ["--null"]:
-        report("null", *target_self_test())
+        for target in targets:
+            report(f"null {target}", *target_self_test(target))
         return 0
     names, unknown = select(argv)
     if unknown:
         print(f"unknown plant(s): {unknown}", file=sys.stderr)
         return 2
-    original = path.read_bytes()
+    originals = {t: (ROOT / t).read_bytes() for t in targets}
     survivors = []
     try:
         for name in names:
-            old, new = PLANTS[name]
+            target, old, new = parts(name)
+            path, original = ROOT / target, originals[target]
             text = original.decode("utf-8")
             if text.count(old) != 1:
                 print(f"plant {name}: anchor occurs {text.count(old)} times",
                       file=sys.stderr)
                 return 2
             path.write_bytes(text.replace(old, new).encode("utf-8"))
-            rc, fails, tail = target_self_test()
+            rc, fails, tail = target_self_test(target)
             path.write_bytes(original)
             report(name, rc, fails, tail)
             if not fails:
                 survivors.append(name)
     finally:
-        path.write_bytes(original)
+        for target, original in originals.items():
+            (ROOT / target).write_bytes(original)
     print(f"plants: {len(names)}, without a FAIL line: {survivors or 'none'}")
     return 1 if survivors else 0
 
diff --git a/tools/audit/seat/r10_roster_sync_mutants.py b/tools/audit/seat/r10_roster_sync_mutants.py
index b38af7906..5f91fea8e 100644
--- a/tools/audit/seat/r10_roster_sync_mutants.py
+++ b/tools/audit/seat/r10_roster_sync_mutants.py
@@ -76,9 +76,9 @@ PLANTS = {
         (SRC, "            if stage != \"in-progress\" or resume.get(\"pr\") != pr.number:",
               "            if False:  # M2")],
     "M3_merged_without_commit": [
-        (SRC, "        changes.append(Change(gid, \"done\", pr.number, pr.merge_commit,\n"
+        (SRC, "        changes.append(Change(gid, closed, pr.number, pr.merge_commit,\n"
               "                              stage, pr.state))",
-              "        changes.append(Change(gid, \"done\", pr.number, None,\n"
+              "        changes.append(Change(gid, closed, pr.number, None,\n"
               "                              stage, pr.state))  # M3")],
     "M4_carry_to_done_appended": [
         (SRC, "                elif not roster_lib.is_open(g):",
diff --git a/tools/audit/seat/roster_edit.py b/tools/audit/seat/roster_edit.py
index f1d132ceb..27be37c9b 100644
--- a/tools/audit/seat/roster_edit.py
+++ b/tools/audit/seat/roster_edit.py
@@ -10,6 +10,8 @@
     python3 tools/audit/seat/roster_edit.py set-resume  <group> --field <stage|commit|branch|last_step|next_step|note> <text | @file>
     python3 tools/audit/seat/roster_edit.py set-after   <group> <G1,G2,... | ->
     python3 tools/audit/seat/roster_edit.py drop-carry  <group> <index | --match TEXT>
+    python3 tools/audit/seat/roster_edit.py mark-carry  <group> <index | --match TEXT>
+        implemented <sha> | moved <GROUP> | dismissed <reason>
         [--at-sha SHA] [--checkout DIR] [--roster-ref BR] [--branch OUT]
         [--roster-path PATH] [--worktree DIR] [--lint-cwd DIR] [--push]
         [--message MSG]
@@ -64,7 +66,12 @@ whose brief text the linter refuses is refused at the same gate, before
 anything reaches GitHub.
 
 Ops (all group ids must exist, except append-group which must not):
-  set-stage    sets resume.stage (and resume.commit with --at-sha);
+  set-stage    sets resume.stage (and resume.commit with --at-sha); `done`
+               over a pending carry is written `carries-open` and printed
+               `set-stage <G>: done -> carries-open (<n> pending carries)`,
+               rc 0 -- never a refusal (#2733): roster_lib.closing_stage,
+               the predicate roster_sync's merge shares (set-resume --field
+               stage reads it too);
   wire-issue   appends an integer issue (to `fixes` with --field fixes),
                refusing a duplicate;
   unwire-issue removes an integer from `issues` (default) or, with
@@ -98,6 +105,13 @@ resolve is refused whether or not the text names a proposal.
                last entry leaves the `carry` list empty, never removing the
                key (27 of the 91 live groups carry `"carry": []`, and none
                omits it, so the key's presence is the file's own shape).
+  mark-carry   discharges one carry (selected as drop-carry selects) by
+               appending `[implemented: <sha>]`, `[moved: <GROUP>]` (an
+               existing open group) or `[dismissed: <reason>]`; refuses a
+               carry already marked. `implemented` records that the sha is
+               on main; it is not a verification. A carry that sat on a
+               closed group at roster_lib.CARRY_CUTOVER is legacy and needs
+               no mark.
 """
 
 from __future__ import annotations
@@ -151,7 +165,7 @@ def run(cmd, cwd=None):
 
 
 # ----------------------------------------------------------------- ops
-def op_set_stage(roster, group, stage, at_sha, rel=""):
+def op_set_stage(roster, group, stage, at_sha, rel="", legacy=None):
     g = _need(roster, group)
     if not isinstance(stage, str) or not stage.strip():
         raise Refuse("stage must be a non-empty string")
@@ -160,7 +174,7 @@ def op_set_stage(roster, group, stage, at_sha, rel=""):
         raise Refuse(why)
     if at_sha and not SHA_RE.match(at_sha):
         raise Refuse(f"--at-sha is not a sha: {at_sha!r}")
-    g.setdefault("resume", {})["stage"] = stage
+    g.setdefault("resume", {})["stage"] = _closing(g, stage, legacy, "set-stage")
     if at_sha:
         g["resume"]["commit"] = at_sha
 
@@ -175,7 +189,7 @@ NON_NULL_RESUME_FIELDS = ("stage", "branch")
 TEXT_RESUME_FIELDS = ("last_step", "next_step", "note")
 
 
-def op_set_resume(roster, group, field, value, rel=""):
+def op_set_resume(roster, group, field, value, rel="", legacy=None):
     g = _need(roster, group)
     if field not in RESUME_FIELDS:
         # argparse's --field choices refuse it first; this guards direct callers
@@ -193,10 +207,25 @@ def op_set_resume(roster, group, field, value, rel=""):
             raise Refuse(why)
     if field == "commit" and not SHA_RE.match(value):
         raise Refuse(f"--field commit needs a sha: {value!r}")
+    if field == "stage":
+        value = _closing(g, value, legacy, "set-resume")
     resume = g.setdefault("resume", {})
     resume[field] = _text(value) if field in TEXT_RESUME_FIELDS else value
 
 
+def _closing(g, stage, legacy, op):
+    """The stage `op` writes for `stage`: roster_lib.closing_stage, the one
+    rule roster_sync's merge applies too. A downgrade is printed with the
+    issues the group wires, which stay wired; nothing is refused (#2733)."""
+    wrote, pending = roster_lib.closing_stage(g, stage, legacy or {})
+    if wrote != stage:
+        wired = sorted(set(g.get("issues") or []) | set(g.get("fixes") or []))
+        print(f"{op} {g.get('group')}: {stage} -> {wrote} "
+              f"({len(pending)} pending carries)"
+              + (f"; wires {' '.join(f'#{n}' for n in wired)}" if wired else ""))
+    return wrote
+
+
 WIRE_FIELDS = ("issues", "fixes")
 
 
@@ -340,37 +369,76 @@ def op_drop_carry(roster, group, index=None, match=None):
     group that already carries a list (all 91 live ones do) is therefore
     byte-restored by append-then-drop of the appended entry."""
     g = _need(roster, group)
-    carry = g.get("carry") or []
+    del g["carry"][_carry_index(g, index, match, "drop-carry")]
+
+
+def _carry_index(g, index, match, op):
+    """The one carry entry `op` names: by 0-based index or by the one entry
+    containing `match`; absent, out of range, unmatched and ambiguous refuse."""
+    group, carry = g.get("group"), g.get("carry") or []
     if not carry:
-        raise Refuse(f"drop-carry: {group} carries nothing")
+        raise Refuse(f"{op}: {group} carries nothing")
     if match is not None:
         hits = [i for i, c in enumerate(carry) if match in c]
         if not hits:
-            raise Refuse(f"drop-carry: no carry entry matches {match!r} "
+            raise Refuse(f"{op}: no carry entry matches {match!r} "
                          f"in {group}")
         if len(hits) > 1:
-            raise Refuse(f"drop-carry: {match!r} is ambiguous in {group}: "
+            raise Refuse(f"{op}: {match!r} is ambiguous in {group}: "
                          f"entries {hits} match; pass an index")
-        i = hits[0]
-    else:
-        try:
-            i = int(index)
-        except ValueError:
-            raise Refuse(f"drop-carry: index must be an integer: {index!r}")
-        if not 0 <= i < len(carry):
-            raise Refuse(f"drop-carry: index {i} out of range for {group} "
-                         f"({len(carry)} entries)")
-    del carry[i]
+        return hits[0]
+    try:
+        i = int(index)
+    except ValueError:
+        raise Refuse(f"{op}: index must be an integer: {index!r}")
+    if not 0 <= i < len(carry):
+        raise Refuse(f"{op}: index {i} out of range for {group} "
+                     f"({len(carry)} entries)")
+    return i
+
+
+def op_mark_carry(roster, group, index, match, kind, arg):
+    """Discharge one carry by appending its mark (roster_lib.carry_mark's
+    grammar), so roster_lib.pending_carries stops counting it."""
+    g = _need(roster, group)
+    i = _carry_index(g, index, match, "mark-carry")
+    if roster_lib.carry_mark(g["carry"][i]):
+        raise Refuse(f"mark-carry: {group} carry[{i}] is already marked "
+                     f"{roster_lib.carry_mark(g['carry'][i])}")
+    if kind not in roster_lib.CARRY_MARKS:
+        raise Refuse(f"mark-carry: the mark is one of "
+                     f"{', '.join(roster_lib.CARRY_MARKS)}, not {kind!r}")
+    arg = " ".join((arg or "").split())
+    if kind == "implemented" and not SHA_RE.match(arg):
+        raise Refuse(f"mark-carry: implemented needs a sha: {arg!r}")
+    if kind == "moved":
+        dest = next((x for x in roster.get("groups", [])
+                     if x.get("group") == arg), None)
+        if dest is None:
+            raise Refuse(f"mark-carry: moved {arg!r} names no group")
+        if arg == group:
+            raise Refuse(f"mark-carry: {group} cannot move a carry to itself")
+        stage = (dest.get("resume") or {}).get("stage")
+        if stage in roster_lib.CARRY_CLOSED:
+            raise Refuse(f"mark-carry: moved {arg} is {stage}; a carry moves "
+                         "to an open group")
+    if kind == "dismissed" and not arg:
+        raise Refuse("mark-carry: dismissed needs a reason")
+    if "]" in arg:
+        raise Refuse(f"mark-carry: a mark's value holds no ']': {arg!r}")
+    g["carry"][i] = f"{g['carry'][i]} [{kind}: {arg}]"
 
 
 def apply_op(roster, op, group, value, field, at_sha, match=None, rel="",
-             sizes=()):
+             sizes=(), legacy=None, rest=()):
     """One op on a loaded roster -- re-run on each attempt of a push race,
     so the edit is applied to the tip it is pushed onto. `rel` is the roster's
     path and `sizes` the duration model's vocabulary, for a refusal to name
-    what it refused; only append-group reads `sizes`."""
+    what it refused; only append-group reads `sizes`. `legacy` is the
+    roster's cut-over carries (roster_lib.read_legacy), which a stage write
+    reads; `rest` is mark-carry's `<kind> <value...>`."""
     if op == "set-stage":
-        op_set_stage(roster, group, value, at_sha, rel)
+        op_set_stage(roster, group, value, at_sha, rel, legacy)
     elif op == "wire-issue":
         op_wire_issue(roster, group, value, field or "issues")
     elif op == "unwire-issue":
@@ -380,11 +448,14 @@ def apply_op(roster, op, group, value, field, at_sha, match=None, rel="",
     elif op == "edit-brief":
         op_edit_brief(roster, group, value)
     elif op == "set-resume":
-        op_set_resume(roster, group, field, value, rel)
+        op_set_resume(roster, group, field, value, rel, legacy)
     elif op == "set-after":
         op_set_after(roster, group, value)
     elif op == "drop-carry":
         op_drop_carry(roster, group, value, match)
+    elif op == "mark-carry":
+        kind, *arg = list(rest) or [""]
+        op_mark_carry(roster, group, value, match, kind, " ".join(arg))
     else:
         op_append_carry(roster, group, value)
 
@@ -742,9 +813,12 @@ def main(argv=None) -> int:
     p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
     p.add_argument("op", choices=("set-stage", "wire-issue", "unwire-issue", "append-group",
                                   "edit-brief", "append-carry", "set-resume",
-                                  "set-after", "drop-carry"))
+                                  "set-after", "drop-carry", "mark-carry"))
     p.add_argument("group")
     p.add_argument("value", nargs="?")
+    p.add_argument("rest", nargs="*",
+                   help="mark-carry: implemented <sha> | moved <GROUP> | "
+                        "dismissed <reason>")
     p.add_argument("--at-sha")
     p.add_argument("--field", choices=RESUME_FIELDS + WIRE_FIELDS,
                    help="set-resume: which resume field to write; "
@@ -752,7 +826,8 @@ def main(argv=None) -> int:
     p.add_argument("--value", dest="value_opt",
                    help="the value, for when a positional value does not fit")
     p.add_argument("--match",
-                   help="drop-carry: drop the one carry entry containing it")
+                   help="drop-carry, mark-carry: the one carry entry "
+                        "containing it")
     p.add_argument("--checkout", default=".")
     p.add_argument("--roster-ref", default=None,
                    help="the base ref (default main)")
@@ -766,16 +841,25 @@ def main(argv=None) -> int:
     p.add_argument("--lint-cwd")
     p.add_argument("--push", action="store_true")
     p.add_argument("--message")
-    a = p.parse_args(argv)
+    a = p.parse_intermixed_args(argv)
+    rest = list(a.rest)
+    if a.op == "mark-carry" and a.match is not None and a.value is not None:
+        # with --match there is no index: the first positional is the kind
+        rest, a.value = [a.value] + rest, None
+    if rest and a.op != "mark-carry":
+        p.error(f"{a.op} takes one value; extra arguments: {rest}")
+    if a.op == "mark-carry" and not rest:
+        p.error("mark-carry needs implemented <sha>, moved <GROUP> or "
+                "dismissed <reason>")
     if a.value is not None and a.value_opt is not None:
         p.error("give the value positionally or with --value, not both")
     value = a.value_opt if a.value is None else a.value
-    if a.match is not None and a.op != "drop-carry":
+    if a.match is not None and a.op not in ("drop-carry", "mark-carry"):
         p.error("--match is a drop-carry flag")
     if a.op == "drop-carry" and value is not None and a.match is not None:
         p.error("drop-carry takes an index or --match, not both")
-    if a.op == "drop-carry" and value is None and a.match is None:
-        p.error("drop-carry needs an index or --match")
+    if a.op in ("drop-carry", "mark-carry") and value is None and a.match is None:
+        p.error(f"{a.op} needs an index or --match")
     if a.match is None and (value is None
                             or (value == "" and a.op != "set-resume")):
         p.error(f"{a.op} needs a value argument")
@@ -807,8 +891,15 @@ def main(argv=None) -> int:
                         roster_lib.read_durations(a.worktree))
                 except roster_lib.SchemaError as e:
                     raise Refuse(str(e))
+            legacy = None
+            if a.op in ("set-stage", "set-resume"):
+                try:
+                    legacy = roster_lib.read_legacy(a.worktree, rel)
+                except roster_lib.RosterNotFound as e:
+                    raise Refuse(f"the carry cut-over is unreadable, so no "
+                                 f"stage is written: {e}")
             apply_op(roster, a.op, a.group, value, a.field, a.at_sha, a.match,
-                     rel, sizes)
+                     rel, sizes, legacy, rest)
             return True
         return write_roster(a.checkout, ref, branch, a.worktree, a.roster_path,
                             msg, a.push, a.lint_cwd, f"{a.op} {a.group}", edit)
@@ -942,10 +1033,12 @@ def _self_test() -> int:
     throwaway_git_clone(origin, drv, "-q")
 
     def edit(op, group, value, push=True, branch="edit-1", lint_cwd=None,
-             at_sha=None, field=None, value_opt=None, match=None, wt="wt"):
+             at_sha=None, field=None, value_opt=None, match=None, wt="wt",
+             rest=()):
         args = [op, group]
         if value is not None:
             args += [value]
+        args += list(rest)
         if field:
             args += ["--field", field]
         if match is not None:
@@ -1304,6 +1397,121 @@ def _self_test() -> int:
     check("append-carry then drop-carry is byte-identical",
           bytes_at() == before_carry)
 
+    # THE CARRY LEDGER (#2733, carries 10 and 31). mark-carry discharges one
+    # carry with a mark; set-stage done over a pending carry writes
+    # carries-open through roster_lib.closing_stage, the predicate roster_sync
+    # shares. On a branch of its own, so the byte pins above are untouched.
+    def said(call):
+        out, err = io.StringIO(), io.StringIO()
+        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
+            rc = sysrc(call)
+        return rc, out.getvalue() + err.getvalue()
+
+    def mark(*rest, match=None):
+        return said(lambda: edit("mark-carry", "R9-B",
+                                 None if match is not None else rest[0],
+                                 branch="mark-1", match=match,
+                                 rest=rest if match is not None else rest[1:]))
+
+    def at_mark(group):
+        return next(g for g in branch_roster("mark-1")["groups"]
+                    if g["group"] == group)
+
+    for text in ("carry one", "carry two", "carry three"):
+        edit("append-carry", "R9-B", text, branch="mark-1")
+    rc, out = mark("0", "implemented", "0123abcd")
+    check("mark-carry by index appends the implemented mark",
+          rc == 0 and at_mark("R9-B")["carry"][0]
+          == "carry one [implemented: 0123abcd]", (rc, out[-300:]))
+    rc, out = mark("moved", "R9-A", match="carry two")
+    check("mark-carry by --match appends the moved mark",
+          rc == 0 and at_mark("R9-B")["carry"][1] == "carry two [moved: R9-A]",
+          (rc, out[-300:]))
+    t0 = tip("mark-1")
+    for name, args, why in (
+            ("a carry already marked", ("0", "dismissed", "again"), "already marked"),
+            ("an unknown mark", ("2", "shipped", "0123abcd"), "mark is one of"),
+            ("implemented without a sha", ("2", "implemented", "main"), "needs a sha"),
+            ("moved to no group", ("2", "moved", "R9-ZZ"), "names no group"),
+            ("moved to itself", ("2", "moved", "R9-B"), "to itself"),
+            ("dismissed with no reason", ("2", "dismissed"), "needs a reason")):
+        rc, out = mark(*args)
+        check(f"mark-carry refuses {name}", rc not in (0, None) and why in out,
+              (rc, out[-300:]))
+    check("refused mark-carry moved nothing", tip("mark-1") == t0)
+    rc, out = said(lambda: edit("set-stage", "R9-B", "done", branch="mark-1"))
+    check("set-stage done over a pending carry writes carries-open and says so",
+          rc == 0 and at_mark("R9-B")["resume"]["stage"] == "carries-open"
+          and "set-stage R9-B: done -> carries-open (1 pending carries)" in out,
+          (rc, at_mark("R9-B")["resume"], out[-300:]))
+    mark("2", "dismissed", "a duplicate of carry two")
+    rc, out = said(lambda: edit("set-stage", "R9-B", "done", branch="mark-1"))
+    check("set-stage done with every carry marked writes done (null control)",
+          rc == 0 and at_mark("R9-B")["resume"]["stage"] == "done",
+          (rc, at_mark("R9-B")["resume"], out[-300:]))
+    # A carry moves only to an open group, and a mark's value never holds the
+    # `]` that would end carry_mark's grammar early (review X7, X8). R9-A is
+    # put in each closed stage in turn; each refusal leaves the branch where it
+    # was, and the null controls -- an open destination, a plain value -- land.
+    edit("append-carry", "R9-B", "carry four", branch="mark-1")
+    edit("append-carry", "R9-B", "carry five", branch="mark-1")
+    for closed in roster_lib.CARRY_CLOSED:
+        edit("set-stage", "R9-A", closed, branch="mark-1")
+        t1 = tip("mark-1")
+        rc, out = mark("3", "moved", "R9-A")
+        check(f"mark-carry refuses moved to a {closed} group",
+              rc not in (0, None) and f"moved R9-A is {closed}" in out
+              and tip("mark-1") == t1, (rc, out[-300:]))
+    t1 = tip("mark-1")
+    rc, out = mark("3", "dismissed", "a]b")
+    check("mark-carry refuses a value holding ']'",
+          rc not in (0, None) and "holds no ']'" in out
+          and tip("mark-1") == t1, (rc, out[-300:]))
+    edit("set-stage", "R9-A", "in-progress", branch="mark-1")
+    rc, out = mark("3", "moved", "R9-A")
+    check("mark-carry moved to an open group lands (null control)",
+          rc == 0 and at_mark("R9-B")["carry"][3] == "carry four [moved: R9-A]",
+          (rc, out[-300:]))
+    rc, out = mark("4", "dismissed", "ab")
+    check("mark-carry with a plain value lands (null control)",
+          rc == 0 and at_mark("R9-B")["carry"][4] == "carry five [dismissed: ab]",
+          (rc, out[-300:]))
+    # The cut-over: a carry on a closed group at the cut-over commit is legacy
+    # and never pending; one appended after it is.
+    edit("set-stage", "R9-A", "done", branch="mark-1")
+    edit("append-carry", "R9-A", "legacy carry", branch="mark-1")
+    saved = dict(roster_lib.CARRY_CUTOVER)
+    roster_lib.CARRY_CUTOVER[FIXTURE_ROSTER] = tip("mark-1")
+    try:
+        rc, out = said(lambda: edit("set-stage", "R9-A", "done", branch="mark-1"))
+        check("a legacy carry alone leaves set-stage done as done (null control)",
+              rc == 0 and at_mark("R9-A")["resume"]["stage"] == "done",
+              (rc, out[-300:]))
+        edit("append-carry", "R9-A", "post-cut-over carry", branch="mark-1")
+        rc, out = said(lambda: edit("set-stage", "R9-A", "done", branch="mark-1"))
+        check("a carry after the cut-over is pending beside a legacy one",
+              rc == 0 and at_mark("R9-A")["resume"]["stage"] == "carries-open"
+              and "(1 pending carries)" in out, (rc, out[-300:]))
+        rc, out = said(lambda: edit("set-resume", "R9-A", "done", field="stage",
+                                    branch="mark-1"))
+        check("set-resume --field stage done reads the same rule",
+              rc == 0 and at_mark("R9-A")["resume"]["stage"] == "carries-open"
+              and "set-resume R9-A: done -> carries-open" in out, (rc, out[-300:]))
+        # An unreadable cut-over refuses the stage write and writes nothing
+        # (review X6): read as "no legacy", the legacy carry would be pending.
+        # The readable null is the "legacy carry alone" check above.
+        roster_lib.CARRY_CUTOVER[FIXTURE_ROSTER] = "f" * 40
+        t1 = tip("mark-1")
+        for op, kw in (("set-stage", {}), ("set-resume", {"field": "stage"})):
+            rc, out = said(lambda: edit(op, "R9-A", "done", branch="mark-1",
+                                        **kw))
+            check(f"{op} refuses an unreadable cut-over and writes nothing",
+                  rc == 2 and "the carry cut-over is unreadable" in out
+                  and tip("mark-1") == t1, (rc, out[-300:]))
+    finally:
+        roster_lib.CARRY_CUTOVER.clear()
+        roster_lib.CARRY_CUTOVER.update(saved)
+
     # THE ROUND-TRIP REGRESSION. The roster's canonical bytes are indent=1,
     # ASCII-escaped, no trailing newline (the file at the fixplan ref). A dump
     # that does not reproduce them rewrites every line of the file on ANY edit
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index ee978de00..e520976b2 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -347,6 +347,85 @@ def open_groups(roster: dict) -> dict:
     return {k: g for k, g in groups_of(roster).items() if is_open(g)}
 
 
+# ------------------------------------------------------------ the carry ledger
+#
+# #2733's first invariant: a carry not yet implemented routes to a group that
+# is not done. ONE predicate (`pending_carries`) says which carries a group
+# still owes; `roster_edit.py set-stage`, `roster_sync.py`'s merge transition
+# and `carry_audit.py roster` all read it, so the writer that closes a group,
+# the reconciler that closes it on a merge and the audit that reports a
+# stranded carry cannot disagree.
+#
+# A carry is discharged by a mark `roster_edit.py mark-carry` appends to its
+# text, `[implemented: <sha>]`, `[moved: <GROUP>]` or `[dismissed: <reason>]`.
+# `implemented` records that the sha is on main; it is not a verification.
+CARRY_MARKS = ("implemented", "moved", "dismissed")
+_CARRY_MARK = re.compile(r" \[(implemented|moved|dismissed): ([^\]\n]+)\]\Z")
+#: The stages in which a group can no longer receive or discharge a carry: the
+#: closed ones, and `absorbed`, whose work lives in its fold destination.
+CARRY_CLOSED = DONE_STAGES + ("absorbed",)
+#: THE CUT-OVER, per roster path: a carry that sat on a closed group at this
+#: roster-branch commit is LEGACY and is never reported, so the invariant
+#: starts at the cut-over with no blanket migration and nothing marked
+#: implemented by default (#2733's design, carry 10(a)). A roster with no entry
+#: has no legacy carries. Changing the cut-over is a change to this line.
+CARRY_CUTOVER = {
+    f"{ROSTERS_DIR}/wave-r10-groups.json":
+        "a4c9fa3d629017fb1a0e5394bbae79cdbdfa4f9b",
+}
+
+
+def carry_mark(text: str) -> tuple[str, str] | None:
+    """(kind, value) of the mark ending `text`, or None when it carries none."""
+    m = _CARRY_MARK.search(text) if isinstance(text, str) else None
+    return (m.group(1), m.group(2)) if m else None
+
+
+def legacy_carries(cutover_roster: dict | None) -> dict:
+    """group -> the carry texts it held while closed at the cut-over."""
+    return {g["group"]: frozenset(c for c in g.get("carry") or []
+                                  if isinstance(c, str))
+            for g in (cutover_roster or {}).get("groups", [])
+            if (g.get("resume") or {}).get("stage") in CARRY_CLOSED}
+
+
+def read_legacy(repo: str, path: str) -> dict:
+    """The legacy carries of the roster at `path`, read at its cut-over commit
+    in `repo`; {} for a roster with no cut-over. A cut-over the clone cannot
+    read raises RosterNotFound: unknowable is a refusal, never 'no legacy',
+    which would report every old carry as stranded."""
+    sha = CARRY_CUTOVER.get(path)
+    return legacy_carries(show_roster(repo, sha, path)) if sha else {}
+
+
+def pending_carries(group: dict, legacy: dict) -> list:
+    """Indices of the carries `group` still owes: unmarked and not legacy."""
+    held = legacy.get(group.get("group"), frozenset())
+    return [i for i, c in enumerate(group.get("carry") or [])
+            if carry_mark(c) is None and c not in held]
+
+
+def closing_stage(group: dict, stage: str, legacy: dict) -> tuple[str, list]:
+    """The stage to write when `stage` is asked for, and the pending carries
+    that decided it: `done` over a pending carry is written `carries-open`,
+    which keeps the group in replan and dispatch. Never a refusal (#2733)."""
+    if stage != "done":
+        return stage, []
+    pending = pending_carries(group, legacy)
+    return ("carries-open" if pending else "done"), pending
+
+
+def stranded(roster: dict, legacy: dict) -> list:
+    """(group, stage, index, text) of every pending carry on a closed group."""
+    out = []
+    for g in roster.get("groups", []):
+        stage = (g.get("resume") or {}).get("stage")
+        if stage in CARRY_CLOSED:
+            out += [(g["group"], stage, i, g["carry"][i])
+                    for i in pending_carries(g, legacy)]
+    return out
+
+
 def depth_of(roster: dict) -> dict:
     """Wave (dependency depth) per group, over the open groups only.
 
@@ -606,6 +685,42 @@ def _self_test() -> int:
           schema_refuses(lambda: read_durations("/nonexistent-hpo-root")),
           "read_durations returned on a missing file")
 
+    # THE CARRY LEDGER (#2733). One predicate decides whether a group still
+    # holds a carry; set-stage, the reconciler and carry_audit's STRANDED arm
+    # all read it.
+    cg = {"group": "G", "resume": {"stage": "done"},
+          "carry": ["old one", "new one",
+                    "done one [implemented: 0123abcd]",
+                    "gone one [moved: R10-X]", "nope [dismissed: a duplicate]"]}
+    legacy = legacy_carries({"groups": [
+        cg | {"carry": ["old one"]},
+        {"group": "OPEN", "resume": {"stage": "in-progress"}, "carry": ["new one"]}]})
+    check("legacy: a carry on a closed group at the cut-over is legacy; an "
+          "open group's carry at the cut-over is not",
+          legacy == {"G": frozenset({"old one"})}, legacy)
+    check("pending: unmarked and not legacy is pending; each of the three "
+          "marks discharges a carry", pending_carries(cg, legacy) == [1],
+          pending_carries(cg, legacy))
+    check("pending: with no cut-over every unmarked carry is pending",
+          pending_carries(cg, {}) == [0, 1], pending_carries(cg, {}))
+    check("a mark is read only at the end of the carry, in its own grammar",
+          carry_mark("x [implemented: 0123abcd]") == ("implemented", "0123abcd")
+          and carry_mark("x [implemented: 0123abcd] and more") is None
+          and carry_mark("x [shipped: 0123abcd]") is None)
+    check("closing: done with a pending carry is written carries-open",
+          closing_stage(cg, "done", legacy) == ("carries-open", [1]),
+          closing_stage(cg, "done", legacy))
+    check("closing (null): done with every carry marked or legacy stays done",
+          closing_stage(cg | {"carry": cg["carry"][:1] + cg["carry"][2:]},
+                        "done", legacy) == ("done", []))
+    check("closing (null): a stage other than done is never rewritten",
+          closing_stage(cg, "in-progress", legacy) == ("in-progress", []))
+    got = [(s[0], s[2]) for s in stranded({"groups": [
+        cg, cg | {"group": "AB", "resume": {"stage": "absorbed"}},
+        cg | {"group": "CO", "resume": {"stage": "carries-open"}}]}, legacy)]
+    check("stranded: a pending carry on a done or absorbed group, never on an "
+          "open one", got == [("G", 1), ("AB", 0), ("AB", 1)], got)
+
     check("non-rosters are ignored",
           newest_roster(["README.md", "wave-r9-groups.json.bak"]) is None)
     with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
diff --git a/tools/audit/seat/roster_sync.py b/tools/audit/seat/roster_sync.py
index 1b01f24e0..35c8ef80a 100644
--- a/tools/audit/seat/roster_sync.py
+++ b/tools/audit/seat/roster_sync.py
@@ -15,7 +15,9 @@ stale stages. This step is that comparison, run every pass by
   MERGED   a group whose branch answers for a merged pull request is `done` at
            that merge commit (`resume.commit`); a merge first observed in this
            pass also has its body's `Carry: <GROUP>` items appended to the
-           destination group's `carry` array.
+           destination group's `carry` array. A group that still owes a
+           carry (`roster_lib.pending_carries`) is written `carries-open`
+           instead, the rule `roster_edit.py set-stage` shares (#2733).
   OPEN     a group whose branch answers for an open pull request is
            `in-progress`, with the number in `resume.pr`.
   no PR    a branch with no open or merged pull request makes no change:
@@ -285,7 +287,8 @@ class Change(NamedTuple):
     state: str
 
 
-def derive(roster: dict, prs: list[PR]) -> tuple[list[Change], list[tuple], list[PR]]:
+def derive(roster: dict, prs: list[PR], legacy: dict | None = None
+           ) -> tuple[list[Change], list[tuple], list[PR]]:
     """(changes, skips, transitions): the stage writes a read supports, the
     groups a human disposition protected, and the merged pull requests whose
     group moves to done in this pass -- the only bodies read for `Carry:`.
@@ -295,7 +298,10 @@ def derive(roster: dict, prs: list[PR]) -> tuple[list[Change], list[tuple], list
     claim (`review`, `in-review`) is left alone while its pull request is open
     and closed to `done` on the merge -- the transition that keeps a merged
     group from being stranded open. Every other derivable stage follows the
-    read: an open pull request makes it `in-progress`, a merge makes it `done`.
+    read: an open pull request makes it `in-progress`, a merge makes it `done`
+    -- or `carries-open` while the group still owes a carry
+    (`roster_lib.closing_stage` over `legacy`, the roster's cut-over carries:
+    the one rule `roster_edit.py set-stage` applies too; #2733 (b)).
     """
     by_group = matches(roster, prs)
     changes: list[Change] = []
@@ -329,7 +335,8 @@ def derive(roster: dict, prs: list[PR]) -> tuple[list[Change], list[tuple], list
         # A transition only: a group already done is a settled record, and its
         # commit is not re-recorded (the tick checks a done commit is in main;
         # a pull request's head is, once merged).
-        changes.append(Change(gid, "done", pr.number, pr.merge_commit,
+        closed, _ = roster_lib.closing_stage(g, "done", legacy or {})
+        changes.append(Change(gid, closed, pr.number, pr.merge_commit,
                               stage, pr.state))
         transitions.append(pr)
     return changes, skips, transitions
@@ -487,10 +494,15 @@ def carry_plan(roster: dict, transitions: list[PR], repo: str,
     return appends, refusals
 
 
-def apply_plan(roster: dict, changes: list[Change], appends: list[tuple]) -> None:
-    """The derived ops, through roster_edit's own op functions."""
+def apply_plan(roster: dict, changes: list[Change], appends: list[tuple],
+               legacy: dict | None = None) -> None:
+    """The derived ops, through roster_edit's own op functions. `legacy` is
+    the cut-over set derive() judged with: op_set_stage re-applies the closing
+    rule, so without it a `done` derived over a legacy-only group would be
+    written `carries-open` (#2733; review X1)."""
     for c in changes:
-        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit)
+        roster_edit.op_set_stage(roster, c.group, c.stage, c.merge_commit,
+                                 legacy=legacy)
         if c.stage == "in-progress":
             # The open pull request's number is the one the ask records; a
             # done group's record is its merge commit.
@@ -563,14 +575,18 @@ def sync(a) -> int:
         rel = roster_lib.roster_path(a.checkout, base, a.roster_path)
         roster = json.loads(run(["git", "-C", a.checkout, "show",
                                  f"{base}:{rel}"]))
-        changes, skips, transitions = derive(roster, prs)
+        try:
+            legacy = roster_lib.read_legacy(a.checkout, rel)
+        except roster_lib.RosterNotFound as e:
+            raise Refuse(f"the carry cut-over is unreadable: {e}")
+        changes, skips, transitions = derive(roster, prs, legacy)
         for gid, why in invalid_commits(a.checkout, roster):
             print(f"roster_sync: RECORD-INVALID {gid} {why}")
         # The carries are judged against the roster this pass will write: a
         # destination this pass makes done refuses the carry, and the stage
         # writes are applied in memory first on a copy.
         projected = copy.deepcopy(roster)
-        apply_plan(projected, changes, [])
+        apply_plan(projected, changes, [], legacy)
         appends, refusals = carry_plan(projected, transitions, a.repo,
                                        a.pr_state)
         for c in changes:
@@ -578,8 +594,12 @@ def sync(a) -> int:
                 print(f"roster_sync: {c.group}: record PR #{c.pr} for stage "
                       f"{c.stage}")
             else:
+                owed = roster_lib.pending_carries(
+                    roster_lib.groups_of(roster)[c.group], legacy)
                 print(f"roster_sync: {c.group}: stage {c.was} -> {c.stage}"
                       + (f" at {c.merge_commit[:12]}" if c.merge_commit else "")
+                      + (f" ({len(owed)} pending carries)"
+                         if c.stage == "carries-open" else "")
                       + f" (PR #{c.pr} {c.state})")
         for s in skips:
             why = s[3] if len(s) > 3 else "a human disposition"
@@ -609,15 +629,15 @@ def sync(a) -> int:
             # Re-derive on the bytes this write path is about to replace --
             # on every attempt of a push race -- so the edit is computed from
             # the file it lands in, never an older read.
-            changes, _, transitions = derive(roster, prs)
+            changes, _, transitions = derive(roster, prs, legacy)
             projected = copy.deepcopy(roster)
-            apply_plan(projected, changes, [])
+            apply_plan(projected, changes, [], legacy)
             appends, _ = carry_plan(projected, transitions, a.repo, a.pr_state)
             if not changes and not appends:
                 print(f"roster_sync: {branch} already carries these; "
                       "nothing written")
                 return False
-            apply_plan(roster, changes, appends)
+            apply_plan(roster, changes, appends, legacy)
             return True
 
         try:
@@ -782,10 +802,37 @@ def self_test() -> int:
           by.get("L-OK") is not None and by["L-OK"].stage == "in-progress",
           by)
 
+    # THE CARRY LEDGER (#2733 (b), carry 31): a merge over a group that still
+    # owes a carry writes carries-open, through roster_lib.closing_stage --
+    # the predicate roster_edit's set-stage shares -- and a group whose carries
+    # are all marked or legacy is written done. The body's carries are still
+    # read: the transition is a merge either way.
+    owed = {"groups": [
+        {"group": "C-OWES", "carry": ["owed one", "x [implemented: 0123abcd]"],
+         "resume": {"stage": "in-progress", "branch": "handoff/c-owes"}},
+        {"group": "C-PAID", "carry": ["legacy one", "y [dismissed: dup]"],
+         "resume": {"stage": "in-progress", "branch": "handoff/c-paid"}},
+    ]}
+    got_changes, _, got_tr = derive(owed, [
+        PR(51, MERGED, "handoff/c-owes", "5" * 40, ""),
+        PR(52, MERGED, "handoff/c-paid", "6" * 40, ""),
+    ], {"C-PAID": frozenset({"legacy one"})})
+    by = {c.group: c for c in got_changes}
+    check("a merge over a pending carry writes carries-open, with its commit",
+          by.get("C-OWES") is not None and by["C-OWES"].stage == "carries-open"
+          and by["C-OWES"].merge_commit == "5" * 40, by)
+    check("a merge with every carry marked or legacy writes done (null control)",
+          by.get("C-PAID") is not None and by["C-PAID"].stage == "done", by)
+    check("both merges are transitions whose bodies are read for carries",
+          sorted(p.number for p in got_tr) == [51, 52], got_tr)
+
 
 
-    def build(tmp: Path, lint_src: str) -> tuple[Path, Path, Path]:
-        """(bare origin, driver clone, fixture roster path at the driver)."""
+    def build(tmp: Path, lint_src: str, history=None
+              ) -> tuple[Path, Path, Path]:
+        """(bare origin, driver clone, fixture roster path at the driver).
+        `history` is the rosters main commits in order, one commit each
+        (default: ROSTER_FIXTURE alone); main's tip holds the last."""
         tmp.mkdir(parents=True, exist_ok=True)
         seed = tmp / "seed"
         seed.mkdir()
@@ -793,11 +840,12 @@ def self_test() -> int:
         (seed / roster_edit.BRIEF_LINT_NEW).write_text(lint_src,
                                                       encoding="utf-8")
         (seed / ROSTER).parent.mkdir(parents=True, exist_ok=True)
-        (seed / ROSTER).write_text(roster_edit.dump(ROSTER_FIXTURE),
-                                   encoding="utf-8")
         throwaway_git_init(seed, "-q", "-b", "main")
-        git("-C", str(seed), "add", "-A")
-        git("-C", str(seed), "commit", "-q", "-m", "fixture roster")
+        for each in history or [ROSTER_FIXTURE]:
+            (seed / ROSTER).write_text(roster_edit.dump(each),
+                                       encoding="utf-8")
+            git("-C", str(seed), "add", "-A")
+            git("-C", str(seed), "commit", "-q", "-m", "fixture roster")
         bare = tmp / "origin.git"
         throwaway_git_clone(seed, bare, "-q", "--bare")
         drv = tmp / "drv"
@@ -1108,6 +1156,69 @@ def self_test() -> int:
         check("--roster-file with --apply is refused (no branch to write)",
               rc == 2 and "read-only" in err, (rc, err))
 
+        # THE CUT-OVER, END TO END through sync() (#2733; review X1, X2). A
+        # carry the group held while closed at roster_lib.CARRY_CUTOVER is
+        # legacy: the merge of a group whose only carry is legacy is written
+        # done -- by the write path's own re-derive, not only the dry run's
+        # print. A cut-over the clone cannot read refuses and writes nothing:
+        # read as "no legacy", every legacy carry would be pending and the
+        # merge would write carries-open.
+        def leg_group(stage):
+            return {"group": "R9-LEG", "lane": "L1", "issues": [], "fixes": [],
+                    "after": [], "brief": "legacy", "carry": ["legacy one"],
+                    "resume": {"stage": stage, "branch": "handoff/r9-leg"}}
+        leg_at_cut = {"repo": "fixture/roster", "session": "r9-sync",
+                      "groups": [leg_group("done")]}
+        leg_tip = {"repo": "fixture/roster", "session": "r9-sync",
+                   "groups": [leg_group("in-progress")]}
+        leg_prs = root / "prs-leg.json"
+        leg_prs.write_text(json.dumps([
+            {"number": 61, "state": "MERGED", "headRefName": "handoff/r9-leg",
+             "mergeCommit": {"oid": "6" * 40},
+             "body": "## Friction\n\n- none\n"}]), encoding="utf-8")
+        saved_cut = dict(roster_lib.CARRY_CUTOVER)
+        try:
+            for name, cut_of, want in (
+                    ("readable", lambda d: git("-C", str(d), "rev-parse",
+                                                "origin/main~1"), "done"),
+                    ("absent", lambda d: None, "carries-open")):
+                bare_l, drv_l, _ = build(root / f"leg-{name}", LINT_OK,
+                                         [leg_at_cut, leg_tip])
+                roster_lib.CARRY_CUTOVER.clear()
+                cut = cut_of(drv_l)
+                if cut:
+                    roster_lib.CARRY_CUTOVER[ROSTER] = cut
+                rc, out, err = calls(drv_l, leg_prs, "--apply",
+                                     "--worktree", str(root / f"wt-leg-{name}"))
+                got = (roster_lib.groups_of(roster_at(bare_l, branch))
+                       ["R9-LEG"]["resume"].get("stage")
+                       if branch in branches(bare_l) else None)
+                if name == "readable":
+                    check("sync --apply writes done over a group whose only "
+                          "carry is legacy (the write path reads the cut-over)",
+                          rc == 0 and got == "done"
+                          and "R9-LEG: stage in-progress -> done" in out,
+                          (rc, got, out[-300:], err[-300:]))
+                else:
+                    check("with no cut-over the same carry is pending and sync "
+                          "--apply writes carries-open (null control)",
+                          rc == 0 and got == "carries-open",
+                          (rc, got, out[-300:], err[-300:]))
+            bare_u, drv_u, _ = build(root / "leg-unreadable", LINT_OK,
+                                     [leg_at_cut, leg_tip])
+            roster_lib.CARRY_CUTOVER.clear()
+            roster_lib.CARRY_CUTOVER[ROSTER] = "f" * 40
+            rc, out, err = calls(drv_u, leg_prs, "--apply",
+                                 "--worktree", str(root / "wt-leg-unreadable"))
+            check("an unreadable cut-over refuses sync --apply rc 2, naming it",
+                  rc == 2 and "the carry cut-over is unreadable" in err,
+                  (rc, out[-300:], err[-300:]))
+            check("and the unreadable cut-over wrote nothing",
+                  branch not in branches(bare_u), branches(bare_u))
+        finally:
+            roster_lib.CARRY_CUTOVER.clear()
+            roster_lib.CARRY_CUTOVER.update(saved_cut)
+
         # THE LINT GATE is in the path: a refused roster is never pushed.
         bare2, drv2, _ = build(root / "two", LINT_BAD)
         wt2 = root / "wt-two"
diff --git a/tools/policy/brief_lint.mjs b/tools/policy/brief_lint.mjs
index 8083d3461..7f4a43df6 100644
--- a/tools/policy/brief_lint.mjs
+++ b/tools/policy/brief_lint.mjs
@@ -749,6 +749,15 @@ function checkShape(groups, findings) {
     } else if (typeof g.resume.stage !== 'string' || !g.resume.stage.trim()) {
       bad(label, '`resume.stage` is missing or is not a non-empty string')
     }
+    // #2733's second invariant: a live group lists at least one issue. A
+    // warning, not an error, so roster_edit's --push gate and a fly-in's
+    // registration are never blocked; read only on a group of the
+    // orchestrator's schema (one carrying `issues` or `fixes`), and live is
+    // this linter's own rule: every stage but STAGE_SKIP.
+    const wired = ['issues', 'fixes'].filter((k) => Array.isArray(g[k]))
+    if (wired.length && g.resume?.stage !== STAGE_SKIP && wired.every((k) => g[k].length === 0)) {
+      findings.push({ group: label, severity: 'warning', kind: 'issues', message: 'a live group lists no issue in `issues` or `fixes` (#2733 invariant 2)' })
+    }
     // lintAfterEdges skips a non-array `after` rather than walking its
     // characters, so without this a string here would pass in silence.
     if (g.after !== undefined && !Array.isArray(g.after)) {
@@ -1085,6 +1094,30 @@ function assertAcceptanceFixture(name, label, opts, required) {
   return 0
 }
 
+// #2733's second invariant, a WARNING by design (so neither roster_edit's
+// --push lint gate nor a fly-in registration is blocked): a live group lists
+// at least one issue in `issues` or `fixes`. Driven in memory, both ways: the
+// issueless live group warns; one that gains an issue, a done group and a
+// group of another schema (no `issues`/`fixes` keys) do not.
+function assertIssuelessWarning() {
+  const g = (group, stage, extra) => ({ group, brief: 'probe', resume: { stage }, ...extra })
+  const findings = []
+  checkShape([
+    g('bare', 'not-started', { issues: [], fixes: [] }),
+    g('issued', 'not-started', { issues: [], fixes: [7] }),
+    g('closed', STAGE_SKIP, { issues: [], fixes: [] }),
+    g('other-schema', 'pending', {}),
+  ], findings)
+  const warned = findings.filter((f) => f.severity === 'warning' && f.kind === 'issues').map((f) => f.group)
+  const errors = findings.filter((f) => f.severity === 'error')
+  if (warned.join() === 'bare' && errors.length === 0) {
+    console.log('\nISSUELESS ok: a live group with no issue warns; one with an issue, a done group and another schema do not')
+    return 0
+  }
+  console.log(`\nISSUELESS VACUOUS: warned [${warned}] errors ${errors.length}; want [bare] and 0`)
+  return 1
+}
+
 // SYMBOL_GREP_EXCLUDE, bounded by the tree in both directions. The ceiling
 // refuses an entry that names nothing, which is the dead weight the archive
 // created and nothing caught. The floor refuses the deletion of an entry the
@@ -1331,6 +1364,7 @@ function main() {
     acceptanceRc += assertDriverGuard()
     acceptanceRc += assertGrepExcludeBounded()
     acceptanceRc += assertLocateOldFirst()
+    acceptanceRc += assertIssuelessWarning()
     acceptanceRc += assertRosterIssues()
     acceptanceRc += assertCarryFixtures()
   }

