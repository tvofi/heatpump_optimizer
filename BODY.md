<!-- The headings below are what `pr-contract` requires: each is content or an
explicit `n/a: <reason>`. Run
`tools/pr/prepr.sh <this body>` before opening. -->

## Re-cut

Round 4 of #3232. This body is re-taken whole; round history is deleted, and every figure below was taken in this pass.

Bound the process worker's reply. Before this change `_run_in_process` wrote the job and blocked in `pickle.load(stdout)` inside `with _PROCESS_LOCK:` with no deadline. A worker that is alive but silent never raises, so the #511 fallback never fired. Every later solve then queued on the lock, a reload did not help (the lock and the worker are module globals), and Home Assistant's stop ran into the supervisor timeout because `_shutdown_process_pool` could not take the lock. The contributor observed this on a Raspberry Pi 4 install (v7.1.2, HA 2026.10.4) on 2026-11-05.

What the branch does (`coordinator.py`, `services.py`):
- **Reply deadline (the contributor's change).** `_read_reply` waits for the pipe to turn readable under `PROCESS_REPLY_TIMEOUT_S` (1800 s), through a `selectors` selector, which also accepts a descriptor at or above FD_SETSIZE. On expiry the worker is killed, its reap is bounded, the handle is cleared and `ProcessWorkerTimeout` (a `ProcessWorkerUnavailable`) is raised. `_await_optimize` does not rerun a timed-out job in process: it raises the translated `process_worker_timeout` `UpdateFailed`, so the last plan stays in effect, and its warning is held (`log_held`, `process_worker_timeout:<entry_id>`). The stop path takes the lock with `_SHUTDOWN_LOCK_TIMEOUT_S` (5 s).
- **Off-loop route.** `_await_off_loop` re-raises the timeout rather than rerunning the job on the executor with no deadline, and holds a per-job warning (`off_loop_timeout:<qualname>`), cleared when that job next completes. This round pins both halves (review item 1).
- **Frame deadline.** Once the pipe is readable, `pickle.load` reads through `_frame_reader`, a closure pair (`read`, `readline`) over the raw descriptor. Every read is checked against `_REPLY_FRAME_TIMEOUT_S` (60 s). A writer stopped mid-frame (SIGSTOP, a stalled host) is reaped as `ProcessWorkerTimeout` and the lock is freed (review item 2).
- **Frame size.** New this round: `read` refuses any request that would take the frame past `_REPLY_FRAME_MAX_BYTES` (256 MiB). It checks the length the unpickler asks for, before `os.read` allocates it. The refusal is a `ValueError`, so it takes the existing transport route in `_run_in_process`: the worker is reaped mid-frame, the lock is released, and the caller gets `ProcessWorkerUnavailable` (in-process fallback for a solve).
- **Diagnosis service.** `handle_diagnose_interval` catches `ProcessWorkerUnavailable` (and so `ProcessWorkerTimeout`) from `async_diagnose_interval`. It raises `HomeAssistantError` with `translation_key="diagnose_interval_failed"` (in `strings.json`, `en.json`, `sv.json`), which is the shape the other services use for a failed call (review item 3).

Why 256 MiB: the cap must sit above any real reply and above the reviewer's 50 MB round-trip control, but well below a Raspberry Pi's memory. Real replies measured on the whole feature suite peak at 22,913 bytes (`optimize_in_process`; see `## Figures`), so the cap leaves about four orders of magnitude of headroom. Alternatives considered:
- *No size cap, deadline only.* Lost: a declared length from the worker would still drive one `os.read` allocation of any size.
- *Raising `ProcessWorkerTimeout` for an oversized frame.* Lost: it is not a timeout, and `_await_optimize` would then keep the last plan, where a transport fault correctly falls back in process.

**Trust boundary.** Every change leaves the same boundary in place. The worker is the integration's own child process, launched by `_ensure_worker` from the installed package. Its reply is still unpickled in the parent, as it was at base. No new deserialisation is added: `_frame_reader` only feeds the same `pickle.load` the bytes it already read, now under a time bound and a size bound. The job the worker may run is unchanged (`fn, args` chosen by the parent). The diagnosis translation only reshapes an exception that already reached the service caller.

## Acknowledgements

Thanks to @Bankaifan for the original change in #3226: the bounded reply deadline on the process worker, and the field report and shutdown traces that found the hang. This pull request is a seat re-author of that contribution. Decision 0011 gives an outside contributor no way to author a pull request here, so the seat re-authored it. Their four commits (`61cec72ac`, `010534bbc`, `dd4416f1a`, `5088d3688`, author Bankaifan) are kept intact: no edit, squash or rebase. The seat's repairs are separate commits on top of them.

## Head

`4eddf95fe1c7ebebc59b1257fb01a95553390f32`. It descends from the PR head `6e048afc6d857f65b62108e0648543dd611bd433` and merges origin/main at `4b7e1770ba81fa02a8dda531463eba68e987ff59` (2026-11-06, after a stamp). `tools/pr/prepr.sh` ran clean at this head (`PRE-PR: 4eddf95fe... rc=0`). origin/main then moved to `57958d6a44c4f489384705ba64e8f65a8507f6b7` (checked 18:56Z). That delta is `dev/programme/delivery/3258.md` and `dev/programme/rosters/wave-r10-groups.json` only, and `git merge-tree --write-tree origin/main HEAD` reports no conflict. It is not merged: main moved five times during this round, and `fixer.md` step 6 merges main before the handoff only on a conflict or a `DIRTY` head. The claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` are byte-identical to that main. Figures below name the SHA they were taken at.

## Mutation proof

Each mutant was applied to its own worktree of `1b40b2058` with a checked string replacement (it must match exactly once) and run with `PYTHONPATH=tests/hastub python3 tests/features.py`:
- m4, the `log_held(hass, key, True, ...)` line in `_await_off_loop`'s `except ProcessWorkerTimeout` deleted, re-raise kept: `1 of 4902 FEATURE CHECKS FAILED`. `FAIL two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery  [latch records=[]]`.
- m6, the clearing `log_held(hass, key, False)` before `return result` deleted: `1 of 4902 FEATURE CHECKS FAILED`. Same check, `[latch records=[(30, 'process worker gave no reply within 0.5 s; sleep skipped this cycle')]]` (the WARNING with no Resolved line).
- m-frame, `_read_reply` back on `pickle.load(stdout)` (frame bound removed): `2 of 4902 FEATURE CHECKS FAILED`:
  - `FAIL a worker stopped mid-reply raises ProcessWorkerTimeout, is reaped and frees the lock  [raised None after 30.0 s; returned 'split'; ...]`: the stalled writer held the lock for its whole 30 s stall.
  - `FAIL a reply frame past its size cap is a transport fault: ...`.
- m-size, the size guard `if size > left_bytes:` made `if False:`: `2 of 4902 FEATURE CHECKS FAILED`:
  - `FAIL a reply frame past its size cap is a transport fault: the worker is reaped and the lock freed`.
  - `FAIL the frame reader refuses a declared length past its cap at once, and waits on one under it  [results=[('ProcessWorkerTimeout', 0.300...), ('ProcessWorkerTimeout', 0.300...)]]`.
  - That check now probes the length at the cap itself and reads `... and waits on one at it`. The tightening killed the comparison's `CMP_BOUND` survivor (below).
- m-diag, the `except ProcessWorkerUnavailable` in `handle_diagnose_interval` narrowed to `except ZeroDivisionError`: `2 of 4902 FEATURE CHECKS FAILED`:
  - `FAIL a diagnosis failing with ProcessWorkerTimeout reaches the service caller translated  [raised ProcessWorkerTimeout('process worker gave no reply within 1800 s')]`.
  - `FAIL a diagnosis failing with ProcessWorkerUnavailable reaches the service caller translated  [raised ProcessWorkerUnavailable('process worker cannot start: boom')]`.
- The mutation table's own mutants on the new size guard, from `python3 tests/mutation_table.py --pin-killed --base origin/main`:
  - `GUARD_OFF` killed by `tests/features.py` and pinned (`_frame_reader.read.GUARD_OFF.821e5720.json`).
  - `CMP_BOUND` (`>` to `>=`) survived the first run. After the check moved to the exact cap it was killed and pinned (`_frame_reader.read.CMP_BOUND.821e5720.json`).
  - The third run at `7e778b9d3`: `PIN KILLED: nothing to pin`.
- Residual, disclosed: the bounded reap `worker.wait(timeout=_SHUTDOWN_LOCK_TIMEOUT_S)` after a timeout's kill needs a child that survives SIGKILL, which no portable check can produce. Carry: dismissed: needs a child in uninterruptible sleep, which no portable test produces; disclosed in verdict/3232

## Null control

- The unmutated tree runs the same suite green: `ALL 4902 FEATURE CHECKS PASSED` at `4eddf95fe` (and at `7e778b9d3` before the main merges). Each mutant above fails only the checks named for it.
- The size checks carry their own controls:
  - A 900,000-byte reply under a 1,000,000-byte cap returns whole (`null control: a reply under the frame size cap returns whole`).
  - A 50 MB reply returns whole under the shipped cap and deadline (`null control: a 50 MB reply arrives whole through the frame reader, inside its deadline`).
  - The reader refuses a declared length one byte past the cap within 0.1 s, and waits out its deadline on one exactly at it. A refusal that came from the deadline rather than the guard would take the full 0.3 s and fail the check.
- The frame deadline's controls: a frame written in two halves inside the deadline returns, and a worker that dies mid-frame is a transport fault, not a timeout.
- The 50 MB round trip (review item 2) is under the 60 s frame deadline at the head: median 0.148 s, max 0.150 s over 5 runs. Control at origin/main `817c2b16`, which has no frame reader: median 0.095 s, max 0.110 s. Both from the same probe (below).

## Figures

- `ALL 4902 FEATURE CHECKS PASSED` at `4eddf95fe` — `PYTHONPATH=tests/hastub python3 tests/features.py`
- `ALL 2637 ENTITY CHECKS PASSED`, including `ok   R10 N-log-flood barrier`, at `4eddf95fe` — `PYTHONPATH=tests/hastub python3 tests/entities.py`
- `STRUCTURE RATCHET PASSED` at `4eddf95fe` — `python3 tests/structure.py`
- `MODE: SCOPED -- 26 script(s) run, 7 scoped out.` — `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
- `28 TEST SCRIPT(S) PASSED; 6 SCOPED OUT AND NOT RUN` at `d3c5afc43`, the previous merge of main; the last merge (`862affd0..4b7e1770`) adds only `tests/mutation_ledger/killed_by/` pins for other modules (`git diff --name-only 862affd0 4b7e1770`) — `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`
- `PIN KILLED: nothing to pin` at `7e778b9d3` — `python3 tests/mutation_table.py --pin-killed --base origin/main`
- 50 MB round trip, head median 0.148 s / max 0.150 s; origin/main median 0.095 s / max 0.110 s — a scratch probe that warms a worker, then times `_run_in_process(bytes, (50_000_000,))` five times from each tree root (sha1 `add8d9c88653dd536caf208a6c885b1054b95d65`, not committed: a one-off probe)
- Largest real reply 22,913 bytes (`optimize_in_process`), out of 1772 replies in one full feature run; the only larger frame is the 50 MB control (`bytes`). Instrument: a scratch worktree of `c17f1938a` whose `process_worker._dump` appends `len(blob)` and the job's qualname to a log before writing. Not committed: a one-off measurement
- toolchain: numpy 2.5.4 and scipy 1.18.1, equal to `tests/requirements-ci.txt`; `cloud-setup.sh --check` reports `OK` — `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'`

## Unpinned sites

None this diff leaves open. The two new size-guard sites are pinned under `tests/mutation_ledger/killed_by/coordinator.py/`. The size cap's value is pinned by the design-value check `the reply frame size cap stays at its 256 MiB design value`, because every behavioural check shortens it. That check encodes a design choice (fixer step 11): changing the cap means changing its check.

## Red checks

The final head has not run CI yet. At the previous head `6e048afc6`, the only concluded non-success check was:
- `codeql / Analyze (python)`: **cancelled** (job 127737658362, run 42170673519). It started 05:49:59Z and the log ends `##[error]The operation was canceled.` at 06:35:02Z in `Waiting for processing to finish`. That is the job's `timeout-minutes: 45` (`.github/workflows/codeql.yml`), a cancel in the analyzer's processing wait, not a result about this diff. It **needs a re-run** at the new head. No cheaper detector exists: CodeQL's analysis time is not something a local check reproduces.
- `gate` (x3) aggregated that cancel (`FAIL codeql / Analyze (python): cancelled`).

Reds concluded on an earlier commit of this branch, the round-1 head `e80a319c2` (run 42135610131), each answered at this head:
- `tests / fast (3.14)`: `1 TEST SCRIPT(S) FAILED`. The failing script was `tests/entities.py`, `R10 N-log-flood barrier` (`1 of 2632 ENTITY CHECKS FAILED` in verdict/3232's run at that head): the `_await_optimize` timeout warning was an unlatched `_LOGGER.warning`. This head routes it through `log_held` and reads `ALL 2637 ENTITY CHECKS PASSED` with `ok   R10 N-log-flood barrier`. Cheaper detector: `tests/entities.py` run locally before the handoff, about 9 minutes per run, already in `scope.run`. Run here.
- `tests / mutation` and `tests / mutation-autofix`: that head left its added sites unpinned, and the autofix log read `skip-measure-failed -- THE REPAIR DID NOT HAPPEN`. Every site this diff adds is now pinned (`PIN KILLED: nothing to pin` at `7e778b9d3`). Cheaper detector: `prepr.sh` step 6d, which reports `the diff adds no unpinned mutation site` at this head.
- `tests / replay`: `cycle_cost ... runner class unknown: ref_ms 27.26 lies in no band of COST_RUNNER_CLASSES`. That is a gap in the instrument's runner calibration, and this diff does not cause it. No cheaper detector exists for this PR, because the red depends on which runner CI draws.

## Forward-carry

none

## Friction

- harness-identity: contradiction: the routine's header says to pin `git config user.name seat` before any commit, and its brief says `hpo-fixer` and "Never commit as 'seat'". The container also exports `GIT_AUTHOR_NAME=seat` and `GIT_COMMITTER_NAME=seat`, which override `git config`. The round-3 seat commits (`b8cb6ef36` .. `9a54629e1`) carry `seat`. This round's commits set the hpo-fixer identity through the environment per command. Carry: dismissed: dispatch-template wording outside this PR, recorded for the orchestrator's friction triage
- wip-ref-race: unclear: `handoff-wip/r10-ext-3226` moved to `9a54629e1` (a `seat` merge of origin/main, tree identical to this seat's own) 24 s before this seat's first push, from no session reachable here. This seat's commits were replayed onto it, so the ref stayed fast-forward. It suggests the routine fired twice. Carry: dismissed: scheduler behaviour outside this repository, recorded for the orchestrator
- arch-score-plant: cost: a passing `tests/arch_score.py` run leaves `$RUNNER_TEMP/base` behind (a worktree of its `/tmp/archscore-plant-*` repo), so the next run in the same container exits 1, and `prepr.sh`'s closures step refuses `failed while being recorded: tests/arch_score.py (exit 1)`. Measured in this round: after the scoped gate's run, prepr run 1 refused; with the directory removed, run 2 passed the closures step; run 3 refused again. CI's fresh `RUNNER_TEMP` never sees it. Carry: dismissed: tooling outside this PR's scope, recorded for the orchestrator's friction triage
