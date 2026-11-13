# Review packet #3552
head: 67ebee9d59ab35e448773f8f5d95b9bb04c60ed9
base: 3b9749dac55a85c200005352c661198c982e5799

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=131873486156 neutral
arch-score / arch-score id=131873154484 in_progress
arm id=131870033770 skipped
budget-raise-gate / budget-raise-gate id=131873154147 success
cancel-superseded id=131870039478 queued
codeql / Analyze (actions) id=131873154414 success
codeql / Analyze (javascript-typescript) id=131873154355 queued
codeql / Analyze (python) id=131873154761 queued
governance / delivery-status id=131873154361 queued
governance / delivery-status-publish id=131873157181 skipped
governance / env-matrix id=131873154593 queued
governance / instrument-self-tests id=131873154396 queued
governance / policy-docs id=131873154435 queued
governance / record id=131873157560 skipped
governance / wave-script id=131873154411 queued
hassfest / hassfest id=131873154290 success
kernel-points id=131873156537 skipped
prelude id=131870039765 queued
refresh id=131870039907 queued
tests / briefs id=131873154489 queued
tests / closure-scope id=131873154422 in_progress
tests / mutation id=131873154353 queued
tests / nightly-status id=131873154496 queued
validate / validate-hacs id=131873154316 queued

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131873154396: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/archive/carries/carry-1412.json b/dev/archive/carries/carry-1412.json
index a260e39559..bb7d61a30d 100644
--- a/dev/archive/carries/carry-1412.json
+++ b/dev/archive/carries/carry-1412.json
@@ -17,7 +17,7 @@
     {
       "from": "the pull request that adds inventory(), the completeness ledger and the unpinned-site ratchet to tests/mutation_table.py (the enforcement half of #1412; the populator half is not landed by it)",
       "effect": "narrows",
-      "control": "Established by measurement with its null control. Enumerating all 3798 candidates over 64 production modules through `mutation_table.inventory()` and grouping by the ledger key `triage_key(s)` = `file:line KIND` yields 46 keys with two candidates each, and every one of the 46 is CLAMP_DROP -- a line carrying two `min`/`max` calls, whose two candidates share the same `old` (the whole line text) but differ in `new` (which call is replaced). The null control is the other five operators: the same census over GUARD_OFF (2012), RETURN_DEL (902), BOOLOP (315), CONST (133) and RAISE_DEL (4) yields zero keys with more than one candidate, so the collision is specific to CLAMP_DROP's per-call generation, not a general property of the key. The perturbation that would void the finding is keying on `(file, line, kind, new)` instead of `(file, line, kind)`: that census finds zero collisions, because the `new` text disambiguates the inner call from the outer call. The concrete instance is custom_components/heatpump_optimizer/optimizer.py:4671, `p_dhw_run = max(0.1, min(p_max * 0.8, p_max))`: two CLAMP_DROP candidates share the key and the same `old`, so a single disposition at that key covers both and cannot say the inner `min` is a dead clamp (equivalent) while the outer `max` is a real clamp -- which is exactly why that dead-clamp instance is not recorded under survivor_triage in this PR.",
+      "control": "Established by measurement with its null control. Enumerating all 3798 candidates over 64 production modules through `mutation_table.inventory()` and grouping by the ledger key `triage_key(s)` = `file:line KIND` yields 46 keys with two candidates each, and every one of the 46 is CLAMP_DROP -- a line carrying two `min`/`max` calls, whose two candidates share the same `old` (the whole line text) but differ in `new` (which call is replaced). The null control is the other five operators: the same census over GUARD_OFF (2012), RETURN_DEL (902), BOOLOP (315), CONST (133) and RAISE_DEL (4) yields zero keys with more than one candidate, so the collision is specific to CLAMP_DROP's per-call generation, not a general property of the key. The perturbation that would void the finding is keying on `(file, line, kind, new)` instead of `(file, line, kind)`: that census finds zero collisions, because the `new` text disambiguates the inner call from the outer call. The concrete instance, re-measured at the tree of the pull request that re-anchored this citation (the original line had left the module), is the statement `solar_fraction = min(future_solar_6_12h / max(typical_heat_loss * 6, 0.1), 1.0)` in custom_components/heatpump_optimizer/optimizer.py, found by that phrase and not by a line number: two CLAMP_DROP candidates share the key and the same `old`, so a single disposition at that key covers both and cannot say the inner `max` is a real clamp while the outer `min` is a dead one (or the reverse) -- which is exactly why a colliding instance is not recorded under survivor_triage by its line key alone.",
       "remeasure": "Do not trust this paragraph's count: it is measured at this PR's head, and a later stage is judged against its own merge base. Re-run `python3 -c \"import sys; sys.path.insert(0,'tests'); import mutation_table as m; from collections import Counter; c=Counter(m.triage_key(s) for s in m.inventory()); print(sorted((k,v) for k,v in c.items() if v>1))\"` from the repository root and read the printed keys: expect exactly the colliding CLAMP_DROP lines, and confirm the other five kinds contribute none. Then perturb: key the same census on `(file, line, kind, new)` and confirm the collisions disappear. A populator that records a disposition for a colliding line without accounting for both candidates silently marks a real clamp equivalent to a void one.",
       "brief": "The ledger key `file:line KIND` plus the `old` pin does not uniquely identify a candidate site where a line carries two `min`/`max` calls: 46 such lines exist, all CLAMP_DROP, each yielding two candidates with the same key and `old` but a different mutation. The populator that fills `killed_by` in tests/mutation_budgets.json must therefore key on the mutation target -- the text it replaces, or the source segment -- not on `file:line KIND` alone, before it writes a disposition for a colliding line; a disposition keyed only on the line covers both candidates and cannot express that one is void (a dead clamp) while the other is a real clamp. The instance that made this concrete is a dead inner clamp inside a real outer clamp on the same line, left unrecorded in this PR for exactly that reason."
     },
diff --git a/dev/programme/delivery/3552.md b/dev/programme/delivery/3552.md
new file mode 100644
index 0000000000..bc11fd6c58
--- /dev/null
+++ b/dev/programme/delivery/3552.md
@@ -0,0 +1 @@
+- [#3552](https://github.com/tvofi/heatpump_optimizer/pull/3552) — **open**, R10-HOTFIX-CARRY-1412-CONTROL: r10 hotfix carry 1412 control (R10-HOTFIX-CARRY-1412-CONTROL)
diff --git a/tools/policy/legacy_control_files.json b/tools/policy/legacy_control_files.json
index 33e2d476fb..54537062d8 100644
--- a/tools/policy/legacy_control_files.json
+++ b/tools/policy/legacy_control_files.json
@@ -4,7 +4,6 @@
     "carry-1336.json",
     "carry-1395.json",
     "carry-1398.json",
-    "carry-1412.json",
     "carry-1454.json",
     "carry-1459.json",
     "carry-1463.json",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
