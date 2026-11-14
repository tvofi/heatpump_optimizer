Fix review: merge 3ab3d5b5ab4b21d147977652f14d5cf0de280006

bus-nonce: 6200efa5a1b3f398b738401673560a82
pending-ci: gate

## Scope

Round: a later round over the reviewed head fd5fe52fa788805433e1f1fe36b1824e0943838e, scoped by the dispatch brief to the conflict resolution of the stacked hand-merge (PR 3580 ec9645014c, PR 3576 8317d9e1b2, PR 3569 57ee4591d0, then the clean merge 3ab3d5b5ab). The review packet printed `Review scope: full` only because no verdict on verdict/3532 names fd5fe52; the brief's delta scope governs. The three merged train heads are reviewed PRs and are not under review here. No production delta widens the scope: duty_switch.py's delta from fd5fe52 is the docstring alone, and away.py's delta is PR 3576's own clean-merged change, which touches nothing this PR adds.

## Evidence

- Remerge diffs (`git show --remerge-diff`, ev/remerge-*.txt): abb8c7fc66 resolves strings.json and de/en/sv; fa3e6f2a5c resolves sv.json; 411f54ea8d resolves the duty_switch.py docstring; 3ab3d5b5ab has none, a clean merge.
- Whole-tree oracle (ev/tree-oracle.txt): at each merge, the committed tree differs from `git merge-tree --write-tree` of its two parents only in the conflicted files, and only by the 5 marker and losing-side lines per hunk. The final merge's tree equals merge-tree(fd5fe52, 411f54ea8d) exactly.
- Key-level oracle (ev/oracle.txt): I took a leaf-level 3-way union of every train head over its merge base with fd5fe52 and compared it to the head for strings.json and de/en/sv. Each file has 1507 leaves and 0 mismatches. The one overlap is sv space_setpoint_unit, which both 3580 and 3576 change from their shared ancestor c79e44e. The head carries 3576's later text ("framledningsentitet", "från entiteten"), which supersedes 3580's, and that is the correct resolution. This oracle is my own script, not the merger's check-3532-oracle.txt, which this seat cannot reach.
- PR-owned keys (ev/prkeys.txt): in each of the four files, the only PR-owned leaf is data_description.space_setpoint_entity, and it is byte-equal to fd5fe52 at the head. The train's space_setpoint_unit sits beside it. That is a union, as the brief states.
- duty_switch.py docstring: the kept sentence from 3569 is true of the merged code. At the head, Direction.decay sets `factor = min(self.weights(when)[1], N_CAP) / n`, which caps on every decay, including a zero-age one. Direction.book sets `scale = min(1.0, N_CAP / self.n)`, scaling k and kept_w alike. Direction.from_row never caps, and it accepts k and kept_w up to `_N_MAX` = 1e6. DutySwitchLearner.note_pass calls decay on every direction on each pass, so a record stored over N_CAP is held to N_CAP by the first pass. The merger's reading is confirmed on all three methods. The code itself is unchanged from fd5fe52; only the docstring moved.
- Cap pins run at the head with `PYTHONPATH=tests/hastub python3 tests/features.py` (ev/features-wt.txt): EXIT 0, with no FAIL line and 5724 ok lines.
- RESULT mutant decay-cap-dropped (ev/mutant-decay.diff, `factor = self.weights(when)[1] / n`): EXIT 1, 2 FAIL. These are "n has a ceiling: …" and "the cap is held on decay as well as at booking: a record stored at four times the cap is held to it by the first pass …". The docstring's sentence is pinned.
- RESULT mutant book-cap-dropped (ev/mutant-book.diff, `scale = 1.0`): EXIT 1, 4 FAIL. These are "n has a ceiling …", "the decayed count is held at the cap …", "the cap scales both counts alike …" and "from p = 1 at the cap the latch holds after twelve …".
- Merge with main: `git merge-tree --write-tree origin/main 3ab3d5b5ab` at origin/main a77d71fb75 returned rc=0, with no conflict (ev/merge-tree.txt).
- VERSION and the manifest are untouched between the merge base and the head.
- CI: `merge_train.py classify 3ab3d5b5ab… --pr 3532` printed `WAIT 3ab3d5b5ab4b21d147977652f14d5cf0de280006 pending: gate red: none` on every run from 10:59 to 11:32 UTC (rc=3, ev/classify.log). No required red has been read, so no `## Red checks` answer is owed at this point.
- carry_audit check: rc 0 (`CARRY-AUDIT: 0 finding item(s)`) over this verdict; the PR body was read through the packet's own run at the head, which printed 0 finding items.
- Head re-read before return: refs/heads/fix/r10-duty-switch-restart-learning-pr-b-p2 is still 3ab3d5b5ab4b21d147977652f14d5cf0de280006.

## Findings

- The PR body is not accurate at this head. Its `## Head` section says the code "was already in it and main merged cleanly" and does not name the three train-head merges this head contains. The body also repeats its `## Mutation proof` through `## Unpinned sites` sections after a garbled `## Red checks`).` line. This is a body defect, and the orchestrator's script sets that body. Carry: dismissed: body text owned by the orchestrator's body script, outside this resolution review's scope; no code effect
