Question: R10-CARRY-AUDIT-P5 has no carry left to build; confirm it can close.

Measured at origin/main e23124ff6e (it contains handoff-wip a72500c787): carries 0-3 and 6 are marked implemented d1def1ea63, and carry 4 (bus.sh --topic) is in bus.sh carry_landed.
Carry 5 (landed counts main's roster OR the round branch): carry_audit.py load_dests already reads the round branch's roster (roster_lib.round_ref) even when --roster-ref origin/main is given, and group_text unions both rosters (P319), so a carry held on the round branch only already lands. The remaining difference is only that body_push.sh:193 and bus.sh:245,250,265 still pass --roster-ref origin/main; dropping it would switch the primary roster read to the worktree's tree and change behaviour, so I did not.
Asked: close the group, or say whether the flag should still be dropped.
No code change made; body_push.sh not run (nothing to hand off).
