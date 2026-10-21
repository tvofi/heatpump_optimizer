Fix review: merge 3449af66fe527a9681f4308d732a236bc9f2fbd7

bus-nonce: ba2ca656e9b4b1d5ae92441ce857063d

Round 2. Head 3449af66fe527a9681f4308d732a236bc9f2fbd7, unchanged from the
dispatch; measured in a detached worktree at that SHA
(`~/hpo-seats/r10s3/r10-sav-reasons-review/wt`), merge base
`9fdc5846afe72a5edbd90a4c86cf92f74e62020c`. Evidence:
`~/hpo-seats/r10s3/r10-sav-reasons-review/evidence-r2/`. Box load1 2.1-4.8;
every wall clock below was taken inside that range. The booking harness is the
FIXER'S own — it first appears in this branch's commit `0ca2fafd7` — and the
body does not claim otherwise; I built one instrument of my own,
`reviewer_exhibit.py`, disclosed below and copied into the evidence dir.

## The two reds the fixer attributes to this box — confirmed at the merge base

`tests/optimality.py`, run from each tree's own tests, concurrently:

    FAIL one|summer_negative|shoulder: a recorded claim still has a gap
    cert one|summer_negative|shoulder obj  0.254795  re-polish +0.0000%  ladder +0.0000%  claimed=True
    1 of 84 OPTIMALITY CHECKS FAILED

The merge base and the head print the same cell, objective, both gaps and the
same 1-of-84 count (~90 s each, load1 2.1-4.8).

`tests/stress.py`, both ends: `FAIL shoulder: cheaper than holding the setpoint
[4.67 vs 3.96]`, `1 of 113 STRESS CHECKS FAILED` at both (~4 min 15 s each).

Both reproduce identically at the merge base, so neither is the diff's.

## What I confirmed

1. **The finding.** `sav_reasons_booking.py` at the merge base books
   `reason:idle 0.4 / reason:untagged 0.0` and `space_reason 'idle'`; at the
   head `0.0 / 0.4` and `'boost'`, `dhw_reason 'idle'` both ends. The harness
   moves under its own perturbation. Its `shasum -a 1` is
   `5396e54c685a9faf5f6526a82dcb52440d558dbc`, the body's figure, re-derived.
2. **The typing repair.** `~/.local/state/hpo/venv-ha/bin/python
   tests/typing_ruler.py --mypy` at the head: `errors did not grow`,
   `type_ignores did not grow`, `ALL 9 typing-ruler checks PASSED` (12.3 s).
   The repair is a narrowing (two branches, `if reason and ...`), not a widened
   type; the diff adds no `# type: ignore`.
3. **The two base reds.** Reproduced, above.
4. **The red answers.** Head check-runs: `typing` success, `mutation` success,
   `nightly-status` failure. `typing` and `mutation` are named and true; the
   mutation lane's log reads `baseline tests/features.py: rc=0 failed=0`,
   `0 survivor(s) of 5 evaluated`, `MUTATION TABLE PASSED`, so the green is
   measured, not INCONCLUSIVE. `nightly-status` grades `main` and the diff adds
   only its own delivery row, so `defect-root-cause.md`'s exemption applies and
   no answer is owed.
5. **The rule under attack.** An exhibit exists; it is a seam this PR does not
   close, disclosed in the tree and outside the group's owning seam, so I do not
   block on it (section below, with its carry).

The mutation proof, re-run as step 1 requires: the body's mutation 1
(`code = reason`) applied to `ledger.explain_metered` in its own worktree and
`PYTHONPATH=tests/hastub:tests python3 tests/features.py` run (~3 min 46 s):
`5 of 4267 FEATURE CHECKS FAILED`. The four R10-SAV-REASONS checks the body
names all fail with its quoted details (`idle={'kwh': 0.4, 'sek': 0.8},
untagged={'kwh': 0.0, 'sek': 0.0}`; `{'cheap_price': 2.25, 'idle': 0.75,
'untagged': 0.0}`; the arms). The fifth is the older `an interval without a tag
books as untagged, not as nothing`; the body's `## Unpinned sites` names the
absent-reason arm, so the proof stands. At the head every named check is green.

The ratchet and the body: `tests/structure.py` at the head prints `STRUCTURE
RATCHET PASSED`, every row `<=` its budget, `recorded_at 4e5801eb5064` an
ancestor of HEAD. `tests/structure_budgets.json` moves four rows DOWN and
raises none, recorded in its own commit with its reason. `VERSION`, the
manifest and the notes heading are untouched; both claim files byte-identical
to origin/main; `merge-tree --write-tree origin/main HEAD` exits 0. `prepr.sh`
with `PREPR_SKIP_CLOSURES=1` on the body: `PRE-PR: 3449af66...` rc 0,
`pr-body 0 error(s)`, `FIGURES: 10 resolved, 13 not verified, 0 refused`,
`CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`.
The `## Head` check accepts `5fd7c769a` plus the autofix commit `3449af66f` on
top of it. The ADVISOR carry is in `handoff/audit-r10-roster`'s R10-ADVISOR
`brief` (current tip `aaf70eb2d`), stating both the control (`tests/card.mjs`
pins the fallback) and the gap (the map). The body's cited tip `0d34adee` does
NOT carry it; the branch does, so the carry has landed.

## The rule the fixer asked to be attacked first

Executed, both ends, with `reviewer_exhibit.py` (mine):

    PLAN  space 1.0 kW (cheap_price)  dhw 0.0 kW (idle)   METER 3.0 kW for 1.0 h
      spot 3.0   reason:cheap_price 3.0   reason:idle 0.0   reason:untagged 0.0

The plan commands 1.0 kW in total and nothing on DHW; the meter sees 3.0 kW and
the whole draw books `cheap_price`. The body's rule — "a channel whose reason
says the plan drew nothing … books REASON_UNTAGGED" — is not reached for the
idle channel, because `dhw_share = planned_dhw / planned_total = 0` hands the
whole unit's energy to the running channel before `explain_metered` sees it.
So when the excess IS the idle channel's draw (the body's own "standing draw"),
it books the running channel's cause: the owner's complaint at a smaller scale.

Non-blocking, on three measured reasons. The meter is a point sample of the
whole unit (`actual_power_kw`, multiplied by the interval), so neither I nor
the fix can separate that draw from the running channel's own cycling — the
magnitude rule was measured unsound in round 1 and remains so. The split is a
pre-existing, thrice-documented limitation (`_accumulate_energy`'s,
`explain_metered`'s and `sensor.py`'s docstrings: "one meter, two circuits").
And the owning seam is reason tagging; the split is the architect note's
after-edge, not this diff's. `R10-HEAT-METER` replaces the plan-based split
with a measured, mode-based per-interval one, and must feed the reason lines,
not only the COP learner. Carry: R10-HEAT-METER — the orchestrator lands it in
that group's `brief` before this merge, per `finding-propagation.md`.

## What I could not establish

The gate's `10306 s` wall clock: not re-derived — the heavy run is CI's, and the
local closures skip is the owner's ruling. The archscore `dS +0.0023`: not
re-run; CI's `arch-score` is green and the delta since round 1 is data rows. The
body's "`1 unpinned site(s)` the diff adds": not reproducible at this head —
`ci_predict.py --base 9fdc5846a` prints `no closures or fast red predicted …
(a data-file read is not seen)`, because `3449af66f` pinned the last site.

## Code-owned?

No. No path the diff touches matches `.github/CODEOWNERS`, GitHub has requested
no owner review, and `tests/stress.py` — which the brief names — is not in the
diff at this head (nor in any commit of the branch). The approver App's review
is the one this PR needs.
