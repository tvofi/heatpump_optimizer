A 750 L buffer tank behind a manual mixing valve is a store in the two-zone
model and nothing at all in the single-zone one. The single-zone step had no
valve branch — the merge base's own docstring says the `valve_target` argument
"is accepted and ignored there" — and the terminal cost's store credit was
nested inside the two-zone branch, while `config_flow` offers
`CONF_BUFFER_TANK_VOLUME` to every install with no `when=` gate. So an install
with a valve and a tank, and zoning off (the default), planned exactly as if no
tank existed: the buffer plan was byte-identical to the no-buffer plan and the
tank never left its start temperature.

This models the tank in the single-zone step: the valve throttles the flow to
the commanded target, the tank supplies the slab within its energy bound,
charging stops at `buffer_max_temp` and books what it refuses, the COP is priced
at the tank's own temperature, the Euler stability law carries the tank's own
row, and the terminal cost credits a valved store in either zoning. The
two-zone arithmetic is unchanged (its arm reads bit-identical figures).

It also carries the group's root-cause work: process state (c), and a census
that drives the tank's three live capabilities in **every** value of the zoning
domain, registered in `tests/entities.py`'s `_P2_CENSUSES`.

The commits before the merge are what let the above land under the ratchets.
The store's physics pushed `ThermalModel` past its class budget and left one
clone over `duplication_copies`; merging the batch's copies into module helpers
paid both but put extra calls into the sub-step loop, which the production-call
channel priced over its 1.05x allowance on an unchanged plan, so that attempt
is discarded. The payment instead moves the scalar two-zone valved delivery
verbatim into `_valve_two_zone_delivery` (one call per scalar step) and has the
batch's single-zone store block call `_single_valve_rates` rather than restate
it. The moved law first read too many scalars, which put one function over the
ten-parameter guard (the score read WORSENS); it now takes the step's own
`state` and reads `p.radiator_power_fraction` and `_buffer_capacity(p)`, so it
reads ten and the score is NULL. The price is one `_buffer_capacity` call per
two-zone valved step, which moved the judged families to 1.028x/1.030x against
the 1.05x allowance.

Fix review 1 blocked `fa6eb482b` class-open: the savings reference
(`_compute_baseline_power`) sized the pump to the emitters' need as if the step
delivered straight to them. Behind a valve the step charges the tank and the
valve draws from it at the curve, so whenever the need outran the curve (a
night setback's recovery) the reference charged its tank to `buffer_max_temp`,
paid for the refused heat, and booked it as savings: single-zone 27.79 kWh
refused, `predicted_savings` 0.74 -> 32.32 on the finder's flat day; the
two-zone reference had the same blindness at the base (14.92 kWh against the
unvalved 9.00). This head models the tank in the reference the way the step
does: `thermal_model.valve_charge_demand` inverts the step's own valve draw law
(the pump replaces what the circuits draw at the tank's present temperature
plus its standing loss, and moves the tank to the lowest temperature whose
draw meets the need, never past the curve, nor `buffer_max_temp` behind a
direct slab; no need idles the pump); `optimizer._thermostat_demand` routes
both zonings through it behind a throttling valve (the step's own predicate,
`mixing_valve.is_throttling`), and `_reference_cop` prices the draw at the
tank's flow temperature as both steps do. Unvalved installs are unchanged
(the finder harness's 16 no-buffer arms are byte-identical to the base).

Alternatives considered: (a) settle the reference's refused heat afterwards,
subtracting it from the baseline cost: rejected, it keeps a reference that
charges stored heat it never uses and still misreports the stored-energy gap;
(b) gate the reference on `buffer_is_store` instead of `is_throttling`:
rejected, the step routes heat through the tank behind any valve whatever the
volume, so that gate would leave the 35 L valved tank's reference blind;
(c) a per-zoning copy of the valve branch: it was the first cut and read
`duplication_copies` 35 -> 36 in `archscore`, so one router owns it.

Closes #2500

Part of #2499. #2712 fixed that issue's slab/UA-estimate half and carried its
plan-versus-relaxed-DP residual here. This branch measures the residual,
confirms it survives the flat-price null, and carries it forward (below) rather
than fixed, so #2499 stays open on that residual.

## Head

`12510c484f3bde0080d97d692ce14321d6da6bf5` merges the authored code head `e41708750fc50c1da7cc302041641a96dcdde5a0` and then merges origin/main `6349205b6` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`80ddb0554d6a48a7a317e137b010cbbce0447cca` merges the authored code head `e41708750fc50c1da7cc302041641a96dcdde5a0` and then merges origin/main `2b274fe06` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`e41708750fc50c1da7cc302041641a96dcdde5a0` (fixer seat, round 10, fix review 1 rework) is the
authored code head: a merge of `origin/main` `aaf8af512` into `baff727d1`, which
is 19 commits over the reviewed head `fa6eb482b` (`git rev-list --count
fa6eb482b..baff727d1`). `update_pr.sh` stopped on `tests/golden/claimed_drift.txt`
(`CONFLICTING CLAIMS: both sides rewrote the claim list`: main added
R10-HOUSE-GRADE's five coord claims); the resolution is main's file with this
branch's six suspensions applied and its note and nine claims appended, no
other line changed; every other file merged clean (`tests/closures.json` by its
driver). Main's side touches neither `optimizer.py`, `thermal_model.py` nor
`tests/structure_budgets.json` (`git diff --stat 07295d4ea aaf8af512 --` those
paths prints nothing); after the merge `tests/structure.py` reads `STRUCTURE
RATCHET PASSED` and the rework's `tests/features.py` block `ALL 12 FEATURES
BLOCK PASSED`. Figures headed `at baff727d1` below were taken before the merge.
First the failing test (`f7368ec86`), then the fix (`a0cfb763e`), then checks
and simplifications each mutation run demanded, the router (`744d6c3a3`) and
its `class_excess_loc` re-record (`d73b2568c`), the golden claims
(`f5b03191c`, `5e9915032`, `baff727d1`), and the stale-pin deletion
(`8a05c3515`). Every
figure under `## Figures` headed `at baff727d1` was re-taken at this head;
everything else is as the notes below say.

`fa6eb482bcaf1900ad3f86b994e31e8731f69c62` merges the authored code head `a5f40d84c407c90fbaf51cf6de6b14c8e062b765` and then merges origin/main `07295d4ea` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`a5f40d84c407c90fbaf51cf6de6b14c8e062b765` (fixer seat, round 10) is four commits over the previous head `fc841f51d88b0dbae35684be00f4012d63059b23` (`ci: pin killed mutants`):

- `2aa7f2d9910ec27d228e117285caf1dc42b6326b`, a merge whose parents are `fc841f51d` and `origin/main` `e8cb7e68302b1d350bb8219fea99e911170af030` (`git log -1 --format=%P 2aa7f2d99`). GitHub read the head `DIRTY`; `git merge-tree --write-tree origin/main fc841f51d` with this checkout's drivers exits 0 and prints only `LEDGER-MERGE: resolved tests/structure_budgets.json` (`class_excess_loc: 18047 + both deltas = 17996`) and `LEDGER-MERGE: resolved tests/closures.json` (`inert_reads.tests/harness_headers.py: merged as a set (900 entries)`), so the conflict is the two driver files GitHub's own merge cannot resolve, and the merge is that driver output, no hand resolution. The base is now `e8cb7e683` (`git merge-base origin/main HEAD`); the reviewed range is `git diff --shortstat e8cb7e683...55bbe8b62`, one more file at `a5f40d84c`: 40 files, 1161 insertions, 176 deletions.
- `bcffa264969a488419fa38fd94eea890ab801cd8`: `ThermalModel._substeps_and_loss`'s single-zone valved row read `c_buf = p.buffer_tank_thermal_mass; if c_buf < 1e-6: c_buf = 0.04`, a fourth inline copy of the fallback `_buffer_capacity` owns, and that copy carried two survivors (`_substeps_and_loss` CMP_BOUND and GUARD_OFF at `e26455a8#2`); it now reads `c_buf = _buffer_capacity(p)`, the same expression. `_single_valve_rates`'s `dT_cap = np.maximum(0.0, p.buffer_max_temp - T_buf) / max(dt_hours, 1e-6)` held a killed clamp and a surviving divisor floor under one ledger anchor, so any triage of the floor would have covered the clamp (fixer step 14); it is now `headroom_k = np.maximum(...)` then `dT_cap = headroom_k / max(dt_hours, 1e-6)`, the same operations in the same order.
- `55bbe8b622500b12919ddc47397e59c40a25a57d`: three `survivor_triage` rows (verdict `equivalent`) for the survivors the pin drive left that no reachable input can kill; `## Unpinned sites` names each.
- `a5f40d84c407c90fbaf51cf6de6b14c8e062b765`: `tests/structure.py --record`, `class_excess_loc` 17996 -> 17994 (the two lines `bcffa2649` deleted from the class), `recorded_at` -> `e8cb7e683`.

Everything below this note's other notes was measured at `8d0a1c3f7` (or the heads it names) and is not re-taken here except where `## Figures` says `at a5f40d84c`.

`cd731ff0d1ec231db24054d197c5a86d0f9d5757` merges origin/main `6eb552157` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head, and then adds one commit containing only this PR's own row, `dev/programme/delivery/2887.md`.

`52783d67715be8304d5b4bde75bcd3cdad789350` merges origin/main `4db1d3e28` into the authored code head `8d0a1c3f7f699f94f1da93ef4e0c29c1f00cb22c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`8d0a1c3f7f699f94f1da93ef4e0c29c1f00cb22c`, a merge whose parents are the
branch's `5c01e40658af339371b22b1b7c141ae3e539deb9` and `origin/main`'s
`67178dc6a589cf95d2ce7cff36d8bbf17343e8dc` (`git log -1 --format=%P HEAD`).
The base is `67178dc6a` itself (`git merge-base origin/main HEAD`), so the
reviewed range is the branch's own 15 commits and 14 changed files
(`git rev-list --count 67178dc6a..8d0a1c3f7`; `git diff --stat
67178dc6a...8d0a1c3f7`: 1008 insertions, 191 deletions).

The one conflict is `dev/audit/config/bugclasses.json` — this branch's
`R10-RCA-BUFFER-STORE` class against main's `R10-N-vocabulary-drift` row;
`git merge-tree --write-tree 5c01e4065 67178dc6a` names that path and no
other, and the resolution keeps both classes (the file at this head carries the
`R10-RCA-BUFFER-STORE` and `R10-N-vocabulary-drift` class entries, with main's
sibling rows intact), which is the union `tools/merge/ledger_merge.py` writes
for that file.
`fix-review.md` step 13 makes a conflict on any path but the two claim files
the reader's to block on, so the resolution is recorded here rather than left to
a merge-state field. `tests/structure_budgets.json` merged through the same
driver to `class_excess_loc` 17999 — the merge base's 18067 plus both sides'
deltas (−48 on the branch, −20 on main) — and `tests/structure.py` measures the
merged tree at exactly 17999, with `functions_cc_over_15` 27 and `recorded_at`
524c1896b. `tests/closures.json` merged as a set under that driver (main's added
stub scripts land beside the branch's rows, e.g.
`tests/hastub/homeassistant/components/sensor.py`); both are re-measured below.

The merge is committed twice,
`78f65274e5b0a3f91e89463ceaf7198370fe3fe6` on
`refs/heads/fix/r10-buffer-store` and `8d0a1c3f7` on the handoff ref, and the
trees are identical (`git diff 78f65274e 8d0a1c3f7` prints nothing). The
branch's pre-merge commit `5c01e4065` is the structure budget's re-record
(`functions_cc_over_15` 28 → 27), a data row `tests/structure.py` reads.

`custom_components/heatpump_optimizer/thermal_model.py` is byte-identical at the
pre-merge head `0db6d58` and this head (both
`800921b3a5da0fc85dd3f9994c408657b3bd877a`), so the store and valve code is
unchanged by the merge; main's `optimizer.py` changes are re-measured in the
figures below. Every figure was re-taken over `67178dc6a...8d0a1c3f7`.

## Mutation proof

Fix review 1 rework, at `baff727d1`: seventeen runs of the block this rework
adds to `tests/features.py` (from `_RT_TARGETS` to the valve hold schedule
section) through `tools/audit/seat/features_block.py`, each on a `git archive`
of the head with one mutant applied (`mutants.py` in the seat's evidence):
**16 KILLED, 0 SURVIVED; the null (no mutant) passes**.

| mutant | first check that goes red |
|---|---|
| M1 router's valve guard off (`if False:`) | `single-zone: the savings reference never charges its valved tank into the cap` (refused 27.79 kWh, tank 70.0 C) and both zonings' cost checks |
| M2 router's unvalved tank-loss term off | `two-zone, no valve: the reference replaces the tank's standing loss` |
| M3 kinks not capped at `buffer_max_temp` | `behind a direct slab the tank law stops at buffer_max_temp` (tank NaN) |
| M4 `_reference_cop` flow-blind | `the valved reference prices its draw at the step's own tank-flow COP` (1 kW made 1.8210 kW; COP 2.8875) |
| M5 idle guard off | `the tank law idles the pump when the emitters need nothing` |
| M5b idle bound `<=` -> `<` | the same check |
| M6 charge term dropped | both zonings' `a valved reference costs the unvalved one plus the tank's loss`, `the tank law charges to the temperature whose draw is the need` |
| M7 goal pinned at the top kink | `the tank law charges to the temperature whose draw is the need` |
| M8 `headroom_k` clamp dropped (`thermal_model.py:1756`) | `single-zone valve: a tank above buffer_max_temp cools at its physical rate` (refused 14.094 kW) |
| M9 circuit draw floor dropped | `the tank law charges to the temperature whose draw is the need` (22 C tank arm) |
| M10 circuit draw not capped at the curve | the same family |
| M11 zoning guard off | the two-zone checks |
| M12 single-zone circuit list deleted | every single-zone check |
| M16 two-zone demand drops `q_upper` | `two-zone valve: the reference charges for the radiators' need over a hot slab` (0.000 kW) |
| M17 router always single-zone | the two-zone checks |

M8 is the site the body used to say `tests/features.py` kills and fix review 1
found it did not at `fa6eb482b`: it now does, through the new check (and
`mutation-autofix` pins the anchor).

Eleven mutants, each applied to the production tree and run against the group
probe (`tests/features.py`'s four `_grad_parity` cells plus the store section,
the new batch twin included) at this head (a `git archive` copy of `8d0a1c3f7`
whose `thermal_model.py` and `optimizer.py` hash identically to the head's —
`ba192d7e…` and `330a8830…`; `thermal_model.py` is also byte-identical to
`0db6d58` where ten of the eleven apply, and M1's `optimizer.py` target still
matches exactly once): **11 KILLED, 0 SURVIVED**, each by the checks named here,
pasted from the run.

| mutant | checks that go red |
|---|---|
| M1 terminal credit two-zone only | `single-zone: the terminal cost credits a valved store tank`; `zoned store census: the terminal cost credits the tank in every zoning (#2500)` (single-zone 0.0000, two-zone -17.3299) |
| M2 scalar valve branch off | 9 checks: both `single-zone with valve` parity checks, `single-zone: the valved tank is charged for the cheap night` (tank peaked at 25.0 C from 25 C), `… the tank's loss is the slab's delivery plus standing loss` (0.0000 vs 0.5039 kWh), `… the slab receives exactly what the tank delivered`, `… charging stops at buffer_max_temp` (refused 0.000 kW), `… the step prices the COP at the tank's own temperature`, and both census arms on the tank move and the cap |
| M3 batch valve branch off | both `two-zone with valve` parity checks; `batch twin: charging into buffer_max_temp matches the scalar step bit-for-bit` (all six tracks diverged) |
| M4 scalar COP ignores the tank | both `single-zone with valve` parity checks; `… the step prices the COP at the tank's own temperature` (60 C tank +2.055 K against the priced 1.348 K) |
| M5 batch COP ignores the tank | both `single-zone with valve` parity checks |
| M6 energy bound dropped | `single-zone valve: a small tank coasting one step never falls below the slab` (tank ended at -55.90 C against a 22 C slab) |
| M7 stability row blind to the tank | `… the stability count subdivides for the tank's own row` (one step 26.796 C vs 400 sub-steps 27.649 C) |
| M8 no `buffer_max_temp` clamp | `… charging stops at buffer_max_temp and books the refusal` (tank 72.41 C, refused 0.000 kW); `zoned store census: the cap books what it refuses …` |
| M9 both single-zone COP rows ignore the tank | `… the step prices the COP at the tank's own temperature` — the mutant the parity pair cannot see, because both twins agree while both are wrong |
| M10 shared energy bound dropped | `… a small tank coasting one step never falls below the slab` (tank ended at -55.90 C); the bound is one expression, `_tank_bounded_draw`, and the batch's single-zone block calls it too |
| M11 batch cap not clamped | `batch twin: charging into buffer_max_temp matches the scalar step bit-for-bit` (buffer and refused tracks diverged; peak refused 12.1085 kW past a 70 C cap) |

M11 is why the new twin check exists: the four parity cells start a 750 L tank
with charge to spare, so no step refuses heat and a defect confined to the
batch's own clamp survives every one of them. The twin drives the tank into
`buffer_max_temp` and demands bit-identity on six tracks.

The census is demonstrated per arm **and per zoning** -- a census that only
echoed the single-zone arm would pass the base/hand comparison while blind to a
regression in the two-zone path. Each plant is one zoning's path broken, the
other left live; M2, M3 and M8 reproduce three of the four plants above at this
head:

| plant | valve arm | cap arm | credit arm |
|---|---|---|---|
| C1 single-zone valve branch off | FAIL (SZ +0.0000 K) | FAIL (SZ 0.0000 kW) | ok |
| C2 two-zone step blind to the valve | FAIL (TZ +0.0000 K) | FAIL (TZ 0.0000 kW) | ok |
| C3 credit gated to two-zone only | ok | ok | FAIL (SZ 0.0000) |
| C4 credit gated to single-zone only | ok | ok | FAIL (TZ 0.0000) |

## Null control

- **Fix review 1 rework, the flat-price arm** (nothing can be stored for):
  `dev/audit/harnesses/r10_buffer_store.py reference`, the finder's cell. The
  unvalved reference is the control: it reads 8.15 kWh (single-zone) and 9.00
  (two-zone) at `fa6eb482b` and at `baff727d1`. The valved reference reads 27.19
  and 14.92 at `fa6eb482b`, 8.10 and 7.99 at `baff727d1`; its refused heat 27.79
  and 0.00 kWh at `fa6eb482b`, 0.00 and 0.00 at `baff727d1`.

- **The unmodified tree.** At `3b4180dcc` the 750 L buffer plan on a spread
  price day is **byte-identical** to its no-buffer twin (`21d0378f2f79`, cost
  22.184 each, tank rise +0.00 K) — the tank is absent, not merely under-used.
- **Flat price** (the day's mean: nothing to store for). At this head the tank
  rises **+0.00 K** in both the 750 L and the 0 L arm, so the +40.00 K on the
  spread day is arbitrage and not an artefact of the new branch. The two flat
  arms do not price identically (38.059 vs 50.457): a valve lowers the flow
  temperature to the load, a COP effect with no storage in it.
- **Accuracy, calibrated.** `accuracy` on realised == predicted reads
  `power_ratio 1.0`, `cost_error_percent 0.0` at both ends.

## Figures

At `baff727d1` (base `07295d4ea`; `origin/main` was `53c4b9cb0` at
`date -u` 2026-10-28T04:10Z):

- The finder's harness, `dev/audit/harnesses/r10_setpoint_boost.py` (sha1
  `878ce05bcd060e151dcf3631cac7109a71d7fe85`, unchanged by this PR), run
  unmodified from each tree's `git archive`: at the base `07295d4ea` the 16 buffer
  plans are byte-identical to their no-buffer twins (the finding); at
  `fa6eb482b` and at `baff727d1` none are. Its `savings` column on the 750 L cells,
  `fa6eb482b` -> `baff727d1`: spread (0.6, no DHW, set-point) 42.79 -> 8.83, flat
  (0.6, no DHW, duty) 32.32 -> 1.66, flat (1.7, no DHW, duty) 86.76 -> 2.88;
  the no-buffer twins read 8.95, 0.74 and 1.98 at all three trees. The 16
  no-buffer rows are byte-identical (`diff` of the rows) between `fa6eb482b`
  and `baff727d1`: the null.
- `dev/audit/harnesses/r10_buffer_store.py reference` (new mode; exits 1 when a
  valved reference refuses heat): rc=1 at `fa6eb482b` (`1 valved arm(s) refuse
  heat`), rc=0 at the base and at `baff727d1`. Rows as `## Null control`; savings
  single-zone 750 L 32.32 (73.6 %) at `fa6eb482b` -> 1.66 (12.7 %) at `baff727d1`
  against the unvalved 0.74 (5.6 %); two-zone 8.08 (33.5 %) -> 0.73 (5.7 %)
  against 2.17 (14.9 %).
- `r10_buffer_store.py plans 0`: spread 750 L `6736c81e1bc8` / 22.75 / 0.984 /
  +40.00 / 22.400; flat 750 L `29965f7373d6` / 23.77 / 0.319 / +0.00 / 38.409;
  the 0 L arms `21d0378f2f79` / 22.63 and `1144455deb6a` / 31.22 as before. The
  valved plans moved because the reference's energy anchors three of the space
  solve's starts. **Correction**: the flat 750 L hash at `fa6eb482b` reads
  `5d1137c8e29e` on this seat and `0c6ea1b722ec` on the reviewer's, with the
  same four figures: the hash of that cell is host-dependent, so the claim
  across hosts is the figures, not the hash.
- **Correction**: `CI PREDICT: 4 unpinned site(s)` (quoted at
  `55bbe8b62`) does not re-derive; the reviewer read 1 at `fa6eb482b` and at
  `55bbe8b62`. At `baff727d1`: `python3 tools/pr/ci_predict.py --base origin/main`
  prints `11 unpinned site(s) the diff adds`, each under `## Unpinned
  sites`.
- Seam census, the rule `git grep -n "\.simulate_step(\|compute_cop(" --
  custom_components` (every reader that drives the step or converts heat and
  electricity), dispositioned: `optimizer._thermostat_demand_single` and
  `_thermostat_demand_two_zone` and the reference's COP line, closed here;
  `optimizer._deferred_energy_cost`, already guarded (its buffer share is
  priced at the flow-derated COP, v4.0.5); `sysid._valve_drive`, deliberate
  (#1524: `q / compute_cop(outdoor)` is turned back into electrical power so
  the plant prices the lift); `optimizer._replay_end_state`,
  `away.estimate_recovery_hours`, `diagnosis._room_after`,
  `topology._advisor_replay`, `coordinator._replay_step`: drive the step with
  a given power and size nothing, so the step's own tank law applies; every
  other `compute_cop(` hit is a reading for a sensor, a learner sample or the
  terminal cost's `cop_end` beside its own `cop_buffer`, none sizing a valved
  step's power.
- Comfort, the reference's own (`comfort_probe.py`, the setback schedule of the
  new check): valved shortfall 2.74 Kh against the unvalved 1.66 (single-zone,
  scale 0.6) and 17.49 against 5.34 (scale 1.7); two-zone 2.38 / 1.83 and
  8.19 / 5.05. Behind the configured curve the reference recovers from a
  setback slower than an unvalved pump at nameplate, so it is cheaper there
  and the published savings are understated, the direction the reference's
  own wood-share comment accepts; on the finder's 1.7 set-point flat cells
  that reads `savings` -6.89 and -6.69. See `## Forward-carry`.
- `GOLDEN_MODE=drift GOLDEN_REF=07295d4ea python3 tests/golden.py`: `NO
  UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc=0, with nine valved
  fixtures claimed in `tests/golden/claimed_drift.txt` (six may-drift entries
  suspended): `baseline_cost` DOWN in eight (e.g. `valve_storage` 146.865 ->
  129.695, `valve_storage_low_target` 195.205 -> 111.103, `wood_two_tank`
  141.475 -> 120.254) and UP in `valve_upper_direct_slab` (125.709 -> 126.782);
  `valve_storage_flat_prices` and `valve_storage_low_target` move plan leaves
  too (the reference-anchored starts). No unvalved fixture moves. The same run
  without `GOLDEN_REF` compares with `origin/main`'s tip and reads `RECORD PR
  CLAIMS` on `card_claimed_drift.txt`, main's later edit (`## Red checks`).
- `tests/features.py` R9-F2.1 P3: from a 25 C tank the two-zone storage solve
  now reaches its basin without the continuation (j 110.153954 both arms,
  against 110.436632 / 110.559859 at `fa6eb482b`); the cell's tank starts at
  30 C, where the continuation separates (108.974413 against 109.715147,
  `f21_probe.py`; 35 C reads +0.118, the 25 C cells of the other weathers and
  prices +0.000365 or 0). The single-zone null arm keeps its 25 C tank.
- `python3 tests/structure.py`: `class_excess_loc` 17994 -> 17988, recorded in
  `d73b2568c` (the router replaced the class method's zoning branch); every
  other row unchanged. `python3 tools/audit/archscore/score.py --diff
  07295d4ea baff727d1`: `Architecture score: dS +0.0000 NULL`.
- `dev/audit/harnesses/r10_demand_overbook.py --one null --dp` and `--one
  owner_i01 --dp` at `e01696141` (the production code `baff727d1` carries less the
  router, which is the same arithmetic): plan_kwh 11.78 against dp_kwh 9.88,
  and 5.37 against 3.88, identical to `8d0a1c3f7`'s figures below.
- Local results, `PYTHONPATH=tests/hastub` under the CI venv: `tests/features.py` `ALL 4549 FEATURE CHECKS PASSED` and `tests/entities.py` `ALL 2467 ENTITY CHECKS PASSED` at `5e9915032` (the code this head carries; the later commits are one ledger deletion and four claim lines); `tests/structure.py` `STRUCTURE RATCHET PASSED` at `5e9915032`; the merge-base drift run above at `baff727d1`; and at `3d3bbe8a1` (the tank law before its simplifications) `tests/backtest.py`, `doc_claims.py`, `edge.py`, `finite_boundary.py`, `guard_pins.py`, `harness_headers.py`, `manual_plan.py`, `plan_view.py`, `solar_alignment.py`, `typing_ruler.py`, `validate.py` and `wood_advisor.py` rc=0. `tests/stress.py` is left to CI (`fixer.md` step 5).

At `a5f40d84c` (base `e8cb7e683`, `date -u` 2026-10-28):

- `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_buffer_store.py plans 0`, each from a `git archive` of the named tree: at `55bbe8b62` (`a5f40d84c` adds only the budget row) spread 750 L `6a546df76556` / 22.41 / 1.000 / +40.00 / 21.947, spread 0 L `21d0378f2f79` / 22.63 / 0.965 / +0.00 / 22.184, identical False; flat 750 L `5d1137c8e29e` / 23.55 / 0.321 / +0.00 / 38.059, flat 0 L `1144455deb6a` / 31.22 / 0.242 / +0.00 / 50.457. The same six lines at the previous head `fc841f51d`, so the fold and split move no plan. Null: the new base `e8cb7e683` reads the buffer plan **identical True** to the no-buffer plan on both days (`21d0378f2f79`, `1144455deb6a`), so main's merge did not give the base a store.
- `python3 tools/audit/archscore/score.py --diff e8cb7e683 55bbe8b62`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py` at `55bbe8b62`: `class_excess_loc 17994 (budget 17996, -2; not yet recorded)`, the only row moved; recorded in `a5f40d84c`.
- `python3 tools/pr/ci_predict.py --base origin/main` at `55bbe8b62`: `CI PREDICT: 4 unpinned site(s) the diff adds` and `no closures, fast, wave-script or instrument red predicted against e8cb7e68302b`.
- `python3 tests/closure.py select --diff e8cb7e683`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- Local results at `55bbe8b62` (the code that `a5f40d84c` carries; its only later change is the `tests/structure.py --record` of `class_excess_loc`): `tests/entities.py` rc=0, `tests/guard_pins.py` rc=0, `tests/finite_boundary.py` rc=0, `GOLDEN_MODE=drift tests/golden.py` rc=0 (`NO UNCLAIMED DRIFT: 56 scenario(s)`), `tests/features.py` `ALL 4537 FEATURE CHECKS PASSED` (`logs/local-features.log`). `tests/features.py` holds the check M7 named (`the stability count subdivides for the tank's own row`), the row `bcffa2649` touched.

Measured at `8d0a1c3f7` and not re-taken (the delta since is the merge of main, the fold and the split above):

- `dev/audit/harnesses/r10_buffer_store.py plans 0` — 750 L manual valve vs no
  buffer, spread and flat, at `3b4180dcc` and at this head. Base spread 750 L
  `21d0378f2f79` / 22.63 kWh / cheap-quarter 0.965 / +0.00 K / 22.184 /
  identical **True**; base flat 0 L `1144455deb6a` / 50.457 / True. Head
  spread 750 L `6a546df76556` / 22.41 / 1.000 / +40.00 / 21.947 / False; head
  spread 0 L `21d0378f2f79` / 22.63 / 0.965 / +0.00 / 22.184; head flat 750 L
  `5d1137c8e29e` / 23.55 / 0.321 / +0.00 / 38.059; head flat 0 L
  `1144455deb6a` / 31.22 / 0.242 / +0.00 / 50.457.
- `dev/audit/rca/R10-RCA-BUFFER-STORE.md` — the group's root-cause work, with
  its disclosure that the roster's `next_step` was `rca` and the brief gave it
  to the group's own fixer, so the separate-seat independence the contract asks
  for is not obtained. Cause: one fact ("is this buffer tank a store?") decided
  by two predicates — the step had no valve branch and the credit sat inside
  `if params.two_zone_enabled:` — while `_settlement_caps` priced the buffer in
  every zoning. Process state **(c)**: followed, and did not produce the
  intended result — the parity grid built three of the four zoning x valve
  cells (33 `ThermalParameters` constructions in the base's
  `tests/features.py` set `mixing_valve_mode`, 32 of them also
  `two_zone_enabled=True`), and `config_flow` has offered a buffer to every
  install since the base with no `when=` gate, so nothing moved underneath it.
  Cost test: the census costs **0.0003 s median / 0.0003 s worst** marginal in
  `tests/features.py` here (the RCA's loaded sample: **0.001 s / 0.031 s**),
  which runs once per gated pull request; the tree carries **2,338 merges** over
  `v6.7.12..v7.0.4` (`git rev-list --merges --count v6.7.12..v7.0.4`, ten tag
  intervals — the RCA divides the same count by seven) = **234 per release**, so
  **0.07 s per release** at this sample (0.23 s on the RCA's, 7.3 s on its
  worst); the defect costs **4.35 h = 15,660 s** per occurrence and the class
  carries **0.66 instances per release**, so **10,336 s per release** against
  0.07 s — about **1.5×10^5×** (4.4×10^4× on the RCA's sample, 1.4×10^3× on its
  worst). The census's domain is the zoning flag's two values, enumerated, so
  it cannot skip a slot; its three check texts are registered in
  `_P2_CENSUSES`, which refuses a vanished text (`CENSUS-MISSING`).
- The store block out of this head's `tests/features.py` (18 checks, extracted
  by text by the group's probe): **9 ok, 9 FAIL** at `3b4180dcc` (the head's
  test file against that production) and **18 ok, 0 FAIL** at this head. The
  three census readings are the same lines in both: base valve `single-zone
  +0.0000 K, two-zone +0.1973 K`; cap `single-zone 0.0000 kW, two-zone 1.5947
  kW`; credit `single-zone 0.0000, two-zone -17.3299`. At head: `+0.2744 /
  +0.1973 K`, `3.4614 / 1.5947 kW`, `-17.3299 / -17.3299`.
- The wider probe (`mutants.py`'s probe: the same block plus the four
  `_grad_parity` cells, **34 checks**) reads **25 ok, 9 FAIL** at the base and
  **34 ok, 0 FAIL** at this head.
- `dev/audit/harnesses/r10_buffer_store.py bench 5` — `optimize` wall time and
  peak RSS over 5 solves per arm on the owner shape, at the base and at this
  head in the same window: head 7.397 s median / 16.082 s worst / 89.0 MB
  against base 2.666 / 7.236 / 87.8 MB; the flat no-buffer null 2.441 / 3.144 /
  90.9 MB against 3.686 / 5.867 / 81.6 MB. The null reads **0.66x** here (the
  head faster), so this pair is dominated by machine load and is not the
  performance figure.
- The same arms in **CPU seconds**, which is the reading that does not move
  with the box's load (`benchcpu2.py`, 10 solves per arm, one process per tree,
  the same seeded price sequence at both ends). Two pairs, each end taken at
  the same moment: against the branch's own base (`3b4180dcc`) the owner arm
  **8.016 s → 22.305 s** (**×2.78**; per-solve medians 0.888 → 2.313, ×2.61),
  and against the merge base `67178dc6a` **8.587 → 22.693 s** (**×2.64**;
  medians 0.969 → 2.317, ×2.39). The flat no-buffer null reads **×1.08**
  (9.325 → 10.034; medians 0.958 → 1.018, ×1.06) and **×1.05** (9.675 → 10.171;
  medians 1.001 → 1.025, ×1.02), so the ratio is the store's and not the
  instrument's dispersion. The production-call channel
  (`stress.calls_population`): the two-zone valved families 1.028x and 1.030x
  (plans unchanged, the channel's work count `vouched 1.000x`, against the 1.05x
  allowance), every other family 1.000x, and the single-zone valved family
  3.155x raw / 1.852x vouched — it re-plans, 64 objective evaluations against
  40, and the channel classifies a re-planned family separately.
- `dev/audit/harnesses/r10_buffer_store.py accuracy` — the two fields'
  definitions read off the tree (`power_ratio` = mean(actual/predicted) over
  samples with predicted > 0.05; `cost_error_percent` = (Σpredicted −
  Σactual)/Σactual, positive when the plan over-books): calibrated `1.0 / 0.0`,
  realised 1.4× predicted `1.4 / -28.57`, plan over-books 40 % `0.714 / 40.0`.
  A mutant that flips the subtraction gives `1.4 / +28.57` and `0.714 / -40.0`
  while the calibrated null stays `0.0` — the sign convention is pinned.
- `dev/audit/harnesses/r10_demand_overbook.py --one null --dp` and
  `--one owner_i01 --dp` — the flat-price null arm and the owner-shape arm with
  the relaxed DP reference. Null (flat prices, learned scale 0.992 against a true
  1.0, 287 samples): `plan/deliv 1.205`, 12.1/10.8/11.5/14.4/15.9 kWh planned
  against 9.6/9.3/9.2/11.9/13.5 delivered, `plan_kwh 11.78` against `dp_kwh
  9.88` (**+19.2 %** learned, +20.8 % against the true-house DP), cost gap
  94.66 %/91.30 %. Owner shape (scale 0.628 against a true 0.6, 350 samples):
  `plan/deliv 1.18`, `plan_kwh 5.37` against `dp_kwh 3.88` (**+38.4 %** learned,
  +43.2 % true), cost gap 17.03 %/16.52 %. The over-booking survives the
  flat-price null, so it is demand-side, not price-chasing.

## Architecture score

Architecture score: dS +0.0000 NULL (`tools/audit/archscore/score.py --diff
e8cb7e683 55bbe8b62`; at `8d0a1c3f7` over `67178dc6a` it also read NULL). `tests/arch_score_head.py` reads **ALL 18 CHECKS
PASSED** at this head, and `tests/structure.py` reads every metric within its
budget at `8d0a1c3f7` (`class_excess_loc` 17999, `recorded_at` 524c1896b); at `a5f40d84c` the recorded table is `class_excess_loc` 17994, `recorded_at` e8cb7e683.

## Unpinned sites

- `custom_components/heatpump_optimizer/optimizer.py:508 RETURN_DEL: return q_upper + q_floor`: `_thermostat_demand_two_zone`'s return; a `pass` returns None into the router and every two-zone check raises; M16 kills the same line's sum. Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/optimizer.py:536 GUARD_OFF: if mixing_valve.is_throttling(p.mixing_valve_mode):`: the router's valve gate. Killed by M1; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/optimizer.py:544 RETURN_DEL: return need`: the router's unvalved return; None reaches `max(0.0, required_thermal - ext_i)` and every unvalved reference raises. Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1756 CLAMP_DROP: headroom_k = np.maximum(0.0, p.buffer_max_temp - T_buf)`: `_single_valve_rates`' headroom floor. Killed by M8 through `single-zone valve: a tank above buffer_max_temp cools at its physical rate`; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1772 GUARD_OFF: if not p.two_zone_enabled:`: `_valve_draw_circuits`' zoning. Killed by M11; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1777 RETURN_DEL: return [(ua, flow_set, state.slab_temperature)]`: the single-zone circuit. Killed by M12; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1792 CLAMP_DROP*2: return sum(ua * max(0.0, min(tank, top) - zone) for ua, top,`: `_circuit_draw`'s floor and curve cap. Killed by M9 and M10; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1792 RETURN_DEL: return sum(ua * max(0.0, min(tank, top) - zone) for ua, top,`: None into `np.interp` raises in every valved reference. Pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1812 CMP_BOUND: if need_kw <= 0.0:`: the idle bound. Killed by M5b (a zero need behind a tank colder than the slab); pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1812 GUARD_OFF: if need_kw <= 0.0:`: the idle guard. Killed by M5; pinned by `mutation-autofix`.
- `custom_components/heatpump_optimizer/thermal_model.py:1824 CLAMP_DROP: min(t, p.buffer_max_temp) for _, top, zone in circuits for t`: the tank cap behind a direct slab. Killed by M3; pinned by `mutation-autofix`.

The pre-rework list below was taken at `8d0a1c3f7`; those sites are pinned or
triaged on this branch already (`ci_predict` no longer lists them).

At `a5f40d84c`, `python3 tools/pr/ci_predict.py --base origin/main` lists four
sites the diff adds unpinned (`CI PREDICT: 4 unpinned site(s) the diff adds`);
the `tests / mutation` run at `fc841f51d` (job 122542872450) refused six, of
which `bcffa2649` deleted two (the folded fallback) and split one line in two.

- `custom_components/heatpump_optimizer/thermal_model.py:1684 CMP_BOUND: return 0.04 if c_buf < 1e-6 else c_buf`: survivor triage, `equivalent`, `tests/mutation_ledger/survivor_triage/thermal_model.py/_buffer_capacity.CMP_BOUND.c7ca72ab.json`. The arms differ only at `c_buf == 1e-6` exactly; every volume writer (the `_number(10, 1500, 5, 'L')` selector, the quick-setup 500 L, the 35 L default) gives `c_buf >= 0.0116`. Survival: `mutation-pins` shard job 122440356132 at `cd731ff0d`, `1677 CMP_BOUND -- lives`.
- `custom_components/heatpump_optimizer/thermal_model.py:1727 CLAMP_DROP: / max(dt_hours, 1e-6)`: survivor triage, `equivalent`, `.../_tank_bounded_draw.CLAMP_DROP.ebabcabd.json`: dt_hours is a positive step or sub-step length in both callers. Survival: shard job 122440356297, `1720 CLAMP_DROP -- lives`.
- `custom_components/heatpump_optimizer/thermal_model.py:1756 CLAMP_DROP: headroom_k = np.maximum(0.0, p.buffer_max_temp - T_buf)`: pinned by `mutation-autofix`: the same mutant on the pre-split line was `killed by tests/features.py` (shard job 122440356131), and the split gives it an anchor of its own, so the next pin drive records it.
- `custom_components/heatpump_optimizer/thermal_model.py:1757 CLAMP_DROP: dT_cap = headroom_k / max(dt_hours, 1e-6)`: survivor triage, `equivalent`, `.../_single_valve_rates.CLAMP_DROP.31345538.json`; the same divisor floor as 1727. Survival: shard job 122440356131, `1749 CLAMP_DROP -- lives`, measured on the pre-split line, whose dropped floor is this same expression.

The 25 sites the earlier body listed at `8d0a1c3f7` are, by the same `ci_predict.py` read at `a5f40d84c`, pinned (by `mutation-autofix`'s `fc841f51d` and the rows already on main) or among the four above.

## Red checks

- **Fix review 1 rework, local reds and how each was answered**, before
  this head was pushed (no check runs at `baff727d1` yet):
  `GOLDEN_MODE=drift tests/golden.py` read `5 UNCLAIMED DRIFT(S)`, then
  `CLAIMED AND MAY-DRIFT` once claimed: the five are claimed and their
  may-drift entries suspended. A run against `origin/main`'s tip instead of the
  merge base reads `RECORD PR CLAIMS` on `card_claimed_drift.txt`, which this
  branch does not touch: main changed it after `07295d4ea`, the two-dot trap
  `CLAUDE.md` rule 3 names. `tests/features.py`'s wood-share reference check
  and R9-F2.1 P3 (both answered under `## Figures` and in the commits) and
  `ci_predict`'s `STALE PIN` on `_thermostat_demand_two_zone RETURN_DEL
  04d776b6` (deleted, `8a05c3515`); the first drift run's tail showed five of
  its nine drifts and the claims were written from it, so four went in a
  second commit (`baff727d1`). Cheaper detector: none cheaper than the
  ones that ran; each is the local run of the check CI would run, at seconds
  to minutes on a seat.
- `tests/optimality.py` `one|summer_negative|shoulder` reads the same at
  `baff727d1` as at `8d0a1c3f7` (this host's arm64 basin, below).
Reds on this pull request's earlier heads, read with `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` (no check run exists at `a5f40d84c` until its push; the reviewer reads that head's own rollup).

- `tests / mutation` — red at `fc841f51d` (run 40605154960, job 122542872450): `MUTATION TABLE REFUSED -- 3813 unpinned site(s) against 3814 at the ratchet base 6eb552157 ..., 6 of them added by this diff`, after `mutation-autofix` had pinned the killed ones (`fc841f51d`, `ci: pin killed mutants`); red earlier at `cd731ff0d` (job 122439826301) and `52783d677` (job 122405319553) on the then-unpinned sites. Answer: the six were survivors, which no tool may triage (`ci-autofix.md`). `bcffa2649` removes two by deleting a duplicate of `_buffer_capacity`'s fallback and separates a killed clamp from a surviving floor; `a5f40d84c` triages the three that no reachable input can kill; the clamp is left to `mutation-autofix`'s pin, so this check stays red at `a5f40d84c` until that bot commit (one site, `thermal_model.py:1756`). The cheaper detector exists and ran: `prepr.sh` step 6d's `ci_predict.py` named every one of the six before the PR; the cost was a body that disposed of them as "pinned by `mutation-autofix`; a survivor is equivalence" without writing the triage rows.
- `governance / instrument-self-tests` — not red at any head of this pull request: `success` at `fc841f51d` (job 122542872544) and `52783d677` (job 122405319332); `cancelled` at `cd731ff0d` (job 122439826567, run 40574874260 superseded). No answer owed; named because it was reported red.
- `prelude` — red at `cd731ff0d` (run 40574873474, job 122438486750): `FAIL run(s) [40574874260] still adding sources after 8700 s`, a wait on a sibling run that was itself later cancelled. Answer: no defect of this diff; a CI scheduling timeout with no cheaper detector at the seat.
- `pr-contract / pr-contract` and `gate` — red at `cd731ff0d` (jobs 122543135800, 122543337610; 122509599588, 122510079459): ``check `prelude` is red and `## Red checks` does not name it``. Answer: this section names it; the cheaper detector is `prepr.sh`'s step 7c, which reads the same red history and was not re-run on the bot-pushed heads.

Earlier reds, observed and answered at the heads they name:

- `tests/optimality.py` — `one|summer_negative|shoulder: a recorded claim
  still has a gap (not stale)`: claimed but the measured gap is 0.0000 %, at or
  below the bar. Answer: **this host's platform, documented at
  `tests/optimality.py:711-717`** — "CI's linux fast lane still measures ladder
  +10.55 % (obj 0.3058), though the arm64 seat reaches the basin (obj 0.2548,
  0.0000 %); the gate's platform is the one that counts, so this claim reads
  stale on arm64 only." The cell cannot be reached by this diff either:
  `_cert_inputs` builds `profiles.house(two_zone=False)`, which sets a 200 L
  tank and no `mixing_valve_mode`, so `buffer_is_store` is false and neither the
  store's physics nor the credit is live in it.
- `node tests/card.mjs` — Node's V8 heap aborts at **2047.0 MB live** (317.8 s
  into this head's run)
  (`FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed -
  JavaScript heap out of memory`) with **no check failing**: every card check
  printed before the abort is `ok` (1290 of them), and `node tests/card_drift.mjs`
  reads `identical in all 45 states` at this head.
  Null control: the same script at this head with
  `NODE_OPTIONS=--max-old-space-size=4096` prints `ALL CARD CHECKS PASSED`
  (1306 `ok` lines, none failed), so the red is this host's default V8 heap and
  not the diff.
- `tests/stress.py` — `no scenario exceeds its own recorded cost by the budget
  factor` reads the `summer/1z/space/valve` family near its own budget and
  straddles it by run: red at the pre-merge gate (`5.3x` its reference against
  a `4.6x` budget — `1.54x` recorded x the `3.0` factor — confirmed at median
  5.6x over 3 re-solves, min 5.5x, max 5.9x, at `173b71ba4`), green in the gate
  at `5c01e4065` (`ok`; worst scenario `shoulder/tariff+pv+cycle` at 107.8x of
  268x). No check run exists at `8d0a1c3f7`, so this head's margin is unread
  until its first gate. That family is the one this branch re-plans (64
  objective evaluations against 40, above), and the solver-work channel exempts
  it by name; the CPU benchmark prices the store at 2.6–2.8x on the owner shape
  and the budget channel divides by the run's own reference solve, so the margin
  is a cost reading, not a check regression. If it recurs, the disposition is a
  `tests/stress_budgets.json` raise on that scenario's recorded ratio, which is
  the owner's under `budget-raise-gate`, not this seat's.
- `tests/stress.py` — `shoulder: cheaper than holding the setpoint`
  [4.67 vs 3.96]. Answer: **base's, not this diff's.** The case is
  `buffer 200 L, valve 'none'`, and `ThermalParameters.buffer_is_store` is
  `mixing_valve.is_throttling(...) and buffer_tank_volume >=
  BUFFER_STORE_MIN_VOLUME`, false for a `'none'` valve — so neither the store's
  physics nor the terminal credit can reach it. Measured with the same driver
  at the merge base (`3b4180dcc`), at current `origin/main` (`67178dc6a`) and at
  this head: `predicted 4.6716 / thermostat 3.9585` in all three.

## Forward-carry

- **The 272 s solve outlier (D15 L4) is not reproduced.** On the owner shape the
  worst solve at this head is 16.1 s in the wall pair, and the flat-price null
  reaches 3.1 s; no input shape here produces 272 s.
  Carry: dismissed: measured and not reproduced on every input shape this harness drives; no bound or warm start is owed without the owner-box shape
- **The live store costs 2.6–2.8x CPU on the owner shape.** Two paired runs of
  the same seeded 10-solve sequence, each end taken at the same moment: against
  the branch's own base `3b4180dcc` 8.016 s → 22.305 s (×2.78, medians
  0.888 → 2.313), and against the merge base `67178dc6a` 8.587 → 22.693 s
  (×2.64, medians 0.969 → 2.317). The flat no-buffer null reads 1.08x and 1.05x
  (9.325 → 10.034 and 9.675 → 10.171). The two-zone valved families sit at
  1.028x/1.030x of the 1.05x call-channel allowance (plans unchanged), and the
  single-zone valved family re-plans (64 objective evaluations against 40,
  exempt there). A bound or a warm start on the planner must earn the 2.6–2.8x.
  Lands in `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-STORE-RACES (handoff/audit-r10-roster at b5ea7fda7a9e)
- **The two accuracy biases are separate, and neither is a sign slip.** The live
  bundle reads `power_ratio ≈ 1.31`, `cost_error ≈ -29 %`: reality delivers more
  power and costs more than the plan booked. The DP arms read the plan booking
  more energy than the relaxed DP optimum (+19.2 % on the flat-price null,
  +38.4 % on the owner shape) and more than the house then receives
  (`plan/deliv` 1.205 and 1.18). So the *planner* over-books against its own
  reference, while the *realised* run over-runs the plan; the two live on
  different comparisons and neither cancels the other. The definitions are
  pinned (`accuracy`, above), and a pure power ratio of 1.31 would read a cost
  error of -23.7 %, not -29 %, so the owner's pair also carries a ~7 % cost-per-
  kWh component or two different sample windows. The same arms are #2499's
  residual: the plan books +19.2 % more kWh than the relaxed DP optimum on the
  flat-price null and +38.4 % on the owner shape, and the gap survives the null,
  so it is demand-side and #2499 stays open on it rather than closing on this
  measurement. R10-STORE-RACES inherits the residual: close it as a demand-model
  fix with the same flat-price null, or refute it and say why, either way with
  `dev/audit/harnesses/r10_demand_overbook.py`. Lands in
  `dev/programme/rosters/wave-r10-groups.json`.
  Re-measured at `e01696141`, identical. Lands in the group's `carry` on `handoff/audit-r10-roster` at `5704c4048` (`roster_queue.py readback`: exact match, carry index 2 of R10-STORE-RACES).
  Carry: R10-STORE-RACES (handoff/audit-r10-roster at 5704c4048)
- **Two homes for the 35 L fallback, on purpose.** `_buffer_capacity` words it
  once, and the two-zone step and the batch step each still inline it
  (`if c_buf < 1e-6: c_buf = 0.04`); the single-zone stability row's copy, added by this branch, now calls it (`bcffa2649`). The step's copy sits two lines above the
  call that now also computes it; routing the step through the helper would
  delete those lines and drop `class_excess_loc`, at one more call per
  two-zone step — the call channel is at 1.030x of its 1.05x allowance, so it
  is left to the group that next prices that family. Lands in
  `dev/programme/rosters/wave-r10-groups.json`.
  Carry: R10-STORE-RACES (handoff/audit-r10-roster at d6217f814a7c)

- **The valved reference under-heats a setback's recovery against an unvalved
  one** (`## Figures`, comfort: 17.49 against 5.34 Kh at scale 1.7), because
  the configured curve, not the pump's nameplate, caps what a valve delivers;
  that is the install's physics, and the plan faces the same curve. It makes
  the reference cheaper, so `predicted_savings` on those cells is understated
  (to -6.89 on the finder's 1.7 flat set-point cell), never inflated. A
  reference that also lifts the valve's target to recover would be a
  different thermostat than the configured one.
  Carry: dismissed: conservative direction, measured above with its unvalved control; the reference models the install the user configured

## Friction

- `gitignore-global-config: cost`: `.gitignore:28` ignores `config/` at any
  depth, so `git add dev/audit/config/bugclasses.json` (a **tracked** file)
  prints *"The following paths are ignored"* and exits 1; `git add -A` skips new
  files there silently. Both nested `config/` directories in this tree
  (`dev/audit/config`, `dev/governance/config`) are tracked, and
  `git check-ignore --no-index -v` names `.gitignore:28` for each, so the rule is
  anchored wrong for a repository with policy config directories. Carry: dismissed: its destination R10-FLOW-JIDOKA merged as #2853 without it and is done; the re-route is owed to the orchestrator (DECISION-OWED in the session's to-main.txt)
- main-red-invisible: unenforced: `tests/stress.py`'s shoulder economics check
  is red on the merge base (`3b4180dcc`) and on current main (`67178dc6a`) with
  the identical reading (`predicted 4.6716 / thermostat 3.9585`), and no
  check-run at main's head shows it: at `67178dc6a` the `gate` check completed in
  20 s and the push's `sweep` in 19 s, and of the `tests / ...` jobs only
  `ci-ratchet` and `coverage-ratchet` ran. A full-suite pass on main is therefore not visible in
  that push's checks, so a base red travels unremarked into a branch's gate. Not
  this group's to fix; the after-merge bookkeeping must read main's own suite
  state. Carry: R10-FLOW-POSTMERGE (handoff/audit-r10-roster at c0dbb4585d68)



