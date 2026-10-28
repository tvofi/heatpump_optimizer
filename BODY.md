R10-RCA-PREPR-HEAD-GRADERS is the root-cause record for #2916's red `governance / policy-docs` and `governance / env-matrix`. It also builds the countermeasure that record calls for.

`f008c2b75` wrote a `named-docs` exclusion into `tools/policy/policy_lint.mjs`'s `CORPUS_EXCLUDED`. CI's restore step graded the PR with the base's copy of that file, so the exclusion was never read. `prepr.sh` and `ci_predict.py` were both green on the same head.

The record is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md`, and `dev/audit/config/bugclasses.json` cites it under `_rca` and class I3. Its harnesses are in `dev/audit/rca/prepr-head-graders/`.

**Process state: (c).**
- `prepr.sh` steps 3–4 and 3f3 grade the head's copy, which is the push-to-main direction.
- #2707's `agreement` arm grades the base's copy, but its unit (`lane_files()`) holds only the agreement lane: two of the eleven runs the pinned jobs restore.
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
| standing cost per predictor run | about 4.3 s |
| standing cost per PR (about 3 runs) | about 13 s |
| expected defect cost per PR, CI floor only | 2.9 s |
| expected defect cost per PR, with the measured fixer round (median 2 h 46 m) | 92 s |

**Countermeasure.** A `graders` arm in `tools/pr/ci_predict.py`, beside `agreement`, through the factored `ci_tree_run`. It runs, under the base's copy and on one CI tree per job, every run the `policy-docs`, `env-matrix` and `wave-script` jobs restore:

| grader (modes) | marker | reported on | key |
|---|---|---|---|
| `policy_lint.mjs` (default, `--hooks`) | `CORPUS` | `policy-docs`, `env-matrix` | its `.mjs` closure |
| `check-wave-script.mjs` | `WAVE CHECK` | `wave-script`, `env-matrix` | its `.mjs` closure |
| `field_coverage.mjs` | `FIELD COVERAGE` | `policy-docs` | its own file (a run takes about 110 s) |
| `rules_sync.mjs --check` | `RULES SYNC` | `policy-docs` | its `.mjs` closure |
| `fragments_sync.mjs` | `FRAGMENTS` | `policy-docs` | its `.mjs` closure |
| `codeowners_gap.py --check` | `CODEOWNERS` | `policy-docs` | its own file (Python) |
| `agreement.mjs --self-test` | `LANE SELF-TEST` | `wave-script` | its `.mjs` closure |

The population is not a list: `pinned_runs` reads it from governance.yml's run lines, and `grader_gaps` (in the self-test) refuses a restored run that no row, the `agreement` arm or a reasoned exemption (`policy_lint.mjs --report`, whose step ends `|| true`) covers, and a job whose head-copy program spawns a row's grader but is missing from that row's reds.

`prepr.sh` step 6d and `body_push.sh` both run the predictor, so this PR does not edit `prepr.sh`. The record's section 6 explains why the brief's `prepr.sh` step was drafted and then withdrawn: it would duplicate the tree build and leave the handoff gate blind.

Two smaller edits come with the arm:
- `agreement_py.restore_specs` now takes a job name. The default is unchanged.
- The `named-docs` refusal in `policy_lint.mjs` now points at `corpus_excluded.json`, not at the Set.

**Owner approval.** This PR touches no code-owned path. The record proposes, and does not make, one line for `gate-scoping.md` (record section 7). That line is policy and needs the owner's approval.

## Head note

Round 2. The round-1 review was `Fix review: blocked 718ed364dfac4d2d1193502058c4adcf01c386cf class-open`.

- **Class-open (the block).** The five runs it named (`rules_sync.mjs --check`, `fragments_sync.mjs`, `codeowners_gap.py --check`, `policy_lint.mjs --hooks`, `agreement.mjs --self-test`) are now rows or modes. The population is derived from the pinned jobs (`pinned_runs`) and closed by a self-test (`grader_gaps`). The derivation found one more seam the review did not list: `env-matrix`'s head-copy `policy_lint_envmatrix.mjs` spawns `check-wave-script.mjs` too, so WAVE CHECK now reports `env-matrix`. Record section 4 measures the five runs: zero round-10 instances (the failed step of each of the 40 red pinned jobs, read from the jobs API, is never one of them). They are built anyway, at about 1.5 s per run, because the class is the restored runs.
- **M7 killed.** `"env-matrix"` dropped from CORPUS's reds now fails the self-test's `grader_gaps` row; so do the WAVE CHECK twin, the `--hooks` mode dropped and the RULES SYNC row dropped.
- **The rca-entry figure.** It is 125 at the base and 126 with this record (127 after `origin/main`'s R10-RCA-CLOSURE-ARGV merged in).
- **One CI tree per job.** Every keyed row of a job runs in one clone, so seven rows cost two clones, not seven.
- **Carried, not fixed:** the `review_packet.py` host-path false positive (see `## Forward-carry`).

## Head

`fc7f6b7af0f952a342cfb6a3aa6d32722aaeaa8a` is the head. It continues round 1's `744734457` with the round-2 commits and two merges of `origin/main` (`beb570c81`, then `b6f6ceca4`); the second needed a hand resolution in `tools/pr/ci_predict.py` (main's new `self-test-reads` arm beside `graders` in `ARMS`, and main's `seen` suffix kept in the green line) and in `dev/audit/config/bugclasses.json` (main's file, with this record's `_rca` entry and I3 `rca` id re-applied). The branch was cut from `origin/main` `eab04d0eb`.

## Mutation proof

**The arm, through `python3 -I tools/pr/ci_predict.py --self-test`,** each mutant run from a copy of `tools/pr/ci_predict.py` at round 2's code (`3849accd6`):

| mutant | what it changes | result | rows that went red |
|---|---|---|---|
| M1 | the `graders` entry dropped from `predict`'s arms | 1 failed | `an exclusion written into the head's policy_lint.mjs only is predicted red (#2916)` |
| M2 | `ci_tree_run`'s pathspec restore from the tip deleted | 3 failed | that row; `a grammar registered only in the head's copy is predicted red`; `a head copy of the lane that exits 1 is predicted green (null control: CI runs the base's)` |
| M3 | a refusing run no longer recorded | 1 failed | the #2916 row |

**The key and the population, in process (`grader_key_self_test`, which `--self-test` runs):**

| mutant | what it changes | result |
|---|---|---|
| M4 | FIELD COVERAGE keyed on its whole closure | 1 failed: `and not by policy_lint.mjs, which its closure holds` |
| M5 | `grader_hit`'s restore-pathspec filter dropped | 0 failed (equivalent: every closure `.mjs` is under `tools/policy/*.mjs`, which every pinned job restores; kept because it states the rule) |
| M7 | `"env-matrix"` dropped from CORPUS's reds (round 1's survivor) | 1 failed: `every run a pinned job restores is predicted, or exempt with a reason` names `policy_lint_envmatrix.mjs spawns policy_lint.mjs, but CORPUS does not report env-matrix` |
| M8 | CORPUS's `--hooks` mode dropped | 1 failed: the same row names `tools/policy/policy_lint.mjs --hooks is restored from the base and no arm runs it` |
| M9 | the RULES SYNC row dropped | 2 failed: `RULES SYNC is keyed by rules_sync.mjs …` and the gap row naming `rules_sync.mjs --check` |

## Null control

**Demonstrations** with `bash dev/audit/rca/prepr-head-graders/demo.sh <head> <base> <out> [comment]`:

| head | base | result | time |
|---|---|---|---|
| `f008c2b75` (#2916 pre-fix) | `eab04d0eb` | rc 1. Prints `PREDICT governance / policy-docs CORPUS REFUSED by the base's copy, over tools/policy/policy_lint.mjs: ERROR   [named-docs] tools/audit/seat/beatd_shims/git: …` and the same for `env-matrix`. Round 2: RULES SYNC, CORPUS `--hooks` and LANE SELF-TEST, keyed by the same file, run and pass | 44 s |
| `c991d64cd` (the repair) | `eab04d0eb` | rc 0, not keyed | — |
| `c991d64cd` plus a comment in `policy_lint.mjs`, so every keyed row runs | `eab04d0eb` | rc 0 | 41 s |
| #2737 (`deb7a4c1e^2` against `^1`; edited `policy_lint.mjs`, green on CI) | `deb7a4c1e^1` | rc 0 (round 1) | 47 s |
| #2207 `d176dd143` | `17f1c55fa` | rc 1, WAVE CHECK (round 1) | — |
| #2207's green head `98bd07a62` | `97750ec79` | rc 0 (round 1) | — |
| #2529 `e9d54acdf` | `9fdc5846a` | rc 1, FIELD COVERAGE `agreement_restore.py is unregistered` (round 1) | 107 s |
| #2636 `2aa2b5dbe` | `d6308d77c` | rc 1, FIELD COVERAGE BLIND; CORPUS stays green, as CI's did (round 1) | 134 s |

**Self-test at the head:** `ci_predict self-test: 0 failed` (51 ok rows, 420 s).

## Figures

- 543 round-10 first-parent merges since 2026-10-14 up to `beb570c81`; 70 of them, plus open #2910 and #2916, touch a restored path: `git log origin/main --first-parent --merges --since=2026-10-14 --oneline`, each diffed against the restore pathspecs.
- The base-copy and head-copy verdict of each candidate, on CI's tree: `bash dev/audit/rca/prepr-head-graders/attribute.sh <head> <PINNED> <job> <out>`, with each run's `PINNED` read from its job log (`check source restored from …`).
- The failed step of each of the 40 red pinned jobs (Lint the policy corpus 5, Refuse a governance check input field no check reads 2, Drive the wave script's branching 2, Refuse two readers of one concept that disagree 11, Require each declared environment shape to produce its declared outcome 8): `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>` over the 40 job ids.
- #2916's red at 17:10:29 after the 17:05:13 push (316 s); `policy-docs` 65 s and `env-matrix` 153 s of runner time: `gh api repos/tvofi/heatpump_optimizer/commits/e09b123f9653c446c4afac46bfbc4948d1460f0c/check-runs`.
- The six fixer rounds from red to the next green head (44 m, 50 m, 2 h 10 m, 3 h 23 m, 3 h 36 m, 10 h 28 m): each PR's commits with their `policy-docs` or `wave-script` check-run, `gh api repos/tvofi/heatpump_optimizer/pulls/<N>/commits`.
- Keys hit, of the 543 merges: CORPUS 16, WAVE CHECK 10, FIELD COVERAGE 7, RULES SYNC 16, FRAGMENTS 2, CODEOWNERS 1, LANE SELF-TEST 20, any row 30: `git diff --name-only <merge>^1...<merge>^2` over the same merges, against each row's key set.
- Runtimes alone: `rules_sync.mjs --check` 0.2 s, `fragments_sync.mjs` 1.7 s, `codeowners_gap.py --check` 6.5 s, `policy_lint.mjs --hooks` 6.2 s, `agreement.mjs --self-test` 1.4 s: each command once from this worktree.
- Nothing keyed: `--only graders` 1.22, 1.01 and 1.03 s, against `--only orphans` 0.41, 0.51 and 0.45 s, in a clone at `origin/main` with this predictor copied in: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --only graders`.
- Keyed, both trees: 41.07, 41.01 and 42.93 s on this branch: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --only graders`; 44 s and 41 s: the `seconds=` line of `demo.sh`.
- `fold_ledger: 0 violation(s)`, 125 rca entries at `eab04d0eb` and 126 with this record (127 here, with main's R10-RCA-CLOSURE-ARGV): `python3 -I tools/audit/fold_ledger.py check`.

## Red checks

none

## Forward-carry

- **`ref_privacy._leaks` matches the host's home as a bare substring.** The round-1 review found `review_packet.py render` refusing `host-path` on `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md:4`: under `HOME=/root` (a cloud seat) the string `/root` occurs inside `dev/governance/roles/root-cause.md`, so every diff citing that contract is refused there; the same line under a macOS seat's home returns `[]`. The fix is a path-segment boundary after the home. It is an instrument defect outside this record's class, in the file R10-RECORD-API-O1 owns. Lands in `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md` section 7. Carry: R10-RECORD-API-O1

## Friction

none
