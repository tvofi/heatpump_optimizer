Quiet train output by default (owner card 2026-10-24, carry 0) and `pr_bounded` in the 12 seat self-tests that lacked it (carry 1).

## Head

38aee2235ae2dbc72ef1023e5baa27b8ffa1d619

## Mutation proof

In `quiet_log` (merge_train.py) the predicate `if not KEY_LINE.match(m):` replaced by `if False:`; `python3 tools/audit/seat/merge_train.py --self-test` then prints `FAIL quiet log: chatter is not shown until a stop` and `FAIL quiet log: a stop shows the failing step's tail, bounded, then itself` (2 failed). Restored, 0 failed.

## Null control

Unmodified tree: no quiet log exists, `merge_train.py batch` prints every progress line. With `--verbose` or `TRAIN_VERBOSE=1` that stream is unchanged (the parser check pins the flag off by default; the log callable is injected only when neither is set), so exit codes agree across modes by construction: only the `log` callable differs.

## Figures

`none`

Functions touched in merge_train.py: new `quiet_log` and `KEY_LINE` (before `class Train`), `_parser` (one `--verbose` flag), `main` (the batch/run log injection), and `_self_test` (four checks). No logic of `Train` is edited. The 12 scripts take one line each at their `--self-test` entry: `[ -n "${PR_BOUND:-}" ] || { . pr_args.sh; pr_bounded NAME bash "$0" --self-test; }`; the self-tests of ci-watch, cloud-setup, delivery_row, failure_logs, handoff_push, heartbeat, seat_venv, tick_loop ran rc 0 after the edit.

Scope kept to the brief's "output calls only in merge_train.py": update_pr.sh and open_pr.sh already send the pusher's output to a log and print only its key lines, so they are not changed.

## Red checks

none

## Forward-carry

none

## Friction

none
