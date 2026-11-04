Fix review: merge cf2ed7303beaea740760c0afe8c58411169b9522

bus-nonce: 7b85f81d1322bebda0435cc560baf955

## Round

Round 2 (repair of the round-1 block on 5640ad9d, nonce fb2bd131). Reviewed head `cf2ed7303beaea740760c0afe8c58411169b9522`, still `refs/pull/3191/head` when this was written. The merge base `8e90d8144` is origin/main. `dev/governance/roles/` is unchanged between the merge base and main.

## Evidence

- RESULT selftest-head: `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` at the head printed `486 passed, 0 failed`, rc 0 (`ev/selftest-head.tail`). This matches the body's 486.
- RESULT mutant-A (`return 1` first in `closures_owes_slot`): 485 passed, 1 failed, rc 2. Red row: "closures_owes_slot: a scoped diff with scripts ... owes the slot" (`ev/mutant-A.*`). It survived in round 1 and is now killed.
- RESULT mutant-B (`scoped` changed to `full`): 484 passed, 2 failed. Red rows: the same row, and "and a full diff owes none" (`ev/mutant-B.*`). Killed.
- RESULT mutant-C (delete `SLOT_TAKEN=1`): 484 passed, 2 failed. Red rows: "a failing slot-take is attempted once ..." (got 2) and "the unleased marker is written once" (`ev/mutant-C.*`). Killed.
- RESULT mutant-D (my own: delete the `take_slot` in 3f3's else-arm): 484 passed, 2 failed. Red rows: the call-site count (got 4, wanted 5) and the driven 3f3 row (`ev/mutant-D.*`). Killed. This matches the body's D.
- Null control: the `closures_owes_slot` rows for empty `affected.scripts`, skip, full and records-here false all pass at the head. Mutant B shows the full arm is load-bearing. The 3f3 "plan skipping both takes no slot" row passes.
- Plant, end to end: a one-line change to `.github/workflows/arch-score.yml` on top of the head, run through the real `bash tools/pr/prepr.sh` (no stubs) in a clone whose origin/main is the head, so the plant is the only diff (`ev/plant-commit.txt`, `ev/plant-isolated.log`). The log reads, in order: `skip mutants`, `skip brief_lint`, `ok heavy slot taken slot=0`, `ok field coverage`. The slot is taken immediately before 3f3 and after the light steps. The `REFUSE agreement lane` line in that log comes from my plant commit's subject being read by the merge-subject corpus (agreement_py reads `git log --first-parent`). It is an artefact of the plant, not of this PR. The same lane is `ok` on the PR's own diff (`ev/plant-vs-main.log`, a first plant run against real main, which includes the PR's policy files and so leases at the mutants step).
- Class: the body's rule `grep -n 'heavy_skip \"' tools/pr/prepr.sh` returns mutants (4011), field coverage (4065) and register check (4100). The first two are leased. 3f5 is ruled light in the code comment beside it, and the body cites my round-1 figure of about 0.5 s. All three are dispositioned. The other heavy-gated sites (3h self-test, 6b closures, 6d' diff mutants) call `take_slot`.
- `git merge-tree --write-tree origin/main cf2ed7303beaea740760c0afe8c58411169b9522` exits 0 with no conflict (`ev/merge-tree.txt`).
- `VERSION`, the manifest, the notes heading and the claim files are not in the diff. The diff has 6 files: three gate-scoping copies, nudge.md, the delivery row and prepr.sh.
- Figures: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. `closure.py select` printed `MODE: SCOPED -- 1 script(s) run`. Both match the body. I did not re-run `tests/entities.py` for the body's 2602 figure; CI is green at this head.
- CI: `merge_train.py classify cf2ed7303beaea740760c0afe8c58411169b9522 --pr 3191` exited 0 with `GREEN cf2ed7303beaea740760c0afe8c58411169b9522 pending: none red: none` (`ev/classify.txt`). The body answers the red `tests / nightly-status` as inherited and not required, and the diff does not reach what it reads.
- `## Head` names `cf2ed7303beaea740760c0afe8c58411169b9522` and its code head `1584530f3`. The head I measured is the head the body names.
- Not re-derived (carried from round 1): the 4/4-slot pool figure and the 90 s timeout null control.
- I built no harness of my own. The finder's mutants A, B and C are taken from verdict/3191's ev/, and D is the body's own.
- Approval: the policy edits (gate-scoping.md and its generated copies, nudge.md) still need tvofi's approving review, whatever this verdict says.

## Findings

- Follow-up: carry 26's "slot-wait minutes per prepr over a day, before and after" is still unmeasured, and the body discloses it. It is owed after the merge: count slot waits over a day of prepr logs, fixer logs included, and compare them with the 29-of-35 baseline. Carry: R10-PREPR-CAP

## Friction

- The frugal-routing hook refused a sixth inline read or monitor in one prompt. The pre-bash hook refused `pkill`, so I killed the first plant run by PID. Neither changed a result.
