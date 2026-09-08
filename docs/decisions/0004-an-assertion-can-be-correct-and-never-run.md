# 0004 — An assertion can be correct and never run

Status: accepted. Supersedes nothing; sits beside `0002`, which it is repeatedly
mistaken for.

## Context

`0002` names SELF-WITNESSED PROXY ASSERTION: a property that is false on a
healthy tree has no natural witness, so the author writes down a model of the
check and pins the model. Its subject is an assertion whose CONTENT is wrong.

Five defects in this repository are not that. In every one the content is
right. `checkProvenance`'s acceptance really does refuse an emptied check —
driven, it refuses. What varied was whether the line EXECUTED, and that was
decided by a fact about the clone rather than about the code.

**The cause.** *A check's environment-dependence is reasoned about where the
check READS the environment, and not where the assertion that DRIVES it does.
The result is an assertion that is correct, that did not run, and whose run is
byte-identical to one where it did.*

The five, with the environment fact that decided each:

| # | site | decided by |
|---|---|---|
| 1 | acceptance drove `checkProvenance` with `HEAD`, skipped when `HEAD == origin/main` | `governance.yml` also runs on push to `main`, where they are equal |
| 2 | the same skip still counted its pins | the same |
| 3 | the mutation lane read only an exit code | a clone with no `origin/main` |
| 4 | `check-wave-script.mjs` scans a directory for rosters | the population can be zero |
| 5 | the acceptance demanded a refusal the check declines to give | a shallow clone |

**Two of the five were written by the commits that closed the previous class.**
Instance 3 is inside `0002`'s own countermeasure. Instance 5 was introduced by
the commit that landed `0003` and its rule *"do not report a refusal you have
not established"* — it added the arm that declines in a shallow clone and, in
the same diff, an assertion demanding a refusal in exactly that shape. A class
that reproduces inside its own remedy twice, at two levels, with the author
reasoning correctly about the level below, is not the old class recurring.

**The handling already existed, in another file, and nothing carried it.**
`tests/entities.py` distinguishes "cannot look" from "no" for the same git
call, and says so in its own message. That landed two days before the commit
that wrote *"this clone is not shallow"* into a check that runs in shallow
clones.

## Decision

**Ask the environment where the assertion runs, not only where the check reads
it.** A guard on the check does not protect an assertion that drives the check.

**A run that could not drive an assertion says so, and does not claim its
pins.** A skipped drive that still counts is a total the run did not earn.

**Say how much was skipped, not merely that something was.** The distinction is
load-bearing: an arm that could not run is not the same as a check that could
not run, and reporting the larger claims less than the run earned. `SKIP` on a
whole check and `skip` on one arm are different words here for that reason.

**A check that discovers its population by scanning must guard AND disclose
it.** A floor catches zero. Only a printed count catches seven becoming four,
and a helper that prints its detail only on failure discloses nothing on the
path that matters.

**Prefer the remote ref, and refuse when there is no baseline.** A local `main`
goes stale silently — measured here at one merge behind — and a detached CI
checkout has none at all. The two failures are silent in opposite directions.

## The countermeasure

`.claude/workflows/policy_lint_envmatrix.mjs`, run by the `env-matrix` job.
It builds the environment shapes this repository declares it supports — `pr`,
`push-main`, `no-remote`, `shallow`, `no-rosters` — and requires each shape's
declared outcome. That is the thing no author's single run can establish, which
is why it is a separate job from the lane that proves the checks are right.

It guards its own vacuity: a matrix that built three of five shapes prints
`MATRIX VACUOUS` and fails, because a matrix that ran a subset certifies
nothing. The `shallow` row asserts the PROPERTY — an undrivable arm is said out
loud and not counted — rather than the fix's exact spelling, so it does not
merely test the patch that prompted it.

**Shown failing on the defects it was written for**, by SHA:

```
e3449a5   7 outcomes held, 6 did not   instances 1, 2, 3
b34af6b  10 outcomes held, 3 did not   instances 4, 5
HEAD     13 outcomes held, 0 did not   null control
```

**Cost test.** 8.4 s per run against 480 s for the cheapest measured
review round that caught one. Break-even is 57 runs per catch; the observed
rate is one instance per 9.6 governance runs, a margin of about 6×. Both sides
are wall-clock, but the left is machine seconds and the right is agent seconds
— weighting them equally is the conservative reading, and it never narrows.

## Consequences

The matrix is a floor, not a proof: it covers five shapes, and a sixth the
repository starts depending on is invisible until someone adds a row. It cannot
see a shape it was not told about, which is `0003`'s limit reappearing one level
up — so the list of shapes is written where a reader meets it, not inferred.

Two residuals stay, disclosed rather than fixed: `brief_lint` downgrades a
citation error to a warning when a cited tag is absent from the clone, and the
`PULL_REQUEST_TEMPLATE.md` drift assertion is protected only by an adjacent
check that happens to fail first.
