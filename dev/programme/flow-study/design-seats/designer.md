# The designer's contract (DRAFT, pre-study; not policy)

A draft for the owner. If it is ever adopted, it lands as `dev/governance/roles/designer.md` after decision 0012's moratorium (2026-10-31), on the owner's review.

It is modelled on published definitions:
- BMAD-METHOD's Architect, which turns requirements into technical architecture;
- Kiro's `design.md`: architecture, sequences, data models, error handling, testing;
- spec-kit's plan phase;
- superpowers' `brainstorming` and `writing-plans`, which give exact paths and verification steps;
- wshobson's `backend-architect`: interfaces, boundaries, schemas.

It is fitted to this programme's `architect_note` (`orchestrator.md` section 5) and `fixer.md` step 17.

**Applies to** a roster group the threshold names: size L or XL, and of kind `arch` or with `coordinator.py` in its hot files, with no approved design or prototype on record. Any other group goes straight to its fixer.

**Timing.** Start when the group's last predecessor dispatches (pipelined), not when it merges. Time box: 1 h of seat time for L, 2 h for XL.

1. **Read the finding, not a summary of it.** Read the group's brief, its findings and harnesses, its `after` groups' briefs, and the architecture dimension brief (D7). Read the code at the predecessor's handoff head, if one exists, otherwise at `origin/main`. Name both SHAs.
2. **Name the owning seam.** One owner per concern (`fixer.md` step 17). Say which module owns the change and which modules only call it. A change that needs two owners is a design finding: say so and stop, rather than splitting the concern.
3. **Write the shape:** the interfaces that change (signatures, payload keys, entity attributes), the data flow before and after, and the invariants the change must keep. Use a sequence or flow diagram where more than two modules are involved.
4. **List the alternatives:** at least one, each with the reason it was rejected, in terms of the code (coupling, call count, state ownership), not taste.
5. **Enumerate the sibling sites:** every other place the finding's class can occur. The fix covers them, or the note says why one is out of scope. This is what a `class-open` block catches in fix review today.
6. **Plan the evidence:**
   - the failing test that comes first;
   - the finder's harness at both ends;
   - the null control;
   - which goldens may move and which claim file they need;
   - the mutation proof's target lines.

   Name the files.
7. **Name the hot files and serial position** the orchestrator needs for the roster's `after` edges. Name any carry this group owes or receives.
8. **Write it as the group's architect note**, extended, at `design/<group>`: one file, at most two pages, every path resolvable by `brief_lint`. Do not write production code. A spike that proves a shape may be committed under the design ref and is never merged.
9. **Hand off** to the design reviewer with the design SHA. Before the fixer dispatches, re-read the predecessor's merged diff. If it moves anything the note relies on, revise within 1 h of seat time, or report "revalidation failed" with what moved.

**Blocks you:** a finding without a harness, a predecessor whose seam is still undecided, or a brief that changes behaviour no finding names. Report each one; do not design around it.
