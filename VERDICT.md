Fix review: blocked 9ce0179f77aa68eab6440c3d85aa92e788936b22 carry-missing: Carry: R10-FLOW-MAIN-GATE names a group that is done on origin/handoff/audit-r10-roster, the roster roster_sync lands merged carries on, so carry_plan would refuse it and the harness additions would have no owner; R10-ORCH-REVIEW-PACKET is live on both rosters

bus-nonce: 2f0d457e7e935991c56f61a84de92eca

## Block

This is round 4, at the same head as rounds 2 and 3. The body changed in one place only. The round-3 marker `Carry: #2959` now reads `Carry: R10-FLOW-MAIN-GATE` (`ev/body-diff-vs-round3.txt`). The new marker still has no live owner. Round 3 suggested this marker, and that suggestion was wrong: it read only main's roster.

- `carry_audit.load_dests()` in its default mode accepts `R10-FLOW-MAIN-GATE` as `(True, '')`. It accepts it because main's roster (`origin/main`, e5ddba1) still has the group at `carries-open`. Pinned to the brief's roster, `load_dests(ref='origin/handoff/audit-r10-roster')` returns `(False, 'R10-FLOW-MAIN-GATE is done (resume.stage done)')` (`ev/carry-dests-roster-ref.txt`). The group was already `done` there at 465eee3b2, at 18:29Z, before round 3 was written. It is still `done` at the ref tip, 6acfdfa41 (19:35Z).
- That ref is where the carry would land. `roster_sync.carry_plan` appends a merged body's `Carry: <GROUP>` items to the round's roster branch ("never the base"). For a group that `roster_lib.is_open` reads as closed, it records a refusal ("the destination is done") and does not append. So at merge the harness additions owed to `dev/audit/harnesses/r10_seat_selftests_mutants.py` would land nowhere. finding-propagation.md says: "A group at `resume.stage: done` is not a destination".
- The marker has a second problem even if the group were reopened. The work this carry hands on starts only after #2959 merges ("owed after #2959 merges"). #2959 is the PR open in this group (`fix/r10-flow-main-gate`, "harness: the carries' mutants in the seat self-tests"). So the group would close at the moment the owed work could start.
- What would clear it, as a body-only change: re-point the marker to `R10-ORCH-REVIEW-PACKET`. That group owns `tools/audit/seat/review_packet.py`, is at `carries-open`, and `Dests.check` returns `(True, '')` for it under both the default mode and the pinned roster ref. Another option is a carry file under `dev/programme/carries/`, but that is a tree change and would need a new head. Choosing between them is the orchestrator's call. This is the fourth round, and fixer.md calls for a re-cut from the fourth. Every block since round 2 has been about the body's markers, not the cut, so I judge that a re-cut buys nothing here. The orchestrator owns that call too.

## Findings

- The harness sites this PR adds to the seat self-tests are owed to `dev/audit/harnesses/r10_seat_selftests_mutants.py` after #2959 merges. The body's marker names a destination that is done where carries land (see Block). This is the live owner of `review_packet.py`. Carry: R10-ORCH-REVIEW-PACKET
- Instrument finding. `carry_audit.py` reads a group that is open on main's roster but done on the round roster as live. In default mode it returns `(True, '')`, because the main roster wins over the round ref. `roster_sync.carry_plan`, the tool that lands the carry, reads the round roster and refuses the same destination. The review packet's `carry_audit at the head`, pr-contract's and the train's pre-flight therefore pass a carry that will be dropped at merge. Round 3 relied on that default reading and endorsed this marker. A destination check should apply the reading the lander applies. Carry: R10-FLY-CARRY-DISPOSITION
- The roster sources disagree on the group's state. `R10-FLOW-MAIN-GATE` is at `carries-open` on main and `done` on `origin/handoff/audit-r10-roster`. roster_sync names `carries-open` a protected human disposition that a merged PR must not turn into `done`. The rule also says a roster edit must never land on main, so main's value may only be stale. I did not trace which side is right. Carry: R10-ORCH-ROSTER-SCHEMA
- Round 3 found that the null-control bullet "UNAVAILABLE arm: a failing `gh`, and a git read that cannot resolve" names arms that are already in the base, and that the arm this head actually adds goes unnamed. The body is unchanged there, and the count still reconciles at 42 + 9 = 51. Carry: dismissed: wording only, the arm exists and the count is right; fold into the same body patch
- The unpinned survivors M6, M6b, M8 and M9 are carried to R10-FLY-PACKET-RED-PATHS. That group is `in-progress` on the round roster now, but it closes when this PR merges. They were accepted in round 2 as declared survivors. Carry: dismissed: declared survivors accepted in round 2, the carry is a record and not a hand-on

## Evidence

- Head reviewed: 9ce0179f77aa68eab6440c3d85aa92e788936b22 (`ev/HEAD.txt`), from a detached worktree. It was still the PR head by REST, with the PR last updated 2026-10-29T19:39:10Z (`ev/pr-head-at-review.txt`). Merge base ce5940c0d. The roles diff `merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Body against round 3's snapshot: the only change is the mutation-proof `Carry:` marker, `#2959` → `R10-FLOW-MAIN-GATE`, plus one trailing blank line (`ev/body-diff-vs-round3.txt`, `ev/pr-body-at-review.txt`). Round 3's accepted figures and mutant work were carried, not re-run, because nothing in the body contradicts them.
- RESULT self-test at the head: `review_packet self-test: 51 checks, 0 failed` (`ev/selftest-head.txt`). It matches the body.
- Carry destinations (`ev/carry-dests.txt`, `ev/carry-dests-roster-ref.txt`):
  - default mode: R10-FLOW-MAIN-GATE True; R10-FLY-PACKET-RED-PATHS True (resolved on the round ref); the M3 `dismissed:` reason True.
  - `--roster-ref origin/handoff/audit-r10-roster`: R10-FLOW-MAIN-GATE False (done); R10-FLY-PACKET-RED-PATHS True.
  - `--roster-ref origin/main`: R10-FLY-PACKET-RED-PATHS is not a group there.
  - R10-ORCH-REVIEW-PACKET and R10-FLY-CARRY-DISPOSITION: True under both modes.
- `carry_audit.py pr 2962`: `1 bad destination(s)` (`ev/carry-audit-pr.txt`). This is the stale `#2959` item in the round-2 review 6506038459, not the body.
- Review packet rendered here (`ev/review-packet.md`): Refusals none, Advisories none, `CARRY-AUDIT: 0 finding item(s)`. The packet's carry pass parses finding items only, so it does not test the body's markers.
- Merge: `git merge-tree --write-tree origin/main 9ce0179f…` at e5ddba1 exits 0 with no conflict (`ev/merge-tree.txt`).
- CI (check-runs REST, 107 runs over all pages, all completed, `ev/check-runs.txt`): the only red is `tests / nightly-status`, which is main's. The diff touches `review_packet.py` and `delivery/2962.md`, nothing that check reads, and the body's `## Red checks` answers it. The latest `pr-contract` run started 19:41:04Z, after that red concluded at 18:51:37Z, and succeeded. `tests / mutation` is success; I did not read its log.
- `VERSION`, the manifest version and the release-notes heading are untouched.
- Not re-derived here (CI's heavy runs are cited instead): `closure.py select`, `structure.py`, and the prepr lines.
