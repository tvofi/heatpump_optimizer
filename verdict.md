Fix review: merge 9a2b6ba8fe6b0040b87680ef5f79388f45686884

bus-nonce: 79bc7b1e3ff57b6adf67626030d429b9

## Round

First round. Measured head 9a2b6ba8fe6b0040b87680ef5f79388f45686884 (= refs/pull/3199/head and fix/r10-prod-residue-pins at verdict time); merge base and origin/main 8e90d81443317f76f22602a89651f7ca17c633f9. Role file current: three-dot diff of dev/governance/roles/ against origin/main is empty.

## Evidence

- RESULT head: PYTHONPATH=tests/hastub python3 tests/features.py -> ALL 4782 FEATURE CHECKS PASSED, rc 0 (ev/features-head.log).
- RESULT mutant mA (pump_arbiter.py restored to the merge base, the body's #2365 mutant): 1 of 4782 FAILED, the #2365 split/log check, [('space', 'space', 96)]; matches the body.
- RESULT mutant mB (forget_held(self.hass) removed from coordinator async_shutdown): 1 of 4782 FAILED, the #2351 re-arm check, [[30, 10]]; matches the body.
- RESULT mutant mC (strict < to <= in the _share short-remainder guard): 1 of 4782 FAILED, the boundary check, [('dhw', 'dhw')]; matches the body.
- RESULT mutant mD (my own: only the dhw_min line back to 15.0): 1 of 4782 FAILED, [('space', 'space', 48)]: each literal is pinned on its own.
- RESULT mutant mE (my own: log_steps returns 96): 1 of 4782 FAILED, [('dhw', 'space', 96)].
- RESULT mutant mF (log_steps body to pass, the ledger's RETURN_DEL pin): tests/typing_ruler.py rc 1, by_code[empty-body] recorded 0 measured 1; the new pin log_steps.RETURN_DEL.abf5020b is earned (ev/typing-mF.log).
- Null controls: both null-control checks pass on the head and on every mutant (only one check fails per mutant).
- Mutation-ledger moves (item 14): the two deleted pins name sites the diff removes; the three added pins were each reproduced as kills above (CMP_BOUND by mC, RETURN_DEL by mF, GUARD_OFF taken from CI's green mutation lane, not re-run per the cite-heavy-runs rule).
- Class (item 6): the brief scopes the class to pump_arbiter.py's step-width spellings. A grep of pump_arbiter.py at the head for 15, 15.0, 96, 0.25 finds only docstring prose; no remaining code literal. LOG_STEPS has no remaining reference outside the roster text and the ledger.
- Claims (item 4): env_drift.py --all -> NO UNCLAIMED DRIFT, 56 scenarios; NO STALE FIXTURE, 56 fixtures (ev/env_drift.txt). No golden or claim file in the diff.
- Item 5: VERSION, manifest and RELEASE_NOTES.md untouched (three-dot diff empty).
- tests/structure.py at the head: STRUCTURE RATCHET PASSED; no budget file touched.
- Merge (item 13): git merge-tree --write-tree origin/main 9a2b6ba8fe6b0040b87680ef5f79388f45686884 rc 0, tree 0ca330b11331df1a3955daabca9929d94c4af783, no conflict (ev/merge-tree.txt).
- CI (item 11): merge_train.py classify -> GREEN 9a2b6ba8fe6b0040b87680ef5f79388f45686884 pending: none red: none (ev/classify.txt). The only red check run is tests / nightly-status; this diff does not reach what it reads, so it is not this PR's. The body answers the mutation lane that prepr.sh predicted (cheaper detector: prepr.sh step 6d, already standing).
- Item 7: the body names 9a2b6ba8fe6b0040b87680ef5f79388f45686884 as head, with authored code head 316f0a2ee; the one commit between them is only dev/programme/delivery/3199.md.
- Item 10: the body's forward-carry is none. Nothing found here changes a later stage.
- Item 15: the edit stays inside the architect note's seam (pump_arbiter _share and the log length take the width from plan_step; coordinator.py not edited).
- Harness (item 9): the roster carries prescribe the failing tests and null controls but point to no committed finder script. I took those prescriptions as the harness and ran them through the PR's own features.py checks at the head and at the mutants. I built no instrument of my own.

## Findings

- Residual: pump_arbiter.py docstrings (lines 3, 40, 110, 113) still say "15-minute" step in prose. Prose about today's width does not need to follow a patched constant. Carry: dismissed: documentation prose, no code spelling of the width remains
- Follow-up: neither roster carry names a committed finder harness. The checks this PR adds to features.py now play that role. Carry: dismissed: the carries prescribed the tests and this PR lands them

## Friction

- The frugal inline-search hook refused plain greps after a few calls in this seat, so one lookup went to a scout.
