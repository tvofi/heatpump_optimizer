Fix review: merge c44e95fe3b826fa2d17b6c8ddb3877a62840b850

bus-nonce: ec8cf72732f08e036a6c123a6aaed7a5

## Round

Round 1: the PR carries one authored code commit (1224b42d), the orchestrator's main merge (be4c0768) and its own delivery row (c44e95fe).

## Findings

- No committed finder's harness exists for V118 (fix-review.md step 9). The instance (#2856, nightly run 40300518367 `skip-train-hold`) is a live-run observation that cannot be replayed offline. The triage (dev/programme/triage/s6-batch34.md, P198, lines 143-173) prescribes the test shape this PR commits: the executed `_train_hold_status` harness in tests/entities.py, extended with `_hold_calls`. The fixer built that extension and discloses it in the body, and I measured with it. Carry: dismissed: the triage itself names this executed step harness as the instrument, and this PR commits it into the tree, so nothing stays out of tree.

## Evidence

- Head measured: c44e95fe3b826fa2d17b6c8ddb3877a62840b850 (ev/HEAD.txt). At verdict time the PR head is unchanged (refs/pull/2918/head = c44e95fe).
- Role contract: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so fix-review.md is current.
- Review packet rendered: no refusals, no advisories, carry_audit 0 items, figure_lint 4 resolved / 1 not verified / 0 refused (ev/review-packet.md).
- RESULT head: `PYTHONPATH=tests/hastub python tests/entities.py` gives `ALL 2470 ENTITY CHECKS PASSED`, rc=0 (ev/entities-head.txt), matching the body. Run under a Python 3.13 venv with tests/requirements-ci.txt that I built: the container's default python3 is 3.11, which cannot parse tests/entities.py (PEP 701 f-strings).
- RESULT mutation proof (the body's mutant: .github/workflows/nightly.yml replaced by the merge base's copy): `3 of 2470 ENTITY CHECKS FAILED`, exactly the three new checks the body names (ev/entities-mutant-prefix-nightly.txt). The other indented FAIL lines in that log are self-test sub-lines, which the total does not count.
- RESULT my own targeted mutants (ev/targeted-mutants.diff), all killed:
  - m2: approver review POST made a no-op. 3 failed: reviewed-under-hold, the absent/stale null control and the pitch check (ev/entities-m2.txt).
  - m3: the first guard refusal no longer calls dismiss_bot. 1 failed: refused-under-hold (ev/entities-m3.txt).
  - m4: hold age comparison inverted (-gt). 5 failed: the hold arm, the in-test mutant, the bound/future/absent/unreadable null controls, the stale null control and the pitch check (ev/entities-m4.txt).
- Null controls re-run at the head: no hold (422) or a stale hold with the guard and green wait passing returns ('merged', True, False, True); the six non-skipping hold arms return `refused`, and only the two unreadable arms warn. All pass at the head.
- Premise check: tools/audit/seat/merge_train.py:1079-1105, the `--bot-prs` sweep, merges on `record_row.py --automerge-check --require-green` and posts no review, so a beat that skips before the review starves it, as the body states. The reordered step at the head (nightly.yml, `id: automerge`) runs: head read, guard (refusal dismisses), one approver review per head, train hold, pitch, green wait, merge. Only the merge moves main, and it still follows the hold.
- Class rule re-run: `say|exit 0` over the automerge step (ev/class-rule-exits.txt). The exits before the hold are skip-unread (head unreadable), refused, skip-unread (reviews read failed) and skip-review-refused (the POST itself failed). The body lists only the first two; the other two sit inside the review block and cannot skip a review that could be posted, so the class is one seam and closed.
- Figures re-derived: `python tests/structure.py` gives STRUCTURE RATCHET PASSED (ev/structure.txt); `tests/closure.py select` gives `MODE: FULL`, reason `.github/workflows/nightly.yml changes the gate itself` (ev/closure-select.txt). Both match the body.
- VERSION, the manifest version, RELEASE_NOTES.md and tests/golden/ are untouched in the three-dot diff (ev/version-untouched.txt). No claim files, budgets, closures.json or INERT moved, so step 14 has no instrument movement to earn.
- Merge: `git merge-tree --write-tree origin/main c44e95fe` at origin/main beb570c8 gives tree befbef30, rc=0, with no conflict and no claim-driver involvement (ev/merge-tree.txt).
- CI at this head (public check-runs API, all concluded; ev/check-runs.txt, ev/check-runs.json): every check is success or skipped, CodeQL included, and none is red. pr-contract succeeded (123018424778), gate succeeded, and tests/mutation succeeded. The diff touches only a workflow and tests/entities.py, so it writes no production code line for the mutation lane to draw a mutant from. Step 11 owes nothing: there is no red check, and the body's `## Red checks: none` agrees.
- Forward-carry: the body says none. The change alters no later stage's procedure; nudge.md section 6 and dev/README.md's train-hold line stay true under the new order, which I checked against nudge.md:65.
- Architecture (step 15): a move within one step, adding no new approval site or key, the smallest of the triage's options. Sound.
