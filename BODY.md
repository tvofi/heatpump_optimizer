R9-RO-11 (lane RO, roster group R9-RO-11, no tracking issue). This PR adds a pre-push CI predictor to `prepr.sh` and defers the local `--pin-killed` decision in `fixer.md` to `ci-autofix.md`. tvofi approved the fold on 2026-10-07 (items 1 and 3, with a small pre-study first).

Round 2 answers the round-1 block at `2d12904f`, with the orchestrator's decisions under the owner's mandate:
- NO RECORDING is now scoped to the diff, so a red main already carries no longer refuses a branch.
- Unpinned mutation sites now warn and do not refuse. The body owes each site a line under `## Unpinned sites`.
- The docstring now says which arms reuse CI's functions and which are the predictor's own model.
- The closures green count is re-derived below.

## Pre-study

**Method.** I pulled every check run at every commit of the eight round-9 fix pull requests (#2007, #2010, #2014, #2024, #2025, #1987, #2026, #2027): 146 commits, 0 API failures. For each red that was not a state check, I read the job log through the API. The predictor was then replayed over every commit that carried a `closures` or `mutation` run, using `tools/audit/seat/ci_predict_replay.sh`, which landed in this PR.

**Reds by check and whether a cheap static check predicts them.** Each count is the number of distinct commits with that check red.

| check | red commits | cause, read from the log | static, seconds? |
|---|---|---|---|
| `delivery-status`, `nightly-status` | 31 each | state checks (row not yet written; main's nightly) | no: not a property of the head |
| `closures` | 15 | UNDER-SCOPED from a new module (#2024 `flow_meter.py`, #2025 `entry_config.py`) or a new top-level import of an existing module (#2025 `inputs.py`, `freq_control.py`; #1987 `quiet_windows.py`); NO RECORDING for a new test script in no derive lane (#1987 `debug_collect.py`, 3 commits); INERT READS from a new harness beside the ones `harness_headers.py` reads by glob (#2010, #2026); INERT READS of `eg_b7_seam_hubs.py`, which main had moved (4 commits, inherited); UNDER-SCOPED on `services.yaml` read as data (#1987, 1 commit) | yes, except the inherited and data-file reads |
| `pr-contract` | 14 | the body | already `prepr.sh` step 7 |
| `mutation` | 10 | `MUTATION TABLE REFUSED -- ... N of them added by this diff` | yes: the ratchet is source-only |
| `mutation-autofix` | 10 | 8 `skip-no-measurement` (the drive's sites are `NOT RUN ... would have overrun --budget-minutes`), 2 `skip-measure-failed` | n/a: this is the repair job |
| `closures-autofix` | 10 | 4 `skip-manual-repair-owed`, 6 `skip-failed-recording` | n/a: this is the repair job |
| `typing` | 6 | mypy errors grew | partly: `typing_ruler.py` with pinned mypy, an existing local check |
| `fast (3.14)` | 6 | `entities.py` refused an unclassified file (#2024, 2 commits), plus `stress.py`, `env_drift.py`, `harness_headers.py` and `manual_plan.py` reds | the `entities.py` arm only |
| `env-matrix` | 5 | `policy_lint` path (inherited from main's move) | no: main's |
| `budget-raise-gate` | 2 | an owner-gated raise (#2024) | no: an owner gate, by design |
| `mutation-nightly` | 2 | baseline red | no: heavy |
| `Analyze (python)` | 1 | CodeQL | no |

**Options compared.**

| option | catches, of the reds this round | cost |
|---|---|---|
| (a) a prepr predictor: static, from the three-dot diff | `mutation` sites listed on 11 of 11 red commits with a run in the replay; `closures` on 12 of 15 (the misses are 2 inherited main reds and 1 data-file read); the `entities.py` arm of `fast` on 2 of 2 | about 3 s per run, with no test, recording or mutant |
| (b) a handoff gate that waits for the CI autofix chain | 0: none of the 20 autofix runs pushed a repair | a full CI round per head, then a red the fixer must still repair |
| (c) prepr step 6b's local closure recording, which already exists | `closures` UNDER-SCOPED only, and only for scripts this machine records | the scoped scripts' whole run time; closure recordings are on the owner's heavy-scripts list (2026-10-07), so seats skip it |
| (d) repair the autofix chain: the mutation drive's budget overrun, and the classifier statuses | potentially both classes, after the push | a separate change to `tests.yml` and `mutation_table.py`; it does not stop a red reaching the reviewer's head |

**Choice: (a).** It is the cheapest option, and it is the only one that catches most of these reds before the handoff. (b) catches nothing on this round's evidence. (d) is worth doing, but it lands after the push, not before. It is named under Forward-carry and not built here. Of (a)'s arms, the closures and `fast` predictions refuse. The mutation sites warn, because `ci-autofix.md` has `mutation-autofix` pin them after the push; step 7d asks the body for each site's disposition instead.

## The change

- **`tools/pr/ci_predict.py`** reads the merge base three-dot, and every arm is scoped to the files the diff adds or changes. Three arms call CI's own functions:
  - **UNCLASSIFIED** calls `closure.orphan_files()`, which is what `entities.py` refuses.
  - The INERT test inside both closure arms calls `closure.is_inert`.
  - **ADDED UNPINNED** calls `mutation_table`'s `inventory`, `unpinned_sites`, `base_unpinned_sites`, `added_unpinned` and `diff_sides`. These are the calls the `mutation` job refuses on, made before any baseline runs.

  Two arms are the predictor's own model, because CI learns their answer by running:
  - **UNDER-SCOPED / INERT READS (import)** resolves imports statically, where CI records them at run time. It takes a top-level import edge the diff adds, starting from a file some closure executes (the closure lists every top-level import that file had at the base), whose target that closure omits. It follows the target's own top-level imports, skips `tests/hastub/`, and prints one line per target. Its INERT READS sibling (glob) flags a new INERT file beside three or more same-suffix files a script's `inert_reads` lists.
  - **NO RECORDING** reads the `rec tests/...` lines of `tests/derive_closures.sh`, where CI sees which recordings exist. It covers only scripts the diff adds or changes, or every script when the diff edits the lane file.

  The predictor omits CI's count-only ratchet refusal and its ledger form refusals. That under-predicts, which is safe for a predictor.
- **`prepr.sh` step 6d** runs the predictor. It refuses on a predicted `closures` or `fast` red. Unpinned sites are a WARN, never a refusal, because `ci-autofix.md` has `mutation-autofix` pin them after the push. The step writes the site keys to a file.
- **`prepr.sh` step 7d** refuses a body only when that file is non-empty and the body's `## Unpinned sites` section is missing or omits a listed `file:line KIND` key. The self-test drives both steps on a throwaway clone.
- **`fixer.md` step 2** no longer says "no local `--pin-killed`", which contradicted `ci-autofix.md`'s "When `mutation-autofix` goes red, run `--pin-killed` yourself". It now says that when `--pin-killed` runs is `ci-autofix.md`'s, that step 6d lists the unpinned sites the diff adds, and that `## Unpinned sites` gives each one its disposition: pinned by `mutation-autofix`, a value check, or a written triage. This replaces the old line about survivors and stays within the `fixer.md` cap.
- **`tools/audit/seat/ci_predict_replay.sh`** is the replay instrument behind the tables above.

**Not seen, by design.** A data file a script opens by name (#1987's `services.yaml`), a read through a dynamic path, an import inside a function, and a red main already carries. Each was traded for the null control below.

## Head

`38c79586131cac118daa85081e205cc402ff34df` (merge base `8d7903e69cfe`, origin/main at 2026-10-07). It merges origin/main, #1987 included, into round 2's commits `d5978b2b` and `8fa3f5f0`.

## Mutation proof

Each mutant was applied in a scratch worktree at round 2's code, then `bash tools/pr/prepr.sh --self-test` was run and the mutant restored. The driver is a scratch loop over eight sed replacements. Each mutant's run was sequential and alone.

| mutant | self-test red |
|---|---|
| `orphans` arm off | "6d predicts entities' refusal of a new file in no closure and not on INERT" |
| `no_recording` arm off | "6d predicts NO RECORDING for a selectable script no derive lane records" |
| `under_scoped` arm off | "6d predicts UNDER-SCOPED for a new import from a file a closure lists" |
| `inert_siblings` arm off | "6d predicts INERT READS for a new harness beside the ones a glob-reading script lists" |
| `unpinned` arm off | "6d predicts ADDED UNPINNED ...", "6d writes the three planted site keys for step 7d", and 4 of the 7d arms (6 red) |
| NO RECORDING unscoped (`if s not in recorded]`) | "6d charges no branch with an unrecorded script main already carries (null control)", and "and so the unrelated branch passes 6d" |
| mutation sets the rc again (`1 if out else 0`) | "and an unpinned site warns, never refuses: mutation-autofix may pin it after the push" |
| 7d reads the whole body (`sec=$(cat "$1")`) | "7d reads the keys under ## Unpinned sites only, not anywhere in the body" |

## Null control

- **Self-test null arms.**
  - A comment in `tests/wood_advisor.py` is quiet, at rc=0.
  - A function-level import of a new module predicts no UNDER-SCOPED.
  - The reviewer's plant passes. "Main" adds `tests/zz_main_unrecorded_check.py`, unrecorded, and a branch from it only comments `tests/wood_advisor.py`. That branch gets no NO RECORDING line and rc=0.
  - 7d passes a section that names every listed site.
  - 7d owes nothing when the diff adds no site.
- **This head.** `python3 tools/pr/ci_predict.py` prints `CI PREDICT: no closures or fast red predicted against 8d7903e69cfe`. This diff adds no production site, so 7d owes no `## Unpinned sites`.
- **Replay, mutation.** All 20 commits where CI's `mutation` concluded success list no site.
- **Replay, closures.** Of the 16 commits where CI's `closures` concluded success, 15 are quiet. The exception is #2026 `e6e9b775`, which flags `boost_replay_fork_parity.py` and `ci_script_seconds.py`. CI's `closures` measured those same two files red as INERT READS one commit earlier, at `dca94a64`. The fixer cleared them by `baa6c237`, and the predictor is quiet there.
- **The green count, re-derived.** Round 1 said 13 green commits. The reviewer's replay found 15. This round's finds 16, under the same rule. The difference is not in the predictor; it is which `closures` runs had concluded when each replay read the API:
  - Round 1's 13 left out #2025 `0dfb63a8` and #2026 `d279db99`. Their runs were still in flight then, and the reviewer read both as success.
  - The reviewer's 15 left out #1987 `1e91aa59`, which was pending then and is success now.

  Every one of those three is quiet.
- **Two false alarms removed in round 1,** both found by the replay:
  - a stub module that a text-reading script lists without executing;
  - a function-level import that `guard_pins.py` never calls.

## Figures

- The red census: a scratch loop over `gh api repos/tvofi/heatpump_optimizer/pulls/<N>/commits` and `.../commits/<sha>/check-runs`. It covered 146 commits with 0 API failures, and the per-check counts are the table above. Job logs came from `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`; there were 82 logs, with 0 failures.
- `tools/audit/seat/ci_predict_replay.sh <scratch> 2007 2010 2014 2024 2025 1987 2026 2027` was run at this round's code. It printed one row per commit carrying a `closures` or `mutation` run, and `replay failures (API or worktree): 0`. Predicted against CI:
  - `mutation`: sites were listed on 11 of 11 red commits and on 0 of 20 green commits.
  - `closures`: 12 of 15 red commits were predicted, and 1 of 16 green commits (`e6e9b775`, above).

  The counting rule is one row per replayed commit, keyed on its CI conclusion (`success` or `failure`; cancelled, skipped and pending rows are excluded) and on whether its PREDICT count for that job is above zero. #1987 merged during this round, so the replay now compares a merged pull request with its merge commit's first parent; the fork point with the tip is the head itself. Its rows match the reviewer's round-1 rows.

  The `mutation` counts match CI's "added by this diff" count where both measure the same base: #2007 `26002ff5` is 17 against 17, and #2025 `a390f589` is 55 against 55. They differ by up to 5 where CI's merge ref compares against a newer main tip: #2010 `ace05371` is 42 against 47.
- The #2025 `a390f589` UNDER-SCOPED targets and script counts are `entry_config.py` 21, `inputs.py` 5 and `freq_control.py` 5. These equal the per-file script counts in CI's `closures` log at that commit.
- `python3 tools/pr/ci_predict.py` took 3.8 s wall at this head (`time`).
- `bash tools/pr/prepr.sh --self-test` prints `210 passed, 0 failed`.
- `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s) across 40 policy file(s)`. `node tools/policy/policy_lint.mjs --budgets` shows `fixer.md` at 4865 of its 4866 tokens.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run`. Every new or edited code file is INERT under `tools/`.

## Red checks

- delivery-status: a state check, red on main's unread rows. The orchestrator writes this PR's row.
- nightly-status: inherited from main. This branch changes no nightly script or input.
- budget-raise-gate: cancelled at round 1's head `2d12904f`, not failed. This diff raises no budget; the cancelled run needs a rerun.
- Nothing else was red at `2d12904f`, and no CI has run at this head yet. CI's check runs at the head are the record.

## Forward-carry

There is no later stage of this group. The orchestrator is proposing a separate roster group for the broken autofix chain. The finding, kept here for that group:
- `mutation-autofix` repaired none of this round's 10 runs. Eight were `skip-no-measurement`, because every site was `NOT RUN ... would have overrun --budget-minutes` after a 345 s `env_drift.py` baseline; two were `skip-measure-failed`.
- `closures-autofix` repaired none of its 10 runs: 4 were `skip-manual-repair-owed` and 6 were `skip-failed-recording`.

Option (d) above is that group's fix. It is why 6d's mutation arm warns and asks the body for a disposition instead of waiting on a bot commit.

## Friction

- `fixer.md: contradiction: step 2 said "no local --pin-killed" while ci-autofix.md says "When mutation-autofix goes red, run --pin-killed yourself"; resolved here by deferring to ci-autofix.md`

## Approval

This PR edits the policy file `dev/governance/roles/fixer.md` (step 2). It needs tvofi's approving review at the head before merging. `tools/pr/prepr.sh`, `tools/pr/ci_predict.py` and `tools/audit/seat/ci_predict_replay.sh` are instruments.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
