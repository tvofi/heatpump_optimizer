Fix review: blocked c1c105ebe9d91860249679a85e4f4f68605b1100 stale-premise: P402's ACCEPT creates R10-FLY-STAMP-FLUSH-HOLD, which already exists and merged as #3280 (aaaec2128, 2026-11-07T18:26+01) before this PR's base

bus-nonce: e3c35a8d23a97c2fe31bf958e3ac96e4

## Block

The ruling reads its facts at origin/main be813ecd4 (2026-11-07 06:51), where stamp.py holds 0 train-hold references. #3280 (R10-FLY-STAMP-FLUSH-HOLD, "fly stamp flush hold") merged at 18:26 the same day and is an ancestor of both this PR's base 263b3908 and this head. At the head's base, record_flush already takes a held collaborator, prints a line when a hold appears, changes or clears, spends no dispatch under a live hold, and names a live hold at timeout (stamp.py TRAIN_HOLD_REF, record_flush docstring). The roster branch handoff/audit-r10-roster already carries a group with that exact name. The ruling's Binding therefore directs a fixer to build a landed change and its claim that no open group owns stamp.py's flush is not true. Re-triage at current main: the flush half is a non-finding (landed); only the unverified second-TERM-during-unwind probe on merge_train.py (the ruling's "first" step) may still be open, and #3280 also touched merge_train.py, so it needs re-measuring there before any ACCEPT.

## Evidence

- merge-tree origin/main vs head: rc=0, no conflict.
- merge_train.py classify: GREEN, pending none, red none. owed-reds takes no --pr/--head flags in this checkout, so I did not obtain its list; no required red exists.
- Diff: two new docs files (triage/s6-batch131.md, delivery/3385.md); no production, VERSION or claim change. Mutation proof and null control (roster_edit ruling_verdict/triage_refusal) not re-run; moot given the block.
- ev/ancestry.txt holds the ancestry and grep outputs above; ev/HEAD.txt holds c1c105ebe9d91860249679a85e4f4f68605b1100.
- Not re-derived: the ruling's line numbers, ledger SLIP and 23 min figures (host-local logs).
- Round: first review.
