R9-RO-11 (lane RO, roster group R9-RO-11, no tracking issue). This PR adds a pre-push CI predictor to `prepr.sh` and defers the local `--pin-killed` decision in `fixer.md` to `ci-autofix.md`. tvofi approved the fold on 2026-10-07 (items 1 and 3, with a small pre-study first).

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
| (a) a prepr predictor: static, from the three-dot diff | `mutation` on 11 of 11 red commits with a run in the replay; `closures` on 12 of 15 (the misses are 2 inherited main reds and 1 data-file read); the `entities.py` arm of `fast` on 2 of 2 | about 3 s per run, with no test, recording or mutant |
| (b) a handoff gate that waits for the CI autofix chain | 0: none of the 20 autofix runs pushed a repair | a full CI round per head, then a red the fixer must still repair |
| (c) prepr step 6b's local closure recording, which already exists | `closures` UNDER-SCOPED only, and only for scripts this machine records | the scoped scripts' whole run time; closure recordings are on the owner's heavy-scripts list (2026-10-07), so seats skip it |
| (d) repair the autofix chain: the mutation drive's budget overrun, and the classifier statuses | potentially both classes, after the push | a separate change to `tests.yml` and `mutation_table.py`; it does not stop a red reaching the reviewer's head |

**Choice: (a).** It is the cheapest option, and it is the only one that catches most of these reds before the handoff. (b) catches nothing on this round's evidence. (d) is worth doing, but it lands after the push, not before. It is named under Forward-carry and not built here.

## The change

- **`tools/pr/ci_predict.py`** reads the merge base three-dot. It uses CI's own functions and the committed table, and runs nothing heavy. It has five arms:
  - **UNCLASSIFIED**: a changed file in `closure.orphan_files()`, which is what `entities.py` refuses.
  - **NO RECORDING**: a selectable script that no `rec` line of `tests/derive_closures.sh` records.
  - **UNDER-SCOPED / INERT READS (import)**: a top-level import edge that the diff adds. The edge must start from a file that some closure executes (the closure lists every top-level import that file had at the base), and its target must be missing from that closure. The arm follows the target's own top-level imports. It skips `tests/hastub/` and collapses its output to one line per target.
  - **INERT READS (glob)**: a new INERT file beside three or more same-suffix files that a script's `inert_reads` lists.
  - **ADDED UNPINNED**: `mutation_table`'s `inventory`, `unpinned_sites`, `base_unpinned_sites` and `added_unpinned`. These are the same calls the `mutation` job refuses on, made before any baseline runs.
- **`prepr.sh` step 6d** runs the predictor. It prints the PREDICT lines and refuses on any prediction. The self-test drives it on a throwaway clone.
- **`fixer.md` step 2** no longer says "no local `--pin-killed`", which contradicted `ci-autofix.md`'s "When `mutation-autofix` goes red, run `--pin-killed` yourself". It now says that when `--pin-killed` runs is `ci-autofix.md`'s, and that step 6d names the unpinned sites first. The cut is token-neutral against the `fixer.md` cap.
- **`tools/audit/seat/ci_predict_replay.sh`** is the replay instrument behind the tables above.

**Not seen, by design.** A data file a script opens by name (#1987's `services.yaml`), a read through a dynamic path, an import inside a function, and a red main already carries. Each was traded for the null control below.

## Head

`74944e8a811c9f65be162a6ccc246b510091741b` (merge base `e7479ad19f96`, origin/main at 2026-10-07).

## Mutation proof

Each mutant replaced one `preds += <arm>(...)` call in `ci_predict.py` with `[]` in a scratch worktree at the head, then ran `bash tools/pr/prepr.sh --self-test`. The driver is a scratch loop over the five arms.

| mutant | self-test red |
|---|---|
| `orphans` off | "6d predicts entities' refusal of a new file in no closure and not on INERT" |
| `no_recording` off | "6d predicts NO RECORDING for a selectable script no derive lane records" |
| `under_scoped` off | "6d predicts UNDER-SCOPED for a new import from a file a closure lists" |
| `inert_siblings` off | "6d predicts INERT READS for a new harness beside the ones a glob-reading script lists" |
| `unpinned` off | "6d predicts ADDED UNPINNED for a guard the diff adds with no pin", and "and the step refuses on a prediction" |

## Null control

- **Self-test null arms.** A comment in `tests/wood_advisor.py` is quiet, at rc=0. A function-level import of a new module predicts no UNDER-SCOPED.
- **This head.** `python3 tools/pr/ci_predict.py` prints `CI PREDICT: none of closures' or mutation's static reds against e7479ad19f96`.
- **Replay, mutation.** All 18 commits where CI's `mutation` concluded success are quiet on the mutation arm.
- **Replay, closures.** Of the 13 commits where CI's `closures` concluded success, 12 are quiet. The exception is #2026 `e6e9b775`, which flags `boost_replay_fork_parity.py` and `ci_script_seconds.py`. CI's `closures` measured those same two files red as INERT READS one commit earlier, at `dca94a64`. The fixer cleared them by `baa6c237`, and the predictor is quiet there.
- **Two false alarms removed during development.** The first cut flagged them, and the replay found them:
  - a stub module that a text-reading script (`structure.py`) lists without executing;
  - an import inside a function that `guard_pins.py` never calls (#1987 `quiet_windows` to `silent_mode`, where `closures` stayed green).

  Each is now excluded, and each has a self-test null arm or a rule.

## Figures

- The red census: a scratch loop over `gh api repos/tvofi/heatpump_optimizer/pulls/<N>/commits` and `.../commits/<sha>/check-runs`. It covered 146 commits with 0 API failures, and the per-check counts are the table above. Job logs came from `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`; there were 82 logs, with 0 failures.
- `tools/audit/seat/ci_predict_replay.sh <scratch> 2007 2010 2014 2024 2025 1987 2026 2027` printed one row per commit carrying a `closures` or `mutation` run, and `replay failures (API or worktree): 0`. Predicted against CI:
  - `mutation`: 11 of 11 red commits predicted, and 0 of 18 green commits predicted.
  - `closures`: 12 of 15 red commits predicted, and 1 of 13 green commits predicted (`e6e9b775`, above).

  The counting rule is one row per replayed commit, keyed on its CI conclusion (`success` or `failure`; cancelled, skipped and pending rows are excluded) and on whether its PREDICT count for that job is above zero.

  The predicted `mutation` counts match CI's "added by this diff" count exactly where both measure the same base: #2007 `26002ff5` is 17 against 17, and #2025 `a390f589` is 55 against 55. They differ by up to 5 where CI's merge ref compares against a newer main tip than the commit's own fork point: #2010 `ace05371` is 42 against 47.
- The #2025 `a390f589` UNDER-SCOPED targets and script counts are `entry_config.py` 21, `inputs.py` 5 and `freq_control.py` 5. These equal the per-file script counts in CI's `closures` log at that commit.
- `python3 tools/pr/ci_predict.py` took about 3 s wall at this head (`time`), and the mutation ratchet arm alone was 6.4 s at c327da7f under load.
- `bash tools/pr/prepr.sh --self-test` prints `201 passed, 0 failed`.
- `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s) across 40 policy file(s)`. `node tools/policy/policy_lint.mjs --budgets` shows `fixer.md` at 4865 of its 4866 tokens.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run`. All three new or edited code files are INERT under `tools/`.

## Red checks

none at the time of writing. No CI has run at this head yet, so CI's check runs at the head are the record.

## Forward-carry

There is no later stage of this group. One finding is for the orchestrator to place: `mutation-autofix` repaired none of this round's 10 runs. Eight were `skip-no-measurement`, because every site was `NOT RUN ... would have overrun --budget-minutes` after a 345 s `env_drift.py` baseline. `closures-autofix` repaired none of its 10 runs either. Option (d) above is the fix. I did not file it, per CLAUDE.md's fix-verify-file order. It belongs to whichever group owns `tests.yml`'s autofix jobs.

## Friction

- `fixer.md: contradiction: step 2 said "no local --pin-killed" while ci-autofix.md says "When mutation-autofix goes red, run --pin-killed yourself"; resolved here by deferring to ci-autofix.md`

## Approval

This PR edits the policy file `dev/governance/roles/fixer.md` (step 2). It needs tvofi's approving review at the head before merging. `tools/pr/prepr.sh`, `tools/pr/ci_predict.py` and `tools/audit/seat/ci_predict_replay.sh` are instruments.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
