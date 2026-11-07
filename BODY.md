R10-HANDOFF-PATH part 2 (r10-handoff-path-p2): pr_args.sh resolves its own directory once at source time; open_driver.py stem escape, guarded log read and a STUCK line after three tries. Part of #201.

## Head

Measured at the merge of origin/main a37c58e5f into the code commit 1e994e484 (head 2a8a3e338751cfd1cf10ae2305d9062591378fdf). origin/main moved after the first prepr run, so main was merged and prepr rerun on this head.

## Mutation proof

- `mut:argsdir` (the PR_ARGS_DIR line of pr_args.sh deleted): `bash tools/audit/seat/pr_args.sh --self-test` goes red on "sourced by a relative path from a fresh clone, then cd'd into a stale sibling, passes" and "update_pr: run by a relative path from a fresh worktree ... passes the freshness check" (both mutant arms refuse as STALE CHECKOUT).
- `python3 -I dev/audit/harnesses/r10_open_driver_mutants.py`: 22 mutants, survived=0, M0 null-ok. New: M-escape (drops the percent escape), M-maxtries (retries forever), M-stuckowed (OWED instead of STUCK); M-bo-*, M-open-stem, M-reap-* and M-launch re-anchored to the new text.

## Null control

The unmodified pr_args.sh refuses the relative-path arms (same self-test, mutant arm); the null arm "the same clone made stale refuses STALE CHECKOUT" stays red-on-stale. Two failed opens print OWED, not STUCK; `r10-plain` launches as before; a new sha for a stuck topic launches again.

## Figures

- `bash tools/audit/seat/pr_args.sh --self-test`: 0 failed (the new arms A, B, C and their mutants included).
- `python3 -I tools/audit/seat/open_driver.py --self-test`: 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh`: rc=0 on the code commit before the merge of main.

## Red checks

none

## Forward-carry

State of each carry (0-based) of the part-scope carry 17:

- Carry 7: built. PR_ARGS_DIR beside PR_FRESH_PATHS; pr_tools_fresh, pr_pushers and the self-test read it. Arms: fresh clone sourced by relative path then cd to a stale sibling passes; the same clone made stale refuses; mutant argsdir red. Carry: R10-HANDOFF-PATH
- Carry 16: built, same change. Arm runs update_pr.sh by a relative path from a fresh worktree whose common checkout is behind origin/main: passes the freshness check; mutant refuses. update_pr.sh and open_pr.sh untouched. Afterwards the dispatch seat drops HPO_ALLOW_STALE_TOOLS=1 from its update scripts. Carry: dispatch seat (drop the override). Carry: R10-HANDOFF-PATH
- Carry 10: built. stem() escapes the percent sign before the slash; per-topic files are t-<stem>.log/.rc so topic open-driver cannot overwrite open-driver.log; the hostile-topic log read is guarded (a missing file reports FAIL). Carry: R10-HANDOFF-PATH
- Carries 11 and 15: built. After the retry limit open_driver.py prints one `STUCK <topic> <sha8> rc=<n> <reason>` line per pass (prefix read by the OPENER regex in beat_jobs.py, unchanged). Choice stated: the design's backoff (30 min) replaced the 5-minute start; waits 30 min, 60 min; three runs at most; then STUCK instead of the OWED line; a new sha starts fresh. Carry: R10-HANDOFF-PATH
- Carry 5: already built at the merge base; verified by arms "failed open not marked seen", "backoff holds the retry", "retry after backoff" (all green). No gap. Carry: R10-HANDOFF-PATH
- Carry 14: already built at the merge base; verified by arms "sav-comfort-p2" (suffixed topic) and "NEEDS-TITLE opens nothing" (null control). No gap. Carry: R10-HANDOFF-PATH
- Carries 0 to 4, 6, 8, 13 (update_pr.sh, open_pr.sh, prepr.sh reuse) and 12 (cloud_relay.sh): not in this part; they stay open on the roster. Carry: R10-HANDOFF-PATH.
- Before editing, the open PR set was checked by file list: none edited open_driver.py or pr_args.sh. Carry: R10-HANDOFF-PATH

## Friction

none
