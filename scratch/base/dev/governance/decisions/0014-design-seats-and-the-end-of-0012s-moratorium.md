# 0014 — Design seats for L and XL groups; decision 0012 is revoked

Status: recorded 2026-10-21 from the repository owner's rulings R16–R19 of that
date (owner ruling 2026-10-21, `dev/programme/flow-study/RULINGS-201-3.md` at
commit `30c57744ad8aab329d0054880fc9a3154262f204`, on branch
`claude/dazzling-gauss-7l3u2b`) and the owner's addendum to R16 (#201 comment
6322712314). Revokes 0012, which is kept as history. Lands as roster group
R10-FLOW-DESIGN-POLICY.

## Context

The Lean flow study's design-seat pre-study (`design-seats/STUDY.md` at the same
commit) measured where design defects surface. Inside a round they are few:
of 148 blocked fix-review verdicts over #2206–#2580, 7 were design-class
strictly and 15 counting `class-open`. After the merge they are many: 49 of
round 10's 123 audit findings came from the architecture dimension (D7, ARCH2
and ARCH3), against 10 of round 9's 143. Its model put the pipelined variant
at no change in the round's completion time at mid settings with a
revalidation box of at most 1 h, about 4% more tokens, about 6% fewer bugs
introduced and about a quarter fewer design-class bugs. It recommended a
round-11 pilot, partly because 0012's moratorium barred new role contracts
until 2026-10-31.

## Decision

1. **0012 is revoked** (R16 and its addendum): no part of it binds a seat,
   its moratorium included, and its file is kept as history only.
2. **Two seats join the process** (R17): the designer
   (`dev/governance/roles/designer.md`) and the design reviewer
   (`dev/governance/roles/design-review.md`). Every roster group of size L or
   XL with no approved design, pre-study or prototype gets a pipelined design
   and design review before its fixer: the designer starts when the group's
   last predecessor dispatches, and the fixer dispatches only after
   `Design review: approve`. The approved note is the group's architect note,
   which `fixer.md` step 17 and `fix-review.md` step 15 bind. Until the
   contracts merge, the seats run on the drafts pinned at the pack commit.
3. **Rationale** (R18): fewer future architecture-dimension findings. The
   owner adopted the seats in round 10 rather than piloting them in round 11,
   for a benefit the in-round model does not credit.
4. **The corpus-cap raise** the two contracts need is approved by the ruling
   (R19); it still merges on the owner's approving review, with its
   `## Raise justification`.

## Consequences

- The revalidation box is a hard 1 h: at 2 h the study's model puts the round
  at 91–94 h against 86 h.
- The study's section 8 kill and keep criteria become the monitoring: median
  revalidation above 1 h, or no first-pass-yield gain after 8 designed groups,
  is a reason to withdraw the seats; design-class blocks and next-round D7
  findings on designed groups falling by a quarter is the reason to keep them.
  The token cost is measured from the seats' own reports where they give one;
  the study found no token figure recorded in the tree.
- Roster stages `design` and `design-review`, the refs `design/<group>` and
  `design-verdict/<group>`, and their dispatch are mechanised by
  R10-FLOW-DESIGN-STAGES; until then they run by hand on the same ref names.
- `dev/governance/decisions/` and `dev/governance/roles/` are `@tvofi`'s in
  `.github/CODEOWNERS`: this record and the two contracts are policy and merge
  on the owner's approving review.

## Approval

Awaiting the owner's approving review.
