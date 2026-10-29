Fix review: merge 9ce0179f77aa68eab6440c3d85aa92e788936b22

bus-nonce: edbdd5b5caf336f9a1772671d3ad9582

Round 5, at the same head as rounds 2 to 4. Round 4's block is cleared. The body's marker now reads `Carry: R10-ORCH-REVIEW-PACKET`, and the carry text is on the roster ref.

## Findings

- The harness sites this PR adds to `tools/audit/seat/review_packet.py` (`unanswered_reds`, `diff_paths --paths-file/--existing-file`, `raise Unavailable`) still have to be added to `dev/audit/harnesses/r10_seat_selftests_mutants.py` once #2959 releases that file. The carry is landed at its destination (see Evidence), with acceptance figures and a null control. Carry: R10-ORCH-REVIEW-PACKET
- The unpinned survivors M6, M6b, M8 and M9 are declared in the body. They were accepted in round 2 as declared survivors, so the declaration is the disposition. Carry: dismissed: declared survivors accepted in round 2, the carry is a record and not a hand-on
- The M3 survivor (`--base` dropped) cannot be pinned without a real commit range. Carry: dismissed: --base cannot be pinned without a real commit range in the self-test
- `carry_audit.py pr 2962` still prints one BAD-DEST. It is item 75f08830 of the round-2 verdict comment, whose old marker `Carry: #2959` the body has since replaced. It is not in the body, and the body-side marker it duplicates is now resolved. Carry: dismissed: stale marker in a superseded verdict comment, the body's marker is the live carry; the orchestrator may hand-patch that comment if the train's pre-flight reads it

## Evidence

- Head reviewed: 9ce0179f77aa68eab6440c3d85aa92e788936b22 (`ev/HEAD.txt`). The REST PR head is still that SHA (PR updated 19:51:22Z). The `dev/governance/roles/` diff merge-base...origin/main is empty, so the contract is current.
- RESULT carry destination: `origin/handoff/audit-r10-roster` is at f54eeb3a5cc5b32935785c7dea59994e9555bd21. In `dev/programme/rosters/wave-r10-groups.json` the group `R10-ORCH-REVIEW-PACKET` (`resume.stage` carries-open) holds the "From #2962 (R10-FLY-PACKET-RED-PATHS)" text as carry index 13 of 14. It names the three site families, the acceptance (M1 fails 4 of 51, M2 and M5 fail 2, M7 fails 1), the survivors left declared, and the null control (a diff of `.github/workflows/nightly.yml` still leaves `tests / nightly-status` unanswered) (`ev/carry-landed.txt`).
- RESULT destinations under `carry_audit.load_dests`: with `--roster-ref origin/handoff/audit-r10-roster`, R10-ORCH-REVIEW-PACKET, R10-FLY-PACKET-RED-PATHS (in-progress) and the M3 `dismissed:` reason all return `(True, '')`. With the default (main) reading, R10-ORCH-REVIEW-PACKET is also `(True, '')`. R10-FLY-PACKET-RED-PATHS is a group only on the round roster, as in round 4.
- RESULT body markers: the body carries only `Carry: R10-ORCH-REVIEW-PACKET`, four `Carry: R10-FLY-PACKET-RED-PATHS` and one `Carry: dismissed:`; all resolve. The packet's `CARRY-AUDIT` line reads 0 finding items; the packet's `Refusals` and `Advisories` are both none (`ev/review-packet.md`).
- RESULT self-test at the head, my own run in a detached worktree: `review_packet self-test: 51 checks, 0 failed` (`ev/selftest-head.txt`). The body's figure matches. The code, figures and mutants were accepted in rounds 2 and 3 and were not re-run; the diff is `tools/audit/seat/review_packet.py` and `dev/programme/delivery/2962.md` only, unchanged from then.
- RESULT merge: `git merge-tree --write-tree origin/main 9ce0179f…` at origin/main e5ddba1 exits 0, no conflict (`ev/merge-tree.txt`). `VERSION`, the manifest and the notes heading are untouched.
- CI on this head (check-runs REST, 101 runs, `ev/check-runs.txt`): the only non-success, non-skipped run is `tests / nightly-status` (failure). It grades main's Nightly; the diff touches nothing it reads, and the body's `## Red checks` answers it (fix-review.md 11). The latest `pr-contract` run started 19:52:59Z, after that red concluded, and succeeded. `gate` succeeded. `tests / mutation` is success; its log was not read.
- Not re-derived (CI's heavy runs are cited instead): `closure.py select`, `structure.py`, and the prepr lines.
