Fix review: merge 611102f07624b45af9e434ec4359f6db3f8e5b14

bus-nonce: 601134f483919666cf071bdfdd80e6b3

## Scope

Round 3, a delta re-review of #3442 (R10-SAV-VALUATION-RESIDUE) at the handoff tip 611102f07624b45af9e434ec4359f6db3f8e5b14. It resumes from round 2's `merge` verdict at 7c398bfbdaf389a767a473e320eba20c2b6fbec3 (probe/rev-3442-d9b89d35), which could not post because main was red, and does not redo what that verdict settled. This is not the fourth round, so `fixer.md` owes no re-cut.

The tip is f1e49686 plus one commit, which adds `tests/mutation_ledger/killed_by/optimizer.py/_terminal_row_cost.row_cost.GUARD_OFF.9afb8da3.json`. 7c398bfb is a merge of f1e49686 and this tip, and the two trees are byte-identical (18c7a44e3f8d…). So the patch at this tip is exactly the one round 2 reviewed. `review_carry.py` prints `FRESH-REVIEW` only because 611102f07 is an ancestor of 7c398bfb rather than a descendant (`force-push`). The delta touches no production or test line, so it does not widen the review. The body's changes are the Carry 7–9 line, `## Head`, the `## Figures` repair item, and the `tests / mutation` entry under `## Red checks`.

## Evidence

- RESULT tree identity: `git rev-parse 7c398bfb^{tree} 611102f07^{tree}` gives the same tree for both (ev/tree_identity.txt). Round 2's RESULTs therefore hold at this tip unchanged: M-COPYSIGN killed, M-CLAMP equivalent and triaged, the guard deletion redundant, the companion figures, and `STRUCTURE RATCHET PASSED`.
- RESULT 2712 pin, re-run with the body's own instrument at the tip: `python3 tools/audit/seat/mutant_run.py --in-place --spec ev/mutant_spec.json --cmd 'bash ev/killcmd.sh'`. The spec makes `optimizer.py:2712` `if refill is not None:` into `if False:`. The kill command is `mutation_table.py`'s `killed()` rule against the measured baseline: rc != 0 and more than 1 FAIL line in `PYTHONPATH=tests/hastub python3 tests/features.py`. It printed `SURVIVED NULL` and `KILLED row_cost_split_refill_GUARD_OFF`, rc=0 (ev/mutant_run_2712.log). The NULL is the null control. This matches the body's `## Figures` repair item and round 2's M-GUARD, where the added FAIL was `R10-SAV-VALUATION-RESIDUE: on a valved install ...`. The worktree was clean at HEAD afterwards.
- RESULT killed_by row: the file is valid JSON with the same key set as existing rows (`anchor`, `killed_by`, `old`, `reason`). Its `old` is the literal line at optimizer.py:2712, and `killed_by` is `tests/features.py`, the script that kills it. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base $(git merge-base origin/main HEAD)` at the tip exits 0 with `no closures, fast, governance or instrument red predicted`, and it lists no `ADDED UNPINNED` site (ev/ci_predict.log). That last fact is the body's claim. I did not run CI's `mutation-pins` job, which is CI's heavy run; this verdict cites none of it.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 611102f07` with origin/main at 50e4b1aa exits 0. Its stderr is `LEDGER-MERGE: resolved tests/closures.json` and it reports no conflict (ev/merge_tree.txt). The head is behind main but merges cleanly, so main is no block.
- RESULT version and claims: the three-dot diff from the merge base touches none of `VERSION`, the manifest, `RELEASE_NOTES.md` or either claim file.
- Body head: `## Head` names 611102f07624b45af9e434ec4359f6db3f8e5b14, the tip I measured. The body ref handoff-body/r10-sav-valuation-residue@e61f5f7e names `Code: 611102f07…`.
- Body changes: the Carry 7–9 line restates Carries 4–6 (the residual, the attribution and the secant) and adds no new figure. Its -3.90 % / -8.02 % are the residual figures round 2 left un-re-derived, and the tree is unchanged since, so they are still not re-derived here.
- Red checks: the owed set is `merge_train.py owed-reds` (ev/owed_reds.txt), which includes `tests / mutation` and `tests / fast (3.14)`. The body answers `tests / mutation` (red at f1e49686, cured by this tip's pin) with its cheaper-detector answer (`ci_predict.py` step 6d). It answers `tests / fast (3.14)` as main's inherited combi census, fixed by PR #3466. `governance / instrument-self-tests` (main's, fixed by PR #3474) is outside the owed set, so it is neither owed an answer nor a block.
- CI: no PR head sits at this tip yet and there is no review packet, so I waited on no CI and read no check runs for this verdict. The train re-proves the tip on current main.
- Forward-carry: unchanged since round 2. The two `Carry: R10-SAV-VALUATION-RESIDUE` items each name a pending orchestrator ruling on the owner, which is `fixer.md`'s exception.

## Findings

none

## Friction

none
