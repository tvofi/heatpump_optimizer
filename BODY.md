Part 1 of R10-COP-GATE (#2262). Part of #2262; it does not close here (the
roster gives this group `fixes: []`), and the group's remaining carries are a
second pull request in this group, on topic `r10-cop-gate-p2` (see
`## Forward-carry`).

Without a heat reading the COP learner reads a ratio of metered draw to the
plan's ask as efficiency, which is a COP only while the draw follows the ask.
On the owner's install (STUDY R10-IDENT Q2) it does not: the running-draw
window's own rule, `draw_range.follows_ask`, reads False on the owner's
running pairs (log-log slope under `FOLLOW_SLOPE_MIN`). The tree had no state
that said so, and it still folded the intervals that happened to land within
`COP_ASK_TOLERANCE` of their ask.

This adds the honest state and the draw-follows check (L3). No threshold
changes: `COP_BASELINE_MIN_SAMPLES`, the tolerance, the duty floor and the
tracking gate are untouched.

- `accuracy.cop_observability`: `heat_metered` (a heat counter or the thermal
  power entity, `probe_install(...).measured_heat`, over an electrical
  figure), `draw_follows_plan`, `not_measurable`, `awaiting_draw_evidence`
  (follows_ask None), `no_electric_meter` (nothing to divide by). Which
  electrical figure divides is the install probe's,
  `InstallCapability.cop_electric()`: a heat counter's span divides by the
  electric counter `heat_pump_energy_entity`, any other reading by the power
  entity.
- `MeasuredCop.judge_ratio`: once `follows_ask` is False an interval is
  `draw_off_ask`, inside the tolerance or not. A draw that follows its ask,
  and one with no evidence yet, behave as before.
- The observed-COP sensor waits for `heat_meter` while `not_measurable`, and
  publishes `measured_at`, `last_refusal` and `observability`.
- D15 seam (2): the latch carries the instant it folded (`MeasuredCop.at`,
  persisted; a record stored before it loads with the age unknown, not now).
- D15 seam (3): the accuracy residual is `MeasuredCop.residual`, taken only
  from a COP folded after the settling interval opened, against the curve it
  folded on.
- Carry 4 (draw pairing): the pending prediction records the interval's own
  `split` and `flow_command`, and `draw_range.fold` reads those inside
  `accuracy.pairs_interval`'s window, the one owner of `0.05 <= h <= 2.0` for
  both readers.

Alternatives for the electrical-figure rule (fixer.md step 17): reading it in
`_learning_view` off the entry mapping lost, because the entry-config census in
`tests/entities.py` refuses that in a migrated module and it put an
install-capability rule in the coordinator. `heat_energy.meter_of(self).counter`
also lost: only the first observed cycle sets it. The probe already owns
`measured_heat` from the same keys, so it owns this rule too.

## Re-cut

Round four's body, carried through a merge of `origin/main` at `1148ee635` (the merge of #2917, part 1). Every figure below was re-taken on the merged tree in this pass; round history is not restated.

## Head

`9db84212731f2cce6fce2a8dda34dbf07fecee0f` (`9db8421`): a merge of origin/main `1148ee635e8278ebbb033b524d54001b2a89218c` into the PR head `2c162670b4dfcf450fe2ac74fd604100e0b64ead`. The merge applied with no conflicts, the claimnotes driver installed (`python3 tests/env_drift.py --install-merge-driver`). `git diff origin/main HEAD --name-only` names `dev/programme/delivery/2975.md` and `tests/features.py` only; the second holds the round-four check. `git diff --quiet origin/main HEAD -- VERSION RELEASE_NOTES.md tests/golden && echo identical` printed `identical`, so both claim files are main's own and this branch claims nothing (claim-files.md); `python3 tests/env_drift.py --claims-only 1148ee635e82...` prints `claims hygiene: ... ok`. No production line is added over main.

## Mutation proof

The mutation proof of round four stands: the merge touches no production file, and `git diff origin/main HEAD --name-only` shows the only code delta is `tests/features.py`. Mutants (all in `accuracy.py` and `coordinator.py`) and their kills are recorded in the previous body of this topic (`handoff-body/r10-cop-gate-r4` at `ba126f00a`). They were not re-driven in this pass: the production lines are main's, and the check that kills them is unchanged by the merge. The merged tree runs it green (see Figures).

## Null control

The previous body's controls stand (unmutated tree green; the 30-minute prediction pairs both readers). The merged tree's unmutated run is the control in Figures.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/features.py` at `9db842127`: `ALL 4586 FEATURE CHECKS PASSED`, rc=0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, running `tests/entities.py` and `tests/features.py`; rule: merge base is `1148ee635`, the instrument prints the count. `tests/entities.py` was started and is left to CI (it exceeded this seat's time bound); `tests/features.py` is the run above.
- `tests/closure.py selftest`: `ALL 117 closure shrink pins PASSED`; `tests/layout.py`: `layout self-test: ok`.
- `python3 tools/pr/ci_predict.py`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 1148ee635e82`.

## Unpinned sites

None: the diff over main adds no production line.

## Red checks

- `pr-contract` / merge verdict at `f6ff3e56`: refused carry on `tests/golden/claimed_drift.txt` because the branch's copy diverged from main's after #2917. Answered here: the merged claim files are byte-identical to main's. Cheaper detector: `tests/env_drift.py --claims-only`, already in `run_always`; no new one owed.
- DIRTY against main after #2917 merged: resolved by this merge, not a re-cut (fixer.md step 6).
- The checks answered in the previous body (`fast`, `coverage-ratchet`, `mutation-autofix`, `mutation`, `instrument-self-tests`, `delivery-status`, `nightly-status`) are unchanged by this merge, and their answers stand there.

## Forward-carry

Destination: the roster entry `R10-COP-GATE` in
`dev/programme/rosters/wave-r10-groups.json`, which already carries each text
(numbering is its `carry` array, 1-based). Part 2 of this group, topic
`r10-cop-gate-p2`, delivers them. Carry: R10-COP-GATE

- Carries 6, 7 and 14: the heat-pump grade's hover reason codes, the
  plain-words metric text, and the `envelope_drivers` interface mirror.
  Carry: R10-COP-GATE
- Carries 9 and 10: the vent latch freezing COP/DHW/buffer/sysid, and the
  sticky freeze reason. Their own text says VERIFY first, plus a design note,
  before code. Carry: R10-COP-GATE
- Carry 12: the learned top's consumer through `draw_range.planned_range`.
  Carry: R10-COP-GATE
- Carries 13 and 16: `_fold_flow_lift` reading the interval's attribution.
  Carry: R10-COP-GATE
- Carry 8, in part: the refusal codes render verbatim here, but its control
  (a counter install with no electric counter shows `unaligned_meters`) is
  not measured. This head publishes `observability=no_electric_meter` for
  that install. Carry: R10-COP-GATE
- The `pr_args.sh` `mut:unlock` liveness race (under `## Red checks`) belongs
  to that instrument's owner. It changes no later stage of this group.
  Carry: R10-COP-GATE

Delivered here: carries 1, 3 (seams 2 and 3), 4, 5, 11 and 15. Carry 2 is
R10-UX-HEALTH's. Carry: R10-COP-GATE

## Friction

- brief-scope: cost: the group's carry list holds 16 entries, across COP eligibility, the heat-pump grade UI, a vent-detector design study and the flow-bias gate, against an M size and one owning seam. One seat could not deliver it in the 2 h bound, so the group lands in two parts. Carry: R10-COP-GATE
- fix-review: stale: the block was measured at `67ffb958b`, and `c9bf05dfe` already carried three of its four answers when this seat was dispatched. A re-dispatch keyed on the verdict's head, rather than the live head, re-ran work already done. Carry: R10-COP-GATE
- mutation-table: cost: a GUARD_OFF pin is the `if False:` form only, so a guard whose `if True:` mutant lives (the reviewer's m10) reads as pinned in the ledger. Carry: R10-COP-GATE
