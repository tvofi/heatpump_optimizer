# Review packet #3735
head: 20edc8b3cdc7a1270a7c0238e04ecdf6cfad725d
base: a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=136945889742 success
arch-score / arch-score id=136945783832 success
arm id=136945525895 skipped
budget-raise-gate / budget-raise-gate id=136945783830 failure
cancel-superseded id=136945530497 success
codeql id=136945762933 skipped
codeql / Analyze (actions) id=136945783854 success
codeql / Analyze (javascript-typescript) id=136945783874 success
codeql / Analyze (python) id=136945783918 success
gate id=136946096757 failure
governance id=136945763399 skipped
governance / env-matrix id=136945783860 in_progress
governance / instrument-self-tests id=136945783926 in_progress
governance / policy-docs id=136945783810 success
governance / record id=136945785299 skipped
governance / wave-script id=136945783941 success
hassfest id=136945763250 skipped
hassfest / hassfest id=136945783815 success
kernel-points id=136945784601 skipped
pr-contract id=136946097253 skipped
prelude id=136945530749 success
refresh id=136945530676 success
sweep-self id=136946448191 skipped
tests id=136945763427 skipped
tests / arch-instrument id=136946216549 in_progress
tests / briefs id=136945783817 success
tests / browser id=136946216505 in_progress
tests / closure-scope id=136945783870 success
tests / closures id=136946216516 in_progress
tests / coverage id=136946216467 in_progress
tests / fast (3.14) id=136946216513 in_progress
tests / mutation id=136945783811 success
tests / mutation-autofix id=136946458077 skipped
tests / mutation-pins id=136946456563 skipped
tests / nightly-ha id=136946218136 skipped
tests / nightly-status id=136945783889 success
tests / replay id=136946217977 skipped
tests / typing id=136946216407 success
validate id=136945763494 skipped
validate / validate-hacs id=136945783770 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 136945783926: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 20edc8b3cdc7a1270a7c0238e04ecdf6cfad725d in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 8 script(s) run, 25 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/policy/budget_raise_gate.py --base $(git merge-base origin/main HEAD) --head HEAD --pr 3735
             `tools/policy/budget_raise_gate.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 4 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3735.md b/dev/programme/delivery/3735.md
new file mode 100644
index 0000000000..771f99440a
--- /dev/null
+++ b/dev/programme/delivery/3735.md
@@ -0,0 +1 @@
+- [#3735](https://github.com/tvofi/heatpump_optimizer/pull/3735) — **open**, R11-SEAM-ratchet-raise: ratchet raise (R11-SEAM-ratchet-raise)
diff --git a/tests/structure.py b/tests/structure.py
index 87a5d72cd4..095a39f220 100644
--- a/tests/structure.py
+++ b/tests/structure.py
@@ -35,6 +35,10 @@ Metrics (definitions, one line each; the code is the authority):
                               copies merged, dead code deleted -- lower it
                               (#2285's review). A class under the limit costs
                               nothing, so a new small class is free
+  module_excess_loc           every module's span past MODULE_LOC_LIMIT,
+                              summed: a module-level function in no class and
+                              under the function thresholds is priced
+                              (D7-s1-04)
   max_method_loc              the largest function span in the integration --
                               the WORST offender, not a count of offenders
                               (#374). Reads 0 when nothing exceeds
@@ -98,8 +102,10 @@ Metrics (definitions, one line each; the code is the authority):
                               comprehension clause and its ifs, each match
                               case), counted over the whole function span
                               including nested defs
-  const_modules_over_50       modules importing more than 50 names from
-                              ``.const``
+  const_modules_over_50       modules reading more than 50 distinct names of
+                              ``.const``, through ``from .const import`` or a
+                              binding of the module (``const.X``): a
+                              re-spelling moves nothing (D7-s1-01)
   import_cycle_modules        modules in a cycle of the package's import
                               graph, function-scope imports in and imports
                               under ``if TYPE_CHECKING:`` out (#1738)
@@ -257,6 +263,9 @@ DUP_WINDOW_STATEMENTS = 2
 DUP_MIN_NODES = 30
 CC_LIMITS = (25, 15)
 CONST_FANOUT_LIMIT = 50
+# The module span past which a module's lines are priced (owner, 2026-11-18;
+# D7-s1-04): module_excess_loc sums each module's lines beyond it.
+MODULE_LOC_LIMIT = 2000
 
 # The seam partition of #193's plan of record. A coordinator method's seam is
 # its entry in SEAM_MAP_FILE, never its name (#1539): bucketing by name let a
@@ -2925,6 +2934,44 @@ def class_excess(trees: list[tuple[Path, ast.Module]],
 # the metrics
 
 
+def module_excess(trees: list[tuple[Path, ast.Module]]) -> int:
+    """``module_excess_loc``: each module's span past MODULE_LOC_LIMIT, summed (D7-s1-04).
+
+    The class rows price lines inside a class, and the function rows a
+    function crossing 150 lines or CC 15. A module-level function under both
+    was in no row: coordinator.py could grow beside its class while the class
+    rows fell. A module's span runs from line 1 to the end of its last
+    statement, so lines cost the same in a class, a helper or a function, and
+    a module under the limit costs nothing. A sum, not a threshold count: a
+    count stops pricing a module once it has crossed the line.
+    """
+    return sum(max(0, (tree.body[-1].end_lineno if tree.body else 0) - MODULE_LOC_LIMIT)
+               for _path, tree in trees)
+
+
+def const_names_read(tree: ast.Module) -> set[str]:
+    """The distinct ``.const`` names a module reads, by either spelling (D7-s1-01).
+
+    ``from .const import X`` and ``const.X`` off ``from . import const [as c]``
+    are the same dependency. Counting only the names on from-import statements
+    read entry_config.py's 118 binding reads as 3. A re-spelling of
+    thermal_model.py's from-import lowered the row with the coupling unchanged.
+    """
+    names: set[str] = set()
+    bindings: set[str] = set()
+    for node in ast.walk(tree):
+        if not isinstance(node, ast.ImportFrom):
+            continue
+        if (node.level == 1 and node.module == "const") or node.module == "heatpump_optimizer.const":
+            names |= {a.name for a in node.names}
+        elif node.level == 1 and node.module is None:
+            bindings |= {a.asname or a.name for a in node.names if a.name == "const"}
+    if bindings:
+        names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
+                  and isinstance(n.value, ast.Name) and n.value.id in bindings}
+    return names
+
+
 def measure() -> dict:
     """Recompute every metric from the working tree. Returns a dict with the
     flat metric values (the budget keys) under ``metrics`` and everything the
@@ -2935,7 +2982,7 @@ def measure() -> dict:
     god_classes = []       # (loc, file, span, name, methods)
     monsters = []          # (loc, file, span, name)
     cc_scores = []         # (cc, file, line, name)
-    const_fanout = {}      # file -> imported names from .const
+    const_fanout = {}      # file -> distinct .const names read, by either spelling
 
     # -- classes, functions, imports, dead symbols -------------------------
     top_level_defs: dict[tuple[str, str], int] = {}
@@ -2978,13 +3025,7 @@ def measure() -> dict:
             if cc > CC_LIMITS[1]:
                 cc_scores.append((cc, rel, fn.lineno, fn.name))
 
-        fanout = 0
-        for node in ast.walk(tree):
-            if isinstance(node, ast.ImportFrom) and (
-                (node.level == 1 and node.module == "const")
-                or node.module == "heatpump_optimizer.const"
-            ):
-                fanout += len(node.names)
+        fanout = len(const_names_read(tree))
         if fanout:
             const_fanout[rel] = fanout
 
@@ -3024,6 +3065,9 @@ def measure() -> dict:
         # Every class's lines past the limit, the coordinator's helpers in
         # its span: growth anywhere is priced, a verbatim move is not a gain.
         "class_excess_loc": excess,
+        # Every module's lines past MODULE_LOC_LIMIT: lines outside any
+        # class are priced too (D7-s1-04).
+        "module_excess_loc": module_excess(trees),
         # The worst offender, off tables that are already built and already
         # sorted (#374). The four threshold counts above stop pricing a
         # function once it has crossed the line, so without these two the
@@ -3110,7 +3154,7 @@ def print_report(result: dict) -> None:
           " module docstring)" % metrics["max_cc"])
 
     print()
-    print("########## .const import fan-out (names imported per module) ##########")
+    print("########## .const fan-out (distinct names read per module, either spelling) ##########")
     for rel, n in tables["const_fanout"].items():
         flag = "  > %d" % CONST_FANOUT_LIMIT if n > CONST_FANOUT_LIMIT else ""
         print(f"  {rel}: {n}{flag}")
@@ -4185,6 +4229,47 @@ def class_self_check() -> tuple[tuple[str, bool], ...]:
     )
 
 
+def const_self_check() -> tuple[tuple[str, bool], ...]:
+    """Pin const_modules_over_50's key (D7-s1-01): the distinct names read, by either spelling."""
+    names = [f"CONF_K{i}" for i in range(CONST_FANOUT_LIMIT + 1)]
+    imported = "from .const import " + ", ".join(names) + "\nX = [" + ", ".join(names) + "]\n"
+    bound = "from . import const\nX = [" + ", ".join(f"const.{n}" for n in names) + "]\n"
+    aliased = "from . import const as c\nX = [" + ", ".join(f"c.{n}" for n in names) + "]\n"
+    both = "from .const import CONF_K0\n" + bound
+    unbound = "X = [" + ", ".join(f"other.{n}" for n in names) + "]\n"
+
+    def read(src: str) -> int:
+        return len(const_names_read(ast.parse(src)))
+
+    return (
+        ("a from-import re-spelled as a binding read moves no const row",
+         read(bound) == read(imported) == CONST_FANOUT_LIMIT + 1),
+        ("a read through an aliased binding of const counts", read(aliased) == read(bound)),
+        ("a name read by both spellings counts once", read(both) == read(bound)),
+        ("an attribute read off a name that is not a const binding is no const read",
+         read(unbound) == 0),
+    )
+
+
+def module_self_check() -> tuple[tuple[str, bool], ...]:
+    """Pin module_excess_loc (D7-s1-04): a module's growth is priced wherever in it the lines land."""
+    under = "".join(f"x{i} = {i}\n" for i in range(MODULE_LOC_LIMIT))
+    fn = "def grown():\n" + MOVED_BODY
+    method = "class Grown:\n" + "".join("    " + ln + "\n" for ln in fn.splitlines())
+    added = span_loc(ast.parse(fn).body[0])
+
+    def excess(src: str) -> int:
+        return module_excess([(PACKAGE_DIR / "m.py", ast.parse(src))])
+
+    return (
+        ("a module at the module limit costs nothing", excess(under) == 0),
+        ("a module-level function past the module limit is priced by its lines",
+         excess(under + fn) == added),
+        ("the same lines in a class past the module limit cost the same",
+         excess(under + method) == excess(under + fn) + 1),
+    )
+
+
 # ``HA_ENTITY_METHODS``' two halves, side by side: the same member name on the
 # class HA instantiates and on one it does not. A key of the name alone reads
 # both the same -- the entry would then silence a same-named member of a class
@@ -4357,6 +4442,8 @@ def self_check() -> int:
         *role_self_check(),
         *typed_self_check(),
         *class_self_check(),
+        *const_self_check(),
+        *module_self_check(),
         *entity_self_check(),
     )
     failures = [message for message, ok in rules if not ok]
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f3676b586c..2250123720 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,6 +1,6 @@
 {
  "class_excess_loc": 17322,
- "const_modules_over_50": 3,
+ "const_modules_over_50": 4,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
  "coordinator_private_reach": 0,
@@ -15,7 +15,8 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
+ "module_excess_loc": 21718,
  "name_kept_members": 38,
- "recorded_at": "8751943e17ef4d3ec699e7859ae829b4528d8ce7",
+ "recorded_at": "e698fc8ac374a1d72c230b55d938d75b03b7de67",
  "seam_cut_total": 415
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
