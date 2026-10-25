Fix review: blocked ffbcb3cb5626e19fae8802dc1b6e66e3cc1e7a1e carry-missing: not carried to R10-GATE-DEFER

bus-nonce: 68f7275d43a52ea6d264dc2cad52c812

Round 2, after the blocked verdict at `a569538ef` (`review/2756`). Head reviewed `ffbcb3cb5626e19fae8802dc1b6e66e3cc1e7a1e`, still the PR head at 01:23Z (`ev/HEAD.txt`). Roles contract current: the three-dot roles diff against `origin/main` `662a3809c` printed nothing (`ev/cheap_checks.txt`).

## Block

- Round 1's block is re-routed but not paid. The record and body now name R10-GATE-DEFER, a live group, which fixes round 1's dead destination. But the precondition carry (M2 is legitimate only beside M1, with the M1 mutant control and the before/after harness demonstration) exists only as quoted text in `dev/audit/rca/R10-RCA-CODESCAN-WAIT.md` section 5 and in the PR body. `finding-propagation.md` says "the record [is] not propagation" and that "the producing PR does not merge until the carry is in the tree", on the roster or on `handoff/audit-r10-roster`, with the body citing the branch SHA. R10-GATE-DEFER has 0 `carry` entries on `origin/main` `662a3809c` and 0 on `origin/handoff/audit-r10-roster` `2124781cf`, and its `brief` mentions neither `WAIT_MAX_S` nor #2756 (`ev/gate_defer_roster.txt`). The body names no roster branch SHA. `carry_audit.py pr 2756` prints `5 routed, 0 bad destination(s)` against both refs (`ev/carry_audit.txt`), but that only checks that the destination is live, not that the write landed. To unblock: someone with the write (the orchestrator, per the body) runs `roster_edit.py append-carry R10-GATE-DEFER` with the section 5 quoted text onto `handoff/audit-r10-roster`, reads it back, and the body cites that branch SHA. No change to the record is needed.

## Findings

- Main's roster still holds R10-RCA-CODESCAN-WAIT `carry[0]`, which says M3 "stays owed here". M3 is on main (verified below), so the carry is stale. The body asks the orchestrator to drop it. That is a roster write, and it is still owed. Carry: dismissed: the body routes it to the orchestrator's `roster_edit.py drop-carry`, and it changes no stage's work
- CI at this head has not concluded. At 01:23Z every `ffbcb3cb` run was `queued` (prelude, refresh and cancel-superseded of runs 40149738738 and 40149739945). So no red at this head is answered or excused yet. Steps 11 and 12 must be re-read when the merge re-review takes place. Carry: R10-GATE-DEFER

## Evidence

- Round-1 findings 2 and 3 are paid in the record. Section 5 now says what carry 25 landed (M2, M3), where M1 and M4's prelude case are built, and why M4's `codescan_wait.py` half is dropped. The body's `## Red checks` answers the `718fcadb2` `pr-contract` and `gate` reds and the `a569538ef` defer-rule `gate` red, each with a cheaper detector and its standing cost.
- M3 mutation at the head (`ev/mutants_head.txt`): `codescan_wait.py --self-test` prints `17 checks, 0 failed`. With `, file=sys.stderr` dropped from line 139 it prints `17 checks, 1 failed` (case 16). This matches the body.
- Harness mutation at the head: `selftest: 9 checks, 0 failed`. With `inv = e["id"] < low` flipped to `>` it prints `9 checks, 5 failed`. This matches the body.
- M1 at R10-GATE-DEFER (`ev/m1_gate_defer.txt`): the branch has moved to `b2ff00056`, and `5150d1723` is its ancestor. `prelude.py --self-test` prints `29 checks, 0 failed`. With `waits_on` reduced to `run["id"] != run_id and run["id"] < run_id` it prints `29 checks, 1 failed`: "M1: waits for a LATER code run". The ordered-pair null case still passes. This matches the body.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`. The diff touches the same 4 files as round 1, and nothing in VERSION, the manifest, RELEASE_NOTES or the claim files.
- `git merge-tree --write-tree origin/main ffbcb3cb` exits 0 (`ev/merge_tree.txt`).
- Check runs are recorded in `ev/check_runs.txt`: `9dead62bc` and `e7b774926` have no CI runs (only dependabot), and every run at `ffbcb3cb` was queued at 01:23Z.
- Window figures not re-derived this round: 202 runs, INVERTED 27 / ORDERED 67, RED 16/0, the 26.2 min median and 14 of 16 above 600 s. Round 1 re-derived the 202/27/67 and 16/0 counts in the same window. The new median rule is now stated but was not re-run here. The body marks the 87/57, 3/2 and 10 min figures as carried and not re-taken.
