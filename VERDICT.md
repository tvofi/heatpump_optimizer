Fix review: blocked 9ce0179f77aa68eab6440c3d85aa92e788936b22 carry-missing: the body's Carry: #2959 names no live destination (carry_audit: no live roster group lists #2959 and there is no dev/programme/carries/carry-2959.json); the open group holding #2959 is R10-FLOW-MAIN-GATE

bus-nonce: b967b5e76ea5b0685f1bfc296b1370b9

## Block

Round 3, at the same head as round 2. The round-2 block is cleared. The figures now hold at this head: 51 checks, and M1 gives 51 checks with 4 failed. The null-control arms exist. M6, M6b, M8, M9 and M3 are dispositioned. One carry is still dead.

- `## Mutation proof` defers the harness additions to `dev/audit/harnesses/r10_seat_selftests_mutants.py` with `Carry: #2959`. `tools/audit/carry_audit.py`'s destination check, `Dests.check('#2959')` loaded from main's roster plus `origin/handoff/audit-r10-roster`, returns `#2959 has no owner: no live roster group lists it and there is no dev/programme/carries/carry-2959.json` (`ev/carry-dests.txt`). `carry_audit.py pr 2962` reports the same marker in the round-2 verdict as `BAD-DEST` (`ev/carry-audit.txt`, rc 1). A carry to a destination with no owner is not a carry under finding-propagation.md.
- What would clear it, with no code change: re-point the marker to the open group that holds #2959. `#2959` is open on branch `fix/r10-flow-main-gate`, and `Dests.check('R10-FLOW-MAIN-GATE')` returns `(True, '')` (stage `carries-open` on main). The alternative is a `carry-2959.json`. This is round 3. A fourth round over a body-only marker is a repair of the body, not of the cut, so I judge that fixer.md's re-cut does not apply. The orchestrator owns that call.

## Findings

- The harness sites this PR adds to the seat self-tests are still owed to `r10_seat_selftests_mutants.py` after #2959 merges. The body's marker names a destination with no owner (see Block). Carry: R10-FLOW-MAIN-GATE
- The null-control bullet "UNAVAILABLE arm: a failing `gh`, and a git read that cannot resolve" describes two arms that are already in the base's self-test (`ev/selftest-base.txt`). The arm this head really adds is "red-unanswered: a path list policy_lint refuses is UNAVAILABLE, not no unanswered red". That arm goes unnamed. The count still reconciles: 42 + 9 new = 51, and the bullet stands in for the new arm. Carry: dismissed: wording only, the arm exists and the count is right; fold into the same body patch
- The unpinned survivors M6, M6b, M8 and M9 are carried to R10-FLY-PACKET-RED-PATHS, the group this PR closes. The destination is live now (`resolved on origin/handoff/audit-r10-roster`). Once the group is done at merge, nothing will own them. They were accepted in round 2 as declared survivors, so the declaration is the disposition. Carry: dismissed: declared survivors accepted in round 2, the carry is a record and not a hand-on

## Evidence

- Head reviewed: 9ce0179f77aa68eab6440c3d85aa92e788936b22 (`ev/HEAD.txt`), from a detached worktree. It was still the PR head by REST at 19:37Z, PR updated 19:30:34Z (`ev/pr-body-at-review.txt`). Merge base ce5940c0d1d8f611a818d53e7fffcafb48b356c1. origin/main is now e5ddba1fad5e, 6 commits ahead. The roles diff `merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT self-test head: `review_packet self-test: 51 checks, 0 failed`. Base: `42 checks, 0 failed`. The 9 new checks are listed in the diff of `ev/selftest-base.txt` against `ev/selftest-head.txt`.
- RESULT M1 (the body's sed, my own re-run): `51 checks, 4 failed`, rc 1 (`ev/M1.txt`). The failing checks are the test-file arm, the delivery-row arm, the policy_lint-refuses UNAVAILABLE arm, and the diff_paths→red-unanswered arm. The tree was restored clean. The body's "I did not re-run M1" is now re-derived by this seat.
- Null-control bullets: each one maps to an `ok` line at the head. The arms are the test-only file, `tests/nightly_status.py`, #2954's workflows, no concluded red, the delivery arm and its null, and the two diff_paths arms. The UNAVAILABLE bullet is the exception (see Findings).
- Unpinned sites: M6, M6b, M8, M9 and M3 are declared as round 2 asked. The code findings from round 2 are not re-litigated, and the body does not contradict them. The M3 `dismissed:` reason passes `Dests.check`.
- carry_audit over the body alone (`check --body`): 0 finding items (`ev/carry-audit-body.txt`). That pass only parses findings, so it does not test the marker. The destination test in Block does.
- Merge: `git merge-tree --write-tree origin/main 9ce0179f…` at e5ddba1 gives 47982222c1d9, rc 0, no conflict (`ev/merge-tree.txt`).
- CI (check-runs REST, 94 runs, all completed, `ev/check-runs.txt`): the only red is `tests / nightly-status`. That is main's red: the diff, `review_packet.py` and `delivery/2962.md`, touches nothing it reads, and the body's `## Red checks` answers it. The latest `pr-contract` run started 19:31:58Z and succeeded, after the last red concluded. `tests / mutation` is success; its log was not read.
- Review packet rendered here (`ev/review-packet.md`): Refusals none, Advisories none.
- Not re-derived (CI's heavy runs are cited instead): `closure.py select`, `structure.py`, and the prepr lines.
