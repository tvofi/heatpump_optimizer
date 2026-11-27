#3885 L7 (design `design.md` on `design/r11-ci-3885-queue` at 43ff5ae6c1464d640acbce4ee03ab7cd23579c26, approved at adbd80a4): the two remaining whole-run re-run POSTs re-ran every job that had already succeeded. `merge_train.py` K15 (b) stale re-run (`Train.unstale`) and `cancel_superseded.py` `priority_step` now POST `.../rerun-failed-jobs`, which re-runs failed and cancelled jobs, and fall back to `.../rerun` only when GitHub refuses that (a run with no failed or cancelled job; a run cancelled before any job was created). Without the fallback a refusal would have left the stale check-run unconcluded (a merge stop) or dropped a held run unrun after `HELD_MAX_AGE_S`: the design names neither case, so the fallback keeps both paths' outcome where the design's replacement alone would change it. Leaves #3885 open.

L2 at this base (fd93aa3e9b), against the design's L2 section: `tools/ci/sweep.py` `fresh` leaves a STALE-PIN red undispatched when `code_red` names a code unit (or a `tests / fast` shard, #3902) that concluded `failure` at the head (`sweep_selftest.py` rows `stale pin, #3885: a code unit red at the head is no stale verdict ...` and `stale pin, #3902: a red fast shard ...`). Of the design's example narrowings, a code-unit job still running at the head, or one cancelled there, still takes the one dispatch: `code_red` skips jobs not `completed` and counts only `failure`. Whether those remaining dispatches are duplicates is what the `ci3885_light.py dup` arm measures, and this container cannot run it (it shells `gh api`; GitHub is reachable here only through the MCP tools), so L2 is not reported closed. Its destination is under `## Forward-carry`.

## Head

030d07524cdd33f317435059bc6cd2b1dbadbb0f on `origin/main` fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5 (2026-11-27T00:05Z).

## Mutation proof

Each production change reverted to its base text, the file's own self-test run (MUTANT_CMD per file below):
- `priority_step` back to `api([f"repos/{repo}/actions/runs/{rid}/rerun"], "POST")`: `cancel_superseded self-test: 88 checks, 2 failed` -- `FAIL priority: the cancel is recorded, then re-run once no priority run is queued`, `FAIL priority L7: a refused failed-only re-run falls back to the whole run, once`.
- `rerun_failed_first`'s fallback deleted: 1 failed -- `FAIL priority L7: a refused failed-only re-run falls back to the whole run, once`.
- `Train.unstale`'s POST back to `.../rerun`: `merge_train self-test: 841 checks, 3 failed` -- `FAIL K15 (b): a stale check-run at the head is re-run once, before the merge attempt, and logged with its run id`, `FAIL K15 (b) L7: the stale re-run is failed-only, never the whole run while GitHub accepts that`, `FAIL K15 (b) L7: a refused failed-only re-run falls back to the whole run, once, and merges (null: the accepted case above posts no whole-run re-run)`.
- `Train.unstale`'s fallback deleted: 1 failed -- the last of those three.

Diff mutants (`tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --max-mutants 40 --report-only`, PREPR_SKIP_CODE=1 so run by hand):
- MUTANT_CMD=`python3 tools/pr/cancel_superseded.py --self-test`, `--path tools/pr/cancel_superseded.py`: rc 0 (`--report-only`), every mutant of a production line killed; 3 SURVIVED, all in the file's own self-test: `SURVIVED tools/pr/cancel_superseded.py:938 CONST_SWAP  r3 = priority_step(pstub_refuse, repo=REPO, plan_=nop, held=held, allow_cancel=False,`, `SURVIVED tools/pr/cancel_superseded.py:927 STMT_DEL  pass`, `SURVIVED tools/pr/cancel_superseded.py:940 STMT_DEL  pass`.
- MUTANT_CMD=`python3 tools/audit/seat/merge_train.py --self-test`, `--path tools/audit/seat/merge_train.py`: rc 0 (`--report-only`), every mutant of a production line killed; 8 SURVIVED, all in the self-test: `SURVIVED tools/audit/seat/merge_train.py:5283 CONST_SWAP  return 2, "HTTP 403: This workflow run cannot be rerun"` and `STMT_DEL  pass` at 9254, 9261, 9269, 9285, 9303, 9307, 9310. An earlier run's `SURVIVED tools/audit/seat/merge_train.py:9255 CONST_SWAP  not any(c[-2].endswith("/rerun") for c in calls))` was killed by making that row compare the posted re-run list (030d07524c).

## Unpinned sites

Every survivor is a self-test line in the production file, none a production line:
- `cancel_superseded.py:927` and `:940`, `merge_train.py` 9254, 9261, 9269, 9285, 9303, 9307 and 9310: each is a `check(...)` statement deleted; deleting an assertion cannot fail the suite it belongs to. Disposition: equivalent by construction (a check's deletion is the reviewer's to read, not a mutant's).
- `cancel_superseded.py:938` `allow_cancel=True` -> `False`: `priority_step` reads `allow_cancel` only on a plan with a priority run queued, and this row's plan (`nop`) has none. Equivalent.
- `merge_train.py:5283` the stub's refusal rc `1` -> `2`: `Train.unstale` tests `if code:`, so any non-zero rc is the same refusal. Equivalent.

## Null control

The unmodified tree's self-tests: `python3 tools/pr/cancel_superseded.py --self-test` at fd93aa3e9b reads `87 checks, 0 failed` and expects `.../rerun` in its priority row; `python3 tools/audit/seat/merge_train.py --self-test` reads `839 checks, 0 failed`, counting `.../rerun` POSTs. The new rows' own nulls: the accepted failed-only case posts no whole-run re-run (`K15 (b) L7: the stale re-run is failed-only ...`), and `merge_pr.sh --self-test`'s `unstale_head` rows (`a check-run whose run is still in progress is not re-run (null control)`) stay green: `merge_pr self-test: 50 checks, 0 failed` at the head.

## Figures

- Whole-run re-run POST sites: `git grep -nE 'runs/\{[^}]+\}/rerun"' -- tools .github` -- base: `merge_train.py` (`Train.unstale`) and `cancel_superseded.py` (`priority_step`, plus its self-test row); head: the same two names, each now only the refused-failed-only fallback. Wider rule `git grep -nE '/rerun(["'"'"' )]|$)' -- tools .github tests` minus `rerun-failed-jobs`: every other hit is `actions/jobs/<id>/rerun` (job-scoped: `gate.py`, `sweep.py`, `ci_probe.py`, `ghapi.py`) or a self-test fixture (`gh_read.py`, `merge_pr.sh`, `sweep_selftest.py`); `codeql-triage-poll.sh` already passes `gh run rerun --failed`. Class closed: no production whole-run re-run remains outside the two fallbacks.
- Harness `dev/audit/harnesses/ci3885_queue.py` `rerun` arm, before (the code being replaced is what ran): this container reaches GitHub only through the GitHub MCP tools, so `ci3885_queue.py fetch` (which shells `gh api`) was not run. The arm's rule (a job of attempt >= 2 whose same-named job concluded success in the previous attempt, `gate` and `sweep-self` excluded, a job whose `started_at` equals the previous attempt's counted as a listing copy, not executed) was applied to `list_workflow_jobs filter=all` for 6 of the 11 attempt >= 2 CI runs created 2026-11-26 15:39Z-23:22Z (45907841043, 45907700288, 45897462684, 45891233921, 45891227294, 45883572405): 0 jobs re-executed after success, 0 runner-min; 64 listing copies excluded. Null (the arm's perturbation): counting copies as executed reads 64; attempt-1 jobs read as re-runs: 0. The design's 11-25 figure was 4 jobs, 5 runner-min, so L7 is a bound on a rare path, not a measured saving. After: owed on the first busy day past the merge (the arm reads CI history, which this branch cannot have).
- Architecture score: not run (`tools/` files only; no package seam).

## Red checks

none

## Forward-carry

- L2's remaining dispatches (a code unit running or cancelled at the head) are unmeasured at this base: `dev/programme/carries/carry-3885.json` carry 1 already holds the instruction (its `remeasure` clause: `ci3885_light.py dup DAY` on a busy day after the merge base, unit sets compared), so this pull request writes nothing new there; the L3 pull request, which edits `tools/ci/sweep.py`, reads it. Carry: #3885

## Friction

none
