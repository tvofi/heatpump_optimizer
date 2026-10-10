<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
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

`beb97ea691f95f20de19f512460ee7ad361c35ba` merges the authored code head `2b8fdf844cd36ccabdfc24b310ef0ac75b311c91` into this PR's previous head, which carried its own row `dev/programme/delivery/2118.md`. The PR tree is that code head plus the row.

`2b8fdf844cd36ccabdfc24b310ef0ac75b311c91`, measured against merge base
`7cd5a588cbbbef354c00148040da2d720b8a888c`. Every figure below was re-taken at that
head on this box (macOS, Python 3.14.7 from
`$HOME/.local/state/hpo/venv-ci/bin`, the typing census from a pinned
`.venv-typing` of the same pins the `typing` job installs) except the ones named
as CI's and except the ones explicitly attributed to an earlier commit of this
branch. Figures that are a function of `origin/main`'s tip were taken against
`969c3a5c84d0ee6fb403ecebd18d16c810b3e40c` at 2026-10-10T17:33:36Z; that tip
moves, the commands do not.

This head is the repair of the blocked head `bc048801823eb4f77cfa42f54083214c154336a5`
(verdict: `root-cause-unanswered: typing and mutation went red at this head and
## Red checks names neither`). It adds two things to it, and nothing else:
the merge of `72cfb1d07` — the `mutation-autofix` bot's own `ci: pin killed
mutants` commit, six ledger files pinning the seven sites the `mutation` check
refused, waited for and not duplicated (`ci-autofix.md`) — and `2b8fdf844`, a
one-line typing annotation answering the `typing` red (under `## Red checks` 6).
The authored feature head is unchanged: `ff2c85753644cf2f713b9da312758869954fbd4a`,
followed by this PR's own row `bc0488018` (`dev/programme/delivery/2118.md`),
the bot's pins, and the annotation.

**This head is a twice-retargeted branch.** It was cut from `a8ce87571` (#2024),
and `origin/main` has taken thirteen merges since — #2041 #2056 #2057 #2059
#2065 #2067 #2068 #2069 #2074 #2078, then #2073 #2010 #2071 — so it carries two
merge commits (`7297c1bd1` for `23d354970`, `d3fbdcf63` for `7cd5a588c`), by
merge and not by a re-cut (`fixer.md` step 6, tvofi 2026-10-01). Git resolved
every file of both; the `ledgermerge` driver took `tests/structure_budgets.json`
and `tests/closures.json` each time, and the two claim files came out identical
to main's. Nothing was resolved by choosing a side, and nothing is carried
across the second merge: `fixer.md` step 6 re-executes steps 2–8 on the merged
tree, so every figure below is from that re-execution at this head. What main
brought that this branch interacts with: #2065's `draw_range.py` and its 396
lines of `tests/features.py` (a new production module, so the censuses moved);
#2068's `arch-score` required check, `tools/audit/archscore/gate.py` and the
`## Architecture score` rule this body answers; and #2073's stale-pin arm in
`tools/pr/ci_predict.py`, which reads the ledger's backward direction — the arm
a move like this one can redden, and the one the `## Unpinned sites` section
below reports on.

Twelve authored or bot commits over the feature: the feature (`eed6aee87`), the
three ratchet rows it moved down recorded with their reasons (`69d2dab1f`), the
harness's canonical `repo_root` copy and a corrected comment (`29b02f1f5`), the
one-predicate interval rule with the arm it was missing (`68172a557`), the probe
with its equivalent-mutant triage row (`ad150485f`, whose message was amended
after its runs to correct a stated count of trees in it — `git rev-parse
ad150485f^{tree}` is `5d94597f893991ab63451f58aba21d44454d6eaa`, unchanged by
the amend), the two source-text pins this diff moved (`f9809c06a`, under
`## Red checks`), one retarget commit each (`7297c1bd1` + `27415fa53` for the
first, `d3fbdcf63` + `ff2c85753` for the second, each pair being the merge and
the provenance re-record it needs), the delivery row (`bc0488018`), the bot's
pin commit (`72cfb1d07`, authored by `mutation-autofix`, merged not cherry-picked
so its provenance stays its own) and the typing annotation (`2b8fdf844`).

## A prior handoff already holds this topic

`refs/heads/handoff/r9-ux-10` carries `bcbc1af3b` (2026-10-08, author Tvofi2),
a complete handoff for this same group, with its body at
`refs/heads/handoff-body/r9-ux-10` (`87e22e92c`). No pull request was ever
opened for it: `gh pr list --state all --head fix/r9-ux-10` returns `[]`
(re-checked at this head, 2026-10-10). It is
stacked on `handoff/r9-ux9` at `543393cc`, i.e. cut BEFORE #2024 merged, and
its own body says "Retarget or update this PR from `main` only after #2024
merges".

This seat did not move that ref: a handoff is frozen and only the orchestrator
moves it (`fixer.md` step 6), and a non-fast-forward push would have destroyed
another seat's work. This branch therefore goes to `handoff/r9-ux-10-v2` and
its body to `handoff-body/r9-ux-10-v2`, and **the choice between the two
designs is the orchestrator's**, not this seat's. The orchestrator chose this
one — #2118 is open from `fix/r9-ux-10-v2`, and its first review confirmed the
fix sound and blocked only the body and the two reds this head answers. The
four measured facts below bear on that choice:

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
  "$D"; cat "$D/scope.txt"`. Sixteen changed files at this head — the previous
  head's ten, plus the six ledger files the bot's pin commit adds. The four
  scoped out are
  `frontend.py`, `ha_contract.py`, `layout.py` and `open_meteo.py` — and
  `layout.py` is a `run_always` script, so it ran anyway and is in the list
  below. Keyed on the mode line, not the count.
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`. Three rows moved
  and all three moved DOWN, recorded in `69d2dab1f` with the reasons in that
  commit message: `duplication_copies` 38 → 37, `max_class_loc` 8818 → 8795,
  `seam_cut_total` 762 → 760, against main's caps at this merge base (38 / 8818
  / 762, `git show origin/main:tests/structure_budgets.json`). **No raise is
  asked and no budget moved up**; two merges later the readings are unchanged,
  and `recorded_at` was re-pointed each time (`ff2c85753`, to `7cd5a588c`). The
  seam table's own rows say where the cut went: fetch's `xmeth` 32 → 31 and
  learning's `xattr` 233 → 232, against learning's `xmeth` reading 60 on both
  sides because the one new learning→core edge (the helper's `_commanded_split`
  call) offsets the `_current_weather` edge that existed twice and now exists
  once.
- `BLOCK head: rc=0 failing_checks=0` … `BLOCK base: rc=0 failing_checks=6`,
  the eleven killable mutants at 1 to 4 failing checks, `m_except_return_del` at
  0, and `NULL CONTROL … True` / `BITES … True` — `PYTHONPATH=tests/hastub
  python3 dev/audit/harnesses/ux10_flow_into_model.py <out-dir>`, re-run at
  this head: all twelve mutant counts identical to the table under
  `## Mutation proof`, `ALL 8 UX-10 EXTRACT PASSED` in the head block's own
  output, every unset-arm figure unchanged head == base.
- No unpinned-sites line at all, and `no closures or fast red predicted against
  7cd5a588cbbb` — `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py
  --base origin/main` at this head. The six sites the previous head listed are
  the bot's pins now (`72cfb1d07`), so the predictor has nothing to report;
  the composition and each site's readback are under `## Unpinned sites`.
- `pinned custom_components/heatpump_optimizer/coordinator.py:830 RETURN_DEL`
  and `pinned custom_components/heatpump_optimizer/coordinator.py:872
  RETURN_DEL` beside `LIST RETURN_DEL: 1171 site(s) in 71 file(s), 820
  unpinned, ratcheted` — `PYTHONPATH=tests/hastub python3
  tests/mutation_table.py --list RETURN_DEL` at this head, after the bot's
  pins: the instrument that counts the inventory reads both of this diff's
  RETURN_DEL sites back as pinned, 830 by the bot's pin and 872 by its triage
  row, and the unpinned stock is one lower than the base's 821.
- `claims_extracted=125 claims`, `claims_checked=125`, `claims_true=123`,
  `claims_false=0`, `claims_stale=0`, `claims_unverifiable=2`,
  `arch_modules_on_disk=75 modules`, `arch_map_listed=75 modules`,
  `arch_map_missing=0 modules`, `ha_module_level_importers=27 modules`,
  `config_defaults_compared=89 rows`, `config_ranges_compared=91 rows` —
  `PYTHONPATH=tests/hastub:custom_components python3
  dev/audit/rounds/round4/D6/claims.py`, which is the census the coordinator
  asked to re-derive because #2065 added a production module and the 74-vs-75
  merge-only-false class has bitten twice. Both counts read 75 on the merged
  tree and the map misses none: this branch adds no module, so the census is
  main's own and consistent.
- `NO UNCLAIMED DRIFT: 5 scenario(s) checked against origin/main NO STALE
  FIXTURE: 5 committed fixture(s) still match what this tree computes` —
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py`; `claims hygiene:
  origin/main ok` — `PYTHONPATH=tests/hastub python3 tests/env_drift.py
  --claims-only origin/main`; and both claim files byte-identical to the merge
  base — `git diff --quiet $(git merge-base origin/main HEAD) HEAD --
  tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt`.
- `TOTAL: 0 error(s) across 40 policy file(s)` — `node
  tools/policy/policy_lint.mjs`; `node tools/policy/policy_lint.mjs --budgets`
  exits 0 and no policy file is touched by this diff (`docs/configuration.md`
  is not in `POLICY_GLOBS`). `prepr.sh`'s `check policy corpus` line names the
  policy files `origin/main` moved since the original base (`fixer.md`,
  `fix-review.md`, `ci-autofix.md`, `claim-files.md`, `PULL_REQUEST_TEMPLATE.md`
  and the generated `.claude/rules` copies); all were re-read, and the two
  obligations that change are step 5's, which now also names `tests/run.sh`'s
  four `run_always` scripts (all four ran), and the template's new `arch-score`
  rule, answered under `## Architecture score`.
- `RESULT read=63 ignored=25 declared_none=34 blind=0 dead=0 refused=0
  runs=139 seconds=82.9` and `FIELD COVERAGE ok` — `node
  tools/policy/field_coverage.mjs`, re-run at this head, directly so the detail
  survives (`## Red checks` 5).
- `ALL 9 typing-ruler checks PASSED` under the pinned toolchain —
  `<venv-typing>/bin/python tests/typing_ruler.py --mypy`, the same census the
  `typing` CI job runs (mypy 2.3.1, homeassistant-stubs 2026.9.3): red first at
  the blocked head (`errors 1`, `by_code[no-any-return] 1`), green at this one
  (`errors did not grow ... ok`, census 0), the repair `## Red checks` 6
  describes.
- Ten `simulate_step` call sites, one passing the parameter — `grep -rn
  "\.simulate_step(" custom_components/heatpump_optimizer/*.py` (ten lines) and
  `grep -rn measured_heat_kw custom_components/`.
- The diff's own size — `git diff --numstat $(git merge-base origin/main HEAD)
  HEAD`: 89 added / 36 deleted in `coordinator.py`, 38 / 6 in
  `thermal_model.py`, 1 / 1 in `docs/configuration.md`, 377, 331/5, 2, 1 and
  4/4 in the harness, `tests/features.py`, `seam_map.json`, `closures.json`
  and the budget table, and the bot's six 6-line pin files plus this branch's
  own 6-line triage row under `tests/mutation_ledger/`. The annotation commit
  re-annotates a line the branch itself added, so `coordinator.py`'s numstat is
  unchanged by it. 127 production lines added and 42
  deleted, the deletions being the two replay blocks the helper replaced; well
  inside the preamble's ~400.
- **`tests/features.py`: the complete run at the previous merged head, and why
  this head's could not be completed here.** At `27415fa53` — this head's tree
  less the three commits #2073/#2010/#2071 merged in `d3fbdcf63` — the full run
  read `1 of 3938 FEATURE CHECKS FAILED`, the one being the merge base's own
  storage-plan check (`## Red checks` 4), with all 8 of this branch's new checks
  passing inside it. At this head it was attempted three times and none
  completed: the first was killed when the session process exited with the box's
  restart, and the second and third ran against `uptime` load averages of 65 to
  80 with nineteen competing test processes, the last reaching 11.6 kB of
  warnings and not one check in half an hour on 5% of a core. No attempt was
  stopped by a failing check, and none of the three is evidence about the tree —
  `tests/features.py` is the file the retarget changed least, main's 396-line
  #2065 block and this branch's 331-line block sitting in disjoint regions of
  it, and the one check that does fail is measured at this head's own merge base
  by the slice under `## Red checks` 4 with the identical two numbers. CI's
  `features` lane re-runs it at this head on a runner, and that is the figure a
  reviewer should take.
- The rest of `scope.run` and the four `run_always` scripts, green on this box,
  each with its own summary line — `PYTHONPATH=tests/hastub python3
  tests/<name>.py` or `node tests/<name>.mjs` at this head (Python 3.14.7 from
  `$HOME/.local/state/hpo/venv-ci/bin` for the scripts that need it):
  `entities.py` (`ALL
  2250 ENTITY CHECKS PASSED` — 2285 at `ff2c85753`, before the delivery row
  landed; measured at `bc0488018` too, which also reads 2250, so the row the
  delivery commit added is what moved the count, not this repair), `arch_score.py --smoke` (`ALL 257 ARCHITECTURE
  SCORE CHECKS PASSED`), `arch_score_head.py` (`ALL 15 ARCHITECTURE SCORE HEAD
  CHECKS PASSED`), `config_flow_steps.py` (`ALL 499 checks PASSED`), `doc_claims.py`
  (`ALL 160 checks PASSED`), `typing_ruler.py` (`ALL 11 typing-ruler source
  checks PASSED`), `guard_pins.py` (`ALL 50 GUARD PIN CHECKS PASSED`),
  `manual_plan.py` (`ALL 129 manual plan checks PASSED`), `debug_collect.py`
  (`ALL 64 DEBUG COLLECT CHECKS PASSED`), `block_duty.py` (`ALL 46 BLOCK DUTY
  CHECKS PASSED`), `wood_advisor.py` (`ALL 7 wood-advisor checks PASSED`),
  `deployment_shape.py` (`ALL DEPLOYMENT SHAPE CHECKS PASSED`),
  `solar_alignment.py`, `edge.py` (`ALL EDGE CASES PASS`), `validate.py` (`NO
  ISSUES`), `finite_boundary.py` (`ALL 84 FINITE BOUNDARY CHECKS PASSED`),
  `layout.py` (`layout
  self-test: ok`, `run_always`), `closure.py selftest` (`ALL 57 closure shrink
  pins PASSED`, `run_always`), `md_tables.mjs`
  (`doc_orphaned_table_rows=0`, `doc_misrendered_lines=0`), `plan_view.py`
  (`plan reason codes, price provenance and slot energy OK`), `card.mjs` (`ALL
  CARD CHECKS PASSED`) and `card_drift.mjs` (`card_drift: identical in all 40
  states`). `harness_headers.py` at this head, under the 3.14 venv:
  `ALL 109 HARNESS HEADER CHECKS PASSED` — the twelve failures the previous
  head reported were the box's load, and running it under the 3.11 system
  python reddens thirteen instead (a SyntaxError in one harness the older
  interpreter cannot parse), so the venv is part of the command.
  `boost_drift_replay.py` (`ALL 46 BOOST DRIFT CHECKS PASSED`) — it needed the
  full run under the 3.14 venv on this loaded box, and completed.
- The `## Architecture score` gate read by its own tool: `python3
  tools/audit/archscore/gate.py --base 7cd5a588cbbb --head HEAD --body
  <BODY.md>` exits 0 and prints `… coord_footprint 2586 -> 2591 … PASS`, so the
  section above satisfies the required check rather than merely naming the
  metric.
- LEFT TO CI, under the owner's 2026-10-07 ruling that heavy scripts run there
  and seats cite check-runs: `stress.py` (which also holds the gate lease, and
  this seat never took it by hand), `optimality.py`, `golden.py`,
  `backtest.py`, and `arch_score.py`'s full corpus (the planted cases measured
  against the pin; its `--smoke` arm, which is what proves every case still
  applies, ran locally and is a figure above). All are named in `scope.run`;
  `arch_score.py`'s planted corpus is unaffected by this diff because the cases
  apply to the PIN — `tests/arch_score.py`'s own smoke arm calls
  `cases.extract_pin`, and the dedupe this branch lands is the corpus's
  `G2_dedupe` control, whose anchors live in the pinned copy.

## Architecture score

`PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff
origin/main` at this head reads `Architecture score: dS -0.0028 WORSENS
(inadmissible: coord_footprint 2586->2591)`. One metric rises. The
`arch-score` required check and the `## Architecture score` rule that answers a
rise both landed on `main` after this branch's merge base, in #2068
(`.github/workflows/arch-score.yml`, `tools/audit/archscore/gate.py`), so this
section is written to that rule rather than to the merge base's template, which
called the command optional and report-only.

- `coord_footprint` 2586 -> 2591: the metric counts logic statements in the coordinator class plus every module-level function handed it, and this branch hands it two, `_replay_interval` and `_interval_measured_heat_kw`.
  The first is a dedupe, and the metric's own docstring says an Extract Method or a dedupe is not growth because plumbing is not counted: the two learners' identical replay blocks became one helper, and the calls that replaced them are delegations. The rise is the second function, which is a decision that did not exist at any price before this branch — whether the interval a learner replays may be spoken for by a meter at all: a reading exists, the plan gave the interval to space heating, and nothing else refuses it. That decision is the feature, and the net +4 is what it costs in this metric's units.
  The fifth statement is the repair's own annotation (`2b8fdf844`): `_plumbing`
  in `tools/audit/archscore/metrics/footprint.py` excludes an `ast.Assign`
  whose value is a simple attribute -- which `heat_kw = coord._flow_bias
  .heat_output_kw` was -- but not the `ast.AnnAssign` that declaring the local's
  type makes of it, so the typed line counts. The alternative that keeps 2590,
  `return float(heat_kw)`, re-keys the bot's RETURN_DEL pin -- the ledger key
  digests the line's text, and `ci-autofix.md` forbids duplicating a bot that
  has already acted -- and would open a fresh unpinned site at this head, so
  one counted statement is the cheaper of the two repairs on every axis but
  this metric's, and on this one by exactly one unit. This seat did not decompose the +4 per function; `score.py --diff` prints the pair and the metric's rule, and a reviewer who wants the split can drive `archscore.metrics.footprint` over the two trees.
  The same change moves all three of `tests/structure.py`'s rows DOWN: `duplication_copies` 38 → 37 (the clone pair the helper absorbs), `max_class_loc` 8818 → 8795 (the two copies left the measured class span, the helper being module-level) and `seam_cut_total` 762 → 760 (the `_current_weather` edge and the `_thermal_model` read each existed twice and now exist once, against the one new learning→core edge the interval rule adds). So the feature's four logic statements are bought with 23 lines of class span, one counted clone and two seam crossings, and no budget row and no other gate metric moves; the fifth is the annotation, priced above.
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
4. **Not this branch's, and not this box's tree — a known class with a seat on
   it.** The fourth of those failures, and the only one still failing at this
   head (`1 of 3938 FEATURE CHECKS FAILED`), is `R9-F2.1 P3: the shipped storage
   plan is no worse on its own objective than the half-price floor's plan refined
   under it [shipped 110.4366, seeded with the half-price plan 110.1297]`, a
   solver-objective comparison. Measured at both ends of this branch rather than
   argued: that check's own block (the R9-F2.1 section of `tests/features.py`,
   sliced out and driven standalone) run inside a `git archive 23d354970` copy of
   the merge base prints the identical FAIL with the identical two numbers, and
   `tests/env_drift.py` — the standing instrument for exactly this question,
   which compares this tree against `origin/main` in one environment because
   solver floats are not bit-stable across BLAS builds — reports no drift on this
   head. A one-off scratch probe drove both zone steps over a grid of powers,
   step lengths, external heats, humidities and a throttling and a non-throttling
   valve at both trees and compared every `repr` of every resulting state:
   identical, so no solver objective can differ between them. The orchestrator
   independently confirms the class: `R9-F2.1 P3` is BLAS-kernel-red at `main` on
   this box, group **R9-RC-BLAS-KERNEL-RED** has an opus seat on it, and the
   R9-DBG-2 lane was refused by the same check. Per that instruction this seat
   did not repair it and weakened nothing. The check is its own detector and it
   fires at the base, so this is not a red this branch turned and
   `defect-root-cause.md`'s cheaper-detector question has no purchase on it. No
   pull request is open on this head yet, so there are no check-runs to cite;
   CI's `features` lane on the runner is the authority once the orchestrator
   pushes, and this box is not it — the recorded route for a green
   `features`/`optimality` locally is the hpo-ci Linux container with its
   Sandybridge pin.
5. **`field coverage` refused in the orchestrator's `app_push.sh` run and does
   not reproduce here.** That run printed `REFUSE field coverage — FIELD COVERAGE
   REFUSED: a BLIND field, a DEAD entry or a REFUSED run above` and
   `PRE-PR: f9809c06a 000000000010000000000000`, while this seat's runs at the
   same commit printed an all-zero flag word — so the difference was the tree or
   the environment, not the body, and the retarget was the answer to the tree
   half of it. Re-run at this head, directly rather than through `prepr.sh` so
   the detail survives: `node tools/policy/field_coverage.mjs` → rc=0,
   `RESULT read=63 ignored=25 declared_none=34 blind=0 dead=0 refused=0
   runs=139 seconds=116.3`, `FIELD COVERAGE ok`. Not reproduced, so not
   diagnosed; the one candidate this seat can name from the tool's own rule is a
   transient — a perturbed arm that *errors* is a refusal, and only the ruleset
   arm's LOAD may skip, so a `gh api` refusal under the shared quota mid-run
   reads as `refused=1` and nothing else. The reason the orchestrator's log
   carried only the summary line is `prepr.sh` itself: step 3f3 writes the tool's
   whole output to `/tmp/prepr-fc.$$`, prints `tail -1` of it as the step line,
   and `rm -f`s the file on the next line, so the three causes the refusal names
   are exactly the three things the seat cannot then tell apart (`## Friction`).
6. **`typing`, red at `bc0488018` and still red at `72cfb1d07` -- this branch's,
   and fixed in this head.** The CI census read `FAIL errors did not grow
   [recorded 0, measured 1 (+1)]` and `FAIL by_code[no-any-return] did not grow
   [recorded 0, measured 1 (+1)]`, the module `coordinator.py 1`: the new
   `_interval_measured_heat_kw` declares `-> float | None` and returned
   `heat_kw`, inferred `Any` because it is read off `coord: Any` -- mypy
   `--strict`'s `no-any-return`. Reproduced locally before repairing it:
   the pinned toolchain the job itself installs (mypy 2.3.1 /
   homeassistant-stubs 2026.9.3, in a venv that already existed on this box)
   printed `coordinator.py:830: error: Returning Any from function declared to
   return "float | None" [no-any-return]`. The fix is one line, `2b8fdf844`:
   the local is declared `heat_kw: float | None = coord._flow_bias
   .heat_output_kw` -- the field's own type (`flow_lift.py`'s `heat_output_kw:
   float | None`), so the return is typed and the census returns to 0
   (`ALL 9 typing-ruler checks PASSED` under `--mypy`, the figure under
   `## Figures`). No budget was touched: the honest repair is the annotation,
   not an entry in a census capped at 0. **The cheaper detector is the same
   census run locally, before the push**: it cost ~70 s against a CI round trip
   plus a review round; its standing cost is one pinned venv per seat and ~70 s
   per push, and the finding is that the authoring seat did not run it -- the
   check itself is the cheapest detector that exists, and no new mechanism is
   owed.
7. **`mutation`, red at `bc0488018` -- this branch's, and repaired by the bot
   whose lane it is.** The check refused `4614 unpinned site(s) against 4608 at
   the ratchet base d3dbf2c3f, 7 of them added by this diff`:
   `coordinator.py:828 CMP_BOUND*2`, `coordinator.py:828 GUARD_OFF`,
   `coordinator.py:830 RETURN_DEL`, `coordinator.py:5029 GUARD_OFF`,
   `coordinator.py:5184 GUARD_OFF` and `thermal_model.py:2604 CLAMP_DROP`.
   `ci-autofix.md` names unpinned sites as `mutation-autofix`'s to repair, so
   this seat waited for the bot commit and did not duplicate it: `72cfb1d07`
   (`ci: pin killed mutants`) landed the six ledger files driving all seven
   sites to pinned, each `killed_by tests/features.py` -- the same driver and
   checks the branch's own probe had measured (`m_veto` 1, `m_bound_dhw` 4,
   `m_bound_space` 1, `m_veto_tail_del` 4, `m_guard_off_house` 1,
   `m_guard_off_lower` 1), which is why the bot's pins and the probe's kill
   table agree site for site. The seventh site this diff adds,
   `_replay_interval`'s except-arm `return None`, is equivalent and carries its
   written triage row, not a pin (`## Unpinned sites`). Read back at this head
   through the counting instrument: `mutation_table.py --list RETURN_DEL`
   prints `pinned coordinator.py:830` and `pinned coordinator.py:872`,
   `LIST RETURN_DEL: 1171 site(s) in 71 file(s), 820 unpinned, ratcheted`
   (821 before the pins), and the table check itself prints no `ADDED UNPINNED`
   line. **The cheaper detector is the `mutation` job plus its own autofix
   lane**: the class is repaired mechanically, at the push, with no seat
   involvement, and that is the standing detector; none cheaper exists and
   none is owed.
8. **`pr-contract`, red at `bc0488018` -- the same two reds, unnamed.** Its log
   carries exactly two refusals about the body -- `check 'mutation' is red and
   '## Red checks' does not name it` and the same for `typing` -- and the
   repair is this body: items 6 and 7 above name both checks and answer the
   cheaper-detector question `defect-root-cause.md`'s second trigger asks. The
   pre-flight's `'Closes #2016' ... not in the intended list` line is the
   local invocation's argument list, not a CI refusal; closing #2016 is this
   PR's disposition of that issue and stands.


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
- `defect-root-cause`: `cost`: `prepr.sh` step 3f3 runs
  `tools/policy/field_coverage.mjs` into `/tmp/prepr-fc.$$`, prints `tail -1` of
  it as the step line, and `rm -f`s the file on the next line. When the step
  refuses, its own message names three causes — "a BLIND field, a DEAD entry or
  a REFUSED run above" — and "above" is the file it just deleted, so the seat
  must know to re-run the tool by hand (116 s, 139 perturbed runs, and the
  ruleset arm needs `gh api`) to learn which of the three fired. The orchestrator's
  `app_push.sh` refusal on this branch produced exactly that one-line summary and
  nothing else. Keeping the file, or printing the `BLIND`/`DEAD`/`REFUSED` lines
  beside the summary, costs one line of `prepr.sh`.
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

Re-derived at this head, not carried: the site keys, the count and the
composition all move with the tree, and a merge moves the line numbers of every
site in a file it touched. Both directions of the ledger are read, because
#2073 taught `ci_predict.py` the backward one:

    PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main

printed, at the previous head `bc0488018`, `CI PREDICT: 6 unpinned site(s) the
diff adds -- a warning; the body owes each a line under ## Unpinned sites` and
then `CI PREDICT: no closures or fast red predicted against 7cd5a588cbbb`, with
**no `STALE PIN` line at all**. At this head it prints only the second line:
the six sites are the bot's pins now (`72cfb1d07`, `ci: pin killed mutants`),
so the diff adds none, and not one of the base's pins went stale under this
branch. The seventh site this diff adds,
`_replay_interval`'s `except`-arm `return None`, is equivalent and carries its
triage row instead, so it never listed.

A report reaching this seat described eleven sites at an earlier merged head,
with `_coarsen`'s "pre-existing shifted" entries dropping out and
`_without_private_ids` contributing four of its own. Neither name exists
anywhere in `origin/main`'s tree or in this branch's —
`git grep -lE "_without_private_ids|pre-existing shifted" origin/main` and the
same pattern over the working tree both print nothing — and no instrument here
prints eleven at either head, so that composition could not be reproduced and is
not carried. What the instruments print at this head is what follows, each site
with its own reason.

Seven sites the diff added, six killable and one equivalent. The six are now
**pinned, by the bot and not by this seat**: `mutation-autofix` committed
`72cfb1d07` (`ci: pin killed mutants`) from CI's own measurement, and this seat
waited for that commit and merged it rather than duplicating it
(`ci-autofix.md`). The driver and the killing check the bot's pins record are
the same ones the probe measured locally by its own variant of the same
mutation:

- `custom_components/heatpump_optimizer/coordinator.py:828 GUARD_OFF` — the
  interval predicate's guard, in `_interval_measured_heat_kw`. Pinned by
  `mutation-autofix` at `72cfb1d07`; driver `tests/features.py`, the refusing-arms check,
  measured locally as `m_veto` (1 failing check).
- `custom_components/heatpump_optimizer/coordinator.py:828 CMP_BOUND*2` — the
  same line's two comparisons, one site each. Pinned by `mutation-autofix` at
  `72cfb1d07`;
  driver `tests/features.py`, the planted arms for the `dhw_kw` bound
  (`m_bound_dhw`, 4) and the nothing-commanded arm for the `space_kw` bound
  (`m_bound_space`, 1).
- `custom_components/heatpump_optimizer/coordinator.py:830 RETURN_DEL` — that
  function's tail. Pinned by `mutation-autofix` at `72cfb1d07`; driver
  `tests/features.py`, the
  three checks that assert a value does arrive (`m_veto_tail_del`, 4).
- `custom_components/heatpump_optimizer/coordinator.py:5029 GUARD_OFF` and
  `custom_components/heatpump_optimizer/coordinator.py:5184 GUARD_OFF` — the two
  learners' `if predicted_state is None:` guards, which are the pair the
  extraction introduced. Pinned by `mutation-autofix` at `72cfb1d07`; driver
  `tests/features.py`, "a replay that raises costs the sample and nothing else",
  which drives `_t2_raise_model` on each learner (`m_guard_off_house`,
  `m_guard_off_lower`, 1 each).
- `custom_components/heatpump_optimizer/thermal_model.py:2604 CLAMP_DROP` — the
  `max(0.0, external_heat_kw)` clamp the base carried on this line, re-digested
  because the line's left operand is now named `pump_heat_kw`. It was unpinned
  at the base too: no `_simulate_step_single` row exists under
  `tests/mutation_ledger/killed_by/thermal_model.py/` or
  `survivor_triage/thermal_model.py/`, so one anchor retired and one was added
  and the inventory count does not grow from it. Nothing in this diff reaches
  it — no check here passes a negative `external_heat_kw` — so it was the one
  site a driver might have left alive; the bot's commit answers that question:
  `ThermalModel._simulate_step_single.CLAMP_DROP.3faedba0.json`, `killed_by
  tests/features.py`, so a driver did kill it and the anchor the line's
  re-naming retired is replaced at this head.
- **The triaged equivalent, which no longer lists**:
  `custom_components/heatpump_optimizer/coordinator.py:872 RETURN_DEL` — the
  ledger key is a content anchor, `FILE:SCOPE KIND DIGEST`
  (`custom_components/heatpump_optimizer/coordinator.py:_replay_interval
  RETURN_DEL d7923b87`), so it survived both merges and both line shifts.
  **Written triage, verdict `equivalent`**, landed as
  `tests/mutation_ledger/survivor_triage/coordinator.py/_replay_interval.RETURN_DEL.d7923b87.json`:
  the statement is the last one in `_replay_interval`'s `except` arm, so
  replacing it with `pass` lets the function fall off its own end and return the
  same `None`. Measured rather than argued — the probe's `m_except_return_del`
  variant applies exactly that replacement and the block reports
  `failing_checks=0`, against 1 to 4 for the eleven other variants, two of which
  (`m_guard_off_house`, `m_guard_off_lower`) reach that same arm through
  `_t2_raise_model`.

Read back through the instrument that counts the inventory rather than by the
file's existence:

    PYTHONPATH=tests/hastub python3 tests/mutation_table.py --list RETURN_DEL

prints `pinned custom_components/heatpump_optimizer/coordinator.py:830
RETURN_DEL: pass` and `pinned
custom_components/heatpump_optimizer/coordinator.py:872 RETURN_DEL: pass`, and
closes `LIST RETURN_DEL: 1171 site(s) in 71 file(s), 820 unpinned, ratcheted`
— 830's pin is the bot's (`RETURN_DEL.0b52bd72.json`, `killed_by
tests/features.py`) and its key digests the line's text, which is why the
typing annotation kept `return heat_kw` byte-identical: a `float()` at that
return would have re-keyed the site and unpinned it again.

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


