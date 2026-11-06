## Re-cut

This body replaces the earlier body of this pull request. Nothing in it is carried from that body: every figure below was taken by my own command at the head named under `## Head`. Its scope is ONLY the round-3 blocked finding, `mutation-vacuous`: the `log_held` `off_loop_timeout` warning in `_await_off_loop` and its clearing were pinned by no check (mutants m4 and m6). No code changes in this re-cut: the code head is unchanged.

Bound the process worker's reply wait (`_run_in_process`), so a worker that is alive but silent no longer holds `_PROCESS_LOCK` forever.

## Acknowledgements

Thanks to @Bankaifan for the original change in #3226, the bounded reply deadline. This pull request is a seat re-author of that contribution, with his commits kept intact (each still authored by Bankaifan). Everything else on the branch is a seat commit on top.

Trust boundary: the worker is spawned by the integration and talks to it over a pickle pipe, and the integration unpickles what the worker writes. Each change leaves that boundary unchanged: the reply deadline and the frame bound only limit how long the reader waits; they add no new reader of untrusted input and no new pickle load, and the bytes handed to `pickle.load` are the same bytes as before. The diagnose-service translation runs in the service layer after the worker call and reads no worker data beyond the exception text.

## Head

`9a54629e11622402cb001502b9087650c1adc6a4`. `origin/main` has moved since this head was cut (the PR base read `b36679cea`; at this run it reads `33e60b5b7`). This re-cut changes only the body, so the code was not merged or re-run through `tools/pr/prepr.sh`; the merge with main belongs to the orchestrator's update of the PR head.

## Mutation proof

Each mutant was applied to its own detached worktree of `9a54629e1` and run with `PYTHONPATH=tests/hastub python3 tests/features.py`.
- m4: the `log_held(hass, key, True, "%s; %s skipped this cycle", err, name)` line deleted from `_await_off_loop`'s `except ProcessWorkerTimeout` clause, re-raise kept. Result: `1 of 4898 FEATURE CHECKS FAILED`; `FAIL two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery  [latch records=[]]`.
- m6: the clearing `log_held(hass, key, False)` before `return result` deleted. Result: `1 of 4898 FEATURE CHECKS FAILED`; the same check, `[latch records=[(30, 'process worker gave no reply within 0.5 s; sleep skipped this cycle')]]` (the WARNING, no recovery).

## Null control

The unmutated head, same command: `ok   two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery` and `ALL 4898 FEATURE CHECKS PASSED`. The check requires the WARNING and then the INFO `Resolved`, so a run that only warns (m6) and a run that never warns (m4) both fail it.

## Figures

- `ALL 4898 FEATURE CHECKS PASSED` at the head; m4 and m6 each `1 of 4898 FEATURE CHECKS FAILED` — `PYTHONPATH=tests/hastub python3 tests/features.py`

## Red checks

`none`. Every check-run of the pull request's current head `a6591432e579337fe81df0f813bf3aeb82919b55` (a merge of `9a54629e1`) was read: 7 runs in one page (`total_count` 7), none concluded red (three queued, two in progress, `cancel-superseded` success, `arm` skipped). Earlier concluded reds, including `codeql / Analyze (python)` cancelled at its 45-minute job limit at the previous head `6e048afc6`, are not concluded results at this head; if CodeQL cancels again it needs a re-run, as a cancel is a runner-time result, not about this diff.

Reds of the branch's ancestry (an earlier head, run 42135610131), named because the lint lists them; each concluded success at the later head `6e048afc6`:
- `tests / fast (3.14)`: `tests/entities.py` failed the R10 N-log-flood barrier (an unlatched WARNING). Cheaper detector: run `tests/entities.py` before the handoff; its standing cost is about 9 minutes.
- `tests / mutation`: an earlier head left its added mutation sites unpinned. Cheaper detector: `tools/pr/prepr.sh` mutation step before the handoff; its cost is that step's run time.
- `tests / mutation-autofix`: the same unpinned sites (`skip-measure-failed`), same answer as `tests / mutation`.
- `tests / replay`: a runner-calibration refusal (`runner class unknown`) of the cycle-cost instrument, set by which runner CI draws. No cheaper detector exists for this diff.
- `governance / delivery-status` and `tests / nightly-status`: they grade `main` (other pull requests' overdue rows, the nightly's own state), not this diff. No cheaper detector exists for this diff.

## Forward-carry

Built at the head, in the code, and out of this re-cut's scope (nothing here re-derives them):
- The frame-read bound: `_read_reply` unpickles through `_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S)` (60 s), so a worker that stops mid-reply no longer holds the lock. No live roster group fits a process-worker transport fix (R10-LOOP-CPU is done); the only live group that owns `coordinator.py` is R10-CLONE-2238, so it is the nearest owner, and the destination file is `custom_components/heatpump_optimizer/coordinator.py` (checks and mutation pins in `tests/features.py`). Carry: R10-CLONE-2238
- The diagnose-service translation: `handle_diagnose_interval` in `services.py` turns `ProcessWorkerUnavailable`, including `ProcessWorkerTimeout`, into `HomeAssistantError` with `translation_key="diagnose_interval_failed"`. No live roster group lists `services.py` (R10-SERVICES-GUARD is done); destination file `custom_components/heatpump_optimizer/services.py`, with `strings.json`, `en.json` and `sv.json`, and R10-CLONE-2238 is named only because the audit needs a live group. Carry: R10-CLONE-2238
- SECURITY.md has no contributor-acknowledgement text and the earlier rounds' briefs did not ask for it, so it is not edited here (no code changes); if the owner wants the thanks there, destination file `SECURITY.md`. Carry: dismissed: no earlier brief asked for it and this re-cut changes no files

## Friction

none
