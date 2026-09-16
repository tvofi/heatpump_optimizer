# The fixer's contract (the standing gate protocol as a checklist)

You own one PR group: one subsystem, at most five findings, at most about 400
production lines. You work in your own worktree branched from `origin/main`.

1. **Never touch `VERSION`, the manifest version or the `RELEASE_NOTES.md`
   heading.** Versions are assigned by `tools/release/stamp.py` after the
   merge. The rule is keyed on the manifest's `version` field, not the file:
   an edit leaving it unchanged is allowed; the command is `prepr.sh` step 5's.
   Compare three-dot, never two-dot: a two-dot `git diff origin/main <branch>`
   during a PR #399 pre-merge check reported `tests/closures.json` as changed
   by the branch, when the difference was `main`'s own newer commits the
   branch had not merged.
2. **Failing test first**, importing the production symbol (a test that
   re-implements a formula pins nothing; `tests/README.md`). Record the
   mutation proof in the PR body: delete the fix's production line(s), run
   the closure, paste the failing check names, restore. **Mutate the predicate,
   not the tail**: a line appended past a script's own return changes nothing,
   and a vacuous mutation reads exactly like a passing check — `exit 3` on the
   end of `.claude/hooks/pre-edit.sh` left `policy_lint --hooks` at rc=0.
3. **Re-execute the finding's harness on your branch**: before and after, with
   the head SHA measured, in the PR body. **Every quantified claim carries a
   null control, not only cost, gain and time**: a count, a percentage, an
   "every" or a "none" is a measurement, owed the command that produced it and
   the result that would have appeared had it been false. **Never print a
   conclusion beside a command** — `diff a b && echo IDENTICAL`, never
   `diff a b; echo "(empty means identical)"`, which prints either way. A figure
   from a sliding window, or one an instrument prints, is stale after you write
   it: state the rule or name the instrument, never the number. A learner or guard
   change is measured at both ends of its input range — an install with zero
   evidence, and one on the clamp — a fix has been worse than its bug before.
4. **Goldens that move are claimed by whoever measured the drift**, in
   `tests/golden/claimed_drift.txt` or `card_claimed_drift.txt`, with the
   expected direction per fixture. `claims-for:` stays at the live `VERSION`.
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
   locally, then you push the branch with `tools/audit/push.sh`, handing it the
   body: it refuses before it pushes anything if that body fails the contract
   check (#678). The PR's own checks are green before the handoff in step 6 —
   `fix-review.md` step 11 reads those rather than the body's account of them.

   **Take the gate lease only when `MODE: FULL` or `scope.run` names
   `tests/stress.py`**, the one script the lock exists for; the commands, and
   why `mkdir` and a shell pid is not a lease, are `gate-scoping.md`'s.

   `GOLDEN_MODE=drift` against the merge base always: strict mode compares
   solver floats that do not reproduce across BLAS builds, so it is honest
   only in the environment that recorded the fixtures. `tests/README.md` has
   the detail. `python3 tests/structure.py` is seconds and runs before every
   push regardless.
6. Hand off to the adversarial fix reviewer. **After any rebase or merge,
   steps 2–8 are re-executed**: the evidence describes one tree, and either
   makes a new one — **the body included**, because a figure that is a function
   of `origin/main`'s tip is false the moment `main` moves. Stamp such a figure
   with that tip and `date -u`.

   **The handoff freezes the branch.** Until then, update it from `origin/main`
   whenever you need to — `git merge origin/main`, never rebase. After it, the
   head is the reviewer's measuring surface and **only the orchestrator moves
   it**: a head that moves mid-review invalidates measurements already taken,
   and the reviewer cannot tell which of its numbers still describe the tree.
   If your branch goes stale while a review is in flight, say so and hand it
   back; do not merge it yourself. Moving it anyway is a verdict the reviewer
   may return against you — **Re-read the head before you post**, in
   `fix-review.md`.

   Landing a PR is never yours in any case — that is the **orchestrator's**, the
   seat the Model-routing table gives control flow, merges and sequencing, or a
   merge-and-release seat it starts. `git merge origin/main` into your own
   branch and merging the pull request differ; only the first was ever yours,
   and only before the handoff. "Coordinator" here is `coordinator.py` and its
   ratchet budgets, never a seat.
7. The PR body closes its issues (`Closes #N`), names the head SHA measured,
   and carries every executed number, each in `## Figures` with its command.
8. **A quoted number states the rule that produced it, not just its value.**
   Three agents counting "the same" published-attribute census (#373) got
   59, 50, and 124/147/50, because each asked a subtly different question;
   only a count whose rule is written down is re-derivable by whoever reads
   the body next. Say what you counted, not only how many.
   **Name the instrument you re-ran, and its scope.** If the block you are
   clearing was demonstrated with an *instance*, your verification may not be a
   search for that instance — it must check the *property* the block stated. If
   no such instrument exists, say so, and say what you did instead.
   A root-cause analysis established this class over three pull requests where
   each fix was verified against the demonstrated instance's form while a
   sibling carrying the same property in a different form survived — one of them
   created by the same commit. That analysis, its cost test and the detector it
   built and rejected are recorded on **#592**, which is where this step was
   added. Its measurements are deliberately not quoted here: they are a share of
   a moving population and decay, which is what step 3 above forbids — three
   figures were quoted in a first draft and a reviewer refuted all three.

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
11. **A check pins the artifact it reads, not the one it is named for.** The
    #546 set check was named for `apply_topology`'s schema and read the module
    constant that schema is built from, so a schema that stopped agreeing with
    the constant was invisible — `slab_shunt` plus a junk key passed all 2002
    checks (#550). Read the registered artifact, as `tests/entities.py` does.
    Then probe a key the read does **not** name: under `extra=vol.ALLOW_EXTRA`
    the read set is still exactly right while the schema accepts anything, so
    the probe is the reader's own null control.

    **Say where a check encodes a design choice.** #546's required every slot
    place to be accepted, settling which of two artifacts was authoritative;
    under the other plausible fix it failed 4 of 7, and three were the test's
    opinion rather than a defect. Prejudging is legitimate — saying so is what
    stops the next seat reading a legitimate tightening as a bug.

12. **The seam a method belongs to is decided by its NAME, first match wins.**
    `tests/structure.py`'s `seam_bucket` walks `SEAM_REGEXES` in order and
    returns on the first regex that matches the method name; anything matching
    none is `core`. So a method whose name happens to match an earlier seam's
    pattern is priced against **that** seam, not the one it belongs to — and a
    cut measured on the wrong bucket is measured against state the seam does not
    own. Before pricing an extraction, run the candidate method names through
    the bucketing yourself and say which seam each landed in. A name collision
    is silent: nothing fails, the number is simply about a different thing.

13. **`tests/hastub` is not Home Assistant, and a green test may pin the stub.**
    `tests/ha_contract.py` records what each stub symbol is — faithful,
    divergent, simplified, unverified, or a holder — and runs its contracts
    against both the stub and, nightly, the real package. **Before asserting
    that a test proves a production property, check whether the stub is what
    satisfied it.** Four separate seats hit this in one day: the stub had no
    loop protection, no `section`, no `state` property on `SensorEntity`, and a
    `NumberSelector` that validated nothing. Each made a real defect invisible
    to every lane.

    If your work depends on a symbol's upstream behaviour, add or read its
    contract rather than assuming; if you must extend the stub, argue the
    fidelity against upstream rather than shaping it to what your test needs —
    that shape is exactly the one that agrees with a wrong implementation.

14. **An allow-list is keyed on something, and your entry silences everything
    that key matches.** Before adding a case to a pin, a baseline or a
    suppression list, name the key's fields, name the property that makes your
    own occurrence legitimate, then key the occurrence the pin exists to catch
    and compare the two. Equal keys mean the entry blinds the pin at the site
    it watches, and the answer is to change the route until no entry is needed,
    or to widen the key until the two separate — never to add it and note the
    risk. #714 declined an entry in `tests/nightly_ha.py`'s `KNOWN_BLOCKING`,
    keyed on (call, file, source snippet): its report was legitimate only
    because the caller was `atexit`, running after the loop was gone, and no
    field of that key carries a caller — so the entry would equally have
    matched that line reached from a coroutine, #525's class at the one site
    the pin exists to watch.

    **A fix that changes the route leaves the reported text where it was, so
    name the route.** #714 rerouted the caller and left `worker.wait(timeout=2)`
    in place: grepping the report's own call, file and snippet finds them
    unchanged and reads the defect as open, and grepping for their absence
    finds nothing and reads the same. The line is no help either — not in the
    key, and #714's own fix moved that call 24 lines. Anchor the claim to
    what moved: branch, registration, frame count.

15. **A bitwise-parity claim over numpy reductions is per-architecture.**
    `np.sum(matrix, axis=1)` is not `np.sum(matrix[b])`, and neither is a
    reduction over a row VIEW of a batched array one over the fresh array
    the scalar expression builds: numpy's pairwise loop treats alignment
    and stride as inputs, and which paths it takes is a backend property —
    #948's batched cost terms were bit-identical to the scalar objective
    on the arm64 seat that wrote them (twice, under two designs) and
    re-planned 19 of 51 stress scenarios on CI's x86_64, at the 96-step
    production width only, so a 48-step parity grid passed unseen. Where
    the contract is bitwise, run the SCALAR EXPRESSION per row, on the
    fresh per-row arrays that expression's own elementwise ops allocate —
    batch only what is elementwise end to end — and drive the parity grid
    at the production width.

    The same rule holds one level up and across interpreter versions: a
    reduction whose scalar form is a PYTHON BUILTIN is compensated
    arithmetic on CPython 3.12+ — builtin `sum` is Neumaier — and no
    vectorized accumulation reproduces it. #948's terminal twin
    accumulated plain vector adds against the scalar closure's `sum`:
    1-2 ulp apart, which diverged both of optimality's jac races on CI's
    3.14 runner while every 3.11 seat was green, because 3.11's `sum` is
    plain accumulation — the seat was structurally blind, not unlucky.
    Make the twin call the scalar closure's own function per row, and put
    detector rows on the parity grid that separate the two summations
    (measured: ~12% of random three-term sums), so the interpreter class
    that diverges — CI's — runs the detector.

**When a structural budget blocks the work.** A `tests/structure.py` failure is
a decision point, not a wall, and it has three answers rather than two: pay for
the lines elsewhere; re-record because the tree genuinely improved; or, for a
genuine new production feature, **raise** the budget because the capability is
worth the structure it costs (`--record --allow-regression="<reason>"`, with
that reason in the **commit** message: `main`'s history keeps a commit message
and never a pull-request body — decision 0010, true under either merge method).
Paying for the lines is the first question; a raise is for when you cannot.

**Ask which class the budget you fear is even measured on.** Some rows come from
the single class named by `COORDINATOR_CLASS_NAME`; the rest from every parsed
module. A method added outside that **class** moves none of the first group, so
the payment question -- which has cost several seats a scan and once a near-halt
-- does not arise there. *Class*, not file: `coordinator.py` holds several, and
adding a method, call and attribute to `CoordinatorContext` moves no row.

**Derive the split, do not carry it.** The coordinator-scoped rows are the ones
`measure()` selects or keys by `COORDINATOR_CLASS_NAME`. Re-derive at your merge
base; a list here would be a carried number, which this file already refuses.

**Read the expression, not the value.** `attrbag_classes_over_30` has the
coordinator as its only member and a `top_is_coordinator` flag beside it, yet is
tree-wide: enough attributes on a class in any other module move it.

**An empty payment pool is a halt only where a payment was owed.** Let
`python3 tests/structure.py` name what moved at your merge base. Outside the
coordinator class a split usually moves the maxima *down* -- which the gate still
refuses until you re-record them, with the reason in the commit.

A raise is the owner's, confirmed before the push (`CLAUDE.md` rule 2), and not
something a reviewer can wave through. But a metric at zero headroom is not a
veto on new functionality, and asking is an available move: #398 was refused in
part because `coordinator_attrs` stood at 176/176 and a new attribute read as
costing an existing one.

## Before you hand off: carry what you found forward

Your PR does not merge until any finding that **changes how a later stage must
work** is in that stage's own brief — `finding-propagation.md` states the test,
what to write and where it goes, and a comment on this PR discharges none of it.
Name the destination in your PR body — which brief, contract, carry file or
roster received it — so the reviewer checks the destination rather than takes
your word.

## Before you hand off: answer any check your branch turned red

`defect-root-cause.md`'s second trigger fires on your own PR: name each check
that went red in the body and answer it there — the cheaper detector and its
standing cost, or the finding that none exists. `UNDER-SCOPED` and `INHERITED
CLAIMS` are answered by naming them (`ci-autofix.md`). You are naming the
trigger, not analysing it; the analysis is `root-cause.md`'s seat.

A harness the closure recorder cannot see — one that shells out to
subprocesses, like `tests/harness_headers.py` — will not turn red on your PR
at all; treat its headers' EXPECTED lines as production state and re-record
them in the same pull request that changes what they print (#968 → #979:
only main's forced-full run caught it).

## Past three rounds, re-cut rather than repair

The owner's rule. At the **fourth** round, replace the body instead of repairing
it: the headings `.github/PULL_REQUEST_TEMPLATE.md` requires, the arms that
fire, and only figures re-taken in that pass. Round history is deleted, not
restated. **A re-cut body blocked on `claims` again is a signal about the fix**,
so the orchestrator splits the branch or closes it.
