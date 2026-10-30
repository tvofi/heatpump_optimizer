# Review packet #2925
head: 5682d74e56315ec90ef394191170147111e35382
base: 2d151411f80c3f868c4de5b3a878c673cb88df02

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123893032619 success
arch-score id=123922191089 skipped
arch-score / arch-score id=123922229319 success
arm id=123892713002 skipped
budget-raise-gate / budget-raise-gate id=123922273564 success
cancel-superseded id=123922261708 success
codeql id=123922246475 skipped
codeql / Analyze (actions) id=123922229242 success
codeql / Analyze (javascript-typescript) id=123922228941 success
codeql / Analyze (python) id=123922229320 success
gate id=123922811661 success
governance id=123922203180 skipped
governance / delivery-status id=123922265472 success
governance / delivery-status-publish id=123922229508 skipped
governance / env-matrix id=123922229154 success
governance / instrument-self-tests id=123922258879 success
governance / policy-docs id=123922229504 success
governance / record id=123922229261 skipped
governance / wave-script id=123922265120 success
hassfest id=123922252577 skipped
hassfest / hassfest id=123922269840 success
kernel-points id=123922273813 skipped
pr-contract id=123922191783 skipped
pr-contract / pr-contract id=123922521796 success
prelude id=123922264199 success
refresh id=123922228647 success
tests id=123922203133 skipped
tests / arch-instrument id=123922230384 success
tests / briefs id=123922229300 success
tests / browser id=123922230288 success
tests / ci-ratchet id=123922230880 skipped
tests / claims-autofix id=123922230099 skipped
tests / closure-scope id=123922278964 success
tests / closures id=123922230006 success
tests / closures-autofix id=123922230869 skipped
tests / coverage id=123922230476 success
tests / coverage-ratchet id=123922231244 success
tests / fast (3.14) id=123922230427 success
tests / graders-head-copy id=123922230518 success
tests / lane-proofs id=123922231232 success
tests / mutation id=123922229679 success
tests / mutation-autofix id=123922230308 skipped
tests / mutation-pins id=123922230190 skipped
tests / nightly-ha id=123922230559 skipped
tests / nightly-status id=123922264100 failure
tests / replay id=123922230163 skipped
tests / typing id=123922230314 success
validate id=123922203307 skipped
validate / validate-hacs id=123922268860 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item c8404e8b: dismissed:no live roster group owns tools/audit/seat/ref_privacy.py, and the defect bites only a cloud seat rendering a review packet
NOTE body item 162aa32f: R10-FLY-CIPREDICT-RESTORING: R10-FLY-CIPREDICT-RESTORING resolved on origin/handoff/audit-r10-roster
NOTE body item d356ff9c: R10-FLY-CIPREDICT-RESTORING: R10-FLY-CIPREDICT-RESTORING resolved on origin/handoff/audit-r10-roster
NOTE body item 7c254668: dismissed:a status snapshot at one head, with no finding to own (item 959730db)
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 -I dev/audit/rca/prepr-head-graders/keycount.py 14fbf218d 2026-10-14
             `dev/audit/rca/prepr-head-graders/keycount.py` is in the tree at this head
  ok         python3 -I dev/audit/rca/prepr-head-graders/jobtime.py 14fbf218d wave-script policy-docs
             `dev/audit/rca/prepr-head-graders/jobtime.py` is in the tree at this head
  ok         bash dev/audit/rca/prepr-head-graders/plant.sh <head> gate <head> <out>
             `dev/audit/rca/prepr-head-graders/plant.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 8 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/audit/config/bugclasses.json b/dev/audit/config/bugclasses.json
index 58fae56c0..b02ecbc1c 100644
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
@@ -1196,7 +1196,8 @@
       "RCA-1567-unpinned-installs",
       "RCA-1589-policy-docs-red",
       "RCA-R8-I3-1516",
-      "R10-RCA-2671-WAVE-SCRIPT"
+      "R10-RCA-2671-WAVE-SCRIPT",
+      "R10-RCA-PREPR-HEAD-GRADERS"
     ],
     "rca_planned": [],
     "trigger": {
@@ -4601,6 +4602,22 @@
         "dev/audit/rca/R10-RCA-CLOSURE-ARGV.md"
       ]
     },
+    "R10-RCA-PREPR-HEAD-GRADERS": {
+      "class": "I3",
+      "level": "instance-or-process",
+      "subject": "#2916 red trigger: policy-docs and env-matrix graded f008c2b75's CORPUS_EXCLUDED edit with the base's policy_lint.mjs (named-docs beatd_shims/git) while prepr.sh and ci_predict.py were green; 8 round-10 PRs (#2207 #2366 #2529 #2609 #2636 #2671 #2739 #2916) red on a pinned grader the branch edited, base copy red and head copy green on CI's tree",
+      "trigger": "2 (red check): CI code run 40732339443, governance / policy-docs and governance / env-matrix",
+      "date": "2026-10-28",
+      "status": "proposed",
+      "parts_missing": [],
+      "process_state": "(c) prepr.sh steps 3-4 and 3f3 grade the head's copy (push-to-main's direction); ci_predict.py's agreement arm (#2707) graded the base's copy keyed on lane_files(), the agreement lane's loads, and no arm ran policy_lint.mjs, check-wave-script.mjs or field_coverage.mjs that way; the named-docs refusal directed the fixer to the pinned Set",
+      "countermeasure": "built: ci_predict.py graders arm, keyed on each governance.yml job that restores its check source (restore_jobs) by the diff's paths that job's restore pathspecs cover and the base tip holds (restored_hit), running every program the job runs (pinned_runs, less the agreement arm's two and policy_lint.mjs --report) on CI's merge tree, jobs side by side; the agreement arm re-keyed the same way and lane_files() deleted; no load grammar (review round 4's re-cut); opt-in under --record-self-tests (prepr.sh step 6d), so body_push.sh stays seconds: 57 s per prepr run weighted over 584 round-10 merges against 85 s expected defect cost per PR with the fixer round; the named-docs message now names corpus_excluded.json",
+      "landed": null,
+      "in_tree_home": "dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md",
+      "doc": [
+        "dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md"
+      ]
+    },
     "R10-RCA-FRICTION-RESIDUE": {
       "class": null,
       "level": "instance-or-process",
diff --git a/dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md b/dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md
new file mode 100644
index 000000000..62641970d
--- /dev/null
+++ b/dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md
@@ -0,0 +1,249 @@
+# R10-RCA-PREPR-HEAD-GRADERS: a grader edit every local path passed and CI's base copy refused
+
+The root-cause seat for #2916 (R10-ORCH-BEATD arm a), run beside the fix and not inside it (the
+root-cause role contract, `dev/governance/rules/defect-root-cause.md`). The instances (section 4)
+were measured on 2026-10-28 against `origin/main` `eab04d0eb`. Section 5's denominator and costs
+and section 6's demonstration were re-taken on 2026-10-29 at the head the pull-request body names,
+against `origin/main` `14fbf218d`. Every time is UTC. The seat filed no issue; review round 7
+opened a carry for section 7's open jobs, which now lives in the roster group R10-FLY-CIPREDICT-RESTORING.
+
+**Result: state (c).** 8 measured pull requests in round 10, past the audit-class threshold of 3 in
+one round. The class is I3, which is barriered.
+
+**Countermeasure: built.** `tools/pr/ci_predict.py`'s `graders` arm. A `governance.yml` job that restores its
+check source from the base is keyed when the diff changes a path that job's own restore pathspecs cover;
+the arm then runs every program that job runs, on CI's merge tree, with the base's copies restored.
+The key is the restore list itself, so the arm needs no model of what a grader loads. Its scope is
+`governance.yml`'s restoring jobs; the restoring jobs in other workflows are outside it (section 7).
+
+## 1. The defect, reproduced
+
+Trigger 2, a red check. CI run 40732339443 on `e09b123f9` went red on `governance / policy-docs`
+(job 122973705767) and `governance / env-matrix` (job 122973705691). Both logs print `check source
+restored from eab04d0eb…: 1 file(s) differ` and the same refusal: `ERROR [named-docs]
+tools/audit/seat/beatd_shims/git: is named by .claude/rules/claim-files.md but has no cap …`. The PR
+body records `prepr.sh` rc 0 and `ci_predict.py` printing "no closures, fast, wave-script or
+instrument red predicted" at `f008c2b75`.
+
+`dev/audit/rca/prepr-head-graders/attribute.sh` builds CI's tree (`e09b123f9` merged into
+`eab04d0eb`, base first) and grades it twice:
+
+| run | `policy_lint.mjs` copy | rc | first refusal |
+|---|---|---|---|
+| `attribute.sh` on `e09b123f9` / `eab04d0eb` | the branch's (what prepr step 3 ran) | 0 | none |
+| the same tree | the base's (what the job's restore step runs) | 1 | `[named-docs] tools/audit/seat/beatd_shims/git` |
+
+**Which side moved: the branch.** `f008c2b75` added the path to the `CORPUS_EXCLUDED` Set inside
+`tools/policy/policy_lint.mjs`. That file matches the restore step's `'tools/policy/*.mjs'`, so CI
+replaced it with the base's copy before grading. The repair, `c991d64cd`, moved the entry into
+`dev/governance/config/corpus_excluded.json`, outside the pathspec.
+
+**The refusal told the fixer to make the edit.** The named-docs message ended "add it to
+CORPUS_EXCLUDED with a reason", the one remedy no pull request's CI run reads.
+
+## 2. Cause
+
+1. **Every local path grades the head's copy of a pinned grader.** `prepr.sh` steps 3–4 and 3f3 run
+   `policy_lint.mjs`, the agreement lane, `check-wave-script.mjs` and `field_coverage.mjs` from the
+   head: the push-to-main direction. `gate-scoping.md`'s "prepr.sh is not CI" section states the
+   asymmetry and names no detector.
+2. **The one local arm in the pull-request direction was keyed on a model of one lane's loads.**
+   #2707's `agreement` arm keyed on `lane_files()`, the agreement lane's import closure; the other
+   restored programs had no arm.
+
+**The named cause.** In round 10 no local check ran the restored graders the way CI grades a pull
+request, with the base's copy on the merge of the head into the base. An exclusion, rule or
+registration written into a restored grader, or into anything it loads, passed every local path
+and only CI refused it.
+
+**What the review rounds showed about the countermeasure's form.** Three rounds keyed the arm on
+what a grader loads, read from its source; each review found a restored file that reading could not
+see (`budget_raise_gate.py`, which `policy_lint.mjs` spawns; `vendor/markdown-it.min.js`, which
+`render_md.mjs` `require()`s). The class is defined by the jobs' restore pathspecs, so the key is
+those pathspecs, not a grammar of loads.
+
+## 3. Process state: (c)
+
+The process is the pre-handoff gate that predicts CI's verdict: `prepr.sh` steps 3–4 and 6d, and the
+`ci_predict.py` run inside `body_push.sh`. It existed, was followed and passed; none of its units
+graded the restored programs in the pull-request direction.
+
+- **Not (a).** A check for this shape existed for one lane: the `agreement` arm since `0c7d6ca4f`
+  (#2707, 2026-10-24). Its key did not reach `policy_lint.mjs`.
+- **Not (b).** No instruction was broken; the fixer did what the refusal said.
+- **Not (d).** The restore pathspec has covered `tools/policy/*.mjs` since R9-RO-2.
+
+## 4. Reach: the instances
+
+Measured 2026-10-28 and not re-taken: it is history, independent of the head. The search: every
+round-10 first-parent merge since 2026-10-14 touching a restored path, plus the two open PRs with
+one; every failed `policy-docs`, `env-matrix`, `wave-script` or `briefs` check-run on their commits;
+each log; each candidate through `attribute.sh` at the logged `PINNED`, with `origin/main` set to
+`PINNED` and a `gh` stub exiting 1 first on `PATH` (the live ruleset has moved since). An instance
+is: base copy red, head copy green, on CI's tree.
+
+| PR | red head(s) | `PINNED` | grader | base copy |
+|---|---|---|---|---|
+| #2207 | `d176dd143`, `4b58d3d6e`, `17fd924a6` | `17f1c55fa` | `check-wave-script.mjs` | FAIL "…the cadence is otherwise read from the round number…" |
+| #2366 | `78dbdbda6` | `017045fef` | `agreement.mjs` | `unregistered=1` |
+| #2529 | `e9d54acdf`, `4eac335d8` | `9fdc5846a` | `field_coverage.mjs` | REFUSED "registry: `pinned tools/policy/agreement_restore.py` is unregistered" |
+| #2609 | `a0520623a` | `6c8903a44` | `policy_lint.mjs`; `agreement.mjs` | `[named-docs] dev/README.md`; `unregistered=1` |
+| #2636 | `2aa2b5dbe`, `328e222fe` | `d6308d77c` | `field_coverage.mjs` | BLIND "hooks `attribution.commit` …" |
+| #2671 | `338c9ba49` | `fd7e289d0` | `agreement.mjs` | `unregistered=3` (R10-RCA-2671-WAVE-SCRIPT §1) |
+| #2739 | `9439a0948` | `e97f5749b` | `agreement.mjs` | `unregistered=1` |
+| #2916 | `e09b123f9` (code `f008c2b75`) | `eab04d0eb` | `policy_lint.mjs` | `[named-docs] tools/audit/seat/beatd_shims/git` |
+
+Every head copy was rc 0. The red-to-next-green fixer rounds measured were 44 m, 50 m, 2 h 10 m,
+3 h 23 m, 3 h 36 m and 10 h 28 m (median 2 h 46 m, 9,960 s). Measured non-instances: #2216 (base copy
+green), #2423 (both copies `divergent=2`), #2578 and #2591 (both copies refuse), #2441, #2442 and
+#2589 (API unreachable), #2673 (live required-contexts drift). Of the 40 red pinned jobs read, none
+failed in a `rules_sync.mjs --check`, `fragments_sync.mjs`, `codeowners_gap.py --check`,
+`policy_lint.mjs --hooks` or `agreement.mjs --self-test` step.
+
+Five of the eight fall outside the `agreement` arm's unit: #2207, #2529, #2609's `policy_lint` half,
+#2636 and #2916.
+
+## 5. Cost test
+
+Unit: wall-clock seconds per pull request.
+
+**cost(defect).** One CI run to a visible red: 316 s on #2916 (push 17:05:13, red 17:10:29). A
+fixer round: the 9,960 s median above.
+
+**P(recurrence).** The five instances outside the `agreement` arm, over the round-10 first-parent
+merges: `git rev-list --first-parent --merges --since=2026-10-14 14fbf218d` counts 584. 5 / 584 =
+0.86 %. Expected per pull request: 0.0086 × 316 = 2.7 s on the CI floor, 0.0086 × 9,960 = 85 s with
+the fixer round.
+
+**Keyed share**, re-taken with `python3 -I dev/audit/rca/prepr-head-graders/keycount.py 14fbf218d
+2026-10-14` (the arm's own `restored_hit` over each merge's first-parent diff and its first parent's
+governance.yml):
+
+| jobs keyed together | merges of 584 |
+|---|---|
+| env-matrix + policy-docs + wave-script | 69 |
+| policy-docs + wave-script | 1 |
+| wave-script alone | 71 |
+| none | 443 |
+
+The null control, a pathspec no path matches, keys 0 merges.
+
+**Run cost per job**, re-taken on this head against `14fbf218d` with `python3 -I
+dev/audit/rca/prepr-head-graders/jobtime.py 14fbf218d wave-script policy-docs` (`ci_tree_run` per
+job, every `grader_runs` program, all rc 0); env-matrix's is the arm's whole run
+(`ci_predict.py --base origin/main --only graders`, the three jobs side by side):
+
+| job | wall | dominated by |
+|---|---|---|
+| wave-script | 3.0 s | — |
+| policy-docs | 215.5 s | `field_coverage.mjs` 181.6 s, `policy_lint.mjs` 25.0 s |
+| env-matrix | about 477 s | `policy_lint_envmatrix.mjs`; the arm's whole run, all three jobs side by side, took 477.0 s |
+
+The jobs run side by side, so a run costs its slowest keyed job. Weighted per predictor run:
+(69 × 477 + 1 × 216 + 71 × 3) / 584 = 57 s.
+
+**The form the cost picks.** At every predictor run (`body_push.sh` and each `prepr.sh` step 6d)
+the standing cost would be a multiple of the 85 s it buys, and `body_push.sh`'s own record
+(R10-HANDOFF-PREPR-BOUNCE) priced a minutes-long handoff gate out. So the arm is opt-in under
+`--record-self-tests`, the flag `prepr.sh` step 6d already passes for the other arm that runs a
+gate's programs, and `body_push.sh` stays seconds. At one `prepr.sh` run per pull request the arm
+costs 57 s against 85 s expected; it breaks even at about 1.5 runs. The number of `prepr.sh` runs per
+pull request is not measured here.
+
+**Verdict: build.** The barrier rule binds either way: the class is past the per-round threshold and
+I3 is barriered, so the cost test picks the form, not whether. Not built, each with its reason:
+
+- Mirroring each step's own skip (`field_coverage.mjs` runs on CI only when one of its inputs
+  changed) would cut policy-docs' cost, but it is a second grammar over governance.yml's step
+  conditions, the shape this record drops.
+- Grading only the restored programs and not env-matrix's head-copy matrix would leave env-matrix's
+  verdict modelled, not run.
+
+## 6. Countermeasure, built
+
+**`tools/pr/ci_predict.py`:**
+
+- `restore_jobs(text)`: every governance.yml job holding the "Restore the check source from the
+  base commit" step (today `policy-docs`, `env-matrix`, `wave-script`).
+- `restored_hit(names, specs, at_tip, covers)`: the diff's paths a job's restore pathspecs cover
+  and the base tip holds. That is the key, for both arms that grade with the base's copy.
+- `pinned_runs(text, root)`: every `node`/`python3` program a restoring job runs, with its argv,
+  in order. `grader_runs` drops the `agreement` arm's two (`agreement_py.py --out`,
+  `agreement.mjs --py-json`) and `GRADER_EXEMPT`'s one (`policy_lint.mjs --report`, whose step ends
+  `|| true`). Runner tokens are mapped by `RUN_TOKENS` (`$PWD`, `$RUNNER_TEMP`,
+  `$(git rev-parse HEAD)`); `grader_gaps` names a run line passing any other token and an exemption
+  no run line still holds, and the self-test holds that list empty.
+- `ci_tree_run(root, tip, job, steps)`: the tree build the `agreement` arm had, factored out and
+  reading the job's own restore list (`agreement_py.restore_specs(text, job)`).
+- `grader_preds`: one CI tree per keyed job, side by side, every run made; a refusal is
+  `PREDICT governance / <job> GRADER <program> <argv> REFUSED by the base's copy, over <paths>: <first line>`.
+- The `agreement` arm is re-keyed from `lane_files()` to `restored_hit` for `wave-script`, and
+  `lane_files()` is deleted.
+- Opt-in under `--record-self-tests`, as section 5 says.
+
+**`tools/policy/agreement_py.py`:** `restore_specs(text, name=JOB)` reads any job's list; the default
+is unchanged for CI's base copy.
+
+**`tools/policy/policy_lint.mjs`:** the named-docs refusal now names `corpus_excluded.json`'s
+`excluded` and says why the Set is not read on a pull request (#2609, #2916). The message half of
+the cause. A pinned grader's text, so this branch's own `policy-docs` grades it with the base's copy;
+no verdict changes.
+
+### Demonstration
+
+Each plant is `dev/audit/rca/prepr-head-graders/plant.sh <head> <mdit|gate> <predictor> <out>`: a
+commit on top of this head, graded with `--base` the head itself so only the plant is in the diff
+(`--only graders`). The four runs shared the host, so their times are contended.
+
+| plant | predictor | result | s |
+|---|---|---|---|
+| a comment appended to `tools/policy/vendor/markdown-it.min.js` (review round 3's seam) | round 4's head `5a119e8af` | rc 0, no row run: the miss | 0.7 |
+| the same | this head | rc 0: all three jobs keyed and every run made, green (a comment changes no verdict) | 609 |
+| `budget_raise_gate.py`'s `JUSTIFICATION_SCORE` accepting `Arch score`, `prepr/raise/good.md` using that spelling (review round 2's seam) | this head | **rc 1**, `PREDICT governance / policy-docs GRADER policy_lint.mjs REFUSED by the base's copy, over tools/policy/budget_raise_gate.py: FIXTURE VACUOUS: the raise-justification arm on prepr/raise/good.md drew 1 error(s)` | 608 |
+| the same | `5a119e8af` | rc 1, the same refusal on `policy-docs` and, by its row's model, on `env-matrix` | 325 |
+
+On the gate plant the new arm ran env-matrix's own matrix program on CI's tree and it passed, where
+round 3's arm reported env-matrix red because its CORPUS row was modelled as reaching that job. No
+CI run of this plant exists, so which is right was not measured; the new arm's answer is a run, not
+a model.
+
+### Self-test
+
+`python3 -I tools/pr/ci_predict.py --self-test` gains `graders_self_test`:
+
+- On this tree's governance.yml, `vendor/markdown-it.min.js` and `budget_raise_gate.py` key all
+  three restoring jobs; `corpus_excluded.json` keys none; a restored path the base tip lacks keys none.
+- The arm makes every pinned run but the agreement arm's and the exempt; no run line has an
+  unmapped token (null control), and a planted `$ODD` token and a dropped exemption are each a gap.
+- In a throwaway repo whose one restoring job grades a corpus through a `require()`d vendored file
+  and a spawned Python gate: an exclusion written into the grader, an edit to the vendored file and
+  an edit to the gate are each predicted red; the repair in the unrestored data file (the grader
+  keyed by a comment), a corpus-only diff and the plant staged but not committed are green.
+- `predict` reaches the arm by name.
+
+`plant_self_test` now runs each case with `--only` its own arm, since a plant under `tools/policy/`
+keys the graders arm.
+
+## 7. Recorded
+
+- `bugclasses.json` `_rca["R10-RCA-PREPR-HEAD-GRADERS"]`, class I3, in I3's `rca` list.
+- **A policy line, proposed and not made.** `gate-scoping.md`'s "prepr.sh is not CI" section could
+  name the detector: "step 6d's `ci_predict.py --record-self-tests` runs every program a governance.yml
+  restoring job runs, on CI's tree, when the diff changes a path that job restores". That file is
+  policy, so the owner approves it.
+- **Left open: the restoring jobs outside governance.yml.** The rule that enumerates the class's
+  jobs is `git grep -n -- "- name: Restore the check source from the base commit" HEAD --
+  .github/workflows/`. Outside governance.yml it returns three jobs, each restoring from the base
+  and grading the pull request with that copy, and `restore_jobs` reads governance.yml only:
+  - `briefs` (tests.yml), which runs `brief_lint.mjs`; Carry: R10-FLY-CIPREDICT-RESTORING
+  - `pr-contract` (pr-contract.yml); Carry: R10-FLY-CIPREDICT-RESTORING
+  - `budget-raise-gate` (budget-raise-gate.yml, called from ci.yml on pull requests), which restores
+    `tools/policy/*.py` and runs the base's `tools/policy/budget_raise_gate.py`. It reads live
+    reviews, so a local run of it could only be partial. Carry: R10-FLY-CIPREDICT-RESTORING
+
+  None of the three is predicted by this arm, so a branch editing a file one of them restores is
+  still graded by the base's copy with no local warning. Section 4's census read `briefs`
+  check-runs and counted no `briefs` instance; it did not read `pr-contract` or
+  `budget-raise-gate`, so their instances are unmeasured. This record does not claim them. Their destination is the roster group R10-FLY-CIPREDICT-RESTORING, whose
+  `brief` (roster `0cdedcc9c02ebf52c96d14ffe5425ba9270efa8e` on `handoff/audit-r10-roster`) holds the enumeration rule as the control and the
+  unmeasured `pr-contract` and `budget-raise-gate` instances as its precondition.
diff --git a/dev/audit/rca/prepr-head-graders/attribute.sh b/dev/audit/rca/prepr-head-graders/attribute.sh
new file mode 100755
index 000000000..b8f8a0c89
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/attribute.sh
@@ -0,0 +1,66 @@
+#!/usr/bin/env bash
+# R10-RCA-PREPR-HEAD-GRADERS: attribute one red pinned-job run to the grader copy.
+#
+#   attribute.sh <head-sha> <pinned-sha> <job> <out-dir>
+#
+# Builds CI's tree for a pull-request run -- a merge of <head> into <pinned>,
+# pinned as first parent, the way refs/pull/N/merge is built -- in a shared
+# throwaway clone whose origin/main is <pinned> (agreement.mjs's merge-subject
+# walk reads `merge-base HEAD origin/main`; a live origin/main that has since
+# merged the pull request moves that walk, R10-RCA-2671-WAVE-SCRIPT section 1).
+# It then runs <job>'s corpus graders on that tree twice: with the pull
+# request's own copy of every pinned program (what prepr.sh steps 3-4 run) and
+# with <pinned>'s copy of each pinned program the branch changed (what the
+# job's "Restore the check source from the base commit" step runs). The
+# pinned pathspecs are read from the merge tree's own governance.yml by
+# prepr.sh's own reader (PIN_AWK and pin_read, extracted, never run whole).
+#
+# An instance of the class is: base copy red, head copy green, on one tree.
+# Prints one line: `<job> head=<rc> base=<rc> files=<n> first=<first refusal>`.
+# Writes only under <out-dir>; the clone is removed on exit.
+set -u
+head=$1 pinned=$2 job=$3 out=$4
+root=$(git rev-parse --show-toplevel)
+. "$root/tests/throwaway_git.sh"
+mkdir -p "$out"
+tree=$(git merge-tree --write-tree "$pinned" "$head" 2>/dev/null) || { echo "$job merge-conflict"; exit 2; }
+tree=${tree%%$'\n'*}
+merge=$(git commit-tree "$tree" -p "$pinned" -p "$head" -m "ci-shape merge of $head into $pinned")
+wt=$(mktemp -d "$out/wt.XXXXXX")
+trap 'rm -rf "$wt"' EXIT
+throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" || { echo "$job no-clone"; exit 2; }
+cd "$wt/t" || exit 2
+throwaway_git_env
+git checkout -q --detach "$merge" && git update-ref refs/remotes/origin/main "$pinned" || { echo "$job no-checkout"; exit 2; }
+
+sed -n '/^PIN_AWK=\$(cat <<.AWK.$/,/^pinned_paths()/p' "$root/tools/pr/prepr.sh" > "$wt/pin.sh"
+echo 'pinned_paths .github/workflows/governance.yml' >> "$wt/pin.sh"
+pins=$(bash "$wt/pin.sh")
+[ -n "$pins" ] || { echo "$job no-pins"; exit 2; }
+files=()
+while IFS= read -r f; do
+  hit=1
+  while IFS= read -r p; do
+    [ -n "$p" ] || continue
+    if [[ $f == $p || $f == "$p"/* ]]; then hit=0; break; fi
+  done <<<"$pins"
+  [ "$hit" -eq 0 ] || continue
+  git cat-file -e "$pinned:$f" 2>/dev/null || continue
+  files+=("$f")
+done < <(git diff --no-renames --name-only "$pinned...$head")
+
+pick() { if test -f ".claude/workflows/$1"; then echo ".claude/workflows/$1"; else echo "tools/policy/$1"; fi; }
+grade() { # log -> rc
+  case $job in
+    policy-docs|env-matrix) node "$(pick policy_lint.mjs)" ;;
+    check-wave-script) node "$(pick check-wave-script.mjs)" ;;
+    agreement)
+      python3 -I "$(pick agreement_py.py)" --out "$1.json" && node "$(pick agreement.mjs)" --py-json "$1.json" ;;
+    field-coverage) node "$(pick field_coverage.mjs)" ;;
+  esac >"$1" 2>&1
+}
+grade "$out/head.log"; hrc=$?
+if [ "${#files[@]}" -gt 0 ]; then git checkout -q "$pinned" -- "${files[@]}"; fi
+grade "$out/base.log"; brc=$?
+first=$(grep -E 'ERROR +\[|RESULT divergent=|^  FAIL |BLIND |DEAD |REFUSED ' "$out/base.log" | grep -v 'probe, expected' | head -1 | tr -s ' ' | cut -c1-160)
+echo "$job head=$hrc base=$brc files=${#files[@]} first=${first:-none}"
diff --git a/dev/audit/rca/prepr-head-graders/demo.sh b/dev/audit/rca/prepr-head-graders/demo.sh
new file mode 100644
index 000000000..fbd0a3948
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/demo.sh
@@ -0,0 +1,36 @@
+#!/usr/bin/env bash
+# R10-RCA-PREPR-HEAD-GRADERS: drive the countermeasure, tools/pr/ci_predict.py's
+# `graders` arm, on one historical head against the base CI graded it with.
+#
+#   demo.sh <head-sha> <base-sha> <out-dir> [comment]
+#
+# A shared throwaway clone is checked out at <head>, its origin/main set to
+# <base>, and this branch's ci_predict.py and agreement_py.py are copied over
+# the old head's copies UNCOMMITTED: the predictor is the code under test, and
+# the arm grades only committed state (the merge of HEAD into the base), so
+# the copies change what predicts, never what is predicted. With a fourth
+# argument a commit appending a `//` comment to tools/policy/policy_lint.mjs
+# is made first, so the arm is keyed and a green result is the arm run and
+# passing, not a skip. Prints the predictor's PREDICT and CI PREDICT lines,
+# then `rc=<rc> seconds=<s>`. The seat's own checkout is never touched.
+set -u
+head=$1 base=$2 out=$3 comment=${4:-}
+root=$(git rev-parse --show-toplevel)
+. "$root/tests/throwaway_git.sh"
+mkdir -p "$out"
+wt=$(mktemp -d "$out/wt.XXXXXX")
+trap 'rm -rf "$wt"' EXIT
+throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" || { echo "rc=x no-clone"; exit 2; }
+cd "$wt/t" || exit 2
+throwaway_git_env
+git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$base" || { echo "rc=x no-checkout"; exit 2; }
+if [ -n "$comment" ]; then
+  echo '// a comment the null control adds so the graders arm is keyed' >> tools/policy/policy_lint.mjs
+  git commit -qam "null control: a comment in policy_lint.mjs" || exit 2
+fi
+cp "$root/tools/pr/ci_predict.py" tools/pr/ci_predict.py
+cp "$root/tools/policy/agreement_py.py" tools/policy/agreement_py.py
+t0=$(date +%s)
+PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$base" --only graders > "$out/predict.out" 2>&1; rc=$?
+grep -E '^(PREDICT|CI PREDICT)' "$out/predict.out" | cut -c1-400
+echo "rc=$rc seconds=$(( $(date +%s) - t0 ))"
diff --git a/dev/audit/rca/prepr-head-graders/jobtime.py b/dev/audit/rca/prepr-head-graders/jobtime.py
new file mode 100644
index 000000000..abcbe57db
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/jobtime.py
@@ -0,0 +1,41 @@
+"""R10-RCA-PREPR-HEAD-GRADERS: each restoring job's `grader_runs`, timed one job at a
+time on CI's tree for this HEAD merged into <base> (`ci_predict.ci_tree_run`).
+
+    python3 -I dev/audit/rca/prepr-head-graders/jobtime.py <base> <job>...
+
+Prints, per job, its wall seconds and each run as (program, flags, rc, seconds).
+"""
+import subprocess
+import sys
+import time
+from pathlib import Path
+
+root = Path.cwd()
+sys.path[:0] = [str(root / p) for p in ("tools/pr", "tools/policy", "tests", "tests/hastub")]
+import agreement_py  # noqa: E402
+import ci_predict as c  # noqa: E402
+
+
+def main(base: str, *jobs: str) -> int:
+    tip = c.git(root, "rev-parse", base).strip()
+    text = (root / agreement_py.WORKFLOW).read_text()
+    for job in jobs:
+        t, per = time.time(), []
+
+        def step(p, a):
+            def g(r, run, tmp):
+                args = [c.RUN_TOKENS[x](r, tmp) if x in c.RUN_TOKENS else
+                        next((c.RUN_TOKENS[k](r, tmp) + x[len(k):] for k in c.RUN_TOKENS if x.startswith(k + "/")), x)
+                        for x in a]
+                s = time.time()
+                o = run(*((sys.executable, "-I", p) if p.endswith(".py") else ("node", p)), *args)
+                per.append((Path(p).name, " ".join(x for x in a if x.startswith("--")), o.returncode, round(time.time() - s, 1)))
+                return subprocess.CompletedProcess(o.args, 0, "", "")
+            return g
+        c.ci_tree_run(root, tip, job, tuple(step(p, a) for p, a in c.grader_runs(text, root, job)))
+        print(job, round(time.time() - t, 1), per, flush=True)
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main(*sys.argv[1:]))
diff --git a/dev/audit/rca/prepr-head-graders/keycount.py b/dev/audit/rca/prepr-head-graders/keycount.py
new file mode 100644
index 000000000..91c386963
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/keycount.py
@@ -0,0 +1,54 @@
+"""How many first-parent merges into main each restoring job's key reaches: a
+merge is keyed for a job when its first-parent diff changes a path that job's
+restore pathspecs cover and its first parent holds (`ci_predict.restored_hit`,
+the graders arm's own rule, over the first parent's own governance.yml). Each
+set of jobs keyed together is counted too: they run side by side. A
+pathspec no path matches is the null control: it keys nothing.
+
+    python3 -I dev/audit/rca/prepr-head-graders/keycount.py <tip> <since>
+
+Run from the root of the tree whose predictor is measured.
+"""
+import subprocess
+import sys
+from pathlib import Path
+
+root = Path.cwd()
+sys.path[:0] = [str(root / "tools/pr"), str(root / "tools/policy"), str(root / "tests")]
+import agreement_py  # noqa: E402
+import ci_predict  # noqa: E402
+
+
+def git(*a: str) -> str:
+    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
+
+
+def main(tip: str, since: str) -> int:
+    merges = git("rev-list", "--first-parent", "--merges", f"--since={since}", tip).split()
+    print(f"merges {len(merges)} (git rev-list --first-parent --merges --since={since} {tip})")
+    keyed: dict[str, int] = {}
+    sets: dict[tuple[str, ...], int] = {}
+    anyjob = null = 0
+    for m in merges:
+        text = git("show", f"{m}^1:{agreement_py.WORKFLOW}")
+        names = git("diff", "--no-renames", "--name-only", f"{m}^1", m).split()
+        at_tip = set(git("ls-tree", "-r", "--name-only", f"{m}^1").splitlines())
+        hit = [j for j in ci_predict.restore_jobs(text)
+               if ci_predict.restored_hit(names, agreement_py.restore_specs(text, j), at_tip, agreement_py.covers)]
+        for j in hit:
+            keyed[j] = keyed.get(j, 0) + 1
+        anyjob += bool(hit)
+        if hit:
+            sets[tuple(sorted(hit))] = sets.get(tuple(sorted(hit)), 0) + 1
+        null += bool(ci_predict.restored_hit(names, ["no/such/path"], at_tip, agreement_py.covers))
+    for j, n in sorted(keyed.items()):
+        print(f"{j}: {n} keyed")
+    for jobs, n in sorted(sets.items()):
+        print(f"exactly {' + '.join(jobs)}: {n}")
+    print(f"any job keyed: {anyjob}")
+    print(f"null control (pathspec no/such/path): {null} keyed")
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main(*sys.argv[1:3]))
diff --git a/dev/audit/rca/prepr-head-graders/mutants.py b/dev/audit/rca/prepr-head-graders/mutants.py
new file mode 100644
index 000000000..5f9c69018
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/mutants.py
@@ -0,0 +1,25 @@
+"""R10-RCA-PREPR-HEAD-GRADERS: each mutant of the graders arm's predicates, run against
+graders_self_test from a copy of tools/pr/; prints each mutant's failing checks.
+
+    python3 -I dev/audit/rca/prepr-head-graders/mutants.py .
+"""
+import subprocess, sys, tempfile, shutil
+from pathlib import Path
+root = Path(sys.argv[1]).resolve(); src = (root / "tools/pr/ci_predict.py").read_text()
+M = {
+ "M1 restored_hit keys nothing": ("return sorted(p for p in names if p in at_tip and any(covers(s, p) for s in specs))", "return []"),
+ "M2 restored_hit ignores the base tip": ("p in at_tip and any(covers(s, p)", "any(covers(s, p)"),
+ "M3 grader_runs drops no exemption": ("not in GRADER_EXEMPT.keys() | AGREEMENT_RUNS]", "not in AGREEMENT_RUNS]"),
+ "M4 predict's graders entry removed": ('        ("graders", lambda: grader_preds(root, base_ref)),\n', ""),
+ "M5 ci_tree_run restores nothing": ('        run("git", "checkout", tip, f"--pathspec-from-file={tmp / \'pinned.list\'}", "--pathspec-file-nul")\n', ""),
+}
+for name, (a, b) in M.items():
+    assert src.count(a) == 1, name
+    d = Path(tempfile.mkdtemp()); shutil.copytree(root / "tools/pr", d / "pr")
+    (d / "pr/ci_predict.py").write_text(src.replace(a, b))
+    out = subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {str(d/'pr')!r}); from pathlib import Path; import ci_predict as c; print('bad', c.graders_self_test(Path({str(root)!r})))"],
+                         capture_output=True, text=True, cwd=root).stdout
+    fails = [l.strip()[:110] for l in out.splitlines() if "FAIL" in l]
+    print(f"{name}: {out.strip().splitlines()[-1] if out.strip() else 'no output'}; {len(fails)} FAIL")
+    for f in fails: print("   ", f)
+    shutil.rmtree(d)
diff --git a/dev/audit/rca/prepr-head-graders/plant.sh b/dev/audit/rca/prepr-head-graders/plant.sh
new file mode 100755
index 000000000..947a1aeb3
--- /dev/null
+++ b/dev/audit/rca/prepr-head-graders/plant.sh
@@ -0,0 +1,33 @@
+#!/usr/bin/env bash
+# R10-RCA-PREPR-HEAD-GRADERS: one review-round plant, committed on <head> and
+# graded by the `graders` arm of <predictor-sha>'s ci_predict.py with --base
+# <head>, so only the plant is in the diff.
+#
+#   plant.sh <head> <mdit|gate> <predictor-sha> <out-file>
+#
+# mdit: a comment appended to tools/policy/vendor/markdown-it.min.js (review
+# round 3's seam). gate: budget_raise_gate.py's JUSTIFICATION_SCORE accepting
+# `Arch score`, with prepr/raise/good.md using that spelling (round 2's seam).
+# A shared throwaway clone; the seat's own checkout is never touched. Writes
+# the predictor's output, then `rc=<rc> seconds=<s>`, to <out-file>.
+set -u
+head=$1 kind=$2 pred=$3 out=$4
+root=$(git rev-parse --show-toplevel)
+. "$root/tests/throwaway_git.sh"
+wt=$(mktemp -d); trap 'rm -rf "$wt"' EXIT
+throwaway_git_clone -q --shared --no-checkout "$root" "$wt/t" >/dev/null || exit 2
+cd "$wt/t" || exit 2
+throwaway_git_env
+git checkout -q --detach "$head" && git update-ref refs/remotes/origin/main "$head" || exit 2
+case $kind in
+  mdit) printf '\n/* plant: an edit to the vendored parser only */\n' >> tools/policy/vendor/markdown-it.min.js ;;
+  gate) sed -i 's/Architecture score: dS \[+-\]/Arch(?:itecture)? score: dS [+-]/' tools/policy/budget_raise_gate.py
+        sed -i 's/^Architecture score: dS +0.1000 IMPROVES/Arch score: dS +0.1000 IMPROVES/' tools/policy/fixtures/policy-rot/prepr/raise/good.md ;;
+  *) echo "plant.sh: no plant $kind"; exit 2 ;;
+esac
+git commit -qam "plant $kind" || exit 2
+git show "$pred:tools/pr/ci_predict.py" > tools/pr/ci_predict.py
+git show "$pred:tools/policy/agreement_py.py" > tools/policy/agreement_py.py
+t0=$(date +%s.%N)
+PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base "$head" --only graders > "$out" 2>&1; rc=$?
+echo "rc=$rc seconds=$(echo "$(date +%s.%N) - $t0" | bc)" >> "$out"
diff --git a/dev/programme/delivery/2925.md b/dev/programme/delivery/2925.md
new file mode 100644
index 000000000..e72d70236
--- /dev/null
+++ b/dev/programme/delivery/2925.md
@@ -0,0 +1 @@
+- [#2925](https://github.com/tvofi/heatpump_optimizer/pull/2925) — **open**, rca(R10-RCA-PREPR-HEAD-GRADERS): root-cause record for a pinned grader the branch edits, graded by CI with the base's copy (R10-RCA-PREPR-HEAD-GRADERS)
diff --git a/tools/policy/agreement_py.py b/tools/policy/agreement_py.py
index 32f5c141c..125b5b0e6 100644
--- a/tools/policy/agreement_py.py
+++ b/tools/policy/agreement_py.py
@@ -105,11 +105,12 @@ def closure(root, reader):
     return sorted(seen)
 
 
-def restore_specs(text):
-    """The wave-script restore step's pathspecs, as written."""
-    job = re.search(rf"^  {re.escape(JOB)}:\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)", text, re.M | re.S)
+def restore_specs(text, name=JOB):
+    """A job's restore step pathspecs, as written: wave-script's by default;
+    tools/pr/ci_predict.py reads policy-docs' the same way."""
+    job = re.search(rf"^  {re.escape(name)}:\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)", text, re.M | re.S)
     if not job:
-        raise ValueError(f"no `{JOB}` job")
+        raise ValueError(f"no `{name}` job")
     step = re.search(r"- name: Restore the check source from the base commit\n(.*?)(?=\n      - |\Z)",
                      job.group(1), re.S)
     if not step:
diff --git a/tools/policy/policy_lint.mjs b/tools/policy/policy_lint.mjs
index 790b0002f..f8f98b627 100644
--- a/tools/policy/policy_lint.mjs
+++ b/tools/policy/policy_lint.mjs
@@ -927,7 +927,7 @@ function checkNamedDocs(budget) {
     severity: 'error',
     check: 'named-docs',
     where: rel,
-    message: `is named by ${src} but has no cap in ${BUDGET_FILE}, so prose moved into it leaves the corpus and buys headroom in every cap at once. Bring it under a POLICY_GLOBS pattern so a cap on it is actually compared, or add it to CORPUS_EXCLUDED with a reason. A cap alone does not do it: a cap on a file no glob matches is refused by checkOrphanCaps precisely because it measures nothing.`,
+    message: `is named by ${src} but has no cap in ${BUDGET_FILE}, so prose moved into it leaves the corpus and buys headroom in every cap at once. Bring it under a POLICY_GLOBS pattern so a cap on it is actually compared, or exclude it with a reason in ${CORPUS_EXCLUDED_DATA}'s \`excluded\` -- not in this file's CORPUS_EXCLUDED, which a pull request's CI run grades with the base's copy of, so an entry only this branch writes there is never read (#2609, #2916). A cap alone does not do it: a cap on a file no glob matches is refused by checkOrphanCaps precisely because it measures nothing.`,
   }))
 }
 
diff --git a/tools/pr/ci_predict.py b/tools/pr/ci_predict.py
index cef106159..b623767ed 100644
--- a/tools/pr/ci_predict.py
+++ b/tools/pr/ci_predict.py
@@ -28,7 +28,10 @@ more run CI's own command where no local path ran it the way CI does
 WIRING (`selftest_wiring.py --check`, the same job, which a diff adding a
 self-testing tool to `tools/` left to CI: #2870's `review_packet.py`) and
 AGREEMENT (`wave-script`'s agreement lane under the base's copy, as the
-pull request is graded, where `prepr.sh` step 3f4 runs the head's). One is this predictor's own model, because CI learns the answer by
+pull request is graded, where `prepr.sh` step 3f4 runs the head's) and
+GRADER (every program a job that restores its check source from the base
+runs, on CI's tree, when the diff changes a path that job restores:
+dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md). One is this predictor's own model, because CI learns the answer by
 running: the import arm resolves imports statically where CI records them at
 run time. (A fourth arm, NO RECORDING, read the `rec tests/...` lines of
 `tests/derive_closures.sh`; round-9 C1 derived the full arm's recording set
@@ -37,8 +40,9 @@ says so where it stood.) Every arm is
 scoped to what the three-dot diff adds or changes, so a red main already
 carries is never charged to a branch. Nothing here runs a test, a recording
 or a mutant: seconds, never a heavy script, but for AGREEMENT, which runs the
-lane in a throwaway clone (about 10 s) and only on a diff to a file it loads,
-and SELF-TEST READS, opt-in by `--record-self-tests` (prepr's 6d passes it):
+lane in a throwaway clone (about 10 s) and only on a diff to a path its job
+restores, and two opt-in by `--record-self-tests` (prepr's 6d passes it):
+GRADER, minutes where keyed (measured in its record), and SELF-TEST READS,
 a changed file's own `--self-test`, recorded by `closure._exec_record` and
 graded as its host's record by `closure.check`, for each gate script whose
 source runs that self-test (0.5 s to 29 s a file, measured;
@@ -88,7 +92,8 @@ from pathlib import Path
 # (DESIGN-P2 section 9); gate.REQUIRED pins every value but `ledger`.
 JOB = {"closures": "tests / closures", "fast": "tests / fast (3.14)",
        "mutation": "tests / mutation", "carry": "pr-contract / pr-contract",
-       "wave-script": "governance / wave-script", "instrument": "governance / instrument-self-tests"}
+       "wave-script": "governance / wave-script", "instrument": "governance / instrument-self-tests",
+       "policy-docs": "governance / policy-docs", "env-matrix": "governance / env-matrix"}
 
 
 def git(root: Path, *args: str) -> str | None:
@@ -505,54 +510,78 @@ def privacy_preds(root: Path) -> list[tuple[str, str]]:
 # The agreement lane at either layout, in the order `wave-script` tries them.
 AGREEMENT = (".claude/workflows/agreement.mjs", "tools/policy/agreement.mjs")
 EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
+# The step a job restores its graders from the base commit in: the jobs that
+# hold it are the pull-request direction's whole population.
+RESTORE_STEP = "- name: Restore the check source from the base commit"
 
 
-def lane_files(root: Path) -> set[str]:
-    """What the agreement lane loads: agreement_py.py's own `closure` (its
-    restore precondition's list) and agreement.mjs's, its relative imports and
-    `load`/`at` literals over every .mjs file those reach."""
-    import layout
-    mjs = next((p for p in AGREEMENT if (root / p).is_file()
-                and (root / p).with_name("agreement_py.py").is_file()), None)
-    if mjs is None:
-        return set()
-    sys.path.insert(0, str(root / Path(mjs).parent))
-    import agreement_py
-    seen = set(agreement_py.closure(root, root / Path(mjs).with_name("agreement_py.py")))
-    stack = [mjs]
-    while stack:
-        p = layout.locate(stack.pop(), root=root)
-        if p in seen or not p.endswith(".mjs") or not (root / p).is_file():
-            continue
-        seen.add(p)
-        src = (root / p).read_text()
-        stack += [str(Path(p).parent / m) for m in re.findall(r"from '(\./[^']+)'", src)]
-        stack += re.findall(r"\b(?:load|at)\('([^']+)'\)", src)
-    return seen
+def job_text(text: str, job: str) -> str:
+    m = re.search(rf"^  {re.escape(job)}:\n(.*?)(?=^  [a-z][\w-]*:\n|\Z)", text, re.M | re.S)
+    return m.group(1) if m else ""
 
 
-def agreement_preds(root: Path, base_ref: str, changed: set[str]) -> list[tuple[str, str]]:
-    """`wave-script`'s agreement lane as CI runs it on the pull request: the
-    merge of HEAD into the base tip (base first), the job's restore pathspecs
-    checked out from that tip, in a clone whose origin/main is the tip (a live
-    origin/main past the PR moves the merge-subject walk onto its own merges).
+def restore_jobs(text: str) -> list[str]:
+    """Each governance.yml job that restores its check source from the base."""
+    return [j for j in re.findall(r"^  ([a-z][\w-]*):\n", text, re.M) if RESTORE_STEP in job_text(text, j)]
 
-    prepr.sh step 3f4 runs the head's copy, push-to-main's direction; the two
-    differ only where the diff edits a file the lane loads, so that diff is
-    the key (dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, countermeasure A:
-    #2671's registration passed 3f4 and was UNREGISTERED under the base's
-    copy). A base without the lane runs none, as the job skips it.
-    """
-    hit = sorted(changed & lane_files(root))
-    tip = (git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}") or "").strip()
-    if not hit or not tip or not any(git(root, "cat-file", "-e", f"{tip}:{p}") is not None for p in AGREEMENT):
-        return []
+
+def restored_hit(names, specs, at_tip, covers) -> list[str]:
+    """The diff's paths a job grades with the base's copy of: covered by its
+    restore pathspecs and held by the base tip. Only there do the head's and
+    CI's copies differ, whatever loads them; a path the tip lacks is not
+    restored, and a data file the job does not restore reaches CI as the
+    branch has it (corpus_excluded.json, #2916's repair)."""
+    return sorted(p for p in names if p in at_tip and any(covers(s, p) for s in specs))
+
+
+# Each runner token a pinned run line passes, as the predictor's CI tree has it.
+RUN_TOKENS = {"$PWD": lambda r, tmp: str(r), "$RUNNER_TEMP": lambda r, tmp: str(tmp),
+              "${RUNNER_TEMP}": lambda r, tmp: str(tmp),
+              "$(git rev-parse HEAD)": lambda r, tmp: (git(r, "rev-parse", "HEAD") or "").strip()}
+
+
+def pinned_runs(text: str, root: Path | None = None) -> list[tuple[str, str, tuple[str, ...]]]:
+    """Each program a restoring job runs, from governance.yml's own run text, in
+    its order: (job, the program's path, its argv as written). With `root`,
+    only a path the tree holds: each run line names both layouts and `test -f`
+    runs the one that exists."""
+    import shlex
+    out = []
+    for job in restore_jobs(text):
+        body = "\n".join(l for l in job_text(text, job).splitlines() if not l.lstrip().startswith("#"))
+        for prog, rest in re.findall(r"(?:node|python3(?: -I)?)\s+([\w./-]+\.(?:mjs|py))([^;&|\n]*)", body):
+            run = (job, prog, tuple(shlex.split(rest)))
+            if (root is None or (root / prog).is_file()) and run not in out:
+                out.append(run)
+    return out
+
+
+# The runs the `agreement` arm makes (`--py-json` reads what `--out` writes),
+# and the ones that grade nothing, each with its reason.
+AGREEMENT_RUNS = {("wave-script", "agreement_py.py", "--out"), ("wave-script", "agreement.mjs", "--py-json")}
+GRADER_EXEMPT = {
+    ("policy-docs", "policy_lint.mjs", "--report"): "its step ends `|| true`: it prints and never reddens",
+}
+
+
+def run_key(job: str, prog: str, argv) -> tuple[str, ...]:
+    return (job, Path(prog).name, *(a for a in argv if a.startswith("--")))
+
+
+def ci_tree_run(root: Path, tip: str, job: str, steps) -> tuple[str, subprocess.CompletedProcess | None]:
+    """Run `steps` (each a function of the tree, its runner and a scratch
+    directory) where CI's pull-request run of `job` runs them: the merge of
+    HEAD into the base tip (base first), the job's restore pathspecs checked
+    out from that tip, in a clone whose origin/main is the tip (a live
+    origin/main past the PR moves the merge-subject walk onto its own merges).
+    Returns ("unmerged", None) on a conflict, else ("ran", the first failing
+    step's process or the last)."""
     import shutil
     import tempfile
     import agreement_py
     from throwaway_git import throwaway_git_clone
     head = (git(root, "rev-parse", "HEAD") or "").strip()
-    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-agreement-"))
+    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-tree-"))
     r = tmp / "r"
     try:
         env = throwaway_git_clone(root, r, "-q", "--shared", "--no-checkout")
@@ -563,29 +592,154 @@ def agreement_preds(root: Path, base_ref: str, changed: set[str]) -> list[tuple[
         run("git", "update-ref", "refs/remotes/origin/main", tip)
         run("git", "checkout", "-q", "--detach", tip)
         if run("git", "merge", "-q", "--no-ff", "-m", f"Merge {head} into {tip}", head).returncode:
-            return [("wave-script", f"AGREEMENT UNMERGED: HEAD does not merge into {tip[:12]}, "
-                                    f"and CI runs nothing on a conflict; merge the base first")]
+            return "unmerged", None
         shutil.rmtree(r / ".claude" / "workflows" / "vendor", ignore_errors=True)
-        specs = agreement_py.restore_specs((r / agreement_py.WORKFLOW).read_text())
+        specs = agreement_py.restore_specs((r / agreement_py.WORKFLOW).read_text(), job)
         (tmp / "pinned.list").write_text(run("git", "diff", "--no-renames", "--name-only", "-z", EMPTY_TREE, tip, "--", *specs).stdout)
         run("git", "checkout", tip, f"--pathspec-from-file={tmp / 'pinned.list'}", "--pathspec-file-nul")
-        py = next(p for p in (".claude/workflows/agreement_py.py", "tools/policy/agreement_py.py") if (r / p).is_file())
-        out = run(sys.executable, "-I", py, "--out", str(tmp / "agreement.json"))
-        if out.returncode == 0:
-            out = run("node", next(p for p in AGREEMENT if (r / p).is_file()), "--py-json", str(tmp / "agreement.json"))
-    except (OSError, StopIteration, ValueError) as e:
-        return [("wave-script", f"AGREEMENT UNRUN {type(e).__name__}: {e}")]
+        out = None
+        for step in steps:
+            out = step(r, run, tmp)
+            if out.returncode:
+                break
+        return "ran", out
     finally:
         shutil.rmtree(tmp, ignore_errors=True)
+
+
+def keyed_jobs(root: Path, base_ref: str) -> tuple[str, dict[str, list[str]], object]:
+    """(the base tip, each restoring job the diff keys -> its `restored_hit`,
+    agreement_py) -- the tip "" when the base or the workflow does not resolve."""
+    home = next((d for d in (".claude/workflows", "tools/policy") if (root / d / "agreement_py.py").is_file()), None)
+    tip = (git(root, "rev-parse", "--verify", f"{base_ref}^{{commit}}") or "").strip()
+    if home is None or not tip:
+        return "", {}, None
+    sys.path.insert(0, str(root / home))
+    import agreement_py
+    wf = root / agreement_py.WORKFLOW
+    if not wf.is_file():
+        return "", {}, agreement_py
+    text = wf.read_text()
+    names = (git(root, "diff", "--name-only", "--no-renames", f"{tip}...HEAD") or "").split()
+    at_tip = set((git(root, "ls-tree", "-r", "--name-only", tip) or "").splitlines())
+    keyed = {}
+    for job in restore_jobs(text):
+        hit = restored_hit(names, agreement_py.restore_specs(text, job), at_tip, agreement_py.covers)
+        if hit:
+            keyed[job] = hit
+    return tip, keyed, agreement_py
+
+
+def over(hit: list[str]) -> str:
+    return ", ".join(hit[:3]) + (f" and {len(hit) - 3} more" if len(hit) > 3 else "")
+
+
+def agreement_preds(root: Path, base_ref: str) -> list[tuple[str, str]]:
+    """`wave-script`'s agreement lane as CI runs it on the pull request
+    (`ci_tree_run`).
+
+    prepr.sh step 3f4 runs the head's copy, push-to-main's direction; the two
+    differ only where the diff edits a path the job restores, so that diff is
+    the key (`restored_hit`; dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md,
+    countermeasure A: #2671's registration passed 3f4 and was UNREGISTERED
+    under the base's copy). A base without the lane runs none, as the job
+    skips it.
+    """
+    tip, keyed, _ = keyed_jobs(root, base_ref)
+    hit = keyed.get("wave-script")
+    if not hit or not any(git(root, "cat-file", "-e", f"{tip}:{p}") is not None for p in AGREEMENT):
+        return []
+
+    def py(r, run, tmp):
+        p = next(p for p in (".claude/workflows/agreement_py.py", "tools/policy/agreement_py.py") if (r / p).is_file())
+        return run(sys.executable, "-I", p, "--out", str(tmp / "agreement.json"))
+
+    def lane(r, run, tmp):
+        return run("node", next(p for p in AGREEMENT if (r / p).is_file()), "--py-json", str(tmp / "agreement.json"))
+    try:
+        state, out = ci_tree_run(root, tip, "wave-script", (py, lane))
+    except (OSError, StopIteration, ValueError) as e:
+        return [("wave-script", f"AGREEMENT UNRUN {type(e).__name__}: {e}")]
+    if state == "unmerged":
+        return [("wave-script", f"AGREEMENT UNMERGED: HEAD does not merge into {tip[:12]}, "
+                                f"and CI runs nothing on a conflict; merge the base first")]
     if out.returncode == 0:
         return []
     lines = [l for l in out.stdout.splitlines() if l.strip()] or [f"rc {out.returncode}: {out.stderr.strip()[-200:]}"]
     why = [l.strip() for l in lines if l.split()[0] in ("UNRESTORED", "DIVERGENT", "UNREGISTERED", "DEAD", "REFUSED")]
     result = next((l for l in reversed(lines) if l.startswith("RESULT ")), lines[-1].strip())
-    return [("wave-script", f"AGREEMENT {result} (the base's copy, over {', '.join(hit)})")] + \
+    return [("wave-script", f"AGREEMENT {result} (the base's copy, over {over(hit)})")] + \
            [("wave-script", f"AGREEMENT {w}") for w in why]
 
 
+def grader_runs(text: str, root: Path, job: str) -> list[tuple[str, tuple[str, ...]]]:
+    """The runs of `job` the graders arm makes: every one `pinned_runs` reads
+    but the `agreement` arm's and `GRADER_EXEMPT`'s."""
+    return [(prog, argv) for j, prog, argv in pinned_runs(text, root)
+            if j == job and run_key(j, prog, argv) not in GRADER_EXEMPT.keys() | AGREEMENT_RUNS]
+
+
+def grader_gaps(text: str) -> list[str]:
+    """A run line the arm cannot run as CI does (a runner token `RUN_TOKENS`
+    does not map), and an exemption no run line still holds. Empty is the
+    population closed over governance.yml."""
+    runs = pinned_runs(text)
+    gaps = [f"{job}: {prog} {' '.join(argv)} passes {a!r}, which RUN_TOKENS does not map"
+            for job, prog, argv in runs for a in argv if "$" in a and a not in RUN_TOKENS
+            and not any(a.startswith(t) and a[len(t):].startswith("/") for t in RUN_TOKENS)]
+    held = {run_key(job, prog, argv) for job, prog, argv in runs}
+    gaps += [f"GRADER_EXEMPT: no run line still holds {' '.join(e)}" for e in GRADER_EXEMPT if e not in held]
+    return gaps
+
+
+def grader_preds(root: Path, base_ref: str) -> list[tuple[str, str]]:
+    """Each run of each restoring job the diff keys (`restored_hit`), as CI
+    runs it on the pull request (`ci_tree_run`): every `grader_runs` program,
+    restored or the head's own, since a head copy that loads a restored file
+    grades with the base's copy of it too. The jobs run side by side, one CI
+    tree each; a refusal names the run and the restored paths that keyed it."""
+    from concurrent.futures import ThreadPoolExecutor
+    tip, keyed, agreement_py = keyed_jobs(root, base_ref)
+    if not keyed:
+        return []
+    text = (root / agreement_py.WORKFLOW).read_text()
+
+    def one(job: str) -> list[tuple[str, str]]:
+        hit, results = keyed[job], []
+
+        def step(prog, argv):
+            def grade(r, run, tmp):
+                args = [RUN_TOKENS[a](r, tmp) if a in RUN_TOKENS else
+                        next((RUN_TOKENS[t](r, tmp) + a[len(t):] for t in RUN_TOKENS if a.startswith(t + "/")), a)
+                        for a in argv]
+                cmd = (sys.executable, "-I", prog) if prog.endswith(".py") else ("node", prog)
+                out = run(*cmd, *args)
+                if out.returncode:
+                    results.append((prog, argv, out))
+                return subprocess.CompletedProcess(out.args, 0, out.stdout, out.stderr)  # run every step
+            return grade
+        runs = grader_runs(text, root, job)
+        try:
+            state, _ = ci_tree_run(root, tip, job, tuple(step(p, a) for p, a in runs))
+        except (OSError, StopIteration, ValueError) as e:
+            return [(job, f"GRADER UNRUN {type(e).__name__}: {e}")]
+        if state == "unmerged":
+            return [(job, f"GRADER UNMERGED: HEAD does not merge into {tip[:12]}, and CI runs nothing "
+                          f"on a conflict; merge the base first")]
+        preds = []
+        for prog, argv, out in results:
+            lines = [l.strip() for l in out.stdout.splitlines() if l.strip()] or \
+                [f"rc {out.returncode}: {out.stderr.strip()[-200:]}"]
+            first = next((l for l in lines if l.startswith(("ERROR", "FAIL", "REFUSED", "BLIND", "DEAD", "MISSING",
+                                                            "NOT WIRED", "STALE", "DRIFT", "SELF-TEST FAILED"))
+                          and "probe, expected" not in l), lines[-1])
+            label = " ".join((Path(prog).name, *argv))
+            preds.append((job, f"GRADER {label} REFUSED by the base's copy, over {over(hit)}: {first[:240]}"))
+        return preds
+    with ThreadPoolExecutor(max_workers=len(keyed)) as pool:
+        return [p for preds in pool.map(one, sorted(keyed)) for p in preds]
+
+
 def orphans(changed, closure):
     """A changed file in no closure and on no list: entities.py's refusal."""
     return [("fast", f"UNCLASSIFIED {f}: in no measured closure and not on "
@@ -644,7 +798,7 @@ def unpinned(base):
 # alone, and reaching it by running every other arm cost 6.5 s of CPU against
 # the 5 s budget the seat's checks meet (eight others then; R10-FLOW-JIDOKA's
 # review, 2026-10-26).
-ARMS = ("orphans", "layout", "privacy", "wiring", "agreement", "no-recording",
+ARMS = ("orphans", "layout", "privacy", "wiring", "agreement", "graders", "no-recording",
         "under-scoped", "inert-siblings", "left-inert", "mutation", "self-test-reads")
 
 
@@ -669,7 +823,8 @@ def predict(root: Path, base_ref: str, pairs: set | None = None,
         ("layout", lambda: layout_preds(root, base)),
         ("privacy", lambda: privacy_preds(root)),
         ("wiring", lambda: wiring_preds(root, changed)),
-        ("agreement", lambda: agreement_preds(root, base_ref, changed)),
+        ("agreement", lambda: agreement_preds(root, base_ref)),
+        ("graders", lambda: grader_preds(root, base_ref)),
         ("no-recording", lambda: no_recording(root, base, changed, closure)),
         ("under-scoped", lambda: under_scoped(root, base, changed, tracked, closures,
                                               inert_reads, closure, pairs, scripts)),
@@ -681,8 +836,10 @@ def predict(root: Path, base_ref: str, pairs: set | None = None,
     )
     preds: list[tuple[str, str]] = []
     for name, arm in arms:
-        # The one arm that runs code: on --record-self-tests (prepr 6d) or by name.
-        if (only is None and (name != "self-test-reads" or record)) or name == only:
+        # The arms that run a gate's programs: on --record-self-tests (prepr 6d)
+        # or by name. `graders` takes minutes where it is keyed, so body_push.sh's
+        # seconds-budget run leaves it to prepr (R10-RCA-PREPR-HEAD-GRADERS).
+        if (only is None and (name not in ("self-test-reads", "graders") or record)) or name == only:
             preds += arm()
     if body:
         preds += carry_preds(root, body)
@@ -746,6 +903,12 @@ def repairs(root: Path, preds, scripts: set) -> list[str]:
                    "the lane is graded by the copy it replaces: repair what the base's copy refuses, and a "
                    "registration only the head's copy carries has no local repair "
                    "(dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md, cause 3): the body names it under ## Red checks")
+    if any(l.startswith("GRADER ") for _, l in preds):
+        out.append("a GRADER refusal is CI's verdict under the base's copy of every path the job restores, so an "
+                   "exclusion, registration or rule written into a restored grader, or into anything it loads, is "
+                   "graded by the copy it replaces: move it into the data the grader reads (corpus_excluded.json "
+                   "for named-docs, #2916's repair), or land the grader change first "
+                   "(dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md); the body names it under ## Red checks")
     if any(j == "instrument" for j, _ in preds):
         out.append("a REF PRIVACY refusal is repaired as `python3 -I tools/audit/seat/ref_privacy.py --check` "
                    "names it: a push site guarded and registered in PUSHERS, a published host path scrubbed")
@@ -855,7 +1018,8 @@ def main(argv: list[str] | None = None) -> int:
                     help="run only this arm: a caller that needs one question answered")
     ap.add_argument("--record-self-tests", action="store_true",
                     help="also record each changed file's own self-test a gate script runs "
-                         "(SELF-TEST READS: seconds per file, so prepr's 6d passes it)")
+                         "(SELF-TEST READS: seconds per file) and run each restoring job's programs "
+                         "the diff keys (GRADER: minutes where keyed), so prepr's 6d passes it")
     ap.add_argument("--self-test", action="store_true")
     ap.add_argument("--rekey-body", metavar="BODY", help="re-key BODY's moved `## Unpinned sites` lines in place")
     ap.add_argument("--from", dest="frm", metavar="SHA", help="with --rekey-body: the code sha the keys were taken at")
@@ -917,7 +1081,7 @@ def main(argv: list[str] | None = None) -> int:
     else:
         ran = args.record_self_tests or args.only == "self-test-reads"
         seen = (" unless a changed file's own self-test makes it" if ran else "")
-        print(f"CI PREDICT: no closures, fast, wave-script or instrument red predicted against "
+        print(f"CI PREDICT: no closures, fast, governance or instrument red predicted against "
               f"{base[:12]} (a data-file read is not seen{seen})")
     return rc
 
@@ -978,6 +1142,7 @@ def self_test() -> int:
     bad += self_test_reads_self_test(root)
     bad += rekey_self_test()
     bad += wiring_self_test(root)
+    bad += graders_self_test(root)
     gate = root / "tools" / "ci" / "gate.py"
     if gate.exists():
         sys.path.insert(0, str(root / "tools" / "ci"))
@@ -992,6 +1157,128 @@ def self_test() -> int:
     return 1 if bad else 0
 
 
+def graders_self_test(root: Path) -> int:
+    """The graders arm's key, population and run, with no load grammar to test.
+
+    Key: on this tree's governance.yml, the two files review rounds 2 and 3
+    found outside every load-grammar key -- the vendored parser
+    `render_md.mjs` requires and the gate `policy_lint.mjs` spawns -- key all
+    three restoring jobs, and the data file #2916's repair moved its entry to
+    keys none. Population: every run line is runnable as CI runs it and every
+    exemption still matches one, each perturbed once. Run: a throwaway repo
+    whose one restoring job grades a corpus through a required vendored file
+    and a spawned Python gate, each plant committed on the base; the nulls are
+    the repair in an unrestored data file, a corpus-only diff (not keyed) and a
+    plant staged but not committed. Last, `predict` reaches the arm by name.
+    """
+    import shutil
+    import tempfile
+    sys.path[:0] = [str(root / "tests"), str(root / "tools" / "policy")]
+    import agreement_py
+    from throwaway_git import throwaway_git_init
+    text = (root / agreement_py.WORKFLOW).read_text()
+    tracked = set((git(root, "ls-files") or "").split())
+    jobs = restore_jobs(text)
+    bad = 0
+
+    def ck(label, ok, why=""):
+        nonlocal bad
+        print(f"  {'ok  ' if ok else 'FAIL'} {label}{' -- ' + why if not ok and why else ''}")
+        bad += not ok
+
+    def keys(path, at_tip=tracked):
+        return [j for j in jobs if restored_hit([path], agreement_py.restore_specs(text, j), at_tip, agreement_py.covers)]
+    three = {"policy-docs", "env-matrix", "wave-script"}
+    for path in ("tools/policy/vendor/markdown-it.min.js", "tools/policy/budget_raise_gate.py"):
+        ck(f"{path} keys every restoring job", set(keys(path)) == three, str(keys(path)))
+    ck("dev/governance/config/corpus_excluded.json keys no job (a data file CI reads as the branch has it)",
+       keys("dev/governance/config/corpus_excluded.json") == [])
+    ck("a restored path the base tip lacks keys no job (nothing to restore it from)",
+       keys("tools/policy/vendor/markdown-it.min.js", tracked - {"tools/policy/vendor/markdown-it.min.js"}) == [])
+    runs = {run_key(*r) for r in pinned_runs(text, root)}
+    made = {run_key(j, p, a) for j in jobs for p, a in grader_runs(text, root, j)}
+    want = {("policy-docs", "policy_lint.mjs"), ("policy-docs", "policy_lint.mjs", "--hooks"),
+            ("wave-script", "check-wave-script.mjs"), ("env-matrix", "policy_lint_envmatrix.mjs")}
+    ck("the arm makes every pinned run but the agreement arm's and the exempt", made == runs - AGREEMENT_RUNS -
+       GRADER_EXEMPT.keys() and want <= made and not made & (AGREEMENT_RUNS | GRADER_EXEMPT.keys()), str(made))
+    ck("every pinned run line is runnable as CI runs it (null control: no gap)", grader_gaps(text) == [],
+       str(grader_gaps(text)))
+    odd = text.replace("node tools/policy/check-wave-script.mjs;", "node tools/policy/check-wave-script.mjs $ODD;", 1)
+    ck("a run line passing a token RUN_TOKENS does not map is a gap", odd != text and any("$ODD" in g for g in grader_gaps(odd)))
+    unexempt = text.replace("--report", "--reprt")
+    ck("an exemption no run line holds is a gap", any(g.startswith("GRADER_EXEMPT") for g in grader_gaps(unexempt)))
+
+    workflow = ("jobs:\n  policy-docs:\n    steps:\n"
+                "      - name: Restore the check source from the base commit\n        run: |\n"
+                '          git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$PINNED" -- \\\n'
+                "            'g/*.mjs' 'g/*.py' 'g/vendor' > \"$RUNNER_TEMP/pinned.list\"\n"
+                "      - name: Grade the corpus\n        run: node g/grade.mjs\n")
+    grade = ("import { createRequire } from 'module'\nimport { execFileSync } from 'child_process'\n"
+             "import fs from 'fs'\nconst require = createRequire(import.meta.url)\n"
+             "const lib = require('./vendor/lib.js')\n"
+             "const EXCLUDED = new Set([...JSON.parse(fs.readFileSync('data/excluded.json', 'utf8'))])\n"
+             "for (const f of fs.readdirSync('corpus').sort()) {\n  if (EXCLUDED.has(f)) continue\n"
+             "  const gate = execFileSync('python3', ['g/gate.py', f]).toString().trim()\n"
+             "  if (!lib.ok(f) || gate !== 'ok') { console.log(`ERROR ${f}`); process.exit(1) }\n}\n")
+    base_files = {".github/workflows/governance.yml": workflow, "g/grade.mjs": grade,
+                  "g/vendor/lib.js": "exports.ok = f => !f.startsWith('bad')\n",
+                  "g/gate.py": "import sys\nprint('no' if 'worse' in sys.argv[1] else 'ok')\n",
+                  "data/excluded.json": "[]\n", "corpus/good.md": "x\n",
+                  "tools/policy/agreement_py.py": (root / "tools" / "policy" / "agreement_py.py").read_text()}
+
+    def app(t):
+        return lambda s: s + t
+    inline = {"g/grade.mjs": lambda s: s.replace("...JSON", "'bad1.md', ...JSON"), "corpus/bad1.md": app("x\n")}
+    vendored = {"g/vendor/lib.js": lambda s: s.replace("!f.startsWith('bad')", "true"), "corpus/bad1.md": app("x\n")}
+    gated = {"g/gate.py": lambda s: s.replace("'worse' in", "'never' in"), "corpus/worse.md": app("x\n")}
+    cases = [("an exclusion written into the restored grader is predicted red (#2916's shape)", inline, True,
+              "GRADER grade.mjs REFUSED by the base's copy, over g/grade.mjs: ERROR bad1.md"),
+             ("an edit to a vendored file the grader requires is predicted red (round 3's markdown-it.min.js)",
+              vendored, True, "over g/vendor/lib.js: ERROR bad1.md"),
+             ("an edit to a gate the grader spawns is predicted red (round 2's budget_raise_gate.py)", gated, True,
+              "over g/gate.py: ERROR worse.md"),
+             ("the exclusion in the unrestored data file, the grader keyed by a comment, is predicted green "
+              "(null control: the repair)", {"data/excluded.json": lambda s: '["bad1.md"]\n',
+                                             "corpus/bad1.md": app("x\n"), "g/grade.mjs": app("// a comment\n")}, True, None),
+             ("a corpus-only diff the base's grader refuses is not run (null control: the key; prepr runs the "
+              "same copy CI does)", {"corpus/bad1.md": app("x\n")}, True, None),
+             ("the inline exclusion staged and not committed is predicted green (null control)", inline, False, None)]
+    tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-graders-"))
+    try:
+        for label, edits, commit, want in cases:
+            r = tmp / f"r{cases.index((label, edits, commit, want))}"
+            env = throwaway_git_init(r, "-q", "-b", "main")
+
+            def run(*a):
+                return subprocess.run(a, cwd=r, env=env, capture_output=True, text=True)
+            for p, body in base_files.items():
+                (r / p).parent.mkdir(parents=True, exist_ok=True)
+                (r / p).write_text(body)
+            run("git", "add", "-A")
+            run("git", "commit", "-qm", "base")
+            tip = run("git", "rev-parse", "HEAD").stdout.strip()
+            for p, edit in edits.items():
+                (r / p).write_text(edit((r / p).read_text() if (r / p).exists() else ""))
+            run("git", "add", "-A")
+            if commit:
+                run("git", "commit", "-qm", label)
+            got = grader_preds(r, tip)
+            ok = (any(j == "policy-docs" and want in l for j, l in got) if want else not got)
+            ck(label, ok, str(got))
+    finally:
+        shutil.rmtree(tmp, ignore_errors=True)
+    g = globals()
+    real = g["grader_preds"]
+    g["grader_preds"] = lambda _root, _base: [("policy-docs", "GRADER sentinel")]
+    try:
+        _, preds, _ = predict(root, "HEAD", only="graders")
+    finally:
+        g["grader_preds"] = real
+    ck("predict reaches the graders arm by name (its call site, not only its helper)",
+       ("policy-docs", "GRADER sentinel") in preds, str(preds))
+    return bad
+
+
 def self_test_reads_self_test(root: Path) -> int:
     """SELF-TEST READS over planted records, graded by CI's own `check`.
 
@@ -1234,6 +1521,7 @@ def plant_self_test(root: Path) -> int:
                  app('if __name__ == "__main__":\n    pass  # --self-test\n')}, True)],
               "instrument", ("UNWIRED", "UNWIRED tools/audit/seat/planted_selftest.py:"), 1)]
     marker = {"fast": "LAYOUT", "instrument": "REF PRIVACY", "wave-script": "AGREEMENT"}
+    arm = {"LAYOUT": "layout", "REF PRIVACY": "privacy", "AGREEMENT": "agreement", "UNWIRED": "wiring"}
     head = (git(root, "rev-parse", "HEAD") or "").strip()
     tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-plant-"))
     r = tmp / "r"
@@ -1273,12 +1561,14 @@ def plant_self_test(root: Path) -> int:
                 if commit == "tip":
                     tip = run("git", "rev-parse", "HEAD").stdout.strip()
                     run("git", "checkout", "-q", "--detach", base)
-            out = subprocess.run((sys.executable, "-I", "tools/pr/ci_predict.py", "--base", tip), cwd=r, env=penv,
-                                 capture_output=True, text=True)
-            lines = out.stdout.splitlines()
             # A case may name its own line marker (a job can hold two arms) as
-            # `(marker, text)`; `text` None is that arm's null control.
+            # `(marker, text)`; `text` None is that arm's null control. Only
+            # that arm runs: a plant under tools/policy/ keys the graders arm,
+            # which runs every restoring job's programs (graders_self_test's).
             mark, want_text = want if isinstance(want, tuple) else (marker[job], want)
+            out = subprocess.run((sys.executable, "-I", "tools/pr/ci_predict.py", "--base", tip, "--only", arm[mark]),
+                                 cwd=r, env=penv, capture_output=True, text=True)
+            lines = out.stdout.splitlines()
             tag = f"PREDICT {JOB[job]} {mark}"
             fix = any(l.startswith(f"CI PREDICT: a{'n' if job == 'wave-script' else ''} {marker[job]} refusal") for l in lines)
             hit = (any(l.startswith(tag) and want_text in l for l in lines) and fix if want_text

