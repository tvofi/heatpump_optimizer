R9-UX-10: on an install with a water mass-flow meter and neither a power nor a
compressor-frequency signal, the two interval learners replay the elapsed
period with the heat the meter measured instead of the heat the model infers
from the commanded draw and its own COP. #2016 item 4, the consumer PR #2024
(R9-UX-9) deferred: that group landed the config key, the unit conversion, the
options field and the published `measured_heat_output_kw`, and
`docs/configuration.md` said of it "read for display only and does not feed the
learners". This group makes that sentence false and rewrites it.

Closes #2016

`ThermalModel.simulate_step` takes `measured_heat_kw` and both zone steps spend
it in place of the `cop * electrical_power` they infer for Q_hp; free external
heat still joins it exactly as before, and `None` — the default, and what every
planning call passes, a horizon holding no measurement — is byte-for-byte the
previous behaviour. Only the two interval learners pass one, through
`_replay_interval`, which is the dedupe of their identical replay block, so the
substitution is decided in one place and the two cannot diverge about what the
elapsed interval delivered. `_interval_measured_heat_kw` answers that question:
the flow meter's own refusals (no key, an outranking power or frequency signal,
a stale, negative, unknown-unit or no-drop reading) are `flow_meter
.read_heat_output_kw`'s and are restated nowhere, and one refusal is new here —
an interval the plan gave partly or wholly to something other than space
heating, because the meter reads one sum and these learners persist what they
conclude.

What it measures: fourteen copies of the tree in
`dev/audit/harnesses/ux10_flow_into_model.py` — the head, the merge base's
production files under this head's tests (the failing-first red), and one
mutant per site the diff adds — each running the new block of
`tests/features.py` sliced verbatim out of it, and each printing eleven
`repr`'d figures: six on the key-unset arm, which are the byte-identical null
control, and five on the planted arm, which are what the substitution moves.

## Head

`f9809c06ae7d5cdf13e3cf2ece3d3b74b69c9fdc`, measured against merge base
`a8ce87571e6b1c093e57036207828c74c70644f4` (`git fetch origin main` at
`Fri Oct  9 15:45:25 UTC 2026`). Every figure below was taken at that head on
this box (macOS, Python 3.14.7 from `$HOME/.local/state/hpo/venv-ci/bin`)
except the ones named as CI's, and except the two named as taken at
`ad150485f` — the tree differs between the two only in `tests/features.py`,
and every script in that pair was re-run here.

Six commits on top of the merge base: the feature (`eed6aee87`), the three
ratchet rows it moved down recorded with their reasons (`69d2dab1f`), the
harness's canonical `repo_root` copy and a corrected comment (`29b02f1f5`), the
one-predicate interval rule with the arm it was missing (`68172a557`), the probe
with its equivalent-mutant triage row (`ad150485f`, whose message was amended
after its runs to correct a stated count of trees in it — `git rev-parse
HEAD^{tree}` is `5d94597f893991ab63451f58aba21d44454d6eaa` on both sides of the
amend), and the two source-text pins this diff moved (`f9809c06a`, under
`## Red checks`).

## A prior handoff already holds this topic

`refs/heads/handoff/r9-ux-10` carries `bcbc1af3b` (2026-10-08, author Tvofi2),
a complete handoff for this same group, with its body at
`refs/heads/handoff-body/r9-ux-10` (`87e22e92c`). No pull request was ever
opened for it: `gh pr list --state all --head fix/r9-ux-10` returns `[]`. It is
stacked on `handoff/r9-ux9` at `543393cc`, i.e. cut BEFORE #2024 merged, and
its own body says "Retarget or update this PR from `main` only after #2024
merges".

This seat did not move that ref: a handoff is frozen and only the orchestrator
moves it (`fixer.md` step 6), and a non-fast-forward push would have destroyed
another seat's work. This branch therefore goes to `handoff/r9-ux-10-v2` and
its body to `handoff-body/r9-ux-10-v2`, and **the choice between the two
designs is the orchestrator's**, not this seat's. Four measured facts bear on
it:

1. **Its budget rows are now raises.** That branch records `max_class_loc`
   9047 and `seam_cut_total` 767 in `tests/structure_budgets.json`
   (`git show bcbc1af3b:tests/structure_budgets.json`). Main's caps at this
   merge base are 8818 and 762, so updating that branch from main loosens both
   and `budget-raise-gate` (decision 0013) refuses a raise without the owner's
   approving review at its head. This branch records 8795 and 760 — both down,
   no raise, no owner ask.
2. **The two designs differ in which channel carries the heat.** That branch
   passes the metered kW as `simulate_step`'s `external_heat_kw` with 0.0
   electrical power. That channel is the wood furnace's — `external_heat.py`
   owns its detector, its config and its ledger line — and its body records the
   consequence: "A two-tank plant keeps the commanded figure, because its
   free-heat input charges the wood tank and the step has no route for the
   pump's metered heat there." This branch adds `measured_heat_kw` as the
   pump's own term, leaves `external_heat_kw` one concept, carves out no plant,
   and still lets free heat join the measured pump heat.
3. **Its reason for rejecting the replay dedupe does not hold here.** That body
   rejects it "because `tools/audit/archscore/planted/perturb/G2_dedupe.py`
   plants exactly that dedupe as the archscore's perturbation". Measured: the
   planted cases are applied to the PIN, not to the working tree —
   `tests/arch_score.py`'s own smoke arm calls `cases.extract_pin(...)` and
   builds each case on that copy — so landing the dedupe leaves the corpus
   untouched. `PYTHONPATH=tests/hastub python3 tests/arch_score.py --smoke` at
   this head: rc=0, `ALL 237 ARCHITECTURE SCORE CHECKS PASSED`, including
   `ok a1_G2_dedupe applies to the pinned tree`.
4. **Its measurement strengthens this branch's rejected alternative #1.** That
   body measured the divide-by-the-step's-COP design missing the metered heat
   by up to 0.1639 K at the upper floor of a throttled two-zone Carnot plant
   (tank 60 °C, 2.0 kW, 1.5 h), with single-zone and no-valve plants at 0.0 in
   every cell. This branch rejects the same alternative on reasoning alone; that
   measurement is the better evidence and the two agree.

Both branches feed the same two learners, both refuse a hot-water interval, and
both leave the COP learner alone for the same reason (its denominator would be
unmeasured, which books tracking error as efficiency).

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/ux10_flow_into_model.py <out-dir>`
— one copy of the tree per mutant, the R9-UX-10 block of `tests/features.py`
run in each, failing checks counted. Head: `BLOCK head: rc=0
failing_checks=0`, `ALL 8 UX-10 EXTRACT PASSED`. Merge base under this head's
tests: `BLOCK base: rc=0 failing_checks=6` — the failing-first red, and the two
model checks fail there on `TypeError: ThermalModel.simulate_step() got an
unexpected keyword argument 'measured_heat_kw'` rather than on an assertion, so
the red is the missing production symbol and not a mis-written check.

Each site the diff adds, its mutant and the check that goes red:

| mutant | the production line | failing checks | killed by |
|---|---|---|---|
| `m_sub_single` | `_simulate_step_single`'s `if measured_heat_kw is None` → `if True` | 1 | "the model spends a measured heat output instead of inferring one from the draw" |
| `m_sub_two_zone` | the same predicate in `_simulate_step_two_zone` | 2 | that check's two-zone twin, and "the two-zone house replay predicts a different upper floor" |
| `m_veto` | `_interval_measured_heat_kw`'s predicate → `if False:` | 1 | the arm check, on the hot-water and nothing-commanded arms |
| `m_veto_return_del` | its refusal arm deleted | 1 | the arm check |
| `m_veto_tail_del` | its tail answering `None` (what RETURN_DEL on that line does: the operator leaves `pass`, and the function falls off its end to the same `None`) | 4 | the arm check and the three that assert a value does arrive |
| `m_bound_dhw` | `dhw_kw > 0.0` → `>= 0.0` | 4 | the planted arms: a space-only interval commands `dhw_power` 0.0 |
| `m_bound_space` | `space_kw <= 0.0` → `< 0.0` | 1 | the arm check, on the interval the plan gave nothing |
| `m_guard_off_house` | the house learner's `if predicted_state is None:` → `if False:` | 1 | "a replay that raises costs the sample and nothing else" |
| `m_guard_off_lower` | the lower-floor learner's same guard | 1 | the same check, on the other learner |
| `m_except_return_del` | `_replay_interval`'s `return None` → `pass` | 0 | **equivalent**, and triaged: see `## Unpinned sites` |
| `m_precedence` | `flow_meter.read_heat_output_kw`'s `cap.measured_power or cap.frequency` → `False` | 1 | the arm check, on the power and frequency arms |
| `m_flow_ok` | the same function's `flow.value if flow.ok else None` → `flow.value` | 1 | the arm check, on the stale, negative and unknown-unit arms |

The last two are R9-UX-9's predicates, mutated here because this group is what
makes them load-bearing for a persisted parameter: #2024 pinned that
`read_heat_output_kw` answers `None`, and a learner that read the holder
directly instead of through that gate would leave every one of those checks
green while spending a stale or outranked reading. `m_bound_space` is the one
mutant no check killed until this branch added an arm for it: an interval the
plan gave nothing is refused because `space_kw` must be positive, and the block
now plants `{"power": 0.0}` and asserts the refusal.

## Null control

Three, at three levels.

1. **The model, bitwise.** `simulate_step(..., measured_heat_kw=None)` returns
   a `ThermalState` `==` the one the same call without the keyword returns, on
   both zone paths — asserted in the block, and the substitution's two arms are
   written so the inferred one is the same float expression in the same order
   (`pump_heat_kw = cop * electrical_power`, then `pump_heat_kw + max(0.0,
   external_heat_kw)`), not a re-association of it.
2. **The learner, against the merge base.** The harness prints six `repr`'d
   figures on the key-unset arm — the scale, and the replay's predicted room,
   slab, upper floor, lower floor and residual — and
   `NULL CONTROL every unset-arm figure, head == base: True (6 figures) |
   unchanged in every mutant: True`. Unset is not the same code path as
   "measured and refused", so the block also asserts the two are
   byte-identical to each other (`SCALE_UNSET` 1.01, `ROOM_UNSET` 21.06,
   `SLAB_UNSET` 27.01, `UPPER_UNSET` 20.921666666666667,
   `RESIDUAL_UNSET` -0.021666666666668277 in every tree).
3. **The fixtures, in CI's own instrument.** `PYTHONPATH=tests/hastub python3
   tests/env_drift.py` prints `NO UNCLAIMED DRIFT: 5 scenario(s) checked
   against origin/main` and `NO STALE FIXTURE: 5 committed fixture(s) still
   match what this tree computes`; no fixture configures a flow meter, and both
   claim files are byte-identical to the merge base
   (`git diff --quiet $(git merge-base origin/main HEAD) HEAD --
   tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt`).

**No optimality effect is claimed, so no flat-price difference-in-differences
is owed**, and the reason is structural rather than a measurement: one call
site in the package passes the parameter. `grep -rn "\.simulate_step("
custom_components/heatpump_optimizer/*.py` returns ten, and `grep -rn
measured_heat_kw custom_components/` returns one call — `coordinator.py`'s
`_replay_interval` — against the model's own four internal dispatches. The
nine others are `optimizer.py`'s two solve rollouts, `thermal_model.py`'s two
trajectory entries, `sysid.py`'s two experiment rollouts, `topology.py`'s
sensor-advisor sweep, `away.py`'s recovery estimate and `diagnosis.py`'s
what-if, none of which can receive a measurement. No plan changes on an
install without the key (null control 2 and 3); on one with it, a plan changes
only through the learned `house_heat_loss_scale` or `lower_floor_loss_ratio`,
which is the feature. `tests/optimality.py` and `tests/backtest.py` are in this
diff's scope and are left to CI, which is the standing detector for a
plan-level regression on the fixture installs.

**What the substitution moves, and what it honestly does not.** The block and
the harness separate the two:

- The two-zone upper floor — the temperature the house heat-loss residual is
  differenced against in a two-zone house — moves: `UPPER_PLANTED`
  20.943135666666667 against `UPPER_UNSET` 20.921666666666667, and the
  residual with it, -0.043135666666668016 against -0.021666666666668277. At
  the merge base the planted arm reads the unset arm's number, so the
  difference is this group's.
- The single-zone replay's slab moves (`SLAB_PLANTED` 27.0422035 against
  `SLAB_UNSET` 27.01) and its **room does not** (`ROOM_PLANTED` ==
  `ROOM_UNSET` == 21.06), and the two-zone **lower floor does not** either
  (20.28125 both). That is the model's own shape, not this group's: `_single_
  zone_rates` puts `thermal_power` in the slab's rate and the room's rate
  carries no heat term, and `_two_zone_rates` puts the floor share in the slab
  and the radiator share in the upper floor, so within the ONE step a learner
  replays, the room and the lower floor follow the previous state's slab.
  `_substeps_and_loss` answers 1 for this fixture at every `dt_hours` from 0.25
  to 2.0 and every wind speed tried, so no sub-step re-entry couples them
  either.
- **The fit does not move at one sample, on either path**, and the block says
  so rather than asserting a scale change: `learner_newton_step` moves a sample
  `HOUSE_LOSS_ALPHA` (0.02) of the way to its target, and the harness's
  `SCALE_UNSET` and `SCALE_PLANTED` both read 1.01 from the 1.0 start, in every
  one of the fourteen trees. That the alpha and not the heat input is what
  binds there is a one-off scratch measurement, so it lands in nothing (step 18)
  and is stated with its rule rather than quoted as a figure: driving the real
  learner on the `_t2_house` fixture across commanded powers spanning the
  fixture's range — `_t2_house(power=P)` then `_t2_drive(c,
  "_async_learn_house_heat_loss")` under the block's frozen clock, planted and
  not — printed `scale=1.01` with `samples=1` on every one. What the heat input
  does move is the residual the target is computed from, and that is the
  harness's `RESIDUAL_*` pair above.
- One consequence this group did not cause and cannot fix inside its scope,
  recorded because it bounds the feature: since the single-zone one-step
  replay's room prediction carries no heat-input term at all, v4.0.5's
  "measured power wins over commanded" preference in `_interval_space_power`
  cannot reach a single-zone fit either. The evidence is in the tree rather
  than in a scratch probe. `_single_zone_rates`
  (`custom_components/heatpump_optimizer/thermal_model.py`) returns
  `(q_slab_to_room - q_loss + q_internal + q_solar) / p.room_thermal_mass` for
  the room — no `thermal_power` term — and puts `thermal_power` in the slab's
  rate, and the harness prints exactly that split on one replayed interval:
  `ROOM_PLANTED` == `ROOM_UNSET` (21.06) while `SLAB_PLANTED` 27.0422035 !=
  `SLAB_UNSET` 27.01. Its control is the two-zone twin, whose upper-floor rate
  does carry the radiator share: `UPPER_PLANTED` 20.943135666666667 against
  `UPPER_UNSET` 20.921666666666667 on the same 5.222035 kW, which is what shows
  the instrument can see an effect where the model has one. See
  `## Forward-carry` for why this is not a carry.

## Figures

- `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` — `D=$(mktemp -d); python3
  tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir
  "$D"; cat "$D/scope.txt"`. The four scoped out are `frontend.py`,
  `ha_contract.py`, `layout.py` and `open_meteo.py`. Keyed on the mode line,
  not the count.
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`. Three rows moved
  and all three moved DOWN, recorded in `69d2dab1f` with the reasons in that
  commit message: `duplication_copies` 38 → 37, `max_class_loc` 8818 → 8795,
  `seam_cut_total` 762 → 760. **No raise is asked and no budget moved up.**
  The seam table's own rows say where the cut went: fetch's `xmeth` 32 → 31
  and learning's `xattr` 233 → 232, against learning's `xmeth` reading 60 on
  both sides because the one new learning→core edge (the helper's
  `_commanded_split` call) offsets the `_current_weather` edge that existed
  twice and now exists once.
- `BLOCK head: rc=0 failing_checks=0` … `BLOCK base: rc=0 failing_checks=6`,
  and the eleven per-tree figures — `PYTHONPATH=tests/hastub python3
  dev/audit/harnesses/ux10_flow_into_model.py <out-dir>`.
- 6 unpinned sites, and `no closures or fast red predicted against
  a8ce87571e6b` — `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py
  --base origin/main`. Each is dispositioned under `## Unpinned sites`; the
  seventh this diff added carries its triage row and no longer lists.
- `pinned custom_components/heatpump_optimizer/coordinator.py:870 RETURN_DEL`
  and `LIST RETURN_DEL: 1158 site(s) in 70 file(s), 821 unpinned, ratcheted` —
  `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --list RETURN_DEL`,
  which is the triage row read back by the instrument that counts the
  inventory, not by the file's existence.
- `NO UNCLAIMED DRIFT: 5 scenario(s) checked against origin/main NO STALE
  FIXTURE: 5 committed fixture(s) still match what this tree computes` —
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py`; and `claims hygiene:
  origin/main ok` — `PYTHONPATH=tests/hastub python3 tests/env_drift.py
  --claims-only origin/main`.
- `TOTAL: 0 error(s) across 40 policy file(s)` — `node
  tools/policy/policy_lint.mjs`; `node tools/policy/policy_lint.mjs --budgets`
  exits 0 and no policy file is touched by this diff (`docs/configuration.md`
  is not in `POLICY_GLOBS`). `prepr.sh`'s own `check policy corpus` line names
  six policy files `origin/main` moved since this merge base (`fixer.md`,
  `fix-review.md`, `ci-autofix.md`, `claim-files.md` and the two generated
  `.claude/rules` copies); all six were re-read at `922483383`, and the only
  obligation that changes is step 5's, which now also names `tests/run.sh`'s
  four `run_always` scripts — all four are in the list below.
- Ten `simulate_step` call sites, one passing the parameter — `grep -rn
  "\.simulate_step(" custom_components/heatpump_optimizer/*.py` and `grep -rn
  measured_heat_kw custom_components/`.
- The diff's own size — `git diff --numstat $(git merge-base origin/main HEAD)
  HEAD`: 89 added / 36 deleted in `coordinator.py`, 38 / 6 in
  `thermal_model.py`, 1 / 1 in `docs/configuration.md`, and 376, 331/5, 6, 2, 1
  and 4/4 in the harness, `tests/features.py`, the triage row, `seam_map.json`,
  `closures.json` and the budget table. 127 production lines added and 42
  deleted, the deletions being the two replay blocks the helper replaced; well
  inside the preamble's ~400.
- `1 of 3887 FEATURE CHECKS FAILED` — `PYTHONPATH=tests/hastub python3
  tests/features.py` at this head, the one being the merge base's own
  storage-plan check on this box (`## Red checks` 4). At `ad150485f` the same
  command printed `4 of 3887`, the other three being the pins `f9809c06a`
  follows. All 8 of this branch's new checks pass inside the full run.
- The rest of `scope.run`, green on this box, each with its own summary line —
  `PYTHONPATH=tests/hastub python3 tests/<name>.py` or `node tests/<name>.mjs`.
  At this head: `entities.py` (`ALL 2235 ENTITY CHECKS PASSED`),
  `guard_pins.py` (`ALL 50 GUARD PIN CHECKS PASSED`), `debug_collect.py`
  (`ALL 64 DEBUG COLLECT CHECKS PASSED`), `block_duty.py` (`ALL 46 BLOCK DUTY
  CHECKS PASSED`), `manual_plan.py` (`ALL 129 manual plan checks PASSED`),
  `config_flow_steps.py` (`ALL 499 checks PASSED`), `layout.py` (`layout
  self-test: ok`, a `run_always` script the scope skipped), `closure.py
  selftest` (`ALL 57 closure shrink pins PASSED`, also `run_always`) and
  `structure.py`. At `ad150485f`, whose tree differs only in
  `tests/features.py`, which none of these reads: `harness_headers.py` (`ALL
  109 HARNESS HEADER CHECKS PASSED`), `arch_score.py --smoke` (`ALL 237
  ARCHITECTURE SCORE CHECKS PASSED`), `typing_ruler.py`, `doc_claims.py` (`ALL
  160 checks PASSED`), `deployment_shape.py`, `wood_advisor.py`,
  `solar_alignment.py`, `arch_score_head.py` (`ALL 14 ARCHITECTURE SCORE HEAD
  CHECKS PASSED`), `edge.py` (`ALL EDGE CASES PASS`), `validate.py` (`NO
  ISSUES`), `finite_boundary.py` (`ALL 84 FINITE BOUNDARY CHECKS PASSED`),
  `boost_drift_replay.py` (`ALL 46 BOOST DRIFT CHECKS PASSED`), `env_drift.py`,
  `plan_view.py`, `md_tables.mjs` (`doc_orphaned_table_rows=0`,
  `doc_misrendered_lines=0`), `card.mjs` (`ALL CARD CHECKS PASSED`) and
  `card_drift.mjs` (`identical in all 40 states`).
- LEFT TO CI, under the owner's 2026-10-07 ruling that heavy scripts run there
  and seats cite check-runs: `stress.py` (which also holds the gate lease, and
  this seat never took it by hand), `optimality.py`, `golden.py`,
  `backtest.py`, and `arch_score.py`'s full corpus (the 58 planted cases
  measured against the pin; its `--smoke` arm, which is what proves every case
  still applies, ran locally and is a figure above).
  All five are named in `scope.run`; `arch_score.py`'s planted corpus is
  unaffected by this diff because the cases apply to the PIN —
  `tests/arch_score.py`'s own smoke arm calls `cases.extract_pin`, and the
  dedupe this branch lands is the corpus's `G2_dedupe` control, whose anchors
  live in the pinned copy.

## Architecture score

`PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff
origin/main` at this head reads `Architecture score: dS -0.0022 WORSENS
(inadmissible: coord_footprint 2586->2590)`. One metric rises. The
`arch-score` required check and the `## Architecture score` rule that answers a
rise both landed on `main` after this branch's merge base, in #2068
(`.github/workflows/arch-score.yml`, `tools/audit/archscore/gate.py`), so this
section is written to that rule rather than to the merge base's template, which
called the command optional and report-only.

- `coord_footprint` 2586 -> 2590: the metric counts logic statements in the coordinator class plus every module-level function handed it, and this branch hands it two, `_replay_interval` and `_interval_measured_heat_kw`.
  The first is a dedupe and reads as a fall rather than growth — the two learners' identical replay blocks were a dozen of those statements between them and are five in the helper, and the metric's own docstring says an Extract Method or a dedupe is not growth, because plumbing is not counted. The rise is the second function: a decision that did not exist at any price before this branch, namely whether the interval a learner replays may be spoken for by a meter at all — a reading exists, the plan gave the interval to space heating, and nothing else refuses it. Four statements is that decision, and the decision is the feature.
  The same change moves all three of `tests/structure.py`'s rows DOWN: `duplication_copies` 38 → 37 (the clone pair the helper absorbs), `max_class_loc` 8818 → 8795 (the two copies left the measured class span, the helper being module-level) and `seam_cut_total` 762 → 760 (the `_current_weather` edge and the `_thermal_model` read each existed twice and now exist once, against the one new learning→core edge the interval rule adds). So four logic statements are bought with 23 lines of class span, one counted clone and two seam crossings, and no budget row and no other gate metric moves.
  The alternative that would not raise it is #6 under `## Alternatives considered, and why each lost`: pass the substitution at each learner's own `simulate_step` call and keep both copies. It is cheaper on this metric and worse on every other one — two places deciding what the elapsed interval delivered, which is the divergence the shared helper exists to prevent — and it costs +2 `max_class_loc` and +1 `seam_cut_total` against zero headroom, i.e. a budget raise. `fixer.md` step 17 prices cost last: "Cost is no reason to take the worse fix."

## Red checks

`tests/harness_headers.py` went red once on this branch, `13 of 109 HARNESS
HEADER CHECKS FAILED`, for two unrelated reasons:

1. **This branch's, and the check is the cheaper detector.** `python
   copies=72 differ=['dev/audit/harnesses/ux10_flow_into_model.py']` — the
   harness inlined `repo_root` with the function-local import dropped, so its
   text differed from `tools/audit/repo_root.py`'s. The check that fired is
   the one that exists to fire on it, it costs seconds against the 994 s the
   script takes overall, and no cheaper detector is owed. Fixed in `29b02f1f5`
   by restoring the canonical text byte-for-byte.
2. **Not this branch's, and not the tree's.** The other twelve are one cause:
   `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py exits 0 [rc=124
   cpu=186.5s stderr=wall limit 900s exceeded]` and the eleven `RESULT …
   matches header` rows that cascade from a run that produced nothing. The
   harness spent 186.5 s of CPU inside a 900 s wall on a box running three
   other seats' suites beside it — including this seat's own `features.py` and
   `entities.py` — so the wall bound, not the tree, is what fired. R9-F10.11
   is the group that added this harness's CPU bound for exactly this class of
   flake; the standing detector is that bound, and its standing cost is that a
   shared box can still exceed the wall. Re-run alone, at `ad150485f` (this
   head's tree less the `tests/features.py` pin fixes, which no executed
   harness reads — the three the check runs are `dst_window_factors.py`,
   `window_size_sweep.py` and `option_doc_coverage.py`, and none names
   `features.py`): `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`
   → rc=0, `ALL 109 HARNESS HEADER CHECKS PASSED`.

`tests/features.py` went red on this branch too, and the full run is the
detector that found it:

3. **This branch's — three source-text pins whose subject moved.** At
   `ad150485f` the run printed `4 of 3887 FEATURE CHECKS FAILED` and three were
   this branch's. The #1520 humidity seam rule enumerates every humidity-aware
   call in the four solver-side modules and dispositions each one, so the
   extracted `_replay_interval` call to `simulate_step` was an open seam and the
   two allow-list entries that covered the same call inside each learner went
   stale; and #53's pin reads `hour_of_day=previous_time.hour` out of
   `_async_learn_house_heat_loss`'s own source, where the call no longer is. All
   three are a moved subject, not a behaviour change. `f9809c06a` follows the
   code: one allow-list entry for the helper both learners share, and #53's pin
   reads the helper's source while also holding BOTH learners to calling it, so
   a re-inlined replay that dropped the learned profile now fails a pin that
   names it. No cheaper standing detector exists — the pins live inside
   `tests/features.py`, so only that script runs them; while iterating, this
   seat drove `_p3_seams` directly over the four modules as a scratch tool
   (`open seams: []`, `stale: []`, 9 allowed and 9 used), which is not a figure
   and lands in nothing.
4. **Not this branch's — one check fails at the merge base on this box too.**
   The fourth failure is `R9-F2.1 P3: the shipped storage plan is no worse on
   its own objective than the half-price floor's plan refined under it [shipped
   110.4366, seeded with the half-price plan 110.1297]`, a solver-objective
   comparison, and it is the one failure left at this head (`1 of 3887 FEATURE
   CHECKS FAILED`). Measured twice rather than argued: that check's own block
   (the R9-F2.1 section of `tests/features.py`) run inside a `git archive
   a8ce87571` copy of the merge base prints the identical FAIL with the
   identical two numbers, and `tests/env_drift.py` — the standing instrument for
   exactly this question, which compares this tree against `origin/main` in one
   environment because solver floats are not bit-stable across BLAS builds —
   reports no drift. A one-off scratch probe drove both zone steps over a grid
   of powers, step lengths, external heats, humidities and a throttling and a
   non-throttling valve at both trees and compared every `repr` of every
   resulting state: identical. The check is its own detector and it fires at the
   base, so this is not a red this branch turned, and `defect-root-cause.md`'s
   cheaper-detector question has no purchase on it. No pull request is open on
   this head yet, so there are no check-runs to cite; CI's `features` lane on
   the runner is the authority once the orchestrator pushes, and this box is not
   it — the recorded route for a green `features`/`optimality` locally is the
   hpo-ci Linux container with its Sandybridge pin.

## Forward-carry

none. One finding this group established by measurement has no destination
stage, so `finding-propagation.md`'s test — a stage that has not started, whose
options the finding narrows, whose assumption it invalidates, or whose option
it removes — is not met by anything on the roster: the groups still
`not-started` are R9-UX-6 (money and memory) and R9-UX-7 (model status and
diagnostics), and neither rests on the interval replay's heat input. The
finding is recorded in `## Null control`'s last bullet instead: the
single-zone one-step replay's room prediction carries no heat-input term, so
neither this group's measured heat nor v4.0.5's measured power can reach a
single-zone fit. Fixing it is a change to `_single_zone_rates`' coupling —
D2's judgement, every golden fixture's drift, and outside a UX feature group's
400 lines — and this seat files nothing and posts nothing, so it is handed to
the orchestrator to route.

## Friction

- `ratchet-budgets`: `cost`: `max_class_loc` and `seam_cut_total` both sit at
  zero headroom on a class every feature lane must touch, so a two-line
  feature is priced as a raise unless it carries a dedupe large enough to pay
  for itself. This group found one (the two learners' identical replay block,
  which the archscore corpus already carries as its `G2_dedupe` GOOD control)
  and moved all three rows down, but a lane with no duplication in reach has
  no payment pool at all.
- `gate-scoping`: `cost`: `tests/harness_headers.py` executes three live
  harnesses, one of which has a 900 s wall bound; on a box shared by four
  seats it exceeds the wall and reddens twelve unrelated rows. The gate cannot
  tell a seat whether that red is theirs.
- `delivery-status-tracking`: `stale`: the roster's `R9-UX-10` reads
  `{"stage": "not-started", "branch": null}`
  (`git show origin/handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json`)
  while `refs/heads/handoff/r9-ux-10` has carried a complete handoff for the
  same group since 2026-10-08 02:37, and `refs/heads/handoff-body/r9-ux-10`
  its body. Nothing a dispatched seat reads — the group's brief, its `resume`
  field, #201 — names it, so the group was implemented a second time from
  today's main. The record outranks a wave body, and here the record was the
  thing that was stale: a `resume.stage` of `not-started` over a handoff ref
  that exists is a row not written at the last handoff.

## Unpinned sites

`PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`
lists six sites this diff adds; a seventh it added now carries its triage row
and no longer lists. Of the seven, six are killable and one is equivalent. The
killable ones are `mutation-autofix`'s to pin from CI's own measurement
(`ci-autofix.md` — wait for the bot commit, do not duplicate), and each is
named here with the driver and the check that kills it, measured locally by
the harness's own variant of the same mutation:

- `custom_components/heatpump_optimizer/coordinator.py:826 GUARD_OFF` — pinned
  by `mutation-autofix`; driver `tests/features.py`, the arm check, measured
  locally as `m_veto` (1 failing check).
- `custom_components/heatpump_optimizer/coordinator.py:826 CMP_BOUND*2` —
  pinned by `mutation-autofix`; driver `tests/features.py`, the planted arms
  for the `dhw_kw` bound (`m_bound_dhw`, 4) and the nothing-commanded arm for
  the `space_kw` bound (`m_bound_space`, 1).
- `custom_components/heatpump_optimizer/coordinator.py:828 RETURN_DEL` —
  pinned by `mutation-autofix`; driver `tests/features.py`, the three checks
  that assert a value does arrive (`m_veto_tail_del`, 4).
- `custom_components/heatpump_optimizer/coordinator.py:4992 GUARD_OFF` and
  `custom_components/heatpump_optimizer/coordinator.py:5147 GUARD_OFF` —
  pinned by `mutation-autofix`; driver `tests/features.py`, "a replay that
  raises costs the sample and nothing else", which drives
  `_t2_raise_model` on each learner (`m_guard_off_house`, `m_guard_off_lower`,
  1 each).
- `custom_components/heatpump_optimizer/thermal_model.py:2594 CLAMP_DROP` —
  the `max(0.0, external_heat_kw)` clamp the merge base carried on this line,
  re-digested because the line's left operand is now named `pump_heat_kw`. It
  was unpinned at the base too: no `_simulate_step_single` row exists under
  `tests/mutation_ledger/killed_by/thermal_model.py/` or
  `survivor_triage/thermal_model.py/`, so one anchor retired and one was added
  and the inventory count does not grow from it. If a driver kills it,
  `mutation-autofix` pins it; nothing in this diff reaches it, since no check
  here passes a negative `external_heat_kw`.
- `custom_components/heatpump_optimizer/coordinator.py:870 RETURN_DEL` —
  **written triage, verdict `equivalent`**, landed as
  `tests/mutation_ledger/survivor_triage/coordinator.py/_replay_interval.RETURN_DEL.d7923b87.json`:
  the statement is the last one in `_replay_interval`'s `except` arm, so
  replacing it with `pass` lets the function fall off its own end and return
  the same `None`. Measured rather than argued — the harness's
  `m_except_return_del` variant applies exactly that replacement and the block
  reports `failing_checks=0`, against 1 to 6 for the eleven other variants,
  two of which (`m_guard_off_house`, `m_guard_off_lower`) reach that same arm
  through `_t2_raise_model`. Read back through the instrument that counts the
  inventory: `pinned custom_components/heatpump_optimizer/coordinator.py:870
  RETURN_DEL`.

## Alternatives considered, and why each lost

Step 17's requirement, and the architect note's ownership rules bind the first
two.

1. **Convert the measured heat to an electrical equivalent** (`measured / cop`)
   and pass that as `previous_power`, in `flow_meter.py` or at the call site.
   Lost: the COP that matters is the one the step itself uses, and in the
   two-zone path that is `compute_cop(outdoor, flow_temp=buffer when
   throttled)` — an outside division re-derives model internals and diverges
   silently the day the throttling predicate moves.
2. **Route the measurement through the existing `external_heat_kw` channel**,
   which already adds thermal kW without touching the COP. Lost: that channel
   is the wood furnace's, and in the two-tank branch it charges the wood tank
   (#40's topology); spending it for the pump's own output duplicates a
   concept and mis-routes heat.
3. **Feed `_learn_measured_cop`** with `measured thermal / commanded power`.
   Lost: the denominator is then unmeasured, so every tracking error lands in
   `cop_scale`, the multiplier every plan's cost runs through — the exact
   failure v4.0.5's tracking-EWMA gate exists for — and the precedence rule
   puts the meter only where no power signal exists, which is precisely where
   that gate has nothing to work with.
4. **Fold the measured thermal into `_fold_capacity_envelope`**, which prices
   the plan's per-bucket electrical ceiling as `observed_cop * measured_power`
   and today returns early on a flow-meter install because `_measured_power`
   is `None`. Not taken: a second consumer in another seam, needing the
   near-nameplate, immersion and defrost vetoes that `_learn_measured_cop`'s
   tail supplies and a flow-meter install cannot run. Folding an unvetted
   measurement into a cap that limits every plan is the riskier change and
   belongs in its own group; this one's scope is the replay's heat input.
5. **Split the measured total by the commanded space share** instead of
   refusing a blended interval. Lost: a proportional split is a guess, and the
   tree's own answer to a blended interval is to refuse it —
   `_cop_reference_curve` returns `None` for one and `_interval_space_power`
   returns `None` when the observed mode cannot serve space.
6. **Add the substitution at each learner's own `simulate_step` call**, two
   sites, no extraction. Lost on both counts: the two learners could diverge
   about what the interval delivered, and it is priced at +2 `max_class_loc`
   and +1 `seam_cut_total` against zero headroom, i.e. a raise. The dedupe
   pays for the feature and removes a counted clone besides; it is the
   archscore corpus's own `G2_dedupe` GOOD control, landed as a module-level
   helper rather than the method the control plants, because the class span is
   the binding budget (−23 lines against the method's −2).
