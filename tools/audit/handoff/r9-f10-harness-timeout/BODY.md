<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

`tests/harness_headers.py` ran each live-header harness under a fixed 240 s wall timeout. `sysid_estimator_frontier.py` costs 100-143 CPU-s on one core, so the mutation pool's parallel load pushed it past 240 s of wall; the uncaught `TimeoutExpired` crashed the script and "killed" the comment-only null control, refusing the mutation table on #1808 twice. The bound is now CPU seconds (`RLIMIT_CPU` 240 s, load-independent, same hang detection for a spinning harness) plus a 900 s wall cap for an idle hang, below mutation_table.py's 1200 s driver timeout. A wall overrun is a reported failed check, not a crash. No barrier is lost.

## Head

Code head dd0f2ace379d08bb848b361275277688b4b8d017 (cut from main 0bfb8883).

## Mutation proof

Three new controls in `harness_headers.py`: an idle child past the CPU limit is not killed; a spinning child is killed at it (rc -24); an idle child past the wall cap returns 124. Reverting `run_bounded` to the old wall-only timeout removes all three and the crash returns (see Null control).

## Null control

Main at 0bfb8883, two copies of `tests/harness_headers.py` pinned to one core with `taskset -c 0` (same load shape as the pool): both crashed with `subprocess.TimeoutExpired ... sysid_estimator_frontier.py timed out after 240 seconds`, rc=1. The same two copies on this head: both `ALL 94 HARNESS HEADER CHECKS PASSED`, rc=0.

## Figures

- `time PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/round4/D7/sysid_estimator_frontier.py` printed 143 s real / 141 s user on this cloud box, unloaded.

## Red checks

none

## Forward-carry

none

## Friction

none
