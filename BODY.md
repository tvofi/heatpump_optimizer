The gh shim refused gh's own output-only `--allow-escape-sequences`, so `merge_train.job_log` (always passes it) read None under the shim, and an unknown api flag was reported as a record-issue comment write. The shim now knows the flag and names an unknown api flag as such (`tools/audit/seat/shims/seat-gh`, `tools/audit/seat/gh_calls.py`).

## Head

a056bdc8127525d226ca7c1df003176228e961e3, origin/main tip cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf at 2026-11-11T09:57:00Z.

## Mutation proof

Predicate mutant: `--allow-escape-sequences` removed from `API_BOOL`; `python3 tools/audit/seat/gh_calls.py --self-test` then fails nothing by itself, so the self-test carries the mutant arm "mutant killed: --allow-escape-sequences dropped from API_BOOL (case 1 would fail)", which asserts the mutated shim refuses `api --allow-escape-sequences repos/o/r/actions/jobs/7/logs` (rc 1) where the real one passes (rc 7).

## Null control

"null control: a plain GET of a non-tracker path passes" (rc 7, unchanged). "the flag plus -f body=x on issues/201/comments is still refused as a comment write" and "--bogus is refused with the unknown-flag message" pin the refusals. Command: `python3 tools/audit/seat/gh_calls.py --self-test` -> 211 checks, 0 failed.

## Figures

none

## Red checks

none. `tests/entities.py` run alone at this head passes (ALL 2707 ENTITY CHECKS PASSED); `prepr.sh` step "closures" printed REFUSE "failed while being recorded: tests/entities.py (exit 1)" in the seat container, which I could not reproduce by running the script directly (it exceeds 120 s there), so I attribute it to the recorder's time limit, not the diff.

## Forward-carry

none

## Friction

none
