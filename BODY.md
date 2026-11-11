Residue of R10-PREPR-CAP and R10-FLY-CIPREDICT-RESTORING on the pre-open prediction seam. This head lands carry 4 (the `.gitignore` anchor, pinned by `tests/gitignore_config.py` with a root-level `config/` null control) and carry 6's reproduction attempt as a re-runnable harness. Carries 0-3, 5, 7-23 are not built in this part.

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

- Carry 6 (PREPR-SLOT-LIVELOCK): Carry: dismissed: not reproduced under dev/audit/harnesses/prepr_slot_nested.py at b6c080dbc
- Carries 0-3, 5, 7-23 of the brief (body-check parity, HEAD-ONLY detector, harness_headers inline scan, INERT-import label, receipt carry and Prepr-absent reason, step elapsed seconds, 6d premise, roster-ref fallback, hotfix scope, carry_audit landed rule and own-group resolution) were not started in this seat. Carry: R10-PREPR-RESIDUE

## Friction

none
