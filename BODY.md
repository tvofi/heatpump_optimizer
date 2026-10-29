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

Round four: this body replaces the earlier one (fixer.md, "Past three
rounds"). The block at `67ffb958b` (verdict/2917) named four mutation
survivors: `accuracy.py` `pairs_interval` CMP_BOUND x2, `judge_ratio`'s
trailing RETURN_DEL, `MeasuredCop.residual`'s hot-water GUARD_OFF, and
`coordinator.py` `_record_accuracy`'s `if pairs_interval(elapsed):` (the
reviewer's m10). The previous head `c9bf05dfe` already carried value checks
for the first three and an equivalence triage for the trailing `return None`.
This pass re-takes each mutant at that tree and adds one end-to-end check
for m10 and the window's two readers. Every figure below was taken in this
pass. The PR description above is unchanged.

## Head

`836198dbbd3e9af65862718899879f2938d61f1a`, one commit on top of the PR head
`c9bf05dfe0a1b29eb18dd444a8a32983ea781d77` (fast-forward). The commit adds one
check to `tests/features.py` and touches no production line. Merge base with
origin/main: `66974d47312caa46e9817b9aeae7186e9764e560`. No merge in this
pass: `git merge-tree --write-tree origin/main HEAD` exits 0 against
origin/main `d074b94b0`.

## Mutation proof

Driver: a fresh `git worktree add --detach` of the measured tree per mutant
(so `.git` is present). One exact replacement, asserted to match once. Then
`PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/features.py`. The
driver is an out-of-tree script in this seat's scratch, not in the tree.
The six `accuracy.py` mutants and m10 ran with the new check applied on top of
`c9bf05dfe`; `drawguard` ran at `836198dbb`.

- `pairs_interval` `0.05 <= elapsed_h <= 2.0` -> `0.05 < elapsed_h <= 2.0`
  (CMP_BOUND, low end): `FAIL a pending prediction pairs with the interval
  that closed from 3 minutes to 2 hours old, both ends included ...`.
- `... <= 2.0` -> `... < 2.0` (CMP_BOUND, high end): the same check fails.
- the reviewer's m8, `0.05` -> `0.0`: that check and `FAIL a pending prediction
  a minute or three hours old pairs neither an accuracy sample nor a draw
  reading; one 30 minutes old pairs both (null)  [{'1 min': (1, 1), '30 min':
  (1, 1), '3 h': (0, 0)}]`.
- `MeasuredCop.residual` `if self.curve_dhw and self.dhw_temp is not None:` ->
  `if False:` (GUARD_OFF): `FAIL the residual subtracts the curve the COP
  folded on: a space-heating fold that happens to carry a tank temperature
  reads the space curve, a hot-water fold the hot-water curve ...`.
- the same line, `and` -> `or` (BOOLOP): the same check fails.
- `judge_ratio`'s trailing `return None` -> `pass` (RETURN_DEL): `ALL 4583
  FEATURE CHECKS PASSED`. The mutant is equivalent: the method falls off its
  end and returns None. The triage is
  `tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json`
  (verdict `equivalent`).
- m10, `coordinator.py` `_record_accuracy` `if pairs_interval(elapsed):` ->
  `if True:`: `FAIL a pending prediction a minute or three hours old pairs
  neither ...  [{'1 min': (1, 0), '30 min': (1, 1), '3 h': (1, 0)}]`. This
  is the new check. Before it, m10 left `tests/features.py` green (the
  reviewer's run). The ledger's GUARD_OFF pin of this line is the `if False:`
  form, which the tool generates. `if True:` is not one of its operators, so
  the pin never covered m10.
- `drawguard`, the draw reader's own window term removed (`... and
  pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0):` -> `:`):
  the new check fails with `[{'1 min': (0, 1), '30 min': (1, 1), '3 h': (0,
  1)}]`. So the check reads each reader's window separately: the first
  count is the accuracy sample and the second the draw reading.

## Null control

- The unmutated tree under the same driver (`base`): rc=0, `ALL 4583 FEATURE
  CHECKS PASSED`. That is the control for every mutant above.
- Inside the new check, the 30-minute prediction pairs both readers
  (`(1, 1)`) on every mutant run. So a mutant that broke pairing outright
  would not pass as a window kill.
- The new check's own mutant is m10 above: it goes red when the guard it
  pins is removed.

## Figures

- Mutants: the commands and results are in `## Mutation proof`. Rule: one run
  of the full `tests/features.py` per mutant, with the check count as that
  script prints it.
- `tests / mutation` at `c9bf05dfe` (run 40858829119, job 123396748501):
  `MUTATION TABLE PASSED`. That is the CI record that the four sites carry a
  disposition. The new commit adds no production site.
- `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/mutation_table.py
  --anchor "custom_components/heatpump_optimizer/accuracy.py:pairs_interval
  CMP_BOUND 62f6b3b0" --scripts tests/features.py` at `836198dbb`: `baseline
  tests/features.py: rc=0 failed=0`; `null control ... accuracy.py:50
  NULL_COMMENT survived tests/features.py`; `PIN RE-VERIFICATION: 2
  reproduced, 0 not reproduced`; `killed by tests/features.py:
  ...accuracy.py:787 CMP_BOUND` twice. The other four anchors were not driven
  through the ledger tool, which runs `tests/features.py` serially, about 9
  minutes a run, several runs an anchor. The hand mutants above drive the
  same lines. A first attempt under the container's `python3` read
  `MUTATION TABLE INCONCLUSIVE`, its baseline red on `ModuleNotFoundError: No
  module named 'voluptuous'`: the interpreter, not the tree.
- Scoped gate: `python3 tests/closure.py select --diff
  66974d47312caa46e9817b9aeae7186e9764e560 --workdir D` prints `MODE: SCOPED
  -- 27 script(s) run, 6 scoped out`. This pass's delta is
  `tests/features.py` alone, which passes in full (above). The other
  `scope.run` scripts are left to CI. At `c9bf05dfe` CI's `tests / fast
  (3.14)` concluded success (run 40858829119).
- `run_always` lines at `836198dbb`, `PYTHONPATH=tests/hastub`:
  `tests/env_drift.py --claims-only 66974d47312c...` prints `claims hygiene:
  ... ok`; `tests/closure.py selftest` prints `ALL 117 closure shrink pins
  PASSED`; `tests/layout.py` prints `layout self-test: ok`;
  `tests/harness_headers.py` (venv-ci) prints `ALL 112 HARNESS HEADER CHECKS
  PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at `836198dbb`:
  `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py` at `836198dbb`:
  `CI PREDICT: no closures, fast, wave-script or instrument red predicted
  against 66974d47312c`.
- Untouched in this pass: `git diff c9bf05dfe 836198dbb --name-only` names
  `tests/features.py` only. So `VERSION`, the manifest, `RELEASE_NOTES.md`
  and both claim files are as they were at `c9bf05dfe`.

## Unpinned sites

None added in this pass: the commit adds no production line. The sites the
PR adds carry their dispositions in `tests/mutation_ledger/` (pinned under
`killed_by/`, or the one equivalent triage named above). CI's `tests /
mutation` at `c9bf05dfe` printed `MUTATION TABLE PASSED`.

## Red checks

Every check `pr-contract` lists red across this branch's commits. The run
and job ids are CI's records, read in this pass.

- `tests / fast (3.14)`: `tests/finite_boundary.py`'s Arm 6 seed called
  `MeasuredCop.record` with three arguments after `3ea1d8d48` added `at`.
  Fixed in `e33c174b4`; green at `c9bf05dfe`. The cheaper detector exists:
  the scoped gate, whose `scope.run` names `tests/finite_boundary.py`, and
  `fixer.md` step 5 already requires running it. No new detector is owed.
- `tests / coverage-ratchet`: the same cause. The crashed arm is what
  executes the store.py statements the floor counted. Green at `c9bf05dfe`.
  The cheaper detector is the same `finite_boundary.py` run; no separate one
  is owed.
- `tests / mutation-autofix`: `skip-measure-failed`, because the mutation
  lane's baseline was red on the same crash. Answered by a local
  `--pin-killed` run (`ci-autofix.md`); skipped at `c9bf05dfe`. The cause
  and the detector are the same as above.
- `tests / mutation`: four diff-added sites survived every driver at
  `67ffb958b` (the block above). Answered by checks and a triage. Green at
  `c9bf05dfe` (`MUTATION TABLE PASSED`). The cheaper detector is
  `tools/pr/ci_predict.py` / `prepr.sh` step 6d, which lists unpinned sites
  before the push. It cannot tell a survivor from a killable site, because
  only a drive can, and a local `mutation_table.py --pin-killed` run is
  `ci-autofix.md`'s, already required when `mutation-autofix` cannot run. No
  new detector is owed.
- `governance / instrument-self-tests`: red once at `67ffb958b` (run
  40777080201, job 123129545395). `pr_args.sh --self-test`'s `mut:unlock`
  arm failed once and passed twice more in the same job on the same tree.
  Not this PR's: the diff touches nothing under `tools/` or `.github/`. The
  arm reads the lock holder's liveness after the run returns, and the
  holder's own 0.2 s parent poll can exit it first. This is a timing race in
  that instrument, recorded for its owner. Green at `c9bf05dfe`.
- `governance / delivery-status`: red once at `8220bbf72` (run 40791893520),
  on main's overdue rows #2921, #2910, #2873 and #2909. None of them is this
  PR. Draining overdue rows is the orchestrator's
  (`delivery-status-tracking.md`). Green at `c9bf05dfe`.
- `tests / nightly-status`: red at `c9bf05dfe` (run 40858829119, job
  123396748525). It reports main's nightly lane `nightly-ha (stable)` failing
  in run 40806276912. Not this PR's: that lane runs on `main`, against real
  Home Assistant, and this diff does not touch the workflow. The check is not
  a required context. Its owner is whoever drives main's nightly lane (the
  orchestrator). This seat may not dispatch `nightly.yml --ref main`: the
  brief allows it to write only its return refs.
- `pr-contract / pr-contract`: an earlier body left reds unnamed. This body
  names each. The cheaper detector is `tools/pr/prepr.sh` on the body before
  the handoff.

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
