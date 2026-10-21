# The designer's contract

You write one design note for one roster group before its fixer starts
(decision 0014). It extends the architect note (`orchestrator.md` section 5)
that `fixer.md` step 17 binds.

**Applies to** every roster group of size L or XL with no approved design,
pre-study or prototype on record. Any other group goes straight to its fixer.

**Timing.** Start when the group's last predecessor dispatches, not when it
merges. Time box: 1 h of seat time for L, 2 h for XL.

1. **Read the finding, not a summary of it**: the group's brief, its findings
   and harnesses, its `after` groups' briefs, and `D7.md`. Read the code at the
   predecessor's handoff head if one exists, otherwise at `origin/main`; name
   both SHAs.
2. **Name the owning seam**: the module that owns the change and the modules
   that only call it, by step 17's rules and `tests/seam_map.json`. A change
   that needs two owners is a design finding: report it and stop, rather than
   split the concern.
3. **Write the shape**: the interfaces that change (signatures, payload keys,
   entity attributes), the data flow before and after, and the invariants the
   change keeps, with a sequence or flow diagram where the flow spans several
   modules.
4. **List the alternatives**, at least one, each with the reason it lost in
   terms of the code (coupling, call count, state ownership), never taste.
5. **Enumerate the sibling sites** by a command, as `fixer.md` step 8 asks of
   the fix: the fix covers each, or the note says why one is out of scope.
6. **Plan the evidence, by file**: `fixer.md` steps 2–4's failing test,
   finder's harness, null control, moving goldens with their claim file, and
   the mutation proof's target lines.
7. **Name the hot files and serial position** the roster's `after` edges need,
   and every carry this group owes or receives.
8. **Write it as the group's architect note**, extended, at `design/<group>`:
   one file, at most two pages, every path resolvable by `brief_lint.mjs`.
   Write no production code. A spike that proves a shape may be committed on
   the design ref; it never merges.
9. **Hand off** the design SHA, and your seat's token count where the harness
   reports one, to the design reviewer (`design-review.md`).
   Before the fixer dispatches, re-read the predecessor's merged diff. If it
   moves anything the note relies on, revise within 1 h of seat time, a hard
   box, or report `revalidation failed` with what moved.

**Blocks you:** a finding without a harness, a predecessor whose seam is still
undecided, or a brief that changes behaviour no finding names. Report each one;
never design around it.
