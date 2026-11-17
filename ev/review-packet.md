# Review packet #3694
head: fe298a641f0da65a76394a24cb693bb44480f4c4
base: 38bf516bdd73f926ee9639ffda7b9ca5163fd50e

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133764672359 success
arch-score / arch-score id=133776392920 success
arm id=133760838641 skipped
budget-raise-gate / budget-raise-gate id=133776331329 success
cancel-superseded id=133776390156 success
codeql id=133776387025 skipped
codeql / Analyze (actions) id=133764362607 success
codeql / Analyze (javascript-typescript) id=133764362846 success
codeql / Analyze (python) id=133764362606 success
gate id=133776329538 success
governance id=133776365314 skipped
governance / env-matrix id=133764362623 success
governance / instrument-self-tests id=133764362812 failure
governance / policy-docs id=133764362772 success
governance / record id=133764364640 skipped
governance / wave-script id=133764362713 success
hassfest id=133776390137 skipped
hassfest / hassfest id=133764362621 success
kernel-points id=133776329800 skipped
pr-contract id=133776330402 skipped
pr-contract / pr-contract id=133774059770 success
prelude id=133776379665 success
refresh id=133776390617 success
sweep-self id=133778135550 skipped
tests id=133776329976 skipped
tests / arch-instrument id=133764758789 success
tests / briefs id=133764362818 success
tests / browser id=133764758798 success
tests / ci-ratchet id=133774061024 skipped
tests / claims-autofix id=133767135131 skipped
tests / closure-scope id=133764362751 success
tests / closures id=133764758825 success
tests / closures-autofix id=133774061468 skipped
tests / coverage id=133764758816 success
tests / coverage-ratchet id=133766579201 success
tests / fast (3.14) id=133764758729 success
tests / graders-head-copy id=133766578987 success
tests / lane-proofs id=133767993805 success
tests / mutation id=133764362831 success
tests / mutation-autofix id=133764940902 skipped
tests / mutation-pins id=133764940865 skipped
tests / nightly-ha id=133764760668 skipped
tests / nightly-status id=133764362805 failure
tests / replay id=133764761528 skipped
tests / typing id=133764758814 success
validate id=133776330308 skipped
validate / validate-hacs id=133764362439 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item e5017aca: dismissed:the read takes its universe from the command at each run, so nothing is to be built; only a figure quoted from before this merge is stale, and the read's group is carries-open
NOTE body item e72411f5: R11-INTAKE-R10-RESIDUE
NOTE body item c9cc8bee: R11-INTAKE-R10-RESIDUE
NOTE body item 1d7ad66f: dismissed:built in #3625 and here
NOTE body item 478c4880: dismissed:one occurrence; the body above states what was left so a later dispatch need not re-derive it
NOTE body item e0062a82: dismissed:corrected by this diff, whose arms are the control the carry lacked
CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/audit/enumerate.py --self-test
             `tools/audit/enumerate.py` is in the tree at this head
  ok         python3 -I tools/audit/enumerate.py d12-cells | wc -l
             `tools/audit/enumerate.py` is in the tree at this head
  ok         python3 -I tools/audit/enumerate.py --briefs
             `tools/audit/enumerate.py` is in the tree at this head
  ok         node tools/policy/check-wave-script.mjs
             `tools/policy/check-wave-script.mjs` is in the tree at this head
  ok         python3 -I tools/audit/check_scopes.py --repo .
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 38bf516bdd73f926ee9639ffda7b9ca5163fd50e
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 -I tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1 tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git grep -n -E "population_axes\(|check_scopes\.population\(|[^_a-z]population\(" -- tools dev/audit tests
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/audit/enumerate.py
             `tools/audit/enumerate.py` is in the tree at this head
  ok         tools/audit/product_reads.py
             `tools/audit/product_reads.py` is in the tree at this head
  ok         tools/audit/check_scopes.py
             `tools/audit/check_scopes.py` is in the tree at this head
  ok         tools/audit/seat/plant_recall.py
             `tools/audit/seat/plant_recall.py` is in the tree at this head
  ok         dev/audit/rounds/round9/D13/s1/dora_by_job.py
             `dev/audit/rounds/round9/D13/s1/dora_by_job.py` is in the tree at this head

FIGURES: 16 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3694.md b/dev/programme/delivery/3694.md
new file mode 100644
index 0000000000..782eaca1ea
--- /dev/null
+++ b/dev/programme/delivery/3694.md
@@ -0,0 +1 @@
+- [#3694](https://github.com/tvofi/heatpump_optimizer/pull/3694) — **open**, R11-PRE-BRIEFS-CENSUS, part 2: enumerate.py d12-cells prints the declared levels of tank volume and house size as cells (R11-PRE-BRIEFS-CENSUS)
diff --git a/tools/audit/enumerate.py b/tools/audit/enumerate.py
index 66e7b67c91..0578f26680 100644
--- a/tools/audit/enumerate.py
+++ b/tools/audit/enumerate.py
@@ -21,7 +21,8 @@ Usage: python3 -I tools/audit/enumerate.py <universe> [--repo DIR] [options]
   d9-collections         coordinator.py `self.<attr>` bound to a container, once per class and attribute
   d9-attributes          classes defining or assigning extra_state_attributes
   d9-solves              calls of the solver entry, then of each function holding one, to a fixed point
-  d12-cells [--pairs]    every level `check_scopes.py --population` reads, the card and the blueprints
+  d12-cells [--pairs]    every level `check_scopes.py --population` reads, each level one of its NO-READ
+                         axes declares in objective.json, the card and the blueprints
                          (--pairs: every pair of levels from two axes), each `not run` until a ledger row
   --ledger TSV           with any universe: each line beside its ledger row's asserting test, or `not run`
                          (rows: item, test; for d12-cells: cell, source, test); a row naming no item,
@@ -401,14 +402,18 @@ def tracked(repo):
 
 def population_axes(repo):
     """{axis: [levels]} as `check_scopes.py --population` reads them, by its own reader, and the
-    two totals it prints; a binary axis key is its own axis with levels present and absent."""
+    two totals it prints; a binary axis key is its own axis with levels present and absent. An
+    axis it prints NO-READ is an axis all the same once its row declares `levels` (the continuous
+    ones: no source holds them), and both totals are raised by what those levels add."""
     obj = repo / OBJECTIVE
     sys.path.append(str(Path(__file__).resolve().parent))
     import check_scopes
-    lines, ok = check_scopes.population(json.loads(obj.read_text()).get("population", []), tracked(repo), lambda f: (repo / f).read_text())
+    spec = json.loads(obj.read_text()).get("population", [])
+    lines, ok = check_scopes.population(spec, tracked(repo), lambda f: (repo / f).read_text())
     if not ok:
         raise Refuse("the population is unreadable: " + "; ".join(l for l in lines if l.startswith("UNREADABLE")))
-    axes, totals = {}, {}
+    declared = {a.get("axis"): [str(k) for k in a["levels"]] for a in spec if a.get("levels")}
+    axes, totals, added = {}, {}, []
     for l in lines:
         if "\t" not in l:
             k, _, v = l.partition(": ")
@@ -416,12 +421,18 @@ def population_axes(repo):
             continue
         name, _, rest = l.partition("\t")
         n, _, lv = rest.partition("\t")
-        if n == "NO-READ":
+        if n == "NO-READ" and name in declared:
+            axes[name] = declared[name]
+            added.append(len(declared[name]))
+            print(f"NO-READ axis {name}: its cells are the levels {OBJECTIVE} declares, which no reader compares with their source", file=sys.stderr)
+        elif n == "NO-READ":
             print(f"NO-READ axis {name}: no cell until {OBJECTIVE} declares its levels", file=sys.stderr)
         elif n.endswith("binary axes"):
             axes.update({k: ["absent", "present"] for k in lv.split(",")})
         else:
             axes[name] = lv.split(",")
+    totals["PAIRS"] += totals["LEVELS"] * sum(added) + (sum(added) ** 2 - sum(n * n for n in added)) // 2
+    totals["LEVELS"] += sum(added)
     return axes, totals
 
 
@@ -925,6 +936,17 @@ def self_test():
             msg = str(e)
         arm("a ledger refusal names the row's line", f"{led}:2:" in msg, True)
         arm("d12 a missing ledger is refused", count("d12-cells", t, ledger=str(t / "none.tsv")), "Refuse")
+        edit_json(OBJECTIVE, lambda d: d["population"][2].update(levels={"min": 1, "max": 9}))(t)
+        with contextlib.redirect_stderr(io.StringIO()):
+            arm("d12 a NO-READ axis whose levels are declared is one cell per level", [l for l in run("d12-cells", t) if "size" in l],
+                ["level size=max\tnot run", "level size=min\tnot run"])
+        arm("d12 a declared level pairs with every level of another axis", count("d12-cells", t, pairs=True), (4 + 2) + (4 + 4 * 2) + 2)
+        led.write_text("level size=min\tsimulation\ttests/x.py::t\n")
+        arm("d12 ledger: a declared level's row is joined", count("d12-cells", t, ledger=str(led)), 4 + 2 + 2)
+        edit_json(OBJECTIVE, lambda d: d["population"].append({"axis": "area", "kind": None, "levels": {"lo": 1, "hi": 2}, "no_read": "r", "builder": "G"}))(t)
+        arm("d12 two declared axes pair with each other once", count("d12-cells", t, pairs=True), (4 + 4) + (4 + 4 * 4 + 2 * 2) + 2)
+        edit_json(OBJECTIVE, lambda d: (d["population"].pop(), d["population"][2].update(levels={})))(t)
+        arm("d12 a NO-READ axis declaring no level is no cell", count("d12-cells", t), 4 + 2)
         arm("with no ledger a census prints its items alone", run("d1-inputs", t)[:2], ["input CONF_A_ENTITY", "input CONF_B_ENTITY"])
         for label, text, want in (("a census line is joined to its driving test, the rest not run", "# c\n\ninput CONF_A_ENTITY\ttests/x.py::t\n",
                                    ["input CONF_A_ENTITY\ttests/x.py::t"] + [f"input {k}\tnot run" for k in ("CONF_B_ENTITY", "CONF_F_SENSOR", "CONF_H1", "CONF_H2", "CONF_W_SENSOR")]),

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
