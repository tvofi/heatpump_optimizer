Fix review: merge 068074f0f2c2dfdb57fc1821ed39f3510bc913ed

bus-nonce: 33060221363e5d90867eaaf06c323bf8

## Scope

This is review round 2. The previous verdict blocked 38e3d17e7dd2161627d178a332f6fa1b9b557b19 on `mutation-survivors`. As the owner's 2026-11-09 scope ruling requires, I reviewed only `git diff 38e3d17e7dd2161627d178a332f6fa1b9b557b19 068074f0f2c2dfdb57fc1821ed39f3510bc913ed`. That diff adds 197 lines to `tests/features.py` and 46 new `tests/mutation_ledger/` rows. It changes no `custom_components/` line, so the scope exception does not apply. The fourth-round re-cut rule does not apply either.

## Evidence

- RESULT previous block, the 14 `pump_arbiter.py` survivors: settled. I applied each mutant alone and ran it against an extraction of the R10-WATER-SETPOINT-FEEDBACK block: `tests/features.py` lines 1-107, plus 60660-60764 (the `_PaNS` and `_PA_AUTO` helpers), plus 81525 to the end. The baseline is `ALL 35 FEATURE CHECKS PASSED`, rc 0 (`ev/r10_block_baseline.log`). Mutants killed: 260, 276 and 279 CONST; 920, 922, 930, 934 and 953 CMP_BOUND; 926 RETURN_DEL; 997 CMP_BOUND; 997 GUARD_OFF; 1000 CLAMP_DROP; 1019 CMP_BOUND at both ends. Each fails at least one check (`ev/mutants.txt`; driver `ev/mut_driver.py`, built by this reviewer).
- RESULT the previous reviewer's own survivors: both killed. G (`rec.cut_lo_c` dropped from the lows) fails 1 check, and so does J (the start hold keeps `sent_c`). G was the gap on the parameter-979 lower side; the new 26.4 degC minimum-return replay and the bounds check now close it.
- RESULT 1022 CMP_BOUND (`value >= rec.prev_c`): survives all 35 checks in my run, matching the body. It is triaged `equivalent` at `tests/mutation_ledger/survivor_triage/pump_arbiter.py/_clamp_cut.CMP_BOUND.8aa01955.json`. I checked the triage independently. Under `custom_components/`, `prev_c` and `sent_c` are assigned only at `pump_arbiter.py:310-311` (both default `None`), `:935` and `:1026` (both set `sent_c=None`), and `:985-986`. The `:985-986` assignments in `_note_sent` run only after its early return on `recorded[0] == out`. So whenever `sent_c` is set, it differs from `prev_c`, and `value == sent_c` never equals `prev_c`. The mutant is equivalent.
- RESULT body correction: the false "pinned by `mutation-autofix`" disposition is withdrawn and labelled a correction under `## Unpinned sites`. Its enumerator, `git diff --name-only --diff-filter=A b0762725...068074f0 -- tests/mutation_ledger/`, re-derives to 45 `killed_by` rows and 1 `survivor_triage` row. By commit: 32 from a550c3cac, 13 from 4a927eed7 and 1 from d4b4eff32 (`ev/ledger_delta.txt`). The body's `git grep` count of 11 `sent_c`/`prev_c` lines matches: 6 assignments and 5 reads.
- Not re-derived: `--pin-killed`'s `PIN KILLED: 14 pinned, 0 left unpinned`, its `NULL_COMMENT` control, the scoped-gate count `ALL 5134 FEATURE CHECKS PASSED`, and "Under G ... minutes 9, 13 and 15". I did not re-run them; CI's `tests / mutation` stands in for the first.
- RESULT CI at this head: read live. 111 check runs across 49 names: 25 success, 24 skipped, and no failure, cancellation or timeout in any run at this head (`ev/check_runs.txt`). `gate` 129837856117 succeeded, `pr-contract / pr-contract` succeeded, and `tests / mutation` 129769154265 printed `MUTATION TABLE PASSED` and `0 survivor(s) of 3 evaluated` (`ev/mutation_tail.log`). The red at 38e3d17e7 and a550c3cac is answered under the body's `## Red checks`. It names `prepr.sh` step 6d and `--pin-killed` as the cheaper detectors.
- CI read, unreadable by the instrument: `merge_train.py classify 068074f0... --pr 3405` exited 2 (`REFUSE ci: the check runs at 068074f0f2c2 could not be read`, `ev/classify.log`). The cause is `gh api --paginate`: it follows a `repositories/{id}` Link header, and this session's proxy refuses that link with HTTP 403. The check runs above were therefore read page by page (`page=1` and `page=2` at 100 each). `merge_train.py owed-reds` takes no head argument in this tree, so I did not run it. With no red run at the head, the set of owed reds is empty either way.
- RESULT merge: `git merge-tree --write-tree origin/main 068074f0...` exits 0 at origin/main 45adb0c3b4. The `LEDGER-MERGE: resolved tests/closures.json` line is the driver's own resolution (`ev/merge_tree.txt`).
- RESULT untouched across `b0762725...068074f0`: `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files.
- RESULT head: the PR head reads 068074f0f2c2dfdb57fc1821ed39f3510bc913ed at both the start and the end of this review, and the body's `## Head` names it.
- The previous verdict's two non-blocking findings were carried to #201 there, and the body's carry to #201 still stands. carry_audit at the head reports 2 items routed and 0 unrouted (review packet).

## Findings

none

## Friction

- `merge_train.py classify` cannot read check runs from a cloud seat whose proxy refuses `repositories/{id}` pagination links, so CI wait reported exit 2 here. A manual per-page read substituted. Carry: dismissed: environment proxy limit, not this PR's; the per-page read in ev/check_runs.txt stands in for it
