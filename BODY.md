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
| standing cost per predictor run (round 3's key) | about 16.3 s |
| standing cost per PR (about 3 runs) | about 49 s |
| expected defect cost per PR, CI floor only | 2.9 s |
| expected defect cost per PR, with the measured fixer round (median 2 h 46 m) | 92 s |

**Countermeasure.** A `graders` arm in `tools/pr/ci_predict.py`, beside `agreement`, through the factored `ci_tree_run`. It runs, under the base's copy and on one CI tree per job, every run the `policy-docs`, `env-matrix` and `wave-script` jobs restore:

| grader (modes) | marker | reported on | key |
|---|---|---|---|
| `policy_lint.mjs` (default, `--hooks`) | `CORPUS` | `policy-docs`, `env-matrix` | its `mjs_closure` |
| `check-wave-script.mjs` | `WAVE CHECK` | `wave-script`, `env-matrix` | its `mjs_closure` |
| `field_coverage.mjs` | `FIELD COVERAGE` | `policy-docs` | its `mjs_closure` without static imports (a run takes about 110 s) |
| `rules_sync.mjs --check` | `RULES SYNC` | `policy-docs` | its `mjs_closure` |
| `fragments_sync.mjs` | `FRAGMENTS` | `policy-docs` | its `mjs_closure` |
| `codeowners_gap.py --check` | `CODEOWNERS` | `policy-docs` | its `mjs_closure` without static imports (Python) |
| `agreement.mjs --self-test` | `LANE SELF-TEST` | `wave-script` | its `mjs_closure` |

`mjs_closure` is what a grader loads, transitively: `.mjs` static imports (where the row follows them), `load`/`at` literals, every file a source names to spawn, import at run time or read (`named_loads`), and a Python file's tracked imports.

The population is not a list: `pinned_runs` reads it from governance.yml's run lines, and `grader_gaps` (in the self-test) refuses a restored run that no row, the `agreement` arm or a reasoned exemption (`policy_lint.mjs --report`, whose step ends `|| true`) covers, a job whose head-copy program spawns a row's grader but is missing from that row's reds, and a restored file a row's grader names that is outside the row's key and on no reasoned `GRADER_NAMED_EXEMPT` site.

`prepr.sh` step 6d and `body_push.sh` both run the predictor, so this PR does not edit `prepr.sh`. The record's section 6 explains why the brief's `prepr.sh` step was drafted and then withdrawn: it would duplicate the tree build and leave the handoff gate blind.

Two smaller edits come with the arm:
- `agreement_py.restore_specs` now takes a job name. The default is unchanged.
- The `named-docs` refusal in `policy_lint.mjs` now points at `corpus_excluded.json`, not at the Set.

**Owner approval.** This PR touches no code-owned path. The record proposes, and does not make, one line for `gate-scoping.md` (record section 7). That line is policy and needs the owner's approval.

## Head note

Round 3. The round-2 review was `Fix review: blocked 38422dd1525cbf2cf7ace3e6e04213ea04b0f4ff class-open: tools/policy/budget_raise_gate.py, a restored program the CORPUS run spawns, outside the graders key`.

- **Class-open (the block).** The class is every restored file a row's grader loads, not the plant's instance. The rule that enumerates it is `named_loads` (`tools/pr/ci_predict.py`): each quoted `.mjs`, `.py` or `.sh` path and each `path.join` of literals in a source the row's key holds, resolved beside the source, from the root, or through layout's move map. `mjs_closure` now follows it and a Python file's tracked imports; `grader_gaps` enumerates it over every row and refuses a named restored file outside the key, or an exempt site no source still holds. Run with the named arm removed, the rule returns 42 sites naming 10 files; every one is now keyed, and two sites are exempt with their reasons (record section 6, "Round 3"). It found seams the review did not name: `check-wave-script.mjs` imports `policy_lint.mjs` at run time and reads `prepare_baseline.sh`; `field_coverage.mjs` runs `policy_lint.mjs --hooks`, `codeowners_gap.py` and `budget_raise_gate.py`; `agreement.mjs` imports `tests/throwaway_git.py`; `budget_raise_gate.py` imports `tests/layout.py`.
- **The review's plant** is predicted red at this head (rc 1, `CORPUS REFUSED by the base's copy, over tools/policy/budget_raise_gate.py: FIXTURE VACUOUS …` on `policy-docs` and `env-matrix`) and green at `38422dd15` (rc 0): `## Null control`.
- **The key widened, and its cost was re-taken.** Any row keyed: 40 of 539 merges (28 by round 2's key, counted by the same rule). FIELD COVERAGE, now keyed by `policy_lint.mjs`, is the cost: about 16.3 s per predictor run, 49 s per PR, under the 92 s expected defect cost. Record section 5.
- **Disclosed self-correction.** At `c8eb2dc51`, `named_loads` split a `path.join`'s literals with the regex `'([^']*)'`, which `tests/features.py` also uses; the agreement lane read the two as unregistered readers of one grammar, and `--self-test` failed 6 rows under the head's copy of the lane. `282496dce` splits on commas instead: the lane prints `RESULT divergent=0 unregistered=0 dead=0 refused=0`, and the self-test `0 failed`. Nothing was pushed in between.
- **The `ref_privacy` carry, confirmed.** R10-RECORD-API-O1's roster `brief` and `carry` hold the home-substring defect, on this tree and on `origin/main` (`9573269b1`, from #2852's fix review): `## Forward-carry`.

## Head

`46686b67727e2e1db00c689ab15e8a9ab8e5a77d` is the head. It is round 2's `38422dd15` with five commits on top: `c8eb2dc51` (the named-loads key, its enumeration and the self-test rows), `7d3b78914` (record sections 5, 6 and 7), `282496dce` (a `path.join`'s literals split without a regex) `0ca059dee` (the plant and cost re-taken at `282496dce`) and `46686b677` (two older record lines name the root-cause contract instead of its path; see `## Forward-carry`). No merge: `git merge-tree --write-tree origin/main HEAD` against `origin/main` `6493ea362` (2026-10-28T23:51Z) reports no conflict. The branch was cut from `origin/main` `eab04d0eb`.

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

**Round 3, in process at `282496dce`:** `mjs_closure`'s `named` forced off (the fix's arm deleted), through `grader_key_self_test`:

| mutant | result | rows that went red |
|---|---|---|
| M10 | 4 failed (15 ok unmutated) | `and by budget_raise_gate.py, a program it spawns (review round 2's plant)`; `and by tests/layout.py, which that program imports`; `WAVE CHECK is keyed by check-wave-script.mjs, and by policy_lint.mjs, which it imports at run time`; `every run a pinned job restores is predicted, or exempt …` (it lists the 42 sites) |

M4's row is now `and not by render_md.mjs, which only policy_lint.mjs's static imports reach`; FIELD COVERAGE is keyed by `policy_lint.mjs` by design (it runs it with `--hooks`).

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

**The review's plant** (`evidence/plant.diff` at `origin/review/2925`, committed on the head), `python3 -I tools/pr/ci_predict.py --base <head> --only graders`:

| predictor at | result | time |
|---|---|---|
| `38422dd15` (round 2) | rc 0: `budget_raise_gate.py` keys nothing | 0 s |
| `282496dce` (round 3) | rc 1: `PREDICT governance / policy-docs CORPUS REFUSED by the base's copy, over tools/policy/budget_raise_gate.py: FIXTURE VACUOUS: the raise-justification arm on prepr/raise/good.md drew 1 error(s)`, and the same on `env-matrix` | 292 s |

**Self-test at the head:** `ci_predict self-test: 0 failed` (55 ok rows, 1045 s, at `282496dce`; round 2: 51 rows, 420 s).

## Figures

- 543 round-10 first-parent merges since 2026-10-14 up to `beb570c81`; 70 of them, plus open #2910 and #2916, touch a restored path: `git log origin/main --first-parent --merges --since=2026-10-14 --oneline`, each diffed against the restore pathspecs.
- The base-copy and head-copy verdict of each candidate, on CI's tree: `bash dev/audit/rca/prepr-head-graders/attribute.sh <head> <PINNED> <job> <out>`, with each run's `PINNED` read from its job log (`check source restored from …`).
- The failed step of each of the 40 red pinned jobs (Lint the policy corpus 5, Refuse a governance check input field no check reads 2, Drive the wave script's branching 2, Refuse two readers of one concept that disagree 11, Require each declared environment shape to produce its declared outcome 8): `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>` over the 40 job ids.
- #2916's red at 17:10:29 after the 17:05:13 push (316 s); `policy-docs` 65 s and `env-matrix` 153 s of runner time: `gh api repos/tvofi/heatpump_optimizer/commits/e09b123f9653c446c4afac46bfbc4948d1460f0c/check-runs`.
- The six fixer rounds from red to the next green head (44 m, 50 m, 2 h 10 m, 3 h 23 m, 3 h 36 m, 10 h 28 m): each PR's commits with their `policy-docs` or `wave-script` check-run, `gh api repos/tvofi/heatpump_optimizer/pulls/<N>/commits`.
- Keys hit, of the 543 merges (round 2): CORPUS 16, WAVE CHECK 10, FIELD COVERAGE 7, RULES SYNC 16, FRAGMENTS 2, CODEOWNERS 1, LANE SELF-TEST 20, any row 30: `git diff --name-only <merge>^1...<merge>^2` over the same merges, against each row's key set.
- Keys hit, round 3, of 539 merges by `git rev-list --first-parent --merges --since=2026-10-14 beb570c81`: round-2 key / round-3 key: CORPUS 15/21, WAVE CHECK 9/32, FIELD COVERAGE 7/27, RULES SYNC 15/21, FRAGMENTS 2/4, CODEOWNERS 1/7, LANE SELF-TEST 19/28, any row 28/40: `python3 -I dev/audit/rca/prepr-head-graders/keycount.py beb570c81 2026-10-14`. The round-2 key's file counts (5, 2, 1, 6, 2, 1, 7) match round 2's table, the null control for the counter.
- The named-loads seams: 42 sites naming 10 files, each keyed at the head: `grader_gaps(root, text, agreement_py, key=lambda e, w: mjs_closure(root, e, imports=w, named=False))`; at the head with the default key, `grader_gaps` returns `[]`.
- Nothing keyed, round 3: `--only graders` 0.88, 0.87 and 0.85 s against `--only orphans` 0.16, 0.17 and 0.20 s: `python3 -I tools/pr/ci_predict.py --base HEAD --only <arm>` at `c8eb2dc51` (the third commit changes only how a `path.join`'s literals are split).
- Keyed, round 3: 292 s for the plant (both trees, five rows run): `python3 -I tools/pr/ci_predict.py --base <head> --only graders`.
- Runtimes alone: `rules_sync.mjs --check` 0.2 s, `fragments_sync.mjs` 1.7 s, `codeowners_gap.py --check` 6.5 s, `policy_lint.mjs --hooks` 6.2 s, `agreement.mjs --self-test` 1.4 s: each command once from this worktree.
- Nothing keyed: `--only graders` 1.22, 1.01 and 1.03 s, against `--only orphans` 0.41, 0.51 and 0.45 s, in a clone at `origin/main` with this predictor copied in: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --only graders`.
- Keyed, both trees: 41.07, 41.01 and 42.93 s on this branch: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --only graders`; 44 s and 41 s: the `seconds=` line of `demo.sh`.
- `fold_ledger: 0 violation(s)`, 125 rca entries at `eab04d0eb` and 126 with this record (127 here, with main's R10-RCA-CLOSURE-ARGV): `python3 -I tools/audit/fold_ledger.py check`.

## Red checks

none

## Forward-carry

- **`ref_privacy._leaks` matches the host's home as a bare substring.** The round-1 review found `review_packet.py render` refusing `host-path` on `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md:4`: under `HOME=/root` (a cloud seat) the string `/root` occurs inside `dev/governance/roles/root-cause.md`, so every diff citing that contract is refused there; the same line under a macOS seat's home returns `[]`. The fix is a path-segment boundary after the home. It is an instrument defect outside this record's class, in the file R10-RECORD-API-O1 owns. It is already in that stage's brief: R10-RECORD-API-O1's `brief` and `carry` in `dev/programme/rosters/wave-r10-groups.json`, appended by `9573269b1` from #2852's fix review. Read back on this tree and on `origin/main`: `jq '.. | objects | select(.group? == "R10-RECORD-API-O1") | to_entries[] | select(.value|tostring|contains("no path-segment boundary")) | .key'` prints `carry` and `brief`. Record section 7 cites it. This seat met it too: `prepr.sh`'s `ref privacy` step refused record lines 4 and 473 from rounds 1 and 2 (`27ec34825`, `fc7f6b7af`) under a root home, so `46686b677` takes the tool's own remedy, naming the contract instead of its path; `python3 -I tools/audit/seat/ref_privacy.py --check` then prints `0 refused`. Carry: R10-RECORD-API-O1

## Friction

none
