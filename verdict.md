Fix review: merge 84113541350889c7dc1472a3977ab526b55e4bf2

bus-nonce: 841f3e53d5fed0dcd0cc5c9740d0a035

## Summary

Round 2, delta review of handoff/r10-standing-contracts-p2 (PR 3494). Previous head 907c15d3755fa459b6bd91333fdc2a2828d47995 was blocked mutation-vacuous with four survivors (A floor refusal, B launch.json, I snapshot_live train read, L --train-state pass-through). The delta 907c15d3..84113541 is one commit, 8411354135, touching only tools/audit/seat/hooks_setup.py (self-test cases plus two registered mutants) and tools/audit/seat/pulse.py (self-test live-path case). It changes no production line under custom_components/, so the scope does not widen. All four earlier survivors are now killed. No survivor remains in my run.

## Findings

- The body's `## Mutation proof` says "dropping the spool read fails 1". At this head it fails 2: the new live-path case also goes red (ev/head-body-figures.txt). The figure was carried unchanged from the earlier head. It understates the kill, so no claim fails. Carry: dismissed: understated figure from the earlier head; the mutant is killed more strongly than claimed

## Evidence

- Finder's harness at both ends (ev/mut.py is the previous reviewer's driver from probe/revt-r10-standing-contracts-p2-d7a36074 ev/mut.py, extended with M to P and an optional label filter):
  - RESULT at 907c15d3 (ev/prev-reviewer-mutants.txt): A, B, I and L all SURVIVED. hooks_setup 58 checks, 0 failed. pulse 64 checks, 0 failed. This reproduces the earlier block.
  - RESULT at 84113541 (ev/head-reviewer-mutants.txt): A to L all KILLED. A and B kill hooks_setup.py. I and L kill pulse.py. C to H, J and K are still killed.
  - RESULT reviewer's new targeted mutants on the repaired arms at 84113541, all KILLED: M (launch.json records every env variable, not just HPO_*), N (records cwd as /), O (argv drops the interpreter), P (snapshot_live `if train_state:` set to False).
- Null control: the un-mutated head passes. hooks_setup.py --self-test prints "61 checks, 0 failed" at rc 0 and kills its in-tree MUTANTS, including the two new beatd arms (ev/head-hooks_setup.py.txt). pulse.py --self-test prints "66 checks, 0 failed" at rc 0 (ev/head-pulse.py.txt). The new cases carry their own null controls: beatd at the floor starts and records, and an absent train state holds nothing, so the verdict is STOPPED. Each passes un-mutated, and each is the counterpart of a planted case that the mutants turn red.
- Body figures re-derived at 84113541 (ev/head-body-figures.txt). Answer filter changed to `is not None`: 2 failed, which matches the body. Spool read dropped: 2 failed, where the body says 1 (see Findings).
- Previous verdict's findings: (1) the "forward-carries 24" contradiction is resolved in the handoff body. BODY.md at handoff-body/r10-standing-contracts-p2 now reads "defers 24". PR 3494's live body still has the old line and the old head 88417939, because the PR has not taken the handoff yet. Updating it is the orchestrator's job when it lands this head, not a defect of this head. (2) The second spelling of the train default under an unset HPO_STATE_DIR was dismissed with a Carry in round 1. The delta leaves it unchanged, and it still fails safe.
- Head: BODY.md `## Head` names 84113541350889c7dc1472a3977ab526b55e4bf2. refs/heads/handoff/r10-standing-contracts-p2 still read 84113541350889c7dc1472a3977ab526b55e4bf2 before return.
- `git merge-tree --write-tree origin/main 84113541` (origin/main 0b276e8c0c) exits 0, tree c72d8e9c0c, no conflict (ev/merge-tree.txt).
- The three-dot diff against main touches only HANDOVER.md, beatd.py, liveness.py, hooks_setup.py, instruments/hooks_setup.py.md and pulse.py. It leaves VERSION, the manifest, RELEASE_NOTES.md, claim files, golden fixtures, *_budgets.json and tests/closures.json untouched, and adds no new file.
- CI: PR 3494 exists, but its head is 88417939, not this handoff head. No review packet exists and no CI has run on 84113541, so there is no red check to answer. `merge_train.py owed-reds` names coverage-ratchet, fast, mutation, typing and validate-hacs; none has run on this head.
- Role contract: fix-review.md on main differs from the merge base in wording only. I followed the version rendered from main by role_pack.py.
