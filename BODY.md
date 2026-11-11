Residue of R10-PREPR-CAP and R10-FLY-CIPREDICT-RESTORING on the pre-open prediction seam. This head lands carry 4 (the `.gitignore` anchor, pinned by `tests/gitignore_config.py` with a root-level `config/` null control) and repairs carry 7 (PREPR-SLOT-LIVELOCK): the first review blocked the dismissal because its null control could not fail; the harness is rebuilt with a discriminating bare arm and a real `take_slot` path. Brief carries are 0-based; `Carry N` below is 1-based, one more than the brief's number. Every carry other than the brief's 4 and 6 is not built in this part.

Status by roster index (1-based): carry 5 landed in this head; carry 7 is dismissed below with the discriminating controls named; untouched in this part: carry 1; carry 2; carry 3; carry 4; carry 6; carry 8; carry 9; carry 10; carry 11; carry 12; carry 13; carry 14; carry 15; carry 16; carry 17; carry 18; carry 19; carry 20; carry 21; carry 22; carry 23; carry 24.

## Head

79c063dcda07232b5773c4502a7c16af616fe4b3, measured with `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` (PRE-PR rc=0) at origin/main d08ed31049cd; main has since moved to 6cc15e9b and `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

Carry 4: reverting the `.gitignore` anchor to the unanchored `config/` rule turns `tests/gitignore_config.py` red. Carry 7: `python3 dev/audit/harnesses/prepr_slot_nested.py --mutant` deletes the `export HPO_SLOT_LABEL` line from the cut `take_slot`; the nested arm then queues (nested_finished=0, nested_queue_empty=0, outer_exported_label=0) and the harness exits 1.

## Null control

Carry 4: `git check-ignore` still ignores a root-level `config/`. Carry 7: the bare arm (the same nested `take_slot` call without the label, pool 4/4 held) is still waiting at its bound AND `slot-status` lists its ticket (`queue=prepr-741`, bare_queued=1); the labelled nested arm prints `heavy slot joined prepr-733`, finishes in 0.1 s and leaves `queue=-`. The two arms differ by a slot-status queue entry, not by a bound both miss. The harness never sets HPO_SLOT_LABEL itself: the outer shell runs prepr's real `take_slot` against the real `tests/gate_lock.py` with 3 of 4 slots held and exports the label on the take path (prepr.sh:4184). The WARN path (:4192, unusable lock dir) exports none and the nested call only warns, it does not queue (warn_no_label=1, warn_finished=1). Static control: prepr's `--self-test` branch holds no real `take_slot` call (selftest_branch_takes_slot=0), so the nested self-test cannot queue in any arm.

## Figures

- `python3 dev/audit/harnesses/prepr_slot_nested.py` at 79c063dcda07232b5773c4502a7c16af616fe4b3: verdict=ok; pool_full=1, outer_exported_label=1, nested_finished=1, nested_queue_empty=1, nested_joined=1, bare_finished=0, bare_queued=1, warn_no_label=1, warn_finished=1, selftest_branch_takes_slot=0.
- `--mutant`: verdict=FAIL, rc 1.
- `python3 tests/gitignore_config.py`: carry 4's pin.

## Red checks

none. Main's `tests / fast (3.14)` and `governance / instrument-self-tests` reds at a head lacking 6cc15e9b are inherited and cured by the remerge.

## Forward-carry

- PREPR-SLOT-LIVELOCK: Carry: dismissed: not reproducible, nested heavy steps join the outer slot (dev/audit/harnesses/prepr_slot_nested.py at 79c063dcda07232b5773c4502a7c16af616fe4b3)

## Friction

none
