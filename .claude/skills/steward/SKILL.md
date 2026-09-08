---
name: steward
description: Driving a pull request in this repository to green, where the general rules would act wrongly
---

# Stewarding a pull request here

Read this before acting on a CI failure or a review comment. It states only
where this repository differs from the general rules; everything not named
here is unchanged, and nothing here loosens a prohibition.

The difference is worth reading because two of these have a wrong default: one
tells you to push a fix that the repository forbids you to write, and one
leaves you waiting on a run that will never start.

## S1 A red claim or closure check is a bot's job, not yours

IF `fast` fails with `INHERITED CLAIMS`, or `closures` prints `UNDER-SCOPED`,
THEN wait for the autofix job's commit and push nothing.

Both repairs already exist as jobs. A branch that touches no fixture inherits
the baseline's claim list through the merge, and the repair is to empty it —
which the bot does, and which you must not do by hand.

**Read the job's summary line, not its tick.** The job reports its own status
and goes red exactly when the repair did not happen: `autofix_repair_failed`
in `tests/closure.py` decides that, and prints the remedy beside it. Green
covers both "repaired, commit coming" and "nothing was owed", and the
conclusion alone cannot tell them apart.

Once the job has gone red it has told you no commit is coming, and the rule
against repairing it yourself stops applying.

EXAMPLE BAD: emptying the claim file and pushing while the job is still
running. GOOD: reading the summary, seeing `changed`, and waiting for it.

## S2 A conflicted pull request is not red — it cannot run

IF the pull request is `DIRTY`, THEN no workflow fired and there is no result
to read. Merge `origin/main` locally and push; the merge driver for the claim
files runs only in a clone that installed it, and a runner is not one.

This happens without anyone touching your branch: a merge to the default
branch that moves a claim file flips every open pull request at once.

Confirm a conflict is real before treating it as one:

    git merge-tree --write-tree origin/main HEAD

Install the driver once per clone; a worktree shares its checkout's config.

    python3 tests/env_drift.py --install-merge-driver

## S3 Key on the mode line, never the count

IF the scoped selection prints a mode line, THEN act on the mode. Both modes
can print zero, and they mean opposite things. A push to the default branch
prints no mode line at all, because the forced full run never calls the code
that would.

## S4 Never move a version

IF your change would touch `VERSION`, the integration manifest version, or the
release-notes heading, THEN stop. Versions are assigned after the merge by
`tools/release/stamp.py`, which refuses a branch that moved one.

## S5 Leave the claim files alone unless you are claiming

IF your branch moves no fixture, THEN both claim files stay byte-identical to
the default branch. A branch that does not touch them cannot conflict with
another branch over them, and the guard that catches an inherited list is
satisfied by an empty one.

## S6 Take the lease before a local run that measures the machine

IF a local run would select `tests/stress.py`, THEN take the gate lease first
with `tests/gate_lock.py`. That script measures the machine while it solves,
and its numbers are wrong if anything else is running. A scoped run that does
not select it needs no lease.

## S7 Merge, never rebase, and never force-push

IF you are updating a branch from the default branch, THEN merge. A rebase
invalidates the head a reviewer measured and every checkout of it.

## S8 A red check owes an answer in the body

IF your branch turned any check red, THEN name that check in the pull-request
body and answer it: the cheaper detector that would have caught it and what it
would cost to stand, or the finding that none exists. The reviewer reads the
checks before returning a verdict, and an unanswered one is a blocked verdict.

Naming the trigger is not the analysis. The analysis runs in its own seat.

## S9 Never re-gate an unchanged head

IF a terminal result already exists at this head, THEN it is the result. Re-run
a job only under the narrow conditions the general rules allow, and never to
see whether it comes out differently.

## S10 Create the commit, then write the body, then push

IF a fix also needs the pull-request body corrected, THEN create the commit
first, write the body against the SHA it already has, and push last.

`pr-contract` runs on `synchronize` and reads the body as it stood at push
time. Push before correcting the body and the job measures the stale one, so a
fix leaves a failed run attached to the very commit that repaired it. The
`edited` trigger then produces a second, green run and the latest wins, but the
red one stays in the listing and leaves the pull request `unstable`.

The order above works because a commit's SHA is fixed when the commit is made,
not when it is pushed -- including a cherry-pick onto the branch you push, which
assigns the SHA locally. So `## Head` can always be written before the push;
what cannot is writing it before the commit exists.

Measured on this workflow's own first pull request, three times. Two earlier
forms of this rule failed here: "edit the body first" named a commit the
cherry-pick then renamed, and "correct only `## Head` afterwards" still leaves
one red `synchronize` run on every push, because that is the section the stale
body always gets wrong.

EXAMPLE BAD: push, then update the body, then explain the red run.
GOOD: commit, read the SHA, write the body, push. One run, and it is green.
