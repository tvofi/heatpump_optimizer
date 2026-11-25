Design review: approve d34eaeec5f620fe3e86a7be6a16f5cdcb411a146

Design reviewer, round 4. I read design/R11-OUTSIDE-SELF-SETTING-PUMP at d34eaeec5f from a detached worktree and judged it against base d9100de781. The diff reviewed is `git diff 0acbbc8b91..d34eaeec5f` (design.md only). Nothing was rerun. The section-1 figures are the note's own; the reads below come from the tree at d9100de781 and from handoff/audit-r11-roster at 7ced771ac3.

## Seam, shape, siblings, evidence, cost

- Seam: unchanged from round 3, and the note proposes no change. The citations resolve at the base. coordinator.py:5290 returns `COP_REFUSED_FROZEN` before coordinator.py:5302 calls `owed_scale(..., not experiment)`. accuracy.py:854 defines `PROBE_VOID_CAP = 3`, and accuracy.py:1132 reads it. The predecessors 3f7f29e778, 412ada3942 and 5455c39e21 are all ancestors of the base. `git log 412ada3942..d9100de781` over the three files lists only R11-CARRY-DRAWMAP commits and its merge of main.
- Shape: the note claims nothing beyond the carries. Each round-3 point maps to a check in tests/features.py at the base, found by grep. Three are verbatim: "a replayed interval folds the scale and not the capacity envelope", "a reset mid-probe returns the scale to the base in the same cycle", and "release: no fold lands on a pending heat-ask probe however long it lasts" (features.py:78418, line-wrapped). The fourth is features.py:79341, which reads "... then a frozen cycle or an unread one ...".
- Sibling sites: `git grep -n -e "owed_scale(" -e "PROBE_VOID_CAP" -e "ScaleDither(" -e "\.admit(" -- custom_components` at the base finds accuracy.py and coordinator.py:5302, plus wear.py:172, which is another class. This matches the note.
- Destinations: the note routes the residues to R11-SEAM-learners carries 0 to 3. At roster 7ced771ac3 those carries are items 0116e1a6, dcd51e15, c25b53cc and 4a5e147b, as the note says. design/R11-SEAM-learners (bee723ac4d) takes carry 3 in §3.5 against `cop_dither_fabric.py` with the `null_dither0_*` twins. It takes carry 2 in §9, pending an owner decision. Its house-sample figures (578 and 646 against 671) are the ones in this note. No second design claims this seam: I grepped the 44 other open design/* refs, and only R11-CARRY-DRAWMAP (merged), R11-OUTSIDE-START-APPROACH and R11-SEAM-learners name it. START-APPROACH only reads `scale_response`.
- Evidence and cost: none owed, because the note proposes no change. Owner ruling D4's residual is closed by the gap check: 0 of the 54 `selfset` rows read follows. The heat-led learning that is lost under a re-priced plan is the cost of the fix, not the D4 residual. It is held by R11-SEAM-learners carry 2, which the owner ruling of 2026-11-18 keeps in round 11.

## Decisions routed (not revise points)

- decision: orchestrator. The note asks that no fixer be dispatched and that the group close on its carries. That needs a roster write this seat does not make: carries 5 and 6 marked `[implemented: 412ada3942]` (carry 6 for B1 only), carry 7 marked measured with its residue at R11-SEAM-learners carry 3, and the group's `resume.next_step` ("designer first") cleared.
- decision: orchestrator. design.md at d34eaeec5f no longer contains the round-3 shape or the owner's three decisions of 2026-11-16, though the note says they "stand unchanged". They survive only at 0acbbc8b91 and in this ref's history. If anything later reads design/R11-OUTSIDE-SELF-SETTING-PUMP's head as the design of record, cite 0acbbc8b91 for them.

## Notes for the fixer

- Section 2's quote "two admitted rows then a frozen cycle, an unread one" does not match the check name in the tree, which reads "... a frozen cycle or an unread one ..." (tests/features.py:79341). Anyone who greps the quote finds nothing. Quote the check as the tree has it. Carry: dismissed: no fixer owed (item dr4-a1)
- Section 1's figures are snapshots taken at d9100de781. Re-measure them at the merge base of whichever group builds (c1) or retunes the dither, with null 1 and the gap checks, as the note says. Carry: R11-SEAM-learners (item dr4-a2)
