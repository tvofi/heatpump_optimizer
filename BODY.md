Quiet train output by default (owner card 2026-10-24, carry 0) and `pr_bounded` in the 12 seat self-tests that lacked it (carry 1). Repair round: the first review blocked the keep-list filter for hiding key lines.

## Head

d3e955485a25d93a24f3610cea9b44b5918e7b00

## Mutation proof

Quiet now hides only the nine named shapes in `QUIET_CHATTER` (merge_train.py) and prints every other line, so the per-car merge, post-merge OWED, failing-check, serial/dropped, STALE/OVERLAP/REJOIN and `SKIP #<pr> <phase>:` lines all show. Each mutant below run against `python3 tools/audit/seat/merge_train.py --self-test` (baseline 0 failed); every one is killed:

- `wire_quiet(a, opts)` call in `main` replaced by `pass`: 1 failed.
- `TRAIN_VERBOSE` branch dropped from `wire_quiet`: 1 failed.
- stop flush made unconditional (`if "TRAIN STOPPED" in m:` to `if True:`): 2 failed.
- chatter predicate to `if False:` (nothing hidden): 13 failed.
- chatter predicate to `if True:` (everything hidden): 29 failed.
- one chatter member removed: 1 failed.
- tail bound removed: 2 failed.
- a chatter member changed to `SKIP ` (hides SKIP lines): 4 failed.

## Null control

A seeded stop through `main` (a stub `Train` that logs a merge, an OWED line, a SKIP, a `ci red=` line, then `TRAIN STOPPED`, returns 1) is run three ways: default quiet, `--verbose`, `TRAIN_VERBOSE=1`. The self-test measures that all three return rc 1, that quiet prints the merge, OWED, SKIP, failing-check and stop lines with the held chatter as `  | ` tail ahead of the stop, and that both verbose modes print the unfiltered stream and write no `train-full.log`. 24 real key-line spellings each print in quiet; each of the nine chatter members hides its own sample. The SKIP line stays on stdout, so `train.log` still feeds `merge_throughput`'s skip reader.

## Figures

`none`

Functions touched in merge_train.py: new `QUIET_CHATTER`, `quiet_log` and `wire_quiet` (before `class Train`), `_parser` (one `--verbose` flag), `main` (one `wire_quiet` call), and the post-approval self-test block. No logic of `Train` is edited. The 12 scripts take one line each at their `--self-test` entry: `[ -n "${PR_BOUND:-}" ] || { . pr_args.sh; pr_bounded NAME bash "$0" --self-test; }`.

Scope kept to the brief's "output calls only in merge_train.py": update_pr.sh and open_pr.sh are not changed in this round.

## Red checks

The reds below are on commits already on main that this branch inherits; none is in the owed-reds set (`merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`), and this diff touches no file they read beyond the seat scripts. Each is answered by the finding that no cheaper detector of this branch's own change exists, since the branch did not introduce it:

- `tests / fast (3.14)`: red on main ancestry, not on this diff.
- `governance / delivery-status`: red on main ancestry, not on this diff.
- `governance / instrument-self-tests`: red on main ancestry, not on this diff.
- `tests / nightly-status`: red on main ancestry, not on this diff.
- `tests / replay`: red on main ancestry, not on this diff.

## Forward-carry

none

## Friction

none

Merge repair: origin/main merged in; the one conflict, tools/audit/seat/merge_train.py, was resolved as the union of this branch's quiet-log block (QUIET_CHATTER, quiet_log, wire_quiet) and main's one_job_pulse/BASELINE_JOBS. merge_train.py --self-test 700 checks, 0 failed; prepr.sh rc=0 at the merged head.
