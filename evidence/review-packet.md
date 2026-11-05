# Review packet #3218
head: 0a13dd1a9c053948311df30953557ddb6b341120
base: a45cf7f509477596e8024ad2293073f83f04d3e3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=126948521094 skipped
cancel-superseded id=126949535834 queued
prelude id=126949536023 queued
refresh id=126949535528 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified python3 -c
             python3 runs an inline script rather than a file
  ok         tools/audit/archscore/metrics/footprint.py
             `tools/audit/archscore/metrics/footprint.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head

FIGURES: 5 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/3218.md b/dev/programme/delivery/3218.md
new file mode 100644
index 000000000..612a1c2c9
--- /dev/null
+++ b/dev/programme/delivery/3218.md
@@ -0,0 +1 @@
+- [#3218](https://github.com/tvofi/heatpump_optimizer/pull/3218) — **open**, R10-FLY-ARCHSCORE-STMT-PACKING: fly archscore stmt packing (R10-FLY-ARCHSCORE-STMT-PACKING)
diff --git a/tests/arch_score.py b/tests/arch_score.py
index bae038e26..20fafdc4f 100644
--- a/tests/arch_score.py
+++ b/tests/arch_score.py
@@ -56,7 +56,7 @@ from harness import Results  # noqa: E402
 from throwaway_git import throwaway_git_init  # noqa: E402
 
 from archscore import calibrate, gate, score, vector  # noqa: E402
-from archscore.metrics import card  # noqa: E402
+from archscore.metrics import card, footprint  # noqa: E402
 
 FROZEN_WEIGHTS = "2891a874ad476d7d761743ae7c47bae9779e150190aaf65f9a82e06ddd867978"
 
@@ -439,6 +439,29 @@ def main() -> int:
         R.check("the rename null reads NULL",
                 next(r for r in rows if r["id"] == "rt_00_null_rename")["verdict"] == "NULL")
 
+    # coord_footprint (counter C25): a packed statement reads as the plain ones it spells.
+    def _n(src: str) -> int:
+        return footprint.logic_stmts(ast.parse(src))
+
+    packed_plain = [
+        ("a, b, c = (f(x) for x in xs)", "a = f(xs[0])\nb = f(xs[1])\nc = f(xs[2])"),
+        ("a, b = f(x), g(y)", "a = f(x)\nb = g(y)"),
+        ("a = b = f(x)", "a = f(x)\nb = f(x)"),
+        ("a, b = x.p, x.q", "a = x.p\nb = x.q"),
+        ("a = b = x.p", "a = x.p\nb = x.p"),
+        ("f(x), g(y)", "f(x)\ng(y)"),
+        ("f(x + 1), g(y + 1)", "f(x + 1)\ng(y + 1)"),
+        ("with p() as a, q() as b:\n    pass", "with p() as a:\n    with q() as b:\n        pass"),
+        ("import os, sys", "import os\nimport sys"),
+        ("del a, b", "del a\ndel b"),
+    ]
+    R.check("coord_footprint reads a packed statement as the plain statements it spells (every packing shape)",
+            all(_n(pk) == _n(pl) for pk, pl in packed_plain),
+            f"{[(pk, _n(pk), _n(pl)) for pk, pl in packed_plain if _n(pk) != _n(pl)]}")
+    R.check("coord_footprint control: an unpacked body and a single destructuring read one statement each",
+            _n("a = f(x + 1)") == 1 and _n("a, b = pair") == 2 and _n("a = x.p") == 0,
+            f"{_n('a = f(x + 1)')} {_n('a, b = pair')} {_n('a = x.p')}")
+
     # The check can fail: a moved case must not read as it did.
     good = next(c for c in collected if c["id"] == "d979110c")
     nudged = {**good["cur"], "coord_footprint": good["cur"]["coord_footprint"] + 500}
diff --git a/tests/closures.json b/tests/closures.json
index 7e882192e..c623dd636 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -155,6 +155,7 @@
    "tools/audit/archscore/planted/redteam/45_shape_private_copy.py",
    "tools/audit/archscore/planted/redteam/46_card_rule_respelled.py",
    "tools/audit/archscore/planted/redteam/47_card_template_respelled.py",
+   "tools/audit/archscore/planted/redteam/48_footprint_packed_unpack.py",
    "tools/audit/archscore/planted/redteam/rt_lib.py",
    "tools/audit/archscore/score.py",
    "tools/audit/archscore/vector.py",
diff --git a/tools/audit/archscore/ABOUT.md b/tools/audit/archscore/ABOUT.md
index 3d7678e24..b7094094a 100644
--- a/tools/audit/archscore/ABOUT.md
+++ b/tools/audit/archscore/ABOUT.md
@@ -64,6 +64,7 @@ reads IMPROVES. The attempt is `planted/redteam/<NN>_*.py` and its case id is `r
 | C22 a card function's own names are numbered by first use and its no-op and empty statements dropped (`metrics/card.py`) | the card's copied functions given renamed locals (44); windows split by `void <n>;` (44b, #2373 review) or by a lone `;` (44c, #2373 round-2 review) | 44, 44b, 44c |
 | C23 `shape_copies` (gate-only): a function's own names are numbered, numbers, strings and `mod.X` abstracted as the clone window does (`metrics/shapes.py`) | a below-window rule copied with every name changed (`a3_shape_copies_control`); a private helper copied into its importer (also refused by `duplication_copies`) | 45 |
 | C24 `card_rule_copies` (gate-only): a one-statement card rule -- a run of an `&&`/`||` chain testing one value, its values (a name with its member path) numbered and its strings kept -- spelled at a second site (`metrics/card.rule_copies`); a template literal's run of two or more `${..}` formatting one value (its root name, members as spelled) with the text between them is a rule the same way, and a markup template -- its own text opens or closes a tag -- is none | a rule spelled once more inline below the 20-token window: `== null` written out as `x === null \|\| x === undefined` (46); the #2401 review's three respelled card_shapes rules read card_clone_copies 108 -> 108; the Setup diagram's edge key `${e[0]}>${e[1]}` written out again instead of read from its binding (47) | 46, 47 |
+| C25 `coord_footprint` counts the statements a statement packs (`footprint._units`): a tuple target (`a, b, c = (f(x) for x in xs)`), a tuple value (`a, b = f(), g()`), a chain (`a = b = f()`), a bare tuple expression, several `with` items, several `import` names, a multi-target `del`; a tuple pair of plumbing (`a, b = x.p, x.q`) or a chain of aliases is plumbing, as the plain spelling is | packing plain statements into one AST statement to lower the footprint (the #3185 review, a2e21972: 6 of the 7 statements behind its movement were one packed generator unpack) | 48 |
 
 Attempt 09 deletes a working feature. No structural counter exists: only the behaviour suite sees it,
 and a score is only meaningful for a change whose suite stays green and whose check count does not
@@ -107,6 +108,16 @@ are byte-identical (`calibrate.py --measure-corpus --only-metric untyped_payload
 `ARCHSCORE_ABLATE=C14`, `C1b` or `C6b` reopens its own attempt (it reads IMPROVES) and leaves the other two closed.
 The cases need the pin to hold no instance, so `controls.py`'s `on` names the case an arm is applied on top of.
 
+### What R10-FLY-ARCHSCORE-STMT-PACKING moved (C25)
+
+`coord_footprint` charged a packed statement once, whatever it bound. C25 reads each as the plain statements it spells, so
+the untouched tree reads higher (the stored corpus re-measured with `calibrate.py --measure-corpus --only-metric footprint`)
+and a packed change reads as its plain one. No corpus verdict moved. One planted verdict did:
+`a1_G2_dedupe` (GOOD) reads IMPROVES, not NULL, because the replay block it removes holds `wind_speed, precipitation =
+self._current_weather()`, a packed unpack the old count read as one statement. Siblings enumerated: the shapes in the C25 row;
+`for a, b in x` and a lone destructuring `a, b = pair` are one operation on one value, and read by arity (`pair` is two),
+as the plain `a = pair[0]` would. `ARCHSCORE_ABLATE=C25` reopens attempt 48.
+
 ### What R10-STRUCTURE-BLIND moved (D7-s1-01, D7-s3-01)
 
 `tests/structure.py`'s dead-member census resolves a load's receiver (`ReceiverTypes`), so a member
diff --git a/tools/audit/archscore/calibration/corpus_vectors.json b/tools/audit/archscore/calibration/corpus_vectors.json
index 0a2f5c8f9..a1d24d9d3 100644
--- a/tools/audit/archscore/calibration/corpus_vectors.json
+++ b/tools/audit/archscore/calibration/corpus_vectors.json
@@ -4,7 +4,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2375,
+"coord_footprint": 2460,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -30,7 +30,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2557,
+"coord_footprint": 2632,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -56,7 +56,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 28,
-"coord_footprint": 2350,
+"coord_footprint": 2435,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -82,7 +82,7 @@
 "card_clone_copies": 78,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2564,
+"coord_footprint": 2640,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -108,7 +108,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2573,
+"coord_footprint": 2646,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -134,7 +134,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2557,
+"coord_footprint": 2632,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -160,7 +160,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2602,
+"coord_footprint": 2675,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -186,7 +186,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2573,
+"coord_footprint": 2646,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -212,7 +212,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2324,
+"coord_footprint": 2398,
 "coordinator_multiassigned_attrs": 117,
 "coordinator_private_reach": 46,
 "dead_members": 29,
@@ -238,7 +238,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2356,
+"coord_footprint": 2440,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 46,
 "dead_members": 26,
@@ -264,7 +264,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2355,
+"coord_footprint": 2440,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -292,7 +292,7 @@
 "card_clone_copies": 0,
 "card_dead_definitions": 0,
 "computed_attr_access": 0,
-"coord_footprint": 153,
+"coord_footprint": 156,
 "coordinator_multiassigned_attrs": 10,
 "coordinator_private_reach": 4,
 "dead_members": 34,
@@ -318,7 +318,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2355,
+"coord_footprint": 2440,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -344,7 +344,7 @@
 "card_clone_copies": 61,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2532,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -372,7 +372,7 @@
 "card_clone_copies": 30,
 "card_dead_definitions": 0,
 "computed_attr_access": 14,
-"coord_footprint": 2060,
+"coord_footprint": 2104,
 "coordinator_multiassigned_attrs": 103,
 "coordinator_private_reach": 6,
 "dead_members": 43,
@@ -398,7 +398,7 @@
 "card_clone_copies": 67,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2540,
+"coord_footprint": 2605,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -424,7 +424,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 28,
-"coord_footprint": 2350,
+"coord_footprint": 2435,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -452,7 +452,7 @@
 "card_clone_copies": 30,
 "card_dead_definitions": 0,
 "computed_attr_access": 14,
-"coord_footprint": 1922,
+"coord_footprint": 1962,
 "coordinator_multiassigned_attrs": 96,
 "coordinator_private_reach": 6,
 "dead_members": 42,
@@ -478,7 +478,7 @@
 "card_clone_copies": 86,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2362,
+"coord_footprint": 2446,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -506,7 +506,7 @@
 "card_clone_copies": 20,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 955,
+"coord_footprint": 967,
 "coordinator_multiassigned_attrs": 61,
 "coordinator_private_reach": 5,
 "dead_members": 118,
@@ -532,7 +532,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 21,
-"coord_footprint": 2573,
+"coord_footprint": 2645,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 35,
 "dead_members": 29,
@@ -558,7 +558,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 25,
-"coord_footprint": 2472,
+"coord_footprint": 2561,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 70,
 "dead_members": 25,
@@ -584,7 +584,7 @@
 "card_clone_copies": 87,
 "card_dead_definitions": 0,
 "computed_attr_access": 31,
-"coord_footprint": 2520,
+"coord_footprint": 2609,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 94,
 "dead_members": 13,
@@ -612,7 +612,7 @@
 "card_clone_copies": 0,
 "card_dead_definitions": 0,
 "computed_attr_access": 0,
-"coord_footprint": 195,
+"coord_footprint": 199,
 "coordinator_multiassigned_attrs": 13,
 "coordinator_private_reach": 7,
 "dead_members": 47,
@@ -638,7 +638,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 30,
-"coord_footprint": 2486,
+"coord_footprint": 2573,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 86,
 "dead_members": 14,
@@ -664,7 +664,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2573,
+"coord_footprint": 2646,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -690,7 +690,7 @@
 "card_clone_copies": 67,
 "card_dead_definitions": 0,
 "computed_attr_access": 21,
-"coord_footprint": 2550,
+"coord_footprint": 2615,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -716,7 +716,7 @@
 "card_clone_copies": 54,
 "card_dead_definitions": 1,
 "computed_attr_access": 16,
-"coord_footprint": 2451,
+"coord_footprint": 2514,
 "coordinator_multiassigned_attrs": 129,
 "coordinator_private_reach": 12,
 "dead_members": 45,
@@ -744,7 +744,7 @@
 "card_clone_copies": 19,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 1008,
+"coord_footprint": 1023,
 "coordinator_multiassigned_attrs": 63,
 "coordinator_private_reach": 5,
 "dead_members": 122,
@@ -770,7 +770,7 @@
 "card_clone_copies": 61,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2532,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -796,7 +796,7 @@
 "card_clone_copies": 61,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2532,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -822,7 +822,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2436,
+"coord_footprint": 2512,
 "coordinator_multiassigned_attrs": 127,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -850,7 +850,7 @@
 "card_clone_copies": 46,
 "card_dead_definitions": 0,
 "computed_attr_access": 16,
-"coord_footprint": 2188,
+"coord_footprint": 2240,
 "coordinator_multiassigned_attrs": 109,
 "coordinator_private_reach": 6,
 "dead_members": 41,
@@ -876,7 +876,7 @@
 "card_clone_copies": 87,
 "card_dead_definitions": 0,
 "computed_attr_access": 31,
-"coord_footprint": 2521,
+"coord_footprint": 2610,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 95,
 "dead_members": 13,
@@ -902,7 +902,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2580,
+"coord_footprint": 2653,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -928,7 +928,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2557,
+"coord_footprint": 2632,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -954,7 +954,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2557,
+"coord_footprint": 2632,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -980,7 +980,7 @@
 "card_clone_copies": 87,
 "card_dead_definitions": 0,
 "computed_attr_access": 31,
-"coord_footprint": 2512,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 96,
 "dead_members": 13,
@@ -1006,7 +1006,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2324,
+"coord_footprint": 2398,
 "coordinator_multiassigned_attrs": 117,
 "coordinator_private_reach": 46,
 "dead_members": 29,
@@ -1032,7 +1032,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2367,
+"coord_footprint": 2452,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -1058,7 +1058,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2584,
+"coord_footprint": 2657,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -1084,7 +1084,7 @@
 "card_clone_copies": 87,
 "card_dead_definitions": 0,
 "computed_attr_access": 31,
-"coord_footprint": 2517,
+"coord_footprint": 2606,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 94,
 "dead_members": 13,
@@ -1112,7 +1112,7 @@
 "card_clone_copies": 4,
 "card_dead_definitions": 0,
 "computed_attr_access": 3,
-"coord_footprint": 932,
+"coord_footprint": 950,
 "coordinator_multiassigned_attrs": 62,
 "coordinator_private_reach": 5,
 "dead_members": 128,
@@ -1138,7 +1138,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2602,
+"coord_footprint": 2675,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -1164,7 +1164,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2428,
+"coord_footprint": 2504,
 "coordinator_multiassigned_attrs": 127,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -1190,7 +1190,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2309,
+"coord_footprint": 2383,
 "coordinator_multiassigned_attrs": 117,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -1216,7 +1216,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 30,
-"coord_footprint": 2486,
+"coord_footprint": 2573,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 86,
 "dead_members": 13,
@@ -1242,7 +1242,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2356,
+"coord_footprint": 2440,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 46,
 "dead_members": 26,
@@ -1268,7 +1268,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2580,
+"coord_footprint": 2653,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -1294,7 +1294,7 @@
 "card_clone_copies": 86,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2363,
+"coord_footprint": 2447,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -1320,7 +1320,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2565,
+"coord_footprint": 2641,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -1348,7 +1348,7 @@
 "card_clone_copies": 0,
 "card_dead_definitions": 0,
 "computed_attr_access": 0,
-"coord_footprint": 304,
+"coord_footprint": 308,
 "coordinator_multiassigned_attrs": 22,
 "coordinator_private_reach": 7,
 "dead_members": 60,
@@ -1376,7 +1376,7 @@
 "card_clone_copies": 28,
 "card_dead_definitions": 0,
 "computed_attr_access": 16,
-"coord_footprint": 2186,
+"coord_footprint": 2238,
 "coordinator_multiassigned_attrs": 109,
 "coordinator_private_reach": 6,
 "dead_members": 42,
@@ -1402,7 +1402,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2557,
+"coord_footprint": 2632,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -1428,7 +1428,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 28,
-"coord_footprint": 2350,
+"coord_footprint": 2435,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -1454,7 +1454,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2355,
+"coord_footprint": 2440,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -1482,7 +1482,7 @@
 "card_clone_copies": 12,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 919,
+"coord_footprint": 930,
 "coordinator_multiassigned_attrs": 60,
 "coordinator_private_reach": 5,
 "dead_members": 118,
@@ -1510,7 +1510,7 @@
 "card_clone_copies": 28,
 "card_dead_definitions": 0,
 "computed_attr_access": 16,
-"coord_footprint": 2188,
+"coord_footprint": 2240,
 "coordinator_multiassigned_attrs": 109,
 "coordinator_private_reach": 6,
 "dead_members": 41,
@@ -1538,7 +1538,7 @@
 "card_clone_copies": 30,
 "card_dead_definitions": 0,
 "computed_attr_access": 13,
-"coord_footprint": 1526,
+"coord_footprint": 1559,
 "coordinator_multiassigned_attrs": 79,
 "coordinator_private_reach": 6,
 "dead_members": 41,
@@ -1564,7 +1564,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2557,
+"coord_footprint": 2632,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -1590,7 +1590,7 @@
 "card_clone_copies": 61,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2532,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -1616,7 +1616,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2309,
+"coord_footprint": 2383,
 "coordinator_multiassigned_attrs": 117,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -1642,7 +1642,7 @@
 "card_clone_copies": 76,
 "card_dead_definitions": 0,
 "computed_attr_access": 21,
-"coord_footprint": 2550,
+"coord_footprint": 2619,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 28,
 "dead_members": 30,
@@ -1670,7 +1670,7 @@
 "card_clone_copies": 30,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 1231,
+"coord_footprint": 1254,
 "coordinator_multiassigned_attrs": 67,
 "coordinator_private_reach": 6,
 "dead_members": 37,
@@ -1696,7 +1696,7 @@
 "card_clone_copies": 54,
 "card_dead_definitions": 1,
 "computed_attr_access": 16,
-"coord_footprint": 2463,
+"coord_footprint": 2526,
 "coordinator_multiassigned_attrs": 130,
 "coordinator_private_reach": 12,
 "dead_members": 45,
@@ -1722,7 +1722,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2584,
+"coord_footprint": 2657,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -1750,7 +1750,7 @@
 "card_clone_copies": 0,
 "card_dead_definitions": 0,
 "computed_attr_access": 0,
-"coord_footprint": 264,
+"coord_footprint": 268,
 "coordinator_multiassigned_attrs": 19,
 "coordinator_private_reach": 7,
 "dead_members": 60,
@@ -1776,7 +1776,7 @@
 "card_clone_copies": 78,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2539,
+"coord_footprint": 2615,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 35,
 "dead_members": 29,
@@ -1802,7 +1802,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 21,
-"coord_footprint": 2574,
+"coord_footprint": 2646,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 35,
 "dead_members": 29,
@@ -1830,7 +1830,7 @@
 "card_clone_copies": 19,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 1089,
+"coord_footprint": 1106,
 "coordinator_multiassigned_attrs": 63,
 "coordinator_private_reach": 6,
 "dead_members": 35,
@@ -1856,7 +1856,7 @@
 "card_clone_copies": 87,
 "card_dead_definitions": 0,
 "computed_attr_access": 31,
-"coord_footprint": 2518,
+"coord_footprint": 2607,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 94,
 "dead_members": 13,
@@ -1882,7 +1882,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 24,
-"coord_footprint": 2355,
+"coord_footprint": 2440,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 47,
 "dead_members": 26,
@@ -1910,7 +1910,7 @@
 "card_clone_copies": 21,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 1108,
+"coord_footprint": 1125,
 "coordinator_multiassigned_attrs": 63,
 "coordinator_private_reach": 6,
 "dead_members": 35,
@@ -1936,7 +1936,7 @@
 "card_clone_copies": 46,
 "card_dead_definitions": 0,
 "computed_attr_access": 16,
-"coord_footprint": 2188,
+"coord_footprint": 2240,
 "coordinator_multiassigned_attrs": 109,
 "coordinator_private_reach": 6,
 "dead_members": 41,
@@ -1962,7 +1962,7 @@
 "card_clone_copies": 61,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2532,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -1988,7 +1988,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2573,
+"coord_footprint": 2646,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -2014,7 +2014,7 @@
 "card_clone_copies": 61,
 "card_dead_definitions": 0,
 "computed_attr_access": 19,
-"coord_footprint": 2532,
+"coord_footprint": 2597,
 "coordinator_multiassigned_attrs": 135,
 "coordinator_private_reach": 21,
 "dead_members": 30,
@@ -2042,7 +2042,7 @@
 "card_clone_copies": 21,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 1104,
+"coord_footprint": 1121,
 "coordinator_multiassigned_attrs": 63,
 "coordinator_private_reach": 6,
 "dead_members": 35,
@@ -2068,7 +2068,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2598,
+"coord_footprint": 2671,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -2094,7 +2094,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 30,
-"coord_footprint": 2486,
+"coord_footprint": 2573,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 86,
 "dead_members": 13,
@@ -2120,7 +2120,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2598,
+"coord_footprint": 2671,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 34,
 "dead_members": 29,
@@ -2146,7 +2146,7 @@
 "card_clone_copies": 87,
 "card_dead_definitions": 0,
 "computed_attr_access": 31,
-"coord_footprint": 2521,
+"coord_footprint": 2610,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 94,
 "dead_members": 13,
@@ -2174,7 +2174,7 @@
 "card_clone_copies": 4,
 "card_dead_definitions": 0,
 "computed_attr_access": 2,
-"coord_footprint": 663,
+"coord_footprint": 669,
 "coordinator_multiassigned_attrs": 47,
 "coordinator_private_reach": 4,
 "dead_members": 188,
@@ -2200,7 +2200,7 @@
 "card_clone_copies": 79,
 "card_dead_definitions": 0,
 "computed_attr_access": 21,
-"coord_footprint": 2573,
+"coord_footprint": 2645,
 "coordinator_multiassigned_attrs": 137,
 "coordinator_private_reach": 35,
 "dead_members": 29,
@@ -2226,7 +2226,7 @@
 "card_clone_copies": 81,
 "card_dead_definitions": 0,
 "computed_attr_access": 22,
-"coord_footprint": 2309,
+"coord_footprint": 2383,
 "coordinator_multiassigned_attrs": 117,
 "coordinator_private_reach": 43,
 "dead_members": 29,
@@ -2254,7 +2254,7 @@
 "card_clone_copies": 30,
 "card_dead_definitions": 0,
 "computed_attr_access": 11,
-"coord_footprint": 1371,
+"coord_footprint": 1400,
 "coordinator_multiassigned_attrs": 73,
 "coordinator_private_reach": 6,
 "dead_members": 38,
@@ -2280,7 +2280,7 @@
 "card_clone_copies": 84,
 "card_dead_definitions": 0,
 "computed_attr_access": 30,
-"coord_footprint": 2486,
+"coord_footprint": 2573,
 "coordinator_multiassigned_attrs": 118,
 "coordinator_private_reach": 86,
 "dead_members": 13,
diff --git a/tools/audit/archscore/calibration/expected.json b/tools/audit/archscore/calibration/expected.json
index 03e7d0c00..64c0b1dd4 100644
--- a/tools/audit/archscore/calibration/expected.json
+++ b/tools/audit/archscore/calibration/expected.json
@@ -304,7 +304,7 @@
   "admissible": true,
   "label": "GOOD",
   "set": "planted",
-  "verdict": "NULL"
+  "verdict": "IMPROVES"
  },
  "a1_G3_move_cluster_with_state": {
   "admissible": true,
@@ -1349,5 +1349,11 @@
   "label": "GAME",
   "set": "redteam",
   "verdict": "WORSENS"
+ },
+ "rt_48_footprint_packed_unpack": {
+  "admissible": true,
+  "label": "GAME",
+  "set": "redteam",
+  "verdict": "NULL"
  }
 }
diff --git a/tools/audit/archscore/metrics/footprint.py b/tools/audit/archscore/metrics/footprint.py
index 2e8c850c1..baa1209a3 100644
--- a/tools/audit/archscore/metrics/footprint.py
+++ b/tools/audit/archscore/metrics/footprint.py
@@ -57,8 +57,53 @@ def _plumbing(s: ast.AST) -> bool:
     return False
 
 
+def _arity(t: ast.AST) -> int:
+    """Names a target binds: ``a, (b, c)`` is three, ``x.y`` and ``x[i]`` one each."""
+    if isinstance(t, (ast.Tuple, ast.List)):
+        return sum(_arity(e) for e in t.elts)
+    return _arity(t.value) if isinstance(t, ast.Starred) else 1
+
+
+def _pairs(s: ast.Assign) -> list[tuple[ast.AST, ast.AST]] | None:
+    """The ``(target, value)`` pairs of a tuple target bound to a tuple of the same length, else None."""
+    if len(s.targets) == 1 and isinstance(s.targets[0], (ast.Tuple, ast.List)) \
+            and isinstance(s.value, (ast.Tuple, ast.List)) and len(s.targets[0].elts) == len(s.value.elts) \
+            and not any(isinstance(e, ast.Starred) for e in s.targets[0].elts + s.value.elts):
+        return list(zip(s.targets[0].elts, s.value.elts))
+    return None
+
+
+def _units(s: ast.AST) -> int:
+    """The statements a statement packs (counter C25). One AST statement can hold several: a
+    tuple-unpack ``a, b, c = (f(x) for x in xs)``, a tuple on the right ``a, b = f(), g()``, a chain
+    ``a = b = f()``, a bare tuple ``f(), g()``, ``with p as a, q as b`` and ``import a, b``. Each reads
+    as the plain statements it spells, so packing them lowers no count. A single-target, single-value
+    statement is one."""
+    if isinstance(s, ast.Assign):
+        pairs = _pairs(s)
+        if pairs is not None:  # ``a, b = x.p, x.q`` is the two statements it spells, each judged alone
+            return sum(1 for t, v in pairs if not _plumbing(ast.Assign(targets=[t], value=v)))
+        if len(s.targets) > 1 and all(isinstance(t, ast.Name) for t in s.targets) \
+                and _plumbing(ast.Assign(targets=s.targets[:1], value=s.value)):
+            return 0  # ``a = b = x.y`` is two aliases
+        rhs = len(s.value.elts) if isinstance(s.value, (ast.Tuple, ast.List)) else 1
+        return max(1, sum(_arity(t) for t in s.targets), rhs)
+    if isinstance(s, ast.Expr) and isinstance(s.value, (ast.Tuple, ast.List)):
+        return sum(1 for e in s.value.elts if not _plumbing(ast.Expr(value=e)))
+    if isinstance(s, (ast.With, ast.AsyncWith)):
+        return len(s.items)
+    if isinstance(s, (ast.Import, ast.ImportFrom)):
+        return len(s.names)
+    if isinstance(s, ast.Delete):
+        return sum(_arity(t) for t in s.targets)
+    return 1
+
+
+PACKING_UNITS = True  # False: one per statement, for ``vector.ablated`` (counter C25 off)
+
+
 def logic_stmts(node: ast.AST) -> int:
-    return sum(1 for n in ast.walk(node) if isinstance(n, ast.stmt) and not _is_doc(n)
+    return sum(_units(n) if PACKING_UNITS else 1 for n in ast.walk(node) if isinstance(n, ast.stmt) and not _is_doc(n)
                and not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and not _plumbing(n))
 
diff --git a/tools/audit/archscore/planted/redteam/48_footprint_packed_unpack.py b/tools/audit/archscore/planted/redteam/48_footprint_packed_unpack.py
new file mode 100644
index 000000000..99e1b0460
--- /dev/null
+++ b/tools/audit/archscore/planted/redteam/48_footprint_packed_unpack.py
@@ -0,0 +1,44 @@
+"""Game coord_footprint by packing: runs of adjacent plain assignments in the coordinator class become
+one tuple-unpack of a generator, ``a, b, c = (x for x in (e1, e2, e3))``, which the footprint counted as
+one statement (the #3185 review, a2e21972: 6 of the 7 statements behind its score movement). Nothing is
+improved and the logic is the same; counter C25 reads a packed statement as the plain ones it spells."""
+import ast, sys
+from rt_lib import pkg, replace_nodes
+p = pkg(sys.argv[1]) / "coordinator.py"
+src = p.read_text()
+tree = ast.parse(src)
+cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
+
+
+def plain(s):
+    return (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
+            and isinstance(s.value, (ast.BinOp, ast.Compare, ast.IfExp, ast.BoolOp)))
+
+
+def names(e):
+    return {n.id for n in ast.walk(e) if isinstance(n, ast.Name)}
+
+
+edits = []
+for fn in ast.walk(cls):
+    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
+        continue
+    for body in [fn.body] + [b for n in ast.walk(fn) for b in (getattr(n, "body", None), getattr(n, "orelse", None)) if isinstance(b, list)]:
+        run = []
+        for s in body + [None]:
+            # a run extends while the statement reads no name an earlier statement of the run binds
+            if s is not None and plain(s) and not (names(s.value) & {r.targets[0].id for r in run}) \
+                    and s.targets[0].id not in {n for r in run for n in names(r.value)}:
+                run.append(s)
+                continue
+            if len(run) >= 2:
+                lhs = ", ".join(r.targets[0].id for r in run)
+                rhs = ", ".join(ast.get_source_segment(src, r.value) for r in run)
+                edits.append((run[0], f"{lhs} = (_v for _v in ({rhs}))"))
+                edits.extend((r, "") for r in run[1:])
+            run = [s] if s is not None and plain(s) else []
+edits = [e for i, e in enumerate(edits) if all(e[0] is not f[0] for f in edits[:i])]
+assert edits, "the coordinator has runs of plain assignments"
+replace_nodes(p, edits)
+ast.parse(p.read_text())
+print("packed", sum(1 for _, t in edits if t), "runs")
diff --git a/tools/audit/archscore/vector.py b/tools/audit/archscore/vector.py
index 8f91533a1..00c2a3ac4 100644
--- a/tools/audit/archscore/vector.py
+++ b/tools/audit/archscore/vector.py
@@ -155,6 +155,7 @@ def measure(root: Path, only: set[str] | None = None) -> dict:
         untyped_payload_keys.ANY_SPELLINGS = "C1b" not in off
         untyped_payload_keys.FOLLOW_ANNOTATED = "C14" not in off
         footprint.READ_KW_KEYS = "C11" not in off
+        footprint.PACKING_UNITS = "C25" not in off
         C.FOLLOW_RETURNS = "C15" not in off
         hub_solve_writes.EVENT_ROOTS = "C16" not in off
         hub_solve_writes.PASS_ON = "C16b" not in off

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
