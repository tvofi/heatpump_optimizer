# Review packet #3001
head: 92a57dd44cb9d137d6faa86a2fd281011c26d0d7
base: ca0a6cfbc2e5538e6e2220793831443719ff6e98

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124186579964 neutral
arch-score / arch-score id=124186213980 success
arm id=124186003785 skipped
budget-raise-gate / budget-raise-gate id=124186213869 success
cancel-superseded id=124186003267 success
codeql / Analyze (actions) id=124186213122 success
codeql / Analyze (javascript-typescript) id=124186213121 success
codeql / Analyze (python) id=124186213201 in_progress
governance / delivery-status id=124186213594 success
governance / delivery-status-publish id=124186216610 skipped
governance / env-matrix id=124186213513 success
governance / instrument-self-tests id=124186213615 in_progress
governance / policy-docs id=124186213476 success
governance / record id=124186214881 skipped
governance / wave-script id=124186213485 success
hassfest / hassfest id=124186213048 success
kernel-points id=124186214644 skipped
prelude id=124186003750 in_progress
refresh id=124186003781 success
tests / arch-instrument id=124186537623 in_progress
tests / briefs id=124186214069 success
tests / browser id=124186537430 success
tests / closure-scope id=124186214121 success
tests / closures id=124186537616 in_progress
tests / coverage id=124186537482 in_progress
tests / fast (3.14) id=124186537485 in_progress
tests / mutation id=124186214306 success
tests / mutation-autofix id=124186895790 skipped
tests / mutation-pins id=124186893363 skipped
tests / nightly-ha id=124186539854 skipped
tests / nightly-status id=124186214281 success
tests / replay id=124186539574 skipped
tests / typing id=124186537575 success
validate / validate-hacs id=124186213864 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 254a7894: R10-ORCH-ROSTER-SCHEMA
NOTE body item 71a17405: R10-ORCH-PLANPAGE
NOTE body item 42496ebc: R10-ORCH-PLANPAGE
NOTE body item 8995bb39: R10-ORCH-LEDGER
NOTE body item 78c2b46b: R10-ORCH-PLANPAGE
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/seat/plan_page.py --self-test
             `tools/audit/seat/plan_page.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/state_docs.py --self-test
             `tools/audit/seat/state_docs.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r10_plan_page_mutants.py
             `dev/audit/harnesses/r10_plan_page_mutants.py` is in the tree at this head
  unverified python3 -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_lib,json; r=json.load(open('dev/programme/rosters/wave-r10-groups.json')); print(sum(1 for g in r['groups'] if (g.get('resume') or {}).get('stage') in roster_lib.DISPOSITION))"
             python3 runs an inline script rather than a file
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 507a9ec26
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 507a9ec26
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/sweep_render.py --self-test
             `tools/audit/seat/sweep_render.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --only self-test-reads --record-self-tests
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/derive_closures.sh --single tests/entities.py
             `tests/derive_closures.sh` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  unverified git log --format=%B origin/main..HEAD | grep -ci "claude\|co-authored"
             `git log` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 17 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/harnesses/r10_plan_page_mutants.py b/dev/audit/harnesses/r10_plan_page_mutants.py
index 141b5a5d0..97be0c21b 100644
--- a/dev/audit/harnesses/r10_plan_page_mutants.py
+++ b/dev/audit/harnesses/r10_plan_page_mutants.py
@@ -2,9 +2,10 @@
 """R10-PLAN-ARTIFACT: each behaviour plan_page.py's self-test pins dies alone.
 
 Each mutant is one exact one-occurrence replacement in
-tools/audit/seat/plan_page.py or tools/plan/replan.py (the freshness rule the
-page shares). The driver applies one, runs `plan_page.py --self-test` (and
-`replan.py --self-test` too, for a replan.py mutant and for M0), restores
+tools/audit/seat/plan_page.py, tools/plan/replan.py (the freshness rule the
+page shares) or tools/audit/seat/state_docs.py (which publishes the page).
+The driver applies one, runs `plan_page.py --self-test` (and the mutated
+file's own `--self-test` too, and every one for M0), restores
 the file byte for byte, and refuses to start on a file with uncommitted edits.
 Metric, one line per mutant:
 
@@ -40,6 +41,7 @@ def repo_root(start):
 ROOT = repo_root(__file__)
 PAGE = "tools/audit/seat/plan_page.py"
 PLAN = "tools/plan/replan.py"
+STATE = "tools/audit/seat/state_docs.py"
 
 MUTANTS = [
     ("M0", PAGE, None, None),
@@ -77,6 +79,43 @@ MUTANTS = [
     # R10-PLAN-PRIO: the Tier column is the plan's computed dispatch priority.
     ("tier-column", PAGE,
      '{r["tier"] if r["tier"] is not None else "—"}', '"—"'),
+    # R10-ORCH-PLANPAGE: the scratch generator's five defects (orch-machinery
+    # DESIGN.md S8, 6.7), each mutant restoring its pre-fix shape.
+    ("defect-1-hardcoded-override", PAGE,
+     "    G = roster_lib.groups_of(roster)\n    PG = plan[\"groups\"]",
+     "    G = roster_lib.groups_of(roster)\n    G.update({g: {**G[g], \"resume\": "
+     "{\"stage\": \"not-started\"}} for g in list(G)[:1]})\n    PG = plan[\"groups\"]"),
+    ("defect-2-scratch-graph", PAGE,
+     "blk = [a for a in entry.get(\"after\") or [] if a in G and a not in done]",
+     "blk = [a for a in {\"R9-READY\": [\"R9-LIVE\"]}.get(g, entry.get(\"after\") or [])"
+     " if a in G and a not in done]"),
+    ("defect-3-count-wrong-set", PAGE,
+     "open_iss = (\"—\" if snap.get(\"offline\") else str(sum(",
+     "open_iss = (\"—\" if snap.get(\"offline\") else str(len(snap[\"issues\"]) - 1 + 0 * sum("),
+    ("defect-4-sha8-as-pr", PAGE,
+     "label, pr = f\"merged at {commit[:8]}\", \"merged\"",
+     "label, pr = f\"merged at {commit[:8]}\", f\"#{commit[:8]}\""),
+    ("defect-5-absorbed-as-done", PAGE,
+     "            st = \"held\"\n", "            st = \"done\"\n"),
+    ("held-label", PAGE,
+     "label = _stage(entry) + (f\" into {short(into)}\" if into else \"\") + sfx",
+     "label = \"delivered\" + sfx"),
+    ("unavailable-page-written", PAGE,
+     "    Path(html_out).write_text(unavailable_page(what), encoding=\"utf-8\")\n",
+     "    pass\n"),
+    ("state-page-published", STATE, "        return {page_path: text}, None",
+     "        return {}, None"),
+    ("state-keeps-last-good", STATE,
+     "    return ({} if held else {page_path: text}), why",
+     "    return {page_path: text}, why"),
+    ("state-unavailable-where-none", STATE,
+     "    return ({} if held else {page_path: text}), why", "    return {}, why"),
+    ("state-unread-exits-1", STATE, "rc = 1 if unread else 0", "rc = 0"),
+    ("state-crash-guard", STATE,
+     'if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:', "if False:"),
+    ("unavailable-no-figures", PAGE,
+     "f'<div class=\"stat\"><b>—</b><span>{e(v)}</span></div>'",
+     "f'<div class=\"stat\"><b>0</b><span>{e(v)}</span></div>'"),
 ]
 
 
@@ -88,7 +127,7 @@ def fail_name(line: str) -> str:
 
 def main(argv: list[str]) -> int:
     want = set(argv)
-    for rel in (PAGE, PLAN):
+    for rel in (PAGE, PLAN, STATE):
         if subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", rel]).returncode:
             print(f"refused: {rel} has uncommitted edits")
             return 2
@@ -107,10 +146,13 @@ def main(argv: list[str]) -> int:
                 path.write_text(text.replace(old, new), encoding="utf-8")
             runs = [subprocess.run([sys.executable, "-I", str(ROOT / s), "--self-test"],
                                    capture_output=True, text=True)
-                    for s in (PAGE, PLAN) if s == PAGE or rel == PLAN or old is None]
+                    for s in (PAGE, PLAN, STATE) if s == PAGE or s == rel or old is None]
         finally:
             path.write_bytes(orig)
         fails = [ln for r in runs for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
+        # state_docs.py reports its failures on one line, comma-joined.
+        fails += [f"FAIL {ln}" for r in runs for ln in r.stdout.splitlines()
+                  if re.match(r"\d+ self-test check\(s\) failed: ", ln)]
         rc = max(r.returncode for r in runs)
         if name == "M0":
             verdict = "null" if rc == 0 and not fails else "SURVIVED"
diff --git a/dev/programme/delivery/3001.md b/dev/programme/delivery/3001.md
new file mode 100644
index 000000000..d9b19732b
--- /dev/null
+++ b/dev/programme/delivery/3001.md
@@ -0,0 +1 @@
+- [#3001](https://github.com/tvofi/heatpump_optimizer/pull/3001) — **open**, R10-ORCH-PLANPAGE: plan page published by state_docs, UNAVAILABLE on refusal (R10-ORCH-PLANPAGE)
diff --git a/tests/closure.py b/tests/closure.py
index 2c72928a3..bba004d32 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -598,6 +598,16 @@ INERT_EXCEPT = (
     "dev/audit/harnesses/r10_ci_layout_u5/run_part.py",
     "dev/audit/harnesses/r10_ci_layout_u5/unitcheck.py",
     "tools/pr/codeql_scope.py",
+    # R10-ORCH-PLANPAGE: state_docs.py's self-test (which tests/entities.py runs)
+    # builds the plan page from the real roster, so it imports the plan model and
+    # opens its measured durations. CI predict (self-test-reads) found both INERT
+    # and read. Same route as codeql_scope.py above: the tools/plan/ prefix stays
+    # INERT, the two files move to the recorded closure.
+    "tools/plan/replan.py",
+    "tools/plan/durations.json",
+    # Also read by that self-test (the page renderer replan feeds): tools/audit/seat/
+    # stays INERT, this file joins the recorded closure.
+    "tools/audit/seat/plan_page.py",
     # R9-RO-6: the device-fixture scripts moved under tools/devices/, which is
     # INERT. tests/entities.py and tests/features.py import them, so an edit
     # selects those scripts. Left inside the prefix they would be declared
diff --git a/tests/closures.json b/tests/closures.json
index a40909c5a..ceb95f3f0 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1790,6 +1790,7 @@
    "tools/audit/seat/handover_prompt.py",
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
+   "tools/audit/seat/plan_page.py",
    "tools/audit/seat/plan_table.py",
    "tools/audit/seat/proof_watch.py",
    "tools/audit/seat/queue_pre_flight.py",
@@ -1813,6 +1814,8 @@
    "tools/devices/gen_device_fixtures.py",
    "tools/devices/measure_prefill_corpus.py",
    "tools/merge/ledger_merge.py",
+   "tools/plan/durations.json",
+   "tools/plan/replan.py",
    "tools/policy/agreement.mjs",
    "tools/policy/brief_lint.mjs",
    "tools/policy/check-wave-script.mjs",
diff --git a/tools/audit/seat/instruments/plan_page.py.md b/tools/audit/seat/instruments/plan_page.py.md
index d818edea3..3ee9211c0 100644
--- a/tools/audit/seat/instruments/plan_page.py.md
+++ b/tools/audit/seat/instruments/plan_page.py.md
@@ -10,7 +10,13 @@
   not-done groups projected to close at the last carrying group's finish
   (closed ones dropped, unplanned ones flat), omitted with a note when `gh`
   is absent. When: after a replan at a wave
-  edge. Refusal: a plan `replan.stale_reason` calls stale (its roster blob
-  is not the roster's at its ref now; an `origin/` ref is fetched first) or
-  `replan.check_plan` refuses -- exit 1, nothing written. `--check` of
-  replan.py applies the same freshness rule.
+  edge, through `state_docs.py --plan`, which publishes it as `PLAN.html`
+  beside the plan table. A group whose stage is a human disposition is
+  `held`, never merged or ready. Refusal: a plan `replan.stale_reason` calls
+  stale (its roster blob is not the roster's at its ref now; an `origin/` ref
+  is fetched first), `replan.check_plan` refuses, or the plan records no
+  duration model -- exit 1 and the UNAVAILABLE page (what could not be read,
+  every figure a dash, no table), never a page of zeros. `--check` of
+  replan.py applies the same freshness rule. `--self-test` carries the
+  scratch generator's five defects as fixtures, each killed by its mutant in
+  `dev/audit/harnesses/r10_plan_page_mutants.py`.
diff --git a/tools/audit/seat/instruments/state_docs.py.md b/tools/audit/seat/instruments/state_docs.py.md
index 999007e57..c6f486560 100644
--- a/tools/audit/seat/instruments/state_docs.py.md
+++ b/tools/audit/seat/instruments/state_docs.py.md
@@ -16,6 +16,10 @@
   files, and an already-current tip, which is reported and left alone. The
   commit is plumbing over a temp index, so the calling checkout's index is
   never touched.
+  `--plan PLAN_JSON` adds `PLAN.html`, `plan_page.py`'s page over that plan,
+  to the same commit; a refused page keeps the last good one at the ref (or
+  publishes the UNAVAILABLE page where there is none) and the call exits 1
+  after pushing the other docs. The beat runs no replan, so passes no `--plan`.
   `state_docs.py beat` is the same instrument on a loop, and it lives here
   rather than in a session's scratch for decision 0013's reason — an
   instrument the programme runs belongs where a later session can test it. A
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index 5773ef700..4c5c8b060 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -23,10 +23,15 @@ JSON file of the same shape: {"issues": [{number, title, state}],
 "open_prs": [{number, head_ref, title}], "merged_prs": [{number, title,
 head_ref, merge_commit_sha, merged_at}]}).
 
-REFUSALS (exit 1, nothing written): a plan `replan.stale_reason` calls stale
--- its roster blob is not the roster's blob at the ref now -- and a plan
-`replan.check_plan` refuses. The freshness rule is replan.py's, so `--check`
-and this page cannot disagree about which plans are current.
+REFUSALS (exit 1): a plan `replan.stale_reason` calls stale -- its roster
+blob is not the roster's blob at the ref now --, a plan `replan.check_plan`
+refuses, a plan recording no duration model, and an `origin/` roster ref that
+cannot be fetched. The freshness rule is replan.py's, so `--check` and this
+page cannot disagree about which plans are current. A refusal writes the
+UNAVAILABLE page to `--html`: a heading naming what could not be read, every
+figure a dash, no table -- never a page of zeros, and never a stale page left
+in place as if current. `state_docs.py --plan` publishes this page beside the
+plan table, keeping the last good page at the state ref when one exists.
 
 Status classes, one per group:
   done     resume.stage in roster_lib.DONE_STAGES; labelled with the PR it
@@ -36,6 +41,10 @@ Status classes, one per group:
            plan starts it later than the replan instant);
   partial  a merged `R<N>-GROUP:` titled PR delivered part of an open group;
   blocked  an `after` target is not done, and nothing of it merged;
+  held     resume.stage is a human disposition (roster_lib.DISPOSITION:
+           absorbed, carries-open, deferred, ...), labelled with that word and,
+           for an absorbed group, the group it went to (`absorbed_into`); it is
+           neither merged nor ready to dispatch;
   ready    everything else.
 A branch answers for a group by `roster_lib.group_for_branch`, then by its
 last segment against the tails of the roster's `resume.branch` values (with a
@@ -211,6 +220,10 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
                 label, pr = f"merged at {commit[:8]}", "merged"
             else:
                 label, pr = "folded into another group (no merge of its own)", "merged"
+        elif _stage(entry) in roster_lib.DISPOSITION:
+            st = "held"
+            into = entry.get("absorbed_into")
+            label = _stage(entry) + (f" into {short(into)}" if into else "") + sfx
         elif _stage(entry) in replan.LIVE_STAGES:
             st = "live"
             queued = not pg.get("inherited") and pg["start"] > start0
@@ -452,7 +465,7 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict) -> str:
     chain = plan["critical_path"]
     waves_of = {g: w["wave"] for w in plan["waves"] for g in w["groups"]}
     counts = {k: sum(1 for r in rows if r["st"] == k)
-              for k in ("done", "live", "ready", "partial", "blocked")}
+              for k in _STRIP}
     open_iss = ("—" if snap.get("offline") else str(sum(
         1 for i in snap["issues"]
         if i["state"] == "OPEN" and i["number"] != TRACKING_ISSUE)))
@@ -523,6 +536,28 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict) -> str:
     return page
 
 
+def unavailable_page(what: str) -> str:
+    """The refusal page: what could not be read, every figure a dash, no
+    table. A reader sees that the plan is unknown, not that it is empty."""
+    e = html.escape
+    stats = "".join(f'<div class="stat"><b>—</b><span>{e(v)}</span></div>'
+                    for v in (*_STRIP.values(), "open issues", "projected programme close"))
+    return ("<!doctype html>\n<meta charset=\"utf-8\">\n<title>PLAN UNAVAILABLE</title>\n"
+            f"<main>\n<h1>PLAN UNAVAILABLE — {e(what)}</h1>\n"
+            f'<div class="strip">{stats}</div>\n'
+            "<p>No figure on this page is a measurement. Re-run "
+            "<code>tools/plan/replan.py</code> and this page's generator.</p>\n</main>\n")
+
+
+def _refuse(html_out: str, what: str, detail: list) -> int:
+    """Exit 1 with the UNAVAILABLE page written where the page would be."""
+    print(f"plan_page: refused, wrote the UNAVAILABLE page: {what}", file=sys.stderr)
+    for d in detail:
+        print(f"  {d}", file=sys.stderr)
+    Path(html_out).write_text(unavailable_page(what), encoding="utf-8")
+    return 1
+
+
 # ---------------------------------------------------------------------- cli
 
 def main(argv=None, fetch=fetch_github) -> int:
@@ -551,24 +586,17 @@ def main(argv=None, fetch=fetch_github) -> int:
                             f"+refs/heads/{ref[7:]}:refs/remotes/{ref}"],
                            capture_output=True, text=True)
         if r.returncode:
-            print(f"plan_page: refused: cannot fetch {ref} to test freshness: "
-                  f"{r.stderr.strip()[:200]} (--no-fetch reads it as it is)",
-                  file=sys.stderr)
-            return 1
+            return _refuse(a.html, f"cannot fetch {ref} to test freshness",
+                           [r.stderr.strip()[:200], "--no-fetch reads it as it is"])
     bad = replan.check_plan(plan)
     stale = replan.stale_reason(plan, a.repo, ref, a.roster_path)
     if stale:
         bad.append(f"freshness: {stale}")
     if bad:
-        print(f"plan_page: refused, nothing written: {len(bad)} violation(s)",
-              file=sys.stderr)
-        for b in bad:
-            print(f"  {b}", file=sys.stderr)
-        return 1
+        return _refuse(a.html, f"{len(bad)} plan violation(s): {bad[0]}", bad)
     if "model" not in plan["generated"]:
-        print("plan_page: refused, nothing written: plan.json records no duration "
-              "model (generated.model); re-run tools/plan/replan.py", file=sys.stderr)
-        return 1
+        return _refuse(a.html, "plan.json records no duration model "
+                       "(generated.model); re-run tools/plan/replan.py", [])
     path = roster_lib.roster_path(a.repo, ref, a.roster_path)
     roster = roster_lib.show_roster(a.repo, ref, path)
     snap = (json.loads(Path(a.github_snapshot).read_text(encoding="utf-8"))
@@ -615,6 +643,7 @@ def _self_test() -> int:
         grp("R9-PART", "UX"),
         grp("R9-BLOCK", "UX", after=("R9-LIVE",)),
         grp("R9-READY", "IN", after=("R9-DONE-SHA",), issues=(13,), fixes=(13,)),
+        dict(grp("R9-HELD", "IN", stage="absorbed"), absorbed_into="R9-DONE-SHA"),
     ]}
     snap = {
         "issues": [{"number": 11, "title": "eleven", "state": "CLOSED"},
@@ -664,173 +693,232 @@ def _self_test() -> int:
     check("an open issue on a done group or none is excluded and counted",
           pr_["other"] == {6, 99} and set(pr_["close_at"]) == {1, 2, 4}, pr_)
 
-    with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
-        repo = Path(td) / "repo"
-        rpath = repo / roster_lib.ROSTERS_DIR / "wave-r9-groups.json"
-        rpath.parent.mkdir(parents=True)
-        throwaway_git_init(repo, "-q", "-b", "main")
-
-        def commit(r: dict) -> None:
-            rpath.write_text(json.dumps(r), encoding="utf-8")
-            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
-            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "r"], check=True)
-        commit(roster)
-        r_, ref_, blob_ = replan.load_roster(str(repo), "main")
-        plan = replan.build_plan(r_, durations, dict(replan.DEFAULT_CAPS), start,
-                                 "v1.0.0", ref_, blob_)
-        planf, snapf = Path(td) / "plan.json", Path(td) / "snap.json"
-        planf.write_text(json.dumps(plan), encoding="utf-8")
-        snapf.write_text(json.dumps(snap), encoding="utf-8")
-
-        rows = {r["g"]: r for r in build_rows(roster, plan, snap)}
-        st = {g: (r["st"], r["label"], r["pr"]) for g, r in rows.items()}
-        check("done: the PR is found by merge commit",
-              st["R9-DONE-SHA"] == ("done", "merged PR #21", "#21"), st["R9-DONE-SHA"])
-        check("done: the PR is found by branch when no merge commit matches",
-              st["R9-DONE-BR"] == ("done", "merged PR #22", "#22"), st["R9-DONE-BR"])
-        check("done: no PR found falls back to the commit's sha8",
-              st["R9-DONE-NONE"] == ("done", "merged at cccccccc", "merged"),
-              st["R9-DONE-NONE"])
-        check("live", st["R9-LIVE"][0] == "live" and st["R9-LIVE"][1] == "in-progress",
-              st["R9-LIVE"])
-        check("the open PR maps by the branch-tail fallback",
-              st["R9-LIVE"][2] == "#31", st["R9-LIVE"])
-        check("the fallback is needed: roster_lib alone does not map it",
-              roster_lib.group_for_branch(roster, "handoff/r9-live-g-pr") is None)
-        check("an open PR whose branch names no group maps by its title",
-              st["R9-READY"][2] == "#32", st["R9-READY"])
-        check("a title naming two groups maps to neither",
-              "#33" not in st["R9-PART"][2] + st["R9-READY"][2], st["R9-PART"])
-        check("partial: a merged R9-PART: title on an open group",
-              st["R9-PART"][:2] == ("partial", "part merged #23, residual open"),
-              st["R9-PART"])
-        check("blocked: an after target not done",
-              st["R9-BLOCK"][:2] == ("blocked", "waiting on LIVE"), st["R9-BLOCK"])
-        check("ready: its only after target is done", st["R9-READY"][0] == "ready",
-              st["R9-READY"])
-        check("blocked-by is the roster's after less the done groups",
-              rows["R9-BLOCK"]["blk"] == ["R9-LIVE"] and rows["R9-READY"]["blk"] == [],
-              (rows["R9-BLOCK"]["blk"], rows["R9-READY"]["blk"]))
-
-        page = render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
-                      plan, snap)
-        check("a closed issue's chip is struck",
-              '<span class="chip closer closed" title="eleven">#11</span>' in page)
-        check("an open issue's chip is not",
-              '<span class="chip" title="twelve">#12</span>' in page
-              and '<span class="chip closer" title="thirteen">#13</span>' in page)
-        for cls, want in (("done", 3), ("live", 1), ("ready", 1), ("partial", 1),
-                          ("blocked", 1)):
-            check(f"rows carry the {cls} class", page.count(f'<tr class="{cls}"') == want,
-                  page.count(f'<tr class="{cls}"'))
-            check(f"the summary strip counts {cls}",
-                  f"<b>{want}</b><span>{_STRIP[cls]}</span>" in page)
-        check("the open-issue count leaves out the tracking issue",
-              "<b>2</b><span>open issues" in page)
-        check("every template field is filled", "{{" not in page,
-              re.findall(r"\{\{\w+\}\}", page))
-        check("the round comes from the roster path", "<h1>Round 9 Fix Plan</h1>" in page)
-        model = plan["generated"]["model"]
-        check("the methodology states the plan's sizes and live fraction",
-              f"S {model['sizes_hours']['S']:g} h" in page
-              and f"{model['live_remaining_fraction'] * 100:g}%" in page)
-        check("every open group has a bar; no done group does",
-              all(f'data-name="{short(g)}"' in page for g in rows if rows[g]["st"] != "done")
-              and 'data-name="DONE-SHA"' not in page)
-        check("critical-path groups carry the mark",
-              all(rows[g]["crit"] for g in plan["critical_path"])
-              and page.count('class="critmark"') == len(plan["critical_path"]))
-        check("every open group's tier is shown, and a merged group's is not",
-              all(f'<td class="tier">{rows[g]["tier"]}</td>' in page
-                  for g in rows if rows[g]["tier"] is not None)
-              and all(rows[g]["tier"] is None for g in rows if rows[g]["st"] == "done")
-              and '<td class="tier">—</td>' in page
-              and '<th title="dispatch tier' in page,
-              {g: rows[g]["tier"] for g in rows})
-        check("the critical path is tier 0 and production tier 1",
-              all(rows[g]["tier"] == 0 for g in plan["critical_path"])
-              and any(rows[g]["tier"] == 1 for g in rows if rows[g]["st"] != "done"),
-              {g: rows[g]["tier"] for g in rows})
-        check("a planned stamp is drawn", 'class="stampline"' in page)
-        check("the filter and hide-merged controls ship",
-              'id="hide-done"' in page and 'data-f="blocked"' in page)
-        check("no machine path in the page", not re.search(r"/(home|Users|tmp)/", page))
-        # The caption's figure is the links the chart draws, not the ones it
-        # leaves to the marks: two fixtures where those differ, one each way.
-        links = max(0, len(plan["critical_path"]) - 1)
-        check("the caption counts the links drawn (none drawn, one left)",
-              page.count('class="critline"') == 0 and links == 1
-              and f"0 of {links} critical-path links are drawn" in page,
-              re.findall(r"\d+ of \d+ critical-path links", page))
-        apart = json.loads(json.dumps(plan))
-        apart["groups"]["R9-BLOCK"]["lane"] = "Product UX"  # adjacent lane: drawn
-        page2 = render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
-                       apart, snap)
-        check("the caption counts the links drawn (one drawn, none left)",
-              page2.count('class="critline"') == 1
-              and f"1 of {links} critical-path links are drawn" in page2,
-              re.findall(r"\d+ of \d+ critical-path links", page2))
-
-        sec = issues_section(roster, plan, snap)
-        check("the issues chart is the first section, drawn from the open set",
-              0 <= page.find("Projected open issues") < page.find("<h2>Swimlanes")
-              and "2 open now" in page and "1 other open issues" in page
-              and sec.count("<polyline") == 1, re.findall(r"\d+ open now", page))
-        no_gh = {"issues": [], "open_prs": [], "merged_prs": [], "offline": True}
-        check("no GitHub state: the chart is omitted with a note",
-              "Omitted" in issues_section(roster, plan, no_gh)
-              and "<polyline" not in issues_section(roster, plan, no_gh))
-
-        out = Path(td) / "page.html"
-        argv = ["--plan", str(planf), "--html", str(out), "--repo", str(repo),
-                "--github-snapshot", str(snapf)]
-        check("a fresh plan renders (null control)",
-              main(argv, fetch=fetch_refused) == 0 and out.is_file())
-        out.unlink()
-
-        def no_gh_binary(_repo):
-            raise FileNotFoundError("gh")
-        try:
-            with contextlib.redirect_stderr(io.StringIO()):
-                rc = main(argv[:-2], fetch=no_gh_binary)
-        except Exception as exc:  # a crash is the failure this check names
-            rc = f"raised {type(exc).__name__}"
-        check("no gh binary: the page is still written, chart omitted, no crash",
-              rc == 0 and out.is_file() and "Omitted" in out.read_text(encoding="utf-8"), rc)
-        out.unlink(missing_ok=True)
-
-        def refused(variant: dict, why: str) -> tuple:
-            """main on a fresh variant of the plan: rc, a file, the refusal."""
-            vf = Path(td) / "variant.json"
-            vf.write_text(json.dumps(variant), encoding="utf-8")
-            err = io.StringIO()
+    # A crash mid-arm is a failure of its own, reported with the checks that
+    # failed before it (a mutant that breaks the renderer reads as killed).
+    try:
+        with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
+            repo = Path(td) / "repo"
+            rpath = repo / roster_lib.ROSTERS_DIR / "wave-r9-groups.json"
+            rpath.parent.mkdir(parents=True)
+            throwaway_git_init(repo, "-q", "-b", "main")
+
+            def commit(r: dict) -> None:
+                rpath.write_text(json.dumps(r), encoding="utf-8")
+                subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
+                subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "r"], check=True)
+            commit(roster)
+            r_, ref_, blob_ = replan.load_roster(str(repo), "main")
+            plan = replan.build_plan(r_, durations, dict(replan.DEFAULT_CAPS), start,
+                                     "v1.0.0", ref_, blob_)
+            planf, snapf = Path(td) / "plan.json", Path(td) / "snap.json"
+            planf.write_text(json.dumps(plan), encoding="utf-8")
+            snapf.write_text(json.dumps(snap), encoding="utf-8")
+
+            rows = {r["g"]: r for r in build_rows(roster, plan, snap)}
+            st = {g: (r["st"], r["label"], r["pr"]) for g, r in rows.items()}
+            check("done: the PR is found by merge commit",
+                  st["R9-DONE-SHA"] == ("done", "merged PR #21", "#21"), st["R9-DONE-SHA"])
+            check("done: the PR is found by branch when no merge commit matches",
+                  st["R9-DONE-BR"] == ("done", "merged PR #22", "#22"), st["R9-DONE-BR"])
+            check("done: no PR found falls back to the commit's sha8",
+                  st["R9-DONE-NONE"] == ("done", "merged at cccccccc", "merged"),
+                  st["R9-DONE-NONE"])
+            check("live", st["R9-LIVE"][0] == "live" and st["R9-LIVE"][1] == "in-progress",
+                  st["R9-LIVE"])
+            check("the open PR maps by the branch-tail fallback",
+                  st["R9-LIVE"][2] == "#31", st["R9-LIVE"])
+            check("the fallback is needed: roster_lib alone does not map it",
+                  roster_lib.group_for_branch(roster, "handoff/r9-live-g-pr") is None)
+            check("an open PR whose branch names no group maps by its title",
+                  st["R9-READY"][2] == "#32", st["R9-READY"])
+            check("a title naming two groups maps to neither",
+                  "#33" not in st["R9-PART"][2] + st["R9-READY"][2], st["R9-PART"])
+            check("partial: a merged R9-PART: title on an open group",
+                  st["R9-PART"][:2] == ("partial", "part merged #23, residual open"),
+                  st["R9-PART"])
+            check("blocked: an after target not done",
+                  st["R9-BLOCK"][:2] == ("blocked", "waiting on LIVE"), st["R9-BLOCK"])
+            check("ready: its only after target is done", st["R9-READY"][0] == "ready",
+                  st["R9-READY"])
+            check("held: a disposition stage is its own class, naming the group it went to",
+                  st["R9-HELD"][:2] == ("held", "absorbed into DONE-SHA"), st["R9-HELD"])
+
+            # The scratch generator's five defects (orch-machinery DESIGN.md S8 and
+            # 6.7), each as a fixture carrying its pre-fix shape; a mutant renderer
+            # line restoring the shape fails the arm (r10_plan_page_mutants.py).
+            # 1: `groups["R10-ARCH-DOCS"] = {... "stage": "not-started"}` overrode a
+            # group the roster calls done. The status is the roster's, every group.
+            check("defect 1: every row's status is the roster's own stage",
+                  all((rows[g]["st"] == "done") == (_stage(e) in roster_lib.DONE_STAGES)
+                      for g, e in roster_lib.groups_of(roster).items()),
+                  {g: rows[g]["st"] for g in rows})
+            # 2: `EDGES = json.load(REPLAN-EDGES.json)`, a scratch graph differing
+            # from the roster's `after`. The fixture graph says R9-READY waits on
+            # R9-LIVE; the roster says it waits on a done group.
+            scratch_edges = {"R9-READY": ["R9-LIVE"]}
+            check("defect 2: the blockers are the roster's after, never a scratch graph",
+                  all(rows[g]["blk"] == [a for a in e.get("after") or []
+                                         if roster_lib.is_open(roster_lib.groups_of(roster)[a])]
+                      for g, e in roster_lib.groups_of(roster).items())
+                  and rows["R9-READY"]["blk"] != scratch_edges["R9-READY"],
+                  {g: rows[g]["blk"] for g in rows})
+            # 3 is the open-issue count, checked on the page below (the issue list
+            # holds a closed issue and the tracking issue: `len(ISS) - 1` reads 3).
+            # 4: `pr=f"#{MERGED[g]}"` printed a commit prefix as a PR number.
+            check("defect 4: a done group with no merged PR names its sha8, never #sha8",
+                  st["R9-DONE-NONE"][2] == "merged" and "#cccccccc" not in st["R9-DONE-NONE"][2]
+                  and not any(r["pr"].startswith("#c") for r in rows.values()), st["R9-DONE-NONE"])
+            # 5: the status text said folded while the pill class stayed `done`. An
+            # absorbed group is held, in text and class, and is not counted merged.
+            check("defect 5: an absorbed group is not rendered done or delivered",
+                  rows["R9-HELD"]["st"] == "held" and "merged" not in rows["R9-HELD"]["label"]
+                  and "deliver" not in rows["R9-HELD"]["label"], rows["R9-HELD"])
+            check("blocked-by is the roster's after less the done groups",
+                  rows["R9-BLOCK"]["blk"] == ["R9-LIVE"] and rows["R9-READY"]["blk"] == [],
+                  (rows["R9-BLOCK"]["blk"], rows["R9-READY"]["blk"]))
+
+            page = render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                          plan, snap)
+            check("a closed issue's chip is struck",
+                  '<span class="chip closer closed" title="eleven">#11</span>' in page)
+            check("an open issue's chip is not",
+                  '<span class="chip" title="twelve">#12</span>' in page
+                  and '<span class="chip closer" title="thirteen">#13</span>' in page)
+            for cls, want in (("done", 3), ("live", 1), ("ready", 1), ("partial", 1),
+                              ("blocked", 1), ("held", 1)):
+                check(f"rows carry the {cls} class", page.count(f'<tr class="{cls}"') == want,
+                      page.count(f'<tr class="{cls}"'))
+                check(f"the summary strip counts {cls}",
+                      f"<b>{want}</b><span>{_STRIP[cls]}</span>" in page)
+            check("defect 3: the open-issue count is the open set less the tracking issue",
+                  "<b>2</b><span>open issues" in page
+                  and len(snap["issues"]) - 1 != 2, re.findall(r"<b>\d+</b><span>open issues", page))
+            check("a page that drew is not the UNAVAILABLE page (null control)",
+                  "UNAVAILABLE" not in page and "<table" in page)
+            check("every template field is filled", "{{" not in page,
+                  re.findall(r"\{\{\w+\}\}", page))
+            check("the round comes from the roster path", "<h1>Round 9 Fix Plan</h1>" in page)
+            model = plan["generated"]["model"]
+            check("the methodology states the plan's sizes and live fraction",
+                  f"S {model['sizes_hours']['S']:g} h" in page
+                  and f"{model['live_remaining_fraction'] * 100:g}%" in page)
+            check("every open group has a bar; no done group does",
+                  all(f'data-name="{short(g)}"' in page for g in rows if rows[g]["st"] != "done")
+                  and 'data-name="DONE-SHA"' not in page)
+            check("critical-path groups carry the mark",
+                  all(rows[g]["crit"] for g in plan["critical_path"])
+                  and page.count('class="critmark"') == len(plan["critical_path"]))
+            check("every open group's tier is shown, and a merged group's is not",
+                  all(f'<td class="tier">{rows[g]["tier"]}</td>' in page
+                      for g in rows if rows[g]["tier"] is not None)
+                  and all(rows[g]["tier"] is None for g in rows if rows[g]["st"] == "done")
+                  and '<td class="tier">—</td>' in page
+                  and '<th title="dispatch tier' in page,
+                  {g: rows[g]["tier"] for g in rows})
+            check("the critical path is tier 0 and production tier 1",
+                  all(rows[g]["tier"] == 0 for g in plan["critical_path"])
+                  and any(rows[g]["tier"] == 1 for g in rows if rows[g]["st"] != "done"),
+                  {g: rows[g]["tier"] for g in rows})
+            check("a planned stamp is drawn", 'class="stampline"' in page)
+            check("the filter and hide-merged controls ship",
+                  'id="hide-done"' in page and 'data-f="blocked"' in page)
+            check("no machine path in the page", not re.search(r"/(home|Users|tmp)/", page))
+            # The caption's figure is the links the chart draws, not the ones it
+            # leaves to the marks: two fixtures where those differ, one each way.
+            links = max(0, len(plan["critical_path"]) - 1)
+            check("the caption counts the links drawn (none drawn, one left)",
+                  page.count('class="critline"') == 0 and links == 1
+                  and f"0 of {links} critical-path links are drawn" in page,
+                  re.findall(r"\d+ of \d+ critical-path links", page))
+            apart = json.loads(json.dumps(plan))
+            apart["groups"]["R9-BLOCK"]["lane"] = "Product UX"  # adjacent lane: drawn
+            page2 = render(roster, f"main:{roster_lib.ROSTERS_DIR}/wave-r9-groups.json",
+                           apart, snap)
+            check("the caption counts the links drawn (one drawn, none left)",
+                  page2.count('class="critline"') == 1
+                  and f"1 of {links} critical-path links are drawn" in page2,
+                  re.findall(r"\d+ of \d+ critical-path links", page2))
+
+            sec = issues_section(roster, plan, snap)
+            check("the issues chart is the first section, drawn from the open set",
+                  0 <= page.find("Projected open issues") < page.find("<h2>Swimlanes")
+                  and "2 open now" in page and "1 other open issues" in page
+                  and sec.count("<polyline") == 1, re.findall(r"\d+ open now", page))
+            no_gh = {"issues": [], "open_prs": [], "merged_prs": [], "offline": True}
+            check("no GitHub state: the chart is omitted with a note",
+                  "Omitted" in issues_section(roster, plan, no_gh)
+                  and "<polyline" not in issues_section(roster, plan, no_gh))
+
+            out = Path(td) / "page.html"
+            argv = ["--plan", str(planf), "--html", str(out), "--repo", str(repo),
+                    "--github-snapshot", str(snapf)]
+            check("a fresh plan renders (null control)",
+                  main(argv, fetch=fetch_refused) == 0 and out.is_file())
+            out.unlink()
+
+            def no_gh_binary(_repo):
+                raise FileNotFoundError("gh")
             try:
-                with contextlib.redirect_stderr(err):
-                    rc = main(["--plan", str(vf)] + argv[2:], fetch=fetch_refused)
-            except Exception as exc:  # a refusal that crashes is not one
+                with contextlib.redirect_stderr(io.StringIO()):
+                    rc = main(argv[:-2], fetch=no_gh_binary)
+            except Exception as exc:  # a crash is the failure this check names
                 rc = f"raised {type(exc).__name__}"
-            return rc, out.exists(), why in err.getvalue()
-        modelless = json.loads(json.dumps(plan))
-        del modelless["generated"]["model"]
-        check("a fresh plan recording no duration model is refused, nothing written",
-              refused(modelless, "generated.model") == (1, False, True),
-              refused(modelless, "generated.model"))
-        violating = json.loads(json.dumps(plan))
-        violating["summary"]["stamps"] += 1
-        check("the violating variant is fresh: only check_plan can refuse it",
-              replan.stale_reason(violating, str(repo)) is None
-              and replan.check_plan(violating))
-        check("a fresh plan that check_plan refuses is refused, nothing written",
-              refused(violating, "summary: stamp count") == (1, False, True),
-              refused(violating, "summary: stamp count"))
-        moved = json.loads(json.dumps(roster))
-        moved["groups"][3]["resume"]["stage"] = "done"
-        commit(moved)
-        rc = main(argv, fetch=fetch_refused)
-        check("a stale plan is refused, nothing written",
-              rc == 1 and not out.exists(), (rc, out.exists()))
-        check("and replan --check refuses the same plan",
-              bool(replan.stale_reason(plan, str(repo))))
+            check("no gh binary: the page is still written, chart omitted, no crash",
+                  rc == 0 and out.is_file() and "Omitted" in out.read_text(encoding="utf-8"), rc)
+            out.unlink(missing_ok=True)
+
+            def refused(variant: dict, why: str) -> tuple:
+                """main on a fresh variant of the plan: rc, a file, the refusal."""
+                vf = Path(td) / "variant.json"
+                vf.write_text(json.dumps(variant), encoding="utf-8")
+                err = io.StringIO()
+                try:
+                    with contextlib.redirect_stderr(err):
+                        rc = main(["--plan", str(vf)] + argv[2:], fetch=fetch_refused)
+                except Exception as exc:  # a refusal that crashes is not one
+                    rc = f"raised {type(exc).__name__}"
+                text = out.read_text(encoding="utf-8") if out.exists() else ""
+                out.unlink(missing_ok=True)
+                return rc, unavailable(text), why in err.getvalue()
+            def unavailable(text: str) -> bool:
+                """The refusal page: the heading, no table, no figure but a dash."""
+                return (text.startswith("<!doctype html>") and "<h1>PLAN UNAVAILABLE — " in text
+                        and "<table" not in text and not re.search(r"<b>\d", text))
+            modelless = json.loads(json.dumps(plan))
+            del modelless["generated"]["model"]
+            check("a fresh plan recording no duration model is refused: the UNAVAILABLE page",
+                  refused(modelless, "generated.model") == (1, True, True),
+                  refused(modelless, "generated.model"))
+            violating = json.loads(json.dumps(plan))
+            violating["summary"]["stamps"] += 1
+            check("the violating variant is fresh: only check_plan can refuse it",
+                  replan.stale_reason(violating, str(repo)) is None
+                  and replan.check_plan(violating))
+            check("a fresh plan that check_plan refuses is refused: the UNAVAILABLE page",
+                  refused(violating, "summary: stamp count") == (1, True, True),
+                  refused(violating, "summary: stamp count"))
+            moved = json.loads(json.dumps(roster))
+            moved["groups"][3]["resume"]["stage"] = "done"
+            commit(moved)
+            with contextlib.redirect_stderr(io.StringIO()):
+                rc = main(argv, fetch=fetch_refused)
+            text = out.read_text(encoding="utf-8") if out.exists() else ""
+            check("a stale plan is refused: the UNAVAILABLE page names the freshness rule",
+                  rc == 1 and unavailable(text) and "freshness" in text, (rc, text[:300]))
+            out.unlink(missing_ok=True)
+            unfetchable = ["--plan", str(planf), "--html", str(out), "--repo", str(repo),
+                           "--roster-ref", "origin/no-such-roster", "--github-snapshot", str(snapf)]
+            with contextlib.redirect_stderr(io.StringIO()):
+                rc = main(unfetchable, fetch=fetch_refused)
+            text = out.read_text(encoding="utf-8") if out.exists() else ""
+            check("an unfetchable roster ref is refused: the UNAVAILABLE page names it",
+                  rc == 1 and unavailable(text) and "origin/no-such-roster" in text,
+                  (rc, text[:300]))
+            out.unlink(missing_ok=True)
+            check("and replan --check refuses the same plan",
+                  bool(replan.stale_reason(plan, str(repo))))
+    except Exception as exc:  # noqa: BLE001 -- reported, never swallowed
+        check("the fixture arms ran to the end", False, f"{type(exc).__name__}: {exc}")
     print(f"plan_page self-test: {n[0]} checks, {len(fails)} failed")
     for f in fails:
         print("FAIL", f)
@@ -838,7 +926,8 @@ def _self_test() -> int:
 
 
 _STRIP = {"done": "groups merged", "live": "fixers working", "ready": "ready, not started",
-          "blocked": "waiting on a group", "partial": "part merged, residual open"}
+          "blocked": "waiting on a group", "partial": "part merged, residual open",
+          "held": "held by a disposition"}
 
 # The page. `{{name}}` is filled by `render`; every value is escaped there.
 _TEMPLATE = """<!doctype html>
@@ -883,6 +972,7 @@ svg{display:block;font-family:var(--mono)}
 .bar.ready{fill:var(--ready-bg);stroke:var(--ready)}
 .bar.blocked{fill:var(--blocked-bg);stroke:var(--blocked)}
 .bar.partial{fill:var(--partial-bg);stroke:var(--partial);stroke-dasharray:3 2}
+.bar.held{fill:var(--blocked-bg);stroke:var(--blocked);stroke-dasharray:1 2}
 .bar.crit{stroke:var(--accent);stroke-width:2.2}
 .barlab{fill:var(--fg);font-size:10.5px;paint-order:stroke;stroke:var(--panel);stroke-width:3;stroke-linejoin:round}
 .critline{fill:none;stroke:var(--accent);stroke-width:1.6;stroke-dasharray:4 3;opacity:.85}
@@ -915,6 +1005,7 @@ td.d{min-width:260px;max-width:440px}
 .pill.ready{background:var(--ready-bg);color:var(--ready);border-color:var(--ready)}
 .pill.blocked{background:var(--blocked-bg);color:var(--blocked);border-color:var(--blocked)}
 .pill.partial{background:var(--partial-bg);color:var(--partial);border-color:var(--partial);border-style:dashed}
+.pill.held{background:var(--blocked-bg);color:var(--blocked);border-color:var(--blocked);border-style:dotted}
 .chip{display:inline-block;font:.76rem var(--mono);border:1px solid var(--line);border-radius:4px;padding:0 5px;margin:0 3px 3px 0}
 .chip.closer{border-color:var(--fg);font-weight:600}
 .chip.closed{text-decoration:line-through;color:var(--muted)}
@@ -939,6 +1030,7 @@ td.d{min-width:260px;max-width:440px}
   <div class="stat"><b>{{n_ready}}</b><span>ready, not started</span></div>
   <div class="stat"><b>{{n_blocked}}</b><span>waiting on a group</span></div>
   <div class="stat"><b>{{n_partial}}</b><span>part merged, residual open</span></div>
+  <div class="stat"><b>{{n_held}}</b><span>held by a disposition</span></div>
   <div class="stat"><b>{{open_iss}}</b><span>open issues (excl. #{{tracking}})</span></div>
   <div class="stat end"><b>{{end}}</b><span>projected programme close</span></div>
 </div>
@@ -952,6 +1044,7 @@ td.d{min-width:260px;max-width:440px}
     <span><i style="background:var(--ready-bg);border-color:var(--ready)"></i>ready</span>
     <span><i style="background:var(--blocked-bg);border-color:var(--blocked)"></i>waiting</span>
     <span><i style="background:var(--partial-bg);border-color:var(--partial);border-style:dashed"></i>part merged</span>
+    <span><i style="background:var(--blocked-bg);border-color:var(--blocked);border-style:dotted"></i>held</span>
     <span><i style="background:transparent;border-color:var(--accent);border-width:2px"></i>critical path (◆ marks each link)</span>
     <span><i style="background:transparent;border-color:var(--done);border-style:dashed"></i>planned stamp</span>
     <span><i style="background:transparent;border:0;border-top:2px solid var(--accent)"></i>groups in flight above the {{slots}}-slot cap line</span>
@@ -968,6 +1061,7 @@ td.d{min-width:260px;max-width:440px}
     <button type="button" data-f="ready" aria-pressed="false">Ready</button>
     <button type="button" data-f="blocked" aria-pressed="false">Waiting</button>
     <button type="button" data-f="partial" aria-pressed="false">Part merged</button>
+    <button type="button" data-f="held" aria-pressed="false">Held</button>
     <button type="button" data-f="done" aria-pressed="false">Merged</button>
     <label class="chk"><input type="checkbox" id="hide-done"> Hide merged</label>
   </div>
diff --git a/tools/audit/seat/state_docs.py b/tools/audit/seat/state_docs.py
index 430c45716..545ba1e04 100644
--- a/tools/audit/seat/state_docs.py
+++ b/tools/audit/seat/state_docs.py
@@ -4,7 +4,8 @@
     python3 tools/audit/seat/state_docs.py [--repo OWNER/REPO] \
         [--roster-ref GITREF [--roster-path PATH] | --roster-file PATH] \
         [--checkout DIR] [--state-ref BR] [--pr-state FILE] \
-        [--mirror DIR] [--push] [--message M]
+        [--mirror DIR] [--push] [--message M] \
+        [--plan PLAN_JSON [--github-snapshot FILE]]
     python3 tools/audit/seat/state_docs.py beat [the same flags] \
         [--watch-ref REF] [--interval SECONDS] [--tip-file PATH] [--once]
     python3 tools/audit/seat/state_docs.py --self-test
@@ -34,6 +35,15 @@ Stateless like the other seat tools: every input is a flag, nothing about a
 session or a machine is hardcoded, stdlib only, and the four generators
 are RUN, never re-implemented -- their logic lives in exactly one place.
 
+`--plan` adds the plan page: `plan_page.py` draws that plan.json (the one
+`tools/plan/replan.py` just wrote) as `PLAN.html`, published in the same
+commit as `PLAN-TABLE.md` -- one ref, one durable path. A page that refuses
+(a stale or violating plan, an unreadable roster) is the UNAVAILABLE page: the
+ref keeps the last good PLAN.html, with its own snapshot time, when it holds
+one, and carries the UNAVAILABLE page when it holds none; either way the call
+publishes the other docs and exits 1, so the caller sees the plan unread. The
+beat runs no replan, so it never passes `--plan`.
+
 `beat` is the recurring half of tvofi's 2026-10-09 instruction that the state
 docs are regenerated continuously rather than at session end. It replaces the
 session-local loop an orchestrator kept in its own scratch directory, which is
@@ -62,6 +72,9 @@ pass then regenerates the docs for it; a sync that refuses (an unreadable
 from __future__ import annotations
 
 import argparse
+import contextlib
+import datetime as dt
+import io
 import json
 import os
 import subprocess
@@ -88,6 +101,8 @@ BEAT_INTERVAL = 300.0
 #: evidence, the older state docs -- is carried, never touched.
 DOC_NAMES = ("PLAN-TABLE.md", "FLOW-BOARD.md", "RESUME-CURRENT.md",
              "NEXT-SESSION-PROMPT.md")
+#: `--plan`'s page, in the write set only on a call that draws it.
+PLAN_PAGE = "PLAN.html"
 
 
 class State(NamedTuple):
@@ -425,6 +440,36 @@ def run_self_test() -> int:
         return self_test()
 
 
+def draw_plan_page(a, staging: Path, page_path: str, prev: str | None):
+    """`plan_page.py` over `--plan`: (staged {path: text}, refusal or None).
+
+    A refusal stages the UNAVAILABLE page only where the state ref holds no
+    PLAN.html; otherwise nothing is staged and the last good page is carried.
+    """
+    target = staging / PLAN_PAGE
+    cmd = [sys.executable, str(SEAT / "plan_page.py"), "--plan", a.plan,
+           "--html", str(target), "--repo", a.checkout, "--gh-repo", a.repo]
+    if a.roster_path:
+        cmd += ["--roster-path", a.roster_path]
+    if a.github_snapshot:
+        cmd += ["--github-snapshot", a.github_snapshot]
+    r = subprocess.run(cmd, cwd=a.checkout, capture_output=True, text=True)
+    text = target.read_text(encoding="utf-8") if target.exists() else ""
+    if r.returncode == 0 and text.strip():
+        return {page_path: text}, None
+    if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:
+        raise Refuse(f"plan_page.py failed rc {r.returncode}: "
+                     f"{(r.stderr or r.stdout).strip()[:400]}")
+    why = (r.stderr.strip().splitlines() or ["refused"])[0]
+    held = bool(prev) and subprocess.run(
+        ["git", "-C", a.checkout, "cat-file", "-e", f"{prev}:{page_path}"],
+        capture_output=True).returncode == 0
+    print(f"state_docs: {PLAN_PAGE} UNAVAILABLE: {why}; "
+          + ("the state ref keeps its last good page" if held
+             else "publishing the UNAVAILABLE page"), file=sys.stderr)
+    return ({} if held else {page_path: text}), why
+
+
 # --------------------------------------------------------------------- main
 def parser(beat_mode: bool = False) -> argparse.ArgumentParser:
     """One flag surface for both forms: `beat` adds only the loop's own
@@ -453,6 +498,11 @@ def parser(beat_mode: bool = False) -> argparse.ArgumentParser:
                    help="push the state ref; without it this is a dry run")
     p.add_argument("--message")
     p.add_argument("--self-test", action="store_true")
+    if not beat_mode:
+        p.add_argument("--plan",
+                       help="plan.json to draw as PLAN.html (plan_page.py)")
+        p.add_argument("--github-snapshot",
+                       help="GitHub state for the plan page instead of gh")
     if beat_mode:
         p.add_argument("--watch-ref", default=WATCH_REF,
                        help="the full ref name a pass reads at origin")
@@ -491,18 +541,25 @@ def main(argv=None) -> int:
         st8 = state_of(roster_round_of(a))
         state_ref = a.state_ref or st8.ref
         print(f"round state: {state_ref} at {st8.dir}/")
+        write_set = st8.write_set
+        prev = remote_tip(a.checkout, f"refs/heads/{state_ref}")
+        unread = None
         with tempfile.TemporaryDirectory() as st:
             staged = generate(a.repo, roster_args, a.checkout, a.pr_state,
                               Path(st), st8.dir)
+            if a.plan:
+                write_set += (f"{st8.dir}/{PLAN_PAGE}",)
+                page, unread = draw_plan_page(a, Path(st), write_set[-1], prev)
+                staged.update(page)
+        rc = 1 if unread else 0
         for path in sorted(staged):
             print(f"generated {path}: "
                   f"{len(staged[path].encode('utf-8'))} bytes")
-        prev = remote_tip(a.checkout, f"refs/heads/{state_ref}")
-        tree = write_tree(a.checkout, staged, prev, st8.write_set)
+        tree = write_tree(a.checkout, staged, prev, write_set)
         if prev:
             changed = run(["git", "diff-tree", "-r", "--name-only", prev,
                            tree], cwd=a.checkout).split()
-            bad = sorted(p for p in changed if p not in st8.write_set)
+            bad = sorted(p for p in changed if p not in write_set)
             if bad:  # unreachable while write_tree's guard holds; checked
                 raise Refuse(  # again here, before any commit exists to push
                     f"the commit would touch paths outside the write set: "
@@ -511,11 +568,11 @@ def main(argv=None) -> int:
                 print(f"already current: {state_ref} at {prev[:12]} carries "
                       "these bytes; nothing to commit or push")
                 mirror_files(staged, a.mirror)
-                return 0
+                return rc
         else:
             names = run(["git", "ls-tree", "-r", "--name-only", tree],
                         cwd=a.checkout).split()
-            if sorted(names) != sorted(st8.write_set):
+            if sorted(names) != sorted(write_set):
                 raise Refuse(f"the first commit on {state_ref} would carry "
                              f"{sorted(names)}, not exactly the write set")
         message = a.message or (
@@ -535,13 +592,108 @@ def main(argv=None) -> int:
         else:
             print(f"ready: would push {state_ref} at {commit} (no --push)")
         mirror_files(staged, a.mirror)
-        return 0
+        return rc
     except Refuse as e:
         print(f"state_docs: REFUSED: {e}", file=sys.stderr)
         return 2
 
 
 # ---------------------------------------------------------------- self-test
+def plan_page_arms(root: Path, ok, git) -> None:
+    """`--plan`: the page in the same commit as the plan table; a refused
+    page keeps the last good one at the ref, or publishes the UNAVAILABLE
+    page where there is none; both exit 1. A roster at a ref, because the
+    plan's freshness is a blob at a ref (replan.stale_reason)."""
+    sys.path.insert(0, str(SEAT.parents[1] / "plan"))
+    import replan
+    from throwaway_git import throwaway_git_clone, throwaway_git_init
+    seed, bare, drv = root / "pseed", root / "p.git", root / "pdrv"
+    rel = f"{roster_lib.ROSTERS_DIR}/wave-r9-groups.json"
+    (seed / rel).parent.mkdir(parents=True)
+    groups = [{"group": "R9-P", "lane": "IN", "kind": "defect", "size": "S",
+               "issues": [], "fixes": [], "after": [], "brief": "fixture P.",
+               "resume": {"stage": "not-started"}}]
+    (seed / rel).write_text(json.dumps({"groups": groups}), encoding="utf-8")
+    throwaway_git_init(seed, "-q", "-b", "main")
+    git("-C", str(seed), "add", "-A")
+    git("-C", str(seed), "commit", "-q", "-m", "plan roster")
+    throwaway_git_clone(seed, bare, "-q", "--bare")
+    throwaway_git_clone(bare, drv, "-q")
+    durations = json.loads((SEAT.parents[1] / "plan" / "durations.json")
+                           .read_text(encoding="utf-8"))
+    r_, ref_, blob_ = replan.load_roster(str(drv), "main")
+    plan = replan.build_plan(r_, durations, dict(replan.DEFAULT_CAPS),
+                             dt.datetime(2026, 1, 5), "v1.0.0", ref_, blob_)
+    planf, snapf = root / "plan.json", root / "psnap.json"
+    planf.write_text(json.dumps(plan), encoding="utf-8")
+    snapf.write_text(json.dumps({"issues": [], "open_prs": [], "merged_prs": []}),
+                     encoding="utf-8")
+    mirror, prs = root / "pmirror", root / "pprs.json"
+    prs.write_text("[]", encoding="utf-8")
+    argv = ["--checkout", str(drv), "--roster-ref", "main", "--pr-state", str(prs),
+            "--plan", str(planf),
+            "--github-snapshot", str(snapf), "--mirror", str(mirror), "--push"]
+    state_ref, sdir, write_set = state_of(9)
+    page_path = f"{sdir}/{PLAN_PAGE}"
+
+    def at(tip, path):
+        r = subprocess.run(["git", "-C", str(bare), "show", f"{tip}:{path}"],
+                           capture_output=True, text=True)
+        return r.stdout if r.returncode == 0 else None
+
+    def tip_of(ref):
+        r = subprocess.run(["git", "-C", str(bare), "rev-parse", "-q", "--verify",
+                            f"refs/heads/{ref}"], capture_output=True, text=True)
+        return r.stdout.strip() or "no-such-ref"
+
+    err = io.StringIO()
+    with contextlib.redirect_stderr(err):
+        rc = main(argv)
+    ok("plan page: the first --plan call exits 0", rc == 0, err.getvalue()[-600:])
+    if rc:
+        return
+    tip1 = tip_of(state_ref)
+    good = at(tip1, page_path) or ""
+    ok("plan page: a fresh plan draws PLAN.html in the plan table's commit",
+       rc == 0 and "Fix Plan" in good and "UNAVAILABLE" not in good
+       and at(tip1, write_set[0]) is not None, (rc, good[:200]))
+    ok("plan page: the mirror carries PLAN.html",
+       (mirror / PLAN_PAGE).read_text(encoding="utf-8") == good)
+    ok("plan page: without --plan the write set holds no PLAN.html (null control)",
+       page_path not in write_set)
+    # The roster moves under the plan: plan_page refuses it as stale.
+    groups[0]["resume"]["stage"] = "in-progress"
+    (drv / rel).write_text(json.dumps({"groups": groups}), encoding="utf-8")
+    git("-C", str(drv), "commit", "-q", "-am", "roster moved")
+    err = io.StringIO()
+    with contextlib.redirect_stderr(err):
+        rc = main(argv)
+    tip2 = tip_of(state_ref)
+    ok("plan page: a stale plan keeps the last good page at the ref, exit 1",
+       rc == 1 and tip2 != tip1 and at(tip2, page_path) == good
+       and "keeps its last good page" in err.getvalue(),
+       (rc, tip2 == tip1, err.getvalue()[-300:]))
+    with contextlib.redirect_stderr(io.StringIO()):
+        rc = main(argv + ["--state-ref", "fresh-state"])
+    first = at(tip_of("fresh-state"), page_path) or ""
+    ok("plan page: with no page at the ref, the UNAVAILABLE page is published",
+       rc == 1 and "<h1>PLAN UNAVAILABLE — " in first and "<table" not in first,
+       (rc, first[:200]))
+    # A crash is not a refusal: plan_page.py dies on a malformed plan.json
+    # with a traceback, rc 1 and no page. That must refuse with rc 2 and
+    # publish nothing, not an empty PLAN.html at exit 1.
+    badf = root / "bad-plan.json"
+    badf.write_text("{", encoding="utf-8")
+    crash_argv = [str(badf) if x == str(planf) else x for x in argv]
+    err = io.StringIO()
+    with contextlib.redirect_stderr(err):
+        rc = main(crash_argv + ["--state-ref", "crash-state"])
+    ok("plan page: a crashing page refuses with rc 2 and publishes no PLAN.html",
+       rc == 2 and tip_of("crash-state") == "no-such-ref"
+       and "plan_page.py failed rc 1" in err.getvalue(),
+       (rc, tip_of("crash-state"), err.getvalue()[-300:]))
+
+
 def self_test() -> int:
     """Offline: tmp dirs and fixture repos, no network in any arm."""
     sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
@@ -635,6 +787,7 @@ def self_test() -> int:
            == sorted(Path(p).name for p in WRITE_SET))
         ok("parent is the previous tip",
            state0 in git("-C", str(bare), "log", "--format=%P", "-1", tip))
+        plan_page_arms(root, ok, git)
         # THE GUARD: a write outside the four files refuses, in both the
         # direct check and a real write_tree call over the live tip.
         try:
diff --git a/tools/audit/seat/sweep_render.py b/tools/audit/seat/sweep_render.py
index 1fe34ea35..6ff465e85 100644
--- a/tools/audit/seat/sweep_render.py
+++ b/tools/audit/seat/sweep_render.py
@@ -67,7 +67,7 @@ HOST = re.compile(HOME_DIR)
 #: the self-test pins; the template is still the one owner of the wording.
 DEFAULTS = {
     "record beat: the replan": "tools/plan/replan.py --out",
-    "record beat: the plan page": "tools/audit/seat/plan_page.py --plan",
+    "record beat: the plan page": "state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}",
     "tick board read unfiltered": "REVIEW OWED",
     "tick board: owner flags": "OWNER FLAG:",
     "tick board: design builds": "DESIGN-BUILD:",
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index d83f27918..89a683fab 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -35,8 +35,8 @@ rendered text that no overlay value supplied.
 | `seat_ledger` | the session's seat ledger file, updated every sweep |
 | `plan_slots` | `replan.py --slots`: concurrent fixer slots the plan schedules (10 unless the owner set another) |
 | `plan_seats` | `replan.py --seats`: seats the plan may use (99 unless the owner set another) |
-| `plan_json` | the plan JSON `replan.py --out` writes and `plan_page.py --plan` reads |
-| `plan_page` | the plan page `plan_page.py --html` writes, republished at the same path |
+| `plan_json` | the plan JSON `replan.py --out` writes and `state_docs.py --plan` draws |
+| `plan_page` | the plan page, `PLAN.html` in the state mirror (`state_docs.py --plan` writes it), republished at the same path |
 | `state_mirror` | the directory `state_docs.py --mirror` writes |
 | `tick_alive` | the tick seat's liveness file, touched every pass |
 | `tick_log` | the tick seat's log |
@@ -62,7 +62,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4) After each merge (`dev/governance/roles/nudge.md` steps 12 and 18): `tools/audit/seat/roster_edit.py set-stage` for a roster group, one #201 comment through `tools/pr/gh_comment.py` with its read-back, `tools/audit/worktree_gc.sh {{repo}}`, the issues the merge commit closed read back (`dev/governance/roles/orchestrator.md` section 4), and the finished seat's worktrees under {{seat_root}} and its scratch removed.
 
-(4b) Record beat, every sweep, merge or none: `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}}`, then `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}}`, then `python3 tools/audit/seat/plan_page.py --plan {{plan_json}} --html {{plan_page}}`, republished at the same path.
+(4b) Record beat, every sweep, merge or none: `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, which publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. Exit 1 there is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): re-run the replan, never hand-run `plan_page.py` around the refusal.
 
 (4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first.
 

