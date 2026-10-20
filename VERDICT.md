Fix review: blocked 44ea3af3f1b8c6ca3ad32c6d4edb45920fcf5687 head-moved: measured 44ea3af3f1b8c6ca3ad32c6d4edb45920fcf5687, head is 294bf66ffb463faf842f6a0f43c119b27005b558

Round: 1 at the dispatched head. The PR's earlier review rounds were round 1 at
345cdf58 (blocked carry-missing), rounds 2 and 3 at afabd5b6 (blocked, then
merge). This is not a fourth repair round of one head: I measured a head none of
those reviewed, and the fixer added two test-and-ledger commits since round 3.

## Head, and what the move costs

Measured: 44ea3af3f1b8c6ca3ad32c6d4edb45920fcf5687, the head my nonce
da4664480025ee08a56aadf47e523638 was dispatched at. Before posting I re-read
the head and it had moved: 294bf66ffb463faf842f6a0f43c119b27005b558.

I checked the delta rather than assuming it (`git diff 44ea3af3..294bf66f`):
294bf66f is the merge of origin/main d99b400a5 (PR #2480,
fix/r10-follower-debounce) into 44ea3af3, and the five files it moves are
`.github/workflows/pr-contract-rerun.yml`, `dev/audit/harnesses/follower_debounce.py`,
`dev/programme/delivery/2480.md`, `tests/closures.json` and `tests/entities.py`.
Only `tests/closures.json` is a path this PR also touches, and the merged file
carries both harness entries (`follower_debounce.py` at closure line 3444,
`r10_setpoint_boost.py` at 3476). **Every number below survives the delta**: no
production line, check, mutation-ledger row, harness or delivery row of #2465
moves between the two heads. What does not survive is CI: the runs at 44ea3af3
were cancelled as superseded when the new head arrived (`fast (3.14)`,
`mutation`, `closures`, `lane-proofs`, `composed-proof`, `mutation-pins` all
`cancelled`), so the heavy lanes are unmeasured at both heads and must run at
294bf66f. The body also changed after my first read (three lines: the head line,
the `ci_predict` figure, and the `pr-contract` answer, which now states the
current 6/6 routing); I re-read it and the figures below are against the
corrected body.

## The brief's core: the nine added-site dispositions

The body claims 9 added unpinned sites disposed: 8 `killed_by tests/features.py`
rows and 1 `survivor_triage equivalent` (`pump_arbiter.py:_flow_target
CLAMP_DROP 38a077e7`). I did not take that on its word.

**Re-derived by the in-tree instrument: 1 of 9 attempted, and it REFUSED on
this seat.** `python3 tests/mutation_table.py --anchor '<anchor>' --scripts
tests/features.py` drives the recorded driver; the first anchor
(`draw_range.py:<module> CONST 3b4c559c`) refused:

    MUTATION TABLE REFUSED -- nothing was measured: 1 mutant(s) timed out

(ev/anchor_const_3b4c559c.txt). The seat was running nine drives at once on a
shared machine at load 40-80; `tests/features.py` in this tree spawns its own
sub-scripts (`tests/dst_checks.py` and others), so a single driver run exceeded
the tool's timeout. I stopped the other eight drives rather than queue more
timeouts and re-ran this anchor at a 40-minute floor; its mutant run, baseline
and null control are still in flight at posting. **The 8 `killed_by` rows are
therefore not re-derived by their driver in this verdict, and round 2 at
294bf66f owes that measurement.** What I can say without overclaiming: I read
each of the eight checks against its mutant's operator text and each would
redden for the reason named; the first null control survived every driver in
every run (ev/anchor_*.txt), so the driver's green baseline is not in doubt.

**The ninth, re-derived and sound.** The `CLAMP_DROP` mutant prints `lo=floor_c`
for `lo=min(floor_c, heat_c)` in `_flow_target`'s `_bounded` call. I re-derived
the equivalence myself: `quantise_setpoint_c` applies `max(out, ceil_step(lo))`
then `min(..., floor_step(hi))` with `hi=heat_c`. With `floor_c <= heat_c` both
texts pass the same `lo`. With `floor_c > heat_c`, the mutant raises `out` to at
least `ceil_step(floor_c)`, which is above `heat_c`, and the following cap
returns `floor_step(heat_c)`; the original's `ceil_step(heat_c)` also reaches
that cap, and `ceil_step(heat_c) >= floor_step(heat_c)`, so it returns the same
`floor_step(heat_c)`. The unit conversion is a monotone affine map, so the
Fahrenheit path is equal too. This is an honest `equivalent`, not a triage on a
killable mutant. The fixer's 7680-cell scratch probe and its `lo=None` null
control are named in the ledger but not committed, so I did not re-run them; the
ledger's `--anchor` re-verification is the in-tree check, and it is part of what
round 2 owes.

## The harness, both ends

The finding is the owner's v7.0.1 report; it has no committed finder harness,
and the body does not claim one. `dev/audit/harnesses/r10_setpoint_boost.py` is
this PR's own instrument (added by the diff), so this is the fixer's harness at
both trees and I name it as such.

RESULT harness at head 44ea3af3 (`--no-solves`): `floor: cells 155 heating floor at or below the gate 0`; `window plan: running samples 72 engaged False observed (0.8999999999999999, None) idle 0.3 planned None`; `window probe: running samples 72 engaged True observed (2.9399999999999995, 3.0) idle 0.3 planned (2.9399999999999995, 3.0)`; `failures 0` (ev/harness_head_nosolves.txt)
RESULT harness at baseline 4a3cbcf62 (same instrument, run with the tree as cwd): `floor: cells 155 heating floor at or below the gate 63`; `window plan: ... engaged True observed (0.8999999999999999, 2.034) idle None planned (0.8999999999999999, 2.034)`; probe `engaged True observed (2.9399999999999995, 3.0)` idle None; `failures 0` (ev/harness_base_nosolves.txt)
RESULT harness with solves, both trees, `diff` of the per-plan sha1 lines: identical, 32 plans, `failures 0` at both (ev/harness_head_solves.txt, ev/harness_base_solves.txt)
RESULT relaxed-start control, by each cell's own objective: `spread: cells 16 relaxed start objective lower 8 higher 0 identical plan 8`; `flat: cells 16 ... lower 0 higher 0 identical plan 16` at both trees. The body states the fixer's 0/16 and a reviewer's 2/14 for the flat day and names the solver-environment dependence; this seat reads 0/16, which is the fixer's figure, so the machine dependence is disclosed and reproduced, not contradicted.

Instrument trap found and corrected: `tests/harness.py` inserts `custom_components`
and `tests` *relatively* onto `sys.path`, so running the harness from one tree's
cwd with `PYTHONPATH` pointed at another tree silently measures the cwd's tree.
My first baseline attempt did exactly that and reproduced the head's numbers;
run from the base tree's own cwd it returns the body's 63/2.034. The body's
"both trees" figures are therefore honest, and a later seat must `cd` to the
tree it measures.

## Ratchet

RESULT `python3 tests/mutation_table.py --scope changed --base origin/main` at head: `4147 unpinned site(s) of 6264 candidate sites, 4147 at the ratchet base b701723895a12ef29a9281551ab0fe82643744e2; the ledger agrees with the deterministic inventory` (ev/mutation_scope_changed.txt). The count is back to its base, as the body says.
RESULT `python3 tests/mutation_table.py --pin-killed --base origin/main`: `PIN KILLED -- 0 new unpinned site(s) ... to drive`, `PIN KILLED: nothing to pin`, rc 0 (ev/pin_killed.txt)
RESULT `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against b701723895a1 (a data-file read is not seen)` (ev/ci_predict.txt)

Non-blocking accuracy point for round 2: the body's `## Red checks` mutation
answer calls `mutation_table.py --scope changed --base origin/main` a
"source-only -- no clone, no baseline, no solve" detector and says "`prepr.sh`
step 6d already runs it". Both are wrong as written: once the ratchet passes,
that command proceeds into the sampled mutation table (my run did, and I stopped
it), and prepr step 6d runs `tools/pr/ci_predict.py`, not this command. The
refusal arm *is* source-only and names the added sites in seconds, so the
detector answers the trigger it exists for; only its description is overstated.

## Red checks

RESULT CI at 44ea3af3, the head's own body check (job log, ev/pr_contract_log_head.txt): `record red-history 17 commit(s) between origin/main and this head, every failure conclusion across them: arch-score, mutation`; `PR-BODY: 0 error(s)`; `FIGURES: 11 resolved, 0 not verified, 0 refused`; `no version edit`; `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`; pr-contract success.
Both range reds are named and answered in `## Red checks` (`arch-score` with the coordinator-footprint repair and its cheaper detector; `mutation` with the nine dispositions). No other gate check concluded red at the head; the eleven `cancelled` contexts (`ci-ratchet`, `closures`, `fast (3.14)`, `lane-proofs`, `composed-proof`, `mutation` and the five autofix/pin jobs) are supersession, not failure. At 294bf66f the only red is `nightly-status`, which this diff does not reach.
RESULT the body's cited optimality failure re-derived from check-run 117692786859's own log: `cert one|summer_negative|shoulder obj 0.305809 re-polish +0.0051% ladder +10.5544%` and `FAIL one|summer_negative|shoulder: no unclaimed gap above the bar ... ladder 10.5544%, bar 0.1000%` (ev/optimality_checkrun_117692786859.txt). The body's "+10.55 %" is real; its "main eeb607dd6" names a descendant of the run's head b7a34f98, whose message records that the gap persists on CI's platform.

## Carries

RESULT `python3 -I tools/audit/carry_audit.py check --body <pr body>`: `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry_audit_body.txt; CI's own step agrees).
The six items route to four groups. R10-CEILING-PROBE's three items are in that group's `carry` array at origin/main (landed by `f4d751e49 roster_edit append-carry R10-CEILING-PROBE`), each stating its control — the gain identification, the probe to reach the real maximum with fix B as its prerequisite, and "the ceiling probe's controls should include a gate-held draw above idle" (ev/carry_destinations_full.txt). R10-DEMAND-OVERBOOK, R10-BUFFER-STORE and R10-COP-PARTLOAD each state the carried item and its controls in their own `brief`. Non-blocking: the body still cites `handoff/audit-r10-roster` d8250cd44 as where the destinations stand, and at that SHA the CEILING-PROBE `carry` array is still empty; the items landed on main afterwards, which is the tree the PR merges into.

## Claim files and version

RESULT `python3 tests/env_drift.py --claims-only b70172389`: `claims hygiene: b701723895a12ef29a9281551ab0fe82643744e2 ok`, rc 0 (ev/env_drift_claims_only.txt). The diff moves no `tests/golden` or `tests/fixtures` path and writes neither claim file.
RESULT `python3 tests/env_drift.py --all` was started and had not finished when I posted (it captures the environment matrix per fixture set and the seat was contended); I do not report it as run. No fixture the claim files cover is moved by this diff, so the claim half above is the load-bearing one.
RESULT VERSION, the manifest version and the notes heading: no path in the PR diff moves them (`git diff --name-only b70172389...HEAD` matches none), and CI's version-edit step reads `no version edit` (ev/pr_contract_log_head.txt).

## Merge

RESULT `git merge-tree --write-tree origin/main(a2b25bbc5) 44ea3af3`: exit 0, tree `012b1f16`, `LEDGER-MERGE: resolved tests/closures.json` with `inert_reads.tests/harness_headers.py` merged as a set, no `MERGE-CLAIM` line, no conflict (ev/merge_tree.txt). Re-run against the head at posting, `git merge-tree --write-tree origin/main(a2b25bbc5) 294bf66f`: exit 0, the **same tree `012b1f16`** — the merge result is byte-identical to the one measured before the head moved, and the superseding merge carries both closures entries.

## Architecture (fixer.md step 17, added lines)

Sound as far as I can judge: the gate now has one owner (`_gate_c`) and the floor's rule stays in `thermal_model` with the gate passed in; quantisation is at the one write owner (`inputs`), not per caller; `flow_command(coord)` is plumbing and the decision (`_flow_command`) is handed neither the coordinator nor anything that reaches into it; the store reuses its `_ACCURACY` table rather than a parallel record; units ride the names; missing input returns `None`. `coordinator.py`'s class gains no line. CI's `arch-score` is success at the head and at 294bf66f. The roster group's `architect_note` is null, so none was owed.

## Notes, non-blocking

- **A hand-set fractional disinfection floor on a whole-degree entity can re-raise the issue the repair clears.** `setpoint_check._dhw` re-raises when `pump < floor - 0.25`, and the repair now writes the floor quantised to the entity's step. For the integer-°C floors the config selector allows (`_number(35, 55, 1)` / `_number(55, 70, 1)`) the worst case is the 0.2222 K the body names, which clears. But a floor edited into `.storage` at e.g. 48.05 °C on a °F entity is written 118 °F = 47.78 °C, 0.27 K low, which re-raises (`ev/probe_repairs_f.txt`; the probe is mine, scratch only). Rounding a floor *up* would remove the class. I do not block on it: the UI cannot produce that config, and I could not show a reachable one.
- `dev/audit/harnesses/draw_range_evidence.py` still runs against the changed `observed()` return (`ev/draw_range_evidence_head.txt`), because every uncommanded sample is full-power evidence; no break.
- The idle window learned at the gate can absorb compressor draw (disclosed and carried to R10-CEILING-PROBE).

## What I could not verify

- The 8 `killed_by` re-derivations by `tests/features.py` (the driver timed out on this seat; one anchor re-run still in flight at posting). Round 2 owes them.
- The fixer's hand mutants M1-M15 and the 7680-cell equivalence probe: scratch only, not in the tree.
- The owner's export aggregates (54 samples, 41 at p_min, 0.33-0.73 kW, 25.0 written): private, not re-derivable, not reported as confirmed.
- `env_drift.py --all` (did not finish); the claim half ran clean and no covered fixture moves.

bus-nonce: da4664480025ee08a56aadf47e523638
