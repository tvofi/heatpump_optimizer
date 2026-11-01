# Review packet #3147
head: dba968f8d579890b70db289f0b5bd0400d0b921b
base: 0166aefd7047b98e275bc0ab4e604fac3a7c75c6

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: green
CodeQL id=125005467927 success
arch-score id=125017425621 skipped
arch-score / arch-score id=125016251021 success
arm id=125005075829 skipped
budget-raise-gate / budget-raise-gate id=125017423839 success
cancel-superseded id=125007454448 skipped
codeql id=125017424910 skipped
codeql / Analyze (actions) id=125005259363 success
codeql / Analyze (javascript-typescript) id=125005259428 success
codeql / Analyze (python) id=125005259536 success
gate id=125017757809 success
governance id=125017425356 skipped
governance / delivery-status id=125005259411 success
governance / delivery-status-publish id=125005260622 skipped
governance / env-matrix id=125005259548 success
governance / instrument-self-tests id=125005259556 success
governance / policy-docs id=125005259503 success
governance / record id=125005260925 skipped
governance / wave-script id=125005259497 success
hassfest id=125017425305 skipped
hassfest / hassfest id=125005259456 success
kernel-points id=125017425426 skipped
pr-contract id=125017758584 skipped
pr-contract / pr-contract id=125016581919 success
prelude id=125007453504 success
refresh id=125007453642 success
tests id=125017425434 skipped
tests / arch-instrument id=125005892448 success
tests / briefs id=125005259379 success
tests / browser id=125005892390 success
tests / ci-ratchet id=125015993252 skipped
tests / claims-autofix id=125012091624 skipped
tests / closure-scope id=125005259518 success
tests / closures id=125005892356 success
tests / closures-autofix id=125015993508 skipped
tests / coverage id=125005892366 success
tests / coverage-ratchet id=125014221885 success
tests / fast (3.14) id=125005892461 success
tests / graders-head-copy id=125014221891 success
tests / lane-proofs id=125015029272 success
tests / mutation id=125005259475 success
tests / mutation-autofix id=125006314713 skipped
tests / mutation-pins id=125006314884 skipped
tests / nightly-ha id=125005893595 skipped
tests / nightly-status id=125005259483 success
tests / replay id=125005894137 skipped
tests / typing id=125005892536 success
validate id=125017425027 skipped
validate / validate-hacs id=125005259427 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item e280cf30: #201
NOTE body item a89d0169: #201
NOTE body item 89eeae7b: dismissed:the install step already detects it
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         python tests/typing_ruler.py --mypy --emit <file>
             `tests/typing_ruler.py` is in the tree at this head
  unverified git grep -n 'reversed(' -- custom_components/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/audit/seat/seat_venv.sh --self-test
             `tools/audit/seat/seat_venv.sh` is in the tree at this head
  ok         bash tools/audit/seat/cloud-setup.sh --self-test
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff <merge base> HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tests/closure.py select --diff <merge base>
             `tests/closure.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head
  ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         tests/env_drift.py --all ca6333333afc1ec7937b9792880458d190f4d4d2
             `tests/env_drift.py` is in the tree at this head

FIGURES: 12 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/learner_progress.py b/custom_components/heatpump_optimizer/learner_progress.py
index 4afc59fd8..8f6981842 100644
--- a/custom_components/heatpump_optimizer/learner_progress.py
+++ b/custom_components/heatpump_optimizer/learner_progress.py
@@ -75,6 +75,9 @@ def snapshot_rates(
     negative rate, which ``learner_progress`` treats as nothing counted.
     """
     rates: dict[str, float | None] = dict.fromkeys(counts)
+    # Declared, not inferred: mypy 2.4's reversed() overload reads Any out of
+    # a sequence whose element type holds Any.
+    snap: Mapping[str, Any]
     for snap in reversed(snapshots):
         taken = stored_instant(snap.get("taken_at"))
         if taken is None:
diff --git a/custom_components/heatpump_optimizer/snapshots.py b/custom_components/heatpump_optimizer/snapshots.py
index 31a474963..07a8f82d8 100644
--- a/custom_components/heatpump_optimizer/snapshots.py
+++ b/custom_components/heatpump_optimizer/snapshots.py
@@ -200,6 +200,9 @@ class SnapshotRing:
         depend on this never
         raising (#D1-05).
         """
+        # Declared, not inferred: mypy 2.4's reversed() overload reads Any
+        # out of a sequence whose element type holds Any.
+        snap: dict[str, Any]
         for snap in reversed(self.snapshots):
             if not snap.get("healthy") or "before_reset" in snap:
                 continue
diff --git a/dev/programme/carries/carry-201.json b/dev/programme/carries/carry-201.json
index cddce81ae..4ebd6673b 100644
--- a/dev/programme/carries/carry-201.json
+++ b/dev/programme/carries/carry-201.json
@@ -1,166 +1,180 @@
 {
-  "_comment": [
-    "Carry destination for the round-5 governance/record findings (#1301, R5-D11-02",
-    "and #1303, R5-D13-01). Round 5 filed 48 findings as #1293-#1340 and no umbrella",
-    "issue of its own, so the destination is #201 -- the audit programme's standing",
-    "tracking issue, the one that received round 5's own round-end comment -- and no",
-    "roster group in this tree claims it. Shape and required fields:",
-    ".claude/rules/finding-propagation.md. Linted by",
-    "tools/policy/brief_lint.mjs (the `briefs` CI job).",
-    "A later entry carries to the D0 dimension of a later audit round, from #2114's",
-    "re-key of the R9-F2.1 P3 storage check. The D0 method brief",
-    "(dev/governance/dimensions/D0.md) is policy, so it was not edited: this file is",
-    "the in-tree brief of a stage with no live roster group."
-  ],
-  "issue": 201,
-  "stage": "any later seat that stamps a release (tools/release/stamp.py, the deploy-key tag push of dev/governance/decisions/0009-agent-identities-for-author-and-approver.md step 5); the D13 dimension of a later audit round (dev/governance/dimensions/D13.md is its method, dev/audit/rounds/round5/D13/seat-a/dora_cfr.py its harness); the D11 dimension of a later audit round, whose method dev/governance/dimensions/D11.md is and whose subject is .github/workflows/governance.yml; and the D0 dimension of a later audit round, whose method dev/governance/dimensions/D0.md is and whose capture harness is tests/optimality.py; and any later seat that repairs the nightly-ha positive control in tests/nightly_ha.py (the check is `check_hb_positive_control`, and the sites the RCA names are the py-spy call and the heartbeat pin); the next planning seat (the schedule model at tools/plan/replan.py and the page it feeds); and the roster owner's next re-record of the roster's wave field; the owner's decision on the off-host liveness barrier for audit class N-silent-stop (dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md section 6, the seat that creates the schedule); and any later seat that maintains tools/audit/seat/failure_logs.sh or runs it from a cloud seat; the owner's decision whether to run the planted-defect audit that the review-strength guardrail names when it trips (tools/audit/seat/review_strength.py --guardrail, report-only under owner ruling R13)",
-  "carries": [
-    {
-      "from": "the round-5 D11-02 finding (#1301), whose fix is rule \"rows\" in tools/release/stamp.py -- the stamp now re-applies `record`'s own predicate to the window it is about to close",
-      "effect": "narrows",
-      "control": "The window `<last v* tag>..origin/main` is the window `record` reads, and the tag push is main-protect's only bypass, so one stamp can carry every rowless merge behind the new tag out of every future window at once. Established by measurement, not argument: the finding's harness (dev/audit/rounds/round5/D11/seat-b/corpus_churn.py) reads the same counts at origin/main before this fix and at this fix's head, and the number that matters is the INSTRUMENT's, not the harness's -- `python3 tests/delivery_status.py --check` exits 0 over a window whose merges are minutes old, because at stamp time every merge is PENDING and `--check` refuses only OVERDUE and UNCHECKED; the new `--require-rows` exits 1 over the same ledger and names the rowless merges. The perturbation that would have voided it: a row added for one window merge moves the count by exactly one. The fix is measurement-neutral by construction -- corpus_churn.py prints byte-identical RESULT lines at the pre-fix and post-fix heads, which is the null control separating `--require-rows` (reading the ledger under a stricter bar) from a change to the ledger itself.",
-      "remeasure": "At your own merge base: `python3 tests/delivery_status.py --check` and `python3 tests/delivery_status.py --require-rows` over the same tree, then `python3 dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`. They agree on every verdict but PENDING, and that single disagreement is the whole finding; a later round that reads them as the same predicate has re-derived the escape.",
-      "brief": "Stamp-time precondition, not an opportunity: `tools/release/stamp.py` REFUSES to stamp when any merged pull request in the window it would close has no disposition row, and the only override is the explicit `--allow-rowless` flag, which prints the instrument's own output before proceeding. The rows it demands are the ones `record` demands, on the same two surfaces tests/delivery_status.py's DISPOSITION_FILES names. A stamp over a rowless window is no longer an ordinary release step: it is a knowingly deferred batch, and it is recorded as one. The re-application lives in the stamp's module docstring as rule \"rows\", so a seat that reads the contract rather than the flag sees it before it runs."
-    },
-    {
-      "from": "the round-5 D13-01 finding (#1303), whose fix makes the CFR exclusion list a registered in-tree artifact that the instrument reads from the repository root, failing closed when it is absent",
-      "effect": "narrows",
-      "control": "The finding: the round-5 harness opened `cfr_exclusions.json` beside itself, so `cfr_excluded` came from a file the tree did not carry -- and dev/governance/dimensions/D13.md asks for `a JSON file beside policy_budgets.json that your first round creates with a reason per job`. Established by measurement at both ends in a clone at the round's baseline: with the sibling list and the tree holding no list, the harness prints cfr_excluded=0.0; with the artifact registered at dev/governance/config/cfr_exclusions.json and the sibling removed, it prints the identical eight-merge numbers, which is the null control that shows the re-point moved the citation and not the metric. The perturbation the brief names still moves the number by exactly the excluded job's head count: `EXCLUSION_DROP=record` takes cfr_excluded 0.0 -> 1.0, record's eight of eight heads. And the fail-closed arm: with the artifact removed the harness raises, naming the registered path, rather than silently excluding nobody -- which is the always-green shape a metric `retaken minus the by-design reds` degrades into.",
-      "remeasure": "At your own merge base: run the D13 instrument (dev/audit/rounds/round5/D13/seat-a/dora_cfr.py) with its fixtures, then again with EXCLUSION_DROP naming the excluded job. If the second run's cfr_excluded does not move by that job's head count, the list is not being read. Then `python3 -c \"import json;print(sorted(json.load(open('dev/governance/config/cfr_exclusions.json'))['excluded_jobs']))\"` -- the list is a narrowing of the metric, so a round that GROWS it is making a deliberate edit, and an unjustified entry hides a real change failure rather than a by-design one.",
-      "brief": "Constraint on how the exclusion list is carried: it is ONE registered artifact at `dev/governance/config/cfr_exclusions.json`, a top-level object with an `excluded_jobs` map keyed by check-run name beside a `_comment`, in the shape dev/governance/config/policy_budgets.json takes. The instrument resolves it against the REPOSITORY, not against the seat, and raises when the map is missing or empty -- so a later round does not create a second list under a name of its choosing, and does not publish an un-excluded rate under the excluded rate's name. Each entry carries the reason and the citation it rests on; the one entry at the round-5 values is `record`, and the reason a later round must re-check rather than assume is that the red is by design only while the batch interval holds."
-    },
-    {
-      "from": "the round-6 D11-02 finding (#1403), whose fix adds the `Restore the check source from the base commit` step to the `policy-docs` job of .github/workflows/governance.yml and the entry-point exit-status arm to tools/policy/policy_lint_mutants.mjs",
-      "effect": "narrows",
-      "control": "The assumption before this fix was that a required context which grades the policy corpus runs the corpus's own checker. It did not: `policy-docs` checked out no `ref:`, so the program grading the corpus was the pull request's copy of it. Established by measurement at both ends in a worktree of the fix's head whose only differences were a corpus defect (one line of CLAUDE.md citing a file the tree does not carry, line count unchanged) and a one-line mutation of the checker's exit status -- `process.exit(errors > 0 || rc ? 1 : 0)` gated on `process.env.POLICY_LINT_TEMPLATE`, which is the shape that evades the gate's own witness. Before the fix, that tree's `node tools/policy/policy_lint.mjs` exited 0 while printing `ERROR [citations] CLAUDE.md:20` and `ERROR [index]`, its stdout byte-identical to the unmutated checker's, and the base's mutation lane exited 0 as well; the acceptance's template arms in tests/entities.py, which empty the checker and demand a red, returned 1 and 0. After the fix, on the same tree: the lane exits 1 naming the exit status, and the required context's own command exits 1 naming the corpus defect once the pin has run, the pin reporting one file differing from the pull request's copy. The null control runs both ways: on the healthy tree at the same head the pin restores nothing and the lint stays at 0, and with the pinned ref equal to the head -- the push-to-main shape, where the step reads `github.sha` -- the checkout is a no-op over a clean tree.",
-      "remeasure": "At your own merge base: apply the same two perturbations (a corpus defect that does not change a line count, and an exit status that does not track the findings), then run the job's own commands in this order -- `node tools/policy/policy_lint_mutants.mjs` must exit nonzero naming the exit status; `git checkout <base> -- 'tools/policy/*.mjs' 'tools/policy/*.py' 'tools/policy/vendor'` must print a count you can read; `node tools/policy/policy_lint.mjs` must exit 1 with your corpus defect named. Require both ends: on the healthy tree each of those is 0, and a pin whose checkout silently matched nothing would leave the mutated checker in place and print a count of zero. Then check the three shapes the pin does not cover, each a candidate finding rather than a refutation: a criteria edit, a checker added as a module beside the pinned programs, and a program edited together with the self-test lane that drives it.",
-      "brief": "Constraint on any seat adding a corpus check or moving a step in the `policy-docs` job of .github/workflows/governance.yml. (1) A corpus check is a function inside tools/policy/policy_lint.mjs, named in that file's own lists of check names, never a module beside it: the new step restores the `.mjs` and `.py` programs under tools/policy/ plus tools/policy/vendor from the base commit, and a file the base does not carry cannot be restored, so a checker added as its own module stays the pull request's own and the corpus is graded by the copy under test -- the defect of #1403 in its original shape. (2) The job now has two halves and that step is the boundary. The five steps above it -- tools/policy/policy_lint_mutants.mjs, the `--self-test` runs of tools/policy/fragments_sync.mjs and tools/policy/record-predicate/sweep.mjs, the `--hooks` run of tools/policy/policy_lint.mjs and the `self-test` run of tools/pr/gh_comment.py -- drive the PULL REQUEST's programs on purpose, because a self-test that ran the base's copy would report on neither; every step below it grades the pull request's data with the base's programs. Moving a step across that boundary silently changes which side of it a check is on. (3) The pin covers programs, not criteria: dev/governance/config/policy_budgets.json, dev/governance/config/policy_known_bad.json, dev/governance/config/cfr_exclusions.json and the sync surface tools/policy/fragments_sync.mjs checks against .claude/workflows/web-fragments.md stay the pull request's, because a fixture's expected outcome has to be the data under test. Those three places -- a criteria file, a checker outside the restored paths, and the self-test block above the step -- are where the pull request's own copy is still what runs, and that is where a later round hunting this class of defect should look."
-    },
-    {
-      "from": "the pull request fixing the round-6 D13-03 finding (#1407), which makes the round-4 DORA instrument (dev/audit/rounds/round4/D11/dora_keys.py, `cfr_keyings`) report the change-failure rate at BOTH keyings -- at the merge commit, where `dev/governance/config/cfr_exclusions.json` acts, and at the pull-request head, where a merge is gated -- and pins the pair in tests/entities.py",
-      "effect": "narrows",
-      "control": "The finding: the exclusion list's single entry `record` fails at 58 of the 67 merge commits in the window v6.6.0..e336cc2c and is SKIPPED at every one of the 67 pull-request heads, because its workflow gates the job to the non-pull_request event. So excluding it moves the merge-keyed rate 0.925 -> 0.09 and leaves the head-keyed rate at 0.134 -- the rate at the surface a merge is actually gated on, unchanged. Established by measurement at both ends: the instrument prints the un-excluded rate beside the excluded one from the same call over the same maps, so the exclusion's own delta is visible on each keying, and it is 56 merges at the merge keying and zero at the head keying; the round-6 finder harness measured the same figures, so the tracked instrument reproduces them rather than restating them. The perturbation that would have voided it: the names failing at the HEAD are `nightly-status` (7 of the 67) and `delivery-status` (2 of the 67), so one entry added for either moves the head keying and the pair stops separating the two surfaces. The key-set null control tests/entities.py already holds -- `excluded_jobs` is exactly the set holding `record`, with the gate jobs absent -- is what refuses that entry.",
-      "remeasure": "At your own merge base, run `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D11/dora_keys.py` and read `cfr_merge_keyed` beside `cfr_head_keyed`; both are RESULT lines the instrument prints, and `cfr_exclusions` is printed with them so the list a rate came from is on the same screen. Or run dev/audit/rounds/round5/D13/seat-a/dora_cfr.py with `EXCLUSION_DROP=record`, which moves the merge-keyed rate by that job's head count. A rate reported at one keying only, or an entry added for a name that fails at the head, is this finding re-derived. The instrument pins its window (`D13_SINCE` / `D13_HEAD`), so a re-take names its own baseline instead of tracking a moving main.",
-      "brief": "Constraint on every change-failure rate a later round reports: the rate is TWO numbers -- the merge-keyed rate and the pull-request-head-keyed rate -- printed together and never one alone, because `dev/governance/config/cfr_exclusions.json` narrows only the merge keying while a merge is gated on the head keying. The artifact's `_keying` field states that rule for whoever edits the list, and dev/governance/dimensions/D13.md's DORA item asks for the list without naming a keying, which is how the single-number report arose. A check-run name that fails at the pull-request head is a real gate red: it must NOT be added to the list, however much it costs the merge keying, and a report that names such a name as excluded is the escape this carry closes."
-    },
-    {
-      "from": "the pull request fixing the round-7 D13-06 finding (#1476), which makes the same round-4 DORA instrument report the rate PER CHECK-RUN NAME at both keyings (dev/audit/rounds/round4/D11/dora_keys.py, `cfr_by_name`), and records `mutation` in dev/governance/config/cfr_exclusions.json's new `not_excluded` map as a name deliberately NOT on the list",
-      "effect": "narrows",
-      "control": "The finding: the carry above settles that the rate is two numbers, but two aggregates still do not say WHICH name separates them, and over the round-7 window the whole separation is one name. `mutation` fails 4 of the window's 31 merge commits and 0 of its 31 pull-request heads, so it is the entire 0.129 between the merge-keyed rate (0.226) and the head-keyed one (0.129) -- invisible in either published figure, and the reason a reader cannot tell a merge-surface red from a head-surface one. Established by measurement at both ends: `cfr_by_name` prints the pair `[merge, head]` for every name failing at EITHER surface, over the same maps `cfr_keyings` aggregates, so the four names other than `mutation` that fail at the merge keying print [0.032, 0.0] apiece and `delivery-status` prints the mirror [0.0, 0.129]. The perturbation that would have voided it: adding one name to the exclusion list IN MEMORY moves the merge-keyed rate by exactly that name's count and leaves the head-keyed rate where it was -- `mutation` 0.226 -> 0.097 while the head keying stays 0.129 -- which is the arithmetic statement that it is a merge-surface red. The null control is the key set: a name failing at neither surface (`record`, 0 of 31 here) is ABSENT from the map rather than a zero row, so the map's keys are compared as a set and never as a total.",
-      "remeasure": "At your own merge base, run `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D11/dora_keys.py` and read the `cfr_by_name` RESULT beside `cfr_merge_keyed` / `cfr_head_keyed`; the per-name pairs must sum to the aggregate keyings over the same window, and any name whose pair is nonzero at one surface only is a candidate the list owner must judge. Then `python3 -c \"import json;print(sorted(json.load(open('dev/governance/config/cfr_exclusions.json'))['excluded_jobs']))\"` -- it must still be exactly `['record']`. A round that reports a single per-name number, or that finds `mutation` (or `nightly-status`, or `delivery-status`) added to `excluded_jobs`, has re-derived this finding or the one above it.",
-      "brief": "Constraint on how a later round reports the change-failure rate: per-name at both keyings, BESIDE the two aggregates and never instead of them. Two aggregate rates hide which name separates the surfaces, and here the whole difference is one name -- and the instrument cannot decide whether that name's merge-surface red is a change failure at all. `mutation` fails 4 of the window's 31 merge commits (two pairs merged 4-5 s apart, i.e. two batch merges) where neither pull request's own head failed it, because the lane's inventory is the TREE (`tests/mutation_table.py`'s `unpinned_sites`) and on a push to `main` its scoping base IS `HEAD`, so a batch's merged tree can red it where no head did. Nothing in the finding says the red is spurious; it says whether a merge-surface red on a batch-merged tree is a change failure is the exclusion list owner's judgement, and it is recorded rather than made: `mutation` stays off the list, and dev/governance/config/cfr_exclusions.json's `not_excluded` map carries the reason and the citation so the next reader meets the answer in the artifact rather than in a merged pull request's comments. Adding it to `excluded_jobs` is the same deliberate edit as growing the list, and owes the same justification."
-    },
-    {
-      "from": "the seam the R7-INSTR-01 fix (#1477) returned when tools/audit/prepare_baseline.sh was run as its own generator control: at this tree's merge base the script REFUSES to prepare a baseline for every round number except 4, so the documented way to prepare a round is inoperative for the next round",
-      "effect": "removes",
-      "control": "The script's `finders_can_start` step refuses when a file a `tests/*.py` script hands to `Path(...)` or `open()` exists in the source checkout but not in the tree it just prepared, and `strip_earlier_rounds` deletes every `tools/audit/round*` except the round being prepared. Two files under `tools/audit/round4/` are read that way by tests/entities.py -- `Path(\"dev/audit/rounds/round4/D6/claims.json\")` and `Path(\"tools/audit/round4/D11/governance_cost.py\")`, added 2026-09-19 (a7d97d20) and 2026-09-20 (cd4b1927) -- while the refusal itself dates from round 4 (c68259b8, 2026-09-12). Each was harmless alone; together, any preparation whose round is not 4 drops files the HEAD tests open, and the script refuses after creating the worktrees and before writing any BASELINE.md. Established by measurement, not argument: in a throwaway clone of this tree's merge base, `PYTHON=<interp> bash tools/audit/prepare_baseline.sh 98 6e2a0f2a` and the same script with this fix applied at round 99 both print `refusing: the preparation dropped file(s) a tests/*.py script opens unguarded: tools/audit/round4/D11/governance_cost.py dev/audit/rounds/round4/D6/claims.json`, while the SAME script at round 4 completes -- `RESULT finders_can_start=ok` for the export and all five worktrees -- which is the control separating the round-from-4 strip from the environment. The rounds since have been prepared by hand (round 6's dev/audit/rounds/round6/BASELINE.md is hand-written and round 7's D13 was dispatched by hand), so this is a latent cost rather than a stopped programme.",
-      "remeasure": "At your own merge base, in a scratch clone so the worktrees and the export land outside this repository: `git clone --depth 1 --no-single-branch file://<this checkout> /tmp/pb && cd /tmp/pb && PYTHON=$(command -v python3) bash tools/audit/prepare_baseline.sh 98 $(git rev-parse HEAD)`. A refusal naming `tools/audit/round4/...` is this seam re-derived; then run it at round 4 and require it to complete, which is what says the refusal is about the strip and not about your clone. Two questions are open and belong to whoever holds the audit wall rather than to a fixer: whether the strip should exempt a file a HEAD test reads unguarded, or whether those two tests should read the register through a path that survives a round's preparation. Do not settle it by widening `finders_can_start` -- the refusal is the half that catches a preparation dropping a file by accident, and it is the only guard there.",
-      "brief": "Constraint on preparing the NEXT round's baseline: running `tools/audit/prepare_baseline.sh <round> <sha>` for any round other than 4 refuses at this tree, after creating the worktrees and before writing any BASELINE.md, and the refusal is correct about its own predicate -- the prepared tree really does lack two files tests/entities.py opens unguarded, so a finder in it would die at import before its first measurement. Prepare the round deliberately instead of around the script: either carry the two `tools/audit/round4/` files into the export and the worktrees (the wall's rule is that earlier rounds must not STEER a finder, and a file a test reads is not steering), or re-point those two tests at a path that survives. Then take what #1477 fixed as given -- D13 is a dimension of the schedule in .claude/workflows/audit-find.js and needs a worktree rather than the export -- and keep the two lists it shares with this file's ISOLATED_DIMS in step, which tools/policy/check-wave-script.mjs now derives and refuses to see drift."
-    },
-    {
-      "from": "the v6.7.8 stamp hotfix (the pull request repairing main's red entities check after the stamp commit), whose fix restores the may-drift entry R9-F2.3 (#1723) suspended for its wood_coil claim -- which the stamp deleted without restoring -- and moves the R8-P3 coverage ruling into tests/env_drift.py's may_drift_coverage_error, executed by --claims-only",
-      "effect": "narrows",
-      "control": "Established by measurement at both ends. At the stamp head, tests/entities.py's own check failed with uncovered ['wood_coil'] while the stamp's claims self-check had printed 'claims hygiene: HEAD^1 ok' -- the stamp's self-check DOES exec `tests/env_drift.py --claims-only HEAD^1` on the post-stamp tree, but --claims-only carried the scope rule (entries within MAY_DRIFT_ALLOWED, no name both claimed and may-drift) and not the coverage rule (every allowed name is may-drift or claimed for THIS VERSION), so a claim deleted by the stamp left its suspended entry covered by nothing. With the fix, the same --claims-only invocation on the broken tree refuses with MAY-DRIFT UNCOVERED naming wood_coil and exits 1, which publish_stamp treats as a refusal: undo_local_stamp discards the stamp commit before anything is pushed. The perturbation that would have voided it: re-suspending the entry at the fix head reproduces the refusal, restoring it returns exit 0. The null control: on the healthy tree the added rule changes no verdict -- claims hygiene stays ok -- because a tree whose may-drift list is complete satisfies the coverage rule by construction.",
-      "remeasure": "At your own merge base: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only <ref>` on a tree whose claim file suspends a may-drift entry for a claim that is absent or stamped for another VERSION must exit 1 with MAY-DRIFT UNCOVERED naming that entry; restoring the entry verbatim (or carrying the claim for the tree's own VERSION) must exit 0. Before running tools/release/stamp.py over a main whose claim file carries a suspension note, restore every suspended entry verbatim -- the note's own text carries the line -- or the stamp's self-check will discard the commit after making it.",
-      "brief": "Stamp-time precondition, not an opportunity: a stamp that empties the claim list owes every suspended may-drift entry back, verbatim, because a name may leave the may-drift list only while THIS release claims it (the R8-P3 ruling, option (a)) and the claim the suspension was made for expires with the stamp. The obligation is enforced, not advisory -- tools/release/stamp.py's claims self-check execs `tests/env_drift.py --claims-only HEAD^1` on the post-stamp tree and undo_local_stamp discards the commit on refusal -- so a stamping seat that misses the restore loses only the stamp run, never main's green. A suspension note in the claim file is a promise to a human; the coverage rule is the same promise made to the instrument, and the second is the one that refuses."
-    },
-    {
-      "from": "PR #1879 (tools: programme instruments live in the tree, and a check refuses temp paths), whose tools/audit/seat/tmp_paths.py runs in governance.yml's non-grading instrument-self-tests job rather than in a required one",
-      "effect": "narrows",
-      "control": "Established by measurement at both ends. With tools/audit/seat/tmp_paths.py run in the wave-script job (a grading, required job) and tools/audit/seat/ unowned (tvofi, 2026-10-03: audit instruments are not code-owned), `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` refused it as UNCOVERED (uncovered_files=1); moved to instrument-self-tests, whose env sets HPO_JOB_GRADES: nothing, the same command reports uncovered_files=0 and tags it NO-PR-JOB. The null control: tools/audit/seat/merge_train.py, run in that same job from the start, was never reported uncovered. tmp_paths.py --check itself refuses 14 lines at origin/main 20f597c6 and 0 at the PR head, so the check works; only its gate status is weaker than a required grader's.",
-      "remeasure": "At your own merge base: `git cat-file -e <base>:tools/audit/seat/tmp_paths.py` must succeed before any job can restore it from the base; then add it to a pinned job's `git checkout \"$PINNED\" --` list in .github/workflows/governance.yml, declare it in tools/policy/field_coverage.mjs's DECLARED map (that program is pinned, so the declaration must already be on main when the pin lands), and run `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (must report it PINNED, uncovered_files=0), `node tools/policy/field_coverage.mjs` (FIELD COVERAGE ok) and `bash tools/pr/prepr.sh` (its pinned-graders step names a local path for it).",
-      "brief": "Owed follow-up, two pull requests after #1879 merges: make tools/audit/seat/tmp_paths.py a pinned grader in a required governance.yml job, so a temp or machine path in a tracked script, workflow or decision record turns a required context red rather than the non-required instrument-self-tests. Step one declares it in tools/policy/field_coverage.mjs's DECLARED map (pinned, so it must land first); step two restores it from the base in a required job and runs `--check` there. It must not be made code-owned to get there: the owner ruled that audit instruments carry no owner, and decision 0013 stands unamended. Until both land, a red instrument-self-tests at a head is still a red check pr-contract makes the body answer, and tools/audit/seat/merge_train.py stops on it because it is not on the train's ignore list."
-    },
-    {
-      "from": "RCA stale-pins (PR #2073, dev/audit/rca/R9-RCA-stale-pins.md): the frozen fixture tools/policy/fixtures/wave-1b-931dffe.json, pinned by REQUIRED_931DFFE's `wood_share:1152` entry in tools/policy/brief_lint.mjs, which requires a path:line (anchored) ERROR naming thermal_model.py:1152 and so depends on the production file's line layout",
-      "effect": "narrows",
-      "control": "Established by measurement at both ends, with its null control, on origin/main 47b083b0. Unmodified tree: `node tools/policy/brief_lint.mjs` rc 0, `FIXTURE ok: 14 error(s) pin the 931dffe acceptance (9 required)`. Perturbation: prepend 14 comment lines to custom_components/heatpump_optimizer/thermal_model.py (a `return` at line 1138 moves to 1152, inside the +-1 window checkPathLine reads) -> rc 1, `FIXTURE VACUOUS: 931dffe acceptance pins missing`. Prepending 1 line instead leaves it rc 0, so the fixture is not simply shift-sensitive: it needs the cited line NOT to sit near a `return`, which any unrelated production edit above it can change. #2066's new property in thermal_model.py did exactly this.",
-      "remeasure": "Do not trust 1138/1152: they are measured at 47b083b0 and a later stage is judged against its own merge base. At your merge base, list `grep -n '\\breturn\\b' custom_components/heatpump_optimizer/thermal_model.py` near line 1152, prepend (1152 - n) comment lines for the nearest `return` at line n above it, run `node tools/policy/brief_lint.mjs`, and confirm whether it still goes VACUOUS; restore the file afterwards.",
-      "brief": "The D11 round, or whichever seat next edits tools/policy/brief_lint.mjs: stop REQUIRED_931DFFE's `wood_share:1152` pin depending on the live line layout of custom_components/heatpump_optimizer/thermal_model.py, so an unrelated production edit cannot turn `briefs` red. Candidate repairs, to be chosen with the control: point the fixture's citation at a file the fixture owns, or have the pin assert the lookup's refusal reason rather than the production line. Demonstrate it by rerunning the 14-line prepend above: before the repair rc 1, after it rc 0, and a deliberately wrong citation must still produce the ERROR. Do not make prepr.sh run brief_lint on every production diff instead; it took 1 m 45 s under load on 47b083b0 for this one fixture."
-    },
-    {
-      "from": "RCA stale-pins review (PR #2073, round 1, reviewer observation on #2070): CI never runs a round instrument's `--perturb` arm, so an instrument under dev/audit/rounds/ that a production move breaks turns nothing red",
-      "effect": "narrows",
-      "control": "Established at origin/main 47b083b0 by search, with a null control, not by reproducing #2070's breakage. `git grep -n -e '--perturb' -- .github` returns no line, while `git grep -n -e '--perturb' -- dev/audit | wc -l` returns 1704, so no workflow step invokes a perturbation arm. The null control is that CI does run some round instruments: `.github/workflows/governance.yml` line 411 runs `codeowners_gap.py --self-test`, so the absence above is specific to `--perturb`, not to round instruments in general. Not measured here: which round instruments broke on #2070's move of `_on_off_service`.",
-      "remeasure": "At your merge base rerun both `git grep` commands, and list what `--perturb` arms exist with `git grep -l -e '--perturb' -- 'dev/audit/rounds/*.py'`. A workflow that has since added a perturb runner makes the first command non-empty, and this carry is void for the arms it runs.",
-      "brief": "The D11 or D13 round: decide whether CI should run a round's `--perturb` arms, or whether instruments that CI never exercises are expected to rot, and record the decision. This is a different class from the stale-pin RCA (a local predictor porting half of a CI refusal): here no detector exists at any cost. Apply the cost test first, since 1704 mentions across dev/audit means a blanket run is likely unaffordable; a per-round opt-in list is the candidate form. Do not fold it into prepr.sh's step 6d."
-    },
-    {
-      "from": "the pull request for R9-RC-BLAS-KERNEL-RED (#2114), which re-keyed the R9-F2.1 P3 storage check in tests/features.py off a race whose verdict is a property of the runner's BLAS kernel and onto the continuation's own gain, leaving that race measured and printed but not gating",
-      "effect": "invalidates",
-      "control": "Established by measurement with its null control, and the check now prints both sides of the race it no longer gates. On this box (Apple M1, numpy 2.4.6 Accelerate-backed) one run reads `j_plain=110.436632` for the shipped multi-start plan against `j_seeded_half_price=110.129674` for the same solve warm-started from the half-price plan -- 0.307 on the table -- while the Linux kernels of record measured the two within 0.0096 (+0.1000 Sandybridge, +0.0905 Haswell, +0.0904 Nehalem; cited from PR #1726's null control and this check's own log, not re-taken here). The null control is the kernel axis: the same race reads about zero on every kernel of record, which is what separates a kernel-selected basin from a sub-optimal solver. The perturbation that would void the finding is a second kernel class where production's multi-start lands in the half-price plan's basin. The re-key is measurement-neutral by construction -- the old predicate is deleted and the new one reads only the continuation gain -- so nothing in this diff gates the race, and both its figures reach the log on every run.",
-      "remeasure": "Do not carry the figures above: they are one box's snapshot. At your merge base read them off the runner instead: `PYTHONPATH=tests/hastub python3 tests/features.py` emits `RESULT f21_p3_two_zone=... j_plain=... j_continuation_off=... continuation_gain=... j_seeded_half_price=...` beside the check's own verdict, and tests/run.sh prints the kernel class on the same run, so a red that coincides with a kernel-class change is readable from the log rather than by a root-cause seat. Re-measure any challenger gap on a second kernel class before calling it sub-optimality, and where that is not possible say so: this box's numpy is Accelerate-backed, so `OPENBLAS_CORETYPE` selects nothing there and the Linux rows cannot be re-taken locally -- the container lane that could was retired 2026-10-04 and dev/governance/rules/gate-scoping.md forbids re-deriving closures off Linux.",
-      "brief": "Price optimality is measured per kernel, and a shipped plan can be worse on the runner rather than in the solver. On this box the production multi-start ships a plan 0.307 SEK/day above the same solve warm-started from the half-price plan, where the Linux kernels of record measured the two within 0.0096 -- and the check's old bound, `j_plain <= j_seeded + 0.1`, was the measuring platform's own margin (+0.1000 on the container's Sandybridge, -0.2070 here) rather than a number below it, so that check was red on Accelerate only. For the D0 round: (1) record the kernel class beside every gap you report; CLAUDE.md rule 3 already states the premise -- solver floats do not reproduce across BLAS builds, so only a canonical environment can honestly record one -- and a gap from a start-placement race is a property of the runner as well as the solver. (2) A warm start from the best challenger is this dimension's own Method step 2, so this is the gap D0 is written to find and not a new technique; what is new is that its sign can depend on which basin the starts land in, which the fix's harness dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py measures and the archived finder instrument dev/audit/harnesses/k1725_blas_kernel_gap.py measured. (3) A single-kernel win is a candidate finding and not yet a sub-optimality: re-run it on a second kernel class, or state that the gap is kernel-relative. If it is real off this kernel the repair is in the multi-start's seeding, not in the check that printed it -- that check is green on the Linux kernels of record and on this box, and no bound on the race holds across both."
-    },
-    {
-      "from": "the pull request fixing R9-ROW-STALE (#2111), which makes tools/audit/seat/record_row.py's `--plan` ask whether an existing row already tells the merge it records (`row_matches_merge`) rather than only whether a row exists (`has_row`), so the record-autofix beat now rewrites a stale row it previously left alone",
-      "effect": "narrows",
-      "control": "Established by measurement with its null control at the lane's merge base 7cd5a588c, on a clean worktree of it: `--enumerate` from that tree's instrument (unchanged by the fix) and `--plan` from the fix's head. The beat's reach IS its window -- `--enumerate` reads `<last tag>..HEAD` -- so the then-last tag v6.7.17 enumerates 18 merges and plans 18 rewrites, all 18 of them stale, while the same run from v6.7.13, the window that covers the whole defect, plans 103. The 85 rows in the difference are reached by no automatic run: the tag has already moved past them and the beat always starts at the tag. The perturbation that would void it is the window itself -- a last tag at or before v6.7.13, or a beat that walked back behind its tag, makes the two counts equal -- and the other arm the two numbers separate is a plan of 0 at v6.7.13, which would say the rows were already correct rather than unreached.",
-      "remeasure": "At your own merge base, on a worktree of origin/main: `python3 -I tools/audit/seat/record_row.py --enumerate --since $(git describe --tags --abbrev=0)` then `--plan`, and read the planned-row count; repeat with `--since v6.7.13`, the earliest tag that reaches the oldest stale row. The two counts differ by exactly the rows the beat's window cannot reach. Do not carry 18 and 85: the last tag moves with every release, and both counts are functions of main's tip and of which rows were written pre-merge. A seat that reads the two counts as equal has either re-derived the window or found that it has since widened; run the wide window before concluding either.",
-      "brief": "Constraint on record upkeep, and the owed action this lane leaves behind. The record-autofix beat (`tools/audit/seat/record_row.py`, driven by the `record-autofix` job) corrects ONLY the merges its tag window covers -- `--enumerate` reads `<last tag>..HEAD`, deliberately, since re-reading the whole history on every push is the cost it refuses -- so a row that went stale BEFORE the last tag is corrected by no automatic run, however correct the merge predicate now is. The next seat to do record upkeep owes one explicit run of the correction over a window that reaches the defect: `python3 -I tools/audit/seat/record_row.py --enumerate --since v6.7.13`, then `--plan` and `--apply` with `--root` at a worktree of origin/main. Measured at 7cd5a588c that plans the 103 stale rows this lane's fix exists to correct, plus the 2 merges that carry no row at all and are written rather than rewritten, one line per file, and re-plans to 0 -- the beat's own convergence, asked for over a window wide enough to include the rows. Nothing widens the tag window on its own, so this is a precondition on the record being correct rather than a recommendation: the fix converges the record inside the window it is run over, and the rows behind the tag are corrected only when a seat asks for them."
-    },
-    {
-      "from": "the R10-RCA-NIGHTLY-PYSPY record (#2479), whose RCA is dev/audit/rca/nightly-ha-pyspy-timeout.md: the nightly-ha (stable) red is `hb:positive_control` failing when its single `py-spy dump --nonblocking` call times out at 30 s against CPython 3.14.6 / py-spy 0.4.2",
-      "effect": "narrows",
-      "control": "The RCA measures the class from CI's own job logs, not from argument: three failed nightly-ha jobs each carry two `py-spy did not run: TimeoutExpired` lines and `FAIL hb:positive_control`, and two green jobs at the same image digest read `py-spy rc=0` with `Python v3.14.6`; the null is the green pair, which shows the sample can succeed. The perturbation that would void the finding is a green job whose positive control ran with no py-spy call at all.",
-      "remeasure": "At your own merge base: read the nightly-ha job logs for the newest three reds and the newest greens and compare the `py-spy` line and the `hb:positive_control` verdict, as the RCA's section 1 does. The container lane is CI-only, so the local reproduction in the RCA is a claim to re-run there, not a measurement a seat can take on the stock box.",
-      "brief": "Constraint, not an opportunity: `check_hb_positive_control` passes on ONE racy sample. A repair must not simply retry until it succeeds (that converts a measured red into a flaky green); it must either take the sample with a method whose failure is distinguishable from a real hang, or make the check's sample deterministic. The countermeasure the RCA proposes (A) and its demonstration obligation are in dev/audit/rca/nightly-ha-pyspy-timeout.md section 5; carry the demonstration with the fix. The RCA's proposal (C) is an owner decision and is not this carry."
-    },
-    {
-      "from": "the round-10 planning pull request that added tools/plan/replan.py; its cross-check of the out-of-tree plan documents against the roster found the wave table stale",
-      "effect": "invalidates",
-      "control": "At roster blob 277cdd359193 the wave table names 10 wave-1 groups, 7 of them already done, and 17 wave-2 groups, of which DEEPLINK-HANDLERS, FREQ-DEFROST, NIGHT-FOLDS, REPLAY-LANE, SAV-REASONS and TRAIN-HOLD are in progress now. Its 146.2 h critical path comes from after-edges the roster no longer carries. Null control: the depth derived from the roster's own after-edges is acyclic and reproduces the replanner's dispatch order, so the disagreement is in the document's source, not in the derivation; the document was cut two roster edits earlier (blob 78b01864, 63 groups).",
-      "remeasure": "At your merge base run `python3 -I tools/plan/replan.py --roster-ref origin/handoff/audit-r10-roster --out /tmp/plan.json` and read its wave table. A wave table whose first row contains a done group, or whose second contains an in-progress group, is this staleness re-derived.",
-      "brief": "Constraint on the next planning seat: the wave plan is the schedule model's output, never a hand-written table. The dependency graph is the roster's after-edges, done-ness is the roster's stage, and a wave is a dispatch instant rather than a dependency depth. The out-of-tree wave table, drain note and hand-cut wave JSON are historical: they predate roster edits, cover fewer groups than the roster carries, and their critical path comes from edges that no longer exist. Re-derive with the model instead of editing the prose."
-    },
-    {
-      "from": "the round-10 planning pull request's cross-check of the hand-cut wave JSON against the roster",
-      "effect": "removes",
-      "control": "The hand-cut wave JSON names 39 groups, all of which exist; 7 are done, and 18 of the roster's open groups appear in no wave at all. Nothing reads it: no tracked file opens it, and the renderer that used to is now fed by the plan model. Null control: the model emits a wave for every open group, so the 18 uncovered groups are a property of the file, not of the roster.",
-      "remeasure": "`git grep -n 'WAVES.json' -- tools tests .github` should return nothing once this carry is the only mention; then re-run the replanner and confirm its group list covers every open roster group.",
-      "brief": "The hand-cut wave JSON is retired. It is not an input to any tool and must not be regenerated in its shape; the round's wave plan is the model's emitted plan. A group enters the plan by entering the roster, and the replanner picks it up without a second file to edit."
-    },
-    {
-      "from": "the round-10 planning pull request's cross-check of the drain note against the live board",
-      "effect": "invalidates",
-      "control": "The drain note plans 16 open pull requests in seven lettered batches; at measurement 2 were open (#2490 and #2488), and the batches it names by number have merged. Its merge-mechanism principles still hold; its PR inventory and batch schedule do not. Null control: the count is read live from the pull-request list, so the difference is the board draining, not a miscount.",
-      "remeasure": "`gh pr list -R tvofi/heatpump_optimizer --state open --json number` and compare with the drain note's batch table; every batch whose pull requests have merged is a spent schedule.",
-      "brief": "Constraint on a drain: the merge-mechanism rules in the drain note bind (batch by mechanism, recarry only inside the train, never rebase a head under review, serialise the coordinator file), but its pull-request inventory and batch schedule do not. Take what is open and in what order from the live board and the plan model; do not re-run a spent batch."
-    },
-    {
-      "from": "the round-10 planning pull request's cross-check of the roster's stored wave field against the depth its after-edges derive",
-      "effect": "invalidates",
-      "control": "The roster records a wave per group and its own comment calls that the dependency depth. At blob 277cdd359193 the stored value disagrees with the depth derived from the after-edges for 40 of the 45 open groups that store one; the other five store none. NIGHT-FOLDS stores 6 and derives 1. Null control: the derivation is acyclic and reproduces the replanner's order, so the discrepancy is in the stored field, not in the edges.",
-      "remeasure": "Run the replanner and compare each open group's level in its output with the roster's wave. Any disagreement means the roster was not re-recorded after its edges changed.",
-      "brief": "Constraint on the roster owner: the wave field must be set from the after-edges' derived depth at the next roster edit, or dropped. A reader must not take it as the schedule: the schedule is the model's wave (a dispatch instant) and the dependency depth is the model's level. Until the field is re-recorded it is stale metadata, and a plan built from it will put in-progress work in a later wave."
-    },
-    {
-      "from": "the round-10 root-cause seat for R10-RCA-ORCH-CONTINUITY (class N-silent-stop, #2557), whose countermeasure is the detector tools/audit/seat/pulse.py and whose record is dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md",
-      "effect": "narrows",
-      "control": "The class owes a class-eliminating barrier and the tree carries only a detector. pulse.py judges three consumers (opener, verdict router, state beat) by their owed input on origin, so its verdict is the same on and off the orchestrator host; but its only scheduled run is sweep step 5, inside the session it watches, so a stopped host stops the watch with it. Established by measurement over round 10: `python3 dev/audit/harnesses/pulse_replay.py --since 2026-10-15T00:00Z --until 2026-10-21T08:00Z` reads 609 samples, the opener STOPPED in 25 samples in 1 window (2026-10-16 08:45Z-14:45Z) and the state beat STOPPED in 37 samples in 5 windows, each a stop no on-host run reported. The null control: the same replay with `--opener-h 1000 --state-min 100000` reads 0 windows on both arms, so the windows are the bounds firing, not the replay. Cost test from the record's section 4: defect 3.0 h/day against an hourly off-host run at about 3.3 min/day.",
-      "remeasure": "At your own head: `python3 -I tools/audit/seat/pulse.py --self-test` (every check ok) and the replay above with its null control. Then check whether any off-host schedule runs `pulse.py` and reaches the owner on exit 1 or 2: list the account's scheduled cloud probes and `grep -n pulse.py .github/workflows/*.yml`. A `pulse.py` that appears only in the `instrument-self-tests` job and sweep step 5 means the class is still `detector`, and a silent stop of the host is still silent.",
-      "brief": "Owner's call, not a seat's: choose the barrier the record's section 6 names -- (A, recommended) an hourly scheduled cloud probe at origin/main running `pulse.py --dump` that notifies the owner on exit 1 or 2, account configuration with no tree change; or (B) an hourly CI cron running `pulse.py`, which puts pulse.py and bus.sh on the required-check enforcement surface and whose failure mail reaches only the cron line's last editor. Until one runs, `dev/audit/config/bugclasses.json` records N-silent-stop as `detector`, never `barriered`, and no seat may record it otherwise on the strength of the self-test or sweep step 5."
-    },
-    {
-      "from": "the round-10 root-cause seat for R10-RCA-ORCH-CONTINUITY (#2557), whose red-check answers had to read job logs from a cloud seat",
-      "effect": "invalidates",
-      "control": "The assumption: `bash tools/audit/seat/failure_logs.sh <pr>` prints a pull request's failing lines from any seat. It does not from a cloud seat: the script reads the head with `gh pr view --json headRefOid`, which is GraphQL, and a cloud seat's `gh` refuses GraphQL with HTTP 403, so the script exits 2 at that line and prints nothing. Measured at the #2557 head 7e312ed2e: `bash tools/audit/seat/failure_logs.sh 2557` exits 2 in 0.5 s with empty output, and `gh pr view 2557 --json headRefOid` prints `HTTP 403: GitHub GraphQL is not available from Claude Code sessions`. The null control: the REST read of the same field, `gh api repos/tvofi/heatpump_optimizer/pulls/2557 --jq .head.sha`, prints 7e312ed2e482faf04be7eb27f38d92aef2b6fae5 with exit 0 from the same seat, so the refusal is the GraphQL route, not the seat's access to the pull request.",
-      "remeasure": "From a cloud seat at your head: `bash tools/audit/seat/failure_logs.sh <an open PR>; echo $?` beside `gh api repos/tvofi/heatpump_optimizer/pulls/<that PR> --jq .head.sha`. Exit 2 with empty output while the REST read succeeds is this finding re-derived; a printed failing line means the head read has been moved off GraphQL. Separately check the job-log fetch: the REST job-log route redirects to a blob host the cloud proxy refused (403) at #2557's red-check answer, so a script fixed at the head read may still print nothing at the log read.",
-      "brief": "Constraint on any seat reading CI failures from a cloud seat: `failure_logs.sh` is inoperative there and exits 2 silently -- an exit 2 is not 'no red', it is 'not read'. Read the head with the REST pulls endpoint and the failing lines through the GitHub MCP job-log tool (.claude/workflows/web-fragments.md is the MCP mapping) until the script is fixed; a seat that maintains the script moves its head read to `gh api repos/<repo>/pulls/<n> --jq .head.sha` and re-measures the job-log route from a cloud seat before claiming it works there."
-    },
-    {
-      "from": "R10-FLY-YIELD-GUARD (#2765), the review-strength guardrail in tools/audit/seat/review_strength.py (`--guardrail`), and its round-1 fix review (review/2765), which ruled this an owner's call under R13 rather than a seat's",
-      "effect": "narrows",
-      "control": "The guardrail already trips on the live bus. With the bus fetched at 2026-10-25T00:37Z (812 verdicts, 0 outside the grammar), `python3 -I tools/audit/seat/review_strength.py --window X=2026-10-01T00:00Z..2026-10-24T10:00Z --guardrail` reads the all arm at incidence 3/30, P = 0.0166, would-trip, and the local arm at 0/20, P = 0.0014, would-trip; the same command cut at 2026-10-25T06:00Z (after the fetch, so every verdict on the bus) reads all 2/30, P = 0.0041, and local 0/20, both would-trip, with cloud 2/20, P = 0.0526, ok. The null control: the same command cut at 2026-10-20T12:00Z, before the trough, reads all 8/30 (P = 0.5282), cloud 7/20 and local 8/20, every arm ok, so the trip is the recent window and not the calibration. A trip is not a verdict on the reviewers: low incidence is also what a scarce supply of defects produces, and only a planted defect of a known class, caught or missed, separates the two. The trip is conditional on classification: widening REAL by every word the guardrail's unclassified line names at the 2026-10-24T10:00Z cut (41, `--real-extra` set to that line) lifts the all arm to 6/30, P = 0.2238, ok, and cloud to 6/20, while local stays 0/20, P = 0.0014, would-trip; the next carry in this file owns that classification.",
-      "remeasure": "At your own head, after `python3 -I tools/audit/seat/review_strength.py --fetch --window X=2026-10-01T00:00Z..<now> --guardrail`: read the three GUARDRAIL arm lines. Every figure above is a snapshot of the bus at its fetch; a later cut reads a different last 30 and last 20. Repeat the 2026-10-20T12:00Z cut as the null control: an arm that trips there too means the calibration (P0, ALPHA, N) moved, not the reviews.",
-      "brief": "Owner's call, not a seat's: whether a guardrail trip dispatches the planted-defect audit it names, and whether to adopt the threshold (P0 = 0.28, ALPHA = 0.05; the all arm trips at k <= 4 of 30, a seat-family arm at k <= 1 of 20). Until the owner rules, the guardrail stays report-only under R13: no seat turns a `would-trip` line into an exit code, a block or a dispatch, and no seat reads a trip as evidence that the reviews are weak. Building the dispatch the audit needs is R10-ORCH-DISPATCH-REG's, carried in its roster group."
-    },
-    {
-      "from": "R10-FLY-YIELD-GUARD (#2765) and its round-1 fix review (review/2765, non-blocking finding 2): the guardrail's `unclassified` line, which routes a blocked word that is neither real nor taught for classifying instead of counting it as bookkeeping",
-      "effect": "invalidates",
-      "control": "The incidence k every guardrail arm reads is a lower bound while the unclassified line is non-empty: at the 2026-10-24T10:00Z cut it names 41 words, several of which read as engineering catches (mutant-survived, unpinned-site, mutation-unpinned, null-control-unpinned, figure-wrong, body-false, spec-unmet, closures-under-approximated, docs-code-mismatch). Measured with the bus fetched at 2026-10-25T00:37Z: `python3 -I tools/audit/seat/review_strength.py --window X=2026-10-01T00:00Z..2026-10-24T10:00Z --guardrail --real-extra <those nine>` leaves every arm's line unchanged (all 3/30, P = 0.0166, would-trip; cloud 3/20; local 0/20), as the round-1 review's sensitivity run found, so the trip does not rest on those nine. The perturbation that shows the widening is read: `--real-extra` set to all 41 words lifts the all arm to 6/30, P = 0.2238, ok, and cloud to 6/20, so the all arm's trip does rest on the classification of the other 32. The line grows: cut at 2026-10-25T06:00Z it names 51 words.",
-      "remeasure": "At your own head: `python3 -I tools/audit/seat/review_strength.py --fetch --window X=2026-10-01T00:00Z..<now> --guardrail` and read the last line; then the same command with `--real-extra` set to every word you would classify real, and compare the arm lines. An arm whose line moves under the widening is a figure resting on unclassified words, and P0 (24/85 at yield-probe.md's post-cloud window) must be re-derived under the same widening before the two are compared.",
-      "brief": "Constraint on the D13 seat of a later audit round, which owns REAL's list (REAL_CATCH and REAL_EXTRA in tools/audit/seat/review_strength.py): classify every word the guardrail's unclassified line names as real or bookkeeping, with the verdict that used it as evidence, and re-derive P0 under the new list in the same pull request. Widening REAL without re-deriving P0 moves k and its baseline apart and makes the threshold meaningless; leaving the line unclassified keeps every arm's k a lower bound, which no seat may report as an exact incidence."
-    }
-  ]
+ "_comment": [
+  "Carry destination for the round-5 governance/record findings (#1301, R5-D11-02",
+  "and #1303, R5-D13-01). Round 5 filed 48 findings as #1293-#1340 and no umbrella",
+  "issue of its own, so the destination is #201 -- the audit programme's standing",
+  "tracking issue, the one that received round 5's own round-end comment -- and no",
+  "roster group in this tree claims it. Shape and required fields:",
+  ".claude/rules/finding-propagation.md. Linted by",
+  "tools/policy/brief_lint.mjs (the `briefs` CI job).",
+  "A later entry carries to the D0 dimension of a later audit round, from #2114's",
+  "re-key of the R9-F2.1 P3 storage check. The D0 method brief",
+  "(dev/governance/dimensions/D0.md) is policy, so it was not edited: this file is",
+  "the in-tree brief of a stage with no live roster group."
+ ],
+ "issue": 201,
+ "stage": "any later seat that stamps a release (tools/release/stamp.py, the deploy-key tag push of dev/governance/decisions/0009-agent-identities-for-author-and-approver.md step 5); the D13 dimension of a later audit round (dev/governance/dimensions/D13.md is its method, dev/audit/rounds/round5/D13/seat-a/dora_cfr.py its harness); the D11 dimension of a later audit round, whose method dev/governance/dimensions/D11.md is and whose subject is .github/workflows/governance.yml; and the D0 dimension of a later audit round, whose method dev/governance/dimensions/D0.md is and whose capture harness is tests/optimality.py; and any later seat that repairs the nightly-ha positive control in tests/nightly_ha.py (the check is `check_hb_positive_control`, and the sites the RCA names are the py-spy call and the heartbeat pin); the next planning seat (the schedule model at tools/plan/replan.py and the page it feeds); and the roster owner's next re-record of the roster's wave field; the owner's decision on the off-host liveness barrier for audit class N-silent-stop (dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md section 6, the seat that creates the schedule); and any later seat that maintains tools/audit/seat/failure_logs.sh or runs it from a cloud seat; the owner's decision whether to run the planted-defect audit that the review-strength guardrail names when it trips (tools/audit/seat/review_strength.py --guardrail, report-only under owner ruling R13); and the next seat that moves the typing ruler (tests/typing_ruler.py, its pair in tests/typing_budgets.json) off homeassistant-stubs; and the owner's next paste of tools/audit/seat/cloud-setup.sh into the environment's setup script",
+ "carries": [
+  {
+   "from": "the round-5 D11-02 finding (#1301), whose fix is rule \"rows\" in tools/release/stamp.py -- the stamp now re-applies `record`'s own predicate to the window it is about to close",
+   "effect": "narrows",
+   "control": "The window `<last v* tag>..origin/main` is the window `record` reads, and the tag push is main-protect's only bypass, so one stamp can carry every rowless merge behind the new tag out of every future window at once. Established by measurement, not argument: the finding's harness (dev/audit/rounds/round5/D11/seat-b/corpus_churn.py) reads the same counts at origin/main before this fix and at this fix's head, and the number that matters is the INSTRUMENT's, not the harness's -- `python3 tests/delivery_status.py --check` exits 0 over a window whose merges are minutes old, because at stamp time every merge is PENDING and `--check` refuses only OVERDUE and UNCHECKED; the new `--require-rows` exits 1 over the same ledger and names the rowless merges. The perturbation that would have voided it: a row added for one window merge moves the count by exactly one. The fix is measurement-neutral by construction -- corpus_churn.py prints byte-identical RESULT lines at the pre-fix and post-fix heads, which is the null control separating `--require-rows` (reading the ledger under a stricter bar) from a change to the ledger itself.",
+   "remeasure": "At your own merge base: `python3 tests/delivery_status.py --check` and `python3 tests/delivery_status.py --require-rows` over the same tree, then `python3 dev/audit/rounds/round5/D11/seat-b/corpus_churn.py`. They agree on every verdict but PENDING, and that single disagreement is the whole finding; a later round that reads them as the same predicate has re-derived the escape.",
+   "brief": "Stamp-time precondition, not an opportunity: `tools/release/stamp.py` REFUSES to stamp when any merged pull request in the window it would close has no disposition row, and the only override is the explicit `--allow-rowless` flag, which prints the instrument's own output before proceeding. The rows it demands are the ones `record` demands, on the same two surfaces tests/delivery_status.py's DISPOSITION_FILES names. A stamp over a rowless window is no longer an ordinary release step: it is a knowingly deferred batch, and it is recorded as one. The re-application lives in the stamp's module docstring as rule \"rows\", so a seat that reads the contract rather than the flag sees it before it runs."
+  },
+  {
+   "from": "the round-5 D13-01 finding (#1303), whose fix makes the CFR exclusion list a registered in-tree artifact that the instrument reads from the repository root, failing closed when it is absent",
+   "effect": "narrows",
+   "control": "The finding: the round-5 harness opened `cfr_exclusions.json` beside itself, so `cfr_excluded` came from a file the tree did not carry -- and dev/governance/dimensions/D13.md asks for `a JSON file beside policy_budgets.json that your first round creates with a reason per job`. Established by measurement at both ends in a clone at the round's baseline: with the sibling list and the tree holding no list, the harness prints cfr_excluded=0.0; with the artifact registered at dev/governance/config/cfr_exclusions.json and the sibling removed, it prints the identical eight-merge numbers, which is the null control that shows the re-point moved the citation and not the metric. The perturbation the brief names still moves the number by exactly the excluded job's head count: `EXCLUSION_DROP=record` takes cfr_excluded 0.0 -> 1.0, record's eight of eight heads. And the fail-closed arm: with the artifact removed the harness raises, naming the registered path, rather than silently excluding nobody -- which is the always-green shape a metric `retaken minus the by-design reds` degrades into.",
+   "remeasure": "At your own merge base: run the D13 instrument (dev/audit/rounds/round5/D13/seat-a/dora_cfr.py) with its fixtures, then again with EXCLUSION_DROP naming the excluded job. If the second run's cfr_excluded does not move by that job's head count, the list is not being read. Then `python3 -c \"import json;print(sorted(json.load(open('dev/governance/config/cfr_exclusions.json'))['excluded_jobs']))\"` -- the list is a narrowing of the metric, so a round that GROWS it is making a deliberate edit, and an unjustified entry hides a real change failure rather than a by-design one.",
+   "brief": "Constraint on how the exclusion list is carried: it is ONE registered artifact at `dev/governance/config/cfr_exclusions.json`, a top-level object with an `excluded_jobs` map keyed by check-run name beside a `_comment`, in the shape dev/governance/config/policy_budgets.json takes. The instrument resolves it against the REPOSITORY, not against the seat, and raises when the map is missing or empty -- so a later round does not create a second list under a name of its choosing, and does not publish an un-excluded rate under the excluded rate's name. Each entry carries the reason and the citation it rests on; the one entry at the round-5 values is `record`, and the reason a later round must re-check rather than assume is that the red is by design only while the batch interval holds."
+  },
+  {
+   "from": "the round-6 D11-02 finding (#1403), whose fix adds the `Restore the check source from the base commit` step to the `policy-docs` job of .github/workflows/governance.yml and the entry-point exit-status arm to tools/policy/policy_lint_mutants.mjs",
+   "effect": "narrows",
+   "control": "The assumption before this fix was that a required context which grades the policy corpus runs the corpus's own checker. It did not: `policy-docs` checked out no `ref:`, so the program grading the corpus was the pull request's copy of it. Established by measurement at both ends in a worktree of the fix's head whose only differences were a corpus defect (one line of CLAUDE.md citing a file the tree does not carry, line count unchanged) and a one-line mutation of the checker's exit status -- `process.exit(errors > 0 || rc ? 1 : 0)` gated on `process.env.POLICY_LINT_TEMPLATE`, which is the shape that evades the gate's own witness. Before the fix, that tree's `node tools/policy/policy_lint.mjs` exited 0 while printing `ERROR [citations] CLAUDE.md:20` and `ERROR [index]`, its stdout byte-identical to the unmutated checker's, and the base's mutation lane exited 0 as well; the acceptance's template arms in tests/entities.py, which empty the checker and demand a red, returned 1 and 0. After the fix, on the same tree: the lane exits 1 naming the exit status, and the required context's own command exits 1 naming the corpus defect once the pin has run, the pin reporting one file differing from the pull request's copy. The null control runs both ways: on the healthy tree at the same head the pin restores nothing and the lint stays at 0, and with the pinned ref equal to the head -- the push-to-main shape, where the step reads `github.sha` -- the checkout is a no-op over a clean tree.",
+   "remeasure": "At your own merge base: apply the same two perturbations (a corpus defect that does not change a line count, and an exit status that does not track the findings), then run the job's own commands in this order -- `node tools/policy/policy_lint_mutants.mjs` must exit nonzero naming the exit status; `git checkout <base> -- 'tools/policy/*.mjs' 'tools/policy/*.py' 'tools/policy/vendor'` must print a count you can read; `node tools/policy/policy_lint.mjs` must exit 1 with your corpus defect named. Require both ends: on the healthy tree each of those is 0, and a pin whose checkout silently matched nothing would leave the mutated checker in place and print a count of zero. Then check the three shapes the pin does not cover, each a candidate finding rather than a refutation: a criteria edit, a checker added as a module beside the pinned programs, and a program edited together with the self-test lane that drives it.",
+   "brief": "Constraint on any seat adding a corpus check or moving a step in the `policy-docs` job of .github/workflows/governance.yml. (1) A corpus check is a function inside tools/policy/policy_lint.mjs, named in that file's own lists of check names, never a module beside it: the new step restores the `.mjs` and `.py` programs under tools/policy/ plus tools/policy/vendor from the base commit, and a file the base does not carry cannot be restored, so a checker added as its own module stays the pull request's own and the corpus is graded by the copy under test -- the defect of #1403 in its original shape. (2) The job now has two halves and that step is the boundary. The five steps above it -- tools/policy/policy_lint_mutants.mjs, the `--self-test` runs of tools/policy/fragments_sync.mjs and tools/policy/record-predicate/sweep.mjs, the `--hooks` run of tools/policy/policy_lint.mjs and the `self-test` run of tools/pr/gh_comment.py -- drive the PULL REQUEST's programs on purpose, because a self-test that ran the base's copy would report on neither; every step below it grades the pull request's data with the base's programs. Moving a step across that boundary silently changes which side of it a check is on. (3) The pin covers programs, not criteria: dev/governance/config/policy_budgets.json, dev/governance/config/policy_known_bad.json, dev/governance/config/cfr_exclusions.json and the sync surface tools/policy/fragments_sync.mjs checks against .claude/workflows/web-fragments.md stay the pull request's, because a fixture's expected outcome has to be the data under test. Those three places -- a criteria file, a checker outside the restored paths, and the self-test block above the step -- are where the pull request's own copy is still what runs, and that is where a later round hunting this class of defect should look."
+  },
+  {
+   "from": "the pull request fixing the round-6 D13-03 finding (#1407), which makes the round-4 DORA instrument (dev/audit/rounds/round4/D11/dora_keys.py, `cfr_keyings`) report the change-failure rate at BOTH keyings -- at the merge commit, where `dev/governance/config/cfr_exclusions.json` acts, and at the pull-request head, where a merge is gated -- and pins the pair in tests/entities.py",
+   "effect": "narrows",
+   "control": "The finding: the exclusion list's single entry `record` fails at 58 of the 67 merge commits in the window v6.6.0..e336cc2c and is SKIPPED at every one of the 67 pull-request heads, because its workflow gates the job to the non-pull_request event. So excluding it moves the merge-keyed rate 0.925 -> 0.09 and leaves the head-keyed rate at 0.134 -- the rate at the surface a merge is actually gated on, unchanged. Established by measurement at both ends: the instrument prints the un-excluded rate beside the excluded one from the same call over the same maps, so the exclusion's own delta is visible on each keying, and it is 56 merges at the merge keying and zero at the head keying; the round-6 finder harness measured the same figures, so the tracked instrument reproduces them rather than restating them. The perturbation that would have voided it: the names failing at the HEAD are `nightly-status` (7 of the 67) and `delivery-status` (2 of the 67), so one entry added for either moves the head keying and the pair stops separating the two surfaces. The key-set null control tests/entities.py already holds -- `excluded_jobs` is exactly the set holding `record`, with the gate jobs absent -- is what refuses that entry.",
+   "remeasure": "At your own merge base, run `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D11/dora_keys.py` and read `cfr_merge_keyed` beside `cfr_head_keyed`; both are RESULT lines the instrument prints, and `cfr_exclusions` is printed with them so the list a rate came from is on the same screen. Or run dev/audit/rounds/round5/D13/seat-a/dora_cfr.py with `EXCLUSION_DROP=record`, which moves the merge-keyed rate by that job's head count. A rate reported at one keying only, or an entry added for a name that fails at the head, is this finding re-derived. The instrument pins its window (`D13_SINCE` / `D13_HEAD`), so a re-take names its own baseline instead of tracking a moving main.",
+   "brief": "Constraint on every change-failure rate a later round reports: the rate is TWO numbers -- the merge-keyed rate and the pull-request-head-keyed rate -- printed together and never one alone, because `dev/governance/config/cfr_exclusions.json` narrows only the merge keying while a merge is gated on the head keying. The artifact's `_keying` field states that rule for whoever edits the list, and dev/governance/dimensions/D13.md's DORA item asks for the list without naming a keying, which is how the single-number report arose. A check-run name that fails at the pull-request head is a real gate red: it must NOT be added to the list, however much it costs the merge keying, and a report that names such a name as excluded is the escape this carry closes."
+  },
+  {
+   "from": "the pull request fixing the round-7 D13-06 finding (#1476), which makes the same round-4 DORA instrument report the rate PER CHECK-RUN NAME at both keyings (dev/audit/rounds/round4/D11/dora_keys.py, `cfr_by_name`), and records `mutation` in dev/governance/config/cfr_exclusions.json's new `not_excluded` map as a name deliberately NOT on the list",
+   "effect": "narrows",
+   "control": "The finding: the carry above settles that the rate is two numbers, but two aggregates still do not say WHICH name separates them, and over the round-7 window the whole separation is one name. `mutation` fails 4 of the window's 31 merge commits and 0 of its 31 pull-request heads, so it is the entire 0.129 between the merge-keyed rate (0.226) and the head-keyed one (0.129) -- invisible in either published figure, and the reason a reader cannot tell a merge-surface red from a head-surface one. Established by measurement at both ends: `cfr_by_name` prints the pair `[merge, head]` for every name failing at EITHER surface, over the same maps `cfr_keyings` aggregates, so the four names other than `mutation` that fail at the merge keying print [0.032, 0.0] apiece and `delivery-status` prints the mirror [0.0, 0.129]. The perturbation that would have voided it: adding one name to the exclusion list IN MEMORY moves the merge-keyed rate by exactly that name's count and leaves the head-keyed rate where it was -- `mutation` 0.226 -> 0.097 while the head keying stays 0.129 -- which is the arithmetic statement that it is a merge-surface red. The null control is the key set: a name failing at neither surface (`record`, 0 of 31 here) is ABSENT from the map rather than a zero row, so the map's keys are compared as a set and never as a total.",
+   "remeasure": "At your own merge base, run `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D11/dora_keys.py` and read the `cfr_by_name` RESULT beside `cfr_merge_keyed` / `cfr_head_keyed`; the per-name pairs must sum to the aggregate keyings over the same window, and any name whose pair is nonzero at one surface only is a candidate the list owner must judge. Then `python3 -c \"import json;print(sorted(json.load(open('dev/governance/config/cfr_exclusions.json'))['excluded_jobs']))\"` -- it must still be exactly `['record']`. A round that reports a single per-name number, or that finds `mutation` (or `nightly-status`, or `delivery-status`) added to `excluded_jobs`, has re-derived this finding or the one above it.",
+   "brief": "Constraint on how a later round reports the change-failure rate: per-name at both keyings, BESIDE the two aggregates and never instead of them. Two aggregate rates hide which name separates the surfaces, and here the whole difference is one name -- and the instrument cannot decide whether that name's merge-surface red is a change failure at all. `mutation` fails 4 of the window's 31 merge commits (two pairs merged 4-5 s apart, i.e. two batch merges) where neither pull request's own head failed it, because the lane's inventory is the TREE (`tests/mutation_table.py`'s `unpinned_sites`) and on a push to `main` its scoping base IS `HEAD`, so a batch's merged tree can red it where no head did. Nothing in the finding says the red is spurious; it says whether a merge-surface red on a batch-merged tree is a change failure is the exclusion list owner's judgement, and it is recorded rather than made: `mutation` stays off the list, and dev/governance/config/cfr_exclusions.json's `not_excluded` map carries the reason and the citation so the next reader meets the answer in the artifact rather than in a merged pull request's comments. Adding it to `excluded_jobs` is the same deliberate edit as growing the list, and owes the same justification."
+  },
+  {
+   "from": "the seam the R7-INSTR-01 fix (#1477) returned when tools/audit/prepare_baseline.sh was run as its own generator control: at this tree's merge base the script REFUSES to prepare a baseline for every round number except 4, so the documented way to prepare a round is inoperative for the next round",
+   "effect": "removes",
+   "control": "The script's `finders_can_start` step refuses when a file a `tests/*.py` script hands to `Path(...)` or `open()` exists in the source checkout but not in the tree it just prepared, and `strip_earlier_rounds` deletes every `tools/audit/round*` except the round being prepared. Two files under `tools/audit/round4/` are read that way by tests/entities.py -- `Path(\"dev/audit/rounds/round4/D6/claims.json\")` and `Path(\"tools/audit/round4/D11/governance_cost.py\")`, added 2026-09-19 (a7d97d20) and 2026-09-20 (cd4b1927) -- while the refusal itself dates from round 4 (c68259b8, 2026-09-12). Each was harmless alone; together, any preparation whose round is not 4 drops files the HEAD tests open, and the script refuses after creating the worktrees and before writing any BASELINE.md. Established by measurement, not argument: in a throwaway clone of this tree's merge base, `PYTHON=<interp> bash tools/audit/prepare_baseline.sh 98 6e2a0f2a` and the same script with this fix applied at round 99 both print `refusing: the preparation dropped file(s) a tests/*.py script opens unguarded: tools/audit/round4/D11/governance_cost.py dev/audit/rounds/round4/D6/claims.json`, while the SAME script at round 4 completes -- `RESULT finders_can_start=ok` for the export and all five worktrees -- which is the control separating the round-from-4 strip from the environment. The rounds since have been prepared by hand (round 6's dev/audit/rounds/round6/BASELINE.md is hand-written and round 7's D13 was dispatched by hand), so this is a latent cost rather than a stopped programme.",
+   "remeasure": "At your own merge base, in a scratch clone so the worktrees and the export land outside this repository: `git clone --depth 1 --no-single-branch file://<this checkout> /tmp/pb && cd /tmp/pb && PYTHON=$(command -v python3) bash tools/audit/prepare_baseline.sh 98 $(git rev-parse HEAD)`. A refusal naming `tools/audit/round4/...` is this seam re-derived; then run it at round 4 and require it to complete, which is what says the refusal is about the strip and not about your clone. Two questions are open and belong to whoever holds the audit wall rather than to a fixer: whether the strip should exempt a file a HEAD test reads unguarded, or whether those two tests should read the register through a path that survives a round's preparation. Do not settle it by widening `finders_can_start` -- the refusal is the half that catches a preparation dropping a file by accident, and it is the only guard there.",
+   "brief": "Constraint on preparing the NEXT round's baseline: running `tools/audit/prepare_baseline.sh <round> <sha>` for any round other than 4 refuses at this tree, after creating the worktrees and before writing any BASELINE.md, and the refusal is correct about its own predicate -- the prepared tree really does lack two files tests/entities.py opens unguarded, so a finder in it would die at import before its first measurement. Prepare the round deliberately instead of around the script: either carry the two `tools/audit/round4/` files into the export and the worktrees (the wall's rule is that earlier rounds must not STEER a finder, and a file a test reads is not steering), or re-point those two tests at a path that survives. Then take what #1477 fixed as given -- D13 is a dimension of the schedule in .claude/workflows/audit-find.js and needs a worktree rather than the export -- and keep the two lists it shares with this file's ISOLATED_DIMS in step, which tools/policy/check-wave-script.mjs now derives and refuses to see drift."
+  },
+  {
+   "from": "the v6.7.8 stamp hotfix (the pull request repairing main's red entities check after the stamp commit), whose fix restores the may-drift entry R9-F2.3 (#1723) suspended for its wood_coil claim -- which the stamp deleted without restoring -- and moves the R8-P3 coverage ruling into tests/env_drift.py's may_drift_coverage_error, executed by --claims-only",
+   "effect": "narrows",
+   "control": "Established by measurement at both ends. At the stamp head, tests/entities.py's own check failed with uncovered ['wood_coil'] while the stamp's claims self-check had printed 'claims hygiene: HEAD^1 ok' -- the stamp's self-check DOES exec `tests/env_drift.py --claims-only HEAD^1` on the post-stamp tree, but --claims-only carried the scope rule (entries within MAY_DRIFT_ALLOWED, no name both claimed and may-drift) and not the coverage rule (every allowed name is may-drift or claimed for THIS VERSION), so a claim deleted by the stamp left its suspended entry covered by nothing. With the fix, the same --claims-only invocation on the broken tree refuses with MAY-DRIFT UNCOVERED naming wood_coil and exits 1, which publish_stamp treats as a refusal: undo_local_stamp discards the stamp commit before anything is pushed. The perturbation that would have voided it: re-suspending the entry at the fix head reproduces the refusal, restoring it returns exit 0. The null control: on the healthy tree the added rule changes no verdict -- claims hygiene stays ok -- because a tree whose may-drift list is complete satisfies the coverage rule by construction.",
+   "remeasure": "At your own merge base: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only <ref>` on a tree whose claim file suspends a may-drift entry for a claim that is absent or stamped for another VERSION must exit 1 with MAY-DRIFT UNCOVERED naming that entry; restoring the entry verbatim (or carrying the claim for the tree's own VERSION) must exit 0. Before running tools/release/stamp.py over a main whose claim file carries a suspension note, restore every suspended entry verbatim -- the note's own text carries the line -- or the stamp's self-check will discard the commit after making it.",
+   "brief": "Stamp-time precondition, not an opportunity: a stamp that empties the claim list owes every suspended may-drift entry back, verbatim, because a name may leave the may-drift list only while THIS release claims it (the R8-P3 ruling, option (a)) and the claim the suspension was made for expires with the stamp. The obligation is enforced, not advisory -- tools/release/stamp.py's claims self-check execs `tests/env_drift.py --claims-only HEAD^1` on the post-stamp tree and undo_local_stamp discards the commit on refusal -- so a stamping seat that misses the restore loses only the stamp run, never main's green. A suspension note in the claim file is a promise to a human; the coverage rule is the same promise made to the instrument, and the second is the one that refuses."
+  },
+  {
+   "from": "PR #1879 (tools: programme instruments live in the tree, and a check refuses temp paths), whose tools/audit/seat/tmp_paths.py runs in governance.yml's non-grading instrument-self-tests job rather than in a required one",
+   "effect": "narrows",
+   "control": "Established by measurement at both ends. With tools/audit/seat/tmp_paths.py run in the wave-script job (a grading, required job) and tools/audit/seat/ unowned (tvofi, 2026-10-03: audit instruments are not code-owned), `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` refused it as UNCOVERED (uncovered_files=1); moved to instrument-self-tests, whose env sets HPO_JOB_GRADES: nothing, the same command reports uncovered_files=0 and tags it NO-PR-JOB. The null control: tools/audit/seat/merge_train.py, run in that same job from the start, was never reported uncovered. tmp_paths.py --check itself refuses 14 lines at origin/main 20f597c6 and 0 at the PR head, so the check works; only its gate status is weaker than a required grader's.",
+   "remeasure": "At your own merge base: `git cat-file -e <base>:tools/audit/seat/tmp_paths.py` must succeed before any job can restore it from the base; then add it to a pinned job's `git checkout \"$PINNED\" --` list in .github/workflows/governance.yml, declare it in tools/policy/field_coverage.mjs's DECLARED map (that program is pinned, so the declaration must already be on main when the pin lands), and run `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (must report it PINNED, uncovered_files=0), `node tools/policy/field_coverage.mjs` (FIELD COVERAGE ok) and `bash tools/pr/prepr.sh` (its pinned-graders step names a local path for it).",
+   "brief": "Owed follow-up, two pull requests after #1879 merges: make tools/audit/seat/tmp_paths.py a pinned grader in a required governance.yml job, so a temp or machine path in a tracked script, workflow or decision record turns a required context red rather than the non-required instrument-self-tests. Step one declares it in tools/policy/field_coverage.mjs's DECLARED map (pinned, so it must land first); step two restores it from the base in a required job and runs `--check` there. It must not be made code-owned to get there: the owner ruled that audit instruments carry no owner, and decision 0013 stands unamended. Until both land, a red instrument-self-tests at a head is still a red check pr-contract makes the body answer, and tools/audit/seat/merge_train.py stops on it because it is not on the train's ignore list."
+  },
+  {
+   "from": "RCA stale-pins (PR #2073, dev/audit/rca/R9-RCA-stale-pins.md): the frozen fixture tools/policy/fixtures/wave-1b-931dffe.json, pinned by REQUIRED_931DFFE's `wood_share:1152` entry in tools/policy/brief_lint.mjs, which requires a path:line (anchored) ERROR naming thermal_model.py:1152 and so depends on the production file's line layout",
+   "effect": "narrows",
+   "control": "Established by measurement at both ends, with its null control, on origin/main 47b083b0. Unmodified tree: `node tools/policy/brief_lint.mjs` rc 0, `FIXTURE ok: 14 error(s) pin the 931dffe acceptance (9 required)`. Perturbation: prepend 14 comment lines to custom_components/heatpump_optimizer/thermal_model.py (a `return` at line 1138 moves to 1152, inside the +-1 window checkPathLine reads) -> rc 1, `FIXTURE VACUOUS: 931dffe acceptance pins missing`. Prepending 1 line instead leaves it rc 0, so the fixture is not simply shift-sensitive: it needs the cited line NOT to sit near a `return`, which any unrelated production edit above it can change. #2066's new property in thermal_model.py did exactly this.",
+   "remeasure": "Do not trust 1138/1152: they are measured at 47b083b0 and a later stage is judged against its own merge base. At your merge base, list `grep -n '\\breturn\\b' custom_components/heatpump_optimizer/thermal_model.py` near line 1152, prepend (1152 - n) comment lines for the nearest `return` at line n above it, run `node tools/policy/brief_lint.mjs`, and confirm whether it still goes VACUOUS; restore the file afterwards.",
+   "brief": "The D11 round, or whichever seat next edits tools/policy/brief_lint.mjs: stop REQUIRED_931DFFE's `wood_share:1152` pin depending on the live line layout of custom_components/heatpump_optimizer/thermal_model.py, so an unrelated production edit cannot turn `briefs` red. Candidate repairs, to be chosen with the control: point the fixture's citation at a file the fixture owns, or have the pin assert the lookup's refusal reason rather than the production line. Demonstrate it by rerunning the 14-line prepend above: before the repair rc 1, after it rc 0, and a deliberately wrong citation must still produce the ERROR. Do not make prepr.sh run brief_lint on every production diff instead; it took 1 m 45 s under load on 47b083b0 for this one fixture."
+  },
+  {
+   "from": "RCA stale-pins review (PR #2073, round 1, reviewer observation on #2070): CI never runs a round instrument's `--perturb` arm, so an instrument under dev/audit/rounds/ that a production move breaks turns nothing red",
+   "effect": "narrows",
+   "control": "Established at origin/main 47b083b0 by search, with a null control, not by reproducing #2070's breakage. `git grep -n -e '--perturb' -- .github` returns no line, while `git grep -n -e '--perturb' -- dev/audit | wc -l` returns 1704, so no workflow step invokes a perturbation arm. The null control is that CI does run some round instruments: `.github/workflows/governance.yml` line 411 runs `codeowners_gap.py --self-test`, so the absence above is specific to `--perturb`, not to round instruments in general. Not measured here: which round instruments broke on #2070's move of `_on_off_service`.",
+   "remeasure": "At your merge base rerun both `git grep` commands, and list what `--perturb` arms exist with `git grep -l -e '--perturb' -- 'dev/audit/rounds/*.py'`. A workflow that has since added a perturb runner makes the first command non-empty, and this carry is void for the arms it runs.",
+   "brief": "The D11 or D13 round: decide whether CI should run a round's `--perturb` arms, or whether instruments that CI never exercises are expected to rot, and record the decision. This is a different class from the stale-pin RCA (a local predictor porting half of a CI refusal): here no detector exists at any cost. Apply the cost test first, since 1704 mentions across dev/audit means a blanket run is likely unaffordable; a per-round opt-in list is the candidate form. Do not fold it into prepr.sh's step 6d."
+  },
+  {
+   "from": "the pull request for R9-RC-BLAS-KERNEL-RED (#2114), which re-keyed the R9-F2.1 P3 storage check in tests/features.py off a race whose verdict is a property of the runner's BLAS kernel and onto the continuation's own gain, leaving that race measured and printed but not gating",
+   "effect": "invalidates",
+   "control": "Established by measurement with its null control, and the check now prints both sides of the race it no longer gates. On this box (Apple M1, numpy 2.4.6 Accelerate-backed) one run reads `j_plain=110.436632` for the shipped multi-start plan against `j_seeded_half_price=110.129674` for the same solve warm-started from the half-price plan -- 0.307 on the table -- while the Linux kernels of record measured the two within 0.0096 (+0.1000 Sandybridge, +0.0905 Haswell, +0.0904 Nehalem; cited from PR #1726's null control and this check's own log, not re-taken here). The null control is the kernel axis: the same race reads about zero on every kernel of record, which is what separates a kernel-selected basin from a sub-optimal solver. The perturbation that would void the finding is a second kernel class where production's multi-start lands in the half-price plan's basin. The re-key is measurement-neutral by construction -- the old predicate is deleted and the new one reads only the continuation gain -- so nothing in this diff gates the race, and both its figures reach the log on every run.",
+   "remeasure": "Do not carry the figures above: they are one box's snapshot. At your merge base read them off the runner instead: `PYTHONPATH=tests/hastub python3 tests/features.py` emits `RESULT f21_p3_two_zone=... j_plain=... j_continuation_off=... continuation_gain=... j_seeded_half_price=...` beside the check's own verdict, and tests/run.sh prints the kernel class on the same run, so a red that coincides with a kernel-class change is readable from the log rather than by a root-cause seat. Re-measure any challenger gap on a second kernel class before calling it sub-optimality, and where that is not possible say so: this box's numpy is Accelerate-backed, so `OPENBLAS_CORETYPE` selects nothing there and the Linux rows cannot be re-taken locally -- the container lane that could was retired 2026-10-04 and dev/governance/rules/gate-scoping.md forbids re-deriving closures off Linux.",
+   "brief": "Price optimality is measured per kernel, and a shipped plan can be worse on the runner rather than in the solver. On this box the production multi-start ships a plan 0.307 SEK/day above the same solve warm-started from the half-price plan, where the Linux kernels of record measured the two within 0.0096 -- and the check's old bound, `j_plain <= j_seeded + 0.1`, was the measuring platform's own margin (+0.1000 on the container's Sandybridge, -0.2070 here) rather than a number below it, so that check was red on Accelerate only. For the D0 round: (1) record the kernel class beside every gap you report; CLAUDE.md rule 3 already states the premise -- solver floats do not reproduce across BLAS builds, so only a canonical environment can honestly record one -- and a gap from a start-placement race is a property of the runner as well as the solver. (2) A warm start from the best challenger is this dimension's own Method step 2, so this is the gap D0 is written to find and not a new technique; what is new is that its sign can depend on which basin the starts land in, which the fix's harness dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py measures and the archived finder instrument dev/audit/harnesses/k1725_blas_kernel_gap.py measured. (3) A single-kernel win is a candidate finding and not yet a sub-optimality: re-run it on a second kernel class, or state that the gap is kernel-relative. If it is real off this kernel the repair is in the multi-start's seeding, not in the check that printed it -- that check is green on the Linux kernels of record and on this box, and no bound on the race holds across both."
+  },
+  {
+   "from": "the pull request fixing R9-ROW-STALE (#2111), which makes tools/audit/seat/record_row.py's `--plan` ask whether an existing row already tells the merge it records (`row_matches_merge`) rather than only whether a row exists (`has_row`), so the record-autofix beat now rewrites a stale row it previously left alone",
+   "effect": "narrows",
+   "control": "Established by measurement with its null control at the lane's merge base 7cd5a588c, on a clean worktree of it: `--enumerate` from that tree's instrument (unchanged by the fix) and `--plan` from the fix's head. The beat's reach IS its window -- `--enumerate` reads `<last tag>..HEAD` -- so the then-last tag v6.7.17 enumerates 18 merges and plans 18 rewrites, all 18 of them stale, while the same run from v6.7.13, the window that covers the whole defect, plans 103. The 85 rows in the difference are reached by no automatic run: the tag has already moved past them and the beat always starts at the tag. The perturbation that would void it is the window itself -- a last tag at or before v6.7.13, or a beat that walked back behind its tag, makes the two counts equal -- and the other arm the two numbers separate is a plan of 0 at v6.7.13, which would say the rows were already correct rather than unreached.",
+   "remeasure": "At your own merge base, on a worktree of origin/main: `python3 -I tools/audit/seat/record_row.py --enumerate --since $(git describe --tags --abbrev=0)` then `--plan`, and read the planned-row count; repeat with `--since v6.7.13`, the earliest tag that reaches the oldest stale row. The two counts differ by exactly the rows the beat's window cannot reach. Do not carry 18 and 85: the last tag moves with every release, and both counts are functions of main's tip and of which rows were written pre-merge. A seat that reads the two counts as equal has either re-derived the window or found that it has since widened; run the wide window before concluding either.",
+   "brief": "Constraint on record upkeep, and the owed action this lane leaves behind. The record-autofix beat (`tools/audit/seat/record_row.py`, driven by the `record-autofix` job) corrects ONLY the merges its tag window covers -- `--enumerate` reads `<last tag>..HEAD`, deliberately, since re-reading the whole history on every push is the cost it refuses -- so a row that went stale BEFORE the last tag is corrected by no automatic run, however correct the merge predicate now is. The next seat to do record upkeep owes one explicit run of the correction over a window that reaches the defect: `python3 -I tools/audit/seat/record_row.py --enumerate --since v6.7.13`, then `--plan` and `--apply` with `--root` at a worktree of origin/main. Measured at 7cd5a588c that plans the 103 stale rows this lane's fix exists to correct, plus the 2 merges that carry no row at all and are written rather than rewritten, one line per file, and re-plans to 0 -- the beat's own convergence, asked for over a window wide enough to include the rows. Nothing widens the tag window on its own, so this is a precondition on the record being correct rather than a recommendation: the fix converges the record inside the window it is run over, and the rows behind the tag are corrected only when a seat asks for them."
+  },
+  {
+   "from": "the R10-RCA-NIGHTLY-PYSPY record (#2479), whose RCA is dev/audit/rca/nightly-ha-pyspy-timeout.md: the nightly-ha (stable) red is `hb:positive_control` failing when its single `py-spy dump --nonblocking` call times out at 30 s against CPython 3.14.6 / py-spy 0.4.2",
+   "effect": "narrows",
+   "control": "The RCA measures the class from CI's own job logs, not from argument: three failed nightly-ha jobs each carry two `py-spy did not run: TimeoutExpired` lines and `FAIL hb:positive_control`, and two green jobs at the same image digest read `py-spy rc=0` with `Python v3.14.6`; the null is the green pair, which shows the sample can succeed. The perturbation that would void the finding is a green job whose positive control ran with no py-spy call at all.",
+   "remeasure": "At your own merge base: read the nightly-ha job logs for the newest three reds and the newest greens and compare the `py-spy` line and the `hb:positive_control` verdict, as the RCA's section 1 does. The container lane is CI-only, so the local reproduction in the RCA is a claim to re-run there, not a measurement a seat can take on the stock box.",
+   "brief": "Constraint, not an opportunity: `check_hb_positive_control` passes on ONE racy sample. A repair must not simply retry until it succeeds (that converts a measured red into a flaky green); it must either take the sample with a method whose failure is distinguishable from a real hang, or make the check's sample deterministic. The countermeasure the RCA proposes (A) and its demonstration obligation are in dev/audit/rca/nightly-ha-pyspy-timeout.md section 5; carry the demonstration with the fix. The RCA's proposal (C) is an owner decision and is not this carry."
+  },
+  {
+   "from": "the round-10 planning pull request that added tools/plan/replan.py; its cross-check of the out-of-tree plan documents against the roster found the wave table stale",
+   "effect": "invalidates",
+   "control": "At roster blob 277cdd359193 the wave table names 10 wave-1 groups, 7 of them already done, and 17 wave-2 groups, of which DEEPLINK-HANDLERS, FREQ-DEFROST, NIGHT-FOLDS, REPLAY-LANE, SAV-REASONS and TRAIN-HOLD are in progress now. Its 146.2 h critical path comes from after-edges the roster no longer carries. Null control: the depth derived from the roster's own after-edges is acyclic and reproduces the replanner's dispatch order, so the disagreement is in the document's source, not in the derivation; the document was cut two roster edits earlier (blob 78b01864, 63 groups).",
+   "remeasure": "At your merge base run `python3 -I tools/plan/replan.py --roster-ref origin/handoff/audit-r10-roster --out /tmp/plan.json` and read its wave table. A wave table whose first row contains a done group, or whose second contains an in-progress group, is this staleness re-derived.",
+   "brief": "Constraint on the next planning seat: the wave plan is the schedule model's output, never a hand-written table. The dependency graph is the roster's after-edges, done-ness is the roster's stage, and a wave is a dispatch instant rather than a dependency depth. The out-of-tree wave table, drain note and hand-cut wave JSON are historical: they predate roster edits, cover fewer groups than the roster carries, and their critical path comes from edges that no longer exist. Re-derive with the model instead of editing the prose."
+  },
+  {
+   "from": "the round-10 planning pull request's cross-check of the hand-cut wave JSON against the roster",
+   "effect": "removes",
+   "control": "The hand-cut wave JSON names 39 groups, all of which exist; 7 are done, and 18 of the roster's open groups appear in no wave at all. Nothing reads it: no tracked file opens it, and the renderer that used to is now fed by the plan model. Null control: the model emits a wave for every open group, so the 18 uncovered groups are a property of the file, not of the roster.",
+   "remeasure": "`git grep -n 'WAVES.json' -- tools tests .github` should return nothing once this carry is the only mention; then re-run the replanner and confirm its group list covers every open roster group.",
+   "brief": "The hand-cut wave JSON is retired. It is not an input to any tool and must not be regenerated in its shape; the round's wave plan is the model's emitted plan. A group enters the plan by entering the roster, and the replanner picks it up without a second file to edit."
+  },
+  {
+   "from": "the round-10 planning pull request's cross-check of the drain note against the live board",
+   "effect": "invalidates",
+   "control": "The drain note plans 16 open pull requests in seven lettered batches; at measurement 2 were open (#2490 and #2488), and the batches it names by number have merged. Its merge-mechanism principles still hold; its PR inventory and batch schedule do not. Null control: the count is read live from the pull-request list, so the difference is the board draining, not a miscount.",
+   "remeasure": "`gh pr list -R tvofi/heatpump_optimizer --state open --json number` and compare with the drain note's batch table; every batch whose pull requests have merged is a spent schedule.",
+   "brief": "Constraint on a drain: the merge-mechanism rules in the drain note bind (batch by mechanism, recarry only inside the train, never rebase a head under review, serialise the coordinator file), but its pull-request inventory and batch schedule do not. Take what is open and in what order from the live board and the plan model; do not re-run a spent batch."
+  },
+  {
+   "from": "the round-10 planning pull request's cross-check of the roster's stored wave field against the depth its after-edges derive",
+   "effect": "invalidates",
+   "control": "The roster records a wave per group and its own comment calls that the dependency depth. At blob 277cdd359193 the stored value disagrees with the depth derived from the after-edges for 40 of the 45 open groups that store one; the other five store none. NIGHT-FOLDS stores 6 and derives 1. Null control: the derivation is acyclic and reproduces the replanner's order, so the discrepancy is in the stored field, not in the edges.",
+   "remeasure": "Run the replanner and compare each open group's level in its output with the roster's wave. Any disagreement means the roster was not re-recorded after its edges changed.",
+   "brief": "Constraint on the roster owner: the wave field must be set from the after-edges' derived depth at the next roster edit, or dropped. A reader must not take it as the schedule: the schedule is the model's wave (a dispatch instant) and the dependency depth is the model's level. Until the field is re-recorded it is stale metadata, and a plan built from it will put in-progress work in a later wave."
+  },
+  {
+   "from": "the round-10 root-cause seat for R10-RCA-ORCH-CONTINUITY (class N-silent-stop, #2557), whose countermeasure is the detector tools/audit/seat/pulse.py and whose record is dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md",
+   "effect": "narrows",
+   "control": "The class owes a class-eliminating barrier and the tree carries only a detector. pulse.py judges three consumers (opener, verdict router, state beat) by their owed input on origin, so its verdict is the same on and off the orchestrator host; but its only scheduled run is sweep step 5, inside the session it watches, so a stopped host stops the watch with it. Established by measurement over round 10: `python3 dev/audit/harnesses/pulse_replay.py --since 2026-10-15T00:00Z --until 2026-10-21T08:00Z` reads 609 samples, the opener STOPPED in 25 samples in 1 window (2026-10-16 08:45Z-14:45Z) and the state beat STOPPED in 37 samples in 5 windows, each a stop no on-host run reported. The null control: the same replay with `--opener-h 1000 --state-min 100000` reads 0 windows on both arms, so the windows are the bounds firing, not the replay. Cost test from the record's section 4: defect 3.0 h/day against an hourly off-host run at about 3.3 min/day.",
+   "remeasure": "At your own head: `python3 -I tools/audit/seat/pulse.py --self-test` (every check ok) and the replay above with its null control. Then check whether any off-host schedule runs `pulse.py` and reaches the owner on exit 1 or 2: list the account's scheduled cloud probes and `grep -n pulse.py .github/workflows/*.yml`. A `pulse.py` that appears only in the `instrument-self-tests` job and sweep step 5 means the class is still `detector`, and a silent stop of the host is still silent.",
+   "brief": "Owner's call, not a seat's: choose the barrier the record's section 6 names -- (A, recommended) an hourly scheduled cloud probe at origin/main running `pulse.py --dump` that notifies the owner on exit 1 or 2, account configuration with no tree change; or (B) an hourly CI cron running `pulse.py`, which puts pulse.py and bus.sh on the required-check enforcement surface and whose failure mail reaches only the cron line's last editor. Until one runs, `dev/audit/config/bugclasses.json` records N-silent-stop as `detector`, never `barriered`, and no seat may record it otherwise on the strength of the self-test or sweep step 5."
+  },
+  {
+   "from": "the round-10 root-cause seat for R10-RCA-ORCH-CONTINUITY (#2557), whose red-check answers had to read job logs from a cloud seat",
+   "effect": "invalidates",
+   "control": "The assumption: `bash tools/audit/seat/failure_logs.sh <pr>` prints a pull request's failing lines from any seat. It does not from a cloud seat: the script reads the head with `gh pr view --json headRefOid`, which is GraphQL, and a cloud seat's `gh` refuses GraphQL with HTTP 403, so the script exits 2 at that line and prints nothing. Measured at the #2557 head 7e312ed2e: `bash tools/audit/seat/failure_logs.sh 2557` exits 2 in 0.5 s with empty output, and `gh pr view 2557 --json headRefOid` prints `HTTP 403: GitHub GraphQL is not available from Claude Code sessions`. The null control: the REST read of the same field, `gh api repos/tvofi/heatpump_optimizer/pulls/2557 --jq .head.sha`, prints 7e312ed2e482faf04be7eb27f38d92aef2b6fae5 with exit 0 from the same seat, so the refusal is the GraphQL route, not the seat's access to the pull request.",
+   "remeasure": "From a cloud seat at your head: `bash tools/audit/seat/failure_logs.sh <an open PR>; echo $?` beside `gh api repos/tvofi/heatpump_optimizer/pulls/<that PR> --jq .head.sha`. Exit 2 with empty output while the REST read succeeds is this finding re-derived; a printed failing line means the head read has been moved off GraphQL. Separately check the job-log fetch: the REST job-log route redirects to a blob host the cloud proxy refused (403) at #2557's red-check answer, so a script fixed at the head read may still print nothing at the log read.",
+   "brief": "Constraint on any seat reading CI failures from a cloud seat: `failure_logs.sh` is inoperative there and exits 2 silently -- an exit 2 is not 'no red', it is 'not read'. Read the head with the REST pulls endpoint and the failing lines through the GitHub MCP job-log tool (.claude/workflows/web-fragments.md is the MCP mapping) until the script is fixed; a seat that maintains the script moves its head read to `gh api repos/<repo>/pulls/<n> --jq .head.sha` and re-measures the job-log route from a cloud seat before claiming it works there."
+  },
+  {
+   "from": "R10-FLY-YIELD-GUARD (#2765), the review-strength guardrail in tools/audit/seat/review_strength.py (`--guardrail`), and its round-1 fix review (review/2765), which ruled this an owner's call under R13 rather than a seat's",
+   "effect": "narrows",
+   "control": "The guardrail already trips on the live bus. With the bus fetched at 2026-10-25T00:37Z (812 verdicts, 0 outside the grammar), `python3 -I tools/audit/seat/review_strength.py --window X=2026-10-01T00:00Z..2026-10-24T10:00Z --guardrail` reads the all arm at incidence 3/30, P = 0.0166, would-trip, and the local arm at 0/20, P = 0.0014, would-trip; the same command cut at 2026-10-25T06:00Z (after the fetch, so every verdict on the bus) reads all 2/30, P = 0.0041, and local 0/20, both would-trip, with cloud 2/20, P = 0.0526, ok. The null control: the same command cut at 2026-10-20T12:00Z, before the trough, reads all 8/30 (P = 0.5282), cloud 7/20 and local 8/20, every arm ok, so the trip is the recent window and not the calibration. A trip is not a verdict on the reviewers: low incidence is also what a scarce supply of defects produces, and only a planted defect of a known class, caught or missed, separates the two. The trip is conditional on classification: widening REAL by every word the guardrail's unclassified line names at the 2026-10-24T10:00Z cut (41, `--real-extra` set to that line) lifts the all arm to 6/30, P = 0.2238, ok, and cloud to 6/20, while local stays 0/20, P = 0.0014, would-trip; the next carry in this file owns that classification.",
+   "remeasure": "At your own head, after `python3 -I tools/audit/seat/review_strength.py --fetch --window X=2026-10-01T00:00Z..<now> --guardrail`: read the three GUARDRAIL arm lines. Every figure above is a snapshot of the bus at its fetch; a later cut reads a different last 30 and last 20. Repeat the 2026-10-20T12:00Z cut as the null control: an arm that trips there too means the calibration (P0, ALPHA, N) moved, not the reviews.",
+   "brief": "Owner's call, not a seat's: whether a guardrail trip dispatches the planted-defect audit it names, and whether to adopt the threshold (P0 = 0.28, ALPHA = 0.05; the all arm trips at k <= 4 of 30, a seat-family arm at k <= 1 of 20). Until the owner rules, the guardrail stays report-only under R13: no seat turns a `would-trip` line into an exit code, a block or a dispatch, and no seat reads a trip as evidence that the reviews are weak. Building the dispatch the audit needs is R10-ORCH-DISPATCH-REG's, carried in its roster group."
+  },
+  {
+   "from": "R10-FLY-YIELD-GUARD (#2765) and its round-1 fix review (review/2765, non-blocking finding 2): the guardrail's `unclassified` line, which routes a blocked word that is neither real nor taught for classifying instead of counting it as bookkeeping",
+   "effect": "invalidates",
+   "control": "The incidence k every guardrail arm reads is a lower bound while the unclassified line is non-empty: at the 2026-10-24T10:00Z cut it names 41 words, several of which read as engineering catches (mutant-survived, unpinned-site, mutation-unpinned, null-control-unpinned, figure-wrong, body-false, spec-unmet, closures-under-approximated, docs-code-mismatch). Measured with the bus fetched at 2026-10-25T00:37Z: `python3 -I tools/audit/seat/review_strength.py --window X=2026-10-01T00:00Z..2026-10-24T10:00Z --guardrail --real-extra <those nine>` leaves every arm's line unchanged (all 3/30, P = 0.0166, would-trip; cloud 3/20; local 0/20), as the round-1 review's sensitivity run found, so the trip does not rest on those nine. The perturbation that shows the widening is read: `--real-extra` set to all 41 words lifts the all arm to 6/30, P = 0.2238, ok, and cloud to 6/20, so the all arm's trip does rest on the classification of the other 32. The line grows: cut at 2026-10-25T06:00Z it names 51 words.",
+   "remeasure": "At your own head: `python3 -I tools/audit/seat/review_strength.py --fetch --window X=2026-10-01T00:00Z..<now> --guardrail` and read the last line; then the same command with `--real-extra` set to every word you would classify real, and compare the arm lines. An arm whose line moves under the widening is a figure resting on unclassified words, and P0 (24/85 at yield-probe.md's post-cloud window) must be re-derived under the same widening before the two are compared.",
+   "brief": "Constraint on the D13 seat of a later audit round, which owns REAL's list (REAL_CATCH and REAL_EXTRA in tools/audit/seat/review_strength.py): classify every word the guardrail's unclassified line names as real or bookkeeping, with the verdict that used it as evidence, and re-derive P0 under the new list in the same pull request. Widening REAL without re-deriving P0 moves k and its baseline apart and makes the threshold meaningless; leaving the line unclassified keeps every arm's k a lower bound, which no seat may report as an exact incidence."
+  },
+  {
+   "from": "R10-DEPS-PIP-BUMP (the fixer-authored replacement of Dependabot #3088, the pip group of 2026-11-01): homeassistant-stubs held at 2026.9.3 while the rest of the group lands",
+   "effect": "invalidates",
+   "control": "Measured with mypy --strict exactly as `run_mypy` in tests/typing_ruler.py invokes it, over custom_components/heatpump_optimizer, at the re-applied typing lock: 70 errors with homeassistant-stubs 2026.10.0, 1 with only the stubs put back at 2026.9.3 (that one is mypy 2.4.1's reversed() overload, fixed in the same pull request), and 0 at main's lock (mypy 2.3.1, stubs 2026.9.3). The perturbation is the stubs pin alone; the other single swaps (mypy back to 2.3.1, homeassistant back to 2026.9.3) leave 69 and 43. homeassistant-stubs 2026.10.0 ships only its dist-info: its PyPI summary is 'Deprecated: Home Assistant Core ships its own type information', so under it mypy reads the py.typed annotations of the installed homeassistant.",
+   "remeasure": "At your own head, build a venv from tests/requirements-typing.txt with homeassistant-stubs dropped (or at its latest release) and run `python tests/typing_ruler.py --mypy --emit <file>` with that venv's interpreter; read the error total and by_code, and the same run at the unchanged lock as the control. The count depends on the installed homeassistant version, so state it with the figure.",
+   "brief": "Constraint on the seat that moves the typing ruler off homeassistant-stubs, which Dependabot will keep proposing at 2026.10.0. The ruler's pinned pair is mypy plus homeassistant-stubs, and that pair stops existing: from 2026.10.0 the stubs are empty and the type source is the homeassistant package itself, so the pair becomes mypy plus homeassistant, recorded in tests/typing_budgets.json's ruler, and lock_disagreements, check_pins and the requirements-typing.txt header move with it. The census then measures a different thing (inferred types the stubs never carried), so its errors are paid in code under the ruler's ratchet or re-recorded as a deliberate, owner-approved measurement change; never land it as a routine version bump. Until then, homeassistant-stubs stays at 2026.9.3 in tests/requirements-typing.txt and homeassistant rides on the lock's overrides."
+  },
+  {
+   "from": "R10-DEPS-PIP-BUMP (the fixer-authored replacement of Dependabot #3088): the seat venv-ha assertion now reads the typing lock's homeassistant pin instead of the literal 2026.9.3",
+   "effect": "invalidates",
+   "control": "The environment runs a pasted copy of tools/audit/seat/cloud-setup.sh, not the checkout's file, and the pasted copy predates this change: its line `\"$PREFIX/venv-ha/bin/python\" -c 'import homeassistant.const as c; assert c.__version__ == \"2026.9.3\"'` runs under `set -euo pipefail` after installing tests/requirements-typing.txt, which now pins homeassistant 2026.10.4. Measured on a venv built from that lock: the literal assertion raises `AssertionError: 2026.10.4`, and the lock-read assertion this pull request lands exits 0. The null control is main's lock, whose homeassistant 2026.9.3 passes both.",
+   "remeasure": "After the paste, start a fresh session and read the session-start `toolchain:` line and `bash tools/audit/seat/cloud-setup.sh --check`; both are OK only when the setup script ran to its end. Before it, `grep -c 'sys.argv\\[1\\], c.__version__' <the pasted script>` reads 0.",
+   "brief": "Owner action, once the pull request that moves the typing lock's homeassistant pin merges: re-paste tools/audit/seat/cloud-setup.sh from main into Project settings > Environment > Setup script. Until then the pasted copy asserts homeassistant 2026.9.3 against a venv-ha holding 2026.10.4, and under `set -euo pipefail` the setup script exits 1 after the install, which tools/audit/seat/cloud-setup.sh's own header says stops every session from starting. The re-pasted script reads the version from the lock, so later lock bumps need no further paste for this line."
+  }
+ ]
 }
diff --git a/dev/programme/delivery/3147.md b/dev/programme/delivery/3147.md
new file mode 100644
index 000000000..5c8b8bf33
--- /dev/null
+++ b/dev/programme/delivery/3147.md
@@ -0,0 +1 @@
+- [#3147](https://github.com/tvofi/heatpump_optimizer/pull/3147) — **open**, R10-DEPS-PIP-BUMP: deps pip bump (R10-DEPS-PIP-BUMP)
diff --git a/tests/requirements-build.txt b/tests/requirements-build.txt
index c9b9cf40a..ad6d2d7f3 100644
--- a/tests/requirements-build.txt
+++ b/tests/requirements-build.txt
@@ -2,12 +2,14 @@
 # `--build-constraint`. `--require-hashes` checks what pip installs, not what
 # it installs into the isolated environment that builds an sdist, so without
 # this file each sdist build fetched setuptools, wheel and Cython unpinned.
-# Two pinned packages publish no wheel for the runners' interpreters and
-# build from source: PyYAML 6.0.1 (tests/requirements-ci.txt) and PyRIC
-# 0.1.6.3 (tests/requirements-typing.txt). Their declared build requirements
-# are the input: PyYAML's `setuptools`, `wheel`, `Cython<3.0`; PyRIC declares
-# none, so pip's default `setuptools>=40.8.0` applies. `setuptools>=61` is
-# lru-dict 1.3.0's, kept although lru-dict 1.4.1 now installs from a wheel.
+# One pinned package publishes no wheel for the runners' interpreters and
+# builds from source: PyRIC 0.1.6.3 (tests/requirements-typing.txt). It
+# declares no build requirements, so pip's default `setuptools>=40.8.0`
+# applies. `setuptools>=61` is lru-dict 1.3.0's, kept although lru-dict 1.4.1
+# now installs from a wheel. `wheel` and `Cython` were PyYAML 6.0.1's, which
+# built from its sdist; PyYAML 6.0.3 installs from a wheel, so no build reads
+# them now. Cython is kept pinned so a future sdist that wants it fails on a
+# hash rather than resolving it unhashed; its old `<3.0` bound was 6.0.1's.
 #
 # A pinned build requirement NOT listed here fails the build closed, with
 # "all requirements must have their versions pinned", rather than resolving it
@@ -15,60 +17,57 @@
 # 3.13.15 and 3.14.7 bundle pip 26.2.1.
 #
 # Regenerate (3.13.15 and 3.14.7 produced one body):
-#   printf 'setuptools>=61\nwheel\nCython<3.0\n' | uv pip compile - \
+#   printf 'setuptools>=61\nwheel\nCython\n' | uv pip compile - \
 #     --python-version 3.13.15 --python-platform x86_64-manylinux_2_28 \
 #     --generate-hashes --no-header --no-annotate -o <body>
 # and replace everything below the blank line that ends this header.
 
-cython==0.29.37 \
-    --hash=sha256:0301d4739c6894e012f1d410052082fdda9e63888c815d9e23e0f7f82fff7d79 \
-    --hash=sha256:0544f7a3e4437b89b356baa15387494c18214e03f2ffaddada5a2c71c3dfd24b \
-    --hash=sha256:0a0a6d5972bb3b8c7363cf19a42a988bb0c0bb5ebd9c736c84eca85113ccfdbe \
-    --hash=sha256:12192ab269e7185720f2d2f8894587bf1da4276db1b9b869e4622a093f18cae6 \
-    --hash=sha256:177481b0a7e003e5c49e2bf0dda1d6fe610c239f17642a5da9f18c2ad0c5f6b6 \
-    --hash=sha256:2618af0b8df26d32ee4e8858d4ad8167546596762620aeade84954ae37194a0e \
-    --hash=sha256:29415d8eb2fdc1ea518ca4810c50a2d062b387d4c9fbcfb3352346e93db22c6d \
-    --hash=sha256:2ad634dc77a6a74022881826099eccac19c9b79153942cc82e754ffac2bec116 \
-    --hash=sha256:2de3e729d25f041036e81e2f15683dd129f977dfb5b06267e30e8d7acec43225 \
-    --hash=sha256:3f87bef1808d255cf13be378c7ad27ae7c6db6df7732217d32428d1daf4109be \
-    --hash=sha256:4658499a41255431f6bbdca7e634e9c8d3a4c190bf24b4aa1646dac751d3da4d \
-    --hash=sha256:562f8f911dbd6f1a1b9be8f6cba097125700355688f613994ccd4406f220557a \
-    --hash=sha256:6c672089fba6a8f6690b8d7924a58c04477771401ad101d53171a13405ee12cb \
-    --hash=sha256:6cddb567dadb3aa3e280a8a35e5126030915ea744c2812206e9c194b8881475d \
-    --hash=sha256:79ecfc48694e156402c05561e0adb0e25a6e9d35ac0b41693733a08219d38c58 \
-    --hash=sha256:852cd4378cbc9ade02f53709107ff9fdad55019a3a636e8a27663ba6cfce10b6 \
-    --hash=sha256:8bf38373773f967cfd793997a6fb96cf972d41a9fce987ace5767349d6f15572 \
-    --hash=sha256:8c39c2f5a0fe29bb01de9b1fb449bf65bed6f192317c677f181732791c63fe28 \
-    --hash=sha256:9450e0766ab65947f8a2a36f9e59079fc879c3807ec936c61725a48c97741a52 \
-    --hash=sha256:95f1d6a83ef2729e67b3fa7318c829ce5b07ac64c084cd6af11c228e0364662c \
-    --hash=sha256:9a455347e20ddfad0c5dfee32a3e855ee96811269e5fd86be622ddc4cb326404 \
-    --hash=sha256:9e68bafeeb97d5a403fb1f7700bd4a55a1f8989824c323ae02ae8a4fcd88f6a1 \
-    --hash=sha256:a6164a05440dcd9daa760c6488bc91bdac1380c7b4b3aca38cf307ba66042d54 \
-    --hash=sha256:ac910a28a2fd3d280faf3077b6fe63b97a4b93994ff05647581846f0e4b2f8d1 \
-    --hash=sha256:af03854571738307a5f30cc6b724081d72db12f907699e7fdfc04c12c839158e \
-    --hash=sha256:af8e7b4397620e2d18259a11f3bfa026eff9846657e397d02616962dd5dd035a \
-    --hash=sha256:b048354fd380278f2fa096e7526973beb6e0491a9d44d7e4e29df52612d25776 \
-    --hash=sha256:b225d5e2091c224d4ab328165fef224ba3919b3ed44bd9b3241416f523b4d51a \
-    --hash=sha256:b6c48f1032b379135a5b4a31976d6c468e02490688acf9254c6c8ed27bd4cbd4 \
-    --hash=sha256:b82584836e9e7c0d6effee976595e5cd7fa88dbef3e96e900187983c1d4637d1 \
-    --hash=sha256:bbce388431a2608a81c8ab13cb14c50611473843ca766031b8b24bb1723faf79 \
-    --hash=sha256:c33508ede9172a6f6f99d5a6dadc7fee23c840423b411ef8b5a403c04e530297 \
-    --hash=sha256:cc1b9ce2b73b9ee8c305e06173b35c7c202d4b82d084a0cd73dcedfd6d310aec \
-    --hash=sha256:d94caf90ae9cb56116ca6d54cdcbccd3c4df6b0cb7233922b2233ee7fe81d05b \
-    --hash=sha256:e14cd44c830e53cf9d7269c87a6bcc638bb065ec07e24990e338162c7001d3c3 \
-    --hash=sha256:e841a8b4f9ceefb2916e32dac4f28a895cd519e8ece71505144da1ee355c548a \
-    --hash=sha256:e8af5975ecfae254d8c0051204fca995dda8f93cf9f0bbf7571e3cda2b0cef4d \
-    --hash=sha256:ea6d208be1906c5df25b674777d5905c6d8e9ef0b201b830849e0729ba08caba \
-    --hash=sha256:f2d621fe4cb50007446742134a890500b34e3f50abaf7993baaca02634af7e15 \
-    --hash=sha256:f813d4a6dd94adee5d4ff266191d1d95bf6d4164a4facc535422c021b2504cfb \
-    --hash=sha256:fa5b6a0f69bf1823c9fd038fa77a2568b78fda2de045a95b48a71dee4d0d578f \
-    --hash=sha256:fe0eaf6b1e9ee97c5ee7bfc943f00e36cf59d929db16886cb018352bff8208da
+cython==3.3.0 \
+    --hash=sha256:03056533fe4fdbc4f1d34a39178f9a4937ff35196f8bcdde2a67b5b5809c61fe \
+    --hash=sha256:03bc5333932f5dda3ba9315298ecdd21daa1b58410bb1f8ce04c78ec8337130a \
+    --hash=sha256:0507d9caf7dc35f1212627145d5d13dbc5dd7128529a6608ab72690472fa688e \
+    --hash=sha256:0deedc2e9a5a664e1adfa4c2d310aa7b54903e1a647c274b6c9213f77a02d637 \
+    --hash=sha256:11e437f086affee8051cec4bb531be3edb646ab66e325154aa6849377f365033 \
+    --hash=sha256:14e825253455e943ca765a95096b355745558436b0c46c24856de9269cc4dbd9 \
+    --hash=sha256:169e56fd411f4cd5bba51c82f8239421d547a846099db2b261e4aed48ba9f51f \
+    --hash=sha256:23942b0662642927a55676e4b26e6840fb166dd7d76436384685227e7e8619a4 \
+    --hash=sha256:26a5e536fc68e85a9de091a0b51c42c5ac834f8d00aaa43f227cbc3efa797ae5 \
+    --hash=sha256:29f38ebafdf23e3da2516f40c4d065da38bfe002181bf93e2b8cf1262449aba6 \
+    --hash=sha256:311a016369adfd1e0015c4f9819168fc0e518451d7efb4435c30d65a3a26d52b \
+    --hash=sha256:333449cc0350baedee5a6af27929eac8a71eac4ec59333c45ff476b33c6c660d \
+    --hash=sha256:428fafed98ea26927000a287b4dfc9ef07339f56656a5329a34eaa593f79a4f8 \
+    --hash=sha256:46072c0d404616b5e652a63882c79cc3f8a1d62635a8692f56ed0e416a4dfed8 \
+    --hash=sha256:4a36c34d1950845b8ac148653b07cdc62421a4b0d9abfcc849e69f1c4ff9919d \
+    --hash=sha256:51999fb834365721b6c7f689cf6e2ec7c8667aae783df9eb5e589c290a414d9c \
+    --hash=sha256:596e8df019372a2cd417805015022d42cb8ee4e1803ccdc11ed00e451625fb66 \
+    --hash=sha256:66d86b6a1548ae64851b211e3c3504535814b8c8e6c46ddcaf01062bf8d5fad2 \
+    --hash=sha256:75c4ae8a6d3a5ccf3cdaba8ab32e6a8d0cd38e3a476aa7ac12df8f8171a8d570 \
+    --hash=sha256:7e321ae700995a16dc3055ada06ffb8d61e1a7434e5d0e811547a45ac1015ebd \
+    --hash=sha256:82f94565b6001bab8e31bf52a0911672910b5735910612a2c0f772c719670006 \
+    --hash=sha256:843d7134e784e7b320ef387512e89f1b29af80c641e176dfa8eabd52aab61c3c \
+    --hash=sha256:8566ea804cfc265f5e9dda71d1b716aa24ee4c3423a5da4b28a248a78c33e3f9 \
+    --hash=sha256:90869072e50b7c8904fe1dd7810321ae901fd5637a6eec6646ed9c57f9eb1081 \
+    --hash=sha256:9b24b5c8cd536946b62086fcafee6d5509d3f549f72d553d2336af87ffbe0da1 \
+    --hash=sha256:ab24d1a4fb6aaf0b5b6fcd75a6d70255fbd3130fa78884c26991f8d5502616b5 \
+    --hash=sha256:b447f6906e0555f05dc4742ef1f99091b1e5d9aa9f16616e772fbf9ff6271616 \
+    --hash=sha256:b55c72e8eccdd508c8de3cf3bbc543aafbb3bf6a518e1ee20358d3241cd780ef \
+    --hash=sha256:b94fb5613b9fe34c27d13ec9972dc0dcd2a2155db2902e93921cadc162610a38 \
+    --hash=sha256:bc2f2a6b65a991666cfd35a35bab0cd88ffba4df2f601edb6e76cc8116de24b9 \
+    --hash=sha256:bf411da3ef1af8763781c219108860f7de33f1100038da35d6bf1b4d83fcb2c0 \
+    --hash=sha256:c4558ba85849ab65dc57e10fd0efb13fabd9d3c09981a2566e18dec7cf47586a \
+    --hash=sha256:dce56c26d388f00a19426371b6926bf2f77c5c03b71d5273e4556c68be98c2dd \
+    --hash=sha256:de883ec6764b61547c1e7674c0d8a8a875d398bd6bb684e46b93d83e4f13b260 \
+    --hash=sha256:e0d2713d2b292c826bc21dc8732bd9e47628103aa3764180c881e04b3fef95dc \
+    --hash=sha256:e6035b5231a9316edc19d6415f4296fd1d0370e2a165a714b3edc167b9ca00e1 \
+    --hash=sha256:ec09dbf73ff4f7be2b339b995fadae9c4bb517bbbed7ec11d6fe99c2092b48fd \
+    --hash=sha256:eda47eb7731c3b41180b58bb83de423f43aa58a677677e3390e8d332b003859e \
+    --hash=sha256:eed0d93fbca7087f143b42c34b05a825849bdf17f101572c2105acfa49aa88b8
 packaging==26.3 \
     --hash=sha256:94edc256424af38762eb31306eed28beb9f0efc50a8837492c9d6fd6004aed79 \
     --hash=sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c
-setuptools==84.1.0 \
-    --hash=sha256:23657205b63d4d31395ab917815247f694aafad28cd21316bf5fd45a51048ea0 \
-    --hash=sha256:5231689c6ac8156cd155cfb98c3fd6fb252c3e7e9bd3d78b64d3c55f132624c9
+setuptools==84.2.1 \
+    --hash=sha256:3ff8b3b5492a0aa66960f4419365a86b84e013070d4313e4d4a6894f5d64d6bc \
+    --hash=sha256:ca140b45d5325a9478f880e351484f62fef15f336462e449ca0c03c873d589c2
 wheel==0.48.0 \
     --hash=sha256:3217dcc807155e45db462d7ef2431f5ddda0d7273b700d05a67b271ceb1287ab \
     --hash=sha256:94800765601e9171bf5d58d066e640662842bcedcbab982b2c90787a2c987322
diff --git a/tests/requirements-ci.txt b/tests/requirements-ci.txt
index 554290a38..075416b19 100644
--- a/tests/requirements-ci.txt
+++ b/tests/requirements-ci.txt
@@ -12,9 +12,10 @@
 # the sha256 of each artifact the index publishes for that version. pip turns
 # on hash-checking mode for any file with a --hash in it, so it refuses an
 # artifact whose digest is not listed here and a dependency not listed at all.
-# PyYAML 6.0.1 publishes no wheel for 3.13 or 3.14, so it builds from the
-# sdist; `--build-constraint tests/requirements-build.txt` hash-pins what that
-# build installs, which --require-hashes alone does not reach.
+# PyYAML 6.0.3 publishes wheels for 3.13 and 3.14, so nothing here builds
+# from an sdist; `--build-constraint tests/requirements-build.txt` stays on
+# the install so a pin that does would have its build hash-pinned, which
+# --require-hashes alone does not reach.
 #
 # Regenerate after changing a pin: delete the edited package's hash lines,
 # then run, once per interpreter the workflow installs this file on, and
@@ -329,251 +330,225 @@ frozenlist==1.8.0 \
 idna==3.20 \
     --hash=sha256:a7db850025b95ded1eae8a46181a1a6c56c92c96f0e2b005d9ff8dc0210cab44 \
     --hash=sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c
-multidict==6.9.1 \
-    --hash=sha256:006c4478de0a1876f4834e14255776286f09b9846b505fe63f67f9d173a9487c \
-    --hash=sha256:024123f0ab402ab33828e24eb80fa8f25167d0d3783ba5f287e39ed741e6abf9 \
-    --hash=sha256:02f6d0c4b70f783305e73f9944d8efe6be1022550f0974ba0ae9d8893c0350fa \
-    --hash=sha256:02fe09dc197b8ae7e355371e51e5dce2f39060cd5a8badf94904527e23a3f188 \
-    --hash=sha256:03731f6fc036180700c9dc2308205a48e5ca6f3ff03087739ab746f294022201 \
-    --hash=sha256:03d47df72f084f757c1cb771188d5f4e3a805e4abc4d67e32509272343ae9382 \
-    --hash=sha256:03fac50ddfd8302175b77863a015eccfae76767cda5506eef86df559ba861e1f \
-    --hash=sha256:042fb0196047e786936a730bd302de83143950da45f2c16078da8f35e1cf7919 \
-    --hash=sha256:083735b7f395894e43adb278d5dae901448883a835ff8f1977e285fefdb10418 \
-    --hash=sha256:095d900c242e00fbe5f321ee072e7278b4153e78c5ce9c1efde167d62c1e4771 \
-    --hash=sha256:0a5769559e3312dd96731fbe15b4abb6033368ac1cad5a98dadd21946a4c7d6c \
-    --hash=sha256:0b2fb8c349d1103863750b5d8cb5ace766917f4b35f3d883c8f778853eaa9f76 \
-    --hash=sha256:0dd655518f136febd96c05131a76a863e32fc2a1d7acd4e3c959e3ceb77d8345 \
-    --hash=sha256:0f06e60fa190aa7abd0914c2a766736fdc8e9f34878c4346338534b73d1b20e2 \
-    --hash=sha256:0f2ce963299d42fa3f22a90adc0fdf174792ffef5ff4c7ffb68260548fb05580 \
-    --hash=sha256:0f3bd290711c6e9486173a6ee7cd4e7f00c3971c7908c1ec1b6e5437c5e4c6f9 \
-    --hash=sha256:10083a8a0f4e1b26b599889e90b9802504ce5d3f7722f925bbb7ca47dd22a7c1 \
-    --hash=sha256:13849a1d4f54c3809ae721e9e83ab28f5ea602f33660cb84eb6ef261eac706c1 \
-    --hash=sha256:14c56f73e78faa1f68bbb826197cd5871994e70e841b8590829c35912ece5c64 \
-    --hash=sha256:15db6a102cbaf1949cf028ecf080aac76d20bcd29ad4e092574db6c6b7af78a5 \
-    --hash=sha256:19e31815d41cefc365489e591d105d2baceb2f65aa75d29471fbdbda8651e006 \
-    --hash=sha256:1a53de2772cfb74559df2eb4456ec4eeb908435ec55a84b69370d9d745d62aa8 \
-    --hash=sha256:1a8adfcaf96f587ab138476eaddef95f29b8a2a8a9afbfea8d2fd62180995d02 \
-    --hash=sha256:1a938761c77e0e6edb0c93d02f4e988d44a69e5195e5a3b893e5553311347132 \
-    --hash=sha256:1c9f3c25df6c9d3bbae4f6fd3f514b1c5c740a2110f56ccf36069c85417e289c \
-    --hash=sha256:1ca5ebe6d454f1e5496cf052386a559f1080bf2de75bf327ebca0a6003b79f19 \
-    --hash=sha256:1d804e4caf5d5da37d6dac1325da5629ebef1e27a294c2b568b295814aa36c7b \
-    --hash=sha256:1fee9a16d88a1c4865610de31ef5c666671020d7a81d1f510eaf3c97d00ebeba \
-    --hash=sha256:23136f5a564654eb61061ec6d5620a4c1ea32c8f552b65e9982a12b72bff601b \
-    --hash=sha256:2784090c30a586d5b45197bd9c32f87fb927216cde302f6cfd76d76577e90f08 \
-    --hash=sha256:29138fef49828542e859828107e42e50d0e587c513b7eb4b2d92bade2b0860fe \
-    --hash=sha256:2c1aeb92eea59d824f004341b26d5e4b47a8a441cf9726769b9a90abf9d0e08f \
-    --hash=sha256:2c5d675da8f1cb5650271c8ad5e95c0a3e5a183c105e72d953b12877b1c8d0fd \
-    --hash=sha256:3100d169ceb7bc8f05f89a6db11d1b21f119975fc26f29dc45a472e3569f0879 \
-    --hash=sha256:31199204b3ced121ff5407a2c342326a5d27e3870abbf94bd80dbd2451b7bc8f \
-    --hash=sha256:32217133dddc58c927805cf6c0731d8144584176b768042ee886d51e71860bc9 \
-    --hash=sha256:33fa55b990f81c2927e01399ace0d18926c69d69baa8cdaa819424132fb97987 \
-    --hash=sha256:35ba0263bae5dd3ad5aad767cc9afc01a8598c7dae30f1b3b2de98b1b32c28bd \
-    --hash=sha256:35fc236507fb1b3138f0af5ecd5f94ed752d4d6d826248eae425f86204013eea \
-    --hash=sha256:361f7206cf341ba94fb015688f5c8b480f8e63bd58a4c14a48aeca7851a241cc \
-    --hash=sha256:369b5aa01b241cd3fea6890bdbb11a1425d87bf1515831500d518f4223e9d72c \
-    --hash=sha256:37245ca4105386194dd1d292a6f2aae09bfe1bd7ac6f9ec25093e3cf8e9b143b \
-    --hash=sha256:372c063f37480f62c1ae32dc3a1a0a5942b180c883f99789075a8a8ec3c4e709 \
-    --hash=sha256:37a9ebe00c698279213d56e6c64e1962ab1e092918270649b397cac3dc196ca4 \
-    --hash=sha256:38c9986f9ce50c459b10de216a05f4bd7ed5ac63887d56e500a52bb464b861ce \
-    --hash=sha256:3adf06c66041aa21eeb8a71e82379b74773298c8e6d3d839b151aae441a99b94 \
-    --hash=sha256:3c95601ed98fad3f6e2f8fe809c3b526b0fab31ef525e00a155e227f3d17f58a \
-    --hash=sha256:40aec5299e1ed71fbb988389059da381c3c1a60e0c649acceb2a35d9b128848e \
-    --hash=sha256:43124fe172ada86d03ac3c8dc8179091341f6724d5e5d5b160e1587e4cd3761b \
-    --hash=sha256:4736d350371337825cac1793c9f7c40701c32a03912548c2a7608e51679cbb96 \
-    --hash=sha256:475d04d5192eba487a3e2f935976340baa24529046e9c1c9c7a3b7bf80445ae1 \
-    --hash=sha256:4a409ccc42aefec904038695d5d7fd6d8f3af2721b7b6401d55135ec7d6d298e \
-    --hash=sha256:4d718fa1b5f0d0dd75e86fbbc5b0c93ea3a5d65216c85c61cd5d7cdddfe08455 \
-    --hash=sha256:501ed8b02a5990c67a91c732843609d43a6be1f7576fcdfc867331239f37fbd3 \
-    --hash=sha256:539c2cd5fed0947c135cd7eabaaac55f48300dfa1de0f3ca4edb5efa6606f471 \
-    --hash=sha256:557a4e1708df428ebe6c3081c83a273d275dad2446ce0d81fc648ac71afdb18d \
-    --hash=sha256:56d834b74c993a7d7cb2b8ab33a0d55c3e0d4a3d2f2da2808a4ad3d79189711b \
-    --hash=sha256:5800368526647146978389dfaa46da3356291e9f0fff9a4ef12e8c2bef964a0d \
-    --hash=sha256:59c123d0e948d760a5f930f316cfefa07e8d632ab84327c0693ee6a88171154f \
-    --hash=sha256:5b30ddf7234e611ca877575b62840e6af5977f92f1f9d532eedbb05a44ff8004 \
-    --hash=sha256:5ecace251ccfa705bf3d7d35c5032cf750f5c629809740405697bce5c118c4a4 \
-    --hash=sha256:5f89dad732280e7a10b74d40b91364f88e13c3f2c08c2ef83a8cd42f7a61af2e \
-    --hash=sha256:637f4ae36264bd7b8d9a60193acddc1d735ad52e8ed53a19931ea6d921fea8e5 \
-    --hash=sha256:63ada7ee2e9345695f9e9bc4c65d72222253f07b1ac94fd0e37555cc6f3c7f60 \
-    --hash=sha256:6441cc837aea58be7d9baef1b2383eb8311ab9303f500f99ac90b584cd78bb14 \
-    --hash=sha256:658f90f49cf5af2441cad0a2b801c3ef520471989a1ec55bcb25b255b2ca8d2f \
-    --hash=sha256:66987aa68b0f7c2a1cc5f388ca962b8ed92b10f79de38d6d0d8c716154f519d9 \
-    --hash=sha256:696477ad71385c4795e3b8e4cf10b0d2c28c2a1ca6a955e031cb1e62993e9ee3 \
-    --hash=sha256:6b7e54fd883671d1a8810704851c044b7173287c552b9f5c3d9e0eb9f00ae194 \
-    --hash=sha256:6bc94fe17c3c56e5418f79515b786b101845f70609b0d19d0c1ba13448e5633a \
-    --hash=sha256:6e6b7e3a1520c39a2772f414cd9ddf5995f77e4e823dfa1522af383addd465a3 \
-    --hash=sha256:6ed30be8918e18c8bed0a2e8b70639ecf02feb61ed00ca2e41cfcb2a50fa3f42 \
-    --hash=sha256:73533644e1f69ea1164d56cc6505f564c6c44072b646b66d67df2d31fed0348c \
-    --hash=sha256:73bcafa21a78d0776b3ee7cd2a63c66f968eb7db8e8d594e32d7329950f6e828 \
-    --hash=sha256:7814bbee202acd3bd240204c17d8b87a4c48c81064fd8674dbe527d94d5a4290 \
-    --hash=sha256:783ba7d845d79ce976afd9c1e91a4e5714671defa198ee789e8b23316083a485 \
-    --hash=sha256:79da2491348b30810728050b4a8ec0416f85884125c2fd44655b3d01150d9c3e \
-    --hash=sha256:7a0c98f6a636adf0d7edd60c61589eaf52d149239af754d0bfeb0effedba53a8 \
-    --hash=sha256:7ab379f95caee071a37cbd8be86d4c65accc651d391f9f97748fef006f38769c \
-    --hash=sha256:7bf6478188f4e47bf5686e8a33da4ae28bf43b1b2528d9ee144d28492bfac60b \
-    --hash=sha256:7c6eecfab7ce4cd9487ff8ba936fe38cdfd68c04faf3d5c710363c6a8e695659 \
-    --hash=sha256:7c708566da8014b120a64b1eb6d200c6c0c8cb36296383723cdb6fc82038270b \
-    --hash=sha256:7c8d5882ba25ac0282258be435d8a05aa0cbcacfce15799154a338f847f159b9 \
-    --hash=sha256:7fc59e9ba821b220944ccfe0f89c9dc4745f6d097569992356eb03869f21e953 \
-    --hash=sha256:7fd79c521f6290c69125fa2b85fa65d9e657e6a8ffaf722dc881b926bef4aa5c \
-    --hash=sha256:803f8b575a71b1b299d677c28db0653459c79b5308874efec813f17b7457c7f1 \
-    --hash=sha256:8050e75af7e4c6e2d5260b84eeedb618f3e452e66473432e085b5d1b81429299 \
-    --hash=sha256:81cdc537e0a42e3c0170752fcadbe450246d5c3b4b7231d6eb9672456605ac94 \
-    --hash=sha256:827c92145b3b976b39430129c89d213b250dacbe5fce678e9a03940e6e848983 \
-    --hash=sha256:854fd2f1bc6e8a56b89910b5cd7261a8b40f13ebb31572da985ce59c7da0886d \
-    --hash=sha256:877ca17fdcfdf5c397493a71e5ff97a87bb181417fe717fdadc77c08c09301ac \
-    --hash=sha256:87cc632c88ee5dc80e12681047839304d98ee5c9a708d686505767001c9b8b9a \
-    --hash=sha256:8879510a76940670517ea1cb589978da44b86e286ec3e50d664ef330817afce7 \
-    --hash=sha256:8885e3808aedbd6725b921fb67dacaae0678933561ddd47c2b01315198c70e2e \
-    --hash=sha256:8b193bf7a443c97d81c47052f60c486071a4bdef4a573fa2514f920089414d45 \
-    --hash=sha256:8ed78ccad4c7b421804f5d524b7740946a7ef75d89dc0dac52e9d7c24c472410 \
-    --hash=sha256:8f2973bbd2bebd9d2e0cd6394c1292a1a19ccd56bdcbe1e174059f1a39be5b40 \
-    --hash=sha256:910d4260512660484c0dc1588a316fbb35a40c081c36fc51d1225351af17cfe4 \
-    --hash=sha256:95052e8777a86bae87c0bd0b5ab22d809e3d1d02bf69e3e66ddda5ba75a05805 \
-    --hash=sha256:95f273bea318a194f656527ee2ed19494327bc500b8e87d9358e3222579aa28d \
-    --hash=sha256:963a8d8f97057082679523d0fd4c53a38f86bc58cabe4556faef682ae53fa2fa \
-    --hash=sha256:976fd7689d69ec78d67d31d38d396d8adb562f7e8368279f76aed4aa451fa06d \
-    --hash=sha256:989261c5f1735a165f2e4e87cf6d5f17ab734fa18f9ad0383d5adfcdaefce701 \
-    --hash=sha256:9ae9614c317c50836689ce2dfde07c05fe0b16378562e2221746c3913ede3c80 \
-    --hash=sha256:9b0124b9c17e9890f0819b2e7a5f65ec9a2f5aabd6c8e7ad090c1675cf70dee6 \
-    --hash=sha256:9c4880d017555d70dea367dd49271830842d48e3891c2da97da7ce8c4abcee40 \
-    --hash=sha256:9c62e71e6289d78c0108d8aeb495f8bd3cad4bc1632fedddc9297ddf287ecc20 \
-    --hash=sha256:9d0a21cf76153de8f2d96a877991d6bc59b9ab5180b949e50db73cc193b4a694 \
-    --hash=sha256:9e14d17773b1b3c758ff153659a1824608a0cb562c45f484b5ed8a433428444a \
-    --hash=sha256:a16a1dc8529f9e734a41c3b856f3eae7ebacdc061dde3f8a844e0c7889c97203 \
-    --hash=sha256:a2212a0c842c723d919ea4a22a9296cb6b244b386e4e6ea92adfc7fbf3095519 \
-    --hash=sha256:a313bad717dde740959d50850c315b75fd4eb0c5e6b4dc8535db0f1c369be125 \
-    --hash=sha256:a32b78c1e52ebd8e247bb68300b90b233300d8816faa008ed0713bc539fb6af0 \
-    --hash=sha256:a3ffe881246d28a862f1985824f484cb7361f44d6b99c4c620436ef56462f38d \
-    --hash=sha256:a49ff5cdb33654cb7d6a3c377aa2a83ddefaa1db31eb10bcf3c180aa84f9af8a \
-    --hash=sha256:a8b75dd3d3638d9a19f23e84af4ffab3b8940422c0df2da2a77005ef5aa3d7ea \
-    --hash=sha256:ab64ace1a68682d191d9bedd9d4c939406ad86b1d9f628180410644249ad46c2 \
-    --hash=sha256:abc7c2e4b47bfe6a9aea434d3fdebb9597ee636e914e92ba352f2068b9142f4c \
-    --hash=sha256:ac348379cf4de5538a0a213be1532d289aa801ec5d267c5909446b9ea2f8e2c3 \
-    --hash=sha256:ac51cd64bae51c462ea58ad2492c9b8209667a4ef60c45c4a304518b67598d5d \
-    --hash=sha256:acddcac38adc8342ba48aba98896faa7928854bebb62542362138655b5367ee3 \
-    --hash=sha256:ad4528cdce058b684f75fad1faf4a6a6c992fe2f08376370ca66e4ce5916a84a \
-    --hash=sha256:aec65b53a07f580606593f877eefbb29a45939bfc0d3fe6e6d9f42b41b749f68 \
-    --hash=sha256:aef74e9beabbd6c4aafc091dabff86d046ccf013ce1e4396c0fbb01b4cad9de8 \
-    --hash=sha256:af1b5a92315048c3e36bbebfa7d4760a9c3e910bc4166f11b20d77d20d6bcfca \
-    --hash=sha256:b22ff30006a2f28f8bff878fb93413cbe3a4d1fd517c28081d848c90e9cfd2c8 \
-    --hash=sha256:b2483da477932ad1983d1d33c18bc3771c6fb00cfbaaed70a875fd547ef8e840 \
-    --hash=sha256:b2f0adc22a4eb31e545221d93fc73a0f6a8cc2379d0f4309f71d1d17ba938b82 \
-    --hash=sha256:b4c9e5d05b126b267ac048a89a0e2d9b48b1b648add62d4872906304a8590610 \
-    --hash=sha256:b4da208a63434d21a3df64d29758e650fc4aa8cb05848554b76949c296539cca \
-    --hash=sha256:b5f8771aaaed7f80e84a4e471d2f29ab6721e4595075e54d03ae1ed951b2000a \
-    --hash=sha256:b65121091567847a8cb520d364ab22ba90e00d3cc55fa9eb34bb439f0684bcd1 \
-    --hash=sha256:b66ccc5c2cdd26e74fa5d4c29ffae424cc6148bf93ce574821783fb3b6d452c5 \
-    --hash=sha256:b69651732c64afb691e50cdc3387cae305e0eeff8804fe3e3ce203876494932a \
-    --hash=sha256:b828cf64d62dc09ac183f03c1aeedd164ade96a2ce4934109452edf29de1dd13 \
-    --hash=sha256:b8a65621b98984a62e59403009591b8a5a7736273aefe1cab64cfb85b365cc07 \
-    --hash=sha256:bb0d664505f4b112f384cffeee82e91e3f6448d8e574989479db4439b68cba05 \
-    --hash=sha256:bb58ba73a3f96f9a3e46b1fab69929d7edbbddb3133ee74b5c3c54074a53c4f1 \
-    --hash=sha256:bc94a68ea5e18f8e85dc6b522bcb53093f692c8eb62b4837ac047da73956cbe4 \
-    --hash=sha256:bd82c4977196681a499bb6ca9e462afbc5c91c1c15b6a991dfbd72733fea4dd2 \
-    --hash=sha256:c0c88085affd35c33e124e36930c5ad96aff9294ce195eaa0fd9cec962b64a82 \
-    --hash=sha256:c148e8b596000dd3e4bfe206e70f3e666be18d72032e0012555f2373c52e35d6 \
-    --hash=sha256:c57541034d12b215ab0a2bfa371d1a8a198da18176d0426c27105b9161a6862d \
-    --hash=sha256:c9648ed33dc8179e4ec04bbc73bd7f0038e1e81217a69467f61f02a78bf07e88 \
-    --hash=sha256:ca65cced0d67a9039e93bcd98a369920e499bf98296844ff56ead01c9085321f \
-    --hash=sha256:cf22b43f35b7dbb9f71e8ee2041b5c00029cdfc28ede3a2f31cf8906f9a6c126 \
-    --hash=sha256:d35a4f1c63f07fbb8c8f9946dea98b21eddf6c57421585f71d91864be3ba2a24 \
-    --hash=sha256:d3b6e6840421c83ccb60398e333b44f910b0907bb409597685ab2eedd1e22eab \
-    --hash=sha256:d73fed4e37158ff00cd271871170b79e40138db51e625fd352fa17c6acb34f67 \
-    --hash=sha256:d7bf9e43282d69561618e8a0ea33368d532ebef42f15c096f427090521dd74f3 \
-    --hash=sha256:d9d6544790ba50438a9c1a903c3c4afb1ec8a7832db5518549275b40ef0dd4b1 \
-    --hash=sha256:db4d697b18b6ef5528b1f36bfa25072cd2a421869f5963bc0e92c8a34b9e2800 \
-    --hash=sha256:dd9a137a4a9becda3094f3831cd026380f75f6855e051eefe4c73ade524f1cc3 \
-    --hash=sha256:de7738b8c0bb74c4cc16bbd7fb49fc2bcf6430dba11b3432cd52768ae40933e8 \
-    --hash=sha256:e3b1aa25f01238886a6baed9e13b9a9240ed344346c79ae280ae65e8603b21d5 \
-    --hash=sha256:e58952f04772f59f11c6e007471449809a30165188669bca8fdb19dde40a8f24 \
-    --hash=sha256:e5ccad4b7bac125722f48d6f862bed3b514d8526deea06316bb72f152cd30a7c \
-    --hash=sha256:e7386aa18d98d6b8af44b92173654ec469237fda35f8e8523e43b581a86f476a \
-    --hash=sha256:e81ae656b9935ac4528a71f96bb7a14d949778ed1897c573d3e7ebb9187f8841 \
-    --hash=sha256:e8f1e362c9352b50ed120f001046fdbb80810c9d56580f4c3fc13bbe30823387 \
-    --hash=sha256:e96ca64383efa107262ee3949f047af5ee4f1845ba09463466c04d35a83bd3ec \
-    --hash=sha256:ea999ae6e80e66ad5eea287860951b033d0104ca34d6d87c7b5125ebe0e12721 \
-    --hash=sha256:ecc89dbd4155b2f8a47f4bbd89242a35ed15e8e0ec581cab5ac65fa38407329d \
-    --hash=sha256:ef01d29fca550ab871fd99154f82c6472aacf8e7def272dfb07b460123850390 \
-    --hash=sha256:f04551dce5a7db8c9659f2e4245494c182d0663b83661803e08d46bfcae5eda1 \
-    --hash=sha256:f0700527dd5bfa8b7204b08330542f4f388899d3c14d885d8a368992e0eb562d \
-    --hash=sha256:f2524ec55b3e65cbe235a8b3c36e2af3b635be02ed05e20c94e70c5c943c009e \
-    --hash=sha256:f5844e7befc707367807586f550fa97e23dcfef0728f02b98c7bc498a961a5df \
-    --hash=sha256:f9dad513626a33670f17cddc6078e30e311f444c957e8dbfc5b2b4603c8b4edb \
-    --hash=sha256:fc0dcb22fa9aeabfe3fa4e0430099acff985ec5d77a851382f76cc6146e780e5 \
-    --hash=sha256:fd882aa29bf402b62bf1fd7c19fd5df4b6528cf468a908864b39368572b662a9
-numpy==2.4.6 \
-    --hash=sha256:001fbb8e08d942dd57599e781f2472269ee7f2755fae407b4f67b2f0b17da3f1 \
-    --hash=sha256:0280e0356c0829a18d9de1cb7eee50ec22ca639878d7240307ca0943d73cd2c4 \
-    --hash=sha256:043191bfa8eab18c776647b62723ac9dddece59743b13f49b2016094129c2b3f \
-    --hash=sha256:06ca2f61ec4385a07a6977c55ba998a4466c123642b4a32694d3128fce18c079 \
-    --hash=sha256:0a041d3d761dc3c35cc56ce0351506a02bcbc25f7b169f652435141a17db9096 \
-    --hash=sha256:0ab0a9c4ffb1a6d95ef519fe4247dba8eb6b18ad93999f76b7f657039acabd47 \
-    --hash=sha256:0c9136e14ed34a9e343a31c533d78a9813a69a3148332bce5e9821cb2f996e66 \
-    --hash=sha256:110f8b71aacb688ec69062bb7f6938a0f8acb01b7c1c4beb453c65b6d234584d \
-    --hash=sha256:112b06a867b235ef466ed3508ddf0238050df9c727cafb5301ac385b899189a1 \
-    --hash=sha256:17f9ade344e7d9b464a084d69bcf18fc691cb1db67c62ed80820bf4926d78f0e \
-    --hash=sha256:1e254a00cdf42b1e4d5b3d68d33af63268d41340d8885df2ab6470f2e1500147 \
-    --hash=sha256:1e978ec1e8bd0e0e4de6bb75de9d30cbb74db6b6a2bb727618613703ca0167dd \
-    --hash=sha256:25c692919ac5a01f170a3bfcd62d745b24fd095c353d50812637d6fcab442e75 \
-    --hash=sha256:260a5d70215b61ab4fadf5c7baacd64821842975eea312125ed3c39a6391b063 \
-    --hash=sha256:2803abfebfc990042cd494d8ce2d5f82e9d847af6d35ec486923aa19dbad5e73 \
-    --hash=sha256:29a287e0cf63ff528da061de6b9f64a4618da591ca1046aafc54062e40ca7eab \
-    --hash=sha256:29cb7f67d10b479ff07c17d33e39f78c07f71c40ef30d63c153d340e96cd3fb4 \
-    --hash=sha256:3213d622a0283a39a93d188f3cf72b26862df52fbb4ca3697f51705016523d41 \
-    --hash=sha256:33111801a01c12a8a1e3721f0a9232f8cfc8ae2c6b7098167e6f623c6073f402 \
-    --hash=sha256:357cc07a6d7b0b182ff02249616a03742827ebb1277546b5c7cd7f7620a45698 \
-    --hash=sha256:38efbc8de75c7a0fc1ac190162d892787f3f47b57cc291231aafee36b80982b7 \
-    --hash=sha256:4081eb135ac24158bd51cdfbef16f1c64df7063b1143f24731387137c092bec8 \
-    --hash=sha256:40fdc1ae7125e518ea98e53e69a4ebc27e1fd50510c47b7ea130cf21e5e1d42b \
-    --hash=sha256:4cfe66903cc32a9921a6733d96b19bb6abf310397581bbad89c228f5abaf0ee8 \
-    --hash=sha256:511dbaf848decaaaf4b4ca48032619fb3138710c4bf7da7617765edad1ef96b0 \
-    --hash=sha256:55cced7c52e981362f708ad635198e97a752dfba412cc03c23bbf3bd8d5cd662 \
-    --hash=sha256:56b39e5e0622a09a25bf5baf62f4bcf0cb8a41ae6e2819cf49bbc5a74c083f91 \
-    --hash=sha256:5dbbdb29840ca3d91ee0fece42fc29278886d908280bfec0a5846c6f901a3eb0 \
-    --hash=sha256:5f9fb9157b4ce2971008323afe46053787b526ef624fea915b261468a8421a0f \
-    --hash=sha256:6180d8b35af935aed8ece3a85e0a43f87393ae0ac87c8d2c8bd2c993f7270ef3 \
-    --hash=sha256:68a5124b13fa6cc2086764a20005d30bc0548146f7f5322f02fce212ca14317f \
-    --hash=sha256:68bb27509ac1b9a3443094260f6326150663b06abe40b73a2f81160623da5b67 \
-    --hash=sha256:6f41ae150c4e32db4f3310cdaf64b1593a03dbabe29eec77fc9b50fe64061df6 \
-    --hash=sha256:7265a2f3d436e54ef9f2b52b5c937e6be778781bd97a590319d7348f1c1ca997 \
-    --hash=sha256:72fbe16c6fac95aedf5937fa873445cec2110be35d8a4e9433d7501fd98dae6b \
-    --hash=sha256:7d92c3819208a60205a12a245c91ad70cb0a85336659b19b834205573ac8456e \
-    --hash=sha256:8155154c7c691289fe18f510b5d4657c68c67989f293f0535a91360392ff6538 \
-    --hash=sha256:81a1cca95ed5bb92aa8b10dd2cdc9a0d3853a50fad926c28b5d7e8ea54389627 \
-    --hash=sha256:89cd468399cfd2504718f0ba50e410dca55a170b61a02ad92bb18c8a65186e93 \
-    --hash=sha256:8ad03c0965fb3c692200e74d458ca28c1dbb4ce96f9a479a8aa041ad5fabca02 \
-    --hash=sha256:90f9849678c75fe7afa2d348ac842c168b0a4d3d61919687216dfc547976d853 \
-    --hash=sha256:948424b06129ce883307e8cff868c31396d8dc7630a59c61d70d98dbe70f222c \
-    --hash=sha256:9cd5ffd25db4e7ba6a375693b3fc0fc1791ec636c17db3720da19bde7180ec43 \
-    --hash=sha256:a0df0043bdb289bde1f62da130d20df23d58b45429f752bc7a8fc5325a225ecd \
-    --hash=sha256:a2c306dea656c12c68f51f4cea133cbe78ca7435eb28c735eac1d3ebe73be6e8 \
-    --hash=sha256:a7830bab239b79cda9c08c2da014761cafb48da6150e1da17ac06283f43b6089 \
-    --hash=sha256:a7c711e21628b52034bb5ab8d1bce291f752fcc5e92accc615778acee1ff4778 \
-    --hash=sha256:aaf159caa35993cb1f56fb9b8e4610d35758e7ca005412eb1daa856a78c9c4b1 \
-    --hash=sha256:ae506e6902902557576a26ff33eda8695e7ecb3cb36c3b573a0765dee114ebdb \
-    --hash=sha256:b507f5c4c1d508876d1819b6bf9a49d365b96320b5d4993426b33a23ca4b8261 \
-    --hash=sha256:bf162abab1c1a736333192707cef898e735a5ca00f38f27eeedf44b39d9e85eb \
-    --hash=sha256:c1a2af6c6ef86344a6b0db6b97834208bf598db514f2b155042439b62605601a \
-    --hash=sha256:c2d37ab77531417474168eb79d6d80b14f821a966818505d03013d0833edb7a8 \
-    --hash=sha256:c4fc99836233ea196540b17ab0983aff60ed07941751930f5f4d05bc3b3b7359 \
-    --hash=sha256:d581b735e177fdcdce6fed8e7e8880a3fb6ee4e3653a3ac6af01c6f4c03effc5 \
-    --hash=sha256:d6da64deb6b8ed903e7560180a92f2d804ee1ba5eeb849ac2748b8c1aba1f6d7 \
-    --hash=sha256:d8e8286dd7cea7895157318d1b91cdacac64c479f3cbc8dce548331728484751 \
-    --hash=sha256:ddea102b48f9e339f3948bf22040944184627a30fdf7f858667673b9c5f033c8 \
-    --hash=sha256:dfa20cc6ca228e6b155b11da03825975ce66aea520985dbbddf0f2a5a495c605 \
-    --hash=sha256:e3e5193ef5a3dc73bceee50f7fdc2c90dbb76c42df8d8fae3d1067a583df579e \
-    --hash=sha256:e3eeb0aabd6bd5ce64faae67e9935203a6991b4bc2a485a767fbafb2c5125f45 \
-    --hash=sha256:e5805d5a22fd19c8ccff10a9561f9df94436b0545619ea579db2d3c35294bce2 \
-    --hash=sha256:e85b752a1e912b70eaad4fafbd4d1238007ab221de2009b9a2f5ae7461239895 \
-    --hash=sha256:eaf7fa2de5c0be8ae6ff8e9bea2ccd725e980541244521d8d4b5f3354a27babe \
-    --hash=sha256:ebfb099f8dcf083deef3ac1ca4c1503f387cf76296fcb3816b66f5ecb5f54fdb \
-    --hash=sha256:ece3d2cfe132e7d51f44a832b303895e6f2d499c5e74dfbdb06ee246147a304a \
-    --hash=sha256:ed9749eef4cbd126da3dc1d6bcb3a57f5eb7ac6a6484146bdbf743f552dfc577 \
-    --hash=sha256:ede83e07a75dd06bc501566c1eca2afc0d61677c1472ac9ad93fdee6e638a48d \
-    --hash=sha256:ef4aea96ce4d3b074422cb4f2f64e216bf9e213004bb58ecfdf50ea02ea8eb9a \
-    --hash=sha256:f3a3570c4a2a16746ac2c31a7c7c7b0c186b95ce902e33db6f28094ed7387dda \
-    --hash=sha256:f407cb6b8e9d6d8c626bc73c945db1706035af8fd632295547bf1c9e46d092d6 \
-    --hash=sha256:f74a575920ab21fe304421a3fc28793d82e299cae9eccb37084e9fc7f3617c20
+multidict==7.2.1 \
+    --hash=sha256:02009b402129a73e1f3da68f48eb999afbacd29f25aef0d5052b84ff5c2786a2 \
+    --hash=sha256:02d9c04d395a36eeebe89e45f2269614a4675b8e83fddcba15bba2be903971e5 \
+    --hash=sha256:03846be88267369908fcd9a91159358a3b142d740991c96e4f696d362fce516c \
+    --hash=sha256:08ea94663d9e7c25d14d78222f7aee906c472d4837766bec62477c38f6e419dc \
+    --hash=sha256:0c454b677214fa604e9c4a38952c685dc88a62c96f5576a7ce550f213d1dc318 \
+    --hash=sha256:0c52fdd8cb8194fcb6969a417149aa1d09d6e48b69fb1b34ee1b1e4cb51ec183 \
+    --hash=sha256:0c7b4d8cc9e6ae7070b8129bdb840215552d4e2689ca765d37eb208a24919209 \
+    --hash=sha256:0d852d3d9638f852158d7de7200dd77f7ff8d77fc8f3d396032f3d847883f631 \
+    --hash=sha256:0eb7fa012ab47b13e96bffc1369642f520adcc4e3d3e170d7f1a2b39fb953bce \
+    --hash=sha256:0ec95a02f9f08246cc7f1d85ac425e4d5c233fd3f098f5be1b2cca16aa690186 \
+    --hash=sha256:0f30d6eaf3cb309b6c21096c6c2b4cf3800f195a78b1babae85f481ce851bdc2 \
+    --hash=sha256:12bbab225ce7f69df75409ab8005b11b4e9309fae863821e019e81b32e53a2a8 \
+    --hash=sha256:13268013a3db11a214ccb6920f778d175b765f69a40509610b92e43602272718 \
+    --hash=sha256:15da10cf11fd8d8716720c95b93180e94c8317405d89d08524c579ef360128ac \
+    --hash=sha256:1d369ed297e79b417766327ece16bb7e89306c588df63c364a85d90d4aeac843 \
+    --hash=sha256:1fb8c1a3480c130c3a6422d5f16f3cad6552bf08c2089dd288ba7134649183b5 \
+    --hash=sha256:2022bd3194968a027f64ed16f9779e62e71a823a9df3971a7328c1d45dfeb9ab \
+    --hash=sha256:21d86f2aa58aa428fb9909d6b8587b75eea827287e3515b8506dca86b55e2c7d \
+    --hash=sha256:223427392fdf993e198644ec40c404fd93f1cd2a61328d18842ecbf154d02c82 \
+    --hash=sha256:2529873a3bf68c372532a9f8058bcf4199e78387e92cd6a01b73334bfe6a7e3f \
+    --hash=sha256:2592fb6c335d67f1912bf72788c02fd5dab305fc3c8c7eab078a5bec1aaa0f88 \
+    --hash=sha256:25ebc4208d9098f77caeb16df895a0e56eb6c3b22870ac4e3ec43e0a9d6a33b6 \
+    --hash=sha256:27166b6ec73eac37696d66b2c6efbd44b6d04b597d655070959df54dc7c71c0b \
+    --hash=sha256:27cc258247b13008742f0e239933ad01dec5ed4e6dfc63849e30e04e1aa5bc82 \
+    --hash=sha256:295a15ccb8cfde9351dd6062b80af4e839460636b3c46813b4aa443905ded86a \
+    --hash=sha256:2b4d0c4e13d329ffee73d46128e32dd3b4aeb2f9c6ac9c8a89eb28d3b82dcea8 \
+    --hash=sha256:2bac371da2c3554a99ba126f545e79ab8e8d9426a3e41df81d00ad725c1e2cbf \
+    --hash=sha256:2c4e6a97f79699f33e6dc13bddb5631781ee79a4a94c1822116d100e7d5c136c \
+    --hash=sha256:2d4cfbbb1023f0f6795b5395c400752fb23a5a09ba756aa9003886bbc47b3e12 \
+    --hash=sha256:2e279ad5a6e9347bc9e043fdbee180a0480c8fd52618c3258e983dd93d98ed49 \
+    --hash=sha256:2f3cf710144b1859f4128051cc27ea86eee83caac5648cf2ca0c1b835261cbbe \
+    --hash=sha256:30572b61c7932e4d3c2ad1e580de7db1f35b7a35d36db38f89397ce3f2e69096 \
+    --hash=sha256:335f715f8c111654f29e4bf19086bdf0245579d2b4f4f59ca8dd9b3003b859c1 \
+    --hash=sha256:363e5db93fc3f65f3218a79fe108d217b9d264181a4e993c77552bfe275d0393 \
+    --hash=sha256:36b868758fb11cfa748c788b793994e73660abec90f83c780a678539c2c468bf \
+    --hash=sha256:37b161535e92776788957a165fcf38a80b33c1efde7b18cab287db4e4574df78 \
+    --hash=sha256:3b7542fad2706595c1b1853b46f2c3c4ae5cc5a6252b7225f294d607a29e1bdf \
+    --hash=sha256:3ca4e2e9102d0788b94894a30a5e3561fd4818a0605d8748d8fe780f890aa069 \
+    --hash=sha256:3ca60708f0ca9d994f46790c5a5c774771e2f1dcb75b12c70a5582f915d0e721 \
+    --hash=sha256:3d22ebb716ac79bf32c2a1d15250f017faef719114af4376e8dd814d6633cf0a \
+    --hash=sha256:3d6fce7cc4ef63d9a7633cbae43e737798412805a4c3ba876cdf472dc6ff9c51 \
+    --hash=sha256:4b338b45dc26ca4bac702e1278754f78613d4d0081e14e94e44fe8e261bf1750 \
+    --hash=sha256:4bebc9587cc29359e3b045518a7a09264fa882a7d165b0d143fdac8eeb7ea948 \
+    --hash=sha256:4d61be3725016ef5db3543c95f1f062d7d150ba776582d959a982af88e75fa55 \
+    --hash=sha256:4eb2650aa240b62ab0c6d87238bee5d14aa4d411c0d69ad61be53e026e0785ba \
+    --hash=sha256:4f31ddf9c00e0e7db848b0236c717acbe8a51954d0d31b4d908c538ab3f0f5bc \
+    --hash=sha256:522f7d2351743804cdf5c5a304bc45f9d55e935dd87706fae2dbeafe0fed0b49 \
+    --hash=sha256:5324411117bdb67cfaeb3d1d28fb783710fcca3d88b855696af99044d7219e4b \
+    --hash=sha256:554ee1d2e71fb5b4059c0c4ee35d8cbc8af2a3147036d65a454c53fea07ff4eb \
+    --hash=sha256:57ac987ec5d26d89bbc48c03e486f659e1367d425c465552ac2e4c4af8219def \
+    --hash=sha256:57b5d0df4c60ab8b1159687610a1c3ae069ad2380d390a79dedff5c82318e714 \
+    --hash=sha256:584ebfa26c9dcf3e465637a5a9afa2647bebb3022b50b1ff384834ba8e0380d1 \
+    --hash=sha256:5a7df927c7999d1d3196176a8d4139d3a0e1765936f5de8c768097275b2d617a \
+    --hash=sha256:5b944091cfa7da4f7a9bd2587569cd90c94b89ec4721f8e87fe62504f2432b67 \
+    --hash=sha256:5deadf03fb4a7842696d551f9f9a06dd4445bb43ca06b5f9736e4e1885561333 \
+    --hash=sha256:5efddcdbcb73f5485dca2b6624edc8ee063604b77bd3a3eb772826063965819f \
+    --hash=sha256:65e4448dadc7c94a8643bb41361e45f3a73d46e36a008a9bc03e9b525f4d7c80 \
+    --hash=sha256:66af55b07e4593790157e85f897f06983ded8a8692cb2fb048f3049c1d3fa172 \
+    --hash=sha256:678ac791b5820d9346eb13c8515fe0c9383659335e5cfc544bf6f54714ca1939 \
+    --hash=sha256:68b97b721d95b77d75e718d1b62a227fa4b3e647bd2a9fb39552d1a79ffb67c0 \
+    --hash=sha256:6966806cf917cbbeb9a8b5c581db52e19c9af0ef5fe009db54c1f5799a6e003f \
+    --hash=sha256:69befda4b1ef57027ea95dc6ed733568642f330fb3203a3e5c5ef107d41e0a1f \
+    --hash=sha256:6e22756c6e2d4f57ead0d2e6be179d8a16d661bee424b81de0c6c0c1305ec39f \
+    --hash=sha256:6efdeed2723431999cf3bcbc84c72dbe0f65d16bb1f84e15a657f5b60ff18ca6 \
+    --hash=sha256:714fe5f3eabd153b1b6911d0b5d31cfc2b808ae6b9e59a32fab17a4e6cdad5a6 \
+    --hash=sha256:7238f7135481926d52a94c18a8cca633a9e72c1cbfccd5796548298a479b0656 \
+    --hash=sha256:74d3e015c28b43b6c1a108eec324ea2efb185c359c459216cabd4cb98f7f02f6 \
+    --hash=sha256:76a4f5132b8dc29eb3c768ee9b47e132a1d24fbc2e9259854c01af9beaff1d49 \
+    --hash=sha256:7726c53b1d59eb57b009a9e8759d4f71049ebdacf30642a198a197f80cea451c \
+    --hash=sha256:781ca5dfc2f1d58e47f52216a0c1c7e1ba91ce8aa235459e20de2d402af77fb3 \
+    --hash=sha256:785ef2f3e372dabc131f228a275f97eca92ad17cfab1ab138790e330d99abe3e \
+    --hash=sha256:7cb1a6bb70edcc06ea65cb9a35654f268ee39d9fc3a52240e6ba074db4d9c99e \
+    --hash=sha256:7fb3bc8d58e1b7c1d9fa1d995e30a4ce9dbe49f4c63c755a1ffdecdfbd026ccb \
+    --hash=sha256:8148c2aaaf4b85d7872f024c8bb0c9b9797cc76b10588e3594a69cb01057472a \
+    --hash=sha256:81a5f84a76401c4330e6db4e170dddd58860b30c4e8a44a181e5c2809c7f9c9d \
+    --hash=sha256:81c6fc88ac9bf6920a0cdf22d3c383964167f12d35eb630463fc6d5ac89e460d \
+    --hash=sha256:822a7fcd33f6922b650e1b26594f09d53c5d011fe655fea7ded27b2728ce2a1b \
+    --hash=sha256:83fbd7cfaca614975efdbdcd9e2df45f3e987e819216468fb73e1db6f0365b98 \
+    --hash=sha256:846b17193f1c373d6f05ada894fadf56bce2473067caea0aab51828849894b31 \
+    --hash=sha256:8648dd5dc4d5db32b5936dc5e85e9a4d79db1135513d40d1f54ca15503750324 \
+    --hash=sha256:873d35366cc115be02a1c858f9b22a1a9f6182b99aab2171ee5276af02a153e3 \
+    --hash=sha256:8c3ff4f5c376df7126695a52af61e6084b69c9e52dcb9f4713e71ce9819e1bfd \
+    --hash=sha256:90efd90a0f9b7ae3844a4fb3ae614321832d364ae19567b7cd312315fac4ec39 \
+    --hash=sha256:9306e0c5595f91874e685be0a9eb743d48ba069c888eea051bec3c67c08b5b8d \
+    --hash=sha256:987f65f6c9321402bc7012f6c6d09ba501b88ddb1640f5b0b4a19f2caafe24a5 \
+    --hash=sha256:9a53776adc1ba923c9e345fdea7b61553c44c17a9af5eba8d8def8c5dcac4dec \
+    --hash=sha256:9c44bd978adddf39df5834c6a1efd7d075c84769a7a084168d035a2a276d9008 \
+    --hash=sha256:9c9f285f788acf2448a57c9b93d31103ac69bd03f92907e2ffbb23c4e2b42eb6 \
+    --hash=sha256:9df532dd12c59a7a4d381646fc1bf5ccb4bcdbd01c0887d07ec769fae965ea9a \
+    --hash=sha256:a0f999155c22c8929cc492949c08c6fe7ec8079a5e1bfdeb34b9a3e4991959d0 \
+    --hash=sha256:a2a322c8a6ca82a5a67ae6542e9c6a13ded9045cfd171dcccc5c213ac4fe0eab \
+    --hash=sha256:a3d28ac22fe658ad7486d1532b3a9084fbf65b428db31f47212c5b0b6da826f1 \
+    --hash=sha256:a3d9a59bcdf8531d46b56bcd512017533510c25e955c2c546efd0743bd840940 \
+    --hash=sha256:a789e3d27fc5665cc0477f10a35a89383313e4c9cf8b5e6af7ea71f039cdcc0e \
+    --hash=sha256:a7d120bdde5b213e67ed7dc80ea3adf4f014453fbc20195d619ba2ceb34084f3 \
+    --hash=sha256:a878fef2797a7c082aa47559af68299372edebc7367bd5128dff2d36e6d820e1 \
+    --hash=sha256:a92e3080d8889b0f7a80ea0c4a72181b4d4d5d3918a03136b4a459f51f5f59da \
+    --hash=sha256:a9cc121b5ee2c8b4bd4b6b526d5a26bb782f4d620463f73707691b2004b8c349 \
+    --hash=sha256:b4821bd30b38144d8ab75df56af0b07e9d71327c9cf94c0c7a1965f865bb9615 \
+    --hash=sha256:b5fb6b048931ea925b484f0c7c01b007981415a00a6c62ee74bbf8d229d39c08 \
+    --hash=sha256:b63acdf4df5a78a15223bbb510bb3e0f8234dfa807610ccb8796d0842db2c801 \
+    --hash=sha256:b81ff0f2d375988152614eaea4d5023c98ecb08f77df4bb1d96762504bb86fca \
+    --hash=sha256:b97bffa5772b7e853303de094829fcd3a9bd49fddd70534651ee4933691f6587 \
+    --hash=sha256:ba5e8d9310a794b853fb0e327d46a827b5b015576341219a591f88ed9d799c27 \
+    --hash=sha256:bc9decb36abd00ed5d123db9df70eb9a0da45d6376d86d64f4a94bfd5a1b83fe \
+    --hash=sha256:c10ac5e3e76837180656079008f71add8339b00c3c26314092bcd1e8e449049f \
+    --hash=sha256:c753b820738cddc097892fee95e7cd716fbdfc9640414c5e9ce9463ad125321b \
+    --hash=sha256:c85a0a54a19429a17ef449e967baffe7b5089cb4f6ef2894c9168a69fa024d05 \
+    --hash=sha256:cadd02ca804d6ebe799a7af19197d9730094fe2cc74b70eb4f374f4b8c1886c1 \
+    --hash=sha256:cb43bb34346155d479acdc5423afccdff79ce1fc66adfcc9de995cbec8a13acf \
+    --hash=sha256:cb7fc8820b206932ec6d8f8985aeba6edfd2932e13b6c4bf2434d6bcbbeef3e1 \
+    --hash=sha256:cba29f12cd717f1cbbe220edf005666f8df0453347217748331a0c2f7522eca4 \
+    --hash=sha256:cd69c99affd1b4debc1f9a53058ea6e3a9b34f2e733840bb45891666cd8ede0a \
+    --hash=sha256:ce0f884408938fbd72e764031d0e23a8f5e438a7bf73641089c7a6465cb84456 \
+    --hash=sha256:cecb2c778f00a65c6ca01410dd194d0e797a9eebb7c6dea0db87718719f293c7 \
+    --hash=sha256:cff7657e79224dea46f2f2e58eb99186656ca63ebe356212210c5c00e9beb814 \
+    --hash=sha256:d0381074dc21225951278d7e4a7a2241f7fb86a4d8b94154dfee1411f49cf851 \
+    --hash=sha256:d094951489bb7836342c005e790bd005e60b669aaf5c936b96dd5d68cbd2e23b \
+    --hash=sha256:d10e49b940e70e2a4e91f44098007dda0bacb78c3f8e31ba7a37ee2ce52269e6 \
+    --hash=sha256:d37773029ba034a2cc970b6eeb67dad3bff9d894393c51f6bb1c6b4f563a032c \
+    --hash=sha256:d4af0d863e72f3ea48e85d3aa1d1b426fd81e9544fd7976fc6d6753584a25b03 \
+    --hash=sha256:d5738cd929f2af8651ebb284467acb58b1ec0f2f4d42489cd0597172bc82e15b \
+    --hash=sha256:d615377a8e7bfc4f1983ede3f411c2ac2b0f7c3053f262d0437b7d8bcc4485e3 \
+    --hash=sha256:dbda2baafe08f8431fd3333be02c261023fd454607e3bde5e7dc00565f7bebcb \
+    --hash=sha256:dc6f3dcb08c4b41e64f2d6cf272b5686d9144db585b2e138a8b1664376ab3921 \
+    --hash=sha256:e0f2b33a6ae233f4da38c77ea32f90aab2cb82ba819d7b6c4f1b68cd33d871b6 \
+    --hash=sha256:e47d058c2db95010f5d2e1f6037acebdfb0e2fa4507650e1041437985c91db38 \
+    --hash=sha256:e64b86d16158954825d12799271979c6944c1fd1d03575b2f22e869c3f7d00dc \
+    --hash=sha256:e8af3e6f1bdbc31fd762b094133b478b89988eaebc63cbe82b1d9e3bbd15cede \
+    --hash=sha256:eb5c4a5b1281985271b6c29be53f2c1a9decf11e30a0e2733439c4d9d61b9ebb \
+    --hash=sha256:ec4ee5d2d624088775e61cada87bbe7629bfd936bfbd57f122a106970d8ab1ee \
+    --hash=sha256:ed6c107642a9acaa7ede32dcd428a6c87e302c5d555ecd3ec132ffa8c6155b4b \
+    --hash=sha256:edffdb3950d3a8b769ddaec3a0962fb7b76b3c96f317f6b88500455a537dded2 \
+    --hash=sha256:efe695cc2081633b02fcb95bc1b13070f6647c9ad52d42a8beeb3c2a7ea062dc \
+    --hash=sha256:f07f06db2e333b68dd52560b8b0b12b6f8bf6053cedebf9af4aecfecd2dc1b32 \
+    --hash=sha256:f15205c67d4c45250fcff5da077f0ae54102b5bc39e9ee8bab90d99e09a728c5 \
+    --hash=sha256:f2087ee23a18d1d618a135eedcafba7dfc40c6be4e8e52d7f29a1c8a2344cfcc \
+    --hash=sha256:f278f118f9fdb5faba5a6792be397fbda094d1568efa4dfe8c3595ce4ce89eea \
+    --hash=sha256:f29885fef157a602d1816439e5da964c70ebcdbbcd4bb9d2d21b7e8bb5636604 \
+    --hash=sha256:f2cc27ec6a53b1d39bab44d2b9dd21cc31e796d01b5e18a76d569721282bb264 \
+    --hash=sha256:f332b16911ffc668baec6aaf8f08a09e1af34a8ee87ccac26bd722589e264645 \
+    --hash=sha256:f5812cfcf7daf3ace5fedf6e2ef8d4b342c92fb8ea3a87c1aed2b50453271093 \
+    --hash=sha256:f62172cf387e92f4928b60e5936b02c06e3c8449ed7fb440978d6c9bcbfc85df \
+    --hash=sha256:f9c118e866164ce05498d9106a4bd01e745321403cd6f0b77a0b2587768f8c06 \
+    --hash=sha256:f9e78d98a29e969a001e953eb09167a48bbc71249e804dae5db987ee7e6531c9 \
+    --hash=sha256:fa0ecd064b0ae18d235283abb5adbc4e07304dba8f2aa7c0d61f28bebcc70d4c \
+    --hash=sha256:fa949c81e3865c10f981dea72fd8d418b59edd13a047a0aee89ae64790113d53 \
+    --hash=sha256:fba33e264cdd2ec43b762b9960d1648478eecfc1ce6e8159e7573510f0412c0a \
+    --hash=sha256:fc45ff19520bc5321dcd9c6dd7df6f35ddd894eed35e5be65d1828a9c3f5e7fb \
+    --hash=sha256:fcfebcb537f419e415b6e2bfc77ddbd33abe3c036f0105410a25a14741df9c31 \
+    --hash=sha256:fd24c4425fdb8e822601335602375c6d0cb020f7a368e1d5842eb7925a9c8748
+numpy==2.5.4 \
+    --hash=sha256:067374eb538c34c745436365cf7b0112595c1d326f21ce4ff340f61230239fbb \
+    --hash=sha256:0b4724a19de67bea8cfc4970798efa78bcbbe2ac2613cfac16721a42d44de2a5 \
+    --hash=sha256:0f02a46e49cfb6c73bdb7aea1c0d3461dbae9aba613542b65f657cd3d17b9fab \
+    --hash=sha256:1c2e71b04c6cad90026e544501bbe0ab9290fa8a4d845e7e8c0d124fb429c988 \
+    --hash=sha256:1ef3aa6d7e29bb13677323114280b05acc57607fa2300e66432d665d5418a162 \
+    --hash=sha256:2132418bf8dd124a427ca9e6a1daf9ee1a87185344c95119ceae868b99466da1 \
+    --hash=sha256:2199ed071f460487c8db2c0e5c0b564494190edb4772fe80f9aad88b2604def5 \
+    --hash=sha256:2377da2dd3ba2c1200956acbab2a358c83b8e1f8531191672d1cd6ad83250d53 \
+    --hash=sha256:298eca75243f2cbbfdb460560b9fb2a1792a33cf2ab4286efd43d92e8d3df508 \
+    --hash=sha256:2c2c4afffdeb7920e445028dd71eb932cac3e704792e964bc2a232426d4f1255 \
+    --hash=sha256:2ca144f15135b6212a5c47b1e2aeca6e412f102f95a2d5d88d8aec77eb255de3 \
+    --hash=sha256:2fa3328f784fc8277fc48026f6cad516f5c561c5d8e2e39b3c9e0c8f23223b34 \
+    --hash=sha256:325518d4245b9e331387702aa58c2ce1dc4cdcbb41dfb4ccd5dcbc7e08db1266 \
+    --hash=sha256:332f3378fe077dd850e677ec01bdcc4f22368fb5d50ef10b2c79230b1bf5a592 \
+    --hash=sha256:3573cd22564692a5b899ec344e5d5b9cc4576f2985b96f22af3564ed54f2710f \
+    --hash=sha256:381a7a3d2e65e64c0ec302795ab9dc12bb1e73f150904699c153716177eebdaf \
+    --hash=sha256:38f47be9f74ab870d2633b5456ae519c43758a8d1fd05342f0ce4ecc034396ee \
+    --hash=sha256:4054173604cd8658796053f1f3bc0befb68ec1c0762c57fdad61e199256a8617 \
+    --hash=sha256:468397ba3c64427474706e5c9123fe266395496714dc684294eac75cd4930d1e \
+    --hash=sha256:4e263278bfb5ee6409db8aedbc4cc32973b1b82bc1e8d3c668551d04d83a7e37 \
+    --hash=sha256:5258bc06526964be5face2fc6f756857a3f24f21ec3e72ca131337a75b165d6c \
+    --hash=sha256:56733449d2544178beaa4545cee357370440cf056c197f9c7bfb19dbfdd0e86d \
+    --hash=sha256:5ec3753760c1a6d8bb91200666e545c3a9728e6269dfb5d6ce02340996698aa3 \
+    --hash=sha256:5fbf7141bbfd63aea22f435c9062a032b9ea0082fe9845dad7f021d3f1234e71 \
+    --hash=sha256:64d1c8ac28a4077cf987e0a71a7a0ef7e2df70722f07f0baa42dbb7eb6938647 \
+    --hash=sha256:64f9c9878c1938476365e11ccfb6b770f3b9e5f045ccddc514235041e6959365 \
+    --hash=sha256:6c109eac9cd439193678f69d70733c1108487546ca8eafc107b510ae10c1aecd \
+    --hash=sha256:6d6a71b9d9a97c03633aa12565ef2825ffa036cc1d99cfd50dacf0f128af4fe2 \
+    --hash=sha256:6ffa07666f8da0eef81d149934a626d0d95fbd6838432a33e66245423a9062c0 \
+    --hash=sha256:7415db95818b39ec475a5eea54d9e3b6bc83e3912158e46da3438cdce399804d \
+    --hash=sha256:77045a4b175bbf5316ec08003880804336c78f92281a1b72222b274ea85ec5ac \
+    --hash=sha256:7a14a461d9340f1b46b8648578aed9cdb8b3b018a8fac6c1dde2c9192a01a87f \
+    --hash=sha256:80d6ef6e8620eb2c2b4c4caad50b5935d6db3cde2d51581b55dcc79e14016d1d \
+    --hash=sha256:81e3420b27048b65eb14c3acf0c174a8cb0e023277716110347d2dcb26026dad \
+    --hash=sha256:823874a507a84af050493b622affde94b6f7c3a0dc22cb2801381bc03b871c00 \
+    --hash=sha256:8b4d2fd2d34e5f8c9235ee787de5631a37a28402b15cb80814df973d2be54129 \
+    --hash=sha256:8dddfbee2e68d26d0d7d7d9cb247b1fd4409241cce32d815a11d97ec2cfde179 \
+    --hash=sha256:950ea81d57ef070665581b6e1b5f6a029306423cd1739c5b95fe78aa30db6b9d \
+    --hash=sha256:956555e0603a4d38019ae6925711cb9dc43195c076a928accf7ea5d50bddfe53 \
+    --hash=sha256:98b053943e5a0474ec0da309d2cb9d3f18ea57f8a2067c2ab7b5f763d1068380 \
+    --hash=sha256:9968ab7e49b93ac6e1c3b2239732183152c9150f16308d30b66a372cffe3483c \
+    --hash=sha256:9a94cf751c9ad8ebaa835bcd3d40dacf8534ad086b88c38029b65123c7999d2a \
+    --hash=sha256:9cb18a327b49c5c337f972b03682f6a49855525faaf3c0d3e9c96cd0fd8880a8 \
+    --hash=sha256:a7b1b6353e36a7e50de2973a38d705c88ee93adcf120673cee7f45a4a3fa223a \
+    --hash=sha256:a813ed7719bf45463c51779e6a98d0385fe905e48447526938a4b8337333d551 \
+    --hash=sha256:aa1cce2ff3f8d953de38b76bf44602caeb69f101430208f64a10067f7cb4b1d3 \
+    --hash=sha256:ad62a416ddcf863bf44bba76fbf6b53366ab0692e294f51cae4b5fbe0d246788 \
+    --hash=sha256:aec3fc4b32ff82421274f5d205c559c51c840c8df66a78efd7f3612dd005a26a \
+    --hash=sha256:b1185012870173de7ae33d370bd45b1cf5baee747ea4b97036b65f4e93016877 \
+    --hash=sha256:b11e8fda06a7d69f15ebf542660b74466c2e51094800c1fb794f47ad4faeef17 \
+    --hash=sha256:b64a85f40e154983960a4167d4c1d57a50c7f109b3d3264a3a984154e90a8454 \
+    --hash=sha256:b86966fbe4ad7de710422175572bcdc75fdedadfb54bc6fab7deabccddd7780b \
+    --hash=sha256:b89d0aaae2fe498c648f4c4795c084db535af5bd98ef942b2a3681fb74ce8645 \
+    --hash=sha256:bc39ac66a7a9a3fbd6134fda43136b60ffde99c8f4501e64e0d2b24da137babf \
+    --hash=sha256:c05ede731b03fb1b7591faca9389ade3267d2bddf1ad8882bb3f2cc5e101694f \
+    --hash=sha256:c6342f54c67093cae5c0227eb0eb772fdb79f2a2c37a6eb278b9909ee06aa356 \
+    --hash=sha256:c668b2f0d651605b58892644b0e302c7157f7159544227758c896982ef384b18 \
+    --hash=sha256:c9b80cdf5cedba0e90d93fa5f9a333c4d65bd545cd669b71bb97ce2b703c9d73 \
+    --hash=sha256:cfd73180400042a7c532d30c5e287bdd03c59ff9ee1b4c0316af0539e29dfe23 \
+    --hash=sha256:d4cccbbc78717966f764cd3af4fb70276fa01fc7a2688af11c78901fa5c04f05 \
+    --hash=sha256:d549420b8858885cea8838a727842249218b9c1da24dd517e25c9c7a948310a3 \
+    --hash=sha256:d8200f16437b289a5bb927c6e184eccc3e8389bc0070fea4cd5b9e13c1757959 \
+    --hash=sha256:e94aef2c639da4a960ad0db8e06471208d8589974953d78b61d345b4eb99e394 \
+    --hash=sha256:fbde6962867ee75b48b0ee29b2b9372ec5d617799dbaf38e82dc0596f2f7738a \
+    --hash=sha256:fe4d21ab149f15e4e6043dfb0de87e6e5f34ac176cde83060e9802981fca2ac2 \
+    --hash=sha256:ffa6ce09a1c6a08e9667dd9c97aa0b14184e8d18f2a14b78b2a2328c9147f076
 propcache==0.5.4 \
     --hash=sha256:004e685b315646c410771836e72a44f143bbe624f29653a42687815069a303d5 \
     --hash=sha256:02c0a34f16889cf800f10f0247a564d8ce6eeab6ffcd7c87198f769067eb8432 \
@@ -713,123 +688,145 @@ propcache==0.5.4 \
     --hash=sha256:f85915e00dcb1cd9f2f890ead064ed40a27df06f0db65be427b29482ae357572 \
     --hash=sha256:fc2461ecc45f17893f8207e73b46ea8ba93e33630e51cf4af3fbc21d47462b1a \
     --hash=sha256:ff6b113f50bc066a698db5d944d2c6dc7507168dd3341e255a8892fd0715a558
-pyyaml==6.0.1 \
-    --hash=sha256:04ac92ad1925b2cff1db0cfebffb6ffc43457495c9b3c39d3fcae417d7125dc5 \
-    --hash=sha256:062582fca9fabdd2c8b54a3ef1c978d786e0f6b3a1510e0ac93ef59e0ddae2bc \
-    --hash=sha256:0d3304d8c0adc42be59c5f8a4d9e3d7379e6955ad754aa9d6ab7a398b59dd1df \
-    --hash=sha256:1635fd110e8d85d55237ab316b5b011de701ea0f29d07611174a1b42f1444741 \
-    --hash=sha256:184c5108a2aca3c5b3d3bf9395d50893a7ab82a38004c8f61c258d4428e80206 \
-    --hash=sha256:18aeb1bf9a78867dc38b259769503436b7c72f7a1f1f4c93ff9a17de54319b27 \
-    --hash=sha256:1d4c7e777c441b20e32f52bd377e0c409713e8bb1386e1099c2415f26e479595 \
-    --hash=sha256:1e2722cc9fbb45d9b87631ac70924c11d3a401b2d7f410cc0e3bbf249f2dca62 \
-    --hash=sha256:1fe35611261b29bd1de0070f0b2f47cb6ff71fa6595c077e42bd0c419fa27b98 \
-    --hash=sha256:28c119d996beec18c05208a8bd78cbe4007878c6dd15091efb73a30e90539696 \
-    --hash=sha256:326c013efe8048858a6d312ddd31d56e468118ad4cdeda36c719bf5bb6192290 \
-    --hash=sha256:40df9b996c2b73138957fe23a16a4f0ba614f4c0efce1e9406a184b6d07fa3a9 \
-    --hash=sha256:42f8152b8dbc4fe7d96729ec2b99c7097d656dc1213a3229ca5383f973a5ed6d \
-    --hash=sha256:49a183be227561de579b4a36efbb21b3eab9651dd81b1858589f796549873dd6 \
-    --hash=sha256:4fb147e7a67ef577a588a0e2c17b6db51dda102c71de36f8549b6816a96e1867 \
-    --hash=sha256:50550eb667afee136e9a77d6dc71ae76a44df8b3e51e41b77f6de2932bfe0f47 \
-    --hash=sha256:510c9deebc5c0225e8c96813043e62b680ba2f9c50a08d3724c7f28a747d1486 \
-    --hash=sha256:5773183b6446b2c99bb77e77595dd486303b4faab2b086e7b17bc6bef28865f6 \
-    --hash=sha256:596106435fa6ad000c2991a98fa58eeb8656ef2325d7e158344fb33864ed87e3 \
-    --hash=sha256:6965a7bc3cf88e5a1c3bd2e0b5c22f8d677dc88a455344035f03399034eb3007 \
-    --hash=sha256:69b023b2b4daa7548bcfbd4aa3da05b3a74b772db9e23b982788168117739938 \
-    --hash=sha256:6c22bec3fbe2524cde73d7ada88f6566758a8f7227bfbf93a408a9d86bcc12a0 \
-    --hash=sha256:704219a11b772aea0d8ecd7058d0082713c3562b4e271b849ad7dc4a5c90c13c \
-    --hash=sha256:7e07cbde391ba96ab58e532ff4803f79c4129397514e1413a7dc761ccd755735 \
-    --hash=sha256:81e0b275a9ecc9c0c0c07b4b90ba548307583c125f54d5b6946cfee6360c733d \
-    --hash=sha256:855fb52b0dc35af121542a76b9a84f8d1cd886ea97c84703eaa6d88e37a2ad28 \
-    --hash=sha256:8d4e9c88387b0f5c7d5f281e55304de64cf7f9c0021a3525bd3b1c542da3b0e4 \
-    --hash=sha256:9046c58c4395dff28dd494285c82ba00b546adfc7ef001486fbf0324bc174fba \
-    --hash=sha256:9eb6caa9a297fc2c2fb8862bc5370d0303ddba53ba97e71f08023b6cd73d16a8 \
-    --hash=sha256:a08c6f0fe150303c1c6b71ebcd7213c2858041a7e01975da3a99aed1e7a378ef \
-    --hash=sha256:a0cd17c15d3bb3fa06978b4e8958dcdc6e0174ccea823003a106c7d4d7899ac5 \
-    --hash=sha256:afd7e57eddb1a54f0f1a974bc4391af8bcce0b444685d936840f125cf046d5bd \
-    --hash=sha256:b1275ad35a5d18c62a7220633c913e1b42d44b46ee12554e5fd39c70a243d6a3 \
-    --hash=sha256:b786eecbdf8499b9ca1d697215862083bd6d2a99965554781d0d8d1ad31e13a0 \
-    --hash=sha256:ba336e390cd8e4d1739f42dfe9bb83a3cc2e80f567d8805e11b46f4a943f5515 \
-    --hash=sha256:baa90d3f661d43131ca170712d903e6295d1f7a0f595074f151c0aed377c9b9c \
-    --hash=sha256:bc1bf2925a1ecd43da378f4db9e4f799775d6367bdb94671027b73b393a7c42c \
-    --hash=sha256:bd4af7373a854424dabd882decdc5579653d7868b8fb26dc7d0e99f823aa5924 \
-    --hash=sha256:bf07ee2fef7014951eeb99f56f39c9bb4af143d8aa3c21b1677805985307da34 \
-    --hash=sha256:bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43 \
-    --hash=sha256:c8098ddcc2a85b61647b2590f825f3db38891662cfc2fc776415143f599bb859 \
-    --hash=sha256:d2b04aac4d386b172d5b9692e2d2da8de7bfb6c387fa4f801fbf6fb2e6ba4673 \
-    --hash=sha256:d483d2cdf104e7c9fa60c544d92981f12ad66a457afae824d146093b8c294c54 \
-    --hash=sha256:d858aa552c999bc8a8d57426ed01e40bef403cd8ccdd0fc5f6f04a00414cac2a \
-    --hash=sha256:e7d73685e87afe9f3b36c799222440d6cf362062f78be1013661b00c5c6f678b \
-    --hash=sha256:f003ed9ad21d6a4713f0a9b5a7a0a79e08dd0f221aff4525a2be4c346ee60aab \
-    --hash=sha256:f22ac1c3cac4dbc50079e965eba2c1058622631e526bd9afd45fedd49ba781fa \
-    --hash=sha256:faca3bdcf85b2fc05d06ff3fbc1f83e1391b3e724afa3feba7d13eeab355484c \
-    --hash=sha256:fca0e3a251908a499833aa292323f32437106001d436eca0e6e7833256674585 \
-    --hash=sha256:fd1592b3fdf65fff2ad0004b5e363300ef59ced41c2e6b3a99d4089fa8c5435d \
-    --hash=sha256:fd66fc5d0da6d9815ba2cebeb4205f95818ff4b79c3ebe268e75d961704af52f
-scipy==1.17.1 \
-    --hash=sha256:010f4333c96c9bb1a4516269e33cb5917b08ef2166d5556ca2fd9f082a9e6ea0 \
-    --hash=sha256:02ae3b274fde71c5e92ac4d54bc06c42d80e399fec704383dcd99b301df37458 \
-    --hash=sha256:08b900519463543aa604a06bec02461558a6e1cef8fdbb8098f77a48a83c8118 \
-    --hash=sha256:131f5aaea57602008f9822e2115029b55d4b5f7c070287699fe45c661d051e39 \
-    --hash=sha256:158dd96d2207e21c966063e1635b1063cd7787b627b6f07305315dd73d9c679e \
-    --hash=sha256:1cc682cea2ae55524432f3cdff9e9a3be743d52a7443d0cba9017c23c87ae2f6 \
-    --hash=sha256:1f95b894f13729334fb990162e911c9e5dc1ab390c58aa6cbecb389c5b5e28ec \
-    --hash=sha256:200e1050faffacc162be6a486a984a0497866ec54149a01270adc8a59b7c7d21 \
-    --hash=sha256:2040ad4d1795a0ae89bfc7e8429677f365d45aa9fd5e4587cf1ea737f927b4a1 \
-    --hash=sha256:2b64ca7d4aee0102a97f3ba22124052b4bd2152522355073580bf4845e2550b6 \
-    --hash=sha256:2ceb2d3e01c5f1d83c4189737a42d9cb2fc38a6eeed225e7515eef71ad301dce \
-    --hash=sha256:35c3a56d2ef83efc372eaec584314bd0ef2e2f0d2adb21c55e6ad5b344c0dcb8 \
-    --hash=sha256:37425bc9175607b0268f493d79a292c39f9d001a357bebb6b88fdfaff13f6448 \
-    --hash=sha256:3877ac408e14da24a6196de0ddcace62092bfc12a83823e92e49e40747e52c19 \
-    --hash=sha256:3fd1fcdab3ea951b610dc4cef356d416d5802991e7e32b5254828d342f7b7e0b \
-    --hash=sha256:41b71f4a3a4cab9d366cd9065b288efc4d4f3c0b37a91a8e0947fb5bd7f31d87 \
-    --hash=sha256:43af8d1f3bea642559019edfe64e9b11192a8978efbd1539d7bc2aaa23d92de4 \
-    --hash=sha256:45abad819184f07240d8a696117a7aacd39787af9e0b719d00285549ed19a1e9 \
-    --hash=sha256:4b400bdc6f79fa02a4d86640310dde87a21fba0c979efff5248908c6f15fad1b \
-    --hash=sha256:4eb6c25dd62ee8d5edf68a8e1c171dd71c292fdae95d8aeb3dd7d7de4c364082 \
-    --hash=sha256:581b2264fc0aa555f3f435a5944da7504ea3a065d7029ad60e7c3d1ae09c5464 \
-    --hash=sha256:5cf36e801231b6a2059bf354720274b7558746f3b1a4efb43fcf557ccd484a87 \
-    --hash=sha256:5e3c5c011904115f88a39308379c17f91546f77c1667cea98739fe0fccea804c \
-    --hash=sha256:6609bc224e9568f65064cfa72edc0f24ee6655b47575954ec6339534b2798369 \
-    --hash=sha256:6e3dcd57ab780c741fde8dc68619de988b966db759a3c3152e8e9142c26295ad \
-    --hash=sha256:6fac755ca3d2c3edcb22f479fceaa241704111414831ddd3bc6056e18516892f \
-    --hash=sha256:744b2bf3640d907b79f3fd7874efe432d1cf171ee721243e350f55234b4cec4c \
-    --hash=sha256:74cbb80d93260fe2ffa334efa24cb8f2f0f622a9b9febf8b483c0b865bfb3475 \
-    --hash=sha256:766e0dc5a616d026a3a1cffa379af959671729083882f50307e18175797b3dfd \
-    --hash=sha256:7bdf2da170b67fdf10bca777614b1c7d96ae3ca5794fd9587dce41eb2966e866 \
-    --hash=sha256:7ff200bf9d24f2e4d5dc6ee8c3ac64d739d3a89e2326ba68aaf6c4a2b838fd7d \
-    --hash=sha256:844e165636711ef41f80b4103ed234181646b98a53c8f05da12ca5ca289134f6 \
-    --hash=sha256:8a604bae87c6195d8b1045eddece0514d041604b14f2727bbc2b3020172045eb \
-    --hash=sha256:94055a11dfebe37c656e70317e1996dc197e1a15bbcc351bcdd4610e128fe1ca \
-    --hash=sha256:95d8e012d8cb8816c226aef832200b1d45109ed4464303e997c5b13122b297c0 \
-    --hash=sha256:9cdc1a2fcfd5c52cfb3045feb399f7b3ce822abdde3a193a6b9a60b3cb5854ca \
-    --hash=sha256:9ecb4efb1cd6e8c4afea0daa91a87fbddbce1b99d2895d151596716c0b2e859d \
-    --hash=sha256:a3472cfbca0a54177d0faa68f697d8ba4c80bbdc19908c3465556d9f7efce9ee \
-    --hash=sha256:a4328d245944d09fd639771de275701ccadf5f781ba0ff092ad141e017eccda4 \
-    --hash=sha256:a48a72c77a310327f6a3a920092fa2b8fd03d7deaa60f093038f22d98e096717 \
-    --hash=sha256:a720477885a9d2411f94a93d16f9d89bad0f28ca23c3f8daa521e2dcc3f44d49 \
-    --hash=sha256:a77cbd07b940d326d39a1d1b37817e2ee4d79cb30e7338f3d0cddffae70fcaa2 \
-    --hash=sha256:a9956e4d4f4a301ebf6cde39850333a6b6110799d470dbbb1e25326ac447f52a \
-    --hash=sha256:adb2642e060a6549c343603a3851ba76ef0b74cc8c079a9a58121c7ec9fe2350 \
-    --hash=sha256:beeda3d4ae615106d7094f7e7cef6218392e4465cc95d25f900bebabfded0950 \
-    --hash=sha256:c80be5ede8f3f8eded4eff73cc99a25c388ce98e555b17d31da05287015ffa5b \
-    --hash=sha256:cc90d2e9c7e5c7f1a482c9875007c095c3194b1cfedca3c2f3291cdc2bc7c086 \
-    --hash=sha256:cd96a1898c0a47be4520327e01f874acfd61fb48a9420f8aa9f6483412ffa444 \
-    --hash=sha256:d2650c1fb97e184d12d8ba010493ee7b322864f7d3d00d3f9bb97d9c21de4068 \
-    --hash=sha256:d30e57c72013c2a4fe441c2fcb8e77b14e152ad48b5464858e07e2ad9fbfceff \
-    --hash=sha256:d59c30000a16d8edc7e64152e30220bfbd724c9bbb08368c054e24c651314f0a \
-    --hash=sha256:dbc12c9f3d185f5c737d801da555fb74b3dcfa1a50b66a1a93e09190f41fab50 \
-    --hash=sha256:e18f12c6b0bc5a592ed23d3f7b891f68fd7f8241d69b7883769eb5d5dfb52696 \
-    --hash=sha256:e19ebea31758fac5893a2ac360fedd00116cbb7628e650842a6691ba7ca28a21 \
-    --hash=sha256:e30bdeaa5deed6bc27b4cc490823cd0347d7dae09119b8803ae576ea0ce52e4c \
-    --hash=sha256:eb092099205ef62cd1782b006658db09e2fed75bffcae7cc0d44052d8aa0f484 \
-    --hash=sha256:eee2cfda04c00a857206a4330f0c5e3e56535494e30ca445eb19ec624ae75118 \
-    --hash=sha256:f4115102802df98b2b0db3cce5cb9b92572633a1197c77b7553e5203f284a5b3 \
-    --hash=sha256:f590cd684941912d10becc07325a3eeb77886fe981415660d9265c4c418d0bea \
-    --hash=sha256:f8885db0bc2bffa59d5c1b72fad7a6a92d3e80e7257f967dd81abb553a90d293 \
-    --hash=sha256:fcb310ddb270a06114bb64bbe53c94926b943f5b7f0842194d585c65eb4edd76
-threadpoolctl==3.6.0 \
-    --hash=sha256:43a0b8fd5a2928500110039e43a5eed8480b918967083ea48dc3ab9f13c4a7fb \
-    --hash=sha256:8ab8b4aa3491d812b623328249fab5302a68d2d71745c8a4c719a2fcaba9f44e
+pyyaml==6.0.3 \
+    --hash=sha256:00c4bdeba853cc34e7dd471f16b4114f4162dc03e6b7afcc2128711f0eca823c \
+    --hash=sha256:0150219816b6a1fa26fb4699fb7daa9caf09eb1999f3b70fb6e786805e80375a \
+    --hash=sha256:02893d100e99e03eda1c8fd5c441d8c60103fd175728e23e431db1b589cf5ab3 \
+    --hash=sha256:02ea2dfa234451bbb8772601d7b8e426c2bfa197136796224e50e35a78777956 \
+    --hash=sha256:0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6 \
+    --hash=sha256:10892704fc220243f5305762e276552a0395f7beb4dbf9b14ec8fd43b57f126c \
+    --hash=sha256:16249ee61e95f858e83976573de0f5b2893b3677ba71c9dd36b9cf8be9ac6d65 \
+    --hash=sha256:1d37d57ad971609cf3c53ba6a7e365e40660e3be0e5175fa9f2365a379d6095a \
+    --hash=sha256:1ebe39cb5fc479422b83de611d14e2c0d3bb2a18bbcb01f229ab3cfbd8fee7a0 \
+    --hash=sha256:214ed4befebe12df36bcc8bc2b64b396ca31be9304b8f59e25c11cf94a4c033b \
+    --hash=sha256:2283a07e2c21a2aa78d9c4442724ec1eb15f5e42a723b99cb3d822d48f5f7ad1 \
+    --hash=sha256:22ba7cfcad58ef3ecddc7ed1db3409af68d023b7f940da23c6c2a1890976eda6 \
+    --hash=sha256:27c0abcb4a5dac13684a37f76e701e054692a9b2d3064b70f5e4eb54810553d7 \
+    --hash=sha256:28c8d926f98f432f88adc23edf2e6d4921ac26fb084b028c733d01868d19007e \
+    --hash=sha256:2e71d11abed7344e42a8849600193d15b6def118602c4c176f748e4583246007 \
+    --hash=sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310 \
+    --hash=sha256:37503bfbfc9d2c40b344d06b2199cf0e96e97957ab1c1b546fd4f87e53e5d3e4 \
+    --hash=sha256:3c5677e12444c15717b902a5798264fa7909e41153cdf9ef7ad571b704a63dd9 \
+    --hash=sha256:3ff07ec89bae51176c0549bc4c63aa6202991da2d9a6129d7aef7f1407d3f295 \
+    --hash=sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea \
+    --hash=sha256:418cf3f2111bc80e0933b2cd8cd04f286338bb88bdc7bc8e6dd775ebde60b5e0 \
+    --hash=sha256:44edc647873928551a01e7a563d7452ccdebee747728c1080d881d68af7b997e \
+    --hash=sha256:4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac \
+    --hash=sha256:4ad1906908f2f5ae4e5a8ddfce73c320c2a1429ec52eafd27138b7f1cbe341c9 \
+    --hash=sha256:501a031947e3a9025ed4405a168e6ef5ae3126c59f90ce0cd6f2bfc477be31b7 \
+    --hash=sha256:5190d403f121660ce8d1d2c1bb2ef1bd05b5f68533fc5c2ea899bd15f4399b35 \
+    --hash=sha256:5498cd1645aa724a7c71c8f378eb29ebe23da2fc0d7a08071d89469bf1d2defb \
+    --hash=sha256:5cf4e27da7e3fbed4d6c3d8e797387aaad68102272f8f9752883bc32d61cb87b \
+    --hash=sha256:5e0b74767e5f8c593e8c9b5912019159ed0533c70051e9cce3e8b6aa699fcd69 \
+    --hash=sha256:5ed875a24292240029e4483f9d4a4b8a1ae08843b9c54f43fcc11e404532a8a5 \
+    --hash=sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b \
+    --hash=sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c \
+    --hash=sha256:6344df0d5755a2c9a276d4473ae6b90647e216ab4757f8426893b5dd2ac3f369 \
+    --hash=sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd \
+    --hash=sha256:652cb6edd41e718550aad172851962662ff2681490a8a711af6a4d288dd96824 \
+    --hash=sha256:66291b10affd76d76f54fad28e22e51719ef9ba22b29e1d7d03d6777a9174198 \
+    --hash=sha256:66e1674c3ef6f541c35191caae2d429b967b99e02040f5ba928632d9a7f0f065 \
+    --hash=sha256:6adc77889b628398debc7b65c073bcb99c4a0237b248cacaf3fe8a557563ef6c \
+    --hash=sha256:79005a0d97d5ddabfeeea4cf676af11e647e41d81c9a7722a193022accdb6b7c \
+    --hash=sha256:7c6610def4f163542a622a73fb39f534f8c101d690126992300bf3207eab9764 \
+    --hash=sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196 \
+    --hash=sha256:8098f252adfa6c80ab48096053f512f2321f0b998f98150cea9bd23d83e1467b \
+    --hash=sha256:850774a7879607d3a6f50d36d04f00ee69e7fc816450e5f7e58d7f17f1ae5c00 \
+    --hash=sha256:8d1fab6bb153a416f9aeb4b8763bc0f22a5586065f86f7664fc23339fc1c1fac \
+    --hash=sha256:8da9669d359f02c0b91ccc01cac4a67f16afec0dac22c2ad09f46bee0697eba8 \
+    --hash=sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e \
+    --hash=sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28 \
+    --hash=sha256:93dda82c9c22deb0a405ea4dc5f2d0cda384168e466364dec6255b293923b2f3 \
+    --hash=sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5 \
+    --hash=sha256:9c57bb8c96f6d1808c030b1687b9b5fb476abaa47f0db9c0101f5e9f394e97f4 \
+    --hash=sha256:9c7708761fccb9397fe64bbc0395abcae8c4bf7b0eac081e12b809bf47700d0b \
+    --hash=sha256:9f3bfb4965eb874431221a3ff3fdcddc7e74e3b07799e0e84ca4a0f867d449bf \
+    --hash=sha256:a33284e20b78bd4a18c8c2282d549d10bc8408a2a7ff57653c0cf0b9be0afce5 \
+    --hash=sha256:a80cb027f6b349846a3bf6d73b5e95e782175e52f22108cfa17876aaeff93702 \
+    --hash=sha256:b30236e45cf30d2b8e7b3e85881719e98507abed1011bf463a8fa23e9c3e98a8 \
+    --hash=sha256:b3bc83488de33889877a0f2543ade9f70c67d66d9ebb4ac959502e12de895788 \
+    --hash=sha256:b865addae83924361678b652338317d1bd7e79b1f4596f96b96c77a5a34b34da \
+    --hash=sha256:b8bb0864c5a28024fac8a632c443c87c5aa6f215c0b126c449ae1a150412f31d \
+    --hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc \
+    --hash=sha256:bdb2c67c6c1390b63c6ff89f210c8fd09d9a1217a465701eac7316313c915e4c \
+    --hash=sha256:c1ff362665ae507275af2853520967820d9124984e0f7466736aea23d8611fba \
+    --hash=sha256:c2514fceb77bc5e7a2f7adfaa1feb2fb311607c9cb518dbc378688ec73d8292f \
+    --hash=sha256:c3355370a2c156cffb25e876646f149d5d68f5e0a3ce86a5084dd0b64a994917 \
+    --hash=sha256:c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5 \
+    --hash=sha256:d0eae10f8159e8fdad514efdc92d74fd8d682c933a6dd088030f3834bc8e6b26 \
+    --hash=sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f \
+    --hash=sha256:ebc55a14a21cb14062aa4162f906cd962b28e2e9ea38f9b4391244cd8de4ae0b \
+    --hash=sha256:eda16858a3cab07b80edaf74336ece1f986ba330fdb8ee0d6c0d68fe82bc96be \
+    --hash=sha256:ee2922902c45ae8ccada2c5b501ab86c36525b883eff4255313a253a3160861c \
+    --hash=sha256:efd7b85f94a6f21e4932043973a7ba2613b059c4a000551892ac9f1d11f5baf3 \
+    --hash=sha256:f7057c9a337546edc7973c0d3ba84ddcdf0daa14533c2065749c9075001090e6 \
+    --hash=sha256:fa160448684b4e94d80416c0fa4aac48967a969efe22931448d853ada8baf926 \
+    --hash=sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0
+scipy==1.18.1 \
+    --hash=sha256:011413b7426b75012840e35649e00fe0a2c3bae89fed433876e3a99251572efc \
+    --hash=sha256:0ac49ea97594532dd44b7136094d35f5440fa06e6d9c6384a74c01764df388c5 \
+    --hash=sha256:0e82073ecc7acc6436fac4b31674109c7e1d3e596789767eda01258a8c9e8123 \
+    --hash=sha256:0fcb3c93519f27bb4f0c4b0f7802cdcaca7fcf93267b75edda2e9f4e8a55cbd7 \
+    --hash=sha256:10ac20c69d880f77f375db44c22e3e6a644f9fefa291d4cd2fb9790a89fc99fd \
+    --hash=sha256:11c423f1049c5755ad4409af52a9ada1cff96fe9b50795d4af3619f292901239 \
+    --hash=sha256:179ce34a8d0fe273d8883ba59e17e052247d08973dfcb743ca52bb1cce2d60b0 \
+    --hash=sha256:1bca3b943fc2567ea49cd02c99abde49da4d5178ec46f624bd8255cda8755beb \
+    --hash=sha256:1d73131e358976663dd969e1fb4ed1404b815cd977eaaedc3b3a133ba2d81c35 \
+    --hash=sha256:2a0b02f9fc46f8520330c23d45e6560db7e3a0d927232139427637f98943e11d \
+    --hash=sha256:2d3ab0e8c69a17dd3559eab8cbb88f258e285c94d572c2719033f90f83290c89 \
+    --hash=sha256:30f464bee641fa8e282577c7dce027308403213c6ca8270bba73285c91024bc5 \
+    --hash=sha256:33a834464fdabc0f26a45508df31b3cc5d028e04dbf6c5ed398541418e0a12fe \
+    --hash=sha256:3ab3523da44749156e1f68b464dc56af11ae4cbc5c739a49d05f32b982eca9f3 \
+    --hash=sha256:3c085faa2cfa879c5141df483f836f4d691045a078224a670fa570fa01612d89 \
+    --hash=sha256:457fd7a2a8edeb044ab6ffbc0aa03ff6cd18491356e5e0c834d76ce621b916d1 \
+    --hash=sha256:49023963c193dacee096301452f223ee24d86ec5807f8df93c0f7221d119e305 \
+    --hash=sha256:52c4b7422442aba924d03ad4019852b08a92e64ea187b933135687bfe2747307 \
+    --hash=sha256:559ed65f60c1af5a03f3912605a1b5114f522c7c32fb23c3376ae8f03219fe28 \
+    --hash=sha256:5632e3ae3d09197c446310cd5187de63e28448ce22f0f67b2b93d97503c0c230 \
+    --hash=sha256:5e4d44984abc0020154ea81b247adeddcc3ac5527b975ff798bd1ba0adc513c2 \
+    --hash=sha256:75b00eb8fb802090aa903f4ea1c7f5a584779f967361e68b7e98e531cc2d7174 \
+    --hash=sha256:78a0d7c918e74a232394117160e7e3db503377572a45bcef8826e4ab8a35feba \
+    --hash=sha256:78c0665edead396b1abb4897c41a5c1d9bf090c8a637a4c20a61678e0a264e66 \
+    --hash=sha256:7bbf207c4453ce1ad2e00b17313852b33310b83090c2311bdaf97f93c0380d12 \
+    --hash=sha256:7f4b8bc363b6d65ee2152bec57568e3c52639bb34c46057b09857a307ed5e21d \
+    --hash=sha256:82f201b4c878551d48558337aab270d3c6cca5507b8737c8d8a608d234cccde0 \
+    --hash=sha256:83de5453a7799afc9048b4616bd085cef126e36412f0ea2f6370c36a2a3a51e7 \
+    --hash=sha256:88f0e784020649f88ea48c9f5ddfa403bf9205820667c0914740b392035afb82 \
+    --hash=sha256:8bcf3c1ba5d6456e2effd30fcbd3459b044d683fcdac79a2e6830f0bdf7de487 \
+    --hash=sha256:911de823097db8b63f034299d12662db93344e6ffa0b881cbb57748974b70168 \
+    --hash=sha256:92c14f5bdbfb6216315ce33e78080474082de8b3830122ba97809bfbe65f75c0 \
+    --hash=sha256:95298364e251be3e60249facbeeca03631d3bb7584f85879516ec55ac717b81f \
+    --hash=sha256:9554bcc6d715ee87a633a3cc8e7703c6628b100dd29cb8a2efc4c0533c7ff729 \
+    --hash=sha256:9f2897bf7737392ad0d5213ea7b6add72a4edf5679b3153106aeb88b6507b3b9 \
+    --hash=sha256:a1d33a7836f7ddc1993427966a0823468ec41bcbdb1a9f9942d1d7e57f803ba3 \
+    --hash=sha256:ac0333bdf38309aa3dcbe7e3fa7ea29e7a2c37c6ea306a757b700ded8e4596ad \
+    --hash=sha256:bff0b729edd992766136b34e39cc76bc2fad905aa58897ee72a9cd000a6d8443 \
+    --hash=sha256:c24acac1e18912761c4700239bbc1fd32f615af690f1584d49b35859be51324d \
+    --hash=sha256:c35d74ce0e193ff740c2f2be2ac913ddc232fe6c1ff40b26cfecb9c670c63314 \
+    --hash=sha256:c825cef2f49e46753726a7181a8e199804a912b29519ada542c6ebc654951899 \
+    --hash=sha256:c9d18a33309122074ea483dd92dd444189166b8b2ec429fe9ed5ac73c7a0aa23 \
+    --hash=sha256:cbf38d043c1aa4ab306e1ada6ab6eddacc3322a20b7af1b30bc93254b366fe09 \
+    --hash=sha256:cd479fc04dd9401e3b4f49e76518768ef99c4f517a98c284eb091fd725719adf \
+    --hash=sha256:ceb30a00ce7c92d459819443d29ca486d882b83fb6738bdcbb2a1cce94ac5daa \
+    --hash=sha256:cfbf154f2ba187f2ed6cce2639efff7d105f1140573642c0161615b6d91d6a87 \
+    --hash=sha256:d2924a03db38dc2e848bca2fe9f077dafb891480b91a00a0963a8cf86dfc31c1 \
+    --hash=sha256:d416b16cccfd70fbf62400e84d0bb2f4e6af519a45557f1692c749b37f14b315 \
+    --hash=sha256:d65d448389b8436493abcf629cc94ad0cf32aecaf06e1acca1de53cc795f2f12 \
+    --hash=sha256:d84a09d0dad90ba6525d8ac1c2334b33e64bf3ccfe9e841f02feb867a22681e4 \
+    --hash=sha256:ddef79fb382df40104a19bb7151b3b23e57c1778fcf857c71ceecd9bd264513f \
+    --hash=sha256:e3b417bf8c2c7c16e8f58ad91db17783ec911ac16e7b50eb6eab6e809b4f5b07 \
+    --hash=sha256:e402cf31eb68f453dbb2d36fc6d722b33f24a55d68b2ae1d92fa6305ca71c298 \
+    --hash=sha256:e6fb6a55cc0ba97b59a1f288fb86dc6fce8bdfc0fffcbfd015e3a954bf2a2d93 \
+    --hash=sha256:e708533e8b2ae2497d65346538a7dcc92814410b25b81432eac66de0f2af8265 \
+    --hash=sha256:ea324d9dd34c38bfb9bec8ca4d1b407db97dbb74029f566b8e322b1b6fe56fe6 \
+    --hash=sha256:eb0dfcf4e28a99c12c999744a2ff67c9b06200e20401c7c88186e33552a46331 \
+    --hash=sha256:eda632a7981f69730d6281f451db9c1c370993a2c0d7ddb43e2a809a2862b83a \
+    --hash=sha256:f29633129f9fa7e88a3f0fca835de2d030bfc9643f7799e1a0c46cee24d38fc7 \
+    --hash=sha256:f55fa87b6c612ecd6b058f167c53231b1d14e412efe361d3d6e38b3631c73218 \
+    --hash=sha256:fdaf5ea890a6183d0565f51a61799d67081bd5b1cf03c5f4b3fd3732108625c9
+threadpoolctl==3.7.0 \
+    --hash=sha256:61348cfb77d53b9242e0017029244b559b810c142ced65b4e21eeca1843959a7 \
+    --hash=sha256:cd8b60b5641b45c67bbf73c64c843235fc2d8a480c87389f52f5dbee893b86be
 voluptuous==0.16.0 \
     --hash=sha256:006535e22fed944aec17bef6e8725472476194743c87bd233e912eb463f8ff05 \
     --hash=sha256:ee342095263e1b5afbd4d418cb5adc92810eebfd07696bb033a261210df33db4
diff --git a/tests/requirements-coverage.txt b/tests/requirements-coverage.txt
index 7aeeaf7f2..2ec445729 100644
--- a/tests/requirements-coverage.txt
+++ b/tests/requirements-coverage.txt
@@ -4,101 +4,128 @@
 # for every `fast` run -- the workflow step that installs this says so too.
 #
 # Regenerate:
-#   echo 'coverage==7.13.1' | uv pip compile - --python-version 3.13.15 \
+#   echo 'coverage==7.17.0' | uv pip compile - --python-version 3.13.15 \
 #     --python-platform x86_64-manylinux_2_28 --generate-hashes \
 #     --no-header --no-annotate -o <body>
 # and replace everything below the blank line that ends this header.
 
-coverage==7.13.1 \
-    --hash=sha256:0403f647055de2609be776965108447deb8e384fe4a553c119e3ff6bfbab4784 \
-    --hash=sha256:0642eae483cc8c2902e4af7298bf886d605e80f26382124cddc3967c2a3df09e \
-    --hash=sha256:0b609fc9cdbd1f02e51f67f51e5aee60a841ef58a68d00d5ee2c0faf357481a3 \
-    --hash=sha256:0d2c11f3ea4db66b5cbded23b20185c35066892c67d80ec4be4bab257b9ad1e0 \
-    --hash=sha256:0e42e0ec0cd3e0d851cb3c91f770c9301f48647cb2877cb78f74bdaa07639a79 \
-    --hash=sha256:132718176cc723026d201e347f800cd1a9e4b62ccd3f82476950834dad501c75 \
-    --hash=sha256:16cc1da46c04fb0fb128b4dc430b78fa2aba8a6c0c9f8eb391fd5103409a6ac6 \
-    --hash=sha256:18be793c4c87de2965e1c0f060f03d9e5aff66cfeae8e1dbe6e5b88056ec153f \
-    --hash=sha256:1a55d509a1dc5a5b708b5dad3b5334e07a16ad4c2185e27b40e4dba796ab7f88 \
-    --hash=sha256:1dcb645d7e34dcbcc96cd7c132b1fc55c39263ca62eb961c064eb3928997363b \
-    --hash=sha256:2016745cb3ba554469d02819d78958b571792bb68e31302610e898f80dd3a573 \
-    --hash=sha256:228b90f613b25ba0019361e4ab81520b343b622fc657daf7e501c4ed6a2366c0 \
-    --hash=sha256:309ef5706e95e62578cda256b97f5e097916a2c26247c287bbe74794e7150df2 \
-    --hash=sha256:339dc63b3eba969067b00f41f15ad161bf2946613156fb131266d8debc8e44d0 \
-    --hash=sha256:3820778ea1387c2b6a818caec01c63adc5b3750211af6447e8dcfb9b6f08dbba \
-    --hash=sha256:3d42df8201e00384736f0df9be2ced39324c3907607d17d50d50116c989d84cd \
-    --hash=sha256:3e7b8bd70c48ffb28461ebe092c2345536fb18bbbf19d287c8913699735f505c \
-    --hash=sha256:3f2f725aa3e909b3c5fdb8192490bdd8e1495e85906af74fe6e34a2a77ba0673 \
-    --hash=sha256:3fc6a169517ca0d7ca6846c3c5392ef2b9e38896f61d615cb75b9e7134d4ee1e \
-    --hash=sha256:45980ea19277dc0a579e432aef6a504fe098ef3a9032ead15e446eb0f1191aee \
-    --hash=sha256:4d010d080c4888371033baab27e47c9df7d6fb28d0b7b7adf85a4a49be9298b3 \
-    --hash=sha256:4de84e71173d4dada2897e5a0e1b7877e5eefbfe0d6a44edee6ce31d9b8ec09e \
-    --hash=sha256:549d195116a1ba1e1ae2f5ca143f9777800f6636eab917d4f02b5310d6d73461 \
-    --hash=sha256:562ec27dfa3f311e0db1ba243ec6e5f6ab96b1edfcfc6cf86f28038bc4961ce6 \
-    --hash=sha256:57dfc8048c72ba48a8c45e188d811e5efd7e49b387effc8fb17e97936dde5bf6 \
-    --hash=sha256:5899d28b5276f536fcf840b18b61a9fce23cc3aec1d114c44c07fe94ebeaa500 \
-    --hash=sha256:60cfb538fe9ef86e5b2ab0ca8fc8d62524777f6c611dcaf76dc16fbe9b8e698a \
-    --hash=sha256:623dcc6d7a7ba450bbdbeedbaa0c42b329bdae16491af2282f12a7e809be7eb9 \
-    --hash=sha256:67170979de0dacac3f3097d02b0ad188d8edcea44ccc44aaa0550af49150c7dc \
-    --hash=sha256:6e73ebb44dca5f708dc871fe0b90cf4cff1a13f9956f747cc87b535a840386f5 \
-    --hash=sha256:6f34591000f06e62085b1865c9bc5f7858df748834662a51edadfd2c3bfe0dd3 \
-    --hash=sha256:724b1b270cb13ea2e6503476e34541a0b1f62280bc997eab443f87790202033d \
-    --hash=sha256:75a6f4aa904301dab8022397a22c0039edc1f51e90b83dbd4464b8a38dc87842 \
-    --hash=sha256:77545b5dcda13b70f872c3b5974ac64c21d05e65b1590b441c8560115dc3a0d1 \
-    --hash=sha256:776483fd35b58d8afe3acbd9988d5de592ab6da2d2a865edfdbc9fdb43e7c486 \
-    --hash=sha256:77cc258aeb29a3417062758975521eae60af6f79e930d6993555eeac6a8eac29 \
-    --hash=sha256:794f7c05af0763b1bbd1b9e6eff0e52ad068be3b12cd96c87de037b01390c968 \
-    --hash=sha256:868a2fae76dfb06e87291bcbd4dcbcc778a8500510b618d50496e520bd94d9b9 \
-    --hash=sha256:8842af7f175078456b8b17f1b73a0d16a65dcbdc653ecefeb00a56b3c8c298c4 \
-    --hash=sha256:8d9bc218650022a768f3775dd7fdac1886437325d8d295d923ebcfef4892ad5c \
-    --hash=sha256:8f572d989142e0908e6acf57ad1b9b86989ff057c006d13b76c146ec6a20216a \
-    --hash=sha256:90480b2134999301eea795b3a9dbf606c6fbab1b489150c501da84a959442465 \
-    --hash=sha256:916abf1ac5cf7eb16bc540a5bf75c71c43a676f5c52fcb9fe75a2bd75fb944e8 \
-    --hash=sha256:92f980729e79b5d16d221038dbf2e8f9a9136afa072f9d5d6ed4cb984b126a09 \
-    --hash=sha256:933082f161bbb3e9f90d00990dc956120f608cdbcaeea15c4d897f56ef4fe416 \
-    --hash=sha256:97ab3647280d458a1f9adb85244e81587505a43c0c7cff851f5116cd2814b894 \
-    --hash=sha256:985b7836931d033570b94c94713c6dba5f9d3ff26045f72c3e5dbc5fe3361e5a \
-    --hash=sha256:9e549d642426e3579b3f4b92d0431543b012dcb6e825c91619d4e93b7363c3f9 \
-    --hash=sha256:9edd0e01a343766add6817bc448408858ba6b489039eaaa2018474e4001651a4 \
-    --hash=sha256:9ee68b21909686eeb21dfcba2c3b81fee70dcf38b140dcd5aa70680995fa3aa5 \
-    --hash=sha256:9f5e772ed5fef25b3de9f2008fe67b92d46831bd2bc5bdc5dd6bfd06b83b316f \
-    --hash=sha256:a03a4f3a19a189919c7055098790285cc5c5b0b3976f8d227aea39dbf9f8bfdb \
-    --hash=sha256:a4d240d260a1aed814790bbe1f10a5ff31ce6c21bc78f0da4a1e8268d6c80dbd \
-    --hash=sha256:a5a68357f686f8c4d527a2dc04f52e669c2fc1cbde38f6f7eb6a0e58cbd17cae \
-    --hash=sha256:a998cc0aeeea4c6d5622a3754da5a493055d2d95186bad877b0a34ea6e6dbe0a \
-    --hash=sha256:b67e47c5595b9224599016e333f5ec25392597a89d5744658f837d204e16c63e \
-    --hash=sha256:b6f3b96617e9852703f5b633ea01315ca45c77e879584f283c44127f0f1ec564 \
-    --hash=sha256:b7593fe7eb5feaa3fbb461ac79aac9f9fc0387a5ca8080b0c6fe2ca27b091afd \
-    --hash=sha256:bb3f6562e89bad0110afbe64e485aac2462efdce6232cdec7862a095dc3412f6 \
-    --hash=sha256:bb4f8c3c9a9f34423dba193f241f617b08ffc63e27f67159f60ae6baf2dcfe0f \
-    --hash=sha256:bd63e7b74661fed317212fab774e2a648bc4bb09b35f25474f8e3325d2945cd7 \
-    --hash=sha256:be753b225d159feb397bd0bf91ae86f689bad0da09d3b301478cd39b878ab31a \
-    --hash=sha256:bf100a3288f9bb7f919b87eb84f87101e197535b9bd0e2c2b5b3179633324fee \
-    --hash=sha256:c223d078112e90dc0e5c4e35b98b9584164bea9fbbd221c0b21c5241f6d51b62 \
-    --hash=sha256:c3d8c679607220979434f494b139dfb00131ebf70bb406553d69c1ff01a5c33d \
-    --hash=sha256:c43257717611ff5e9a1d79dce8e47566235ebda63328718d9b65dd640bc832ef \
-    --hash=sha256:c832ec92c4499ac463186af72f9ed4d8daec15499b16f0a879b0d1c8e5cf4a3b \
-    --hash=sha256:c8e2706ceb622bc63bac98ebb10ef5da80ed70fbd8a7999a5076de3afaef0fb1 \
-    --hash=sha256:cb237bfd0ef4d5eb6a19e29f9e528ac67ac3be932ea6b44fb6cc09b9f3ecff78 \
-    --hash=sha256:ccd7a6fca48ca9c131d9b0a2972a581e28b13416fc313fb98b6d24a03ce9a398 \
-    --hash=sha256:d10a2ed46386e850bb3de503a54f9fe8192e5917fcbb143bfef653a9355e9a53 \
-    --hash=sha256:d1443ba9acbb593fa7c1c29e011d7c9761545fe35e7652e85ce7f51a16f7e08d \
-    --hash=sha256:d2287ac9360dec3837bfdad969963a5d073a09a85d898bd86bea82aa8876ef3c \
-    --hash=sha256:d3c9f051b028810f5a87c88e5d6e9af3c0ff32ef62763bf15d29f740453ca909 \
-    --hash=sha256:d72140ccf8a147e94274024ff6fd8fb7811354cf7ef88b1f0a988ebaa5bc774f \
-    --hash=sha256:d938b4a840fb1523b9dfbbb454f652967f18e197569c32266d4d13f37244c3d9 \
-    --hash=sha256:db622b999ffe49cb891f2fff3b340cdc2f9797d01a0a202a0973ba2562501d90 \
-    --hash=sha256:e09fbecc007f7b6afdfb3b07ce5bd9f8494b6856dd4f577d26c66c391b829851 \
-    --hash=sha256:e1fa280b3ad78eea5be86f94f461c04943d942697e0dac889fa18fff8f5f9147 \
-    --hash=sha256:e4f18eca6028ffa62adbd185a8f1e1dd242f2e68164dba5c2b74a5204850b4cf \
-    --hash=sha256:e825dbb7f84dfa24663dd75835e7257f8882629fc11f03ecf77d84a75134b864 \
-    --hash=sha256:eaecf47ef10c72ece9a2a92118257da87e460e113b83cc0d2905cbbe931792b4 \
-    --hash=sha256:ef6688db9bf91ba111ae734ba6ef1a063304a881749726e0d3575f5c10a9facf \
-    --hash=sha256:f398ba4df52d30b1763f62eed9de5620dcde96e6f491f4c62686736b155aa6e4 \
-    --hash=sha256:f80e2bb21bfab56ed7405c2d79d34b5dc0bc96c2c1d2a067b643a09fb756c43a \
-    --hash=sha256:f83351e0f7dcdb14d7326c3d8d8c4e915fa685cbfdc6281f9470d97a04e9dfe4 \
-    --hash=sha256:f8dca5590fec7a89ed6826fce625595279e586ead52e9e958d3237821fbc750c \
-    --hash=sha256:fa3edde1aa8807de1d05934982416cb3ec46d1d4d91e280bcce7cca01c507992 \
-    --hash=sha256:fea07c1a39a22614acb762e3fbbb4011f65eedafcb2948feeef641ac78b4ee5c \
-    --hash=sha256:ff10896fa55167371960c5908150b434b71c876dfab97b69478f22c8b445ea19 \
-    --hash=sha256:ff86d4e85188bba72cfb876df3e11fa243439882c55957184af44a35bd5880b7 \
-    --hash=sha256:ffed1e4980889765c84a5d1a566159e363b71d6b6fbaf0bebc9d3c30bc016766
+coverage==7.17.0 \
+    --hash=sha256:032d4c2db4c677eb71d43f2f8b80bf64e9346f7a3f7b6ebb13f1782f3cc6c274 \
+    --hash=sha256:03baf0688e14a5a44ffd1eefa8928dfc92b14565e521174e072b31b971aa1657 \
+    --hash=sha256:045c1eeb19fb4eae949850a761102fffb3a5f638b97f977912f95843e54f6669 \
+    --hash=sha256:09e563b49c81cd0a33734e926d7a4a6ef1778d74304cde2dcc3aff8b30ea1036 \
+    --hash=sha256:0a9cb9a0fb58e6fff5442969af36094ecd6976f4907f179e33b27e15355d8f74 \
+    --hash=sha256:0b8bb651a4406fb6a983a905309fec1783443c65e1771b41e92740a0f4a1176b \
+    --hash=sha256:0cfdc938ca3319d873d1f1252e60620a39aee4ebf9dbd7cc58238109ebda9c51 \
+    --hash=sha256:0d0fac604a962ff546beb038cba9a5a09d88e6e3f01612fb46f7bd4fe5dc8dca \
+    --hash=sha256:0edeb6594f080c8de1263cccb239cb316ef77aeb959e2e0f38f2953fcc72a49e \
+    --hash=sha256:11f5f7fb2d97a0fe865f5e7bad4eb0619b957637f676bc088d13844adf26ba95 \
+    --hash=sha256:12961f738d717a046d4bf3f8d1727eb3ebe2ed5478ff96cd6233d4dfc39323d3 \
+    --hash=sha256:12cb8a20ad904a5811e6660d829a586b216e5254b9b34b76dde8a4d65d827dc6 \
+    --hash=sha256:194562ab1eff0d85aee8a17ce4c5c0bc1ebf70a629a7145257123156ad100fd6 \
+    --hash=sha256:1cabb31531002fef5197de5df3c84730aef01e750e25154b9813a2583435aba2 \
+    --hash=sha256:1ee0a982b0e1230b3edf768a7dd022bd2377303763895327ac62deb5efacee03 \
+    --hash=sha256:2bf3ee38a40c0570c316b9e7507c472469586906a20f289705898528c31aaea8 \
+    --hash=sha256:2c680e838ff9e68d491158625ca2c1ddb17d78d791bba96a31f8b839b4990438 \
+    --hash=sha256:2dc9233f39149b5a4f4aba17a4b6bc5cca22e52cfc4b06fdb07d014439b8b2ea \
+    --hash=sha256:2ed3097c6817bc1a7fc8ae0a6131db74aa1150d863cccc308237ff362d3226b2 \
+    --hash=sha256:3067608b4429629f640c1b23d2f69b05d2fd45e00ebb6ee9e8fad220a6c11722 \
+    --hash=sha256:30f5477aac9c9e4a0a641c55f8f8fddd7f3bd91176c912c50f40ffced96b4034 \
+    --hash=sha256:337f87e62e1c5f43c8198d879f677c342d152f84d3f157add12558853cbb8eaf \
+    --hash=sha256:3393209f6894713161ee82a9b0e673e58237e0f9733c6638e7a6c0c620ef0b33 \
+    --hash=sha256:34d65c9e8e257f48a654908005046fbf1bc48d9540ae3776ad08c0acd010e10c \
+    --hash=sha256:38c86e5d74bbfd88a393fa3f91257c1225c63aa6db6d5918de3e49ab04f91c6e \
+    --hash=sha256:3a4459b0f389dd1e51aac3dbfc4ca35b30cae7dc99caa3c0a086d1997a985709 \
+    --hash=sha256:42e6f170d1ac04b7eb3363310a6c41cdfd82c1fe6bf9ffbc4a86f380bdf091c7 \
+    --hash=sha256:4343a9378b964eb3cb80fa90406385de91c7e982a769ca9314d848f93bc0d3f2 \
+    --hash=sha256:460679f53893081edb94eeed011d26be37228ba649b853fd2aed7e4394fb1f35 \
+    --hash=sha256:4e153f0bd6509dbf837fd585f489b3328bfd98f2a718a0b15ae63032148b285c \
+    --hash=sha256:50678474e714c684b82c108e63fbb8f1bcf1266d8293a49980f1d08526f093b5 \
+    --hash=sha256:55939ea4c097fda2edabf80fac5e49bef15597b950a9f29fc56292a895245feb \
+    --hash=sha256:559f748446ee799803686b5784e3deb54c70d655ac386a860e06b11672504ba7 \
+    --hash=sha256:58a304efdf2253fb2ea03d45d0a04cc174a92a0cd5279c28c5bb893ce7410968 \
+    --hash=sha256:5900055351ec89fdffb34b27898815106529ded29a9496464c1ebd6313fd40fa \
+    --hash=sha256:5b7fa0997b8eba7378ac66f31ec7f70164490353ab79b9667d37c0d365e50177 \
+    --hash=sha256:5cc15faaf318ee5040d835a62c75bc6f122d837274f3b5efd47bf9fbd4ac5b85 \
+    --hash=sha256:5ebfbc87836529a31d25c2dec1262c38eea852ec1c46c0f690a515a7339d9c5b \
+    --hash=sha256:5ee9c8bd13a59e301dc2aefe7aa8384633406808de051b1982775667094eb673 \
+    --hash=sha256:600e121e412cd6bdb52ec105b95c6a04da0c9710d1534f6e64a42db667907802 \
+    --hash=sha256:6052e878b628abcd38fa5f2b64abebc686eed4e2267da42434017a9c6d24f241 \
+    --hash=sha256:61cde5222f1933d476647c5a25ed1a8678b7703098cb5a15f4a0aa39967d8c28 \
+    --hash=sha256:62bb77987d3f72a0aaa77c567ee7f9806bc2e748c8f46fafbe1fdb90dd148398 \
+    --hash=sha256:66efc0fb99cee34626fc17d3adac9c3cd816bfdad563bb1e983c3ef432f566d4 \
+    --hash=sha256:6a80a11b90c4a03df1502304cf24ff953255b6b5d076ef79066ecf88baaff31f \
+    --hash=sha256:6abfb6a4cf1cb1b67bc8fccdde177e2d2b781d0d34449e7078156547025140e5 \
+    --hash=sha256:6ae0453a3390e67f7bfbe34417bbdf5b4ebfc21db23fb446a0a41115eeeca6ca \
+    --hash=sha256:6b4593d2871c4c801656dd5861e759f8f5156febd6b6061b02f6a72d64618b7b \
+    --hash=sha256:6cc31f27240d4e080437e3b8229d92f1d809c9a4f233607385373b73974e183e \
+    --hash=sha256:6e09612b1b82c9df1d2b6c85dee88d5aad3e73d77a8ec0b16ac6a7322cbdf5d9 \
+    --hash=sha256:72edd4f9483ae30cd1ba4f230687840ef7b58a16afb1c9e81131fd6d64655f36 \
+    --hash=sha256:791f9ee09814dd30d9562b4f4eb037a371485ec1c830b53999d2320d20c4e764 \
+    --hash=sha256:79cf71e5f9a48877ccfed5baa2c72f45af4feeaa596249e23eb15b473134830e \
+    --hash=sha256:7b5abcae74750302ac4bc77351eaee87c450e4abd3b6225eacde3858e260f8b2 \
+    --hash=sha256:7c570293f001ea91598b90e90cb9b98fddee833e90bbede432cbd218331ccd8e \
+    --hash=sha256:7d6d9d396c8b7bcaf76d774a10140b218111484e54c73a5f2a1b75655381748e \
+    --hash=sha256:7fef12cec4b96f59e09761cbd4fc9bdf4788062d1ae435b920241fc16c8a9549 \
+    --hash=sha256:804fbaf81d09b34e2f8b1159d01e211a50713d743d32fd9b2ca6cf0ae507a66f \
+    --hash=sha256:84538c040f4e6214f663459d89372ce4e6b2bbdd9d397ef0dca7b3ecd56b8eb2 \
+    --hash=sha256:85682ca89bc4601125dcdff23fa70e6274e13c9ad502fba845e6c274ab2c6569 \
+    --hash=sha256:85932227e9dd38e62cd29c17fefdfecfb919eead6af1e3259522d03cf85de983 \
+    --hash=sha256:88a1a9fb0075b83389dd9b403bb3fce976031b3c2aa0e05e3e57143cf639de69 \
+    --hash=sha256:8d823d66afd59566030539c49c7a6acaf3083996682be2dda760c63555842094 \
+    --hash=sha256:8e8113d3852e9377421a61de1917df27b3abb25404a4ecf69f9e64612c4345b5 \
+    --hash=sha256:912a29f338798541d795e2e25903c6fe7a99dee70a40fe4706a9a124649b523e \
+    --hash=sha256:91e487ad07c511da77b574820141a7c2da09bc2a4b4090b5be2424295d100697 \
+    --hash=sha256:96151262832f3c230ebae23b2d6911ad549e1738465946c97004913ff06112ba \
+    --hash=sha256:968c5fb6e0c83cab752d79a70209648ce4d90cae815c60fa229b59e264601062 \
+    --hash=sha256:99a7b390cbccc6bf029ca4da3f0f607c218bb4085e9cd6b58a90d14ca12993c3 \
+    --hash=sha256:9a66074231799d8884d267234d49f60c90b43a945dfe069646b72f3058cd4e67 \
+    --hash=sha256:9c083e253e96fdeeaf48133fe836cac86ace2db215d235700e7f7532420a200c \
+    --hash=sha256:9d1fdf82c6fea57b5e9dada509f9ce9638c8334664e2c98c7f6f1ccf3d143ad2 \
+    --hash=sha256:a01ef92caeedfa4f2ad171a3a8e6fece4565de871d8bca428151bf9929f41048 \
+    --hash=sha256:a14e8d69464da9cbe1dc29e7116dbd37296d1d51a695327c478e250349085089 \
+    --hash=sha256:a1762e85cbbe3b5ff9c6dcbcc1b89d5c72320094292b7b9572bf882c85e428b7 \
+    --hash=sha256:a25cc5e8c23a590815c6a7aa43624234d25cb23b21b484adb8a0daed59860db5 \
+    --hash=sha256:a32ee5831b15ba239bef5d272ae586ca8acea4a661b5f2941f5a0d380e518b23 \
+    --hash=sha256:a3914e2c98c34b94c26d2add3d2a61ccfd3534fc4eaa879ee290bdbb5184ba6c \
+    --hash=sha256:a59c3b470ac3b2432af3598a996affbeb10236cd899a005c1c4e517fcff8b592 \
+    --hash=sha256:a5e2e0625dfc789af0b2e10acfc106b352f314fffbd19e6392a7961c8cbe5d9a \
+    --hash=sha256:acdb5f3c96046efff9dc6c572a6acb2b8d0da09372d7b9a9ed7249cf7d17434f \
+    --hash=sha256:adabc1079ba844b096799ba8638d8df434aca1613f95bb7d5791af320cf05559 \
+    --hash=sha256:adbf3450c0f3f2b2854e282a8758f2b3eddf787eeff24ec9c9bc2cbc38328cc1 \
+    --hash=sha256:aed06129a9f530a948928260d7d2d81c47261355b0127e3c782251b38958463c \
+    --hash=sha256:b2afebb96da9a1bbca142f8cc12320c14e5c215e0a49cded4f191f5a31506a28 \
+    --hash=sha256:b609df3d6d900464207532c5170a65c6ede8d2e0b91f151f90008a866395cd76 \
+    --hash=sha256:b88fb4d4d7608cbcebdc7ff7dbffc2115e3b81d6c33a79147cd79d54fcb080f4 \
+    --hash=sha256:bac487dce0d2aff28ddf1a533a916f771416eee0e493960f611e49037b878e9d \
+    --hash=sha256:bb5ca66937c55bc85d1a5e9c5900a3e4693a8edf2280a9b3672b7b2661a84b95 \
+    --hash=sha256:bd04fd23206be9ad3de13b0b39313094fafa66a1f6baf70f5471c004a9fac47d \
+    --hash=sha256:bd3e9eb493631ff1ca34bf5efac25b5c66724f837bf6182c4fc771c55946423d \
+    --hash=sha256:bfb6f868af552c0ceb2d19220b8cbcc2be096ca26163ac30e682a13041433429 \
+    --hash=sha256:c2c48a36bb970b7265b196032bfd4237c0b373f2b25ef7012d7e905b5b35c19c \
+    --hash=sha256:c3e11b81faafb1f063248735c3e2c5c4183fc1db2c7f46782170dd7760dffcbc \
+    --hash=sha256:c7c5672ecf1b497de7a0b37743bef40e3b58e3207e9fe2ed6682cb0420836a88 \
+    --hash=sha256:c86a39539d10d666bb819c16c94d7edfc1aa2e0531b937f7c549b83d15177c6e \
+    --hash=sha256:c8a58baa8eb6154c6645eadcc19b6c089deab78c24a612a83206f2a8a5992a7c \
+    --hash=sha256:c9ac886242bbd50fb35a2242ba79555a99891e657da33f98b7ca968e3488a350 \
+    --hash=sha256:cbf0b83ce927de6053279ba61342d9f8892afde1385fcba9144cd05d4023d109 \
+    --hash=sha256:cc010a0a7fbdd9bb8bdfd0d3f04a5151275860213cbd7e2b876b29778489c712 \
+    --hash=sha256:cd7397de6cc782f00fe5ac1d75e9b306bcfa49c8b6b8dd6ed1f7709393ad40b3 \
+    --hash=sha256:d45cdc495671fc99268ff3653e0da4244972e9fc0e1fc3ea9de18781ad28963a \
+    --hash=sha256:d472ee1c64868a917a47f02ffb4ac8c22b477f7589d57a3eb0c58b1ad4f0137c \
+    --hash=sha256:d523da3c2e4bca49417768bcdb1a443c5b359dc44b8b93a3102e118fce912c40 \
+    --hash=sha256:da94ec0484e84fce5c7bf8d0f54b97767a90d992653a129b35634699d516e0a5 \
+    --hash=sha256:db645c81cf4d6bcb392ea1894aad65d55d1588a8472c834b25ca575da3029a56 \
+    --hash=sha256:dc5936491e306f2f6f095bd5fba593de11eb0375cee787ca1f245c3a333a523a \
+    --hash=sha256:dfb12891a773cbc2132349c77c690a045a882fe3f98b4bda50dfabb01893f9bd \
+    --hash=sha256:e42a835271922fe7bf98c7a05c78d4032f4e52bf5b07fafa1eadfdfc2f0ad22f \
+    --hash=sha256:e4eaf11d6b0f2147f46cfbf06fe7edcca6f095d0120da00ddc2458995ee869fc \
+    --hash=sha256:e65a1e61a68493fbfbe44d8bec71b3231d81b9917f62d3dafe0e105072147e83 \
+    --hash=sha256:e8a72b26dc5c9a9422e45472b1d67ba5caf273c524c8668cc04b23062663755e \
+    --hash=sha256:e9494d9e99389d39e6a96227749af898d8924ff591cb63944f8a98e68582bf0e \
+    --hash=sha256:ef65e96f0fc1a7c8b7644c7011d47a8228555e7888ac4d6246f715a7f3d7c398 \
+    --hash=sha256:f1fc9a7cea899c51d8a53e66c2f082a3d9e461ece32418d3ef0a0b90c32bfd3d \
+    --hash=sha256:f6cdb47a9be2d3313829bed1d296086287682a3ee901ff987b3432b45705b771 \
+    --hash=sha256:f72640e02a470b57b15cd655820133f6892760209283a363a60e2df932d5f0fe \
+    --hash=sha256:f8bc2cd4c6aa58be1ca243fb8cddb6c3c42031fe4403991ad9cf2b3baed03d9f \
+    --hash=sha256:fb5745048ee20f796b0e3ab61831049e749acff188563e2af32f58ede957ac1b
diff --git a/tests/requirements-typing.txt b/tests/requirements-typing.txt
index fce4253a3..54ed92646 100644
--- a/tests/requirements-typing.txt
+++ b/tests/requirements-typing.txt
@@ -18,33 +18,25 @@
 #       --no-header --no-annotate --override <overrides> -o <body>
 # and replace everything below the blank line that ends this header.
 #
-# <overrides> holds cryptography==50.0.1 and pyopenssl==26.4.0. homeassistant
-# pins cryptography==48.0.1, which carries three advisories (Dependabot 66, 69
-# and 70), and pyopenssl 26.2.0 caps it below 49. mypy imports neither, so the
-# override changes no measured number. Because homeassistant's own pin now
-# disagrees with the lock, CI installs it with --no-deps: this file is already
-# the full resolution. Drop the override once homeassistant pins >= 50.
-#
-# <overrides> also holds pyjwt==2.15.0. homeassistant pins PyJWT==2.13.0,
-# which carries the PyJWT advisories fixed in 2.14.0 and 2.15.0. No tracked
-# module imports jwt and mypy does not execute homeassistant, so this
-# override, like the two above, changes no measured number. Drop it once
-# homeassistant pins >= 2.15.0.
-
-# <overrides> also holds aiohttp==3.14.5 and yarl==1.25.1. homeassistant
-# pins aiohttp==3.14.3, which carries the Dependabot advisories fixed in
-# 3.14.4 (GHSA-2g87-pp6c-29x5, GHSA-494j-54xm-rwp3, GHSA-5wr8-gcqf-gqf3), and
-# yarl==1.24.5, below the >=1.25.1 aiohttp 3.14.4 requires. mypy does not
-# execute either, so the override changes no measured number. Drop both once
-# homeassistant pins aiohttp >= 3.14.4. (3.14.5 is the pip group's bump of
-# 2026-10-21; the advisories above are fixed from 3.14.4 on.)
-#
-# <overrides> also holds uv==0.13.4 and pillow==13.0.0. homeassistant pins
-# uv==0.12.5 and pillow==12.3.0 exactly, so the pip group's bump of both
-# cannot resolve without overriding them. mypy executes neither (pillow is a
-# homeassistant runtime import, uv a package-install helper), so the override
-# changes no measured number. Drop each once homeassistant pins >= the
-# override. certifi needs no override: homeassistant does not pin it.
+# <overrides> holds every pin this lock carries past an exact pin of the
+# package that requires it, which is the set `pip check` lists on the
+# installed lock: homeassistant==2026.10.4 (homeassistant-stubs 2026.9.3
+# pins 2026.9.3), cryptography==50.0.2, uv==0.13.6, pillow==13.0.0,
+# astral==3.2, hass-nabucasa==2.8.1, orjson==3.13.0, python-slugify==9.1.3,
+# securetar==2026.10.0 and sqlalchemy==2.1.6 (homeassistant 2026.10.4 pins
+# each lower), acme==5.8.0 (hass-nabucasa 2.8.1 pins 5.7.0) and
+# python-dateutil==3.0.0 (botocore caps it below 3.0.0); plus
+# pyopenssl==26.4.0, whose 26.2.0 caps cryptography below 49. They are the
+# pip group's bumps (Dependabot #3088, re-applied 2026-11-01), and without
+# them the compile is unsatisfiable. homeassistant-stubs itself stays at
+# 2026.9.3: 2026.10.0 is an empty release deprecating the package (Home
+# Assistant ships py.typed), and under it the ruler reads Home Assistant's
+# own annotations, a different measurement (70 errors at 2026-11-01). mypy executes none of these packages, so
+# the overrides change no measured number. Because the lock disagrees with
+# those pins, CI installs it with --no-deps: this file is already the full
+# resolution. Drop each override once its pinning package pins >= it. (The
+# earlier pyjwt, aiohttp and yarl overrides are gone: homeassistant 2026.10.4
+# pins PyJWT==2.15.1, aiohttp==3.14.5 and yarl==1.25.1 itself.)
 #
 # For a single-package security bump, keep every other pin: delete that
 # package's hash lines and run the same compile command with this lock as its
@@ -53,9 +45,9 @@
 # `--print-requirements` re-resolves unpinned names and moved unrelated
 # packages when run on 2026-10-20.
 
-acme==5.7.0 \
-    --hash=sha256:4be4fe6cf3809c3988d75fa1213ce8e784d9d5d8380cac63c2dca555e105653d \
-    --hash=sha256:a736f88e975f0ebe8c6fcabd3db164d1071b4f9e1a56d1319a9f6997e0a64a0a
+acme==5.8.0 \
+    --hash=sha256:44c4edb53acdd3fa8402cb29c78a6d1bd2005d777a4d2fcd12663bbc3c147b34 \
+    --hash=sha256:637501767248156545d85c23b806381ac346c5eac759f8e35052af85b7bb3933
 aiodns==4.0.4 \
     --hash=sha256:c24dd605bac70a1676ce503f967a98483ff163507198557d8e9db16267e6cfd2 \
     --hash=sha256:cb10e0c0d2591636716ad2fe402e977c16d71bdaf76bb8cb49e8a6633596f736
@@ -274,67 +266,67 @@ annotatedyaml==1.0.2 \
 anyio==4.15.1 \
     --hash=sha256:6152fdbbf9a77fdec97731721bebf7c4c44f7c29b424b0065826173efc7ed101 \
     --hash=sha256:9f28306018cbd6d329e64a36d58256edff76dd996fe423bc957326e578b82a94
-ast-serialize==0.11.2 \
-    --hash=sha256:00119a8fb8c1dc0f1fab023f4d8071fa49e3b0208ee54d589fd463c16ab0124e \
-    --hash=sha256:00bbf1f6669f813b48925b759f7ae4591067d456d443924055cab386e7e0a719 \
-    --hash=sha256:08eda88a0f290a36c38cab33df8bf7e35eb95bc802ca5beb2c8fcda471a7d10c \
-    --hash=sha256:0d01f61352c96370febf6c0dbd488dee9183a731fb2702170da9163ae317cded \
-    --hash=sha256:0de02520c11391a026e62987a9aa2c3c2ff01545155059ddf0c4bdf2c5ecbe9f \
-    --hash=sha256:13b13afe32e845c86a573497729e1b7ddeb26c572c78bf50ece51da23b8fad5e \
-    --hash=sha256:1844ed9a487fb3de7325c52ddb33f2918b66b65cd54d3f8d83d23785ffe99fa4 \
-    --hash=sha256:1d6ad94edbe93bf1dabc06c9f37d55b898fdabc456aa6d7ced5e23c14f795f32 \
-    --hash=sha256:2fa3be25f7f5351b1b39c9f8a52779b2dbf21199efbae564b4746422e8edca4e \
-    --hash=sha256:2fdf31a0bb85ea2575cc91669f005e6647d2efed491231c4dc1497bc9a5b3aa6 \
-    --hash=sha256:3b78e6fdef3b06c86ed263e1962fee5a7b9d2d158e738b212d13b2c605ee12f5 \
-    --hash=sha256:40b2801cf2221bd922d9f69d2f0ebc373c3db47207315d525b2d87fa161a2af4 \
-    --hash=sha256:43b51e6ebe6549bf21416c3c78ee886147b80875a87cc6f69e303dde0d75be0b \
-    --hash=sha256:554d117cb916d8032d85007c654d179efbbfd446174c048062778136a922944f \
-    --hash=sha256:57c0f5cb0021a5beb1e5e4d6e840ae2f23a28909703ef4d256a144cc1ad3d437 \
-    --hash=sha256:59c25f47524efa052971b860e128b1add0c94ede7dd16b2962952c85c3582365 \
-    --hash=sha256:6061a54f39e82a9f2cbcb9c268fc441890e4818a6636473caa4f4063254e0750 \
-    --hash=sha256:75a1c7f46b9c19fc0ae01ca6fd076301628faa2ed7a8edbd55c6353c483946a3 \
-    --hash=sha256:76cc294246e60a914326b4ca88c6a5ea89c064906614aaf1537ce82f09e9449f \
-    --hash=sha256:7aaaffc32905159774a107d3cf33dad59bd41b7a0d1bc9885532186753ee7439 \
-    --hash=sha256:7f1823275b246f9c7d373be6879e4eec09686948895d4ad083f4b27fd7e4da70 \
-    --hash=sha256:8532f20916fa3189d4d785ef2a62d93c4d651ec9c5bffda66d2fc36898351f34 \
-    --hash=sha256:85fbb01e83967a126d71f679f2b9528ef0912cb0854aa1a4657314c34e255b57 \
-    --hash=sha256:89499a439955931281986e97ca4dd3c064bf0d2e0027c0017344eb86667733a1 \
-    --hash=sha256:8a5ffa70e76191dcf240d3c43e20c93b3bfd26f54d89148c762d57837f5bcd2c \
-    --hash=sha256:8d62a47714c8bc432b9fabcc29989c815c5da17327d35151f2fd0d85c2a7a5ff \
-    --hash=sha256:8df32ad4ff7843734a6c2f067ee974f6d3109ee5a2c3e1a9d2f79347bd282a9a \
-    --hash=sha256:976a5bd75845d22f4b52905ddf53ab669ef1b14dba7735f5512841a2ef2b5450 \
-    --hash=sha256:9d80a81ec84660422579bdb8e789f656a794b48c7a1ae1261f6bd8bc1897d17d \
-    --hash=sha256:a0fd40c668b0fa19b8fdb61d9e63d547e2e19cfbfe053a51ef0b6c37070298a8 \
-    --hash=sha256:a586be418eb70a9f1396cea29ddac8f4b9bf277fb73ea2340db31e218bc00f32 \
-    --hash=sha256:a7004ba572f09be34342ccb98dcd4bad5707d3d81adc8cb4c3f685d2a2c51bbc \
-    --hash=sha256:a9ffa8a197a721f07a352d0be6185f5b3e6f9aaebfdb66169ed652108531ae3b \
-    --hash=sha256:ab924ba260efd7509492f272d4e236d24564033f20c005d7c63a107c6a76fc85 \
-    --hash=sha256:abdb3e49ba053c3486ac1263bee9f16cc9a4a8abd9f8c90bfc21e3669f3ad9d1 \
-    --hash=sha256:af8c003ce721b0099dd55cef4ba733500fc3054ea0cc8565d8957aaf7cccdeb4 \
-    --hash=sha256:b17869f4ba261a5fa468a753328a548f4dbaf74b4eadae9e28aff66df7f1425b \
-    --hash=sha256:b4e4558956b6a0fb35e18fba58f7d1810b1f2c0e6b52352572cd5dfb6b4ef33a \
-    --hash=sha256:b9065dd23131a23b41f5bab3bf4e9b3c350a3fe8e36e8200eded9b729fcea484 \
-    --hash=sha256:bfbe47a3a7c368f28836e78b2440a3643ac0ec4c67d9fe53588e1448f0a3d35d \
-    --hash=sha256:c58bb119b73657fdc5569692f316e1e25ca114bd62f7782eb527c6be438ba3a9 \
-    --hash=sha256:cae5addfbb54cc1d47fe947ef9138e9d83849ed1cbc72b819cf36d96a2315b07 \
-    --hash=sha256:cb073bfa15742699d408ac50f60878383b5665ae1791d1b6799ea6f08633cd77 \
-    --hash=sha256:cd320a5c4f1f2742af97eea22954f776379175c5ef2504801e9a155f2ff9a4d7 \
-    --hash=sha256:d60515335750d431e462af6e722bb55720a5e7827192777bddfd9c4376065a4d \
-    --hash=sha256:d70556a2f9230a44c99a655774cde823f056efc34466eabfb4085f0cb1ea9f99 \
-    --hash=sha256:daadf1c3e0224621607ffe16f1379e4bd372271ed2e1db8a67878f0bab3ef7e4 \
-    --hash=sha256:dab599cbdcb7b45b18c41fad746645580b3a24357082b7f0e8921cd373804f27 \
-    --hash=sha256:ec1c20f89c3e0d83576e3c06f79375ce936266591fe0d5fd969914af3185cbaa \
-    --hash=sha256:ee732ae167e686d1d3c00f98d7d82b23138304694f0441b14d7ddf9c0f8a921c \
-    --hash=sha256:efa819d7c14c8e4153dcd84671826331538be7cbe460383fc6386f5eea5bd234 \
-    --hash=sha256:f3109fe4805384effc8d0f8e41fbf875aa8f389af91b4348c1cfb60ea6e4cb82 \
-    --hash=sha256:f3a367e0e05ed2d1b747ceb07aa728a8c204cc008b589127e9bd4f40053d7575 \
-    --hash=sha256:f6a8dfc5ab204a706f6e5d39c6f77c18c27ef084fa2081803a64a9160ce89277 \
-    --hash=sha256:f739e0b601be7300c5697a2573d9200bd1db74b34ab111ef9537b9d5dcd7f106 \
-    --hash=sha256:fd666cebd6ab3b3c0fd348a6202c26e18a401ee34293c3804d3472266bc146f6 \
-    --hash=sha256:feb16d9c2a720e0120c58dd5d6e7b3c7c86b43249b60a3bc212bcb8fa031e2dd
-astral==2.2 \
-    --hash=sha256:b9ef70faf32e81a8ba174d21e8f29dc0b53b409ef035f27e0749ddc13cb5982a \
-    --hash=sha256:e41d9967d5c48be421346552f0f4dedad43ff39a83574f5ff2ad32b6627b6fbe
+ast-serialize==0.13.1 \
+    --hash=sha256:02686b281ec9b8e9614f6f0db27e12e4cac515f336c5d05b678bc9eb73ff2af5 \
+    --hash=sha256:032b09d86c785c3984e975378b7861f2a68ac44e22ba7b07b93a536b2524eeb8 \
+    --hash=sha256:0d764913374ba21df8cd618045b371ed104ce55c6276de7c59e554a4f5ba26fd \
+    --hash=sha256:121e1d08d58b75c15491cc3003609cbad71ac2b0016043c36d30a6b2032b6605 \
+    --hash=sha256:1b158f1c9e3a0d386913924c57995d6df78224868a4d0f215bdd41587c97b34a \
+    --hash=sha256:2015fd0165e463aac3b1aadc6a1fa1e5820c14ca950821f4fe02f8a3f6a388d6 \
+    --hash=sha256:23d768369b89d551077dc173da6892fad00443338417523b6732f4e8ba4a7ed5 \
+    --hash=sha256:2876444a5f87a7c76f371af3c07c2fda563a08bc8af52568df812e8aba4bf568 \
+    --hash=sha256:29422d7bcd9e7f39411571c36cec45ce8a7a9b3ad4b2e7aa64497c15a9e397f6 \
+    --hash=sha256:2bad302ae2427454ef9dab71bd5c3ad67188860c39d36daee38f72031edb39c4 \
+    --hash=sha256:2f9a9ce8b0994f757b941f7f7fe384a6666b4162b941ebc5c248081baea18e47 \
+    --hash=sha256:30cf89b6a6844542d116c758725d13de5b97b9410a51ee577715f761270d0c1c \
+    --hash=sha256:3e129d44b0cffbea24a7f40117ce49e30993c3d119e584d4817ebd6f87246456 \
+    --hash=sha256:401cc84e8888d4d76f2c8d296fa006ed1a5ff993b6aff90dd777c03973efd025 \
+    --hash=sha256:43e8ddd63e80fc280c2f790157386f27f9b9f6ccb9c4f8e803b863cbfb085769 \
+    --hash=sha256:48f11d96c9ec71119612f8e79a8c55c12f2b136716d68347433c561d27a25f43 \
+    --hash=sha256:4bcf1d5f4eefecaa325a34ecf079b2741189e7d0821523f92cb343a389a67489 \
+    --hash=sha256:4e385b17d5bde892a6184003a9aff3518387908b73f8f5ea539313c07c8c0ede \
+    --hash=sha256:4f98da562e5901d69c7dd30885594c5438f859edf354e9ac7517d188fb026c3a \
+    --hash=sha256:523d45bab16ddaf1399c04c4fe81bbf180f81e33c2f7bcbe76be56b0f7311ab4 \
+    --hash=sha256:5d99910e6b9a9b9360bcca2ae99aee36cc912ce058df2a57d1c33099b6cb2593 \
+    --hash=sha256:5db12d843d931b9d1f1519ce66b9cbfe72d8563b75c1204d255322254d1964dd \
+    --hash=sha256:638333fb8ae72c62753f9e794fda20290883ddc65b0d85e26e08f8bb227567ad \
+    --hash=sha256:68f8829d114dab6c9db4a8bbb8d0e342958faee1b5e15a29022678df639960f8 \
+    --hash=sha256:6eb0be64c9b8f1ed26637eef345abe75ea90351c92c85a8aec7838b3af971011 \
+    --hash=sha256:6ffb0f548a7dc126067fdfb7b2325ab5dfcdeecc29faf5e0f0461c96d6ebfa3d \
+    --hash=sha256:732aaae9e498c973fc63fd7f308009b57c4afa6ff59d0b674d894e57d0bca01a \
+    --hash=sha256:75d7750fe98f6f35a96c43aba8d98a2e623e22c778a0c17ab9ede92eb10f5d82 \
+    --hash=sha256:77a6201b69ce42e919f2fd9a559138d5410b5d8afff7c3a6b1f500b0481ff7d8 \
+    --hash=sha256:7a5c38bdb93669c596f94fb7204dd6ebe4fadb19058ac9a2faf2948c2a175f96 \
+    --hash=sha256:7f2427bddfca208e84de700044fadf9aef2769a70bae740a1bdabb89ee9e1117 \
+    --hash=sha256:7f3e8a3eff69af640db985360fef35073fb46956dfc3e5c614cf00920d2746dd \
+    --hash=sha256:847cad4c22953823f5e76d0b126c6f9da670cfa45b1df41b9324e22189d77611 \
+    --hash=sha256:87427913c325adc811e81e7c9a757b061f47ef1e29114ac479aa0953a2687a98 \
+    --hash=sha256:885a62ec6481ce58ab24c6357360d7a82023b62dd7e5e7ceccf59e9662a3272b \
+    --hash=sha256:8899c038b1c15ae8b98e379057fb3ef398ceb0b21d1737a8156dd5a0923b7e51 \
+    --hash=sha256:88df960e67184a71874e5b2ee014f87d1254a0dbc1f903c7bd7b1ab7733ecaef \
+    --hash=sha256:8c8ebd419811c435812d242fb2a173e57dfede198c9ac9a0a584666ebc9b9331 \
+    --hash=sha256:9221e09496fb942901993c1812ee87950cc0ecbb514c7c0f1f5fa6d78f701ed8 \
+    --hash=sha256:929eda0c419e622ab49df3a4c45f81c57dcc10874bbad55d0470a4a03324dac3 \
+    --hash=sha256:9f99786e0d62082a5b121b3437f3167562133711df22128de1e9886f57f0b226 \
+    --hash=sha256:a01b515b25a03184eff4acef25b981ae007916379682e908fc8785b342a0bf3e \
+    --hash=sha256:a789cbe14d0a0e9ec9b32a456e5abc81ad8799479c3cfd88a29e3442262aebe6 \
+    --hash=sha256:a8ab2c2585b2e22e48cd4aff2136fce4eab4ced569b85f150ef9a5a5d6f34d49 \
+    --hash=sha256:aca07de3ca8e3d9f2b716c3c31f4f384fe4bd2d03e09912417cff7a3e08036f7 \
+    --hash=sha256:acf4e9f055d75058ab01536da330648746f2f82b7697a85230547f2d5ebe895c \
+    --hash=sha256:ad88921f95b92bc144d9ad059a0e16f8c1ae69f5239f2d3c6536fd2774f73dfe \
+    --hash=sha256:bf53a3ba1cbe45399fc1e4ccd684b8f2a11cca450f89706b79122f478534c6f5 \
+    --hash=sha256:c652d9f5d52d8b81eff3ff2c95c9dd0f281de45f6ad5d3fa95527550c396454a \
+    --hash=sha256:ca9acc67f796aa2554fa3037dccc022a4b08b38b2ad153edfac9c9bb7cb1f3c6 \
+    --hash=sha256:cc34c670747d85d4232834665e247009413eaebe47c69eaf60a5c439aaecaed9 \
+    --hash=sha256:d9c1a920b2aa0c1e016bed7721689717034ca0dba64ac3a3ff243b003d4e8dd8 \
+    --hash=sha256:ddf7cbc9c8abf70102c4a088efe154bb86bfb825b0a10e556d2b15972cf99bd7 \
+    --hash=sha256:e14c4de98f965647a74e6eaf37e20207124e45451ccd36e84a6f6ebab45e0372 \
+    --hash=sha256:eb41e1906502ac80d24ff343f45008552a3f5b5158607959fe6a07dbfc6eb037 \
+    --hash=sha256:f8b17e2921e56621bcb46792bd3e0b82ca3b85de78d5936e7b8174ba1758b0aa \
+    --hash=sha256:fb8021f4dc3296de18737e3b8b34994411da725374d74a0b9eb32a738f2a23d0
+astral==3.2 \
+    --hash=sha256:9b7c3b412e9e69d172cfb24be0e6addcc9f1bd01a28db8bebe66d75ccc533d88 \
+    --hash=sha256:cb7b49a3f0d4c64ae666be131276d2a3226134c598db10e672028cf8ff855f83
 async-interrupt==1.2.2 \
     --hash=sha256:0a8deb884acfb5fe55188a693ae8a4381bbbd2cb6e670dac83869489513eec2c \
     --hash=sha256:be4331a029b8625777905376a6dc1370984c8c810f30b79703f3ee039d262bf7
@@ -539,18 +531,18 @@ bluetooth-data-tools==1.29.24 \
     --hash=sha256:f3cd96de927ddf3ec44813a829eea7ac1aea53592c0d1355866b4f5170026cd6 \
     --hash=sha256:f54ef148ad751eaf1686380b48847fec7f95c7a12c1593b8b062d92f38619e3d \
     --hash=sha256:fe6ef046b7182e7bc083f43835f8768c842d99f136cb6af1eeb9201928521608
-boto3==1.43.103 \
-    --hash=sha256:524821052527f6446d249bf710847b032d9b12135e346c9751777a0a2811cf04 \
-    --hash=sha256:574796187eb4e4fcaaf5c1b88c1724a1ba5a95bc27aeae5573676178666acc71
-botocore==1.43.103 \
-    --hash=sha256:6a6a561a6de43845ae42bc7ff7e2c798742bfa277f5215398f9c15ed9b1bd67c \
-    --hash=sha256:8c7f220e09f3b7ec99c59c716aa66cf6f5b2b57fd8731544054f3778aa744c6a
+boto3==1.43.121 \
+    --hash=sha256:0599bdde7d0c03d914d9247b0a328ea48c15b0b3b5fb31a153857fa5bc7a4fd3 \
+    --hash=sha256:fc41ea80507416c30a3f7bdea3682124551ec0c36405c0d8149efaf65d9628e7
+botocore==1.43.121 \
+    --hash=sha256:39bfd17e69f3370350e6aac2072df64045d002f9878e09115e85b87c772bd473 \
+    --hash=sha256:69eb571c74ff140cc3a716aed3bc25d09eb7b12de4ea2f990c03785a634f9dcf
 btsocket==0.3.0 \
     --hash=sha256:7ea495de0ff883f0d9f8eea59c72ca7fed492994df668fe476b84d814a147a0d \
     --hash=sha256:949821c1b580a88e73804ad610f5173d6ae258e7b4e389da4f94d614344f1a9c
-certifi==2026.10.19 \
-    --hash=sha256:035c1e85572b141bf1c3a3eff0e33a8eb74917522f2559075ff8d2fea780a1ae \
-    --hash=sha256:42d35340cc5b9ba78e818ddbff0c5b1c2b779de448a340fd1b989f5fa8670e1b
+certifi==2026.10.23 \
+    --hash=sha256:a9895e6e2758b371e0545e321a3a8fd1fcfd9829ada8824a936dfb16aaaf36cd \
+    --hash=sha256:e9b54de76e530bb6cf0ccd036787103acb58fd42ba930ea8bf948ddbaa2f61d1
 cffi==2.1.1 \
     --hash=sha256:046bfc24911b37851ee1b51aab8bffe713d89c68c6a057b09484ce9fd5f69b4e \
     --hash=sha256:06c72bb76605a4b0cd0aad6930b69d4baf7dd5d806cfc409b824191099700e66 \
@@ -652,179 +644,179 @@ cffi==2.1.1 \
     --hash=sha256:f8ec5e643a9a937f64e1999eb9f75d072263751912dc5cd06d3c85f8f44be7c3 \
     --hash=sha256:fb92203a88b3d3053034db775110081c49d28be6551923805e039924093761e4 \
     --hash=sha256:fcd22650c908d7b7da162bbfaab594a1227a15d1643a98c68b122ac642fa2264
-charset-normalizer==3.5.1 \
-    --hash=sha256:00668ebb0609751758682eb0b5857e7c35b9f00e84dfdef062e103244ec94d45 \
-    --hash=sha256:012a22b88a77ca2e59b98ac5889b0deb604147666032f45e6d6e217634d2550d \
-    --hash=sha256:01e93745f7f219b703b60ba7afead36cfc4242782be5af484673fc500df12da5 \
-    --hash=sha256:04368edf83514385ffc3e1cfd4546e595f4f1272dd23ba437a93a9cc3741d47b \
-    --hash=sha256:0722590aabf9dc6a6c0343d523c05458fa2b5047dbe6302fd526bb570600753f \
-    --hash=sha256:07ffd07412fc5d5e84cd8952acf9ff7e4ed7a708e69d1bada19d8ba91711353f \
-    --hash=sha256:09a7bba9f739468c8e78c36a75c33768e53cb1959fc638f510454c14683f00d5 \
-    --hash=sha256:0b2b1b3fa5670c127b246df1d0c059defd41f689a868a3b9d79df9b1cac42d22 \
-    --hash=sha256:0c6dfb5ca6723eeed15aa8e564a014d69fcb8812f94eef11fe3631e0508199f5 \
-    --hash=sha256:0d929fc574b4d6fd9e7c0f5c2ede8716a41911923aa7fa5fce38e0818aa4a1ac \
-    --hash=sha256:13e3afe97712e8887cd516e960c63f0b93122971e5b5e4b2622fe7701771e838 \
-    --hash=sha256:15f024313246a4ed976c60f440bb8d257815513a681d212ff74fd46f7d715a90 \
-    --hash=sha256:195ce897c6153c0700078142cf8efe3e6454ca4cf4357499e4078dfd83396626 \
-    --hash=sha256:19a3dd5aa73cef1c99687c4fc57db016a9c17104ae1185da88ba566a5d3bebe4 \
-    --hash=sha256:1d1c7a53a6c2103925cdd6d7229f8c567379f211c869793df679f2e9f738c369 \
-    --hash=sha256:1f5883d77fd409a261abb5dc8ccbe335720d798b1de4abb3b1d47ccbbc76b53b \
-    --hash=sha256:21b82d8082f6f5e7f456ef0bd16323d08de1266efbfeb476e64b2a91d1471a4e \
-    --hash=sha256:252d099029bcbea642f2a06c4ed5046bdf8b5a8150b64afa5e027e88b106e5ee \
-    --hash=sha256:256dd4d85d9e4dc595e2bc983c980e73f62ddeb3165c58b4c3dfe78c5c8548c1 \
-    --hash=sha256:26422d45fd13551cf564c58932f7d72b4f58b93b0fcf18c35ba6be12b46bb102 \
-    --hash=sha256:2679de311c7946dde5d3b6f44941844133ff5c7cb86099c0061ab1e8901c20a8 \
-    --hash=sha256:29880d17a8eb0b5cfdfd8944b468322928059aa35f1f5fa8ff22b149ec0b42f8 \
-    --hash=sha256:2bced4061f000f7187254a02ad3433ae17eaf991747ceea2f478422590a5bba9 \
-    --hash=sha256:2e9cf9253119d8e5d111f05d71626786fd3d6193817316eab1ca088cdb8593cf \
-    --hash=sha256:2f06b7eae9dbe77fe1d644ca244dad508de8d302870a43f3c559b521270938a0 \
-    --hash=sha256:2f293479cce755c75f1697e87c409b7ae4c555c7dfecb6e988ad13abba943031 \
-    --hash=sha256:329fc3ccb63ad22d867d84c2adea759a64079a37ba4a343433b02c7a2816871e \
-    --hash=sha256:343fb4f2821043bd87095f7b08a1a181febc8e36ac64212143bbfd0a0e1bc235 \
-    --hash=sha256:3588e376b3ea2eea84976f67273d679f229e24c66dce7b82ae45aef04ff6e072 \
-    --hash=sha256:35aea775dc2bd5f54cd84a1cd2696cc3207c479cb9cf0bd346f0d343e4300ddb \
-    --hash=sha256:35fe081843b35aad20ffeccec3eeffbe637b15d14f3fb22cc1b59cd8ec17e93c \
-    --hash=sha256:36047af20e17097c3bb9476c2b7655f2f7aa51322c0ba58c07695bedf755a950 \
-    --hash=sha256:3617ac3cfd8b9888f145ad89dd6e692285834b0201c6074a5eeaad3fd4d668c2 \
-    --hash=sha256:366ec70f5547c640d3ce1985722490f23faf4eb5216a7eeba78277490e78dacb \
-    --hash=sha256:394fea06235c8543390050ed5f529187074b029fb027213f6c46ac11ab5d950e \
-    --hash=sha256:3d27167433c0d5f18dc850f07d0b3816221984fecdc405d6c157a6f0b8f8e9e6 \
-    --hash=sha256:3e5e1224c0a6a90e05843e07adfec669edebec17801c67072f51e59561d63c0b \
-    --hash=sha256:41876ee62a3dddf48ff1121ad8f0798032aa03f2fd35f21f34a4cab14f18d8d2 \
-    --hash=sha256:433c5a81eade63b47e522303bad236f59dba55ea6951746f5558355eeed8c75d \
-    --hash=sha256:4582c27e8c889d64811987b5967fbd3ae0c823fe1fd933b543d55ac20bb475fa \
-    --hash=sha256:485a0d363cafefcd2538a73c7c838daa2035f09b2c9f9b5e3133f80c6aeb84c2 \
-    --hash=sha256:494b70049a4d69aec6e8137c13af4cf8db8c9f9820a1392ac293b0dd2987a818 \
-    --hash=sha256:496846868fea80e479324862fa877f02411f2fd0f83b79ccee2607aa68b2a032 \
-    --hash=sha256:4abdc5f9ad448c1ecbfae2974b820535d6bc6e7eef63babbab3d81cf46968c71 \
-    --hash=sha256:4b599739b93b2cbeded49645ae3c8d1405c29ddfbceac1545c87a3f9580a9e96 \
-    --hash=sha256:4bea7f8ebe90bbd7f0e4a2de42ca6924ba23e3e76418c408ff82f1d46fabd687 \
-    --hash=sha256:4c4fb141a727957c93edfe5c32a26ceb6b5f6461d67146e2d39f51e16170bea8 \
-    --hash=sha256:4c9548dc78002099910abaebc0a72ac58b7d30931869e0351c09b507dff4ece3 \
-    --hash=sha256:4d26f14f041e83dd8edfd61f4cd4fa7285d31798b5bf1f28e70c367ba6c41d61 \
-    --hash=sha256:4f298bdadb8f0b9e5672877f647d1be9373ef5320c9e2f049795e26cad28b6a9 \
-    --hash=sha256:52ec005752a56ae79547a05c0139ca2501a0c866390b6115008456b9f0e7cde1 \
-    --hash=sha256:55261ac0d2941c42f196dd576f543d87a8ee03cd6f5e30dfb4d807b2e3b9121a \
-    --hash=sha256:56490c595a28b1bb27dfc583e816152a9767721ef58b2c03b13f954d2f707420 \
-    --hash=sha256:58d3e12c88e0950bca850ae1f7c256055c097639c2edb9eb123af9807d8b15e4 \
-    --hash=sha256:58d4aa13a59c969dbfdf9e6a9560e242cbfd9e8a8f50c2747714df1a423adf65 \
-    --hash=sha256:59171c6e45bf07d0d5cab3b0bf81d945035530f6873398b3b531c31184d46663 \
-    --hash=sha256:5b6d1386bf0096d26d3a863dc0a487a5b4eb9aa93cf5ba69683d29dde6b9d60f \
-    --hash=sha256:5c0ea61a470e070686aa30892fed79e297d2c8d0ab46b8bcdf027d38c51da591 \
-    --hash=sha256:5c84bec0ab5ae0c64bfe73a7d2adcb5ce73b467523fc27fd6a28ab2aa6cbe35a \
-    --hash=sha256:5ca0555312ae2fe82715cada7fac375530c2f3349e1eaa1bcb33d0283ac79a18 \
-    --hash=sha256:5d8531a6569d025f68e2321e7638fb7978f23db58e5f69f56913837aae03816e \
-    --hash=sha256:5e2d0e146dcb57034f8b97dc58d2d512cb90aba253960ce449f695fec6a82c6f \
-    --hash=sha256:5fc45d653ea8c9a20479167e11d4a0f8cb2fa3470737ab6f9c827532313187b7 \
-    --hash=sha256:6117b84ea48435e5356dc737f5121485c30920ba43375fa7b434fd753df0eac3 \
-    --hash=sha256:6199d5606e2bbf2b096cf64d03f8b6790c91081d5ac866b8e7bb6422738cc60c \
-    --hash=sha256:62b55f6722735a6c472f88361cde6640608773d9443cebdbb51abf436a1fcdd3 \
-    --hash=sha256:687c9ca3035544b113bea2055e180af96fb63c0c476e22a9180f51925186e7b7 \
-    --hash=sha256:6b7430cf5728e68f6c462254009a6ef4086e1bea43cf2f57aa9c55fb4f50ff96 \
-    --hash=sha256:6ba32c4d2abf1d2fe7cf27d280f4cca5664233b0f885549c7761719eb977f486 \
-    --hash=sha256:6c9cdde8becb25a7fde49924511aa2644d6f8081cc8df8e9452724303348d8e3 \
-    --hash=sha256:6df0ec430f9a831772c23ca5a224cba36517a58a84bb32c32bb59a9fa67c47f6 \
-    --hash=sha256:6e2912d4babbc65196ac13c2f53468dc57fb8b9c25ef913e8c59ddf7c6dc0e1b \
-    --hash=sha256:6e5e4d73d588ca5ed09df1b7dcd1b203d1df3c542e3f50d126c947d432b10731 \
-    --hash=sha256:70055ff39b97c99e7ae40ea3e393fb62aa2e44dbd9b29f8d14f42fb0025c3959 \
-    --hash=sha256:706bfd38730a5ac7a365793269a00f4e988178cec121391f4248d84ad8c972e9 \
-    --hash=sha256:7235dc28fc6dd9d832ac7c7bce95367dedb85929f17368a0c2bee1e080b9acbf \
-    --hash=sha256:774d157f112367ff4abd29019f38f023c24e00e56edc7829c20e358a5a913ad8 \
-    --hash=sha256:77efcff2b23071c349402ac1066667a3d011f62398d81408c9b88ad991747c9e \
-    --hash=sha256:789b8982559ae28dad2356519f841655756cdcd96616410590ae0b17454ee64f \
-    --hash=sha256:7ac76cf9afd34929d76eb7fcb63be476a4853d8a96f0dcf2d0db68a0cbdf9885 \
-    --hash=sha256:7c0c10730342b0c9b35dd1d619beb8214e520bd96a1f870f452680b238aab3e0 \
-    --hash=sha256:823f82903d189af463d7df250ef1f7f696f3cee08cc8d91deb565e8d425f6506 \
-    --hash=sha256:838648accb3a7fd9803fd45c87bce8509648eb0c11bc34e216141300977244f2 \
-    --hash=sha256:854066be00447fa8de2ccbbe893e2ffc4b123ef16d897af794c1e18bd4a714b0 \
-    --hash=sha256:85d5855daafc240cc045c026d7a15fd198a09b0fc8ff6f5ecbb5297b509cb11e \
-    --hash=sha256:85de3134b5379856e323ba37c19c9256d39425f7b76a63af52b09fb4664c2e8f \
-    --hash=sha256:87e4f41d375c0b9be2fb5251aee4b8a689169e134535aed81bf085c3b647451e \
-    --hash=sha256:88ca277405c2d3b71c4e1c2ee0e7966e807bcba86a69d11e19ba199d18ae4491 \
-    --hash=sha256:88e85ab89cb822c1e635f51d6d32e488f94e002e70e2f492bdb8b945543f345a \
-    --hash=sha256:8ac8c94b6539074e0f40899301273ac8402b9b3e01c7b7ba269ff30340aaaf20 \
-    --hash=sha256:8fe532b3c966d1fb794e0698e4589d0444017ae77fc0b31edea13c0e35bcc449 \
-    --hash=sha256:9085f87b0e38a2b92b8923059b4e8789fe40d9279712d15dcc670048d77079af \
-    --hash=sha256:90b7481fb62fbe172c558bc6fd1c4c98d82004a54a7551f20e11ac9bf0b8708c \
-    --hash=sha256:92caef967d287a407085d61176fce4012b1dd62daed4eb6d5ceb26d3d2538712 \
-    --hash=sha256:9362dd90aa7dab48c0054a21187791ccf05473f7dba5d92b8033ae62164675e7 \
-    --hash=sha256:94d78ecec2605a8d0398b0f365d5f12a63248438516f5dac536a5eff7337df4a \
-    --hash=sha256:94fbf1c0c6cc0d3d5e50f9a9313a8cdca90dd696d34b381cd1704f8c9e939f20 \
-    --hash=sha256:950f23cb393f85543777b0433f082cddd25b51ab398eac7971146495679efe5f \
-    --hash=sha256:96eefc178f8636b9c760c5829345307fd81cfae9ab1e80997dbddeb0f54ee9a3 \
-    --hash=sha256:96fef3e886d6a9874b14f27fc193fbdc69d5d8035783d86aa4e1cea594e695f9 \
-    --hash=sha256:977cdbd483a9cff38179bea4fd754289a6f2195c7abd414aba85410b3e66cc5e \
-    --hash=sha256:978eab16f55b4ab2c2a745be9a0a840bf8f09a7f227d9c76eb30214d078865a5 \
-    --hash=sha256:994e883d17c559cdfd38c84003c8b27d25424a1077272a17e7cd27bfe0bf57b2 \
-    --hash=sha256:9ac4444d8d4fd4c4bd08bf451ed3167aa9e7ec6cdb41b648794f1d1103652e36 \
-    --hash=sha256:9b5db6052055d34d41230fb78d7c439c23dc536a9896f6cb039e8dd92cfc1263 \
-    --hash=sha256:9d9a0dc7cbe9bec24c3f767c9122c41fe5a1bc43f47cd099d00d393e09769de4 \
-    --hash=sha256:9dbdd9205662134957cf0c324f639bdc5031c0ca056e2369e238db75187c0f11 \
-    --hash=sha256:9eea3ab2597a5e65fe65296e2d6a84570845a6b55532d90333d740d48bbc850a \
-    --hash=sha256:a2028475ba855475b8b4d3cfeb4994269c967aea8b9892dfba907f4263a863a3 \
-    --hash=sha256:a3a370082ce34d0612f421e15fe011c53bb1feff21a26d06ad4fb244dab5a375 \
-    --hash=sha256:a545775cfe815855ea32d7c27731d79da358ef2055b4a25830231b1622dd18aa \
-    --hash=sha256:a5cbd90ecf0fc62e64726917ad083b73001f0563657a87ec3c0b504e277dc90d \
-    --hash=sha256:a6d095662e73e74f0a49988e0593373e243e3a52e27bfeea0a859e88acf4a0f5 \
-    --hash=sha256:a6dac12ff6b846103483683f60c5f8fee205121adc58ffd87e90a90a3af69e99 \
-    --hash=sha256:a951ad59cad9145664a730d3036b40b844e74d2d3683da40111463cd3a83845d \
-    --hash=sha256:aa1099b956fb795e686d073568f6dc002a0bb89765ea6d5b055dd7d9bf1b116c \
-    --hash=sha256:aa2bb0b37202dca27175591f761108b5d34096ade1191ffe4808bdf6b1571488 \
-    --hash=sha256:aae2ee51122d3ae968a3837d97dc24a0aeebb0dea23694422cd172bd30017cd6 \
-    --hash=sha256:ab743e9bc90c1f73552ec33e10e3331315acd2c397b36065b591b0181de533cc \
-    --hash=sha256:ac00177c4831ffa650f8609e4bdddd5fe09c03b1c0c47acece7e6ea20421598b \
-    --hash=sha256:ac13b004224fb341e1e25a1ed5e19d32f57cdb2a403e01f003b46f051a550f6f \
-    --hash=sha256:acaf604462bf330b0d07e7a07c1d6e4adac79e5fb13e9c5140590542cafacc00 \
-    --hash=sha256:ae31a1a1db2ee6cc2942fccaf695c934bc7f3db9f2133a3fef1f367cf1a4ab10 \
-    --hash=sha256:ae4a097991662cd4fff0ddc74e0fe7874f82e00042fa0ea00855645ed0c79598 \
-    --hash=sha256:aea996a6aba25260827c9ea511d1addfde2da9eb686ac961838509086188b7e6 \
-    --hash=sha256:b39b69b347e5e47a3b5b8cfc005c68c1ba347474e3960236c4944a8ecd174962 \
-    --hash=sha256:b54e7e13267d49ffbfe68e25b3cbd774dab38fa37238f71265e91b36146eb21c \
-    --hash=sha256:b9af956078716df40d985fb0dfeb2c2120c5ca92ba4ff4b388acfd01cdc14d08 \
-    --hash=sha256:ba2f37ee79e6338845261a3c5b1784e5d1acdff2c0785b284f1b633033d136ab \
-    --hash=sha256:ba501e667c17d8411f98e67a022d9604ef179aff0e459b7e292c796837c13573 \
-    --hash=sha256:baf3775a2635e5a11fbd5e4e64ee69c7e86875d224a5c72aca4c141064589a90 \
-    --hash=sha256:bb57753e36e4855b8ca375069482250a6246372331a3e4f3407eaebb007443f5 \
-    --hash=sha256:bd6c173f04743d483881bffa1478d5a4624475b8cd1d2194956a75548e191c18 \
-    --hash=sha256:be47f99644b208bff7766314013f9acf57b056b04191d570d68ad14022cf5b1d \
-    --hash=sha256:c010f5581d9c612804cc59fcf7b524b707fbcb72828551237ab545bb5c7034af \
-    --hash=sha256:c1dcc36dcb96abc02236e182d17e0f71430152a6c2c7447421da2d2dc144edea \
-    --hash=sha256:c428c6c31eb5f4277d7f8eccaf767fbd548ddd5ce3c8b4f4cbbfab3d96b5904c \
-    --hash=sha256:c658c50ac0c98cd755a2dd50b7977d3bca7df401dcc47fbdfa87db53ef7d4e8b \
-    --hash=sha256:c71fb0d56c920c269cd3e2e3fe7c610e3f1fdb21a6ce60efa6430ff63676cea6 \
-    --hash=sha256:c7b742bf31c88566b4bb6335a7f393bb322e580b6bb98df7bd0c25e6e3519ce8 \
-    --hash=sha256:cc0329df4caaceb950d2f580b5ac716a377f7059624a0bafaeaf8a218c6ed774 \
-    --hash=sha256:cc5d36d96478aa9c60654bd932525bf32964c62a7281eafdf16d85003a8d6004 \
-    --hash=sha256:ce854f5f478050ade5a238731c4ca985a7d3b3cb53ff600a9b5c3b689b5f0a7a \
-    --hash=sha256:ced3fdd71aaa83ce593746c2edb42b7a59cb4c19c8b5c407781c72e493aae55a \
-    --hash=sha256:cee5dd7c6fb5dd52a0fe2a740f9bc6e3593f5f8b1788bde49de02086f30182b2 \
-    --hash=sha256:cfa1c0cc3a8f9f53f1243a5a99ac36fd003880199383b37672e86ddda9cb07e2 \
-    --hash=sha256:d1ee1e296209fdce05b81b663250eefa02213a2da7b41bf26f7829b8ba3545aa \
-    --hash=sha256:d59b75732e9b6f27388e10c14b0259cc5f2e48c78627d185e6a177b58ad3cffe \
-    --hash=sha256:d63600d620ad0064c3a748b950ac5ea38a80190e5498532efefa4b7b3f1da1f3 \
-    --hash=sha256:dd732602a7009217f658d5863d12d79d373a4de0eebc111094bcdd3bb8e0a6cc \
-    --hash=sha256:e06efa066f7dbadbc84ebc126a97c452a6451dfcf589d89d788484949e1cf795 \
-    --hash=sha256:e199fb99720074809a7720f1c0b4d919eea8b87e88713e0f8f602f7bef543d9d \
-    --hash=sha256:e4b018dc5a0eee4676e38fe84a47a427816c590b93b55d9025274ec4d6ffc2dc \
-    --hash=sha256:e6621fb2a4988d6e53eedc455e5903e2679f3967b8acb3d639f1b63c14a2e893 \
-    --hash=sha256:e71c909f353863b2b89c83de2ebed71ea6d0df8a6ef65a128193c5e650766bef \
-    --hash=sha256:e90251c0c7bdd54a100a0dce3c07b7e637278c93af29dbf78ebb89a58c4bac7d \
-    --hash=sha256:e9fbdce1e47394b09bc9f26ab117dfc8d6491977a11d86f592bb42c779db2fda \
-    --hash=sha256:eb12fb2ba69ffa05f8695f61c69e591dc4b4a12ac3757ac8af8adb259bf56d17 \
-    --hash=sha256:eda059b6bc8bc0812d626fd91a7ce01bf583df0a61296eff390fd94141a34e30 \
-    --hash=sha256:f03ac127268b43ef4fe9e6ab6794a6794b49485a0cc0c1db79876d2f33f75bc7 \
-    --hash=sha256:f298e218441525d3794428b4c8b8fb8662c6d3ea79925d4807ee6b9a96a3bca5 \
-    --hash=sha256:f5542f9b941279d82d41eb0aa9f98eba36fe4df5c7086c651df7944935b37182 \
-    --hash=sha256:f6f7deae3feb4edfa2efaf7c574fe88cbf055038a6abdb40188e4fff66d5699f \
-    --hash=sha256:f9b1e28d0e8dbfa858abdba91d6b547beaf2df1a59bec6da6faae7b96a4991a9 \
-    --hash=sha256:f9f8405c2c758532c74fed975dbee57be1f31a6e865c031870c79a6ed3212ada \
-    --hash=sha256:fa48b1b63d639f9483e0633e092f5851e2348c352f1f9bb6c8182f87884ef876 \
-    --hash=sha256:fb78f6e7fcd8ad785d28cd577168bc1aaee827b25bb8755638f694794ea98f0a \
-    --hash=sha256:fbc597639158fd7c14d55e808718848319540f51b0e6746e3eefa59723a4a348 \
-    --hash=sha256:fce8cbd4997efeb450bd298b54f755dcdff18d496f7a5ddbb4867c6d7c88fdc3 \
-    --hash=sha256:fd0350afdc3aabd5576f60ea109228bd5538139713c7b094c5cd27c73a98bc6f \
-    --hash=sha256:fd0a274c0e5f9a21565cd9d3dd749b61f96b7aa1e20a93aa1ba4029518f2e5c0 \
-    --hash=sha256:fdb8a068947befafba9952162645dc2fecaeb400e64584829ed5e9b2fbe21a7f
+charset-normalizer==3.5.2 \
+    --hash=sha256:01077390b03f7988f11d700a2194e69b119741a86b1a638b1db88891e3eced8e \
+    --hash=sha256:01b0c0d2262a9e28e8484a278c7e1b5d650e3ac8cf2683d2967e25899f208bdf \
+    --hash=sha256:04851f73ae72b8413dddadb16a49dfee95263553741fd42d546f7d66907e6be5 \
+    --hash=sha256:0521c5665880b33d603717defa76c094048900010897909952397feb3039da56 \
+    --hash=sha256:0774bf9bf620249fee3e0b8b9fd3065de213be30f3aa94ce2494b3b638949e26 \
+    --hash=sha256:0891b9d3903c5571c03771ca669a4b0ec5618ca722a5c957d3d29cd4e5062848 \
+    --hash=sha256:0c951d5e6dd9c2ff60609476752bee49da4206adde960ebc247766937f72e718 \
+    --hash=sha256:0fed1d06615f022ee3b13caf5e8b180cfea32bb2c5aded8a9d44277afc040f93 \
+    --hash=sha256:114e4d0c92d618409ed82a99e22b5c5e768fe995f2973f78265f4524f49d4640 \
+    --hash=sha256:11912e4bb14baae7c5d8791aa55ba0a3a03ec6729073307b0f57270abaa713d3 \
+    --hash=sha256:11a4d68a6ecda3292cb1e50239e111543ba5d709bb62a6b4ea1afcfa729d8875 \
+    --hash=sha256:124fbf1a8ff966d87ae05bb8bd45a71f966055ed8bba320d0c7cf450bc5f4d0e \
+    --hash=sha256:1461ac396c4fdb983a675f20aa555624f0ee18ac83d832b9244ffff3d8055275 \
+    --hash=sha256:1503bccbeb36d5527790c3930327704c39af22de3112f1b1666a9f3ce15ee204 \
+    --hash=sha256:15bb4005af6320d259dc7593ca84a38d7fe06a421dbcf7b910ae23979101e787 \
+    --hash=sha256:15c44f7edfd477b06f517a5cc317fc1707edb9de2c865f43d4b6513907473234 \
+    --hash=sha256:16fa0eccf81304b79c5cd87f9271c3b85dd9dd99245e4422ae9c0dd45e0f99d3 \
+    --hash=sha256:183b88127acdb4fabe59d951ab424faf1af7b63cdbb5f776186c1ea2ffcaed98 \
+    --hash=sha256:195c26fb65950f8fce54e26349852b7bdd7c5f120aeefbcc440b8a20faaed4a3 \
+    --hash=sha256:1afb975bd5d68d5ce9f6b6d44fdf2f7e34b895a35e95708a7a91b20a3b51d187 \
+    --hash=sha256:1b4cbc7c3491ccb4aa17fcd8165649d01cf39f76de1696da8631b5f71b85401d \
+    --hash=sha256:1bc0baf5ef96b6ede57d47f4b8fe4d9d84019c3bfcbeb20a41edc6a6ee341f1f \
+    --hash=sha256:1c50fe28bbc2ced33386f298650d91218076c05420e6cbd790b913adc41659e7 \
+    --hash=sha256:1db38f4c5496827c1a501846d64d14c3b80c7e6714e406cd7dc36a9899fa1011 \
+    --hash=sha256:211d5a3eb6af8f513b8d4ca19a8c1b7accab1b5f0d3175f9826b03c1a920dc1f \
+    --hash=sha256:23851fb4e1b85ed3f6c2a27b777cdfe2e19fb5b38429a8faf38c7542b7665869 \
+    --hash=sha256:254eb48b9fa5ee9898a3c445825a1f340fe53712a098904b39b0bddba8ea3cb1 \
+    --hash=sha256:2625388c6c754520c37abaf3b41eb34d1cc4a373f457898f08606c8e362b891d \
+    --hash=sha256:281cb91036248400f4cc957495cccd44c275c2e0c5854f7e45ac5cf7dc193847 \
+    --hash=sha256:28a15fdad492a99b6eccfaaed66ef3f74050680545ea61ec8b2f4c538f1f1320 \
+    --hash=sha256:28b4f0d66fb834ff90f28209ac7bce77868c45d8c93e26f906709d9b7c2e1af9 \
+    --hash=sha256:2a925889534b3748302dae5dead07cc13480de1dac3aea80a941b729b471ef93 \
+    --hash=sha256:2b7b3bbfb4fe8ef40600792d762fbaa9057559f9d3fad209525b7a22b99e91fd \
+    --hash=sha256:2c9ad19a6cfcd5ea5c0d41161d22f9df1dcc277e9bef2751391334546a314c00 \
+    --hash=sha256:2cc961b171b3f3440f410489ab3573e86aea8736134ebbb40ea1338b7f0831bc \
+    --hash=sha256:2ce45c6627b22c47e390bc91a41c3d13032192e699fa0bea96e9671b373d69b0 \
+    --hash=sha256:2e06a3a98f916dd41d27f3105e02e7a40181c98c94b9158733d03a6f80506c09 \
+    --hash=sha256:304d5463e65a35d7bb0850550e0780395395f6fcf452f04db7d5ca7cecc425ac \
+    --hash=sha256:304d8e4d493af723536393eee0c689eb7813f4a474c8b479dee63f1fdd98f621 \
+    --hash=sha256:30fcd120b732aa79317f08dee04d7de0847822e4cf7ee0e9f445bb958832252c \
+    --hash=sha256:31f3930700408d211f13378ccbe1c40845d8da54bd0681fac3a9b5aae81c7aa8 \
+    --hash=sha256:34276fd796040bf0993ab33a369aa572e6979c7aab225a88893667ad8eac8f7a \
+    --hash=sha256:355ad8011081dec5412240c087a9a0c9d4d5039f3ed11a3f13e18c2b29b56c51 \
+    --hash=sha256:38a873987f3be698494da8b2e3085e29da02da7b633dce73e79c699a113d7bf0 \
+    --hash=sha256:39de2a259fc954455c57274dc94c79d5842774e1247a016aff30bc0efed0f4ef \
+    --hash=sha256:3d14b50de6bf4d0edf857a9386836846f982b8f524e188e2e68b96d702bcf4aa \
+    --hash=sha256:3d21b8b13c7592db2ac5e544a6d83187b995257472b0c9e8351b6d507ae37ed6 \
+    --hash=sha256:3d31298449090ab8d47b7b1b2a555ff73cac7ed438a08b7ac160980c7ebed649 \
+    --hash=sha256:3ddacd27458c45bdacd6bd6db644bfb730efbf9e830310186e3045c9c5be8fb2 \
+    --hash=sha256:3df041de8887954562c9b261cba85ca0e9ded74048daf125f45edcfaa4832229 \
+    --hash=sha256:40ab6bffa02ae10a0581e6c198be7d2d8ca5c2a0c64e4ed3465d766df457573e \
+    --hash=sha256:4275811936e2f06feff5e598fb42a1b7ae852da8e39605211892b56b81a34efd \
+    --hash=sha256:443eae2bf318abeaf6f15d785138f71fd6de770e99a92158b8b814265e079115 \
+    --hash=sha256:447441e76ec720b15e64418d32e092297340387053047c7c694f579efb0ee1d9 \
+    --hash=sha256:4495c5002a7b28557e7e222e77e0b661183e432b7d6d2e788101e3f240e05b8c \
+    --hash=sha256:44bd4fbb29dfbeba60e7d2bd000c59e4b21ddb3cc53912b14048d37092706d7c \
+    --hash=sha256:4685902cf26edf013ed7a3da0f426ebba7a00ebb9541386d835afbf002c11cab \
+    --hash=sha256:498dc3188ca05a68231ac3fdbfc7f57eb67e1343c30e0fea17f8218c1599b253 \
+    --hash=sha256:4c2b5031f63e331e3839b40aed2dd6f191e9c07edbde303e7876846ea1946995 \
+    --hash=sha256:4d48f2d08b9de5864e2c8744d4461b862fb149a18274abc8b698c45975573438 \
+    --hash=sha256:4f87960d57feabfb618e4e0af6e7371645fa26a277860739d6e5d6e0012c92f0 \
+    --hash=sha256:50e3adfb96fc189eb27b1cf62d3b598b89b4bb0420d93a3d3e42e137409011be \
+    --hash=sha256:51cf45226a9b588d0d2b4880c62d686934b63ab0bd79ca23ab0e9762eb27441b \
+    --hash=sha256:52aa6992700996af31f375de0c6bacd402b0097fe40b53c426b9f51a90ebabc7 \
+    --hash=sha256:55ea99acb17b9325618de155a0cd6a2e8f5d10be008113e1d433bbb58db543b2 \
+    --hash=sha256:56bc200a365efb37383b7852e4cc5898d3b2da5987289b543956cf8cad71018a \
+    --hash=sha256:588461c2e8384d309bd63e5826019b6977bc66d629b99ac8737bb795d7b2cb5a \
+    --hash=sha256:58ca3755ee7ff7f59b57789ec9833c9de9ea275405cdd240eda1f193112e398a \
+    --hash=sha256:58f361dcbab699cf8f42db3f47c8e7fd1036f138c23a5d08de9fde5f425a730c \
+    --hash=sha256:598a11a2c7ebaa5334bf698bf29568c9c390abac6a154d8170fedecd1cea38c5 \
+    --hash=sha256:59f63901b0031c3136cf64704dcb21de0bbae62ce2c9529bc39d27665463de37 \
+    --hash=sha256:5cde776b7cc66e4f6c99612cea4aa7269aa65863f7a15841b2c264f103822f4e \
+    --hash=sha256:5e2b6b57e9733d39f0c9fd3185efa6b8e29652c4cd8fe94180272cf6ed9a78c4 \
+    --hash=sha256:5fb29fb8cd1a46c27a1bf9613ad5ec2599310d46b4025d9556404a6b6a292800 \
+    --hash=sha256:6045373d5a89a5ec71afde535db987ca28e76dfa276c2d4c818265b375d4b055 \
+    --hash=sha256:619799369eeef6366ed3e8755a5670f4f2f0fb6b30a0fd7264dc0fdc2357058e \
+    --hash=sha256:62588a277bfb59def052abd940703fa35107152bf479781a878617d60faf8fb5 \
+    --hash=sha256:62603db9a7caa0802eaa28c1c46fecd7b3a263a774069c24c3c28c302448721c \
+    --hash=sha256:65cd72beeeca9d3aaea1201e5923859f308f952f9c71de93f06063c79f0f7a3b \
+    --hash=sha256:68eb192d85ab8e5f6ec69c2bc6ac0179fbf04a5ac1569d12fbef74883fe102d0 \
+    --hash=sha256:6bd128f206a7752ae1f2ab6c61bf8a24ba28913a10df8b14c2637b973ff97a80 \
+    --hash=sha256:6be488a102b8cf28d0391d8c4ba7748938ae28b78ad901f8585520fca33ead1a \
+    --hash=sha256:7218e8f32b0956cfcd048fd42d9d5779809745ca1d86113ca56f66e7ae1549c4 \
+    --hash=sha256:7441d755b7ab94f8d4eb3e43ec05482d760842fd263d003a99102d742cd835e2 \
+    --hash=sha256:749e97e1b32313717a565abbe321bc2190bc8b35f1a67e4cdbc7c56c8d8ffe58 \
+    --hash=sha256:75a3ceed0724d625d64b86ca20aba182e4df462e04c2414fc941c0f523f06aac \
+    --hash=sha256:780fbe7cab297b81dad9fb8dc5eb003c0468ffb0d9e5f65068c53a34661a96bc \
+    --hash=sha256:78456a747de8dc58360ffa581f30a002baf5aa28cb262536545e91f113ed7639 \
+    --hash=sha256:7967d08cf06dee78443b874f98c98036f624f3a4e73e11f9f64f5be4d25393cf \
+    --hash=sha256:7a881931aa470808df94a8c380eed2bbbc76cd9dc622310f99665658c821eb6d \
+    --hash=sha256:7dcd882da75ef9adf94903b1e3b9419e8aa8fb4c7396822b834b9ef7fb96954f \
+    --hash=sha256:7e841fb9010836c992c9f12fcbd43a831de93a5f726fc1ccd8ca1d0268c5014c \
+    --hash=sha256:7fdde2c9fd9e3eca40631e024664cf2584272cc8f96308cbe5fdfc930f51d8bc \
+    --hash=sha256:8024d00c3faf3fc0c16e07a69f4405e8eac7cc0ab15f65fe6cf43827c4cf72b4 \
+    --hash=sha256:80d02b6f04e92601a081dd97b23d3128033098bff5d35d392ddcc0476ea11253 \
+    --hash=sha256:838dcc90063569a0448120554591a1d6c4a4ffe11babf048908793154ab86ade \
+    --hash=sha256:849df64e889b2e17230d58410a03dba311a65b163508fd33679b2b737d4b7858 \
+    --hash=sha256:87475fabc8d9996fd9c27debb395e642e8c838d78a00b6e932227a0e06b81e26 \
+    --hash=sha256:87e50a3e7cb90af586b6c5faf23e302a970415ac73bd7bd90a515a04b427ef96 \
+    --hash=sha256:89b53f3cda69831909888e0494f4fa0bcd3537e3e138dabeb620bd6ad946bae8 \
+    --hash=sha256:8a893cc101149f80a653f82062ebc95b34525a2614382e1da5458fe7c6997249 \
+    --hash=sha256:8b2bfab86aa71ae13aa41a6a26aab338e0db2b8bc75434b05aea89e011ff35a4 \
+    --hash=sha256:8d86d6fc60743dc916eb79e2eb1ec4818e21e427731543af40a3021851174a13 \
+    --hash=sha256:915563965d418f986e7e145accc592eae9e1a1be3566ff98a05d7a9ec42a76e1 \
+    --hash=sha256:92888bb3187c5ba50500b00b3b310c9f2c651709d28036077680cb5255450a03 \
+    --hash=sha256:93223adc95033dd47133a46ccfc316a0139176fd79085762e27202ec56018f03 \
+    --hash=sha256:9373ad13ef0d2c0fb761e04e55bfdee5a08b52cef2c882c8fbe9935b1517152e \
+    --hash=sha256:9409a8bf35cf78353942504b24a57de3d75b708997a1e4bd8db71ac8633ce364 \
+    --hash=sha256:9b7f416ff0978e2f2249330527f0ad6fa02f4932e6199692d3b52da2048c19e4 \
+    --hash=sha256:9bde855991b7e362c146535e3136a50bfaffc0487d38b33ca7e5edefc6e23849 \
+    --hash=sha256:9cae88599c7219005d879f98e5ed53341e9a122af585e1091200358a3003d2a0 \
+    --hash=sha256:9cf9b1a857e25c4baceeb3624e92a56df3668f398c4acba74e174d81fb4d1d3a \
+    --hash=sha256:9f56f72050826f63dcee7a7f55b0a77168cb3bfc553fd405e7f8f9ece75a4036 \
+    --hash=sha256:a090bb2c68df85450502e3e20d665e3a5af9c65a84d6508ed477badd49166fd3 \
+    --hash=sha256:a192e2c40070d92c3ccf777e3a5c4ff515573cd2bb7ed0c537fdadbbec5bbf21 \
+    --hash=sha256:a19a731138fc27d5682277d3b9df22855cea1239bce7fcec5f78f42ef2d1f3c3 \
+    --hash=sha256:a66c3bc5ab1f0ff2164fc9965ddd611ff0802173f4b9d24554c563f6ab7e1d6e \
+    --hash=sha256:a815775b6c38d4e0ff7bcffbeba67feded90202bb6a226b8dd35f1c855217413 \
+    --hash=sha256:a89012d6d5476ee112d20d998570ed58df2260a852afb1758809cd6900411d21 \
+    --hash=sha256:ae4f5fea5b8b8ccff88238cc8569303e5ee95efae67fa62922a311397a71f346 \
+    --hash=sha256:b6856554c4f44d79fc2307d5768854310a8f0096e501c75637542c82292b0429 \
+    --hash=sha256:b6b751274acb69d77b3323d6b7dbaa3c7fdfc1eb829b7eb61d262f32e1af9685 \
+    --hash=sha256:b736353c0a625bbd5fcec108576e2385db3496f4f771f785ff32e108d3c3bc45 \
+    --hash=sha256:b7fd005a73d9e657273b7a10dc71a9e03c8fb9ee6999798d6918ce095b81ac7f \
+    --hash=sha256:b91363207bd9dc966a691e959bb47f64b30f7ac4b072be9968b366982f7db77c \
+    --hash=sha256:ba0b1d2620edf869789c3879223f52bf2afc5d31b3cb47cc57b3a12c05e2aa9d \
+    --hash=sha256:bbbfc8e28816f19d7c0f1816664980c0a9875d01b27cdf8eedddb639d9e108ad \
+    --hash=sha256:bd16aabe4a02a297c23417aa17ac6299dbd8c49f673bcd645b4929b11f5a4400 \
+    --hash=sha256:c0afc6800ba57ccc350374c5bd6150419915d95ce93cdbab2d783d75eaf30ecb \
+    --hash=sha256:c6708715abcf3c73b99508253e961a9967f02fe536532834149574eda6de0d1c \
+    --hash=sha256:c7c9ab723cde841fefb34efbad91e87f00a674b1fe1cd0784fde742bf2c154dc \
+    --hash=sha256:c8f3d67aeaf55f017982b73683f0e7342ba2f6635a78f69ce89ebb26aa411e5c \
+    --hash=sha256:c9790464842f85f437dbbb54417eda1e0e6bfc52dd8d22d6fd1c994b73b2dc74 \
+    --hash=sha256:ca403d7e4798f525fdfc78e258820419cbbd0f0ecbab9de7840e3c017cf6b8cf \
+    --hash=sha256:d008d90a7f2471519aef0c90dfbe73b3e6e4d5e66ac48e19154c17e89e98b604 \
+    --hash=sha256:d19fbd981a488e22cd04883659ca6b08f50b5974f9fd7c95655ef6a043e5893f \
+    --hash=sha256:d1befeed746d247c81127bb14de9dc3d30edb6e5976d34f83f86ed262b1d9105 \
+    --hash=sha256:d2374b62878abb00cd8309b32af6c0b715cd02dec0ca74ef12e5069bdc64144a \
+    --hash=sha256:d376bbd28b3a8999db1a103b3b388aee6f1ddeb3e51bc2172993efdcd86e064d \
+    --hash=sha256:d4a7319f304a774bed22115bc891618e45f85065ab44ea6acd07d274e750519a \
+    --hash=sha256:d6734d2ef8a50fbf8445c139477da401f50d62a0606bf00e20ec6d87773fefb1 \
+    --hash=sha256:d760fe2a4d7c3b226cb9026d6a842868d52a7901bd98420e1baf14e80da85cf5 \
+    --hash=sha256:d913de495d90407cd859d263bee2e5d1a4ed3eb6573c04e70d9ec619a7cbed7f \
+    --hash=sha256:db19d07e2e0129e974a0e65d0064fc222a446cd5122c2fd4184d2af9fc734a9e \
+    --hash=sha256:dca9ab98072a5a54ebacebdc45f53e645336b320c667410b061be1ca588ae709 \
+    --hash=sha256:ddc7dacc8ece3a182e7f15cb862d1fd616b46d076cb1ae9dd232b2c38b655874 \
+    --hash=sha256:ddf19c062bea7a0cc80f519243d2c01dd091be0cf952a0750d4ad576709559f5 \
+    --hash=sha256:def79fa35ef0cef8d2accec024f4fdc7ead3012ff02f5215c783f39f03ef8cfc \
+    --hash=sha256:df29a0a7107f7011e77f4eebdddec4c7331e24d787a0b21a46d63bdf7445da95 \
+    --hash=sha256:e09a3942ecbdee5cce73ea9d42da82b81b72ac1bf031ce069b93b5adf4eac8cd \
+    --hash=sha256:e242bb1c5e76e97dfa9e7f209a71e93a01d7f19ffdd5cfbb2e2d55b4f08f8ab0 \
+    --hash=sha256:e243bd13217235fc7290c621941c3f5cc8b66e4872495be821d7436ba2fb838d \
+    --hash=sha256:e2af3aad578aa6bd1384bcf4750fc285e5a9de53f40b7d41e5a0bf748edeb2b3 \
+    --hash=sha256:e4e81e09c1578b8df602e3db08b0b3ea0a6947ad612f52bf8dc5ea8d47691f0c \
+    --hash=sha256:e54da4baf05720032d527874d40b65fa4d7e5c6c6a43d0c3adbeffcaf275a2b3 \
+    --hash=sha256:e80e6c2f55656b4824d72065abb4ddd6a525c74bd78a0aab5d9fc2cf4fb5af50 \
+    --hash=sha256:ed2a239c0ea213acc1908150a3037257083c7c083128f1a4cec2ec4b97dca491 \
+    --hash=sha256:ed905975ab14056a2e5eb1c376cb2e1ebc5396baf84163939c518556fccde9f5 \
+    --hash=sha256:ee21e28f0430bd6dc9086c6e525d5e818a44a5ad19720c8a0ef766792f3eb5e5 \
+    --hash=sha256:ee43c17b173d46a3212baa6ead3ae258eeabdae48c263a01ccf0218c366dd655 \
+    --hash=sha256:ef4fcbf3327382cd4c9f540babd61248208af7b93eec4de397b4d5f58a09e288 \
+    --hash=sha256:eff0ac9dbe711a4aee69bf04a83896aa9b85f19641264053a9f6d48573abb7dd \
+    --hash=sha256:f0aa869112ef88429ae17820d99c3dd9504c9e9c671d3c246f3d7442cb051084 \
+    --hash=sha256:f3c96f633825733f735c5a9cf21d21a257d8e1edf0b1cee0a064b9c424ca0f7d \
+    --hash=sha256:f5833ad231be5eb6553de524a70f48d71b2c8563101750531e0b80184e175cd4 \
+    --hash=sha256:f5ec61164adcec446f8969a3358ec3f9b26bbda3b9213e5586d219afa8df2915 \
+    --hash=sha256:f7d486c83842422badd511868fd8a9a20e9407ace71564b6af47ce7e60a336c1 \
+    --hash=sha256:fb9e68df06293761f9fe66ade60a9bc6d0f5e42b8acf2939a9158af86ab0e5bd \
+    --hash=sha256:fc14a032f813bf5fe624d991960ea83e9715adc27e4c1830a2361eb1d02ac341 \
+    --hash=sha256:fcff63213e8e6e47770541a4607175404f47cbb3ebea7b6058cc82d524a0e424 \
+    --hash=sha256:fd1fbe0f116b6e55da77aca2c6ddcddcfac2186cbf78bdebf40fc156efca389d \
+    --hash=sha256:fe9753dfee015c570d73df76f899f18444d41388bffcde097deba51c4fadbb9f
 ciso8601==2.3.3 \
     --hash=sha256:09deebf3e326ec59d80019b4ad35175c90b99cde789c644b1496811fe3340587 \
     --hash=sha256:16a0bc10783e9f06f46357ef77afb74f9b6a250bee7dbc00d51850d5894cc543 \
@@ -893,103 +885,122 @@ ciso8601==2.3.3 \
     --hash=sha256:ff59c26083b7bef6df4f0d96e4b649b484806d3d7bcc2de14ad43147c3aafb04
 cronsim==2.7 \
     --hash=sha256:1e1431fa08c51dc7f72e67e571c7c7a09af26420169b607badd4ca9677ffad1e
-cryptography==50.0.1 \
-    --hash=sha256:01f41478cf33fc605a6a089cd56d28b45c6c0b45a1928b61797f2621a04bac71 \
-    --hash=sha256:05ba322c4da95b262a212c345af888ef2c37c88c0509756ea00a0e6d68850f23 \
-    --hash=sha256:16c5ecd954b3330ebfb6605eca4fd952da8bef376551d5cc264534e3770a9ee6 \
-    --hash=sha256:2a93d05e34d5f67fba6f891fe85d929999baa7195e853923ea6d7576c9e68c5e \
-    --hash=sha256:2b34d76a652ea2b6faf777c35df230c5637842cd904e04f16230c3f9f03e4361 \
-    --hash=sha256:2ebbfb0f1fed745e91796e3e1080a1440423fdae8ece1b995a1d80883a409054 \
-    --hash=sha256:30a125032e5642a21ff816e021152bd4e7e94f03eff3f4b7fca41cd22bc3110f \
-    --hash=sha256:330fbb252391c596f1ae42c5754449dc924e6ad012dca8efe0d703f9f2d12ec6 \
-    --hash=sha256:359e62deae718bce96170e223fdcb6357e4fbd3bb7a3a75f4430763532560e49 \
-    --hash=sha256:407fe2b6db00939c05c0e945e9914238f2f0a430974839429dafc82b1ee6bee5 \
-    --hash=sha256:42be3bb70596b3abe4ac097b75be223e8b3ab614a0e5de068e3dcc54d71d6149 \
-    --hash=sha256:4c4188f7c0cf655be5c06342b817ed0f9595b69ffa2b12026e5353eed29dea88 \
-    --hash=sha256:51593d180cf6d179bde5c5d065bed81386b1f381656ae7d042b7ffc87a9895ad \
-    --hash=sha256:51afcfceb15597cf2635068e4ac9a56b2abde622edde17f37d85fd7b5306497a \
-    --hash=sha256:53e279950892dc102c6b4e52af03ae5ea92fac572a1ddab78ca73a997f62b69f \
-    --hash=sha256:55d16b1ef3ee0958d893a977b19777887e546c9954ea81b200c3301a864013f2 \
-    --hash=sha256:5dd9bda1c12b4162f6ff568eeb5e0ff956c28d14406e875cfe8a63a2d414ff20 \
-    --hash=sha256:5fe002589592ed749ce77fe0695fcbd3500dd61d7d6db5858a7544c612fa8e45 \
-    --hash=sha256:5fe939deeb161024a6be98229c953b6591fef1f41214497a78fe793a244c017f \
-    --hash=sha256:693c99b49bd37d0d096e4334c10232c77248c415b98d35236094cdf96d57258b \
-    --hash=sha256:76de83fbd91ac49c0feaaa983d0748fd7a53176afac5fb3bf7478d244f0eb527 \
-    --hash=sha256:79bf008d1f9af6071c797ad133e39915dfee7614f18f18f4db9072eb715064a3 \
-    --hash=sha256:804728ce710890870f3aaa344b2e161172d258d768ac139d02cfd9092d0d94e6 \
-    --hash=sha256:8921d58f426793c5f1b47f0b59575780de9a095214958d0eb37d909593db8367 \
-    --hash=sha256:8df2de9102026855887e4587084f6eabd80ed0f345b8ad8a7ac27ab9bf4723e0 \
-    --hash=sha256:9cb3cb952cf5a8abd50c782a98a89d71699715e802fe349704b47f2425b42a94 \
-    --hash=sha256:9dde0a357190eb3b1da1bb9ab750e9c85cba82ca5977aa0836cbb94e92611239 \
-    --hash=sha256:9ebcdd5519be9b652a46f507817a74591774fc3d6923ac364e4dfa64e36b291b \
-    --hash=sha256:a0b1a59e3a089064a0ec309e9428c8e3ae4e161419d20ac33600767e83fc658a \
-    --hash=sha256:a255449073358275b64b67d3f595f268bbef70e72b6edb65e0c70c735bf739c9 \
-    --hash=sha256:a8f40ea47330e71b594a7e246898f93177c259490c63183dbaf9e571d71ed9a5 \
-    --hash=sha256:ac02b07824d4d1001bd4367599f839c19cb171924c796e52c23508ac14c2c0cc \
-    --hash=sha256:aed8db4f6d71c51efb89530e12d9464e7bf2923d46c3205dc794a2a93f8c0648 \
-    --hash=sha256:b8f852c65863251b9e3a1b8c150ce21e59b522dbb6a7d4bc80e680d38388e986 \
-    --hash=sha256:be224a65493ec5b74a158ff22a5522ce4a5ca1e543c647a3a4730d4a09e5f959 \
-    --hash=sha256:ca83d00d9e69cd5eb63f2e69c3a5a59e0cecae5ae14c6ae0b35830fe3b37bad0 \
-    --hash=sha256:cbf74a81765ee67413503ca6e26dcc4f6f5a519822436cc0a1b97aab6c1b8a17 \
-    --hash=sha256:d63ae8f6481fec907ac0f588eee8a90aefde112c633131fe540e5711ddbb5a4e \
-    --hash=sha256:e22dfed744bd4002e909464cb23d2f0b05c6f3113a79ef2e9864a53db737c733 \
-    --hash=sha256:e2ca8fd1b6b4b82a1c4cb02841d0837e3c12336c2e24b520ab8ab3b969733d8f \
-    --hash=sha256:e74591e283fe6eb956416c929eb58262a719fe0311fd9054c62c3350ed8760d8 \
-    --hash=sha256:f74455bb086a85d5e81246412602aaa97ed095e504cd40dd261ef50be42205bf \
-    --hash=sha256:fb4b9672d389c738b175c4166e78310f8a70358886aacd9173ee03a85ffdc671 \
-    --hash=sha256:fc3ed7ebd2a8c96f5b166de0ab9b624996bef3b07bbeb19364dfb78222c22c80 \
-    --hash=sha256:fd3718b960d0b5dd213cdf03f3bcb7000e69dda0de8b956061947ff6bcff5558 \
-    --hash=sha256:ff838d62ec1bfce4f9ba7fa16f4a7b554cd8d0c299e6be37502161a660c84eef
-dbus-fast==5.0.22 \
-    --hash=sha256:027b358d55164f722d7432d6734506751c89b5cee8d516e7282eff3eaa763f05 \
-    --hash=sha256:048f34299fbe82d7b87c56f47e8bd83f62339a4517685abc6671d603a55d2c89 \
-    --hash=sha256:04bac97d0cb754a4d13037d0132517f1df28192d6e0568a0bf6df06623062285 \
-    --hash=sha256:246780dcda59d26dd2fb1d9a15991bc8483e9c241cee8713920a39a363ad4d39 \
-    --hash=sha256:26e26b409e1e6edf5e2a4df8d192625fb38876b074fb5c7d0a5b15c5792e549d \
-    --hash=sha256:279d212e9fb262d595af2e4b5b9e951bc00c73a5c8eeb50f158caa13705b9c84 \
-    --hash=sha256:34dc67d7d21a12399828dd13e63b352750580beea54ea7c729e708f2d2905fef \
-    --hash=sha256:3a699fca957acc845ddb12b47f741dba23ce147fdb93583e0c7e7bad3e9b2355 \
-    --hash=sha256:3eb57d592d84b0bb90e0c077db7ecb61562f49cc9b86a3ef08cbe17243e9cc4f \
-    --hash=sha256:4ffcf16034f71a801bd2108aeffb6337d104c9459e8b1a218d16a917c8a2d2e9 \
-    --hash=sha256:511655d915692f55b8c5f5a535acf80cca9c6d1a35384db7fcfdabaae05dd837 \
-    --hash=sha256:58e4d41f9fea22cfd6dacdf03d53b932bbe15a825af5abad3ca79b91493a15c3 \
-    --hash=sha256:595bd3ccfd8318cbafff79f33a15709fee3728724fd61d5fa220080d73b574cb \
-    --hash=sha256:69a077c296eaab8c30160e861b5514c33d99d67d41d17dbf02e89aae44543b11 \
-    --hash=sha256:6c4dae5292a7924ec062815c34b49043d8386cd22e165f9fb4012de00997cdf1 \
-    --hash=sha256:703e0f8f9af52e8e053394ee2b578042be0c3d8ea2b1488f9db8cb14393cc13f \
-    --hash=sha256:7af3e81287163dbae29d583a19fdab717a896bb097946adde415439b0ee322fb \
-    --hash=sha256:7be4271e38251f1ad726962dec60da887c8ed352d157352e4fc27f56aece5c5d \
-    --hash=sha256:7d1c42963235cfc015a2d2b8c5fe42b65387493b4ad4ce0ec122601c805e6742 \
-    --hash=sha256:7f2af2fc27f3f188387befad5901953863fc8fa6451202083c2b9ec9f970028f \
-    --hash=sha256:83940ea00d7ee2f0c5bcb5d19d7d05e7949e52d467616a0b735d72e7285402ec \
-    --hash=sha256:846f9a6602b4383f989201f7851459fb225a8912cd24b38e63894748545c3040 \
-    --hash=sha256:855f15b7f7805171da2b82de1c317d01cfbb9fb8ac61fcc1e8dec54d8c69fab7 \
-    --hash=sha256:856f0543c593f3480e93e67bcd1aa4ddc1d94a6076cfd3ad4e0f5e2b01b33dc3 \
-    --hash=sha256:886b43446b6fdc3986befbbb88db1365b14e49dd0a7edf84c2c67ac66c7160a4 \
-    --hash=sha256:8f0bcad7f71d2304a68a5b0bc0d24c3fcc14710a2ffcf5f2a27521e3aece71ca \
-    --hash=sha256:92df9fb6d8adeb17b534621c2ee730295bbe1d0c2584d5c82b1db478e3f04e8f \
-    --hash=sha256:959fab6420897ab99410e67d6f9f9a7f6f4cedb6014700768f5e2d71dbff5dc6 \
-    --hash=sha256:96d231d128c1f46f263790335897195dde9dac2f38571782db8ae1d8647bd548 \
-    --hash=sha256:979761985fe343c701f2b7575285d6e370123f7231d4656209ef7824bb686bbb \
-    --hash=sha256:98de6d2c200d8182e1fd0bdde3206fa556b8fa14ebb752a044cd8daa87b4658c \
-    --hash=sha256:9a5b05fd4973862042e5bee2c5e8c5a15297e0b33a975bf25b44becf7bcb3618 \
-    --hash=sha256:a127ff97079fd052d2b5dd752abc3fc5678b0d15ce9d04be1796bcc7f90b8b03 \
-    --hash=sha256:a160cb931f22c43ddc8efe6ff33f03d3111442b9c0007ba58269a717296d8536 \
-    --hash=sha256:b013437b66dc22b8d9aca5e0b0d46bf1980208a143409469fe482d9684a2a717 \
-    --hash=sha256:b3db6388b80ca167299f2eb8eb60e74f07c6e33a1bc4320c42bd9e5ab192c587 \
-    --hash=sha256:b67a02037eb58bcf9e445df60ea0d9d7346fd334abde3aa62e03c75823b53979 \
-    --hash=sha256:b7d90a52be79acbaef257f3a81d5b9b9dec40f1bad29429ac5c7802684fb9b84 \
-    --hash=sha256:c32869678240f233ece5a1137960c0337699dbb39acc02c155929f52543f03fb \
-    --hash=sha256:d8ca39f3f2ab34f88bb343db87c7cf8b07eefa046b23d8c38b3387f150ac609e \
-    --hash=sha256:de10ff3b3cb2acb1c09fe17158a470519000d37bb5ee5fd69c4075e81ce8dcf5 \
-    --hash=sha256:de4d235d1282ebb3ab65b6cddab84e914c045d92ceb381ddcbdbaf66bf1fb132 \
-    --hash=sha256:eb1d7e8e65561d0fd438004fd9e0f981c8a862912fed58dd4e29db1936c39d73 \
-    --hash=sha256:eb31c5ff339a7071b914617a69d5b7c6ba7d411da4b01a5f9b5b2fe51e9d1301 \
-    --hash=sha256:f0926e4cf49989b4ec8233e8fd462eb35a640fcfe81bb75d91675dd47489022b \
-    --hash=sha256:f72b77be63f7bb24cf42936ad10994d40f43fed691f857f7854b5882d6a5227c \
-    --hash=sha256:f74700b1b4fd58acb76f8790e2cd475084d0e59149e0cc035abd239435a339b7 \
-    --hash=sha256:f8244561e503cffcd5e6b1ff6544a44aa0b65b6856f2f64d04345ebf82f8ac48 \
-    --hash=sha256:fb73f1d8374253b7c17d69e902cf2ded1bfb089cb6ae67c10b4e0bdfe1b8fe08
+cryptography==50.0.2 \
+    --hash=sha256:0ddc924c04591c2811ca024d62ecad4f7f6f08af8939c211438f48a16bd23602 \
+    --hash=sha256:0ec5f09541743261e66e291b4a0cbf0fb2997aeaab6d9e9c740b9dba1b58d1c2 \
+    --hash=sha256:0ecbc5652bdb6fc9eaf89a7d196e20941adfe812f43bc4ca05d9150496821047 \
+    --hash=sha256:1981f1db4630889b9ef7803fadef12b056f428cb6b85c27ba57b774793b6093c \
+    --hash=sha256:1ba34f04897fcdaa73f74145c25f3ec146fbd56593853e88adc2e811303c5f42 \
+    --hash=sha256:241449bf940a5d27309bd317e6f9a2af6932113818bb2b8f5c59ddc7ef16da18 \
+    --hash=sha256:25784ce8b9621c90c643efb9e1e2162ab3b0224cae446ad5e70e7fcb1ce18b51 \
+    --hash=sha256:3dc4fd8058cea1644971207d530e1a03a184a805ffc8ebdddf0599d78a331b81 \
+    --hash=sha256:4061c0079120205fb760c58acab6443e217307dcf05e3702cf970e0689972856 \
+    --hash=sha256:4a20ce1e5cb4284a86692fdcba7cb8754185c6b2e5c56fcef3751cf451d3cdc2 \
+    --hash=sha256:4e81d95e5bafc2d6e34e4bed780e53e4d5b9a2f928573428aa4d35fbec1eb0de \
+    --hash=sha256:58a0c478eeca76fe5e07993c5a0703def34a6dc6a0cda4f5564639b33112ffe7 \
+    --hash=sha256:58ddb5a8e3179d12f19e4ea34d2d32e9d63a4baa142c875c1eb59f41b7243acd \
+    --hash=sha256:630ebfea3bf689d075f82316324ff7433dc447fe6bc1bfc76524b74b4a9567d2 \
+    --hash=sha256:6f8700550aa1474a91e5dc07049c46f98b423b5b1ddd0483e0b51362eeeaf5be \
+    --hash=sha256:78198641e5be9521beea5aa782bb551a58068d10e6eb04c9c680c1b69f2e7d45 \
+    --hash=sha256:79def8d059362e7831389ed3be0ecdf58a89386e1271e35dd9f5af84e81bffd0 \
+    --hash=sha256:7a8701d6b584d76e909e3d305b7d126b41439876a5aaf76cddc67fc230eafa2e \
+    --hash=sha256:7afa5a6602a9f29af1f3a2965f831bae7c9d5d597b7cbb716d41ab3b7d89879c \
+    --hash=sha256:7b46165bb56eb4704e2eaaf86f3c940d19154535d9b0ca7d6d590b04060e00d5 \
+    --hash=sha256:7b75de3c8b3be1cdb1052747c929440c3eea46c1bc2cb8a6e3a48388e9b7b452 \
+    --hash=sha256:7c6d0330c472d96f6a6afe24d80dfdf15176c33096f0a4397ae4c60f3dd3be48 \
+    --hash=sha256:828d49b0ff5a0e3975865571c5d91dbbdd0d38d8289b249a163e9425413a5e05 \
+    --hash=sha256:84f964e537f916e2cc85199e5a88742e964939b575ac8598b3f9d6cc416cdaf1 \
+    --hash=sha256:85d0d9a31b9098e98534226d5686b47264b95e62ce459dc2e62fdfc809f9fe93 \
+    --hash=sha256:87e9ce85beb6b328ba370cc6e6aea483c92617b4c95b1d33a49297eb662bfb04 \
+    --hash=sha256:8c71ba2cd31fc93748c38e1b613200ff1c2665cbfd5341fe3a61cfde35a1430e \
+    --hash=sha256:92e665960f25fcdc73725b9cec7a3824f279ba97a98653afe9ffac2e43668f67 \
+    --hash=sha256:94e5e9f108ee10471288214d3d233fbfbb492840a8457eb85178d643ddeb32c7 \
+    --hash=sha256:9c8402a82ea0dc4ceeab793db05f0fafa8ca139ca34fcde5df0f596103c74107 \
+    --hash=sha256:9dab55f57c74c3cad24c323bacbbd04be4705ba6eb0d92e920b1fc4837ed5079 \
+    --hash=sha256:a582ab2ae1d34f67112cadc86702774c9ea4374df6bca6afe672817203c99134 \
+    --hash=sha256:a6557e5f38e065ca9fbdaf7cfc7435ecb1d113aa81a022d1b51921ee7432e227 \
+    --hash=sha256:a9f7355e6fab51f6c369b86fb7571cffa05edee2c2121e0380a37fb9ac1cd5c1 \
+    --hash=sha256:ab50ee449bf968271e820086f10a33d101dd060370abc10bcd22279be2656539 \
+    --hash=sha256:ac9ed99d81760c62fe89d5f0815cdfa1ba9a35141cf30f1c2d044f04b4803d2e \
+    --hash=sha256:b13478603dcd0a2479ff8e87e2c19a7d525734686fe3c49542472293a204212d \
+    --hash=sha256:c423ab384a46c4dff7217b2ea5ba2e11cffdeab6441acd04cf65a369caf0366c \
+    --hash=sha256:c5e67125c7dca78d199ec4e116aa93dbb83494808ecbb8211a2cb09b1bf41dbd \
+    --hash=sha256:c71be1cbfa5cd9a41ee452acf1eccd82b2c05950358b106ec8ceb83411d1a020 \
+    --hash=sha256:cbc8738fd8526d80f35cb3a40d41f41a2e7030bb3b18b09a6778ef63d291c2fd \
+    --hash=sha256:ce47f66801c20ec6c6632453bb5960fe38939e9306970b48b3a5a26de7745d94 \
+    --hash=sha256:d370b8d1dfcdf7130178137f6fbee6140774a1acc6cacefc4b42643ec11d0a3a \
+    --hash=sha256:d38cdff612d06fa6a32840d5e1b1f7a27cee4a349aa9085d94a67789d6bfd408 \
+    --hash=sha256:d8947001be83df1394050758ce0e745dd74fb134eef0a4b5124208dfc3a68c37 \
+    --hash=sha256:deb9fde5c60e437ee4821bc9bc39ff31b42135c27e1dc61ef0a629389c1de62e \
+    --hash=sha256:dfe9763530994147d9af1def057a5b9658b00e8f8fe8743d144d1e0911c2e454 \
+    --hash=sha256:e105ab60406787da31fccc883fc0f733af1efd78f0136a4599692c4083a73d0c \
+    --hash=sha256:e275096ea1e60cc595cda2836fd4a6c725d1125108b868be17f53684d164e2cc \
+    --hash=sha256:edc3342adf8f697fc5f59c887a304356f147b397809440ed64e2fa6af2f50f37 \
+    --hash=sha256:ee247f5c245c9a2fe7c8e2214e295918838e44e00a45a6718451e4004219e767 \
+    --hash=sha256:eef4c2f3423810b3070ab391f85436d2f8bbfcb286ac15cbc73190b3563b1f1a \
+    --hash=sha256:f21e8a22c8605750c7af886bab299a363721264061b4ac0a30efb73cfd58efc5 \
+    --hash=sha256:f265528741e048bce55c3463ed721fb0aa45a5888d8add8cfeccb3035451bbdc \
+    --hash=sha256:f2f9bd7f90c64fe89253f0a2c05e3c4856072660429ce8831b4235bf29403a67 \
+    --hash=sha256:f785f6161f202ab04d8ca194158968798e480ca058943907972da5f12e2881e8 \
+    --hash=sha256:f9f6143a8c75945eb960d9eb98905a441394abfa24afaae239d514ffb2586480 \
+    --hash=sha256:fa8f5efb344d6908a1ce62f4a24e2e5780f825d6f53f5f50ec5ffacac72936cb \
+    --hash=sha256:fdd28f912fccfec1846a94e2e1e8f9b0012f557f0c46fe4f3eb0d7a87afcf90b
+dbus-fast==5.2.0 \
+    --hash=sha256:0858d3f0a9b9fe506e6847c8200e85fda4b62319aa5712e61dfa696f19e0d1f3 \
+    --hash=sha256:0a772708d25c11e980642781f603882e3dc51b5767be19075ffc5a484c4d3411 \
+    --hash=sha256:0c0d6ff2dffa3115fb5c670a0d17474827428ba87991f5e7b4d3791f0abcb07f \
+    --hash=sha256:0c4e7f48961e7c85540086458be0c5ca6ae6272e327c15907bd7d1e777ab2ace \
+    --hash=sha256:0c6df68c231ebb3649d8a1b1a5011876fd44ce780988e329c65e62308ecafbdb \
+    --hash=sha256:0e061cf9b31c540af7641739fef11654392c283f3c611f5009b6019b0d7c6ddd \
+    --hash=sha256:0ffd0427bb7fbae5d3bcf493c294581824bd446a563fd0027e77fba77f634438 \
+    --hash=sha256:1aad5984b9724f438a2ccd5e3df15723aece0d248b309576744345a04eee948a \
+    --hash=sha256:1ef8b5882fb74dcc6eeebb9502fbd247e276309bc0d659097e8793ba193d0af4 \
+    --hash=sha256:236327794a5957238e83c363809903b6a47d1f4fecd64831a29fd09458d90f0e \
+    --hash=sha256:255b79663e44708479a9b15f4a05be633186e6169e9ee4037001b036f2fda989 \
+    --hash=sha256:288111b8d920b5ab445c2d9e4f13cd8521fe5233efe191c4749dd8fd07c5beb9 \
+    --hash=sha256:3177e819532e30da3847d6c10652d4f97e0c07f12180d2e470d60b6141ac8b34 \
+    --hash=sha256:352e4cc8dbc608e297a73784857a8f9841d3a221b10e4b0f6a1b4b5168456e51 \
+    --hash=sha256:383d6d43dcc6b2ca6c079b5a16cb94ea2c86dd8af9a8d22f3f29d960a9fe1533 \
+    --hash=sha256:4944cb6cf92af103b4127e3935f138a8852b8268444ed8bf7975c507cad45c8a \
+    --hash=sha256:4d91ce3cd74b3b8a1518afca3ceb90ab7b280a53e9c50a257453b83e48c4b19c \
+    --hash=sha256:594f755fe172c76dd1a7f6558504244a0713da4ce07d9cf9abb5db80372a5d4f \
+    --hash=sha256:5bde3e9bae0af4bdc27afa9b4550e15ed55c32907b45620d35b36bd0f1ba28b4 \
+    --hash=sha256:5c8b4b70b8811e3fe431370f7e9699c01eb097561ddfa367081e5abdcf34a9a8 \
+    --hash=sha256:5e8d93ca1b3d344c7ff5c4959e6d8ac2c6a0e794aef9d1606177647d537b7e99 \
+    --hash=sha256:5f6cfee9c3de4b8a3dd406abca9aabe2f28ccefc7b68f9b26c4f92ccc9b2fe4e \
+    --hash=sha256:6121b816c9026193256c3e66ff774669c0c30420420e62c270ae2ae3a9592d79 \
+    --hash=sha256:679f2daef2b88d6129845013403b32d184ecf90805fce247340469bd5f495943 \
+    --hash=sha256:74b8a6c22657740523f8d16e4d373925a408c7dc30dfd4935ea21939c042510c \
+    --hash=sha256:788861134ac1794d44a03970fc817896b4bb35247353eeb13c363e238f7d4474 \
+    --hash=sha256:78fe0dd5dbdaaf281d32d4e609f99cdc7eac3872f9ca805d27d30b3f53d893b3 \
+    --hash=sha256:79b842eb42f439fabd47db9deb7846d849933eb864fc53373d355c63f850eaa6 \
+    --hash=sha256:7c66b094e96c221b877ccd6627bc3b9d808ac8317a8f6adc1cb2a0223e7d64e2 \
+    --hash=sha256:90da44436de6f5773637216159b7f0c5b53aa357c54c38593b12ff3ed3a4e649 \
+    --hash=sha256:93615c23d5766c796ce1835bf76d5c20b3908e087e7ffb1da3aa7ac99f2446f8 \
+    --hash=sha256:9945f15b3cff4857a82498ee933f5c56aa949afe3bcbdf62e4c7c670e7ac7ec3 \
+    --hash=sha256:9a17cd5e062ebfa48f996b4aa5db7202eb8e2df9ad5be36bf39198422e6457b8 \
+    --hash=sha256:a0d506adfcbd5451e23ec2b645437ccf419e9ed7ad1f6f82b622d2a292fd23e5 \
+    --hash=sha256:a4a5dddc04b1ade5eb7650d791e2f6fb7c1334595593473914e78a2526ecddda \
+    --hash=sha256:aa260884e2df72d584ffec2d5d2f90ea0d624db8326ff0bea33b59f8998a09f2 \
+    --hash=sha256:ba81e8455b9b893dc6ce31535049b938835beea8c20e85e181fc23e46f0bed12 \
+    --hash=sha256:bcc1514888cbb82533777f3855e06135e5e8526ca6d7f75687b8b1fcf140ce33 \
+    --hash=sha256:c0ca312d8643f1f358f9fd96d2ccaf8dccd01d0c14c08c20e3f1686aa198231d \
+    --hash=sha256:cc171f8b0728626eba19ac5893cbf1a5a813120e6fd0440168ba013f941abeb8 \
+    --hash=sha256:d01ae4246b3b503b529be3f4ad3660d92687b5d0f085683d2ef48ec3247d5133 \
+    --hash=sha256:d828828f879c0536981c1eaf2d4c6fa65fd30354cecb1e16a158a9cda36a827c \
+    --hash=sha256:da7835ccc6e8cb2b54516558097156da6dbf6636c27033b427135bad693317fb \
+    --hash=sha256:dbe4982d86e93fe285c695c0808601e7187f01501df77c2342d4132c11bcac17 \
+    --hash=sha256:ddf103405d0fe9b0c764d3ce8d59e557bed1d68aff7d3b16f6eab94bf6f85d91 \
+    --hash=sha256:e5a0742c9c2bdae7599d1fff06a609cc7cf19d4a84bf7e6e2cea1d086d1ecc0b \
+    --hash=sha256:e5b07944dce15b734f6d0e80a54f66909de6fca0671fdf12ed512758721ba4bb \
+    --hash=sha256:e6f32672a446284b0d381349c91f6602356a4c017c1604fccbcc02347496be92 \
+    --hash=sha256:ec7e32787f43ddd637da4b46576e288deb0148c19253ac5a3cf5a69e8dacbe08 \
+    --hash=sha256:f0c3d3f153fbcdaae27409afe7ac42654ed768c8de2da35aa929ba4143935455 \
+    --hash=sha256:f22ac2df864dd0532f3d797f21118341e7520d6b36ac68a327eac6291624fb2b \
+    --hash=sha256:f4a47be94f369cca2308645345df8a0949e9139f9b0f6e64fbd11945924b13b7 \
+    --hash=sha256:fc04ca465f9d9847aa4273efe85da8fed82988004f1002b833df788f48fc0ecd \
+    --hash=sha256:fc5845602cd734e01bcee84fc2ff08642987d95d42edb434d048103905d3173f \
+    --hash=sha256:ff55fddbc7567cb39f10b5d7e9bed1f2b19c88fc1d18c86fa67ca06becfe8fe7
 envs==1.4 \
     --hash=sha256:4a1fcf85e4d4443e77c348ff7cdd3bfc4c0178b181d447057de342e4172e5ed1 \
     --hash=sha256:9d8435c6985d1cdd68299e04c58e2bdb8ae6cf66b2596a8079e6f9a93f2a0398
@@ -1251,68 +1262,68 @@ greenlet==3.5.6 \
     --hash=sha256:fdacf26402389bdd89857ad3c045a26fe8f3314f9a8b28226f82f88463a65b77 \
     --hash=sha256:fe3170a69fe039b18ad18171e66faa9a75f6fe9d78f968fd9b54e09fbd714d81 \
     --hash=sha256:fea4427d1ffdb3b523d7daa6712038428a4c16c450b9777bdd1221cfee0eab49
-grpcio==1.84.0 \
-    --hash=sha256:026d757df86c5b7a41de8200b9a2cda454aaa5004cb0c7e3374c66eb82f61499 \
-    --hash=sha256:06619ba1515e5ee69fb2a514e95dd8be05ce74cb3928d5b34f87f87c86fe3c27 \
-    --hash=sha256:08735e3d08d24ab3132cf87e2e5dea8746cabcc7d676c2b0b7362f195feef9d9 \
-    --hash=sha256:0d532ade4486dad9b302ffa4d4683d67561051c26d17c4023322845e9fa10140 \
-    --hash=sha256:158c1c11cfb61b4849c3caf4d52de6f5ecd376e14446feb4a90dc95a90d616f5 \
-    --hash=sha256:15bb76489e337fc492685c9758e2fd4d4ab516b901ad830dc5a91987decf00be \
-    --hash=sha256:19aaf172fc2edbefccce3f6e92c5150975dbe56c45744e9e87cf72ebdf85bfbe \
-    --hash=sha256:209414080da8c20af94df1395b635da52dd57b5edc9e917e1deca0dc1c4bb55e \
-    --hash=sha256:210e4c32f907045eb8158273e60c6ab69a3947697df6245dbda381f26c59485b \
-    --hash=sha256:23e6e8e8a75cff88e0a793bfd3becea03a13e2763ae90c1ff573bc19ca5b429a \
-    --hash=sha256:27b8b36200a9fbee6e120246f4a8a41657549107ef19fb2c819c4b2fd524f39a \
-    --hash=sha256:28d2609691da93051e998495108bbddd2a9f7a561253bae94828d81290f30c15 \
-    --hash=sha256:2c024da73b296f040b8360e60bd73a659b230093684a438da0e1260f34cc724e \
-    --hash=sha256:393d8a78bff6731ecc5ad2151a821f8fbc1709b137ebb9c25a4ef399fbdcc914 \
-    --hash=sha256:3d6a82c4fc6c85f2fb7572c86bdb86f84c97b6580e5f6599f711800bac48a5d8 \
-    --hash=sha256:3de427b05f244ba2c2a9bdc67e7a6731c8340811524ecc4435466549f8af1d17 \
-    --hash=sha256:406583b4e8fb2282ebd392e12b963e601c1f82e07125a8c2cb5b144e7e024796 \
-    --hash=sha256:4119efa6519871719ad81f33bc95ab87857dcb1c5801f30a6e592f2c41164169 \
-    --hash=sha256:42959bd50dd660ffc3f2a9bec15a6da4f9aaa0dda555d59ff2d2e80b908456a8 \
-    --hash=sha256:455ed6083353b8e938f1d58c765eab2fbb165731e5b507be30fee344915a2a11 \
-    --hash=sha256:465eef3d17e59ad22a556fc0138f7c7c799df426734344daec42c797d49fda99 \
-    --hash=sha256:47ecf0d9b81d981f07b61bd89eced9d2582f5eaacc3aaa36ad27f81aef70a27f \
-    --hash=sha256:49717e857899f4136d7657bf5aded61ac479110a075438290923a4d86af7cd02 \
-    --hash=sha256:4aaeceeb7fa7d824c322d1ec3208c8495c88478a927295553235435fc49043ad \
-    --hash=sha256:57dc36a5ab0e676f5f6e171de2917fd0aef73f32a9aaf23956bfe19997a30bd1 \
-    --hash=sha256:5933a052946873d01a42119a05420d669bdca436aeba2d1851988ccb12b421c0 \
-    --hash=sha256:5deda5b4bf62769eb98c119cca43d40e1231e34846b19db5cdea821d446a2253 \
-    --hash=sha256:61386101ecaa096b694d0dd278caf99a56aeec78440cc17e918eef0b50f2d567 \
-    --hash=sha256:659728f20fc7a0933ed7b1945435e31014b97ab8a5a7edcbaa70da4794aeb191 \
-    --hash=sha256:70bb4ce8be0c5606bec259cbd7152374470396413b7863a658a08c849e6b29ff \
-    --hash=sha256:71fd60e6e426d293d0a2f685115ad0a0845117602cf13605a4be7524fb5f7bba \
-    --hash=sha256:756ea5c2da00fa65c930284892d2a9706828704ca3ba40b4c51c4834eb39fcfd \
-    --hash=sha256:800b7e00d92553313c0463c200087930aa78678ec1d528193aeb50906f55989b \
-    --hash=sha256:82da34ae4f639c73ac46e521e00c0a49bf86f717b9fb1f405f133e98731e38dc \
-    --hash=sha256:8e1a45d174b6b8589f51dce1cea804aa6c1f72c9c80cba91ae2caabeb6d90540 \
-    --hash=sha256:8e3f508d0e9e6236ba2f08d56e33355e434e785e813149a1b8477d3edf69779d \
-    --hash=sha256:986e9751d416d7a6eaa2fecdac38da63153d63a4b340ba7d624889c490451500 \
-    --hash=sha256:9b73836ba0e16fcbb57c31cf6cbc2907c8d8c790b83679df454b74bd15e0be04 \
-    --hash=sha256:9bab4cf571653a8afffb83ce21aa27b51dfe629b526b7b6adec35491fe1fc2ea \
-    --hash=sha256:a71d24f40b0cc6798feaa978c7411dc1135b7018e9fc0442db611c139bf58344 \
-    --hash=sha256:a9383401d9f116f98cacd4eba6c505a6edb80ba65badfc8e8ed8ae64983bcc44 \
-    --hash=sha256:b44f0a0fc7bc6677d38cc80bca1a32814ce6c8f200fb8b3c1a61c9d77eaefbf3 \
-    --hash=sha256:b5c6f20d657ae09ae4e30d9d3a21edd13f1219d58cc6f999b9d1bb63be9c1baa \
-    --hash=sha256:b61692f0069b3eee2fc8a3a1b7f6c044df9e03fede6ce69b3ca832e1c39f26c5 \
-    --hash=sha256:b8c62888c3e49debf37ad9773e3c02f77b0c1e811f8fb0962f2b6c3bbab5b97a \
-    --hash=sha256:bd8ea8eb3817b226057cc1c0e7ec4b378dcda52043b972b6ff12b1152178967d \
-    --hash=sha256:c5559b492007dc09b4de9b95dab05f0b5e53547aad230cf07e46c7dd017a3be5 \
-    --hash=sha256:d0fdd25faece8a1f95e8a3a8006e29701b5cf8dadb4a8132e68f3134637004a5 \
-    --hash=sha256:e094dd21f077af8194923fc263cad872eaa1802bb0156fd7e5ae18e99cd86715 \
-    --hash=sha256:e41c3993eee896c617dbd8a505085d28b6e84a0445ed9a1f40f95808473cf678 \
-    --hash=sha256:e88d304f094f4937bc27ec6a435e218a084168f11ec630c8d5d39b431d08d81d \
-    --hash=sha256:e90e3bdf7b5eac005fef631adae9cafde16f922def207b80a7c46b253c18ad20 \
-    --hash=sha256:ed2c1493c44d0932f1e55fdb5d1ead658c68288ec5d51b8c4928422d98633ef9 \
-    --hash=sha256:edb6f87fc60ff438557291501b3e16c7a77c3b01a52d782cf276dccc7c5dd89c \
-    --hash=sha256:efb29f8633bf6630dc89de4fe0353ac3d7e4b70ef7b6e29fb40f00e68c127fa5 \
-    --hash=sha256:f6c972474ce691aca74e58d17625450cef153dc4760364cadeb167983ea6d589 \
-    --hash=sha256:f6d178ba6dc8e82976c184b65fddde172d054c17237993a3e083efe4f134d55b \
-    --hash=sha256:f9a456bdbed52a01c9ab8423bdebab04a5363c78676edc55ab9b58bd13bdf9e1 \
-    --hash=sha256:fbdbcd06986ede3ce584083b1dc2afe6808e8943e5cf50ad11183c03aceda25a \
-    --hash=sha256:fc66cb50c93554b86db0b6625ab5c6e9051dbf8847c08d93c84918e02e413fb7 \
-    --hash=sha256:fff5ef3fe1bba7d6147e5f19e01e5e122ac2c076486887ddcb8d42e663400fbe
+grpcio==1.85.0 \
+    --hash=sha256:0633c4ff112d2237d09ded3044b5acee4fb12de7b39ff4dcfb09b0f029c33992 \
+    --hash=sha256:087f297442a62e267f37df0cd03681159c225b8e73741b94d55c515e7a4df81e \
+    --hash=sha256:09ab4af4c4c74baa9b17f9a6fcdcef5be98357774417d624191ec41690df4bb3 \
+    --hash=sha256:17641f3a6ff3512c34e5c367805d2632a43a773d7990f1c4c55243df6bee8fbb \
+    --hash=sha256:1a8ee918b5b18c82be2e5f30978258269b858d7e16a36e8729c09d9654bac2f1 \
+    --hash=sha256:1a94f32df519cb7efe3822f7f3c2daee0b0e2f01a281e1db5dbfb0efd1635b6e \
+    --hash=sha256:25007d0e4657dcdafa9a80677895b71de8c1d6335afb7fa6a4b35330e2d3127a \
+    --hash=sha256:26147a7a3c9d1c865cc16b3f98e5c38e5606932aba236b7627ca7eb4378c5c7e \
+    --hash=sha256:27b024f8420c9d63f7df9f51d4c2d2e54fcf3b26c9963041f5fc75b83f35e87b \
+    --hash=sha256:299b13839203e82be15216ae4c3379801a3ad216feff05b165f14962f0939b0c \
+    --hash=sha256:2a04b67a146f1a95e2bd281614be89b662973535a94eac944135ea86b2e5a7ef \
+    --hash=sha256:2c6a55a4cb43fe9b14d4aae123ee655cdeb288d8810bec8f8c1adce0d4359d8e \
+    --hash=sha256:2dd69ec2998c2285c323bfa2e3acbd7f475881db97aa9359f2edcbf9ae284169 \
+    --hash=sha256:312939c9afac5d9d5e3b9e50c40a9ebfbe444ca35b28a99ce34903cc9279a5b5 \
+    --hash=sha256:372e9cbf91f74127652138b020cf15c6a44541a91aee89c50a5943d1996b44aa \
+    --hash=sha256:3b463b3b97f35149a3f69234de92eddfd7c94c9c19794e3b264ccba7b6b03fac \
+    --hash=sha256:3c49f03d8d74196ca6d1351b749aab3fb3362c850286f28aafcb7cd773134b04 \
+    --hash=sha256:3ec59a8175c0bcf51ac767c7baa9083ec369284e1055614bff246257349d4e19 \
+    --hash=sha256:426e41a32d10f841f41fc67e4e6d150af7e7c7c3433fe61fa3a0ca19a8dc9885 \
+    --hash=sha256:4c6c39eee05f6b98266315486a93f36d73a59adc4d34f8b63f1b5725f897d8ea \
+    --hash=sha256:4ddfe8b667889b9be5990ae674b13f0db0a9eb61972306038d0140a1da0f0b87 \
+    --hash=sha256:5427356333810631bfc3541da05fa57bcd4a0bf846728d8512c9e4bb1f97b261 \
+    --hash=sha256:55a1df9e50009d85fe674fbfe31710b6b3e83702c857114832449c498e78593f \
+    --hash=sha256:55cee7cfe71b29f6b377681936f9a5f35e59f5c941a4d84e2712cb309753e7a9 \
+    --hash=sha256:58c0ffd1eb2a0d7d216a0c8faefde999586fc017e735dfe9d1142a8481f7d0b6 \
+    --hash=sha256:6127bab580cc247c6c62f460485afeba10ec7b9e1b338eef8bde1344acfd9ab2 \
+    --hash=sha256:6248ed9a86c4191a0d8d7fe54eaea0511aadcadc2ec128daa995eaac91e42880 \
+    --hash=sha256:7a24e53259c2005c77b03c48272eec4b374eba027d077e84d0e99f9e30747439 \
+    --hash=sha256:8572f9d7282cded6b018fb0147d09bbe7e59177ba6c452f1903682a80dc0857e \
+    --hash=sha256:864607775e0166a4d3d6bd8276334d96f0b6e9e0a84f3964dc6005db07e9627b \
+    --hash=sha256:86bd1d2e197d3e4cde1c04136db48bf22a6fe873b7f55c83e9747d5b36f0cbb4 \
+    --hash=sha256:874af68625a2ff2585cb112e7583c19a7cb463ab638a7fe5b8a58f76e6d4e7c2 \
+    --hash=sha256:8aa2647afcbe5a87783e9626a2ece6277db33c6604c21690d19b5bd15609e36d \
+    --hash=sha256:8f1c7cb18d7beb81aa65666b739f8a43261df7f9529628e639b578b6d344cdf9 \
+    --hash=sha256:9c91ad19d92ff81600c087db4829c26b47f9dafd04ed0a26c35e21a05d20f671 \
+    --hash=sha256:9eb6e4149d2e8ea7fc56052eabd36f1bd52a3c0a53f1eeec74528654a895456a \
+    --hash=sha256:a03fee5e413938ddb71aa2fd7c52520e2fc3aec2e9602d50464272c75b274a54 \
+    --hash=sha256:a11c8c322a19d6d3cd6fb645127e8f1ca4e8041d05e41e9b24c7678ec7391021 \
+    --hash=sha256:a8dd5c3823194811c5e6932b454bcaa7b8e474a7690ed4ce6246bd502849a82c \
+    --hash=sha256:b016a4663ee8ec37b0e555a65fcc129598404bd5c14d8c00d03f8da551ce0e30 \
+    --hash=sha256:b10f0f0a34ce6b122dbf5dcf8226cbe41509c602af926b1e55113ad9e49cc5f7 \
+    --hash=sha256:b1ea46f63a7a9e19ce5cc09be0a6f9b347e0dcc14c4ab47b48488f6c093b8171 \
+    --hash=sha256:b2da79c303f23e66d08baaa0c78d8b8630c700e1562babb1f326ada0a97ee5d0 \
+    --hash=sha256:ba535a7b78d5049101a896efbb4ef9edd471c322ea4fc0cc8245545b184ff687 \
+    --hash=sha256:beb6ffcf5253f4247efa47837d876e42157969127657fad4a68be181830ddadd \
+    --hash=sha256:c02d956990c55730efcca487a4eac64f8e0fcb3af7e53c9e89cd02a985669709 \
+    --hash=sha256:c5f993fa6b3bf0af33ed7c2bc42f58d22f10964607cf614c2c08b67db80ced60 \
+    --hash=sha256:c8accda49358f99875057ff1ec6a79fead12dac41ac63c1c1e1757a2aab14c1d \
+    --hash=sha256:d115d1d4e31fa964a348e54445154cce1649da4204f07425028608982d056a2b \
+    --hash=sha256:d2ba969495b45ff5e0d10451898387427906b82e28c3c1cfae2dda006e25e18d \
+    --hash=sha256:d617b017395ff7a84fe0aa682890a366afcdd502f2610029052165cd3778b561 \
+    --hash=sha256:d6c43a06a059a95f03013aa5fce9106a6a2b6b78cfff4003a53e0eb410c0e1d7 \
+    --hash=sha256:dbd651df4cf258f2073f8a10f878cee9b8723986ca69206a0da67a2f1651ae86 \
+    --hash=sha256:dc726ae4f2f4e2215cb1b987b8ddd7f4f2f253d6ceb48cfbb9b88555d325e10a \
+    --hash=sha256:dd88a98073ebc0e6771ff8c2fd9451fbf887f575b0da9d30246ee1b2813f6b57 \
+    --hash=sha256:de5b49ab15a350170905b03c03f88f277f83e1910fa87e6f12c63f2da7480a4b \
+    --hash=sha256:e0b87fde3b80955343b37cf9b9deac52432e9e7a4b3e0f92abbd61fee0f7b184 \
+    --hash=sha256:e2f1c3089ed6ae75e24529a498a6b65941fdb6856c3416d62c88da944947fc88 \
+    --hash=sha256:ed8ca34cc644a82602097249bdd9af2526f2fe93c641439a19351f3ed2e91de3 \
+    --hash=sha256:fc1a478ce75e66ab9cbf7077bb12b2a31f75de091122d48845f281f8fd47a0d7 \
+    --hash=sha256:fc2865f523feeac453f35c762a2e4155df58565229d77069b211f2e21de2e79a
 h11==0.16.0 \
     --hash=sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1 \
     --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
@@ -1377,15 +1388,15 @@ habluetooth==7.1.2 \
     --hash=sha256:f325e07fdada45df1022114504ee130194574348a9471a65b65bdc6914228650 \
     --hash=sha256:fdaf26c6f184716eccdf35749bfd11116e54bb8fa2b99f1f1fd45a9c1b90593b \
     --hash=sha256:fe7bb1192a5824b04939e4ad9b445622539266bde13ca09f4941e057cc094fc7
-hass-nabucasa==2.7.0 \
-    --hash=sha256:a07f0dba540e53204363c1ad762967c715ca7bcebc175fa2a50a4d8721c7ce43 \
-    --hash=sha256:fb741a2b6447250e5fc6ff07c09184e3afaf8b1d0028833e58b6a652b26965e3
+hass-nabucasa==2.8.1 \
+    --hash=sha256:28faff85be9c59ae17e9c876af75b2669fdc9bb73d5c561f38c904689dc3325e \
+    --hash=sha256:6006a60dd53f2850820b27cfaa92dae8e9a8ae06b79044721b1f0c6359c84abf
 home-assistant-bluetooth==2.0.0 \
     --hash=sha256:3febd16b194812b156024d9bc8ce8ec7622cdd8d159047cac504cc77ca034ea1 \
     --hash=sha256:8d7c2ac48c303adacad73cb6cdfe7710f2fccd2a367d4c3106acf301b0d22b91
-homeassistant==2026.9.3 \
-    --hash=sha256:27e1b77bd8c9c5d9a7f5ac38a60f46e6a0f941354a509915a262f0d4bcfff388 \
-    --hash=sha256:2a7a0973115f995ea4ef997f2886ad397409e97cab4b4ddcafe07eeaa12f231e
+homeassistant==2026.10.4 \
+    --hash=sha256:71843060980a763187d856a8ff170640f1e287a7b741334cd838c81404f1f452 \
+    --hash=sha256:8410fecb434ab94b3f7724cd80584050f0ceeb856c16ee70202c24037d62238a
 homeassistant-stubs==2026.9.3 \
     --hash=sha256:829563ada8b7f680a669b2cd9427c37af9d9d9acb9fada12741bb9edf9992576 \
     --hash=sha256:85e2446adbf15c102eb41bd5bbec9e1ca34f2febbd80be5f4fb3bcf82555fbdf
@@ -1413,144 +1424,144 @@ jmespath==1.1.0 \
 josepy==2.2.0 \
     --hash=sha256:63e9dd116d4078778c25ca88f880cc5d95f1cab0099bebe3a34c2e299f65d10b \
     --hash=sha256:74c033151337c854f83efe5305a291686cef723b4b970c43cfe7270cf4a677a9
-librt==0.15.0 \
-    --hash=sha256:04d5387b908676c0b8d5d2f5fb58373b4ea382d81f7a6f0fab8ea2a462bb4738 \
-    --hash=sha256:077471b3182db4e17c36ae91555f36a4d2c00080b267f749bcad34a478a9a302 \
-    --hash=sha256:0a15cb554761247d84a3ec0cbdf4078d70725384f0e4662c0fa3b26266eb60ad \
-    --hash=sha256:0da0d94cb802f32a0524653e7201f2cef72d5f700a5407678f5290483d4fcd08 \
-    --hash=sha256:0e2d0c0acf5b0ada7d045912b7cf787c21315c95b38b1fa939ef72d45d366b3d \
-    --hash=sha256:0f0ee3644d951f31055ad07d77d92520e84505dd7a432cc4cd501dd70ee06785 \
-    --hash=sha256:1172c6ad2a88b646e7fe3b480e3fac4ab4418b3443fd8a4061fdd531e0622fc7 \
-    --hash=sha256:1256589e0b0adb31751d685a68bce29d73407ddf4ef05d4188f49d5dcf9566d9 \
-    --hash=sha256:1a1a8cd430c7dd0c083f455cb1b328d7fc682b05c31b940906f7845bdff80881 \
-    --hash=sha256:1cd3b721f24c206398b9e26da3c3a9c011e6e89d06f318ba8ebefc30f1003890 \
-    --hash=sha256:1e47b8ba865d7ede071a91a7163073bbaeb72541f1ef8a07d512c45c7b5007f2 \
-    --hash=sha256:1f4ef2e71db33df4309167ed7f1520c4fae5e611226e159fa9cf33f93e6ddb3d \
-    --hash=sha256:2067ff438048cead9d223ca5675bae2a25e520a7c3e6c1498bf9c6892d22caab \
-    --hash=sha256:22d6263b9d39d7bbb286fa791945646e3218f1be2d693e36fb630f1d0e59cd13 \
-    --hash=sha256:234d8d394721fa0d786af15ebf1f3fb7f3ed82fd1cd0cde45c2f247b5d4281d2 \
-    --hash=sha256:256237037a3ab001ae8d9803b2d43562a4c3aa38739843694349e4d5ebb0fd56 \
-    --hash=sha256:291bf73caf78b9e88d6fae9bfd693207ff7d832e2fdbe2cf8e746bc13f5f892b \
-    --hash=sha256:29c4cab9df457b19672c39be7f384ebb2bc925c4e2684b8780c222b43eb36389 \
-    --hash=sha256:2cfd1a81a648806e6a7717be4cc4d1bb392fa229752bf8444ba365e381e984d6 \
-    --hash=sha256:2fde98cf1fc4bac144ce23c2c4c017b924ba714509ea9334977b0b27050c837d \
-    --hash=sha256:32896a0af72508ea979e0acb4e4c04cbeeae04938167950d535c83c45597167d \
-    --hash=sha256:355e3a4c725225a14262004fc1872a552b9d3634b4f791a0dfc80804aafbfd55 \
-    --hash=sha256:3722a099730704c9a3d70c879fc0f51daec25fe5f1555672d97bc595abeafb95 \
-    --hash=sha256:38c0c7d4b6fc06c3324b3f9162c8391bfc4fd9dde53afe1033ce7edb48d5a714 \
-    --hash=sha256:39ffd14646190c454f0d86e0d256b33f00a87a26ab410e619773b841d0e41416 \
-    --hash=sha256:3de789c82752730f94782a5ee518baf9c05edf85733aeaf73bb6e518755cdf54 \
-    --hash=sha256:3e79f05e4a08b4d880342673312bbc895b56df7765605796f15902eb5367d3ae \
-    --hash=sha256:3ff5893a2c23d886aa9ce786de5ac6ddc74aeeaf90743682b74d920e117d2e28 \
-    --hash=sha256:411ca4d1b905b860ceba7570dd6717a71dedaddcc4b0f77ece710aa41ee11f8d \
-    --hash=sha256:4388184646efe2054911c5b00a1077d6d1ee86a95b7e8ba96dc7850a809f3f40 \
-    --hash=sha256:4a6369168d371207339b1e50d4532b06a7121586141f82599505a3f315751d47 \
-    --hash=sha256:4bbcc257e3babea20a91715c361b24554ec4e8f51aa578568afc230799fe1a19 \
-    --hash=sha256:4e66cbe84437497d951b799d3e1551291b6fb3d643820a7014b3655d57a59162 \
-    --hash=sha256:4e6ee93fc3cf848dcbf0cce2eca73d8e7dcd0cc2b6df3a529d57750b30a4c55c \
-    --hash=sha256:4eafbaff06b9563f8b1c850621ce51605de05208e09d4d71ce490bc972b7b9e8 \
-    --hash=sha256:52e8db01f603f5da0ca30987479acff98769382efc8e142fa3962395dcf3ffdb \
-    --hash=sha256:5500eeae393a184d14e1f35645962c27129d20c81afa4069e6ef826ebc2b3aaa \
-    --hash=sha256:55456ea87d8df21808446d03817be2f65e20391c1c615d9187440dff28cd08dc \
-    --hash=sha256:5563302a8359bc2295bb7084d1a8ed1519df96afb30eb2aa4e0bff7b54228988 \
-    --hash=sha256:567b1c430f8bd560e689421468278ac5941bab4a05303b5d95b6ae10db03f451 \
-    --hash=sha256:57f5eeb6ad4c180de583b1038e61fe5fbd9796bb69a8a1c1a0c7ddbec4c8c60f \
-    --hash=sha256:59fe030d8ae4a57e3fb7756bf35a858de74e04066fc8555c53d0af979132af81 \
-    --hash=sha256:5a6526a2a956bbb1e4ae3568c82e650fc99119c66bb011ea60715744955a2b4d \
-    --hash=sha256:5a86a5a08c2235316bdb359d5dbb6ce0abfca7fac06363103e2c5af571d92f95 \
-    --hash=sha256:5d2a91724463bfed4f573cd7a9fdc856d2e230d0c0e5a61416a93481dccd8605 \
-    --hash=sha256:64b0c8c35aa4c4ed79896359f3e0b285cbe4e610042106500da4811c322cc108 \
-    --hash=sha256:68242379c9b65a582b6e97318a1e9fbd6d445e58954f2d437991c4804ab11578 \
-    --hash=sha256:6912fa5e635d74529ac7cdb1bdf6ca3af4453da8d1edbe0110ee1cb4ad407ebf \
-    --hash=sha256:6c013cd3a1721e69e14380ada97eaa4b7b0cdf1c6b96fa765d4ea47c875088db \
-    --hash=sha256:6c0eb900c0e91f4aebe680845242e614f1864edfd44106380d0752ac29522bf8 \
-    --hash=sha256:6c6624fe268625869485553dd7cc1daf30d22558215bb2a4ff16f67a9801a31a \
-    --hash=sha256:6d15a29033c57490cfe2069097c6fc4049e4e65ffbb749be7dc453b7c4c68965 \
-    --hash=sha256:6d28a05796b99f749bf8794f17ba9ba1612d0076b802e9cfc62c554634e9ce3b \
-    --hash=sha256:6d5225ef8801e4ea5e482fa9b5dfb891dd9ef6f6d870f1f25d449ca2c70ac218 \
-    --hash=sha256:6da110e5f314c19ab8478464d02ae18808ae73d522c15260fa4918acdcd64da9 \
-    --hash=sha256:6ecfc32dfb46fb7b565bcd6abf9412acf978775a998273d22888a6d7953730dd \
-    --hash=sha256:713bd7df21170b982e729e46870f31d6b437bd1a9b4648cffb529bd3c2ec5c4b \
-    --hash=sha256:71599e011ac880e8e45d46047d714871894c7d4ab6f25626f8d4f89da21f368d \
-    --hash=sha256:7220697efaa6e5348fc3d18ee7f8563d4bfecd9872b37ffb915bfc1d08840622 \
-    --hash=sha256:73b30cfa976659b3917c8f6153bdb0591c6a9ec6583599fd24a689b690622022 \
-    --hash=sha256:779a6e7c894737e5983e7790a9c78c4000c30e23c9aada08081bdbea53b0fa60 \
-    --hash=sha256:80811e1c42386ea95c6fb30571d3250ad43d7863f883f787f70517f441150e59 \
-    --hash=sha256:814ff83a25b5fce8b9c80c4dd803153fb5c5599fc74db9e022466938368957ef \
-    --hash=sha256:81a398f45b45a59200e13cd5ad1ae1d3f44334de98b148331afe2cdfee701c52 \
-    --hash=sha256:823b92cf3c18ecd08afc70c42473888b41b6e8ef5046f3b82c05c154a2fa3d22 \
-    --hash=sha256:82909c8f7eb9952656b65d3147afde4cf8e6d5a991eebc86418b5e65843b0ab8 \
-    --hash=sha256:83380ffde38062a2e9bb55d83e74474f6614665528b98a6928720fc006dfffbb \
-    --hash=sha256:8443e38dcfcfdbcf5add5118c623efd788d65ac2e25756d6251a54a06a4d0aca \
-    --hash=sha256:84d244b00604d17df3fc7736c327892d6bba66181254aa4087be807b6c342bdc \
-    --hash=sha256:856f743ae607f2c1380eccb566c0038a9fb3eabf0fc2be2704d76d9f73557239 \
-    --hash=sha256:85ea21ec6730194d67156b0e0b5430ccb1d61f8b8b907e39b37f9812b74a13f0 \
-    --hash=sha256:86a21a7bd3fe3a419512ef424cc1c020f6771d0b29cfddff36d1635a855e63f0 \
-    --hash=sha256:88c2a17815c266e6d8180204ff62cb739ab869ada4a746d4c505331526ac58f1 \
-    --hash=sha256:89cc46cfd15022e35084355478c9ac809d90b1152222706ac9a7655ec21df6fa \
-    --hash=sha256:8ae493ed5f659a7761c43d42f183db514536073ded9bcf671d2d1df47e29a07e \
-    --hash=sha256:8b2fdd7ead3c995c37940a790690660d0ca006c302db26cc51933f6766866fc3 \
-    --hash=sha256:8b62076030baa2d8b1501a46bf0e19c27a489aa90671c55665bff7887f7660b0 \
-    --hash=sha256:8e11699ed745931c395acd3621b07062e0f840efa6935aad87a64ed0995f0915 \
-    --hash=sha256:92bfed8deec93df30286b9fe9e3b1dd17329cc076a192b4ee5ec223841d54953 \
-    --hash=sha256:96bb17dbe8bab3c0954fbebfc69ed395599de75b6bbc35e3270a878e15d4dd65 \
-    --hash=sha256:97335f59082f9fe2ce6c2a9cc6433a0114bbb6cd4d5c09dd76c95c68b9f9a8b0 \
-    --hash=sha256:a417149c0cba4d50b61e992e5a15e69eaf96746609b461cc4ed168aeef6b79dd \
-    --hash=sha256:a5207ec414d1c4a2a7231b2086970dc036f94293cdf338190984958a013a42f1 \
-    --hash=sha256:a54cf9e0ef47b96af580849db5471142200568ce1e02cbf416addab551369570 \
-    --hash=sha256:a56a1d4f859a82ca5b99fc4b82c9b027b15e3c455c5cd99e7d0719f27bb20b6c \
-    --hash=sha256:a5fa8f1f916988d0bf1afea005bda37f56ac41a18016e813ccf0097a8d460ca4 \
-    --hash=sha256:a6cd22c9da0d866558e46a041f1cc0c2bbb26b61b137b2347fa834c332e1d101 \
-    --hash=sha256:aa1f1995789dca3698bc550aaceb09a51bd5df0a057ff84ff15296cd1975b801 \
-    --hash=sha256:b0411b4066db926b80258c60dcb0e6db4c9cee312eab45b7e8866b17ddf9ada1 \
-    --hash=sha256:b230acc1c3bfe2d6f2627ba2b95dc92e58aa494600e9722d0e6ccbc931e59702 \
-    --hash=sha256:b30e600e8f337b9bd7f39b86d9fdfedc73cc46e3d0f745931a23a234220bb7e2 \
-    --hash=sha256:b845b8d48088fad0cadc84be4b8fda63203be7e9237b71015b3925443c1f35ab \
-    --hash=sha256:b87d67e33afaf265262f2a66db578284b88ee2e6fcd224579cb5c15518677ad8 \
-    --hash=sha256:bac89069bc496ebdf4f79ebb57bbd10d0b214c8454225deb672d91002bd17e18 \
-    --hash=sha256:bc25fb356d0c7810bb49ff3df908ad1fda6995d660ab099ded69244ed7ab6053 \
-    --hash=sha256:bccbd8e5b0bffb7106cf18eb1baa3d7194b1cebb3b4b1cdbd4bdb19382a6ee6c \
-    --hash=sha256:c16d15ee371643ab48dc8248a3e680ebbeca573a13af2c3dd0c985b142d77162 \
-    --hash=sha256:c434e072557ade9cbc642d052c89d031efe47d5c9614523619d0d74a02378e81 \
-    --hash=sha256:c47318cd3a61401452de11282242937e3e057c4fd3dbaf601e269d0928a06c0a \
-    --hash=sha256:c70bc1b602cf59917e8f0c7a2cbc8bcc6fbc14d5486136b00707a79619121d63 \
-    --hash=sha256:c7eec6a42018bc1d45763b1c162d3d2bf7c3b9a1b0ed30d3e91dcba390efefcc \
-    --hash=sha256:c802434092b769b1d613ed2e13fac15fbfce1934a74bd10283b03c0fae231cd1 \
-    --hash=sha256:cc30523e3f1a23fb7511cc659834a0d01a1042bb9de359bc1c131cc4ec6c9656 \
-    --hash=sha256:d00d20d1818e82a07a0ee0aa89a98b17ed7916b92441090b683719cb20a59b6d \
-    --hash=sha256:d2813ba2503764f0450680c533d13df7cff9b49df1411062eded5f67db4195b9 \
-    --hash=sha256:d2c05c729b589e734c09578bf5964be48a911765484840d017bbc84f49d4c4ad \
-    --hash=sha256:d4c7bacb70930f3d0a56f4ecf1be474a1f0d941b01dd73b756f3c256d42cb879 \
-    --hash=sha256:d5f51401d102c885b9ca509e62c79b1dbff286e1b9b047fde6f763780789356d \
-    --hash=sha256:d8363d7accb0286ac3a0e633f396e93800dafb8150494505daf9515bbda591f3 \
-    --hash=sha256:d8bc24219b24c0af375718942ab75e3544b2763085f40f965be4326734ae8328 \
-    --hash=sha256:d8edcf6f550e918dca779c069b9e156385c60b406f99fc7641f32c52f7193659 \
-    --hash=sha256:da7a94d6a3411f579d72aa3e3bc5fbca7ed4549f3dbd7e5de3aa567333374285 \
-    --hash=sha256:db13ca398005abcbe538deda87b686d9bd08b7001cf40c4c06b444960ae10a26 \
-    --hash=sha256:dbab647e88d90b3167b91efe7091e248653688ed4337e4f90907a722c7361bb9 \
-    --hash=sha256:dbd605739f228912dc49027cb764456b9757750bdc2b6b7773164db7096c6fd1 \
-    --hash=sha256:e0b5deec9a8664eb722c797241970fd4aa1894d25fda36a1ddac0f7407606bd6 \
-    --hash=sha256:e0d00c708fb2f5822b152429b1ac80a58dbbbc3f6c232c4d13a3f7fcf2ea5b4c \
-    --hash=sha256:e1a49adf16a7c9d9646816c2946135527197b6fcf4347c7b8b761cf1bfbf4489 \
-    --hash=sha256:e3b461183c5fa7681b48560f91515f53a953122fb30c71e07abc67d7ddf58c38 \
-    --hash=sha256:e4c911f15a1652ca94ae9f1abd92e74cbb1b3597d2d92fdd556202f94e8cd455 \
-    --hash=sha256:e56b6a368529bed262da40ce13f8fef590db0479819cca84f16a1f01ac356d0b \
-    --hash=sha256:e87bc679f86a99aa3b26e3c78eeb821a247c9a28eae48eaafcc32c3bf4c3bb9e \
-    --hash=sha256:e8c9a650a188e38bac005048cbe6342e81407782944d01934540ab75e417df21 \
-    --hash=sha256:eab9208b00ca55bf75983ec99f7bf13acc746a36102e98953addaad7f7ea1e1b \
-    --hash=sha256:ec3ba415afaf951f6951b1dd16d3c8e4f540065fc382d7e70b823a79567ca374 \
-    --hash=sha256:ec4b19788f835711a2072f9dbe6b03b3bf32ed1f0fb30cf399bdd59d9f0c33fa \
-    --hash=sha256:f395a4a9a03ac062dbe9a9f82e0c720502e590a38feee6a757bc82e9c63afbd8 \
-    --hash=sha256:f42b74a53e5f26a0ba0007411a7455b66c67ce4022a39cc1f56fc4efd65bcbab \
-    --hash=sha256:f54598964d357b1c5ab77cf5d92f21e598fe0e23cdbe9618480807f81b4eba15 \
-    --hash=sha256:f56b397858a23dacf35ede366ed2212fdc03a6a57a1ad36468ad6e9dc5fac091 \
-    --hash=sha256:f5de7feedc56337a088eb15cd9fafa9938367362221d8cc62c642b7f94821993 \
-    --hash=sha256:f75720477ee05d509a310e856cacc8d909adc182f7b91193c207bcc26d7ee6db \
-    --hash=sha256:f779070399f991400fc451719e0ea388eb7de313388bada2c127a35de05f798a \
-    --hash=sha256:f9ca190fe9edc0eb08eec558a509a16d28d91c35667b8f043cba40ed5e77a959 \
-    --hash=sha256:fa60887537e1d0cd2d9982269d33a709bf54b195cd2b9364fc0a758022af5bd9 \
-    --hash=sha256:fc1ed11c4ad0b91af24def2050f2840ea4567828e3dd058fbe608d982f6e5465 \
-    --hash=sha256:febb1ce6cac545a54e6b769982824e955a700fdd9fbf3a08a3d82c990968b57d
+librt==0.16.0 \
+    --hash=sha256:001bfd59a7d45b17e3e75f2a8c6405280b35e7b84471792778e718c4f368950e \
+    --hash=sha256:0058f9d68721094105917254c72ac0569117bb7b13b9769cf45d26d89f9d21cd \
+    --hash=sha256:02118f56a9c36ddd07dfd9b919d9ecc117ba20a90987d56aa4c429fa34509188 \
+    --hash=sha256:0253721561787b8df8443eb347b7a6461015354e5bdd37ee38a41fef220d2bb0 \
+    --hash=sha256:02d89c813d5ff74b17df72d3a34819d132cd168e56b81bf755b809bd9e46b8c4 \
+    --hash=sha256:0314058469f4d2fd279ce7c62ac274ac82c3918ef7db62ef0697c4c359370155 \
+    --hash=sha256:0dbe4096a7ecc00fa835d24510ad8545a4efef738dac96e0e63516783ccde905 \
+    --hash=sha256:0ead24d2562a49473dddd9efef8581f020007eb0054389c3ee3ffad38b1ca4c9 \
+    --hash=sha256:13b4e8aba90b0b1c82474e9844aa9ffe7ad3faa484350e1da64cb8188d903134 \
+    --hash=sha256:14ed6ebe3e4f85f326d7920011ad30ff49ed9334e62cf88caef9ba973d9e3a92 \
+    --hash=sha256:17bac7f7a16b328fff77e440287693eb017abde913595b5827ebccbc21ecd8a6 \
+    --hash=sha256:1b384b90ab79a7bc30b566895809a636e0666f21f3cf12b54823d025b7e83839 \
+    --hash=sha256:1bc17e54e5305f8d40b7ca203671ff5a9e59c1d0f8ea0f625dcca53a3984de11 \
+    --hash=sha256:1d28ae980ae2218f9c5b95d191e947296f918c9bf0b400d467a9430275bbe678 \
+    --hash=sha256:1e511762a074005bb0aa569166779834e75e438370226930d0ce1866d4b6a33b \
+    --hash=sha256:20fe0bf9053885e21c62b3e091fb5e73e1c54d1daf2e70eb388d70763bcd4220 \
+    --hash=sha256:242e00b3d4fa37c3d3c1ca5f5c9adb7d909ddb1eac9c41f2787320d00caa0af2 \
+    --hash=sha256:25a58a19ea8d83b68209f04912df765e9260635ef77646542ed4b4abe6bc7940 \
+    --hash=sha256:273d00be33792a15189331df10f1f1331621b043881e66c6c4377f7f776e1291 \
+    --hash=sha256:28e038895b998d7a0c7798922ce8a1dc157675df5cf1c9ef0aca809ed804b7a1 \
+    --hash=sha256:2bec3818c7da7c96ceae0ef5915a3d16c52dd08f3ea913bf1fe8568c447c7978 \
+    --hash=sha256:2c4aa329c17bd1aaea4f6e89335d8ccd494b3a5830b6654462273e50e11023f0 \
+    --hash=sha256:300c3ffdc459f4a779a8411ecb188e3ac0b1ff3a3a7b099642555dedae06c69b \
+    --hash=sha256:30b7beaf3f4487b7d8adef1f158b49067cb4d5a19fa7a3bf31a4e7a820e435c5 \
+    --hash=sha256:314e703f0c19320dc8094e7a784b9cf29e1b67402515abf580069a6363c0b4f1 \
+    --hash=sha256:33f41443a1f4e1f099331b3d8120e409fbff84b9760bc1cc9ea496f37ddaa5cc \
+    --hash=sha256:349c0bcb87ebd07481b6ff781e25cdc699723dbe2212e57dabb27f7a13b7b87d \
+    --hash=sha256:36e53948e99bbe3ffea257124cfcae1cfb01831555c9a9c903c9f9a72db7fd07 \
+    --hash=sha256:375bfe6b572a8f6cfc398709356046173bf27e64c4c5edaf5f7062f051fb4bf9 \
+    --hash=sha256:378dfaffb38e59c24a87cde5713cd865d51ff7383fa12947f3907f306ea1ca55 \
+    --hash=sha256:3931f7a3db322e7f44e02a280e3949326ce9579ad388ee8d691dc7c76da9fb70 \
+    --hash=sha256:39ca4f2f2fe05de8e63493da592d84311adabe5bef52b193851981da9816b302 \
+    --hash=sha256:39ec1d5a14e37baf1450a6cabf03fe552340808bf1ad9d71824ab90117716459 \
+    --hash=sha256:3ddeb3c9dedb461bb457c6c7d9aa7fbf35329da313d1a7543d00c8d0f3473c96 \
+    --hash=sha256:3e0c39bdc85370422e8b637be76eb1fd07d30967551b03e62267dd156f553152 \
+    --hash=sha256:3e483a8d69ede8067db70c0e83007423b6925de6fd53afed01d66160f2e9398c \
+    --hash=sha256:3f0b8114c44b2ac06ff5dacd08e07e8e807ff4f46083f2a1602685122559be41 \
+    --hash=sha256:3ff4b2367926b69c6215635902cccb04048e73094e9862900d27cb2c6bbff143 \
+    --hash=sha256:4323193ac0cd025f85af531df8ba91bf24d1973b401697347a6282e8fd3fcf5e \
+    --hash=sha256:468df902df016a06eb0e40b0747dc8d14e47d7a38b18b63b1fb167d85cb94d63 \
+    --hash=sha256:473eebc7866bb0a0c8849a292b5e7157c1aba5d14d0f0f610c52158d6d964262 \
+    --hash=sha256:47ada6ea32636492c61aa8ad27ae3b9404bfe7a97e3ba946d1984236cc741da0 \
+    --hash=sha256:4b6183e2e2e0ee00aac2ec07c7f7d151c97e85666b304f574b71cff0f9fccc4e \
+    --hash=sha256:4e29522c62e28595ff7e324c6834ade51127707f0e255b18d1c1cf03d39c1048 \
+    --hash=sha256:4eb1313a19847089ee81e88742abedf285c60538816640b99742d8534b81d26a \
+    --hash=sha256:52327da75a94012e7f932f913d20d3876bed3c102be00e6c3e8600ff7bdd58a7 \
+    --hash=sha256:54d11f726aae9df5a6ffbbf0a03a52449bbac84a53ef03669cb41cdfd4ae41bf \
+    --hash=sha256:5696d7f52e7b37217cb3a8f92c744fe835942602fdd4c1a8bc4741d3bfdce15e \
+    --hash=sha256:5750a105b42a416f930edc59054927a406effb2550cd5bab92ad7a5842ed5d05 \
+    --hash=sha256:5810ba811297fdf37a1531a57667cb8ace0842013ca8606bf9eb7c24cf4be154 \
+    --hash=sha256:5981c011b306781ce561e18e14230a14524a3d8109b97553666c942c18f31a96 \
+    --hash=sha256:5a269c46ae327d8e6f8c1f85f7516cb52c0fa48127565a1105a4f4a05ff2a0b4 \
+    --hash=sha256:5b976054553670829985ed767feb78fb6bcede0175327c4844dd5c281c1be659 \
+    --hash=sha256:5bcc2c4726ced915b00de0c9856a4eeabfb3fddb93e10e0b8f735b7709358b6d \
+    --hash=sha256:5cd5b092441053364af968ea12084692cb9d4a22f3ce9524e377880bf028761e \
+    --hash=sha256:5f49cff01bd608ef7d97104cb035c75455e79c2d70bf4a506cf773338ac1860d \
+    --hash=sha256:6072e92dd876ff6ceeb6cf371e35e51f479349837391341f479b08df4564242b \
+    --hash=sha256:64c79520414a3fdfc6aabd7593e6169afa14d5f8d9908d4b498db068868b08dd \
+    --hash=sha256:67e718c7a43f8db325abbbf1404e2d535f12f8f7a1a82259568385cc5274b82a \
+    --hash=sha256:69ba927445cfaaffb4081003ef5224c55a5c2ab67ef956f416ef744916e44121 \
+    --hash=sha256:6a63610fa76524edfa605b5b259a603915c7a6e10e54f003e5503030506e81de \
+    --hash=sha256:6c5da27e8056439f927ea896735da60e616c477a8293feaa3233d4e7781a6726 \
+    --hash=sha256:6c8893eae2fd13c5488d94056f3e6e5cf3142bfb1c4acaf136cb33d760c5964b \
+    --hash=sha256:6d4a64283ee61824b5790de882bc68e2d9d7a5143537cb7a966f7354f71646d4 \
+    --hash=sha256:6fe436af2eaf630474f491af5d032cbe45f93fcff5c3b9fe4ab194a7255b20ff \
+    --hash=sha256:71b93b42784e25b975079573c642a8fedb049a7bb31d70a51721b1666b3b2ced \
+    --hash=sha256:7393c9a48dcce4817dbd4b0d8ff6237efe9b0a0609f5b0adaef315f8541726b5 \
+    --hash=sha256:77c7a2b4fe2c1369e0d5aa1cade26740a7b14be32fbc9a5535d617d20065c39d \
+    --hash=sha256:7a1d272724b581bb6bc769dfdafed6da2ecc9886ba2450311de55a4ac2e1e9cd \
+    --hash=sha256:7cc365f006891afb006b52d5ee5ee74c09306ffa20e2f8705a32a4450af2f3ba \
+    --hash=sha256:7e510b7770bee609617a3374a96548eb114cae048023e3f049ee449e7ff2db32 \
+    --hash=sha256:80039ba9b6a7d5f1a0175a4cca6bbefead87bd854c80abad1cb30afe47a830db \
+    --hash=sha256:83d4041a3d9b2fd053a8a4e1f22878b3e5833e2712956382d5c048d791454e91 \
+    --hash=sha256:845a511b60ca43b9880dcc84a9784c891d6a2098c829130b320846c69c9c0c68 \
+    --hash=sha256:877698bf6bca5721d8be345f2fe09778e40ecadea8b58c73075f2b1a53666bf2 \
+    --hash=sha256:8caf96a4ef8fb27d0ac0d1ad8337d26a240acd4a02fe4345d0a8f264753e8f99 \
+    --hash=sha256:8ceafb70f2a4f0826f11031942e59c0728fd98da112dc346d4352bde1e486866 \
+    --hash=sha256:8f36c58e33b304b525c6c9c5076399c6ebf1109e17b9051a05a407b091b9215b \
+    --hash=sha256:8ff5d26c529336be9bd7ae04483235d77778ee7d6444a95353102b542601ce81 \
+    --hash=sha256:909d8e3c1faee44cb762b1c519ff8613dcc5ceae5c99987a00917b5a31fd1d6a \
+    --hash=sha256:92caf82ebef5e12d21c72242b70d1e92536f1711cf2a727a4c276de4b4469087 \
+    --hash=sha256:931a0bb0fcac88f263e269e46eb30ba8e21402cd3c62ca40cb97034c0693fab1 \
+    --hash=sha256:943c6bbecbdf7fa575a4f2952fcfd848c88ef95507c3fca411e89d4ac3ff8143 \
+    --hash=sha256:94aed6a8308818b91677957d1bd03188869cd7aeb23c5dba7912a6c0402f7602 \
+    --hash=sha256:94be5cb7bca4df6201f4183e9e4fa2086c655283d20b38cd84500a69057575a7 \
+    --hash=sha256:953107e2f68d0f3512c48f898b0dbf0ce5cc52bba0f318d847c985dc555ee4cc \
+    --hash=sha256:96f576f2711f8519152ec76d0e599243555c1f07679fa73606ca8c8c868c0be6 \
+    --hash=sha256:a33e0dae1f8592146a4764d54ce842b278732d21a84e17c3bbe6b1bc158a2248 \
+    --hash=sha256:a4aaefb4ba6c07e1aeebb2795c8958148f1d6f9af3b555b53d23d766edb6d67a \
+    --hash=sha256:a8afb6557920860b7a3a596eb804cf37e09e7cf8a803db2478c202acc72d8c2e \
+    --hash=sha256:aa9357a1b4d4fc787bb718a59cb1112c28c8a976d6bfa268b71cc0a4ab8f3a94 \
+    --hash=sha256:ac38d6d8d66bf3d744148dbbc0b8e193e195a51e364ed55e224631f5721891fc \
+    --hash=sha256:ad37d5b9abd49c9a655dcda7ea52a8a752884062ef1ee71ae17c2f2a0f81fe6a \
+    --hash=sha256:aea7b1f2b125dad5de85f049136651bff256c883c65e6b9209b2da0a1ac3cdef \
+    --hash=sha256:afced3dfc17cd805ecf7a3d77996a71cf5f2c75aa66eb0c21a9930f4fc992f86 \
+    --hash=sha256:b0e3e721c75d2e79a76d4422c79d7ba705fe1bbafec907037fe7a657a480a0e3 \
+    --hash=sha256:b6d085d70bce51d43c5c7c36d63490770180d8779e71c49305c87b4213918de7 \
+    --hash=sha256:b95d5d92ab83d39e760a52091bb1baba664f3a2351e39b1e16801e5747c2f0e9 \
+    --hash=sha256:b9d6d4b14e92d876f8026b54c20c445f36425214c1081dc76f74e40db386b82b \
+    --hash=sha256:bc02954b1295de798bbdb0b4e2d8a28c2117de8b5c73dcbeb27dc32572dfb971 \
+    --hash=sha256:bd3150023d3dc2bc70f3784e59ffa1140d56ddba3d8125b3d6f9f85221279bfc \
+    --hash=sha256:be56ba9c884143495b517f23fe794ae367d58cd89ea0fdd6d437e3c024a87f9f \
+    --hash=sha256:c17194318e4c0c0348b36f36c2ec7534436fe0a4c15582403162a4f08c80797a \
+    --hash=sha256:c3d1bb7841a816ace6449bb26d3f9560dbfa20e71c568d23f0f62bf1e68f50b1 \
+    --hash=sha256:c43bd6e642d8a248c114327f98dd25ac5a7cb5aa168ef02f0559b91874df16b8 \
+    --hash=sha256:c5db585d43449a5f54303d4b2774e45e1babd975cfe1630a3d708c0b80c3e560 \
+    --hash=sha256:c5e6144e68b577f157519f2ba88ca20e3ed61c29b00e5cdfa76cd2d45acf059a \
+    --hash=sha256:c6f1b27bf1632a7e016af9f145f82be95e1edd7721a646505c21059257cb5a04 \
+    --hash=sha256:c71d1b76210a36729fedfc5115069b50a3d8619054745f8758fe5d6f19e86671 \
+    --hash=sha256:c72c5295a84bd249526da9bdca38f2e176d15c31c13bb0063c5053f4ca023421 \
+    --hash=sha256:ca8052401c55d7511dda6760719fda7618067e83535d7d0010096d216c34b667 \
+    --hash=sha256:d1aabe3925cbb4a08d15b7b20ba4011b53019da0c4173a25155139b7b1baed65 \
+    --hash=sha256:d3c94211ee0c4f8d649ec06b7c115c0ec4eadb873a0e3154ca15cef3f814b071 \
+    --hash=sha256:d46ca272b251d033dd4527b0dec5f261a28a52bd5fa0f99c117b0a1f8588cc2d \
+    --hash=sha256:d608f0bf3b8cbddd0067fe02cb8cab7d13e8eb9386b23a1843d4363044fd9e22 \
+    --hash=sha256:d6a365f2ab45a984d0e00eee0dd17f599ceab8cadab6ea07b6111c8132fc0e42 \
+    --hash=sha256:d92db7a0f6aee44f1baee94750457e8d2d1c6ccea41842de6268d34e8dc7eddd \
+    --hash=sha256:df183721229ae51eef90108c115b43e98cb169b6155d34480338e5fc6616df00 \
+    --hash=sha256:e05108e0849966f53a8d2d3112a7af881d0efaa479bc735bba91108f9f2350a7 \
+    --hash=sha256:e1967e36ac4cae0c7e9615ad32e1a513cdacff79f9e8afb28bedc91caf48b4f3 \
+    --hash=sha256:e42f8e098b9c5396fefa05fb1cc7e33b0e08fc51da106b5de4a45fd22aac6743 \
+    --hash=sha256:e56aaf8c167548dc8e5d6f3bd0f48dcdd299a23c73be3f744aab79d99e9c7f5d \
+    --hash=sha256:e9ce0bc440e7fd09b5f51f372f0f6640658f854b8fb05260f819cc669c93c42d \
+    --hash=sha256:ebefd60b42e2a82b32d136bb5f7c94eadfcd29f772b547df6f3291d1ed855a1c \
+    --hash=sha256:ef46c1a29ffb8c72e882e22618ec618778eacd0578fb22c6e7cf9c11d15f357b \
+    --hash=sha256:efc49c462d4516b8a58b00b490078fa64689fd1fe66970cc190131d7afb8027e \
+    --hash=sha256:f01f3805f2dae4781c0c34b440e31740d082950bdaf89a6f601ad589a28af57a \
+    --hash=sha256:f06c689cb14afd9b612727553a5ec5a40febf113ca41c4413a2b0b334285884b \
+    --hash=sha256:f1e8591bd8a5a628cd7f07954c6a1592359a878bf032957a8e9057a41d644311 \
+    --hash=sha256:f4462528b6000afe8f16907b5c7c2553abf1df005ba5140e6eb394541c3624c3 \
+    --hash=sha256:f7be7cf555bc30ec12622e9447299cc4a9b8ff307548b634794353db0c2065dc \
+    --hash=sha256:f81b5b19ce748ef68d4746656b7929762eb2fe99269b266e4be07e2ee4de7144 \
+    --hash=sha256:f9807485a908f00355820f18e91e045ffdcdc5adb68aaec40a1e2b88c5f7bba1 \
+    --hash=sha256:fbe4fb8c5445f7496d7f7f6bb0807875d09d47e6771ffa175fb2df2895fb86ba \
+    --hash=sha256:fe4372c52d4849096c6cc1cda2817d293ec51440c890474ed59ef38d46556f18 \
+    --hash=sha256:fe52bf4641069e7978a14253b036cb9002def1926317e710f2e249f8a8c47742 \
+    --hash=sha256:ff7baa55f8e7c69851419e50a666015d02a74198716fd45c0125a2112e0a389f
 lru-dict==1.4.1 \
     --hash=sha256:000ba9a2ab4dd1ad2d91764a6d5cce75a59de51534cdda478d1ddaa3cd8d5c48 \
     --hash=sha256:0158db85dfb2cd2fd2ddaa47709bdb073f814e0a8a149051b70b07e59ac83231 \
@@ -1648,475 +1659,502 @@ lru-dict==1.4.1 \
     --hash=sha256:ff3af42922205620fdc920dcdf580c4c16b32c84a537a03b04b523e5c641a8a9 \
     --hash=sha256:ffad2758ce21d8fd6f0ae2628b31330732db8429a4b5994d2e107bed0ee11e68 \
     --hash=sha256:ffbb4eedc45eb629ca073795c53bf8de935a39cb58014b6af3487098d2f19098
-markupsafe==3.0.3 \
-    --hash=sha256:0303439a41979d9e74d18ff5e2dd8c43ed6c6001fd40e5bf2e43f7bd9bbc523f \
-    --hash=sha256:068f375c472b3e7acbe2d5318dea141359e6900156b5b2ba06a30b169086b91a \
-    --hash=sha256:0bf2a864d67e76e5c9a34dc26ec616a66b9888e25e7b9460e1c76d3293bd9dbf \
-    --hash=sha256:0db14f5dafddbb6d9208827849fad01f1a2609380add406671a26386cdf15a19 \
-    --hash=sha256:0eb9ff8191e8498cca014656ae6b8d61f39da5f95b488805da4bb029cccbfbaf \
-    --hash=sha256:0f4b68347f8c5eab4a13419215bdfd7f8c9b19f2b25520968adfad23eb0ce60c \
-    --hash=sha256:1085e7fbddd3be5f89cc898938f42c0b3c711fdcb37d75221de2666af647c175 \
-    --hash=sha256:116bb52f642a37c115f517494ea5feb03889e04df47eeff5b130b1808ce7c219 \
-    --hash=sha256:12c63dfb4a98206f045aa9563db46507995f7ef6d83b2f68eda65c307c6829eb \
-    --hash=sha256:133a43e73a802c5562be9bbcd03d090aa5a1fe899db609c29e8c8d815c5f6de6 \
-    --hash=sha256:1353ef0c1b138e1907ae78e2f6c63ff67501122006b0f9abad68fda5f4ffc6ab \
-    --hash=sha256:15d939a21d546304880945ca1ecb8a039db6b4dc49b2c5a400387cdae6a62e26 \
-    --hash=sha256:177b5253b2834fe3678cb4a5f0059808258584c559193998be2601324fdeafb1 \
-    --hash=sha256:1872df69a4de6aead3491198eaf13810b565bdbeec3ae2dc8780f14458ec73ce \
-    --hash=sha256:1b4b79e8ebf6b55351f0d91fe80f893b4743f104bff22e90697db1590e47a218 \
-    --hash=sha256:1b52b4fb9df4eb9ae465f8d0c228a00624de2334f216f178a995ccdcf82c4634 \
-    --hash=sha256:1ba88449deb3de88bd40044603fafffb7bc2b055d626a330323a9ed736661695 \
-    --hash=sha256:1cc7ea17a6824959616c525620e387f6dd30fec8cb44f649e31712db02123dad \
-    --hash=sha256:218551f6df4868a8d527e3062d0fb968682fe92054e89978594c28e642c43a73 \
-    --hash=sha256:26a5784ded40c9e318cfc2bdb30fe164bdb8665ded9cd64d500a34fb42067b1c \
-    --hash=sha256:2713baf880df847f2bece4230d4d094280f4e67b1e813eec43b4c0e144a34ffe \
-    --hash=sha256:2a15a08b17dd94c53a1da0438822d70ebcd13f8c3a95abe3a9ef9f11a94830aa \
-    --hash=sha256:2f981d352f04553a7171b8e44369f2af4055f888dfb147d55e42d29e29e74559 \
-    --hash=sha256:32001d6a8fc98c8cb5c947787c5d08b0a50663d139f1305bac5885d98d9b40fa \
-    --hash=sha256:3524b778fe5cfb3452a09d31e7b5adefeea8c5be1d43c4f810ba09f2ceb29d37 \
-    --hash=sha256:3537e01efc9d4dccdf77221fb1cb3b8e1a38d5428920e0657ce299b20324d758 \
-    --hash=sha256:35add3b638a5d900e807944a078b51922212fb3dedb01633a8defc4b01a3c85f \
-    --hash=sha256:38664109c14ffc9e7437e86b4dceb442b0096dfe3541d7864d9cbe1da4cf36c8 \
-    --hash=sha256:3a7e8ae81ae39e62a41ec302f972ba6ae23a5c5396c8e60113e9066ef893da0d \
-    --hash=sha256:3b562dd9e9ea93f13d53989d23a7e775fdfd1066c33494ff43f5418bc8c58a5c \
-    --hash=sha256:457a69a9577064c05a97c41f4e65148652db078a3a509039e64d3467b9e7ef97 \
-    --hash=sha256:4bd4cd07944443f5a265608cc6aab442e4f74dff8088b0dfc8238647b8f6ae9a \
-    --hash=sha256:4e885a3d1efa2eadc93c894a21770e4bc67899e3543680313b09f139e149ab19 \
-    --hash=sha256:4faffd047e07c38848ce017e8725090413cd80cbc23d86e55c587bf979e579c9 \
-    --hash=sha256:509fa21c6deb7a7a273d629cf5ec029bc209d1a51178615ddf718f5918992ab9 \
-    --hash=sha256:5678211cb9333a6468fb8d8be0305520aa073f50d17f089b5b4b477ea6e67fdc \
-    --hash=sha256:591ae9f2a647529ca990bc681daebdd52c8791ff06c2bfa05b65163e28102ef2 \
-    --hash=sha256:5a7d5dc5140555cf21a6fefbdbf8723f06fcd2f63ef108f2854de715e4422cb4 \
-    --hash=sha256:69c0b73548bc525c8cb9a251cddf1931d1db4d2258e9599c28c07ef3580ef354 \
-    --hash=sha256:6b5420a1d9450023228968e7e6a9ce57f65d148ab56d2313fcd589eee96a7a50 \
-    --hash=sha256:722695808f4b6457b320fdc131280796bdceb04ab50fe1795cd540799ebe1698 \
-    --hash=sha256:729586769a26dbceff69f7a7dbbf59ab6572b99d94576a5592625d5b411576b9 \
-    --hash=sha256:77f0643abe7495da77fb436f50f8dab76dbc6e5fd25d39589a0f1fe6548bfa2b \
-    --hash=sha256:795e7751525cae078558e679d646ae45574b47ed6e7771863fcc079a6171a0fc \
-    --hash=sha256:7be7b61bb172e1ed687f1754f8e7484f1c8019780f6f6b0786e76bb01c2ae115 \
-    --hash=sha256:7c3fb7d25180895632e5d3148dbdc29ea38ccb7fd210aa27acbd1201a1902c6e \
-    --hash=sha256:7e68f88e5b8799aa49c85cd116c932a1ac15caaa3f5db09087854d218359e485 \
-    --hash=sha256:83891d0e9fb81a825d9a6d61e3f07550ca70a076484292a70fde82c4b807286f \
-    --hash=sha256:8485f406a96febb5140bfeca44a73e3ce5116b2501ac54fe953e488fb1d03b12 \
-    --hash=sha256:8709b08f4a89aa7586de0aadc8da56180242ee0ada3999749b183aa23df95025 \
-    --hash=sha256:8f71bc33915be5186016f675cd83a1e08523649b0e33efdb898db577ef5bb009 \
-    --hash=sha256:915c04ba3851909ce68ccc2b8e2cd691618c4dc4c4232fb7982bca3f41fd8c3d \
-    --hash=sha256:949b8d66bc381ee8b007cd945914c721d9aba8e27f71959d750a46f7c282b20b \
-    --hash=sha256:94c6f0bb423f739146aec64595853541634bde58b2135f27f61c1ffd1cd4d16a \
-    --hash=sha256:9a1abfdc021a164803f4d485104931fb8f8c1efd55bc6b748d2f5774e78b62c5 \
-    --hash=sha256:9b79b7a16f7fedff2495d684f2b59b0457c3b493778c9eed31111be64d58279f \
-    --hash=sha256:a320721ab5a1aba0a233739394eb907f8c8da5c98c9181d1161e77a0c8e36f2d \
-    --hash=sha256:a4afe79fb3de0b7097d81da19090f4df4f8d3a2b3adaa8764138aac2e44f3af1 \
-    --hash=sha256:ad2cf8aa28b8c020ab2fc8287b0f823d0a7d8630784c31e9ee5edea20f406287 \
-    --hash=sha256:b8512a91625c9b3da6f127803b166b629725e68af71f8184ae7e7d54686a56d6 \
-    --hash=sha256:bc51efed119bc9cfdf792cdeaa4d67e8f6fcccab66ed4bfdd6bde3e59bfcbb2f \
-    --hash=sha256:bdc919ead48f234740ad807933cdf545180bfbe9342c2bb451556db2ed958581 \
-    --hash=sha256:bdd37121970bfd8be76c5fb069c7751683bdf373db1ed6c010162b2a130248ed \
-    --hash=sha256:be8813b57049a7dc738189df53d69395eba14fb99345e0a5994914a3864c8a4b \
-    --hash=sha256:c0c0b3ade1c0b13b936d7970b1d37a57acde9199dc2aecc4c336773e1d86049c \
-    --hash=sha256:c47a551199eb8eb2121d4f0f15ae0f923d31350ab9280078d1e5f12b249e0026 \
-    --hash=sha256:c4ffb7ebf07cfe8931028e3e4c85f0357459a3f9f9490886198848f4fa002ec8 \
-    --hash=sha256:ccfcd093f13f0f0b7fdd0f198b90053bf7b2f02a3927a30e63f3ccc9df56b676 \
-    --hash=sha256:d2ee202e79d8ed691ceebae8e0486bd9a2cd4794cec4824e1c99b6f5009502f6 \
-    --hash=sha256:d53197da72cc091b024dd97249dfc7794d6a56530370992a5e1a08983ad9230e \
-    --hash=sha256:d6dd0be5b5b189d31db7cda48b91d7e0a9795f31430b7f271219ab30f1d3ac9d \
-    --hash=sha256:d88b440e37a16e651bda4c7c2b930eb586fd15ca7406cb39e211fcff3bf3017d \
-    --hash=sha256:de8a88e63464af587c950061a5e6a67d3632e36df62b986892331d4620a35c01 \
-    --hash=sha256:df2449253ef108a379b8b5d6b43f4b1a8e81a061d6537becd5582fba5f9196d7 \
-    --hash=sha256:e1c1493fb6e50ab01d20a22826e57520f1284df32f2d8601fdd90b6304601419 \
-    --hash=sha256:e1cf1972137e83c5d4c136c43ced9ac51d0e124706ee1c8aa8532c1287fa8795 \
-    --hash=sha256:e2103a929dfa2fcaf9bb4e7c091983a49c9ac3b19c9061b6d5427dd7d14d81a1 \
-    --hash=sha256:e56b7d45a839a697b5eb268c82a71bd8c7f6c94d6fd50c3d577fa39a9f1409f5 \
-    --hash=sha256:e8afc3f2ccfa24215f8cb28dcf43f0113ac3c37c2f0f0806d8c70e4228c5cf4d \
-    --hash=sha256:e8fc20152abba6b83724d7ff268c249fa196d8259ff481f3b1476383f8f24e42 \
-    --hash=sha256:eaa9599de571d72e2daf60164784109f19978b327a3910d3e9de8c97b5b70cfe \
-    --hash=sha256:ec15a59cf5af7be74194f7ab02d0f59a62bdcf1a537677ce67a2537c9b87fcda \
-    --hash=sha256:f190daf01f13c72eac4efd5c430a8de82489d9cff23c364c3ea822545032993e \
-    --hash=sha256:f34c41761022dd093b4b6896d4810782ffbabe30f2d443ff5f083e0cbbb8c737 \
-    --hash=sha256:f3e98bb3798ead92273dc0e5fd0f31ade220f59a266ffd8a4f6065e0a3ce0523 \
-    --hash=sha256:f42d0984e947b8adf7dd6dde396e720934d12c506ce84eea8476409563607591 \
-    --hash=sha256:f71a396b3bf33ecaa1626c255855702aca4d3d9fea5e051b41ac59a9c1c41edc \
-    --hash=sha256:f9e130248f4462aaa8e2552d547f36ddadbeaa573879158d721bbd33dfe4743a \
-    --hash=sha256:fed51ac40f757d41b7c48425901843666a6677e3e8eb0abcff09e4ba6e664f50
-mashumaro==3.22 \
-    --hash=sha256:17dc4d7294c33ef380a8b929dda0608577aa2141988c00a0c4932310108fe71d \
-    --hash=sha256:64538cc365204402a060ebde683a86505b5a4344acf6870d79021e9fbfe57360
-multidict==6.9.1 \
-    --hash=sha256:006c4478de0a1876f4834e14255776286f09b9846b505fe63f67f9d173a9487c \
-    --hash=sha256:024123f0ab402ab33828e24eb80fa8f25167d0d3783ba5f287e39ed741e6abf9 \
-    --hash=sha256:02f6d0c4b70f783305e73f9944d8efe6be1022550f0974ba0ae9d8893c0350fa \
-    --hash=sha256:02fe09dc197b8ae7e355371e51e5dce2f39060cd5a8badf94904527e23a3f188 \
-    --hash=sha256:03731f6fc036180700c9dc2308205a48e5ca6f3ff03087739ab746f294022201 \
-    --hash=sha256:03d47df72f084f757c1cb771188d5f4e3a805e4abc4d67e32509272343ae9382 \
-    --hash=sha256:03fac50ddfd8302175b77863a015eccfae76767cda5506eef86df559ba861e1f \
-    --hash=sha256:042fb0196047e786936a730bd302de83143950da45f2c16078da8f35e1cf7919 \
-    --hash=sha256:083735b7f395894e43adb278d5dae901448883a835ff8f1977e285fefdb10418 \
-    --hash=sha256:095d900c242e00fbe5f321ee072e7278b4153e78c5ce9c1efde167d62c1e4771 \
-    --hash=sha256:0a5769559e3312dd96731fbe15b4abb6033368ac1cad5a98dadd21946a4c7d6c \
-    --hash=sha256:0b2fb8c349d1103863750b5d8cb5ace766917f4b35f3d883c8f778853eaa9f76 \
-    --hash=sha256:0dd655518f136febd96c05131a76a863e32fc2a1d7acd4e3c959e3ceb77d8345 \
-    --hash=sha256:0f06e60fa190aa7abd0914c2a766736fdc8e9f34878c4346338534b73d1b20e2 \
-    --hash=sha256:0f2ce963299d42fa3f22a90adc0fdf174792ffef5ff4c7ffb68260548fb05580 \
-    --hash=sha256:0f3bd290711c6e9486173a6ee7cd4e7f00c3971c7908c1ec1b6e5437c5e4c6f9 \
-    --hash=sha256:10083a8a0f4e1b26b599889e90b9802504ce5d3f7722f925bbb7ca47dd22a7c1 \
-    --hash=sha256:13849a1d4f54c3809ae721e9e83ab28f5ea602f33660cb84eb6ef261eac706c1 \
-    --hash=sha256:14c56f73e78faa1f68bbb826197cd5871994e70e841b8590829c35912ece5c64 \
-    --hash=sha256:15db6a102cbaf1949cf028ecf080aac76d20bcd29ad4e092574db6c6b7af78a5 \
-    --hash=sha256:19e31815d41cefc365489e591d105d2baceb2f65aa75d29471fbdbda8651e006 \
-    --hash=sha256:1a53de2772cfb74559df2eb4456ec4eeb908435ec55a84b69370d9d745d62aa8 \
-    --hash=sha256:1a8adfcaf96f587ab138476eaddef95f29b8a2a8a9afbfea8d2fd62180995d02 \
-    --hash=sha256:1a938761c77e0e6edb0c93d02f4e988d44a69e5195e5a3b893e5553311347132 \
-    --hash=sha256:1c9f3c25df6c9d3bbae4f6fd3f514b1c5c740a2110f56ccf36069c85417e289c \
-    --hash=sha256:1ca5ebe6d454f1e5496cf052386a559f1080bf2de75bf327ebca0a6003b79f19 \
-    --hash=sha256:1d804e4caf5d5da37d6dac1325da5629ebef1e27a294c2b568b295814aa36c7b \
-    --hash=sha256:1fee9a16d88a1c4865610de31ef5c666671020d7a81d1f510eaf3c97d00ebeba \
-    --hash=sha256:23136f5a564654eb61061ec6d5620a4c1ea32c8f552b65e9982a12b72bff601b \
-    --hash=sha256:2784090c30a586d5b45197bd9c32f87fb927216cde302f6cfd76d76577e90f08 \
-    --hash=sha256:29138fef49828542e859828107e42e50d0e587c513b7eb4b2d92bade2b0860fe \
-    --hash=sha256:2c1aeb92eea59d824f004341b26d5e4b47a8a441cf9726769b9a90abf9d0e08f \
-    --hash=sha256:2c5d675da8f1cb5650271c8ad5e95c0a3e5a183c105e72d953b12877b1c8d0fd \
-    --hash=sha256:3100d169ceb7bc8f05f89a6db11d1b21f119975fc26f29dc45a472e3569f0879 \
-    --hash=sha256:31199204b3ced121ff5407a2c342326a5d27e3870abbf94bd80dbd2451b7bc8f \
-    --hash=sha256:32217133dddc58c927805cf6c0731d8144584176b768042ee886d51e71860bc9 \
-    --hash=sha256:33fa55b990f81c2927e01399ace0d18926c69d69baa8cdaa819424132fb97987 \
-    --hash=sha256:35ba0263bae5dd3ad5aad767cc9afc01a8598c7dae30f1b3b2de98b1b32c28bd \
-    --hash=sha256:35fc236507fb1b3138f0af5ecd5f94ed752d4d6d826248eae425f86204013eea \
-    --hash=sha256:361f7206cf341ba94fb015688f5c8b480f8e63bd58a4c14a48aeca7851a241cc \
-    --hash=sha256:369b5aa01b241cd3fea6890bdbb11a1425d87bf1515831500d518f4223e9d72c \
-    --hash=sha256:37245ca4105386194dd1d292a6f2aae09bfe1bd7ac6f9ec25093e3cf8e9b143b \
-    --hash=sha256:372c063f37480f62c1ae32dc3a1a0a5942b180c883f99789075a8a8ec3c4e709 \
-    --hash=sha256:37a9ebe00c698279213d56e6c64e1962ab1e092918270649b397cac3dc196ca4 \
-    --hash=sha256:38c9986f9ce50c459b10de216a05f4bd7ed5ac63887d56e500a52bb464b861ce \
-    --hash=sha256:3adf06c66041aa21eeb8a71e82379b74773298c8e6d3d839b151aae441a99b94 \
-    --hash=sha256:3c95601ed98fad3f6e2f8fe809c3b526b0fab31ef525e00a155e227f3d17f58a \
-    --hash=sha256:40aec5299e1ed71fbb988389059da381c3c1a60e0c649acceb2a35d9b128848e \
-    --hash=sha256:43124fe172ada86d03ac3c8dc8179091341f6724d5e5d5b160e1587e4cd3761b \
-    --hash=sha256:4736d350371337825cac1793c9f7c40701c32a03912548c2a7608e51679cbb96 \
-    --hash=sha256:475d04d5192eba487a3e2f935976340baa24529046e9c1c9c7a3b7bf80445ae1 \
-    --hash=sha256:4a409ccc42aefec904038695d5d7fd6d8f3af2721b7b6401d55135ec7d6d298e \
-    --hash=sha256:4d718fa1b5f0d0dd75e86fbbc5b0c93ea3a5d65216c85c61cd5d7cdddfe08455 \
-    --hash=sha256:501ed8b02a5990c67a91c732843609d43a6be1f7576fcdfc867331239f37fbd3 \
-    --hash=sha256:539c2cd5fed0947c135cd7eabaaac55f48300dfa1de0f3ca4edb5efa6606f471 \
-    --hash=sha256:557a4e1708df428ebe6c3081c83a273d275dad2446ce0d81fc648ac71afdb18d \
-    --hash=sha256:56d834b74c993a7d7cb2b8ab33a0d55c3e0d4a3d2f2da2808a4ad3d79189711b \
-    --hash=sha256:5800368526647146978389dfaa46da3356291e9f0fff9a4ef12e8c2bef964a0d \
-    --hash=sha256:59c123d0e948d760a5f930f316cfefa07e8d632ab84327c0693ee6a88171154f \
-    --hash=sha256:5b30ddf7234e611ca877575b62840e6af5977f92f1f9d532eedbb05a44ff8004 \
-    --hash=sha256:5ecace251ccfa705bf3d7d35c5032cf750f5c629809740405697bce5c118c4a4 \
-    --hash=sha256:5f89dad732280e7a10b74d40b91364f88e13c3f2c08c2ef83a8cd42f7a61af2e \
-    --hash=sha256:637f4ae36264bd7b8d9a60193acddc1d735ad52e8ed53a19931ea6d921fea8e5 \
-    --hash=sha256:63ada7ee2e9345695f9e9bc4c65d72222253f07b1ac94fd0e37555cc6f3c7f60 \
-    --hash=sha256:6441cc837aea58be7d9baef1b2383eb8311ab9303f500f99ac90b584cd78bb14 \
-    --hash=sha256:658f90f49cf5af2441cad0a2b801c3ef520471989a1ec55bcb25b255b2ca8d2f \
-    --hash=sha256:66987aa68b0f7c2a1cc5f388ca962b8ed92b10f79de38d6d0d8c716154f519d9 \
-    --hash=sha256:696477ad71385c4795e3b8e4cf10b0d2c28c2a1ca6a955e031cb1e62993e9ee3 \
-    --hash=sha256:6b7e54fd883671d1a8810704851c044b7173287c552b9f5c3d9e0eb9f00ae194 \
-    --hash=sha256:6bc94fe17c3c56e5418f79515b786b101845f70609b0d19d0c1ba13448e5633a \
-    --hash=sha256:6e6b7e3a1520c39a2772f414cd9ddf5995f77e4e823dfa1522af383addd465a3 \
-    --hash=sha256:6ed30be8918e18c8bed0a2e8b70639ecf02feb61ed00ca2e41cfcb2a50fa3f42 \
-    --hash=sha256:73533644e1f69ea1164d56cc6505f564c6c44072b646b66d67df2d31fed0348c \
-    --hash=sha256:73bcafa21a78d0776b3ee7cd2a63c66f968eb7db8e8d594e32d7329950f6e828 \
-    --hash=sha256:7814bbee202acd3bd240204c17d8b87a4c48c81064fd8674dbe527d94d5a4290 \
-    --hash=sha256:783ba7d845d79ce976afd9c1e91a4e5714671defa198ee789e8b23316083a485 \
-    --hash=sha256:79da2491348b30810728050b4a8ec0416f85884125c2fd44655b3d01150d9c3e \
-    --hash=sha256:7a0c98f6a636adf0d7edd60c61589eaf52d149239af754d0bfeb0effedba53a8 \
-    --hash=sha256:7ab379f95caee071a37cbd8be86d4c65accc651d391f9f97748fef006f38769c \
-    --hash=sha256:7bf6478188f4e47bf5686e8a33da4ae28bf43b1b2528d9ee144d28492bfac60b \
-    --hash=sha256:7c6eecfab7ce4cd9487ff8ba936fe38cdfd68c04faf3d5c710363c6a8e695659 \
-    --hash=sha256:7c708566da8014b120a64b1eb6d200c6c0c8cb36296383723cdb6fc82038270b \
-    --hash=sha256:7c8d5882ba25ac0282258be435d8a05aa0cbcacfce15799154a338f847f159b9 \
-    --hash=sha256:7fc59e9ba821b220944ccfe0f89c9dc4745f6d097569992356eb03869f21e953 \
-    --hash=sha256:7fd79c521f6290c69125fa2b85fa65d9e657e6a8ffaf722dc881b926bef4aa5c \
-    --hash=sha256:803f8b575a71b1b299d677c28db0653459c79b5308874efec813f17b7457c7f1 \
-    --hash=sha256:8050e75af7e4c6e2d5260b84eeedb618f3e452e66473432e085b5d1b81429299 \
-    --hash=sha256:81cdc537e0a42e3c0170752fcadbe450246d5c3b4b7231d6eb9672456605ac94 \
-    --hash=sha256:827c92145b3b976b39430129c89d213b250dacbe5fce678e9a03940e6e848983 \
-    --hash=sha256:854fd2f1bc6e8a56b89910b5cd7261a8b40f13ebb31572da985ce59c7da0886d \
-    --hash=sha256:877ca17fdcfdf5c397493a71e5ff97a87bb181417fe717fdadc77c08c09301ac \
-    --hash=sha256:87cc632c88ee5dc80e12681047839304d98ee5c9a708d686505767001c9b8b9a \
-    --hash=sha256:8879510a76940670517ea1cb589978da44b86e286ec3e50d664ef330817afce7 \
-    --hash=sha256:8885e3808aedbd6725b921fb67dacaae0678933561ddd47c2b01315198c70e2e \
-    --hash=sha256:8b193bf7a443c97d81c47052f60c486071a4bdef4a573fa2514f920089414d45 \
-    --hash=sha256:8ed78ccad4c7b421804f5d524b7740946a7ef75d89dc0dac52e9d7c24c472410 \
-    --hash=sha256:8f2973bbd2bebd9d2e0cd6394c1292a1a19ccd56bdcbe1e174059f1a39be5b40 \
-    --hash=sha256:910d4260512660484c0dc1588a316fbb35a40c081c36fc51d1225351af17cfe4 \
-    --hash=sha256:95052e8777a86bae87c0bd0b5ab22d809e3d1d02bf69e3e66ddda5ba75a05805 \
-    --hash=sha256:95f273bea318a194f656527ee2ed19494327bc500b8e87d9358e3222579aa28d \
-    --hash=sha256:963a8d8f97057082679523d0fd4c53a38f86bc58cabe4556faef682ae53fa2fa \
-    --hash=sha256:976fd7689d69ec78d67d31d38d396d8adb562f7e8368279f76aed4aa451fa06d \
-    --hash=sha256:989261c5f1735a165f2e4e87cf6d5f17ab734fa18f9ad0383d5adfcdaefce701 \
-    --hash=sha256:9ae9614c317c50836689ce2dfde07c05fe0b16378562e2221746c3913ede3c80 \
-    --hash=sha256:9b0124b9c17e9890f0819b2e7a5f65ec9a2f5aabd6c8e7ad090c1675cf70dee6 \
-    --hash=sha256:9c4880d017555d70dea367dd49271830842d48e3891c2da97da7ce8c4abcee40 \
-    --hash=sha256:9c62e71e6289d78c0108d8aeb495f8bd3cad4bc1632fedddc9297ddf287ecc20 \
-    --hash=sha256:9d0a21cf76153de8f2d96a877991d6bc59b9ab5180b949e50db73cc193b4a694 \
-    --hash=sha256:9e14d17773b1b3c758ff153659a1824608a0cb562c45f484b5ed8a433428444a \
-    --hash=sha256:a16a1dc8529f9e734a41c3b856f3eae7ebacdc061dde3f8a844e0c7889c97203 \
-    --hash=sha256:a2212a0c842c723d919ea4a22a9296cb6b244b386e4e6ea92adfc7fbf3095519 \
-    --hash=sha256:a313bad717dde740959d50850c315b75fd4eb0c5e6b4dc8535db0f1c369be125 \
-    --hash=sha256:a32b78c1e52ebd8e247bb68300b90b233300d8816faa008ed0713bc539fb6af0 \
-    --hash=sha256:a3ffe881246d28a862f1985824f484cb7361f44d6b99c4c620436ef56462f38d \
-    --hash=sha256:a49ff5cdb33654cb7d6a3c377aa2a83ddefaa1db31eb10bcf3c180aa84f9af8a \
-    --hash=sha256:a8b75dd3d3638d9a19f23e84af4ffab3b8940422c0df2da2a77005ef5aa3d7ea \
-    --hash=sha256:ab64ace1a68682d191d9bedd9d4c939406ad86b1d9f628180410644249ad46c2 \
-    --hash=sha256:abc7c2e4b47bfe6a9aea434d3fdebb9597ee636e914e92ba352f2068b9142f4c \
-    --hash=sha256:ac348379cf4de5538a0a213be1532d289aa801ec5d267c5909446b9ea2f8e2c3 \
-    --hash=sha256:ac51cd64bae51c462ea58ad2492c9b8209667a4ef60c45c4a304518b67598d5d \
-    --hash=sha256:acddcac38adc8342ba48aba98896faa7928854bebb62542362138655b5367ee3 \
-    --hash=sha256:ad4528cdce058b684f75fad1faf4a6a6c992fe2f08376370ca66e4ce5916a84a \
-    --hash=sha256:aec65b53a07f580606593f877eefbb29a45939bfc0d3fe6e6d9f42b41b749f68 \
-    --hash=sha256:aef74e9beabbd6c4aafc091dabff86d046ccf013ce1e4396c0fbb01b4cad9de8 \
-    --hash=sha256:af1b5a92315048c3e36bbebfa7d4760a9c3e910bc4166f11b20d77d20d6bcfca \
-    --hash=sha256:b22ff30006a2f28f8bff878fb93413cbe3a4d1fd517c28081d848c90e9cfd2c8 \
-    --hash=sha256:b2483da477932ad1983d1d33c18bc3771c6fb00cfbaaed70a875fd547ef8e840 \
-    --hash=sha256:b2f0adc22a4eb31e545221d93fc73a0f6a8cc2379d0f4309f71d1d17ba938b82 \
-    --hash=sha256:b4c9e5d05b126b267ac048a89a0e2d9b48b1b648add62d4872906304a8590610 \
-    --hash=sha256:b4da208a63434d21a3df64d29758e650fc4aa8cb05848554b76949c296539cca \
-    --hash=sha256:b5f8771aaaed7f80e84a4e471d2f29ab6721e4595075e54d03ae1ed951b2000a \
-    --hash=sha256:b65121091567847a8cb520d364ab22ba90e00d3cc55fa9eb34bb439f0684bcd1 \
-    --hash=sha256:b66ccc5c2cdd26e74fa5d4c29ffae424cc6148bf93ce574821783fb3b6d452c5 \
-    --hash=sha256:b69651732c64afb691e50cdc3387cae305e0eeff8804fe3e3ce203876494932a \
-    --hash=sha256:b828cf64d62dc09ac183f03c1aeedd164ade96a2ce4934109452edf29de1dd13 \
-    --hash=sha256:b8a65621b98984a62e59403009591b8a5a7736273aefe1cab64cfb85b365cc07 \
-    --hash=sha256:bb0d664505f4b112f384cffeee82e91e3f6448d8e574989479db4439b68cba05 \
-    --hash=sha256:bb58ba73a3f96f9a3e46b1fab69929d7edbbddb3133ee74b5c3c54074a53c4f1 \
-    --hash=sha256:bc94a68ea5e18f8e85dc6b522bcb53093f692c8eb62b4837ac047da73956cbe4 \
-    --hash=sha256:bd82c4977196681a499bb6ca9e462afbc5c91c1c15b6a991dfbd72733fea4dd2 \
-    --hash=sha256:c0c88085affd35c33e124e36930c5ad96aff9294ce195eaa0fd9cec962b64a82 \
-    --hash=sha256:c148e8b596000dd3e4bfe206e70f3e666be18d72032e0012555f2373c52e35d6 \
-    --hash=sha256:c57541034d12b215ab0a2bfa371d1a8a198da18176d0426c27105b9161a6862d \
-    --hash=sha256:c9648ed33dc8179e4ec04bbc73bd7f0038e1e81217a69467f61f02a78bf07e88 \
-    --hash=sha256:ca65cced0d67a9039e93bcd98a369920e499bf98296844ff56ead01c9085321f \
-    --hash=sha256:cf22b43f35b7dbb9f71e8ee2041b5c00029cdfc28ede3a2f31cf8906f9a6c126 \
-    --hash=sha256:d35a4f1c63f07fbb8c8f9946dea98b21eddf6c57421585f71d91864be3ba2a24 \
-    --hash=sha256:d3b6e6840421c83ccb60398e333b44f910b0907bb409597685ab2eedd1e22eab \
-    --hash=sha256:d73fed4e37158ff00cd271871170b79e40138db51e625fd352fa17c6acb34f67 \
-    --hash=sha256:d7bf9e43282d69561618e8a0ea33368d532ebef42f15c096f427090521dd74f3 \
-    --hash=sha256:d9d6544790ba50438a9c1a903c3c4afb1ec8a7832db5518549275b40ef0dd4b1 \
-    --hash=sha256:db4d697b18b6ef5528b1f36bfa25072cd2a421869f5963bc0e92c8a34b9e2800 \
-    --hash=sha256:dd9a137a4a9becda3094f3831cd026380f75f6855e051eefe4c73ade524f1cc3 \
-    --hash=sha256:de7738b8c0bb74c4cc16bbd7fb49fc2bcf6430dba11b3432cd52768ae40933e8 \
-    --hash=sha256:e3b1aa25f01238886a6baed9e13b9a9240ed344346c79ae280ae65e8603b21d5 \
-    --hash=sha256:e58952f04772f59f11c6e007471449809a30165188669bca8fdb19dde40a8f24 \
-    --hash=sha256:e5ccad4b7bac125722f48d6f862bed3b514d8526deea06316bb72f152cd30a7c \
-    --hash=sha256:e7386aa18d98d6b8af44b92173654ec469237fda35f8e8523e43b581a86f476a \
-    --hash=sha256:e81ae656b9935ac4528a71f96bb7a14d949778ed1897c573d3e7ebb9187f8841 \
-    --hash=sha256:e8f1e362c9352b50ed120f001046fdbb80810c9d56580f4c3fc13bbe30823387 \
-    --hash=sha256:e96ca64383efa107262ee3949f047af5ee4f1845ba09463466c04d35a83bd3ec \
-    --hash=sha256:ea999ae6e80e66ad5eea287860951b033d0104ca34d6d87c7b5125ebe0e12721 \
-    --hash=sha256:ecc89dbd4155b2f8a47f4bbd89242a35ed15e8e0ec581cab5ac65fa38407329d \
-    --hash=sha256:ef01d29fca550ab871fd99154f82c6472aacf8e7def272dfb07b460123850390 \
-    --hash=sha256:f04551dce5a7db8c9659f2e4245494c182d0663b83661803e08d46bfcae5eda1 \
-    --hash=sha256:f0700527dd5bfa8b7204b08330542f4f388899d3c14d885d8a368992e0eb562d \
-    --hash=sha256:f2524ec55b3e65cbe235a8b3c36e2af3b635be02ed05e20c94e70c5c943c009e \
-    --hash=sha256:f5844e7befc707367807586f550fa97e23dcfef0728f02b98c7bc498a961a5df \
-    --hash=sha256:f9dad513626a33670f17cddc6078e30e311f444c957e8dbfc5b2b4603c8b4edb \
-    --hash=sha256:fc0dcb22fa9aeabfe3fa4e0430099acff985ec5d77a851382f76cc6146e780e5 \
-    --hash=sha256:fd882aa29bf402b62bf1fd7c19fd5df4b6528cf468a908864b39368572b662a9
-mypy==2.3.1 \
-    --hash=sha256:114dff494000f18bd10d5d95d84b8567b26da60279ecbe838131841df20e635d \
-    --hash=sha256:18162b128c3f9c703cd35f5537446900b0d21a2549aa7a95d21380d2ef643fb0 \
-    --hash=sha256:192abaedf75da1bc0b1cef104927e70ec49c1ef0031cc4825c7ee10a438ed24d \
-    --hash=sha256:1c80fbc405ed8020f5ff3802dc18cf060197bcdd3fbdd6a26ef2fd34dfdd5226 \
-    --hash=sha256:2166b29228835e1f88ff411e96639e6ca3c7fdde84b62ec211f70f86b4051167 \
-    --hash=sha256:2329c0501293d4e1f33bc15d04d6304d65a1cdda967ee93a05c1e681a3923133 \
-    --hash=sha256:2a0ba2e57847849fb0d1fcdabb32786d223095ed8bc121dfe322bcdb3d9c46bc \
-    --hash=sha256:30c0477d4aab7b7f39c8397dc877f2c96b9fe5588ec379f372c56eb63d599f63 \
-    --hash=sha256:375d7013876a8233b2d05be185bfa09f689696cd999ce8b1cfe6acac5c80e8a3 \
-    --hash=sha256:3c80cd23d85368bdd9f37d5231dfd97d35bcbf5bf41af96ef3a9b078ad1957f9 \
-    --hash=sha256:3f7e865dd51f235f60a2dbcd8728a1c095f5ca28f095d48a725b84cd935735c4 \
-    --hash=sha256:47a8a7a0a7f6f6e63995c0ac36fa0c07b127413fdc81f0439b7f3dccafd33561 \
-    --hash=sha256:47c1b1207258513a9d93495f69c8be9de73916186f0e52703e8c461b7a623419 \
-    --hash=sha256:4956f34d145e145562a0a0bf367f642bbc85c04ec2baf47ae015947c3169a85d \
-    --hash=sha256:4c5095a327483591c94e0c8d3ef9e50d4ab1369b541eae007c1f23bc2a41f6bb \
-    --hash=sha256:5159ae60f5dbc3a498af5ba8365505808ac8031bc63f9e00304ad545d40bdd9b \
-    --hash=sha256:52eaf3a155f35cf80b40220288c861eb45f14a2340c1f6cbfbdb0feff32879d1 \
-    --hash=sha256:57a936373fc690c43a8cd7e7e12a35148e4ec5aa7698ad7fc0a9f918bdc5be41 \
-    --hash=sha256:586b3612214cceabb3c0f588c97e7d1e535393f06a60e912e994f6b3ace97523 \
-    --hash=sha256:667196b352f4cf304ded4c10f90cfc179263a1acfb3cdcfa984bdfd340d498bc \
-    --hash=sha256:6941ab3619377bc3f32ca02876b07d27f216f5201604b664d3937ea0fdd23bb4 \
-    --hash=sha256:6ed5c7e3419083268e5c9258bd1c1ef91af44a9e89374dbcaf37b775716e72eb \
-    --hash=sha256:6f041a6de52c9217ca125e78ba0a335cb7fd98a1c0580978e49ab2b126f70b57 \
-    --hash=sha256:71af9c8a894e862b58e92abb08e53b05a384a1e5e5d6dc7cda59126211a53d82 \
-    --hash=sha256:77ad9529e67dca28e511f5cd5671436584ce91f6d3bac159a353158187b986ac \
-    --hash=sha256:83d36c2924df7426333abe7faf4724a7e1aab0d9fd41625e81b4683034b80c13 \
-    --hash=sha256:84081f538ce27375045c02e3d7f81bd11d853400621ae245d87ce7b6c420ec74 \
-    --hash=sha256:851833db876e7b650f93719c74b7879a08e338979c96054fdfc3bfd90a486355 \
-    --hash=sha256:858fc57d3d91fa728e33e7ad71def60fc6272694607b306cd3292db53ae39080 \
-    --hash=sha256:8ad80807dc3ab8ea978b1b2b6e4a657194ace1d4ef03e0e731aff1abd517da29 \
-    --hash=sha256:8e036f06b41630f4c8a1d48f9ac6aa26acc65f8be089973f5519da643318f03f \
-    --hash=sha256:94f04929f1c44c35fb0061e912087edaf504acede963a4a7d00680bd089d8531 \
-    --hash=sha256:9b4eacbee8a69836c06eff6d0dd4e134a07c2b047755b30c08625fe214f322c6 \
-    --hash=sha256:a32bbbb940af990d3be0b8af321c7b6815bb1b3b48142fe7459b9cc5f58959ff \
-    --hash=sha256:b091a455111214cb5c9d54a57b9618e9a49f9fe2a42e4e1ac86e9d104ed96ce8 \
-    --hash=sha256:b9c53e395c12cad2c6d4b67d5da7c6057638a132d85c08b73646b18f802a0045 \
-    --hash=sha256:bb26deed807bdb0457cf3e3f1cd7c4a1cf9d66864eaf1b4a61e06805d4c6b1f9 \
-    --hash=sha256:bbfe022634a2a195406bd469e888d2eaf193b02ba7e607391cd7640374aaae3b \
-    --hash=sha256:bf678dffd16efcda2c15cbd30e9ecc0081388e29ea23687a88e686ed92638dc3 \
-    --hash=sha256:c8637731bb5eee3671eb2c3200827aa3564ed8a9309ecee4d1afe77e6d031bdb \
-    --hash=sha256:cfb12e360242d23d91f5e978d94f58ea66acf5804c4fb6f2f794a20d4cb1b595 \
-    --hash=sha256:d00d769056bde2f4e69c175071eba45cfb44fa1ed92bdfbfe64a93e0543b0cf0 \
-    --hash=sha256:df12e20c9efd614738c71b390007ecd0181125afc4ccafca04d78a1d2eed2c01 \
-    --hash=sha256:e099200a1b1b1223a4951f0a90cbff1b8c91b250ba599dab1f7217a628144d90 \
-    --hash=sha256:e598c8c66401d26b150872154a286e6d484cf2789c3bb28a7556806298423021 \
-    --hash=sha256:e5f1c50bb05b64e2026b52867e8d21106f01313c744a2c4ecc34c90d12e8d6e2 \
-    --hash=sha256:e9144ac16fde007096f9563eb2041b4433c2d705c4218edeb79e7e9d01035ee6 \
-    --hash=sha256:eda22fd4efa9dcd39331d1dede9b5b8b8a7fd69af07592e778433da98610d29e \
-    --hash=sha256:ef0c6335cda9d807f8193d8ff6204a72bc909fa9882aacbca14f43cdb7188306 \
-    --hash=sha256:f12fdb70459d0060dea40b29e52163a961b156106d68d57882a6a9f648983a53 \
-    --hash=sha256:f5d716048611e85ca9eefb2e1baa5d73ede389b5820ded260ea27c757d667af8 \
-    --hash=sha256:ff715e45b2231a8e85de1d163d1b42791e4d7aab8f5145f85fee1b710b735aff
+markupsafe==3.0.4 \
+    --hash=sha256:007e1ffd9bf65bb6ee96df7b258fc632a4868dd5566037986c64781f35a36e98 \
+    --hash=sha256:02fa4acbc6a3fc5c693c34d4dd8c1130b7fe99cc915181b0ddd6f72aeb296002 \
+    --hash=sha256:03470d1a8268e692ecf79ecd565593e59d44219377a7ead61f1f1b94c1f7ff6b \
+    --hash=sha256:04e7902ba80ee4bac1d50a549606527a1dcf0476cd81403db41099d3b60ec653 \
+    --hash=sha256:051417f74bcaaefa316276e0ff723f541616ca51043d070da00249d9bddd3e3c \
+    --hash=sha256:05295589e619b9bed252a86b532b8e27350abc372d18ba89b59375325e91ec1e \
+    --hash=sha256:06de8ef6331f6e822c28d577dc8bf43fe398800477c49498f38fc38b67ff33fc \
+    --hash=sha256:0764a13d34cae40db7bbf3a09b7e9b491bf4603e20b263a7a9d6b8e324975d0a \
+    --hash=sha256:077293e425f28ec737dbcad442a71752e28f8ae27cde3d68acd1fb212091cd92 \
+    --hash=sha256:0930db9bdc62d22944e10b066448bb65dc9abe9112880c7cab8da54db4284d5f \
+    --hash=sha256:0cee7cb0f9a1b6892ea482237d9403b3d1b4603aee057d0ff01f0fac2d019a97 \
+    --hash=sha256:0d9c47709875fdb321452056622e930c52afbc07a7d780762fbb8b4d91ce6fa4 \
+    --hash=sha256:11935df9bf455ed0c04eb87bcd720f02b1fe5e02128a9430f23aed6f93336fc7 \
+    --hash=sha256:12a606a492de952afcb43b59a14aaaaad120e708d3663dd0fdf2d738d427a691 \
+    --hash=sha256:14bd2d845d62ab678eaf81da89d7b621b51756c72346745c1a594c09d49207a2 \
+    --hash=sha256:15ba9e28640feef770374b116a6f019c21f52404aeabe516aa7f800587b98cfc \
+    --hash=sha256:18a801868a884f216e784d7d14db2a4077143ce7610440aee2ce8f734e7cfcde \
+    --hash=sha256:1c0df495a977d10460a94941799c72d5b5ab03d3858d949b55b5a66c8f371c99 \
+    --hash=sha256:1caa2fa5a6184fb233153b35f654e6687bd555476f6170f29d8ee9be1a8b0af9 \
+    --hash=sha256:1e1451fab512d1bcc3dc26988ec1edb0b82c2db909132872cd9356070a6b63df \
+    --hash=sha256:1f1f9477e174582b0a1b583d60b66e1f2cf5d3fe12cee985e4aedf44766600e5 \
+    --hash=sha256:2628d3a8cb648ecebb3c5d6b0a1052d400e4d8b7ac0fb786be8d285b50040d17 \
+    --hash=sha256:26e9867520db70d37f7fb421a7f0d8adb40171011fb84ce869afa1a83370dfa8 \
+    --hash=sha256:2a6ef68ae94aed8721934072b27a3b654ea2100b97e4ab864cf1489c90926fbc \
+    --hash=sha256:2b2b1e18af909b448bb3cf9e3433366f7a8726271fc214e8b10e0f62a78c724b \
+    --hash=sha256:2cb3dd71fc6be918ad4264346a8ed69485f9b7ed7bf35495d8e22807cd6b8bea \
+    --hash=sha256:2d1b7d9308288661f56672b1b157d75fc536714d3638487bbea17b6318a78248 \
+    --hash=sha256:2dad610540cb2e6272855c178f08ae9a1c7ac258a7fb71660553a5f104b42741 \
+    --hash=sha256:2e5a7cd7fdd14fcb1ae5d7d8bf23d24fbd1daefd1fbca2580132e1ea75f098b5 \
+    --hash=sha256:2e9ad7dd851bf45fab9f75cbff4cb493fee9979e8d8c7c9c3ee119022518edd6 \
+    --hash=sha256:340cbb1957ba99929cbf19a75626d36ba1ae21d1730b287d1cf7f824a20c4fc7 \
+    --hash=sha256:34bdde374c5932765d7dc685c4a1d191a3207852d67e8e0a9eb6ea85156181f1 \
+    --hash=sha256:353bd63081912ab8cfa6a0c7d185934cdf8426f04c618bba6bc4b394f2069b67 \
+    --hash=sha256:387d8cd30e69b3f0a72877b9ae717033396404e19095b17fe89753a981fda44f \
+    --hash=sha256:3882fb412298575bae3b9c46868251f15cc69307359f87bb1b382e53d6e5a2c9 \
+    --hash=sha256:38fc55594dab834470b6733dead2ee9e3f657fb0608c769dcafa0ba5ab52f45c \
+    --hash=sha256:396ec4e65cc889f69786b3b89478b471cee5a3bcf468b9d9bb03e1a30fb291fc \
+    --hash=sha256:39dbacefc411633db5b4378b066a9aca70a3d7e2922c9e578d825f844026eeba \
+    --hash=sha256:3a93d9616ddecfb393727a0041a562cf0b15a244e20f2bd25efc7949be4c4f17 \
+    --hash=sha256:3d23795802fc8bd72534836d64489bbf0f67c088959091bdb22e10735a5107bf \
+    --hash=sha256:434139499bb20b502ed3baa1f169e618f924a97e7a777fea1a49446d80106cf6 \
+    --hash=sha256:436e3ffc6310d3c41878c601db29098102fe5d8a467c49da4a4125254e0980f2 \
+    --hash=sha256:489505b03f692c3f376394e49194fa7a7f9e8558d6e293a7056a0032b0c38163 \
+    --hash=sha256:4a540e2d3192792fc84eced57bef37851ccb2b41f73291bb17408eea77bcd278 \
+    --hash=sha256:4a7cdc2a420ca01058182da4253329764d4bfa055564d1eced90e6ba1e8b1d3d \
+    --hash=sha256:4bced6e2a6dba6a28f7dd3c6ce14df1b2dd495923f16ea484cad03decd463b2b \
+    --hash=sha256:4cf3468d5ec187ffffcaca8e61929a37448f215dafc1386a12c750a72fe53634 \
+    --hash=sha256:4e2c4809c14559aa7ef426f27fb35afbb38104c349a903bf8f3600456764bb38 \
+    --hash=sha256:4ed644d75aa94a2baf7ec3a96eaa160ea58c742eb9d27c6506053c5c40fc84ed \
+    --hash=sha256:4f6e0852a0283b1b1fd776eeb7b766a5f440b3e2bd31ab51af3b400585f3965c \
+    --hash=sha256:5066b244f576f91afc8ee3ba029a89f99d39c79b1853fe9d39bea9f0afbec148 \
+    --hash=sha256:5086f9975abb1ab531ee6afca1761e4b59a19b446f3f6522ed776963228cfe5a \
+    --hash=sha256:50b5bedc9ed8a94fc8857a42ef4f84a81ea88f8d4f05dc8705fb23ee6d8dcca7 \
+    --hash=sha256:52704c5d36eb6dda8866493decd61111fff86244c9b1ad225ca01b9e91e5970f \
+    --hash=sha256:55ffd6ce583d97dc71dc92e930324c8c0d25aea7e3ade6ae54ef77cedb096811 \
+    --hash=sha256:569d65055d367e3dcdf30c3f41119467b73d9ee9faf332bdf40402644f5ac08e \
+    --hash=sha256:57f9947a7e57a081c1e3e0a2dd0d2dcf290a4531450e6f611e30084c222a7295 \
+    --hash=sha256:5989cb26b2e1efc6a42216a9f6b5ee495ce5ace2e5b352a9af489976b32d1ee2 \
+    --hash=sha256:5c22873ad1f0532ba40fa1727f3c0fc1bbbaab6d373d4cbe3f0dc74b2e2521c7 \
+    --hash=sha256:5e8b3d0b18fd623afa12ecb2ce8d8becef69f9b5440c6330c7972200e0bb84b0 \
+    --hash=sha256:61631e08084be9e21a8967ec3139c7616ed7c5e9368e05c86d1b39562c8a57b6 \
+    --hash=sha256:64511c54db4e4987aef4c41923235927428729e8174c5dba488429be70a998ed \
+    --hash=sha256:6669c1bf34080161ce49c589cc512ef24d4c704ac9d2b2d3667f519c60418378 \
+    --hash=sha256:672d207103e6b16ca098611b0f9efad6bc00afd47c03d6ef62186495ca677dc0 \
+    --hash=sha256:6768d67d1bce64270e0fdc2e69309d68b9b18ae56ddf6c711d168e9d051c2cac \
+    --hash=sha256:6a45c3d514f2436064db00d7fc8778d888f0236ebfed649b53d13a59e69ad51b \
+    --hash=sha256:6bd9e1788e15bfcf6a9082de42e30387e7b85d211ab21e57a939bb8cfaaf8d96 \
+    --hash=sha256:6d2a9efe686f9de00d0d1ea32a4a5a86d558a2277501bd78d964214eab625e59 \
+    --hash=sha256:6da83a088f8ef93b2d483a8232a4dbf4d69d3d8496b568a03c56becac43e1808 \
+    --hash=sha256:7018d4af1cd272e847aa5917983ab5e83e4f6579f9dbfecd4a79c0ca80b144c2 \
+    --hash=sha256:71f88e749ea29f67f21f3b36433c1dc54c7729ed2a6d9e2da2e0d9e0d7b224eb \
+    --hash=sha256:737c9c3981998eba27f11786f84fddcbabc74068b72a4a1f454ea02094b57b65 \
+    --hash=sha256:73e77980c7207854f00fc4e71fb1626868d5740ab4012623d55c7a99ad122a72 \
+    --hash=sha256:799c39bdf5e2f1292fedd3009f7b3c9e760f10b2420cb9638d56920840ff6db8 \
+    --hash=sha256:7a83aa6e4805df46fed18e989d3d16f86ef60cb50bbc8d9ce3a6be89165fbf6e \
+    --hash=sha256:7d3391b2188d18737cb2fa147028b1096236eaa7e156446c650a489fa2cadc91 \
+    --hash=sha256:7e1636da3d8dfc220b6dd10264db5f2b165e4888c4518594898fbe381049af8a \
+    --hash=sha256:805c8b84534fa10891890f0e4be39f3a99e94615d93e8836bf9fa1fdca2feeb2 \
+    --hash=sha256:811d02d5122171c1941357efd8f9bf4ffe907b7f0a1a4e729a880e4be3f46e3e \
+    --hash=sha256:8138eb83940ec7299024d92d4dee45f601b9e6c5ffde9d25f4e35e326203c707 \
+    --hash=sha256:83b3944fea42a8400edf92fd1770fb8d0d4f7de651353bd2d8525a92dba69a21 \
+    --hash=sha256:849dd2bb0e5e4ab2b71c7191726a4a8d5aa8a610daa584728cbee0b710ddc4ef \
+    --hash=sha256:8698d70a8081ee8c090dbb394768b5789a1da8b131b5499f89d071dd3cfaf6be \
+    --hash=sha256:8781a792a070cf2bd1b86d3aa943894115faaba6e88122a7bf32d62072742453 \
+    --hash=sha256:88d59b473bfb03259722600839af9bbd7fa13a2eb514beefeedb95997882f69a \
+    --hash=sha256:8909c2f1c6dd65e054ac4b573a91c8384d1492281e55d82d159d653f7a13adf6 \
+    --hash=sha256:8965520ac587c94a4ac48b729be3d8b8de00af39699b17585dfb599babe77977 \
+    --hash=sha256:8b5d563170ff8ba3181caa967c99a3c804d1dedb702c7cb93a6a7c32247da978 \
+    --hash=sha256:8e124f974786f831d6043728e38296969d3579db8896fe004682f5758e613581 \
+    --hash=sha256:8f0fac8b13d14bb06c68195f849371924ae53dd7b1c00fed24650f704383b692 \
+    --hash=sha256:9240187afb63d2f9ddc3e032c670356fe941f6e20662ea168a5dc3f1f317e1b3 \
+    --hash=sha256:925f929d6b59a8b3f8b8c6ac363cd0af7eecc81efb3071770b3c6717c450a369 \
+    --hash=sha256:9348cbb300d224fe3b89793262cb093504d4ae927004468463f745188a193e4a \
+    --hash=sha256:9388003072b95f2f1e3fd908604194d653ba21330d811961a78b7da1a77e9e36 \
+    --hash=sha256:9438a2648b2195980cb2dd8e53ed7b8df91319e2d0b70ae61a9e1d1bc8d3bec9 \
+    --hash=sha256:94e4c421742086aeee4c32a506eec8859d7634aad943f7e6aacf70f813478768 \
+    --hash=sha256:94f5407f7bc64fa6463906b896f9904beeeb7dd8dc116ee8e9056c8714ff9916 \
+    --hash=sha256:971a3bbb75d97ae4e2e8f7d4834236f86f85f0c85e04ab2e191db1123b04f80b \
+    --hash=sha256:9e227f3dbe6bde7491cf0a9965d00b88c6b1a4a95d11480ddf88bb96d397c19f \
+    --hash=sha256:9e25feb9e330b63edb0278a0acdf85e50d0cb0fbf49c3084abbe4e24ae195346 \
+    --hash=sha256:9f098115c247e11d138ab83a28fa0323c77015007ea2df73ba5fd714dfefd67c \
+    --hash=sha256:a18f38cafc329bac5e3c2b96c765b4c96d3d103421ed22ab7988c1e3fce27464 \
+    --hash=sha256:a4bbd2d87dd233b9fc5812160c3d0ffbe42edc22a26ce0469f58479ede633fe9 \
+    --hash=sha256:a5fcffb37e602b0b3c1638a97746b9b96125caa9bcf6fa41d337a9261de231ee \
+    --hash=sha256:a8e9f292fcda89b324f2f5c91d13f1424a153e40fc2756f38ee23b15835ff300 \
+    --hash=sha256:a9f54054101545a9a9cccefddf54316aa6e4491611fcbef9e91b3b6bebec04f6 \
+    --hash=sha256:aa2c838cc024642cc04c6854232f32b43e5e22833dd11119c1766c7873b8370d \
+    --hash=sha256:ac0c7c9f1609b0c4c114feb1d7a3409564c7fb77e360bed9e97e5d25dfeaf868 \
+    --hash=sha256:add96447a86d205ab616665d53b2950ee81083757f56e6ea833c8b2917646b46 \
+    --hash=sha256:ae9dcb8fbe244cb82f8a6458b455b927a03685e383d9bacf1ea5ce180b96dc97 \
+    --hash=sha256:b4a635a0487774f841cb1fb62e907e7195cc95bc761e053184b8acc3ceb20733 \
+    --hash=sha256:b4d12837e0203bbace818ff4a7461afdcd78bcd782351cea148139180d7bcffe \
+    --hash=sha256:b61687d0828e72bf5cda24a2690188f37170bd31c9359ac97e4e66569f120a16 \
+    --hash=sha256:b807e598953730f82e4eae3bd30f6a122cf6b31c398c6b504c0e04c13c170429 \
+    --hash=sha256:b8cd1f918b26fd7b1832ece557cc18f2d8747309ff8b3f0ef9d4250c5ad67a39 \
+    --hash=sha256:b91cc9d336957239ff200f30097e6fea2dc6d6fb3c81e853eaa09eac904fd894 \
+    --hash=sha256:bd3ce56ae2cbae3ba82b683bc425cd7e48d2ed8b10f3e818186b6f5646d9271c \
+    --hash=sha256:be6cb0c799abb0e2ba3e618e6d28ddddf7e485f6c2ce938dfa237daf3905072c \
+    --hash=sha256:befb4158af32106b9a93db8d6d1d1cbbd418c0d5aca0cabb7b1780abf0c89169 \
+    --hash=sha256:bf053da3c97a4bc5ecfbb218cdd2983febd91c617be8367d139882aa11e490aa \
+    --hash=sha256:c02e8f18bdedba082cef725942ac823b9b60656db07f7e265cb31618dfd00d77 \
+    --hash=sha256:c1bc67752d5f21013cfe430df4062441714eab79f65a6a05e01505957e9c35fe \
+    --hash=sha256:c61750fadcd119d0825bcb7d7d675dd264dcc89cc05292aab5be68ebdbb374ad \
+    --hash=sha256:c90d5b3d4e944e065a301d741b3c1d784f6bd1f503aa68b4967e32b2ba313d85 \
+    --hash=sha256:c9a7f43c0b202b334cc9184af09bb8f21d3a209e038efaf106936fb69e6b026e \
+    --hash=sha256:cb96e6e088d6cf71c1ea977510948320234824cf226e32f6f6e044f7a9c82b34 \
+    --hash=sha256:cf63c214fe879a65e69a386f915e36104fc84254ab141240f8854602d8e0be2a \
+    --hash=sha256:d1aca03ede943eb80ab3d63bb082c84b7aab85ea83bd0fd0c200260945fb49d9 \
+    --hash=sha256:d2e56fd3b00222722abfb3f5f0759ddbae4b90811b5ad4343c64030ad1bde70c \
+    --hash=sha256:d5f93ebbeb8032d47e349328ec8662d973d9b05a70b3c35df1f91fe419b84749 \
+    --hash=sha256:d882a373d8093c2941e01291b7ced96e9cbe4781da9a7751ca7e6c70385e5214 \
+    --hash=sha256:d920abdfa61279ba1a2ef9484aab07bf03331f8c08a10120fa332353d06e6932 \
+    --hash=sha256:da2af0d7aebfc2074080d72efa6ab8317c62481ef1f896f65d9999c1c01f4494 \
+    --hash=sha256:dd8ea6ebee7aedbf7c749fa80521d9ccf1ba473e0d1e14805caafbaad281c889 \
+    --hash=sha256:de8b364c423ef0a4bad9069657d617f9a5d2b2062457a89b1fa16ee199c399c1 \
+    --hash=sha256:df1ae86ff54725a01fa1a0510b914ca53a161b7050be74f6204e24aded5971d0 \
+    --hash=sha256:dff05cb7016dff1e9fd68f4122c127b65dfc59de5306cfb7ad92f956f230bee2 \
+    --hash=sha256:e1a622f13970d81f95d0c72f9dc090dce9085fccfa4c9f2174377ee32bd15786 \
+    --hash=sha256:e49fb0d1ce92cfa0cb198cc5b1b11cdf9d0638658e2a2db2687e39db7c87fc78 \
+    --hash=sha256:e5c802729725bd07e2bc3ab7b76dc7e0bbfc53129d8f1eb1c002c24cf774717e \
+    --hash=sha256:e841068dc0be4cb6dfb5c890eb88cbdcff2f4a332393c7ec94e8e618bd32c1a8 \
+    --hash=sha256:e916035e3e9930cbdfdd10abf48861340221857f45509565898e012263f7b289 \
+    --hash=sha256:eba154571c16e032112afac0dc2dfe9e63c2ceb7aedd07bb7eecf2ce26d4dd4c \
+    --hash=sha256:f03460ff076f70ab595bb45a0205ccea1971443575b6920c52e755dec2b3fbfe \
+    --hash=sha256:f0ec3b750b59375eab5b0fb2b9254810c00a3375be6d789899f1055a1d556237 \
+    --hash=sha256:f291bcf42ae98eb5107edb162c3c998b4a89648fd8e99ed4cbd12705292788cd \
+    --hash=sha256:f61efe1d2fe0de16158a5fe1d1cf3c14bdb6aecd54d8938fd26512c525c1f624 \
+    --hash=sha256:f68edfc67aabac33708941f26f22a7b8e9f81429bc0cf249fcf7d66b23af8d19 \
+    --hash=sha256:fa95848c929b6a75f6848d3c9793e59db365ee436776e57db835cdbfa79ba977 \
+    --hash=sha256:fd9f8797427910198f95bced71ddfed61130d7e349213bfb8466c9c99e2c46a8 \
+    --hash=sha256:fdb4ca07ab75ffadab4a8b135ad59cdbb3156b99310f3d565370da74a15d6bd3
+mashumaro==3.23 \
+    --hash=sha256:a671279ce93119d41c54adcd767753ae68adb32b9473de2f9d5d1720d2376231 \
+    --hash=sha256:ed69d5bc548c76efbb5286cc0e541a6b8796e621385f986e25b750364011abf5
+multidict==7.2.1 \
+    --hash=sha256:02009b402129a73e1f3da68f48eb999afbacd29f25aef0d5052b84ff5c2786a2 \
+    --hash=sha256:02d9c04d395a36eeebe89e45f2269614a4675b8e83fddcba15bba2be903971e5 \
+    --hash=sha256:03846be88267369908fcd9a91159358a3b142d740991c96e4f696d362fce516c \
+    --hash=sha256:08ea94663d9e7c25d14d78222f7aee906c472d4837766bec62477c38f6e419dc \
+    --hash=sha256:0c454b677214fa604e9c4a38952c685dc88a62c96f5576a7ce550f213d1dc318 \
+    --hash=sha256:0c52fdd8cb8194fcb6969a417149aa1d09d6e48b69fb1b34ee1b1e4cb51ec183 \
+    --hash=sha256:0c7b4d8cc9e6ae7070b8129bdb840215552d4e2689ca765d37eb208a24919209 \
+    --hash=sha256:0d852d3d9638f852158d7de7200dd77f7ff8d77fc8f3d396032f3d847883f631 \
+    --hash=sha256:0eb7fa012ab47b13e96bffc1369642f520adcc4e3d3e170d7f1a2b39fb953bce \
+    --hash=sha256:0ec95a02f9f08246cc7f1d85ac425e4d5c233fd3f098f5be1b2cca16aa690186 \
+    --hash=sha256:0f30d6eaf3cb309b6c21096c6c2b4cf3800f195a78b1babae85f481ce851bdc2 \
+    --hash=sha256:12bbab225ce7f69df75409ab8005b11b4e9309fae863821e019e81b32e53a2a8 \
+    --hash=sha256:13268013a3db11a214ccb6920f778d175b765f69a40509610b92e43602272718 \
+    --hash=sha256:15da10cf11fd8d8716720c95b93180e94c8317405d89d08524c579ef360128ac \
+    --hash=sha256:1d369ed297e79b417766327ece16bb7e89306c588df63c364a85d90d4aeac843 \
+    --hash=sha256:1fb8c1a3480c130c3a6422d5f16f3cad6552bf08c2089dd288ba7134649183b5 \
+    --hash=sha256:2022bd3194968a027f64ed16f9779e62e71a823a9df3971a7328c1d45dfeb9ab \
+    --hash=sha256:21d86f2aa58aa428fb9909d6b8587b75eea827287e3515b8506dca86b55e2c7d \
+    --hash=sha256:223427392fdf993e198644ec40c404fd93f1cd2a61328d18842ecbf154d02c82 \
+    --hash=sha256:2529873a3bf68c372532a9f8058bcf4199e78387e92cd6a01b73334bfe6a7e3f \
+    --hash=sha256:2592fb6c335d67f1912bf72788c02fd5dab305fc3c8c7eab078a5bec1aaa0f88 \
+    --hash=sha256:25ebc4208d9098f77caeb16df895a0e56eb6c3b22870ac4e3ec43e0a9d6a33b6 \
+    --hash=sha256:27166b6ec73eac37696d66b2c6efbd44b6d04b597d655070959df54dc7c71c0b \
+    --hash=sha256:27cc258247b13008742f0e239933ad01dec5ed4e6dfc63849e30e04e1aa5bc82 \
+    --hash=sha256:295a15ccb8cfde9351dd6062b80af4e839460636b3c46813b4aa443905ded86a \
+    --hash=sha256:2b4d0c4e13d329ffee73d46128e32dd3b4aeb2f9c6ac9c8a89eb28d3b82dcea8 \
+    --hash=sha256:2bac371da2c3554a99ba126f545e79ab8e8d9426a3e41df81d00ad725c1e2cbf \
+    --hash=sha256:2c4e6a97f79699f33e6dc13bddb5631781ee79a4a94c1822116d100e7d5c136c \
+    --hash=sha256:2d4cfbbb1023f0f6795b5395c400752fb23a5a09ba756aa9003886bbc47b3e12 \
+    --hash=sha256:2e279ad5a6e9347bc9e043fdbee180a0480c8fd52618c3258e983dd93d98ed49 \
+    --hash=sha256:2f3cf710144b1859f4128051cc27ea86eee83caac5648cf2ca0c1b835261cbbe \
+    --hash=sha256:30572b61c7932e4d3c2ad1e580de7db1f35b7a35d36db38f89397ce3f2e69096 \
+    --hash=sha256:335f715f8c111654f29e4bf19086bdf0245579d2b4f4f59ca8dd9b3003b859c1 \
+    --hash=sha256:363e5db93fc3f65f3218a79fe108d217b9d264181a4e993c77552bfe275d0393 \
+    --hash=sha256:36b868758fb11cfa748c788b793994e73660abec90f83c780a678539c2c468bf \
+    --hash=sha256:37b161535e92776788957a165fcf38a80b33c1efde7b18cab287db4e4574df78 \
+    --hash=sha256:3b7542fad2706595c1b1853b46f2c3c4ae5cc5a6252b7225f294d607a29e1bdf \
+    --hash=sha256:3ca4e2e9102d0788b94894a30a5e3561fd4818a0605d8748d8fe780f890aa069 \
+    --hash=sha256:3ca60708f0ca9d994f46790c5a5c774771e2f1dcb75b12c70a5582f915d0e721 \
+    --hash=sha256:3d22ebb716ac79bf32c2a1d15250f017faef719114af4376e8dd814d6633cf0a \
+    --hash=sha256:3d6fce7cc4ef63d9a7633cbae43e737798412805a4c3ba876cdf472dc6ff9c51 \
+    --hash=sha256:4b338b45dc26ca4bac702e1278754f78613d4d0081e14e94e44fe8e261bf1750 \
+    --hash=sha256:4bebc9587cc29359e3b045518a7a09264fa882a7d165b0d143fdac8eeb7ea948 \
+    --hash=sha256:4d61be3725016ef5db3543c95f1f062d7d150ba776582d959a982af88e75fa55 \
+    --hash=sha256:4eb2650aa240b62ab0c6d87238bee5d14aa4d411c0d69ad61be53e026e0785ba \
+    --hash=sha256:4f31ddf9c00e0e7db848b0236c717acbe8a51954d0d31b4d908c538ab3f0f5bc \
+    --hash=sha256:522f7d2351743804cdf5c5a304bc45f9d55e935dd87706fae2dbeafe0fed0b49 \
+    --hash=sha256:5324411117bdb67cfaeb3d1d28fb783710fcca3d88b855696af99044d7219e4b \
+    --hash=sha256:554ee1d2e71fb5b4059c0c4ee35d8cbc8af2a3147036d65a454c53fea07ff4eb \
+    --hash=sha256:57ac987ec5d26d89bbc48c03e486f659e1367d425c465552ac2e4c4af8219def \
+    --hash=sha256:57b5d0df4c60ab8b1159687610a1c3ae069ad2380d390a79dedff5c82318e714 \
+    --hash=sha256:584ebfa26c9dcf3e465637a5a9afa2647bebb3022b50b1ff384834ba8e0380d1 \
+    --hash=sha256:5a7df927c7999d1d3196176a8d4139d3a0e1765936f5de8c768097275b2d617a \
+    --hash=sha256:5b944091cfa7da4f7a9bd2587569cd90c94b89ec4721f8e87fe62504f2432b67 \
+    --hash=sha256:5deadf03fb4a7842696d551f9f9a06dd4445bb43ca06b5f9736e4e1885561333 \
+    --hash=sha256:5efddcdbcb73f5485dca2b6624edc8ee063604b77bd3a3eb772826063965819f \
+    --hash=sha256:65e4448dadc7c94a8643bb41361e45f3a73d46e36a008a9bc03e9b525f4d7c80 \
+    --hash=sha256:66af55b07e4593790157e85f897f06983ded8a8692cb2fb048f3049c1d3fa172 \
+    --hash=sha256:678ac791b5820d9346eb13c8515fe0c9383659335e5cfc544bf6f54714ca1939 \
+    --hash=sha256:68b97b721d95b77d75e718d1b62a227fa4b3e647bd2a9fb39552d1a79ffb67c0 \
+    --hash=sha256:6966806cf917cbbeb9a8b5c581db52e19c9af0ef5fe009db54c1f5799a6e003f \
+    --hash=sha256:69befda4b1ef57027ea95dc6ed733568642f330fb3203a3e5c5ef107d41e0a1f \
+    --hash=sha256:6e22756c6e2d4f57ead0d2e6be179d8a16d661bee424b81de0c6c0c1305ec39f \
+    --hash=sha256:6efdeed2723431999cf3bcbc84c72dbe0f65d16bb1f84e15a657f5b60ff18ca6 \
+    --hash=sha256:714fe5f3eabd153b1b6911d0b5d31cfc2b808ae6b9e59a32fab17a4e6cdad5a6 \
+    --hash=sha256:7238f7135481926d52a94c18a8cca633a9e72c1cbfccd5796548298a479b0656 \
+    --hash=sha256:74d3e015c28b43b6c1a108eec324ea2efb185c359c459216cabd4cb98f7f02f6 \
+    --hash=sha256:76a4f5132b8dc29eb3c768ee9b47e132a1d24fbc2e9259854c01af9beaff1d49 \
+    --hash=sha256:7726c53b1d59eb57b009a9e8759d4f71049ebdacf30642a198a197f80cea451c \
+    --hash=sha256:781ca5dfc2f1d58e47f52216a0c1c7e1ba91ce8aa235459e20de2d402af77fb3 \
+    --hash=sha256:785ef2f3e372dabc131f228a275f97eca92ad17cfab1ab138790e330d99abe3e \
+    --hash=sha256:7cb1a6bb70edcc06ea65cb9a35654f268ee39d9fc3a52240e6ba074db4d9c99e \
+    --hash=sha256:7fb3bc8d58e1b7c1d9fa1d995e30a4ce9dbe49f4c63c755a1ffdecdfbd026ccb \
+    --hash=sha256:8148c2aaaf4b85d7872f024c8bb0c9b9797cc76b10588e3594a69cb01057472a \
+    --hash=sha256:81a5f84a76401c4330e6db4e170dddd58860b30c4e8a44a181e5c2809c7f9c9d \
+    --hash=sha256:81c6fc88ac9bf6920a0cdf22d3c383964167f12d35eb630463fc6d5ac89e460d \
+    --hash=sha256:822a7fcd33f6922b650e1b26594f09d53c5d011fe655fea7ded27b2728ce2a1b \
+    --hash=sha256:83fbd7cfaca614975efdbdcd9e2df45f3e987e819216468fb73e1db6f0365b98 \
+    --hash=sha256:846b17193f1c373d6f05ada894fadf56bce2473067caea0aab51828849894b31 \
+    --hash=sha256:8648dd5dc4d5db32b5936dc5e85e9a4d79db1135513d40d1f54ca15503750324 \
+    --hash=sha256:873d35366cc115be02a1c858f9b22a1a9f6182b99aab2171ee5276af02a153e3 \
+    --hash=sha256:8c3ff4f5c376df7126695a52af61e6084b69c9e52dcb9f4713e71ce9819e1bfd \
+    --hash=sha256:90efd90a0f9b7ae3844a4fb3ae614321832d364ae19567b7cd312315fac4ec39 \
+    --hash=sha256:9306e0c5595f91874e685be0a9eb743d48ba069c888eea051bec3c67c08b5b8d \
+    --hash=sha256:987f65f6c9321402bc7012f6c6d09ba501b88ddb1640f5b0b4a19f2caafe24a5 \
+    --hash=sha256:9a53776adc1ba923c9e345fdea7b61553c44c17a9af5eba8d8def8c5dcac4dec \
+    --hash=sha256:9c44bd978adddf39df5834c6a1efd7d075c84769a7a084168d035a2a276d9008 \
+    --hash=sha256:9c9f285f788acf2448a57c9b93d31103ac69bd03f92907e2ffbb23c4e2b42eb6 \
+    --hash=sha256:9df532dd12c59a7a4d381646fc1bf5ccb4bcdbd01c0887d07ec769fae965ea9a \
+    --hash=sha256:a0f999155c22c8929cc492949c08c6fe7ec8079a5e1bfdeb34b9a3e4991959d0 \
+    --hash=sha256:a2a322c8a6ca82a5a67ae6542e9c6a13ded9045cfd171dcccc5c213ac4fe0eab \
+    --hash=sha256:a3d28ac22fe658ad7486d1532b3a9084fbf65b428db31f47212c5b0b6da826f1 \
+    --hash=sha256:a3d9a59bcdf8531d46b56bcd512017533510c25e955c2c546efd0743bd840940 \
+    --hash=sha256:a789e3d27fc5665cc0477f10a35a89383313e4c9cf8b5e6af7ea71f039cdcc0e \
+    --hash=sha256:a7d120bdde5b213e67ed7dc80ea3adf4f014453fbc20195d619ba2ceb34084f3 \
+    --hash=sha256:a878fef2797a7c082aa47559af68299372edebc7367bd5128dff2d36e6d820e1 \
+    --hash=sha256:a92e3080d8889b0f7a80ea0c4a72181b4d4d5d3918a03136b4a459f51f5f59da \
+    --hash=sha256:a9cc121b5ee2c8b4bd4b6b526d5a26bb782f4d620463f73707691b2004b8c349 \
+    --hash=sha256:b4821bd30b38144d8ab75df56af0b07e9d71327c9cf94c0c7a1965f865bb9615 \
+    --hash=sha256:b5fb6b048931ea925b484f0c7c01b007981415a00a6c62ee74bbf8d229d39c08 \
+    --hash=sha256:b63acdf4df5a78a15223bbb510bb3e0f8234dfa807610ccb8796d0842db2c801 \
+    --hash=sha256:b81ff0f2d375988152614eaea4d5023c98ecb08f77df4bb1d96762504bb86fca \
+    --hash=sha256:b97bffa5772b7e853303de094829fcd3a9bd49fddd70534651ee4933691f6587 \
+    --hash=sha256:ba5e8d9310a794b853fb0e327d46a827b5b015576341219a591f88ed9d799c27 \
+    --hash=sha256:bc9decb36abd00ed5d123db9df70eb9a0da45d6376d86d64f4a94bfd5a1b83fe \
+    --hash=sha256:c10ac5e3e76837180656079008f71add8339b00c3c26314092bcd1e8e449049f \
+    --hash=sha256:c753b820738cddc097892fee95e7cd716fbdfc9640414c5e9ce9463ad125321b \
+    --hash=sha256:c85a0a54a19429a17ef449e967baffe7b5089cb4f6ef2894c9168a69fa024d05 \
+    --hash=sha256:cadd02ca804d6ebe799a7af19197d9730094fe2cc74b70eb4f374f4b8c1886c1 \
+    --hash=sha256:cb43bb34346155d479acdc5423afccdff79ce1fc66adfcc9de995cbec8a13acf \
+    --hash=sha256:cb7fc8820b206932ec6d8f8985aeba6edfd2932e13b6c4bf2434d6bcbbeef3e1 \
+    --hash=sha256:cba29f12cd717f1cbbe220edf005666f8df0453347217748331a0c2f7522eca4 \
+    --hash=sha256:cd69c99affd1b4debc1f9a53058ea6e3a9b34f2e733840bb45891666cd8ede0a \
+    --hash=sha256:ce0f884408938fbd72e764031d0e23a8f5e438a7bf73641089c7a6465cb84456 \
+    --hash=sha256:cecb2c778f00a65c6ca01410dd194d0e797a9eebb7c6dea0db87718719f293c7 \
+    --hash=sha256:cff7657e79224dea46f2f2e58eb99186656ca63ebe356212210c5c00e9beb814 \
+    --hash=sha256:d0381074dc21225951278d7e4a7a2241f7fb86a4d8b94154dfee1411f49cf851 \
+    --hash=sha256:d094951489bb7836342c005e790bd005e60b669aaf5c936b96dd5d68cbd2e23b \
+    --hash=sha256:d10e49b940e70e2a4e91f44098007dda0bacb78c3f8e31ba7a37ee2ce52269e6 \
+    --hash=sha256:d37773029ba034a2cc970b6eeb67dad3bff9d894393c51f6bb1c6b4f563a032c \
+    --hash=sha256:d4af0d863e72f3ea48e85d3aa1d1b426fd81e9544fd7976fc6d6753584a25b03 \
+    --hash=sha256:d5738cd929f2af8651ebb284467acb58b1ec0f2f4d42489cd0597172bc82e15b \
+    --hash=sha256:d615377a8e7bfc4f1983ede3f411c2ac2b0f7c3053f262d0437b7d8bcc4485e3 \
+    --hash=sha256:dbda2baafe08f8431fd3333be02c261023fd454607e3bde5e7dc00565f7bebcb \
+    --hash=sha256:dc6f3dcb08c4b41e64f2d6cf272b5686d9144db585b2e138a8b1664376ab3921 \
+    --hash=sha256:e0f2b33a6ae233f4da38c77ea32f90aab2cb82ba819d7b6c4f1b68cd33d871b6 \
+    --hash=sha256:e47d058c2db95010f5d2e1f6037acebdfb0e2fa4507650e1041437985c91db38 \
+    --hash=sha256:e64b86d16158954825d12799271979c6944c1fd1d03575b2f22e869c3f7d00dc \
+    --hash=sha256:e8af3e6f1bdbc31fd762b094133b478b89988eaebc63cbe82b1d9e3bbd15cede \
+    --hash=sha256:eb5c4a5b1281985271b6c29be53f2c1a9decf11e30a0e2733439c4d9d61b9ebb \
+    --hash=sha256:ec4ee5d2d624088775e61cada87bbe7629bfd936bfbd57f122a106970d8ab1ee \
+    --hash=sha256:ed6c107642a9acaa7ede32dcd428a6c87e302c5d555ecd3ec132ffa8c6155b4b \
+    --hash=sha256:edffdb3950d3a8b769ddaec3a0962fb7b76b3c96f317f6b88500455a537dded2 \
+    --hash=sha256:efe695cc2081633b02fcb95bc1b13070f6647c9ad52d42a8beeb3c2a7ea062dc \
+    --hash=sha256:f07f06db2e333b68dd52560b8b0b12b6f8bf6053cedebf9af4aecfecd2dc1b32 \
+    --hash=sha256:f15205c67d4c45250fcff5da077f0ae54102b5bc39e9ee8bab90d99e09a728c5 \
+    --hash=sha256:f2087ee23a18d1d618a135eedcafba7dfc40c6be4e8e52d7f29a1c8a2344cfcc \
+    --hash=sha256:f278f118f9fdb5faba5a6792be397fbda094d1568efa4dfe8c3595ce4ce89eea \
+    --hash=sha256:f29885fef157a602d1816439e5da964c70ebcdbbcd4bb9d2d21b7e8bb5636604 \
+    --hash=sha256:f2cc27ec6a53b1d39bab44d2b9dd21cc31e796d01b5e18a76d569721282bb264 \
+    --hash=sha256:f332b16911ffc668baec6aaf8f08a09e1af34a8ee87ccac26bd722589e264645 \
+    --hash=sha256:f5812cfcf7daf3ace5fedf6e2ef8d4b342c92fb8ea3a87c1aed2b50453271093 \
+    --hash=sha256:f62172cf387e92f4928b60e5936b02c06e3c8449ed7fb440978d6c9bcbfc85df \
+    --hash=sha256:f9c118e866164ce05498d9106a4bd01e745321403cd6f0b77a0b2587768f8c06 \
+    --hash=sha256:f9e78d98a29e969a001e953eb09167a48bbc71249e804dae5db987ee7e6531c9 \
+    --hash=sha256:fa0ecd064b0ae18d235283abb5adbc4e07304dba8f2aa7c0d61f28bebcc70d4c \
+    --hash=sha256:fa949c81e3865c10f981dea72fd8d418b59edd13a047a0aee89ae64790113d53 \
+    --hash=sha256:fba33e264cdd2ec43b762b9960d1648478eecfc1ce6e8159e7573510f0412c0a \
+    --hash=sha256:fc45ff19520bc5321dcd9c6dd7df6f35ddd894eed35e5be65d1828a9c3f5e7fb \
+    --hash=sha256:fcfebcb537f419e415b6e2bfc77ddbd33abe3c036f0105410a25a14741df9c31 \
+    --hash=sha256:fd24c4425fdb8e822601335602375c6d0cb020f7a368e1d5842eb7925a9c8748
+mypy==2.4.1 \
+    --hash=sha256:01b7718552d017f88d1151f3cc9d6556d778a90bd58060a2c3d87d070f9099fb \
+    --hash=sha256:0724cf95fabc87ca4a2d5b7f276b43f51afce8a3804bde704490b008e377e50b \
+    --hash=sha256:080cf64a60b90a73435542feecf4171904cc5710658165b40c6869115d4aa100 \
+    --hash=sha256:0c5bf267645351887b72903fd2f5fbddcf85234e0e6c4ad94e2fcfb4f0c3f971 \
+    --hash=sha256:0e95ad0bec03ced9a73b42514208abd24c789e67f0e1eba476e276dd7a2dea3a \
+    --hash=sha256:0f0a8b8f5dee799195a3f2670a5b2617ac7193d3563f52dbef42ad6770c6a9db \
+    --hash=sha256:133886ef1a7a8cf673df55d865e41580c6c46aa9b8e31e1325dfe315c038f745 \
+    --hash=sha256:1784648d6ec8c2b5465e3f26241b845a0b3cb4e56c993c64abe16989e7698999 \
+    --hash=sha256:1fb70621535c22fd4b1a0450d37ed1d6c5eb39656a1cebfb189084c12de54ba7 \
+    --hash=sha256:2875280687e64740e6ddcef43bd4c5852ad45ff34549740f6aea3f0373870b93 \
+    --hash=sha256:2b4e0aa029ad0c1d42cc494daf86d1e0efd15dab4db7bd096ece29e8a9689c6a \
+    --hash=sha256:3467b1d13000812ab85dc2a3834b9379ec77798ca1bcabe434e23fb21fead692 \
+    --hash=sha256:3f1613bfe6726169a5680ec3dad5fe1f6d96285c12aded51ad432eadedd39d45 \
+    --hash=sha256:4af5ad558033bf71a44a1be149ed61633522824f84c1b6bc2445d3fe2d2a5296 \
+    --hash=sha256:4c194c5d878130fca1ae662dfb1feb6274afbab0b40032c80147377e0ea803d5 \
+    --hash=sha256:4e18d0da3898b3bcd16192f15a206e7b8b8dd0f4a0b3e51aa5bd5c2afe749e2c \
+    --hash=sha256:51f742d4154824837ca6e92aa81f00eec222700a3c337bd258e5562a3880d75a \
+    --hash=sha256:63b590965691e540a335fa74dadf31a7069142f6b72e234689bbd244edf55623 \
+    --hash=sha256:63c6ff0e7ea546943001a91639c9f0c64b60d239268fa5d29e4a6c87f82c2373 \
+    --hash=sha256:680ba5d9f0e3fe0c746b3d14df15f2a718e4bc308a1145616a1ea691ce7c354b \
+    --hash=sha256:6f7225951a277dd0d6add900731d487174b7d24ac133c09d670ed63b4d8cb90d \
+    --hash=sha256:70196470ac300f444a302a738541101893c2c57804078b33690286a7899149e9 \
+    --hash=sha256:70971cc0bcb1d3f03d2eb68fa430a6481ccc03558dc001d9534d7e5fa274c392 \
+    --hash=sha256:71eda06e5bae51976ce869fda429159c9cec678bd02f25bb197f0265c8f991be \
+    --hash=sha256:727890a32f1858c09549eb55a8b234fe990d460450b28f03e8213ef925f1247c \
+    --hash=sha256:7344869cad05f073b8cae2826774fa0161e3eb2f5c685b76813574008d77d750 \
+    --hash=sha256:79a1e79199e980fb41f219cb3d4746d25c64b0b623840d3ed57df1cdc13a6502 \
+    --hash=sha256:8e437811ebd26d3e6258efb562a711b385c139be597dffed5e735c801d15c77f \
+    --hash=sha256:9d7dafd56179d296651df9e1844b91c9517c379398f017a2a435d077a28943c1 \
+    --hash=sha256:9ed1195502cca32be5ef756b1693477f4991db2f2e34eaa90cc4ad6bea4f9531 \
+    --hash=sha256:a20ff6cd2af7a670c64f089bfa5fbcebe8ff3bf896c5e6ac7c9862c7960e4494 \
+    --hash=sha256:a2d4a51db92059eecc2c33b2a5194b28585ebfd917292c015fe87a77dbff6cd2 \
+    --hash=sha256:a5b5da107dc2c93fb0a22f7a45dbaea5dc131afc7056b5468d78e819f9a138e6 \
+    --hash=sha256:acdd82cb3a2eb10720e87706a128d75785d005a8c47e36a4973221524f41fc56 \
+    --hash=sha256:b69a15fc2e75858d6b15e91ed3a0dcff1a533265183b64734138791fe0f49aa5 \
+    --hash=sha256:be4c03f33c55500191df2ed4a9b5e7edbdd1fff067fe361a5a9b1b5d3262da6e \
+    --hash=sha256:beb254fec368c4e7f7f82a5f310c6470b893ec88a90b66426da971c6826b0453 \
+    --hash=sha256:c3a4d0c47053cc90035dd3a2c321112b593ad42935d0cbfd747288e1564fa8ca \
+    --hash=sha256:c45485061ba08f700acc12cfc8b177e6997e6bc353605babfc0abb081e079456 \
+    --hash=sha256:c535efcb91f7e66f41b9bd2b5dbd78900a7609ce88f4c020d668e4c82d082b0b \
+    --hash=sha256:c6c7210e40dd423af7d65cbe428b5906d11dc60659337bdae4e5fdf02ce32ed7 \
+    --hash=sha256:d4c343b2a720741a016d720b255e75581a50e2bede61d53250484e18562a1d64 \
+    --hash=sha256:d63737426a048a27705a4eedb828669f4bc0873612a1b46b0b9fe892b2ebaaaf \
+    --hash=sha256:d6e081b466e88d4343adffe11aff0f02df34b5b9070b4b700053a0b7294c0be1 \
+    --hash=sha256:d923cec43316f0e6736b8298fd00abeaaf348a091c20e7296b3aebceecb63eca \
+    --hash=sha256:db599d03e7d60d15f2e0a11665c18bc52a88699fcab990fdf8cecd5be8ac801c \
+    --hash=sha256:de95648e0a6d46fa9929b956ed2c87c5dc9933d4d59945e6390e9d753c74e7c1 \
+    --hash=sha256:ea0714d2bccaf6d010c970e1d3ba2c9c2add79d2030aad2ef03167d788948276 \
+    --hash=sha256:ec416d5d2ae689e681f5727e328723f18d8b5dc8c903a146b7851dc5727aad8a \
+    --hash=sha256:ef8d5be90032261197ac388d945d8ff4f476c95880798a1911760af64ddfe71f \
+    --hash=sha256:f44dd4c5ab22df21206dd926c98381ebdbf5bfd696df37dd38ded2d23143fcb6 \
+    --hash=sha256:f9118a3f50de264b614861bb11814833a742138ac3c8e2e49a860b6977fb2704
 mypy-extensions==1.1.0 \
     --hash=sha256:1be4cccdb0f2482337c4743e60421de3a356cd97508abadd57d47403e94f5505 \
     --hash=sha256:52e68efc3284861e772bbcd66823fde5ae21fd2fdb51c62a211403730b916558
-numpy==2.5.3 \
-    --hash=sha256:012e66aca395d795496446e52aeeb5866312a5d4d3f27da270e5a0b43f70dc5c \
-    --hash=sha256:09d5a423c71ad5feb5625844ad58050e35df43871004b52ac9c0ad44a56775be \
-    --hash=sha256:09ffa5d903faeaa5c4dd05009cf81c8bab9f2cb37c548b8d39b65b4cfa7c97f7 \
-    --hash=sha256:0a59a421a32580a009e8a1751345bf829631b990dc1794b80514ab722b435def \
-    --hash=sha256:116f96cadd935c6122e9228d676fe7ede19e741f5c8bb1c3cddbe0c51ccebea2 \
-    --hash=sha256:1302b90c0e52281681b2975adfe8a860cb7b12216a27b4b0b4207c44bf7bccf0 \
-    --hash=sha256:15aa985ac73a8db02db7663381aa109510449d3819d37206caed27b33a65a8a6 \
-    --hash=sha256:1aad64d99730d013cfc6debafed22783b4fc5a7f4b8bc744d2d8cf7dcc880551 \
-    --hash=sha256:1c80eabb4035ecf4ca9cd49cde8a9fdd69a729e63e6474887d1523ade7aa277f \
-    --hash=sha256:1f3ed25271581281f2fccb1adcedfcde4c07362eec69189b50baf6f90e3ae159 \
-    --hash=sha256:1fb6f8fb9ff0b3a69f52c66ce397b0246583e9f28616231b0e32ca49259a5fa6 \
-    --hash=sha256:214045a5bf00113a146ab9ee9730c44501af6723cdf1f6830932f7b5ef2e7af0 \
-    --hash=sha256:26e15e4aecd8617dfbaecb37d223e365d7b39411fba20454be2670a96aa74cb5 \
-    --hash=sha256:2c25dfa72943e4336ddb6b0ee4277b47a0c85bede0807530ec68103bf58e2c10 \
-    --hash=sha256:2d8240cb4c16fd831074aa2b2cf9fc54664d826341d61c372245b96a74a49a9a \
-    --hash=sha256:350ba9783ce969cf9f7ce6e6a9a58e1a6e2a19ca025b7ee448c4db727706212a \
-    --hash=sha256:4c8a6d2ebce6305fd82fbefca827775437147052a976ee7c94b36a0c1b52ac6c \
-    --hash=sha256:4f8929ee6c96bfbd7b4ed2032e0c03af86fe1826740ab61ddabf9072d06e57ff \
-    --hash=sha256:536f963710a4e63934d80ac0dc4f478804a83e9a84b6828018f25d09953ada33 \
-    --hash=sha256:54a115e5a73b8fc44f0cebef486365a1894b5c9760685d4558b72b7c3eb846e0 \
-    --hash=sha256:595d020938c84e320bcf40ad71089e108eac0d377cd018e14a8c094f39e98d85 \
-    --hash=sha256:66a78fe4556c60aceda5916f9eacd638b18e9e681016ec302dcb4682d6d4d034 \
-    --hash=sha256:6b05c171afb3aa07adbd20abc00aea86fe375beb0fdb9ef780ec5b7f63bab1c0 \
-    --hash=sha256:6cef4bb1706dfec49243c05d921eefb4e190d41e2528b30d8035ea1f36b4c24a \
-    --hash=sha256:6f24021b9f22bc6301c37b196974a92c1c18dccedb6fef3dd252e95f2d6adbe4 \
-    --hash=sha256:71b39d9f935b6ec0f8753e3e2afb51e3efba6f2e05b68b32a40754d24bcd4a3c \
-    --hash=sha256:71cad2b2a7451ab79d8f5e71b453485b6775963d5cf794179144a7463fe6e8ec \
-    --hash=sha256:76c2c1e6bfa5c84adc6434dfbf013aa92096a7985221762c8f11fedfd20fff58 \
-    --hash=sha256:8617bbfae4486cf99c9f899966699428d19da931d06ca94ad3da986c76e15997 \
-    --hash=sha256:86bff898a431c0fb71f7610b75726e75a54d47b37edc9d537f48de63bb3c0b90 \
-    --hash=sha256:8e4dd766076855b5ff7ea52fa5f07ce26286726e0f8bff446b7739d02e6ea204 \
-    --hash=sha256:92f30e89b8ee0ecf363033576c422b2f58fed6a80bed0aa48dff6d14c654663e \
-    --hash=sha256:93e1f5447e2b1e479d7bd74701e84746b86450cff1fc368b132d195e2b8f8211 \
-    --hash=sha256:9a37475425b431b4d060f23b4f52cd2f3aef6bc7c654bd760adf0040eec9d435 \
-    --hash=sha256:9deb49575e5b0b94ed72c8a64ec4d033381adc27e9060ae842971f697ba96104 \
-    --hash=sha256:a5fa86b80fd24bcd1aff83ad23be44ea323de3f787be8f8b15d4a65621e25321 \
-    --hash=sha256:a6391fafaba97500887132cd582abc6e19452b1ac775a47caa7b24490e152058 \
-    --hash=sha256:a72f874bc9e10e4b8f80426fb49716d5141f64442a0c8418065093ec8017fbb0 \
-    --hash=sha256:ac7bb1c52d445bd4f8f7f97fefe6abc3a084dc4d63df50d79b17fa2b78e89297 \
-    --hash=sha256:adc1ada2662f8a5f960b8a10d9986897e7499ef07e06d4cfe7197f8cce923c07 \
-    --hash=sha256:b00eefbcf0f292945c4b4dec2ae845389ef5bcdcd596e6e4328051db5b5ba694 \
-    --hash=sha256:b0521d0f4aebb6e06189451025fa17a913287b13c03d5fe05c017333b654ea5b \
-    --hash=sha256:b5d93cf48f687479941d12b69c873ad2cc76bbd487f0091c2200636497f34034 \
-    --hash=sha256:b7e18c623bb5c95acb3b3328861272816ba199fb531921c5d6d0b675f1fde9e3 \
-    --hash=sha256:bd4cb9ad3c7889b9b3fe0a9a9fb5d2ed26f9879bff2608d9f01aed147a20d231 \
-    --hash=sha256:be5a8381859b6da607c84f4f7d6847725f1cf1853ef8a2c9e115b7d58bef47dc \
-    --hash=sha256:befa1ae5bd6030b3f512b43ff3fa5290bbed6b84411a44244b14adf835f5b89d \
-    --hash=sha256:bf63afbe037eb5d2fe87fbcc7778e61da53ebaf21d938a4515aa73b62532a5d4 \
-    --hash=sha256:c00abe94c1a69d75d827dcf1c025b25c8a45d230b3bcd77a9020883a1b047653 \
-    --hash=sha256:c2381f82999704f818e2c987a865050e285ec3621262c66d40f5a96c8f899f8e \
-    --hash=sha256:c76d5dde9f445058f83d0c02af00557a4db91de9a9a57c0df87d1535001d654b \
-    --hash=sha256:cb189f09db39283b26bfd061ec16189e14f71c6755207f72a0f7540867afe5b9 \
-    --hash=sha256:ccb32e0525d29e8b0572eb84c9a57af0e7a4e615726927506f55063c62414034 \
-    --hash=sha256:ccbc4665079665c3cf3bab4db9f6b095370cd6437d66be549b6c2a1fd19e1958 \
-    --hash=sha256:d1c89973648c85069c5046ad460f7b8a00218b29a2e42359ac8cc63e9ab94832 \
-    --hash=sha256:df2d5874ff183595a4ba404edd04f6bd9b5505c1d7708573f6a6c17489a67563 \
-    --hash=sha256:e01c918ac3d48e18a927cf7b14a26a3e29ff2bdf2eacb976da0aecd6a43ed034 \
-    --hash=sha256:e6ab667ba76450084eb64013762c438ea76d9d29cc676dcd6c2e9892ba37f841 \
-    --hash=sha256:e931e4f499e0dc7ef29d269a8e5b35dd722e5d14be07df6240166ea7c6532fae \
-    --hash=sha256:f54660b0eb6b0b9f36e7fe1cdfdff472028dd0d14acd9b9b65098efbad059469 \
-    --hash=sha256:f59a878c33d6b88122d80d239bb3b845d58708750b0cb06a09aebb9b18ec696c \
-    --hash=sha256:f7fabeb6cea87d65f3b926de33d03fb016cfdc29314c90974383b5582ae72891 \
-    --hash=sha256:f9579f383d1bf9df80081e72760e84960a7fd4f88cf0c9e535a8597c9bb646f5 \
-    --hash=sha256:f9a2353b37a1a9e78fd82b27ad7e2a32a2d036604d18f02b05e3136c62ca3b09 \
-    --hash=sha256:fc36dc566135b5eceec4cf89758fcb719266a019ef07dae1754ae7c9f617ef3e \
-    --hash=sha256:ffdc76bfcae6b255dff75202c5e7feaf95b40246bc0a17944facc1fecf9f79ab
+numpy==2.5.4 \
+    --hash=sha256:067374eb538c34c745436365cf7b0112595c1d326f21ce4ff340f61230239fbb \
+    --hash=sha256:0b4724a19de67bea8cfc4970798efa78bcbbe2ac2613cfac16721a42d44de2a5 \
+    --hash=sha256:0f02a46e49cfb6c73bdb7aea1c0d3461dbae9aba613542b65f657cd3d17b9fab \
+    --hash=sha256:1c2e71b04c6cad90026e544501bbe0ab9290fa8a4d845e7e8c0d124fb429c988 \
+    --hash=sha256:1ef3aa6d7e29bb13677323114280b05acc57607fa2300e66432d665d5418a162 \
+    --hash=sha256:2132418bf8dd124a427ca9e6a1daf9ee1a87185344c95119ceae868b99466da1 \
+    --hash=sha256:2199ed071f460487c8db2c0e5c0b564494190edb4772fe80f9aad88b2604def5 \
+    --hash=sha256:2377da2dd3ba2c1200956acbab2a358c83b8e1f8531191672d1cd6ad83250d53 \
+    --hash=sha256:298eca75243f2cbbfdb460560b9fb2a1792a33cf2ab4286efd43d92e8d3df508 \
+    --hash=sha256:2c2c4afffdeb7920e445028dd71eb932cac3e704792e964bc2a232426d4f1255 \
+    --hash=sha256:2ca144f15135b6212a5c47b1e2aeca6e412f102f95a2d5d88d8aec77eb255de3 \
+    --hash=sha256:2fa3328f784fc8277fc48026f6cad516f5c561c5d8e2e39b3c9e0c8f23223b34 \
+    --hash=sha256:325518d4245b9e331387702aa58c2ce1dc4cdcbb41dfb4ccd5dcbc7e08db1266 \
+    --hash=sha256:332f3378fe077dd850e677ec01bdcc4f22368fb5d50ef10b2c79230b1bf5a592 \
+    --hash=sha256:3573cd22564692a5b899ec344e5d5b9cc4576f2985b96f22af3564ed54f2710f \
+    --hash=sha256:381a7a3d2e65e64c0ec302795ab9dc12bb1e73f150904699c153716177eebdaf \
+    --hash=sha256:38f47be9f74ab870d2633b5456ae519c43758a8d1fd05342f0ce4ecc034396ee \
+    --hash=sha256:4054173604cd8658796053f1f3bc0befb68ec1c0762c57fdad61e199256a8617 \
+    --hash=sha256:468397ba3c64427474706e5c9123fe266395496714dc684294eac75cd4930d1e \
+    --hash=sha256:4e263278bfb5ee6409db8aedbc4cc32973b1b82bc1e8d3c668551d04d83a7e37 \
+    --hash=sha256:5258bc06526964be5face2fc6f756857a3f24f21ec3e72ca131337a75b165d6c \
+    --hash=sha256:56733449d2544178beaa4545cee357370440cf056c197f9c7bfb19dbfdd0e86d \
+    --hash=sha256:5ec3753760c1a6d8bb91200666e545c3a9728e6269dfb5d6ce02340996698aa3 \
+    --hash=sha256:5fbf7141bbfd63aea22f435c9062a032b9ea0082fe9845dad7f021d3f1234e71 \
+    --hash=sha256:64d1c8ac28a4077cf987e0a71a7a0ef7e2df70722f07f0baa42dbb7eb6938647 \
+    --hash=sha256:64f9c9878c1938476365e11ccfb6b770f3b9e5f045ccddc514235041e6959365 \
+    --hash=sha256:6c109eac9cd439193678f69d70733c1108487546ca8eafc107b510ae10c1aecd \
+    --hash=sha256:6d6a71b9d9a97c03633aa12565ef2825ffa036cc1d99cfd50dacf0f128af4fe2 \
+    --hash=sha256:6ffa07666f8da0eef81d149934a626d0d95fbd6838432a33e66245423a9062c0 \
+    --hash=sha256:7415db95818b39ec475a5eea54d9e3b6bc83e3912158e46da3438cdce399804d \
+    --hash=sha256:77045a4b175bbf5316ec08003880804336c78f92281a1b72222b274ea85ec5ac \
+    --hash=sha256:7a14a461d9340f1b46b8648578aed9cdb8b3b018a8fac6c1dde2c9192a01a87f \
+    --hash=sha256:80d6ef6e8620eb2c2b4c4caad50b5935d6db3cde2d51581b55dcc79e14016d1d \
+    --hash=sha256:81e3420b27048b65eb14c3acf0c174a8cb0e023277716110347d2dcb26026dad \
+    --hash=sha256:823874a507a84af050493b622affde94b6f7c3a0dc22cb2801381bc03b871c00 \
+    --hash=sha256:8b4d2fd2d34e5f8c9235ee787de5631a37a28402b15cb80814df973d2be54129 \
+    --hash=sha256:8dddfbee2e68d26d0d7d7d9cb247b1fd4409241cce32d815a11d97ec2cfde179 \
+    --hash=sha256:950ea81d57ef070665581b6e1b5f6a029306423cd1739c5b95fe78aa30db6b9d \
+    --hash=sha256:956555e0603a4d38019ae6925711cb9dc43195c076a928accf7ea5d50bddfe53 \
+    --hash=sha256:98b053943e5a0474ec0da309d2cb9d3f18ea57f8a2067c2ab7b5f763d1068380 \
+    --hash=sha256:9968ab7e49b93ac6e1c3b2239732183152c9150f16308d30b66a372cffe3483c \
+    --hash=sha256:9a94cf751c9ad8ebaa835bcd3d40dacf8534ad086b88c38029b65123c7999d2a \
+    --hash=sha256:9cb18a327b49c5c337f972b03682f6a49855525faaf3c0d3e9c96cd0fd8880a8 \
+    --hash=sha256:a7b1b6353e36a7e50de2973a38d705c88ee93adcf120673cee7f45a4a3fa223a \
+    --hash=sha256:a813ed7719bf45463c51779e6a98d0385fe905e48447526938a4b8337333d551 \
+    --hash=sha256:aa1cce2ff3f8d953de38b76bf44602caeb69f101430208f64a10067f7cb4b1d3 \
+    --hash=sha256:ad62a416ddcf863bf44bba76fbf6b53366ab0692e294f51cae4b5fbe0d246788 \
+    --hash=sha256:aec3fc4b32ff82421274f5d205c559c51c840c8df66a78efd7f3612dd005a26a \
+    --hash=sha256:b1185012870173de7ae33d370bd45b1cf5baee747ea4b97036b65f4e93016877 \
+    --hash=sha256:b11e8fda06a7d69f15ebf542660b74466c2e51094800c1fb794f47ad4faeef17 \
+    --hash=sha256:b64a85f40e154983960a4167d4c1d57a50c7f109b3d3264a3a984154e90a8454 \
+    --hash=sha256:b86966fbe4ad7de710422175572bcdc75fdedadfb54bc6fab7deabccddd7780b \
+    --hash=sha256:b89d0aaae2fe498c648f4c4795c084db535af5bd98ef942b2a3681fb74ce8645 \
+    --hash=sha256:bc39ac66a7a9a3fbd6134fda43136b60ffde99c8f4501e64e0d2b24da137babf \
+    --hash=sha256:c05ede731b03fb1b7591faca9389ade3267d2bddf1ad8882bb3f2cc5e101694f \
+    --hash=sha256:c6342f54c67093cae5c0227eb0eb772fdb79f2a2c37a6eb278b9909ee06aa356 \
+    --hash=sha256:c668b2f0d651605b58892644b0e302c7157f7159544227758c896982ef384b18 \
+    --hash=sha256:c9b80cdf5cedba0e90d93fa5f9a333c4d65bd545cd669b71bb97ce2b703c9d73 \
+    --hash=sha256:cfd73180400042a7c532d30c5e287bdd03c59ff9ee1b4c0316af0539e29dfe23 \
+    --hash=sha256:d4cccbbc78717966f764cd3af4fb70276fa01fc7a2688af11c78901fa5c04f05 \
+    --hash=sha256:d549420b8858885cea8838a727842249218b9c1da24dd517e25c9c7a948310a3 \
+    --hash=sha256:d8200f16437b289a5bb927c6e184eccc3e8389bc0070fea4cd5b9e13c1757959 \
+    --hash=sha256:e94aef2c639da4a960ad0db8e06471208d8589974953d78b61d345b4eb99e394 \
+    --hash=sha256:fbde6962867ee75b48b0ee29b2b9372ec5d617799dbaf38e82dc0596f2f7738a \
+    --hash=sha256:fe4d21ab149f15e4e6043dfb0de87e6e5f34ac176cde83060e9802981fca2ac2 \
+    --hash=sha256:ffa6ce09a1c6a08e9667dd9c97aa0b14184e8d18f2a14b78b2a2328c9147f076
 numpy-typing-compat==20260602.2.5 \
     --hash=sha256:1885a678e9a24564839ed5d1711c0031735fb7de7f0b5ed88d550e5d45a8d4f9 \
     --hash=sha256:21ba7757c8924d359a9ed3ab2163c282a70983ae64498fdba6d1892a6641c8b1
-optype==0.18.0 \
-    --hash=sha256:91822ed8516e7a4f225ba53d30f291776c35f31553fb952d7cda98286679c5a6 \
-    --hash=sha256:ea10dee61b15ca299ed0d97025d362585c4dfc5481159bb999a1d0d414bbcb04
-orjson==3.11.9 \
-    --hash=sha256:011382e2a60fda9d46f1cdee31068cfc52ffe952b587d683ec0463002802a0f4 \
-    --hash=sha256:03db380e3780fa0015ed776a90f20e8e20bb11dde13b216ce19e5718e3dfba62 \
-    --hash=sha256:051b102c93b4f634e89f3866b07b9a9a98915ada541f4ec30f177067b2694979 \
-    --hash=sha256:08f4d8ebb44925c794e535b2bebc507cebf32209df81de22ae285fb0d8d66de0 \
-    --hash=sha256:0b34789fa0da61cf7bef0546b09c738fb195331e017e477096d129e9105ab03d \
-    --hash=sha256:0e4eed3b200023042814d2fc8a5d2e880f13b52e1ed2485e83da4f3962f7dc1a \
-    --hash=sha256:115ab5f5f4a0f203cc2a5f0fb09aee503a3f771aa08392949ab5ca230c4fbdbd \
-    --hash=sha256:135869ef917b8704ea0a94e01620e0c05021c15c52036e4663baffe75e72f8ce \
-    --hash=sha256:147302878da387104b66bb4a8b0227d1d487e976ce41a8501916161072ed87b1 \
-    --hash=sha256:14ed654580c1ed2bc217352ec82f91b047aef82951aa71c7f64e0dcb03c0e180 \
-    --hash=sha256:16969c9d369c98eb084889c6e4d2d39b77c7eb38ceccf8da2a9fff62ae908980 \
-    --hash=sha256:19b72ed11572a2ee51a67a903afbe5af504f84ed6f529c0fe44b0ab3fb5cc697 \
-    --hash=sha256:231742b4a11dad8d5380a435962c57e91b7c37b79be858f4ef1c0df1a259897e \
-    --hash=sha256:25e4aed0312d292c09f61af25bba34e0b2c88546041472b09088c39a4d828af1 \
-    --hash=sha256:26a473dbb4162108b27901492546f83c76fdcea3d0eadff00ae7a07e18dcce09 \
-    --hash=sha256:277fefe9d76ee17eb14debf399e3533d4d63b5f677a4d3719eb763536af1f4bd \
-    --hash=sha256:2d057a602cdd19a0ad680417527c45b6961a095081c0f46fe0e03e304aac6470 \
-    --hash=sha256:32ef5f4283a3be81913947d19608eacb7c6608026851123790cd9cc8982af34b \
-    --hash=sha256:33d7d766701847dc6729846362dc27895d2f2d2251264f9d10e7cb9878194877 \
-    --hash=sha256:34fd2317602587321faab75ab76c623a0117e80841a6413654f04e47f339a8fb \
-    --hash=sha256:3513550321f8c8c811a7c3297b8a630e82dc08e4c10216d07703c997776236cd \
-    --hash=sha256:380cdce7ba24989af81d0a7013d0aaec5d0e2a21734c0e2681b1bc4f141957fe \
-    --hash=sha256:3a81d52442a7c99b3662333235b3adf96a1715864658b35bb797212be7bddb97 \
-    --hash=sha256:3ebca4179031ee716ed076ffadc29428e900512f6fccee8614c9983157fcf19c \
-    --hash=sha256:48ee05097750de0ff69ed5b7bbcf0732182fd57a24043dcc2a1da780a5ead3a5 \
-    --hash=sha256:4bab1b2d6141fe7b32ae71dac905666ece4f94936efbfb13d55bb7739a3a6021 \
-    --hash=sha256:4d4e98d6f3b8afed8bc8cd9718ec0cdf46661826beefb53fe8eafb37f2bf0362 \
-    --hash=sha256:4d7fde5501b944f83b3e665e1b31343ff6e154b15560a16b7130ea1e594a4206 \
-    --hash=sha256:4da3c38a2083ca4aaf9c2a36776cce3e9328e6647b10d118948f3cfb4913ffe4 \
-    --hash=sha256:4e39364e726a8fff737309aff059ff67d8a8c8d5b677be7bb49a8b3e84b7e218 \
-    --hash=sha256:4fd66214623f1b17501df9f0543bef0b833979ab5b6ded1e1d123222866aa8c9 \
-    --hash=sha256:4fef17e1f8722c11587a6ef18e35902450221da0028e65dbaaa543619e68e48f \
-    --hash=sha256:53b50b0e14084b8f7e29c5ce84c5af0f1160169b30d8a6914231d97d2fe297d4 \
-    --hash=sha256:57ea77fb70a448ce87d18fca050193202a3da5e54598f6501ca5476fb66cfe02 \
-    --hash=sha256:59e403b1cc5a676da8eaf31f6254801b7341b3e29efa85f92b48d272637e77be \
-    --hash=sha256:5b192c6cf397e4455b11523c5cf2b18ed084c1bbd61b6c0926344d2129481972 \
-    --hash=sha256:5f63aaf97afd9f6dec5b1a68e1b8da12bfccb4cb9a9a65c3e0b6c847849e7586 \
-    --hash=sha256:63e0efbc991250c0b3143488fa57d95affcabbfc63c99c48d625dd37779aafe2 \
-    --hash=sha256:6cc7923789694fd58f001cbcac7e47abc13af4d560ebbfcf3b41a8b1a0748124 \
-    --hash=sha256:71e63adb0e1f1ed5d9e168f50a91ceb93ae6420731d222dc7da5c69409aa47aa \
-    --hash=sha256:71f3db16e69b667b132e0f305a833d5497da302d801508cbb051ed9a9819da47 \
-    --hash=sha256:844417969855fc7a41be124aafe83dc424592a7f77cd4501900c67307122b92c \
-    --hash=sha256:8697ab6a080a5c46edaad50e2bc5bd8c7ca5c66442d24104fa44ec74910a8244 \
-    --hash=sha256:87e4d4ab280b0c87424d47695bec2182caf8cfc17879ea78dab76680194abc13 \
-    --hash=sha256:8aff7da9952a5ad1cef8e68017724d96c7b9a66e99e91d6252e1b133d67a7b10 \
-    --hash=sha256:8ecc30f10465fa1e0ce13fd01d9e22c316e5053a719a8d915d4545a09a5ff677 \
-    --hash=sha256:97d0d932803c1b164fde11cb542a9efcb1e0f63b184537cca65887147906ff48 \
-    --hash=sha256:97db4c94a7db398a5bd636273324f0b3fd58b350bbbac8bb380ceb825a9b40f4 \
-    --hash=sha256:9af678d6488357948f1f84c6cd1c1d397c014e1ae2f98ae082a44eb48f602624 \
-    --hash=sha256:9ef6fe90aadef185c7b128859f40beb24720b4ecea95379fc9000931179c3a49 \
-    --hash=sha256:9f78cf8fec5bd627f4082b8dfeac7871b43d7f3274904492a43dab39f18a19a0 \
-    --hash=sha256:a028425d1b440c5d92a6be1e1a020739dfe67ea87d96c6dbe828c1b30041728b \
-    --hash=sha256:a6082706765a95a6680d812e1daf1c0cfe8adec7831b3ff3b625693f3b461b1c \
-    --hash=sha256:a8f5f8bc7ce7d59f08d9f99fa510c06496164a24cb5f3d34537dbd9ca30132e2 \
-    --hash=sha256:aaea64f3f467d22e70eeed68bdccb3bc4f83f650446c4a03c59f2cba28a108db \
-    --hash=sha256:ace6c58523302d3b97b6ac5c38a5298a54b473762b6be82726b4265c41029f92 \
-    --hash=sha256:b3afcf569c15577a9fe64627292daa3e6b3a70f4fb77a5df246a87ec21681b94 \
-    --hash=sha256:b6ef1979adc4bc243523f1a2ba91418030a8e29b0a99cbe7e0e2d6807d4dce6e \
-    --hash=sha256:be4fa4f0af7fa18951f7ab3fc2148e223af211bf03f59e1c6034ec3f97f21d61 \
-    --hash=sha256:c2d3dc759490128c5c1711a53eeaa8ee1d437fd0038ffd2b6008abf46db3f882 \
-    --hash=sha256:c5d001196b89fa9cf0a4ab79766cd835b991a166e4b621ba95089edc50c429ff \
-    --hash=sha256:cce9127885941bd28f080cecf1f1d288336b7e0d812c345b08be88b572796254 \
-    --hash=sha256:cde1a448023ba7d5bb4c01c5afb48894380b5e4956e0627266526587ef4e535f \
-    --hash=sha256:d4087e5c0209a0a8efe4de3303c234b9c44d1174161dcd851e8eea07c7560b32 \
-    --hash=sha256:d8ea516b3726d190e1b4297e6f4e7a8650347ae053868a18163b4dd3641d1fff \
-    --hash=sha256:e30ab17845bb9fa54ccf67fa4f9f5282652d54faa6d17452f47d0f369d038673 \
-    --hash=sha256:e5c9b8f28e726e97d97696c826bc7bea5d71cecd63576dba92924a32c1961291 \
-    --hash=sha256:ea407d4ccf5891d667d045fecae97a7a1e5e87b3b97f97ae1803c2e741130be0 \
-    --hash=sha256:ea5c46eb2d3af39e806b986f4b09d5c2706a1f5afde3cbf7544ce6616127173c \
-    --hash=sha256:eebdbdeef0094e4f5aefa20dcd4eb2368ab5e7a3b4edea27f1e7b2892e009cf9 \
-    --hash=sha256:f01c4818b3fc9b0da8e096722a84318071eaa118df35f6ed2344da0e73a5444f \
-    --hash=sha256:f36b7f32c7c0db4a719f1fc5824db4a9c6f8bd1a354debb91faf26ebf3a4c71e \
-    --hash=sha256:f5d89a2ed90731df3be64bab0aa44f78bff39fdc9d71c291f4a8023aa46425b7 \
-    --hash=sha256:ffe02797b5e9f3a9d8292ddcd289b474ad13e81ad83cd1891a240811f1d2cb81
+optype==0.19.0 \
+    --hash=sha256:31bff7d2e51e88916a11affed80dbe306ca9e74c76b93b143f1355bb127a7a8c \
+    --hash=sha256:50ce4c0ca419026eeae4130dc90c6a0b9a0b54ffe1d940fc26e8d0058903de4c
+orjson==3.13.0 \
+    --hash=sha256:0526a3456db67b264c6d661b5f090077f326b6cd074d0ef53a72763595dec5d7 \
+    --hash=sha256:08bf722f923d2100bc5e5a5dcf72c656db557049c1bea26582fdd5dd9d5395a1 \
+    --hash=sha256:1807c2fa49d393c7ee95fd1ef1b39cbb24aa3ccd81f30b84503ba59407666960 \
+    --hash=sha256:1d84820b2ec4ac975cba482214032de5b0dbdd17046170c98e642ef9c4a4ee4b \
+    --hash=sha256:2715c4808d1571029ed18fd07a82140bf3ba7def0dc89f8d015c416e3649bf87 \
+    --hash=sha256:3ef75ed7e81dae34a3649f82df52cd85f9ac839a7d6ec78ab355b33b3b27ef7f \
+    --hash=sha256:4329c19b8a25693f60a77b867c9d2a3ab637b20e36f5b7bea7f5acb492b44b15 \
+    --hash=sha256:45e34deb3437509f4ec9888dd9ee5dc426cfe21be10f1eb4ea3a9e4d33034f9e \
+    --hash=sha256:4e5c8175e1574dcbe446ee654275d353c1d78bbd9a0dc9f209bf35c9df72d171 \
+    --hash=sha256:4ee06e53b998c71ce3eb93b86222912fdd9dcced685ac64d4525d36fac338ea4 \
+    --hash=sha256:4f66eac85b072092e9941c3111882afd7527bf926cbc717038fa3654b582002b \
+    --hash=sha256:50a5202ba388b3850ba24437951727d3aa6d79a21964a30ae8dc6a059a5fd34c \
+    --hash=sha256:51d11525bc3ca736fa97ce4e4c7da9999cc00bf261522bede43b4e7531bd7965 \
+    --hash=sha256:554948becd1110123ef9f6a6e1310fd92b2d07d2cbac6dbf65df3de75702e736 \
+    --hash=sha256:58a9619d88f8818d9ab6b39d70d203789457ba13c1ed5d274f33ce9ae7e81a36 \
+    --hash=sha256:5ef4d4157392a0439b74f7e49e5636b4ea43d9616bd0884effc0195fffcaa2d5 \
+    --hash=sha256:637dbca1fccffe83780e806fbc0f17427c0c59bf822528eb0acc8f0aa9f19acb \
+    --hash=sha256:64e8f345048d988c8b68d3882e5d41028fca1219a9939b32e4a77be34c8ae8e3 \
+    --hash=sha256:65c4e0e106ccc7265b488385659117a6805c37d042f737558ecd68aa0c67ad8f \
+    --hash=sha256:6adcaa85d79977659a448b4123a88eb33511a11ed2db243535ad7ea88a6668e0 \
+    --hash=sha256:6c8bfe728b81b0fd58a3c7f3f9c5a113f87f2992c9948e0f28707aafd737c0bc \
+    --hash=sha256:6d0684895b119ad167fb4ec05113639dc7f728022deec4756a710e838ed92e7a \
+    --hash=sha256:6ff2a2c67f35202f7d823753d38ad371a9b7fc297567cdfff4420e763cb9f6f8 \
+    --hash=sha256:7804dd1d6161da0e53b284c2aebf20f23e78eaac617300803e1467d1828d987f \
+    --hash=sha256:78a12d4f8d740cc9ae197f5223682e5e960ba61b4fb2ce5a6a3bb54e83fde28e \
+    --hash=sha256:7991921c5da527a963b6d4cffd0e4ea89c7e71d4be0c8be1bfe6edb223ce7d96 \
+    --hash=sha256:7b3bc6b81835ce65f4729ae401607583d41139c6de95bc7453f450f1391d3e7b \
+    --hash=sha256:83705c12b4afde10c62a5dd3fe6fdb21b7900bd0dcd5af1c85612ae94d0ee590 \
+    --hash=sha256:84d87e322e1674408f85adea63f11aa19201eba082755aec20ebc217f493bbd2 \
+    --hash=sha256:8594956a75223f657e1e68c568c0eeb3dd145f02cd6b78a47fd9a8095dbc4eae \
+    --hash=sha256:89bcf2d4bc6c9a7e1763c8cf534f38712e66b76a0fefda7fb7785462f0d635e4 \
+    --hash=sha256:89efecad02515df7f318d0613b5dfd6d2a1acd323a2b8294712789a715945525 \
+    --hash=sha256:8c2ac5c09b017c484df1b4c68b2cf250b4e8ba08204cb58e7cd6cbbc71a9c902 \
+    --hash=sha256:91d933e668ff0ffe164d7c2daec36beba6d1ce7fadb71538fbe142a71f8a1e6e \
+    --hash=sha256:93c70a5e22bbbbdeafc7b273441e8452a196041d67fd4d9a9c450c66370a8486 \
+    --hash=sha256:948bad47f2e2e43527f14248364a0e5dee26dd3184691010ec4a1ebeb0fd6771 \
+    --hash=sha256:9825b954155b345c4759f24e5f8d652b9aec2261bb5d4e1abe06bba0a1200535 \
+    --hash=sha256:a0377d6962fa431c93ecd78fdea771bb62ec545b24ee0c5d4e32acf2260af259 \
+    --hash=sha256:a79cdc4934fe81f593072c94e13da3095e9d41c2deef8f6ff2901794ca1c5042 \
+    --hash=sha256:a7bfc7db961c7d96cb75889dc6a1e4ae1e91d87ee61da564f582bd742b8dfeef \
+    --hash=sha256:ac81530647c3423107cf61c3481e91f57134e9ddfb6ef83f5150ccbdcbc3a3ee \
+    --hash=sha256:ae1d895cf7bbfd50ef34bb63bb727b14514f259f3e3f8dd010783bd38e864c6e \
+    --hash=sha256:b081f0e7b600ff24513dec4ca75507fa05e904607847e386e8310d5b7b96b6c7 \
+    --hash=sha256:b571236d8393edcd3236e07423f762bfcf571f852aad667a3bce9e7b755e0790 \
+    --hash=sha256:b74c30e56346aad067937d766846ee74c231d1d18aad3f324e9b9261de3b2d5e \
+    --hash=sha256:bceadfd314bd238f584fc229a4bbaf0e573597e7a026dec5429fbf29fd66c641 \
+    --hash=sha256:c5e3ccaac3106e8fa6e2f2f6962449d7c757d7b067e41b395a19d6f0d6cec892 \
+    --hash=sha256:c749ab3ac30b5ab1ffb7677f8b92eacfdfdc5260210baa398f845bc3714c05d8 \
+    --hash=sha256:cbed5f4c4b88d94bcc36115f4c3bb3aa25da1563a5c3328aa3acebce2b083040 \
+    --hash=sha256:d1de5eb04485110c5da4c657e49168995d55e076b1ce60f1a042e254f4186c4f \
+    --hash=sha256:dd61e64802d51d1e4f16531c64536354fc3bc67932dc0cff254044f72bf0f187 \
+    --hash=sha256:dd9d9a101bd8dbfad112170f009cd155e52bb8c936468821a0d03cbb96c0e426 \
+    --hash=sha256:ded33b972cffdaf4ca0ac917338ab61d2bb10d68987dbcae641c313fbfdbf499 \
+    --hash=sha256:e8e05549f3b30f9d8a8e28c5aba11cc2a4b90b90961ec685ca58444b0815fc09 \
+    --hash=sha256:e9b61676116f755126b90e740a9cff36b91562f47ec330056cc88cc3b9f02f4b \
+    --hash=sha256:efa160215c4630836d3b1250af4c7a305acd8239e0d75aff986b8088c2fcacb6 \
+    --hash=sha256:f5c05a8fee59309f537590a1ff12d3c1009c485e96a50a9ac60dd085c09d0fc0 \
+    --hash=sha256:fb8644dc6d705e1269ed2842bf4dbe2b4e50d670de503bf79d5cef3a5148a4c7 \
+    --hash=sha256:fbbad6b9b1da43f25c1f5b20cd5a268e028a2fc95d5a8d1ade6059973bc71584
 packaging==26.3 \
     --hash=sha256:94edc256424af38762eb31306eed28beb9f0efc50a8837492c9d6fd6004aed79 \
     --hash=sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c
@@ -2207,131 +2245,148 @@ pillow==13.0.0 \
     --hash=sha256:fc481f742ccda20e9ed760b8f978dff50f2a4e9bc253ac167fb0a05b0783ef52 \
     --hash=sha256:ff3fe9eb621fbb9db4c4be33ab946f6bac5f98ab50ca8d3260503653656c961b \
     --hash=sha256:ffea6b2986a797c84b6d1d27d4f43e0b83c73fc16281a930891cd237cf0d08fe
-probatio==0.11.4 \
-    --hash=sha256:39edf5370c2ebe4b06bc0d78b53c97fe23c05d5266e599cf40660ce90d88b270 \
-    --hash=sha256:7c407497ff22dd6133321fa3315ed394f564a83d642c1498848993cd87093be3
-propcache==0.5.2 \
-    --hash=sha256:01c4fc7480cd0598bb4b57022df55b9ca296da7fc5a8760bd8451a7e63a7d427 \
-    --hash=sha256:04dc2390d9edbbaef7461f33322555976ffddf0b650a038649d026358714e6c5 \
-    --hash=sha256:06187263ddad280d05b4d8a8b3bb7d164cbebd469236544a42e6d9b28ac6a4fa \
-    --hash=sha256:0958834041a0166d343b8d2cedcd8bcbaeb4fdbe0cf08320c5379f143c3be6e7 \
-    --hash=sha256:099aaf4b4d1a02265b92a977edf00b5c4f63b3b17ac6de39b0d637c9cac0188a \
-    --hash=sha256:0d2c9bf8528f135dbb805ce027567e09164f7efa51a2be07458a2c0420f292d0 \
-    --hash=sha256:0fd59b5af35f74da48d905dcbad55449ba13be91823cb05a9bd590bbf5b61660 \
-    --hash=sha256:10734b5484ea113152ee25a91dccedf81631791805d2c9ccb054958e51842c94 \
-    --hash=sha256:13fef48778b5a2a756523fdb781326b028ca75e32858b04f2cdd19f394564917 \
-    --hash=sha256:178b4a2cdaac1818e2bf1c5a99b94383fa73ea5382e032a48dec07dc5668dc42 \
-    --hash=sha256:196913dea116aeb5a2ba95af4ddcb7ea85559ae07d8eee8751688310d09168c3 \
-    --hash=sha256:1b31822f4474c4036bae62de9402710051d431a606d6a0f907fec79935a071aa \
-    --hash=sha256:1ca071adabaab6e9219924bbe00af821f1ee7de113a9eca1cdc292de3d120f4d \
-    --hash=sha256:1d1ad32d9d4355e2be65574fd0bfd3677e7066b009cd5b9b2dee8aa6a6393b33 \
-    --hash=sha256:1dbcf7675229b35d31abb6547d8ebc8c27a830ac3f9a794edff6254873ec7c0a \
-    --hash=sha256:2293949b855ce597f2826452d17c2d545fb5622379c4ea6fdf525e9b8e8a2511 \
-    --hash=sha256:26a4dca084132874e639895c3135dfad5eb20bae209f62d1aeb31b03e601c3c0 \
-    --hash=sha256:2800a4a8ead6b28cccd1ec54b59346f0def7922ee1c7598e8499c733cfbb7c84 \
-    --hash=sha256:29cbaac5ea0212663e6845e04b5e188d5a6ae6dd919810ac835bf1d3b42c3f4c \
-    --hash=sha256:29f9309a2e42b0d273be006fdb4be2d6c39a47f6f57d8fb1cf9f81481df81b66 \
-    --hash=sha256:2d7aa89ebca5acc98cba9d1472d976e394782f587bad6661003602a619fd1821 \
-    --hash=sha256:2f22cbbac9e26a8e864c0985ff1268d5d939d53d9d9411a9824279097e03a2cb \
-    --hash=sha256:2f8ea531c794b9d6274acd4e8d2c2ebcac590a4361d27482edd3010b79f1325e \
-    --hash=sha256:3115559b8effafd63b142ea5ed53d63a16ea6469cbc63dce4ee194b42db5d853 \
-    --hash=sha256:32775082acd2d807ee3db715c7770d38767b817870acfa08c29e057f3c4d5b56 \
-    --hash=sha256:3430bb2bfe1331885c427745a751e774ee679fd4344f80b97bf879815fe8fa55 \
-    --hash=sha256:3b199b9b2b3d6a7edf3183ba8a9a137a22b97f7df525feb5ae1eccf026d2a9c6 \
-    --hash=sha256:40314bca9ac559716fe374094fc81c11dcc34b64fd6c585360f5775690505704 \
-    --hash=sha256:44e488ef40dbb452700b2b1f8188934121f6648f52c295055662d2191959ff82 \
-    --hash=sha256:452b5065457eb9991ec5eb38ff41d6cd4c991c9ac7c531c4d5849ae473a9a13f \
-    --hash=sha256:45f11346f884bc47444f6e6647131055844134c3175b629f84952e2b5cd62b64 \
-    --hash=sha256:46088abff4cba581dea21ae0467a480526cb25aa5f3c269e909f800328bc3999 \
-    --hash=sha256:4621064bbf28fa77ff64dd5d94367c04684c67d3a5bf1dff25f0cd0d98a38f3b \
-    --hash=sha256:4bc8ff1feffc6a61c7002ffe84634c41b822e104990ae009f44a0834430070bb \
-    --hash=sha256:4db0ba63d693afd40d249bd93f842b5f144f8fcbb83de05660373bcf30517b1d \
-    --hash=sha256:51f96d685ab16e88cab128cd37a52c5da540809c8b879fa047731bfcb4ad35a4 \
-    --hash=sha256:54adaa85a22078d1e306304a40984dc5be99d599bf3dc0a24dc98f7daeab89ab \
-    --hash=sha256:552ffadf6ad409844bc5919c42a0a83d88314cedddaea0e41e80a8b8fffe881f \
-    --hash=sha256:5538d2c13d93e4698af7e092b57bc7298fd35d1d58e656ae18f23ee0d0378e03 \
-    --hash=sha256:5570dbcc97571c15f68068e529c92715a12f8d54030e272d264b377e22bd17a5 \
-    --hash=sha256:5671d09a36b06d0fd4a3da0fccbcae360e9b1570924171a15e9e0997f0249fba \
-    --hash=sha256:583c19759d9eec1e5b69e2fbef36a7d9c326041be9746cb822d335c8cedc2979 \
-    --hash=sha256:5aaa2b923c1944ac8febd6609cb373540a5563e7cbcb0fd770f75dace2eb817b \
-    --hash=sha256:5dbc581d2814337da56222fab8dc5f161cd798a434e49bac27930aaef798e144 \
-    --hash=sha256:5fcb98e7598b1ee0addab320d90f65b530297a867dbfe9de52ea838077e16e3d \
-    --hash=sha256:6041d31504dc1779d700e1edcfb08eea334b357620b06681a4eabb57a74e574e \
-    --hash=sha256:66ea454f095ddf5b6b14f56c064c0941c4788be11e18d2464cf643bf7203ff67 \
-    --hash=sha256:68ce1c44c7a813a7f71ea04315a8c7b330b63db99d059a797a4651bb6f69f117 \
-    --hash=sha256:6a997d0489e9668a384fcfd5061b857aa5361de73191cac204d04b889cfbbafa \
-    --hash=sha256:6bf3be92233808fcd338eba0fb4d0b59ec5772af4f4ecfcec450d1bfc0f8b5eb \
-    --hash=sha256:6de8bd93ddde9b992cf2b2e0d796d501a19026b5b9fd87356d7d0779531a8d96 \
-    --hash=sha256:6e7b8719005dd1175be4ab1cd25e9b98659a5e0347331506ec6760d2773a7fb5 \
-    --hash=sha256:6f328175a2cde1f0ff2c4ed8ce968b9dcfb55f3a7153f39e2957ed994da13476 \
-    --hash=sha256:72d61e16dd78228b58c5d47be830ff3da7e5f139abdf0aef9d86cde1c5cf2191 \
-    --hash=sha256:74b70780220e2dd89175ca24b81b68b67c83db499ae611e7f2313cb329801c78 \
-    --hash=sha256:79aa3ff0a9b566633b642fa9caf7e21ed1c13d6feca718187873f199e1514078 \
-    --hash=sha256:7afa37062e6650640e932e4cc9297d81f9f42d9944029cc386b8247dea4da837 \
-    --hash=sha256:80168e2ebe4d3ec6599d10ad8f520304ae1cad9b6c5a95372aef1b66b7bfb53a \
-    --hash=sha256:806719138ecd720339a12410fb9614ac9b2b2d3a5fdf8235d56981c36f4039ba \
-    --hash=sha256:8114f28879e0904748e831c3a7774261bd9e75f49be089f389a76f959dcd13fe \
-    --hash=sha256:81e3a30b0bb60caa22033dd0f8a3618d1d67356212514f62c57db75cb0ef410c \
-    --hash=sha256:823581fd5cb08b12a48bfa11fe962a7916766b6170c17b028fbdf762b85eb9bf \
-    --hash=sha256:85341b12b9d55bad0bded24cac341bb34289469e03a11f3f583ea1cc1db0326c \
-    --hash=sha256:857187f381f88c8e2fa2fe56ab94879d011b883d5a2ee5a1b60a8cd2a06846d9 \
-    --hash=sha256:8a90efd5777e996e42d568db9ac740b944d691e565cbfd31b2f7832f9184b2b8 \
-    --hash=sha256:8b73ab70f1a3351fbc71f663b3e645af6dd0329100c353081cf69c37433fc6fe \
-    --hash=sha256:8c7972d8f193740d9175f0998ab38717e6cd322d5935c5b0fef8c0d323fd9031 \
-    --hash=sha256:8e778ebd44ef4f66ed60a0416b06b489687db264a9c0b3620362f26489492913 \
-    --hash=sha256:9282fb1a3bccd038da9f768b927b24a0c753e466c086b7c4f3c6982851eefb2d \
-    --hash=sha256:949c91d1a990cf3b2e8188dfcfb25005e0b834a06c63fa4ef9f360878ce21ecf \
-    --hash=sha256:95f1e3f4760d404b13c9976c0229b2b49a3c8e2c62a9ce92efdd2b11ada75e3f \
-    --hash=sha256:97797ebb098e670a2f92dd66f32897e30d7615b14e7f59711de23e30a9072539 \
-    --hash=sha256:a0e399a2eccb91ed18721f86aa85757727400b6865c89e88934781deb9c8498b \
-    --hash=sha256:a473b3440261e0c60706e732b2ed2f517857344fc21bf48fdfe211e2d98eb285 \
-    --hash=sha256:a4840ab0ae0216d952f4b53dc6d0b992bfc2bedbfe360bdd9b548bc184c08959 \
-    --hash=sha256:a592f5f3da71c8691c788c13cb6734b6d17663d2e1cb8caddf0673d01ef8847d \
-    --hash=sha256:a6ae2198be502c10f09b2516e7b5d019816924bc3183a43ce792a7bd6625e6f4 \
-    --hash=sha256:a6ddc6ac9e25de626c1f129c1b467d7ecd33ce2237d3fd0c4e429feef0a7ee1f \
-    --hash=sha256:acd2c8edba48e31e58a363b8cf4e5c7db3b04b3f9e371f601df30d9b0d244836 \
-    --hash=sha256:b05d643f944a8c3c4bd86d65ffd87bf3264b617f87791940302bc474d2ff5274 \
-    --hash=sha256:b96db7141a592cbc968daf1feea83a118e6ab378af4abbc72b248c895414c22d \
-    --hash=sha256:ba338430e87ceb9c8f0cf754de38a9860560261e56c00376debd628698a7364f \
-    --hash=sha256:ba57fffe4ac99c5d30076161b5866336d97600769bad35cc68f7774b15298a4e \
-    --hash=sha256:be1ddfcbb376e3de5d2e2db1d58d6d67463e6b4f9f040c000de8e300295465fe \
-    --hash=sha256:c0cb9ed24c8964e172768d455a38254c2dd8a552905729ce006cad3d3dda59b1 \
-    --hash=sha256:c60462af8e6dc30c35407c7237ea908d777b22862bbee27bc4699c0d8bcdc45a \
-    --hash=sha256:c66afea89b1e43725731d2004732a046fe6fe955d51f952c3e95a7314a284a39 \
-    --hash=sha256:c6844ba6364fb12f403928a82cfd295ab103a2b315c77c747b2dbe4a41894ea7 \
-    --hash=sha256:c80f4ba3e8f00189165999a742ee526ebeccedf6c3f7beb0c7df821e9772435a \
-    --hash=sha256:cafca7e56c12bb02ae16d283742bef25a61122e9dab2b5b3f2ccbe589ce32164 \
-    --hash=sha256:cc1177027eda740fdb152706bd215a3f124e3eea15afc39f2cb9fe351b50619e \
-    --hash=sha256:cc49723e2f60d6b32a0f0b08a3fd6d13203c07f1cd9566cfce0f12a917c967a2 \
-    --hash=sha256:cc6fc3cc62e8501d3ed62894425040d2728ecddb1ed072737a5c70bd537aa9f0 \
-    --hash=sha256:cd416c1de191973c52ff1a12a57446bfc7642797b282d7caf2162d7d1b8aa9a0 \
-    --hash=sha256:cd645f03898405cabe694fb8bc35241e3a9c332ec85627584fe3de201452b335 \
-    --hash=sha256:cef6cea3922890dd6c9654971001fa797b526c16ab5e1e46c05fd6f877be7568 \
-    --hash=sha256:cfa21e036ce1e1db2be04ba3b85d2df1bb1702fa01932d984c5464c665228ff4 \
-    --hash=sha256:d0326e2e5e1f3163fa306c834e48e8d490e5fae607a097a40c0648109b47ba80 \
-    --hash=sha256:d310c013aad2c72f1c3f2f8dd3279d460a858c551f97aeb8c63e4693cca7b4d2 \
-    --hash=sha256:d447bb0b3054be5818458fbb171208b1d9ff11eba14e18ca18b90cbb45767370 \
-    --hash=sha256:d4dc37dec6c6cdad0b57881a5658fd14fbf53e333b1a86cf86559f190e1d9ec4 \
-    --hash=sha256:d5a81be28596d6559f6131ef33e10200de6e17643b3c74ce03f9eb103be6ae8b \
-    --hash=sha256:d9ee8826a7d47863a08ac44e1a5f611a462eefc3a194b492da242128bec75b42 \
-    --hash=sha256:db2b80ea58eab4f86b2beec3cc8b39e8ff9276ac20e96b7cce43c8ae84cd6b5a \
-    --hash=sha256:decfca4c79dd53ebab484b00cc4b6717d8c369f86e74aa4ca395a64ac651495e \
-    --hash=sha256:dfed59d0a5aeb01e242e66ff0300bc4a265a7c05f612d30016f0b60b1017d757 \
-    --hash=sha256:e00820e192c8dbebcafb383ebbf99030895f09905e7a0eb2e0340a0bcc2bc825 \
-    --hash=sha256:e4294d04a94dcab1b3bccd8b66d962dcad411a1d19414b2a41d1445f1de32ad0 \
-    --hash=sha256:e59bc9e66329185b93dab73f210f1a37f81cb40f321501db8017c9aea15dba27 \
-    --hash=sha256:e5cbfac9f61484f7e9f3597775500cd3ebe8274e9b050c38f9525c77c97520bf \
-    --hash=sha256:f064f8d2b59177878b7615df1735cd8fe3462ed6be8c7b217d17a276489c2b7f \
-    --hash=sha256:f156a3529f38063b6dbaf356e15602a7f95f8055b1295a438433a6386f10463d \
-    --hash=sha256:f19bb891234d72535764d703bfed1153cc34f4214d5bd7150aee1eec9e8f4366 \
-    --hash=sha256:f7467da8a9822bf1a55336f877340c5bcbd3c482afc43a99771169f74a26dedc \
-    --hash=sha256:f78abfa8dfc32376fd1aacf597b2f2fbbe0ea751419aee718af5d4f82537ef8c \
-    --hash=sha256:f7eabc04151c78a9f4d5bbb5f1faf571e4defeb4b585e0fe95b60ff2dbe4d3d7 \
-    --hash=sha256:f814362777a9f841adddb200ecdf8f5cb1e5a3c4b7a86378edbd6ccb26edd702 \
-    --hash=sha256:fc299c129490f55f254cd90be0deca4764e36e9a7c08b4aa588479a3bbed3098 \
-    --hash=sha256:fc76378c62a0f04d0cd82fbb1a2cd2d7e28fcb40d5873f28a6c44e388aaa2751 \
-    --hash=sha256:fc88b26f08d634f7bc819a7852e5214f5802641ab8d9fd5326892292eee1993e \
-    --hash=sha256:fe67a3d11cd9b4efabfa45c3d00ffba2b26811442a73a581a94b67c2b5faccf6
+probatio==0.13.0 \
+    --hash=sha256:b592d11c89b536fa42617c3f23fb8798aeb659da2113cc2ec1ff8759f8a34d8a \
+    --hash=sha256:b5941dfdb68d813fbe49551d8802b241c4774f756fe51dfdedbad33e27797373
+propcache==0.5.4 \
+    --hash=sha256:004e685b315646c410771836e72a44f143bbe624f29653a42687815069a303d5 \
+    --hash=sha256:02c0a34f16889cf800f10f0247a564d8ce6eeab6ffcd7c87198f769067eb8432 \
+    --hash=sha256:03969626faf0783a592dfa17e28eac06018bd0b44dafae6943d53b92421a7f72 \
+    --hash=sha256:03b229037d25b801e7af53fd52b9fc49d9439b036fca1e087e02780631adfa97 \
+    --hash=sha256:0951315a6b3142ee2167404d707743f0157c110091342b1aa0accac5cf0e4acf \
+    --hash=sha256:0a095db8e15a6020db149ecbed6461939fe74f6acaa3ae8b702a1fe8c38cd983 \
+    --hash=sha256:0c889f6fa84957bc7e8b4eab71fd16a0455068d5045e3aa40c733071d2b2fd77 \
+    --hash=sha256:0d21d0d2c82bbfeb1677a9711f38df968f9837576102bb4add1bd449d28d88f1 \
+    --hash=sha256:10ef33a68a61ce317e095fd2e202a592ea92392b90944a78c993f0d9a73ab06c \
+    --hash=sha256:12682126712ddc19b70ff819debbd279e58adf1f0c8f8f8138c18ade2044b284 \
+    --hash=sha256:135036c5cfc93864affb0f9af9a27e5d7a71cb7bd745e7b6dbfc2d56cc30e827 \
+    --hash=sha256:13e52b6e0bde97dee98ab66552dbff2931649c96f1ac432eac299fe689ec373b \
+    --hash=sha256:141fdbd73748db0cf7636035030aaac383d2efde8f34e7bc24594cc776d225b8 \
+    --hash=sha256:146f48a9e4812611a7581003b1a39de56c34967046310c4171a68ef908c9a745 \
+    --hash=sha256:174507f82d3594622acb1dd2dafecf2d899d6d506335494e7107767bf05f3aae \
+    --hash=sha256:1783582065a1f07f9d9ee1e992e13f15d7dc8fb1eb3a7476d43eb3f2e69d26bb \
+    --hash=sha256:17a7400cec0256f0a71ae71f9da398f9894c956ff6668a1c9d317b3367316320 \
+    --hash=sha256:1b2f3bec4261a94019575481c726c29850f72e27907773c75b1de421e20e9f9d \
+    --hash=sha256:1d759d05634f1b038fb625a66662a8c85e5a8fec912da381b5149ddac107482b \
+    --hash=sha256:1df8d8561b21465c5dd56110a01caf897e026d065b4b84e98a488209094272ec \
+    --hash=sha256:213bb68d9ced5cf2bf717b1071bf2b09b4b04c426256f9fe6d054c60318424c4 \
+    --hash=sha256:23278f808cd81d5ada7184a76606b925fb3389c60e1077b2cd7da7b1fcf0553c \
+    --hash=sha256:251c63dd46a0659bb875cb254dc4c1e79ee91a847c737cd62373295afc2235dc \
+    --hash=sha256:279655a16973f1ee2bd2fe79973137681642fd9ae0d89215bba263726eb0dc3a \
+    --hash=sha256:2814ecd8e818f487bee4b0f921bc4d1c176cc5fc71ac0f072d0fa67eda4ac14b \
+    --hash=sha256:286867fb156488c251a3721766e380ac4495e4fd6b51aaa1403d89ce7f4359d9 \
+    --hash=sha256:2dba2f02d2d5c09ef8a0e6c1a42aeaa451f4be9898cb00b04fe98717da2eb23b \
+    --hash=sha256:30cc1cebaf9aef49db06357a50398323ae04d70460c0491837d026ab7d6452ea \
+    --hash=sha256:31eb43ba2edc704ab2ec27815315dd8a19def0fb16215be4cfe8d32fe78ffd51 \
+    --hash=sha256:350b272b2279f4135a64fc0c304a5d08e28a137c9573442c606152446638a831 \
+    --hash=sha256:36c0d9db44b523ef93d03341b1c42d69ff01d673c053d1b1c6c3a363bcaa39ba \
+    --hash=sha256:3af0c8642b2da4815d86e631232ac8286e17644fad907c19508aa8e7cb4ba8ad \
+    --hash=sha256:3cd3a7edb6b95b9b33998135ebfa18d709da82290fb8f27c858970b5a12c8b56 \
+    --hash=sha256:3d605bb239b796e82a81c6709548b2bd460ab73b4590cb0c83de8a2dd9694d0f \
+    --hash=sha256:3e413d7a4a9b4866b7a761d6060d434b64d23cd35122eda3b026a0bbe8196b25 \
+    --hash=sha256:3eb2e820e8e2101407da93f17c57cbb7d225461955fc60105daaba14cd421ee2 \
+    --hash=sha256:3fa15757fea1dfcd5b7745cad9f4638929605531bd4018ab2adff7955f1a403d \
+    --hash=sha256:3fc24f209c1b7f7f688b66b98293954f5504279760999b58920ee12dd8471c1d \
+    --hash=sha256:4054acf80d40456a0537f2913b349718649d8d6458a14ab7f48d0ce28c30869d \
+    --hash=sha256:40e94adb1e7d39ff28a8bd8d8b8fbd1df6b9f40976dbe379134f1ce058e532dd \
+    --hash=sha256:420162a77f94eb1cf5ef7893f500016dabd548e73de956785a1dd899cc73006a \
+    --hash=sha256:425f8cc86ab5018b4b8d4a23bc8e74d964bd3d757c3702e301aa79be76c53f6c \
+    --hash=sha256:44149f46500a0a41b95b4d99c2e586a77319539730607b9892974a092788b111 \
+    --hash=sha256:445ee3bfb46e85838387fb3c536a73cc0b994dc192b004e40e170adc54aa2a7e \
+    --hash=sha256:45488d1a5f9ab5bd90aaa1ca20f50fe1922b8ffad71a2009d2adf41355897aac \
+    --hash=sha256:45bebbe252550fec975ba3b62bc6f931643cfd3b5464ef47619cf3fef154e01c \
+    --hash=sha256:45bf2e730ab8905d0527fe05a86500f406e64305c34cc81ebe64b4617cab9760 \
+    --hash=sha256:48cb48c5346a97de792254af77715aa2529c2a1ebc5f586aa0aae44a02f1fe57 \
+    --hash=sha256:4a1f4f5ffa55dce6307631f3cb2948e117e665966ea512e0d502b16c24f567e7 \
+    --hash=sha256:4cfe0a92ae30151869e67a4b5f5e105e4e03ad30b3f38e5211b5bf77d0881993 \
+    --hash=sha256:4d86476a935c88963d9b8e1a9a0d38188790e9622169bfbafa173046846709d3 \
+    --hash=sha256:4e985382be6d15da8d0c2710a6fa7b9070fc9ecdeefb7f580e88373984ec8be3 \
+    --hash=sha256:4f2d880ff60f45898f4acfa152aac8d04e3ee627d90ff4003491bf92239d5757 \
+    --hash=sha256:4fbc1a15dc8cd1689508758d626b372b1f09d28d9577667feaf9e6bfcd8efcbc \
+    --hash=sha256:50e337653721d20ead710da33bf44487fbe8a0db8782714b60306481e9f95b51 \
+    --hash=sha256:53eaa697c4d0422ff4cb714d00231b43352064d97b944033b30c1d57cc506ec0 \
+    --hash=sha256:56fc3f7599528db40b1efa0889a620116e2704144495273d66066e8164e45838 \
+    --hash=sha256:58134228927cee6c047d626c08e60a81be604a20578a12ce752cc5c9a84d4826 \
+    --hash=sha256:594eb4c6ec35e7179b058481f4e9f02521b56de16fa577c4b85c76fb1bf8a9f8 \
+    --hash=sha256:5cacf3c9efd09df409dc33654dd077e1c245ba8fb747b0f0236ef41b7c49b589 \
+    --hash=sha256:60a64cbccaa11b7760ce705a14ada17ba459e7ca9f23ba587eb013821032d7ef \
+    --hash=sha256:62530ca89187827e4a4fe733f971abe81a7542eeea48ff61995f19b64d7199c8 \
+    --hash=sha256:62c60aec739ed00124573cce1178138fd690c7676352d67a37328c1cf51d7468 \
+    --hash=sha256:69fc35c0779522da366c563e5faf203ffc1f8ff0021d5b1337fa4efa5be73177 \
+    --hash=sha256:6af4693716bfb03f1752ef1b30faa593db2c01d5272e9b8564a1549452a979ab \
+    --hash=sha256:6c7599df2b57ebeea8de011b5f2f7b85de95e76037d43d34b95e328430275487 \
+    --hash=sha256:6e9368e87a3efc285e559131092c5db643eb8e56de4ee42064d5baec22ef2bb5 \
+    --hash=sha256:6f0093ac3e9daada202c2082439d414a625c57184727a46e112a3fb2a81cb788 \
+    --hash=sha256:7177c43eddf10a0893c4fec52ebb408fdcd7f7d63962caace9180d8f81b14ece \
+    --hash=sha256:720cf832eb2d0b0dfee129cb3335a26f6ce3cc45ee1187e8f0731758caa16792 \
+    --hash=sha256:770e8209d018175fc0063936fa9583b6d27e88c5ad31543f3383d66080efdd62 \
+    --hash=sha256:7a8d5ff04eb1f85698a78d20c62a14676e7b960dcafde09a388d60ad377d355d \
+    --hash=sha256:7b9100a93b372418d8688f3f2a3e5b45c64d70ca4d6176e121aca1e3bfc1e32f \
+    --hash=sha256:7cc528e760a8af06f2b13e9b9f362cd90c7c718ea61228a96dbd31ba16ed7f47 \
+    --hash=sha256:7ffafcbfc7b549ab940047e505c831eabac5e67de53e1bc174adbc5285c55944 \
+    --hash=sha256:87a3caecf8095e48dc72f84bfa42e23a848cf410cc9cc13031fba4869b706a21 \
+    --hash=sha256:886b59c4d28ca97dd23b025fdfc50a0356be934efbbbca89ad26230067f86fe5 \
+    --hash=sha256:8876b39961e33d912afe3c1bee18ee564fdad0206f873cc15d522756b7f50737 \
+    --hash=sha256:897d1ddf6716e8f47200f7aad9a0efa6cc7586df66c6defa572f9eab379c078e \
+    --hash=sha256:8a1fc236528c457cd739c88abe823da851b7ab645d72792f88658114cc340c12 \
+    --hash=sha256:8a235f73d6e020855dc29dff012d920c02ee0feab8d73a24185a7569f4be1161 \
+    --hash=sha256:8f911c395cef73c510bac566da9507bb6a43e7763d0c79138dc60ee53f11207e \
+    --hash=sha256:96f7c5c15656040ddcbc51e56dc59b58aa25999d743c126abd425b9766ab43e9 \
+    --hash=sha256:978f28401afbc76cdc3df9e1717b4229a06b626a1dcc75db4e1f2beb3884c3e9 \
+    --hash=sha256:98914de2c4d7f0f9f4a8c6ea4bf05841f4175796941e3ef7d47eb718f22311fb \
+    --hash=sha256:9a2a8a50a93dee0268a860a07fa3b4bd968f8ce4dbd794957da772f395368526 \
+    --hash=sha256:9cbfff4423eef4cc6cafc021469641a2b835f610b2647a6c5281903e21b8670d \
+    --hash=sha256:9e9ab13760aa8b6d0881ae7cb04fd891d8d490cd2554ea8e79bb278399169bcc \
+    --hash=sha256:9f3551b8a35c1df3e7ea4d2d86edee15f0dde1bddd434a71744048683544d0ef \
+    --hash=sha256:9f86f7259efe2c951f43e57d471c9b41daa5bfc7db9f67189059cf1ae6d77fd9 \
+    --hash=sha256:9fb0a5be8d9aa213150e8d8148a42aca4984b285bcad1e69587dc4298edd929b \
+    --hash=sha256:a219f0ac59817a9114dd2aa57c13180f993e819ba658c7ddab4b66ed1ee0d370 \
+    --hash=sha256:a419ee85e654927baabda3929c03c0cc1112bf472ff0dfd6142f4e3a81ca4162 \
+    --hash=sha256:a4d7a54719b67338a305dca2ce6aafe366817df94ddfd4b5514374356f5ca546 \
+    --hash=sha256:a5793c7698a53f56f4a1889a4737c7eeb1b7ad0842fa6b1abca22913ff79c8c1 \
+    --hash=sha256:a5e8ef588c109725dc713ba69aadcac00a1ef90c2ce9c0a8c7075128f569f47f \
+    --hash=sha256:a74bfa37147cc08fb29df10bd9c16f40fa7f860cd3a6d2fff853323a94f6e17f \
+    --hash=sha256:ada748108a43d29b7c328ba7db3755327cd94f028bcc1a7ee3f0addcfacd9c38 \
+    --hash=sha256:ae58f361bd5dae942717c65d3413b478c70aea9c462599e7b9adad3731db3894 \
+    --hash=sha256:b28f41fa3b8c6900457f858ec5b03998f3a6d535fbc1bb2edec5961ea05ec429 \
+    --hash=sha256:b3083bfe87f95c756e610bd8025f26cbd1cd4aaa03a422f2d65efb7a97cd53d8 \
+    --hash=sha256:b61805357d966680acf68b3b6d49772631ed9df44ebece10ff1460e117a7da8a \
+    --hash=sha256:b77c313314524ca9c38fbd70f73515d04597ac58c40c939bc0e71eeb4abff680 \
+    --hash=sha256:bee7d3aed13d56f54e681df38c3a23031bc9e3863f687d9d598825c9146acd7d \
+    --hash=sha256:c02c0e570c5c7e077b0181a9f3cdb7d4c3617d1cda6b5c95bd5d34022923d82c \
+    --hash=sha256:c174bfd1c48a1b51a3078e95586dde718374bac79719ab3541ec9e74aec40574 \
+    --hash=sha256:c2ba30a89035b57b73e00475de948521602f543d79ce01db10b04b36c4c76fc8 \
+    --hash=sha256:c3e98c55bde2bcf7db3c70d1aed7ae9aa8aebbf19a250c66645cde44cdb8b867 \
+    --hash=sha256:c3ef2818d63bc86071e9d2989ae75a1bc32b8f7059cfd9f5abbbee70c32e2ed6 \
+    --hash=sha256:c83acbce9f2b5e3f5f5eda9e53d2001fed22fcdfef81274a9e02d8fd53b70a30 \
+    --hash=sha256:c9281e922c072158c91974d4589f1dbe0fee6d467f284c28e463f9f5a4d933f4 \
+    --hash=sha256:cc07876cfb079b6f6f36d21ce75784ad6c2c6b563eeac0ed26c2fa2669b85df9 \
+    --hash=sha256:ccf4f7a79e26bb7efb06ecd50c177833b71df05cbc748701372325e6bcc17f6f \
+    --hash=sha256:cdee8205a44d0be91bbac4c41b95d86641b72dfc7aef1279400e4fda3f26a937 \
+    --hash=sha256:ceb3e879afac028f93d272c957814695dc5569e4904262dbee92f6c41bd5e4a3 \
+    --hash=sha256:d1f5a500bfcbb2c0ab85e98a0dcd70f5899d34efe365a0187700369a79603031 \
+    --hash=sha256:d42a9a856a4a6e2f6c10f1318c07e7daa498d6593abe745c71dae4521a26ca39 \
+    --hash=sha256:d83b12902eb8bce151259c86c03ba746600b2d994543de46e370cecf96c452f2 \
+    --hash=sha256:d8e017eeb7482bed34cdb0d61cf2bcfc88d104bbab296a17cd16a6af8aabc70e \
+    --hash=sha256:db3ae52ccc150dbc84704e9d642743897f3e1c54742ff34cacb661e52e3818a9 \
+    --hash=sha256:dbab5f5ff6897c81f355d079010cdae85b02e5a0b518b5251523b8ad8ae9ac3c \
+    --hash=sha256:dc4242ca653c9b30ab51c5f8193323e7bc0928f897ee9103201e59a43abcb72e \
+    --hash=sha256:dcbf346a318a5e30063f547630b02bb787ce2f45b6368d5da143660b6a3835d8 \
+    --hash=sha256:dd2ac8f5b643454c2cc6b6118b13da16e88f4a6434fc3ba61aca384029f04f36 \
+    --hash=sha256:e1d52a05dc417279f7e5c7618c5dfbbc29923aaf9bc0a5c1802ddcebf54c61a0 \
+    --hash=sha256:e6720ba44ad7e72174314d0e1fb0172494cff5c73a3a8a2159c3d2402ff15565 \
+    --hash=sha256:e738ab81179510ce79b2eac9a6ecf47feffd9e76d1c72e403005dddb6e36c06c \
+    --hash=sha256:e904d4d01f36bd6e197590be1533c44e06058771e0746dd073a8ebb3ef880858 \
+    --hash=sha256:e9f165403b81fea7e89c932d89046a1e3d9a3a60e8d7ef2f249dccdcb0982bf5 \
+    --hash=sha256:ec6a85f424afa8d23e0d9a094e5dbb6eda01da91c92b9183cd433768247ffc97 \
+    --hash=sha256:ee19113bce2f3acd46432050688b70f61acd6857d75abb9ec96341b7e9ced123 \
+    --hash=sha256:ef3b928d9c984322b5c44e6964d8dbc653da87d2d8ee1647fa6da43072e650a9 \
+    --hash=sha256:f273dcf7149a50527c4fd1f55cfe9eac0f60753f5af544b4c9352578e20c0874 \
+    --hash=sha256:f5470694918830da62fac9e69133b53d23b736d7070e587b27a4a2be37e08e68 \
+    --hash=sha256:f574e460d1c8a08384a016fdb09ccf3543433263ed6b2f97104f979e64ea57c2 \
+    --hash=sha256:f85915e00dcb1cd9f2f890ead064ed40a27df06f0db65be427b29482ae357572 \
+    --hash=sha256:fc2461ecc45f17893f8207e73b46ea8ba93e33630e51cf4af3fbc21d47462b1a \
+    --hash=sha256:ff6b113f50bc066a698db5d944d2c6dc7507168dd3341e255a8892fd0715a558
 psutil==7.2.2 \
     --hash=sha256:0746f5f8d406af344fd547f1c8daa5f5c33dbc293bb8d6a16d80b4bb88f59372 \
     --hash=sha256:076a2d2f923fd4821644f5ba89f059523da90dc9014e85f8e45a5774ca5bc6f9 \
@@ -2357,101 +2412,115 @@ psutil==7.2.2 \
 psutil-home-assistant==0.0.1 \
     --hash=sha256:35a782e93e23db845fc4a57b05df9c52c2d5c24f5b233bd63b01bae4efae3c41 \
     --hash=sha256:ebe4f3a98d76d93a3140da2823e9ef59ca50a59761fdc453b30b4407c4c1bdb8
-pycares==5.0.1 \
-    --hash=sha256:07260c6c0eff8aa809d6cd64010303098c7d0fe79176aba207d747c9ffc7a95a \
-    --hash=sha256:07711acb0ef75758f081fb7436acaccc91e8afd5ae34fd35d4edc44297e81f27 \
-    --hash=sha256:09ef90da8da3026fcba4ed223bd71e8057608d5b3fec4f5990b52ae1e8c855cc \
-    --hash=sha256:0e99af0a1ce015ab6cc6bd85ce158d95ed89fb3b654515f1d0989d1afcf11026 \
-    --hash=sha256:145d8a20f7fd1d58a2e49b7ef4309ec9bdcab479ac65c2e49480e20d3f890c23 \
-    --hash=sha256:153239d8c51f9e051d37867287ee1b283a201076e4cd9f4624ead30c86dfd5c9 \
-    --hash=sha256:171182baa32951fffd1568ba9b934a76f36ed86c6248855ec6f82bbb3954d604 \
-    --hash=sha256:206ce9f3cb9d51f5065c81b23c22996230fbc2cf58ae22834c623631b2b473aa \
-    --hash=sha256:252d4e5a52a68f825eaa90e16b595f9baee22c760f51e286ab612c6829b96de3 \
-    --hash=sha256:258c38aaa82ad1d565b4591cdb93d2c191be8e0a2c70926999c8e0b717a01f2a \
-    --hash=sha256:2a511c9f3b11b7ce9f159c956ea1b8f2de7f419d7ca9fa24528d582cb015dbf9 \
-    --hash=sha256:2ee551be4f3f3ac814ac8547586c464c9035e914f5122a534d25de147fa745e1 \
-    --hash=sha256:30e5db1ae85cffb031dd8bc1b37903cd74c6d37eb737643bbca3ff2cd4bc6ae2 \
-    --hash=sha256:35dd5858ee1246bd092a212b5e85a8ef70853f7cfaf16b99569bf4af3ae4695d \
-    --hash=sha256:36b9ff18ef231277f99a846feade50b417187a96f742689a9d08b9594e386de4 \
-    --hash=sha256:3c4dfc80cc8b43dc79e02a15486c58eead5cae0a40906d6be64e2522285b5b39 \
-    --hash=sha256:3f323b0ddfd2c7896af6fba4f8851d34d3d13387566aa573d93330fb01cb1038 \
-    --hash=sha256:433b9a4b5a7e10ef8aef0b957e6cd0bfc1bb5bc730d2729f04e93c91c25979c0 \
-    --hash=sha256:45fb3b07231120e8cb5b75be7f15f16115003e9251991dc37a3e5c63733d63b5 \
-    --hash=sha256:48ac858124728b8bac0591aa8361c683064fefe35794c29b3a954818c59f1e9b \
-    --hash=sha256:4b9c4c8bb69bab863f677fa166653bb872bfa5d5a742f1f30bebc2d53b6e71db \
-    --hash=sha256:4d1713e602ab09882c3e65499b2cc763bff0371117327cad704cf524268c2604 \
-    --hash=sha256:4e1630844c695fc41e760d653d775d03c61bf8c5ac259e90784f7f270e8c440c \
-    --hash=sha256:5003cbbae0a943f49089cc149996c3d078cef482971d834535032d53558f4d48 \
-    --hash=sha256:50e21f27a91be122e066ddd78c2d0d2769e547561481d8342a9d652a345b89f7 \
-    --hash=sha256:52901b7a15a3b99631021a90fa3d1451d42b47b977208928012bf8238f70ba13 \
-    --hash=sha256:534dd25083e7ba4c65fedbc94126bada53fe8de4466d9ca29b7aa2ab4eec36b4 \
-    --hash=sha256:57f6fd696213329d9a69b9664a68b1ff2a71ccbdc1fc928a42c9a92858c1ec5d \
-    --hash=sha256:58634f83992c81f438987b572d371825dae187d3a09d6e213edbe71fbb4ba18c \
-    --hash=sha256:5a3c249c830432631439815f9a818463416f2a8cbdb1e988e78757de9ae75081 \
-    --hash=sha256:5c63fb2498b05e9f5670a1bf3b900c5d09343b3b6d5001a9714d593f9eb54de1 \
-    --hash=sha256:5de9e7ce52d638d78723c24704eb032e60b96fbb6fe90c6b3110882987251377 \
-    --hash=sha256:5e40ea4a0ef0c01a02ef7f7390a58c62d237d5ad48d36bc3245e9c2ac181cc22 \
-    --hash=sha256:602f3eac4b880a2527d21f52b2319cb10fde9225d103d338c4d0b2b07f136849 \
-    --hash=sha256:71316f7a87c15a8d32127ff01374dc2c969c37410693cc0cf6532590b7f18e7a \
-    --hash=sha256:7d1b2c6b152c65f14d0e12d741fabb78a487f0f0d22773eede8d8cfc97af612b \
-    --hash=sha256:7d7c4f5d8b88b586ef2288142b806250020e6490b9f2bd8fd5f634a78fd20fcf \
-    --hash=sha256:82bd37fec2a3fa62add30d4a3854720f7b051386e2f18e6e8f4ee94b89b5a7b0 \
-    --hash=sha256:83115177cc0f1c8e6fbeb4e483d676f91d0ce90aad2933d5f0c87feccdc05688 \
-    --hash=sha256:83da4b2e30bb80a424337376af0bce1216d787821b71c74d2f2bf3d40ea0bcf9 \
-    --hash=sha256:8848bbea6b5c2a0f7c9d0231ee455c3ce976c5c85904e014b2e9aa636a34140e \
-    --hash=sha256:89fbb801bd7328d38025ab3576eee697cf9eca1f45774a0353b6a68a867e5516 \
-    --hash=sha256:8c1aa549b8c2f2e224215c793d660270778dcba9abc3b85abbc7c41eabe4f1e5 \
-    --hash=sha256:8c8ffcc9a48cfc296fe1aefc07d2c8e29a7f97e4bb366ce17effea6a38825f70 \
-    --hash=sha256:8dc84c0bce595c572971c1a9c7a3b417465572382968faac9bfddebd60e946b4 \
-    --hash=sha256:94cb140b78bde232f6eb64c95cdac08dac9ae1829bfee1c436932eea10aabd39 \
-    --hash=sha256:9528dc11749e5e098c996475b60f879e1db5a6cb3dd0cdc747530620bb1a8941 \
-    --hash=sha256:954a379055d6c66b2e878b52235b382168d1a3230793ff44454019394aecac5e \
-    --hash=sha256:965ec648814829788233155ef3f6d4d7e7d6183460d10f9c71859c504f8f488b \
-    --hash=sha256:97ceda969f5a5d5c6b15558b658c29e4301b3a2c4615523797b5f9d4ac74772e \
-    --hash=sha256:9d0878edabfbecb48a29e8769284003d8dbc05936122fe361849cd5fa52722e0 \
-    --hash=sha256:9de80997de7538619b7dd28ec4371e5172e3f9480e4fc648726d3d5ba661ca05 \
-    --hash=sha256:a1c3736deef003f0c57bc4e7f94d54270d0824350a8f5ceaba3a20b2ce8fb427 \
-    --hash=sha256:a2117dffbb78615bfdb41ad77b17038689e4e01c66f153649e80d268c6228b4f \
-    --hash=sha256:a7d197835cdb4b202a3b12562b32799e27bb132262d4aa1ac3ee9d440e8ec22c \
-    --hash=sha256:adc592534a10fe24fd1a801173c46769f75b97c440c9162f5d402ee1ba3eaf51 \
-    --hash=sha256:ae9ec2aa3553d33e6220aeb1a05f4853fb83fce4cec3e0dea2dc970338ea47dc \
-    --hash=sha256:b8efc38c2703e3530b823a4165a7b28d7ce0fdcf41960fb7a4ca834a0f8cfe79 \
-    --hash=sha256:bdc6bcafb72a97b3cdd529fc87210e59e67feb647a7e138110656023599b84da \
-    --hash=sha256:c257c6e7bf310cdb5823aa9d9a28f1e370fed8c653a968d38a954a8f8e0375ce \
-    --hash=sha256:c29ca77ff9712e20787201ca8e76ad89384771c0e058a0a4f3dc05afbc4b32de \
-    --hash=sha256:cc0cdeadb2892e7f0ab30b6a288a357441c21dcff2ce16e91fccbc9fae9d1e2a \
-    --hash=sha256:ccc1b2df8a09ca20eefbe20b9f7a484d376525c0fb173cfadd692320013c6bc5 \
-    --hash=sha256:ce193ebd54f4c74538b751ebb0923a9208c234ff180589d4d3cec134c001840e \
-    --hash=sha256:cf2699883b88713670d3f9c0a1e44ac24c70aeace9f8c6aa7f0b9f222d5b08a5 \
-    --hash=sha256:d3eb5e6ba290efd8b543a2cb77ad938c3494250e6e0302ee2aa55c06bbe153cd \
-    --hash=sha256:d765afb52d579879f5c4f005763827d3b1eb86b23139e9614e6089c9f98db017 \
-    --hash=sha256:db7c9c9f16e8311998667a7488e817f8cbeedec2447bac827c71804663f1437e \
-    --hash=sha256:dedd6d41bd09dbed7eeea84a30b4b6fd1cacf9523a3047e088b5e692cff13d84 \
-    --hash=sha256:e0a86eff6bf9e91d5dd8876b1b82ee45704f46b1104c24291d3dea2c1fc8ebcb \
-    --hash=sha256:e330e3561be259ad7a1b7b0ce282c872938625f76587fae7ac8d6bc5af1d0c3d \
-    --hash=sha256:e380bf6eff42c260f829a0a14547e13375e949053a966c23ca204a13647ef265 \
-    --hash=sha256:e63328df86d37150ce697fb5d9313d1d468dd4dddee1d09342cb2ed241ce6ad9 \
-    --hash=sha256:ea0d57ba5add4bfbcc40cbdfa92bbb8a5ef0c4c21881e26c7229d9bdc92a4533 \
-    --hash=sha256:eb93ea76094c46fd4a1294eb49affcf849d36d9b939322009d2bee7d507fcb20 \
-    --hash=sha256:ebc9daba03c7ff3f62616c84c6cb37517445d15df00e1754852d6006039eb4a4 \
-    --hash=sha256:efbe7f89425a14edbc94787042309be77cb3674415eb6079b356e1f9552ba747 \
-    --hash=sha256:f11424bf5cf6226d0b136ed47daa58434e377c61b62d0100d1de7793f8e34a72 \
-    --hash=sha256:f444ab7f318e9b2c209b45496fb07bff5e7ada606e15d5253a162964aa078527 \
-    --hash=sha256:f498a6606247bfe896c2a4d837db711eb7b0ba23e409e16e4b23def4bada4b9d \
-    --hash=sha256:f760ed82ad8b7311ada58f9f68673e135ece3b1beb06d3ec8723a4f3d5dd824e \
-    --hash=sha256:f78ab823732b050d658eb735d553726663c9bccdeeee0653247533a23eb2e255 \
-    --hash=sha256:f8ef4c70c1edaf022875a8f9ff6c0c064f82831225acc91aa1b4f4d389e2e03a \
-    --hash=sha256:faa093af3bea365947325ec23ed24efe81dcb0efc1be7e19a36ba37108945237 \
-    --hash=sha256:fe9ce4361809903261c4b055284ba91d94adedfd2202e0257920b9085d505e37
+pycares==5.2.1 \
+    --hash=sha256:00d87ab92f8f19fc1b043aa0263e112133986047ae4aa8bc45c4506c68a6fdc5 \
+    --hash=sha256:05b445d655cfc9446388b668ce41135600e40c284fe411f46bb51ed81ed48401 \
+    --hash=sha256:07ad25040fd672d1ec3a9bc946430e174147661ebed954e22b2ab4eef5ec043f \
+    --hash=sha256:0b169ecd6e6a693c083fc7a6d503882768f75476fcf892354344cafc58a13240 \
+    --hash=sha256:0d511c94e22c92788ede11ea4e5fbb4ec3e40583fcfc59636b4a61524ddcbf84 \
+    --hash=sha256:10d6ac376b2bf4123fb50356ff08f1b36084885aaf9fcc6bdcd86118f19ac670 \
+    --hash=sha256:120520916b98c88c98e6deb870680f96bad7d94ce70bc31fd19db9478b211161 \
+    --hash=sha256:122539d254e2e66a0b811e98652aa62dcd88f2c22c833c0b44e5a444810079b2 \
+    --hash=sha256:15991eaa3e9e4ad05a678250389c7df7270056d3733eeb5c45d0025d7c0cdaf6 \
+    --hash=sha256:16f5d48c11a787a99e0d66a82c6d37c22439c269b8db20bc2709974e1db814b3 \
+    --hash=sha256:173c5dbb662901547f087cdb8881ffa17b01e1eaea669dd9778c6e4a178e4694 \
+    --hash=sha256:184b12c237903a2e081bce4a100321e22af6ddc5665686b78a695b6e65165858 \
+    --hash=sha256:184b51aafb40318d1bd64773a40e5a8330a4b6e89d6c4a4dc05f8a0f63943c89 \
+    --hash=sha256:21feb36f7f73c89f5a0b03cb44ccee52465228740b9e60262762e8c44d82da9b \
+    --hash=sha256:2b5084c9b24b18b2c0a2e0a73a39dd01e5ae095f8a702e72cada12796e73773d \
+    --hash=sha256:2e22f39ac1e4e79ccb4273d10367a103ca7d3e6d205d0375983c423aea279b73 \
+    --hash=sha256:3046c9de2382b7a4bad513035b22a4fd22a215e4e37ccaab9d00cd6aeb732a55 \
+    --hash=sha256:33af6e781ccbf17900952acba1c60bfbf4a566a33e3e32afef3f874f49cad319 \
+    --hash=sha256:35306b04d320f32196c395ad54ba31962213ed8682138505c62aa9931ab770e8 \
+    --hash=sha256:35a48b5f6b4da473de997aa5dddd2ee0cae12cb32e3451a375a78a570258dacd \
+    --hash=sha256:3955ce0cad64b6b527b1fb982a5222cc50d040d3fef0d947f02af4693f94023d \
+    --hash=sha256:3d6bd9b382093b67cfcdb9a430b58279b7593d958eea851f44a768fbb1cdc4df \
+    --hash=sha256:3d7563db520e414aedca434504f042cf5c57eb42e01ea6236eb07e26d2ad07c0 \
+    --hash=sha256:3db315688e0042b47c97a0752adebbd2e31799f51c6da034c34a5a1b8e2d52a3 \
+    --hash=sha256:3e89edc56a3745046676207958bf3dbf2971c5df0d64de9f7a893eba8bf255b4 \
+    --hash=sha256:3eb8311931e5233f187a1569f384301f41e2e07afe0a910d70aab3fca25321a4 \
+    --hash=sha256:401dcc74d9b1265b3c53e9847f4d86b5a521b1e3ebdb77c23a228cfb1172c2f9 \
+    --hash=sha256:4119bc75c81622ffb9e91e6e2fed09e1ccb594c9a58bcb8f9584ffd2d469b6e1 \
+    --hash=sha256:433c46e04e16040a927ac9f2f1787c3fd25c7bc9d71e35b4ed9fa126c4dbbb46 \
+    --hash=sha256:43c912dd17e2f7770a1f51fc7fdc461939fd14d09945736cc4e8ab7586cfc311 \
+    --hash=sha256:4477105f3abaef427fc828d03c61bb426235e53dbee737bbcf56a9d216d4e641 \
+    --hash=sha256:45ac1759e05210d0bf821c8392a7973571157b1e1fdfaa4194702c1e96da9135 \
+    --hash=sha256:46cb389dfd5995431ad910c8235adac43b1884100d57707fb78cb11761ec6c47 \
+    --hash=sha256:48270369c219d382299258c86488159cbbf69a6c63a980a29bfbeea270430435 \
+    --hash=sha256:4a465e7e87bfdeb12cbb3d3a2def6311be728a61929a961162264d308ff8f8fc \
+    --hash=sha256:4ad83faf65b0083f65464598bd830c0e01743d364860158a92fd33d1d1c1c94b \
+    --hash=sha256:4b1a5d7209b6900d3feb6e8c1a68c7ab856de8616581a9b9f04906f87f3eda6d \
+    --hash=sha256:4f57fe42479ff13b82256658950650640eb1acb876e5fab0a564ada57f48643a \
+    --hash=sha256:4fee5ddd11186c95331eb3f3d7418b0853a1ce40ce10376399301e87e7a9e5de \
+    --hash=sha256:555c4bd79bfe8b0c94f065878b1edd3d79cd4a7f7e5ff747e9e9fcefebb52045 \
+    --hash=sha256:5572b884f1c43c78ffc10f434de66565c84b459215c2f7b7ed67a6f51adf908e \
+    --hash=sha256:57beaf1baa9405ed4faff0075380c4cdad6d7a9066c796fd55fe11e237c7bb29 \
+    --hash=sha256:5df9bf3385d370d1a2962ff7b49485e65291ffc2b57c74ba3baade173cdd1ecc \
+    --hash=sha256:6055027e41756a09d963eb68b12975da710b36cbced2b60b5a1c73448446cf11 \
+    --hash=sha256:61235fd2bead60f9ed0548b1e1eb4e9925ffe1e6ebf5bb12d45feba6cbfd45b5 \
+    --hash=sha256:61b0ffe5dab7e0209f95ff5119eb5001e98846ed82687f41fa36d74e9087cd22 \
+    --hash=sha256:67792fe8a2927d7d97c7e662dd5d8177dbc85e631eb8577ab66007bfb71ef844 \
+    --hash=sha256:67abdfa283cc612320122c60810d1461ccad77162b367732591e5261d8242d0f \
+    --hash=sha256:696b9162aa9b5bf5910feaa1ca860b27facdbc146ed628caa21b7e75d21e8369 \
+    --hash=sha256:6c1d17ad95afb6ed88940dbb1d042db0bb45b70e0c056fdfdb6a10dfd4b98d61 \
+    --hash=sha256:6e52b6e97dec1a5ebeaefa4b51ceec04ab4154789e8ee795ceb5d1375044024b \
+    --hash=sha256:6e760236af5509c9612b2b30c30ae0519b624518eccec69ab94b487a7c07a0a9 \
+    --hash=sha256:6f73c334955424e0ff6f50f595010ee464cf01fd58c5e8b5929c573a7c48a6dd \
+    --hash=sha256:7878ea14cf173055efc8f7cda516eabf59351cb6f87279a81ee7746d40280397 \
+    --hash=sha256:7b73d3bb9a11f29f3af642ba4f8894910555fa87ae73ebb94b3e6efbcd8fe690 \
+    --hash=sha256:7c70f6c1834fff8e8b78d5d9748343ac8eef64830c58be77aa95efd04c4cf877 \
+    --hash=sha256:7ca6962897ff59ad82a695f93fbb22a76536375e621f867cedf86aad7be0a8e0 \
+    --hash=sha256:7dcf05eee2585c09d8bf781ab62e453e53fd5f5f86e6b6969a73e7792297893f \
+    --hash=sha256:7e5407e70e1afce27d0fa10d61bf802501f0bab12159771b469c9a4c9da3cc41 \
+    --hash=sha256:7f4ee91dac1c6c4cae18e5a478e836ec959d8710752a2fb9b23af03ef57b42c1 \
+    --hash=sha256:84c3d66a053a8b53cf7febe4a4eab3dd8797e08ebaeca11c2a0365bf03693ae7 \
+    --hash=sha256:8616a510b3f726588f11c02187fa5d7087b091b80402514df404776699318c24 \
+    --hash=sha256:8700dc8f161315a6fb0f7398b7aa2fc63d2988bb9ae27b78e2a5aacc3d498337 \
+    --hash=sha256:8c3b9e4047d5b87cdd589eab25519befa5c20fb4facb4512a09ee252b42f4e42 \
+    --hash=sha256:8cf593d70dff99a70ab796c887ab3ce29c18268b98733eaa5d2890b04fd80088 \
+    --hash=sha256:8d41eb52a472fc3e164976b3a5eeb4fcafd3817eb9436b803159a036ede79738 \
+    --hash=sha256:93f2837e7fdc5dab2557524d0394cb588d04345edf278ba0f542ad60f93bb6f0 \
+    --hash=sha256:97abfe4266be952cd7928fb7915ac02c1109e0ab0d0c9bdd033d691a67c2b481 \
+    --hash=sha256:97b26c2a50244a7052d1b64570c39d7176ca5e9e0ba25e36e1bdd3b3bddd9790 \
+    --hash=sha256:9a37815fe782773054f4c8c7cd5359cbdc79a20d86385371698f4251541b823f \
+    --hash=sha256:9cefd860313c2ef7ec8ef9327492f727340de0ad2d14ad4c119a746986e07469 \
+    --hash=sha256:a806ace0535a3c5eb7fd8fba35b3ff0ab271e47562131c7e4363bc63b972789b \
+    --hash=sha256:aec88dbe102a9356d72bad6976fa1b36882684fe4258b36dea6671eecb8d0270 \
+    --hash=sha256:b1734b3091cb4fd6ccc9f86c8575956fe0e103a2242292a44ff3e990969bb432 \
+    --hash=sha256:b39221e4727512e0110a07c7a0da0b607bde21c2ef9bdb2b173364c8a2348e54 \
+    --hash=sha256:b39a3743378abb831057e3c41ae91f0cbc5da0555feb6009cce2ca4fdbfe8821 \
+    --hash=sha256:b6f4a1ea065d3cac6eca7f66a31a4ffae4ffcd27f22149145d08d669574b6fac \
+    --hash=sha256:bb3c18022a96d2a4bfbb04120db24f400ad7cdb7a728581cb5fdc5cc2b1a3e81 \
+    --hash=sha256:c0c113684326dcf41e834e9493d667390e3edb095e8f09c950d938052720ea3b \
+    --hash=sha256:c19be1e86a29243672bf21358a81fe414228a46319d2b2f5aed5e243e51be489 \
+    --hash=sha256:c1b16c46bf158d15f173fc6307a04102718ed0191ea52554aa156af04187bb1a \
+    --hash=sha256:c55d7a9992393b4d93ead9dc26ed548449cd1a73c60114b6ac29210c91933d1b \
+    --hash=sha256:c7777105f28c05e2f2e1484106d5dba4cea809f5a4a4c0d10f329466db54d05a \
+    --hash=sha256:c8948802dba6c7823e29d8a73d6ea960d29ecead2da858a4bd5ca478017a476e \
+    --hash=sha256:d7e026212ac345a0d7d8a55c94d61f7977f5e1797c340a7685d1899fd32aca0e \
+    --hash=sha256:d8006889b281fb67f86c506514b44aab767bed286a7be6e6ff31bee0a02402d2 \
+    --hash=sha256:dc133f0281826f16b4bdf8f44646c23868e5cf2a960416f9feb738a61e1bd493 \
+    --hash=sha256:e226221891def02aefa5f5c8d66a9408f1c7a25611f830c3f6ef9874299055f8 \
+    --hash=sha256:e2b896888722b32ac3ab6625a49c759c4a6cce8c4e2476ef07fcaba153116dcd \
+    --hash=sha256:e338ad4212300d1bbf80dfb43731ba512d797054b9166dc336fb0e011214fca6 \
+    --hash=sha256:e57b72e8da27854a8f59f5bf4548c6167d0249f13f93b599bc7df8167f667c8c \
+    --hash=sha256:ec1abe7bc799d3c00c43c22dcb74a2889c4dd61bca03e9342fae9892a4d6a44f \
+    --hash=sha256:ed1844259c009f75bffbd58887ab5ae9336fcb3f5342f03f66af0260bd5b349c \
+    --hash=sha256:f06316804f88b32e4eeaf6ed1048bd65aeb57fc65587c90f07bbd9dc5591b1ec \
+    --hash=sha256:f4291963890b12366382bda11cf9ddc0e8d45b8c974829df3b63ed1a7ab544a1 \
+    --hash=sha256:f4304431df0a21b19891cf1408fd816bf9fd92fdd2020041914e6cb5e7d9b73b \
+    --hash=sha256:f5e33e287fbb25277f400667e46cd0e77f488917452cb520647de97a48ae5cd1 \
+    --hash=sha256:fb1816f6ca6ad13e857cf4d1e577f0900b84fb38f06f609e782cac17ff37741f \
+    --hash=sha256:fceebb23a86d1e1ee6946ea76143ab9207a4bb0f49d285885b7e25f1b64ec7e1
 pycognito==2024.5.1 \
     --hash=sha256:c821895dc62b7aea410fdccae4f96d8be7cab374182339f50a03de0fcb93f9ea \
     --hash=sha256:e211c66698c2c3dc8680e95107c2b4a922f504c3f7c179c27b8ee1ab0fc23ae4
-pycparser==3.0 \
-    --hash=sha256:600f49d217304a5902ac3c37e1281c9fe94e4d0489de643a9504c5cdfdfc6b29 \
-    --hash=sha256:b727414169a36b7d524c1c3e31839a521725078d7b2ff038656844266160a992
-pyjwt==2.15.0 \
-    --hash=sha256:7a3742debf6b879e912dbb9819ceec1594be812452b78c5f2e2dfc56564954f8 \
-    --hash=sha256:b11c5f9791d7bf51c2b39a81ed669f6b2dbbd669df2942f6c60167e9e3d1abe4
+pycparser==3.12 \
+    --hash=sha256:a076f3f489b39b43ed13563a1dafe42447445bec2e294154ec5c57fcdda4c85e \
+    --hash=sha256:f03387877eab82ce01bbdfd0ba7252ee55a90b1c708d5129e2ce915475cf1db6
+pyjwt==2.15.1 \
+    --hash=sha256:42d59d631f7768a1028a64c7ff581a9bf7519804daf91fc5b6c56e30eec5e193 \
+    --hash=sha256:4f259e80cdfb6b3fc18a7de51fd1ef9ec79652f25019bae68975ca2468a34df8
 pynacl==1.6.2 \
     --hash=sha256:018494d6d696ae03c7e656e5e74cdfd8ea1326962cc401bcf018f1ed8436811c \
     --hash=sha256:04316d1fc625d860b6c162fff704eb8426b1a8bcd3abacea11142cbd99a6b574 \
@@ -2481,20 +2550,20 @@ pynacl==1.6.2 \
 pyopenssl==26.4.0 \
     --hash=sha256:28dfcce0162b9211413e26dfbfdf1d24317fbeba18fc93c12400a1856b2a0bc7 \
     --hash=sha256:f0eb0cb2d581d3ad2b9c489468485e7f2ab6727d08401bcf9d824c3caddf3c1c
-pyrfc3339==2.1.0 \
-    --hash=sha256:560f3f972e339f579513fe1396974352fd575ef27caff160a38b312252fcddf3 \
-    --hash=sha256:c569a9714faf115cdb20b51e830e798c1f4de8dabb07f6ff25d221b5d09d8d7f
+pyrfc3339==2.1.1 \
+    --hash=sha256:4973172cb8b29c14caca7f76e6a52890d9e59ec2722dd5eb29b7fdd9fda2232f \
+    --hash=sha256:b144d63819bd4c1ebf9cb57e12f4cba567fcf23d6e8f2f829ba9c7810ea4b951
 pyric==0.1.6.3 \
     --hash=sha256:b539b01cafebd2406c00097f94525ea0f8ecd1dd92f7731f43eac0ef16c2ccc9
-python-dateutil==2.9.0.post0 \
-    --hash=sha256:37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3 \
-    --hash=sha256:a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427
-python-slugify==8.0.4 \
-    --hash=sha256:276540b79961052b66b7d116620b36518847f52d5fd9e3a70164fc8c50faa6b8 \
-    --hash=sha256:59202371d1d05b54a9e7720c5e038f928f45daaffe41dd10822f3907b937c856
-pytz==2026.4 \
-    --hash=sha256:464303645bafafd72418898368b2429458f709cf1eb6a15372fbcc396b64da63 \
-    --hash=sha256:9d514388fbc89ca0833203464272ac485b8828568ab73532f5020f17e892a0ff
+python-dateutil==3.0.0 \
+    --hash=sha256:3c79630202e4152c6add678446984236efe4f57e84d8e892aab0637bab82e9fd \
+    --hash=sha256:7ebcb3c29a92f3ceafe79a7a48a5c45677e9e004bbeec5742ac0bbb00560b7a2
+python-slugify==9.1.3 \
+    --hash=sha256:90e997f2e0987239ce95e12f700086eb18e1d1d3ee22624fbbdbd095afca42b6 \
+    --hash=sha256:9aced0670e54c5603e2335c0fa9a4011ad4bc41ecb3c46e8097294c46fd60ed4
+pytz==2026.6 \
+    --hash=sha256:3b0fc2727707663d6e517936f444fd8a8b240f1fc32f4bf7ee03274245945284 \
+    --hash=sha256:7fed3fee8fd6bd4a2b7b75a8d56021d0624127bf69bd5691f115db929ac570b3
 pyyaml==6.0.3 \
     --hash=sha256:00c4bdeba853cc34e7dd471f16b4114f4162dc03e6b7afcc2128711f0eca823c \
     --hash=sha256:0150219816b6a1fa26fb4699fb7daa9caf09eb1999f3b70fb6e786805e80375a \
@@ -2569,211 +2638,231 @@ pyyaml==6.0.3 \
     --hash=sha256:f7057c9a337546edc7973c0d3ba84ddcdf0daa14533c2065749c9075001090e6 \
     --hash=sha256:fa160448684b4e94d80416c0fa4aac48967a969efe22931448d853ada8baf926 \
     --hash=sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0
-regex==2026.9.10 \
-    --hash=sha256:030fa9e23624e39b3b94e46b90a5abd1a1678eb2f58fcdd3fd6c27526bf91c7e \
-    --hash=sha256:032da15431c890d376f53547f0a6219f4f4cd19f3e4f11bdc321453b5bd207e4 \
-    --hash=sha256:044bd4639b6bb409ec9e5d8b7accd57e02b4c4a4e2eafde916f8ae8006b3e40b \
-    --hash=sha256:048a89ee797db10160bd2bd519286577a6b43a100279bd4b7d8456a3d69c80a0 \
-    --hash=sha256:05fb018cfe7144585fc83882405906ff84994a2d154afc2509ecc7752c51f864 \
-    --hash=sha256:07b45ba5c94b8fcb30cb6c56a11f715c57533a3017964504322ea52690a27b72 \
-    --hash=sha256:0aa7589394230e0f0a422ab6b90841ff12c87e855e7aaf75d192a54a5f124548 \
-    --hash=sha256:0acee94b480dd853e39434aa9a575f95385b1b4b8fa3feae56db363ca5cad782 \
-    --hash=sha256:0b9ba3b2765cdfe18f0f561a69f78a69701f2896654a81c711108d35d14e5099 \
-    --hash=sha256:0c32480f3371b75068decaf9e5da72c224e953830dd71e36e06cf80e30ea39d8 \
-    --hash=sha256:1270cdec69248592bbe38a0b263ed58d907b891bd2b93703e225c317e421bda1 \
-    --hash=sha256:13c52fc377792675f604a207a2ae5958c080f6854f7698d40d9ff034d95b1e76 \
-    --hash=sha256:14caa05ce39ec70437af5aac8814c50ee6628f4a90353871c059692f448a164f \
-    --hash=sha256:1562aabd9d4eb09bd88a62ad97ed06800094b529ac43419e43020b9cefec79b0 \
-    --hash=sha256:175cf49ce7a994c88b8f15e3cb17cdb66a48ebb2d36de736b8205033db950f89 \
-    --hash=sha256:1aa309ab7ba89a62d6cf70dbd38d4176440bce3c7001ab86256704cf4c18c6eb \
-    --hash=sha256:1ad10a135fa0b4e4a462a61d07c6654d7518cfdb5cb8da08f9ff7d61384af1fe \
-    --hash=sha256:1b891f77554bff991804cee24b78b40789f7d5993a24c7907bc7025fd2a70c8d \
-    --hash=sha256:1e321e2c84f0e52c457f5ea5944f796d6e8e09cb99738ea98dcc1bfe402a128d \
-    --hash=sha256:1e954e246466d5a1a78f563ce8364b5d7cb19e7adb0ccdec8f9c9610083187bc \
-    --hash=sha256:1f0a8b4928823bc8b217a1ab7bf3d90598909dec9a70fbbfe9a52cc4eca55990 \
-    --hash=sha256:1fbc8314436353e097c050e11b01a6c11433579437ed0579730157676ef59e2f \
-    --hash=sha256:20e8bfb07ad79a282f8b95b56fe67f9750b1b7f775724e4ba1f23cb296115ce4 \
-    --hash=sha256:217e98ba5fc8908ed8ffd4ebac04753a0c831067cbfb495b9821b94cc61eaa76 \
-    --hash=sha256:239620b0e0681669367c0e218c8eb2551d9f8fe3b9fccfc8d0003377804e8348 \
-    --hash=sha256:23ac9a28180f274d7dd7651fa131ad5b02d343b75df4b040737f0356223895dd \
-    --hash=sha256:2479171edccced52ef02b899558f88ab2c235fe05b93180fdcae1670aacd89e1 \
-    --hash=sha256:24d12a625a37c89c2b09303402a06942f55f071b95a7916a49c17034c3d47cd5 \
-    --hash=sha256:2dd9286093c71afc8f55ef035c5b9d2776641fd72c6535f1febc92d0b0be9666 \
-    --hash=sha256:2e67f8843f0e4b931f1fa860bf3bbe4134b714c0155cc5c7c0d7ea450230aae0 \
-    --hash=sha256:31e4df2b11d48f61d511019bc1ee9b477055f17c352b68fe72db7a98b14d603c \
-    --hash=sha256:3264132d576847ab5f88bb83e7debe67854bf165b3ea613bd467312b6099536a \
-    --hash=sha256:3540734dbe241ebb3b87d5713781f6749a3e4d45480f506aa5fb5cbb0c37d249 \
-    --hash=sha256:35ba3bab0c45079735f55ac61526774de1d84bc4a0333cc554e1a4ab74913924 \
-    --hash=sha256:3a66e40a1a20de96a2fee00ed67e11012b62d85b277688258677fd19997addb7 \
-    --hash=sha256:3bdeed3318a8eb2bbadc9c56347e0ff651639e934a47e168d05a3b12929fd0e7 \
-    --hash=sha256:3fb4ae8cf83ef4e9addd43b2da31a9f45be816a8036fae8af59c8998b72718e2 \
-    --hash=sha256:4971776b4f2bd7fd9a83eceb2cb2592cbe2924f639fe8045e6a9de5ba4bfcf25 \
-    --hash=sha256:4a761ea45f2ad74c575ef5850ea514cef97302a552d3c7c9d1a1a870d4661d6c \
-    --hash=sha256:4c66d54042a14a503907d81861b8a5235e6d1f03d4fbc1d8767f652eaf957ac1 \
-    --hash=sha256:4db7d00c4afbfbb55b8e17b1e371da11418ea9389b030acec63c1fa4c7ad4b86 \
-    --hash=sha256:4f0407474ffac8e5e89d93ca41d60891e29f0ab8423eb66ff292d850a86a0843 \
-    --hash=sha256:53e182b6b04d0011909b47d51a2d72d908de07c7b1c7f16b3adda2204d723bc1 \
-    --hash=sha256:5847e22bbf959764d776937d791d034cc2d19b787e361c88d97e859e8dc68502 \
-    --hash=sha256:58c01f7b81079cf0817ba831ff4d9eff5d28be4a3ac76c353e6f09bd63f4c386 \
-    --hash=sha256:58da726d3e766c0b3f5a3997dfaf0275898a1107b8191cdd6b0437fe45fd817d \
-    --hash=sha256:5bef622850cf760154719d4e0d74b0a855962432995168e250069899ae12fe8f \
-    --hash=sha256:5ccd139b2061132e7b265cfb4b4721baeb9f8928b81415304abf1ec7e3181c26 \
-    --hash=sha256:5cef9f3d14796500ea834c41dbe688f1f6b23c7024dc23e8a794d7ebaf5d71d0 \
-    --hash=sha256:63bb62cf62217dc38c8a6b2b61b165b0e4eb8fa93b0aba12139251c0986a8fa3 \
-    --hash=sha256:681ed38664b64c6617d3c3c332018d1948c77e139c5ea667c1886efa671e426f \
-    --hash=sha256:6888065672b341e5246f391ec16dc258a29218ac784172fd67c30d941544755b \
-    --hash=sha256:6aebdd9a946de328b3f6f61dbf48dd064a36eb6dddf96e34ae6651d37f6e9383 \
-    --hash=sha256:6afcad14310f1311d077553ed374b42a5e538f85a8c884b4e38e52de091c8077 \
-    --hash=sha256:6b34a778c695d24e77c140e3b4c95da69282e34f2f6b02b55656aa4a0379f643 \
-    --hash=sha256:6fd555fc9abef50c530869690b2daca054c8811a7aff632d11f9a7b2590b2742 \
-    --hash=sha256:71879292c9c7ac67b1680345b16daba1be937cb027362cfa04e68f65db2dcfdd \
-    --hash=sha256:75242f44a3e283106077be4ab717bc535e4701c9d54ad69e195945c22f137a1d \
-    --hash=sha256:75aa39d3f4f1650eea84e46b0d8cefe77dd5478c10e3d0aaf0b0f00493475a7a \
-    --hash=sha256:75f9297b16fcb588a1f8d8a55dabef3c0c20b0c7bac43c87ceaaaf1a825c12f4 \
-    --hash=sha256:79e9432995e14c749d34209413de5e621ec8e67789bf4f46dbfabea9d06a2406 \
-    --hash=sha256:7abb38b8c40f3a235235a44da452c64b7b5c1d650ec6351027db0e090804f2e5 \
-    --hash=sha256:7dcad477c49c4c626a6c4fcd71b39a971aa217060cc40a6569fd24edcc0fa509 \
-    --hash=sha256:7e6c0b5ec6ddee4032247585dc491b0fa58627745b66a705728703a3f0331231 \
-    --hash=sha256:7f8f10015866608fe4c043cec2e4fe4c39a94bb50e45091de4cdf4004b9ae4b0 \
-    --hash=sha256:866de9f98df0611d7b62b3a8729d3284a64c0cc6edd90bb95a533e443a4939cb \
-    --hash=sha256:87f5f75c109f08f5c602d68e1af54cead8165189c727b6ac946b30b9833a3ba4 \
-    --hash=sha256:880ac684c27176464c00c3fdc456116364f5ebc70da07aad0c2d4a7ba45e98db \
-    --hash=sha256:88b02aa8d0ec9b6189fe933d425775882271c23700ac11fd26d1779b0f56fde3 \
-    --hash=sha256:8ba1f78bd4fef2d8f84b894ec28ac3481afe6cc07aaa253ad4717ef7b3fe6bcb \
-    --hash=sha256:8c07021a4faa3f092869adbd1f35cdc7a592276c807aeebc3ceb8ff1a638f0b4 \
-    --hash=sha256:8d5c4518235a2ec1611e57af85fa488d529c1106aacff12adadcedf8687012cd \
-    --hash=sha256:8e127d9a80cbf1c3276bb465c6d047e8705e97b58c2b8f2f0c0a69c336b44b37 \
-    --hash=sha256:94c5ce3bc41d226b4eb89ca3f842b2e28c031487fb1f34eb2153d98235831325 \
-    --hash=sha256:94d096369b7cd96d15343fef5257fe39eff9d0e8758b92a0e15e358b92cdb2fc \
-    --hash=sha256:968c1e33edd9a104d1bf24c8d476c72de7e3839ae7f894b37e9e4f4739fdeeca \
-    --hash=sha256:990797e765d89a423880052c68b61c31afe701de94a8c060f61c40605ca6c727 \
-    --hash=sha256:9ce239acb15843ab03976626af810a4424b0409689ec2bbc52088ab5479ab487 \
-    --hash=sha256:9d772586951d7d6a5d162d48f414065e483b1c81ab38fd8ed97c78b05883421a \
-    --hash=sha256:9fbd2e5d8002dc49a6129fb321ec51c57a025e752ed525ddce0ba9223c4350a7 \
-    --hash=sha256:a41693eb3fc4b92e6127d113813c6c395237f7edd3224abf67609af48c690d11 \
-    --hash=sha256:abbfc1c33bf8efddcc43844aba61e036d74a918680dc3ce8ce2538b004eda0f9 \
-    --hash=sha256:b298cdc33c5cc6969ff07f0fba19cc73e0fd8576373c50935feadaca2f6b4405 \
-    --hash=sha256:b43456de605c8ee77eb75f07bc1ee44ba27f9cee22207deb77d495e954b7d953 \
-    --hash=sha256:b71649169a9fcf30b395ee01047fa7ad6654a4c900ca75b23c04dedcce6a1f8c \
-    --hash=sha256:b91c37551bf39d75116c02b146956f65b9aa0337a4a652f4ae186983789d4001 \
-    --hash=sha256:b9d36b03dc362aa40ffaaec9d9bd75e87763529563ec008c43b0e07782f5be7a \
-    --hash=sha256:bafa41b0dd63669e5c0f8adf3d24819efeb73c847f492eb011212eb352e69041 \
-    --hash=sha256:bb7774924f8cd69f49cba0b3c2d679a6326f777e0e67d130ad5203e4df53f0d3 \
-    --hash=sha256:bf29611e5376fec8f795879bb5c6153a76c3a292573d173c26784042b01eb840 \
-    --hash=sha256:c014641157e9049b0603b8daa5343bd408d9b757b709aaa0f373cd3fab2d7944 \
-    --hash=sha256:c103b3b14e011774af4fb7e4617ad4d72b9171905cd3b231a70a4efd76e477d7 \
-    --hash=sha256:c22df8dd6373bbe3898e77429ffc85594300e39d752fd0e68a31e59d37899376 \
-    --hash=sha256:c25a754bb81a2edcfc3b65eda50f017d736f818112ed43e8aafd595cb00678ae \
-    --hash=sha256:c32818b28bcd153b25b63038348a9fe9b9fbcddb60df43f204c3ab55eeb57f77 \
-    --hash=sha256:c37fa93bf18bf4f90b01c0fa9f11ea567ee4b7dd8bf96e63663e5edc37aa38cf \
-    --hash=sha256:c3d95d7d9538b5b726dd6fcd7b6117a71e6565202f6d64f5845fb4d8f203f533 \
-    --hash=sha256:c8fbd9cb30c68c1686b94029b9ef845d5870d3d65baf66cb126b676849b9d72b \
-    --hash=sha256:cb76a9c4e07a6a47849726af0ed14c41741a182f097f134a8cf29c1bc0f4dde8 \
-    --hash=sha256:ce7c118cb102975f974585688357a717ffbf9dddd64ab0bb1bc93eb5b367cf95 \
-    --hash=sha256:cf377960d2ac37d987394a9dbaa75e91338c41a46d41e1d25e90125e7b3ee2dc \
-    --hash=sha256:d278ad30ec83b6b9202685b0f80b741a51ea3ca7f0595ebda96e7628b6398876 \
-    --hash=sha256:d2d377fd1cad611b806cdd732d86b65f536c768209890cb442556548daa65a23 \
-    --hash=sha256:d414c411c06fe0009eac33488fb1591c66b5c2673e342e452e7bb2fe63da8194 \
-    --hash=sha256:d8c668af8f7bdb1d18739c27d30cd9f4b371495a883f75a002fb7a39d740fecd \
-    --hash=sha256:dce932f8e3ba936475ea3d0d8b59f7b050a9e206e994f53f8fd80299871e87da \
-    --hash=sha256:debc629e98b95abaea1cf3057ca296151f348c697c9b8a59d18013adb302c0dd \
-    --hash=sha256:e0dc78251154b66dc60211563fc115345da332eaa881e4e2523fb1edae3772f4 \
-    --hash=sha256:e5e4a6e0734a685d13b9685622bb503bdbb2927f8b0df025a5085f0ea067475b \
-    --hash=sha256:e6b99181d184d0f5c7b36b8d12b94d1e9499cce6246594331f9edc5d2ea9fceb \
-    --hash=sha256:e7327795089ddb44912dce1434e1d7244be2e9fb48fcc2d6782936af7a3062db \
-    --hash=sha256:ebb2ba68e4641a994061f70bf44ed448fba0b9b1d18c94ffb9efc1cca805b39b \
-    --hash=sha256:ec8855f08c17895a26fbf5f19ed829722e19b34a96629e49a43c92974924026b \
-    --hash=sha256:ecb2e7acb18f8cc4a67f0ad986c0af291ea4dd385d0614ba9bc09d7f8bbb478c \
-    --hash=sha256:ef4c0a9dfdc90581b90b1b95a8c3d1557f8ff8f5a2a53536d26314de699d1468 \
-    --hash=sha256:ef4ce69ff97fbb44b46751cfea5e859ad0b66d1a50abf34954f0645f51e81671 \
-    --hash=sha256:ef5a059ea1c6ee5d1c7e99a2484e628608d010921efe876c6f0e2029d2f35eca \
-    --hash=sha256:f0e2e5d23448b660d60a6ed85c46cc03b4b48bd276b8f4041d4a5fe2a4a0626b \
-    --hash=sha256:f2374c27deb189b282ec7e16106752c22ad39b056bbd8018960b1e4cc95d67a1 \
-    --hash=sha256:f2f43bf4e47ff7ce9e585558706d698c6204d0f80bf2207766382ed817c8e9f4 \
-    --hash=sha256:f5c629df03adec31ee505dda3c8988f106c9390e4cbd343600036eb8b3d6724f \
-    --hash=sha256:f70b9f0e39c2dba1d9da6bf7ef7c377cad7277f8440e9a69be05ede529ff024c \
-    --hash=sha256:f7d4656e17ab736e9415a6442a345bfc97bb8b7dcce47884bb74a37f70f08d0c \
-    --hash=sha256:f8bdec659a8fa7af51a32b224b3b7c02bc415d54ffd35187b1d224176b17d607 \
-    --hash=sha256:faa911fbbcf8ac90bda0e0657d60768e3390954ef0588211d63a22add1cb1cd1 \
-    --hash=sha256:fbc4e2f3cb7ce8436154e6483079e7d35eeb321a952fa936e180300630d8b873 \
-    --hash=sha256:fd6bd89b9fc06018d35851cab0240adb7dd84d51941b19f6574ac90cd54e3ae5 \
-    --hash=sha256:ff4d7b14ea19e50c8d9d6d83f45bd9b45cbb624c07ac1fa54db0a019049abed7 \
-    --hash=sha256:ff6b3267318661dfddf6b3628663e00e5946bd0a5c8fa678537a1401f0388f91 \
-    --hash=sha256:ffc2da104e43db716ce30cef9f28049a1faa6aca385dd8771b033268d0730b07
+regex==2026.9.29 \
+    --hash=sha256:01000ddf0e3ffef97f2413ceb514f6313040106b6d18a03ee00a4fe35c1eb1db \
+    --hash=sha256:0166844493626c5015c6088ee15c9ca2fd060ca15b7641d1657da6a58432ae33 \
+    --hash=sha256:044265d77d94f5e3cb2fd72c76723807c429cb8c533e9d4672d0334a6f14f588 \
+    --hash=sha256:0476e5bcbe6e1ba3d1c4cc7bbb1c3ba78e3b979b5c8a88d0a6a8cdd4992b8c84 \
+    --hash=sha256:066d0e3dbfdd739bce2bf8c2a41dd16f73e3d8adc2eb06dd803a36a307f56075 \
+    --hash=sha256:0b65c72739f981377c9c22e0c5c3cd7f42da7bd8a3c9209330fac772c7d893ed \
+    --hash=sha256:0c992c19cd45058a4b92f68f139c93db168b48fb1f322c9a7cd620806afb6b51 \
+    --hash=sha256:0cc63b5e47c12a48d90c7e9d7de6a035dd14f62868aaedbb4e0ff8ba2b8bfe7b \
+    --hash=sha256:0dd8af32e9f7b56b7f95cc1fd79b23054c3bdc172392ae560acc24d57b7ffe71 \
+    --hash=sha256:0def9fb6abac55492d6d51cddb7225d07d6f279e774e0adc08569a54a5fc8d46 \
+    --hash=sha256:0fd2c901cc307a745ad4bc87f20060d7a0825a3371d1e93488af22e7a387f78f \
+    --hash=sha256:1043aedf5917caa861bcb25a9c11460049656bdf0017a90a309fa8f255467725 \
+    --hash=sha256:121a76a0985db80ceae9e171c337f8c927868e37d01b54e3ce87bc87f9c6a208 \
+    --hash=sha256:143533cc4b6fbc5b95aca0a5b8d541088d374831593def000ec89322c220221d \
+    --hash=sha256:14e953ff3607c92d7675bf79c4d4509ef6782aa8c08509f179f9b3d6d0679e86 \
+    --hash=sha256:18ae8eed4526e35bdb754d61562b90bf5c00a67fdcf3cc1380dd59597486631b \
+    --hash=sha256:19959129885356df0e97556856f77eb2888380dac18bed075a7c05c5128c618d \
+    --hash=sha256:1ba8c6a416569ce0d37e83e28a254a61dc99a419084dfb6476cea02d997f74fa \
+    --hash=sha256:1c2a0026062abcc321a53db4a185ceba0b59a66b5d37b0808917a88b55a5257f \
+    --hash=sha256:1d9fe8091b2e89d470df68a9331111ed008ae8aae6bf1e8e1fba4086a495c84e \
+    --hash=sha256:2089fe39c406784d90101c726755ffa1497bb74638fd434300d2b88006186de8 \
+    --hash=sha256:23ae6fdad9e63e54038f5ef78aba2933faca61e24d432786589e737bc5522ebb \
+    --hash=sha256:26ec4ccce55aa533fbd603d08911b01101a8fcfec987845ac3ae2c7087b2bde3 \
+    --hash=sha256:2f7f7aa47b229f2b39a2ae2596d2ad5625d77b5eb9856fac2dab3eb506cdd0a0 \
+    --hash=sha256:31b003f9a070335e2a8233ee9b14a3ca8e6d792012ae011f741bf0aaf11744c5 \
+    --hash=sha256:32ab11df9677ca80bcbb5fe4eb1da9109a5019239a054836efc6fa1c64e683cf \
+    --hash=sha256:33026515aebc0e70d1c89978e53e8d695d35d9e472f8d5b34465ba3c74028650 \
+    --hash=sha256:34b6925af9853bf461950e6508910f179fd6e9b1a7ec8548e069606b7e51a26b \
+    --hash=sha256:352cf115a810b357caa35193ab656ecf5ef41056855e82f292c99e8514f8d954 \
+    --hash=sha256:39ab5894d971f9ac68baa6eca5c50387db579cfcacf36ae8df3feceb1815e6d0 \
+    --hash=sha256:3a21a9509d0ee88e7a70e1ad228cd2f0e0fd1e187458db132e8a8d18c97daf9d \
+    --hash=sha256:3c5c2ef13797466aa64170cbb66ad98a32351dd4127694cea7199f80f213750d \
+    --hash=sha256:3e778bfccd63075167709136afbc251c1f683758d5bf49c803c60ac3f894ce6b \
+    --hash=sha256:3f1e6cb402a89457582cd696f982559217d13484a193202c394015297968c86d \
+    --hash=sha256:42e82e578c904445d4c8a35b8f28052cf567593215fa5db06266fbc6f77aaa2e \
+    --hash=sha256:4408b2b27a95ca8cc48b7411945753773353b5c93b307754781086c99d3a576f \
+    --hash=sha256:446654b29bfaa30500d80947eda42cef1449dc8a87f4e3cf061cc8485d3a1f0b \
+    --hash=sha256:45010bcfe66df41522d56c9b6114e87ecc597a08970ff6a2ced24415c141ae5f \
+    --hash=sha256:49ee178ca31c94621294bf9b8b676a92a2e6bba8af0529591753719e57edb621 \
+    --hash=sha256:4d7d93613b01b0199961330e49cfc52d479b3d5776c56c691db31130c0a07d91 \
+    --hash=sha256:4fb41211d2333eb930a51e0546a65999761cf1f572a4da56ef9b8a62966c06f2 \
+    --hash=sha256:4fe97894d1b306c919b4e50def1e6f6c522f4d03a7283811f4d108f1ce5d3ac2 \
+    --hash=sha256:554bffadcbcb6d5f4e5fb10a61cc52084b9a63d1dab5f10bcd2c4343972e8e2c \
+    --hash=sha256:59b49507f47479e299a9e1bc41b5cb83a7afda0540625f1dbae886615978acbf \
+    --hash=sha256:5eeb8edc6110d9194a4d0d54610f64c37a31c605b5dbb7e407fc6ec7fa34a4a1 \
+    --hash=sha256:612b709381c0355b70d89cdb51b7f670591ed5cbbc0e3b5337488019dc667b65 \
+    --hash=sha256:61956f074ecd123f55adca68ee3eab46e6a07ad3f8e64e6db95dfacb444f55c4 \
+    --hash=sha256:6398d5145689503412cc1748895242598d8846b8967b851133b20dc2ed1e21e8 \
+    --hash=sha256:65b408d8fcb273e3499e7ef2ce796810da1becd208c7fb4373692a242d79d461 \
+    --hash=sha256:686ac5350fceae63830bb98805fcb8039325bf4c06d9f6f048ff65229d5bffa5 \
+    --hash=sha256:6a1a824fbed817e0a891103886b68f063b1e83cc51bc97192a90a60195a9291f \
+    --hash=sha256:6abb75ab16bc3281714a5b99548a2225db70dba1f995f6d7f7419b76eb5a8fbe \
+    --hash=sha256:6f7121a8914ed13fcfe2099f895341bfb789f004d4c5a0bdece8fa667da10849 \
+    --hash=sha256:7020ed44df30b3aa492c00ee3b52d0548c1f30c2c6c5bb13ae897680900d3413 \
+    --hash=sha256:720537c7ea6f80dc61913184edb0ce2497a306b39ef19f28505b322553d52bdb \
+    --hash=sha256:724184b4aafed865e4f13ca313fdcb43024300c028ec67319cfa16847d84685e \
+    --hash=sha256:7c03031610e3e6ed1768a2b7a8fc84637c1257b50c5eacaf094c6e17a84fc563 \
+    --hash=sha256:80a5ea3b4fd9d6a5b9a44f7976a9acaaab35aa3c1f6b29e5bd857dfabaded223 \
+    --hash=sha256:80c7cadd3fd2bfde5df8aa0787e315812cad0c313a753095d02f4c2b6c01677b \
+    --hash=sha256:80ea96f5c1a30bf09007d48466521d9c294bebe197c708c3359096e3e3691632 \
+    --hash=sha256:864e9b87ac33c3fb9fb4ad48166d4fdb579c351d5c77deb0d34bccb36a775cd9 \
+    --hash=sha256:87fb80cbe3557e27e7b28b995c2b2eedf689b8886f941ab93e0e288f0976518a \
+    --hash=sha256:8873c4a11c50b9989168881aeb3f08859f469d809941866aa1feefd8be5431f6 \
+    --hash=sha256:888d60953908dcf761aa320c3e390ab8556efbdb551ace63921de90f6ae0848d \
+    --hash=sha256:8b5fcc4771732191b2b7d1dd68d8f0353f47f8d90b6150f6dce58bf1112442cb \
+    --hash=sha256:8f39588af4731c8923c26810eb3b33f76f17633985e40f59c3cd45a33805a895 \
+    --hash=sha256:9173db3be74a35cb6731701094b98120f7ee4876a287882a59cdea1fa7da342f \
+    --hash=sha256:92f05c9c42bde5785dc48770bc2194d9f7442544156f951e19cd31b096cec562 \
+    --hash=sha256:951733b1bbdb71e377cec567b409f1a7881b47cfcad84121aa74cb575fa425ea \
+    --hash=sha256:957bb708e8057ab1649ba566456429d691ec9b90d1c9ad1af1ba7ffbbeaf05f2 \
+    --hash=sha256:9916fda742cd4eede63b286f58c06718324265d727ce0856eb1aac86d0d150d6 \
+    --hash=sha256:9e1d3a4cb7993b708f0ada8d0c84590efd853f169e7147d2202c9da503180242 \
+    --hash=sha256:9e4482589065c8ecd761cff522dcd85f2d39e62f551e37e025d1c7d54772def3 \
+    --hash=sha256:a5300757f8a68f5b6cc33f57338d72a0e3589c5cc9ad5f8504ea06f028be582a \
+    --hash=sha256:a540abfab208e1b7ef2df231c40ef3b6cbb30a0aad6204e9b6a81c10a6794628 \
+    --hash=sha256:a5758353650079898dc1b2b0e95aa51fa23a30d020e06f62c430dd08ee56cdd8 \
+    --hash=sha256:a64b85a4760337cfefdb27d42da6ed8b58e8cde3f2d57b6ef43e76ef6ea9ef47 \
+    --hash=sha256:a655d34b2a6943af32401f3d94f72e9d731f6ad16285815550bf2b4ee69d420a \
+    --hash=sha256:a714befaacbd10092ffe4cea0d3c5f008fb9efe9bc322c715bcdfdee414b9a3d \
+    --hash=sha256:a760da040b47767b4b873adfb7c3b691e9ba2fc60f113f9d0b88f1a62f323e85 \
+    --hash=sha256:addd736a0547d553283adaf4e05d7104e7f2c7b0b092e9b4d28756825f14531f \
+    --hash=sha256:ae4613d7d9dda60fcba95f846cc6f808017f1843f392cf9daad14a6534493d71 \
+    --hash=sha256:b11b589e00095ec69cf79841a76360f9b079e95b0368a25b5ebb951ab0c157ff \
+    --hash=sha256:b3e445b66c80b4eb4234e855ce94d9adc183eedbd632816228d89930b91b2c5b \
+    --hash=sha256:b7b893976e7fe42053da64f2aa27239c24252fd2ec6df471e1be197c0addc3b1 \
+    --hash=sha256:b84f186a7f0536fe4ff9a9fa12d06d007b9b71d4b5352ddcc41f59ad6522a312 \
+    --hash=sha256:b89efc38431793d28b7cd91227e2f952ad7c48df19132b17f43a5fec3c14143b \
+    --hash=sha256:b97a38fb4c732b6832db6bf108963adbcd82ef1268ba2025dce390f45af75efa \
+    --hash=sha256:b9d74e4eee9ddb64c2e92d5d61472c59c21684c059eb7b68767be9628e977859 \
+    --hash=sha256:bb90e7177944b6684738c1fc36aabd2dd00d1de3be7dbe09f91e196f1bc0dc81 \
+    --hash=sha256:bec37990e3d6121f29ecfb594bd8f1bf009e9f7926daba2e50e3b27d3892a783 \
+    --hash=sha256:bf3c49863c23a1ad6da9c30351aed6cff8d5ddbeb63c5c8420ae54e98c7d0138 \
+    --hash=sha256:bf48516e35cf848390ea68850aba53e7c333720d2945b4d2c25b69fc5171723f \
+    --hash=sha256:bfc71e6d970419c1309b3640305298643e2a734cad3f7cfb6d2ddee4175ab53d \
+    --hash=sha256:c0094897d7d01f184b2d7fe8c56c66d64efe01b31f4b7d34205b391387df1111 \
+    --hash=sha256:c03c6eb6ece86dfdcbb34799efaa339b093132e1aceed491ba5e08fe06cdf699 \
+    --hash=sha256:c1a9a6651197fbed6f0212591418b9def774fc3f8324f78d1bf0e6a63e5f8aa1 \
+    --hash=sha256:c3589f40749acce747510bf5d589d54e376cb0930ea58b35effac97e5312b0c1 \
+    --hash=sha256:c4e38dd8f39c43a91d2410ad2b85610701b0979342c3df1d69eaf8e838c757d8 \
+    --hash=sha256:c6c8fabf1dafc1f1ddcbb67896d3f93efb092e8c4b6322d7389b944e76a484e5 \
+    --hash=sha256:c90fcf7804ea0a54b896ce0f2b9565350220b8d4890fd0db461a476a4c687963 \
+    --hash=sha256:c9b602fae1e00b7c035d661ce85575365719192a7b46784bd71cf64c68053aa0 \
+    --hash=sha256:ccb64d887a9db1cd76dbc0f92051a1a478a2a67e7f56c62d915cb881d7734704 \
+    --hash=sha256:d06fcdecc10fc7954d7c8f27a03c96055fe525274dc84a7b0dbdc3d6b9e03dab \
+    --hash=sha256:d0c3082bf79bcd6a614d55916590ad4b8f93200e10b97f463ea5d9d07c9b5f23 \
+    --hash=sha256:d49c18f1ea294cf4adde2e5ac256e98c82ea9d708462ce4bf799dffa7cfe8a2c \
+    --hash=sha256:d60030baaa7bfbb02d650c126cdcddcb6e33dbff14d819434c8fa2fdcaeeeba5 \
+    --hash=sha256:d7cab119d0df0b9413f106b4d7fc34f2872d3574ed3806fb48959c830b1537da \
+    --hash=sha256:d9b77b25b4f395f92de6099ab08e8ae2bc7e51dfe157f22900902243a5cc90c7 \
+    --hash=sha256:dabee8f4935e731fb46b2a3091bdda0d3d94b3bbfb907d2b4f12eefce4009619 \
+    --hash=sha256:db5e82ba15c142425b8406690032df89e39cca4a2e8afbbb9a3d84edc2373ac3 \
+    --hash=sha256:dc79d36d0618752265f0d575915bdc5c5130ecb9c9f6b3bcefeae32e4bdfafcf \
+    --hash=sha256:ddfa987262763c3c22a8367d2a49c244b018a74c3a8e3ab1a864119ad45c5633 \
+    --hash=sha256:e1172147d28d8fbcf8cb8d26c41506169f5ad8fe9ec969cb116835a19d4d8eca \
+    --hash=sha256:e11edba5bc344a32b029a7af9d4b3173982dd79eeafa0b9dbd787364414b0509 \
+    --hash=sha256:e2c89e9b762c57f59d5e99ee8b20202adb892e35f8d3485741340999ca55058e \
+    --hash=sha256:e31f72490b7c12f7790e1e25c3afffd20503ee1bfb43461d7838b871ff244b19 \
+    --hash=sha256:e8c65ef3862a8ad6e86492b6ed9327805dd66904c012bd3649dc67d822ed6c34 \
+    --hash=sha256:ebb8912f565b8cdbbf27debfe00df04202c20e2f651b9e32767930c5eace3621 \
+    --hash=sha256:ed511a0708e2297e1d6431e7fb217e3402791e491e02da800658ace4973df1bb \
+    --hash=sha256:edf06545875f3efa31560d94121e95c7fd70d98b1dfedc0157097d79b13b52ea \
+    --hash=sha256:f0fe9834e5aeccaf19a0d8feb296d66a24be1a7c9922002f842a682cd5abb787 \
+    --hash=sha256:f1a0d5117230dd46b399a30a38afa44f79c99f3168988fdc4f425c3f928b39df \
+    --hash=sha256:f37964e4a5e993d2fd45147741e9dff7f34a2d8c00ab94c4ea0514a4677f959e \
+    --hash=sha256:f57dc6b8fef170f105d2cf5cdce254f47b137d7755086cf7050f47e16582abba \
+    --hash=sha256:f93bc1c3486ef3747e07c9d7c1d0a147b8fbaab975f80e348aed6f71309dfaca \
+    --hash=sha256:fb00027a09a8f9f08028b40dce4c933cf73e4833240ed356583fdc9cfa721566 \
+    --hash=sha256:fb99cc9d45f48895d9d67f6a0b8a57f08d39c174d9f25ad97a313e0470267b1c \
+    --hash=sha256:fdd88ed5e20b1bcdd234421e454962c971aa44b653bdb7f1ea9ef683e90fb649 \
+    --hash=sha256:fe3fa1dd453ed5c7f5ea23a26218329790ed7197a99b90e94330e313959a7f52
 requests==2.34.2 \
     --hash=sha256:2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0 \
     --hash=sha256:f288924cae4e29463698d6d60bc6a4da69c89185ad1e0bcc4104f584e960b9ed
-s3transfer==0.19.2 \
-    --hash=sha256:ba0309fd86be3c27dbf78cdd813c13c5e1df16e5874b99d2535ebbdfb9892993 \
-    --hash=sha256:d8168eccca828cbb2cd573675333f3bddd254313a9c42494b84c76b539e8ba25
+s3transfer==0.19.3 \
+    --hash=sha256:24eb7535804306355e31c952a90022bf5b2f9d760f9a11062c7493a217c08553 \
+    --hash=sha256:8326acc3d056d7f7b8a37110c7d2aea41f67e83f6ae79cd3b5fbcca34c726406
 scipy-stubs==1.18.1.1 \
     --hash=sha256:1a48be1702cad1ae9aa850c62ed157c988d990305880511d0e38994d502664f4 \
     --hash=sha256:87995ba945f04a3c3fb9cdb5c06d093cf3637ca1271ae6799eb8030b63fb2263
-securetar==2026.4.1 \
-    --hash=sha256:536108c7cec0bdd6fb51abd8d293deba02930124d76ec5dd4599ae5e0c755638 \
-    --hash=sha256:7cf66c204d678b9d1e2d17814c83048a6468e928ea00edb7e6c1efe72aab0540
-sentence-stream==1.3.0 \
-    --hash=sha256:7448d131315b85eefdf238e5edd9caa62899acf609145d5e0e10c09812eb8a1d \
-    --hash=sha256:b06261d35729de97df9002a1cc708f9a888f662b80d5d6d008ee69c51f36041b
+securetar==2026.10.0 \
+    --hash=sha256:0cc81a15b09fab5c1b878ca5ea330033bde444c80919b564185535ff006d17fa \
+    --hash=sha256:580e07109bd5c759fbb25b7dca02bd875db2978c33eb27a8538930d6a802a5d3
+sentence-stream==1.4.0 \
+    --hash=sha256:489f008cbcaa12858088f7f83033c07a85d57b3c6a8ee7838bbfd17dd7058b4e \
+    --hash=sha256:b7c3b9c8d96090d84f07d719317e29298ad897fca666455a12160e0780890e54
 six==1.17.0 \
     --hash=sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274 \
     --hash=sha256:ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81
 snitun==0.47.0 \
     --hash=sha256:264975472011b7a211e44880c614d5534f6fe953c125e0cec365bae3a169c578 \
     --hash=sha256:57eb4710f13a03360c07527c8e2d442b8c90e8ff7b94c71228cde5da8dbb755a
-sqlalchemy==2.0.52 \
-    --hash=sha256:11560064cc4696e772298b6221ede59e646386d9f2a85d549365473b972f7850 \
-    --hash=sha256:1b2d9e507a458832adcfbd8af6e2036ddf069b7710b799448542ebccae2dceee \
-    --hash=sha256:1b92a1e23ed40022081217b40d2d1feba4f77064e69ef4f39f68bcbbd148452a \
-    --hash=sha256:2d5e53e36e37129fe0be8b9d08b6e4052c10a963ee6cda56c8c10dcc194b99ca \
-    --hash=sha256:2e15b1d1116a64fc399b8c2694a83f3e792fdc58df28514a81e1dc4f8cf22729 \
-    --hash=sha256:2eb3c6a64b1bfe6704777cfd504e7b8ad093a5f3e03ce67663a5e6742f294e43 \
-    --hash=sha256:2f5fa2b2aca75d2c7f36db3a8dd04717b6fbfd1a964fb32bdeae16698e475ab3 \
-    --hash=sha256:2f9eccf8793c8c3f8dd2dfd11b9e400cb27d1d19370ef732b66017e212107822 \
-    --hash=sha256:309cc8ba50fc5d2174189dfcd49cdf7aa711f8346afcff19f2642ae4fc449c14 \
-    --hash=sha256:37a4d548327b6cab9c7d8cdb4e0e82feabee0110c4d150059068e2d1cfbd99ee \
-    --hash=sha256:3b81b8363a919ce53453591cdb93702e6bd54ade6c4fa2f468fc053baee5ed89 \
-    --hash=sha256:3c95c3044edddb65e4a2f7194ec52ca5a9736f72d33ca3a6fa4196aedcc689fd \
-    --hash=sha256:410d52be41d17f1a236d19520fbe776257dc16516ed06bd16d433311842aefd9 \
-    --hash=sha256:4699dbb8d396d199e7e78fd4d525e3ad3d6008a9c8c0160b87e74c606c2c3736 \
-    --hash=sha256:46f0c46f0d360d727b84660b26c62b295d82306ec2c82b701e97747d2c6dcbe1 \
-    --hash=sha256:49565daf5af554f538e23aef1fc81a95a4e49658f152285e45c02f5fc44f04cd \
-    --hash=sha256:4b89e93bb89eabdbea9d5d3fa2d6cc6544e733c33064339f91e5292480cf130e \
-    --hash=sha256:50bff43b632a56fbf5ed9afdd76307e1512b62051bcd5afb341ae67205bbb6c8 \
-    --hash=sha256:5e2d46356ac2ccb7d268ab6c2319ac6a2b42f1b8d5fd8bd3d46855cd82abee97 \
-    --hash=sha256:5f8438a98d49424acf69d0d53c0a522951dfe49a6f2d86417fbb37ad3066ab43 \
-    --hash=sha256:651d6d8782e80679e6151707c7b490834d46ada526328895abf567f25e63d29c \
-    --hash=sha256:6c1b7ed45bf87b214e0a9def9c2313949067efe6269db5ef18d542ee13250af7 \
-    --hash=sha256:765f439da5bc8696973bc0c8a31fae0912ac3ff1cb9d66246a6b2728ee4fbbc8 \
-    --hash=sha256:77a247d3fd179f6583171e7e0e98f40dc6642ed4f655557515a5a7e25923e9a4 \
-    --hash=sha256:7a0d48c4b80717c61385b4e966e087c839a66cfd7b780641dcb428f4dba65608 \
-    --hash=sha256:812bae5138bfc0aa46fb0686da0fc7f581f68e2bbb05bc24c3713bebaedd1437 \
-    --hash=sha256:8738008376d22f30f411ea3efecf39b51110b6996d80bb73786f30bcfdd5fd3b \
-    --hash=sha256:8cf993f065bc04caa5000b339e8d9d6f3d9d00251511f850147c516c9e07115f \
-    --hash=sha256:923bb183c1dc64fdf7b717965e3d59938ec4f8b8710b419a21ce403e5da9a9e1 \
-    --hash=sha256:9255ceb65a80c1b001129060b63ee776a2e9c288be3b662be36dfbb888fffdcd \
-    --hash=sha256:938325a5373267afc53bfbe72983b20fbd64ca47842aac62433c3da1137ecff1 \
-    --hash=sha256:9876b09b9f1ce7398b0ffece585c0a911244c53191187341f6bcae640e133751 \
-    --hash=sha256:a593db51b3bae75db17a5738ad5f992244b3a03863f83c28117ee482c6a3f76d \
-    --hash=sha256:a7438774e1091192fc50a2bd8ceff5c596912d00ecd46587e88effdea7826101 \
-    --hash=sha256:ab66fa9618269390d4dfa222f2f2f88f7bc4bf5da13905131b818217db7e8057 \
-    --hash=sha256:ab9da41e61b9979b910499d633b241df20c51ee5037e5405b11c2faac3cbe1a2 \
-    --hash=sha256:afda3ec521d0517d0de783fc70030775841900896d832de5bbd066549290470e \
-    --hash=sha256:b08cddb8989775e3c88799d86704bdfc3ee6e9846118201aa5997f16f27e3a15 \
-    --hash=sha256:be8c49131665dfe2cc74c498aa1240ffb548d0fd901325dd11c2c7a18956f727 \
-    --hash=sha256:c1e61d08bdf4ee2f41024569e3400de7d6734ba498144766b11260936ccfa582 \
-    --hash=sha256:c63bda077685c85ca513286547a531ba57e7a68cf0a7ed3bafcc2bbd18896f4d \
-    --hash=sha256:cce4922535db73f9dbb91e3db2b3e851ac629467fd1ebd8e354a60e369521c63 \
-    --hash=sha256:cd9206024b8602e7518bbaf44016c29e0045722f09328d8e654941023920d0b3 \
-    --hash=sha256:cef328349452ae152637df4d11ce5a0919ecdf0a363e16c830c3518ee33bde72 \
-    --hash=sha256:de89de5b5798cafdd7ef7b7b804acec246d6152922128fd9d156cd1701271aff \
-    --hash=sha256:df8f213ceb485d8227b74935eb87ba0d80169a8401eba7835da6e30d6727dac4 \
-    --hash=sha256:dfe9ce533dbe4d0a2ae1486546619bd30b76bcd670539a44d910361376175f5e \
-    --hash=sha256:e0c3ce43907374889f3352bdcc6195c970148a2cb71574cd0237a5071a37fb6c \
-    --hash=sha256:e49f51a5d59857a7a0dcaf9469febf7197d9394bd88f00d69c2c4e848112cdbf \
-    --hash=sha256:f1c850792a3b25a3ad74dade3f05e4f402cdebfea27438bcadafaa1617f77bcc \
-    --hash=sha256:f2b09029ef6f260409eefa5dc2b8276f6c3d7b892bfb50d50e8f852257d4a6b4 \
-    --hash=sha256:f4d4f7afc682961dc567db70e00a7b5bd81ccd3743c46199b0257f0744902dde
+sqlalchemy==2.1.6 \
+    --hash=sha256:015bd7b0687b5feaecb9988bc2f36ecb39daca83bd806b094b43b19ea503b0a9 \
+    --hash=sha256:048d1beb9bfd7ca1afbcfdb8da9519712827df6cccc80a225715ce387d37bb3b \
+    --hash=sha256:0534d3f41295a74d9fe2e0838e06ce6329a0855b2965df5f5d1c4d3f6f1406d0 \
+    --hash=sha256:0bada6bd29ae58a0581bf6977c0a43dfd67388fd09129f1475c37eca370cccd8 \
+    --hash=sha256:0d0424a4189f95886c78b48bb500a1dd7ae6dbae76deb552b15813dc298d9c8f \
+    --hash=sha256:106878cf3795cd3d357e2e858609f9e44f20f19b2d8e48a3532bef3f90b03fbe \
+    --hash=sha256:10a4fe106adbb46c9452f750d8a5d4013d9a7e9752f63631c3b255c062b748d0 \
+    --hash=sha256:17bc5f508f5e5cee2722a5a14af0a48768b40e1fc5d1bfc92abf6ac587636bd7 \
+    --hash=sha256:1927eabf26265ed962627e7a64626d9058da29cc0faea341091302ec108ce305 \
+    --hash=sha256:1b5885ad1226c8eeea6aeabb4c4036e43202e1bd70cc7a50ece98bcd6ebe5566 \
+    --hash=sha256:1e12763cb2a400879c6dfe34995a032f707de635c8cad14d6ba777a1250be90b \
+    --hash=sha256:1ff897d13de613768123dee68474956a51fe641c42bba7af6cb7776716a8dbcb \
+    --hash=sha256:231d0fd85866f847c34c915116c386c83e677ab6f79a94c835b7ae7313b86095 \
+    --hash=sha256:35348ffcbf686055ea7fd02ba4eb76060ed76761648720c63170c5c8bccd85de \
+    --hash=sha256:3974e33fc322b645eedeac8a3dea93022466fee41a6385c744a6656aba293cd4 \
+    --hash=sha256:39ca3a128260fb3aa1c33554f1993bc5ddf3f82375697028c49e7b411ab80b84 \
+    --hash=sha256:3d877b2c46298825e8f32059e8d912d0d100af0e9fefe31fb2abb52192817afb \
+    --hash=sha256:499eae5c9051efe96cb9a73ec2fbde8ffa4186f102b9094ebab8fcc9d3b99f52 \
+    --hash=sha256:5a9b4cbc5f5cda3c9429e1ac503a57f3b95c59886f26af6ffb44e2e7628b7df8 \
+    --hash=sha256:5f9400b1234555b9ae78450123dec7aaf045d8d978a1e94967437ebe561ae120 \
+    --hash=sha256:61dc3fa488208a2f03e0e25ad32950dc024545291acc7348f2e550ea1bc5abb4 \
+    --hash=sha256:641a3742dac4b8f325667b585097de0f1d20eb3498506c92d5f04c20b3a6c823 \
+    --hash=sha256:650f97996a4c529f4930969f3ba11bcdb57ff160ed1cb87ea0174393bf4f5f73 \
+    --hash=sha256:654192c9f192459ee5f63e6606cc6dd8c50681c28e0689d2a494fc9522b357c1 \
+    --hash=sha256:69eeb530ce74be5e202a98ce35aa58b0776c24e64923c4873c25fa56f8e423bc \
+    --hash=sha256:70b435f719d7156623f49ac6539f30dd8471500b5acf399f3b318c1c17f6fa7f \
+    --hash=sha256:73aa8d2f911a54d1310e8258a752207e2d7624f4db46e2320d734fe7218320a1 \
+    --hash=sha256:79c1c20dffd4d8d7e669f096c88f261da8ba3646939cd3eb6faeccb92bae99c3 \
+    --hash=sha256:7ea80b33e57f918509eb91cd074324bff0f9aae40d238121cdc369f449c20649 \
+    --hash=sha256:80009748a5ce0c51a9947542935f9709a1c48b65c69f4a1e56d3072f99e750f2 \
+    --hash=sha256:84033cab9fec2a515a62d76a7b4acafa83339917db9ea911b65b017928ae7dd8 \
+    --hash=sha256:84b359a458611d40061f536b1363733b0af7a71425e4b17d0abb7e543d00e979 \
+    --hash=sha256:89d05a1ef531a1fee86d68e731c428b773bd37aabf743bf63dc3709c86f7254d \
+    --hash=sha256:8de444335e3723959913f6635d579276a3517b8c19cbdfaefb04e73b5480e88b \
+    --hash=sha256:8f9d12a8be271c7a83ded1cb7d85921f1b7f65c655c8dae972130a190211bb57 \
+    --hash=sha256:9245bcbcc3056d440f82e43fb34f94c15361c86b62e14cd9d7880c8e0cf370f6 \
+    --hash=sha256:96ace18758136905f8d5588ec35d6ae4fdc29ce4e4902518263ca33abf10de04 \
+    --hash=sha256:96f5fcdfb7e89b6d895e2ddc165f67b3126a585dfdf2a95b0c1f3fcf3380d7d4 \
+    --hash=sha256:991fa7c6756505e3dc5aad678db5fb0110d9816c2185bc3e2c520de46cfc8c5d \
+    --hash=sha256:9b197f5d2bcd61b939d2f04b77e86ef24bda266518f3e1526bf666deb20d3ddd \
+    --hash=sha256:9b6b5fdcdb6891025117f76f48d7d0f89245d66fab6519f3b856294bab317387 \
+    --hash=sha256:9bd573f8da863781ace89950d57a959397d5048b1cf69931c29b2b4ce1405bd7 \
+    --hash=sha256:9db8bacb2a69b4b5388bc1439463170af28f4cc710933085b81d1658d931d2c2 \
+    --hash=sha256:a053a9d9c9ccc9b72d90ecdcbabcbe57446defc7e8c52fc9978188f78742ac19 \
+    --hash=sha256:a4e4782514c16753f8bce3dd925cd37d26c847bead06e179af6fa4993ce83e88 \
+    --hash=sha256:a909a8eb82ce5a2f1566ebd685a79f3cfd9e049d57e3a0d3e24d56da04913e73 \
+    --hash=sha256:b16a8960ad9cdc923b90dbf431a4739fc81a07b53374ff74b7bdad3be31ce189 \
+    --hash=sha256:b25199a1b499da643de52ab73e972eb07e55e2a95bb99eaa491846098fa2214c \
+    --hash=sha256:b7ddb305126d34fda64c3fe4632a43fb9b724da6cc7d1dedd8434e6c783b285b \
+    --hash=sha256:b9f0b92b4a88b630f1e67df816b43cb017bb583479917dd100541d4f490a9517 \
+    --hash=sha256:bc495d00f235c3df6f376187a4ef48a56e162fdcc0a113ee34518332aa1aa2df \
+    --hash=sha256:bc8b805fb04472e0f9cb3bc6aad90f24b202afc274b7b8bbd48042130e82997a \
+    --hash=sha256:bf883ae772971bc6155cb64cdfb9e31c50a2099f3b7c8b51b0401bf608a9fe8e \
+    --hash=sha256:bf937348d4052eac6cfa93c809ad214be75b1f057e3fc0dd2e374a814a23a16b \
+    --hash=sha256:c314bf9026d865c2b2f67f3b853b4e2edcbe7ed46b67ef11b4a40f0af6aa17b8 \
+    --hash=sha256:c390f76f2fe408aa1a3121f3ca3d5c15698e14d913197417355fe3dc016f787d \
+    --hash=sha256:c757e13b63a25d59a2566c9b2e77adf14d969207a375ca82a9b4fa1a04b37845 \
+    --hash=sha256:cc60fffea328f38187a4fce43f99c6bbf930de2b87b78251f43f2ba64a1af622 \
+    --hash=sha256:d106c2191a3a0dea6873c96ab909f31c13978913714a25023f492e9ccc8ffcc7 \
+    --hash=sha256:d5e4b4dcf85d7f289def0e3167f15aaad101b7744a065fb2019476edf306712c \
+    --hash=sha256:d6e1a9ae71366164800942c477e663b31f3accef55d2e039cb7919fdb54b0086 \
+    --hash=sha256:d8c34c200a124a1a5769671613b3fc05a21d0a50f7ad942cf0ee12d4390a112c \
+    --hash=sha256:d96186af967d7ae3f76d1e9a8fb70b5beb0f0dbdacfd3b418a946fffbb8781ff \
+    --hash=sha256:da21b36d60f47dd04042e9372ffb3d1ededf5c60a76d43f8c3592221fb2d41cd \
+    --hash=sha256:e269c68ec200538ae3fa7f9e8d8ed2b4b34d974c25945286ccc2a488438acf32 \
+    --hash=sha256:e4e4a43cde0dcdff974304ddb48246d6a094e618b6ee9642827ddbfe9fbebadb \
+    --hash=sha256:ea5f3dd7450669acbfee7813d3a2a13876806b1d9e4c1626a7bf587c33c68472 \
+    --hash=sha256:eafb738fbcba39d12543730eacb65e2d5d627965959b3cc6bd6f797b2d52cc0f \
+    --hash=sha256:ed6596fb63c574fd3dc4d9ea58a7b9c6e7235dc3d74a0bd3791559d5a618e947 \
+    --hash=sha256:f0f22627d6436bd120c6dde0936b12fe75498d1e2e9214ec9863be17f9b80997 \
+    --hash=sha256:f1e78019147ff7e08afaffb88fc3a0aa795171b147eacfc7ff873ce7a0d37dff \
+    --hash=sha256:fd1154c6394892e727ff234273f5eb2b4319e5714917b016602435d77add8dcb
 standard-aifc==3.13.0 \
     --hash=sha256:64e249c7cb4b3daf2fdba4e95721f811bde8bdfc43ad9f936589b7bb2fae2e43 \
     --hash=sha256:f7ae09cc57de1224a0dd8e3eb8f73830be7c3d0bc485de4c1f82b4a7f645ac66
@@ -2792,9 +2881,9 @@ threadpoolctl==3.7.0 \
 typing-extensions==4.16.0 \
     --hash=sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8 \
     --hash=sha256:dc983d19a509c94dba722ee6abd33940f7c05a89e243c47e907eb4db6f1a43e5
-tzdata==2026.4 \
-    --hash=sha256:c2169a8b0a7a5e9674da5a135ccdfb2b3e671b333ed9fed17b41f73c34476e81 \
-    --hash=sha256:f1b8bd365d8d210c55353f4d7f8d6d8561c0ba50d704b700d195a9424bba0d79
+tzdata==2026.6 \
+    --hash=sha256:0a10eec6e13ef16b627fabed9a5f2ba61a62b1c67f327305f4e7e412a70b4aec \
+    --hash=sha256:85d2cd9c09f81f0bb29db27759fc83af4f1e620efb814f8c5bf8b4cc4feece6d
 uart-devices==0.1.1 \
     --hash=sha256:3a52c4ae0f5f7400ebe1ae5f6e2a2d40cc0b7f18a50e895236535c4e53c6ed34 \
     --hash=sha256:55bc8cce66465e90b298f0910e5c496bc7be021341c5455954cf61c6253dc123
@@ -2852,26 +2941,26 @@ urllib3==2.8.0 \
 usb-devices==0.5.1 \
     --hash=sha256:8ef45c401490391a3651b3ba748eb213a654ac165be10a0786ab963668c49cc3 \
     --hash=sha256:e77e7972b5ac6a883b3778b0273d9582c5b8ae847ac78fba3d080dd4a4cc69ad
-uv==0.13.4 \
-    --hash=sha256:05e4332791b4d55b6dde8695b7fa6079b26991519f44760887c5dfbd5ca4fe53 \
-    --hash=sha256:205a4f93e568fb24f45a2f3834f1c0a8f1adb5f396bf473c71030ed707dce048 \
-    --hash=sha256:25cc14ff4fd8335d3be2cc493a621a003fdafcb0fb1c953c905daabe4def5ab8 \
-    --hash=sha256:3a9dcb6762c3ba249d8c084315ba03839082af3ece3536cc4164ec735c351d68 \
-    --hash=sha256:4e6b08578c920b86910897f36bb6da7229c8e7e0187976570e2a538cb28b777e \
-    --hash=sha256:52b5c753a7c2d5f8323a70bb4c93118988356331d0758afa6446c81f974e7196 \
-    --hash=sha256:5d89d1028c2e22977d9215cbb79cfe12559cb0c8a507a12e2f3a7e47930cf1bf \
-    --hash=sha256:77062b02856c74697f48328d8a6583ab07e6da0a993e86c2db46f3d1da27c637 \
-    --hash=sha256:7b3cdf868e5415631fe797b648c0d6945d38d388f23367bdd0b6332e80a1fcb0 \
-    --hash=sha256:8ae6ff2b07892379dc767c9064c2b8bbfac88e767edac7ce28e1b0f15d86abb4 \
-    --hash=sha256:95f4eb2b991b53b50ec2b18ab612fca8ba1e7a75a47af0331fb8bcd21da3eb03 \
-    --hash=sha256:b0bff5b9a5061f7a35b1d0c1a94c19af134222c48eb7aadc42f85a038be1b248 \
-    --hash=sha256:b2ff80397273fff0e02c20eacae6882834c811827d6fc08f658db156fe754386 \
-    --hash=sha256:b4bbacea78c9db136cd2ec3147cbfd9ed910b4db5e1877109bd74d0e73bb2eaf \
-    --hash=sha256:d333f01852b817ba05612de31474739da1af7e5463d119b30a9c4331eba1f408 \
-    --hash=sha256:d86a5dec8ab30c70519c71ca5085c8aaf28664836cbc600951cedaa3fc678cbf \
-    --hash=sha256:deffa5a4afdb48f3e44fb26e80377d256b330ddcad0373daff4b54f6162b43a4 \
-    --hash=sha256:e90ab42825587821096cb0d071e387468da38cfa22818c91f9c0b3c0453048e8 \
-    --hash=sha256:fb0e2028d9a8929884344afb7d91d0f65d9783f640d28aede89fca3602bedde9
+uv==0.13.6 \
+    --hash=sha256:1cd4b0a35fa599b83da5437748150319ae0917c522da60898327645382942faa \
+    --hash=sha256:22759b8895e1103578de6fb4cd27e94b4399d021023378d29f01333717751fba \
+    --hash=sha256:29135609166960c74539abdaf4264f9819a0381be18b224125418356d67dd208 \
+    --hash=sha256:2e9a99100abe4f99605366974c4f9fe27f236615e05de8e78c0f357e38f09f97 \
+    --hash=sha256:46c2ef1f744f20007be0cdd66db3022bb1ddcac477c754efda875e401a48d810 \
+    --hash=sha256:4d20de8a3ed6c3d39b4e2f8f7d0411cd13a3959f5191b2b5d0209344034ed056 \
+    --hash=sha256:51361029b7cf91185d0092c4b356d110b4ad629e9cb11593f1e006ac72a72ca9 \
+    --hash=sha256:710c68ea4853aaf70ab2d0ccf2e147dee59449f035a1f8fe7759f087a31cdbf5 \
+    --hash=sha256:722c7f96803f115e53918b8ee8858d1680ea6077c614b6db750747d709ab8d9a \
+    --hash=sha256:7c9bc35ccb65932d8dc10a0669f9c805eaa3c9827ce18ecbecb1bd67944b2cdf \
+    --hash=sha256:7ec5486476d67a4214c460b5492393ee2300d84e1de17b293100a019b413568b \
+    --hash=sha256:8542dcf118ce8a7cf2e4ba1fea7f5cc1638bc02b5b30dab1ead7e9034dc62fd3 \
+    --hash=sha256:95f042b95e67ef8c3d3569bb6e9d895e592002c5e871cf3f1afe407c9d77a294 \
+    --hash=sha256:b2d25a49d135a441f688a6869d6d8062fb6f0a2e3e32e18b72c9de1d0eb9521e \
+    --hash=sha256:b9f57153fc98b7aa41dd6720e3de7578747f60b7bff22f50b76dcc47205bdde3 \
+    --hash=sha256:d1efed1d15102ffdbf5e0fd49a440643dda2d921a2ad856792ae42ccd43c253f \
+    --hash=sha256:d4d7026c7327dd11fc2c0d4bae4735ff6944293d370644f35d2e6e917cdcae04 \
+    --hash=sha256:d762215478854f6cf20c3faed8f1eb30c8101d568e7bc32a3abafc063929d5c5 \
+    --hash=sha256:feb0f1d555798f68f28719cab437ab1dfb5d918db86ab4554215cbf9d940f63b
 voluptuous==0.16.0 \
     --hash=sha256:006535e22fed944aec17bef6e8725472476194743c87bd233e912eb463f8ff05 \
     --hash=sha256:ee342095263e1b5afbd4d418cb5adc92810eebfd07696bb033a261210df33db4
@@ -3017,86 +3106,73 @@ yarl==1.25.1 \
     --hash=sha256:f53dcd26694f148f738edc052b5a69234833e739f10f4c3287bdfd8ec0f7b326 \
     --hash=sha256:f61964f235a43738bfac50da46fc4254943a7eea3051aeb0b6fc7c992c29fadc \
     --hash=sha256:fe01645169a2112aa1d4ebc3e4c5f029c5c8f97adfc32e5d37c993b39a994d75
-zeroconf==0.151.1 \
-    --hash=sha256:0225972a655fd49028decd37139a8deb2a8287661f5ebd6c8c5ba268d5b05999 \
-    --hash=sha256:0add63648ee172b37ce696bd4753ddfdb828ea0fa1005b8a958e700840a17b06 \
-    --hash=sha256:0f95157d58c0cc6c054769fc8e0db947bcdc3103450cbcb1786b6aef8cacd1df \
-    --hash=sha256:0fe95eeca340f90a9b2a1ca9c5c0382770ae20da6999188833e59a154f591bc5 \
-    --hash=sha256:125203ce7c8ca310599feeef5e24a83aea73d5100dfcb6bfe250ae0578c3cb41 \
-    --hash=sha256:1848ce730d6a9829271e7cf9b7166278736b579e382127978110d5311132c63a \
-    --hash=sha256:19848ee652ca2b3b849b6ad6c082c4ac43591c6450d5329dd2bf3b1da074454b \
-    --hash=sha256:1c52e92260638b4d912cdcf654b8fd3c425ad9432603f783524a816bfce36ab9 \
-    --hash=sha256:1f68ddfece7f059e2fd3568c658c4cd27802fe41a4c48319aaef75c12093ab35 \
-    --hash=sha256:252ab0b89399fc8b63fe57a14a33345bb5ef811cba40234bf4e88efd8d77b578 \
-    --hash=sha256:2594832108af9a74eeebe87af96666ae24a006cb7eb8ba80073144dca8291610 \
-    --hash=sha256:29e1f4ec75232904b23883a151e75d1ec72ca909b41d2129156192fa26b7d671 \
-    --hash=sha256:2abaa42654d83c2f24552659ec2512f735ae700be00621c5cda49ab1852ace57 \
-    --hash=sha256:2aeecc65c3ff2951fb5dd4d5a46c5837817186eecdf207327737cdc9ccd3e69e \
-    --hash=sha256:32373f14c32ad72887135a2bd8c1bd07c4b0693841358be7d5f89728fde9e5e9 \
-    --hash=sha256:33d836ff901d074312500b3b5ae463154039736109469999220ed6746a05dfe5 \
-    --hash=sha256:34573b41d2feba4a032fffc3ed9a9f327078bdcec88f5743f601892d63c836c0 \
-    --hash=sha256:39a11cfdf26473e717613fb03d8f35a8cd6935c7d8bcab3a03775f1583ac5465 \
-    --hash=sha256:3b6da862e7fa84e3b6427c09d7e14610b27c91e4e4a15a5a987ea9440925b1f4 \
-    --hash=sha256:3dd3460e31949f740ceb11245a197f9c7510be0a72bb7c977a02a4b4b9b4498f \
-    --hash=sha256:41e48e764f88a15b7e9610d7c0902c4987c22cd737a94330cf5f9475521c6589 \
-    --hash=sha256:466ed94851ff9b3f97d7e35f19ac8c20991914ace4f709856d3b80dad665f635 \
-    --hash=sha256:46d36f552520d84a553de616794c843e42bf57dd8745783cbc32ec8914a4beb1 \
-    --hash=sha256:4755b8363d48fe78d313ae336a7ebd0d8d85f70ed5a76192189edc3eb3b55693 \
-    --hash=sha256:4b225f030c98d5ff3b72926d68a320adafb785437943a6b405cfa012c9cacd62 \
-    --hash=sha256:4bc0c1b74ee39aec39c8e12cdf5520b1c286bb1f49b2b717308f971da04d2b2e \
-    --hash=sha256:4eb3cb02549d2e869d2fd740f0f8bfdce7583c790a2983ce870e9864baa06402 \
-    --hash=sha256:5003d92dfcf4a2f7cef56836a35ff2ac5dff79b4aa877debfb5c81430b0d8023 \
-    --hash=sha256:52f61e239629e3137b205d17e60dc95eed300e7cc67ab66bd3c8989b6eea8779 \
-    --hash=sha256:55cc03275b0e05c947280453671fb2cea118fbbd14b9cec6dc156ce8560aaf0d \
-    --hash=sha256:571939299cb8af40086b8f339d364c711d6c058e3aa935f00d7a406bd33a9619 \
-    --hash=sha256:58d8e8e647b75e84db5aeb36a3c8e92affea258da407e664b66e7c3a09126fbe \
-    --hash=sha256:59877c71cf235897686005eef6b5004b4ab8b0128082f0c46c104adcbc81b01d \
-    --hash=sha256:59c3dacc5cf509112a513504ea9b2cb7e4394443425362a425dfe535a1cf7315 \
-    --hash=sha256:5eb7886e8728b4cc85f0cbc8f6ca25e93c68fb9eaea343b2fa57bea504f139d6 \
-    --hash=sha256:5ec0bc0ca3ecf990072243ebd3e2b351e0dab6e3ba4328613afc322d6b7cdf38 \
-    --hash=sha256:62907c52238c3c88deaeaeacf0da2c6f9fb31e18bfb648a6dd00c0e951735b0a \
-    --hash=sha256:63d94c3c7f3bb841d39c6705a9c060e418f37bb880c8f7b19ee2e1725ab1cdc1 \
-    --hash=sha256:643b79661a9894fe1c77c7daf9175b1c2800f536a39d71557c0a488f70005189 \
-    --hash=sha256:6a1dfd15fa2f00709e2472e969990ddcdac86548bdd0fd2f866aedd0ad50ec2f \
-    --hash=sha256:6d90dc5525ae29d25a1e9d8155d7cab72b2317d90cb094dfd042312d9bb58ef3 \
-    --hash=sha256:6dd29e382936871e685de4efc6089dbe56d6cd93b54267c66847321046da4638 \
-    --hash=sha256:6fd382b515a8ddeadd44e66852d570da94a9abc609b356e7f79ab3a65986219c \
-    --hash=sha256:727c6491708341f1a951500ee8bd46ad88d37c1a1180de4a3582ff6c1619bd1d \
-    --hash=sha256:733490a86d56f9cac2de70b51751746074b9c91f86efbef9fe5aab4f657dc945 \
-    --hash=sha256:73f7ed206f4f05f63b45eb3ce01faf0f0de7806e852cf98fad201a8245efbf1d \
-    --hash=sha256:76cbc5ba8dd141ef9af3f275e2820a01140bb32a8a079e663e951a0e40bef5f0 \
-    --hash=sha256:772c1a0750631901ee74fc2e3a5bf4742ef1f01ca6b9156bb0c7e32f83a6598f \
-    --hash=sha256:819be9bc551369606b13e06b1f280baf3a81a71da1fbc90603b802e28126751d \
-    --hash=sha256:8c4e99dce44d7e630026c4adeb96352a82384f599139af525f67c9c6954ba4ba \
-    --hash=sha256:8e339e6d03b710de8e1c80573a3c0d401d27ab92bb0e44c6ecdbf8a725fab920 \
-    --hash=sha256:90457baeae87fa5901d9eda62c84f2b3483820eb6294620764e7ea22dc1ce4b8 \
-    --hash=sha256:92ba4f36012387b06943ae553d0649b5f5714f8833cc7daf885c1e0ae768be56 \
-    --hash=sha256:9897a36e9459aba29d0bdce4f065e4a1a184e047eae1e56935ddcebc85a65bd8 \
-    --hash=sha256:998c313a2e6388fd3612fc9b11e7d4257e273a7add757d665e62d154dab7b2f2 \
-    --hash=sha256:9d9a4acec72dda072357860134bc6351e4893fd4e13b8cda6b1d2aa6295e6144 \
-    --hash=sha256:9dd35e93850ff78f8162a1d618efb2db25a66cb2d58520451d5292c975737ae4 \
-    --hash=sha256:a3f69d9a58b9f28a208cbec2608135134f47a202ae160d9a762ab84c2ad53d05 \
-    --hash=sha256:abe69cb51b7d0533c45b352c9132d6e033214deaa334a21091a2ed10cdae1dea \
-    --hash=sha256:ac0190dfde1aca59c74240f655b18c9f0b4984249599b89677c6374ea88f6c4d \
-    --hash=sha256:ac3903c34d65a8a00e159368458a397050159fcc4a8fe594950822492ae1c56f \
-    --hash=sha256:ad88554312440642558137464b71b13096e68b01d10b31a4066e77d1414ae560 \
-    --hash=sha256:ae92202269cf437d86f90987b05cb50a21a2a3f5d55e100bad595f21af6af472 \
-    --hash=sha256:ae991fa56aa434bc145245cf141234fd2bcc4368985bb490201a73e8f4142f93 \
-    --hash=sha256:aee18006ed1e5f7bac51c289da74fa46aea36a84e89961560cfab73b5844e345 \
-    --hash=sha256:c23f00508fa0494352ba46b8c410fe39b195e7f720765e551d937149b18c48b9 \
-    --hash=sha256:ca2b53b662f47c0bff17e4d6ef2c96afd2ccf2e3a7f36fc1caf8319dc5fc9a63 \
-    --hash=sha256:cd96e2c53d9a78ec167c7e4ba4ff22ec919854205b9ee0b5bed71d0dfa3e6412 \
-    --hash=sha256:d0d06dfc96223a64498201eacc77621174307b0a1a58349aeb687f59761f53d4 \
-    --hash=sha256:d213b1445fe05cb8ef073e0c96fb9ef88c55e6194a896b527a25cc8bea0c5538 \
-    --hash=sha256:d51539015ff87c7ae19188221df1fff0375aafb546bf6b963655b72019045496 \
-    --hash=sha256:e024d96649cc158cb48ec3d13b179c8e41a7544023aae1415fdf325c0ec97007 \
-    --hash=sha256:e45080633cab548401805c91f2f1d50ecc5d60b4952a631e660ab5c620565d70 \
-    --hash=sha256:e8e5d32d2fbb6c81e80bd813ac61d468db4a2d2d04530611bc16f18483747669 \
-    --hash=sha256:eb58c6345221b18e3d5f344a2f753b0098f3f764ccb031f2aeef4805b349b7c6 \
-    --hash=sha256:eb8e694ea9adbe5829e8569510c2173ecc14c1b127c2153cb709d3faad07256e \
-    --hash=sha256:eb9a98bb424fd7b0b39aab09665f56ae9570f99738343fb89707cff79e318166 \
-    --hash=sha256:ebfb7143610f4c0443c983c50b9ce6474bd785ecf8f2075df8164b1f9fb660ad \
-    --hash=sha256:ef3c51a642b19b22b794fea3c7e88d35ebfd5cb8ff16162840c56c20d5f4e229 \
-    --hash=sha256:fbfe2d2e644cfefea21c87b4b91de3b85ade52a26ceb53146cb537a3326b3c42 \
-    --hash=sha256:fcc26580fd7aa90a74919d234dd83cd3b6daa8a759bf7b9474428453d4fe66af \
-    --hash=sha256:fe794de3da819a73a01afc9f47a6598948ae5c90f86e76fad23efb971b198d04
+zeroconf==0.151.5 \
+    --hash=sha256:00ee9d456519c45c94201334d5cbd2699d5de9cc9ceeb647203b85295640abab \
+    --hash=sha256:05cdec63c6bc2fde2086a174339b40947bc30eead775effaab90c20558835f89 \
+    --hash=sha256:09a933cd3a4bb6a5a0eaf84b58aa0d32af330aa81aa75fc0e300551ccb9b775b \
+    --hash=sha256:11cc483a2fb4a08c8f3456d574c4b64dd8413028fd0bafc8eae77987a63f04c7 \
+    --hash=sha256:137f3c5cf600fccd100513e6d22a265d1b0301278607b84b9eb2de1e54c72fde \
+    --hash=sha256:1ab36f829be85f6546476be525463879e11ce67c6eb18d0b01b1c2b989ba35d0 \
+    --hash=sha256:1ef99729ee6109f08ebee6ce7ef7bd4280747848550462d40275b059e3eaca57 \
+    --hash=sha256:1ff72dd4ba1549814dcd87104997f324989fc2319558e6f4461931c4fc7dacec \
+    --hash=sha256:2304c3fd4717422242cc78315b37d48613109963900e0c9a2b784a91fd6e9c0e \
+    --hash=sha256:23f5d281c130af8f4976a611a1db196d17395d69815aeff3537a599430b9ca5a \
+    --hash=sha256:244d853ec76620cd31c5c4657cff22fb34e181826d833134244135202f92888f \
+    --hash=sha256:28c2ec9d772007eedf11b41a9c9fd3d5c684c17b00721ff8f1ee31b20ad286a1 \
+    --hash=sha256:2e843fdb7249cbf612cf0bdb729d4581d057b78c45423bd46a6bf377832b4ffc \
+    --hash=sha256:35b908297f4a36b5a934aa25dbcf5078bd26fedd7203bf92506041e0bfe32616 \
+    --hash=sha256:37f8a073825a208878e994300c0feb7d6b253e2af3d258678a8beec6b020506a \
+    --hash=sha256:3cba88b0fb77ea1b4dceaebae577c8245852159c525201b2453cd3bd5715cf56 \
+    --hash=sha256:3d3d2f0eb51e605f2010e83ab49db34c70c51304ee88a980ed1c59c0ea20b82f \
+    --hash=sha256:3da652fc2d7ba788651b8713340b6470e7218f6fd8392755666a49636d9d3383 \
+    --hash=sha256:422592b2d7dbe8c82fb0ec38f33898fa4a580587a8ee9a1554d1d5c477cf7903 \
+    --hash=sha256:44b34921217c4387cdb0b4b08ae510d9adbf76e80a3b84ae3f7c1f8cdc60c436 \
+    --hash=sha256:470ec9d7056d8e4d22e22c699a6e2e544c3e0b7bb2d49b700ef516e18d5b67a4 \
+    --hash=sha256:475e527d371fdc8d29d10cd2300140e735a8562df041041465704cff63452d9f \
+    --hash=sha256:47b9f3f49860cb60dd5d1453c681dbcced4cac96960935f1b9f7c24d7f3993ce \
+    --hash=sha256:50f67bf880c28ddc1d8c5717d759ef955a04066e5c9dbfd2dabb0489d01b7239 \
+    --hash=sha256:532e28946f6b384369747771e71094f76aa75b4bc2dfba6c099286d90111caf0 \
+    --hash=sha256:56060316f3464c86c1fbd32287ffab28fbb9c539ffd6a6e070251c455252c50c \
+    --hash=sha256:5846416ae2bddacb1bbb755233dd13c4bd15d94dfd0feb23a4b1abe1e2312302 \
+    --hash=sha256:5cfb9d625a12bb6788c142bd238479444ba43b8cbb56d6e0fd2becc17ef8e4a3 \
+    --hash=sha256:5daadc4306a6def67187dd8a4ee15978d0c4d425bad4dfef7b2131e909edce02 \
+    --hash=sha256:6385a69307ee9ccd71d0d2374f0a822590e2468919acbd4ae6bf3ab5f501a1f3 \
+    --hash=sha256:667d8fb8f6cb02d9e28085759f5c336b26fc596ce427a36dbb20ecd440dfe029 \
+    --hash=sha256:6a4bde05914a6dc6a4de83fb9f85ebcbf7fb1c89d9021122b689ebb6aa9d717c \
+    --hash=sha256:720a872df2924faedd33c737c2b8a4ac43c045b0b278c58d8b32e1eadff4fa9f \
+    --hash=sha256:841b16e18846132fd555cba136fbca2ff33ccd5b332d2c54293ceba242851e7e \
+    --hash=sha256:849c312c7c2f23f1e681ad8d3d2ca4189fb4df9cf426ad1933b3ad0403a5b4f8 \
+    --hash=sha256:8905f5ccf8cfa7e767dc9b0dd009e2787f8d8e5595f2a6d9c3e956cbb1a397cb \
+    --hash=sha256:8b15a9ff99c33622daf4a9b3c0bd0aeac7532b86d62e80e03fc3fab7e154140c \
+    --hash=sha256:92d5f219f09a45bebf28ce40776dbc1f8a0697871ceda8b6b9f2ffe8209826fe \
+    --hash=sha256:92dc32ac2ce69967d288091106581da063136441bd22ad8efd5bb611d692b890 \
+    --hash=sha256:92e9a1494c5938ca4e426150a3ad575e9b2ca14cc8af9372124d8800d791b1b8 \
+    --hash=sha256:9583f52f51f08f7b14e9f09d99cc0e5ed29afd02bfef6f9d89f175a3e3582a33 \
+    --hash=sha256:965d9e92ad34896a2537352a37affcff2daeb8c7af2072451220e753f0de990d \
+    --hash=sha256:99162e67862c2f17aeb5a432c70757419573e33cfab925eed566f8bc2a346bcb \
+    --hash=sha256:9bfb0efd3d9259e3a5e9b2373f895900ea3951ca843be84772b6726b8f16dd60 \
+    --hash=sha256:a382205700aa8ea63634b4a92b41176a6033bef7ec2380bfd0503e3e11e6d598 \
+    --hash=sha256:a48fedd887c3bafe45cf24e08aaa06a1b641ec3403696f4a01701ae64c9088a0 \
+    --hash=sha256:a561c0d95c96aea326bbfd8577044b22499a6154c4ee6a74bc70cd0cc1185743 \
+    --hash=sha256:a941c82401ae04d8548cf3567b22347509b589a867adede2646eee9bdfd4f446 \
+    --hash=sha256:ab67bb2233a0d9ce7d71d01b6791dac50d56c5a814ef1553ac97ae9c43e7eabf \
+    --hash=sha256:b124e30e18f29690907f7f7ed8b79ab34fa8f40fe300a6f5a8f21b04148497e5 \
+    --hash=sha256:b2c0ec31fd0195b3f32dcfb4b6133189278ad18fb27f88a20857adaa8d1589ad \
+    --hash=sha256:b6715218b4348b306ec11799cbc6e365fb078b60e0e5a384c5a6d5f48a495025 \
+    --hash=sha256:bd773d22ddd60f696e0be063a925a9d34f8de7bcc40e4b9c9360c9e081f97ab0 \
+    --hash=sha256:be010daad6e60fbdbbd085c6873dd9b491b2cd1e93f64e4a58722b2db72c2b9b \
+    --hash=sha256:bf19169739ee8608748db3533670f1f8622727e4cf189a7619eadf0895ccf2dd \
+    --hash=sha256:c1f45df00d20918fc7a0c2a6229ae1f9b44fbbef6a161df96c7710098c82e019 \
+    --hash=sha256:c24366d4e60b72adbf6fc954fb8df6165dae44d137f5c8afd8f7272995580681 \
+    --hash=sha256:c3f34b0e863f20af95fca7ef5871536015c964ce07462b6462c3246f6a385177 \
+    --hash=sha256:c6f98dafac6bacb715fd6644921a9220c09499fcaedc308d27e6fd4fd157837e \
+    --hash=sha256:c967096138b7a38ef51b54d71966ec234e1c0353485ab1925b845106db938e47 \
+    --hash=sha256:d702be8e8b456470af59fb268b4756c96b4754c7c4ad8c38035c7f0336ac35c5 \
+    --hash=sha256:d81e8e2c70cc590573069fad9036d1ded7f135c92ada79c89fe547978acf2f90 \
+    --hash=sha256:dc7d125bd01eca9f63e7c65a3e52a81e385ef6ac25721bc67e15b99efc3ce6b0 \
+    --hash=sha256:effc02f3ac1b39828b47db5f7c386b57699e2f2292d9d773879a9d1f9ef137b3 \
+    --hash=sha256:f13dfaa9091daf9c30198149b5d414bc1e92f25aceb0d8d9c9ca3f7ea7a239f8 \
+    --hash=sha256:f346b414b882ac0dee5beb55bc8bd6ad8c7415f26d6ab4629d91bfd6c5f30f62 \
+    --hash=sha256:f5e17c8b93fa9da4e6b125e2dd844cec3c5fe60af223ab6e179ad8ef0674fdbd \
+    --hash=sha256:f8f7ec289a07acb9e272d0f2998759b76ec81dd23b15a7506e05689f630fafd1 \
+    --hash=sha256:faecc5a1f318a920a4f7052a14391ae6def8fd6035313886e88f53705ad9dc8e
diff --git a/tests/typing_budgets.json b/tests/typing_budgets.json
index ba0456583..14da015eb 100644
--- a/tests/typing_budgets.json
+++ b/tests/typing_budgets.json
@@ -38,7 +38,7 @@
     "They differ because only CI can measure the census (#504)."
   ],
   "ruler": {
-    "mypy": "2.3.1",
+    "mypy": "2.4.1",
     "homeassistant_stubs": "2026.9.3",
     "python_min": "3.14.2",
     "python_version_flag": "3.14",
diff --git a/tools/audit/seat/cloud-setup.sh b/tools/audit/seat/cloud-setup.sh
index bdc0a4378..480c5fdb8 100644
--- a/tools/audit/seat/cloud-setup.sh
+++ b/tools/audit/seat/cloud-setup.sh
@@ -12,8 +12,9 @@
 #   venv-ci  tests/requirements-ci.txt, hash-pinned: numpy, scipy and the rest
 #            of what `fast` installs; first on PATH, so `python3` is this one
 #   venv-ha  tests/requirements-typing.txt, hash-pinned, --no-deps exactly as
-#            the `typing` job installs it: mypy, homeassistant 2026.9.3 and
-#            homeassistant-stubs 2026.9.3; exported as HPO_TYPING_PYTHON
+#            the `typing` job installs it: mypy, homeassistant and
+#            homeassistant-stubs; exported as HPO_TYPING_PYTHON, and asserted
+#            to import the lock's homeassistant pin, read from the lock
 #
 # The pins are read from the checkout, never restated here, so this script
 # cannot drift from the lock files; a lock edit reaches the next session.
@@ -177,7 +178,8 @@ pins venv-ci -r "$REPO/tests/requirements-ci.txt"
 pins venv-ha --no-deps -r "$REPO/tests/requirements-typing.txt"
 
 "$PREFIX/venv-ci/bin/python" -c 'import numpy, scipy, voluptuous'
-"$PREFIX/venv-ha/bin/python" -c 'import homeassistant.const as c; assert c.__version__ == "2026.9.3", c.__version__'
+HA_PIN=$(sed -n 's/^homeassistant==\([^ ]*\) .*/\1/p' "$REPO/tests/requirements-typing.txt")
+"$PREFIX/venv-ha/bin/python" -c 'import homeassistant.const as c, sys; assert c.__version__ == sys.argv[1], c.__version__' "$HA_PIN"
 
 write_profile "$PROFILE" "$PREFIX"
 
diff --git a/tools/audit/seat/seat_venv.sh b/tools/audit/seat/seat_venv.sh
index e3157d001..b7b06f7f5 100755
--- a/tools/audit/seat/seat_venv.sh
+++ b/tools/audit/seat/seat_venv.sh
@@ -72,8 +72,10 @@ check() {
     "$("$VENV/bin/python3" -c 'import numpy; print(numpy.__version__)')" \
     "$("$VENV/bin/python3" -c 'import scipy; print(scipy.__version__)')"
   [ -x "$VENV_HA/bin/python" ] || die "no typing venv at $VENV_HA; run $0 to build it"
-  "$VENV_HA/bin/python" -c 'import homeassistant.const as c; assert c.__version__ == "2026.9.3", c.__version__' \
-    || die "$VENV_HA is missing a pinned homeassistant: rebuild"
+  ha_pin=$(sed -n 's/^homeassistant==\([^ ]*\) .*/\1/p' "$ROOT/tests/requirements-typing.txt")
+  [ -n "$ha_pin" ] || die "no homeassistant pin in tests/requirements-typing.txt"
+  "$VENV_HA/bin/python" -c 'import homeassistant.const as c, sys; assert c.__version__ == sys.argv[1], c.__version__' "$ha_pin" \
+    || die "$VENV_HA is missing homeassistant $ha_pin, the typing lock's pin: rebuild"
   printf 'seat_venv: %s homeassistant %s\n' "$VENV_HA" \
     "$("$VENV_HA/bin/python" -c 'import homeassistant.const as c; print(c.__version__)')"
 }
@@ -214,6 +216,30 @@ STUB
   rc=$?
   [ "$rc" != 0 ]
   expect "--check refuses a venv-ha whose homeassistant assertion fails" $?
+  # The assertion's version is the typing lock's homeassistant pin, so a lock
+  # bump needs no edit here (the pip group moved it 2026.9.3 -> 2026.10.4 and
+  # a literal refused every rebuilt venv). The stub venv-ha is a real
+  # interpreter over a fake homeassistant.const, so the assertion itself runs;
+  # the pin is read here with awk, the script reads it its own way.
+  lock_ha=$(awk -F'[= ]+' '$1 == "homeassistant" { print $2; exit }' \
+    "$ROOT/tests/requirements-typing.txt")
+  for v in "$lock_ha" 0.0.0; do
+    mkdir -p "$W/ha-$v/state/venv-ci/bin" "$W/ha-$v/state/venv-ha/bin" "$W/ha-$v/pkg/homeassistant"
+    cp "$ci_stub" "$W/ha-$v/state/venv-ci/bin/python3"
+    : > "$W/ha-$v/pkg/homeassistant/__init__.py"
+    printf '__version__ = "%s"\n' "$v" > "$W/ha-$v/pkg/homeassistant/const.py"
+    printf '#!/bin/sh\nPYTHONPATH=%s exec %s "$@"\n' "$W/ha-$v/pkg" "$real_py" \
+      > "$W/ha-$v/state/venv-ha/bin/python"
+    chmod 755 "$W/ha-$v/state/venv-ha/bin/python"
+  done
+  out=$(HPO_STATE_DIR=$W/ha-$lock_ha/state bash "$ROOT/tools/audit/seat/seat_venv.sh" --check 2>&1)
+  rc=$?
+  [ -n "$lock_ha" ] && [ "$rc" = 0 ] && echo "$out" | grep -qF "homeassistant $lock_ha"
+  expect "--check accepts a venv-ha at the typing lock's homeassistant pin ($lock_ha)" $?
+  out=$(HPO_STATE_DIR=$W/ha-0.0.0/state bash "$ROOT/tools/audit/seat/seat_venv.sh" --check 2>&1)
+  rc=$?
+  [ "$rc" != 0 ]
+  expect "--check refuses a venv-ha off the lock's pin (null control)" $?
   rm -rf "$W/missing/venv-ha"
   mkdir -p "$W/missing/venv-ci/bin"
   cp "$ci_stub" "$W/missing/venv-ci/bin/python3"
@@ -231,8 +257,13 @@ STUB
   expect "pins() still hash-pins (venv-ci control)" $?
   echo "$prod" | grep -qF 'pins "$VENV_HA" --no-deps -r "$ROOT/tests/requirements-typing.txt"'
   expect "the build calls pins() for venv-ha with --no-deps from the typing lock" $?
-  echo "$prod" | grep -qF 'import homeassistant.const as c; assert c.__version__ == "2026.9.3"'
+  assertion='import homeassistant.const as c, sys; assert c.__version__ == sys.argv[1], c.__version__'
+  echo "$prod" | grep -qF "$assertion"
   expect "check() carries cloud-setup.sh's homeassistant assertion" $?
+  grep -qF "$assertion" "$ROOT/tools/audit/seat/cloud-setup.sh"
+  expect "cloud-setup.sh asserts the same homeassistant version" $?
+  grep -qF "s/^homeassistant==" "$ROOT/tools/audit/seat/cloud-setup.sh"
+  expect "cloud-setup.sh reads that version from the typing lock" $?
   grep -qF 'pins venv-ha --no-deps -r "$REPO/tests/requirements-typing.txt"' \
     "$ROOT/tools/audit/seat/cloud-setup.sh"
   expect "cloud-setup.sh is still the oracle for that pins call" $?

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
