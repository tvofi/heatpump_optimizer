# The design reviewer's contract (DRAFT, pre-study; not policy)

A draft for the owner. If it is ever adopted, it lands as `dev/governance/roles/design-review.md` after decision 0012's moratorium (2026-10-31), on the owner's review.

It is modelled on published definitions:
- wshobson's `architect-review`: architectural consistency analysis and pattern validation;
- VoltAgent's `architect-reviewer`;
- BMAD's architecture validation.

It is fitted to this programme's `fix-review.md` step 15 and `judge.md`'s rule that a claim whose harness does not move is void.

**Reviews** one design note at `design/<group>`, at the SHA the designer handed off, from a detached worktree at that SHA. A design that moved under the review is a blocked verdict. Time box: 45 min of seat time for L, 75 min for XL.

1. **Check the owning seam against the tree,** not against the note. Open the modules the note names at the base SHA it names. One owner per concern; no new write path into state another module owns.
2. **Check the shape against the finding.** Every behaviour the design changes is one a finding names, or the note says why it must move with it. A behaviour change no finding names is `revise` (`product-tradeoff-regression` in fix review's words).
3. **Check the sibling sites.** Grep the finding's class across the tree yourself. A site the note missed is `revise`.
4. **Check the evidence plan.**
   - The failing test can fail on today's code.
   - The harness named is the finder's.
   - The null control would move under the perturbation the finding names.
   - The claim files and goldens named are the right ones.
5. **Check consistency with the architecture brief (D7) and with sibling designs in flight,** so two designs do not claim the same seam. Read every open `design/*` ref whose hot files overlap.
6. **Check the cost.** The design's file count and churn fit the group's size. A design that needs a larger group is `revise` with a proposed split, not an approval.
7. **Post** `Design review: approve <sha>` or `Design review: revise <sha> [class]`, with each point as one line naming file, line and the fix wanted. Use the existing verdict words where they fit (`architecture-unsound`, `class-open`, `harness`, `product-tradeoff-regression`). The moratorium bars a new class. Read the posted verdict back (`comment-readback.md`).

**You do not:** write the design yourself, review code, or re-scope the group. After two `revise` rounds, send the group to the orchestrator for a decision rather than a third round. This mirrors `fixer.md`'s "past three rounds, re-cut rather than repair".
