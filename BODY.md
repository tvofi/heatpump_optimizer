R10-RCA-PREPR-HEAD-GRADERS is the root-cause record for #2916's red `governance / policy-docs` and `governance / env-matrix`. It also builds the countermeasure that record calls for.

`f008c2b75` wrote a `named-docs` exclusion into `tools/policy/policy_lint.mjs`'s `CORPUS_EXCLUDED`. CI's restore step graded the PR with the base's copy of that file, so the exclusion was never read. `prepr.sh` and `ci_predict.py` were both green on the same head.

The record is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md`, and `dev/audit/config/bugclasses.json` cites it under `_rca` and class I3. Its harnesses are in `dev/audit/rca/prepr-head-graders/`.

**Process state: (c).**
- `prepr.sh` steps 3–4 and 3f3 grade the head's copy, which is the push-to-main direction.
- #2707's `agreement` arm grades the base's copy, but its unit (`lane_files()`) holds only the agreement lane.
- The `named-docs` message itself directed the fixer to the pinned Set.

**Class: past the audit-class threshold.** Eight round-10 pull requests went red because CI graded a pinned grader the branch edited with the base's copy. In each, the base's copy is red and the head's copy is green, on CI's own merge tree.

| PR | grader |
|---|---|
| #2207 | `check-wave-script.mjs` |
| #2366 | `agreement.mjs` |
| #2529 | `field_coverage.mjs` |
| #2609 | `policy_lint.mjs` and `agreement.mjs` |
| #2636 | `field_coverage.mjs` |
| #2671 | `agreement.mjs` |
| #2739 | `agreement.mjs` |
| #2916 | `policy_lint.mjs` |

I3 is barriered, and the barrier's unit (`field_coverage.mjs`) never compares a local verdict with CI's.

**Cost test: build.**

| figure | value |
|---|---|
| standing cost per predictor run | about 2.6 s |
| standing cost per PR (about 3 runs) | about 7.8 s |
| expected defect cost per PR, CI floor only | 2.9 s |
| expected defect cost per PR, with the measured fixer round (median 2 h 46 m) | 92 s |

**Countermeasure.** A `graders` arm in `tools/pr/ci_predict.py`, beside `agreement`, through the factored `ci_tree_run`. It runs three graders under the base's copy:

| grader | marker | key |
|---|---|---|
| `policy_lint.mjs` | `CORPUS` (reported on `policy-docs` and `env-matrix`) | its `.mjs` closure |
| `check-wave-script.mjs` | `WAVE CHECK` | its `.mjs` closure |
| `field_coverage.mjs` | `FIELD COVERAGE` | its own file only, because its run takes about 110 s |

`prepr.sh` step 6d and `body_push.sh` both run the predictor, so this PR does not edit `prepr.sh`. The record's section 6 explains why the brief's `prepr.sh` step was drafted and then withdrawn: it would duplicate the tree build and leave the handoff gate blind.

Two smaller edits come with the arm:
- `agreement_py.restore_specs` now takes a job name. The default is unchanged.
- The `named-docs` refusal in `policy_lint.mjs` now points at `corpus_excluded.json`, not at the Set.

**Owner approval.** This PR touches no code-owned path. The record proposes, and does not make, one line for `gate-scoping.md` (record section 7). That line is policy and needs the owner's approval.

## Head

`744734457d` is the head. It is the authored commits `f37ac7916`..`27ec34825` with `origin/main` `beb570c81` merged in, a clean automatic merge. The branch was cut from `origin/main` `eab04d0eb`.

## Mutation proof

**The arm, through `python3 -I tools/pr/ci_predict.py --self-test`.** Each mutant ran from a copy of `tools/pr/ci_predict.py`:

| mutant | what it changes | result | rows that went red |
|---|---|---|---|
| M1 | the `graders` entry dropped from `predict`'s arms | 1 failed | `an exclusion written into the head's policy_lint.mjs only is predicted red (#2916)` |
| M2 | `ci_tree_run`'s pathspec restore from the tip deleted | 3 failed | that row; `a grammar registered only in the head's copy is predicted red`; `a head copy of the lane that exits 1 is predicted green (null control: CI runs the base's)` |
| M3 | the REFUSED prediction dropped | 1 failed | the #2916 row |

M2 shows that the factoring is shared code: one restore serves both arms.

**The key, in process (`grader_key_self_test`):**

| mutant | what it changes | result |
|---|---|---|
| M4 | FIELD COVERAGE keyed on its whole closure | 1 failed: `and not by policy_lint.mjs, which its closure holds` |
| M5 | `grader_hit`'s restore-pathspec filter dropped | 0 failed |

M5 is equivalent on today's pathspecs. Every `.mjs` in these closures is under `tools/policy/*.mjs`, which every pinned job restores. The filter is kept because it states the rule: only a restored file can differ.

## Null control

**Demonstrations** with `bash dev/audit/rca/prepr-head-graders/demo.sh <head> <base> <out> [comment]`:

| head | base | result | time |
|---|---|---|---|
| `f008c2b75` (#2916 pre-fix) | `eab04d0eb` | rc 1. Prints `PREDICT governance / policy-docs CORPUS REFUSED by the base's copy, over tools/policy/policy_lint.mjs: ERROR   [named-docs] tools/audit/seat/beatd_shims/git: …`, the same for `env-matrix`, and the CORPUS repair line | 26 s |
| `c991d64cd` (the repair) | `eab04d0eb` | rc 0, not keyed | — |
| `c991d64cd` plus a comment in `policy_lint.mjs`, so the arm runs | `eab04d0eb` | rc 0 | 34 s |
| #2737 (`deb7a4c1e^2` against `^1`; edited `policy_lint.mjs`, green on CI) | `deb7a4c1e^1` | rc 0 | 47 s |
| #2207 `d176dd143` | `17f1c55fa` | rc 1, WAVE CHECK | — |
| #2207's green head `98bd07a62` | `97750ec79` | rc 0 | — |
| #2529 `e9d54acdf` | `9fdc5846a` | rc 1, FIELD COVERAGE `agreement_restore.py is unregistered` | — |
| #2636 `2aa2b5dbe` | `d6308d77c` | rc 1, FIELD COVERAGE BLIND. It also edits `policy_lint.mjs`, and CORPUS stays green, as CI's did | — |

**Self-test at the head:** `ci_predict self-test: 0 failed`.

## Figures

- 543 round-10 first-parent merges since 2026-10-14; 70 of them, plus open #2910 and #2916, touch a restored path: `git log origin/main --first-parent --merges --since=2026-10-14 --oneline`, each diffed against the restore pathspecs.
- The base-copy and head-copy verdict of each candidate, on CI's tree: `bash dev/audit/rca/prepr-head-graders/attribute.sh <head> <PINNED> <job> <out>`, with each run's `PINNED` read from its job log (`check source restored from …`).
- #2916's red at 17:10:29 after the 17:05:13 push (316 s); `policy-docs` 65 s and `env-matrix` 153 s of runner time: `gh api repos/tvofi/heatpump_optimizer/commits/e09b123f9653c446c4afac46bfbc4948d1460f0c/check-runs`.
- The six fixer rounds from red to the next green head (44 m, 50 m, 2 h 10 m, 3 h 23 m, 3 h 36 m, 10 h 28 m): each PR's commits with their `policy-docs` or `wave-script` check-run, `gh api repos/tvofi/heatpump_optimizer/pulls/<N>/commits`.
- Keys hit 15 (`policy_lint` closure), 10 (`check-wave-script` closure) and 7 (`field_coverage.mjs`) of 543 merges: `git diff --name-only <merge>^1...<merge>^2` over the same merges.
- Unkeyed overhead: `--only graders` 0.55, 0.57 and 0.76 s, against `--only orphans` 0.45, 0.42 and 0.38 s: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --only graders`.
- Keyed run times of 26, 34, 47, 3, 107 and 134 s: the `seconds=` line of `bash dev/audit/rca/prepr-head-graders/demo.sh`.
- `policy_lint.mjs` at `f008c2b75` took 22.3 s with the head's copy and 22.6 s with the merge base's: `node tools/policy/policy_lint.mjs` under `/usr/bin/time -p`.
- `fold_ledger: 0 violation(s)`, with 126 rca entries before this one: `python3 -I tools/audit/fold_ledger.py check`.

## Red checks

none

## Forward-carry

none

## Friction

none
