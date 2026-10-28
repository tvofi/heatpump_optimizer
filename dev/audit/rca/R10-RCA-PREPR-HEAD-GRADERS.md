# R10-RCA-PREPR-HEAD-GRADERS: a grader edit every local path passed and CI's base copy refused

The root-cause seat for #2916 (R10-ORCH-BEATD arm a). It ran beside the fix
(`handoff/r10-orch-beatd` `c991d64cd`) and not inside it (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`). Measured 2026-10-28 from 17:30Z to 18:40Z against
`origin/main` `eab04d0eb`. Every time is UTC. Every CI figure was read from the Actions API in that
window. The seat filed no issue and did not edit #2916's branch.

**Result: state (c).** The class has **8 measured pull requests in round 10**, which is past the
audit-class threshold of 3 in one round. Its class, I3, is barriered.

**Cost test: build.**

**Countermeasure: built.** It is `tools/pr/ci_predict.py`'s `graders` arm. The arm runs, under
the base's copy and on CI's merge tree, every program the three pinned jobs restore and run:
`policy_lint.mjs` (default and `--hooks`), `check-wave-script.mjs`, `field_coverage.mjs`,
`rules_sync.mjs --check`, `fragments_sync.mjs`, `codeowners_gap.py --check` and
`agreement.mjs --self-test`. Each is keyed on the diff editing a file it loads. The population is
derived from governance.yml's own run lines (`pinned_runs`), not listed by hand, and the
self-test refuses a restored run that no arm covers (`grader_gaps`, section 6). The arm sits
beside the `agreement` arm (#2707), which covers the lane's `--py-json` run. `prepr.sh` step 6d
and `body_push.sh` both run the predictor, so both gain the arm without an edit.

**Round 2** (fix review blocked round 1, `class-open` at `718ed364d`). Round 1 took the population
from the measured instances: four graders. The reviewer enumerated it from the pinned jobs and
found five more runs: `rules_sync.mjs --check`, `fragments_sync.mjs`, `codeowners_gap.py --check`,
`policy_lint.mjs --hooks` and `agreement.mjs --self-test`. The derivation also found a sixth, an
indirect one: `env-matrix`'s head-copy `policy_lint_envmatrix.mjs` spawns `check-wave-script.mjs`
as well as `policy_lint.mjs`, so a WAVE CHECK red reaches `env-matrix` too. Section 4 measures
every run's round-10 instances; section 6 covers all of them.

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
2. **The one local arm that ran the pull-request direction reached two runs of eleven** (the
   restored runs section 4 enumerates, the lane's `--out` and `--py-json`; round 1 said "one grader of four", counting only the graders
   that went red).
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
the intended result, because none of its units graded `policy_lint.mjs`, `check-wave-script.mjs`
or `field_coverage.mjs` (the three that went red) in the pull-request direction.

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

**The population, and the runs with no instance (round 2).** `pinned_runs` reads every
`node`/`python3` run in the `policy-docs`, `env-matrix` and `wave-script` jobs of governance.yml,
keeps the layout the tree holds, and marks each run the job restores (`agreement_py.covers` over
that job's own restore list). Restored runs: `policy_lint.mjs` (default, `--hooks`, `--report`),
`field_coverage.mjs`, `rules_sync.mjs --check`, `fragments_sync.mjs`, `codeowners_gap.py --check`
(policy-docs); `check-wave-script.mjs`, `agreement_py.py --out`, `agreement.mjs --py-json`,
`agreement.mjs --self-test` (wave-script). Head-copy runs: `policy_lint_envmatrix.mjs`
(env-matrix), which spawns `policy_lint.mjs` and `check-wave-script.mjs`, and `fold_ledger.py`
(wave-script), which spawns no grader.

The failed step of each of the 40 red pinned jobs above was read from the jobs API
(`.steps[] | select(.conclusion == "failure")`). Every one failed in "Lint the policy corpus" (5),
"Refuse a governance check input field no check reads" (2), "Drive the wave script's branching"
(2), "Refuse two readers of one concept that disagree" (11) or "Require each declared environment
shape to produce its declared outcome" (8). **None failed in the `rules_sync.mjs --check`,
`fragments_sync.mjs`, `codeowners_gap.py --check`, `policy_lint.mjs --hooks` or
`agreement.mjs --self-test` step: zero round-10 instances for those five runs.** A job stops at
its first failing step, so a later step's red under an earlier one is not counted; no PR in the
set had such a pair after its repair. They are covered anyway (section 6), because each costs
0.2–6.5 s and shares the clone the measured graders already pay for. `policy_lint.mjs --report`
is exempt: its step ends `|| true`.

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

Round 2's figures, re-taken over the same 543 merges (to `beb570c81`) with the round-2 arm:

**When no key is hit**, the arm adds about 0.6 s to a predictor run: `--only graders` 1.22, 1.01
and 1.03 s against `--only orphans` 0.41, 0.51 and 0.45 s, in a clone at `origin/main` with this
branch's predictor copied in. (Round 1's three rows cost 0.1–0.3 s; seven rows walk seven
closures.)

**Each row's key, with merges keyed (of 543):**

| row | key | keyed | runtime alone on this tree |
|---|---|---|---|
| CORPUS (`policy_lint.mjs`, default and `--hooks`) | its 5-file `.mjs` closure | 16 | 22 s and 6.2 s |
| WAVE CHECK (`check-wave-script.mjs`) | its 2-file closure | 10 | 3 s |
| FIELD COVERAGE (`field_coverage.mjs`) | its own file | 7 | about 110 s |
| RULES SYNC (`rules_sync.mjs --check`) | its 6-file closure | 16 | 0.2 s |
| FRAGMENTS (`fragments_sync.mjs`) | its 2-file closure | 2 | 1.7 s |
| CODEOWNERS (`codeowners_gap.py --check`) | its own file (Python) | 1 | 6.5 s |
| LANE SELF-TEST (`agreement.mjs --self-test`) | its 7-file closure | 20 | 1.4 s |

All rows of one job share one CI tree, built once (`grader_preds` groups by job). Any row keyed:
30 of 543 merges. Measured with both trees built and every keyed row run: 44 s on `f008c2b75`, 41 s
on `c991d64cd` with a comment, 41.0–42.9 s on this branch's own head (3 runs).
`field_coverage.mjs` is keyed on its own file only because its closure holds `policy_lint.mjs`.

**Weighted:** 0.6 + (30 × 42 + 7 × 110) / 543 = 4.3 s per predictor run. The predictor runs once
per handoff in `body_push.sh` and once per `prepr.sh` run in step 6d. At about 3 runs per pull
request, that is about 13 s per pull request.

| | per pull request |
|---|---|
| standing cost (about 3 predictor runs) | 13 s |
| expected defect cost, CI floor only | 2.9 s |
| expected defect cost, with the fixer round | 92 s |

**Round 3's key**, re-taken with `dev/audit/rca/prepr-head-graders/keycount.py beb570c81
2026-10-14` (539 merges by its rule, `git rev-list --first-parent --merges --since=2026-10-14`;
the round-2 key counted by that same rule is its null control and reproduces round 2's file counts):

| row | round-2 key, keyed | round-3 key, keyed |
|---|---|---|
| CORPUS | 5 files, 15 | 7 files, 21 |
| WAVE CHECK | 2 files, 9 | 12 files, 32 |
| FIELD COVERAGE | 1 file, 7 | 8 files, 27 |
| RULES SYNC | 6 files, 15 | 8 files, 21 |
| FRAGMENTS | 2 files, 2 | 3 files, 4 |
| CODEOWNERS | 1 file, 1 | 3 files, 7 |
| LANE SELF-TEST | 7 files, 19 | 12 files, 28 |
| any row | 28 | 40 |

When no key is hit, `--only graders` takes 0.85–0.88 s against `--only orphans` 0.16–0.20 s (3
runs each, `named_loads` and the Python-import walk cached per file): about 0.7 s.

**Weighted, round 3:** FIELD COVERAGE's 27 keyed merges at the plant's 289 s, an upper bound since
it runs five rows, and the other 13 at round 2's 42 s, not re-taken: 0.7 + (27 × 289 + 13 × 42) /
539 = 16.2 s per predictor run, about 49 s per pull request at 3 runs. That is under the 92 s
expected defect cost with the fixer round, so the verdict below holds, with less margin than
round 2's 13 s.

### Verdict: build

- On the CI floor alone, the arm does not pay for itself.
- Counting the fixer round, it pays for itself about 1.9 times over at round 3's key (92 s against
  49 s; round 2's narrower key, 7 times), and the round-10 record shows that round every time. The five round-2 rows have no instance and add about 1.5 s per run
  (their key hits, mostly inside trees the measured rows already build); they are built because
  the class is the restored runs, not the ones that happened to go red.
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

  | grader (modes) | restore list | red reported on | marker |
  |---|---|---|---|
  | `policy_lint.mjs` (default, `--hooks`) | `policy-docs`' | `policy-docs` and `env-matrix` | `CORPUS` |
  | `check-wave-script.mjs` | `wave-script`'s | `wave-script` and `env-matrix` | `WAVE CHECK` |
  | `field_coverage.mjs` | `policy-docs`' | `policy-docs` | `FIELD COVERAGE` |
  | `rules_sync.mjs --check` | `policy-docs`' | `policy-docs` | `RULES SYNC` |
  | `fragments_sync.mjs` | `policy-docs`' | `policy-docs` | `FRAGMENTS` |
  | `codeowners_gap.py --check` | `policy-docs`' | `policy-docs` | `CODEOWNERS` |
  | `agreement.mjs --self-test` | `wave-script`'s | `wave-script` | `LANE SELF-TEST` |

  A refusal in a non-default mode names it (`CORPUS --hooks REFUSED …`). One CI tree per job runs
  every keyed row and mode.
- `pinned_runs` and `grader_gaps` close the population over governance.yml. A restored run must
  be a row's (in that mode, reaching that job), one of `AGREEMENT_RUNS` (the `agreement` arm's
  `--out` and `--py-json`) or in `GRADER_EXEMPT` with its reason (`policy_lint.mjs --report`: the
  step ends `|| true`). A job whose head-copy program names a row's grader as a quoted program
  (`'policy_lint.mjs'` in `policy_lint_envmatrix.mjs`) must be in that row's reds. The self-test
  holds the gap list empty, so a run line added to a pinned job with no arm turns
  `ci_predict.py --self-test` red. WAVE CHECK reaching `env-matrix` was found this way: the arm
  grades `check-wave-script.mjs` on CI's tree, not in `env-matrix`'s no-rosters shape, which stays
  host-dependent (`prepr.sh`'s `PINNED_ELSEWHERE`).

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

### Round 3: what a grader names keys it

Review round 2 blocked on a seam the round-2 rule could not see. `policy_lint.mjs` runs
`budget_raise_gate.py` (`raiseJustification`) in its own fixture acceptance, `policy-docs` restores
`tools/policy/*.py`, and `mjs_closure` followed only `.mjs` imports and `load`/`at` literals. So a
head edit to `budget_raise_gate.py`, with the fixture it grades, was predicted green and went red
under the base's copy.

The class is every restored file a row's grader loads, not only the programs it spawns. The rule
that enumerates it is `named_loads`: each quoted program or module path (`.mjs`, `.py`, `.sh`) and
each `path.join` of literals in a source the row's key holds, resolved beside the source, from the
root, or through layout's move map. A static `from '…'` import is the import arm's.

- `mjs_closure` follows `named_loads` and a Python file's tracked imports, transitively. `whole`
  still decides whether static `.mjs` imports are followed, so FIELD COVERAGE's 110 s run stays off
  `policy_lint.mjs`'s import closure.
- `grader_gaps` scans every source in each row's key. A named file the job restores, outside the
  row's key and on no `GRADER_NAMED_EXEMPT` site, is a gap. So is an exempt site that no source
  still holds. An exempt site is keyed on (the naming file, the file named, that line's text), so a
  load added on another line keys and is never silenced.

The seams the rule returns, from the key with `named_loads` removed (`grader_gaps(…,
key=lambda e, w: mjs_closure(root, e, imports=w, named=False))`): 42 sites naming 10 files, each
below; `tests/layout.py` is the Python-import arm's, which the rule does not enumerate:

| row | named at | file | disposition |
|---|---|---|---|
| CORPUS, FIELD COVERAGE, RULES SYNC, WAVE CHECK, LANE SELF-TEST | `policy_lint.mjs` (`raiseJustification`) | `tools/policy/budget_raise_gate.py` | keyed (the review's plant) |
| those five | `budget_raise_gate.py`'s import | `tests/layout.py` | keyed (Python-import arm) |
| FIELD COVERAGE, WAVE CHECK | `policy_lint.mjs`, a named `brief_lint.mjs` | `tools/policy/brief_lint.mjs` | keyed |
| LANE SELF-TEST, WAVE CHECK | `stamp.py` | `tests/delivery_status.py` | keyed |
| WAVE CHECK | `check-wave-script.mjs`, three run-time `import()`s | `tools/policy/policy_lint.mjs` | keyed |
| WAVE CHECK | `check-wave-script.mjs`, an `at()` read | `tools/audit/prepare_baseline.sh` | keyed |
| FIELD COVERAGE | `field_coverage.mjs`, `--hooks` spawn | `tools/policy/policy_lint.mjs` | keyed |
| FIELD COVERAGE | `field_coverage.mjs`, a `python3 -c` import | `tools/policy/budget_raise_gate.py` | keyed |
| FIELD COVERAGE | `field_coverage.mjs`, a `locate()` spawn | `codeowners_gap.py` | keyed |
| FIELD COVERAGE | `field_coverage.mjs`, a `path.join(HERE, …)` import | `tools/policy/counts.mjs` | keyed |
| CODEOWNERS, FIELD COVERAGE | `codeowners_gap.py` | `tools/coverage/coverage_tree.sh` | keyed |
| LANE SELF-TEST | `agreement.mjs`, an `at()` path for `sys.path` | `tests/throwaway_git.py` | keyed |
| LANE SELF-TEST, WAVE CHECK | `policy_lint.mjs`, `path.join(ROOT, 'tools', 'release', 'stamp.py')` | `tools/release/stamp.py` | keyed |
| CORPUS and the rows importing it | `policy_lint.mjs`'s `REPORTER_INPUTS` | `tests/delivery_status.py` | exempt: a path compared with a diff's, never read |
| CODEOWNERS | `codeowners_gap.py`'s EXEC self-test case | `tools/policy/policy_lint.mjs` | exempt: run text parsed, never run |

The plant from the review, re-run on this branch (`demo`-style, the plant committed on the head):

| predictor at | base | result | s |
|---|---|---|---|
| `38422dd15` (round 2's head) | the head | rc 0, `budget_raise_gate.py` keys nothing | 0 |
| `c8eb2dc51` (round 3) | the head | **rc 1**, `CORPUS REFUSED by the base's copy, over tools/policy/budget_raise_gate.py: FIXTURE VACUOUS: the raise-justification arm on prepr/raise/good.md drew 1 error(s)`, on `policy-docs` and `env-matrix` | 289 |

The plant is review round 2's `plant.diff`: `JUSTIFICATION_SCORE` accepts `Arch score: dS`, and
`fixtures/policy-rot/prepr/raise/good.md` uses that spelling. The 289 s run builds both trees and
runs five rows (CORPUS in two modes, FIELD COVERAGE, RULES SYNC, WAVE CHECK, LANE SELF-TEST).

### Demonstration

The runs use `dev/audit/rca/prepr-head-graders/demo.sh`. Each one is a shared throwaway clone at the
head, with `origin/main` set to the base. This branch's predictor is copied in uncommitted, so it
changes what predicts and never what is predicted. FIELD COVERAGE runs have the `gh` stub on
`PATH`.

| head | base | result | s |
|---|---|---|---|
| `f008c2b75` (#2916, before the repair) | `eab04d0eb` | **rc 1** — `PREDICT governance / policy-docs CORPUS REFUSED by the base's copy, over tools/policy/policy_lint.mjs: ERROR [named-docs] tools/audit/seat/beatd_shims/git …`, the same line for `env-matrix`, and the repair line. Round 2: the same two lines; RULES SYNC, CORPUS `--hooks` and LANE SELF-TEST, keyed by the same file, run and pass | 26 (round 2: 44) |
| `c991d64cd` (the repair) | `eab04d0eb` | rc 0, not keyed. CI grades with the copies prepr ran, and step 3's `policy_lint` passes there | 0 |
| `c991d64cd` plus a comment in `policy_lint.mjs`, so the arm runs (null control) | `eab04d0eb` | **rc 0** (round 2: rc 0, all keyed rows run) | 34 (round 2: 41) |
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
- **Fifteen `grader_key_self_test` rows:**
  - CORPUS is keyed by `policy_lint.mjs` and by `counts.mjs`, and not by `corpus_excluded.json`.
  - CORPUS is keyed by `budget_raise_gate.py`, which `policy_lint.mjs` spawns, and by
    `tests/layout.py`, which that program imports.
  - WAVE CHECK is keyed by `policy_lint.mjs`, which `check-wave-script.mjs` imports at run time.
  - FIELD COVERAGE is keyed by its own file and by `policy_lint.mjs`, which it runs with `--hooks`,
    and not by `render_md.mjs`, which only `policy_lint.mjs`'s static imports reach.
  - RULES SYNC is keyed by `rules_sync.mjs`; CODEOWNERS by `codeowners_gap.py`, and not by
    `policy_lint.mjs`, which it names only in an exempt site.
  - Every restored pinned run is predicted or exempt, and every restored file a grader names is in
    its key or on an exempt site (null control: the gap list is empty).
  - Five perturbations are each named as a gap: CORPUS without `env-matrix` (round 1's surviving
    M7), the RULES SYNC row dropped, CORPUS without `--hooks`, a key blind to named files
    (`budget_raise_gate.py` under CORPUS), and an exempt site no source holds.

Mutation proof is in the pull-request body.

## 7. Recorded

- `bugclasses.json` `_rca["R10-RCA-PREPR-HEAD-GRADERS"]`, class I3, added to I3's `rca` list.
- **A policy line, proposed and not made.** `gate-scoping.md`'s "prepr.sh is not CI" section names
  no detector for its asymmetry. The proposed line: "step 6d's `ci_predict.py` runs
  `policy_lint.mjs`, `check-wave-script.mjs`, `field_coverage.mjs` and the agreement lane under the
  base's copy when the diff edits one". That file is policy, so the owner approves it.
- **Left open.** `brief_lint.mjs` (`briefs`, tests.yml) is a pinned grader with no pull-request
  direction arm; `pinned_runs` reads governance.yml's three pinned jobs only. The round shows no
  `briefs` instance (no failed `briefs` check-run among the 72 pull requests), so this record does
  not cost it. Adding it is one `GRADERS` row, its key, and tests.yml in `pinned_runs`.
- **Carried, not fixed here.** The round-1 review found `review_packet.py render` refusing
  `host-path` on this record because `ref_privacy._leaks` matches the host's home as a bare
  substring: under `HOME=/root` (a cloud seat) every citation of `dev/governance/roles/root-cause.md`
  matches. It is an instrument defect in `tools/audit/seat/ref_privacy.py`, outside this record's
  class; it is carried to R10-RECORD-API-O1, the open group that owns that file. That group's
  roster `brief` and `carry` in `dev/programme/rosters/wave-r10-groups.json` already hold it, from
  #2852's fix review (`9573269b1`); read back with `jq '.. | objects | select(.group? ==
  "R10-RECORD-API-O1") | to_entries[] | select(.value|tostring|contains("no path-segment
  boundary")) | .key'`, which prints `carry` and `brief` on this tree and on `origin/main`.
