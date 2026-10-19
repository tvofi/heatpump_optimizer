---
description: A finding that changes how a later stage must work goes into that stage's own brief before the PR that produced it merges
paths:
  - "dev/governance/**"
  - ".claude/workflows/*.json"
  - "dev/programme/rosters/*.json"
  - "dev/programme/carries/*.json"
---
# Forward-carrying a finding

**A finding that changes how a later stage must work is written into that
stage's own brief before the PR that produced it merges.**

## When it applies

The finding must be **established by measurement with its null control** — the
perturbation that would have made it fail — not by argument. An unverified
observation is not carried; it is measured first or dropped.

Given that, it applies whenever the finding does any of three things to a stage
that has not started:

- **narrows what that stage may do** — a technique it was expected to use is
  refused, or is now legitimate only under a precondition;
- **invalidates an assumption it rests on** — a figure, a partition, an
  environment, a tool version it was scored against turns out not to hold;
- **removes an option it was expected to have** — a dependency will not install,
  a budget it was to spend has been spent, an interface is not available.

No threshold of "importance" gates this, the adjective a seat under time
pressure argues its way out of: if it changes what a later stage must do, it is
carried.

## A comment is not propagation

**A PR comment, an issue comment, and the record are not propagation.** They
<<<<<<< HEAD
record the finding; they do not deliver it. The test is **where the seat who
needs this will be looking**: its own brief, the role contract under
`dev/governance/roles/`, `CLAUDE.md`. A finding that lives only in the PR that
produced it will be re-derived by the next stage, or — the usual outcome — not
derived at all, and the refused technique gets attempted again.
=======
record the finding; they do not deliver it. The test is **where the seat who needs this will be looking**: its own brief, the
role contract under `dev/governance/roles/`, `CLAUDE.md`. It will not read the comments
of a PR that merged stages before it started. A finding left only in its PR
is re-derived by the next stage or, usually, not at all, and the refused
technique is attempted again.
>>>>>>> origin/main

## What to write

- **Carry the control, not only the claim.** The next stage needs the
  measurement that separates the real thing from its imitation. A conclusion
  without its control cannot be checked, or re-established after a rebase.
- **State the precondition, not the opportunity.** "This lever gained N points"
  invites the next seat to reach for it. "This lever is legitimate only when X,
  demonstrated per case" is what keeps the next stage honest. Where a technique
  was refused, name the refusal and what it turned on.
- **Give the numbers a re-measurement instruction.** Figures carried into a
  brief are snapshots; the stage is judged against its own merge-base.

## Where it goes

- **Constrains one stage** → that stage's brief. **A stage's brief lives in two
<<<<<<< HEAD
  places, and both must receive it**: a live group's `brief` string in the
  roster under `dev/programme/rosters/`, which the linter and the next
  session read; and any out-of-tree brief file a running
  session hands its seats. Carrying to the scratch copy alone leaves the tree
  unchanged, and the tree is what survives the session.
=======
  places, and both must receive it**: a live group's `brief` string in its
  roster, the round's under `dev/programme/rosters/` or a web-fix-wave
  `groupsFile` under `.claude/workflows/`, which the next session reads; and
  any out-of-tree brief file a running session hands its seats. Carrying to the
  scratch copy alone leaves unchanged the tree, which is what survives the session.
>>>>>>> origin/main
- **Constrains every seat** → the **role contract** it belongs to under
  `dev/governance/roles/` (`fixer.md`, `fix-review.md`, `judge.md`), **once**:
  every seat of that role reads it. Do not copy it into each stage's brief:
  duplication goes stale unevenly, and a reader who finds two versions trusts
  neither.
- **The stage has no live roster group** → its own `dev/programme/carries/carry-<N>.json`,
  N the destination issue, and **creating it is part of the finding**. A group
  at `resume.stage: done` is not a destination: nothing dispatches or lints it.
  `brief_lint.mjs` states the fields and refuses a carry at an issue a live
  group covers, so no stage has two destinations.
<<<<<<< HEAD
- **A sibling seam in the same stage** — an open seam the enumeration rule
  returns (`fixer.md` step 8) — goes to **a new issue filed by the same pull
  request**, or a carry file under the branch above. The destinations this rule
  names are stages that have not started, so a seam in the running stage has
  none: that is how the fifth seam escaped #1345.
=======
- **A sibling seam in the same stage** — an open seam the enumeration rule returns
  (`fixer.md` step 8) — goes to **a new issue filed by the same pull request**, or a
  carry file under the branch above. This rule's other destinations are stages
  not yet started, so a running stage's seam has none (#1345's fifth seam).
>>>>>>> origin/main

**While two copies disagree, the newer one is right and the other is the bug.**
Say which is which in the carry, so a seat finding its brief and roster in
conflict need not guess; the out-of-tree copy needs no pull request, so it is
usually the newer.

## Enforcement

<<<<<<< HEAD
The producing PR does not merge until the carry is **in the tree**. **Every
finding a body or a `Fix review:` verdict records names its destination**, so a
reviewer opens it rather than taking the claim: each `## Friction` and
`## Forward-carry` line, non-blocking note, residual or out-of-scope item
carries `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>`.
`tools/audit/carry_audit.py` refuses a missing marker and a destination gone or
done — a roster group not live, an issue no live group, carry file or
O-brief owns: `pr-contract` on the body, the train's pre-flight on verdicts.

**Verify the write landed.** A scripted edit matching nothing reports
success — `str.replace` and `sed` both do; this rule first landed with seven of
nine carries missing that way. Read the destination back:
`brief_lint.mjs` does it for a roster and a carry file, and for a role
contract nothing does.
=======
The producing PR does not merge until the carry is **in the tree**; a carry to
the round's roster, once on its branch `handoff/audit-r<N>-roster` (tvofi,
2026-10-18), which lands on main at each stamp and before branch cleanup
and stays while `git diff origin/main...<branch> -- dev/programme/rosters/`
prints anything. The body names the file, the stage and (a roster carry) the
branch SHA: the reviewer opens that, not the claim.

**Name a destination that exists.** A carry pointing at a file `git grep` cannot
find is not a carry, and a rule that makes an unfindable destination a merge
blocker is worse than no rule: the seat cannot comply, nor the reviewer check.

**Verify the write landed, do not assume it.** A scripted edit that matches
nothing reports success — `str.replace` and `sed` both do; this rule first
landed with seven of nine carries missing. Read the destination back:
`brief_lint.mjs` does it for a roster and a carry file, and for a role contract
nothing does.
>>>>>>> origin/main
