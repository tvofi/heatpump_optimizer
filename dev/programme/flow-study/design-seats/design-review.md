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
7. **Post** `Design review: approve <sha>` or `Design review: revise <sha> [class]`, with each point as one line naming file, line and the fix wanted. Use the existing verdict words where they fit (`architecture-unsound`, `class-open`, `harness`, `product-tradeoff-regression`); no new class is needed. Read the posted verdict back (`comment-readback.md`).

**You do not:** write the design yourself, review code, or re-scope the group.

**Notes for the fixer are findings, not revise points.** An implementation hint, a test to add, or an edge case for the fixer to cover goes into the design note's "Notes for the fixer" section as a carried observation (`Carry: <group> (item <id>)`). The fixer and fix review own it from there. `revise` is only for a defect in the design itself: the owning seam, the shape, the sibling sites, the evidence plan, or the cost. Live: R10-SCORES went 8 → 4 → approve over three rounds, and each round also produced fixer notes. Counting those as revisions would have held it open.

**Decisions are routed, not revised.** A point only the orchestrator or owner can settle (scope, ordering, a product trade-off) is marked `decision: orchestrator` or `decision: owner`. It goes to them in the first round and does not count as a revise point.

**Three notes at most**, as in `fixer.md`'s "past three rounds, re-cut rather than repair". If the third note still draws `revise`, there is no fourth: the designer re-cuts to the minimal shape the fixer can start from, and the remaining points become carries. Live: R10-SCORES took 8, then 4 revise points, at about 20 min per review round.
