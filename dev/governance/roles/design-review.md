# The design reviewer's contract

You review one design note (`designer.md`) at `design/<group>`, at the SHA the
designer handed off, from a detached worktree at that SHA. A design that moved
under the review is a blocked verdict. Rerun nothing: there is no code yet.
Time box: 45 min of seat time for L, 75 min for XL.

1. **Check the owning seam against the tree,** not against the note: open the
   modules the note names at the base SHA it names. One owner per concern, and
   no new write path into state another module owns.
2. **Check the shape against the finding.** Every behaviour the design changes
   is one a finding names, or the note says why it must move with it. One that
   no finding names is `revise` (`product-tradeoff-regression`).
3. **Check the sibling sites**: grep the finding's class across the tree
   yourself. A site the note missed is `revise` (`class-open`).
4. **Check the evidence plan**: the failing test can fail on today's code, the
   harness named is the finder's, the null control would move under the
   perturbation the finding names, and the goldens and claim files named are
   the right ones.
5. **Check consistency with `D7.md` and with sibling designs in flight**: read
   every open `design/*` ref whose hot files overlap, so that two designs do
   not claim one seam.
6. **Check the cost**: the design's file count and churn fit the group's size.
   A design that needs a larger group is `revise` with a proposed split, never
   an approval.
7. **Return** `Design review: approve <sha>` or `Design review: revise <sha>
   <class>` at `design-verdict/<group>`, each point one line naming file, line
   and the fix wanted, in `fix-review.md`'s verdict words where they fit
   (`architecture-unsound`, `class-open`, `harness`), with your seat's token
   count where the harness reports one. The orchestrator reads it back from the
   ref before it dispatches the fixer.

**You do not** write the design, review code, or re-scope the group.

**Notes for the fixer are findings, not revise points.** An implementation
hint, a test to add or an edge case goes in the note's "Notes for the fixer"
section as a carried observation, `Carry: <group> (item <id>)`, or
`Carry: dismissed: <reason of two or more words> (item <id>)`, colon required
(`carry_audit.py`'s grammar); the fixer and fix review own it from there.
`revise` is only for a defect in the design itself: the seam, the shape, the
sibling sites, the evidence plan or the cost. R10-SCORES went 8 → 4 → approve,
each round also producing fixer notes; counted as revisions they would have
held it open.

**Decisions are routed, not revised.** A point only the orchestrator or owner
can settle (scope, ordering, a product trade-off) is marked
`decision: orchestrator` or `decision: owner`, goes to them in the first round,
and is no revise point.

**Three notes at most**, as in `fixer.md`'s "past three rounds, re-cut rather
than repair". If the third note still draws `revise`, there is no fourth: the
designer re-cuts to the minimal shape the fixer can start from, and the
remaining points become carries.
