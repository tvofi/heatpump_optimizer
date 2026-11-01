R10-FLY-SUITE-ENV-FLAKES (root-cause seat, R10-RCA-ENTITIES-MACOS): on the macOS seat host, `tests/entities.py` raised `PermissionError: Cannot get task port` at module level in `_hb_stdlib_reads` (line 18448 at the base) and ended there. As a result, 1049 of its 2535 `ok` lines never ran in any local scoped gate that selected it. That hid three real reds that only Linux CI caught: #3022, #3047 (two heads) and #3078. Now the denial is a named `SKIP` on darwin and the script runs on. Off darwin it still raises, so CI's Linux run is unchanged.

The record is `dev/audit/rca/R10-RCA-ENTITIES-MACOS.md`:

- the cause, `120cd1bb6`, which gates a real child sample on the interpreter's unwinder rather than on the host's permission to read a child;
- the process state, (d), with its evidence;
- the class search;
- the cost test, with measured numbers;
- the carried process-noticing half: `tests/run.sh` naming a script that ended before its summary.

## Head

`813c5ade7e091e069c3f021bc5c27a52a74855cb`. The `tests/entities.py` runs below were measured at `5acd75eec`. The two commits after it add only the RCA document, the seam harness (`dev/audit/`, INERT) and the one `tests/closures.json` INERT READS entry `ci_predict.py --apply-inert` wrote. The script's own text is the same at both.

## Mutation proof

`python3 dev/audit/harnesses/r10_rca_entities_macos_seam.py` cuts `_hb_stdlib_sampling` and its three checks verbatim from `tests/entities.py` and runs them against a stub `R`, with no real sample, so it works on any host. Each mutant turns exactly one check red:

- M1, the denial escapes (the base behaviour): FAIL `a macOS host that denies the stdlib sampler its child's task port skips that one check…` `['PermissionError']`.
- M2, a Linux denial is skipped: FAIL `null control: off macOS the same denial is no skip…` `(None, 'linux: Cannot get task port…')`.
- M3, any error is skipped: FAIL `null control: a sampler that reads is taken as before, and any other error is no skip`.
- M4, a skip with no reason, which would fall through to the no-unwinder arm and pass silently: FAIL on the first check `(None, '')`.

Head: 0 FAILs, `SEAM HARNESS OK`. Known unpinned: deleting the call site's `print` hides the SKIP line's name. It neither ends the script nor changes the count, so a macOS total stays one below CI's.

Failing test first: `aa2afb9b1` added the three checks with the base behaviour. On this host the first check FAILs (`['PermissionError']`), and the script still ends at the real sampler (rc=1).

## Null control

- Base `61b0076f4` on this host (macOS, seat venv 3.14.7): rc=1, traceback at line 18448, no summary line, 1486 `ok` lines, 75 s.
- Fix `5acd75eec`, same host: rc=0, `ALL 2495 ENTITY CHECKS PASSED`, 2535 `ok` lines, one `  SKIP the stdlib sample of a real spinning process reads as the spin to the control  [darwin: Cannot get task port …]`, 621 s.
- The detector detects: one planted `R.check(..., False)` before the final `sys.exit`. At the base it gives rc=1 at the sampler and no planted FAIL line, so the red is hidden. At the fix it gives `FAIL planted red past the macOS sampler  [planted]` and `1 of 2496 ENTITY CHECKS FAILED`, so the red is seen.
- Linux: no container runtime on this host. By construction, a read that succeeds returns to the same branch as before, an interpreter with no unwinder takes the same `else`, and M2 pins the off-darwin re-raise. CI's `tests / fast (3.14)` on this head is the Linux run. It must print `ok   the stdlib sample of a real spinning process reads as the spin to the control, and of the same process outside it does not`, with no `SKIP` line, and a total of 2496.

- The scoped gate (`MODE: SCOPED -- 2 script(s) run`; `prepr.sh` prints the mode, the seat runs the scripts): `tests/entities.py` as above. `tests/harness_headers.py` at this head on this host: `12 of 112 HARNESS HEADER CHECKS FAILED`. All 12 come from one harness, `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`: `rc=124 cpu=163.6s stderr=wall limit 900s exceeded`, 163.6 s of CPU against its 480 s bound, so the wall clock ran out at a load average of about 100 on this host. Its 11 RESULT lines then read `printed=None`. This diff touches neither that harness nor anything it reads, and the new harness is not among the failures. CI's Linux run is the authority for it.

## Figures

- `python3 dev/audit/harnesses/r10_rca_entities_macos_seam.py | tail -1` -> `SEAM HARNESS OK`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py | tail -1` -> `ALL 2495 ENTITY CHECKS PASSED` (macOS, at `5acd75eec`).
- `python3 tests/structure.py | tail -1` -> `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff 61b0076f4` -> `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`).
- `python3 tools/pr/ci_predict.py --base origin/main | tail -1` -> `CI PREDICT: no closures, fast, governance or instrument red predicted against 61b0076f4854 (a data-file read is not seen)`.
- Cost test: 19 of 134 PRs opened since 2026-10-29 name the crash. Their 12 failing `tests / fast` jobs hold 5 real entities.py reds past line 18448, in 3 PRs. Each costs about 3060 s on the merge path, against 546 s added to a local macOS run. The enumeration and per-PR table are in `dev/audit/rca/R10-RCA-ENTITIES-MACOS.md` section 4.

## Red checks

`none` on this branch.

## Forward-carry

- `tests/run.sh` reports a script that exits without its summary line (`ALL N … PASSED` or `N of M … FAILED`) the same as a red. It should name it `ENDED BEFORE ITS SUMMARY`, so that the next host-dependent module-level exception is seen the first time. Standing cost: one last-line read per script. It touches the gate, which forces `MODE: FULL`, and it is a separate seam. Carry: R10-FLY-SUITE-ENV-FLAKES

## Friction

`none`
