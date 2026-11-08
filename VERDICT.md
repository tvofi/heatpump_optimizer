Fix review: merge 4b3af66de2b935ae66c986693bece3e85c9addef

bus-nonce: 0cb0ae0c917ed362173380f2cf7d7403

Round 1. Head measured: 4b3af66de2b935ae66c986693bece3e85c9addef (ev/HEAD.txt). The PR adds no production line: an RCA document, a recorded fixture, a harness, a mutant spec, an index entry and an INERT READS entry.

## Findings

(none this PR leaves unsettled; the body's own carries are routed to #201 and carry_audit reads them as routed.)

## Evidence

- Merge: `git merge-tree --write-tree origin/main 4b3af66de2b935ae66c986693bece3e85c9addef` rc 0, no conflict (ev/mergetree.txt).
- VERSION, manifest version and notes heading: three-dot diff empty (ev/version.txt). dev/governance/roles/ diff against main empty.
- RESULT selftest: `SELFTEST ok: 18 expected result(s), 2 null controls` (ev/selftest.txt).
- RESULT loop: reruns=129 predicted_listed=129 predicted_without_skipped=38, matching the body (ev/loop.txt).
- RESULT census, re-run in full (ev/census.txt): deferral_reds=86, heads_with_deferral=43, prs_with_deferral=13, non_deferral_reds=276, residual_red=18, residual_red_decider_success=0, stale_pin_reds_after_fix=6, stale_pin_reruns_after_fix=2, waiting_reds=45/heads 25/median 31.0/max 142.8, at_once_reds=41/heads 18/median 32.2/max 54.0, at_once_lag_min_max_decider_success=1.5, at_once_green_by_human=6, bot_reran_content_reds=257, gate_min=159, prs=6. Every figure the body quotes re-derived. Fixture sha1 91154dda3fa995a445fe459896f0dc9bd11cfadb matches.
- Mutants (spec, selftest as the command): 15 mutants, 14 KILLED, 1 survivor M3-green-after-red, NULL passes (ev/mutants.txt). M3 (`>` to `>=`) is disclosed in the body as equivalent on the recorded data; I accept it as equivalent (no gate success shares a second with a deferral red at its head) and it settles nothing downstream.
- fold_ledger check: 0 violation(s); tests/structure.py: STRUCTURE RATCHET PASSED. No budget file edited, so no raise.
- carry_audit at the head (packet): 5 finding items, 5 routed, 0 unrouted, 0 bad destination. Findings carried to #201 are the orchestrator's to land in the P436 and sweep.py groups; the body says so itself.
- CI: `merge_train.py classify 4b3af66de2b935ae66c986693bece3e85c9addef --pr 3354` exit 0 GREEN (pending none, red none).
- Red-check answer (step 11): the body states no check went red; classify reads none red at this head, so nothing is owed. Mutation lane was a no-production-line diff and drew no mutant; the body says so and uses spec mutants.
- Not re-derived: the fixture's recording from GitHub (no gh here); I re-ran the offline harness only. The #3278 replay arm and the `git archive` variants of loop were not re-run (they need other-sha exports); the in-tree default loop arm was.
- Forward-carry (step 10): the body routes its forward items to #201 (the dispatcher cannot write the roster branch); accepted as a Carry destination that exists.
