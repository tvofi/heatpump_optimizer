# RCA: unstamped tag v7.1.2 reached users

Seat: root-cause, group R10-RCA-RELEASE-TAG, trigger 1 (the defect reached a
released version). Tree: `origin/main` at `c3a279e32`. This seat fixes nothing;
the `release.yml` guard belongs to R10-HOTFIX-RELEASE-TAG and is not built here.

## What happened, from the API and the tree

- `v7.1.2` is a lightweight tag on `b8e823699`, the web-UI merge of #3161
  (committed 2026-11-02 19:52:05Z). `VERSION` at that commit is `7.1.1`;
  `RELEASE_NOTES.md` has no `## v7.1.2` section. Every stamp commit is titled
  `vX: stamp ...` and carries its own `VERSION`; this one is not a stamp commit.
- The Release run (134, event `push`, actor `tvofi`) was created 21:07:51Z. The
  tag therefore existed by then. The `release.yml` ancestry step passed, since
  `b8e823699` is on main; that step checks "on main", not "is a stamp".
- The run failed at 21:08:49Z, in the publish step: "release v7.1.2 does not
  carry heatpump_optimizer.zip; left as a draft, not published". The asset
  `heatpump_optimizer.zip` shows `created_at` 21:08:49Z, so the read-back ran
  in the same second the upload landed. I did not reproduce this race.
- The release was published at 21:16:19Z, 7.5 minutes after the run ended
  red, by something other than that run. The API shows the draft's author
  (`github-actions[bot]`) but not who published it.
- Rulesets `release-tags-protect` (tag, id 23937752) and `main-protect`
  both have `updated_at` stamps close to those events: 21:08:06Z and 21:16:38Z
  (the latter is main-protect's).

## Who pushed it

Not knowable from what the API and the tree show. Narrowed:

- A push event's actor is `tvofi` for a deploy-key push and for a push with
  the owner's own credential alike. A lightweight tag carries no tagger.
- `release-tags-protect` has one bypass actor, `DeployKey` (always), with
  rules `creation`, `update`, `deletion`, `non_fast_forward` on `refs/tags/v*`.
  If the ruleset was in this state at push time, the pusher held a deploy key.
  It was **not** `stamp.py`: stamp creates its own commit and tags that, and
  this tag is on a merge commit with a stale `VERSION`. So either someone used
  the key by hand (`git tag` + push), or the ruleset was not yet in this state.
- The ruleset's `updated_at` (21:08:06Z) falls 15 s after the run started, so
  the ruleset may have been edited after the tag. Its history endpoint
  returns 403 for this seat's credential, so I cannot tell. Nobody should
  read this as evidence of misuse; the owner can read the history in the UI.

## Does the tag ruleset admit a non-stamp pusher?

Yes, in principle. The bypass is an identity (the deploy key), not an
operation. Any holder of that key can create `v*` at any commit. Nothing about
the key says "only via `stamp.py`". `release.yml` says this itself (comment
at the ancestry step: the ruleset is the barrier against a deliberate release).
The ruleset is also the only barrier: the tag then triggers a workflow that
runs whatever the commit contains.

## Process state: (c)

The process (only the deploy-key bypass may create a `v*` tag; the workflow
refuses commits off main) was followed and did not produce the intended result,
because its unit is **who** and **where** (identity, ancestry) while the
intended invariant is **what**: a release tag names a stamp commit whose
`VERSION` equals the tag. Not (a): both barriers existed. Not (b): nothing
shows a rule was ignored. Not (d): no precondition is known to have changed.
The countermeasure therefore changes the unit of the check, not the number of
instructions; "tell the key holder harder" is the wrong fix.

The red-main refusal in `stamp.py` rule 2 was never reached: the tag did not
come through the stamp.

## Class reach (searched, with a null control)

For the 40 newest `v[0-9]*` tags, I compared `VERSION` at the tagged commit
with the tag. Result: one mismatch, `v7.1.2`; the other 39 agree. 156 `v*`
tags exist in total. The same shape (a ref the stamp did not write) reaches
any `v*` the key can push, and the `workflow_dispatch` path, which creates the
tag itself at the commit it runs on and passes the same ancestry step.
The second defect in the incident, a release listed Latest after its run
failed, is a separate shape: a human or tool publishing a draft the workflow
had refused to. No repository check can see a UI click.

## Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

- P(recurrence): 1 mismatch among the 40 newest tags measured here; the older
  116 tags I did not check. I use 1/40 = 2.5% per release as an upper-end
  estimate, measured on a sample, not a class frequency from the register.
  Release cadence is about one tag every 1 to 3 days (v7.1.0 on 10-30,
  v7.1.1 on 11-02, v7.1.2 on 11-02).
- cost(defect): the release carried the wrong version for at least 8 minutes
  (from the run's failure to the publish) and was listed Latest; the asset
  showed 9 downloads when read. Cleanup is an owner-time job of the order of
  tens of minutes (new stamp, retag, delete or republish). I did not time it;
  this is my estimate.
- cost(countermeasure): a `release.yml` step comparing `VERSION` at the tag's
  commit with the tag is one `git show` and one string compare per release,
  on the order of 1 s, once per release. At 2.5% x ~30 minutes = ~45 s of
  expected owner time per release, against ~1 s per release, it passes by a
  wide margin even if my defect estimate is off by 10x.

## Countermeasure (not built here)

1. **Addresses state (c).** In `release.yml`, before the notes step, refuse
   unless `git show "$GITHUB_SHA:VERSION"` equals `${TAG#v}` and the commit
   subject starts with `${TAG}:`. This is R10-HOTFIX-RELEASE-TAG's scope.
   When built it owes the demonstration this role requires: failing at
   `b8e823699` (VERSION 7.1.1, tag v7.1.2) and passing at `78dd34354` (v7.1.1);
   a null control on a stamp tag; a check that does not pass by skipping.
2. Recommended for the owner, no repository change: the publish read-back
   raced the asset upload, so a red Release run should be re-run, not
   published by hand. This is a procedure for the owner and I record it, not
   enforce it.

Recorded refusal: no check for "who may hold or use the deploy key" is
proposed; the key's purpose is to bypass the rule and it has no per-operation
scope on GitHub. The workflow check above is the cheaper detector.

Not asserted: who pushed, whether the ruleset was in its current state at
push time, and what published the release at 21:16:19Z.
