Fix review: merge 87319cb1c2218489d112548e05512100221660a5

bus-nonce: 957bea34d88103b222cfe699057230dc

## Round

This is round 2, the second review of #3184. The prior verdict (nonce 7da3c0d1) blocked 913e74e8 as mutation-vacuous: `freq_control.py:228 GUARD_OFF` in `FrequencyMap.evidence_exhausted` survived the suite. The repair is 7ec46c8a3 (a new features check) and e8a21c53b (the pin json), followed by two merges of origin/main. `review_carry.py c34999c1… 87319cb1…` prints FRESH-REVIEW (`ev/review_carry.txt`), so this is a full review at the head, measured from detached worktrees at head 87319cb1c2218489d112548e05512100221660a5 and at its merge base 8e90d81443317f76f22602a89651f7ca17c633f9 (= origin/main).

## Summary

The block is repaired. The 228 GUARD_OFF mutant is now killed by the check the body names, and that check's null arm passes at the head. The finder's harness reads 6 at the base, 0 at the head and 0 under the base null. Under the 228 mutant alone it reads 1, which matches what the suite sees. CI classifies this head GREEN. The merge with origin/main is clean.

## Findings

none

## Evidence

Step 1, mutation proof for the repaired site. One line was mutated, `freq_control.py:228` -> `if False:` (`ev/mutant_228.diff`), and `PYTHONPATH=tests/hastub python3 tests/features.py` was run:
- head unmutated: `ALL 4786 FEATURE CHECKS PASSED`, rc=0 (`ev/features_head.tail.log`).
- mutant: `1 of 4786 FEATURE CHECKS FAILED`, rc=1. The only FAIL is "evidence below a target the plan calls off is not exhaustion (D8-s1-01)", the check the body names (`ev/features_mut.tail.log`).
- The null arm of that check, `evidence_exhausted(0.11)` True on the same map, is part of the passing check at the head. The control is therefore clean, and the check does not fail on a map it cannot satisfy.
- CI `tests / mutation` (job 126587903400) at this head printed `PIN RE-VERIFICATION: 7 reproduced, 0 not reproduced`, `freq_control.py:228 GUARD_OFF -- killed by tests/features.py`, `0 survivor(s) of 7 evaluated` and `MUTATION TABLE PASSED` (`ev/ci_mutation_lane_tail.txt`). Since mutants were evaluated, the result is not INCONCLUSIVE.
- Round 1 already proved the other five seams, each in isolation (prior verdict). The authored delta since then is only the features check and the pin json, so those proofs stand.

Step 2, the finder's harness at both ends. `dev/audit/harnesses/r10_run_owner_probes.py` was run from a copy placed in each worktree, because the harness resolves the repo from its own path:
- RESULT probes_failed=6 count (base 8e90d814) (`ev/probes_base.txt`)
- RESULT probes_failed=0 count (base --perturb, the null) (`ev/probes_base_perturb.txt`)
- RESULT probes_failed=0 count (head) (`ev/probes_head.txt`)
- RESULT probes_failed=1 count (head with the 228 mutant, `FAIL freq_control.FrequencyMap.evidence_exhausted: exhausted=True owner_runs=False`) (`ev/probes_mut228.txt`). The suite and the finder's probe now agree on this mutant.
- Process note: a first run invoked the head's copy from the base worktree. It read 0 at the base and 0 under the mutant, because it imported the head's tree. Those runs were discarded and re-taken as above.

Step 4, claims. Three-dot `tests/golden/claimed_drift.txt` differs from the merge base only by this PR's header text and its one `shape:` claim. `card_claimed_drift.txt` is identical. `env_drift.py --all` was not re-run here. `tests / fast (3.14)` is green at this head and carries that check.

Step 5. VERSION, manifest.json and the RELEASE_NOTES.md heading are untouched (three-dot stat empty).

Step 6, class. `enumerate_p2.py` printed `RESULT F1_run_threshold=13 count` at base 8e90d814 and `=9` at the head (`ev/enum_base.txt`, `ev/enum_head.txt`). The four removed seams are exactly the four in the diff, and every other line differs only by line number. The remaining nine are dispositioned in the body, as in round 1.

Step 7. The body's `## Head` names 87319cb1c2218489d112548e05512100221660a5, the head measured here.

Step 11, red checks. The live `get_check_runs` read 55 runs, every workflow concluded.
- `tests / replay` is red: `synthetic-dhw-only.json: cycle_cost [cpu_ratio 3.069 over its budget 2.173]` (`ev/ci_replay_tail.txt`). The body answers this fixture's red as runner timing. Re-measured here at both ends, the base reads `cpu_ratio 2.568` FAIL and the head `2.732` FAIL (`ev/replay_dhwonly_*.log`). The base fails the same way, so the red is not this diff's. The lane is not required.
- `tests / nightly-status` is red: main's nightly. The diff does not reach it.
- `pr-contract / pr-contract` (job 126611468129) started at 13:44:00Z, after the last red concluded (replay at 13:14:08Z), and passed. That is the evidence that the body answered the reds.
- `merge_train.py classify 87319cb1… --pr 3184` printed `GREEN 87319cb1c2218489d112548e05512100221660a5 pending: none red: none`, rc=0 (`ev/classify.txt`).

Step 13. `git merge-tree --write-tree origin/main 87319cb1…` against origin/main 8e90d81443317f76f22602a89651f7ca17c633f9 exited 0 (`ev/merge-tree.txt`).

Step 14. `python3 tests/structure.py` at the head printed `STRUCTURE RATCHET PASSED` (`ev/structure_head.txt`). The new ledger json for 228 is earned: removing the gate turns the named check red (step 1). The other ledger jsons in the range diff come from origin/main's merges, not from this branch.

Step 15. The authored lines since round 1 are one features check and one pin json, with no production change. Round 1's architecture judgement stands.

Steps 9 and 10. The finder's P2 harness is committed. `## Forward-carry` is none, and nothing found here changes a later stage.

Step 12. The head was re-read before return (below).

## Friction

- The frugal routing hook refused a foreground wait and a Monitor as "inline search op 6/7". The wait was routed through a read-only scout. Its report claimed a 50-minute wait that its own 58 s runtime contradicts, so the scout's figures were discarded and every number above was re-read directly from the logs.
Self-audit: carry_audit.py check on this verdict printed CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s), rc 0.
