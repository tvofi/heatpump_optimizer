# BLOCKED: r10-docs-strings-residue-p2 (PR 3580), repair round

Question: PR 3580's content is already on main, so its diff is empty. Close it as landed through #3562, or hand off something else?

Measured against origin/main 237fad44532d1927cf65612d395cc5833c60ce99 on 2026-11-14:

- `git merge-base --is-ancestor <c> origin/main` succeeds for d0963ece7f, 3047b48a3e and ec9645014c (the head the merge verdict was posted at). It fails only for a27666c2a7, the orchestrator's automatic merge of main cbc42e0.
- They reached main through #3562's branch: 066e497fbd "Merge PR 3580 head ec96450 into R10-HOTFIX-BOOST-FLOW-CEILING (stacked)", merged as 237fad4453.
- `git merge-tree --write-tree origin/main a27666c2a7` exits 0 with tree 8d98786a43, which equals `origin/main^{tree}`. Control: the same command at the merge base cbc42e0 gives a 9-file diff (strings.json, en, de, sv, docs/configuration.md, docs/dashboard-card.md, docs/setup.md, tests/doc_claims.py, dev/programme/delivery/3580.md).
- Merging origin/main into a27666c2a7 (local commit, not pushed) gives an empty `git diff origin/main HEAD`. `tests/closure.py select` answers `MODE: FULL -- reason: no changed files could be determined`. `tests/doc_claims.py` at that merge: `ALL 386 checks PASSED`, so main carries this PR's carry 5-13 pins green.
- GitHub's `mergeable_state: dirty` is not a textual conflict. A trial `git merge` of 237fad4 into a27666c2a7 with the custom drivers disabled completes automatically.

I made no code change and pushed nothing to handoff/ or handoff-body/. The PR body's `## Forward-carry` (carry 12 to R11-INTAKE-R10-RESIDUE, items a0e752f6) is unaffected by this question.
