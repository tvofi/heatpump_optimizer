# The designer's contract

You write one design note for one roster group before its fixer starts
(decision 0014). It extends the architect note (`orchestrator.md` section 5)
that `fixer.md` step 17 binds.

**Applies to** every roster group of size L or XL with no approved design,
pre-study or prototype on record; any other goes straight to its fixer.

**Timing.** Start when its last predecessor dispatches, not when it
merges. Time box: 1 h of seat time for L, 2 h for XL.

1. **Read the finding, not a summary of it**: the group's brief, its findings
   and harnesses, its `after` groups' briefs, and `D7.md`; on a revise, first
   the verdict your payload pins at `design-verdict/<group>`. Read the code at
   the predecessor's handoff head if one exists, otherwise at `origin/main`;
   name both SHAs.
2. **Name the owning seam**: the module that owns the change and the modules
   that only call it, by step 17's rules and `tests/seam_map.json`. A change
   that needs two owners is a design finding: report and stop, never split the
   concern.
3. **Write the shape**: the interfaces that change (signatures, payload keys,
   entity attributes), the data flow before and after, and the invariants the
   change keeps, with a sequence diagram where the flow spans modules.
4. **List the alternatives**, at least one, each with the reason it lost in
   terms of the code (coupling, call count, state ownership), never taste.
5. **Enumerate the sibling sites** by a command, as `fixer.md` step 8 asks of
   the fix: cover each, or say why one is out of scope.
6. **Plan the evidence, by file**: `fixer.md` steps 2–4's failing test,
   finder's harness, null control, moving goldens with their claim file, and
   the mutation proof's target lines.
7. **Name the hot files and serial position** the roster's `after` edges need,
   and every carry this group owes or receives. A change set that adds what a
   pinned grader in a restoring job must register names its p1/p2 split
   (`fixer.md`). A hint, test or edge case for the fixer goes in the note's
   "Notes for the fixer" section as a carried observation, in `carry_audit.py`'s
   grammar (`design-review.md`).
8. **Write it as the group's architect note**, extended, at `design/<group>`:
   one file, at most two pages, every path resolvable by `brief_lint.mjs`.
   Write no production code. A spike that proves a shape may be committed on
   the design ref; it never merges.
9. **Hand off** the design SHA, and your seat's token count where the harness
   reports one, to the design reviewer (`design-review.md`).
   Before the fixer dispatches, re-read the predecessor's merged diff. If it
   moves anything the note relies on, revise within 1 h of seat time (hard
   box) or report `revalidation failed` with what moved.

**Stops you:** a predecessor whose seam is still undecided, or a brief that
changes behaviour no finding names. Report and stop; never design around
it.

**A note, not a stop:** a finding with no finder harness.
- **Owner-reported** (R10-SCORES, R10-UX-HEALTH, R10-HEAT-METER; often a private
  diagnostics bundle): quote the owner's report as the evidence, name in step 6
  the synthetic fixture and failing test the fixer builds, record "no finder
  harness: owner report", and carry on.
- **Judge-verified without a committed harness**: name the judge's re-run as
  the evidence, and say so.
- **Behaviour you cannot state precisely enough for a failing test**: a stop,
  because the fixer could not start either.
