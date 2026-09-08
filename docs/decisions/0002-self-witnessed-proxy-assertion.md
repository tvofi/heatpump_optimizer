---
status: accepted
supersedes: []
superseded-by: []
---

# 0002 — A check whose only witness is its author's model of it

## Why this is a root-cause analysis and not a fix

The enforced trigger in `defect-root-cause.md` is a red check, and this class
never turned one red: every instance was found by an adversarial reader, before
the branch merged. What applies instead is the recurrence rule — at roughly the
third instance of an error, the answer is this seat rather than another fix.
The class is at seven.

`defect-root-cause.md` records the analysis on the qualifying defect's issue.
This one is recorded here instead, because the defect is a property of the
linter's acceptance rather than of a shipped behaviour, and the countermeasure
is in the same tree; the audit's tracking issue names this file rather than
carrying a second copy that would drift from it.

## The seven

All in `.claude/workflows/policy_lint.mjs`'s acceptance, over two days. Each
subject is the commit that repaired the one above it, which is why the list
reads as one defect being chased rather than seven unrelated ones. None of these
SHAs is reachable from `main`: the first six squash-merged as #614 and the last
belongs to #615, and citing a commit that no longer exists on the default branch
is the dead-citation class this audit removes, so the pull request is the
durable name.

    a706193  checkCoverage lands. Its acceptance tests the POLICY_GLOBS
             patterns, not the function; emptying the function is invisible.
    0bc152f  first repair: the probe drives the real function
    3f2dfc4  the pin asserted list membership; membership was not the property
    6091080  the pin asserted the wrapper's NAME; a `return []` body kept it
    90d7779  the harness swapped a production binding and so could not see its
             production default, which `() => []` would have voided silently
    777714f  the pin asserted a SPELLING (`!== null`); the property is "the
             value coalesces away", and `() => {}` was refused wrongly
    9c48ee7  three of four budget cap comparisons land with no witness at all

Repaired at `fa5b8a1` (this branch), which also added `checkNamedDocs` and gave
it a witness in the same commit — the first instance where the shape was
anticipated rather than found.

## The cause

**A property that is false on a healthy tree has no natural witness, so the
author writes down a model of the check and pins the model.** The model and the
check are authored at the same moment, from the same understanding, so the pin
agrees with the check by construction. It does not test it.

Every one of the seven is that substitution, at a different distance from the
function: the glob patterns instead of the function, the list instead of the
call, the name instead of the body, the swapped binding instead of the default,
the spelling instead of the property, and — in the caps — no substitute at all,
because a corpus that exceeds no cap makes all four comparisons false at once
and none of them observable.

The repository's own standard was followed each time. `defect-root-cause.md`
requires a detector be demonstrated failing; the demonstrations were run, and
they passed, because a demonstration derived from the author's model of the
check tests that model.

## Process state: (c), followed and did not produce the intended result

Not (b). "Demonstrate the detector failing" was obeyed in all seven, and the
mutation used was the one the author believed disabled the check. The
instruction is silent on where the mutation comes from, and that is the gap: a
mutation the author chooses is part of the model under test.

## The cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per
occurrence.

    standing cost   0.35s per governance run, 0.35s per prepr.sh run, measured
                    three times (342, 345, 366 ms). The lane runs the acceptance
                    only, never the corpus, so it is CHEAPER than the lint pass
                    beside it, which takes 1.605s.
    maintenance     0. The enumeration is read from production's own
                    CORPUS_CHECK_NAMES, so a check added later is mutated by
                    this lane on the pull request that adds it, with no edit
                    here. A second copy of that list would be this same defect
                    one level up.
    cost(defect)    one adversarial review round each, seven times in two days.
                    The branch that produced four of them ran seven rounds.
    P(recurrence)   measured, not estimated: 7 in 2 days, and the corpus check
                    count went 3 -> 5 over the same window, so the surface is
                    growing.

## Decision

Build `.claude/workflows/policy_lint_mutants.mjs`: for each name in production's
`CORPUS_CHECK_NAMES`, empty that function's return, run the REAL acceptance, and
demand a refusal. The mutation is not the author's choice — it is the same
mutation for every check, and it is the one every instance above turned out to
survive.

Three verdicts, never two. `PIN` (the acceptance refused it), `ACCEPTED` (the
check is deletable in silence), `CRASH` (the anchor did not resolve, or the
acceptance threw). A lane that reported "not pinned" for a mutation it never
applied would be the same defect again, so an unmeasured check is a failure and
says which of the two it is.

A null control runs first: the unmutated acceptance must return 0. On a tree
where the acceptance is already red, every mutant is "detected" for free.

## What it does not cover, measured rather than inferred

Its granularity is the wired entry point, so it covers a check that reports
nothing. Emptying `coverageOverTree` subsumes emptying `checkCoverage`, because
a wrapper returns what its implementation returns — delegation is covered.

Three of the seven are outside it and keep the witnesses that were built for
them: `90d7779` is a production binding's default rather than a check;
`777714f` is a pin that asserted the wrong property, which no mutation of the
production function can expose; and `9c48ee7` is a comparison INSIDE a check
whose other arms still fired, so the function kept returning findings. That last
is what `assertAcceptance`'s `capClasses` loop is for. Removal from the wired
list is covered by the existing `wiredNames` pin, not by this lane.

Stating this is the point. The failure mode being remedied is a check believed
to cover more than it does.

## Evidence: shown failing on the defect, and passing once fixed

Failing, on the tree where the first instance lived. `checkCoverage` emptied at
`a3dab2e`, byte-identical output to the clean run:

    clean   rc=0   FIXTURE ok: 29 error(s) hold 19 pins across 7 check classes
    mutant  rc=0   FIXTURE ok: 29 error(s) hold 19 pins across 7 check classes

Failing on today's tree, with one witness removed. Deleting the 22-line
named-docs drive block from `assertAcceptance` and running the lane:

    PIN      checkIndex          FIXTURE VACUOUS: check 'index' produced 0 ...
    PIN      checkDuplicates     FIXTURE VACUOUS: check 'duplicates' produced 0 ...
    PIN      checkBudgets        FIXTURE VACUOUS: the 'file' budget comparison ...
    PIN      coverageOverTree    FIXTURE VACUOUS: checkCoverage did not report ...
    ACCEPTED namedDocsOverTree   the acceptance returned 0 with this check
                                 reporting nothing at all
    rc=1

Exactly one verdict moved, and it is the one whose witness was removed. Passing
with the block restored: rc=0, all five `PIN`.

The `CRASH` verdict is reachable, not decorative. Rewriting a check as
`const checkDuplicates = (files) => {` gives:

    CRASH    checkDuplicates     the anchor `function checkDuplicates(` matched
                                 0 time(s), expected exactly 1; nothing was
                                 mutated

A signature merely broken across lines still mutates correctly and reports
`PIN`, because a JavaScript character class matches newlines.

Null control on `main` at `2b5e416`, where all three corpus checks of the day
were genuinely pinned — each empty-return mutant is refused there, so the lane
is not simply reporting that old trees fail:

    checkBudgets     rc=1   check 'budgets' produced 0 error(s), 2 required
    checkIndex       rc=1   check 'index' produced 0 error(s), 2 required
    checkDuplicates  rc=1   check 'duplicates' produced 0 error(s), 1 required

## The claim that the enumeration costs nothing, tested by an event rather than asserted

Two checks were added to `policy_lint.mjs` after this lane was written —
`checkOrphanCaps`, closing an escape the #615 review found, and
`checkProvenance`. Neither touched this file. The lane picked up both from
`CORPUS_CHECK_NAMES` and reported `PIN` for each, so the zero-maintenance term in
the cost test above is measured rather than argued. `checkProvenance` reached its
first run WITHOUT a witness and the lane said `ACCEPTED`, which is what sent its
author back to write the drive.

## Consequences

A corpus check that survives its own deletion is named on the pull request that
lands it, by the check's own name, rather than by the next reader who thinks to
ask. The lane runs in `governance.yml`'s `policy-docs` job and as step 3a of
`prepr.sh`, so a seat sees it before pushing.

It does not make a witness unnecessary; it makes a missing one visible. The
answer to `ACCEPTED` is still to drive the check against a state where its
property is true, which is what the `capClasses` and named-docs blocks do.
