# D7 — Architecture and maintainability, round 7

Baseline: `f9d6f78243fa65f6fa128d2357752a2ae7f60648`
Auditor model: claude-fable-5
Root rule: every harness resolves the repo root from `__file__` (`parents[4]`),
per the README trap; run from the export root with
`PYTHONPATH=tests/hastub`.

## Method

D7's brief is a six-item checklist. I ran the whole checklist's first item
(structure metrics) as a reading, drove item 2 (sysid plant) to a finding,
and verified item 2's control arm and the two-state forward model exactly.
Items 3 (learner freeze vs COP flow), 4 (`last_buffer_trajectory` call order),
5 (this-year train spot mutations) and 6 (dead code) were not completed to a
committed harness within budget; see "Not finished".

## Findings

### D7-01 — the two-state sysid fit's fixed-width intercept ridge biases UA +7.4 % and the adoption gate is blind to it

**Claim.** On a noise-free step response of the production two-state
`ThermalModel`, `SystemIdentification.identify_slab` — the production sysid
path — reports a heat-loss coefficient biased **+7.44 %** (range
7.438–7.453 % across the light/medium/heavy building presets) when the true
free heat is 0 kW (the unoccupied night window the experiment actually runs
in), and the #1410 adoption gate admits it at `ua_profile_halfwidth` ≈ 1e-4
(three orders of magnitude below the `log 1.10` bar).

**Mechanism.** `identify()` (the one-state identifier) regularises its
intercept with a *data-scaled* ridge — `prior_rel = s_noise / prior_sd`, so on
clean data `s_noise → 0` and the prior has no weight, recovering the truth
exactly. `identify_slab()` (the two-state identifier) instead appends ONE
pseudo-observation `(G − gains_prior_kw) / SLAB_INTERCEPT_PRIOR_SD_KW` with a
**fixed** width `0.1 kW` to the residual vector (`sysid.py:1690-1696`). Clean
data never out-weighs a fixed-width pseudo-observation, so the fitted gains
are pinned to the 0.3 kW prior (`gains_fit = 0.300000` exactly) and the +0.3 kW
of unmodelled free heat is absorbed by the UA column, biasing it up ~7.4 %.

The #1410 gate (`coordinator.py:10454-10456`) bounds the fitted UA's own
profile-likelihood *half-width* — a measure of the fit's self-consistency, not
its accuracy. A prior-dominated, systematically biased fit has a tiny residual
and therefore a tiny half-width, so the gate is structurally blind to exactly
the bias the ridge produces. The result is adopted at near-full weight
(`weight = 1 − hw/bar ≈ 1.0`), seeding `house_heat_loss_scale` ~7.4 % high.

**Instrumented symbol.** `heatpump_optimizer.sysid:SystemIdentification.identify_slab`
**Perturbation.** `SysIdConfig.gains_prior_kw` 0.3 (default) → 0.0: the bias
moves 7.44 % → 0.000 % (direction down), and `gains_fit` moves 0.3000 → 0.0000,
isolating the ridge as the sole mechanism.
**Metric.** relative UA bias = `(fitted heat_loss_kw_per_c − true_ua) / true_ua`,
with admitted = `ua_profile_halfwidth ≤ UA_ADOPTION_HALFWIDTH_BAR`.

**Severity.** medium — a systematic, bounded (+7.4 %) bias in the opt-in
system-identification feature that seeds a published value
(`house_heat_loss_scale`); workaround is disabling sysid; the passive learner
eventually re-corrects it. Not `high`: opt-in, bounded, and one of three
published scalars rather than a silently wrong money/comfort answer on every
install.

**Proposed fix scope.** Make the two-state intercept ridge data-scaled like the
one-state twin (weight the `(G − prior_g)/0.1` pseudo-observation by the
residual noise, so clean data out-weighs it), or add an accuracy-facing gate
(e.g. refuse when the fitted gains are pinned at the prior while the excursion
is large). One file: `custom_components/heatpump_optimizer/sysid.py`.

## Non-findings (checked and held)

- **Structure ratchet is exactly at budget (a reading of a carried metric).**
  `PYTHONPATH=tests/hastub python3 tests/structure.py` → all 24 metrics `ok`
  (`coordinator_loc=9127`, `coordinator_methods=227`, `coordinator_attrs=153`,
  `max_cc=48`, `dead_methods=0`, `dead_top_level_symbols=0`, …). The ratchet's
  own numbers, not re-derived.

- **The two-state fit's forward model reproduces the production plant exactly.**
  `_simulate_slab_path` reproduces the production `ThermalModel` step response
  bit-for-bit under the production sample convention (max `|pred − rooms|` = 0.0
  at the true parameters), and `features.py` pins `identify()==0` on the
  declared-plant sequence. So the +7.4 % bias is the prior, not a model error.

- **The one-state identifier is harness-only and correctly refuses slow-slab
  plants.** On the light preset `identify()` returns ≈ the true UA; on
  medium/heavy it refuses (`fitted gains outside plausible bounds` / sign
  guards). The designed split held.

## Harnesses

- `tools/audit/round7/D7/sysid_plant.py` — the finding's harness. Header
  carries the metric definition, the command, the expected values, the baseline
  SHA and the machine; thread-pinned; `__file__`-rooted.

## Not finished

- **Item 3 (learner freeze vs COP flow):** learners enumerated (ComfortLearner,
  CurveLearner, DhwProfileLearner, the house-loss / capacity-envelope / solar /
  internal-gains learners, and sysid) but no contaminated-interval simulation
  was committed.
- **Item 4 (`last_buffer_trajectory` / `_initial_buffer_temp` call order):**
  traced the stash (`_stash_price_horizon`, `optimizer.py:3063`) → read
  (`_settlement_caps`, `optimizer.py:6230`) order and found it correct within
  one `optimize()`; a reordering/second-objective perturbation was not run to a
  number.
- **Item 5 (this-year train spot mutations) and item 6 (dead code by AST +
  runtime sentinel):** not started within budget.

## Exposure

None. No `docs/audit-*.md`, no `docs/backlog.md`, no GitHub, no `gh` was read.
The only prior-finding citations encountered are in-code comments, treated as
context per COMMON.md.
