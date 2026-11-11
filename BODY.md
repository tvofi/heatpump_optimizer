Residue of R10-PREPR-CAP and R10-FLY-CIPREDICT-RESTORING on the pre-open prediction seam. This head lands carry 4 (the `.gitignore` anchor, pinned by `tests/gitignore_config.py` with a root-level `config/` null control) and carry 6's reproduction attempt as a re-runnable harness. Brief carries are 0-based; `Carry N` below is 1-based, one more than the brief's number. Every carry other than the brief's 4 and 6 is not built in this part.

Status by roster index (1-based): carry 5 landed in this head; carry 7 is dismissed below; untouched in this part: carry 1; carry 2; carry 3; carry 4; carry 6; carry 8; carry 9; carry 10; carry 11; carry 12; carry 13; carry 14; carry 15; carry 16; carry 17; carry 18; carry 19; carry 20; carry 21; carry 22; carry 23; carry 24.

## Head

b6c080dbcc6cd2294e3ae0913a2c818670749566, measured with `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` (PRE-PR rc=0) at origin/main d08ed31049cd.

## Mutation proof

Carry 4: reverting the `.gitignore` anchor to the unanchored `config/` rule turns `tests/gitignore_config.py` red (check-ignore then ignores the tracked nested `dev/audit/config/` path). Carry 6 adds no production change, so it has none.

## Null control

Carry 4: `git check-ignore` still ignores a root-level `config/`. Carry 6: `python3 dev/audit/harnesses/prepr_slot_nested.py` with all four slots held by live pids; the bare nested self-test and a direct `slot-take` are both unfinished at their bound, so the pool is genuinely full.

## Figures

- `python3 dev/audit/harnesses/prepr_slot_nested.py` at b6c080dbc: labelled_rc=0, labelled_real_slot_lines=0, labelled_queued=0, bare_finished=0, direct_take_finished=0 (the labelled nested self-test completed in about 7 minutes without queueing).
- `python3 tests/gitignore_config.py`: carry 4's pin.

## Red checks

none. Main's `tests / fast (3.14)` and `governance / instrument-self-tests` reds are known and not on this branch (fixed by #3466 and #3474).

## Forward-carry

- PREPR-SLOT-LIVELOCK: Carry: dismissed: not reproduced under dev/audit/harnesses/prepr_slot_nested.py at b6c080dbc

## Friction

none
