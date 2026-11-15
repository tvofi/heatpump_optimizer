# Review packet #3627
head: 3ad61a1f6e09044cd47db34952a3ab681db1b1e5
base: 66865be375f4ee283ee556f53fcd76cc3dbf40e2

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132934153999 success
arch-score / arch-score id=132933999681 success
arm id=132933615286 skipped
budget-raise-gate / budget-raise-gate id=132933999672 failure
cancel-superseded id=132933615459 success
codeql id=132934001160 skipped
codeql / Analyze (actions) id=132933980777 success
codeql / Analyze (javascript-typescript) id=132933980769 success
codeql / Analyze (python) id=132933980758 success
gate id=132934588906 failure
governance id=132934000998 skipped
governance / env-matrix id=132933980790 success
governance / instrument-self-tests id=132933980731 in_progress
governance / policy-docs id=132933980713 success
governance / record id=132933982456 skipped
governance / wave-script id=132933980754 success
hassfest id=132934000851 skipped
hassfest / hassfest id=132933980634 success
kernel-points id=132934000782 skipped
pr-contract id=132934590514 skipped
prelude id=132933615379 success
refresh id=132933615155 success
sweep-self id=132934896719 skipped
tests id=132934001552 skipped
tests / arch-instrument id=132934231750 success
tests / briefs id=132933980866 success
tests / browser id=132934231633 success
tests / closure-scope id=132933980726 success
tests / closures id=132934231587 in_progress
tests / coverage id=132934231631 in_progress
tests / fast (3.14) id=132934231584 in_progress
tests / mutation id=132933980742 success
tests / mutation-autofix id=132934470343 skipped
tests / mutation-pins id=132934469647 skipped
tests / nightly-ha id=132934233607 skipped
tests / nightly-status id=132933980722 success
tests / replay id=132934233176 skipped
tests / typing id=132934231620 success
validate id=132934000804 skipped
validate / validate-hacs id=132933980760 success

## Refusals
red-unanswered: concluded red check `budget-raise-gate / budget-raise-gate` is not named in ## Red checks
introduced-red: unreadable: head governance / instrument-self-tests job 132933980731: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
required-wait: required context `gate` reads concluded failure at 3ad61a1f6e09044cd47db34952a3ab681db1b1e5 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item a185b9af: dismissed:the next record pull request re-derives that list from the tree.
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 1 script(s) run, 32 scoped out.
             no segment of this names a program this check knows
  ok         python3 tools/audit/machinery_ratchet.py --measure --head origin/main
             `tools/audit/machinery_ratchet.py` is in the tree at this head
  ok         python3 -I tools/audit/machinery_ratchet.py --check --base origin/main --head HEAD --pr 1
             `tools/audit/machinery_ratchet.py` is in the tree at this head
  unverified git grep -n -E 'major\
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n -i severity -- 'tools/**/*.py' | grep -i -E 'bar|skip|exempt'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head

FIGURES: 6 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/.claude/rules/ratchet-budgets.md b/.claude/rules/ratchet-budgets.md
index f8b475d8ed..71ca3105c5 100644
--- a/.claude/rules/ratchet-budgets.md
+++ b/.claude/rules/ratchet-budgets.md
@@ -14,19 +14,14 @@ paths:
 corpus: a policy file may shrink freely and never grow past its cap. Deliberately
 not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
 not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
-and deletion is what this corpus most needs. That asymmetry has a hole only
-visible when three caps are read together.
+and deletion is what this corpus most needs.
 
 **`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
 plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
 before a seat has read anything. Moving prose out of `CLAUDE.md` into a
-`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
-split that made `CLAUDE.md` an index the floor fell by more than half while
-`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
-than carrying either here, which `brief-citations.md` calls an error outright.
-The scoping is a real improvement — what would be dishonest is recording that
-drop as the ratchet, which hands the next pull request headroom nobody earned and
-prices a scoped rule at zero however far it grows.
+`paths:`-scoped rule therefore lowers it **without deleting a line**. Recording that drop as the ratchet
+hands the next pull request headroom nobody earned and prices a scoped rule at
+zero however far it grows.
 
 **`corpus_tokens` does not move when prose moves — while every capped file is a
 measured one.** It sums the policy files the globs match, so a split between two
@@ -40,9 +35,7 @@ that cannot be complete.
 **`roles` charges a seat for what it loads once it opens a file.** Each entry
 gives an `opens` list — one representative file per surface that role touches —
 and the cap is the floor plus every scoped rule whose globs match one of them.
-The floor is not the cost: at the same split every role paid more than the floor,
-and the record seat more than the whole floor cap that preceded it. A cap only
-the empty session meets is not measuring the thing it is named for. `opens` is a
+`opens` is a
 fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
 by re-measuring against fewer files.
 
@@ -62,9 +55,6 @@ the merged tree — is
 not needed for a collision inside the band, where neither branch edits the line.
 It stays the right move for one larger than the band.
 
-The ratchet is deferred, not disabled: a new brief-sized document is still
-refused, and that arm has to stay red for this to be a ratchet at all.
-
 **Re-record an aggregate down** when `--budgets` shows it more than `_band`
 below its cap, and on any reclassification — the case the next section names.
 
@@ -107,6 +97,16 @@ as a known defect is not a ratchet.
 production, and nonproduct lines per 1000 product lines. Each closes the
 other's hole (splitting production lowers the first, not the second; a pure
 move costs neither). Each cap takes its band as above; the window is frozen.
+
+**A target, not a record** (tvofi, 2026-11-13, card P2):
+`machinery_target_budgets.json` lowers `nonproduction_merges` by `step` every
+`every_merges` merges past its `anchor` (the rule: the program's THE TARGET;
+the enumerator: `--measure`, its target and merges past the anchor). It refuses a
+non-production pull request past it, never a production one or main's push. At
+a round start the orchestrator records the cap down to `--measure` and asks
+the owner for the round's anchor and step: a later anchor or a slower decline
+is a raise. **One in, one out:** a required check (the set
+`merge_train.py owed-reds` prints) enters only in the pull request retiring one.
 **The owner's exemption**: a change proving over 20% improvement in CI time,
 programme completion time, right-first-time or token usage appends its
 `exemptions` entry (number, measure, before, after, each one's command,
diff --git a/.cursor/rules/ratchet-budgets.mdc b/.cursor/rules/ratchet-budgets.mdc
index 92e0f77051..b9b2685906 100644
--- a/.cursor/rules/ratchet-budgets.mdc
+++ b/.cursor/rules/ratchet-budgets.mdc
@@ -9,19 +9,14 @@ alwaysApply: true
 corpus: a policy file may shrink freely and never grow past its cap. Deliberately
 not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
 not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
-and deletion is what this corpus most needs. That asymmetry has a hole only
-visible when three caps are read together.
+and deletion is what this corpus most needs.
 
 **`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
 plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
 before a seat has read anything. Moving prose out of `CLAUDE.md` into a
-`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
-split that made `CLAUDE.md` an index the floor fell by more than half while
-`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
-than carrying either here, which `brief-citations.md` calls an error outright.
-The scoping is a real improvement — what would be dishonest is recording that
-drop as the ratchet, which hands the next pull request headroom nobody earned and
-prices a scoped rule at zero however far it grows.
+`paths:`-scoped rule therefore lowers it **without deleting a line**. Recording that drop as the ratchet
+hands the next pull request headroom nobody earned and prices a scoped rule at
+zero however far it grows.
 
 **`corpus_tokens` does not move when prose moves — while every capped file is a
 measured one.** It sums the policy files the globs match, so a split between two
@@ -35,9 +30,7 @@ that cannot be complete.
 **`roles` charges a seat for what it loads once it opens a file.** Each entry
 gives an `opens` list — one representative file per surface that role touches —
 and the cap is the floor plus every scoped rule whose globs match one of them.
-The floor is not the cost: at the same split every role paid more than the floor,
-and the record seat more than the whole floor cap that preceded it. A cap only
-the empty session meets is not measuring the thing it is named for. `opens` is a
+`opens` is a
 fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
 by re-measuring against fewer files.
 
@@ -57,9 +50,6 @@ the merged tree — is
 not needed for a collision inside the band, where neither branch edits the line.
 It stays the right move for one larger than the band.
 
-The ratchet is deferred, not disabled: a new brief-sized document is still
-refused, and that arm has to stay red for this to be a ratchet at all.
-
 **Re-record an aggregate down** when `--budgets` shows it more than `_band`
 below its cap, and on any reclassification — the case the next section names.
 
@@ -102,6 +92,16 @@ as a known defect is not a ratchet.
 production, and nonproduct lines per 1000 product lines. Each closes the
 other's hole (splitting production lowers the first, not the second; a pure
 move costs neither). Each cap takes its band as above; the window is frozen.
+
+**A target, not a record** (tvofi, 2026-11-13, card P2):
+`machinery_target_budgets.json` lowers `nonproduction_merges` by `step` every
+`every_merges` merges past its `anchor` (the rule: the program's THE TARGET;
+the enumerator: `--measure`, its target and merges past the anchor). It refuses a
+non-production pull request past it, never a production one or main's push. At
+a round start the orchestrator records the cap down to `--measure` and asks
+the owner for the round's anchor and step: a later anchor or a slower decline
+is a raise. **One in, one out:** a required check (the set
+`merge_train.py owed-reds` prints) enters only in the pull request retiring one.
 **The owner's exemption**: a change proving over 20% improvement in CI time,
 programme completion time, right-first-time or token usage appends its
 `exemptions` entry (number, measure, before, after, each one's command,
diff --git a/dev/audit/README.md b/dev/audit/README.md
index 3a708b9930..0c0cce43a7 100644
--- a/dev/audit/README.md
+++ b/dev/audit/README.md
@@ -83,26 +83,18 @@ or fixes a red, meaning the required `gate` job's on main (`tools/ci/gate.py`)
 or a self-test red its own pull request introduces, never one inherited from
 main; the rest waits for an instrument window the owner opens. Each round-11
 machinery group names its ground; the merge seat checks it at admission. Of the owner's open-PR cap (`DEFAULT_CAPS` in
-`tools/plan/replan.py`), 10 slots (the owner's count, not a tree value) are reserved for
-`custom_components/` pull requests; a machinery PR never takes one, nor a
+`tools/plan/replan.py`), `PRODUCTION_SLOTS` are production's
+(`pr_cap.py dispatch-gate --machinery`); a machinery PR never takes one, nor a
 production one waits for a machinery slot. A proposal
-is accepted only when its friction blocks a production merge, else ruled LOG
-(`proposal-triage.md`, once per round at round end). Exempt from all three: a proposal proving over 20% on
+is accepted only when its friction blocks a production merge, else ruled LOG.
+Exempt from all three: a proposal proving over 20% on
 CI time, programme completion time, right-first-time rate or token usage,
 against a measured baseline and a null control
 (`dev/governance/rules/ratchet-budgets.md`).
 
 **Round 11's opening plan carries:**
 
-- An owner decision on moving the repository to an organization so the native
-  merge queue replaces the train (a merge-queue ruleset returns HTTP 422 on a
-  user-owned repository; round 10's D13 probe). Weigh plan, visibility, the
-  HACS redirect, App installations, deploy key, ruleset ids and owner-keyed
-  instruments; after a transfer re-probe queue latency, `merge_group` gate
-  names and CI minutes; adopt or decline, and close the held groups the queue
-  makes moot (R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY,
-  R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE, R10-FLOW-BODY-ONLY (a)).
-  Context: the Lean flow pre-study, section K9 (out of the tree).
+- The organization transfer is ruled out (tvofi, 2026-11-14; `dev/programme/HANDOVER.md`).
 - Intake's baseline: R10-PROTECTION-CENSUS's result,
   `dev/audit/rounds/round10/protection-census/`. On it, B1 (triage batch 245,
   P740) opens the round unless ordered into round 10: on an all-product diff
@@ -164,7 +156,10 @@ Before phase 1, the pickup; each later step is its owner's rule.
    `python3 -c "import sys,glob,json;sys.path[:0]=['tools/audit/seat'];from roster_lib import FINISHED_STAGES as F;r=max(glob.glob('dev/programme/rosters/wave-r*-groups.json'),key=lambda p:int(p.split('-r')[1].split('-')[0]));[print(g['group'],g['resume']['stage']) for g in json.load(open(r))['groups'] if g['resume']['stage'] not in F+('refused',)]"`
 2. Evaluation before the baseline: decision 0018, R11-PRE-OBJECTIVE-FUNCTION, `check_scopes.py`.
 3. Denominator, unreached remainder, added dimensions, D11, D13: R10-DIMENSIONS-FULL-COVERAGE part 2, carried on R11-INTAKE-R10-RESIDUE.
-4. Scope: an owner-filed or outside-filed item folds into the ongoing round
+4. Proposals: the prior round's proposals file and prototypes, in
+   `$HPO_STATE_DIR/r<N-1>/` (`orchestrator.md`, the instrument freeze), ruled by
+   its round-end batch in `dev/programme/triage/`; ACCEPTs are built before finders.
+5. Scope: an owner-filed or outside-filed item folds into the ongoing round
    unless its filer explicitly defers it; silence is not one. Record who, when
    and their words in the group's note (`roster_edit.py set-resume --field note`).
 
diff --git a/dev/governance/config/machinery_budgets.json b/dev/governance/config/machinery_budgets.json
index 531694e94a..d338a9cd28 100644
--- a/dev/governance/config/machinery_budgets.json
+++ b/dev/governance/config/machinery_budgets.json
@@ -1,8 +1,8 @@
 {
   "_comment": "One-sided caps on what main's merges are spent on, graded by tools/audit/machinery_ratchet.py over the newest window_merges first-parent merges (the counting rule is that program's docstring). Each cap is compared against cap + its _band; re-record a cap down when the measurement falls more than its band below it. Policy: dev/governance/rules/ratchet-budgets.md, the machinery section.",
-  "_recorded": "Measured by `python3 tools/audit/machinery_ratchet.py --measure --window 580 --bands 150` at c3a279e3252a8b57bb00b5a677318cd4fe20387f. window_merges is the owner's fourteen-day count, frozen: a change to it is a raise.",
+  "_recorded": "Caps measured by `python3 tools/audit/machinery_ratchet.py --measure --window 580 --bands 150` at c3a279e3252a8b57bb00b5a677318cd4fe20387f; nonproduction_merges re-recorded down by `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` at b3831ff64eca1936f0b618193ee86c3e337b51a9, more than its band below the cap (churn_per_kilo_product_lines stays: within its band). window_merges is the owner's fourteen-day count, frozen: a change to it is a raise.",
   "window_merges": 580,
-  "nonproduction_merges": 521,
+  "nonproduction_merges": 478,
   "nonproduction_merges_band": 5,
   "churn_per_kilo_product_lines": 14797,
   "churn_per_kilo_product_lines_band": 3636,
diff --git a/dev/governance/config/machinery_target_budgets.json b/dev/governance/config/machinery_target_budgets.json
new file mode 100644
index 0000000000..f28a78ec10
--- /dev/null
+++ b/dev/governance/config/machinery_target_budgets.json
@@ -0,0 +1,7 @@
+{
+  "_comment": "The declining target on machinery_budgets.json's nonproduction_merges (tvofi, 2026-11-13, card P2), graded by tools/audit/machinery_ratchet.py (THE TARGET in its docstring): the cap less `step` for every `every_merges` first-parent merges past `anchor`, binding a non-production candidate only. Policy: dev/governance/rules/ratchet-budgets.md, the machinery section.",
+  "_recorded": "Anchor: the commit nonproduction_merges was recorded at, by `python3 tools/audit/machinery_ratchet.py --measure --head origin/main`. every_merges is half the frozen window_merges (the owner's seven days of merges); step is 10% of the recorded cap, rounded half up (process convergence audit d5d7ff8187, section 6 row a2).",
+  "anchor": "b3831ff64eca1936f0b618193ee86c3e337b51a9",
+  "every_merges": 290,
+  "step": 48
+}
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index f18f72f2f4..8736d5c3d6 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -108,12 +108,18 @@ whenever you merge.
   `OUTSIDE ... owed=triage` line (`tools/audit/seat/outside_intake.py`) is
   triaged or designed, then wired into a roster group or refused
   (`outside_intake.py refuse`); `owed=answer` goes to `standing-dispatch.md`.
-- **A proposal waits for the round-end triage** (`proposal-triage.md`, once per
-  round; tvofi 2026-11-14): a process, tooling or instrument proposal from the
-  sweep, a seat's result or a verdict is consolidated, never routed before its
-  ruling. Where a mandate lets you act on a recommendation absent the owner,
-  that means adding it to the batch; an ACCEPT reaches the next round's roster
-  citing its ruling. An instrument fix stays local and in-round.
+- **The instrument freeze, every round** (card P11): you or a seat work
+  an instrument fault around locally by a prototype kept runnable in
+  `$HPO_STATE_DIR/r<N>/proto/<id>/`, each use a sweep-log line `WORKAROUND <id>
+  onset=<UTC> cost=<min>`. Its permanent fix, as every other proposal, is entry
+  `<id>` of the proposals file in `$HPO_STATE_DIR/r<N>/`, citing the prototype
+  and its measured effect, never built in-round: `proposal-triage.md`
+  rules them once at round end, duplicates merged, uses and cost summed; an
+  ACCEPT is built at the next round's start before its finders, the rest
+  refused with their numbers. A workaround never changes production code,
+  loosens a gate or budget, or skips a review. Exempt: a production defect, an
+  owner order, a red required check on main, an owner or outside item. A
+  recommendation taken under a mandate joins the batch.
 - **Establish the work is not already done or in flight.** One
   `list_pull_requests` over the open set, and the issue's comments.
 - **Give it the constraints that already exist**: findings carried into its
@@ -128,7 +134,7 @@ whenever you merge.
   shape); it binds them (`fixer.md` 17). A serial chain orders groups whose
   owning seams overlap, not groups that share a file.
 - **A round's scope freezes at its register**: a mid-round finding goes to the
-  next round's unless it is expedite or a size-S fly-in.
+  next round's unless expedite, a size-S fly-in, or an undeferred owner or outside item.
 - **An L or XL group with no approved design, pre-study or prototype is
   designed first** (decision 0014): dispatch `designer.md` when its last
   predecessor dispatches, `design-review.md` at the design's head, and its
diff --git a/dev/governance/roles/proposal-triage.md b/dev/governance/roles/proposal-triage.md
index 62eabf1f24..680f993f7b 100644
--- a/dev/governance/roles/proposal-triage.md
+++ b/dev/governance/roles/proposal-triage.md
@@ -19,10 +19,10 @@ ACCEPT. Blocking no production merge: LOG, bar the exemption in
 
 **Machinery.** A planned machinery group, or a non-production CI lane or
 seat, stays only on a measured gain of at least 10% on them. Repair of such
-code (outside `custom_components/`) with roster `severity` `low` or `normal`
-meets both (over 20% to add); `medium`, `high`, `major`, `critical`,
-root-cause countermeasure, closeout, owner directive skip them; unset is
-classified first, never assumed major.
+code (outside `custom_components/`) meets both (over 20% to add) at any
+roster `severity`; only a red required check on main or a blocked production
+pull request skips them (owner card P2), as do a root-cause
+countermeasure, closeout and an owner directive.
 
 **Verdicts:** ACCEPT names a destination (a next-round roster group and carry,
 or new group, brief); DEFER, what would change it or the owning group; REJECT,
diff --git a/dev/governance/rules/ratchet-budgets.md b/dev/governance/rules/ratchet-budgets.md
index f8b475d8ed..71ca3105c5 100644
--- a/dev/governance/rules/ratchet-budgets.md
+++ b/dev/governance/rules/ratchet-budgets.md
@@ -14,19 +14,14 @@ paths:
 corpus: a policy file may shrink freely and never grow past its cap. Deliberately
 not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
 not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
-and deletion is what this corpus most needs. That asymmetry has a hole only
-visible when three caps are read together.
+and deletion is what this corpus most needs.
 
 **`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
 plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
 before a seat has read anything. Moving prose out of `CLAUDE.md` into a
-`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
-split that made `CLAUDE.md` an index the floor fell by more than half while
-`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
-than carrying either here, which `brief-citations.md` calls an error outright.
-The scoping is a real improvement — what would be dishonest is recording that
-drop as the ratchet, which hands the next pull request headroom nobody earned and
-prices a scoped rule at zero however far it grows.
+`paths:`-scoped rule therefore lowers it **without deleting a line**. Recording that drop as the ratchet
+hands the next pull request headroom nobody earned and prices a scoped rule at
+zero however far it grows.
 
 **`corpus_tokens` does not move when prose moves — while every capped file is a
 measured one.** It sums the policy files the globs match, so a split between two
@@ -40,9 +35,7 @@ that cannot be complete.
 **`roles` charges a seat for what it loads once it opens a file.** Each entry
 gives an `opens` list — one representative file per surface that role touches —
 and the cap is the floor plus every scoped rule whose globs match one of them.
-The floor is not the cost: at the same split every role paid more than the floor,
-and the record seat more than the whole floor cap that preceded it. A cap only
-the empty session meets is not measuring the thing it is named for. `opens` is a
+`opens` is a
 fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
 by re-measuring against fewer files.
 
@@ -62,9 +55,6 @@ the merged tree — is
 not needed for a collision inside the band, where neither branch edits the line.
 It stays the right move for one larger than the band.
 
-The ratchet is deferred, not disabled: a new brief-sized document is still
-refused, and that arm has to stay red for this to be a ratchet at all.
-
 **Re-record an aggregate down** when `--budgets` shows it more than `_band`
 below its cap, and on any reclassification — the case the next section names.
 
@@ -107,6 +97,16 @@ as a known defect is not a ratchet.
 production, and nonproduct lines per 1000 product lines. Each closes the
 other's hole (splitting production lowers the first, not the second; a pure
 move costs neither). Each cap takes its band as above; the window is frozen.
+
+**A target, not a record** (tvofi, 2026-11-13, card P2):
+`machinery_target_budgets.json` lowers `nonproduction_merges` by `step` every
+`every_merges` merges past its `anchor` (the rule: the program's THE TARGET;
+the enumerator: `--measure`, its target and merges past the anchor). It refuses a
+non-production pull request past it, never a production one or main's push. At
+a round start the orchestrator records the cap down to `--measure` and asks
+the owner for the round's anchor and step: a later anchor or a slower decline
+is a raise. **One in, one out:** a required check (the set
+`merge_train.py owed-reds` prints) enters only in the pull request retiring one.
 **The owner's exemption**: a change proving over 20% improvement in CI time,
 programme completion time, right-first-time or token usage appends its
 `exemptions` entry (number, measure, before, after, each one's command,
diff --git a/dev/programme/delivery/3627.md b/dev/programme/delivery/3627.md
new file mode 100644
index 0000000000..fbf3df267c
--- /dev/null
+++ b/dev/programme/delivery/3627.md
@@ -0,0 +1 @@
+- [#3627](https://github.com/tvofi/heatpump_optimizer/pull/3627) — **open**, R11-PRE-MACHINERY-LIMITER: r11 pre machinery limiter (R11-PRE-MACHINERY-LIMITER)
diff --git a/tools/audit/machinery_ratchet.py b/tools/audit/machinery_ratchet.py
index acc96a6143..06dab21ce6 100644
--- a/tools/audit/machinery_ratchet.py
+++ b/tools/audit/machinery_ratchet.py
@@ -47,8 +47,21 @@ in the budgets file's `exemptions` list exempts merge M only when all hold:
     are read from M's tree too.
 An exempted merge leaves the window and the next older merge fills its slot.
 
-Exit 0: inside both caps. 1: a cap exceeded. 2: usage, an unreadable budgets
-file, or a history shorter than the window.
+THE TARGET (tvofi, 2026-11-13, card P2: a target that declines over a round,
+not a record of the status quo). `dev/governance/config/
+machinery_target_budgets.json` holds `anchor` (the commit the cap was recorded
+at), `every_merges` and `step`. With n the first-parent merges after the anchor
+up to the base (PR mode) or the head (push mode), the target is
+  nonproduction_merges - step * floor(n / every_merges), never below 0,
+compared against target plus nonproduction_merges' band, again by merge count,
+never hours. It refuses only a candidate that is not production and not
+exempted: a production candidate cannot raise the metric, and in push mode the
+target is a report line, so the schedule passing the window turns no check on
+main red. The caps above stay the ceiling in both modes. No file, no target.
+
+Exit 0: inside both caps. 1: a cap, or the target on its candidate, exceeded.
+2: usage, an unreadable budgets or target file, or a history shorter than the
+window.
 """
 from __future__ import annotations
 
@@ -63,6 +76,8 @@ from fractions import Fraction
 from pathlib import Path
 
 BUDGETS = "dev/governance/config/machinery_budgets.json"
+TARGET_BUDGETS = "dev/governance/config/machinery_target_budgets.json"
+TARGET_KEYS = ("every_merges", "step")
 PRODUCT_PREFIXES = ("custom_components/", "blueprints/")
 RECORD_PREFIXES = ("dev/programme/",)
 RECORD_FILES = ("RELEASE_NOTES.md", "VERSION")
@@ -308,6 +323,42 @@ def load_budgets(text: str) -> dict:
     return doc
 
 
+def load_target(repo: str, rev: str) -> dict | None:
+    """The target file at `rev`, None when it is absent, refused when it is
+    malformed or its anchor is not an ancestor of `rev`: an unreadable target
+    is never no target."""
+    r = _git(repo, "show", f"{rev}:{TARGET_BUDGETS}", check=False)
+    if r.returncode != 0:
+        return None
+    try:
+        doc = json.loads(r.stdout)
+    except ValueError as e:
+        raise Refusal(f"{TARGET_BUDGETS} does not parse ({e})")
+    if not isinstance(doc, dict):
+        raise Refusal(f"{TARGET_BUDGETS} is not an object")
+    extra = sorted(k for k in doc if not k.startswith("_") and k not in ("anchor", *TARGET_KEYS))
+    if extra:
+        raise Refusal(f"{TARGET_BUDGETS}: {extra} is not a key this ratchet reads")
+    for k in TARGET_KEYS:
+        v = doc.get(k)
+        if isinstance(v, bool) or not isinstance(v, int) or v < (1 if k == "every_merges" else 0):
+            raise Refusal(f"{TARGET_BUDGETS}: {k} is {v!r}")
+    a = doc.get("anchor")
+    if not isinstance(a, str) or not re.fullmatch(r"[0-9a-f]{40}", a):
+        raise Refusal(f"{TARGET_BUDGETS}: anchor is {a!r}, not a full commit sha")
+    return doc
+
+
+def scheduled_target(repo: str, tip: str, cap: int, tdoc: dict) -> tuple[int, int]:
+    """(the target, n merges past the anchor) at `tip`."""
+    a = tdoc["anchor"]
+    if _git(repo, "merge-base", "--is-ancestor", a, tip, check=False).returncode != 0:
+        raise Refusal(f"{TARGET_BUDGETS}: anchor {a[:12]} is not an ancestor of {tip}")
+    n = sum(1 for line in _git(repo, "rev-list", "--first-parent", "--parents", f"{a}..{tip}")
+            .stdout.splitlines() if len(line.split()) == 3)
+    return max(0, cap - tdoc["step"] * (n // tdoc["every_merges"])), n
+
+
 def measure(repo: str, head: str, budgets_doc: dict, base: str | None = None,
             pr: int | None = None, grader: Grader | None = None) -> tuple[dict, list, list]:
     """The window's metrics: push mode without `base`, PR mode with it."""
@@ -369,6 +420,18 @@ def check(repo: str, head: str, base: str | None, pr: int | None, out=print) ->
     for c in CAPS:
         cap, band = doc[c], doc[c + BAND_SUFFIX]
         out(f"  {'FAIL' if c in bad else 'ok  '} {c} {m[c]} <= {cap} + band {band}")
+    tdoc = load_target(repo, head)
+    if tdoc is not None:
+        c = CAPS[0]
+        t, n = scheduled_target(repo, base or head, doc[c], tdoc)
+        cand = rows[0] if base and rows and rows[0]["sha"] == head else None
+        binds = cand is not None and cand["kind"] != "production"
+        past = m[c] > t + doc[c + BAND_SUFFIX]
+        word = ("FAIL" if past else "ok  ") if binds else "info"
+        out(f"  {word} target {c} {m[c]} <= {t} + band {doc[c + BAND_SUFFIX]} ({n} merge(s) "
+            f"past anchor {tdoc['anchor'][:12]}, {tdoc['step']} down per {tdoc['every_merges']})")
+        if binds and past:
+            bad.append("target")
     if bad:
         out("machinery_ratchet: refused; pay by landing production work, record an exemption "
             "the change earns (ratchet-budgets.md), or ask the owner for a raise")
@@ -679,6 +742,53 @@ def self_test() -> int:
                 got = "refused"
             ok(f"load_budgets refuses {label}", got, "refused")
 
+        # 6. The target: a schedule over merges past its anchor, binding only a
+        # non-production, unexempted candidate. Window 3, cap 2, band 0; the
+        # target falls by 2 every 2 merges past the anchor.
+        r = fresh("target")
+        r.merge(1, PRODM); r.merge(2, MACH); r.merge(3, PRODM); r.merge(4, MACH)
+        anchor = r.tip
+        tgt = lambda **k: [("set", TARGET_BUDGETS, json.dumps(
+            {"_comment": "fixture", "anchor": anchor, "every_merges": 2, "step": 2, **k}))]
+        r.merge(5, PRODM + budgets_ops(caps(m1=2, w=3)) + tgt())
+        # 1 merge past the anchor: the target is still 2. Each candidate is
+        # cut from the base's own tree, so no earlier candidate's lines leak in.
+        at = {"files": dict(r.files)}
+
+        def cand(ops: list, drop: tuple = ()) -> tuple[int, str]:
+            r.files = {k: v for k, v in at["files"].items() if k not in drop}
+            return run_cli(r, "--check", "--base", r.tip, "--head", r.side(ops), "--pr", "9")
+        rc, txt = cand(MACH)
+        ok("target: 1 merge past the anchor is still 2, so a machinery candidate at 2 passes",
+           (rc, "ok   target nonproduction_merges 2 <= 2 + band 0 (1 merge(s) past" in txt), (0, True))
+        r.merge(6, RECM)                              # 2 merges past: target 0
+        at["files"] = dict(r.files)
+        rc, txt = cand(MACH)
+        ok("target: 2 merges past it falls to 0 and refuses the machinery candidate under its cap",
+           (rc, "FAIL target nonproduction_merges 2 <= 0" in txt, "ok   nonproduction_merges 2 <= 2" in txt),
+           (1, True, True))
+        ok("target: a record candidate is not production and is refused too", cand(RECM)[0], 1)
+        rc, txt = cand(PRODM)
+        ok("target: a production candidate is never refused by it (a report line)",
+           (rc, "info target" in txt), (0, True))
+        ok("target: an exempted machinery candidate passes",
+           cand(MACH + budgets_ops(caps(m1=2, w=3, ex=[entry(9)])) + [("set", "ev/proof.txt", "m\n")])[0], 0)
+        rc, txt = run_cli(r, "--check", "--head", r.tip)
+        ok("target: push mode reports it and stays green under the cap", (rc, "info target" in txt), (0, True))
+        ok("target: --measure prints it beside the metrics",
+           {k: json.loads(run_cli(r, "--measure", "--head", r.tip)[1])[k]
+            for k in ("target", "merges_past_anchor")}, {"target": 0, "merges_past_anchor": 2})
+        ok("target: no file, no target: the refused candidate passes (null control)",
+           cand(MACH, drop=(TARGET_BUDGETS,))[0], 0)
+        for label, ops in (("an unread key", tgt(open_groups=1)), ("a zero every_merges", tgt(every_merges=0)),
+                           ("a short anchor", tgt(anchor=anchor[:12])),
+                           ("an anchor off the history", tgt(anchor="0" * 40))):
+            ok(f"target: {label} is refused, never read as no target", cand(MACH + ops)[0], 2)
+        ok("target: a file that is not an object is refused",
+           cand(MACH + [("set", TARGET_BUDGETS, "[]")])[0], 2)
+        ok("target: every_merges 1 and step 0 are the bounds it reads (null control)",
+           [cand(MACH + tgt(every_merges=1, step=s_))[0] for s_ in (0, 2)], [0, 1])
+
     ok("--check-event: a base and a PR number select PR mode",
        event_args({"MACHINERY_BASE": "b", "MACHINERY_HEAD": "h", "MACHINERY_PR": "7"}), ("h", "b", 7))
     ok("--check-event: a base with no PR number is push mode at the head",
@@ -717,6 +827,10 @@ def main(argv: list[str]) -> int:
             doc = ({WINDOW_KEY: a.window} if a.window
                    else load_budgets(_budgets_text(a.repo, a.head, BUDGETS)))
             m, _, skipped = measure(a.repo, a.head, doc, a.base, pr)
+            tdoc = None if a.window else load_target(a.repo, a.head)
+            if tdoc is not None:
+                m["target"], m["merges_past_anchor"] = scheduled_target(
+                    a.repo, a.base or a.head, doc[CAPS[0]], tdoc)
             print(json.dumps({"head": _git(a.repo, "rev-parse", a.head).stdout.strip(), **m,
                               "exempted": [s["sha"] for s in skipped]}, sort_keys=True))
             if a.bands:
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index 581d0bc5b0..16f08226d0 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -619,7 +619,8 @@ class Tick:
         HPO_WIP_CAP -- at the cap a new group is not dispatched, while opening
         and merging are always allowed; and the counted PRs whose three-dot
         diff touches the coordinator, against its cap of 2. A diff one_pr
-        could not read leaves the second count a floor: flagged. A roster or a
+        could not read leaves the second count a floor: flagged. Then the open
+        PRs by class against the machinery slots (`pr_cap.class_line`). A roster or a
         cap it cannot read is UNREADABLE, never a clean zero."""
         cap_mod = _module("pr_cap_tick", "tools/audit/seat/pr_cap.py")
         if cap_mod is None:
@@ -643,6 +644,11 @@ class Tick:
         if unread:
             text += f"; diff UNREADABLE at {', '.join('#' + str(x) for x in unread)}, so at least {k}"
         self.line(S, text, flag=k > kcap or bool(unread))
+        rule, slots = cap_mod.product_rule(), cap_mod.open_slots()
+        if rule is None or slots is None:
+            self.unreadable(S, "PR classes", "machinery_ratchet.is_product or replan.DEFAULT_CAPS")
+        else:
+            self.line(S, *cap_mod.class_line(cap_mod.by_class(counted, files, rule), slots))
 
     def _verdict_authors(self, pw) -> "tuple[set, int] | None":
         """The approver App's identity off app_approve.sh, through
@@ -4862,6 +4868,14 @@ def self_test() -> int:
             ("a diff it cannot read flags the coordinator count as a floor",
              one(unread, "coordinator.py PRs: ")["flag"] is True
              and "UNREADABLE at #2, so at least 0" in one(unread, "coordinator.py PRs: ")["text"]),
+            ("open PRs by class: the three touching a product path are production",
+             one(at, "open PRs by class: ") == {"flag": False, "text": "open PRs by class: 3 production, "
+                                                "3 machinery; machinery slots 3/10 (10 of 20 reserved for production)"}),
+            ("an unread diff is its own class, counted against the machinery slots",
+             one(unread, "open PRs by class: ")["text"].startswith(
+                 "open PRs by class: 0 production, 1 machinery, 1 unread; machinery slots 2/10")),
+            ("twenty machinery PRs fill the machinery slots: flagged (null: six above are not)",
+             one(board, "open PRs by class: ")["flag"] is True),
             ("an invalid HPO_WIP_CAP is UNREADABLE, never a count",
              any(l["flag"] and "UNREADABLE: WIP cap" in l["text"] for l in badcap)
              and not any(l["text"].startswith("WIP: ") for l in badcap)),
diff --git a/tools/audit/seat/pr_cap.py b/tools/audit/seat/pr_cap.py
index 72acbac659..3e81b5419a 100644
--- a/tools/audit/seat/pr_cap.py
+++ b/tools/audit/seat/pr_cap.py
@@ -4,7 +4,7 @@
     python3 -I tools/audit/seat/pr_cap.py info --repo OWNER/REPO
     python3 -I tools/audit/seat/pr_cap.py dispatch-gate [--repo PATH]
         [--roster-file PATH | --roster-ref GITREF [--roster-path PATH]]
-        [--over-cap REASON]
+        [--over-cap REASON] [--machinery OWNER/REPO]
     python3 -I tools/audit/seat/pr_cap.py --self-test
 
 THE RULING (tvofi, 2026-10-20, moving 2026-10-18's open-PR cap; restated
@@ -25,6 +25,15 @@ by it. Opening is how work LEAVES work-in-progress, not how it enters. So:
     `wip_groups`, M from `counted`, flagged at or over the cap. It does not
     dispatch and does not gate; it reports.
 
+THE PRODUCTION SLOTS (tvofi, 2026-11-01; `dev/audit/README.md`, "Production
+share"). Of the owner's open-pull-request slots (`DEFAULT_CAPS` in
+`tools/plan/replan.py`), PRODUCTION_SLOTS are reserved for production: a pull
+request whose diff touches a product path (`machinery_ratchet.is_product`, the
+one predicate) is production, any other machinery. `dispatch-gate --machinery
+OWNER/REPO` refuses a machinery group once machinery and unread pull requests
+fill the rest; a production group never waits for a machinery slot.
+`orchestrator_tick.py` prints `class_line` every pass.
+
 WHAT "BOT" MEANS HERE, a design choice. Every pull request this repository's
 seats open is authored by the hpo-author App (decision 0011), which GitHub
 reports as a bot. Excluding every bot would count nothing, so a bot is an author
@@ -37,6 +46,8 @@ Lines (one per call, on stderr; exit 0 to pass, 1 to refuse, 2 for usage):
       or --over-cap <reason>
   dispatch: OVER-CAP: WIP 6/6, overridden: <reason> (G1, ...)
   open_pr: 20 open PRs; the cap gates dispatch, not opening
+  dispatch: REFUSE: machinery slots: 10/10 (#1, ...); production holds the
+      other 10
 """
 from __future__ import annotations
 
@@ -58,6 +69,9 @@ COORDINATOR_PATH = "custom_components/heatpump_optimizer/coordinator.py"
 COORDINATOR_CAP = 2
 FIELDS = "number,title,author"
 SELF = os.path.abspath(__file__)
+ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SELF))))
+PRODUCTION_SLOTS = 10  # the owner's count, 2026-11-01
+GH_FILES_LIMIT = 100  # gh lists at most this many files per pull request
 _RL = None
 
 
@@ -189,6 +203,94 @@ def coordinator_prs(files_by_pr: dict) -> "tuple[list, list]":
     return hit, unread
 
 
+def _load(name: str, rel: str):
+    """A module of the tree by path, None when this copy has no tree beside it
+    (pr_args.sh copies this file alone into a seat directory)."""
+    p = os.path.join(ROOT, rel)
+    if not os.path.isfile(p):
+        return None
+    spec = importlib.util.spec_from_file_location(name, p)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def product_rule():
+    """machinery_ratchet.is_product, or None when unreadable."""
+    m = _load("machinery_ratchet_pr_cap", "tools/audit/machinery_ratchet.py")
+    return getattr(m, "is_product", None)
+
+
+def open_slots() -> "int | None":
+    """replan.py's DEFAULT_CAPS slots, or None when unreadable."""
+    m = _load("replan_pr_cap", "tools/plan/replan.py")
+    v = (getattr(m, "DEFAULT_CAPS", None) or {}).get("slots")
+    return v if isinstance(v, int) and v > PRODUCTION_SLOTS else None
+
+
+def by_class(prs: list, files_by_pr: dict, is_product) -> dict:
+    """{production, machinery, unread: [PR numbers]}: a diff it cannot read is
+    neither, never machinery by default nor production."""
+    out = {"production": [], "machinery": [], "unread": []}
+    for pr in prs:
+        fs = files_by_pr.get(pr["number"])
+        k = "unread" if fs is None else (  # mut:classunread
+            "production" if any(is_product(f) for f in fs) else "machinery")
+        out[k].append(pr["number"])
+    return out
+
+
+def class_line(classes: dict, slots: int) -> "tuple[str, bool]":
+    """(the tick's line, flagged): flagged once machinery and unread fill the
+    slots production does not hold."""
+    free = slots - PRODUCTION_SLOTS
+    m, u = len(classes["machinery"]), len(classes["unread"])
+    text = (f"open PRs by class: {len(classes['production'])} production, {m} machinery"
+            + (f", {u} unread" if u else "")
+            + f"; machinery slots {m + u}/{free} ({PRODUCTION_SLOTS} of {slots} reserved for production)")
+    return text, m + u >= free  # mut:classflag
+
+
+def machinery_gate(classes: "dict | None", why: str, slots: "int | None") -> "tuple[int, str]":
+    """(exit status, line) for dispatching a machinery group: refused once
+    machinery and unread pull requests fill the slots production does not hold."""
+    if classes is None or slots is None: return 1, f"dispatch: REFUSE: machinery slots: unread ({why}); no pass"  # mut:mslotunread
+    free = slots - PRODUCTION_SLOTS
+    taken = classes["machinery"] + classes["unread"]
+    ids = ", ".join(f"#{n}" for n in taken)
+    if len(taken) < free:
+        return 0, f"dispatch: machinery slots {len(taken)}/{free}: may dispatch a machinery group"
+    return 1, (f"dispatch: REFUSE: machinery slots: {len(taken)}/{free} ({ids}); "  # mut:mslot
+               f"production holds the other {PRODUCTION_SLOTS}")
+
+
+def read_classes(repo: str, gh=None, rule=None) -> "tuple[dict | None, str]":
+    """(by_class over the open pull requests read with their files, '') or
+    (None, why): a list or a file list gh may have truncated is unread."""
+    rule = rule or product_rule()
+    if rule is None:
+        return None, "machinery_ratchet.is_product is not beside this copy"
+    argv = ["pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
+            "--json", FIELDS + ",files"]
+    if gh is not None:
+        rc, out = gh(argv)
+    else:
+        r = subprocess.run(["gh", *argv], capture_output=True, text=True)
+        rc, out = r.returncode, r.stdout + r.stderr
+    if rc != 0:
+        return None, f"gh exited {rc}: {out.strip()[-160:]}"
+    try:
+        prs = json.loads(out)
+    except ValueError as e:
+        return None, f"not JSON: {e}"
+    if not isinstance(prs, list) or len(prs) >= 200:
+        return None, "not a list, or 200 or more returned"
+    prs = counted(prs)
+    files = {p["number"]: (None if len(p.get("files") or []) >= GH_FILES_LIMIT
+                           else [f.get("path", "") for f in p.get("files") or []]) for p in prs}
+    return by_class(prs, files, rule), ""
+
+
 def _doc_stage() -> dict:
     """The first named group of stages, for the self-test's rosters."""
     return {"groups": [{"group": f"G{i}", "resume": {"stage": s}}
@@ -310,6 +412,31 @@ def self_test() -> int:
     hit, unread = coordinator_prs({1: [COORDINATOR_PATH], 2: ["x.py"], 3: None})
     ck("coordinator PRs: the diff that touches it counts, an unread diff is named apart",
        hit == [1] and unread == [3])
+    # ---- the production slots -------------------------------------------
+    prod = lambda f: f.startswith("custom_components/")
+    board = [{"number": i, "title": "t", "author": app} for i in range(1, 5)]
+    cls = by_class(board, {1: ["custom_components/a.py", "tools/x.py"], 2: ["tools/x.py"],
+                           3: [], 4: None}, prod)
+    ck("by class: a product path makes production, none machinery, an unread diff neither",
+       cls == {"production": [1], "machinery": [2, 3], "unread": [4]})
+    text, flag = class_line(cls, 13)
+    ck("the tick line names each class and the machinery slots, unread counted against them",
+       text == "open PRs by class: 1 production, 2 machinery, 1 unread; machinery slots 3/3 "
+       "(10 of 13 reserved for production)" and flag)
+    ck("null control: below the machinery slots the line is not flagged",
+       class_line(cls, 14)[1] is False)
+    rc, line = machinery_gate(cls, "", 13)
+    ck("a machinery group is refused once machinery and unread fill the free slots",
+       rc == 1 and line == "dispatch: REFUSE: machinery slots: 3/3 (#2, #3, #4); production holds the other 10")
+    ck("null control: one free machinery slot passes", machinery_gate(cls, "", 14)[0] == 0)
+    ck("unread classes or slots refuse, never a clean zero",
+       machinery_gate(None, "gh exited 1", 20)[0] == 1 and machinery_gate(cls, "", None)[0] == 1)
+    many = [{"path": f"tools/{i}"} for i in range(GH_FILES_LIMIT)]
+    got, _ = read_classes("o/r", gh=lambda a: (0, json.dumps(
+        [{"number": 7, "title": "t", "author": app, "files": many},
+         {"number": 8, "title": "t", "author": app, "files": many[:1]}])), rule=prod)
+    ck("a file list at gh's limit may be truncated: unread, not machinery",
+       got == {"production": [], "machinery": [8], "unread": [7]})
     print(f"pr_cap self-test: {total} checks, {failed} failed")
     return 1 if failed else 0
 
@@ -342,6 +469,10 @@ def main(argv: list) -> int:
         rc, line = dispatch_gate(roster, where, wip_cap_from_env(),
                                  _opt(argv, "--over-cap"))
         print(line, file=sys.stderr)
+        slug = _opt(argv, "--machinery")
+        if rc == 0 and slug is not None:
+            rc, line = machinery_gate(*read_classes(slug), open_slots())
+            print(line, file=sys.stderr)
         return rc
     print(__doc__.split("\n\n")[1], file=sys.stderr)
     return 2
diff --git a/tools/policy/budget_raise_gate.py b/tools/policy/budget_raise_gate.py
index c871a99934..0f55399349 100644
--- a/tools/policy/budget_raise_gate.py
+++ b/tools/policy/budget_raise_gate.py
@@ -253,6 +253,14 @@ SCHEMA: dict[str, list[tuple[tuple[str, ...], str]]] = {
         (("churn_per_kilo_product_lines",), MAX),
         (("churn_per_kilo_product_lines_band",), MAX),
     ],
+    # Its declining target (card P2): a later anchor restarts the decline, a
+    # longer stride or a smaller step slows it; each is a raise.
+    "dev/governance/config/machinery_target_budgets.json": [
+        (("_*",), FREE),
+        (("anchor",), FROZEN),
+        (("every_merges",), MAX),
+        (("step",), MIN),
+    ],
 }
 
 
@@ -942,6 +950,16 @@ def self_test() -> int:
           (True, True))
     check("machinery: a comment edited is routine", raised(G, g0, {**g0, "_comment": "y"}), False)
 
+    T = "dev/governance/config/machinery_target_budgets.json"
+    t0 = {"_recorded": "x", "anchor": "a" * 40, "every_merges": 290, "step": 48}
+    check("target: null control", raised(T, t0, t0), False)
+    check("target: a faster decline is routine",
+          (raised(T, t0, {**t0, "step": 49}), raised(T, t0, {**t0, "every_merges": 289})), (False, False))
+    check("target: a slower decline is a raise",
+          (raised(T, t0, {**t0, "step": 47}), raised(T, t0, {**t0, "every_merges": 291})), (True, True))
+    check("target: a moved anchor is a raise", raised(T, t0, {**t0, "anchor": "b" * 40}), True)
+    check("target: the file removed is a raise", raised(T, t0, None), True)
+
     U = "tests/new_budgets.json"
     check("unknown file: a change with no schema is a raise", raised(U, {"x": 1}, {"x": 0}), True)
     check("unknown file: added is a raise", raised(U, None, {"x": 1}), True)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
