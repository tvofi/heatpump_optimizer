Fix review: merge dd399a0078992afd9d55e6e3d1a0849b575fdb14

bus-nonce: ad9c46508dcb0528817790d386c8416b
pending-ci: gate

## Scope

This is round 4. Round 3 returned `Fix review: merge 6e37c4c3362ffb65f4e9b26631252c766bb733ea` on ref `probe/rev-3812-413d7a1b` (de876bbc81). `tools/audit/seat/review_carry.py 6e37c4c336 dd399a0078` prints `CARRY` (`ev/review_carry.out`). The one branch-only commit is dd399a0078, `ci: pin killed mutants` by `github-actions[bot]`. It adds four `tests/mutation_ledger/killed_by/` rows and touches no production, test or harness line (`ev/delta_dd399a0078.diff`). So the round-3 measurements carry, and this round reads only that delta and the live checks (fix-review.md step 12). This is the fourth round, so the role file owes a re-cut. No re-cut is needed because the verdict carries.

I rendered the role pack at origin/main 505ed38e97. `git diff <merge-base>...origin/main -- dev/governance/roles/` is not empty (main's own role edits, e.g. #3839's open-axis rule), so I followed main's copy. The delta has no class claim and no quantified set, so that rule has nothing to block at this head.

## Evidence

- The delta's four pins: coordinator.py `_command_valve_target GUARD_OFF 9a0bd3f8`, mixing_valve.py `ValveTarget.command CMP_BOUND 9e52e37e`, off_restore.py `_arm_restorer GUARD_OFF 72d8a4e6`, and pump_arbiter.py `_release_row GUARD_OFF 88e2f26e`. Each `old` line occurs exactly once in its file at the head (`ev/pin_anchors.txt`). These are the body's `## Unpinned sites` coordinator.py:7764, mixing_valve.py:237, off_restore.py:243 and pump_arbiter.py:2271. All four are listed there as killed locally, with the pin owed to `mutation-autofix`.
- Reviewer re-run of one pin: `_release_row`'s `if coord is None:` set to `if False:` (pump_arbiter.py:2271), with `PYTHONPATH=tests/hastub python3 tests/features.py` in a detached worktree at the head. The result is KILLED by the body's named check "the row's release on an entry whose coordinator is gone answers not done without raising: ..." (output line 5742), with its null control passing. I stopped the run after the kill, so this is a kill check and not a full-suite count (`ev/mut_release_row.summary.txt`, `ev/mut_release_row.diff`) (`ev/mut_release_row.features.out`).
- Step 13: `git merge-tree --write-tree origin/main dd399a0078` at origin/main 505ed38e97 exits 0. Both ledger files print `LEDGER-MERGE: resolved` (`ev/merge_tree.out`).
- Step 5: pr-contract's version step reads `no version edit` at this head (`ev/ci_pr_contract_137075736262.txt`).
- Owed reds: `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing` and `validate / validate-hacs` (`ev/owed_reds.txt`).
- `tests / mutation` (job 137048858549) is red at this head with `MUTATION TABLE REFUSED -- 1954 unpinned site(s) against 1950 ... 7 of them added by this diff`. The seven are freq_control.py:319 and 325, mixing_valve.py:244, off_restore.py:234 and 235, and pump_arbiter.py:1833 and 2281 (`ev/ci_mutation_137048858549.txt`). All seven are in the body's `## Unpinned sites` as killed locally, with the pin owed to `mutation-autofix`, and the body's `## Red checks` answers `tests / mutation` (no cheaper detector, because the pinning lane is CI's). That is the killed-unpinned repair `ci-autofix.md` names. The pin shards `mutation-pins (1)` and `(2)` were still in progress at packet render. `classify` lists no red, so classify decides.
- `pr-contract / pr-contract` (job 137075736262) is red only on `figure-block line 139: block scope-line names head=6e37c4c3362f ..., this run is head=dd399a007899`. It is outside the owed set; see Findings.
- CI: `merge_train.py classify dd399a0078992afd9d55e6e3d1a0849b575fdb14 --pr 3812` was polled about every 75 s (`ev/classify.log`). The last line was `WAIT dd399a0078992afd9d55e6e3d1a0849b575fdb14 pending: gate red: none` at 03:55 UTC. Every run from 03:25 to 03:55 UTC exited 3 (WAIT), and the head did not move (`ev/classify.last`). The relay posts this verdict once CI is green at this head.

## Findings

- Note: body-stale: the body's `## Head` and its `scope-line` figure block still name 6e37c4c336. The bot's pin push moved the head to dd399a0078, which is what turns `pr-contract` red. Paperwork outside `custom_components/`, so not a block. Carry: dismissed: the orchestrator's body refresh (`figure_block.py refresh`) re-renders it at the final head
- Note: carry-missing: the body's three Forward-carry items (to R11-SEAM-actuation-writes twice, and to R11-SEAM-kernel-step) are still routed in the body only, unchanged since round 2. Carry: dismissed: the body routes all three to the orchestrator, who writes them onto those groups' briefs; landing them is the orchestrator's, not a code defect
- Note: departures: the four departures the body lists are unchanged and outside this delta, and each stays pending owner confirmation. Carry: dismissed: recorded in the body as pending owner confirmation; the owner's approving review at merge decides it
- Residual: reviewer mutant REV-E (round 2) still survives, as recorded in round 3. It adds a `restored(...)` call when an empty entry is dropped, which empties the owner's record. This delta touches no production line, so it is unchanged. Carry: dismissed: no check pins whether an empty drop leaves the owner's record, and either behaviour leaves the entity correct
