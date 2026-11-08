Fix review: merge 930e1786863a0bfba7cbde0aa2e6dd246f9a4f11

bus-nonce: 13fb86f549b9b4f074ab6f79972708e0

## Evidence

- Round 1. Reviewed from a detached worktree at 930e1786863a0bfba7cbde0aa2e6dd246f9a4f11, three-dot against merge base 8a4974d1522f979f5b1c837df8e3a76b535bf35e. Four files: fix-review.md step 13, cloud_dispatch.py (the fixer and reviewer prompt text plus three self-test checks), the instrument doc, and the delivery row dev/programme/delivery/3338.md (present).
- RESULT ci: `merge_train.py classify` printed `GREEN 930e1786863a0bfba7cbde0aa2e6dd246f9a4f11 pending: none red: none` (rc 0). The packet digest lists no concluded red on any check run, which matches the body's `## Red checks: none` (ev/classify.txt, ev/review-packet.md).
- RESULT merge: `git merge-tree --write-tree origin/main <head>` printed tree 0728dd4a6455 with rc 0, so no conflict (ev/merge-tree.txt).
- RESULT self-test: `cloud_dispatch.py --self-test` at the head printed 129 checks, 0 failed. This matches the body's figure (ev/self-test-head.txt).
- RESULT failing-first: the head's self_test run against the base's `_prompt` failed both new arms (129 checks, 2 failed).
- RESULT mutation: 6 of 6 mutants on the changed prompt lines were killed: the reviewer line reverted, the reviewer's "never" clause weakened, the fixer's no-re-merge clause inverted, the conditional changed to always, the old unconditional sentence restored (the brief's named mutant), and "first clean" changed to "last clean" (ev/mutations.txt).
- RESULT null control: injecting the reviewer phrase into the probe seat line fails the null-control check. Its harness moves under its own perturbation, so the control is not void.
- RESULT archscore: `score.py --diff <merge-base> HEAD` printed `Architecture score: dS +0.0000 NULL` (ev/archscore.txt).
- RESULT structure: `tests/structure.py` printed STRUCTURE RATCHET PASSED. The three-dot diff touches no `*_budgets.json`, VERSION, manifest or RELEASE_NOTES.md.
- RESULT entities: `tests/entities.py` did NOT run clean here, and the cause is the environment, not the PR. venv-ci's python3 has no `homeassistant` module (ModuleNotFoundError from tests/harness.py), and venv-ha lacks `paho`. It fails the same way at the merge base. The PR's only new tracked file is a delivery row, a class closure.py already handles (test row at tests/closure.py:2982). CI `tests / closures` and `tests / closure-scope` concluded success.
- Scope vs roster carry 0: the brief names fixer, repair-round and reviewer text. cloud_dispatch.py has no separate repair-round prompt: repair rounds render the fixer role, which changed. A grep of tools/, .claude/ and dev/governance/ found no other "merge a moved origin/main" instruction. fixer.md lines 93-95 already state the conditional merge rule, so the body is right that no carry to R10-FIXER-MD-SPELLING-CORPUS is owed. The --preamble flag was not built, as the brief says.
- Policy (fix-review.md step 13), what it changes for a seat: a reviewer is now told explicitly that the only main-related block is a merge-tree conflict, and never a head that is behind main but merges cleanly (tvofi 11-07). The claim-file conflict rule is unchanged ("a conflict off the two claim files is yours"). The old rationale clause ("because you cannot know the merged result is correct") was dropped, and "yours to block on" became "yours". The previous sentence ("Block on main only on one") carries the block meaning, so the rule is not weakened. This is code-owned policy and merges on tvofi's review or under the mandate in force. The body claims no approval.
- `## Head` names the current head 930e1786863a0bfba7cbde0aa2e6dd246f9a4f11, and the head did not move during this review.

## Findings

- Body accuracy: the second paragraph of `## Head` still describes bc59a13f63cb ("no merge was made, per this change's own rule"). The head actually contains 6ea650f9d, a merge of origin/main into the branch, which tvofi's identity made before this rule lands. The first paragraph names the current head correctly, and the code is unaffected. Carry: dismissed: stale body prose only; the first paragraph of ## Head is current and nothing downstream reads the stale sentence
