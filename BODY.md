Part 1 of R10-COP-GATE (#2262). Part of #2262; it does not close here (the
roster gives this group `fixes: []`), and the group's remaining carries are a
second pull request in this group, on topic `r10-cop-gate-p2` (see the
forward-carry section).

Without a heat reading the COP learner reads a ratio of metered draw to the
plan's ask as efficiency, which is a COP only while the draw follows the ask.
On the owner's install (STUDY R10-IDENT Q2) it does not: the running-draw
window's own rule, `draw_range.follows_ask`, reads False on the owner's 65
running pairs (log-log slope 0.40 against `FOLLOW_SLOPE_MIN` 0.5). The tree
had no state that said so, and it still folded the intervals that happened to
land within `COP_ASK_TOLERANCE` of their ask.

This adds the honest state and the draw-follows check (L3), no threshold
change (`COP_BASELINE_MIN_SAMPLES`, the tolerance, the duty floor and the
tracking gate are untouched):

- `accuracy.cop_observability`: `heat_metered` (a heat counter or the thermal
  power entity, `probe_install(...).measured_heat`, over an electrical
  figure), `draw_follows_plan`, `not_measurable`, `awaiting_draw_evidence`
  (follows_ask None), `no_electric_meter` (nothing to divide by). Which
  electrical figure divides is the install probe's,
  `InstallCapability.cop_electric()`: a heat counter's span divides by the
  electric counter `heat_pump_energy_entity`, every other reading by the power
  entity, so a counter install without an electric counter is
  `no_electric_meter`, never a gate pass. A heat reading wins over any draw
  evidence, so a thermal-power install is never `not_measurable`.
- `MeasuredCop.judge_ratio`: once `follows_ask` is False every interval is
  `draw_off_ask`, inside the tolerance or not. A draw that follows its ask,
  and one with no evidence yet, behave as before.
- The observed-COP sensor waits for `heat_meter` while `not_measurable`, and
  publishes `measured_at`, `last_refusal` (the latest interval's code
  verbatim: `span_open` beside a measured COP on a counter install,
  `unaligned_meters` and the `SPAN_REFUSED_*` codes as themselves) and
  `observability`.
- D15 seam (2): the latch carries the instant it folded (`MeasuredCop.at`,
  persisted; a record stored before it loads with the age unknown, never
  now). Payload `measured_cop_at`, diagnostics `cop_learner.measured_at`.
- D15 seam (3): the accuracy residual is `MeasuredCop.residual`, taken only
  from a COP folded after the settling interval opened.
- Carry 4 (draw pairing): the pending prediction records the interval's own
  `split` and `flow_command`, and `draw_range.fold` reads those inside the
  accuracy pairing's window (`accuracy.pairs_interval`, now the one owner of
  `0.05 <= h <= 2.0` for both readers), not the action the solve adopted next.

Alternatives for the electrical-figure rule (fixer.md step 17): the first cut
read it in `_learning_view` off the entry mapping (two `ctx._config.get`
reads, one keyed on a bare `CONF_HEAT_ENERGY_ENTITY`), which the entry-config
census in `tests/entities.py` refuses in a migrated module and which put an
install-capability rule in the coordinator; `heat_energy.meter_of(self).counter`
before it is set only by the first observed cycle. The probe already owns
`measured_heat` from the same keys, so it owns this too.

The finder's harness gained a one-line port: `owner_rows.py` crashed on the
stored baseline's `"1:dhw"` key before its draw-follows arm; space bins are
now read as integers and the hot-water key skipped.

## Head
`309f44882234ea0138a6e39a16fee81da858701c`, merge base with origin/main
`beb570c817c4efcae0d5f6f4bba52f3383baf8db` (origin/main's tip at 2026-10-28
19:08Z, `git fetch` at that time). Cut from `aaf8af512`. Commits: `3ea1d8d48` the
fix; `614fdc7d4` harness classification, five stale `MeasuredCop` pins
dropped; `52ef373cb` footprint paid; `575ba5f61` structure gains recorded;
`2c3de4661` the counter install's electric key; `0b8e0e970` the per-cycle
fold tests settle two cycles; `572ed657a` merges origin/main `edd7e0e14`;
`d3ce1d33f` the electrical-figure rule moved into the install probe;
`718768025` merges origin/main `beb570c81`; `a90db5e2b` merges the PR head
`d4ec6fcce` (the merge bot's main merge; tree identical to `718768025`,
`git diff 718768025 a90db5e2b` empty), so the PR branch fast-forwards;
`309f44882` passes the fold instant in `tests/finite_boundary.py`'s seed.

What the `beb570c81` merge touched: no conflicting hunk, and no hunk inside
this diff's own lines. Main's side moved `coordinator.py`, `debugger.py`,
`diagnostics.py`, `inputs.py`, `payload.py`, `store.py` and `tests/features.py`
(`git diff d3ce1d33f 718768025 --stat -- custom_components tests/features.py`:
6 production files, 194 insertions, 34 deletions); the ledger driver merged
`tests/structure_budgets.json` (`class_excess_loc` 18029, `max_class_loc` 8152)
and `tests/closures.json` key by key. The PR was `DIRTY` on GitHub because
GitHub runs no merge driver on those two ledgers; locally the drivers resolved
them. Claim files: neither conflicted; `card_claimed_drift.txt`, `VERSION` and
`RELEASE_NOTES.md` byte-identical to the merge base (`git diff --quiet
$(git merge-base origin/main HEAD)...HEAD -- tests/golden/card_claimed_drift.txt
VERSION RELEASE_NOTES.md` rc 0); `claimed_drift.txt` unchanged from `d3ce1d33f`'s
claim at `claims-for: 7.0.5`, `VERSION` 7.0.5.

## Mutation proof

Driver `~/hpo-seats/r10s6/fix-cop-gate-s10/tools/mutant.sh` (scratch): an
rsync copy without `.git`, one exact replacement (site count 1), then
`~/hpo-seats/r10s6/fix-cop-gate-s10/tools/cg_block.py tests/features.py`
(the header plus the block from "COP learner duty floor keys on the
modulation floor" to "R9-UX-6: money and memory", 34 checks, every
R10-COP-GATE check among them) or `PYTHONPATH=tests/hastub python3
tests/entities.py`. Unmutated copy: `ALL 34 CG BLOCK PASSED`.

Failing test first: the head's tests over `git archive edd7e0e14
custom_components`: `FAIL a draw the window shows ignores its ask folds
nothing, even within the ask tolerance ... [self-set 12/12 (None); follows
12/12]`, then `AttributeError: ... no attribute 'cop_observability'` (rc=1).

m1, m2, m3, m6 ran on `572ed657a` (`d3ce1d33f` touches none of their sites);
m5b and m4 on the head's production code.

- m1 `judge_ratio` `if follows is False:` -> `if False:`: 2 of 34, `FAIL a
  draw that ignores the ask (varying or flat) is refused as off-ask ...` and
  `FAIL a draw the window shows ignores its ask folds nothing ...`.
- m2 `pending["split"], ctx._thermal_params` -> `self._commanded_split(),
  ctx._thermal_params`: 1 of 34, `FAIL the draw window pairs the closed
  interval's reading with that interval's own ask (1.5 kW) ... [moved [(1.5,
  3.0)] ...]`.
- m3 `MeasuredCop.residual` drop ` or utc_elapsed_seconds(self.at, since) <=
  0.0`: 2 of 34, `FAIL the accuracy residual reads the latch only for the
  interval it folded in ...` and the pairing check's residual arm.
- m5b `cop_electric` -> `return self.measured_power`: 1 of 34, `FAIL the
  coordinator's state: ... a heat counter without an electric counter has
  nothing to divide by`.
- m6 `self.at = at` -> `pass`: `FAIL a folded COP carries the instant it
  folded ... [at None -> None]`, then `TypeError` (rc=1).
- m4 `if data.get("cop_observability") == COP_NOT_MEASURABLE:` -> `if
  False:`: `tests/entities.py` `FAIL a COP not measurable here waits for a
  heat meter; ...`. Its other FAIL lines are the no-`.git` runner's and the
  self-test fixtures' known-bad arms (`a3:`..`a13:`, `hb:`); it also printed
  the entry-config census `STRAY [('coordinator.py', '_learning_view',
  'CONF_HEAT_ENERGY_ENTITY')]`, a real red at `0b8e0e970` that `d3ce1d33f`
  removes (its result at this head is CI's).

After the `beb570c81` merge (`309f44882`): the m1-m6 sites are untouched by
main's side of the merge (no hunk of `git diff d3ce1d33f 718768025` falls in
`judge_ratio`, `MeasuredCop`, `cop_electric`, `_waiting_for` or the
`_record_accuracy` draw guard), and the mutants were not re-run at this head;
the scratch driver above is not on this seat. What re-executes them at the
merged head is `tests/mutation_table.py --pin-killed --base origin/main`
(below, under `## Red checks`, `mutation`).

`309f44882` (the seed fix): before, at `a90db5e2b` (`git archive HEAD~1`),
`PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` raised `TypeError:
MeasuredCop.record() missing 1 required positional argument: 'at'` from
`_a6_enrich` (rc 1); after, `ALL 108 FINITE BOUNDARY CHECKS PASSED` (rc 0).
## Null control

- A draw that follows its ask still folds: follows 12/12 at head, and under
  m1 the follows arm stays 12/12 while the self-set arm moves.
- Companion `synthetic.follows.folded=12/12` at both ends.
- `dev/audit/harnesses/cop_duty_floor.py`: 31 RESULT rows, all but the four
  in `## Figures` identical at both ends (`diff`).
- An unchanged ask pairs alike (`_cg_same == [(1.5, 1.5)]`).
- Companion `--slope-follow` (draws 1.3 x the ask): `owner.folds=77
  folds_within_tolerance=0` at both ends.

- `tests/finite_boundary.py`'s store.py arm: with the seed fix, `coverage run
  --include='*/heatpump_optimizer/store.py' tests/finite_boundary.py` misses 1
  of 253 statements; at `a90db5e2b` (no fix) it misses 20 (the domain arm
  aborts). That is the mechanism of `coverage-ratchet`'s store.py figure, and
  the unfixed run is its null control.
## Figures
Re-taken at this head (`309f44882`, merge base `beb570c81`; the harness runs
used the tree of `a90db5e2b`, which differs from the head only in
`tests/finite_boundary.py`, a file no harness below reads), seat Python 3.14.7
(`/opt/hpo/venv-ci`), 2026-10-28 19:10Z-19:51Z UTC. Base = `git archive
beb570c81 | tar -x` with the head's two harness files copied in.

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py`
  (synthetic arm; the private owner bundle is not on this seat, so the owner
  arm was not re-run): base `synthetic.selfset.folded=12/12 refusal=None
  observability=absent`, `synthetic.follows.folded=12/12 refusal=None
  observability=absent`; head `synthetic.selfset.folded=0/12
  refusal=draw_off_ask observability=not_measurable`,
  `synthetic.follows.folded=12/12 refusal=None
  observability=draw_follows_plan`. Harness sha1
  d03dd93508936796fba5ec07ce387d393c9d8b60, unchanged.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`,
  base -> head, `diff` of the RESULT lines (31 each): only
  `selfmod_independent` 9/96 0.976 -> 5/96 0.987, `selfmod_independent_4kw`
  33/96 0.780 -> 29/96 0.789, `selfset_hourly` 7/96 0.978 -> 5/96 0.985,
  `p4_follow_lag1tick` 37/96 1.002 -> 24/96 0.983 differ; the same four rows
  and values as at `d3ce1d33f`. Harness sha1
  9587bead80b5f4b103c510a9f46a4c70e3ea2a91, unchanged.
- `python3 tools/audit/archscore/score.py --diff beb570c81` at `309f44882`:
  `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at `309f44882`:
  `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py` at `309f44882`:
  `no closures, fast, wave-script or instrument red predicted against
  beb570c817c4`; it lists the unpinned sites under `## Unpinned sites`.
- `python3 tests/closure.py select --diff beb570c81 --workdir D` at
  `309f44882`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- Scoped gate at `a90db5e2b` (`GATE_SCOPE=auto GATE_SCOPE_BASE=beb570c81
  GOLDEN_MODE=drift GOLDEN_REF=beb570c81 PYTHONPATH=tests/hastub bash
  tests/run.sh`, started 19:12Z): `MODE: SCOPED -- 27 script(s) run, 6
  scoped out`; `1 TEST SCRIPT(S) FAILED`, `tests/finite_boundary.py` (the
  `TypeError` above), every other selected script green (`tests/features.py`
  `ALL 4540 FEATURE CHECKS PASSED`, `tests/entities.py` `ALL 2468 ENTITY
  CHECKS PASSED`, `tests/stress.py` `ALL 113 STRESS CHECKS PASSED`). At
  `309f44882`, `tests/finite_boundary.py` alone: `ALL 108 FINITE BOUNDARY
  CHECKS PASSED`; the gate was not re-run in full at `309f44882`, whose delta
  is that one test line.

Taken at `d3ce1d33f` (merge base `edd7e0e14`) by the previous seat and not
re-taken here (the owner bundle is the previous seat's):


Owner bundle `~/Downloads/config_entry-heatpump_optimizer-01M0GGS19KP0FH4E7K9S003DTV-11.json`
(private, derived ratios only). Base = `git archive edd7e0e14 | tar -x` with
this branch's `tests/` and the two harness files copied in. Harness sha1s:
`dev/audit/harnesses/r10_cop_gate.py` d03dd93508936796fba5ec07ce387d393c9d8b60,
`dev/audit/rounds/round10/study-ident/owner_rows.py`
ce04b0dd15eabed34457a515afa8955de193fc04,
`dev/audit/harnesses/cop_duty_floor.py` 9587bead80b5f4b103c510a9f46a4c70e3ea2a91.

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py <bundle>`
  (head at `d3ce1d33f`): base `synthetic.selfset.folded=12/12 refusal=None
  observability=absent`, `owner.running_pairs=65 follows_ask=False`,
  `owner.folds=2 folds_within_tolerance=2`; head
  `synthetic.selfset.folded=0/12 refusal=draw_off_ask
  observability=not_measurable`, `owner.folds=0 folds_within_tolerance=0`,
  `owner.heat_metered=False observability=not_measurable`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-ident/owner_rows.py <bundle>`
  (merged tree): `diff` of RESULT lines at both ends prints only `load1`;
  `cop.refusal.FOLDS=5`, `FOLDS_within_ask_tolerance=2`,
  `follow.running_pairs=65 follows_ask=False loglog_slope=0.40`,
  `cop.with_evidence.follows_ask=True folds=25`.
- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`
  (merged tree), base -> head: `selfmod_independent` 9/96 0.976 -> 5/96
  0.987, `selfmod_independent_4kw` 33/96 0.780 -> 29/96 0.789,
  `selfset_hourly` 7/96 0.978 -> 5/96 0.985, `p4_follow_lag1tick` 37/96
  1.002 -> 24/96 0.983 (open loop; its absolute scale is not the truth).
- `dev/audit/harnesses/r10_thermal_power_option.py`: not re-run; at
  `aaf8af512` it raised `AttributeError: 'Gate' object has no attribute
  '_fold_cop_evidence'` at both ends. The thermal-power arm is the features
  check "the coordinator's state: ... a thermal-power install never is".
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at `d3ce1d33f`:
  `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py` at `d3ce1d33f`:
  no red predicted against edd7e0e14e08; 20 unpinned sites.
- `python3 tests/closure.py select --diff edd7e0e14 --workdir D` at
  `d3ce1d33f`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- Scoped gate at `d3ce1d33f` (`GATE_SCOPE=auto GATE_SCOPE_BASE=edd7e0e14
  GOLDEN_MODE=drift GOLDEN_REF=edd7e0e14 PYTHONPATH=tests/hastub bash
  tests/run.sh`, started 09:09Z, seat load average 200-350): env_drift
  `--claims-only` and `closure.py selftest` (`ALL 117 closure shrink pins
  PASSED`) green, `tests/features.py` `ALL 4540 FEATURE CHECKS PASSED`; the
  remaining scripts had not reported at 10:35Z and are CI's; no local result
  is claimed for them.
- Golden drift: six ADD-ONLY leaves per `coord_*` fixture, claimed in
  `tests/golden/claimed_drift.txt` at `claims-for: 7.0.5`;
  `card_claimed_drift.txt` byte-identical to the merge base.

## Unpinned sites

Every site `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py` lists at `309f44882` (merge base `beb570c81`; 20, the same sites as at `d3ce1d33f`, two `coordinator.py` lines moved +14 by main's side of the merge: 9837 -> 9851, 9872 -> 9886), each under `custom_components/`, so `mutation-autofix` pins it; the mutants under `## Mutation proof` kill the ones they drove:

- `custom_components/heatpump_optimizer/accuracy.py:787 CMP_BOUND*2`: `pairs_interval`; mutation-autofix.
- `custom_components/heatpump_optimizer/accuracy.py:787 RETURN_DEL`: `pairs_interval`; mutation-autofix.
- `custom_components/heatpump_optimizer/accuracy.py:838 GUARD_OFF`: `cop_observability`; mutation-autofix; value check "cop_observability: heat metered beats ...".
- `custom_components/heatpump_optimizer/accuracy.py:840 GUARD_OFF`: `cop_observability`; mutation-autofix; value check "cop_observability: heat metered beats ...".
- `custom_components/heatpump_optimizer/accuracy.py:842 GUARD_OFF`: `cop_observability`; mutation-autofix; value check "cop_observability: heat metered beats ...".
- `custom_components/heatpump_optimizer/accuracy.py:844 RETURN_DEL`: `cop_observability`; mutation-autofix; value check "cop_observability: heat metered beats ...".
- `custom_components/heatpump_optimizer/accuracy.py:905 GUARD_OFF`: `judge_ratio` (`if follows is False`); mutation-autofix; killed by m1.
- `custom_components/heatpump_optimizer/accuracy.py:916 RETURN_DEL`: `judge_ratio`; mutation-autofix.
- `custom_components/heatpump_optimizer/accuracy.py:932 CMP_BOUND`: `MeasuredCop.residual`; mutation-autofix; the time guard killed by m3.
- `custom_components/heatpump_optimizer/accuracy.py:932 GUARD_OFF`: `MeasuredCop.residual`; mutation-autofix; the time guard killed by m3.
- `custom_components/heatpump_optimizer/accuracy.py:934 BOOLOP`: `MeasuredCop.residual`; mutation-autofix.
- `custom_components/heatpump_optimizer/accuracy.py:934 GUARD_OFF`: `MeasuredCop.residual`; mutation-autofix.
- `custom_components/heatpump_optimizer/accuracy.py:938 RETURN_DEL`: `MeasuredCop.residual`; mutation-autofix; value check "the accuracy residual reads the latch only ...".
- `custom_components/heatpump_optimizer/accuracy.py:943 RETURN_DEL`: `MeasuredCop.as_dict`; mutation-autofix; value check "a folded COP carries the instant it folded".
- `custom_components/heatpump_optimizer/accuracy.py:961 GUARD_OFF`: `MeasuredCop.from_dict`; mutation-autofix; value check "a folded COP carries the instant it folded".
- `custom_components/heatpump_optimizer/accuracy.py:963 RETURN_DEL`: `MeasuredCop.from_dict`; mutation-autofix; value check "a folded COP carries the instant it folded".
- `custom_components/heatpump_optimizer/coordinator.py:9851 GUARD_OFF`: `_record_accuracy`, the draw fold guard; mutation-autofix; killed by m2's check.
- `custom_components/heatpump_optimizer/coordinator.py:9886 GUARD_OFF`: `_record_accuracy`, `pairs_interval(elapsed)`; mutation-autofix.
- `custom_components/heatpump_optimizer/sensor.py:1689 GUARD_OFF`: `ObservedCOPSensor._waiting_for`; mutation-autofix; killed by m4.
- `custom_components/heatpump_optimizer/thermal_model.py:1295 RETURN_DEL`: `InstallCapability.cop_electric`; mutation-autofix; killed by m5b.

## Red checks

Each concluded red at the previous PR head `d4ec6fcce`, by its exact name:

- `tests / fast (3.14)`: this PR's. `tests/finite_boundary.py`'s domain-arm
  seed `_a6_enrich` called `MeasuredCop.record(3.17, True, 52.5)`, which
  `3ea1d8d48` gave a required `at`; `TypeError`. Fixed in `309f44882` (the
  seed passes `t0`). Cheaper detector: the scoped gate, which selects
  `tests/finite_boundary.py` for this diff and failed it in 105 s; the
  previous seat's gate at `d3ce1d33f` had not reported that script when it
  handed off (its body: "had not reported at 10:35Z and are CI's").
- `tests / coverage-ratchet`: this PR's, a consequence of the red above.
  `store.py: 93.28 %` under the 95 % per-module floor: the aborted
  `finite_boundary.py` domain arm leaves 19 store.py statements unexecuted
  (`## Null control`: 20 missed without the fix, 1 with it). No coverage
  re-run of the full tree here; CI's at the new head is the proof.
- `tests / mutation-autofix`: `skip-measure-failed` ("THE REPAIR DID NOT
  HAPPEN"), the bot's measurement on a red baseline. The same red baseline
  reproduces locally: `tests/mutation_table.py --pin-killed --base
  origin/main` at `a90db5e2b` printed `MUTATION TABLE INCONCLUSIVE -- the
  baseline is already red in tests/finite_boundary.py`. `309f44882` greens
  that baseline; a re-run of `--pin-killed` at `309f44882` was started at
  19:51Z and had not finished at handoff (each mutant re-runs `features.py`,
  about 700 s), so no pins are committed here and none is claimed;
  `mutation-autofix` at the new head is expected to pin the killed sites
  (`ci-autofix.md`: once the PR exists, wait for the bot commit).
- `tests / mutation`: red by construction on the 20 sites under
  `## Unpinned sites` until those pins land; it is not a separate defect.
- `pr-contract / pr-contract` and `gate`: `gate` aggregates the others
  (its log: `FAIL tests / fast (3.14)`, `tests / mutation`, `pr-contract /
  pr-contract`); it has no cause of its own. `pr-contract` ran on the `DIRTY`
  head `d4ec6fcce` with a body whose `## Head` named `d3ce1d33f` and whose
  `## Red checks` named none of these reds; this body names the new head and
  every red. Its failing step is not in the log tail this seat read, so the
  cause is inferred, not shown; CI's run at the new head is the proof.

## Forward-carry

Destination: the roster entry `R10-COP-GATE` in `dev/programme/rosters/wave-r10-groups.json`, which already carries each text (numbering is its `carry` array, 1-based); part 2 of this group, topic `r10-cop-gate-p2` (orchestrator ruling: same group, no deferral out of round 10), delivers them. Carry: R10-COP-GATE

- Carries 6, 7 and 14: the heat-pump grade's hover reason codes, plain-words metric text, and the `envelope_drivers` interface mirror. Carry: R10-COP-GATE
- Carries 9 and 10: vent latch freezing COP/DHW/buffer/sysid and the sticky freeze reason; VERIFY-first plus a design note by their own text, before code. Carry: R10-COP-GATE
- Carry 12: the learned top's consumer through `draw_range.planned_range`. Carry: R10-COP-GATE
- Carries 13 and 16: `_fold_flow_lift` reading the interval's attribution. Carry: R10-COP-GATE
- Carry 8, in part: the refusal codes render verbatim here, but its control (a counter install with no electric counter shows `unaligned_meters`) is not measured; this head publishes `observability=no_electric_meter` for that install. Carry: R10-COP-GATE

Delivered here: carries 1, 3 (seams 2 and 3), 4, 5, 11 and 15; carry 2 is R10-UX-HEALTH's. Carry: R10-COP-GATE

## Friction

- brief-scope: cost: the group's carry list holds 16 entries spanning COP eligibility, the heat-pump grade UI, a vent-detector design study and the flow-bias gate, against an M size and one owning seam; one seat could not deliver it in the 2 h bound, so the group lands in two parts. Carry: R10-COP-GATE
