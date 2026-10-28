# R10-RCA-PREPR-HEAD-GRADERS: a grader edit every local path passed and CI's base copy refused

The root-cause seat for #2916 (R10-ORCH-BEATD arm a). It ran beside the fix
(`handoff/r10-orch-beatd` `c991d64cd`) and not inside it (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`). Measured 2026-10-28 from 17:30Z to 18:40Z against
`origin/main` `eab04d0eb`. Every time is UTC. Every CI figure was read from the Actions API in that
window. The seat filed no issue and did not edit #2916's branch.

**Result: state (c).** The class has **8 measured pull requests in round 10**, which is past the
audit-class threshold of 3 in one round. Its class, I3, is barriered.

**Cost test: build.**

**Countermeasure: built.** It is `tools/pr/ci_predict.py`'s `graders` arm. The arm runs
`policy_lint.mjs`, `check-wave-script.mjs` and `field_coverage.mjs` under the base's copy, on CI's
merge tree, keyed on the diff editing a file the grader loads. It sits beside the `agreement` arm
(#2707), which already covered the fourth pinned corpus grader. `prepr.sh` step 6d and
`body_push.sh` both run the predictor, so both gain the arm without an edit.

## 1. The defect, reproduced

Trigger 2, a red check. The CI code run on `e09b123f9` (run 40732339443) went red on two jobs:
`governance / policy-docs` (job 122973705767) and `governance / env-matrix` (job 122973705691).

- Both logs print `check source restored from eab04d0eb…: 1 file(s) differ`.
- Both carry the same refusal: `ERROR [named-docs] tools/audit/seat/beatd_shims/git: is named by
  .claude/rules/claim-files.md but has no cap …`.
- The PR body records `prepr.sh` at `f008c2b75` as "rc 0, with 32 ok, 6 skip and 0 REFUSE".
- The PR body records `ci_predict.py` printing "no closures, fast, wave-script or instrument red
  predicted".

`dev/audit/rca/prepr-head-graders/attribute.sh` reproduces CI's verdict:

1. It builds CI's tree: `e09b123f9` merged into `eab04d0eb`, with the base as first parent.
2. It runs the job's grader in a shared throwaway clone whose `origin/main` is the base.
3. It grades the same tree twice: once with the branch's own copies, once with the base's copy of
   each pinned file the branch changed.

| run | `policy_lint.mjs` copy | rc | first refusal |
|---|---|---|---|
| `attribute.sh` on `e09b123f9` / `eab04d0eb` | the branch's (what prepr step 3 ran) | 0 | none |
| the same tree | the base's (what the job's restore step runs) | 1 | `[named-docs] tools/audit/seat/beatd_shims/git` |
| `f008c2b75`'s own worktree, `node tools/policy/policy_lint.mjs` | the branch's | 0 | none, 22.3 s wall |
| the same worktree, after `git checkout 71fe1f7fc -- tools/policy/policy_lint.mjs` | the merge base's | 1 | the same named-docs line, 22.6 s wall |

**Which side moved.** The grader did not move. The branch moved:

- `f008c2b75` added `'tools/audit/seat/beatd_shims/git'` to the `CORPUS_EXCLUDED` Set inside
  `tools/policy/policy_lint.mjs`.
- `tools/policy/policy_lint.mjs` matches the restore step's `'tools/policy/*.mjs'` pathspec. CI
  therefore replaced the branch's copy with the base's before it graded.
- The repair, `c991d64cd`, moved the entry into `dev/governance/config/corpus_excluded.json`, which
  is outside that pathspec. That file's `_why_data_not_source` key has given this same reason since
  #1403.

**The refusal told the fixer to make the edit.** The named-docs message ended "add it to
CORPUS_EXCLUDED with a reason". `CORPUS_EXCLUDED` is the Set inside the pinned program, and no pull
request's CI run reads that Set. The message named the one remedy CI cannot see. The only remedy CI
accepts is the data file.

## 2. Cause

Two mechanisms produce one named cause.

1. **Every local path grades the head's copy of a pinned grader.** `prepr.sh` steps 3–4 run
   `policy_lint.mjs`, the agreement lane and `check-wave-script.mjs` from this head. Step 3f3 runs
   `field_coverage.mjs` from this head too. That is the push-to-main direction.
   `gate-scoping.md`'s "prepr.sh is not CI" section states the asymmetry ("CI grades with the base's
   copy of each pinned grader, prepr with this head's") and cites #2366. It names no detector.
2. **The one local arm that ran the pull-request direction reached one grader of four.**
   - R10-RCA-2671-WAVE-SCRIPT stated the asymmetry for every pinned grader: "No local path runs that
     direction for any pinned grader".
   - That record's countermeasure A was keyed on "the lane's reader closure", meaning the agreement
     lane only.
   - #2707 built A as `ci_predict.py`'s `agreement` arm. `body_push.sh` and `prepr.sh` step 6d both
     run it.
   - The arm's unit is `lane_files()`: `agreement_py.closure` plus the `.mjs` imports of
     `agreement.mjs`. `tools/policy/policy_lint.mjs` is not in that set.
   - So on `f008c2b75` the arm ran and printed nothing. The body's "no … red predicted" line is that
     run.

**The named cause.** In round 10, no local check ran `policy_lint.mjs`, `check-wave-script.mjs` or
`field_coverage.mjs` the way CI grades a pull request: with the base's copy, on the merge of the
head into the base. An exclusion, a rule or a registration written into one of those graders
therefore passed every local path, and only CI refused it. For `named-docs`, the grader's own
message pointed the fixer at that edit.

## 3. Process state: (c)

The process is the pre-handoff gate that predicts CI's verdict. It has two parts:

- `prepr.sh` steps 3–4 and step 6d.
- The `ci_predict.py` run inside `body_push.sh`.

That gate existed, was followed, and passed. The fixer's body quotes both runs. It did not produce
the intended result, because none of its units graded these three programs in the pull-request
direction.

- **Not (a).** A check for this shape existed: the `agreement` arm, since `0c7d6ca4f` (#2707,
  2026-10-24 21:35Z). Its unit did not reach `policy_lint.mjs`.
- **Not (b).** No instruction was broken. The fixer did what the refusal said to do.
- **Not (d).** No precondition changed. The restore pathspec has covered `tools/policy/*.mjs` since
  R9-RO-2, and all three graders lived under it for the whole round.
- **The barrier's unit.** I3's barrier is `field_coverage.mjs`. It perturbs each leaf of a
  registered check's input and runs the real check. It never compares a local verdict with CI's
  verdict, so it cannot reach this shape. The unit that did reach this shape, for one lane, is
  #2707's arm. The countermeasure widens that unit. It does not add a count of arms.

## 4. Reach: the instances

The search had four steps:

1. Read every round-10 first-parent merge into `main` since 2026-10-14: 543 merges. Of those, 70
   touched a path in governance.yml's restore list. The 2 open pull requests with such a path,
   #2910 and #2916, were added.
2. For every commit of those 72 pull requests, read the check-runs for a failed `policy-docs`,
   `env-matrix`, `wave-script`, `briefs` or `pr-contract`. `pr-contract` reds are body checks, so
   they were set aside.
3. Fetch the logs of the 40 remaining failed jobs.
4. Run each candidate through `attribute.sh` at the logged `PINNED`.

Two confounds were removed in step 4:

- `origin/main` is set to `PINNED`. The merge-subject walk reads it (R10-RCA-2671-WAVE-SCRIPT §1).
- For `policy_lint.mjs` and `field_coverage.mjs`, a `gh` stub that exits 1 goes first on `PATH`.
  Both read the live ruleset, which has changed since these runs. Without the stub, every rerun
  read as red on `required-contexts`.

An instance means: on CI's tree, the base's copy is red and the head's copy is green.

| PR | red head(s) | `PINNED` | grader | base copy | head copy | red → next green head |
|---|---|---|---|---|---|---|
| #2207 | `d176dd143`, `4b58d3d6e`, `17fd924a6` | `17f1c55fa` | `check-wave-script.mjs` | FAIL "…the cadence is otherwise read from the round number…" | 0 | 17:25:49 → 19:35:19 on 10-14 (2 h 10 m, 3 red heads) |
| #2366 | `78dbdbda6` | `017045fef` | `agreement.mjs` | `unregistered=1` | 0 | 00:35:18 → 01:25:47 on 10-18 (50 m) |
| #2529 | `e9d54acdf`, `4eac335d8` | `9fdc5846a` | `field_coverage.mjs` | REFUSED "registry: `pinned tools/policy/agreement_restore.py` is unregistered" | 0 | 23:25:04 on 10-20 → 09:52:41 on 10-21 (10 h 28 m, 2 red heads) |
| #2609 | `a0520623a` | `6c8903a44` | `policy_lint.mjs`; `agreement.mjs` | `[named-docs] dev/README.md`; `unregistered=1` | 0; 0 | 11:14:50 → 11:59:10 on 10-22 (44 m) |
| #2636 | `2aa2b5dbe`, `328e222fe` | `d6308d77c` | `field_coverage.mjs` | BLIND "hooks `attribution.commit` …" | 0 | 00:49:15 → 04:25:14 on 10-23 (3 h 36 m, 2 red heads) |
| #2671 | `338c9ba49` | `fd7e289d0` | `agreement.mjs` | `unregistered=3` (R10-RCA-2671-WAVE-SCRIPT §1; not re-run here) | 0 | — |
| #2739 | `9439a0948` | `e97f5749b` | `agreement.mjs` | `unregistered=1` | 0 | 15:00:59 → 18:23:33 on 10-24 (3 h 23 m) |
| #2916 | `e09b123f9` (code `f008c2b75`) | `eab04d0eb` | `policy_lint.mjs` | `[named-docs] tools/audit/seat/beatd_shims/git` | 0 | red at 17:10:29; the repair `c991d64cd` was committed at 17:17:21 and is on the handoff ref only |

**That is 8 pull requests and 9 grader instances in round 10.** The threshold is 3 or more in one
round, so the class is past it. Over 543 merges, that is 1.5 % of pull requests. #2609 and #2916
share one shape: a `named-docs` exclusion written into `CORPUS_EXCLUDED`.

**Not instances.** Each was measured:

| PR | finding |
|---|---|
| #2216 | The base copy is green on CI's tree. Not reproduced. |
| #2423 | Both copies print `divergent=2`, so `prepr.sh` showed the red too. This is R10-RCA-2671-WAVE-SCRIPT's cause 3. |
| #2368, #2390, #2406, #2408, #2415, #2421 | `divergent=2` at base `07a09406a`. This was main's own merge-subject divergence, which #2423 fixed (R10-RCA-2671-WAVE-SCRIPT §4). Not re-run. |
| #2578, #2591 | Both copies refuse with `[budgets] tools/audit/briefs/orchestrator.md`. |
| #2441, #2442, #2589 | `env-matrix` printed "the GitHub API is unreachable". |
| #2673 | Drift in the live required contexts. |

**After the `agreement` arm landed** (2026-10-24 21:35Z), no agreement instance was measured. #2739
went red at 15:00Z that same day, and `0c7d6ca4f` is not in its head. Every instance from the other
three graders falls outside that arm's unit: #2207, #2529, #2636, #2609's `policy_lint` half and
#2916. The arm's existence did not decide these outcomes; its unit did.

**Earlier rounds.**

- #1403 is the same shape: round evidence and its exclusions shipped in one branch. It is why
  `corpus_excluded.json` exists.
- #1633 (R9-RC1) is the opposite direction: the head's copy was red and the base's was green.
  `prepr.sh` steps 3e–3g were built for that direction.

## 5. Cost test

The unit is wall-clock seconds per pull request.

### cost(defect), per occurrence, measured

- **One CI run to a visible red.** On #2916 the push came at 17:05:13 and the red at 17:10:29:
  316 s. Runner time was 65 s for `policy-docs` and 153 s for `env-matrix`. The CI code run kept
  running until 17:47:13.
- **A fixer round, from the red to the next green head.** The six measured rounds were 44 m, 50 m,
  2 h 10 m, 3 h 23 m, 3 h 36 m and 10 h 28 m. The median is 2 h 46 m, or 9,960 s.
- **Re-review: none measured.** The bus holds no verdict on any red head of #2207, #2366, #2529,
  #2609, #2636 or #2739, because in each case the red came before the review. For #2916, the review
  owed at open on `e09b123f9` is superseded by the repair head.

### P(recurrence)

This counts only the shapes the `agreement` arm does not cover: #2207, #2529, #2609's
`policy_lint` half, #2636 and #2916. That is 5 in 543 round-10 merges, or 0.92 %.

### Expected defect cost per pull request

- CI floor only: 0.0092 × 316 s = 2.9 s.
- With the fixer round: 0.0092 × 9,960 s = 92 s.

### cost(countermeasure, recurring), measured on this branch

**When no key is hit**, the arm adds 0.1–0.3 s to a predictor run. `--only graders` took 0.55, 0.57
and 0.76 s. `--only orphans` took 0.45, 0.42 and 0.38 s.

**Each grader's key and its cost when hit:**

| grader | key | merges keyed (of 543) | measured cost when keyed |
|---|---|---|---|
| `policy_lint.mjs` | a file in its 5-file `.mjs` closure | 15 | 26 s on `f008c2b75`; 34 s on `c991d64cd` with a comment |
| `check-wave-script.mjs` | a file in its 2-file closure | 10 | 3 s on #2207 |
| `field_coverage.mjs` | its own file only | 7 | 107 s on #2529; 134 s on #2636 |

`field_coverage.mjs` is keyed on its own file only because its closure holds `policy_lint.mjs`.
Keying it on the closure would add a 110 s run to every `policy_lint.mjs` edit.

**Weighted:** 0.2 + (15 × 30 + 10 × 3 + 7 × 120) / 543 = 2.6 s per predictor run. The predictor
runs once per handoff in `body_push.sh` and once per `prepr.sh` run in step 6d. At about 3 runs per
pull request, that is about 7.8 s per pull request.

| | per pull request |
|---|---|
| standing cost (about 3 predictor runs) | 7.8 s |
| expected defect cost, CI floor only | 2.9 s |
| expected defect cost, with the fixer round | 92 s |

### Verdict: build

- On the CI floor alone, the arm does not pay for itself.
- Counting the fixer round, it pays for itself 12 times over, and the round-10 record shows that
  round every time.
- The barrier rule binds either way. The class is past the per-round threshold, and I3 is
  barriered. The cost test only picks the form.
- The cheapest form is the existing arm's unit, widened. A second implementation in `prepr.sh`
  would cost more and buy nothing: see section 6.

## 6. Countermeasure, built

### Why `ci_predict.py` and not a `prepr.sh` step

The brief proposed a `prepr.sh` step. It was drafted and self-tested (9 rows, with 7 of 7 mutants
killed). It was then withdrawn, for three reasons:

- `ci_predict.py` already builds CI's tree for the `agreement` arm: the merge into the tip, the
  job's restore pathspecs and `origin/main`. A `prepr.sh` step would be a second copy of that code.
- `body_push.sh` runs only the predictor, so a `prepr.sh` step would leave the handoff gate blind.
  #2707's body records this same split.
- `prepr.sh` step 6d already runs the predictor, so `prepr.sh` gains the arm with no edit.

### What changed

**`tools/pr/ci_predict.py`:**

- The tree build in `agreement_preds` is factored into `ci_tree_run(root, tip, job, steps)`. The
  `agreement` arm calls it, and its behaviour is unchanged.
- `mjs_closure` is factored out of `lane_files`.
- A `graders` arm is added over a `GRADERS` table:

  | grader | restore list | red reported on | marker |
  |---|---|---|---|
  | `policy_lint.mjs` | `policy-docs`' | `policy-docs` and `env-matrix` | `CORPUS` |
  | `check-wave-script.mjs` | `wave-script`'s | `wave-script` | `WAVE CHECK` |
  | `field_coverage.mjs` | `policy-docs`' | `policy-docs` | `FIELD COVERAGE` |

- `grader_hit` keys each grader. A changed file keys it when the file is in the grader's key set
  and is covered by the job's restore pathspecs (`agreement_py.covers`). Only there can the head's
  copy and the base's copy differ. A data file such as `corpus_excluded.json` reaches CI as the
  branch has it, so it keys nothing.
- The arm's repair line says what to do: move the entry into the data the grader reads, or land the
  grader change first.

**`tools/policy/agreement_py.py`:** `restore_specs(text, name=JOB)` now reads any job's restore list.
The default is unchanged, so CI's base copy calls it as before.

**`tools/policy/policy_lint.mjs`:** the `named-docs` refusal now names `corpus_excluded.json`'s
`excluded` list. It says why the Set is not read on a pull request, and it cites #2609 and #2916.
This fixes the message half of the cause. The edit is text in a pinned grader, so this branch's own
`policy-docs` grades it with the base's copy. That works, because no verdict changes.

### Demonstration

The runs use `dev/audit/rca/prepr-head-graders/demo.sh`. Each one is a shared throwaway clone at the
head, with `origin/main` set to the base. This branch's predictor is copied in uncommitted, so it
changes what predicts and never what is predicted. FIELD COVERAGE runs have the `gh` stub on
`PATH`.

| head | base | result | s |
|---|---|---|---|
| `f008c2b75` (#2916, before the repair) | `eab04d0eb` | **rc 1** — `PREDICT governance / policy-docs CORPUS REFUSED by the base's copy, over tools/policy/policy_lint.mjs: ERROR [named-docs] tools/audit/seat/beatd_shims/git …`, the same line for `env-matrix`, and the repair line | 26 |
| `c991d64cd` (the repair) | `eab04d0eb` | rc 0, not keyed. CI grades with the copies prepr ran, and step 3's `policy_lint` passes there | 0 |
| `c991d64cd` plus a comment in `policy_lint.mjs`, so the arm runs (null control) | `eab04d0eb` | **rc 0** | 34 |
| #2737's head `deb7a4c1e^2`, which edited `policy_lint.mjs` and was green on CI (null control) | `deb7a4c1e^1` | rc 0 | 47 |
| `d176dd143` (#2207) | `17f1c55fa` | rc 1, `WAVE CHECK REFUSED … FAIL …the cadence is otherwise read from the round number` | 3 |
| `98bd07a62` (#2207's green head) | `97750ec79` | rc 0 | 0 |
| `e9d54acdf` (#2529) | `9fdc5846a` | rc 1, `FIELD COVERAGE REFUSED … registry: pinned tools/policy/agreement_restore.py is unregistered` | 107 |
| `2aa2b5dbe` (#2636; it also edits `policy_lint.mjs`, and CORPUS stays green, as CI's did) | `d6308d77c` | rc 1, `FIELD COVERAGE REFUSED … BLIND hooks attribution.commit` | 134 |

### Self-test

`python3 -I tools/pr/ci_predict.py --self-test` prints `0 failed`. It adds these rows:

- **Three `plant_self_test` cases:**
  - #2916's shape is predicted red: an executable named `git` under `tools/audit/seat/`, excluded
    only in the head's `policy_lint.mjs`.
  - The repair is predicted green: the same entry in `corpus_excluded.json`, with `policy_lint.mjs`
    still edited so that the arm runs.
  - The plant staged but not committed is predicted green.
- **Six `grader_key_self_test` rows:**
  - CORPUS is keyed by `policy_lint.mjs` and by `counts.mjs`, and not by `corpus_excluded.json`.
  - WAVE CHECK is not keyed by `policy_lint.mjs`.
  - FIELD COVERAGE is keyed by its own file, and not by `policy_lint.mjs`.

Mutation proof is in the pull-request body.

## 7. Recorded

- `bugclasses.json` `_rca["R10-RCA-PREPR-HEAD-GRADERS"]`, class I3, added to I3's `rca` list.
- **A policy line, proposed and not made.** `gate-scoping.md`'s "prepr.sh is not CI" section names
  no detector for its asymmetry. The proposed line: "step 6d's `ci_predict.py` runs
  `policy_lint.mjs`, `check-wave-script.mjs`, `field_coverage.mjs` and the agreement lane under the
  base's copy when the diff edits one". That file is policy, so the owner approves it.
- **Left open.** `brief_lint.mjs` (`briefs`, tests.yml) is a pinned grader with no pull-request
  direction arm. The round shows no `briefs` instance, so this record does not cost it. Adding it is
  one `GRADERS` row and its key.
