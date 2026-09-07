---
description: A finding that changes how a later stage must work goes into that stage's own brief before the PR that produced it merges
paths:
  - "tools/audit/briefs/**"
  - ".claude/workflows/*-groups.json"
  - "docs/plan*.md"
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

Deliberately, no threshold of "importance" gates this. That adjective is the one
a seat under time pressure argues its way out of, and the three effects above
already carry the whole test: if it changes what a later stage must do, it is
carried.

## A comment is not propagation

**A PR comment, an issue comment, and the record are not propagation.** They
record the finding; they do not deliver it.

The test is **where the seat who needs this will be looking**: its own brief, the
role contract under `tools/audit/briefs/`, `CLAUDE.md`. It will not read the comments
of a PR that merged several stages before it started. A finding that lives only
in the PR that produced it will be re-derived by the next stage, or — the usual
outcome — not derived at all, and the refused technique gets attempted again.

## What to write

- **Carry the control, not only the claim.** The next stage needs the
  measurement that separates the real thing from its imitation. A conclusion
  without its control cannot be checked, and cannot be re-established after a
  rebase.
- **State the precondition, not the opportunity.** "This lever gained N points"
  invites the next seat to reach for it. "This lever is legitimate only when X,
  demonstrated per case" is what keeps the next stage honest. Where a technique
  was refused, name the refusal and what it turned on.
- **Give the numbers a re-measurement instruction.** Figures carried into a
  brief are snapshots; the stage is judged against its own merge-base.

## Where it goes

- **Constrains one stage** → that stage's brief. **A stage's brief lives in two
  places, and both must receive it**: the roster `brief` string in
  `.claude/workflows/wave-*-groups.json`, which is in the tree and is what the
  linter and the next session read; and any out-of-tree brief file a running
  session hands its seats. They are separate destinations, not one — carrying to
  a session's own scratch copy leaves the tree unchanged, and the tree is what
  survives the session.
- **Constrains every seat** → the **role contract** it belongs to under
  `tools/audit/briefs/` (`fixer.md`, `fix-review.md`, `judge.md`), **once**.
  That is the in-tree file every seat of that role reads, so it is the
  destination a reviewer can open. Do not copy it into each stage's brief:
  duplication goes stale unevenly, and a reader who finds two versions trusts
  neither. If the session also runs an out-of-tree shared block, that is a
  convenience copy of the contract and never the only home.
- **The stage has no brief yet** → the plan row that will become one, and
  **creating that row is part of the finding**. A rule that silently does not
  apply to unplanned work fails precisely where unplanned work needs it most.

**While two copies disagree, the newer one is right and the other is the bug.**
Say which is which in the carry itself, because a seat that finds a conflict
between its brief and the roster must not have to guess. The out-of-tree copy
can be updated in a minute with no PR, so it will usually be ahead; the record
PR that follows the merge brings the tree level.

## Enforcement

The producing PR does not merge until the carry is **in the tree**. Its body
names the file and the stage that received it, so a reviewer opens the
destination rather than taking the claim.

**Name a destination that exists.** A carry pointing at a file `git grep` cannot
find is not a carry, and a rule that makes an unfindable destination a merge
blocker is worse than no rule — the seat cannot comply and the reviewer cannot
check. If the right destination does not exist yet, creating it is part of the
carry.

**Verify the write landed, do not assume it.** A scripted edit that matches
nothing usually reports success — `str.replace` and `sed` both do — so the
check is to read the destination back and confirm the text is there. Asserting
that the anchor was findable is not the same as asserting the edit was made,
and this rule was itself first landed with seven of nine carries missing for
exactly that reason.
