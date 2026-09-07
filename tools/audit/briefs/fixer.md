# The fixer's contract (the standing gate protocol as a checklist)

You own one PR group: one subsystem, at most five findings, at most about 400
production lines. You work in your own worktree branched from `origin/main`.

1. **Never touch `VERSION`, the manifest version or the `RELEASE_NOTES.md`
   heading.** Versions are assigned by `tools/release/stamp.py` after the
   merge. The reviewer checks
   `git diff origin/main...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json`
   is empty — three-dot, never two-dot: a two-dot `git diff origin/main
   <branch>` during a PR #399 pre-merge check reported `tests/closures.json`
   as changed by the branch, when the difference was `main`'s own newer
   commits the branch had not merged. Any branch-vs-main comparison is
   three-dot for the same reason, not only this one.
2. **Failing test first**, importing the production symbol (a test that
   re-implements a formula pins nothing; `tests/README.md`). Record the
   mutation proof in the PR body: delete the fix's production line(s), run
   the closure, paste the failing check names, restore.
3. **Re-execute the finding's harness on your branch**: before and after, with
   the head SHA measured, in the PR body. A cost, gain or time claim carries
   its null control. A learner or guard change is measured at both ends of
   its input range — an install with zero evidence, and one sitting on the
   clamp — because a fix has been worse than its bug before, silently.
4. **Goldens that move are claimed by whoever measured the drift**, in
   `tests/golden/claimed_drift.txt` or `card_claimed_drift.txt`, with the
   expected direction per fixture. `claims-for:` stays at the current
   `VERSION`.
5. **Measure the gate's scope, then run what it names.** The gate is scoped
   from measured closures, so derive the selection rather than assume it:

       D=$(mktemp -d); python3 tests/closure.py select \
         --diff $(git merge-base origin/main HEAD) --workdir "$D"
       cat "$D/scope.txt"; cat "$D/scope.run"

   Key on the **mode line**, never the count — `MODE: SCOPED -- 0 script(s)
   run` and `MODE: FULL` both print zero and mean opposite things. Run what
   `scope.run` names, with `PYTHONPATH=tests/hastub`, and leave the remainder
   to CI. `tests/README.md` ("The scoped gate") is the in-tree source for why
   that is safe and what it costs: CI runs the same `run.sh` in the same drift
   mode against the same merge base, and a full run is about forty minutes. So
   `MODE: FULL` reports a diff the gate cannot scope — often a gate file or a
   doc — not an instruction to spend forty minutes reproducing CI.

   **Running locally does not discharge CI.** What `scope.run` names is green
   locally before you push, and the PR's own checks are green before the
   handoff in step 6 — `fix-review.md` step 11 reads those checks rather than
   the body's account of them, and a check that went red owes an answer in the
   body.

   **Take the gate lease only when `MODE: FULL` or `scope.run` names
   `tests/stress.py`**, the one script the lock exists for (`CLAUDE.md`
   "Running it"; `tests/README.md`). Never `mkdir` and a shell pid, which #404
   replaced: that lock carries no lease, `run.sh` will not renew it, and a
   waiter cannot reclaim it after a crash.

       python3 tests/gate_lock.py take --label <your-label>
       HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
         GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
       python3 tests/gate_lock.py renew --label <your-label>   # between commands
       python3 tests/gate_lock.py release --label <your-label>

   `GOLDEN_MODE=drift` against the merge base always: strict mode compares
   solver floats that do not reproduce across BLAS builds, so it is honest
   only in the environment that recorded the fixtures. `tests/README.md` has
   the detail. `python3 tests/structure.py` is seconds and runs before every
   push regardless.
6. Hand off to the adversarial fix reviewer. **After any rebase or merge,
   steps 2–4 are re-executed**: the evidence describes one tree, and either
   makes a new one.

   **The handoff freezes the branch.** Until then, update it from `origin/main`
   whenever you need to — `git merge origin/main`, never rebase. After it, the
   head is the reviewer's measuring surface and **only the orchestrator moves
   it**: a head that moves mid-review invalidates measurements already taken,
   and the reviewer cannot tell which of its numbers still describe the tree.
   If your branch goes stale while a review is in flight, say so and hand it
   back; do not merge it yourself. Moving it anyway is a verdict the reviewer
   may return against you — **Re-read the head before you post**, in
   `fix-review.md`.

   Landing a PR is never yours in any case — that is the orchestrator's, or a
   merge-and-release seat it starts. `git merge origin/main` into your own
   branch and `gh pr merge` are different acts; only the first was ever yours,
   and only before the handoff.

   The seat is the **orchestrator** — the one the Model-routing table gives
   control flow, merges and sequencing. In this repository "coordinator" is
   `coordinator.py` and the `coordinator_loc` / `coordinator_attrs` budgets the
   ratchet section below measures. It is never the name of a seat.
7. The PR body closes its issues (`Closes #N`), names the head SHA measured,
   and carries every executed number.
8. **A quoted number states the rule that produced it, not just its value.**
   Three agents counting "the same" published-attribute census (#373) got
   59, 50, and 124/147/50, because each asked a subtly different question;
   only a count whose rule is written down is re-derivable by whoever reads
   the body next. Say what you counted, not only how many.
9. **A claim should be true; if wrong, correct it — anchored to a lane,
   function, marker or SHA, never a bare line number — and delete only when
   no such correction exists.** Delete on sight, not as a last resort, when
   the claim is only motivation or scaffolding the finished text doesn't
   need. PR #386 took four repair rounds to correct 17 citations; only its
   last two survivors — bare-line-number claims a later merge falsified, and
   by then unneeded — were settled by deletion.
10. **If the wrong text is generated, fix the generator first, and run it.**
    Correcting prose a script emits leaves the script emitting the old text on
    its next run, so the correction is undone rather than kept — #539 found
    `tools/audit/prepare_baseline.sh` writing the `mkdir` gate lock `CLAUDE.md`
    forbids into every new auditor's `BASELINE.md`, alongside the same
    instruction in agent prompt strings under `.claude/workflows/`. Grep for
    the wrong form across the whole tree before deciding what to edit, because
    a generator is rarely the only copy. **A generator fixed without being run
    is a claim, not a fix**: run it and paste what it now emits, with the same
    run at the merge base as the control. Distinguish text that *instructs*
    from a record that *recounts* — a measurement record stays as written.
11. **A check pins the artifact it reads, not the one it is named for — and a
    structural read needs a behavioural control.** The #546 set check was named
    for `apply_topology`'s schema and read `topology.POSITION_PLACES`, the
    module constant that schema is built from, so a schema that stopped
    agreeing with the constant was invisible: re-adding `slab_shunt` and an
    arbitrary junk key to the schema **passed all 2002 checks**, and the check
    named *"not a label map the schema borrows"* passed while the schema
    borrowed exactly such a map (#550). Read the registered artifact —
    `hass.services._schemas[(DOMAIN, service)]`, as `tests/entities.py` already
    does. Then cross-check that reading against behaviour, because reading the
    validator has its own blind spot of the same shape: under
    `extra=vol.ALLOW_EXTRA` the read set is still exactly right and the schema
    still accepts anything, and only probing a key the read does **not** name
    catches it. That probe is the reader's null control.

    **Say whether the check encodes a design choice, and prefer a bound where
    the design is undecided.** The #546 check required every slot place to be
    accepted, which settled which of two artifacts was authoritative: under the
    other plausible fix for the same issue — accepted == exactly the card's box
    set — it failed **4 of 7**, and three of those failures were the test's
    opinion rather than a defect. A check that must prejudge is legitimate, but
    say so where it is written, because the seat whose tightening reddens it
    will otherwise read it as a bug and weaken it.

**When a structural budget blocks the work.** A `tests/structure.py` failure is
a decision point, not a wall, and it has three answers rather than two: pay for
the lines elsewhere; re-record because the tree genuinely improved; or, for a
genuine new production feature, **raise** the budget because the capability is
worth the structure it costs (`--record --allow-regression="<reason>"`, with
that reason in the **commit** message, because the squash-merge keeps the commit
and discards the branch). Paying for the lines is still the first question, and
a raise is only for the case where the honest answer is that you cannot.

A raise **requires the repository owner's explicit confirmation, obtained before
you push.** It is not a judgement a fixer makes alone and it is not something a
reviewer can wave through, so an agent that finds itself wanting one **stops and
asks** rather than proceeding and explaining afterwards. This is not a route for
accommodating sloppiness, an unexamined refactor, or a feature that has not been
measured. But a metric sitting at zero headroom is not a veto on new
functionality, and asking is an available move — #398 was refused in part
because `coordinator_attrs` stood at 176/176 and a new attribute was read as
costing the deletion of an existing one. `cross_seam_fraction` is exempt from
all of this: it is a tolerance metric and is **never** re-recorded.

## Before you hand off: carry what you found forward

Your PR does not merge until any finding that **changes how a later stage must
work** is written into that stage's own brief. It qualifies when you established
it by measurement, with the null control, and it narrows what a later stage may
do, invalidates an assumption it rests on, or removes an option it was expected
to have — a technique refused, a figure that no longer holds, a dependency that
will not install, a budget already spent.

**Putting it in this PR's comments does not discharge it.** The next seat reads
its own brief, its roster entry, `CLAUDE.md` and this contract; it does not
read the comments of a PR that merged before it started. Carry the **control**
as well as the claim, and state the **precondition** rather than the opportunity
— "this gained N points" invites the next seat to reach for it, "this is
legitimate only when X, demonstrated per case" is what keeps them honest.

A finding that constrains every seat goes in the role contract it belongs to
under `tools/audit/briefs/` once, not
into each brief. If the stage that needs it has no brief yet, it goes in the
plan row that will become one, and creating that row is part of the finding.

Name the destination in your PR body — which brief, block or plan row received
it — so the reviewer checks the destination rather than takes your word.

See `.cursor/rules/finding-propagation.mdc`.

## Before you hand off: answer any check your branch turned red

`.cursor/rules/defect-root-cause.mdc` has two triggers, and one of them fires on
your own PR: a defect that **turned a check red where a cheaper detector could
have run**. Name that check in your PR body and answer the question there — the
cheaper detector and its standing cost, or the finding that none exists.
`UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them; their
countermeasure is the autofix job `ci-autofix.mdc` already describes.

You are naming the trigger, not analysing it. The analysis runs in its own seat
(`tools/audit/briefs/root-cause.md`), never in yours, for the same reason the
fix review is not yours. What you owe is that the trigger is visible to a seat
other than the one that tripped it.

The reviewer reads your checks rather than your account of them, and an
unanswered red check is `blocked: root-cause trigger unanswered for <check>`.
