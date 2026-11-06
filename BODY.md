<!-- The headings below are what `pr-contract` requires: each is content or an
explicit `n/a: <reason>`. Run
`tools/pr/prepr.sh <this body>` before opening. -->

Bound the process worker's reply wait and the stop path's lock. This is the seat-authored re-author of the outside contributor Bankaifan's PR #3226. This round repairs the round-2 review's block (verdict/3232, `mutation-vacuous`) and builds the review's two further findings. Round 10 defers no defect, so neither is carried.

`_run_in_process` wrote the job and then blocked in `pickle.load(stdout)` with no deadline, inside `with _PROCESS_LOCK:`. A worker that is alive but silent never raises, so the #511 fallback never fired. Every later solve, every reload and the stop path then queued on the lock. The contributor observed this on one install (v7.1.2, HA 2026.10.4, Raspberry Pi 4) on 2026-11-05.

**Contributor credit.** The deadline change is by Bankaifan (PR #3226, head `ba704972f6494d4e6af520095e940b049d9afed3`). The contributor's four commits (`61cec72ac`, `010534bbc`, `dd4416f1a`, `5088d3688`) are kept unchanged, each authored by Bankaifan. Every repair is a new seat commit on top, merged with main and never rebased.

What earlier rounds landed, unchanged here:
- the 1800 s reply deadline (`PROCESS_REPLY_TIMEOUT_S`) and `ProcessWorkerTimeout`;
- the bounded stop-path lock;
- the selector wait (`_reply_ready`, fd >= 1024);
- the held `_await_optimize` warning;
- `_await_off_loop` re-raising a timeout instead of rerunning the job on the executor.

This round, one item per brief entry:
1. **The block: the off-loop warning was pinned by no check.** A new check in the `worker read timeout` section runs `_await_off_loop(hass, time.sleep, 30)` past a 0.5 s deadline twice, then `time.sleep(0)` within the deadline, with a sink on `log_held`'s logger. It requires exactly `[WARNING, INFO]`, the INFO line `Resolved: off loop timeout:sleep`, and the job name in both lines. m4 and m6 now each turn it red (below).
2. **The frame read: `pickle.load(stdout)` was unbounded once the pipe turned readable.** The reply read moves into `_read_reply`. After the reply deadline's readiness wait, it unpickles through `_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S)` (60 s), a `read`/`readline` closure pair over the raw descriptor. Every read waits under one frame deadline, and the deadline is checked explicitly. Two reasons it is not left to the readiness wait alone: a descriptor at end of stream always reads as ready, and the wait could otherwise never expire there. A stall raises `ProcessWorkerTimeout("process worker stopped mid-reply ...")`. `_run_in_process`'s `except ProcessWorkerTimeout` then clears `_PROCESS_WORKER`, kills the worker, reaps it within `_SHUTDOWN_LOCK_TIMEOUT_S` and re-raises, and the `with` releases the lock. The reader reads the raw descriptor and never the `BufferedReader`, because bytes held in that buffer are invisible to a selector. It has no `peek`, so the unpickler reads exactly the frame and nothing past it. An end of stream mid-frame stays a transport fault (`ProcessWorkerUnavailable`), not a timeout.
3. **The note: `async_diagnose_interval` let the worker's own exceptions reach the service caller.** `handle_diagnose_interval` (services.py) now catches `ProcessWorkerUnavailable`, including its `ProcessWorkerTimeout`, per entry. It raises the shape the other services use for a failed call: `HomeAssistantError`, `translation_key="diagnose_interval_failed"`, with placeholders `entry_ids` and `error`. The key is in `strings.json`, `en.json` and `sv.json`, and is registered in the exception-key census (`_ET_KEYS`). The translation lives in the service layer, which owns service errors, so no `homeassistant` exception is imported into the worker path. The button path (`off_the_action`) is a background task with no caller to answer, so it is unchanged.
4. **CI at the old head:** see `## Red checks`.

Shapes considered and not taken:
- *A `_FrameReader` class.* Its `readline`, which only `pickle` calls, reads to `tests/structure.py` as a dead method, so `dead_methods` and `name_kept_members` would each rise by 1. The closure pair carries the same two functions without a protocol class. The ratchet passes with no budget touched.
- *A length-prefixed reply frame.* It changes the worker's wire protocol on both sides, along with every in-memory test stream. The reader keeps the protocol.
- *A `min(size, 1 MiB)` clamp on `os.read`.* It was dropped: the 50 MB round trip took 0.13 s with and without it, because a pipe read returns at most what is buffered. Its only effect was an unkillable mutation site.
- *Respelling `os.read` to get past the InputReader-key census.* The census keyed its read calls on the method name alone, so it counted `os.read(fd, ...)` as an input read (`reads keyed some other way: ['coordinator.py:1950 fd']`). Step 14 says to widen the key until the occurrences separate. The census now skips a call whose receiver is the name `os`, because an InputReader is never reached as `os`. It still flags any other `.read(...)` receiver, as before. This encodes a design choice: a module-level `os` read is a descriptor read.

## Head

`9a54629e11622402cb001502b9087650c1adc6a4`. It descends from the PR head `6e048afc6d857f65b62108e0648543dd611bd433` and merges origin/main at `b36679ceaa65a08a67a84f0d934c93aa15f7c7f3`. At this head, `tests/structure.py` (`STRUCTURE RATCHET PASSED`), the scope's MODE line and `tools/pr/prepr.sh` were re-run. prepr.sh read `PRE-PR: 9a54629e11622402cb001502b9087650c1adc6a4 ... rc=0` at 2026-11-06 13:11 UTC, with origin/main at `b36679cea`. Main has not moved since, so no second run was needed.

The suite runs (features, entities, the five mutants and the base control) and the 50 MB probe were measured at `feaafef5d021851bf5a01ea06a1bbae2bb2580db`, this branch's merge with origin/main `7e8939d38`. The head's last merge brings `7e8939d38..b36679cea`, which touches only `dev/audit/harnesses/r10_triage_p391.py`, `dev/programme/delivery/3238.md`, `dev/programme/delivery/3243.md`, `dev/programme/triage/s6-batch126.md`, `tests/closures.json` and `tests/gate_lock.py` (`git diff --stat 7e8939d38 b36679cea`). None of these is production code or an input those suites read, so the figures carry to this head unchanged. The base null control (`ALL 4876 FEATURE CHECKS PASSED`) is at `7e8939d38`.

## Mutation proof

Each mutant was applied to its own worktree of the head and run with `PYTHONPATH=tests/hastub python3 tests/features.py`. The control is the unmutated head, which reads `ALL 4898 FEATURE CHECKS PASSED`.
- m4: the `log_held(hass, key, True, ...)` line deleted from `_await_off_loop`'s `except ProcessWorkerTimeout` clause, with the re-raise kept. Result: `1 of 4898 FEATURE CHECKS FAILED`, `FAIL two off-loop timeouts of one job warn once, naming it, and its next completion logs the recovery  [latch records=[]]`.
- m6: the clearing `log_held(hass, key, False)` before `return result` deleted. Result: `1 of 4898 FEATURE CHECKS FAILED`, the same check, `[latch records=[(30, 'process worker gave no reply within 0.5 s; sleep skipped this cycle')]]` (the WARNING with no recovery).
- m8: the frame bound removed (`return pickle.load(_frame_reader(fd, _REPLY_FRAME_TIMEOUT_S))` -> `return pickle.load(stdout)`). Result: `FAIL a worker stopped mid-reply raises ProcessWorkerTimeout, is reaped and frees the lock  [raised None after 30.0 s; returned 'split'; ...]`. The lock was held for the whole 30 s stall. The script then exits non-zero on an uncaught `ProcessWorkerUnavailable` later in that section.
- m9: `raise` inserted at the top of `handle_diagnose_interval`'s `except ProcessWorkerUnavailable` clause. Result: `2 of 4898 FEATURE CHECKS FAILED`: `a diagnosis failing with ProcessWorkerTimeout reaches the service caller translated  [raised ProcessWorkerTimeout('process worker gave no reply within 1800 s')]` and the same for `ProcessWorkerUnavailable('process worker cannot start: boom')`.
- m10: the reader's end-of-stream guard `if not chunk:` -> `if False:`. Result: `FAIL a worker that dies mid-reply is a transport fault, not a timeout  [raised ProcessWorkerTimeout('process worker stopped mid-reply: the frame did not arrive within 0.5 s') after 0.52 s]`. Before the explicit deadline check (`b25c7084c`), this mutant hung forever: a pipe at end of stream reads as always ready. The mutation table recorded that hang as `timed out`.
- The mutation table's own mutants: 0 new sites left unpinned (see `## Unpinned sites`). That covers this round's 12 killed pins under `tests/mutation_ledger/killed_by/` and 1 triage. The 2 pins on the old `has_fd and not _reply_ready(...)` line (`_run_in_process` BOOLOP and GUARD_OFF) went stale when that guard moved into `_read_reply`, and were removed. Its successors are pinned as `_read_reply` GUARD_OFF and RETURN_DEL.

## Null control

- The unmutated head passes every check above, so each red is the mutant's.
- The base, origin/main `7e8939d38`, reads `ALL 4876 FEATURE CHECKS PASSED` and has none of these checks.
- In-section null controls, each green at the head:
  - `null control: a 50 MB reply arrives whole through the frame reader, inside its deadline`.
  - `null control: a reply frame written in two halves inside the frame deadline returns`. This is the same harness job as the stalled-writer check (`harness.split_reply`), with a 0.05 s pause instead of a 30 s one.
  - `null control: a diagnosis that runs is returned by the service`. This returns `{"diagnosis": {"e1": {"residual": 0.1}}}` through the same patched target list as the two failing diagnoses.
- The off-loop warning check is its own control. It requires the INFO `Resolved` line after the WARNING, so a run that only warned (m6) and a run that only resolved both fail it.
- For the census key: at `338b61e98`, before the receiver skip, `tests/entities.py` failed `every InputReader key is an options-flow entity field ...  [... reads keyed some other way: ['coordinator.py:1950 fd']]`. At the head it passes. `grep -rn "os\.read(" custom_components/heatpump_optimizer/` returns that one line only.

## Figures

- `ALL 4898 FEATURE CHECKS PASSED` at the head, against `ALL 4876 FEATURE CHECKS PASSED` at origin/main `7e8939d38`: the PR adds 22 checks. Of those, 12 are the earlier rounds' and 10 are this round's: the off-loop warning, the frame deadline's design value, the 50 MB and two-halves null controls, the stalled writer, the dead writer, readline, and the diagnose null control plus its two failures — `PYTHONPATH=tests/hastub python3 tests/features.py`
- `ALL 2632 ENTITY CHECKS PASSED`, including `ok   R10 N-log-flood barrier` — `PYTHONPATH=tests/hastub python3 tests/entities.py`
- `STRUCTURE RATCHET PASSED`, with no budget file touched — `python3 tests/structure.py`
- `MODE: SCOPED -- 26 script(s) run, 7 scoped out`, keyed on the mode line — `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$(mktemp -d)"`
- 50 MB reply round trip: `50000000 bytes in 0.15 s` on each of 3 runs at the head, under the shipped 1800 s and 60 s deadlines, so the frame deadline has about 400x headroom. Null control on origin/main `7e8939d38`, which has no frame reader: `0.08 s` on each of 3 runs. The probe is scratch, `probe50.py` (sha1 `16578527aed32a817f685f3ab33ca5362a258ddd`), and calls `_run_in_process(bytes, (50_000_000,))` three times after a warm call. The committed check pins only `< _REPLY_FRAME_TIMEOUT_S`, not the time.
- mutation sites: `PIN KILLED: 10 pinned, 4 left unpinned` on the first run. The 4 were: the dropped clamp (deleted); the end-of-stream guard (timed out, then made killable by `b25c7084c` and pinned); and the two readline sites (pinned by the new readline check). Later runs read `2 pinned, 1 left unpinned (1 survived)`, which is the equivalent `CMP_BOUND` triaged below. `--list CMP_BOUND` then shows it `pinned` — `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py --jobs 3`
- toolchain: numpy 2.5.4 and scipy 1.18.1, equal to `tests/requirements-ci.txt`; `cloud-setup.sh --check` reads OK (venv-ci's python3) — `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'`
- the 1800 s deadline rests on the contributor's solve-time spread from one install's recorder (median 18 s, max 426 s), which cannot be re-derived in tree. The design-value check pins its band, 4 x 426 s <= deadline <= 30 min. The 60 s frame deadline is pinned by `the reply frame deadline stays at its 60 s design value`. That check encodes a design choice: changing the value means changing the check.

## Unpinned sites

None. Every site this round's diff adds is either pinned by a `tests/features.py` kill under `tests/mutation_ledger/killed_by/` or triaged:
- killed: `@module.CONST.cb651c79` (`_REPLY_FRAME_TIMEOUT_S`), `_frame_reader.RETURN_DEL`, `_frame_reader.read` CMP_BOUND, GUARD_OFF x2 and RETURN_DEL, `_frame_reader.readline` BOOLOP and RETURN_DEL, `_read_reply` GUARD_OFF and RETURN_DEL, `_run_in_process.RAISE_DEL.d876a130`, and `services.py/handle_diagnose_interval.GUARD_OFF.7beb0a59`.
- triaged equivalent: `survivor_triage/coordinator.py/_frame_reader.read.CMP_BOUND.fb715113.json`. The mutant turns `left_s <= 0` into `< 0`, which differs only at a remaining time of exactly 0.0. Even then the outcome is the same: a poll that returns at once, then a negative remainder on the next pass. The mutation table drove it and reported `lives`.

## Red checks

- The final head has not run CI yet, so no concluded red exists at `9a54629e1`.
- At the previous head `6e048afc6`, verdict/3232 read every check-run page. The only non-success, non-skipped checks were `gate` x3, which aggregates the others, and `codeql / Analyze (python)`.
- `codeql / Analyze (python)` was **cancelled**, which is not a result about the diff. The cause, from its job log (`ev/codeql-python.log` on `refs/heads/probe/rev-3232-e3ffee93`): the job ran from 05:50, reached `codeql database finalize` at 06:15:37, and ended `##[error]The operation was canceled.` at 06:35:02. The job is capped at `timeout-minutes: 45` in `.github/workflows/codeql.yml`, so the CodeQL analyzer hit its 45-minute job limit in the finalize/analyze stage. **It needs a re-run.** The new head starts a fresh one, but a re-run is still owed if it cancels again. A cheaper detector than CI is not available: the cancel depends on analyzer wall time on the runner CI draws, not on anything in this diff. The gate's `FAIL codeql / Analyze (python): cancelled` is that same cancel.
- `tests / fast`, `mutation`, `coverage`, `replay`, `closures`, `arch-instrument` and `instrument-self-tests` all concluded success at `6e048afc6`.
- Reds in this branch's ancestry, all at `e80a319c2` (run 42135610131, the re-author head before round 2). Each was answered in round 2's body, and the round-2 head `6e048afc6` concluded success on every one:
  - `tests / fast (3.14)`: `tests/entities.py` failed `R10 N-log-flood barrier` (`1 of 2632 ENTITY CHECKS FAILED`, verdict/3232's run), fixed by the held `_await_optimize` warning. The cheaper detector exists: run `tests/entities.py` locally before the handoff, about 9 minutes. This round ran it at the final head (`ALL 2632 ENTITY CHECKS PASSED`).
  - `tests / mutation` and `tests / mutation-autofix`: the autofix log read `mutation-autofix: skip-measure-failed -- THE REPAIR DID NOT HAPPEN ... Pin the new sites yourself`. That head left its added sites unpinned. The cheaper detector is `tools/pr/prepr.sh` step 6d before the handoff. This round's sites are all pinned or triaged (`## Unpinned sites`).
  - `tests / replay`: `cycle_cost ... runner class unknown: ref_ms 27.26 lies in no band of COST_RUNNER_CLASSES`. That is a runner-calibration gap in the instrument, not caused by this diff. No cheaper detector exists for this PR, because it depends on which runner CI draws.
  - `governance / delivery-status` and `tests / nightly-status`: these grade `main`. The red was other PRs' OVERDUE rows and the nightly's own state. This diff's only file they read, `dev/programme/delivery/3232.md`, is the orchestrator's row for this PR. Both concluded success at `6e048afc6`. No cheaper detector exists here.
- Code-scanning alerts cannot be read from this seat (HTTP 403 at earlier rounds); `pr-contract` lists any.

## Forward-carry

none

## Friction

- arch-score-plant: cost: `tests/arch_score.py` again left `$RUNNER_TEMP/base` behind, a worktree of its deleted temporary plant repo. The next run then failed `FAIL arch-score.yml: a head edit to tests/structure.py is not what the gate loads (the #2068 plant)  [fatal: '<RUNNER_TEMP>/base' already exists`, and prepr.sh refused `closures ... failed while being recorded: tests/arch_score.py (exit 1)`. Removing the directory made the next prepr run clean. This is the same friction round 2 recorded. Carry: dismissed: tooling outside this PR's scope, recorded again for the orchestrator's friction triage
- mutation-pin-hang: cost: a mutant that turns a bounded loop into an infinite one (m10 before `b25c7084c`) is reported `timed out`. That is indistinguishable from a slow driver, even though the run proved the mutant never terminates. A raised `--timeout 3000` timed out the same way. Carry: dismissed: the cure here was a sounder loop (an explicit deadline), not a tooling change; recorded for the orchestrator's friction triage
- seat-identity: contradiction: the payload's setup line pins `git config user.name seat` / `seat@users.noreply.github.com`, while its brief asks for the `hpo-fixer` identity with the noreply address. The session environment authored every commit as `seat` <seat@users.noreply.github.com> even after a local `hpo-fixer` config, so this round's commits match the setup line and the earlier seat commits. Carry: dismissed: payload wording for the orchestrator to settle, no code consequence
