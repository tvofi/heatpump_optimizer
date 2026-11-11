Residue of R10-PREPR-CAP and R10-FLY-CIPREDICT-RESTORING on the pre-open prediction seam. This head lands carry 4 (the `.gitignore` anchor, pinned by `tests/gitignore_config.py` with a root-level `config/` null control) and carry 6's reproduction attempt as a re-runnable harness. Brief carries are 0-based; `Carry N` below is 1-based, one more than the brief's number. Every carry other than the brief's 4 and 6 is not built in this part.

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

- Carry 1 (the brief's carry 0): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 2 (the brief's carry 1): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 3 (the brief's carry 2): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 4 (the brief's carry 3): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 5 (the brief's carry 4, the .gitignore anchor): landed in this head, pinned by tests/gitignore_config.py. Carry: dismissed: landed in this head
- Carry 6 (the brief's carry 5): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 7 (the brief's carry 6, PREPR-SLOT-LIVELOCK): Carry: dismissed: not reproduced under dev/audit/harnesses/prepr_slot_nested.py at b6c080dbc
- Carry 8 (the brief's carry 7): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 9 (the brief's carry 8): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 10 (the brief's carry 9): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 11 (the brief's carry 10): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 12 (the brief's carry 11): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 13 (the brief's carry 12): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 14 (the brief's carry 13): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 15 (the brief's carry 14): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 16 (the brief's carry 15): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 17 (the brief's carry 16): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 18 (the brief's carry 17): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 19 (the brief's carry 18): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 20 (the brief's carry 19): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 21 (the brief's carry 20): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 22 (the brief's carry 21): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 23 (the brief's carry 22): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE
- Carry 24 (the brief's carry 23): not built in this part; the seat stopped after carries 4 and 6. Carry: R10-PREPR-RESIDUE

## Friction

none
