# R10-RCA-ENTITIES-MACOS: `tests/entities.py` ends at the stdlib sampler on a macOS seat host

The root-cause record for a recurring seat-reported defect: run locally on the
macOS seat host, `tests/entities.py` raised `PermissionError: Cannot get task
port` at module level in `_hb_stdlib_reads` and ended there. Every check past
that line went unrun in every local scoped gate that selected the script, and
three real reds there reached CI before anyone saw them. Group:
`R10-FLY-SUITE-ENV-FLAKES` (roster files include `tests/entities.py`; its brief
already owns macOS-only reds in the same heartbeat checks). Measured
2026-11-01 at merge base `61b0076f48546fe29cae35dfdb5949ad6d0c6feb`, host
Darwin 27.2.0, seat venv Python 3.14.7.

## 1. Cause

`120cd1bb6` (R10-FLY-NIGHTLY-HB, #2964, 2026-10-29) added a real sample of a
child process at module level in `tests/entities.py` (`_hb_stdlib_reads`,
line 18448 at the base). The sample is gated on
`find_spec("_remote_debugging") is not None`, which tests whether the
**interpreter** can unwind a remote process. The real precondition is whether
the **host** lets this process read its child. Linux allows that under Yama's
default `ptrace_scope` (the function's docstring reasons about Linux only),
and macOS does not: `task_for_pid` needs root or the
`com.apple.system-task-ports` entitlement, even for the caller's own child.
Reproduced in isolation: `RemoteUnwinder(<child pid>).get_stack_trace()` raises
`PermissionError("Cannot get task port for PID … (kern_return_t: 5)…")`.

Raised at module level, the error ends the script. Two properties of the suite
then made it look like any other red:

- `tests/run.sh` reports a script that ended before its summary line the same
  way as one that failed a check (`1 TEST SCRIPT(S) FAILED`).
- A green `tests/entities.py` prints 50 `FAIL` lines from planted controls (50
  in the green run below), so a seat cannot tell a real red from FAIL lines.

## 2. Process state: (d), the precondition changed underneath

The process is the local scoped gate in `gate-scoping.md` and `fixer.md`: run
the scripts `closure.py select` names before the handoff. Every instance below
followed it. Each seat ran `tests/entities.py`, saw it end, and reported that
in its body. Before `120cd1bb6` the script finished on this host, and its known
macOS reds (`hb:positive_control`, the BSD `wc -l` padding, in this group's
brief) still ended in a summary line. The process relied on one precondition,
that a selected script runs to its summary on the seat host, and `120cd1bb6`
broke it. Nothing in the gate noticed, because a crash reads as a red. This is
not (b): the seats did what the process said. It is not (a): the check existed
and ran on CI. So the countermeasure is not a firmer instruction.

## 3. Class search

- `grep -n "/proc/\|ptrace\|geteuid\|_remote_debugging\|sys.platform"
  tests/entities.py`: the only real sample of another process is this site.
- `grep -rln "RemoteUnwinder\|_STDLIB_SAMPLE\|_remote_debugging" tests tools
  custom_components`: `tests/entities.py` and `tests/nightly_ha.py`. The second
  samples inside the heartbeat container, which is given `SYS_PTRACE`, on
  Linux, and never on the seat host.
- What reaches wider than this site is the shape: any module-level exception
  that depends on the host ends a single-file suite at that point, and
  `run.sh` cannot tell that from a red. That part is carried, not built here
  (section 6).

## 4. Cost test

**How much was skipped** (this host, seat venv,
`PYTHONPATH=tests/hastub python3 tests/entities.py`):

| run | result | `  ok ` lines | wall-clock |
|---|---|---|---|
| base `61b0076f4` | rc=1, traceback at line 18448, no summary | 1486 | 75 s |
| fix `5acd75eec` | rc=0, `ALL 2495 ENTITY CHECKS PASSED`, one named `SKIP` | 2535 | 621 s |

So 1049 of 2535 `ok` lines (41 %) never ran locally, along with 88 % of the
script's wall-clock and lines 18448 to 40639 (55 % of the file).

**How often** (since `120cd1bb6`, 2026-10-29 10:07Z, to 2026-11-01 04:15Z,
about 66 h). `gh pr list --state all --search "created:>=2026-10-29"` returns
134 PRs, and 19 of their bodies name `task port` or `_hb_stdlib_reads`:
#2997, #3005, #3006, #3016, #3022, #3024, #3026, #3038, #3047, #3048, #3049,
#3050, #3051, #3052, #3054, #3062, #3073, #3075 and #3078.

**Reds it hid.** Over those 19 PRs, every failing `tests / fast` check-run was
pulled (12 jobs). Each job's FAIL names were diffed against the green run's
planted-control names. Three PRs, five jobs, had a real `tests/entities.py` red
past line 18448, which the local run could not reach:

| PR | head(s) | the red | line |
|---|---|---|---|
| #3022 | 2d58f010b | R10 N-log-flood barrier (`_void_heat_loss_learners`) | 40437 |
| #3047 | e2b12a171, 4a593ba9b (3 jobs) | R10 N-log-flood barrier (`async_factory_reset`) | 40437 |
| #3078 | df35202ab | `debug replay: trim_replay carries sparse export attributes forward` | 39213 |

#3016's entities red (line 16488) sat before the sampler and was visible
locally, so it is not counted.

**Cost per hidden red**, measured on #3078: red run 41269647846, 03:33:25Z to
04:03:59Z (30.6 min; its `fast` job 03:34:18Z to 03:47:22Z), plus the seat's repair and re-handoff, with the next CI at 04:08:43Z.
That is about 35 min to the next CI start. The CI cycle the repair then needs
(about 30 min) would not have existed had the red been found locally. Call it
about 51 min (3060 s) per hidden red, on the critical path to merge. Over 19
instances with 3 hidden-red PRs (#3047 took two heads), that is 4 × 3060 s =
12240 s, or about 644 s per instance. On top of that, every instance paid seat
time to work around the crash: #3054 ran base and head twice each at 75 s and
diffed the name sets, #3047 and #3078 extracted and ran slices, and #3016 built
a scratch 3.13 venv. That is at least 150 s per instance (#3054's two runs),
not counted above.

**Cost of the countermeasure**, standing: 0 s on Linux, where the path is
unchanged. On macOS each local run of `tests/entities.py` now takes about
546 s longer, because the remaining checks run. That is the cost the scoped
gate already assigns the script, and CI pays it on every PR. The defect had
made the local run artificially cheap, and the fix restores the cost rather
than adding a new one. Even counted in full: 546 s < 644 s + 150 s per
instance, and the 546 s run in a background gate while the 3060 s sat on the
merge path. **Build.**

## 5. Countermeasure (built): a named SKIP, and the script runs on

`tests/entities.py`, `_hb_stdlib_sampling`: the sample of the spinning and idle
child is taken through one seam. A `PermissionError` on `darwin` returns
`(None, "darwin: <message>")`. Off darwin it re-raises, so CI's Linux run is
unchanged. The call site prints
`  SKIP the stdlib sample of a real spinning process reads as the spin to the control  [darwin: Cannot get task port …]`
and the script continues. The skipped check is not counted, so a macOS total
reads one below CI's.

**Failing test first.** Commit `aa2afb9b1` added three checks against the seam
with the base behaviour, where the error escapes. On this host the first check
FAILs (`['PermissionError']`) and the script still ends at the real sampler.

**Detects the defect it is for.** One planted `R.check(..., False)` before the
final `sys.exit`, run on this host:

- at the base `61b0076f4`: rc=1, `PermissionError` at line 18448, no planted
  FAIL line, so the red is hidden;
- at the fix `5acd75eec`: rc=1, the named `SKIP` line, `FAIL planted red past
  the macOS sampler  [planted]`, and `1 of 2496 ENTITY CHECKS FAILED`, so the
  red is seen.

**Mutation proof.** `python3 dev/audit/harnesses/r10_rca_entities_macos_seam.py`
cuts the seam and its checks verbatim from the file and runs them against a
stub `R` in milliseconds on any host:

- head 0 FAILs;
- M1 (no catch) 1;
- M2 (Linux denial skipped) 1;
- M3 (any error skipped) 1;
- M4 (skip with no reason, which would fall through to the no-unwinder arm and
  pass silently) 1.

One unpinned edit is known: deleting the call site's `print` hides the skip's
name, but it does not end the script or change the count.

**Null control (Linux).** No container runtime on this host. By construction,
a read that succeeds returns `(samples, None)` to the same branch as before,
and an interpreter without an unwinder takes the same `else` branch. M2 pins
the off-darwin re-raise. CI's `tests / fast (3.14)` on this head is the run: it
must print `ok   the stdlib sample of a real spinning process reads as the
spin…`, and no `SKIP` line.

## 6. Carried, not built

The process-noticing half of (d): `tests/run.sh` should report a script that
exits without its summary line (`ALL N … PASSED` or `N of M … FAILED`) as
`ENDED BEFORE ITS SUMMARY`, separate from a red. Then the next host-dependent
module-level exception in any suite file is named the first time. Standing
cost is one read of the script's last line, a few milliseconds. It touches
the gate itself, which forces `MODE: FULL` on its PR, and it is a separate seam
from this one. Carry: `R10-FLY-SUITE-ENV-FLAKES`.
