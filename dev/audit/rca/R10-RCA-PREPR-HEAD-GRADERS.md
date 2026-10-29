# R10-RCA-PREPR-HEAD-GRADERS: a grader edit every local path passed and CI's base copy refused

The root-cause seat for #2916 (R10-ORCH-BEATD arm a), run beside the fix and not inside it (the
root-cause role contract, `dev/governance/rules/defect-root-cause.md`). The instances (section 4)
were measured on 2026-10-28 against `origin/main` `eab04d0eb`. Section 5's denominator and costs
and section 6's demonstration were re-taken on 2026-10-29 at the head the pull-request body names,
against `origin/main` `14fbf218d`. Every time is UTC. The seat filed no issue; review round 7
filed #2952 as the destination of section 7's open jobs.

**Result: state (c).** 8 measured pull requests in round 10, past the audit-class threshold of 3 in
one round. The class is I3, which is barriered.

**Countermeasure: built.** `tools/pr/ci_predict.py`'s `graders` arm. A `governance.yml` job that restores its
check source from the base is keyed when the diff changes a path that job's own restore pathspecs cover;
the arm then runs every program that job runs, on CI's merge tree, with the base's copies restored.
The key is the restore list itself, so the arm needs no model of what a grader loads. Its scope is
`governance.yml`'s restoring jobs; the restoring jobs in other workflows are outside it (section 7).

## 1. The defect, reproduced

Trigger 2, a red check. CI run 40732339443 on `e09b123f9` went red on `governance / policy-docs`
(job 122973705767) and `governance / env-matrix` (job 122973705691). Both logs print `check source
restored from eab04d0eb…: 1 file(s) differ` and the same refusal: `ERROR [named-docs]
tools/audit/seat/beatd_shims/git: is named by .claude/rules/claim-files.md but has no cap …`. The PR
body records `prepr.sh` rc 0 and `ci_predict.py` printing "no closures, fast, wave-script or
instrument red predicted" at `f008c2b75`.

`dev/audit/rca/prepr-head-graders/attribute.sh` builds CI's tree (`e09b123f9` merged into
`eab04d0eb`, base first) and grades it twice:

| run | `policy_lint.mjs` copy | rc | first refusal |
|---|---|---|---|
| `attribute.sh` on `e09b123f9` / `eab04d0eb` | the branch's (what prepr step 3 ran) | 0 | none |
| the same tree | the base's (what the job's restore step runs) | 1 | `[named-docs] tools/audit/seat/beatd_shims/git` |

**Which side moved: the branch.** `f008c2b75` added the path to the `CORPUS_EXCLUDED` Set inside
`tools/policy/policy_lint.mjs`. That file matches the restore step's `'tools/policy/*.mjs'`, so CI
replaced it with the base's copy before grading. The repair, `c991d64cd`, moved the entry into
`dev/governance/config/corpus_excluded.json`, outside the pathspec.

**The refusal told the fixer to make the edit.** The named-docs message ended "add it to
CORPUS_EXCLUDED with a reason", the one remedy no pull request's CI run reads.

## 2. Cause

1. **Every local path grades the head's copy of a pinned grader.** `prepr.sh` steps 3–4 and 3f3 run
   `policy_lint.mjs`, the agreement lane, `check-wave-script.mjs` and `field_coverage.mjs` from the
   head: the push-to-main direction. `gate-scoping.md`'s "prepr.sh is not CI" section states the
   asymmetry and names no detector.
2. **The one local arm in the pull-request direction was keyed on a model of one lane's loads.**
   #2707's `agreement` arm keyed on `lane_files()`, the agreement lane's import closure; the other
   restored programs had no arm.

**The named cause.** In round 10 no local check ran the restored graders the way CI grades a pull
request, with the base's copy on the merge of the head into the base. An exclusion, rule or
registration written into a restored grader, or into anything it loads, passed every local path
and only CI refused it.

**What the review rounds showed about the countermeasure's form.** Three rounds keyed the arm on
what a grader loads, read from its source; each review found a restored file that reading could not
see (`budget_raise_gate.py`, which `policy_lint.mjs` spawns; `vendor/markdown-it.min.js`, which
`render_md.mjs` `require()`s). The class is defined by the jobs' restore pathspecs, so the key is
those pathspecs, not a grammar of loads.

## 3. Process state: (c)

The process is the pre-handoff gate that predicts CI's verdict: `prepr.sh` steps 3–4 and 6d, and the
`ci_predict.py` run inside `body_push.sh`. It existed, was followed and passed; none of its units
graded the restored programs in the pull-request direction.

- **Not (a).** A check for this shape existed for one lane: the `agreement` arm since `0c7d6ca4f`
  (#2707, 2026-10-24). Its key did not reach `policy_lint.mjs`.
- **Not (b).** No instruction was broken; the fixer did what the refusal said.
- **Not (d).** The restore pathspec has covered `tools/policy/*.mjs` since R9-RO-2.

## 4. Reach: the instances

Measured 2026-10-28 and not re-taken: it is history, independent of the head. The search: every
round-10 first-parent merge since 2026-10-14 touching a restored path, plus the two open PRs with
one; every failed `policy-docs`, `env-matrix`, `wave-script` or `briefs` check-run on their commits;
each log; each candidate through `attribute.sh` at the logged `PINNED`, with `origin/main` set to
`PINNED` and a `gh` stub exiting 1 first on `PATH` (the live ruleset has moved since). An instance
is: base copy red, head copy green, on CI's tree.

| PR | red head(s) | `PINNED` | grader | base copy |
|---|---|---|---|---|
| #2207 | `d176dd143`, `4b58d3d6e`, `17fd924a6` | `17f1c55fa` | `check-wave-script.mjs` | FAIL "…the cadence is otherwise read from the round number…" |
| #2366 | `78dbdbda6` | `017045fef` | `agreement.mjs` | `unregistered=1` |
| #2529 | `e9d54acdf`, `4eac335d8` | `9fdc5846a` | `field_coverage.mjs` | REFUSED "registry: `pinned tools/policy/agreement_restore.py` is unregistered" |
| #2609 | `a0520623a` | `6c8903a44` | `policy_lint.mjs`; `agreement.mjs` | `[named-docs] dev/README.md`; `unregistered=1` |
| #2636 | `2aa2b5dbe`, `328e222fe` | `d6308d77c` | `field_coverage.mjs` | BLIND "hooks `attribution.commit` …" |
| #2671 | `338c9ba49` | `fd7e289d0` | `agreement.mjs` | `unregistered=3` (R10-RCA-2671-WAVE-SCRIPT §1) |
| #2739 | `9439a0948` | `e97f5749b` | `agreement.mjs` | `unregistered=1` |
| #2916 | `e09b123f9` (code `f008c2b75`) | `eab04d0eb` | `policy_lint.mjs` | `[named-docs] tools/audit/seat/beatd_shims/git` |

Every head copy was rc 0. The red-to-next-green fixer rounds measured were 44 m, 50 m, 2 h 10 m,
3 h 23 m, 3 h 36 m and 10 h 28 m (median 2 h 46 m, 9,960 s). Measured non-instances: #2216 (base copy
green), #2423 (both copies `divergent=2`), #2578 and #2591 (both copies refuse), #2441, #2442 and
#2589 (API unreachable), #2673 (live required-contexts drift). Of the 40 red pinned jobs read, none
failed in a `rules_sync.mjs --check`, `fragments_sync.mjs`, `codeowners_gap.py --check`,
`policy_lint.mjs --hooks` or `agreement.mjs --self-test` step.

Five of the eight fall outside the `agreement` arm's unit: #2207, #2529, #2609's `policy_lint` half,
#2636 and #2916.

## 5. Cost test

Unit: wall-clock seconds per pull request.

**cost(defect).** One CI run to a visible red: 316 s on #2916 (push 17:05:13, red 17:10:29). A
fixer round: the 9,960 s median above.

**P(recurrence).** The five instances outside the `agreement` arm, over the round-10 first-parent
merges: `git rev-list --first-parent --merges --since=2026-10-14 14fbf218d` counts 584. 5 / 584 =
0.86 %. Expected per pull request: 0.0086 × 316 = 2.7 s on the CI floor, 0.0086 × 9,960 = 85 s with
the fixer round.

**Keyed share**, re-taken with `python3 -I dev/audit/rca/prepr-head-graders/keycount.py 14fbf218d
2026-10-14` (the arm's own `restored_hit` over each merge's first-parent diff and its first parent's
governance.yml):

| jobs keyed together | merges of 584 |
|---|---|
| env-matrix + policy-docs + wave-script | 69 |
| policy-docs + wave-script | 1 |
| wave-script alone | 71 |
| none | 443 |

The null control, a pathspec no path matches, keys 0 merges.

**Run cost per job**, re-taken on this head against `14fbf218d` with `python3 -I
dev/audit/rca/prepr-head-graders/jobtime.py 14fbf218d wave-script policy-docs` (`ci_tree_run` per
job, every `grader_runs` program, all rc 0); env-matrix's is the arm's whole run
(`ci_predict.py --base origin/main --only graders`, the three jobs side by side):

| job | wall | dominated by |
|---|---|---|
| wave-script | 3.0 s | — |
| policy-docs | 215.5 s | `field_coverage.mjs` 181.6 s, `policy_lint.mjs` 25.0 s |
| env-matrix | about 477 s | `policy_lint_envmatrix.mjs`; the arm's whole run, all three jobs side by side, took 477.0 s |

The jobs run side by side, so a run costs its slowest keyed job. Weighted per predictor run:
(69 × 477 + 1 × 216 + 71 × 3) / 584 = 57 s.

**The form the cost picks.** At every predictor run (`body_push.sh` and each `prepr.sh` step 6d)
the standing cost would be a multiple of the 85 s it buys, and `body_push.sh`'s own record
(R10-HANDOFF-PREPR-BOUNCE) priced a minutes-long handoff gate out. So the arm is opt-in under
`--record-self-tests`, the flag `prepr.sh` step 6d already passes for the other arm that runs a
gate's programs, and `body_push.sh` stays seconds. At one `prepr.sh` run per pull request the arm
costs 57 s against 85 s expected; it breaks even at about 1.5 runs. The number of `prepr.sh` runs per
pull request is not measured here.

**Verdict: build.** The barrier rule binds either way: the class is past the per-round threshold and
I3 is barriered, so the cost test picks the form, not whether. Not built, each with its reason:

- Mirroring each step's own skip (`field_coverage.mjs` runs on CI only when one of its inputs
  changed) would cut policy-docs' cost, but it is a second grammar over governance.yml's step
  conditions, the shape this record drops.
- Grading only the restored programs and not env-matrix's head-copy matrix would leave env-matrix's
  verdict modelled, not run.

## 6. Countermeasure, built

**`tools/pr/ci_predict.py`:**

- `restore_jobs(text)`: every governance.yml job holding the "Restore the check source from the
  base commit" step (today `policy-docs`, `env-matrix`, `wave-script`).
- `restored_hit(names, specs, at_tip, covers)`: the diff's paths a job's restore pathspecs cover
  and the base tip holds. That is the key, for both arms that grade with the base's copy.
- `pinned_runs(text, root)`: every `node`/`python3` program a restoring job runs, with its argv,
  in order. `grader_runs` drops the `agreement` arm's two (`agreement_py.py --out`,
  `agreement.mjs --py-json`) and `GRADER_EXEMPT`'s one (`policy_lint.mjs --report`, whose step ends
  `|| true`). Runner tokens are mapped by `RUN_TOKENS` (`$PWD`, `$RUNNER_TEMP`,
  `$(git rev-parse HEAD)`); `grader_gaps` names a run line passing any other token and an exemption
  no run line still holds, and the self-test holds that list empty.
- `ci_tree_run(root, tip, job, steps)`: the tree build the `agreement` arm had, factored out and
  reading the job's own restore list (`agreement_py.restore_specs(text, job)`).
- `grader_preds`: one CI tree per keyed job, side by side, every run made; a refusal is
  `PREDICT governance / <job> GRADER <program> <argv> REFUSED by the base's copy, over <paths>: <first line>`.
- The `agreement` arm is re-keyed from `lane_files()` to `restored_hit` for `wave-script`, and
  `lane_files()` is deleted.
- Opt-in under `--record-self-tests`, as section 5 says.

**`tools/policy/agreement_py.py`:** `restore_specs(text, name=JOB)` reads any job's list; the default
is unchanged for CI's base copy.

**`tools/policy/policy_lint.mjs`:** the named-docs refusal now names `corpus_excluded.json`'s
`excluded` and says why the Set is not read on a pull request (#2609, #2916). The message half of
the cause. A pinned grader's text, so this branch's own `policy-docs` grades it with the base's copy;
no verdict changes.

### Demonstration

Each plant is `dev/audit/rca/prepr-head-graders/plant.sh <head> <mdit|gate> <predictor> <out>`: a
commit on top of this head, graded with `--base` the head itself so only the plant is in the diff
(`--only graders`). The four runs shared the host, so their times are contended.

| plant | predictor | result | s |
|---|---|---|---|
| a comment appended to `tools/policy/vendor/markdown-it.min.js` (review round 3's seam) | round 4's head `5a119e8af` | rc 0, no row run: the miss | 0.7 |
| the same | this head | rc 0: all three jobs keyed and every run made, green (a comment changes no verdict) | 609 |
| `budget_raise_gate.py`'s `JUSTIFICATION_SCORE` accepting `Arch score`, `prepr/raise/good.md` using that spelling (review round 2's seam) | this head | **rc 1**, `PREDICT governance / policy-docs GRADER policy_lint.mjs REFUSED by the base's copy, over tools/policy/budget_raise_gate.py: FIXTURE VACUOUS: the raise-justification arm on prepr/raise/good.md drew 1 error(s)` | 608 |
| the same | `5a119e8af` | rc 1, the same refusal on `policy-docs` and, by its row's model, on `env-matrix` | 325 |

On the gate plant the new arm ran env-matrix's own matrix program on CI's tree and it passed, where
round 3's arm reported env-matrix red because its CORPUS row was modelled as reaching that job. No
CI run of this plant exists, so which is right was not measured; the new arm's answer is a run, not
a model.

### Self-test

`python3 -I tools/pr/ci_predict.py --self-test` gains `graders_self_test`:

- On this tree's governance.yml, `vendor/markdown-it.min.js` and `budget_raise_gate.py` key all
  three restoring jobs; `corpus_excluded.json` keys none; a restored path the base tip lacks keys none.
- The arm makes every pinned run but the agreement arm's and the exempt; no run line has an
  unmapped token (null control), and a planted `$ODD` token and a dropped exemption are each a gap.
- In a throwaway repo whose one restoring job grades a corpus through a `require()`d vendored file
  and a spawned Python gate: an exclusion written into the grader, an edit to the vendored file and
  an edit to the gate are each predicted red; the repair in the unrestored data file (the grader
  keyed by a comment), a corpus-only diff and the plant staged but not committed are green.
- `predict` reaches the arm by name.

`plant_self_test` now runs each case with `--only` its own arm, since a plant under `tools/policy/`
keys the graders arm.

## 7. Recorded

- `bugclasses.json` `_rca["R10-RCA-PREPR-HEAD-GRADERS"]`, class I3, in I3's `rca` list.
- **A policy line, proposed and not made.** `gate-scoping.md`'s "prepr.sh is not CI" section could
  name the detector: "step 6d's `ci_predict.py --record-self-tests` runs every program a governance.yml
  restoring job runs, on CI's tree, when the diff changes a path that job restores". That file is
  policy, so the owner approves it.
- **Left open: the restoring jobs outside governance.yml.** The rule that enumerates the class's
  jobs is `git grep -n -- "- name: Restore the check source from the base commit" HEAD --
  .github/workflows/`. Outside governance.yml it returns three jobs, each restoring from the base
  and grading the pull request with that copy, and `restore_jobs` reads governance.yml only:
  - `briefs` (tests.yml), which runs `brief_lint.mjs`; Carry: #2952
  - `pr-contract` (pr-contract.yml); Carry: #2952
  - `budget-raise-gate` (budget-raise-gate.yml, called from ci.yml on pull requests), which restores
    `tools/policy/*.py` and runs the base's `tools/policy/budget_raise_gate.py`. It reads live
    reviews, so a local run of it could only be partial. Carry: #2952

  None of the three is predicted by this arm, so a branch editing a file one of them restores is
  still graded by the base's copy with no local warning. Section 4's census read `briefs`
  check-runs and counted no `briefs` instance; it did not read `pr-contract` or
  `budget-raise-gate`, so their instances are unmeasured. This record does not claim them. Their destination is #2952, whose brief is
  `dev/programme/carries/carry-2952.json`: the enumeration rule as the control, the
  unmeasured `pr-contract` and `budget-raise-gate` instances as its precondition.
