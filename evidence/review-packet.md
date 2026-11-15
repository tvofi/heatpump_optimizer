# Review packet #3600
head: e3df1f1ca69586ecb91b465cba874ece98a9689b
base: 23cc7b8e1d004279d99bd59f3d2bd2a8f885b426

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=132622049503 queued
arm id=132620620794 skipped
budget-raise-gate / budget-raise-gate id=132622049490 queued
cancel-superseded id=132621709601 queued
codeql id=132622050670 skipped
governance id=132622051161 skipped
hassfest id=132622050855 skipped
kernel-points id=132622051215 skipped
prelude id=132621709261 queued
refresh id=132621709507 queued
tests id=132622051339 skipped
validate id=132622050728 skipped

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 53cbebab: R11-PRE-OBJECTIVE-FUNCTION: R11-PRE-OBJECTIVE-FUNCTION resolved on origin/handoff/audit-r10-roster
NOTE body item d891553c: R11-INTAKE-R10-RESIDUE
NOTE body item 9f33edc5: R11-INTAKE-R10-RESIDUE
NOTE body item cd649fef: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

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
diff --git a/dev/audit/README.md b/dev/audit/README.md
index ed19414654..518f25119e 100644
--- a/dev/audit/README.md
+++ b/dev/audit/README.md
@@ -41,14 +41,12 @@ or removed one goes red. Decision 0016 ties a round to its major version.
 | 13 closure | every phase drained | the criteria below hold | `tools/audit/seat/state_docs.py`, `tools/audit/seat/handover_prompt.py`, `tools/audit/seat/resume_doc.py` | `orchestrator.md` section 9 | the final state comment on #201 |
 
 Lessons (triage batch 141, P545): stack a later part only under the stack
-study's conditions, at the parent's merge verdict, never its handoff (round
-10's replay: 0.00 to 0.06 h gained in every arm); log a cloud fire by the
+study's conditions, at the parent's merge verdict, never its handoff; log a cloud fire by the
 session id `list_runs` shows about 2 min later, never by the trigger id, which
 later answers 404; an owner order with a trigger condition joins the
 orchestrator's pending list the turn it is given, and rotation carries it;
 `roster_edit.py append-carry` takes no `--reason`, and each queued op's drain
-refusal is read back, since a refused line is never retried. A shape
-classifier is driven over a spelling corpus (`fixer.md` step 2).
+refusal is read back, since a refused line is never retried.
 
 Closure, the owner's sentence (tvofi, 2026-11-07): "The programme is not
 considered closed until both v.10.0.0 and the catalog PR has landed, there are
@@ -67,11 +65,9 @@ only after tvofi says they opened the card's tabs on it, never without.
   stays. Owner, verbatim: "make sure the retirement of the standing seats dont
   cause you to run things inline": a seat stays until its job is live and
   verified, and its work never moves into the orchestrator's turns.
-- Context rotation, a fresh context between stages (rca, fix, handoff), never
-  mid-task or mid-merge: about 150 k tokens for mechanical, standing and relay
-  seats, reviewers and S and M fixers; about 300 k for L and XL fixers,
-  designers, pre-studies, root-cause and plan seats; about 500 k for the
-  orchestrator, which rotates through `state_docs.py` and the resume.
+- Context rotation between stages, never mid-task or mid-merge: sizes in
+  `fixer.md` and `standing.md`; the orchestrator at about 500 k tokens, through
+  `state_docs.py` and the resume.
 - A blocked verdict of a mechanical class (carry-*, body or figure staleness,
   red-check answer, row-format, head-moved, conflict) goes to a script where
   one exists, else to a fresh sonnet or haiku seat on a short brief; a
@@ -102,27 +98,22 @@ against a measured baseline and a null control
   user-owned repository; round 10's D13 probe). Weigh plan, visibility, the
   HACS redirect, App installations, deploy key, ruleset ids and owner-keyed
   instruments; after a transfer re-probe queue latency, `merge_group` gate
-  names and CI minutes against the train; adopt or decline, and close the held
-  groups the queue makes moot (R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY,
-  R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE, R10-FLOW-BODY-ONLY (a)). Context: the Lean flow
-  pre-study, section K9 (out of the tree).
+  names and CI minutes; adopt or decline, and close the held groups the queue
+  makes moot (R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY,
+  R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE, R10-FLOW-BODY-ONLY (a)).
+  Context: the Lean flow pre-study, section K9 (out of the tree).
 - Intake's baseline: R10-PROTECTION-CENSUS's result,
-  `dev/audit/rounds/round10/protection-census/`. On it, B1
-  (triage batch 245, P740) opens the round unless ordered into round 10: on an
-  all-product diff `briefs`, `policy-docs` and `wave-script` turn advisory, and
-  `blueprints/` joins the product predicate.
+  `dev/audit/rounds/round10/protection-census/`. On it, B1 (triage batch 245,
+  P740) opens the round unless ordered into round 10: on an all-product diff
+  `briefs`, `policy-docs` and `wave-script` turn advisory, and `blueprints/`
+  joins the product predicate.
 - Retire the merge and dispatch seats into beat jobs (tvofi 2026-11-12;
   R10-STANDING-CONTRACTS-P2 carries 9, 12-14), size L, design first: the train
   (`train.sh`, `merge_train.py`) reports each pitch to the digest and retires
   `standing-merge.md`; `standing-dispatch.md`'s dispatch half calls `bus.sh
   dispatch`, never a second writer of the registry or reviewer-fire close. A
   seat stops only after its job ran one real cycle beside it (one pitch merged,
-  the seat agreeing), never into the orchestrator's turns. Load, session s14
-  from 2026-11-11T01:02Z: 48 merges, 46 reviewer fires.
-- Every round-10 group at stage deferred reopens as written, brief and
-  carries kept (triage batches 238, 240 and 241 name them and the carries
-  re-homed to the groups owning `merge_train.py`,
-  `tools/pr/cancel_superseded.py` and `tests/entities.py`).
+  the seat agreeing), never into the orchestrator's turns.
 - R11-INTAKE-R10-RESIDUE holds R10-ROUND-PLAYBOOK-FINAL's carries 17, 25, 26 and
   35 to 41, as written on the roster. Carry 31 goes with it: one paragraph each
   in `dev/governance/dimensions/D11.md` and `D13.md`, naming the convergence
@@ -163,6 +154,19 @@ against a measured baseline and a null control
   a decision record is named by number, never by path, so none joins
   `policy_lint`'s corpus.
 
+## Round start
+
+Before phase 1, the pickup; each later step is its owner's rule.
+
+1. Pickup: read each line to none, a disposition per line by `tools/audit/seat/roster_edit.py` (scheduled, built before finders, refused with a reason):
+   `python3 tools/audit/carry_audit.py roster`
+   `python3 -c "import glob,json;r=max(glob.glob('dev/programme/rosters/wave-r*-groups.json'),key=lambda p:int(p.split('-r')[1].split('-')[0]));[print(g['group'],g['resume']['stage']) for g in json.load(open(r))['groups'] if g['resume']['stage'] not in ('done','absorbed','refused')]"`
+2. Evaluation before the baseline: decision 0018, R11-PRE-OBJECTIVE-FUNCTION, `check_scopes.py`.
+3. Denominator, unreached remainder, added dimensions, D11, D13: R10-DIMENSIONS-FULL-COVERAGE part 2, carried on R11-INTAKE-R10-RESIDUE.
+4. Scope: an owner-filed or outside-filed item folds into the ongoing round
+   unless its filer explicitly defers it; silence is not one. Record who, when
+   and their words in the group's note (`roster_edit.py set-resume --field note`).
+
 ## The harness contract
 
 A harness is a standalone script under `dev/audit/rounds/round<N>/D<k>/`, Python or
@@ -270,32 +274,30 @@ brief cited by it.
 A harness `tools/audit/seat/moved_paths.py` lists with a `[STALE?]` read is a
 record, not re-run at `main`, unless a bug class's `detector` or `barrier`, or
 the latest round's `ISSUES.json` or `JUDGE.json`, cites it: then it is
-repaired, old path first. A seat re-running a retired one repairs it first.
+repaired, old path first.
 
 ## A defect in an instrument is a finding
 
 A defect your dimension's method meets in an instrument (`tests/hastub`, the
 gate's checks and budgets, the harness contract, the lint lanes, this toolkit)
-is a finding **of your dimension** under the same bar as any other, not prose
-in a report. It goes panel, judge, then issue, and **filing waits for the
-judge**, who re-measures with the accused instrument; a verifier who cannot
-make the accused check fire has not refuted it, and says which they could not
-separate. `CLAUDE.md`'s order still governs: a one-line instrument repair is
-made in place, with no issue.
+is a finding **of your dimension** under the same bar as any other. It goes
+panel, judge, then issue, and **filing waits for the judge**, who re-measures
+with the accused instrument; a verifier who cannot make the accused check fire
+has not refuted it. `CLAUDE.md`'s order still governs: a one-line instrument
+repair is made in place, with no issue.
 
 ## Rounds 1-3 are at a SHA
 
 `tools/audit/round1/` to `round3/`, the done rosters `wave-1b-groups.json`,
 `wave-2-groups.json` and `wave-3-groups.json`, `web-phase0.js` and
 `triage-quiet-judges.json` are at
-**`d5d8c4a72fa7be7aebecc9e58d55002be17cac08`** (`origin/main` at v6.3.18, on
-`main`'s first-parent history; `git show d5d8c4a:tools/audit/round2/JUDGE.md`);
-their briefs record what a judge established and refuted, so read them before
-re-deriving anything a group in them settled. Every number anything still acts
-on is in `dev/programme/register/audit-2026-09.md`. Round 2's harnesses are at
-`757e164` (which still run is `round2/HARNESSES.md` at `d5d8c4a`, final at
-that commit only), its numbers recorded at `c398fc84`; the tag `audit-round2-evidence` moved once, so cite the SHA. A
-harness's root rule varies (`D6/claims.py` measures the working directory,
+**`d5d8c4a72fa7be7aebecc9e58d55002be17cac08`** (v6.3.18; `git show
+d5d8c4a:tools/audit/round2/JUDGE.md`); their briefs record what a judge
+established and refuted, so read them before re-deriving. Every number anything
+still acts on is in `dev/programme/register/audit-2026-09.md`. Round 2's
+harnesses are at `757e164` (`round2/HARNESSES.md` at `d5d8c4a` says which still
+run), its numbers at `c398fc84`; the tag `audit-round2-evidence` moved once, so
+cite the SHA. A harness's root rule varies (`D6/claims.py` measures the working directory,
 `D7/sysid_plant.py` its own checkout): copy it into the tree under test and say
 which it used.
 
@@ -310,6 +312,3 @@ evidence is archived, instruments are kept.
 | `h8_single_scenario.py` | whether the stress gate detects a 2x regression confined to one scenario, and stays quiet on a multi-start basin flip (#346) | `291ae76` (#378) | anyone changing `tests/stress.py`'s per-scenario or solver-work rules |
 | `h9_basin_coverage.py` | how many of the 51 sweep scenarios the solver-work rule judges rather than exempts, against the tree's own floor (#387) | `32f309f` (#388) | the same |
 | `k1725_blas_kernel_gap.py` | the ftol check's arms and the R9-F2.1 P3 margins, per OpenBLAS kernel via `OPENBLAS_CORETYPE` | `613bff1b` (#1726, #1725) | anyone adding a knife-edge optimizer comparison (`tests/README.md`'s kernel rule) |
-
-All four drive production symbols under the harness contract; never run
-`j5_gil.py` on `FakeHass` (the first trap above).
diff --git a/dev/programme/delivery/3600.md b/dev/programme/delivery/3600.md
new file mode 100644
index 0000000000..97e4726e06
--- /dev/null
+++ b/dev/programme/delivery/3600.md
@@ -0,0 +1 @@
+- [#3600](https://github.com/tvofi/heatpump_optimizer/pull/3600) — **open**, R10-PLAYBOOK-ROUND-START: the playbook's round-start section (pickup, evaluation, denominator, scope) (R10-PLAYBOOK-ROUND-START)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
