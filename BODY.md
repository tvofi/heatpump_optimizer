Part 1 of R10-COP-GATE (#2262). Part of #2262; it does not close here (the
roster gives this group `fixes: []`), and the group's remaining carries are a
second pull request in this group, on topic `r10-cop-gate-p2` (see the
forward-carry section).

Without a heat reading the COP learner reads a ratio of metered draw to the
plan's ask as efficiency, which is a COP only while the draw follows the ask.
On the owner's install (STUDY R10-IDENT Q2) it does not: the running-draw
window's own rule, `draw_range.follows_ask`, reads False on the owner's
running pairs (log-log slope under `FOLLOW_SLOPE_MIN`). The tree had no state
that said so, and it still folded the intervals that happened to land within
`COP_ASK_TOLERANCE` of their ask.

This adds the honest state and the draw-follows check (L3), no threshold
change (`COP_BASELINE_MIN_SAMPLES`, the tolerance, the duty floor and the
tracking gate are untouched):

- `accuracy.cop_observability`: `heat_metered` (a heat counter or the thermal
  power entity, `probe_install(...).measured_heat`, over an electrical
  figure), `draw_follows_plan`, `not_measurable`, `awaiting_draw_evidence`
  (follows_ask None), `no_electric_meter` (nothing to divide by). Which
  electrical figure divides is the install probe's,
  `InstallCapability.cop_electric()`: a heat counter's span divides by the
  electric counter `heat_pump_energy_entity`, any other reading by the power
  entity, so a counter install without an electric counter is
  `no_electric_meter`, not a gate pass. A heat reading wins over draw
  evidence, so a thermal-power install is not `not_measurable`.
- `MeasuredCop.judge_ratio`: once `follows_ask` is False an interval is
  `draw_off_ask`, inside the tolerance or not. A draw that follows its ask,
  and one with no evidence yet, behave as before.
- The observed-COP sensor waits for `heat_meter` while `not_measurable`, and
  publishes `measured_at`, `last_refusal` (the latest interval's code
  verbatim) and `observability`.
- D15 seam (2): the latch carries the instant it folded (`MeasuredCop.at`,
  persisted; a record stored before it loads with the age unknown, not
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
is set only by the first observed cycle. The probe already owns
`measured_heat` from the same keys, so it owns this too.

The finder's harness gained a one-line port: `owner_rows.py` crashed on the
stored baseline's `"1:dhw"` key before its draw-follows arm; space bins are
now read as integers and the hot-water key skipped.

**This repair pass** (`e33c174b4`): `MeasuredCop.record` gained its `at`
argument in `3ea1d8d48`, and `tests/finite_boundary.py`'s Arm 6 rich seed
(`_a6_enrich`) still called it with three. The script died there with a
`TypeError`, so `tests / fast` went red, the store.py statements only that arm
reaches went unrun (`tests / coverage-ratchet`), and the mutation lane's
baseline was red, so `mutation-autofix` could not measure. The seed now
records its COP at `t0 - 2 h`, which also puts the new `measured_cop/at` leaf
in the seed Arm 6 round-trips. With the baseline green, `--pin-killed`
ran here (`ci-autofix.md`, since `mutation-autofix` had gone red): five of
its six survivors gained a killing value check in `tests/features.py` and
the sixth, an equivalent trailing `return None`, a triage. No production
line changes in this pass.

## Head

`d081ec7adc8880e2cca8c603c6229e6091c22c2a`. Its tree is `25157e45d`'s, where every figure below was measured unless a line names another commit: `d081ec7ad` is a `git merge -s ours` of the earlier repair seat's superseded `handoff/r10-cop-gate` return `309f44882` (the same one-line `finite_boundary.py` seed fix, recording at `t0`, on origin/main `beb570c81`, with the mutation lane unrepaired). It keeps that history so the handoff ref moved by fast-forward and not a force-push, and `git rev-parse d081ec7ad^{tree}` equals `25157e45d^{tree}`.

Merge base with origin/main `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`.
`1d4fbbc5c` is the merge-main bot's merge onto `d4ec6fcce`, the orchestrator's
merge of origin/main into the authored code head `d3ce1d33f`. No merge in this
pass: `git merge-tree --write-tree origin/main HEAD` reported no conflict
against origin/main `593f57c44` (2026-10-28 22:16Z). Commits before this
pass: `3ea1d8d48` the fix; `614fdc7d4` harness classification, five stale
`MeasuredCop` pins dropped; `52ef373cb` footprint paid; `575ba5f61` structure
gains recorded; `2c3de4661` the counter install's electric key; `0b8e0e970`
the per-cycle fold tests settle two cycles; `572ed657a` a merge of origin/main;
`d3ce1d33f` the electrical-figure rule moved into the install probe. This
pass: `e33c174b4` (the Arm 6 seed); `f832ffef7` the 15 pins `--pin-killed` measured, three value checks for the five killable survivors and one equivalent triage; `25157e45d` the five pins those checks earned. None of the three touches `custom_components/`.

## Mutation proof

This pass (`e33c174b4`): the failing test came first. At `1d4fbbc5c`,
`PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` exits 1 with
`TypeError: MeasuredCop.record() missing 1 required positional argument: 'at'`
in `_a6_enrich`; at `e33c174b4` it prints `ALL 108 FINITE BOUNDARY CHECKS
PASSED`. Each mutant below was one `sed` replacement in the worktree's
`custom_components/heatpump_optimizer/accuracy.py`, run, then
`git checkout` of that file:

- M1 `MeasuredCop.from_dict`: `return cls(cop=cop, curve_dhw=dhw,
  dhw_temp=temp, at=at)` -> without `at=at`: `tests/finite_boundary.py`
  rc=1, `FAIL the healthy rich seed round-trips unchanged through every
  loader and saver (null control)  [changed=['thermal_learning']]`, `1 of
  108 FINITE BOUNDARY CHECKS FAILED`. Before this pass that arm never ran,
  so no in-tree check read the stored instant's reload through the real
  savers.
- M2 `MeasuredCop.record`: `self.at = at` -> `pass`: survives
  `tests/finite_boundary.py` (rc=0; the seed's instant is not read back by
  a value check there), killed by `tests/features.py` (rc=1, `TypeError:
  unsupported operand type(s) for +: 'NoneType' and 'datetime.timedelta'`
  at the residual check's `_cg_at + timedelta(minutes=1)`), the m6 result
  below.

The authored fix's mutants (previous seat, at `572ed657a` and `d3ce1d33f`,
driver an out-of-tree rsync script; not re-run in this pass, which changes no
production line):

- m1 `judge_ratio` `if follows is False:` -> `if False:`: `FAIL a draw that
  ignores the ask (varying or flat) is refused as off-ask ...` and `FAIL a
  draw the window shows ignores its ask folds nothing ...`.
- m2 `pending["split"], ctx._thermal_params` -> `self._commanded_split(),
  ctx._thermal_params`: `FAIL the draw window pairs the closed interval's
  reading with that interval's own ask (1.5 kW) ...`.
- m3 `MeasuredCop.residual` drop ` or utc_elapsed_seconds(self.at, since) <=
  0.0`: `FAIL the accuracy residual reads the latch only for the interval it
  folded in ...`.
- m5b `cop_electric` -> `return self.measured_power`: `FAIL the coordinator's
  state: ... a heat counter without an electric counter has nothing to divide
  by`.
- m6 `self.at = at` -> `pass`: `FAIL a folded COP carries the instant it
  folded ... [at None -> None]`, then `TypeError`.
- m4 `if data.get("cop_observability") == COP_NOT_MEASURABLE:` -> `if
  False:`: `tests/entities.py` `FAIL a COP not measurable here waits for a
  heat meter; ...`.

## Null control

- Unmutated `e33c174b4`: `tests/finite_boundary.py` `ALL 108 FINITE BOUNDARY
  CHECKS PASSED`, the control for M1 and M2.
- The companion harness's `follows` arm (a draw at 1.3 x the ask) folds
  12/12 at both ends (`## Figures`).
- `tests/mutation_table.py --pin-killed`'s own null control, a comment-only edit at `accuracy.py:50` (`NULL_COMMENT`), survived every driver it ran in the first drive; a killed null would have refused the drive.

## Figures

Seat interpreter: Python 3.13 venv from `tests/requirements-ci.txt` (and
`tests/requirements-coverage.txt` for the coverage figure);
`tools/audit/seat/seat_venv.sh` asks uv for CPython 3.14.7, which this
container cannot download. CI's `fast` leg is 3.14.

- Scoped gate scope, at `1d4fbbc5c` and again at `e33c174b4`:
  `python3 tests/closure.py select --diff b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa --workdir D`
  prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out`, and `diff` of the
  two `scope.run` files is empty.
- Every `scope.run` script except `tests/stress.py` (CI's), each run as
  `PYTHONPATH=tests/hastub GOLDEN_REF=b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa python3 tests/<script>`
  (`node` for the two `.mjs`), at `1d4fbbc5c`: `tests/finite_boundary.py`
  rc=1 (the `TypeError` above), every other script rc=0. CI's `fast (3.14)`
  at that head reported `1 TEST SCRIPT(S) FAILED`.
- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` at
  `e33c174b4`: rc=0, `ALL 108 FINITE BOUNDARY CHECKS PASSED`. This pass
  changes that file alone, and no other script in `scope.run` reads it.
- store.py statements `tests/finite_boundary.py` alone executes,
  `python3 -m coverage run --include='*/store.py' tests/finite_boundary.py`
  then `python3 -m coverage report`: 253 statements, 20 missed at
  `1d4fbbc5c` (the script crashed), 1 missed at `e33c174b4`. CI's
  `coverage-ratchet` at `1d4fbbc5c` read store.py at 93.28 %, which is
  236/253 (17 missed) over the whole suite; the per-module floor is 95.0 %.
  The suite-wide figure at the new head is CI's.
- Companion harness `dev/audit/harnesses/r10_cop_gate.py` (sha1
  d03dd93508936796fba5ec07ce387d393c9d8b60), synthetic arm (no bundle),
  `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py`
  in a `git archive` copy of each end (base: `b6f6ceca4`'s tree with this
  head's `tests/` and the harness copied in): base
  `synthetic.selfset.folded=12/12 refusal=None observability=absent`,
  `synthetic.follows.folded=12/12 refusal=None observability=absent`; head
  `e33c174b4` `synthetic.selfset.folded=0/12 refusal=draw_off_ask
  observability=not_measurable`, `synthetic.follows.folded=12/12
  refusal=None observability=draw_follows_plan`.
- The owner-bundle arms of `r10_cop_gate.py` and
  `dev/audit/rounds/round10/study-ident/owner_rows.py`, and
  `dev/audit/harnesses/cop_duty_floor.py`'s base-to-head rows, are not
  re-taken in this pass: the bundle is private and not in this container,
  and no production line changed since `d3ce1d33f`, where the previous seat
  measured them. No figure from them is restated here.
- `python3 tools/audit/archscore/score.py --diff b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`
  at `e33c174b4`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at the head:
  `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main`:
  first drive at `e33c174b4`: 21 new unpinned sites against `b6f6ceca4`, `PIN KILLED: 15 pinned, 6 left unpinned` (rc=1). Second drive at `f832ffef7`, after the three new checks and the triage: 5 new unpinned sites, `PIN KILLED: 5 pinned, 0 left unpinned` (rc=0).
- `PYTHONPATH=tests/hastub python3 tests/features.py` at `f832ffef7`: `ALL 4542 FEATURE CHECKS PASSED` (4540 before the two new checks).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py` at `25157e45d`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted against b6f6ceca4f03`.
- Golden drift: six ADD-ONLY leaves per `coord_*` fixture, claimed in
  `tests/golden/claimed_drift.txt` at `claims-for: 7.0.5`;
  `card_claimed_drift.txt` byte-identical to the merge base.

## Unpinned sites

Every site the diff adds, as `tests/mutation_table.py --pin-killed --base origin/main` drove them (first drive at `e33c174b4`, second at `f832ffef7`); each is now in `tests/mutation_ledger/`:

- `accuracy.py:787 CMP_BOUND` (two sites, one anchor): `pairs_interval`'s inclusive ends; lived in the first drive; new check "a pending prediction pairs with the interval that closed from 3 minutes to 2 hours old, both ends included ..."; pinned, killed by `tests/features.py`.
- `accuracy.py:787 RETURN_DEL`: `pairs_interval`; pinned, killed by `tests/features.py`.
- `accuracy.py:838`, `:840`, `:842 GUARD_OFF` and `:844 RETURN_DEL`: `cop_observability`; pinned, killed by `tests/features.py`.
- `accuracy.py:905 GUARD_OFF`: `judge_ratio`'s `if follows is False`; pinned, killed by `tests/features.py`.
- `accuracy.py:916 RETURN_DEL`: `judge_ratio`'s trailing `return None`; lived; equivalent (the method falls off its end and returns None on every input), triaged in `tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json`.
- `accuracy.py:932 CMP_BOUND`: `MeasuredCop.residual`'s `<= 0.0`; lived in the first drive; the residual check now reads a fold at exactly the interval's opening as none; pinned, killed by `tests/features.py`.
- `accuracy.py:932 GUARD_OFF`: `MeasuredCop.residual`'s guard; pinned, killed by `tests/features.py`.
- `accuracy.py:934 BOOLOP` and `GUARD_OFF`: `MeasuredCop.residual`'s curve choice; lived in the first drive; new check "the residual subtracts the curve the COP folded on ..."; pinned, killed by `tests/features.py`.
- `accuracy.py:938 RETURN_DEL`: `MeasuredCop.residual`; pinned, killed by `tests/features.py`.
- `accuracy.py:943 RETURN_DEL`: `MeasuredCop.as_dict`; pinned, killed by `tests/features.py`.
- `accuracy.py:961 GUARD_OFF` and `:963 RETURN_DEL`: `MeasuredCop.from_dict`; pinned, killed by `tests/features.py`.
- `coordinator.py:9851 GUARD_OFF` and `:9886 GUARD_OFF`: `_record_accuracy`, the draw fold guard and `pairs_interval(elapsed)`; pinned, killed by `tests/features.py`.
- `sensor.py:1689 GUARD_OFF`: `ObservedCOPSensor._waiting_for`; pinned, killed by `tests/entities.py`.
- `thermal_model.py:1295 RETURN_DEL`: `InstallCapability.cop_electric`; pinned, killed by `tests/features.py`.

## Red checks

Every check `pr-contract` lists red across this branch's commits:

- `tests / fast (3.14)`: `tests/finite_boundary.py` died in `_a6_enrich` on
  the old three-argument `MeasuredCop.record` call. Fixed in `e33c174b4`.
  The cheaper detector exists and was not run to completion: the scoped
  gate, whose `scope.run` names `tests/finite_boundary.py` (about 70 s
  alone). The previous seat's local gate reported `tests/features.py` and
  left the remaining scripts to CI; a seat that runs every `scope.run`
  script before handoff catches this at that cost, which `fixer.md` step 5
  already requires. No new detector is owed.
- `tests / coverage-ratchet`: store.py 93.28 % against the 95.0 % per-module
  floor, the same cause: the crashed arm is what executes those store.py
  statements (20 missed by that script at `1d4fbbc5c`, 1 at `e33c174b4`).
  Its cheaper detector is the same `finite_boundary.py` run; no separate one
  is owed.
- `tests / mutation`: unpinned sites the diff adds. The lane's measure needs a green baseline, which the `finite_boundary.py` crash denied; the sites are now pinned or triaged (`## Unpinned sites`). The cheaper detector for the unpinned sites is `prepr.sh` step 6d (`ci_predict.py`), which listed them before the push; the previous body answered them as `mutation-autofix`'s, and that job could not run. No new detector is owed.
- `tests / mutation-autofix`: `skip-measure-failed` at `1d4fbbc5c`, because
  the mutation lane's baseline was red on the same `finite_boundary.py`
  crash, so no pin could be measured. Answered by `--pin-killed` run here
  (`ci-autofix.md`: when `mutation-autofix` goes red, run it yourself).
  Same root cause; no separate detector is owed.
- `governance / instrument-self-tests`: red once, at `67ffb958b` (the
  orchestrator's delivery-row commit, which adds only
  `dev/programme/delivery/2917.md`), run 40777080201, job 123129545395.
  Its failing step is "Show the PR opener (delivery_row.sh's and
  pr_args.sh's self-tests)": `pr_args self-test: 144 checks, 1 failed`, the
  one `FAIL   mutant mut:unlock (its line deleted): the holder is still alive
  when the run returns`. The same `tools/audit/seat/pr_args.sh --self-test`
  ran twice more in that job on the same tree, in "Show the PR argument
  builder" and "Show the PR updater", and printed `144 checks, 0 failed`
  both times, the `mut:unlock` arm `ok`. Cause: a timing race in that
  mutant arm, not in this diff. With `PR_AFTER_REAP` deleted the lock
  holder is never signalled, but it still exits by itself once its
  `os.getppid() == p` poll (every 0.2 s) sees `update_pr.sh` gone; the arm
  reads `kill -0` on the holder after the run returns, so when that poll
  wins the race the mutant reads as killed-early and the arm FAILs. This
  red grades main's instrument and its inputs this diff does not touch:
  `git diff $(git merge-base origin/main origin/fix/r10-cop-gate)...origin/fix/r10-cop-gate --name-only`
  names nothing under `tools/` or `.github/`, and `pr_args.sh` is
  unchanged between `67ffb958b` and origin/main `486e65cbd`. No cheaper
  detector on this branch's side exists: no seat-side run of this diff
  could have predicted it, since the same self-test passes on the same
  tree two runs in three. The defect is the arm's (a liveness read with a
  0.2 s self-exit window); it is recorded here as a finding for that
  instrument's owner, not fixed in this PR.
- `governance / delivery-status`: red once, at `8220bbf72` (the
  `mutation-autofix` bot's pin commit), run 40791893520, job 123179758416.
  It runs main's pinned `tests/delivery_status.py --check` (`PINNED:
  b0b2d7697`) over main's delivery records and printed `DELIVERY STATUS
  OVERDUE -- 18 rowed, 12 pending, 4 overdue (overdue at 12 commits)`; the
  four overdue rows are #2921, #2910, #2873 and #2909, none of them this
  PR. This red grades main and its inputs this diff does not touch: the
  branch's only delivery file is its own row `dev/programme/delivery/2917.md`,
  which the check did not list overdue. The job's own log says it "is NOT
  a required context and a red here blocks no merge". No cheaper detector
  is owed by this PR: draining overdue rows is the orchestrator's
  (`delivery-status-tracking.md`), not a seat's.
- `pr-contract / pr-contract`: the previous body's `## Red checks` said
  `none` and named none of the four above. This body names each. The cheaper
  detector is `tools/pr/prepr.sh` on the body before handoff, which reads
  the same red history; run here to exit 0.

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
