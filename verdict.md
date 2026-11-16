Fix review: merge da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e

bus-nonce: 7675f737dcf9d1a8ebf4413275759678
pending-ci: tests / closures, tests / coverage-ratchet, tests / fast (3.14), tests / graders-head-copy

## Round

Second round, over the reviewed head 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e. The packet's `## Review scope` reads delta. The previous verdict blocked only on a merge conflict with main and said that the diff itself was not reviewed. So the PR's own diff (`git diff $(git merge-base origin/main HEAD)...HEAD`, 16 files, instrument/CI only, nothing under `custom_components/`) was reviewed in full at this head, together with the hand-resolved merge da36537f13 (parents 7a2b2cdef2, d4968fe08b). No production delta exists, so nothing widens past the diff.

## Previous finding

- The merge-conflict block is resolved. `git merge-tree --write-tree origin/main da36537f13` exits 0 against origin/main f9b680fee4 (only `LEDGER-MERGE: resolved tests/closures.json`). The four formerly conflicting paths carry both sides at the head. `beat_jobs.py` ROWS/RUN hold main's `scorecard` and the PR's `toolchain-promote`. `governance.yml` holds main's round-metrics step and the PR's toolchain step. INSTRUMENTS.md and `beat_jobs.py.md` hold both entries.

## Head

- The PR's live head moved during review to 911384553f94d18fc6803b6674de27d700ebcb9f, `ci: merge main` by github-actions onto main's 315dda8f62 (#3648). `review_carry.py da36537f13 911384553f` prints `CARRY` (0 non-merge branch-only commits), and 911384553f's tree equals `git merge-tree --write-tree da36537f13 315dda8f62` (ddc49de3c7). By step 12 this verdict carries there through `app_approve.sh --carry`. No figure below was re-taken at 911384553f.

## Evidence

- Mutation proof, fixer's harness (the builder's, not a finder's; the body says no finder harness exists for this group): `python3 dev/audit/harnesses/r11_toolchain_mutants.py` at this head prints `RESULT mutants=26`, `RESULT survived=0`, and every M0 is `null-ok` (ev/selftest-r11_toolchain_mutants.py.txt).
- Reviewer's own mutants (ev/reviewer-mutants-driver.py, ev/reviewer-mutants.txt), each one exact replacement followed by the mutated file's self-test: 9 of 10 were killed. Killed: beat-refusal-silent, beat-no-statefile, beat-held-prefix, walk-no-movable, init-twice, held-runs-2, sha-nonsha-head, status-cancelled-green (gate `status` reading cancelled as green), prune-prefix-loose (`"toolchain" in name`). Survived: scan-unbounded (see Findings).
- Self-tests at this head: `toolchain self-test: 42 checks, 0 failed`; `gate self-test: 120 checks, 0 failed`; `SELF-TEST PASS (79 checks)` (prune_refs); `beat_jobs self-test: 273 checks, 0 failed`. Each matches the body except beat_jobs (see Notes).
- Step 6 class rule: the body's three enumerators re-run at merge base d4968fe08b and at the head give (a) 45/45, (b) 19/20, (c) 22/22. The only new (b) line is `tools/audit/seat/toolchain.py` (ev/enumerator-b-*.txt), which matches the body's claim. The seams they return are dispositioned in the body's Forward-carry.
- Step 4/5: the diff touches no claim file, `VERSION`, manifest, `RELEASE_NOTES.md` or `custom_components/`.
- Step 13: ev/merge-tree.txt; rc 0; no MERGE-CLAIM line.
- Step 7: the body names da36537f13 as its head.
- Step 16: no actuator write is touched.
- CI: `merge_train.py classify da36537f13 --pr 3654` was polled about every 77 s from 06:03 to 06:33 UTC and printed `WAIT da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e pending: gate red: none` throughout (ev/classify.log). Still running at 06:33: tests / closures, tests / coverage-ratchet, tests / fast (3.14), tests / graders-head-copy. Concluded red: `tests / nightly-status` and one `gate` run. Neither is in `merge_train.py owed-reds`, and classify reads gate red: none, so no `## Red checks` answer is owed.
- review_packet render: REFUSE introduced-red (instrument-self-tests in_progress at render); classify decides (ev/review-packet.md).

## Notes

- Note: body-figure: the body quotes `beat_jobs self-test: 261 checks, 0 failed`; this head prints 273 checks, 0 failed. The other twelve rows came in with main's merge, and the body's figures were taken at a2c094d8c0.
- Note: carry-own-group: the own-group carries `R11-PRE-TOOLCHAIN-PIN (item tp2)` were read against fixer.md's two exceptions. Item 806e1101 (ref init and who may push it) is a pending owner decision. The rest are the unbuilt remainder of the approved design's named parts p1/p2, which the body's Friction raises with the orchestrator as a part-line/design mismatch. They were taken as the split-part exception, not as a carry-missing block. The roster (handoff/audit-r10-roster, wave-r11-groups.json) already holds item 806e1101.

## Findings

- Follow-up: `toolchain.py` `choose`'s walk bound `[:SCAN_RUNS]` is unpinned. Removing it leaves `toolchain self-test: 42 checks, 0 failed`, so up to LIST_RUNS=30 runs' job listings could be read per pass with no check failing. It is a cost bound and not a correctness predicate: the walk still stops at the ref and at the first green. Carry: R11-PRE-TOOLCHAIN-PIN
