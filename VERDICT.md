Fix review: merge 333aba9074bd22f40c5a18f83e15309652b89fb7

bus-nonce: 1c869bbdbabc45f49ff5c3ebefb5db48
pending-ci: gate

Round 2 (delta over the reviewed head 7caa9f561c3f9407b060b579c7a2c512d223bc8d). The branch adds one commit since then, b85164a43d (self-test pins in `tools/audit/seat/orchestrator_tick.py` and `tools/audit/seat/ledger.py`), merged by eaa61675b4. The head 333aba9074 merges main 4ce615b5e6 and hand-resolves the conflict in `ledger.py`'s `KINDS`. The delta changes no `custom_components/` file, so the review scope is not widened.

## Findings

- Follow-up: the round-1 finding still stands at this head. OUTSIDE-CHAIN-IDLE is in `beat_jobs.FAMILY` but not in `owed_unactioned.FAMILY`, and `OPENER ABSENT` is in neither, so the repair-discharges census cannot see an unactioned outside-chain line. b85164a43d does not change either family. Carry: R11-PRE-ACK-COMPLETION

## Evidence

- Round-1 block resolved. All seven named mutants are killed at this head (`ev/mut_block7.txt`, driver `ev/mutant_driver.py`, the round-1 driver pointed at a detached worktree of 333aba9074):
  - m6-dr-fetch-unreadable: killed by the new check "a failed fetch of the design refs is UNREADABLE and owes no line".
  - m25-dr-timeread-unreadable: killed. The self-test raises KeyError before the new commit-time arm can assert, and the arm itself also pins it.
  - m12-ud-cp: killed by "a carries-open group whose gate is open ... prints the line with its age". That check now requires `UNDISPATCHED: CP R10-OI`, and a new null control covers the non-CP case.
  - m24-dr-cp: killed by the new CP arms in both `orchestrator_tick` and `ledger` self-tests.
  - m22-ledger-arm: killed. The disposition fixture now goes through `ledger.dispose`, which refuses `refs/heads/design/`, and `ledger.py --self-test` also exits 2.
  - m23-ud-wipseat: killed by "every SEAT_REFS family is a seat". `SeatStub` now answers only the refs whose patterns match the argv, and a null control shows that a `probe/` ref is no seat.
  - m16-op-stuck3: killed by the new n=1, n=2 and n=3 STUCK arm.
- Regression: the other 18 round-1 mutants (m1–m5, m7–m11, m13–m15, m17–m20, m26) are all still killed (`ev/mut_rest.txt`). m21 is beat_jobs-only and its file is outside the delta, so I did not re-run it.
- Self-tests at the head (`ev/selftests.txt`): orchestrator_tick 368 checks, 0 failed; ledger 108/0; owed_unactioned 60/0; beat_jobs 156/0 (`--no-mutants`); `tests/structure.py` STRUCTURE RATCHET PASSED.
- Merge resolution (`git show --remerge-diff 333aba9074`): `KINDS` keeps main's `handoff-skipped` and the branch's `design-review`, so both sides are kept and nothing is lost.
- Merge with main: `git merge-tree --write-tree origin/main 333aba9074` exits 0 with origin/main at 4ce615b5e6, which is the head's own second parent. There is no conflict and the head is not behind main.
- Role contracts: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Versions and claims: the three-dot diff touches no `VERSION`, manifest, `RELEASE_NOTES.md`, claim file or `custom_components/` file.
- Head: the body's `## Head` names 333aba9074, which is the head I measured, and traces the authored head b85164a43d through eaa61675b4.
- Finder's harness: none is committed. As in round 1, the body stands the self-test fixture in for the 2026-11-11T05:06Z replay, and I could not re-derive the replay.
- Note: figure: the body's `## Figures` are still round 1's, measured at 441f741b9f: orchestrator_tick 356/0 and ledger 104/0. At this head they are 368/0 and 108/0. The `## Mutation proof` section does not list the seven round-2 pins. `python3 tools/audit/seat/beat_jobs_selftest.py: exit 0` is still vacuous, as noted in round 1. Carry: dismissed: evidence, not a finding
- Red checks: the body says "none". See the CI line for the live state.
- CI: `merge_train.py classify 333aba9074bd22f40c5a18f83e15309652b89fb7 --pr 3635` printed `WAIT 333aba9074bd22f40c5a18f83e15309652b89fb7 pending: gate red: none` (rc 3) on every one of 24 runs between 06:30:07Z and 06:59:43Z (`ev/classify.log`). No red was seen, so the verdict carries `pending-ci: gate`.
- Head unchanged at verdict time: `fix/r11-pre-ack-completion` is still 333aba9074.
