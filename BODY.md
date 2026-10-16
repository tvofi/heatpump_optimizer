The four-`prepr.sh` cap in `nudge.md` §8 becomes a lease it cannot exceed. `tests/gate_lock.py` gains a slot-counted pool beside `stress.py`'s exclusive lease; `tools/pr/prepr.sh` takes one slot for its whole run and hands it to its heavy steps; `tests/derive_closures.sh` takes one standalone; `tests/run.sh`'s lease arm dispatches `needs_lease`'s new third answer; `gate-scoping.md` and `nudge.md` §8 state the scope and that the lease, not the tick's count, is the enforcement.

Why. The cap was the orchestrator's, held by hand and enforced by nothing: the tick counted and flagged it, and nothing blocked a fifth. On 2026-10-14 ten ran at once, each spawning a nested `--self-test` chain, and `load1` reached 168 on 8 cores. The rule now written down: a script that MEASURES the machine takes the exclusive lease (`stress.py`, `harness_headers.py`); one that is multi-minute CPU-bound joins the four slots (a `closures.json` recording at or above `SLOT_MIN_SECONDS`); one that takes seconds runs unleased. The classifier is derived from the recordings, never carried, so a script that gets heavier moves itself into the pool the next time the recordings are re-taken.

Closes #2267.

## Head

`f36c16eebe246227a1ca5cc9c0f8a48e5c6d87f9`

## Mutation proof

Four mutants, each restored with `git checkout --` after its run. The closure of `tests/gate_lock.py` and `tests/run.sh` is `tests/entities.py` (SCOPED, with `harness_headers.py`); `tools/pr/prepr.sh` is graded by its own `--self-test`, which the governance job re-runs.

E1 -- the classifier's slot answer and the owner clamp, both in `tests/gate_lock.py` (`return "slot"` to `return "none"`; the clamp condition to `if False:`).

    PYTHONPATH=tests/hastub python3 tests/entities.py   ->  2 of 2333 ENTITY CHECKS FAILED
      FAIL run.sh leases a FULL or stress run itself, for the scripts that measure alone, and a second one waits  [need=['lease', 'lease', 'none', 'none'] waited=True rc=[3] released=True]
      FAIL the heavy-slot capacity is the cap unless the owner raises it (#2267)  [heavy_slots over (unset,3,8,8+owner,junk,0)=[4, 3, 8, 8, 4, 4]]

The two reds are separate predicates read by separate checks: the first is the classifier's answers over (full, stress, entities, structure), the second is `heavy_slots()` over five environments. No other check moved.

E2 -- the third answer's two consumers: `tests/run.sh`'s `slot-auto-lease` line, and `tests/derive_closures.sh`'s join guard (`if [ -n "${HPO_SLOT_LABEL:-}" ]` to `if false`).

    PYTHONPATH=tests/hastub python3 tests/entities.py   ->  2 of 2333 ENTITY CHECKS FAILED
      FAIL run.sh leases a FULL or stress run itself, for the scripts that measure alone, and a second one waits  [need=['lease', 'lease', 'slot', 'none'] waited=True rc=[3] released=True]
      FAIL derive_closures.sh takes a heavy slot standalone and joins one it is inside (#2267)  [inside_takes=True outside_takes=True]

The first red is the wiring pin (run.sh no longer names `slot-auto-lease`); the second is the join arm, whose `inside_takes=True` is the mutant and whose `outside_takes=True` control still holds -- so the check separates the two arms rather than passing for a derive that never takes a slot either way.

E3 -- the pool's reclaim branch in `_free_slot` (`if owner.expired or _orphaned(pool, owner):` to `if False:`).

    PYTHONPATH=tests/hastub python3 tests/entities.py   ->  1 of 2333 ENTITY CHECKS FAILED
      FAIL a heavy slot whose owner process is gone is reclaimed; a live owner's is not (#2267)  [stolen=False live_admitted=False]

The reclaim check is the only red, so the capacity row beside it still passes and the mutant kills only the branch it removed.

P1 -- `prepr.sh`'s export of the slot label (`export HPO_SLOT_LABEL="$SLOT_LABEL"` deleted).

    bash tools/pr/prepr.sh --self-test   ->  273 passed, 1 failed
      FAIL and exports its label, so a nested heavy step joins this slot (got 0, wanted 1)

The take, release and join rows all stayed `ok`, so the mutant kills only the export line.

## Null control

Three, one per claim. The pool's: the concurrency harness at six slots admits all five of a five-way race, so `acquired=4` at four slots is the pool's count and not a hard-coded four; and its nested control is the same `derive_closures.sh` run WITHOUT `$HPO_SLOT_LABEL`, which does take a slot, so the "does not re-acquire" arm is the variable and not a derive that never takes one. The wiring's: `bash tools/pr/prepr.sh --self-test` at the unmodified head prints `274 passed, 0 failed`. And the BASE reads the defect the finding states: the same slot commands against origin/main's `tests/gate_lock.py` acquire none (`acquired=0`, `refused=5`), because origin/main has no `slot-take` subcommand at all, and its `needs-lease` answered only `lease`/`none` -- the cap it states is a convention with no mechanism behind it.

## Figures

- `python3 /tmp/r10-prepr-cap/measure/slot_evidence.py /tmp/r10-prepr-cap/wt 4` -> `CAPACITY slots=4 n=5: acquired=4 refused=1`, `CAPACITY null control slots=6 n=5: acquired=5`, `QUEUE waiting=True queued_line=True rc=0`, `NESTED inside_takes=False outside_takes=True` (sha1 `a25ef6a25b10d1cad913ab5193de93a223dd925a`)
- `python3 /tmp/r10-prepr-cap/measure/slots5.py /tmp/r10-prepr-cap/wt/tests/gate_lock.py 4 5 3` against origin/main's `tests/gate_lock.py` -> `slots=4 n=5 acquired=0 refused=5 child_errors=0` (the base arm; sha1 `3281396525c6785d94ca58e7c828389bb71ed5f3`)
- `python3 tests/gate_lock.py slot-status`, while a `prepr.sh` run is in flight -> the run's slot held by label `prepr-<pid>`
- `python3 /tmp/r10-prepr-cap/measure/pgmeasure.py bash tools/pr/prepr.sh --self-test` -> `rc=0 wall=182.8s peak_pg_procs=11 samples=756` (the nested chain's own process group; sha1 `8480b675392ee2d7c399ece6286740fcead8706d`)
- its null control, `python3 /tmp/r10-prepr-cap/measure/pgmeasure.py bash tools/pr/prepr.sh /tmp/null-body.md` (a run that refuses before any heavy step) -> `rc=2 wall=0.3s peak_pg_procs=2 samples=1`

`slot_evidence.py`, `slots5.py` and `pgmeasure.py` are out-of-tree probes under this seat's scratch. On a shared box the box's own other seats move `load1` by more than one prepr chain does, so the chain figure is its OWN process group (`peak_pg_procs`), which is attributable, and never a box-wide load delta.

## Red checks

none. No check ran red on this branch. The one local red during development was this branch's own `prepr.sh --self-test` row, "no early-exit grep reads a pipe under pipefail in the drained scripts", which caught the first draft of the new self-test rows (`printf ... | grep -q` reading a pipe) before any push; the repair is the herestring form in the same rows.

## Approval

Policy. This diff changes `dev/governance/rules/gate-scoping.md` (canon; `.claude/rules/` and `.cursor/rules/` regenerate from it) and `dev/governance/roles/nudge.md`, so the owner's approving review at this head is owed before the merge, and `pr-contract` requires this section. Nothing else in the diff is a policy path.

## Forward-carry

`none`. The finding changes no later stage's brief: `nudge.md` §8 still governs how many preprs a seat starts, and the cap it states is now also the pool's. One observation, recorded rather than propagated: `tools/audit/seat/orchestrator_tick.py` counts `prepr.sh` PROCESSES, so after this change a WAITING fifth is still counted and the tick can flag above four while only four load the box. Its advice ("do not start a fifth") stays correct, and the load it warns about is now bound by the lease whether a seat obeys or not.

## Friction

- `delivery-status-tracking: contradiction: this group's roster entry lists #2267 under `issues` with `fixes: []`, while the brief's Closing paragraph says the pull request names it with a closing keyword; this body follows the brief and closes it.`
- `gate-scoping: cost: the rule sits at a per-file line cap of 61 with no headroom, so naming the pool there cost a line-neutral rewrite that dropped its FIFO and expiry sentences from the prose; they stay in `gate_lock.py`'s own docstring and in the code.`
