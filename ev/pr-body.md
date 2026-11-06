Bound the process worker's reply. Before this change `_run_in_process` wrote the job and blocked in `pickle.load(stdout)` inside `with _PROCESS_LOCK:` with no deadline. A worker that is alive but silent never raises, so the #511 fallback never fired. Every later solve then queued on the lock, a reload did not help, and Home Assistant's stop ran into the supervisor timeout. The branch adds:
- the reply deadline (`PROCESS_REPLY_TIMEOUT_S`, 1800 s; the contributor's change);
- the off-loop route's re-raise and held warning;
- the frame deadline (`_REPLY_FRAME_TIMEOUT_S`, 60 s) and the frame size cap (`_REPLY_FRAME_MAX_BYTES`, 256 MiB, round 4);
- the stop path's bounded lock (`_SHUTDOWN_LOCK_TIMEOUT_S`, 5 s);
- the diagnosis service's translated failure (`diagnose_interval_failed`).

This round repairs one red: `codeql / Analyze (python)` ran past its 45-minute job limit and was cancelled at every recent head of this pull request. The cause, measured below, is CodeQL's Python **extraction** of `tests/features.py`, not query evaluation and not the runner. This PR's 387-line test section inside that 78k-line module pushed the file's extraction from 817–1389 s (main) to 2146–2211 s.

The fix moves that section's body, with round 4's 60 size-cap lines, into `tests/worker_deadlines.py`. It is a module, not a script, exposing `run(R, parent_pid)`, and `features.py` imports and calls it at the section's old place. The checks still run, report and kill mutants as feature checks, while CodeQL extracts them as a separate small file. `tests/features.py` is main's text plus the 3 translation-key lines and the 8-line call. This round changes no production code, and nothing is excluded from analysis.

Why a module and not a second runnable script: a new `tests/*.py` script raises the CI ratchet's every-script-once count (`tests/ci_budgets.json` `script_runs_per_push`, 54) to 56. The first cut, a standalone `tests/worker_timeout.py`, read `budget 54, every-script-once count 56` in `tests/entities.py`, which is a budget raise, so it was replaced. The module is on `tests/closure.py`'s `NOT_A_TEST` list and on run.sh's two accounting skip lists beside `harness.py`. It is measured through the closures of `features.py` and `entities.py`.

**Trust boundary.** Every change leaves the same boundary in place. The worker is the integration's own child process, launched by `_ensure_worker` from the installed package. Its reply is still unpickled in the parent, as it was at base. No new deserialisation is added: `_frame_reader` only feeds the same `pickle.load` the bytes it already read, now under a time bound and a size bound. The job the worker may run is unchanged (`fn, args` chosen by the parent). The diagnosis translation only reshapes an exception that already reached the service caller. This round touches no file under `custom_components/`. The reply deadline, the frame bound (time and size) and the diagnose-service translation keep every check (26, now in `tests/worker_deadlines.py`) and all 20 mutation pins, each re-recorded against `tests/features.py` (`## Mutation proof`).

## Acknowledgements

Thanks to @Bankaifan for the original change in #3226: the bounded reply deadline on the process worker, and the field report and shutdown traces that found the hang. This pull request is a seat re-author of that contribution. Decision 0011 gives an outside contributor no way to author a pull request here, so the seat re-authored it. His four commits (`61cec72ac`, `010534bbc`, `dd4416f1a`, `5088d3688`, author Bankaifan) are kept intact: no edit, squash or rebase. The seat's repairs are separate commits on top of them.

## Head

`bba5b4d4d7ac37f339850de36b1ca24573f8c821` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

`79f202f8ea3e2cc6a67c6438dafd2cd192dd81e3`. It descends from the PR head `0e59de5574d72746dbcd3fa1319d3ad3dd64776b` (round 4's handoff `4eddf95fe` merged into it) and from `origin/main` `9cbd7dd0d7a66163b5b593dfe55f1d8b220785de`, read at 2026-11-06T20:29:40Z. It merges `origin/main` three times and that PR head once. Every figure below was taken at this head unless it names another SHA. `features.py`, `entities.py`, `structure.py` and `closure.py selftest` ran after the last merge. The closures of `features.py` and `entities.py` were recorded before the round-4 merge, which added no import to either.

## Mutation proof

The move must not lose a kill. Each `killed_by` row this pull request adds was deleted and re-recorded with `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --scope changed --base origin/main --scripts tests/features.py`, while the checks reach `features.py` only through `worker_deadlines.run`.
- The 18 rows of rounds 1–3: 17 sites `killed by tests/features.py` in the first run (`PIN KILLED: 17 pinned, 1 left unpinned`, `1 timed out`). The 18th, coordinator.py `_frame_reader.read` `CMP_BOUND` (`while size >= 0:`), ran out the default 1200 s per-mutant timeout, because each frame read then waits out its 60 s deadline. A re-drive with `--timeout 6000 --jobs 1` read `pinned custom_components/heatpump_optimizer/coordinator.py:1944 CMP_BOUND -- killed by tests/features.py`, `PIN KILLED: 1 pinned, 0 left unpinned`. These were recorded before the round-4 merge.
- The 2 round-4 size-guard rows (`_frame_reader.read.GUARD_OFF.821e5720`, `_frame_reader.read.CMP_BOUND.821e5720`), after the merge, with `--jobs 2 --timeout 6000`: `PIN KILLED: 2 pinned, 0 left unpinned`.
- The sites are coordinator.py:
  - `CONST` ×3 (the reply deadline, the shutdown lock wait, the frame deadline) and `_shutdown_process_pool` `GUARD_OFF`;
  - `_reply_ready` `RETURN_DEL`;
  - `_frame_reader`: `CMP_BOUND` ×2, `GUARD_OFF` ×3, `RETURN_DEL` ×3, `BOOLOP`;
  - `_read_reply` `GUARD_OFF`/`RETURN_DEL`, `_run_in_process` `RAISE_DEL`, and `_await_off_loop` `RAISE_DEL`/`RETURN_DEL`.

  Plus services.py `handle_diagnose_interval` `GUARD_OFF`. The re-recorded files are the same anchors the PR head carried; the `diff` of the basename lists is empty. The `survivor_triage` row `_frame_reader.read.CMP_BOUND.fb715113` is unchanged.

## Null control

Each pin run: `null control custom_components/heatpump_optimizer/coordinator.py:381 NULL_COMMENT survived tests/features.py`, and `baseline tests/features.py: rc=0 failed=0`. A driver that failed on any edit would have killed the comment-only mutant too. The suite's count is the move's own null control: `ALL 4902 FEATURE CHECKS PASSED` at this head, the same 4902 the PR head counted with the checks inline. A check lost in the move would have lowered it.

## Figures

- `tests/features.py` extraction, main: 817 s, 967 s, 1389 s. Jobs 127952679731, 127954661976, 127995766058 (whole job 28 min, 31 min, 43 min) — `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs | grep -E "Extracted file .* in [0-9]{5,}ms"`
- `tests/features.py` extraction, PR head `a6591432e`: 2211 s (job 127991077283) and 2146 s (job 127962199961). In job 127932155925 it had not finished after 2675 s, from the first extracted file at 13:59:42 to the cancel at 14:44:17. Queries began at 16:30:37 and 15:34:53, and both jobs were cancelled 7 and 9 minutes into query evaluation, which takes 13–19 minutes on main — same command
- `tests/entities.py` extraction: main 342–688 s, head 317–671 s. Its cost is the same at both ends, so it is not the cause — same command
- `tests/features.py` lines: 78350 on main (`a2240924`, `817c2b16`, `30638cf0` alike), 78740 at `a6591432e`, 78361 (78350 + 3 translation-key lines + the 8-line call) at this head — `git show <sha>:tests/features.py | wc -l`
- `ALL 4902 FEATURE CHECKS PASSED` at this head — `PYTHONPATH=tests/hastub python3 tests/features.py`
- `ALL 2637 ENTITY CHECKS PASSED` at this head — `PYTHONPATH=tests/hastub python3 tests/entities.py`. Before run.sh's accounting lists skipped `worker_deadlines.py` it read `2 of 2637` (fixed in `b074d6c75`). The standalone first cut read `budget 54, every-script-once count 56` (the opening paragraphs)
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`
- `ALL 118 closure shrink pins PASSED` — `python3 tests/closure.py selftest`
- the closures of `features.py` (146 files) and `entities.py` (553 files) each gain exactly `tests/worker_deadlines.py` — `./tests/derive_closures.sh --single tests/features.py`
- scope `MODE: FULL` (reason: `tests/closure.py changes the gate itself`), because the diff adds `worker_deadlines.py` to `NOT_A_TEST`. What I ran is listed above; the rest is CI's — `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`

Prediction, not a measurement: CodeQL has **not yet run at this head**. Its extraction now sees `tests/features.py` at main's size plus 11 lines, and `tests/worker_deadlines.py` as a separate 532-line file, so this job should take what main's does, 28–43 min. I could not run the CodeQL CLI in this container, so the PR's own check-run is the first measurement.

## Red checks

- `codeql / Analyze (python)`: cancelled at the 45-minute job limit at `a6591432e` three times, jobs 127932155925, 127962199961 and 127991077283, and at the earlier head `6e048afc6` (job 127737658362). The earlier bodies called this runner-side; that was wrong. Cause: CodeQL's Python extractor spent 2146 s and more on `tests/features.py` once this PR had added 387 lines to it, against 817–1389 s on main for the same file without them. The job then ran out of time in query evaluation (`## Figures`). Fixed by moving the section's body to `tests/worker_deadlines.py`. Cheaper detector: none in the tree. No local check measures a file's CodeQL extraction cost, and the job's 28–43 min main-branch run is the standing cost of the only detector, which is CodeQL itself.
- `pr-contract / pr-contract` and `gate`: red at `a6591432e` because they wait for a finished CodeQL unit; same cause, same fix.
- `governance / instrument-self-tests`: no cancel at `a6591432e`. Every non-success, non-skipped check-run there was read: `gate` ×5 failure, `codeql / Analyze (python)` cancelled, `pr-contract / pr-contract` failure, `CodeQL` neutral. The 30-minute main-wide cancels, cured by R10-PROCESS-SLIM #3245, did not occur here.

Reds of the branch's ancestry (an earlier head, run 42135610131), named because the lint lists them; each concluded success at the later head `6e048afc6`:
- `tests / fast (3.14)`: `tests/entities.py` failed the R10 N-log-flood barrier (an unlatched WARNING). Cheaper detector: run `tests/entities.py` before the handoff; its standing cost is about 7 minutes (414 s here).
- `tests / mutation`: an earlier head left its added mutation sites unpinned. Cheaper detector: `tools/pr/prepr.sh` mutation step before the handoff; its cost is that step's run time.
- `tests / mutation-autofix`: the same unpinned sites (`skip-measure-failed`), same answer as `tests / mutation`.
- `tests / replay`: a runner-calibration refusal (`runner class unknown`) of the cycle-cost instrument, set by which runner CI draws. No cheaper detector exists for this diff.
- `governance / delivery-status` and `tests / nightly-status`: they grade `main` (other pull requests' overdue rows, the nightly's own state), not this diff. No cheaper detector exists for this diff.

## Forward-carry

- `tests/features.py` costs CodeQL 817–1389 s of extraction on main, and the whole python job ran 43 min on main at `30638cf0`, within 2 minutes of its 45-minute limit. Any pull request that adds a few hundred lines to that one module can cancel CodeQL the way this one did. The nearest owner is R10-PROCESS-SLIM (the CI-cost lane: `.github/workflows/codeql.yml` timeout and the split of `tests/features.py`). Landing it in that brief means writing the round's roster branch (`carry_audit.py land-ops`), which this seat's dispatch forbids, so `body_push.sh` refused it as `CARRY-MISSING`; the orchestrator decides. Carry: dismissed: this seat may not write the roster branch; the orchestrator lands it on R10-PROCESS-SLIM or refuses it
- Two fixer seats ran on this topic at once: this one (the CodeQL repair) and round 4 (the frame size cap). Round 4 handed off at `4eddf95fe` while this round was running, and the orchestrator merged it into the PR head as `0e59de557`. This head merges that and ports round 4's three `features.py` hunks into `tests/worker_deadlines.py`: 2 check blocks and the design-value pin, with names translated, 4 checks in all (26 = 22 + 4). `refs/heads/handoff-wip/r10-ext-3226` held round 4's lineage, now ending in its `BLOCKED` note `711f2719d`. This round could not fast-forward it and did not overwrite or delete it, so its step pushes stayed local. Carry: dismissed: orchestrator's dispatch, not a finding

## Friction

- fixer-step-push: contradiction: the brief says to step-push fast-forward only to `handoff-wip/r10-ext-3226` and to delete it after the handoff, but a concurrent seat on the same topic owned that ref, and its tip `711f2719d` is not in this head's ancestry, so neither was possible without discarding them. Carry: dismissed: orchestrator's dispatch, not a finding

