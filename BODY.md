Part 2 of R10-FLY-TRAIN-DEFAULTS: the folded after-merge bookkeeping (R10-FLOW-POSTMERGE, R10-FLY-RECORD-BEAT), the CARRIED HEAD refusal (P96), the spool drain order (P312), the CI-review wait (P331) and the standing-merge.md statement (P330). Policy files changed (standing-merge.md, nudge.md): merges on the owner's approving review. Closes none.

Carries of the brief, each answered in this diff:
Carry 1 (part 2 and P312): the after-merge bookkeeping is `postmerge.py`/`record_beat.py`, run by `merge_pr.sh` and the train's landing; the spool drains `--priority`, then critical-path, then arrival (HOTFIX-first control in merge_train.py's self-test).
Carry 2 (P330): standing-merge.md's Instruments paragraph states the train-join rule, within its cap, no raise.
Carry 3 (P92): `set-stage owed <GROUP> <sha>` with the group from `record_beat.resolve_group` (equality, then resume.pr, else no-group); printed only when the roster sync fails (a departure, disclosed above). Mutants record_beat-2 and the R9-FR-1/R9-FR-10 style fixture pin it.
Carry 4 (P331): review_settle time-bounded and policy_refusal arm 2, fixtures for the #3031 and #3039 shapes and the null parks.
Carry 5 (the brief's remaining sub-carries): all in the sections above.

## Head

17b38f7d9884ebab41561a5dfe2cdea768f939f2

## Mutation proof

- `merge_pr.sh`: comparison made unconditional (`true && return 0`) fails "a verdict for another head refuses CARRIED HEAD and posts nothing"; deleting the postmerge line fails the two postmerge arms.
- `merge_train.py`: drain key replaced by `0` fails both P312 arms; the settling run check forced true fails "P331 (2) null: the run ended long ago".
- `r10_seat_selftests_mutants.py postmerge-1 postmerge-2 record_beat-1 record_beat-2 S10`: RESULT survivors=0.

## Null control

Equal verdict SHA posts as today; no priority and nothing critical keeps arrival order; a concluded review run is not waited for; a run ended long ago parks as before; a clean postmerge run owes nothing and closes nothing.

## Figures

- `python3 -I tools/audit/seat/merge_train.py --self-test`: 396 checks, 0 failed
- `bash tools/audit/seat/merge_pr.sh --self-test`: 22 checks, 0 failed
- `python3 -I tools/audit/seat/postmerge.py --self-test`: 16 checks, 0 failed
- `python3 -I tools/audit/seat/record_beat.py --self-test`: 16 checks, 0 failed
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `python3 tests/entities.py`: ALL 2493 ENTITY CHECKS PASSED; `python3 tests/harness_headers.py`: 112 passed
- `node tools/policy/policy_lint.mjs --budgets`: standing-merge.md within its cap, no raise
- origin/main moved to a7dd7f50d during the work; merged (no conflict); prepr.sh run on the merge head, its two body refusals (carry routing) repaired and re-checked by --body-check and ci_predict.

Not as written in the brief: the `set-stage owed <GROUP> <sha>` line prints only when roster_sync fails, not after every merge. The tick-finder control is a full-sha substring test, not a run of the tick's code. `r10_main_gate_replay.py` reads live GitHub and read the same with and without --pending; it exercises code this diff does not change. Main's suite state is read through `merge_train.py classify --main` (no third rule). No ledger-event writes beyond postmerge-owed open/close.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Policy files changed: `dev/governance/roles/standing-merge.md` (P330's train-join statement, within its cap) and `dev/governance/roles/nudge.md` (step 12 cut to its exceptions). Owner approval is pending: this pull request merges only on tvofi's approving review at its head (or mandate 6329234399, scope all). This seat claims none.
