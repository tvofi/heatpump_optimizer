# The fixer's contract (the standing gate protocol as a checklist)

You own one PR group: one subsystem, at most five findings, at most about 400
production lines. You work in your own worktree branched from `origin/main`.
Read only your roster group (`jq`). Run a job outliving your turn as a
background task, whose exit wakes you; never end a turn on a detached one.
Wait on CI through one `seat/ci-watch.sh` or `seat/proof_watch.py` (the 60 s
API floor is theirs), woken by its exit, never polling;
past the handoff, do not wait. Rotate to a fresh context between stages (rca,
fix, handoff) through refs, never mid-task, by ~150 k tokens (S, M), ~300 k (L, XL).

1. **Never touch `VERSION`, the manifest version or the `RELEASE_NOTES.md`
   heading** (`CLAUDE.md` rule 4). The rule is keyed on the manifest's
   `version` field, not the file; the command is `prepr.sh` step 5's.
2. **Failing test first**, importing the production symbol (a test that
   re-implements a formula pins nothing; `tests/README.md`). Record the
   mutation proof in the PR body: delete the fix's production line(s), run
   the closure, paste the failing check names, restore. **Mutate the predicate,
   not the tail**: a line past a script's own return changes nothing, nor
   `exit $?` to `exit 0` under `set -e` (write `|| true; exit 0`; #2709), and a
   vacuous mutation reads exactly like a passing check.
   A guard that classifies text by shape is driven over a generated spelling
   corpus (case, quoting, glued options, delimiters, wrapping) with the corpus
   size named in the body; a spelling the reviewer finds is added to it.
   A `git archive` copy fails the #363 `recorded_at` check, and a self-test
   needing a checkout, on every mutant, baseline included.
   **The diff's survivors are yours before the handoff; `--pin-killed` is
   `ci-autofix.md`'s.** Set `prepr.sh`'s `MUTANT_CMD` to the group's self-test
   or a `features_block.py` call (`MUTANT_IN_PLACE=1` for a checkout); it draws only
   the first 40 mutants of added `.py` lines outside `tests/` and `dev/`. Each
   `SURVIVED` line and step 6d unpinned site gets a killing check or an `## Unpinned
   sites` disposition: pinned by `mutation-autofix` (its lane mutates `custom_components/`
   only; a `tools/` site needs an in-tree mutant harness), a value check, or a triage under
   `tests/mutation_ledger/survivor_triage/` (the ratchet reads no body). Run the
   ledger's own mutant before claiming a kill (#2445).
3. **Re-execute the finding's harness on your branch**: before and after, with
   the head SHA measured, in the PR body. It may not be at your head — a round's
   `D*/*.py` harnesses stay out of the tree (a Linux-only closure re-derivation;
   commit `21acaf8e`) and its register can merge after you — so run it from the
   baseline export and cite `$EXPORT/<path>` with its sha1, which `figure_lint`
   reports unverified, not refused. A harness measuring what the fix rightly
   leaves alone reads flat at both ends: say so, and add a sha1-cited companion
   applying the tree's own rule to the same inputs, reading the defect at the
   baseline and not at the head. A fold deleting a name the harness drives
   leaves only its count arm readable at the head;
   the fixer ports the rest, as its own (`fix-review.md` step 9; #2365).
   **Every quantified claim carries a null control, not only cost, gain and
   time**: a count, a percentage, an "every" or a "none" is a measurement, owed
   the command that produced it and the result that would have appeared had it
   been false. **Never print a conclusion beside a command** — `diff a b &&
   echo IDENTICAL`, never `diff a b; echo "(empty means identical)"`, which
   prints either way. A figure from a sliding window, or one an instrument
   prints, is stale after you write it: state the rule or name the instrument,
   never the number. A learner or guard change is measured at both ends of its
   input range — an install with zero evidence, and one on the clamp — a fix
   has been worse than its bug before.
4. **Goldens that move are claimed by whoever measured the drift**, in
   `tests/golden/claimed_drift.txt` or `card_claimed_drift.txt`, with the
   expected direction per fixture. `claims-for:` stays at the live `VERSION`.
5. **Measure the gate's scope, then run what it names.** Derive it:

       D=$(mktemp -d); python3 tests/closure.py select \
         --diff $(git merge-base origin/main HEAD) --workdir "$D"
       cat "$D/scope.txt"; cat "$D/scope.run"

   Key on the **mode line**, never the count (`CLAUDE.md` rule 1). Run what
   `scope.run` and `tests/run.sh`'s `run_always` lines name, with
   `PYTHONPATH=tests/hastub`, leaving the rest to CI (`tests/README.md`, "The
   scoped gate"): `MODE: FULL` is a diff the gate cannot scope (a gate file,
   a doc, a scratch file: keep the body out), not CI to reproduce.
   **No scope selects `card_browser.mjs`**, which CI runs past the handoff:
   run it on a `GRID_SURFACE` diff (recipe: `web-fragments.md`; #2841).

   **Running locally does not discharge CI.** What `scope.run` names is green,
   every red `prepr.sh` step 6d predicts is repaired before the handoff
   (`ci-autofix.md`'s wait starts at the PR), and the body passes
   `tools/pr/prepr.sh`, run on a committed tree (step 6f reads `HEAD`; 7e is
   the carry check); the orchestrator opens
   the PR (`docs/decisions/0011-app-authored-identity.md`).

   **`ci_predict.py` printing `BOOTSTRAP`** (the base's copy of the changed
   grader refuses, the head's passes in `prepr.sh`) is not `BLOCKED`: register
   in unpinned data the grader reads (`corpus_excluded.json`, #2916), or split:
   p1 the grader hunks alone, p2 the rest, a WIP handoff until p1 is on main
   (decision 0013, Consequences).

   **`run.sh` takes the gate lease itself, around `tests/stress.py` alone**;
   the queue, the wait bound and holding it by hand are `gate-scoping.md`'s.
   A mutation proof leaves `stress.py` to CI's required mutation check: never
   run it locally per mutant.

   `GOLDEN_MODE=drift` against the merge base always (`CLAUDE.md` rule 3);
   `python3 tests/structure.py` before every push.
6. Hand off to the adversarial fix reviewer. **After any rebase or merge,
   steps 2–8 are re-executed** (past the handoff, where its delta reaches):
   the evidence describes one tree, and either makes a new one — **the body
   included**, because a figure that is a function of `origin/main`'s tip is
   false the moment `main` moves; stamp it with that tip and `date -u`. The code
   head goes to `handoff/<topic>`, the body to the orphan `handoff-body/<topic>`
   by `seat/body_push.sh`, whose offline `review_packet.py handoff` refusals you
   answer first. That push is the handoff; `handoff_push.sh` opens the PR.

   **The handoff freezes the branch.** Until then, merge `origin/main` (never
   rebase) only when `git merge-tree --write-tree origin/main HEAD` reports a
   conflict or the head is `DIRTY`. A delta re-applied to
   a branch cut from an older base is diffed line by line against its
   sibling's head, or a stale copy reverts it (#2368). After it, the head is
   the reviewer's measuring surface and **only the orchestrator, the merge-main
   bot or `--carry` moves it**: a mid-review move leaves the reviewer unable to
   tell which numbers still describe the tree.
   **A conflict with main after it is resolved by merge, never a re-cut**
   (tvofi, 2026-10-01): the orchestrator merges `origin/main` into the head, or
   hands you a semantic one to merge alike; the same reviewer judges that delta
   alone (`fix-review.md` step 12). Landing is the **orchestrator's** or its release seat's.
7. The PR body closes its issues (`Closes #N`), names the head SHA measured
   (a `--carry` head: no re-take; name bot reds), and carries every executed
   number in `## Figures` with its command.
8. **A quoted number states the rule that produced it, not just its value.**
   Only a count whose rule is written down is re-derivable. **Name the instrument you re-ran, and its scope.** If the
   block you are clearing was demonstrated with an *instance*, your verification
   may not be a search for that instance — it must check the property the
   phenomenon states, not the property the block's text states: name a rule that enumerates the class's seams (a command,
   not a description), run it, and put every seam it returns in `## Figures` against
   its disposition — closed in this diff, already guarded, or a distinct finding named
   by id. An un-dispositioned seam is an open seam, class not closed. If no such
   instrument exists, say so and what you did instead. This is step 11 applied to
   your own instrument: one inherited from the finder is keyed to the instance it
   demonstrated (#592's root cause).
   For a P2 finding, the rule step 8 names is a registry entry in `tests/entities.py`'s P2
   owners block (fact, shape, owner, dispositions), landed in the same PR, not a one-shot
   command. Where the fact has no syntactic shape (physics consistency, failure signalling,
   cycle fencing), the PR extends or adds a census that drives every sibling it enumerates with
   the same input and compares their outputs, and **the census asserts its own preconditions**
   (a census that skips a class of slots refuses the day a skipped slot gains a writer).
   A fix that changes one reader of a governance concept registers the concept in
   `agreement.mjs` with every reader the enumeration returns.

9. **A claim should be true; if wrong, correct it — anchored to a lane,
   function, marker or SHA, never a bare line number — and delete only when
   no such correction exists.** Delete on sight, not as a last resort, when
   the claim is only motivation or scaffolding the finished text doesn't need.
10. **If the wrong text is generated, fix the generator first, and run it.**
    Correcting prose a script emits leaves the script emitting the old text on
    its next run, so the correction is undone rather than kept. Grep for the
    wrong form across the whole tree before deciding what to edit.
    **A generator fixed without being run is a claim, not a fix**: run it,
    paste what it now emits, and run it at the merge base as the control.
    Text that *instructs* differs from a record that *recounts*: a measurement
    record stays as written.
11. **A check pins the artifact it reads, not the one it is named for.** The
    #546 check read the constant `apply_topology`'s schema is built from, so a
    schema that stopped agreeing with it was invisible (#550). Read the
    registered artifact, as `tests/entities.py` does. Then probe a key the read
    does **not** name: under `extra=vol.ALLOW_EXTRA` the read set is still
    exactly right while the schema accepts anything, so the probe is the
    reader's own null control.

    **Say where a check encodes a design choice** (#546's settled which of two
    artifacts was authoritative): saying so stops the next seat reading a
    legitimate tightening as a bug.

12. **The seam a method belongs to is its entry in `tests/seam_map.json`
    (#1539, 548c818), not its name.** A new or renamed coordinator method is
    refused by the ratchet until you add its entry by hand, in the same diff,
    with the seam you chose. Never run `--seed-seam-map`: it re-derives every
    entry from the retired name rule. Before pricing an extraction, say which
    seam each candidate carries in the map.

13. **`tests/hastub` is not Home Assistant, and a green test may pin the stub.**
    `tests/ha_contract.py` records each stub symbol's fidelity and runs its
    contracts against the stub and, nightly, the real package. **Before
    asserting that a test proves a production property, check whether the stub
    satisfied it.**

    If your work depends on a symbol's upstream behaviour, add or read its
    contract; if you extend the stub, argue the fidelity against upstream, not
    what your test needs — that shape agrees with a wrong implementation.

14. **An allow-list is keyed on something, and your entry silences everything
    that key matches.** Before adding a case to a pin, a baseline or a
    suppression list, name the key's fields, name the property that makes your
    own occurrence legitimate, then key the occurrence the pin exists to catch
    and compare the two. Equal keys blind the pin at the site it watches, and
    the answer is to change the route until no entry is needed, or to widen the
    key until the two separate — never to add it and note the risk.

    **A fix that changes the route leaves the reported text where it was, so
    name the route.** #714 rerouted the caller and left `worker.wait(timeout=2)`
    in place: grepping the report's call, file and snippet reads the defect as
    open, and grepping for their absence finds nothing and reads the same.
    Anchor the claim to what moved: branch, registration, frame count.

15. **A bitwise-parity claim over numpy reductions is per-architecture.**
    `np.sum(matrix, axis=1)` is not `np.sum(matrix[b])`, and neither is a
    reduction over a row VIEW of a batched array one over the fresh array the
    scalar expression builds: numpy's pairwise loop takes alignment and stride
    as inputs, per backend. Where the contract is bitwise, run the SCALAR
    EXPRESSION per row, on the fresh per-row arrays that expression's own
    elementwise ops allocate — batch only what is elementwise end to end — and
    drive the parity grid at the production width.

    The same rule holds one level up and across interpreter versions: a
    reduction whose scalar form is a PYTHON BUILTIN is compensated arithmetic
    on CPython 3.12+ — builtin `sum` is Neumaier — and no vectorized
    accumulation reproduces it. Make the twin call the scalar closure's own
    function per row, and put detector rows on the parity grid that separate
    the two summations, so the interpreter class that diverges — CI's — runs the detector.

    A per-row twin removes re-entry, not work; when it is the fix for a
    recomputation finding, re-measure the finding's cost on the fixed tree and
    report it; if parity forbids vectorising, the fix is a recorded partial with
    its remaining share, not a close.

16. **An age computed from a stamp ahead of the reading clock is unknowable,
    never 0** (#775's refusal; #1532 pinned the technique #775 had refused).
17. **Take the fix that yields the better code; it is architecturally sound**
    (tvofi, 2026-10-08). Where one fix satisfies the check and another removes
    the cause or simplifies the design, take the second; the body names the
    alternatives and why each lost. Soundness is judged on added lines:
    - one owner per concern: the module owning the concept, or a small new
      one; `coordinator.py` orchestrates and does not compute;
    - no `homeassistant` import added to model, optimizer or learner modules
      (`dhw_learning.py`, `defrost.py` and others hold one); the HA glue
      calls into them, never the reverse;
    - side effects at the edges: entity reads through `inputs.py`'s
      `InputReader`, actuator writes from the coordinator or `pump_arbiter.py`,
      store, network, notification and issue-registry calls in the module
      owning that edge; computation stays pure;
    - inputs passed in, no `entry.options` read below the glue; module state
      only as a per-coordinator `WeakKeyDictionary` side table (`boost.py`);
    - units in names; a constant beside the module owning it, one shared
      across modules in `const.py`; each literal justified;
    - missing or invalid input returns `None` or refuses, never a guess;
    - the existing mechanism, never a parallel one: entity descriptions,
      repairs, diagnostics, translations, the store's versioned migration;
    - the smallest public surface, testable without HA; no concept duplicated;
    - `tests/structure.py` and `tools/audit/archscore/score.py --diff` not
      regressed, or the raise path below where only it lands the better
      architecture; a production diff also takes sound score gains in code it
      touches, dS in `## Figures`;
    - a group's architect note (`orchestrator.md` section 5) followed; a departure is raised, not made.

    Cost is no reason to take the worse fix; the preamble's scope still binds,
    and a fix not sound within it stops and asks the orchestrator. An
    improvement claim names its mechanism, which the reviewer removes as the
    null control (`fix-review.md` step 14). Never move a metric by a change
    that does not improve the code: a mechanical split, code moved to an
    unmeasured path, a triage on a killable mutant, or cases enumerated where a structural fix exists.
18. **What a later round or seat reruns, or a body figure needs reproduced,
    lands in the same pull request** (tvofi, 2026-10-03): a harness in
    `dev/audit/harnesses/`, a driver or env recipe in `tools/audit/seat/`,
    classified (step 5); a one-off probe, or a reviewer's driver, stays in
    scratch or evidence. A new harness is a predicted closures red
    (`tests/harness_headers.py` reads the directory) that
    `tools/pr/ci_predict.py --apply-inert` repairs before the handoff.
    `git status` lists each (`git check-ignore -v` names a local exclude hiding
    one); `tools/audit/seat/tmp_paths.py` refuses temp or machine paths.

**When a budget blocks the work** (`tests/structure.py`, or a cap
`policy_lint.mjs --budgets` prints), the answers come in order (tvofi,
2026-10-03). **First pay** with a change that objectively improves the code: a
simplification, removed duplication, deleted dead code or spent prose,
never a step-17 shape. Re-record where the tree genuinely improved. **Raise only
where the raise is the only option that truly improves the code** (`--record --allow-regression="<reason>"`, that
reason in the **commit** message: `main`'s history keeps a commit message and
never a pull-request body — decision 0010, true under either merge method).

**Ask which class the budget you fear is even measured on.** Some rows come from
the single class named by `COORDINATOR_CLASS_NAME`; the rest from every parsed
module. A method added outside that **class** moves none of the first group, so
the payment question does not arise there. *Class*, not file: `coordinator.py`
holds several; `CoordinatorContext` additions move no row. Derive the split at your merge base.

**An empty payment pool is a halt only where a payment was owed.** Let
`python3 tests/structure.py` name what moved at your merge base. Outside the
coordinator class a split moves the maxima *down*; re-record them.

A raise is the owner's, confirmed before the push (`CLAUDE.md` rule 2); zero
headroom is no veto on new functionality or the better fix (#398). **The ask and the PR body list every
payment you considered and why each was not taken**, measured where possible,
never a bare assertion; the reviewer judges them (`fix-review.md` step 14).

## Before you hand off: carry what you found forward

Your PR does not merge until any finding that **changes how a later stage must
work** is in that stage's own brief — `finding-propagation.md` states the test,
what to write and where it goes, and a comment on this PR discharges none of it.
Name the destination in your PR body — which brief, contract, carry file or
roster received it — so the reviewer checks the destination rather than takes
your word.

**A finding in your own group's seam is built in this PR, not carried.**
`Carry: <own group>` only names a pending owner or orchestrator ruling, or a
split part the approved plan names.

## Before you hand off: answer any check your branch turned red

`defect-root-cause.md`'s second trigger fires on your own PR, as its Enforcement section states.
`UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them (`ci-autofix.md`).

## Past three rounds, re-cut rather than repair

The owner's rule. At the **fourth** round, replace the body under a `## Re-cut`
note, which `bus.sh dispatch` requires: the headings `.github/PULL_REQUEST_TEMPLATE.md`
requires, the arms that fire, and only figures re-taken in that pass. Round
history is deleted, not restated — except a **disclosed self-correction** (`dev/programme/HANDOVER.md`'s #1058
tie-break). **A re-cut body blocked on `claims` again is a signal about the fix**:
the orchestrator splits or closes it.

**Never for a mechanical-only gap** (tvofi, 2026-11-09): `bus.sh dispatch` reads the
latest block's class and dispatches with no `## Re-cut` when it is `ci-red`,
`red-unanswered`, body or contract, `conflict`, `head-moved`, a carry or an ungated
step. A CI-only block (`ci-red`, `ci-wait`, `ci-pending`, a cancelled run) is
mechanical and does not count toward the three-round rule; a judgement class, an
unknown one or an unreadable log refuses.
