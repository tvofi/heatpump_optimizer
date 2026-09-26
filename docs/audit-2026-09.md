# Codebase audit, September 2026

The eleven-dimension audit, run as a workflow and repeated until dry: one
fresh-eyes auditor per dimension in parallel, findings deduped, adversarial
verification (from round 8 one verifier per dimension and no panel kill, a judge
who re-measures every finding; rounds 1-7 ran three verifiers per panel and
killed by majority refute), one GitHub issue per verified finding, fixes
grouped into PRs by blast radius, each merged and released under the standing
gate protocol (`docs/plan-open-issues.md`, "Standing rules"; versions assigned
by `tools/release/stamp.py` at merge time). A new finder round follows each
round's fixes; the loop stops at the stop floor recorded per round.

Every finding and every fix carries an executed number, not an argument. A
finding without executed evidence is discarded at intake; a number the judge
cannot reproduce within the harness's tolerance is `unreproduced` and blocks
the round from being called dry.

**This is a living document.** One section per round. Status values:
`reported` → `verified` / `weakened` / `refuted` / `unreproduced` /
`withdrawn` → `issue #N` → `fixed (PR #N)` → `released (vX.Y.Z)`, or
`wontfix (reason)`. Where a status column and a body paragraph disagree, the
status column is the truth.

The briefs, the finding schema, the harness contract and the harnesses live
under `tools/audit/`; the orchestration scripts under `.claude/workflows/`.

## Round 1 — baseline v6.2.0 (`4bf3d7d`), 2026-09-01

Round 1's harnesses and verifier reports were session artifacts and were not
preserved; the numbers below are as recorded, and round 2 re-measures anything
it needs to build on. Stop floor for round 1: none was set.

### The dimensions

| # | Dimension | Auditor status |
|---|-----------|----------------|
| 0 | Price optimality (sub-optimal planning) | reported (2 findings) |
| 1 | Robustness and stability | reported (5 findings) |
| 2 | Mathematical and physical sanity | reported (1 finding) |
| 3 | Test-suite gaps, suite resource use | reported (8 findings) |
| 4 | UI/UX — card and config flow | reported (10 findings) |
| 5 | Docs structure, flow, content; code comments | reported (5 findings) |
| 6 | README/documentation claim verification | reported (2 findings) |
| 7 | Architecture and maintainability | reported (6 findings) |
| 8 | Sensor verification and ordering | reported (6 findings) |
| 9 | CPU and memory efficiency (Pi-class target) | reported (4 findings) |
| 10 | HA quality tiers (Bronze→Platinum) | reported (15 findings) |

### Findings register — round 1

Severity from the reporting auditor; subject to the verification panel.
Detailed evidence lives in the per-dimension reports (session artifacts) and
will be summarized in the PRs that fix each finding.

#### D1 — Robustness and stability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D1-01 | critical | Corrupted ledger month permanently wedges every future update cycle (`ledger.py` `from_dict` accepts malformed `lines`; crash in `_roll_month` precedes month-close, so it repeats forever) | fixed (PR #134), released v6.2.10 |
| D1-02 | high | 13 deferred `hass.async_create_task` calls in coordinator `__init__` race `async_shutdown`; fast unload/reload leaks live state-change listeners referencing a torn-down coordinator | refuted (panel: stub divergence, not reachable through the config-entry state machine); hygiene residue shipped in #144 |
| D1-03 | high | GIL contention from the executor-wrapped solve degrades event-loop tick latency ~190–300× during every solve (measured) | merged into M1; fixed (PR #133), released v6.2.8 |
| D1-04 | medium | Weather-forecast fetch failure silently fabricates a flatlined zero-rain/zero-solar 48 h forecast, forever, with no staleness flag | merged into M2; fixed (PR #158), released v6.2.13 |
| D1-05 | medium | Corrupted snapshot `accuracy` field crashes the drift-rollback insurance path (manual service and automatic attempt) | fixed (PR #134), released v6.2.10 |

#### D2 — Mathematical and physical sanity

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D2-01 | medium | `sysid.identify()` over-estimates UA under sensor noise (errors-in-variables: `T_prev` on both sides). Executed: +44 % at 0.05 °C noise, +108 % at 0.10 °C; biased fits clear the 0.3 adoption gate on realistic cold-night windows. Ridge regularizes only the intercept; confidence damper keys off a range outdoor drift inflates | issue #190 |
Verified sound (executed): energy conservation ~1e-14 kWh closure; DHW balance
8e-16; dt-invariance; scalar/batch bit parity; `predicted_cost == Σ price·power·dt`
and the savings identity to 1e-6 across golden scenarios; capacity tariff charges
the monthly peak once; COP monotone, Carnot fraction 0.35–0.42.

#### D4 — UI/UX

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D4-01 | critical | Card chart SVG text at phone width renders at 3.19 px glyph height (viewBox-unit fonts scale with container; 3× shrink from desktop) | fixed (PR #135), released v6.2.11 |
| D4-02 | high | Single-point series render nothing while the legend chip still reads "active" | fixed (PR #135), released v6.2.11 |
| D4-03 | high | "Estimated prices" label overlaps lane-row labels (78 % of glyph height) | fixed (PR #135), released v6.2.11 |
| D4-04 | high | Hardcoded "SEK" in config-flow labels and two Repairs notices despite currency-agnostic price data | issue #168 |
| D4-05 | high | `grid_fee_rules` accepts any sign/magnitude across all layers — a sign-flip typo silently becomes a permanent fee subsidy | issue #169 |
| D4-06 | medium | "Projected savings" headline discloses its baseline only via hover tooltip | fixed (PR #135), released v6.2.11 |
| D4-07 | medium | `day_start_hour` (0–12) / `day_end_hour` (18–23) slider ranges are disjoint, forbidding valid schedules and shielding a real validator | issue #170 |
| D4-08 | medium | `dhw_windows` accepts a meaningless 1-minute window | issue #171 |
| D4-09 | medium | "Self-learning and diagnostics" options page is the densest with zero grouping (~6 themes, 18 fields) | issue #198 |
| D4-10 | medium | 55 sensors in one flat device; only 10 diagnostic-categorized, only 6 disabled-by-default | issue #179 |
#### D5 — Docs structure, flow, content

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D5-01 | high | configuration.md "1·Basics" table missing four real always-asked fields (Tuya support) | fixed (PR #127), released v6.2.7 |
| D5-02 | high | Same four fields make configuration.md's "17 assignable keys" (actual 21) and "eighteen fields" (actual 22) wrong | fixed (PR #127), released v6.2.7 |
| D5-03 | medium | architecture.md "42 modules" + module map omit `pump_mode.py`/`pump_signals.py` (stale since v5.1.7) | fixed (PR #127), released v6.2.7 |
| D5-04 | medium | plan-open-issues.md "authoritative" delivery table lists six shipped issues as open and reverses a fact about the batched-FD gradient | fixed (PR #127), released v6.2.7 |
| D5-05 | low-med | tests/README.md omits `manual_plan.py` and `setup_qa_render.mjs`, both run.sh-wired | fixed (PR #127), released v6.2.7 |

Link-check: 45/45 clean. No factually-wrong code comments found (4 techniques).

#### D6 — README and metadata claims

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D6-01 | medium | manifest.json `documentation`/`issue_tracker`/`codeowners` point to a non-existent GitHub identity (404) | fixed (PR #127), released v6.2.7 |
| D6-02 | medium | `apply_manual_plan` documented `example:` values fail the service's own voluptuous schema (YAML-folded strings vs `vol.Any(None, [dict])`) | issue #172 |
52-row claims table otherwise verified true (entity counts, defaults, services,
performance claims, card behavior).

#### D7 — Architecture and maintainability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D7-01 | critical | coordinator.py: one 10,041-line class, 249 methods, welded by 142 instance attrs (66 multi-assigned) + a 206-key output dict; 59 % of internal calls cross clusters — state is the coupling | programme #193 **closed 2026-09-10** by the W4-G14 close-out (Wave 4, S0–S13; roster `.claude/workflows/wave-4-groups.json`): S0–S11 landed, S4 and S12 recorded halts (#508, #637) — no subsystem API emerged, the facades stay, and the seam moves are owed by no stage; the welded-class condition itself still holds, re-measured with `python3 tests/structure.py` at the close-out's merge base; the coverage half of the judge's S12 is W5-G7 (#195); the seam moves S12 could not make are Wave 5's W5-G9 (dhw profile learner) and W5-G10 (legionella guard), owner-approved 2026-09-10 |
| D7-02 | high | sysid fits a first-order plant to a ≥2nd-order house; on high-mass slab targets it returns implausible signs within the comfort excursion (inert on target houses); −49 % UA bias only at comfort-impossible steps | issue #191 |
| D7-03 | high | Scalar vs batch physics: ~720 duplicated lines (11 verbatim equations) kept identical only by `_grad_parity` — 5 configs/1 weather, space-only, never the DHW path | fixed (PR #133), released v6.2.8 (parity breadth residual) |
| D7-04 | medium | `last_buffer_trajectory` side-channel: scalar writes, batch doesn't; contained today, latent stale-read trap, no test | fixed (PR #133), released v6.2.8 |
| D7-05 | medium | Freeze-gate asymmetry: `_accuracy.record()` gated only on pump signals; open-window intervals still poison trust/damp/band/drift baseline (demo: trust 1.00→0.93) | issue #192 |
| D7-06 | low | 5 verified dead symbols + 4 unused CONF keys | issue #178 |
Non-findings: 0 import cycles; config sprawl modest (141/166 keys read);
layering clean; no QA-renderer leakage into production.

#### D10 — HA quality scale

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D10-01 | high | Services registered per config-entry, not in `async_setup` (action-setup, Bronze) | issue #180 |
| D10-02 | high | `hass.data[DOMAIN]` everywhere; `ConfigEntry.runtime_data` never used (runtime-data, Bronze) | issue #181 |
| D10-03 | high | No duplicate-entry protection in config flow (unique-config-entry, Bronze) | issue #182 |
| D10-04 | high | Config-flow tests never exercise a full flow, error paths, or dup prevention (config-flow-test-coverage, Bronze) | issue #194 |
| D10-05 | medium | No uninstall/removal instructions in docs (docs-removal-instructions, Bronze) | issue #183 |
| D10-06 | critical | `async_shutdown()` override drops `super()` — base coordinator refresh timer/debouncer leak on every unload/reload (config-entry-unloading, Silver) | fixed (PR #144), released v6.2.12 |
| D10-07 | high | Tibber fetch failures swallowed — `last_update_success` never flips, entities never go unavailable (entity-unavailable, Silver) | fixed (PR #144), released v6.2.12 |
| D10-08 | high | No reauthentication flow for the Tibber token (reauthentication-flow, Silver) | issue #187 |
| D10-09 | medium | Tibber outage logs ERROR every poll cycle, not once (log-when-unavailable, Silver) | fixed (PR #144), released v6.2.12 |
| D10-10 | medium | No platform declares `PARALLEL_UPDATES` (parallel-updates, Silver) | issue #184 |
| D10-11 | low | Sampled test coverage far below the 95 % bar (time-boxed single-script sample) | fixed (PR #889), released v6.4.3 |
| D10-12 | medium | No diagnostics platform (diagnostics, Gold) | issue #188 |
| D10-13 | low | 64 hardcoded `_attr_icon`, zero icons.json (icon-translations, Gold) | issue #189 |
| D10-14 | low | No reconfigure flow (reconfiguration-flow, Gold) | issue #196 |
| D10-15 | low | mypy: 160 errors, majority stub artifacts — informational (strict-typing, Platinum) | issue #197 |
Passes confirmed by execution: entity-unique-id (65×2, 0 collisions),
has-entity-name, repair-issues, devices, async-dependency, inject-websession.

#### D8 — Sensor verification and ordering

Method: 15-topology × 65-entity-class matrix (975 rows) driven against the
real coordinator.

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D8-01 | critical | `ScheduleSensor` leaks `numpy.float64` via `solar_gain_trajectory` attributes; HA's orjson serializer crashes on it (sibling field already routes through `_plain_types`, this one doesn't) | issue #173 |
| D8-02 | high | `_fetch_weather_forecast()` empty-result path silently keeps stale forecast data forever — no exception, no signal (proved via fetch transition) | merged into M2; fixed (PR #158), released v6.2.13 |
| D8-03 | medium | DHW domain scattered across 3 entity_id prefixes (`dhw_*`/`hot_water_*`/`mixed_hot_water`) breaking alphabetical clustering | issue #174 |
| D8-04 | medium | "stat_kind" headline-card family split 2-vs-2 across `entity_category`, burying half in Diagnostics | issue #175 |
| D8-05 | low | `PredictionAccuracySensor` missing its siblings' evidence-wait pattern | issue #176 |
| D8-06 | low | ECL110 sensors missing `entity_category=DIAGNOSTIC` unlike other disabled-by-default sensors | issue #177 |
Disproved leads documented as non-findings (permanently-unavailable sensors,
naive timestamps, DHW staleness, negative values) — traced to harness gaps,
not product bugs. All findings re-executed before reporting.

#### D9 — CPU and memory efficiency (Pi-class)

Pi extrapolation factor ×5 (range 4–8); counts used as contention-immune
evidence; harnesses preserved for the verification panel.

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D9-01 | critical → fixed (PR #133, v6.2.8) | v6.2.0's batched gradient is bypassed on 38 of 39 DHW-enabled golden scenarios: any DHW block makes bounds non-uniform → scalar FD fallback. Default two-zone DHW solve = 941,472 simulate_step calls (×40 the batched 23,520), 9,321 sims/gradient; ~8.9 s vs 0.93 s here, ~45 s on Pi | fixed (PR #133), released v6.2.8 |
| D9-02 | high | Solve in executor starves the HA event loop 75–76 % of solve wall time (5 ms heartbeat ticks at 21 ms); longest native GIL hold 23–62 ms; severity gated by D9-01's duration | issue #199 |
| D9-03 | high | Stress gate: one 1400× per-scenario ratio spans a 1913× scenario cost spread — cheapest scenario can regress 2626× and still pass. The "CI is 4× looser" claim is stale (absolute budget retired; CI == local defaults) | issue #166 |
| D9-04 | medium | Zero memory instrumentation anywhere in the gate; proposed budgets from measured baselines | issue #167 |
Non-findings (measured): 1 solve/cycle; DHW planning 0.5–13 % of cycle;
`_build_data_dict` ~7 ms/137 KiB no retention; retained structures bounded
(~2 B/cycle); recorder ingests 8.5 KB/cycle (87 % excluded); batched path
confirmed working for DHW-off two-zone (0.93 s).

#### D0 — Price optimality

Method: capture harness wrapping `_multi_start_minimize` so every reference
races the exact production objective/bounds; feasibility-checked (comfort
parity) before any "cheaper" verdict; leave-one-out on all aggregates.

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D0-01 | medium | All three L-BFGS-B starts cluster at ~0.52–0.55 energy fraction; on arbitrage-structured prices they land in one basin. A bang-bang start (frac 0.35) reaches strictly cheaper comfort-feasible plans: falling-price 3.06 % (1.79 SEK/day), cheap-late 1.58 %, mid-spike 1.01 %; 3/8 shapes clean-cheaper; survives leave-one-out. Step-0 action differs (OFF vs ON), so MPC re-planning does not mask it | issue #185 |
| D0-02 | low | `_MULTI_START_SOLVES=2` discards one of three candidates by raw pre-refinement score; refines below the shipped result in 5/10 profiles; clean impact marginal (≤0.105 SEK/day) | issue #186 |
Non-findings (executed): DHW decomposition converges in one pass (Δcost 0.000 ×5);
terminal stored-heat credit sound; longer horizons don't lower realized cost;
no cross-tick warm-start exists (lock-in impossible); PV surplus fully consumed;
capacity tariff shaves peak 6.0→3.99 kW.

#### D3 — Test-suite gaps

Method: mutation testing against the shipped tree — delete/invert a production
line, re-run every script in its measured closure (tests/closures.json), and
see whether the suite notices. Every verdict below is a full-closure run.

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D3-01 | critical | Compressor-cycling penalty deleted from the objective — vacuous even in the stress.py test titled "a cycling cost reduces compressor starts" (full 13-script closure passes) | refuted (CI's `env_drift.py --all` catches the mutant) |
| D3-02 | critical | COP-learner trust-region clamp deleted — a single bad sample can move the plant efficiency model unbounded; full closure passes | fixed (PR #132), released v6.2.9 |
| D3-03 | high | ECL110 first-order lag physics deleted — displace value exposed on two entities, asserted by value nowhere (13 scripts pass) | fixed (PR #132), released v6.2.9 |
| D3-04 | high | COP-degradation repair text can claim the full monthly bill for a 1 % shortfall — only placeholder keys checked, never values | fixed (PR #132), released v6.2.9 |
| D3-05 | high | `pump_mode_unreadable` notification path made a no-op — nothing notices | fixed (PR #132), released v6.2.9 |
| D3-06 | high | `climate.hvac_action` hard-coded to a wrong value — zero test references | fixed (PR #132), released v6.2.9 |
| D3-07 | medium | Grid-fee day-range parser wrap-around branch (`"Fri-Mon"`) deleted — every suite string avoids the wrap case | fixed (PR #132), released v6.2.9 |
| D3-08 | medium | Config-flow DHW deadband validation (`_dhw_min_too_close`) permanently disabled — no test notices | fixed (PR #132), released v6.2.9 |

Suite resource notes (for the fix round): closure.py under-records golden.py
~384× (49 real solves, 307 s vs recorded 0.8 s); backtest.py over-recorded
13–19×; stress.py has the worst cost/assertion ratio (97 solves / 30 checks).
DST explicitly confirmed NOT a gap (dedicated 314-line suite).

### Dedup

64 findings reported. Two merges (same phenomenon found independently):

- **M1** := D1-03 + D9-02 — the executor-wrapped solve starves the HA event
  loop via the GIL (~190–300× tick latency; 75–76 % of solve wall). One
  finding, two independent measurements.
- **M2** := D1-04 + D8-02 — `_fetch_weather_forecast` failure/empty paths
  silently produce a fabricated or stale forecast with no staleness signal.

Fix-stage groupings (distinct findings, one owner each): {D2-01, D7-02} sysid;
{D1-02, D10-06} unload lifecycle; {D10-07, D10-09} Tibber failure handling;
{D5-01, D5-02} same four missing fields; {D9-01, D7-03, D7-04} batch/scalar
seam. Net: **62 distinct findings** enter verification.

### Verification round — verdicts

Nine panels, three verifiers each (two on G-panels plus the judge), voting
independently per finding. Majority-refute kills; the judge re-measured the
decisive number wherever verifiers split. 27 verifier reports live in the
session artifacts (`round1/verify/`).

**Killed (3):**

- **D3-01** (cycling-penalty vacuous) — REFUTED 2-0 by executed re-runs: CI's
  actual gate mode (`GOLDEN_MODE=drift` ⇒ `env_drift.py --all`) catches the
  mutant (`compressor_starts 4→8`, second scenario diverges). The finder
  tested the default 5-fixture mode, not the CI mode.
- **D1-02** (deferred-task/shutdown race leaks listeners) — REFUTED, judge-
  ruled on production reachability: real HA serializes setup/unload
  (`setup_lock` on current HA; non-recoverable `SETUP_IN_PROGRESS` on the
  2024.1.0 floor), and the judge verified both listener-registering task
  bodies are await-free, so they complete before unload can begin. The leak
  repros only by calling `async_shutdown()` directly, bypassing the config-
  entry state machine (stub divergence). Hygiene residue (untracked
  `hass.async_create_task`) noted for the lifecycle PR, not a finding.
- **D7-06 (CONF-keys half)** — the 4 "dead" CONF keys REFUTED by judge
  runtime sentinel: all four are read via `getattr(const, f"CONF_{…}")` in
  `ThermalParameters.from_config` (sentinels 0.0123/1.77/0.66/0.42 all
  surfaced). The 5 dead symbols stand.

**Verified as reported (headline items):** D9-01 (critical — 38/39, 941,472
steps, ×40.03 reproduced exactly twice, independently; and largely
recoverable: with the uniform-bounds guardrail relaxed, 11/12 affected golden
scenarios stay byte-identical), D9-03 (strengthened: a ×40 solve-time
regression passes every active stress budget simultaneously), all ten D4
UI/UX findings (3×unanimous incl. real-browser re-measurement), D1-01
(narrowed: HA Store quarantines invalid JSON, wrong-shape valid JSON still
wedges), D1-05, D10-06 (real-HA upstream diff confirms the base-class leak),
D10-07, D10-09, M2 (strengthened: fabricated flatline costs +41.9 % realized
on a cold-front scenario), D3-02…D3-06, D3-08, all D5, D6-01, D10-01…05,
D10-08, D10-10…15, D8-03, D0-02.

**Verified weakened (fix scope adjusted):**

- **D0-01** — mechanism confirmed and deterministic, but the 3.06 % headline
  was energy-only; with production's full objective decomposition the net
  clean gap is ~1.1–1.6 % on adversarial shapes. Medium stands.
- **D2-01** — EIV mechanism and defeatable adoption gate confirmed (twice,
  from scratch); headline +44 % is noise-model-dependent (can reverse sign
  under quantization noise / mismatched priors). Fix must target the gate and
  estimator, not chase the headline number.
- **D7-01** — metrics reproduce exactly; "critical" not earned for a
  maintainability finding (→ high). Direction (state-coupling dominates; DHW
  is the cleanest seam) supported by two independent clusterings.
- **D7-02** — inert-on-target-houses confirmed; production guard makes it
  fail-safe (→ medium; the feature is ineffective, not harmful).
- **D7-03** — duplication is deliberate and triple-enforced; residual is
  parity-coverage breadth (5 configs/1 weather/1 state) (→ medium).
- **D7-04** — zero live bug; latent hygiene (→ low).
- **D7-05** — asymmetry real; production-diluted magnitude small (damp
  no-ops at realistic window populations) (→ low-medium).
- **D8-01** — real HA's serializer default rescues `np.float64`; type
  hygiene, not a crash (critical → low).
- **D8-05, D8-06** — minor; D8-06 survives 2-1 (deliberate-design argument
  recorded for the fix round).
- **D3-03, D3-07** — gaps real; weakened by reachability (ECL110 opt-in;
  wrap-around rules rare).
- **D6-02** — HA's frontend "fill example" path re-parses fine (→ low).
- **D10-03** — multi-entry is deliberate; fix must abort true dups only.
- **M1** — starvation share ~75 % reproduces; the 190–300× tick-latency
  ratio does not (~12–14× under load-stable methodology). Duration gated by
  D9-01's fix.
- **D9-04** — nightly `rolling.py` count-ceilings do guard retained growth;
  the gap is byte-level instrumentation in the gate (→ low-medium).

Round-1 net: **59 findings verified (many re-scoped), 3 killed.** Two
corroborating votes (a3, e1) still in flight can only strengthen the tally;
their data folds into the fix PRs.

### Fix-wave verification notes (written by whoever measured)

- **D9-01's gate scope was corrected during the fix.** The interrupted
  first attempt served the batch to *every* usable bound list and failed
  its own gate: on zero-range bounds (lb == ub — manual pins, or a DHW
  block consuming the whole cap) the one-sided FD step is zero, the
  divided difference is 0/0 = NaN, and the supplied-jac path dies in the
  first line search where scipy's own path survives on a one-ULP nudge
  (executed on the fuse-guard shape: 78.66/status 2 vs 67.19/converged).
  The shipped gate serves all bounds *except* zero-range entries, with
  the rejection asserted directly in features.py.
- **The "12th scenario" the verification panel could not make
  byte-identical is maxfun starvation, not parity.** Under jac=None,
  scipy books every FD row of every gradient into the default 15,000
  evaluation budget; `tariff_plus_two_zone` stopped at nit 43 / nfev
  15,035 / status 1 while the batched path converged at nit 69 / nfev
  283 and landed 7.3 % cheaper (72.54 vs 78.23 SEK) on the same
  objective. The batched gradient is bit-equal to scipy's estimate at
  every jac call of the moved solves. The two tariff fixtures are
  claimed in `tests/golden/claimed_drift.txt`; the other 48 plan
  fixtures are byte-identical.
- **D9-01 re-measured (fix shape): 250.8 s → 35.8 s (7.0×) across all
  49 golden scenarios' optimize() calls; 57 of 58 solves batched (was
  13).** M1's starvation window shrinks by the same factor; the
  residual (sub-second GIL holds) stays deferred per the backlog note.
- **A3's D3-02 mutant was re-executed independently** on the merged
  tree: deleting the trust-region clamp fails 7 feature checks
  ("an extreme COP sample moves cop_scale by at most the clamp's
  max_step"); restored, 1507 pass.
- **A2's stash-pop onto current main corrupted the "perfectly
  partitioned month" test** (the spot add landed inside the loop,
  30× accumulation). Caught by the gate, restored to main's form —
  the failure was the test's, not production's. Every WIP worktree
  merged onto main mid-flight got its full diff re-read after this.

### Fix PRs and releases

Verified findings grouped into fourteen PRs, each owned by one child session,
each merged and released sequentially under the standing gate protocol
(versions assigned at stamp time on main; drift claims written by whoever
measures them; every fix ships with an executed before/after number).

| PR | Scope | Findings | Status |
|----|-------|----------|--------|
| A1 | Batched gradient serves DHW solves; parity breadth; batch side-channel hygiene | D9-01, M1, D7-03 (residual), D7-04 | **released v6.2.8 (PR #133)** |
| A2 | Store robustness: ledger + snapshot corruption | D1-01, D1-05 | **released v6.2.10 (PR #134)** |
| A3 | Close the vacuous-coverage gaps (7 surviving mutants) | D3-02…08 (minus D3-01) | **released v6.2.9 (PR #132)** |
| A4 | Card: phone fonts, single-point series, label collision, visible caveat | D4-01, D4-02, D4-03, D4-06 | **released v6.2.11 (PR #135)** |
| A5 | Docs corrections | D5-01…05, D6-01 | **released v6.2.7 (PR #127)** |
| A6 | Stress gate: per-scenario budgets + memory instrumentation | D9-03, D9-04 | PR #145 open, **red**: its memory pass picks scenarios from this run's costs, not from `stress_budgets.json` (`FAIL every memory-pass scenario has recorded peaks [unrecorded: shoulder/tariff, shoulder/cycle]`); reworked under the round-2 program |
| B1 | Unload lifecycle + Tibber failure semantics | D10-06, D10-07, D10-09 (+D1-02 hygiene) | **released v6.2.12 (PR #144)** |
| B2 | Weather staleness surfaced | M2 | **released v6.2.13 (PR #158)** |
| B3 | Config-flow validation + currency + services example | D4-04, D4-05, D4-07, D4-08, D6-02 | queued |
| B4 | Entity organization & typing hygiene | D8-01, D8-03, D8-04, D8-05, D8-06, D7-06 (symbols), D4-10 (partial) | queued |
| B5 | Quality scale: Bronze/Silver code batch | D10-01, D10-02, D10-03, D10-05, D10-10 (+dup-flow tests toward D10-04) | queued |
| B6 | Optimizer seeding: bang-bang start + refine-before-discard | D0-01, D0-02 | queued |
| C1 | Quality scale: Gold batch (diagnostics, icons, reauth) | D10-08, D10-12, D10-13 | queued |
| C2 | sysid estimator + adoption gate + freeze-gate symmetry | D2-01, D7-02, D7-05 | queued |

Deferred by round 1 with reasons: D7-01 (coordinator decomposition — needs its
own program; seam analysis recorded), D10-04 (full config-flow test suite beyond
dup tests), D10-11 (95 % coverage), D10-14 (reconfigure flow), D10-15 (strict
typing), D4-09 (options-page grouping — blocked on flow-section tooling), D9-02
residual beyond A1's reduction. **Decision 2026-09-02: all seven are fixed under
the round-2 program** — D9-02, D4-09 and D10-14 as fix PRs (behind a `hacs.json`
floor bump for the HA APIs they need), D10-04/D10-11/D10-15 as measured
tranches, D7-01 as its own decomposition program modelled on #136. Every
unfixed round-1 finding has a GitHub issue (label `round-1`); the round-1 fix
wave is tracked in its own issue.

### Status snapshot at the end of round 1's session (2026-09-01)

Released under the standing gate protocol, each merge stamped, tagged
and released with its claims written by whoever measured the drift:

| Release | PR | Findings closed |
|---|---|---|
| v6.2.7 | #127 (A5) | D5-01…05, D6-01 |
| v6.2.8 | #133 (A1) | D9-01, M1, D7-03 residual, D7-04 |
| v6.2.9 | #132 (A3) | D3-02…08 (D3-01 refuted) |
| v6.2.10 | #134 (A2) | D1-01, D1-05 |
| v6.2.11 | #135 (A4) | D4-01, D4-02, D4-03, D4-06 |
| v6.2.12 | #144 (B1) | D10-06, D10-07, D10-09, D1-02 residue |
| v6.2.13 | #158 (B2) | M2 (D1-04, D8-02) |

In flight:

- **A6 (PR #145)** — per-scenario budgets + memory instrumentation.
  CI caught a real design flaw on its first run: memory peaks were
  recorded only for the recording machine's own top-6 dearest
  scenarios, and the runner's dearest set differed ("unrecorded:
  shoulder/tariff, shoulder/cycle"). Fix in flight: record peaks for
  ALL 48 scenarios (check mode still probes only the top-6, which now
  can never be unrecorded). Re-recording, then re-push.
- **B2 (PR #158)** — weather staleness surfaced (M2). Green once,
  merged current main (claims-file conflict resolved keeping the five
  coordinator-capture claims), CI re-running.

Remaining queue, untouched: B3 (config-flow validation + currency +
services example: D4-04, D4-05, D4-07, D4-08, D6-02), B4 (entity
organization: D8-01, D8-03…06, D7-06 symbols, D4-10 partial), B5
(Bronze/Silver code batch: D10-01, D10-02, D10-03, D10-05, D10-10,
dup-flow tests toward D10-04), B6 (optimizer seeding: D0-01, D0-02),
C1 (Gold: D10-08, D10-12, D10-13), C2 (sysid: D2-01, D7-02, D7-05).
Deferred per the backlog note: D7-01, D10-04 (full suite), D10-11,
D10-14, D10-15, D4-09, D9-02 residual.

The second finder round (loop until dry) had not started at this point;
the owner decided on 2026-09-02 to start it immediately, in parallel with
B3…C2 (see Round 2 below).

Operational notes for the next session: versions are assigned at
STAMP time on main (merge first, stamp immediately, then tag; a tag
pushed before its main push strands the release off-main — happened
twice tonight, both reconciled). A concurrent session is landing the
card-decomposition PRs (#136 series), so main moves between fetch and
push: always pull-merge before pushing a stamp, and resolve the
claims-file conflict by keeping the branch's own claims. The scoped
PR gate plus the full main gate caught, between them: the zero-range
bounds divergence (A1, twice), the maxfun starvation explanation (A1),
a stash-pop test corruption (A2), a vacuous getComputedStyle browser
check (A4), and the top-N portability flaw (A6) — the adversarial
verification discipline paying for itself.

## Round 2 — baseline v6.2.14 (`c398fc8`), 2026-09-02

Started 2026-09-02, in parallel with the round-1 fix wave (owner's decision).
Finders measure against the pinned baseline SHA in a `git archive` export, so
merges landing meanwhile cannot move what they measure. Baseline
`c398fc84eec25fc44b60d74aae05b9a2da205884` is v6.2.14, the first green stamp
after #165 merged (`round2/BASELINE.md`, at `d5d8c4a`). Eight dimensions
worked in the read-only export; D0, D3 and D9 in instrumenting worktrees of
the same SHA. Every harness, `REPORT.md` and `report.json` is archived under
`round2/D<k>/` at `d5d8c4a` (see "Harness archive" below for what was left
out).

**Stop floor:** a round is dry when verification confirms no finding of
severity ≥ medium, no correctness bug at any severity, and no row is left
`unreproduced`. Confirmed hygiene lows get issues and one batch PR without
triggering another round.

**What merged on main between the baseline and this register** (the
reference for every "fixed since baseline" row): v6.2.15 (#163, #164 card
lane geometry; #202 this register; #203, #204 closures/claims), v6.2.16
(#145, A6: per-scenario stress budgets + memory line), v6.2.17 (#206, B3:
currency units, grid-fee and DHW-window validation, slider ranges, services
examples; #205, B4: numpy scrub in `sensor._finite`, `dhw_*` entity renames,
entity categories, five dead symbols), v6.3.0 (#207, B5: services in
`async_setup`, `runtime_data`, unique-id guard, `PARALLEL_UPDATES`, removal
docs, HA floor 2024.6.0), v6.3.1 (#209, C1: a reauth flow on HTTP 401/403 and
a diagnostics platform; icons.json deferred with the reason recorded).

### Dimensions

| # | Dimension | Auditor status |
|---|-----------|----------------|
| 0 | Price optimality (sub-optimal planning) | reported (3 findings) |
| 1 | Robustness and stability | reported (5 findings) |
| 2 | Mathematical and physical sanity | reported (5 findings) |
| 3 | Test-suite gaps, suite resource use | reported (10 findings, 7 provisional pending the quiet-window gate) |
| 4 | UI/UX — card and config flow | reported (12 findings) |
| 5 | Docs structure, flow, content; code comments | reported (5 findings) |
| 6 | README/documentation claim verification | reported (5 findings) |
| 7 | Architecture and maintainability | reported (6 findings) |
| 8 | Sensor verification and ordering | reported (4 findings) |
| 9 | CPU and memory efficiency (Pi-class target) | reported (5 findings; wall/CPU numbers provisional) |
| 10 | HA quality scale (Bronze→Platinum) | reported (15 findings) |

### Findings register — round 2

Written by the dedup step from the eleven finder reports (75 findings, all
75 valid against `tools/audit/finding.schema.json`, checked field by field);
verdicts by the panel and the judge. Severity is the finder's. The **Class**
column places each finding against round 1 and against what merged on main
after the baseline:

- **new** — no round-1 counterpart; goes to the panel.
- **corroborates #N** — a round-1 issue still open; the round-2 evidence is
  attached to the issue, no panel, the fix group inherits the harness.
- **fixed since baseline by #PR (vX)** — the judge re-checks on main; no
  panel unless the re-check fails. "(partial)" names the residual.
- **regression: release** — a released round-1 fix whose defect round 2
  measures again; label `regression`, first in the panel queue.
- **refuted-match** — matches a round-1 refuted finding; goes to the panel
  with the refutation attached as one argument.

Where a Status cell and a body note disagree, the Status cell is the truth.

#### D0 — Price optimality

Method: `race_grid.py` records production's `_multi_start_minimize` call
and re-issues it from other starts and budgets on the identical closure,
bounds and jac path; comfort parity is checked before any "cheaper"
verdict; every aggregate carries a flat-price null and leave-one-out.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D0-01 | medium | Capacity tariff: the single-zone solver stalls on the top-k peak plateau (`tariff.peak_cost` sums the top-k window excesses, so a plan with more than k windows tied at the peak is a plateau the 2-point gradient cannot see; L-BFGS-B's ftol fires at a non-stationary point). Beaten at comfort parity in 15/16 winter_cold price×DHW cells, mean 1.26 SEK/solve (2.2 % of objective, 3.3 % of the daily bill) with the 58.29 SEK summer_negative cell dropped; abs(projected gradient) 0.03–20 SEK/kW against PGTOL 1e-5 in 16/16. Perturbations executed: ftol 1e-9 zeroes the restart gap (7→0 cells), peak_count 16 collapses 58.29→0.13 SEK. Flat null: restart gap 0.000; closed loop realises 0.36–1.45 SEK/2 d, so medium not high | new | reported |
| D0-02 | low | Two-zone solves stop on FACTR at non-stationary points: re-submitting production's own x to the identical L-BFGS-B call improves 15/80 cells (mean 0.052 SEK; winter_narrow 2.163 SEK/day = 1.75 % of the bill); abs(pg) > PGTOL in 64/80; flat null max 0.0011 SEK; the receding horizon realises ≤ 0.22 SEK/2 d. Note for #185: the seed-found part of the gap (49/80 cells) survives flat prices (0.155 vs 0.102 SEK), so it is non-convexity, not price structure | new (adjacent to open #185/#186; fix group B6 should read `race_grid.py`) | reported |
| D0-03 | medium | Small buffer tank with a manual mixing valve (golden valve_storage_small_tank, 35 L at 32 °C): the cap-tightened re-solve stops at the tank-clamp kink; beaten at comfort parity in 5/8 price cells, mean 1.13 SEK/solve (4.4 % of the energy bill), max 4.19 SEK; on winter_typical production's own plan breaches the floor by 0.112 K-steps while the bang-bang challenger breaches 0.000; abs(pg) 2–1.1e4 in 8/8. Perturbation: buffer 35→750 L collapses the gap (3.47→0.00, 4.19→0.20) | new | reported |

#### D1 — Robustness and stability

Method: a real asyncio loop with the coordinator driven through
`async_setup_entry` under a modelled `ConfigEntry.async_setup`; solves held
on a `threading.Event` so orderings are deterministic; 2000 seeded store
mutants; frozen clocks.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D1-01 | medium | `ConfigEntryNotReady` from the first refresh leaks the coordinator's listeners and MQTT subscription per retry: after 5 retries 10 state-change listeners, 5 MQTT subscriptions and 5 zombie coordinators (each still running `_on_power_event`); guards-off null 0. `__init__` spawns `_async_setup_peak_guard`/`_async_setup_defrost_watch`/`_async_setup_ecl110_state_subscription`, which register directly on hass, not via `entry.async_on_unload`, and on NotReady HA runs only `async_on_unload` callbacks — `async_unload_entry`/`async_shutdown` never run | refuted-match (r1 D1-02): the same `__init__`-spawned listeners, but a reachability path with no race — the judge's serialisation argument (setup/unload serialised; task bodies await-free) does not cover NotReady, where no unload runs. The panel checks the NotReady semantics against core; the harness header states each assumption | reported (refuted-match D1-02) |
| D1-02 | medium | Reload during a scheduled solve: the torn-down coordinator finishes `_async_update_data` after its own `async_shutdown` returned — 3 service calls (switch.turn_on + 2 mqtt.publish from the pre-reload plan) and 2 store writes, concurrently with the new instance's setup; deterministic. First-solve null 0 (an entry background task, which the state machine cancels); the scheduled refresh is a hass-level task that unload does not cancel, and nothing after the executor await checks `_shutdown_requested` | refuted-match (r1 D1-02): the same "torn-down coordinator still acts" phenomenon by a different mechanism (in-flight scheduled refresh, not `__init__` tasks); the refutation's argument that async_shutdown is only reachable directly does not address a refresh already in flight | reported (refuted-match D1-02) |
| D1-03 | medium | Store loaders crash on corrupt payloads: 152/2000 seeded mutants (200 per store, 10 stores) end a fire-and-forget loader with an unhandled exception; dhw_profile (64), thermal_learning (9, left half-applied) and dhw_draws (1) are never rewritten, so every restart raises again and the learned state stays lost. The update loop never fails (2000/2000); identity null 0/10 stores; snapshots, legionella and manual-plan loaders validate (0/200). A2's ledger/snapshot hardening (v6.2.10) holds | new — extends A2 (r1 D1-01/D1-05) to the other seven stores; `_async_load_manual_plan` is the template. Cross-ref D3-05 (the accuracy store's key-side handler is untested) | reported |
| D1-04 | medium | A price list no longer covering the horizon is planned and actuated on `extend_price_series`' flat 0.5 fallback: 96/96 steps at the constant, known steps 0, the solve runs, savings 13.4 % published, the switch actuated, the cycle green; the only disclosure is `price_known_steps=0`, which no sensor or the card reads. Reach: a 200 response with stale content, or a clock a day off (a failed fetch is honest). Covering-list null 0/96 | new | reported |
| D1-05 | low | `async_simulate`'s `replace(self._thermal_params)` shares the live `DefrostDerate`, the gains profile and `dhw_windows` with the loop while the what-if solves in the executor: 10/10 payload fields torn by an in-place write mid-solve (defrost 9, gains 7, windows 9); the live solve's deep copy shows 0/26. Realistic effect: one EWMA step from `_record_accuracy` landing mid-what-if | new | reported |

#### D2 — Mathematical and physical sanity

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D2-01 | high | Batched single-zone simulation ignores the Euler sub-step: `simulate_trajectory_batch`'s single-zone branch integrates with `dt_hours` per sub-step (`thermal_model.py:2636`) and re-seeds T_room from the initial state on every sub-step of step 0 (`:2606`), while the two-zone branch uses `dt`. Inside the config-flow ranges (slab_thermal_mass ≤ 0.83 kWh/K at slab_heat_transfer 5.0, or 0.1 at the default 0.8) the twin diverges ≥ 5.28 °C within 48 steps (6/6 stiff cells, up to 1e20); the two-zone twin stays bitwise identical; `optimize()` with the batched jac returns "optimal" at objective 108.50 (cost 103.81 SEK) where the scalar jac gives 54.62 (30.08 SEK). n_sub = 1 null 0.0 on all 49 golden configs | new. A1 scope note (checked): the branch predates v6.2.8 — it is in v6.2.0's `simulate_trajectory_batch`, and the harness cell (single-zone, no DHW, uniform bounds) was batched since v6.2.0; A1 (#133) widened the reach to DHW single-zone solves and its `_grad_parity` never had a single-zone sub-step cell. Not a regression of A1 | reported |
| D2-02 | medium | With a mixing valve (`from_config` sets `cop_flow_carnot=True`) `compute_cop(T_out, flow_temp=F)` falls as outdoor temperature rises above 10–17 °C for every F in 45–70 °C: 7/7 flow cells non-monotone, COP(20 °C)/COP(peak) 0.887–0.989; `marginal_cop(T_out, 'buffer', 60 °C)` is 2.034 at 10 °C and 1.880 at 20 °C (−7.6 %) — the COP the simulation, `_terminal_cost` and `_deferred_energy_cost` price the tank at. Mechanism: the base curve's implied Carnot fraction falls 0.33→0.17 while the Carnot ratio's derivative has the sign of (T_ref − T_F) < 0. No-valve null 0 | new | closed #242 (not planned — accepted limit): no admissible formula, plan impact 0.0000 SEK |
| D2-03 | medium | The planning grid steps wall-clock time (`aware_local_midnight + timedelta(15·i min)` in `_price_series`/`_forecast_arrays`/`_Horizon.timestamps`): on all six DST days 2025–2027, 84/96 steps carry a price that is not the price in force at t0 + i·15 min (plain day 0); the spring grid maps 96 labels onto 92 real instants and the optimizer books 6.0 of the day's 29.96 kWh in the four non-existent 02:xx steps; the autumn grid holds the 02:45 CEST step for 75 real minutes at 6 kW. UTC-stepping perturbation → 0 on all six days. (Round 1 recorded "DST explicitly confirmed NOT a gap"; that suite covers the tariff slot fold, not the plan grid) | new | reported |
| D2-04 | medium | sysid confidence cannot reach the 0.3 adoption gate at the default 30-min sampling: a noise-free experiment scores 0.107 with a ceiling of 0.28 (7 rows → 0.35, comfort abort bounds the excursion factor at 0.8); at 15 min clean data scores 0.250 (rejected, UA exact) while a 0.10/0.15 K/h linear drift scores 0.304/0.341 (adopted) with UA −12 %/−24 %. Estimator unbiased under white noise ≤ 0.1 K and 0.1 K quantisation (≤ 1.4 %) | corroborates open #190 (r1 D2-01: the panel said "target the gate and estimator, not the headline"); r2 says the gate is the defect and drift, not noise, is what passes it biased. C2 inherits `sysid_bias.py` | corroborates #190 |
| D2-05 | low | `wood_share` (docstring: continuous across every boundary) jumps from (wood−hp)/margin to 1.0 as wood_temp crosses flow_set while hp_temp is within the switch margin: a jump of 1.0 in share (13.44 kW of a 13.44 kW draw) for a 1e-6 K change; `_wood_share_vec` reproduces it bitwise. One-line region-3 edit → 0 | new | reported |

#### D3 — Test-suite gaps, suite resource use

Method: 2254 deletion sites enumerated by `candidates.py`; 36 weighted
mutants (seed 20260902) plus a comment-only null; each run through its
measured closure and `env_drift --all` against the baseline in a private
scratch copy (`prescreen.py`). 18 killed, 11 survivors classified
equivalent/defensive with the reason, 7 gap candidates below. stress.py,
edge.py and backtest.py were not run (quiet window); golden.py strict does
not reproduce on this box (34/55) so `env_drift --all` stands in, as in CI.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D3-01 | medium | M31 (`sensor.py:1086`): PredictiveInsightSensor can lose all 21 published attributes (`extra_state_attributes` → {}) and none of entities.py (538 checks), `env_drift --all` (55 scenarios) or golden's coordinator captures notice — the captures record `_build_data_dict()`, not entity attributes | new; provisional | fixed (PR #402) |
| D3-02 | medium | M19 (`dhw_schedule.py:433`): `hours_until_next_window`'s inside-a-window return deleted, so `dhw_next_window_in_hours` (predictive_info, DHW view) would read the time to the following window while inside one; 0/9 closure scripts fail — every golden solve starts at 00:00, outside every window | new; provisional | fixed (PR #385) |
| D3-03 | medium | M13 (`coordinator.py:1676`): the DHW setpoint advisor's non-positive-mean-price floor deleted; 0/9 fail — no sweep check and no coordinator scenario uses a negative-price day (`profiles.summer_negative` exists) | new; provisional | fixed (PR #385) |
| D3-04 | low | M32 (`grid_fee.py:141`): `_parse_rule`'s finiteness check deleted; `is_valid_spec('Mon-Fri = nan')` is True and a NaN rate reaches `fee_vector` (the magnitude audit compares with `>` and never sees it); 0/9 fail. B3 (#206) added the sign/magnitude verdicts and their tests but no nan/inf negative (none on main) | new; provisional | fixed (PR #385) |
| D3-05 | low | M21 (`accuracy.py:382`): `AccuracyTracker.from_dict`'s non-numeric-key handler neutralised; 0/9 fail — the malformed-store check carries a NaN and a 'junk' value, never a bad key; `_async_load_accuracy` guards only `async_load()` (cross-ref D1-03) | new; provisional | fixed (PR #385) |
| D3-06 | low | M30 (`open_meteo.py:194`): the per-sample timestamp handler neutralised; 0/10 fail — a malformed `time` would then lose the whole block, and none of open_meteo.py's 30 checks carries one | new; provisional | fixed (PR #402) |
| D3-07 | low | M15 (`inputs.py:352`): `InputReader._age_minutes`' clamp dropped; a future-stamped state would publish a negative age; 0/9 fail | new; provisional — seventh on the finder's quiet-window list ("then M15"); stays provisional if only the top six run | fixed (PR #385) |
| D3-08 | low | Six closure scripts (optimality, validate, manual_plan, plan_view, card.mjs, solar_alignment) ran 30–34 mutants each and killed none, while features.py killed 12/30, entities.py 3/37, env_drift 2/37; between them the six solve 53 optimisations per gate (recorded 223 + 21 + 26 + 2 CI s). Not a deletion argument (they guard solver quality); the closure question is D3-09. Perturbation not executed | new (hygiene) | reported |
| D3-09 | low | Measured closures are the transitive package import: `__init__.py:64-77` imports coordinator and with it the whole integration, so `closures.json` lists 38–44 modules for every solver script; validate.py executes 8 of its 38, optimality.py 8/38, solar_alignment.py 8/38 (const.py is a real import-time dependency); a change to a never-executed module forces 2424 recorded CI seconds. Perturbation (lazy package import) not executed | new (hygiene) | reported |
| D3-10 | medium | The drift gate cannot fail on the five SENSITIVE fixtures: with M01 applied (`dhw_coil_draw_reduction`'s clamp deleted) `env_drift --all` reports wood_coil MAY-DRIFT with 458 leaves moved (baseline_cost 156.16 → 677.82 SEK) and returns rc 0 / NO UNCLAIMED DRIFT, because `tests/env_drift.py:109` leaves those five topologies unjudged by design; only features.py's direct coil check killed M01. Bears on the r1 D3-01 refutation, which rested on `env_drift --all` catching mutants | new (bug) | reported |

#### D4 — UI/UX

Method: the card in Chromium (Playwright 1.49 / Chromium 1148) against
HA's default theme tokens in a modelled `ha-card`, 15 arms × 26 states =
390 renders (`card_geometry.mjs`), plus a Lovelace mount-order harness
(`first_paint_font.mjs`) and a config-flow schema harness. No HA frontend
locally; tile widths modelled (359/372/400/1200 px).

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D4-01 | high | Chart text is 3.70 px on a 359 px phone tile at first paint in the order `hui-card` mounts (setConfig → hass → append), with 0 re-renders on resize (`connectedCallback`'s ResizeObserver only calls `_cacheRect()`; `_maybeRender`'s signature omits the width); when the floor does apply it yields 7.42 px, not 8, because `compactFontUnits(this._measuredCardWidth())` divides by the host width while the svg is 26 px narrower; the expanded dialog has no floor (5.6 px on a 375 px phone). Every phone tile state renders the chart at 3.70/3.84/4.16 px | regression of D4-01 / v6.2.11 (A4's 8 px floor holds only for renders that happen attached, and not in the dialog) | regression: v6.2.11 |
| D4-02 | high | Schedule-editor targets: `rect.lane` 5.5/5.6/11.8/19.9 px tall (phone tile / phone dialog / tablet / desktop dialog; `LANE_H` 15 viewBox units, never floored) and this plan's slots 1.3–22 px wide on a phone; 1,883 targets under 24 px with no spacing rescue across 15 arms (slots 1,344, lanes 367); the lanes are also focusable in the compact tile where editing is disabled | new | reported |
| D4-03 | medium | Axis labels collide at the plot corners in every chart state: the value-axis unit label overlaps the top tick label by 1.9 px (phone) to 8.4 px (desktop dialog), and on tiles ≤ 400 px the first time label overlaps the left axes' bottom tick — 1,039 overlapping text pairs in 390 renders ('60'~'°C' 260, '400'~'W/m²' 245, '6'~'kW' 232). A different pair from r1 D4-03's lane-row collision | new | reported |
| D4-04 | medium | The empty state's `<code>` entity ids spill 31–44 px past the card box on 359 px tiles (26 px at 372, 14 px at 400; 48 overflow rows): `.empty` has no `overflow-wrap` | new | reported |
| D4-05 | medium | Primary-colour text and the Save button render at 2.63:1 in HA's default light theme (`--primary-color` #03a9f4): the what-if actions, the layout verdict and the now/» markers at 12 px on white, Save as white on #03a9f4 in both themes — 891 light-theme text boxes below AA (wi-save 150, wi-pin 90, wi-apply 90, markers 207) | new | reported |
| D4-06 | medium | Opacity-faded active content below AA: `.setup-slot.empty` (the rows that say which sensor is missing — the setup page's purpose) at 2.99:1 light / 4.04:1 dark in 9.3 px on a phone, 600 boxes; `.chip.off` (an active toggle) at 2.43:1 light, 45 boxes | new | reported |
| D4-07 | medium | With a coarse pointer no control grows: 548 targets under 44 px on the coarse arm (setup rows 11.7 px, remove buttons 13.2, range inputs 16, zoom 17.3, layout-bar 18.1, chips 22, dialog tabs 23.7, what-if buttons 24.4); the card's only coarse adaptation is `LANE_EDGE_GRAB_COARSE` | new | reported |
| D4-08 | low | Three of seven `SERIES_DEFS` colours below WCAG 1.4.11's 3:1 on the light background: price #f5a623 (2.03), solar #f2c94c (1.59), house temperature #2fae7a (2.82); dark 0/7 | new (hygiene) | reported |
| D4-09 | low | Form length and grouping: the first setup screen carries 17 fields of which 13 are optional entity pickers; hot_water (23), entities (22), learning (18), grid (18) and thermal_model (16) exceed 15 fields; hot_water's `space_circulation_pump_entity` is off-theme | corroborates open #198 (r1 D4-09, the 18-field learning page) and widens it to five pages and the user step | corroborates #198 |
| D4-10 | low | Submitting the DHW setup step with its own defaults (setpoint 55, anti-legionella 60) logs one WARNING, while `coordinator.py` exempts exactly this stock pair from the `dhw_legionella_above_setpoint` notice | new (hygiene) | reported |
| D4-11 | low | `CARD_VERSION` 5.4.17 in a 6.2.14 release; the console banner misreports it and the duplicate-copy guard (`cardVersion !== CARD_VERSION`) cannot tell two 6.x copies apart. Still true on main: card 5.4.19 vs VERSION 6.3.0; `tools/release/stamp.py` does not touch it | new (hygiene) | reported |
| D4-12 | low | "the same than the saved plan": `stats.delta_detail` ('{verdict} than the saved plan') composed with `stats.the_same` (1 of 3 verdicts); the Swedish template is right for all three | new (hygiene) | reported |

#### D5 — Docs structure, flow, content; code comments

Exposure: none of the audit records; earlier finding ids seen in code and
test comments as context; plan documents' headings read to classify them
for the link graph (recorded in the report).

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D5-01 | low | tests/README.md contradicts the tree in seven statements: the inert-file list (closure.py's INERT deliberately excludes README.md, RELEASE_NOTES.md and the brand images), 53/47 fixture counts (tree: 55/49), `/tmp/plandata.json` twice (per-checkout hashed path), a NOT_A_TEST roster of four (seven), no paragraph for the browser lane (`card_browser.mjs` + CI job), 18 validate scenarios (22). r1 D5-05 fixed two other omissions in the same file | new | reported |
| D5-02 | low | configuration.md:457 ("Leave blank if you do not have one") and :70 ("default sensibly when absent") contradict the shipped defaults and ecl110.md:79-82: both ECL110 topics ship non-empty and `async_publish_ecl110_command` publishes every cycle unless *both* are empty, logging ERROR on failure — on an install without the MQTT integration real HA raises ServiceNotFound every interval (the stub's `FakeServices` returns None, so no test sees it). Still true on main | new — a docs finding with a code implication; flagged for the D10 fix group (default the topics empty, or gate on the MQTT integration) | reported |
| D5-03 | low | tests/README.md, docs/plan-card-decomposition.md and docs/plan-open-issues.md are unreachable from README.md by relative links (3 documents); architecture.md names the test scripts but never links how the tests are run | new | reported |
| D5-04 | low | Five content defects: how-it-works.md:562-565 does not parse ("may move within follow"), :1189 is an unwrapped 134-character insert whose following "Without it" now refers to the wrong noun, README "Project status" names v5.0.0 newest at VERSION 6.2.14, "throttling valve" used 8× in configuration.md and defined on no page, dashboard-card.md h1→h3 skip at :31 | new | reported |
| D5-05 | low | Comments: open_meteo.py:66-69 says surface GHI "cannot exceed" the ~1361 W/m² solar constant beside `_MAX_PLAUSIBLE_GHI = 1400.0`; thermal_model.py:191 names "the set_thermal_params service" (it is `set_thermal_parameters`); coordinator.py:4353, optimizer.py:671, thermal_model.py:1830 restate the next line. Otherwise 872 strict + 209 loose symbol refs resolve and 65 numeric-constant comments agree | new | reported |

#### D6 — README and metadata claims

Method: a 300-row claims table (`claims_table.md`) executed against the
real platforms, the service registry, the config-flow schemas and the
constants; `rolling_learning.py` re-executes the documented reference run.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D6-01 | low | README:259 says the tables show the English names, but 9/55 sensor-table names lack the "(lifetime)" / "(next 24 h)" qualifiers the strings.json names carry. Still true on main after #205's renames (README: 0 qualified rows; strings.json: 9) | new | reported |
| D6-02 | low | services.yaml `set_thermal_parameters.wind_sensitivity_factor` has example 0.15 and says "0.15 means 15 % more heat loss per m/s" while `DEFAULT_WIND_SENSITIVITY` is 0.03 and const.py documents 0.15 as the replaced default. Still true on main (#206 changed only the `apply_manual_plan` examples) | new | reported |
| D6-03 | low | services.yaml declares min 0.0 for `inter_zone_heat_transfer` and min 0 for `window_area`, but `SERVICE_SCHEMA_SET_THERMAL_PARAMS` binds both through `_positive()` = `vol.Range(min=0.01)`: 2/39 selector bounds the call refuses (configuration.md says 0.01, matching the schema). Still true on main | new | reported |
| D6-04 | low | The "6.7 → 0 degree-hours" reference run quoted in README:486-487 and how-it-works.md:1237-1238 does not reproduce: `tests/rolling.py`'s own `run_rolling` gives 9.634 → 0.044 deterministically (two runs bit-identical); the figures are a comment (`rolling.py:452-453`), not an assertion (which is only `breach_learned < breach_plain`). Null (plant_error 1.0): 0 → 0. Machine-dependent, so the fixture machine may give a third pair | new | reported |
| D6-05 | low | DISCLAIMER.md:71-72 calls the savings baseline "a simulated always-on thermostat"; `HeatPumpOptimizer._compute_baseline_power` simulates a conventional thermostat following the per-step comfort schedule (a night setback is not booked as savings); only the hot-water baseline is always-hot, which README:271 states correctly | new | reported |

#### D7 — Architecture and maintainability

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D7-01 | medium | Active system identification cannot identify the production two-store plant: `SystemIdentification.identify()` completes with a usable fit (confidence ≥ 0.3, the `_adopt_system_identification` gate) in 0/24 preset × cadence × noise × bound cells driven against the production `ThermalModel` (the step's heat enters the slab store; during RELAX the room rate stays positive at zero input, which the first-order regression resolves as a wrong-signed coefficient); a first-order control plant is admitted in 4/8 cells with abs(bias) ≤ 8.06 % (positive control). The comfort abort is checked only at sample instants (0.92 °C reached against a 0.8 °C bound) | corroborates open #191 (r1 D7-02: first-order plant on a ≥ 2nd-order house, "inert on target houses"); r2 executes the 0/24 and shows a two-store LS fit identifies UA from the same samples (0–6.4 % bias). C2 inherits `sysid_plant.py` | corroborates #191 |
| D7-02 | medium | The defrost flag freezes the COP learner but not the fabric learners: a defrost-flagged interval in the frost band is rejected by `_learn_measured_cop` and ingested by `_async_learn_house_heat_loss` / `_async_learn_lower_floor_loss`, which replay the *commanded* power, so the delivered-heat shortfall is booked as heat loss: two-zone radiator house `house_heat_loss_scale` 1.0414 at 20 % defrost intervals, 1.0953 at 50 % (400 × 30-min intervals); f = 0 null 1.000000; single-zone 1.000000 (all heat via the slab store) | new — the same freeze-gate asymmetry family as open #192; C2 candidate | reported |
| D7-03 | low | `_record_accuracy` skips `AccuracyTracker.record` only on a pump-signal freeze (`_pump_signals.freeze_reason is None`); intervals frozen for every learner by an open window or an external heat source are still recorded and feed `_confidence_margins` and `temperature_bias()` (ingest 1/1 in both arms); pump-offline null 0. The lead-time scoring three statements earlier already uses `_learning_frozen(CONF_INDOOR_TEMP_ENTITY)` | corroborates open #192 (r1 D7-05, exactly; one-line guard) | corroborates #192 |
| D7-04 | low | `ThermalModel.last_buffer_trajectory` is a side channel worth 5.42 SEK (7.1 % of the schedule's energy cost) on a store configuration if any simulation intervenes between writer and reader; A1's batch poison fires on a stale read (poison_raises = 1); today all four production readers are adjacent to their writer (0 with a model call between); no-valve null 0.000 | new (hygiene) — re-measures released D7-04 (v6.2.8): the containment holds, the attribute remains; a candidate wontfix or a four-call-site return-value refactor | reported |
| D7-05 | low | `HeatPumpOptimizerCoordinator`: 10,269 lines / 256 methods / 174 instance attributes (132 multi-writer); its `_init_*` groups share 30.9 % of attribute references and 66.1 % of self-calls across boundaries; no clustering at k = 6..16 gets cross-cluster attribute references under 0.33; the only seam with cut cost under 40 is the manual-plan group (10 methods, cut 17). Six hub attributes bind the class (`_config` read by 77 methods, `_thermal_params` 63, `hass` 42, `_current_state` 36, `_opt_config` 32, `_current_action` 23) | corroborates open #193 (r1 D7-01; the decomposition program): r2 re-measures with the tree grown 10,041 → 10,269 lines and adds the seam order — manual plan 17, ECL110 15, measurements 48, insurance 67, hub attributes into a context object first | corroborates #193 (closed 2026-09-10; see D7-01) |
| D7-06 | low | Five dead defs (46 lines) never started by thirteen gate scripts (`sys.monitoring` PY_START sentinel) and unreferenced in production and tests: `ComfortLearner.set_configured`, `config_flow._translated_text`, `HeatPumpOptimizerCoordinator.optimization_result` and `.current_state` (properties), `presets._floor_heated_area`; six further production defs (140 lines) are started only because tests call them. The four CONF keys are not in this list | fixed since baseline by #205 (v6.2.17) for `_translated_text` and `_floor_heated_area` (r1 D7-06); #205 named the three member-level ones as out of its scope, so they and the six test-only defs remain (partial) | fixed since baseline by #205 (partial) |

#### D8 — Sensor verification and ordering

Method: 85 cells (17 topologies × 5 input arms) × 2 cycles × 65 entities
through the real platform setups over a real coordinator (`matrix.py`);
11,050 snapshots; two full runs identical.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D8-01 | high | `ThermalState()` constructor defaults (55/40/22/21/5 °C) are published as available temperatures, or values derived from them, through five ungated paths while `_MeasuredTemperatureMixin` makes the corresponding temperature sensors unavailable: climate attributes (dhw/slab/lower/upper/current), Mixed Hot Water (300.0 L / 37.5 shower minutes from the 55 °C default, available without a tank reading in 38 cells), Thermal Battery components and SOC, Indoor (21.0) and Outdoor (5.0 while the plan is solved on the forecast; Estimated COP follows it: 3.32 vs 2.62/2.19 at the real −3/−8 °C) — 1,132 publications over 85 cells × 2 cycles; probes arm 0/5 cells; dhw default 55 → 50 moves Mixed Hot Water 300.0 → 266.7 L | new | reported |
| D8-02 | low | numpy scalars reach entity attributes at three sites (Optimization Schedule `schedule[i].solar_gain` in 85/85 cells, Savings Percentage `deferred_energy_cost`, climate `predicted_savings`) and the Predicted Savings state (30 snapshots in the valve-storage/two-tank/coil cells), bypassing `_plain_types`, which `_build_data_dict` applies to `predictive_info` only | fixed since baseline by #205 (v6.2.17; r1 D8-01/#173): `sensor._finite` now unwraps `np.generic`/`np.ndarray` before the finite test on every sensor's state and attributes, which covers the two sensor sites and the state. The climate attribute site (`climate.py:186`, not a sensor subclass) is outside that scrub — judge re-check on main with `matrix.py` | fixed since baseline by #205 (residual: climate attribute) |
| D8-03 | low | Optimization Schedule and DHW Heating Schedule are built from `result.*[:24]` / `[1:25]` — 6 h at the 15-minute step — while the README row says "the whole 24 h schedule, in attributes" and the plan sensors carry 96 steps; their states ("24 steps", "N heating periods" counting quarter-hour steps) never move between cycles: 170/170 (cell, cycle) pairs truncated | new (hygiene) — README or slice; golden drift on every coord_* fixture if the slice changes | reported |
| D8-04 | low | Alphabetical order splits ten hand-listed families: 15 splits in entity-id order (dhw 2, tariff 2, learning 2, accuracy 1, card_headline 3, lifetime 2, two_zone 3), 15 by English name, 16 by Swedish name | fixed since baseline by #205 (v6.2.17; r1 D8-03/#174) for the DHW family; the other families' splits (13 of 15) are residual hygiene — the judge decides whether they warrant a naming release (partial) | fixed since baseline by #205 (partial) |

#### D9 — CPU and memory efficiency (Pi-class)

Method: call-count hooks on `simulate_step` / `simulate_trajectory_batch`
and scipy's `nfev`/`njev` (final numbers), CPU ratios against
`tests/stress.py:reference_solve` (final), a 1 ms heartbeat on a real loop
(wall, provisional). Pi factor ×7, an assumption stated once. Thread pin
1.000 ± 0.0002 on every harness.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D9-01 | high | One zero-range bound puts the whole solve on the scalar FD path: a forced-off manual pin, or `power_caps_extra` equal to the DHW run power (0.8 p_max) at the steps hot water is planned, makes `_bounds_supported_by_batch` return False, `_multi_start_minimize` passes jac=None and scipy estimates every gradient with n scalar trajectories — 9,222 simulate-step equivalents per gradient and 1.5–1.6 M steps (710–751× the reference solve) instead of 297 per gradient and 38× on the identical solve without the pin/cap (5-cell leave-one-out 9,036–9,295). The golden fuse_guard fixture is already on this path (731,904 steps; D0's harness independently raced it on the scalar path, non-finding). Pi (×7): 2–3 min per solve every 30 min with the loop starved (D9-05) | new — the residual of A1's deliberate scope (v6.2.8 "minus zero-range bounds": the one-sided FD step is 0/0 there); behaviour on these solves is what it was before A1, so not a regression, but untracked until now. Fix: treat lo == hi as fixed variables in the batched jac | reported |
| D9-02 | medium | The stress gate cannot see a 2× or 4× solve regression at the baseline: the worst scenario is 298.8× the reference against `SOLVE_BUDGET_RATIO` 1400 and the sweep 50.7× against 450, so the smallest detectable uniform regression is 4.69× (measured twice: 4.69, 4.67; a doubled `optimize` trips 0 per-scenario and 0 sweep checks); no CI override of either ratio; no memory line anywhere in tests/*.py | fixed since baseline by #145 (A6, v6.2.16; r1 D9-03/#166 and D9-04/#167): per-scenario budgets at recorded × 3 (floor 10×), a stale-table check, `ru_maxrss` + tracemalloc peaks per scenario — the 4× arm and the memory gap are covered; a uniform 2× still passes a ×3 factor. Judge re-check on main with `h7_stress_gate.py` (provisional: CPU ratio) | fixed since baseline by #145 (v6.2.16); single-scenario 2× arm fixed (PR #378), released v6.3.11 — by evaluation count, not CPU; a same-basin cost-per-evaluation regression is still caught only at the 3.0× CPU factor (see #346) |
| D9-03 | low | The batched jac re-evaluates f(x) scipy just computed: each gradient costs 96 batch rows plus 201 scalar simulate_steps (two full scalar trajectories) because `jac(x)` recomputes `objective(x)` for its f0 right after `ScalarFunction` evaluated it (nfev == njev == 103); a one-entry memo halves the scalar steps to 101 per gradient (equivalents 297 → 197) and cuts solve CPU 13 % (908 → 789 ms, provisional); batch rows unchanged at 96 (null) | new | reported |
| D9-04 | low | DHW planning costs 3.4–3.8× a reference solve and 63 % of a single-zone winter DHW solve's CPU: one `_build_dhw_requirements` call is 64 `simulate_dhw_only` calls (6,144 Python-loop tank steps, 7,084 `compute_cop_dhw` calls), of which `_apply_dhw_min_run`'s per-slot re-simulation is 43–59 %; two calls per winter DHW solve (`_co_optimize` re-plans); at 48 h 118 calls / 22,656 steps (13.5× reference). Counts exact; the share is provisional ± 15 %. (Round 1's "DHW planning 0.5–13 % of cycle" used the cycle as denominator) | new | reported |
| D9-05 | medium | The solve starves the event loop for its whole duration: with the solve in a `ThreadPoolExecutor` under a real asyncio loop, a 1 ms heartbeat wakes every 13–15 ms instead of 1.3 ms for 96.7 % (batched two-zone DHW, 0.8 s) to 99.8 % (D9-01 path, 14.7 s) of the solve's wall; longest contiguous hold 39–75 ms inside `simulate_trajectory_batch`; idle null 0 (2.1 ms, 779 ticks/s on the same loaded box); the two `time.sleep(0.002)` yields sit between L-BFGS-B starts and between the DHW and space stages, never inside an iteration; `sys.setswitchinterval(0.05)` moves the hold 39 → 83 ms and leaves the share at 0.96. D1 reports no executor-starvation item to merge | corroborates open #199 (r1 D9-02 / M1 residual after A1: starvation ~75 % then); r2 measures the residual at 0.97 on the batched path and proposes a process executor over the already deep-copied snapshot. The fix group inherits `h3_gil_hold.py` (provisional: wall) | corroborates #199 |

#### D10 — HA quality scale

Exposure: README.md, docs/*.md and DISCLAIMER.md read for the docs-* rules;
`quality_scale.yaml` written by the finder with the executed verdict per
rule.

| ID | Sev | Finding | Class | Status |
|----|-----|---------|-------|--------|
| D10-01 | medium | Nothing prevents a second config entry: 0 duplicate-entry guards in config_flow.py/manifest.json (`abort.already_configured` in strings.json unused); with one entry present the user step returns the temperature form (0/1 aborts). Two entries pin the same suggested entity ids (the second gets `_2`, breaking the card's id-suffix discovery), every service loops over both coordinators, two MPC solves per interval | fixed since baseline by #207 (B5, v6.3.0; r1 D10-03/#182): `entry_identity` (token + the first screen's entity slots) as unique id, `_abort_if_unique_id_configured`; a second heat pump with its own entities still proceeds; entries created before v6.3.0 carry no unique id (noted in #207 as a one-function follow-up). Judge re-check with `check_rules.py` on main | fixed since baseline by #207 |
| D10-02 | medium | A rejected Tibber token is reported as a transient `UpdateFailed`: 0/3 auth-failure responses (401, 403, 200 + errors payload) raise `ConfigEntryAuthFailed`; no `async_step_reauth`; setup retries forever and the reauth repair never appears. The trailing `except Exception` in `_fetch_tibber_prices` converts anything raised inside the request block, so the fix must re-raise `ConfigEntryAuthFailed` ahead of it (a first perturbation without that stayed at 0/3) | fixed since baseline by #209 (C1, v6.3.1; r1 D10-08/#187, still open at commit time): the coordinator starts the entry's reauth flow on HTTP 401/403 once per outage, re-armed on recovery, with a `reauth_confirm` step (EN + SV) — the two status arms; the 200 + errors-payload arm stays an `UpdateFailed` by C1's design ("unambiguous refusals"). Judge re-check on main with `check_rules.py`; the except-ordering trap the finder hit is what C1 had to clear | fixed since baseline by #209 (errors-payload arm to re-check) |
| D10-03 | low | Three consecutive failed refreshes produce four ERROR records with tracebacks: `_tibber_fetch_failed`'s latch logs once (the fetch alone three times: 1 ERROR, null control), but `_async_update_data`'s trailing `except Exception` logs `_LOGGER.error(..., exc_info=True)` on every `UpdateFailed` it re-raises (real HA's coordinator adds its own single ERROR on top); a day-long outage is 49 tracebacks. D1's guards harness independently records "ERROR logged every cycle (no log-once latch)" on the `UpdateFailed` paths. Still true on main (`coordinator.py:4459`, `:4502`) | regression of D10-09 / v6.2.12 (B1's latch was verified on the fetch alone; through the refresh path the outcome D10-09 named — the same ERROR every poll — persists) | regression: v6.2.12 |
| D10-04 | low | Service actions swallow operational failures: with no price data `run_optimization` returns None after a WARNING, `restore_learned_snapshot` answers `{restored: []}`, `simulate_plan` `{'error': 'no_plan'}` — 3/3 return instead of raising; the handlers raise `ServiceValidationError` for bad input (14 sites) but never `HomeAssistantError` for a failed operation, and `async_run_optimization`'s own `except Exception` swallows a raise placed inside it (the raise must sit in the handler). B5's `ServiceValidationError` covers only the no-loaded-entry case | new | reported |
| D10-05 | low | Two buttons stay available after a failed refresh: `ForceOptimizationButton.available` and `SystemIdentificationButton.available` return their own flag without ANDing `CoordinatorEntity.available` (every sensor mixin does) — 2/65 entities available with `last_update_success` False; pressing Optimize now during an outage triggers another failing refresh. Still true on main (`button.py:86`, `:114`) | new — a residual of B1's D10-07 fix (v6.2.12), which made the other 63 entities go unavailable | reported |
| D10-06 | low | All 11 services are registered in `async_setup_entry` (no `async_setup`) and removed after the last unload, so automation validation cannot see `heatpump_optimizer.*` while no entry is loaded | fixed since baseline by #207 (v6.3.0; r1 D10-01/#180): 11 services in `async_setup`, `_loaded_entries` resolves targets at call time, none removed at unload | fixed since baseline by #207 |
| D10-07 | low | No platform declares `PARALLEL_UPDATES` (0/5) | fixed since baseline by #207 (v6.3.0; r1 D10-10/#184): sensor/binary_sensor 0, button/climate/switch 1 | fixed since baseline by #207 |
| D10-08 | low | 24 `hass.data[DOMAIN]` references in seven files and 0 `ConfigEntry.runtime_data`; the five `CoordinatorEntity` base classes live in the platform files, not `entity.py` | fixed since baseline by #207 (v6.3.0; r1 D10-02/#181): `hass_data_domain_reads` 24 → 0, typed `HeatPumpOptimizerConfigEntry`, HA floor 2024.6.0; the `entity.py` half (common-modules) remains — residual hygiene (partial) | fixed since baseline by #207 (partial) |
| D10-09 | low | 0/14 `ServiceValidationError` raises carry `translation_domain`/`translation_key` and strings.json has no `exceptions` block, so every service error reaches the UI in English on an integration that ships Swedish. Still true on main (12 raises, 0 keys, no block) | new (hygiene) | reported |
| D10-10 | low | 64 `_attr_icon` assignments across the platform files and no icons.json (icon-translations, HA ≥ 2024.2) | corroborates open #189 (r1 D10-13): after #207 the floor is 2024.6.0, so the floor objection is gone; C1 (#209) deferred icons.json with the reason recorded (a class-to-unique-id registry first, B4 having just renamed half the family) | corroborates #189 |
| D10-11 | low | No diagnostics platform: `diagnostics.py` absent, 0 `async_get_config_entry_diagnostics` defs, for 149 published keys, thirteen learners and a token that would need redaction; sensor docstrings mention "the diagnostics dump" | fixed since baseline by #209 (C1, v6.3.1; r1 D10-12/#188, still open at commit time): `diagnostics.py` with the token redacted wholesale and a small coordinator snapshot, mutation-proved both ways | fixed since baseline by #209 |
| D10-12 | low | Docs gaps: 0 removal-instruction matches (Bronze), 0 "Known limitations" sections, 0 blueprints or automation examples, 0 supported/unsupported-devices statements over README.md, docs/*.md and DISCLAIMER.md | fixed since baseline by #207 (v6.3.0; r1 D10-05/#183) for the removal section (README "### Removal", test-pinned to the coordinator's store keys); "Known limitations", blueprints and a supported-controls statement remain — residual hygiene (partial) | fixed since baseline by #207 (partial) |
| D10-13 | low | `mypy --strict` (2.3.1, python 3.13, stub on MYPYPATH): 722 errors in 37/45 modules — no-untyped-call 227, type-arg 111, no-untyped-def 106, attr-defined 90, no-any-return 79, union-attr 25; worst coordinator.py 172, sensor.py 144, config_flow.py 114 | corroborates open #197 (r1 D10-15 counted 160 under a different invocation; the tranche should fix the invocation first) | corroborates #197 |
| D10-14 | low | Statement coverage 88.4 % of 12,877 statements over the gate's Python scripts (one run; the 1818 s wall is provisional, the ratio is a count); 20/45 modules reach 95 %; config_flow.py 86.4 % against the 100 % rule — at the baseline 0 tests submit `async_step_user` with input (B5 has since added the first three); lowest: climate.py 59 %, open_meteo.py 67 %, diagnosis.py 77 %, coordinator.py 78 %, frontend.py 80 % | corroborates #195 (closed by #889, released v6.4.3; r1 D10-11: 95 % bar) and #194 (r1 D10-04: config-flow test coverage) — the tranches inherit `coverage_suite.sh` and `coverage/per_module.tsv` | corroborates #195 (released v6.4.3), #194 |
| D10-15 | low | Declarative metadata: `solar_surplus_forecast` and `dhw_heavy_day_demand` publish kWh without `SensorDeviceClass.ENERGY` (5 sensors flagged, the other 3 are °C deltas and correctly classless); `DeviceInfo` without `entry_type=DeviceEntryType.SERVICE` and with manufacturer "Custom" | new (hygiene) | reported |

### Dedup — merges across dimensions

75 findings reported. **No two findings from different dimensions describe
the same phenomenon, so no M-id is issued this round.** The candidate pairs
the dedup step examined, and why each stays apart (cross-references are in
the rows above):

- **D8-02 vs a D4/D10 numpy item** — neither D4 nor D10 reports one (D2's
  non-finding "np.clip passes NaN through in all four learner clamps" is a
  different phenomenon). D8-02's match is cross-round: r1 D8-01/#173, fixed
  by #205.
- **D9-05 vs a D1 executor-starvation item** — D1 reports none; D1-05 is a
  shared-reference race on the what-if's executor path, not starvation.
- **D1-03 (store loaders) vs D10** — D10 has no store-loader item. The
  nearest is D3-05 (the accuracy store's key-side handler is untested):
  same file, different claims (a missing production guard vs a missing
  test), and neither fix subsumes the other (a loader-level `try/except`
  would swallow D3-05's mutant without any test noticing). Cross-referenced
  both ways, not merged.
- **D9-01 vs D0's zero-range remark** — D0's is a non-finding (fuse_guard
  raced on the scalar path, gap 0.281 SEK); cited in D9-01's row as
  corroborating evidence.
- **D2-04 vs D7-01** (both: sysid never adopts a result) — two mechanisms
  (the confidence formula's ceiling vs the model order), two open issues
  (#190, #191); kept apart, both land in fix group C2.
- **D7-02 vs D7-03 vs #192** — three freeze-gate asymmetries; D7-03 is #192
  exactly, D7-02 (defrost vs fabric learners) is new; kept apart.
- **D0-01 vs D0-02** — the same "FACTR fires at a non-stationary point"
  stop and the same proposed restart rule, but different landscapes (top-k
  plateau vs two-zone ill-conditioning) with different null behaviour;
  within-dimension grouping is the finder's and stands.

Net: **75 distinct findings** — 51 new, 9 corroborating an open round-1
issue, 11 fixed since the baseline (7 with a residual for the judge), 2
regressions of a released fix, 2 matching a round-1 refuted finding. **55
rows go to the panel** (new + regression + refuted-match, the two
regressions first: D4-01, D10-03); 9 attach to their issues; 11 go to the
judge's re-check on main.

### Rejected at intake

None. All 75 findings carry every required field, valid enums and patterns,
a `null_control` wherever `cpu_or_wall` is `cpu`/`wall`, and
`leave_one_out.cells ≥ 5` where present (`scratchpad` script, run against
the schema by hand; no `jsonschema` on the box).

Flagged at intake (schema-valid; for the judge, not grounds for rejection):

- **Thread-pin contract**: D1-01/D1-02 report `thread_factor` 58.4 and D1-05
  346.1 against the pin's 1.0 — the real-loop harnesses' process/thread CPU
  ratio is not measuring what the contract means. Every D1 number is a
  count, so nothing rides on it; the quiet window re-takes the factor.
- **Perturbation not executed** (the schema does not require an observed
  value; the judge runs it): D1-02, D1-03, D1-05, D8-02, D8-03, D8-04,
  D10-06…D10-15 (no observed value); D3-08, D3-09 ("not executed"); D5-01…05
  ("predicted"). D0, D2, D4, D6, D7, D9 and D3-01…07, D10-01…05 executed
  theirs.
- **Modelled core semantics**: D1's `lifecycle_realloop.py` implements
  `ConfigEntry.async_setup`/NotReady/reload from memory of core (GitHub was
  off limits); its header states each assumption for the panel to check.
- **Assumed Pi factor**: D9's ×7 is an assumption stated once; every Pi
  number derives from a measured M1 count.
- **Provisional survivors**: D3-01…07 are marked provisional by the finder
  pending the full-gate quiet window (below).

### Non-findings verified

Each report lists what was checked and held with the command and the
number; the headlines, so the next round does not redo them:

- **D0 (13)**: single-zone default solves are at their optimum (16 arms tie
  to 1e-6; the 80-cell single-zone grid mean gap 0.041 SEK); the DHW ↔ space
  decomposition converges in one pass (pass-2 gain 0.000 × 20); the terminal
  credit does what its docstring says (19/20 tails dumped without it); the
  pre-refinement discard rarely loses the winner (the third candidate is
  best in 0/160 grid cells — bears on open #186); the receding horizon does
  not realise the two-zone single-solve gap (≤ 0.22 SEK / 2 d); 6 h and
  48 h horizons at or near optimum; a capacity tariff realises no peak
  charge in either closed-loop arm.
- **D1 (16)**: reload during the first solve and unload-then-setup leak
  nothing (listeners, MQTT subs, timers, futures, instances all 0); no
  exception escapes any lifecycle scenario; Tibber down at boot fails
  honestly and recovers; the live solve reads only copies (0/26 torn);
  clock steps mark the plan stale / clamp its age; InputReader rejects
  unknown/unavailable/3 h-old readings; three failed solves raise the
  repair issue and stop actuation; no corrupt store takes the loop down
  (2000/2000); a Store OSError never breaks the cycle; the five
  DEBUG-swallowed sites recover. Two hygiene observations recorded, not
  raised: `weather_stale_hours` reads −2.0 after a backward clock step;
  `_command_valve_target` / `_file_lead_predictions` failures log
  "Optimization failed" every cycle although the solve succeeded, and the
  failure counter is reset before it is incremented so the repair issue
  cannot trip (cross-ref D10-03).
- **D2 (31)**: energy conservation ≤ 4e-13 kWh (space, DHW coil, n_sub = 3,
  learned gains); the batched twin bitwise on all 49 golden configs and 3
  stiff two-zone cells; batched jac == scipy's 2-point on the default
  house; Euler first order (4.29/4.44); more power never cools a store
  (0/2160); caps clamp rates, refused heat booked; cost / savings / peak /
  PV / compressor-start identities on 49 fixtures (≤ 1.5e-4); COP monotone
  in flow and DHW temperatures; defrost derate bounded; metering windows
  conserve; PeakTracker bills the monthly peak once; grid-fee rules at
  month/weekday/wrap boundaries 0/7; `_known_prices_for` 0 mismatches on
  five spacings; learner clamps hold at both band edges (np.clip passes NaN
  in all four — reachability not traced); sysid unbiased under white noise
  ≤ 0.1 K and 0.1 K quantisation.
- **D3 (35)**: the comment-only null survives everything; 18 mutants
  killed (features.py 12, entities.py 3, env_drift 2, frontend 1,
  open_meteo 1) and 11 survivors classified equivalent/defensive with the
  reason each; the shared drift cache was hit 37/37 and never written;
  golden.py strict does not reproduce here (34/55); thread pin 1.000;
  recorded closure seconds are CI seconds (~14× this box); the may-drift
  fixtures moved for 1/37 mutants (that one is D3-10).
- **D4 (16)**: 0 console errors in 390 renders; 0 hover layout shift; 0
  focus stops without an indicator; every dialog focusable reachable by
  Tab; the phone setup diagram scrolls (6/6 hits reachable); 0 nowrap
  overflows; Swedish complete (686 leaves, 232/232 card strings); every
  field has help text; every error key, select option and menu label
  translated; every default in range and every page accepts its own; no
  key on two options pages; install is 7 screens with 2 must-know fields;
  reduced motion drops only the zoom fade; series colours 7/7 on dark;
  setup rows ≥ 11.7 px.
- **D5 (17)**: 0 broken internal links or anchors outside the
  export-removed backlog; 6/6 external links answer 200; no README/docs
  duplication (one near-duplicate sequence diagram); 872 + 248 + 357
  backticked symbols resolve; docstring defaults match; architecture.md's
  45 modules / 10 HA importers hold; 11 services, 28/11/21 field counts,
  55-row sensor table, 6 disabled, 65/55 entities, card 900×380 / 168 h /
  232 strings; version citations historical.
- **D6 (26)**: 65 entities through the real platforms; sensor/binary/
  button tables match the rosters; units 55/55; diagnostic marks 0
  mismatches; documented attributes present; 11 feature gates flip
  availability; 11 services = README = services.yaml, 35/35 examples pass;
  25 ranges, 41 defaults and constants, 71 NumberSelector ranges, 12
  described mechanisms, 13 option pages — all as documented; the rolling
  learning *property* holds (99.5 % of the breach removed, null 0 → 0);
  10/10 external links; 10 rows unverifiable in the export (backlog, six
  historical measurements).
- **D7 (14)**: 0 import cycles; every `last_buffer_trajectory` reader
  adjacent to its writer; the batch poison fires; `_learning_frozen`
  freezes all seven thermal learners on open window / pump offline /
  external heat (the accuracy tracker excepted — D7-03); the COP learner's
  defrost gate works; the single-zone house learner is immune to
  delivered-power error; a first-order plant is admitted (the sysid harness
  can pass); a two-store LS fit identifies UA (0–6.4 % bias); every
  production addition of this year's train has a test that fails when it is
  deleted (11/11); the scoped gate scopes and falls back to FULL; the suite
  starts 983/1062 defs.
- **D8 (13)**: 0 entities unknown where their data exists (11,050
  snapshots); 0 type or metadata violations; 0 NaN/inf/set/non-str-key
  attributes on any platform; 0 stale entities; 41 numeric readers follow
  their payload; 0 exceptions; entity ids, unique ids and icons clean;
  translation keys identical across strings/en/sv; the disabled set is the
  six; feature gating works (18 enabled-unavailable on the minimal install,
  0 on all-features + probes); 85/85 cells solve optimal in both cycles.
- **D9 (11)**: one `optimize()` per cycle (two `_multi_start_minimize`
  entries: solve_space + the co-optimise re-solve); what-ifs bounded (price
  tiles +1 solve, fuse advisor weekly, card 3 s rate limit); loop-thread
  work 0.4–0.5 % of the executor's (3.1–3.6 ms); no untrimmed collection
  (0.5–0.8 KB/cycle, the accuracy history filling to 672); traced growth
  1.68 KB/cycle in own lines, `ru_maxrss` noise; 2.1 Store saves and 7–10
  KB per cycle; payload 52.7 KB/cycle, 83 % recorder-excluded, ≤ 514
  KB/day recorded; 48/48 stress combinations on the batched path;
  single-zone solves 2.7× / 6.1× reference; the two sleep yields where the
  brief says; thread pin 1.000.
- **D10 (24)**: appropriate-polling 1800 s; a real brands icon; every flow
  field has a data_description; dependencies transparent 3/3; docs-actions
  11/11; no custom triggers or conditions; docs high-level / installation /
  troubleshooting / use-cases / data-update present; 12/12 options pages
  and 17/17 user labels documented; 65 entities, 65 unique ids,
  has_entity_name; entity-event-setup clean (4 unsubscribes); test-before-
  configure 3/3 branches; the first refresh in setup; config-entry-
  unloading (11 → 0 services, base shutdown called); codeowners; one
  service device; discovery exempt; 12 diagnostic entities; 6 disabled;
  translations 0 missing; 11 repair issues translated; async-dependency (0
  sync HTTP, 5 executor offloads); inject-websession 3/0; the log-once
  latch works on the fetch alone (the surplus is D10-03).

### Provisional numbers pending the quiet window

Rows `round2/quiet.json` (at `d5d8c4a`) must update when it lands (a
quiet-window agent is re-taking every provisional number and running the
full gate for D3's surviving mutants):

- **D3-01, D3-02, D3-03, D3-04, D3-05, D3-06** — full-gate confirmation of
  M31, M19, M13, M32, M21, M30 (`GATE_SCOPE=full GOLDEN_MODE=drift
  GOLDEN_REF=c398fc8… GATE_JOBS=1 ./tests/run.sh` with the mutant applied,
  under the gate lock). A kill by stress.py, edge.py or backtest.py
  withdraws the row.
- **D3-07** (M15) — seventh on the finder's list; stays provisional if the
  quiet window runs only the top six.
- **D9-02** — the 4.69× headroom is a CPU ratio (budget / observed worst),
  ± 20 %; re-take, and re-check on main against #145's × 3 factor.
- **D9-04** — the planner share 0.63 (± 15 %) and 70–76 ms; re-take. The
  counts (64 / 6,144 / 7,084) are final.
- **D9-05** — starvation share 0.967, gap p50 13–15 ms, longest hold 39–75
  ms (wall); re-take.
- **D9-01, D9-03** secondary numbers — 751× / 38.5× reference (CPU ratios)
  and 908 → 789 ms; re-take. The per-gradient counts are final.
- **D0-02** secondary — production CPU 111.8 s for 160 solves; the SEK
  gaps and counts are final.
- **D10-14** — the 1818 s script wall; the 88.4 % is a count ratio and
  final.
- **D1-01, D1-02, D1-05** — `thread_factor` 58.4 / 346.1 (see intake
  flags); re-take the factor or explain the harness's measurement; the
  counts are final. D1-02's window size on a Pi (one solve's duration) is
  unmeasured.

### Harness archive

`round2/` at `d5d8c4a` holds `BASELINE.md` and, per
dimension, `REPORT.md`, `report.json`, every harness and its `.out` /
result files, copied from the export (D1, D2, D4, D5, D6, D7, D8, D10) and
the three instrumenting worktrees (D0, D3, D9). Excluded, each regenerated
by its harness's single header command: `D4/shots/` (182 PNGs, 14 MB;
`card_geometry.mjs --shots`), `D4/results.json` (2.05 MB; the same run) and
`D8/matrix_results.json` (1.82 MB; `matrix.py`). Nothing else exceeded
1 MB. `QUIET.md` / `quiet.json` were not yet present at commit time and are
added when the quiet window returns; the quiet-window agent's in-flight
`quiet/` scratch (its run scripts and partial D9 logs, still being written)
was left out for the same fold-in.

### Verification round — panel verdicts (pending the judge)

Three seats per panel, fresh context each, refute-first, majority-refute kills.
Seat 1 measures with a harness it wrote itself, seat 2 attacks consequence and
reachability, seat 3 attacks the perturbation and the scope. The verdicts below
are the panels'; none is final until the judge has re-measured the decisive
number. Panels still to run: D0, D1, D4.

| Finding | Severity after panel | Vote | What the panel changed |
|---|---|---|---|
| D2-01 | high | 3-0 verify | STRENGTHENED and ready to fix. Two seats independently applied the repair (dt=dt_hours/n_sub in the single-zone batch branch + hoist the T_room seed) and got parity 2.5e74 -> 0.0 on every stiff cell with ALL 49/55 goldens byte-identical, features.py 1557/1557. Consequence at the minimal... |
| D2-02 | medium | 3-0 verify | physics confirmed (dCOP/dT_out = -0.26/K, 510 of 1540 cells, 3 of 4 valve modes; COP 0.74 at -25 C/70 C flow is below a resistive heater) but the FIX SCOPE IS REFUTED: the proposed formula is algebraically the shipping code and leaves 6 of 6 cells non-monotone. Plan consequence is 0.0000 SEK on... |
| D2-03 | medium | 3-0 verify | verified: 84 of 96 steps mispriced on all six transition days, one step of real duration 1.25 h (autumn) or -0.75 h (spring, the grid runs backwards in real time) against the uniform dt every consumer integrates with. Why dst_checks.py passes: it never runs... |
| D2-04 | low | 3-0 verify (weakened) | HEADLINE REFUTED, finding weakened to low: the gate ceiling is 0.35 not 0.28 (excursion is the range of T_room - T_out, not the room alone), so a 1 K/h outdoor drift DOES clear the gate - and it is adopted with ZERO bias in 60/60 seeds. No sensor-drift cell cleared the gate in 11 cells x 60... |
| D2-05 | low | 3-0 verify | verified low: the discontinuity is real (jump 1.0, 13.44 kW of a 13.44 kW draw) against a docstring promising continuity, and _wood_share_vec shares it bitwise; 0 of 4.8 M recorded solver calls come within 0.5 K of the cliff (closest 1.33 K) and trajectories reconverge to 5.5e-05 C over 96... |
| D3-01 | pending | 1 of 3 seats reported | 20 attributes, not 21 (small correction). Zero suite references to the sensor or 8 of its keys; the two generic sweeps that touch it assert only non-finiteness and non-crashing |
| D3-02 | pending | 1 of 3 seats reported | mechanism weakened: the branch is NOT dead to the suite - features.py:16663 drives it through the whole optimizer stack (2 differing evaluations in the gate, 106 in rolling) and still passes. That makes HALF THE FINDER'S FIX SCOPE WRONG: no golden scenario starting inside a window will catch... |
| D3-03 | pending | 1 of 3 seats reported | cheapest to close: the assertion that catches it is ALREADY WRITTEN (features.py:7770 'hotter tanks cost more per day') and merely never fed a negative price; profiles.py ships an unused summer_negative. At -0.4 the recommendation flips 48 -> 60 C and every cost_per_day goes negative |
| D3-04 | pending | 1 of 3 seats reported | - |
| D3-05 | pending | 1 of 3 seats reported | consequence weakened: it does NOT abort coordinator setup - _async_load_accuracy is one of twelve fire-and-forget tasks, so the ValueError kills one task and silently leaves dhw_accuracy, defrost, peaks, mode and the comfort learner unloaded every startup |
| D3-06 | pending | 1 of 3 seats reported | - |
| D3-07 | pending | 1 of 3 seats reported | mechanism weakened: 'no freshness check uses a future timestamp' is false - 13 differing evaluations in features.py at age = -306705 min, and it passes. Also date-dependent (the box's clock has drifted past the fixture's frozen NOW), so the count may differ on a re-take; the finding does not... |
| D3-08 | pending | 1 of 3 seats reported | 53 solves reproduced from a different instrument; kill_rate 0/4 for each of solar_alignment, plan_view, manual_plan, validate, optimality against a positive control of 4/4 on features.py |
| D3-09 | pending | 1 of 3 seats reported | validate.py executes 8 of 38 closure modules, name-for-name identical forced list; a stricter definition gives 6 of 38, so the finder's number is generous if anything |
| D3-10 | pending | 1 of 3 seats reported | MOST CONSEQUENTIAL of the ten per seat 1: reproduced with an INDEPENDENT mutant (thermal_model.py:547 wood-tank standby loss x25) - three SENSITIVE fixtures moved 2111 leaves, wood_coil's baseline_cost -2.08 %, and env_drift still printed 'NO UNCLAIMED DRIFT: 55 scenario(s) checked' with rc 0.... |
| D5-01 | low | 3 of 3 seats reported | scope +2 stale closure rows (l.103/104) and the l.155 wrap; env_drift.py:186 'all 53' stale |
| D5-02 | low | 3 of 3 seats reported | mechanism escalation for D10: default topics make every non-MQTT install log 2 ERRORs per cycle (ServiceNotFound); fix is the code default, docs row stays |
| D5-03 | low | 3 of 3 seats reported | 'only inbound links from plan docs' is wrong (0 in-links); count 3 stands; fix needs 3 links not 2 |
| D5-04 | low | 3 of 3 seats reported | one more H1-class line tests/README.md:155; S1 needs a paragraph revision |
| D5-05 | low | 3 of 3 seats reported | scope +1: snapshots.py:170 names restore_snapshot (service is restore_learned_snapshot) |
| D6-01 | low | 3-0 verify | 9 of 55 names; scope complete (no unqualified form elsewhere) |
| D6-02 | low | 3-0 verify | 1 of 25-28 examples off its default; the description sentence is not false, the example is stale |
| D6-03 | low | 3-0 verify | 2 of 39 selectors; scope INCOMPLETE - config_flow admits 0 at four sites and ThermalParameters keeps a stored 0, so widening _positive reconciles all three surfaces |
| D6-04 | low | 3-0 verify | title over-stated: 0.044 IS zero at the quoted precision, so 1 of 2 figures fails; degree-hours is a hinge functional and machine-dependent, so the fix must state the asserted property, never re-record the number. Judge re-takes on the quiet box |
| D6-05 | low | 3-0 verify | seat 2 weakens the claim's wording (0/2 docs state a flat setpoint) but severity stays low; the finder's C305 row is a CONSTANT and is VOID as evidence - seat 3's own harness (1 -> 0 sentences) is the number that counts |
| D8-01 | high | 3-0 verify | STRENGTHENED on reach, CORRECTED on title. Seat 2 drove the real HeatPumpOptimizerConfigFlow to create_entry submitting every form untouched: it completes with zero thermometers configured and dhw_tank_volume=200.0, so this is the DEFAULT install, not a matrix corner. 16 default-derived... |
| D8-02 | low | 3-0 verify | VERIFIED, and the consequence is smaller than the label. Seat 1 found real orjson 3.12.0 on the box and ran Home Assistant's own json_bytes path: 0 failures over 496 payloads, because every numpy leaf is np.float64, which subclasses float. Controls np.float32, np.int64, np.ndarray and np.bool_... |
| D8-03 | low | 3-0 verify | VERIFIED, restate the metric. Seat 1: the schedule attribute spans 5 h 45 min against README.md:286's whole-24-h claim, with 96 forecast steps on the same payload. schedule_truncated=170 is 85 cells x 2 cycles x a constant, so the grid contributes nothing and leave-one-out is meaningless: report... |
| D8-04 | low | 3-0 verify | VERIFIED as hygiene, aggregate corrected. Seat 1: distinct_rosters=1, so the metric is static text and cannot move with any input; nothing supports more than hygiene. Seat 3: leave-one-out on card_headline takes 15 -> 12, the 15 double-counts four entities, and 8 of the 15 splits come from... |
| D9-01 | high | 3-0 verify | STRENGTHENED on reach, CORRECTED on drift. The trigger is structural, not lucky: optimizer.py:3195 clamps p_dhw_run to min(power_caps_extra) and solve_space subtracts it from the same cap, so headroom is identically zero at every planned DHW step for any uniform cap between 0.1 kW and 0.8*p_max.... |
| D9-02 | medium | 3-0 verify | verified and sharpened: stress.py and optimality.py never pass power_caps_extra or space_pins, so D9-01's 13-40x path is UNSAMPLED, not merely under-budgeted - re-sizing a global constant cannot fix that. A single global ratio can never do better than 'detects exactly the factor it was sized... |
| D9-03 | low | 3-0 verify | verified: f0_x_identity = 1.000 (103 of 103 _batch_fd_gradient calls at an x byte-identical to scipy's immediately preceding objective call). The real fix implemented: trajectories per gradient 2.068 -> 1.039, 0 of 49 fixtures change |
| D9-04 | low | 3-0 verify | verified, framing corrected: lead with planner_over_reference (3.4-4.1, stable) not 'the 63 % share', which is 63 % of the CHEAPEST solve (10.4 % on two-zone). Not a hook artefact (0.6191 with one wrapper vs 0.6266 with seven). Two more per-slot re-simulation loops unnamed: optimizer.py:3996... |
| D9-05 | medium | 3-0 verify | verified and UNDERSTATED by the finder: longest GIL hold 265-412 ms (reported 39.4), p99 232-338 ms (reported 35.8), across the quiet window and two independent verifiers; stage attribution is dhw_lp_build / scalar_sim, not simulate_trajectory_batch. The STATED PERTURBATION IS VOID... |
| D10-01 | medium | 3-0 verify | the card-discovery lever does not hold (the card resolves by id suffix); the finding stands on the 5 hard-pinned entity_ids and 5 fan-out service handlers. single_config_entry would break a legitimate two-pump install - use the unique-data shape |
| D10-02 | medium | 3-0 verify | worse than reported: _tibber_fetch_failed raises UpdateFailed INSIDE the try, so the trailing except re-wraps the integration's own signal - one failure burns two outage cycles; real HA would start reauth (raise_on_auth_failed on the first refresh) |
| D10-03 | low | 3-0 verify | understated: the rule wants info-level and once; the home-grown ERROR latch is off-rule before the outer handler re-logs. With real HA's own log-once branch the count is 5, not 4. Scope misses async_run_optimization's per-cycle error and five unlatched actuation sites. Path-independent... |
| D10-04 | low | 2-0 verify (weakened) | narrowed: 1 of 3 is truly silent (run_optimization, registered with no supports_response); the other two name the failure in a documented response. Cite fix: coordinator.py:4825, not 5536 |
| D10-05 | low | 3-0 verify | - |
| D10-06 | low | 3-0 verify | - |
| D10-07 | low | 3-0 verify | - |
| D10-08 | low | 3-0 verify | - |
| D10-09 | low | 3-0 verify | - |
| D10-10 | low | 3-0 verify | - |
| D10-11 | low | 3-0 verify | - |
| D10-12 | low | 2-0 verify (weakened) | narrowed: removal instructions and blueprints genuinely absent; known-limitations and supported-devices exist in prose (discoverability, not information) |
| D10-13 | low | 1-0 verify (weakened) | restate the number: 225-296 of 722 are tests/hastub artefacts (no py.typed, truncated classes); the integration-internal floor is 497. Direction of the fix is not obviously down - annotating can add attr-defined errors |
| D10-14 | low | 2-0 verify (weakened) | config-flow half verified with a killing mutation (config_flow.py:960); the three coverage percentages are UNRESOLVED under the box constraint - judge re-measures. 88.4 % is a lower bound: coordinator.py is 843 of 1491 missed and its closed-loop driver (rolling.py) is the one excluded script |
| D10-15 | low | 1-0 verify (weakened) | SPLIT the row: the ENERGY half is REFUTED as proposed - both sensors are MEASUREMENT forecasts, HA admits ENERGY only with TOTAL/TOTAL_INCREASING, and the finder's one-line fix would fail the repo's own gate at tests/entities.py:1225. The entry_type/manufacturer half stands but maps to no rule... |

**49 findings through a panel so far, 0 refuted, 0 harnesses voided.**
Zero refutes is not zero effect: the panels corrected titles, perturbations,
severities and proposed fix scopes throughout, and several findings came out
of the panel stronger than they went in. The full seat reports are at
`round2/D<k>/verify-<n>.md`, at `d5d8c4a`.

## Round 4 — baseline v6.4.2 (`7dd68dd`), 2026-09-12

The first round at **thirteen** dimensions: `7dd68dd` added D12, generalization.
Evidence is `tools/audit/round4/`, the finder reports at
`round4/D<k>/reports/FINDER.md`, the quiet window at `round4/quiet-window.md`,
and this round's index at `round4/ledger/findings-index.tsv` — which is where
every count below comes from, so re-derive them from that file rather than
reading them here.

**Verified, judged and filed 2026-09-13.** Three verifier seats per finding
(117 votes: 108 verify, 6 weaken, 3 refute), then the judge alone under the
gate lock — verdicts at `round4/judge-verdicts.md`, votes at
`round4/ledger/verify-tally.json`. **34 verified, 4 weakened (D1-INST low
hygiene, D3-S3 low hygiene, D7-03 medium, D11-04 medium hygiene), 1 refuted
(D4-02, killed 3-of-3: the premise — HA's stock dark theme setting
`--text-primary-color: #212121` — is false at every supported version; the
2.783:1 pairing existed only in the finder's hand-written theme table).**
42 issues filed under `[R4-<id>]` titles plus the owner-verified
`[R4-OWNER-01]` (#908); the tracking table is #962.

Two departures from earlier rounds, both deliberate:

- **A defect in an instrument is a finding of the dimension that met it**, under
  the same evidence bar, and it travels panel → judge → issue like any other.
  The rule is in `tools/audit/README.md`. It landed *after* these finders ran,
  so several instrument defects are classed `non_findings` in their own reports
  and are carried into verification by `round4/RESUME.md` instead.
- **Two instrument defects were fixed rather than filed**, which that rule
  explicitly allows: `prepare_baseline.sh` deleted a file `tests/entities.py`
  reads unguarded — the export ran **0 of 1360** entity checks — and carried 116
  round-3 files, including 43 earlier findings with their verdicts, into every
  finder tree.

**There is no Round 3 section in this document.** `tools/audit/round3/ledger/`
records 43 findings filed as issues, so the gap is in the register and not in
the work. It is named here rather than quietly filled by this round.


### The dimensions

| # | Dimension | Findings |
|---|---|---|
| 0 | Price optimality | reported (2 finding(s)) |
| 1 | Robustness and stability | reported (2 finding(s)) |
| 2 | Mathematical and physical sanity | reported (5 finding(s)) |
| 3 | Test-suite gaps | reported (4 survivor(s) after the full gate) |
| 4 | UI/UX | reported (3 finding(s)) |
| 5 | Docs structure, flow, comments | reported (2 finding(s)) |
| 6 | Documentation claim verification | reported (3 finding(s)) |
| 7 | Architecture and maintainability | reported (3 finding(s)) |
| 8 | Sensor verification and ordering | reported (2 finding(s)) |
| 9 | CPU and memory efficiency | reported (2 finding(s)) |
| 10 | HA quality scale | reported (3 finding(s)) |
| 11 | Governance and policy | reported (7 finding(s)) |
| 12 | Generalization | reported (1 finding(s)) |

**35 findings across 13 dimensions**, plus 4 D3 mutation survivors the quiet window put through the full gate. Severity as the finders assigned it, subject to the panel: 2 critical, 10 high, 11 medium, 12 low.

### Findings register — round 4

Severity from the reporting finder. Status is `reported` for every row.

#### D0 — Price optimality

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D0-01 | low | L-BFGS-B ftol=1e-6 halts the space solve short: objective lower in 34 of 70 priced cells, but the gap survives flat prices and the realised-money control moves the wrong way | reported |
| D0-02 | low | the iteration budget the code and tests/optimality.py police is never binding (0 of 488 solves reach the cap) while ftol, which changes every plan, has no gate | reported |

#### D1 — Robustness and stability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D1-01 | high | a non-finite bin in the persisted price shape prices 4 of 96 planning steps at 0.0 SEK/kWh, silently; from_dict checks no finiteness while observe_day does | reported |
| D1-02 | high | one corrupt scalar in the accuracy store raises in _async_load_accuracy and the next cycle overwrites 3 of 3 learned fields, zero log lines, last_update_success True | reported |

#### D2 — Mathematical and physical sanity

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D2-01 | high | tariff._smooth_topk_sum bisects on a bracket not scaled by its own logistic temperature: up to 13.35x the top-k bill it approximates above 5.84 kW excess | reported |
| D2-02 | medium | every shipped DSO catalog row writes a peak-hours mask that discounts 0 of 672 windows, because apply_catalog omits the off-peak factor | reported |
| D2-03 | high | thermal_model.wood_share is discontinuous at hp_temp == flow_set where its docstring claims continuity; one ulp of step-0 power moves 1.110 kWh | reported |
| D2-04 | medium | modelled COP falls below 1.0 in 51 of 328 cells and inverts with rising outdoor below -21 degC: the Carnot and DHW factors apply after the curve's own floor | reported |
| D2-05 | low | grid-fee decimal commas are unreachable: parse_rules splits on the comma _parse_rule converts | reported |

#### D3 — Test-suite gaps

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D3-S1 | - | grid_fee.py:106 parse_month_range: a non-wrapping range like Mar-Sep becomes year-round; the only range assertion uses the wrapping case | survivor (full gate) |
| D3-S2 | - | legionella.py:521: the disabled-feature guard, with both existing assertions running enabled | survivor (full gate) |
| D3-S3 | - | tariff.py:507: the top-k clamp, a no-op on the one fixture that calls it; equivalent through the only production caller | survivor (full gate) |
| D3-S4 | - | optimizer.py:1549 CLAMP_DROP: numpy slices clamp, so no value moves | survivor, judged equivalent |

#### D4 — UI/UX

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D4-01 | high | the plan's lane strip labels render at 6.4 CSS px and 1.01:1 contrast; the card's 8 px floor never reached them because card_browser.mjs filters lane-* out of its own check | reported |
| D4-02 | medium | .wi-save pairs a hard-coded #026aa8 with var(--text-primary-color), which HA default dark sets to #212121: 2.78:1 on the primary confirming action | reported |
| D4-03 | low | the 24 px target floor is emitted only under @media (pointer: coarse), so the zoom pair is 20.22 px at 22.22 px spacing under a mouse | reported |

#### D5 — Docs structure, flow, comments

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D5-01 | medium | docs/configuration.md, the reference README promises documents every field, names 15 of 200 shipped options fields nowhere | reported |
| D5-02 | low | tests/README.md states a stress sweep of 48; sweep_combinations() returns 51 | reported |

#### D6 — Documentation claim verification

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D6-01 | high | docs/architecture.md is stale in ten claims including the HA boundary it exists to state: 21 modules import homeassistant at module level, 11 outside the ten it names | reported |
| D6-02 | medium | Sensor-Gap Euro Advisor is documented with the currency unit and publishes none, so a currency-per-month value is recorded unitless | reported |
| D6-03 | low | docs/automations.md states a Power Headroom precondition the code does not enforce; a capacity tariff alone makes it available at 0.0 kW | reported |

#### D7 — Architecture and maintainability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D7-01 | medium | the sysid experiment is adopted in 0 of 18 cells: the identifier fits one state to a two-state plant (null control on a collapsed plant adopts at 0.940) | reported |
| D7-02 | medium | sysid._sizing_model leaves slab constants at defaults for every house, breaching max_excursion_c in 6 of 18 cells | reported |
| D7-03 | high | _learning_frozen never consults _pump_signals.defrosting, so 3 of 4 learners fold a defrost interval; only _learn_measured_cop refuses, through its own bespoke guard | reported |

#### D8 — Sensor verification and ordering

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D8-01 | low | alphabetical order leaves 159 foreign entities inside the seven families' spans; the two families scoring zero are the only two with a shared name prefix | reported |
| D8-02 | low | four entities are the only ones with no icons.json entry, against a 31/0 control that kills the device-class defence | reported |

#### D9 — CPU and memory efficiency

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D9-05 | medium | the batched objective vectorizes the physics then re-computes the cost in a Python loop over batch rows: _comfort_terms 97.02 calls per gradient, 33.3 % of solve wall | reported |
| D9-06 | medium | tests/stress.py cannot detect a 2x memory regression on any of its 51 scenarios; a 2.03x injection passed all 62 checks, and the CPU-only detection check claims otherwise three lines below | quiet-confirmed |

#### D10 — HA quality scale

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D10-01 | low | quality_scale.yaml has drifted: 3 of 54 declared rows are contradicted when executed, including a config-flow coverage row claiming 100 % against a measured 97.2 % | reported |
| D10-02 | low | docs-known-limitations is declared done with 0 such headings across 4075 lines | reported |
| D10-03 | low | the package root re-binds HeatPumpOptimizerConfigEntry to a bare ConfigEntry, so runtime_data reveals Any in the three entry points while mypy --strict reports 0 errors | reported |

#### D11 — Governance and policy

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D11-01 | critical | main-protect carries no pull_request rule in any of its five versions: 0 of 592 merged pull requests have an approving review by a non-author, and admin bypass is always | reported |
| D11-02 | critical | eight sites instruct a seat holding write and merge grants to act on issue and pull-request text, against zero sentences anywhere naming untrusted input | reported |
| D11-03 | high | the one root-cause trigger CLAUDE.md calls enforced is inert in CI: governance.yml passes no --red, and the same body exits 1 with it and 0 without | reported |
| D11-04 | high | eight tree assertions contradict the live required-check set, which went 18 to 17 to 16; two of the eight cite a file main has since deleted | reported |
| D11-05 | medium | the disposition rule cannot be satisfied before a merge and turns main red on 44 % of pushes; record's if: correctly excludes pull_request events | reported |
| D11-06 | medium | policy_lint --stats reports a class over its own threshold and opens nothing; both --stats and --sunset run under || true and no contract obliges a seat to read either | reported (provisional) |
| D11-07 | low | no release artefact and no provenance: SLSA Build level 0, and 7 of 9 workflow actions on mutable tags | reported (provisional) |

#### D12 — Generalization

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D12-01 | high | every temperature input is adopted as degC whatever unit HA reports: 10 of 13 guarded inputs misread on a non-metric instance, and the 96-step plan totals 0.0 kWh | reported |

## Coordination protocol (two sessions, one queue)

Both sessions act on GitHub as `tvofi`, so a claim is a label plus a comment, never an assignee.

| Mechanism | Rule |
|---|---|
| Ownership labels | `owner:zcode` and `owner:claude-40`. Applied to an issue before any branch is cut. An issue carrying the other session's label is not touched. |
| Claim comment | `claimed-by: <session> · branch <name> · <UTC time>` as the first action after labelling. Releasing: remove the label, comment `released`. |
| Branch prefix | zcode: `zcode/…`. claude-40: `claude/…`. |
| PR ↔ issue | Every fix PR body carries `Closes #N` and `Part of #201`. |
| Judge labels | `judge:pending` on creation → `judge:verified` / `judge:weakened` / `judge:unreproduced` with the judge's number as a comment. A fixer may not start on `judge:pending`. |
| Merge queue | Before `gh pr merge`: `git fetch`; if `git log v<last-tag>..origin/main` is non-empty the previous merge is unstamped — wait. One merge at a time. |
| Stamp | Only `tools/release/stamp.py --push --push-key ~/.zcode/stamp-deploy.key --known-hosts ~/.zcode/github_known_hosts`, from the local box, only after the merge commit's own `fast` + `closures` are green, after every behaviour-moving merge. Never edit VERSION, the manifest version or the notes heading in a branch. Never stamp by hand. |
| Gate | `python3 tests/gate_lock.py take/renew/release --label <session>`, and only when `tests/closure.py select` reports `MODE: FULL` or names `tests/stress.py`; never `mkdir` and a shell pid (#404). One local full gate per box; never clear a lock by hand — an expired lease or abandoned hold is stolen by the script, not by you. `GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD)` locally. |
| Claim files | A branch that moves no fixture leaves both claim lists empty. |

Partition: zcode owns every D10 item (#189, #194–#197, #216–#218) and the coordinator decomposition program (#193, #222–#226); claude-40 owns #227, #198, #199 and every round-2 D0–D9 finding.

## Round 6 — baseline v6.6.9 (`e336cc2c`), 2026-09-22

The first round at **fourteen** dimensions: D13 (process yield and cost) joined
the thirteen round 4 ran. Baseline `e336cc2c530882a142ef298de6420706d96a6300`,
the round-5 completion stamp — so **every round-5 issue was already closed when
these finders ran**, and each finding below that has a round-5 counterpart is a
measurement of the tree *after* that counterpart's fix.

Evidence is `tools/audit/round6/`: every dimension's `REPORT.md`, the finding
JSONs of the twelve dimensions that carry one, the recorded `RESULT` output and
fixtures. **The 60 harness `.py` files are not in this commit** and neither are
D4's 138 screenshots; the reason, the exact predicate and the recipe are under
*What this commit does not carry* below. Reports were written by their finders
except D5, D6, D8, D11, D12 and D13, whose `REPORT.md` writes were refused and
whose reports the orchestrator reconstructed from the finders' inline returns
(each JSON says so in `report_note`). D1 and D7 wrote finding JSONs that landed
only in the session's `/tmp` scratch and are committed here for the first time.
**D2 and D10 have no finding JSON at all** — their findings exist as prose in
their `REPORT.md`, which is the source of record for those three rows.

**The quiet window is complete.** D9-01's wall figure was re-taken by the
judge on an idle box, D3 ran its six recorded mutants through the full gate
(`GATE_SCOPE=full GOLDEN_MODE=drift`), and the five post-dedup findings that
resulted (D3-02…D3-05, D7-03-EXT) are included below with their judge verdicts.

### Intake validation

Every finding was validated field by field against `tools/audit/finding.schema.json`
by the checks this round's dedup brief names — the required finding fields, the
`cpu_or_wall` enum, the `cpu|wall ⇒ null_control` conditional, the id pattern, the
severity enum and the `stop_rule_class` enum. **26 of 26 pass; 0 rejected at
intake.** Two intake notes, neither a rejection:

- **D2 and D10 have no finding JSON to validate** (see above). Their three
  findings were validated from their `REPORT.md` text; every field the brief's
  check names is present there. One schema-required evidence field, D10-01's
  `evidence.thread_factor`, is stated nowhere in the D10 report and is recorded
  as **absent rather than invented**; D10's numbers are counts and exit codes,
  so a thread factor measures nothing this row rests on.
- D3-01's perturbation needs the optional package `orjson` installed. It is
  deliberately absent from `tests/requirements-ci.txt`, and the box that ran this
  round had it uninstalled mid-round — **a verifier that runs the harness without
  installing `orjson` reproduces the perturbed arm only** and will read the
  finding as already fixed.

### Dedup — 26 findings, 26 rows, 0 merges

The merge rule is the finder contract's: one row per mechanism, but **do not
merge findings whose finder stated distinct instrumented symbols, perturbations
or consequences**. Three pairs were examined and refused:

- **D1-01 / D1-02** share one root — *a persisted scalar is converted with
  `float()` and no finiteness test* — and the D1 report says so itself, then
  reports them separately because each has its own instrumented symbol, its own
  one-line perturbation and its own consequence, so the fix wave can take them as
  independent one-line changes. Kept as two rows.
- **D0-01 / D0-02** share the instrumented symbol `optimizer:_multi_start_minimize`
  and nothing else: D0-01 prices the refined set, D0-02 a stale comment, and
  D0-02's own null control measures the drop it describes at 0.0000 % in 80 of 80
  cells — the defect is the count in the comment, not the cut.
- **D6-02 / D6-03** share `sensor:HeatPumpOptimizerSensorBase.entity_id`, but one
  perturbation pins the prefix and the other renames the entry, and the
  consequences differ (two blueprints whose `default:` sensor does not exist
  versus two documents that tell users the prefix follows their entry name).

**Classification.** 19 new, **5 corroborating a closed round-5 issue**, 1
regression of a released fix, 1 matching a refuted earlier finding. The
"corroborates an *open* round-5 issue" branch is **empty, and that is a fact
about the calendar rather than the findings**: round 5 filed 48 findings as
#1293–#1340 and all 48 were closed before `e336cc2c`. The five that corroborate a
closed one are therefore measured on the post-fix tree — for four of them the
released fix is provably narrower than the phenomenon it closed.

**The round-5 carry files are the binding argument for six of these rows**, and
a panel must read them rather than the issue titles: `carry-1295.json` (D0-01),
`carry-1300.json` (D11-01), `carry-1308.json` (D7-01), `carry-1320.json`
(D4-01), `carry-1330.json` (D7-02) and `carry-201.json` (D13-03). Each states
what the round-5 fix narrowed and what a later seat must re-establish at its own
merge base.

### The dimensions

| # | Dimension | Findings |
|---|---|---|
| 0 | Price optimality | reported (2 finding(s)) |
| 1 | Robustness and stability | reported (2 finding(s)) |
| 2 | Mathematical and physical sanity | reported (2 finding(s)) |
| 3 | Test-suite gaps | reported (5 finding(s)) |
| 4 | UI/UX | reported (1 finding(s)) |
| 5 | Docs structure, flow and content; code comments | reported (2 finding(s)) |
| 6 | README and documentation claim verification | reported (3 finding(s)) |
| 7 | Architecture and maintainability | reported (4 finding(s)) |
| 8 | Sensor verification and ordering | reported (1 finding(s)) |
| 9 | CPU and memory efficiency, Raspberry-Pi-class target | reported (2 finding(s); D9-01 provisional) |
| 10 | HA integration quality scale | reported (1 finding(s)) |
| 11 | Governance mechanisms and policy | reported (2 finding(s)) |
| 12 | Generalization | reported (1 finding(s)) |
| 13 | Process yield and cost | reported (3 finding(s)) |

**31 findings across 14 dimensions.** Judge severity: 7 high, 12 medium, 12 low
(23 verified, 8 weakened, 0 refuted, 0 unreproduced).

### Findings register — round 6

Severity from the reporting finder. Status is `reported` for every row except
where noted.

#### D0 — Price optimality

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D0-01 | medium | the space solve refines only its four pre-scored candidates, so 8 structured bang-bang seeds plus a raised `_MULTI_START_SOLVES` lower the objective by a median 0.0615 % (max 11.1729 %) over 64 heating cells — **objective-only, and the deferred round-5 #1294 change exactly** | weakened → low |
| D0-02 | low | `_MULTI_START_SOLVES` is 4 while the seam is handed 5 candidates in 80 of 80 cells (the #1295 warm start), and the constant's comment still reads "The candidates number four, so this is the whole list" | verified |

#### D1 — Robustness and stability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D1-01 | high | a `NaN` in the DHW-profile store's `cooling_rate` installs a non-finite value on the live model and is never reset or logged: 5 non-finite landing sites, the learner's own EWMA absorbs it, and the next save writes it back — the fifth seam of the family round-5 #1296 guarded four of | verified |
| D1-02 | high | a `NaN` in one cell of the accuracy store's `defrost.duty` survives `DefrostDerate.from_dict` and becomes `DERATE_MIN`: `compute_cop` prices that bucket at 0.55x the healthy COP at all 8 substitution cells, permanently, with no log line | verified |

#### D2 — Mathematical and physical sanity

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D2-01 | high | `DefrostDerate.factor` answers from hard-edged buckets, so the COP every price runs through steps by up to 1.61437 COP across a 1e-9 change in outdoor temperature (and 1.37812 COP across 69.999999 → 70.000001 % RH) where the no-duty null arm reads 1.75e-10 | verified |
| D2-02 | medium | `simulate_dhw_step`'s inlet floor is a heat source with no source: with the tank's surroundings at 20 C the clamp manufactures 0.10022–1.30291 kWh/day of heat at the shipped config surface's inlet maximum (25 C by option, 33 C with the seasonal amplitude), and the tank is pinned at the floor | verified |

#### D3 — Test-suite gaps

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D3-01 | medium | `tests/entities.py`, in the production closure of all 64 modules, reports 3 of 1678 checks failed on the pristine baseline whenever the optional, unpinned `orjson` is importable — `hastub`'s `_json_bytes` takes an `orjson.dumps` fast path that does not refuse non-finite floats, and its refusal `walk()` is reached only when `orjson` is missing | verified (fix direction inverted) |

| D3-02 | low | test-suite gap: deleting the silent-mode no-window guard (`silent_mode.py:79`) survives the full gate — mutant 17, `if not windows and weekly is None: return None` → `if False` (NOGUARD) | verified |
| D3-03 | low | test-suite gap: forcing the buffer-cap re-solve branch (`optimizer.py:3546`) survives the full gate — mutant 18, `if changed:` → `if True` (ALWAYS) | verified |
| D3-04 | low | test-suite gap: forcing the emitter-normalisation branch (`presets.py:153`) survives the full gate — mutant 26, `if upper_emitter not in EMITTERS` → `if True` (ALWAYS) | verified |
| D3-05 | low | test-suite gap: forcing the defrost accrual branch (`defrost.py:599`) survives the full gate — mutant 30, `if delta is not None and delta > 0` → `if True` (ALWAYS) | verified |

#### D4 — UI/UX

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D4-01 | medium | the plan card's score pill is the one control in a 528-cell matrix under the card's own coarse-pointer floor — 25 px at 375x812 and 39 px at 768x1024, against `TARGET_MIN_PX_COARSE = 44` — because it is absent from `htmlTargetFloor`'s selector list and carries only the R5-D4-02 padding rule | verified |

#### D5 — Docs structure, flow and content; code comments

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D5-01 | medium | the committed `docs/img/marginal-cop.svg` is not what its generator produces from the shipped model: its curves decode to marginal COP 0.888/0.956 at −20 C where the model returns 1.0, because the figure predates the #928 resistive bound and `docs/` is INERT so nothing re-runs the generator | verified |
| D5-02 | low | README's `## Documentation` table names 8 rows and omits `docs/automations.md`, a page the README links four times in its own prose | verified |

#### D6 — README and documentation claim verification

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D6-01 | medium | README L894-895/L214-215 tell users without an ECL110 to clear two MQTT topics that must be cleared, but all three ECL110 topic options ship with an empty-string default and `_publish_ecl110` returns early — `docs/ecl110.md` documents the correct behaviour and `tests/nightly_ha.py:2531` repeats the false premise | verified |
| D6-02 | medium | two of the three blueprints README presents as importable worked examples default their sensor input to entity ids the sensor platform never builds (a missing `cost_` token against the pinned prefix at `sensor.py:365`) | verified |
| D6-03 | low | `docs/automations.md` L7-11 and two blueprint descriptions tell users the entity prefix follows the entry name, but the token is a hard-coded literal: 0 of 59 sensor ids carry `slug(entry.title)` after the entry is renamed | verified |

#### D7 — Architecture and maintainability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D7-01 | high | the production sysid adoption gate admits UA errors over 10 % in 14 of the 75 experiments it accepts on the three shipped presets, worst −28.7018 % at confidence 0.97751 — a variance failure `_slab_confidence` cannot see because it has no term for the parameter of interest | verified |
| D7-02 | low | `SystemIdentification.identify` (379 lines) is entered 0 times by the only call sequence production uses, and `tests/structure_budgets.json`'s `dead_top_level_symbols` row reads 0 because `structure.py` walks module-level definitions only | verified |
| D7-03 | medium | on `heavy_old` with a drifting room sensor `identify_slab` raises an uncaught `OverflowError` out of `_lm_solve` (8 of 48 experiments), unwinding through `_async_update_data` and failing the whole update cycle; the armed night is discarded with `last_run` set | verified (trigger 0.03) |

| D7-03-EXT | high | the same drifting-room divergence hangs silently at drift 0.03/0.04: finite 2.5e19 kW/K drives 2.6e17 substeps with no log line, consuming the whole 30-day window — judge-confirmed | verified |

#### D8 — Sensor verification and ordering

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D8-01 | medium | with DHW unconfigured, five of the six `_DHWEntityMixin` entities are enabled by default and `available is False` in every refresh — five dead entities for a user with no hot water, where only `DHWTemperatureSensor` is disabled by default | verified |

#### D9 — CPU and memory efficiency, Raspberry-Pi-class target

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D9-01 | medium | a production solve on a `ThreadPoolExecutor` thread starves a real loop's 1 ms heartbeat for 0.9737 of its wall time, and neutralising all eight production `sleep(0.002)` yields moves that share only to 0.9812 — the maximum gap is set by the longest single L-BFGS-B run, which no between-run yield can bound | weakened → medium |
| D9-02 | low | `tests/stress.py:SolverWork` counts step-equivalents on two seams only, so the DHW planner's 24 `simulate_dhw_only` calls per solve — 29.63 % of all simulated work on the single-zone DHW solve — are counted by neither channel | weakened → low |

#### D10 — HA integration quality scale

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D10-01 | medium | the Silver `test-coverage` row is keyed to a package ratio, so 59 of the package's 64 modules can fall to 0 % with the per-pull-request check green, and `sysid.py` is already below the rule's per-module 95 % bar at 94.62 % (492/520, 28 missed) — `tests/entities.py`'s pin encodes `done iff package_percent_floor >= 95.0` and cannot see the difference | weakened → medium |

#### D11 — Governance mechanisms and policy

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D11-01 | high | 0 of the 37 tracked files that produce or implement the checks the live ruleset requires is matched by an owner-carrying `.github/CODEOWNERS` pattern, so `require_code_owner_review` cannot demand the owner for a change to the checks themselves (9 of the 14 in-window merges touching that surface were approved by `hpo-approver` alone) | verified |
| D11-02 | high | a required check is executed from the change it is checking: `governance.yml`'s `policy-docs` checks out no `ref:`, so a one-line `process.exit(0)` in `policy_lint.mjs` makes it exit 0 on a corpus the same run reports red, stdout byte-identical, and `policy_lint_mutants.mjs` does not notice | verified |

#### D12 — Generalization

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D12-01 | medium | `battery.build()` guards the optional buffer/DHW stores with `state.<field> is not None` on non-Optional floats defaulting to 40.0/55.0 C that nothing ever sets to `None`, so both guards are invariant: a 35 L buffer the plant's own `describe_setup()` reports as `is_store: false` is published as a storage component (8 of 8 cells, 13.32 kWh fabricated) | weakened → low |

#### D13 — Process yield and cost

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D13-01 | high | over `v6.6.0..e336cc2c`, all 11 of the window's 74 parseable review verdicts that are rework are head-moved re-verification, the `head-moved` class `web-fix-wave.js` defines for exactly that has 0 verdicts, and there are 0 engineering-blocking verdicts | weakened → medium |
| D13-02 | medium | 4 of the window's 67 merges (0.060) carry no parsable verdict, all automation-authored, while `policy_lint.mjs --stats` reports a denominator of 64 — the histogram prints the population it saw, not the merges the window contains | weakened → medium |
| D13-03 | medium | `.claude/workflows/cfr_exclusions.json` is keyed where the excluded job cannot gate a merge: excluding `record` moves CFR to 0.090 of 67 at the merge commit, but `record` is skipped at 67 of 67 PR heads, where the failing names are `nightly-status` (7/67) and `delivery-status` (2/67) and the rate is 0.134 either way | weakened → low |

### Judge verdicts — round 6

The audit judge re-measured every survivor and the deferred D9-01 wall figure on
an idle box and assigned the stop-rule class. **31 findings: 23 verified, 8
weakened, 0 refuted, 0 unreproduced.** Final severity 7 high / 12 medium / 12 low.
Panel vote is the three-verifier tally (`v` = verify, `w` = weaken).

| ID | panel | verdict | final |
|----|-------|---------|-------|
| D0-01 | v/w/w | weakened | low |
| D0-02 | v×3 | verified | low |
| D1-01 | v×3 | verified | high |
| D1-02 | v×3 | verified | high |
| D2-01 | v×3 | verified | high |
| D2-02 | v/v/w | verified | medium |
| D3-01 | v/v/w | verified | medium |
| D3-02 | full gate | verified | low |
| D3-03 | full gate | verified | low |
| D3-04 | full gate | verified | low |
| D3-05 | full gate | verified | low |
| D4-01 | v×3 | verified | medium |
| D5-01 | v×3 | verified | medium |
| D5-02 | v×3 | verified | low |
| D6-01 | v×3 | verified | medium |
| D6-02 | v×3 | verified | medium |
| D6-03 | v×3 | verified | low |
| D7-01 | v/v/w | verified | high |
| D7-02 | v×3 | verified | low |
| D7-03 | w/w/v | verified | medium |
| D7-03-EXT | judge | verified | high |
| D8-01 | v×3 | verified | medium |
| D9-01 | w/w/v | weakened | medium |
| D9-02 | v/v/w | weakened | low |
| D10-01 | w×3 | weakened | medium |
| D11-01 | v×3 | verified | high |
| D11-02 | v×3 | verified | high |
| D12-01 | w/w/v | weakened | low |
| D13-01 | w/w/v | weakened | medium |
| D13-02 | w/w/v | weakened | medium |
| D13-03 | w×3 | weakened | low |

Judge decisions of note: D3-01's fix direction is INVERTED (the stub fast path
is faithful to real orjson); D2-02 kept medium (33 C is in the shipped config);
D7-03's trigger is 0.03, not 0.02; D7-03-EXT is HIGH (the hang blocks the event
loop); D3 mutants S17/S18/S26/S30 all confirmed as test-suite gaps.

### Dedup notes

**Classifications.** One argument each, as the dedup step hands them to the panel.

| ID | Class | Argument |
|----|-------|----------|
| D0-01 | refuted-match, round-5 **#1294** | #1294 was the same change — a raised refinement cut with appended bang-bang seeds — and was **deferred, not fixed**: `carry-1295.json` records that the round-5 branch shipped #1295's warm start and dropped this one, that it cost +23.9 % sweep solver CPU, and that **on CI the two arms of each new behavioural check read identical objective values, so the finding was void on the machine of record**. D0-01 re-proposes the change and prices it in the objective alone over 64 cells; the carry's brief is explicit that a D0 knob must be priced in money (`tests/backtest.py`'s `score`) and in CPU (`stress.py`'s `SolverWork`) beside the objective delta, and this one carries neither. Attach the carry as a refutation argument; the panel should also ask whether the 11.1729 % maximum survives a second BLAS build. |
| D0-02 | new | residue of the released #1295 warm start, which added a fifth candidate without updating `optimizer.py:251`'s comment. Hygiene: the finder's own null control prices the dropped candidate at 0.0000 % in 80 of 80 cells. |
| D1-01 | regression of a released fix (**#1296**) | #1296 shipped `coordinator:_refuses_non_finite` on the four learned scalars dispatched from `_async_load_thermal_learning`; `DhwProfileLearner.apply_cooling_rate` is the fifth seam of that family, has no guard, and its own sibling's docstring names this exact hazard. The fix was narrower than the phenomenon. |
| D1-02 | corroborates closed **#1296** | the same class — a non-finite persisted value reaching live state with no quarantine, no reset and no log line — on a different store (accuracy → `DefrostDerate.from_dict`) that the round-5 guard set does not cover. |
| D2-01 | new | adjacency only: round-5 #1306 (closed) is the mirror-image clamp in `thermal_model`, one that silently deletes heat; this one makes the modelled COP discontinuous in a continuous forecast. Different symbol, different consequence. |
| D2-02 | new | the plan is priced against a source term with no physical origin. The finding's own honesty is worth preserving: the energy identity closes (this is booked heat, not deleted heat) and the golden fixtures do not move because no scenario configures an inlet above 20 C. |
| D3-01 | new — instrument defect | travels panel → judge → issue like any other, per the round-4 rule that a defect in an instrument is a finding of the dimension that met it. See the intake note on `orjson` for the verifier. |
| D4-01 | new — invited by a round-5 carry | `carry-1320.json` names this control by name, says the #1319 fix sized it by padding rather than by a floor, says **the judge accepted its survival under the #1320 perturbation**, and closes with "Measure them as findings of their own if you can price them; do not read their survival as the HTML floor failing." It is therefore **not** a regression of #1319/#1320, and the carry is the argument the panel needs. |
| D5-01 | new | a committed figure that no gate re-derives because `docs/` is INERT. |
| D5-02 | new | adjacency only: round-5 #1323 (closed) measured *inbound links* to handover and plan pages; this measures the README's own index table, and `docs/automations.md` is link-reachable, so #1323's check cannot see it. |
| D6-01 | new | a doc claim the code contradicts, with the contradicting module named in three places. |
| D6-02 | new | same defect class as closed #1326 (an artifact naming an entity the build never creates) on a surface #1326's fix did not touch: #1326 corrected prose, these are `default:` keys in two shipped blueprints. Worth the panel's explicit read as a class rather than a second instance. |
| D6-03 | new | the *documentation* half of the same pinned literal D6-02 measures. Kept separate: this one's fix is prose, D6-02's is YAML, and the finder's perturbations differ. |
| D7-01 | corroborates closed **#1308** | #1308's fix multiplied `identify()`'s excursion term by a drift-share discount. D7-01 measures `identify_slab` — the two-state fit that `_finish` routes **every declared plant** to, i.e. the path production actually runs after #1329/#1330 — whose `_slab_confidence` has no discount and no term for the parameter of interest at all. `carry-1308.json` predicted the asymmetry: "confidence is no longer a pure excitation/SNR read". The baseline includes #1375's sysid-adoption work. |
| D7-02 | new | residue of the released #1330 fix: refusing the cadence-gap path by name removed `identify()`'s last production route, so 379 lines and 11 sysid checks in `tests/features.py` pin a regression the integration never runs. The row also prices the ratchet's granularity (`dead_top_level_symbols` walks module-level defs only, so `optimizer.py:2100`'s duplicate `return` is invisible). |
| D7-03 | new | an exception leaving a production symbol; `_lm_solve` clips one of its three parameters and documents that it clips them. |
| D8-01 | corroborates closed **#1335** | #1335's fix gated 14 enabled-by-default unavailable entities with an evidence marker; the five `_DHWEntityMixin` classes are the same class outside that set, and the family default is mixed (the temperature sensor alone is off). |
| D9-01 | corroborates closed **#1337** | the round-5 finding measured 96.6–97.6 % starvation on the `#511` fallback route; this measures 0.9737 at a baseline that includes whatever closed it, and prices the eight yields at 0.75 of a point. **What closed #1337 is not verifiable from the tree** — there is no `carry-1337.json` and no in-tree citation of it — so the panel should establish whether the eight `sleep(0.002)` sites were its fix before reading this as a regression. |
| D9-02 | new — instrument defect | adjacency only: closed #1338 measured the same instrument's *sensitivity floor*; this names an entry point it never wraps. Different mechanism, so not merged. |
| D10-01 | new | the row's status is honestly keyed to the record it names; what fails is the *predicate* — the rule's bar is per module and the record is a package ratio. Round 4's D10-01 measured register rows contradicted by execution; this is a true status keyed to the wrong quantity, and the panel should not read it as the earlier finding recurring. |
| D11-01 | new | adjacency only: closed #1300 (and `carry-1300.json`) is the boundary's *ruleset ids*; this is the *enforcement surface's* CODEOWNERS coverage. The carry's remeasure — enumerate both rulesets — is still the right first step for any D11 seat. |
| D11-02 | new | the finder states its own fix scope also closes D11-01, but the mechanisms are distinct (a checkout `ref:` versus an owner pattern), so they stay two rows and the panel should price them together. |
| D12-01 | corroborates closed **#1302** | #1302 was the same phenomenon — a component published for a plant that does not model it — and its fix covered the ECL110 topics. D12-01's finder additionally names #1335's shape: the per-store sensors were gated by probe and the aggregate was left. |
| D13-01 | new | a process-shape finding: the rework is real, the class that names it exists, and nothing emits it. |
| D13-02 | new | adjacency only: closed #1304 folded a verdict class `VERDICT_RE` refuses; this is the histogram's denominator and the merges it never saw. |
| D13-03 | new | bears directly on closed #1303's artifact — `carry-201.json` names `.claude/workflows/cfr_exclusions.json` as the list #1303 registered, and its brief warns that growing the list is a deliberate act because an unjustified entry hides a real change failure. D13-03 measures the other end: the *keying* the metric reads is the merge commit, where `record` cannot gate, so the exclusion is inert where it is applied. |

**Two round-level observations**, recorded rather than filed:

- **Exposure contamination in the baseline export.** Three finders report that
  `tools/audit/round3/`, `round4/`, `round5/`, `round5-fix/` and
  `RELEASE_NOTES.md` were still present in the export although the round's own
  prep has a `strip_earlier_rounds()` for exactly that. Each says it did not open
  them as a to-find list (D7: "the export was not stripped as the task supposed. I
  did not open them"; D5 and D6 record the same). This is a defect in this round's
  baseline construction, in the same class as round 4's two instrument defects; it
  is named here so the next round's prep is checked before the finders are
  dispatched, and it is not a finding of any dimension.
- **There is no Round 5 section in this document.** Round 5's record is its 48
  issues (#1293–#1340) with their delivery rows, the round-5 harness directories
  under `tools/audit/round5/`, and the `carry-*.json` files — the last of which
  are the binding artifacts for six of this round's rows. Named here rather than
  quietly filled by this round, the way round 4 named the missing Round 3.

### What this commit does not carry

`tests/closure.py`'s `INERT` prefix covers `tools/audit/`, **but not the five-part
round-harness `.py` corpus**: `closure._is_header_corpus` takes any
`tools/audit/round*/D*/*.py` out of the INERT claim, because
`tests/harness_headers.py`'s discovery opens every one of them, so each is a
recorded read of that script and belongs in its closure in `tests/closures.json`.
Round 4's 153 flat-layout harnesses are in that closure; round 5 avoided the
question by nesting its harnesses one level deeper (`round5/D0/seat-a/…`, six
parts, which the predicate does not reach). Round 6's harnesses are at the flat
round-4 depth, and the closure table can only be re-derived on Linux.

So this commit carries every classifiable round-6 file — all 14 `REPORT.md`s, the
12 finding JSONs, the recorded `RESULT` output, the fixtures and the two `.mjs`
harnesses — and **lists the 60 `.py` harnesses in its body instead of committing
them unclassified**. They stand at their finder paths in the export
(`~/audit-r6-baseline`) and the five worktrees
(`~/audit-r6-{D0,D3,D9,D11,D13}`). Two ways to land them, both
for a seat with a Linux runner or the closures job: re-record
`tests/closures.json` so `harness_headers.py`'s closure absorbs the corpus (the
round-4 precedent), or move the corpus one level deeper the way round 5 did and
update the `harness_path` fields with it. Neither belongs in this record-only
commit, and the register's harness paths stay the finder paths until one lands.
D4's 138 screenshots (12 MB) are likewise not committed: they are regenerated by
`node tools/audit/round6/D4/card_qa.mjs --shots`.

## Round 7 — baseline v6.6.10-tree (`f9d6f782`), 2026-09-23

The second round at **fourteen** dimensions. Baseline
`f9d6f78243fa65f6fa128d2357752a2ae7f60648`, the commit that carries the whole
round-6 fix wave — so **every round-6 issue was already closed when these
finders ran**, and each row below that has a round-6 counterpart is a
measurement of the tree *after* that counterpart's fix. The `v6.6.10` stamp
runs in parallel on `6e2a0f2a` and is not part of this baseline. **This
commit is based on the stamped tree**, and the two differ by the stamp and
nothing else: `git diff f9d6f782 6e2a0f2a` is `VERSION`, `manifest.json`'s
`version`, the card's `CARD_VERSION`, `RELEASE_NOTES.md`, and the two claim
files' `claims-for:` lines — every changed line is a version string, and no
production or test logic moves. A fix wave may be based on either tree, and
this register's harness paths and every number in it are the baseline's.

Evidence is `tools/audit/round7/`: every dimension's `REPORT.md`, the finding
JSONs of the **five** dimensions that carry one, the recorded `RESULT`/`.out`
output and the fixtures. **The 44 harness `.py` files are not in this commit**,
for the reason round 6's register gives and under the same predicate; the exact
predicate, the files it reaches and the recipe are under *What this commit does
not carry* below. D11's `REPORT.md` is reconstructed by the orchestrator from
the finder's JSON return — its own `report_note` says so — and every other
report was written by its finder. Nine dimensions reported no finding JSON at
all (see the second intake note).

**The quiet window is complete.** `QUIET.md` re-took the round's one
provisional number (D9-02, on an idle box, two runs) and ran D3-01's four
pre-screened mutant sites through the **full** gate
(`GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1`, one run at a time under the
`quiet-r7` lease). Both results are in the rows below; nothing else was
re-taken, and no other number in this round was provisional.

### Intake validation

Every finding that carries a JSON was validated field by field against
`tools/audit/finding.schema.json` with `jsonschema` 4.26 (`Draft7Validator`),
covering the required finding fields, the `cpu_or_wall` enum, the
`cpu|wall ⇒ null_control` conditional, the id and severity patterns, the
`harness_path` prefix pattern, the `stop_rule_class` enum, and the `title` /
`metric_definition` length limits. **11 of 11 pass; 0 rejected at intake.**

- **Nine of the fourteen dimensions carry no finding JSON** — D0, D2, D4, D5,
  D7, D11, D12 and D13, and D6 as well because it is dry and so has nothing to
  carry. The first eight hold **19** findings, validated from their `REPORT.md`
  text as round 6 did for D2 and D10 — but round 6 had three such findings and
  this round has nineteen. Every one of the nineteen names the executed command,
  the harness, the value and the machine, and every one but D2-01 states a
  perturbation with its direction (D2-01 states a null control, the 200 L cell,
  and no perturbation).
- **The systematic absences, recorded rather than invented**, and they are an
  artifact of the missing JSONs rather than of the findings: **`stop_rule_class`
  is stated for D0, D2, D5, D11 and D12 and absent for D4, D7 and D13**;
  **`instrumented_symbol` is named by D0, D7, D11 and D12 and absent for D2, D4,
  D5 and D13** (D4's instruments measure rendered geometry in a browser, D5's is
  a text scan, D2's are the production symbol named in prose and an AST walk,
  and D13's readers are named in each row's seam rule and `Files:` line); and
  **per-finding `load1`/`thread_factor`/`tolerance` are absent for most prose
  rows**, quoted once at dimension level instead. No number is invented to fill
  one, and the panel should read a prose row's evidence fields from its report
  rather than from a schema shape.
- D9-02's JSON carries the **pre-quiet** figures (`762.1 ms`, share `0.3511`).
  The JSON is the finder's artifact and stands as written; the row below carries
  the quiet values, and `QUIET.md` is the record of the difference.
- **The D10 finder's JSON was written to the seat's scratch, not to the round
  directory.** It is committed here as `tools/audit/round7/D10/report.json` for
  the first time and is byte-identical to `/private/tmp/d10r7/report.json`.

### Dedup — 30 findings, 30 rows, 0 merges

The merge rule is the finder contract's: one row per mechanism, but **do not
merge findings whose finder stated distinct instrumented symbols, perturbations
or consequences**. Three pairs were examined and refused:

- **D4-01 / D4-02** share one root — *intrinsic content wider than a clipping
  ancestor, hidden rather than wrapped or scrolled* — and the D4 report says so
  itself, then adds "a different container and a different fix". They differ on
  the seam (`--seam savings` versus `--seam tabs`), the clipping declaration
  (`.dlg-body`'s `overflow-x: hidden` versus `dialog.expanded`'s
  `overflow: hidden`), the language that triggers them (D4-02 is unreachable in
  English at every width) and the patch that closes them. Kept as two rows.
- **D13-02 / D13-05** both drive `policy_lint.mjs:statsHistogram` against
  `web-fix-wave.js`, but on different literals: D13-02 on the **grammar**
  (`VERDICT_RE`'s anchoring, case and 40-hex requirement versus the histogram's
  `^Fix review:\s*(merge|blocked)\b` with `i`) and D13-05 on the **class
  vocabulary** (`VERDICT_CLASSES` versus the word a reviewer actually wrote).
  The perturbations are one-line edits in different files, and the consequences
  are opposite in direction: D13-02 is the histogram counting shapes the wave
  would refuse, D13-05 is the wave routing a class the histogram counts.
- **D13-01 / D13-02 / D13-03** were each examined against the same question —
  is this one "the reader cannot see its own window" finding? — and refused
  three ways: D13-01 is a missing endpoint request, D13-02 a grammar, D13-03 an
  exit-code headline. Three files, three perturbations, three distinct
  delivered values.

**Classification.** 22 new, **4 corroborating a closed round-5/6 issue**, **2
corroborating a closed round-4-or-earlier issue**, **2 matching a deferred item
`docs/backlog.md` already carries in prose**, 0 regressions of a released fix at
the same symbol, 0 matches to a refuted earlier finding. The "corroborates an
*open* round-5/6 issue" branch is **empty, and that is a fact about the calendar
rather than the findings**: round 6's 38 issues were all closed before
`f9d6f782`. **Five of the six corroborations that name a released fix drive that
fix's own instrument, and in each the fix does not reach the direction
measured** — D0-01 drives the solve certificate #1435 added, D7-01 the adoption
gate #1437 installed, D8-02 the dynamic mixin default #1429 installed, D13-06
the dual keying #1433 installed and D10-02 the checker-only alias #994 left; the
sixth, D10-01, is a recorded decision's stated basis rather than an instrument.

**The round-5 and round-6 carry files are the binding argument for three of
these rows**, and a panel must read them rather than the issue titles:
`carry-1398.json` (D8-02), `carry-1412.json` (D3-02's lane) and `carry-1330.json`
/ `carry-1308.json` (D7-01's history). Each states what the counter-part fix
narrowed and what a later seat must re-establish at its own merge base.

**One pair is one row because its finder made it one.** D3-01 reports four
production sites under a single instrument, a single operator pair and a single
measured closure, so it is one row with four confirmed sites and not four rows;
the sites are named in the row and each is separately actionable.

### The dimensions

| # | Dimension | Findings |
|---|---|---|
| 0 | Price optimality | reported (1 finding(s)) |
| 1 | Robustness and stability | reported (2 finding(s)) |
| 2 | Mathematical and physical sanity | reported (2 finding(s)) |
| 3 | Test-suite gaps | reported (2 finding(s); D3-01's four sites confirmed at the full gate) |
| 4 | UI/UX | reported (3 finding(s)) |
| 5 | Docs structure, flow and content; code comments | reported (2 finding(s)) |
| 6 | README and documentation claim verification | **dry — 0 finding(s)**, 34 of 38 claims executed true |
| 7 | Architecture and maintainability | reported (1 finding(s)) |
| 8 | Sensor verification and ordering | reported (2 finding(s)) |
| 9 | CPU and memory efficiency, Raspberry-Pi-class target | reported (3 finding(s); D9-02 quiet-confirmed) |
| 10 | HA integration quality scale | reported (2 finding(s)) |
| 11 | Governance mechanisms and policy | reported (3 finding(s)) |
| 12 | Generalization | reported (1 finding(s)) |
| 13 | Process yield and cost | reported (6 finding(s)) |

**30 findings across 14 dimensions.** Severity from the reporting finder was
4 high, 19 medium, 7 low; judge-final is **2 high, 19 medium, 9 low**
(26 verified, 4 weakened, 0 refuted, 0 unreproduced). Round 6's 31 findings
were 7 high / 12 medium / 12 low, so this round is one finding lighter and
three narrower at the top.

### Findings register — round 7

Severity from the reporting finder. Status is the judge's verdict — `verified`,
or `weakened → <final severity>` for the four the judge moved — with the judge
section below carrying the panel vote and the class.

#### D0 — Price optimality

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D0-01 | medium | the space-only multi-start anchors energy to the two fractions `{0.35, 1.0}` of the thermostat baseline and never brackets the optimum on the default two-zone winter cell, where the optimum sits at **0.20×** and the shipped plan is 0.4374 % (1.060 SEK/day) above its own objective's fixed point; the recorded solve certificate's ladder `{0.7, 1.25, 1.5, 2.0, 2.5}` starts above 0.7 and is single-zone only, and at flat prices the gap is 0.0000 % — the null control that makes this a price gap and not a comfort one | verified |

#### D1 — Robustness and stability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D1-01 | medium | `async_simulate` sets `_last_simulation` only on its **success** return (`coordinator.py:10751`), so every failing return — the shadow solve raising (`:10700`), `invalid_windows`, `wood_err` — leaves the rate-limit slot empty and each further `simulate_plan` call launches a fresh multi-second solve: 5 calls start **5** shadow solves where the success path starts 1. Reachable in the steady state of the #783 worker-fallback latch, i.e. an install whose child interpreter cannot start | verified (held against the panel) |
| D1-02 | low | `_plan_is_stale` is consulted by `_apply_action` (`coordinator.py:6560`) and nowhere else among the write paths: `_async_drive_pumps` (`:2590`) runs one call later with no staleness test and reads an expired plan at its last step, so 1 of the 2 actuating paths writes to the plant from a horizon the plan has been declared unfit to actuate. The direction is the safe one (the stale `_current_action` forces the space pump ON), which is why this is low — the consequence on this baseline is nil and the gate's authority is what the next write path will be judged against | verified |

#### D2 — Mathematical and physical sanity

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D2-01 | low | `_simulate_step_two_zone` computes the tank's rate over `max(C_buf, 0.01)` while the same step's availability bound and its stiffness count use the raw `C_buf`, so the stored energy becomes `C_actual/0.01` of the heat delivered: at 5 L (`C=0.00580`) the balance closes **+5.456e-03 kWh** long on one step, and at 200 L it closes to 1.2e-15; the same three-way disagreement is written at three more seams in the file (`C_w`, `C_dhw`, and `_stability_substeps`' third value `0.04`). The config flow's own volume floor (10 L) makes every seam unreachable from the UI, which is why it is low | verified |
| D2-02 | low | `HeatPumpOptimizer._terminal_cost_batch` ends with two identical `return cost_batch` lines and the second (`optimizer.py:2119`) cannot execute — the only unreachable statement in all 65 package modules (AST walk; deleting it by text substitution drives the count 1 → 0, so the instrument is drivable) | verified |

#### D3 — Test-suite gaps

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D3-01 | medium | **four production guards and clamps are deletable with no driver in their measured closure failing** — `legionella.py:528` (`if signature == self.ceiling_notice:`, the Repairs-issue de-duplication), `optimizer.py:3131` (`if f.size < n_steps:`, the horizon-length pad), `sensor.py:2547` (`if not isinstance(items, list):`, the payload-type guard) and `thermal_model.py:1309` (`t_in = min(t_in, dhw_setpoint)`, the coil-draw clamp); the finder's `confirm` tier has 7 sites and 4 survivors, the other 3 killed by `tariff.py:139`×2, `coordinator.py:7743` and `optimizer.py:6377` | **confirmed at the full gate** — all four survived `GATE_SCOPE=full GOLDEN_MODE=drift` in the quiet window (`e8e319b5`, `6bf224ae`, `d4c3da05`, `ae78a384`), each killed by no driver, with `env_drift.py --all f9d6f782` in the lane and not among the reds  — judge **weakened → low** (1 of 4 sites genuine) |
| D3-02 | medium | `tests/mutation_table.py` counts a changed exit status as a kill, and `tests/structure.py` exits **2** for a mutant that only *improved* a structure metric — its own output says "Nothing here is a violation" — so a mutant no assertion covers is recorded as killed: `coordinator.py:8708:GUARD_OFF` fires rc=2 with `cut_learning` 285 → 284 and **zero failing checks anywhere**, 1 of the 40-mutant sample, and 2 of the 5 kills in the 22-mutant `t1` pre-screen came from this channel. The recorded `survivor_fraction` is optimistic by however many sites it covers, and `last_measured.full` already sits exactly at its cap (12/40 = 0.30 of 0.30) | verified |

#### D4 — UI/UX

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D4-01 | high | the savings table is `width:100%` inside a `.dlg-body` whose min-content width exceeds it and whose `overflow-x: hidden` forbids any scroll, so the last column — the `%` figures, right-aligned — is painted outside a box no gesture can widen: **22.4 px** of unreachable ink at 375 px in English, 41.1 px in Swedish, 75.2 px at 320 px; leave-one-out over the 20-cell grid drops the most favourable cell and still reads 75.2 px, and at 1280 px the table's `scrollWidth` equals the body's `clientWidth` (1197 = 1197) with every seam at −1. The what-if value cells are the same declaration at 320 px (21.8/12.5 px) | verified |
| D4-02 | medium | `.dlg-tabs` is `flex: 0 0 auto` inside `dialog.expanded`'s `overflow: hidden`, so the longer Swedish tab label `Rådgivare` is clipped where English never overflows: **7.5 px** at 360 px, 45.9 px at 320 px, and the pill spills 6.9 px even at 375 px where the label is inside the box | verified |
| D4-03 | high | one card, one screen, one quantity, two currencies: the headline savings item takes the plan **sensor's** declared `unit_of_measurement` (and says in its own comment that a card-config `currency:` must not relabel it), while the savings table heads take `this.plan.currency()`'s different precedence (`config.currency \|\| attrRaw("currency") \|\| hass.config.currency \|\| "SEK"`), so **3 of the table's 5 heads** contradict the headline it sits above. Three reachable arms, the weakest needing no card edit at all (`--hass USD`); both controls read 0 | weakened → medium (1 of 3 arms) |

#### D5 — Docs structure, flow and content; code comments

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D5-01 | low | `legionella.py:358` says an attempt drives `hours_since` to 0 "because `_dhw_hours_since_legionella` counts attempts too" — **no such symbol exists in the package**; the behaviour described is `hours_since` at `:614`. Three further backticked comment identifiers resolve to nothing (`const.py:80`'s `MIN_POWER`, `sysid.py:1283`'s `T_prev`, `thermal_model.py:1831`'s `MixedHotWater`), and the wrong name is already mirrored into `tests/features.py:27101` | verified |
| D5-02 | low | the card's `hours` error message states a bound its own check does not enforce: `setConfig` rejects on `hours <= 0 \|\| hours > 168` — the accepted range is `(0, 168]` — while `errors.cfg_hours` says "must be a number between 1 and 168" and the editor schema pins `min: 1`; a hand-written `hours: 0.5` therefore passes validation while the message calls it invalid and the editor can neither produce nor correct it (`card_hours_bounds_disagree=1` → 0 under the one-line edit `hours < 1`) | verified |

#### D6 — README and documentation claim verification

**Dry.** `claims_extracted=38`, `claims_checked=34`, **`claims_true=34`**,
`claims_false=0`, `claims_stale=0`, `claims_unverifiable=4` (four external or
historical facts the brief forbids reading: an HA release fact, a since-v5.0.0
translation claim, a one-off comfort-weight measurement, and a wall-clock
figure). Entity names and counts were driven through the real
`async_setup_entry` via `tests/entities.py:collect`, not by listing classes.
The report also records five self-inflicted instrument gaps so a later round is
not misled by them — a `grep CONGESTION` that misses a per-step auxiliary
variable, a slug function that reports four false anchors on `·`/`—` headings,
a regex that reads a comment's `what_if:` instead of the key's, and the two
export-stripped files it had to stub to reach `collect`.

#### D7 — Architecture and maintainability

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D7-01 | medium | `SystemIdentification.identify_slab` appends **one** pseudo-observation of **fixed** width `0.1 kW` to its residual vector (`sysid.py:1690-1696`), where its one-state twin scales its ridge by `prior_rel = s_noise / prior_sd`; clean data never out-weighs a fixed-width pseudo-observation, so the fitted gains pin at the 0.3 kW prior exactly and the unmodelled free heat is absorbed by the UA column — **+7.44 %** (range 7.438–7.453 % across the three building presets) on a noise-free step response with the true free heat at 0 kW. The #1410 adoption gate bounds the fitted UA's *profile-likelihood half-width*, a self-consistency measure, so a prior-dominated fit passes it at ≈1e-4 and is adopted at weight ≈1.0; perturbation `gains_prior_kw` 0.3 → 0.0 moves the bias to 0.000 % | verified |

#### D8 — Sensor verification and ordering

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D8-01 | medium | `SensorGapAdvisorSensor._gaps` prices the missing house-power meter from `coordinator.data["house_power_series"]` and `["heat_pump_power_series"]`, and **`_build_data_dict` never writes either key** — the only two occurrences of the names in production are those reads — so every real install sees an empty series, `_window_peak` returns 0.0, and the house-power slot's "estimated extra cost per month" is a silent **0.00 SEK** where the series prices it at **30.0 SEK**. The tests pass because they feed the advisor a fake coordinator whose data carries the series | verified |
| D8-02 | low | `DHWSetpointAdvisorSensor` (`sensor.py:2361`) is the one hot-water sensor **not** wrapped in `_DHWEntityMixin`, so a no-DHW install ships it enabled by default with `available is False` on every refresh — 1 of 59 sensors, against the five mixin-wrapped DHW entities that correctly ship off. The mixin's `entity_registry_enabled_default` is the dynamic property the round-6 D8 fix installed, so this is the class outside that fix's reach | verified |

#### D9 — CPU and memory efficiency, Raspberry-Pi-class target

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D9-01 | medium | 3,437 of the 9,512 bytes of entity attributes written to the recorder **every optimisation cycle** (36.1 %) are either a series of the class the plan sensors already declare unrecorded (`dhw_usage_profile` 481 B, `components` 470 B, `candidates` 504 B, `gaps` 298 B = 1,753 B) or a byte-identical repeat of a `(key, value)` another entity published in the same cycle (1,684 B over 23 pairs); the plan sensors exclude 15,026 B/cycle by the same rule, which is what makes the inconsistency the finding rather than the taste. `456,576 B/day` recorded; leave-one-out with the largest entity dropped still reads 8,415 B/cycle | verified |
| D9-02 | medium | `optimizer._lbfgsb_restart` runs once per starting candidate and consumes **164 of the default two-zone DHW solve's 442 batched gradients (37.1 %)** and **752.3–756.3 of its 2,140.4–2,146.8 ms CPU (35.2–35.4 %)** — 39.7–40.2 `tests/stress.py:reference_solve` CPU ratios — against the code's own cost model, "one short L-BFGS-B run per candidate, not a second solve": a polish is ~59 % of a main run's length, so four candidates mean eight L-BFGS-B runs where four would do | **quiet-confirmed** (fan-out 0.3511 → 0.3515/0.3523, −1.3 %/−0.8 % on the CPU ms; gradients exact at 164/442 and 0.3710)  — judge **verified** |
| D9-03 | low | `tests/stress.py:1052-1058` tells a reader that both zero-range channels "take the whole solve off the batched jacobian" so scipy estimates every gradient with n scalar calls — measured on the shape that docstring's own builder produces, the fuse-cap solve runs **316** batched gradients, not 0, because the carve-out was removed and the fixed-variable NaN moved into `_batch_fd_gradient`. The second half is why it matters: the one-line edit that genuinely takes the solve off the batch moves the gate's `simulate_steps` channel by **+0.019 %** while its CPU moves 16.1× and its kernel CPU 24.1×, because the channel charges a batch at `rows × steps` — the two committed definitions of the same quantity disagree by a factor of 96 in opposite directions, so a fixer reading one sees a 97× win where the other sees 0.02 % | verified |

#### D10 — HA integration quality scale

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D10-01 | medium | the `strict-typing` (platinum) rule says "you need to add a `py.typed` file to your library" and its Exceptions section says "There are no exceptions to this rule"; the package ships **0** (`qs_py_typed_files=0`) and `quality_scale.yaml` marks the row `done` on a comment — "py.typed is not owed — the Platinum rule's marker-file half does not apply to a custom integration" — that appears in neither the rule text nor its warning box. Adding the file alone leaves `mypy_total` at 441, which is why the two halves of the rule are separate rows | weakened → low (re-open of #829) |
| D10-02 | high | the rule's warning box requires the custom typed config entry to be "used throughout" when `runtime-data` is implemented; the integration does implement it and does define `HeatPumpOptimizerConfigEntry`, but of the **100** `entry` parameters in the package only **10** use the alias and **88** are bare `ConfigEntry`. Two independent instruments agree and both move under one perturbation: `qs_entry_param_bare` 88 → 0 under `--perturb entry-alias`, and `mypy --strict`'s `[type-arg]` slice 95 → 7 (the 88 that vanish are exactly the 88 parameters), with a non-strict null control at 0 | weakened → medium (0 of 88) |

#### D11 — Governance mechanisms and policy

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D11-01 | high | the step that files the friction histogram's would-open verdicts is **skipped in every `record`-job run whose preceding disposition-refusal step fails** — 39 of the last 40 pushes to `main` — while the histogram that names those keys runs in 40 of 40 (it carries `if: always()` and the two filer steps do not): `filer_ran=1`, `filer_skipped=39`, `filer_ran_with_refusal_failed=0`. The #959 option-B loop therefore produces its trigger and the actor never runs. The null control is the one run in 40 whose refusal did not fail (`35701710582`), which is the one run whose filer ran | verified (window slid one run) |
| D11-02 | medium | `friction_issues.mjs:decide` never reads `existing.state`, so for a key whose issue a seat has disposed by closing it the recurrence is written **onto the closed issue** and reported as `UPDATED`; the exact-title search then suppresses a second issue, so a key disposed once can never be represented by an open issue again — 1 of the window's 2 would-open keys is in exactly that state and **0 of the 14 issues the lane has ever filed is open**. One-line sibling mutant moves the closed-issue count 1 → 0 | verified |
| D11-03 | medium | all three arms of `--sunset` fire only on a self-declared marker (`REFUSED BY`, `SUNSET:`, `HONOUR:`) and **none of the 39 policy files carries any of them** — the class reports `proposed (0) held (0)` over the corpus in the shape of a measurement while being unable to name a rule that has outlived its reason. All eight occurrences of the three markers in the whole tree are inside the linter's own fixtures and regexes; appending one marker line to a policy file moves `sunset_proposed` 0 → 1 with the bytes restored in a `finally` | verified |

#### D12 — Generalization

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D12-01 | medium | a config with `two_zone_mode="off"` and the zone keys still present passes the options-flow guard for `mixing_valve_write_target_kind="flow"` — because that guard tests `not current.get("upper_floor_thermal_mass")` (always False once the initial flow has written those keys, which the options flow cannot erase) instead of the model's `two_zone_enabled`, which honours the explicit override — and the saved flow target then issues **0** valve writes on every cycle while the same install's `indoor` target writes 1 under both modes (null control); `two_zone_mode off → on` moves the count 0 → 1. "Is this install two-zone" is decided twice, divergently | verified |

#### D13 — Process yield and cost

| ID | Sev | Finding | Status |
|----|-----|---------|--------|
| D13-01 | medium | `policy_lint.mjs:fetchWindow` fetches two endpoints per pull request (`/pulls/<n>` and `/issues/<n>/comments`) and never `/pulls/<n>/reviews`, so a verdict posted as a review is not merely unweighted but **invisible**: `reviews_endpoint_requests_stats=0` against `pull_requests=31` and `issue_comments=31`, and the perturbation that adds the fetch moves it 0 → 31. The brief defines a verdict as "an issue comment **or** a pull-request review". **This window's magnitude is 0** — across all 31 pull requests and 30 verdicts, `verdicts_from_reviews=0`; every review is an `hpo-approver` echo or a `tvofi` owner review and neither first line starts `Fix review:` | verified |
| D13-02 | medium | the histogram's matcher `^Fix review:\s*(merge\|blocked)\b` with `i` diverges from `web-fix-wave.js`'s `VERDICT_RE` on **four** axes and every difference is one-directional, the histogram accepting what the wave refuses: a missing space, case, a missing 40-hex SHA, a 12-hex SHA, trailing text after the SHA (**7 of the harness's 12 shapes** counted by the histogram and refused by the wave, with 2 control shapes counted by both and 3 refused by both). Within one function the `merge` arm counts a SHA-less line while the `blocked` arm sends the analogous line to `unclassified` | verified |
| D13-03 | medium | the `record` job's summary reads the exit code and nothing else, so a window it could not enumerate is reported **cleaner** than a window it read and found a violation: with the transport forced to HTTP 500 on `/commits/<sha>/pulls` the enumeration falls back to subject mode, `cmdRecordDispositions` exits **0**, and the report step renders "clean — every merged pull request in the window has a disposition" over a window the same run's `enumSkipLine` marks UNCHECKED. The headline a seat opening the run first sees asserts a measured clean window | verified |
| D13-04 | medium | a `pull_request: [edited]` body edit re-runs **five of `governance.yml`'s seven jobs**, and `governance_cost.py` publishes the resulting dispatch count as "the number of rounds the body contract took": keyed on the workflow-run id in each check run's `details_url`, the 31 heads carry **46 dispatches** (12 heads with more than one: 9×2 and 3×3), 15 extra at 145 s each = **2,175 s of governance CI** over a window whose whole governance cost is 226 s/merge; `pr-contract` is 22 s of the 145 and `env-matrix` — a matrix check that cannot read a pull-request body at all — is 73 s. The re-keying perturbation (head → merge commit) takes 46 to 30 and the distribution to `{0:1, 1:30}`, because a merge commit is never edited | verified |
| D13-05 | medium | a block class reviewers **write** is outside `VERDICT_CLASSES`: `#1429`'s `product-tradeoff-regression` is counted by the histogram and routed to `other` by `parseVerdict`, so the two readers disagree about **1 of the window's 2 blocked verdicts** and about 100 % of its engineering blocks (the other is `root-cause-unanswered`, a process class). Adding the word to `VERDICT_CLASSES` moves the disagreement 1 → 0 with the taught control row agreeing in both arms | verified |
| D13-06 | medium | the merge-keyed change-failure rate counts a merge that **passed the same lane at its own head**: `mutation` is **4 of the window's 7 counted merge-keyed failures (0.129) and 0 of the 31 pull-request heads**, so the two keyings read 0.226 and 0.129 and the 4/31 that separates them is invisible. The four merges are `#1426 #1443 #1425 #1442` — two pairs 4–5 s apart, i.e. two batch merges — and `tests/mutation_table.py` computes its inventory from **the tree**, so on a push to `main` (where the base *is* `HEAD`) it measures the merged tree. Filed as a finding about the instrument, not a request to widen the exclusion list: which of the two numbers is a change failure is the list owner's judgement and needs both | verified |

### Judge verdicts — round 7

The audit judge re-measured every finding on the shared, though not idle, box
(`load1` 2.6–4.2, never gated on; `thread_factor` 1.000, 1.0006/1.0016 on the
two solver harnesses that print their own) — the **eight** disputed rows by
re-running their harnesses, perturbations and null controls, the rest by
spot-checking the harnesses that can be driven here — and assigned the
stop-rule class. **30 findings: 26 verified, 4 weakened, 0 refuted, 0
unreproduced.** Final severity **2 high / 19 medium / 9 low**. Panel vote is the
three-verifier tally (`v` = verify, `w` = weaken). No tree is left mutated.

| ID | panel | verdict | final |
|----|-------|---------|-------|
| D0-01 | v×3 | verified | medium |
| D1-01 | w/w/v | verified | medium |
| D1-02 | v×3 | verified | low |
| D2-01 | v×3 | verified | low |
| D2-02 | v×3 | verified | low |
| D3-01 | w×3 | weakened | low |
| D3-02 | v×3 | verified | medium |
| D4-01 | v×3 | verified | high |
| D4-02 | v×3 | verified | medium |
| D4-03 | w×3 | weakened | medium |
| D5-01 | v×3 | verified | low |
| D5-02 | v×3 | verified | low |
| D7-01 | v/v/w | verified | medium |
| D8-01 | v×3 | verified | medium |
| D8-02 | v×3 | verified | low |
| D9-01 | v×3 | verified | medium |
| D9-02 | v×3 | verified | medium |
| D9-03 | v×3 | verified | low |
| D10-01 | w/w/v | weakened | low |
| D10-02 | w/w/v | weakened | medium |
| D11-01 | v×3 | verified | high |
| D11-02 | v×3 | verified | medium |
| D11-03 | v/v/w | verified | medium |
| D12-01 | v×3 | verified | medium |
| D13-01 | v×3 | verified | medium |
| D13-02 | v×3 | verified | medium |
| D13-03 | v×3 | verified | medium |
| D13-04 | v/v/w | verified | medium |
| D13-05 | v×3 | verified | medium |
| D13-06 | v×3 | verified | medium |
| R7-INSTR-01 | round-level | recorded | medium |

The **round-level instrument finding R7-INSTR-01** was not sent to a panel —
it is a round-level observation, recorded rather than dimension-filed — so its
"verdict" column reads `recorded`; it is classed `bug` and filed as its own
issue.

Judge decisions of note: **D1-01 is held at the finder's severity against the
panel majority** (`w/w/v`), decided on the judge's own measurement: the harness
stubs `_await_process`, so its count is *submissions*, not solves. Driving the
real path both ways, the stated consequence materialises on the
shadow-solve-then-raises arm (5 calls → 5 solves, 2,225 ms against 377 ms
healthy, a 5.9× amplification) and not on the named #783 worker-fallback arm
(5 calls → 0 solves, 93 ms), so the severity is unchanged. **D3-01 is weakened
to low, 1 of 4 sites genuine**: `thermal_model.py:1309` is an equivalent mutant
(the downstream `max(0.0, dhw_setpoint - t_in)` floors the numerator whether or
not the clamp runs), `optimizer.py:3131` and `sensor.py:2547` are
distinguishable but unreachable (both pads are ≥ `n_steps` by construction at
every call site; the only producer of `narrative.items` returns `list[dict]`),
and only `legionella.py:528` is a reachable, driver-invisible gap — whose
user-visible half ("a dismissed notice comes straight back") is not itself
measurable in this tree, the stub modelling re-creation as idempotent. **D4-03
is weakened to medium, 1 of 3 arms reachable**: production publishes
`"currency": coordinator.currency` from the same `coordinator.currency` the
headline unit resolves, so `--hass USD` and `--sensor EUR` cannot arise (the
stub's omission of the attribute is what fires them); only the card-config
`currency:` override is reachable, and there the table relabels the sensor's
figures under a headline that keeps them. **D10-01 is weakened to low and is a
re-open, not a fresh defect**: `docs/plan-2026-09-open-issues.md:470` and PR
#876 (`e59ac74`) record #829 closed **completed** with "`py.typed` was not
added" — an owner disposition — so the register's carve-out *comment* is not a
defensible reading of rule text that states no exceptions, and the residual is
to state the executed number and the disposition in that row, not to re-file
the defect. **D10-02 is weakened to medium**: 88 bare / 10 custom and
`mypy_type_arg=95` both reproduce, but **0 of the 88** bare-`ConfigEntry`
parameters has a body that mentions `runtime_data` (AST-confirmed; the
dereferences live at `services.py:376`, `sensor.py:228`, `diagnostics.py:123`,
`__init__.py:316/381/403`), so the literal "used throughout" is still violated
and the row is still claimed `done`, but the consequence is not high. **D7-01
is held at medium**: the fixed-width ridge is deliberate and documented, but
the #1410 gate's own docstring says a clean residual "is exactly what a
prior-dominated, useless fit looks like", and the judge re-took that gate
admitting at halfwidth 1.1e−4 against a 0.0953 bar — a documented mitigation
whose stated failure mode it does not catch. **D11-03 carries a wording
correction**: "unable to name a rule" is too strong — the class *does* fire on
a marker — the defect is that `held (0)` prints in the shape of a measurement
over 39 files none of which carries one. **D13-04 is not by design**: the
`edited` guard's own comment says a body edit "must re-check the contract
without re-running the forty-minute gate", and the measurement says it re-runs
**five** jobs at 145 s, the contract being 22 s of it. **D11-01's window slid
one run** (`refusal_failed` 38, not 39; the ratio is identical) and
**D13-01's** (32 pull requests, not 31) — both re-takes on the moving window,
not disagreement. Stop-rule classes: `bug` for D0-01, D1-01, D2-01, D4-01,
D4-02, D4-03, D7-01, D8-01, D8-02, D9-01, D9-02, D11-01, D11-02, D12-01 and
D13-03; `hygiene` for the other fifteen. One housekeeping item outside the
verdicts, for whoever fixes D3-01: the D3 round's own deliverable cannot merge
— `tools/audit/round7/D3/{probe,screen,structure_kill}.py` force the FULL
suite and its `REPORT.md` is named by `COMMON.md` with no `policy_budgets.json`
cap (QUIET.md records both; the judge reproduced neither) — and *What this
commit does not carry* below names the same predicate.

### Dedup notes

**Classifications.** One argument each, as the dedup step hands them to the panel.

| ID | Class | Argument |
|----|-------|----------|
| D0-01 | corroborates closed round-6 **#1378** | The round-6 D0 finding's class fix is **#1435**, whose delivery row names the issue it closed in passing — "a solve certificate plus a growing energy-diverse cell grid (#1378)" — and that certificate is what this row drives. This measures that certificate and finds its ladder `{0.7, 1.25, 1.5, 2.0, 2.5}` starting **above** the shipped 0.35 seed and its cells **single-zone only**, so the direction measured here — under-heating a two-zone slab to 0.20× baseline energy — is outside the certificate by construction. Round-1 #185 (a bang-bang start at 0.35 on arbitrage prices, closed) and round-5 `carry-1295.json` (the deferred #1294 refinement cut) are the other two directions of the same knob; a D0 fix must price this one in money (`tests/backtest.py`'s `score`) and CPU (`stress.py`'s `SolverWork`) beside the objective, which is what the carry warns about. The flat-price null at 0.0000 % is the argument that this is price structure and not comfort. |
| D1-01 | new | No prior round measures `async_simulate`'s rate-limit slot. Round-2 D1-05 (closed) measured a shared-reference race on the what-if's *executor* path and round 6 filed nothing here; the null control (the same five calls succeeding start 1 solve) separates the limiter from the call loop. |
| D1-02 | new — **named in `docs/backlog.md` item 3** | The phenomenon is not a discovery: `docs/backlog.md` item 3 ("a stale plan never neutralises what it wrote") states that `_apply_action` returns silently on `_plan_is_stale()` and that `_async_drive_pumps` indexes the retained plan by wall clock, and its fix scope reads "gates `_command_frequency()` and `_async_drive_pumps()` on the same predicate". That item has not landed, so this row is the *countable* half of a designed-and-deferred fix: the item is owed a gate, not a diagnosis. The panel should read the backlog item before pricing the fix and should not take this as a new mechanism. |
| D2-01 | new | Adjacency only. Round-6 D2-01 fixed the defrost derate's bucketing (#1381/#1428) and round-6 D2-02 the DHW inlet floor (#1382/#1420); both are held at this baseline and both are named in this round's D2 non-findings. This is the third capacity-shaped defect in the same file, and its own row prices the reachability honestly: every seam is below the config flow's own volume floor. |
| D2-02 | new — residue of a round-6 row's parenthetical | Round-6 D7-02's own row closed with "the row also prices the ratchet's granularity … so `optimizer.py:2100`'s duplicate `return` is invisible", i.e. the statement was **named in a row and fixed by nothing**. The fix that closed that row (**#1443**) touched `sysid.py`, `tests/features.py` and `tests/structure.py` and not `optimizer.py`; the duplicated line is still there (at `:2119`, `:2100` in round 6's reading), and this row is the first to give it an instrument (an AST walk with its own mutation proof) rather than a mention. |
| D3-01 | new | Round-6 D3-02…D3-05 were four *other* sites (#1384, #1385, #1386, #1387), all closed by **#1441**'s test-only fixtures. Round-4's D3-S2 was `legionella.py:521`, the disabled-feature guard — a different line from `:528`. The four sites here were re-run through the **full** gate in the quiet window and all four survived, so the row is `confirmed` rather than `provisional` and no killing check exists to name. |
| D3-02 | new — instrument defect | Travels panel → judge → issue like any other, per the round-4 rule that a defect in an instrument is a finding of the dimension that met it. Adjacency: `carry-1412.json` is the same ledger's key-collision warning (the `killed_by` populator), a different hole in the same record; this one is the **kill rule** reading an exit status whose own output says nothing was violated. `last_measured.full` sits exactly at its cap, so the panel should price the re-take with the fix, not after it. |
| D4-01 | new | Adjacency only. `carry-1320.json` names the card's *hit-target floors* under a coarse pointer and says the #1319 fix sized the control by padding rather than by a floor; this measures **unreachable ink**, a different property of a different container. Round-6 D4-01 (the score pill under the coarse floor, #1388) was a size finding. Nothing in the record measures a clipping ancestor's scroll reach. |
| D4-02 | new | The same root as D4-01 in a different container with a different fix, and the D4 report says so; kept apart for the reason the merge rule gives. The distinguishing measurement is the language arm: English never overflows at any width, so the row is only visible with `--lang sv`. |
| D4-03 | new | Adjacency: closed round-1 **#168** ("Hardcoded SEK in config-flow labels and two Repairs notices despite currency-agnostic price data", fixed by B3 in v6.2.17) is the *origin* of the card's `currency:` option, and `docs/backlog.md` item 11 is the wider currency seam. Neither measures two surfaces of one card resolving the same quantity by different precedence, which is what makes this row a contract defect rather than a hardcoded string; the finder's correction is that the headline's comment is right and the table is what is wrong. |
| D5-01 | new | Round-2 D5-05 (closed) was the same *instrument* — backticked identifiers in production comments that resolve to nothing — and its instance was `thermal_model.py:191` naming the wrong service. This is a fresh instance on a different symbol, and the finder prices the class at 4 with a 1-unit perturbation. |
| D5-02 | new | Adjacency: round-2 D4-07 (#170, closed) was a card slider range "shielding a real validator". This is the same class — a user-facing string stating a bound the code does not enforce — on a different control, and the finder tags it for D4 as well as D5 because the artifact is a user-facing string. |
| D7-01 | corroborates closed round-6 **#1394** | Round-6 D7-01 measured the adoption gate admitting UA errors over 10 % because `_slab_confidence` "has no term for the parameter of interest"; its fix (**#1437**, with the class issue #1410) replaced the variance criterion with the fitted UA's **profile-likelihood half-width**. This row drives that gate — `coordinator.py:10454-10456`, the fix's own line — and shows a prior-dominated fit passing it at ≈1e-4 while carrying a +7.44 % bias, so the fix is **narrower than the phenomenon it was measured against**: a half-width is a self-consistency read, not an accuracy read. `carry-1308.json` and `carry-1330.json` are the history: both concern `identify()`, the one-state twin, and its confidence formula, so neither is the fix under test here. The panel should decide whether this is a corroboration of #1394 or a regression of #1437; the row states which instrument it drove, and the bias is +7.4 % in one direction on clean data, which is falsifiable in one run. |
| D8-01 | new | Adjacency: round-4 D6-02 (closed) is the *same sensor* — the Sensor-Gap advisor documented with a currency unit it does not publish — and its fix was the unit, not the wiring. This row is the missing key: the advisor reads two keys `_build_data_dict` never writes, so the value it publishes is the empty-input fallback on every install, and the tests pass because they feed a fake payload. |
| D8-02 | corroborates closed round-6 **#1398** | `carry-1398.json` is the binding artifact and **this round's finder executed its remeasure**: the round-6 fix replaced the static default-off with a dynamic `entity_registry_enabled_default` property on `_DHWEntityMixin`, and the carry says to read "`e.entity_registry_enabled_default` (the dynamic property) instead of the static `_attr_entity_registry_enabled_default`". That is the instrument this row drives, and it finds the one DHW sensor that is **outside the mixin** — so the fix's own mechanism cannot reach it, and the class round-6 closed at five entities has a sixth member by construction. |
| D9-01 | new | Round-1's D9 non-findings measured the recorder at "8.5 KB/cycle (87 % excluded)" and ruled it clean. This row separates the two halves of that number — what the plan sensors already exclude by the project's own rule (15,026 B/cycle) and what four other entities and six accumulating sensors write anyway (3,437 B/cycle) — and prices the second against the first. The leave-one-out (8,415 B/cycle with the largest entity dropped) is what makes it not a single-sensor row. |
| D9-02 | new | The polish is round-5 D0-02's change (recorded as #1208 in the row itself), so this is a **cost measurement of a released change**, not a defect that was closed and returned. The round-6 D9-01 fix (**#1424**, yield the GIL inside each L-BFGS-B objective evaluation) does not move a share, so it is not this row's history. The null control is the load-bearing half: the space-only shape on a different candidate set reads 0.3580 of CPU and 0.3595 of gradients, so the cost belongs to the polish and not to the DHW planner (93.3 ms, 4.3 %). |
| D9-03 | new — residue of the round-2 D9-01 fix | Round-2 D9-01 (closed) found the zero-range bound forcing the scalar-FD path and its stated fix was "treat `lo == hi` as fixed variables in the batched jac". That fix removed the carve-out (`tests/stress.py:1052-1058` still describes it) and moved the NaN case into `_batch_fd_gradient`, so the sweep's cap and pin scenarios now sample the **batched** path on both sides of the change — 316 gradients where the docstring promises 0. The second half is not the docstring: `SolverWork.simulate_steps` charges a batch at `rows × steps`, so the channel the work rule budgets moves +0.019 % under the edit that moves CPU 16.1×, and the brief's own definition of the same quantity disagrees by 96×. The gate is not blind (its `kernel_ms` and evaluation channels both move), which is why this is low. |
| D10-01 | corroborates closed **#829** | The plan of record's row for `#829` reads "strict-typing is unmet under the repository's own ruler" and records it closed `done` by **#876**, whose delivery row states in terms: "`py.typed` was not added. Typing budgets were not raised." The register's `done` and its comment are therefore the residue of a **recorded decision**, and what this row measures is that the decision's stated basis is not in the rule text the register cites. The panel should read #876's row and the fetched rule text together and decide whether the finding is the register's wording or the rule's reading; the executed number (`qs_py_typed_files=0`) is not in dispute. |
| D10-02 | corroborates closed round-4 **#953 / D10-03** | Round-4 D10-03 measured the package root re-binding `HeatPumpOptimizerConfigEntry` to a bare `ConfigEntry`, "so `runtime_data` reveals `Any` in the three entry points"; its fix (**#994**) parametrised the alias **for the checker only** and the delivery row records why: "a parametrised runtime alias puts a forward reference inside the very name `get_type_hints` resolves on HA 2026's setup path (NameError, measured by the finder and re-executed as mutation arm 2)". That fix made the alias correct and left it unused — 10 of 100 parameters. This is the same class measured package-wide instead of at three entry points, and the count (88) is the size of the narrowness rather than of a new defect. |
| D11-01 | new | Adjacency: round-4 D11-06 (closed) found `policy_lint --stats` "reports a class over its own threshold and opens nothing", and `#959` is the owner decision approving the filing lane at all. This is neither: the histogram **does** open its trigger in 40 of 40 runs and the step that acts on it is **skipped** in 39 of 40, by a GitHub Actions step-skip rule rather than by the linter. The null control is the one run that was not skipped. |
| D11-02 | new | Same lane, different mechanism: `decide` reads the key and not the issue's state, so a disposal by closing is written over and cannot be reversed. The evidence that it has happened is a property of the lane's whole history — 14 filed, 0 open — not of the window. |
| D11-03 | new | Adjacency: round-4 D11-06's second clause named `--sunset` as a mode that "runs under `\|\| true` and no contract obliges a seat to read". This measures the other end: the class reports a zero over 39 files in the shape of a measurement and *cannot* name a rule, because no policy file carries any of its three markers. The eight occurrences in the tree are the linter's own fixtures and regexes, which is itself the argument. |
| D12-01 | new — **named in `docs/backlog.md` item 10** | Item 10 opens "config-flow guards. `smart_write` saves with no valve control" and asks for "a `dhw_mode` select mirroring `CONF_TWO_ZONE_MODE`, honoured ahead of `thermal_model.py`'s key-presence inference". This row is the measured instance of the second half: the guard tests the mass key's presence where the model tests the explicit override, and the consequence is 0 valve writes per cycle forever, with only a log line. As with D1-02, the fix is designed and deferred; the row supplies the instrument and the count it was missing. |
| D13-01 | new | Adjacency: closed round-6 **#1405** (fixed by **#1442**) is the *other* direction of the same reader — a class `web-fix-wave.js` defines, `head-moved`, for which the histogram had 0 verdicts. This is an endpoint the reader never asks for. The second half of the round-6 fix is not this: it keyed a moved head as rework, which changes what the histogram counts, not what it can see. The window's magnitude is 0 and the finding says so, which is why the panel should not read it as a live yield error on this window — the defect is that the metric *cannot* see a review-posted verdict, and the prevalence is GitHub-sourced. |
| D13-02 | new | Adjacency: closed round-6 **#1406** (fixed by **#1439**) measured the same `statsHistogram`'s **denominator** — "the histogram prints the population it saw, not the merges the window contains" — and its fix prints the coverage line beside `STATS`. This measures the same function's **grammar** against the module whose grammar its header claims to have read, and shows the two arms of one function disagreeing about the SHA. Different mechanism, different perturbation (the `'i'` flag), not a regression of #1439. |
| D13-03 | new | Adjacency: closed round-6 **#1407** (fixed by **#1433**) is the exclusion list's *keying*; this is a **different mode's** outcome reporting — `--record`'s exit code standing in for its enumeration. The perturbation is one line in the report step's condition, and the fix the finder recommends is deliberately the cheaper one (key the headline on the UNCHECKED marker) because making `--record` exit non-zero reddens the job on a transient outage, which is the documented reason rc=0 stays. |
| D13-04 | new | No prior round measures the dispatch count. Round-6 D13-02 (#1406) was a verdict-population denominator and round-4 D11-06 was a mode's silence; this is the **workflow run** as the unit a body edit multiplies, and the metric that misnames it (`body_rounds`). The keying perturbation is the argument: moving the count from the head to the merge commit collapses 46 to 30 and `{0:1, 1:30}`, because a merge commit is never edited. |
| D13-05 | new | Corroborates nothing closed, but it is the **mirror image of closed #1405** and should be read beside it: there a class existed and nothing emitted it, here a reviewer emits a class that does not exist, and in both the two readers disagree about what the window contains. 1 of 2 blocked verdicts, and 100 % of its engineering blocks, is the size at this window. |
| D13-06 | corroborates closed round-6 **#1407** | Round-6 D13-03 measured that `cfr_exclusions.json` is "keyed where the excluded job cannot gate a merge" and its fix (**#1433**) made the change-failure rate print **at both keyings**. This row drives that fix's own two numbers and finds a **second name** with the same property: `mutation` is 4 of 7 merge-keyed failures and 0 of 31 heads, so the two readings are 0.226 and 0.129 and the 4/31 between them is invisible in either published figure. It is filed as an instrument finding on purpose: whether a merge-surface red on a batch-merged tree is a change failure is the exclusion list owner's judgement, and that judgement needs the pair side by side. |

**Three round-level observations**, recorded rather than filed:

- **The round-7 prep met a defect in the round driver, and it is a round-level
  instrument finding, not a dimension finding.** `.claude/workflows/audit-find.js`
  is the committed workflow that runs a round, and its `DIMS` list (line 21) is
  `['D0', …, 'D12']` — **thirteen** dimensions, with **no `D13`** — even though
  round 6 ran fourteen and this round did too. The omission is not only the
  dispatch: `WAVES` (line 24) has no `D13` entry, so no wave runs it;
  `ISOLATED` (line 26) is `{D0, D3, D9, D11}` and **not** D13, though D13 reads
  GitHub and needs `.git` exactly as D11 does; and the quiet window's
  `provisional` set (line 92) is computed from `DIMS`, so a provisional D13
  number would never be re-taken. The dedup phase is the sharpest edge: its
  prompt reads "the `${DIMS.length}` reports" and joins
  `${DIMS.map(…)report_path}`, so **a round driven by this workflow cannot
  register D13 at all**, and the failure is silent — the missing-dimension log
  at line 88 iterates `DIMS` and therefore cannot name a dimension that is not
  in it. Round 7's prep dispatched D13 by hand and ran it in an isolated worktree
  (`~/audit-r7-D13`), which is why this register has a D13
  section — but the isolated tree was not enough, because the `ISOLATED` set is
  not what grants a seat the API: D13's first pass was dispatched with GitHub
  out of scope and left five of the brief's six required outputs untaken, and
  the outputs only came back when a second pass read the API. A round driven by
  the workflow would have had neither pass. The fix is one list and its two
  companions, and it belongs to the fix wave the way round 6's `audit-find`
  defects did.
- **Nine of fourteen dimensions wrote no finding JSON.** Round 6 had twelve of
  fourteen; round 7 has five (D1, D3, D8, D9, D10, the last recovered from the
  finder's scratch). The consequence is in *Intake validation* above: 19 of 30
  findings were validated from prose, and the systematic absences
  (`stop_rule_class`, `instrumented_symbol`, per-finding `load1`/`tolerance`)
  track which reports carried one. This is recorded rather than filed because
  it is a property of the fan-out's instructions and not of any dimension's
  work; a later round's prep should say in the finder's own task that the JSON
  is the artifact of record, the way `report_schema` in the workflow already
  does for the dimensions the workflow knows about.
- **There is no Round 3 or Round 5 section in this document**, and this round
  does not fill either. Round 5's record is its 48 issues (#1293–#1340), the
  round-5 harness directories under `tools/audit/round5/` and the
  `carry-*.json` files; Round 3's is `tools/audit/round3/ledger/`. Named here
  rather than quietly filled, the way round 4 named the missing Round 3 and
  round 6 named the missing Round 5.

### What this commit does not carry

`tests/closure.py`'s `INERT` prefix covers `tools/audit/`, **but not the
five-part round-harness `.py` corpus**: `closure._is_header_corpus` takes any
`tools/audit/round*/D*/*.py` out of the INERT claim, because
`tests/harness_headers.py`'s discovery opens every one of them, so each is a
recorded read of that script and belongs in its closure in
`tests/closures.json` — and the closure table can only be re-derived on Linux.
Round 4's harnesses are in that closure; round 5 avoided the question by nesting
one level deeper; round 6 hit it and left its 60 `.py` harnesses at their finder
paths. Round 7 has the same flat layout, and **the 44 `.py` files are listed
here rather than committed unclassified**:

- D0 `underheat_seed.py`; D1 `guards.py`, `store_types.py`, `_explore_lifecycle.py`,
  `_explore_cycle.py`; D2 the ten sweeps (`energy_balance_sweep.py`,
  `batch_parity_sweep.py`, `monotonicity_sweep.py`, `cop_sweep.py`,
  `golden_bounds.py`, `objective_identity.py`, `derate_sweep.py`,
  `sysid_quantised_ensemble.py`, `buffer_cap_conservation.py`,
  `dead_statements.py`); D3 `screen.py`, `probe.py`, `structure_kill.py`;
  D5 `comment_symbols.py`, `docs_structure.py`, `card_hours_bounds.py`;
  D6 `claims_check.py`; D7 `sysid_plant.py`; D8 `matrix.py`, `gap_series.py`,
  `dhw_advisor_default.py`; D9 `payload_bytes.py`, `polish_cost.py`,
  `gradient_cost.py`, `cycle_solves.py`; D10 `qs_rules_r7.py`,
  `mypy_strict.py`, `diag_export_control.py`; D11 `friction_lane_never_runs.py`,
  `friction_closed_issue_swallowed.py`, `sunset_marker_census.py`,
  `conformance_sample.py`; D12 `grid.py`, `plant_conditioning.py`,
  `valve_flow_target.py`; D13, where the three `.mjs` instruments
  (`window_api_ledger.mjs`, `verdict_grammar.mjs`, `class_vocabulary.mjs`) are
  committed and the four `.py` ones (`yield_rounds.py`, `cfr_by_job.py`,
  `gov_cost.py` and their shared `d13lib.py`) are not.

They stand at their finder paths in the export
(`~/audit-r7-baseline`) and the five worktrees
(`~/audit-r7-{D0,D3,D9,D11,D13}`). The two routes to land
them are the ones round 6's register states — re-record `tests/closures.json` so
`harness_headers.py`'s closure absorbs the corpus (the round-4 precedent), or
move the corpus one level deeper the way round 5 did and update the `harness_path`
fields with it. **The exclusion is verified rather than asserted**: with the 44
files in place the corpus predicate reports them, and with them out
`closure.orphan_files()` returns **0** — no committed file of this round forces
the FULL suite.

**One budget item is left open deliberately, and it is named so the fix wave
takes it.** `policy_lint.mjs`'s `named-docs` check refuses a document the corpus
names but no cap measures, and `tools/audit/briefs/COMMON.md` names
`tools/audit/round<N>/D<k>/REPORT.md` while `tools/audit/briefs/fixer.md` names
`BASELINE.md`. On this branch that is **15 errors** — the 14 `REPORT.md` files
committed here plus `tools/audit/round7/BASELINE.md` — where `origin/main`
reports `TOTAL: 0 error(s)` over the same 39 policy files. Round 6's own
register commit paid this in the same pull request by adding fifteen
one-by-one `CORPUS_EXCLUDED` lines to `policy_lint.mjs` (`tools/audit/round6/`
`BASELINE.md` and `D0`…`D13/REPORT.md`, lines 546–560). **That change is not
made here**: it is a change to a measured workflow file rather than to a record,
it needs the same owner-facing read a new `POLICY_GLOBS` pattern would, and the
task that produced this commit asked for the item to be recorded rather than
resolved. The recipe is exact and one commit wide — add the fifteen
`tools/audit/round7/…` lines beside their round-6 twins — and the fix wave
should take it before this branch can pass `policy-docs`.

## Round 8 — baseline `cdf82daa`, 2026-09-23

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`, origin/main at dispatch
(the merge of #1489). The panel: fourteen dimensions, **27 finder seats** (one
to three per dimension), one verifier per dimension, and **one common judge**
across all fourteen. The round ran in a cloud Linux container (4 vCPU, no swap),
not on the audit box, so every timing figure in it is provisional and the
judge's decisions rest on counts and ratios unless a row says otherwise;
`tools/audit/round8/BASELINE.md` records the environment.

**43 findings reached the judge: 29 verified, 10 weakened, 3 refuted and 1
merged.** Of the 39 that survive, D0-s1-01 duplicates the owner's refusal #1293
and is not filed, so **38 are filed**, as #1512-#1549, authored by `tvofi`, each
labelled `round-8`. Final severities of the 38: **0 critical, 5 high, 12 medium,
21 low**; 23 are stop-rule class `bug` and 15 `hygiene`; 22 touch production
code and 16 do not. An earlier copy of D2-s2-01 filed as `claude[bot]` (#1511)
was closed as not planned, pointing at its re-file #1512.

Evidence is `tools/audit/round8/`: each dimension's finder `REPORT-s<n>.md`
where the seat wrote one, every seat's `report-s<n>.json`, every verifier's
`verify-v1.md`, the recorded logs and outputs, the `.mjs` and `.sh` instruments,
and the judge's `JUDGE.md`, `JUDGE.json` and `JUDGE-INPUT.json`. **The 131
harness `.py` files are not in this commit**, for the reason rounds 6 and 7
give; where they are and how to restore them is under *What this commit does not
carry* below.

### Findings register — round 8

One row per filed issue, ordered as filed (severity, then dimension). The title
is the issue's, less its `[R8-<id>]` prefix; each issue body carries its
evidence command, the judge's final severity and class, the proposed fix scope
with a seam rule, and its dedup citations.

| id | issue | dim | severity | class | production | title |
|---|---|---|---|---|---|---|
| D2-s2-01 | #1512 | D2 | high | bug | yes | PeakTracker averages the top-k metering windows, not the top-k days the capacity tariff bills |
| D2-s2-02 | #1513 | D2 | high | bug | yes | Entity price sources are read unit-blind: öre/kWh and SEK/MWh prices reach the plan at 83x and 829x |
| D11-s1-01 | #1514 | D11 | high | bug | no | A PR body edit re-creates policy-docs, env-matrix and wave-script as skipped check runs at the unchanged head |
| D11-s2-01 | #1515 | D11 | high | bug | no | Required checks run PR-editable code no CODEOWNERS pattern owns; a one-line edit turns pr-contract green |
| D11-s2-02 | #1516 | D11 | high | bug | no | release.yml publishes and attests a v* tag or dispatch ref at a commit that is not on main |
| D1-s1-01 | #1517 | D1 | medium | bug | yes | set_thermal_parameters DHW minimums written during a solve are reverted by the away-setback unwind |
| D1-s2-01 | #1518 | D1 | medium | bug | yes | A non-numeric kwh/sek leaf in the persisted ledger passes MonthlyLedger.from_dict and fails every refresh cycle |
| D1-s3-01 | #1519 | D1 | medium | bug | yes | A wrong-shaped Open-Meteo hourly/minutely_15 member raises out of OpenMeteoSolar.async_refresh and fails the whole cycle |
| D2-s1-01 | #1520 | D2 | medium | bug | yes | The DHW planner prices COP at the current humidity, not the forecast; published DHW runs up to 4.4 K below the correct plan |
| D3-s1-01 | #1521 | D3 | medium | bug | no | mutation_table scores env_drift's INHERITED CLAIMS refusal as a kill: 17 of 17 production mutants, a comment-only edit included |
| D4-01 | #1522 | D4 | medium | bug | yes | Keyboard Tab order in the expanded what-if dialog jumps backward up the screen at all three required viewports |
| D7-s1-01 | #1523 | D7 | medium | bug | yes | The active sysid experiment ignores the learning freeze and records external heat, defrost, open-window and stale-indoor nights |
| D7-s1-02 | #1524 | D7 | medium | bug | yes | The one-room sysid model cannot identify a two-zone house: 0 of 3 two-zone presets adopt and experiments overshoot the 0.8 K comfort allowance |
| D7-s1-03 | #1525 | D7 | medium | bug | yes | The sysid adoption gate refuses without a reason: a refused fit stays published as completed, reason ok, with its UA |
| D12-s1-01 | #1526 | D12 | medium | bug | yes | An input_boolean or climate heat-pump switch accepted by assign_entity is never actuated: _apply_action always calls switch.turn_on/turn_off |
| D12-s1-02 | #1527 | D12 | medium | bug | yes | On an install with no hot water, the always-created Hot water boost switch injects 4 kW of DHW into the live action and turns the pump on |
| D13-s1-02 | #1528 | D13 | medium | bug | no | Owner-approved merges skip the fix-review verdict: 8 of 22 carry none, against 0 of 66 app-approved |
| D1-s1-02 | #1529 | D1 | low | bug | yes | diagnose_interval service runs coordinator.diagnose_last_interval on the executor against live state |
| D2-s1-02 | #1530 | D2 | low | bug | yes | With cop_flow_carnot on, the DHW tank is priced up to 45 % more efficient than a buffer at the same water temperature |
| D3-s1-02 | #1531 | D3 | low | bug | no | env_drift's cache key hashes HPO_* variables no capture reads, so every locked or HPO_PLANDATA-setting run re-captures |
| D3-s2-01 | #1532 | D3 | low | hygiene | no | No test drives LegionellaGuard.hours_since with a future timestamp; removing its negative-elapsed clamp survives the whole closure |
| D3-s2-02 | #1533 | D3 | low | hygiene | no | The dhw minimum == ceiling deadband boundary is untested at both service call sites |
| D4-s2-01 | #1534 | D4 | low | hygiene | yes | The ecl110_mqtt_qos options-flow label is untranslated in sv.json |
| D5-s1-01 | #1535 | D5 | low | hygiene | no | README Quick-start diagram numbers screens 3-6 while the prose numbers the same screens 4-7 |
| D5-s2-01 | #1536 | D5 | low | hygiene | yes | Two production comments name MIN_POWER and min_power, bare forms with zero code occurrences |
| D6-s1-01 | #1537 | D6 | low | hygiene | no | README Requirements names numpy and scipy but not threadpoolctl, the manifest's third requirement |
| D7-s2-01 | #1538 | D7 | low | hygiene | yes | structure.py's name-based dead-code screen reports 0 while 12 top-level production symbols are unreachable |
| D7-s2-02 | #1539 | D7 | low | hygiene | no | A pure method rename lowers the zero-headroom cross_seam_edges ratchet for 27 of 227 coordinator methods, by up to 7 |
| D7-s2-03 | #1540 | D7 | low | hygiene | no | Disabling the dhw_coil branch of topology.layout_edges drops the wood_tank->dhw_tank edge and no test notices |
| D8-s1-01 | #1541 | D8 | low | bug | yes | Only the sensor platform scrubs non-finite floats; climate, switch, binary_sensor and datetime publish raw NaN/Inf in-process |
| D8-s2-02 | #1542 | D8 | low | bug | yes | The tank temperature sensor stays disabled by default on installs that configure a tank thermometer, hiding the card's live probe point |
| D9-s1-01 | #1543 | D9 | low | hygiene | yes | The per-candidate L-BFGS-B polish spends 6.3 % of the sweep's gradient evaluations on results it discards, 2.6 % in polishes that end ABNORMAL at iteration 0 |
| D9-s2-01 | #1544 | D9 | low | hygiene | no | No CPU- or memory-budgeted gate script covers coordinator.py, sensor.py, process_worker.py, price_model.py or narrative.py |
| D10-s1-01 | #1545 | D10 | low | hygiene | yes | quality_scale.yaml states qs_entry_param_bare=0; 3 to 4 annotations use the bare ConfigEntry |
| D10-s1-02 | #1546 | D10 | low | hygiene | yes | 4 of 25 exception raise sites omit translation_domain/translation_key although quality_scale.yaml claims all carry them |
| D11-s1-03 | #1547 | D11 | low | bug | no | stop-selfcheck.sh ends a turn on a red policy corpus when the policy change is only staged |
| D11-s2-03 | #1548 | D11 | low | hygiene | no | 12 CI install commands in tests.yml are version-pinned but not hash-pinned |
| D13-s1-01 | #1549 | D13 | low | hygiene | no | statsHistogram reports first-verdict yield 0.963 while one-round yield is 0.8125; its head-moved row lumps 15 re-verifications with 3 repairs |

Per dimension, filed: D1 4, D2 4, D3 4, D4 2, D5 2, D6 1, D7 6, D8 2, D9 2, D10
2, D11 5, D12 2, D13 2. D0 files none (its one surviving finding is the #1293
duplicate).

### Judge verdicts — round 8

The judge's full table, with the finder's severity, the verifier's vote and the
judge's re-measured value and note for every one of the 43, is
`tools/audit/round8/JUDGE.md` (machine-readable: `JUDGE.json`). The five that
were not filed:

| id | verdict | disposition |
|---|---|---|
| D0-s1-01 | verified | duplicate of #1293 (owner refusal, also #920/#826) |
| D8-s2-01 | refuted | The metric reads the entity list literal in `async_setup_entry`, a code-reading measure with no runtime path to a user; sorting the real entity_id strings gives 0 splits. |
| D9-s1-02 | refuted | Re-taken on an idle box, the finder's 65-90 % share reproduces as 0.36-0.45, and removing the yield raises it to 0.70-0.89, so the yield is what bounds the GIL hold. |
| D10-s2-01 | refuted | The 515 comes from running mypy --strict against the untyped test double, which `tests/typing_ruler.py` refuses; the pinned census is errors=0 and the finder's perturbation does not move. |
| D11-s1-02 | merged | merged into D11-s2-01 |

The three refutation reasons are condensed from the judge's `note` for the same
id in `JUDGE.json`, which carries the full re-measurement.

### Instrument notes (judge)

1. orjson is not installed in the audit environment and is missing from
   BASELINE.md's pins. As a result, tools/audit/round8/D8/s1_finite_boundary.py
   silently falls back to a stub that counts every non-finite float as a
   serialisation failure, while real orjson 3.12.0 writes NaN/Inf as null. The
   judge installed orjson into a private --target dir
   (/home/claude/audit-r8/tmp/judge/pyorjson) to re-measure, and D8-s1-01 was
   weakened on that result.
2. Seat temp roots are hard-coded in D3/s1_claimkill.py, D3/v1_suite_mutants.py,
   D9/s2_gate_blind.py, D9/s2_cycle.py, the D9/s1_cycle.py and D9/v1_gil.py
   headers, and D3/s1_cachekey.py's HPO_PLANDATA arm. The judge ran
   sed-rewritten copies under /home/claude/audit-r8/tmp/judge/. The harness
   contract should require roots derived from TMPDIR.
3. Several perturbations edit production files on disk: D0 s1_budget_perturb.sh,
   the D3 claimkill/suite-mutant/s2 harnesses and the D4 CSS edit. A concurrent
   run in the same tree then imports the edited file. The judge's first D2-s1-01
   run overlapped the judge's own D0 ftol edit; that run was discarded and a
   clean re-run gave identical numbers. The contract should prefer in-memory
   perturbation or require the gate lock for on-disk edits.
4. Some finder perturbations are inert or tautological. D10-s2-01's is inert (it
   adds an unused import: 515 -> 515, so the harness is void). D11-s1-02's and
   D9-s2-01's --make-perturbed edit the table the metric reads. D0-s1-01's turns
   production into the comparison arm. D2-s2-02's perturbation is an input
   attribute; the judge added tools/audit/round8/D2/judge_price_unit_fix.py.
   D8-s2-02's harness is a static read whose stated direction contradicts its
   own edit; the judge wrote tools/audit/round8/D8/judge_probe_default.py. Three
   observed values are stale: D7-s1-02 (2, not 1), the D7-s2-01 sentinel (14,
   not 12) and D1-s3-01 (the finder's guard gives 1, not 0).
5. Harness output breaks the contract in three places.
   D1/s3_openmeteo_hostile.py prints no load1, thread_factor or swapins.
   D1/s2_ledger_fuzz.py prints a hard-coded thread_factor. D9/s1_cycle.py does
   not subtract the deliberate executor thread's CPU, so its thread_factor reads
   1.09-1.19 on the idle box.
6. The D8-s2 harnesses read source text instead of hooking a production symbol.
   D5/s1_stepnum.py's node regex truncates labels at <br/>, so it counts 3
   mismatches where there are 4.
7. The D10-s2 finder ran mypy --strict with tests/hastub on the path, which is
   the exact setup tests/typing_ruler.py refuses. The baseline's pinned typing
   job (job 107333392110) passed against a recorded census of 0.
8. Live GitHub data moved between the panel and the judge: open PR #1508
   appeared, and v1_latest_order.py's null went from 0 to 1. Unauthenticated
   api.github.com works for check-runs and rulesets, but /rate_limit returns 403
   in agent sessions.
9. pip download writes into the cwd, so the judge's orjson probe left a wheel in
   the tree root. It was removed at once and git status is clean.
10. Finding ids use two shapes (D4-01 vs D4-s2-01) and were not validated
   against finding.schema.json. The judge could write .md files. Every
   production file is byte-identical to the baseline: git status shows only the
   deletions made by the round preparation, plus the untracked
   tools/audit/round8/.

The hand-off also named two round-preparation defects:
`tools/audit/prepare_baseline.sh` stripped round-4 files that
`tests/entities.py` opens unguarded, so its own `finders_can_start` check
refused its output, and seat-scoped ids such as D1-s1-01 failed
`tools/audit/finding.schema.json`. **Both were fixed by #1507 (`21987ff4`,
round-8 F1) before this commit's merge base**, so neither is open: at this
commit the schema's id pattern accepts D1-s1-01, and `prepare_baseline.sh` keeps
what the gate reads.

### What this commit does not carry

`tests/closure.py` keeps `tools/audit/` INERT except the five-part round-harness
corpus: `closure._is_header_corpus` takes every `tools/audit/round*/D*/*.py` out
of the INERT claim because `tests/harness_headers.py`'s discovery opens each
one, and the closure table that would absorb them can only be re-derived on
Linux. Round 8's layout is flat like rounds 6 and 7, so its **131 `.py`
harnesses are listed here rather than committed unclassified**:

- D0 (9): `s1_budget.py`, `s1_race.py`, `s1_warm.py`, `s2_decomp.py`,
  `s2_rolling.py`, `s2_terminal.py`, `s2_termrace.py`, `v1_descent.py`,
  `v1_mpc.py`
- D1 (14): `s1_alias.py`, `s1_lifecycle.py`, `s1_realloop.py`,
  `s1_setback_race.py`, `s1_thread_reads.py`, `s2_ledger_fuzz.py`,
  `s3_openmeteo_hostile.py`, `s3_weather_poison.py`, `v1_diag_offloop.py`,
  `v1_ledger_cycles.py`, `v1_openmeteo_cycle.py`, `v1_s2_perturb_runner.py`,
  `v1_s3_perturb_runner.py`, `v1_setback_race.py`
- D2 (12): `judge_price_unit_fix.py`, `s1_cop_laws.py`, `s1_dhw_humidity.py`,
  `s1_identities.py`, `s2_cost_identity.py`, `s2_distinct_day_peaks.py`,
  `s2_fee_dst.py`, `s2_price_unit.py`, `v1_cop_laws.py`, `v1_dhw_humidity.py`,
  `v1_peak_days.py`, `v1_price_unit.py`
- D3 (12): `s1_cachekey.py`, `s1_claimkill.py`, `s1_envdrift.py`,
  `s1_prescreen.py`, `s2_finding01_hours_since.py`,
  `s2_finding02_deadband_boundary.py`, `s2_mutate.py`, `v1_cachekey.py`,
  `v1_claimgate.py`, `v1_deadband.py`, `v1_legionella_due.py`,
  `v1_suite_mutants.py`
- D4 (3): `s2_label_coverage.py`, `s2_translation_gap.py`,
  `v1_locale_residual.py`
- D5 (8): `s1_dupcheck.py`, `s1_linkcheck.py`, `s1_stepnum.py`,
  `s2_backtick_check.py`, `s2_comment_idents.py`, `v1_comment_idents_pyscan.py`,
  `v1_stepnum_overlap.py`, `v1_stepnum_position.py`
- D6 (6): `s1_disabled_default.py`, `s1_entity_counts.py`,
  `s1_requirements_claim.py`, `s1_service_examples.py`, `s2_claims_check.py`,
  `v1_requirements_gap.py`
- D7 (16): `s1_gate_silent.py`, `s1_learner_freeze.py`, `s1_statefulness.py`,
  `s1_sysid.py`, `s1_sysid_contam.py`, `s1_sysid_twozone.py`, `s2_reach.py`,
  `s2_rename.py`, `s2_sentinel.py`, `s2_spot.py`, `v1_coil_edge.py`,
  `v1_dead.py`, `v1_gate_silent.py`, `v1_seam_rename.py`, `v1_sysid_freeze.py`,
  `v1_sysid_twozone.py`
- D8 (9): `judge_probe_default.py`, `s1_finite_boundary.py`, `s1_matrix.py`,
  `s2_enabled_analysis.py`, `s2_entity_analysis.py`,
  `s2_entity_analysis_perturbation.py`, `s2_ordering_finding.py`,
  `v1_finite_boundary_binary.py`, `v1_ordering_refute.py`
- D9 (9): `s1_cycle.py`, `s1_gradient.py`, `s1_polish.py`, `s1_solves.py`,
  `s2_cycle.py`, `s2_gate_blind.py`, `s2_stress_2x.py`, `v1_gil.py`,
  `v1_polish_kernel.py`
- D10 (8): `s1_entry_param_bare.py`, `s1_exception_translations.py`,
  `s2_coverage.py`, `s2_strict_typing.py`, `s2_strict_typing_perturb.py`,
  `v1_entry_param_bare_regex.py`, `v1_exception_translation_regex.py`,
  `v1_mypy_breakdown.py`
- D11 (13): `s1_owner_surface.py`, `s1_red_census.py`, `s1_skip_supersede.py`,
  `s1_stop_hook_states.py`, `s2_conformance.py`, `s2_owner_closure.py`,
  `s2_release_gate.py`, `s2_scorecard.py`, `v1_latest_order.py`,
  `v1_owner_flip.py`, `v1_pins.py`, `v1_release_controls.py`, `v1_stop_index.py`
- D12 (6): `s1_actuation.py`, `s1_hpaxis.py`, `s1_matrix.py`,
  `s1_phantom_boost.py`, `v1_boost_effects.py`, `v1_switch_follow.py`
- D13 (6): `s1_dora.py`, `s1_gh.py`, `s1_window.py`, `v1_coverage.py`,
  `v1_gh.py`, `v1_rework.py`

They stand at their finder paths under `handoff/round8/evidence/` at commit
`6f58e33e` on the transport branch `claude/project-thread-s8rmov`, which is not
for merge and must stay until the round-8 fix wave closes. A fixer restores the
whole round, with every issue body's `tools/audit/round8/D<k>/…` path resolving,
by running `git fetch origin claude/project-thread-s8rmov` and then `git archive
6f58e33e handoff/round8/evidence | tar -x --strip-components=3 -C
tools/audit/round8` from the repository root.

The exclusion is checked, not asserted: with the evidence of this commit staged,
`closure.orphan_files()` returns `[]`, so no committed round-8 file forces the
FULL suite.

`named-docs` names two round-8 files, `BASELINE.md` (by
`tools/audit/briefs/fixer.md`) and `JUDGE.md` (by
`.claude/rules/finding-propagation.md`). Both are added to
`.claude/workflows/corpus_excluded.json` beside the round-6 and round-7 entries.
With them `node .claude/workflows/policy_lint.mjs` reports `TOTAL: 0 error(s)`,
and without them it reports 2. The finder reports are named `REPORT-s<n>.md`,
which no policy file names, so they need no entry.

## Round 9 — intake, baseline `1936d5ca`, 2026-09-26

Intake for round 9, batch 1, done by hand from `.claude/workflows/audit-find.js`'s intake step. Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. This section is the **intake register**: findings as reported by their finder and lead seats, validated against `tools/audit/finding.schema.json` and registered one row per finding. It does **not** merge, cluster, dedupe or verify — that is the judge's first step, which follows. `status` is `reported` for every row here; nothing has been judged yet.

Inputs: 122 finder findings from 40 seats (`accepted.json`), 25 findings the leads seats converted (`lead_findings.json`, `from_lead: true`), and D3-s2's catch-up batch of 2 findings from `origin/handoff/audit-r9-find-B2:tools/audit/round9/reports-B2.json` (box B2). `rejected.json` and `lead_rejected.json` were both empty at hand-off; the rejections below are this intake's own schema check.

### Dimension status — round 9 intake

| # | Dimension | Seats reported | Findings accepted | Rejected at intake |
|---|-----------|-----------------|--------------------|----------------------|
| 0 | Price optimality | 3 | 3 | 0 |
| 1 | Robustness and stability | 5 | 29 | 3 |
| 2 | Mathematical and physical sanity | 4 | 10 | 2 |
| 3 | Test-suite gaps | 2 (D3-s2 catch-up); D3-s3 deferred (catch-up) | 3 | 0 |
| 4 | UI/UX | 2 | 15 | 0 |
| 5 | Docs structure, flow and content; code comments | 2 | 8 | 2 |
| 6 | README and documentation claim verification | 2 | 10 | 0 |
| 7 | Architecture and maintainability | 3 | 5 | 4 |
| 8 | Sensor verification and ordering | 3 | 7 | 3 |
| 9 | CPU and memory efficiency, Raspberry-Pi-class target | 2 | 7 | 2 |
| 10 | Home Assistant integration quality scale | 2 | 4 | 0 |
| 11 | Governance mechanisms and policy | 2 | 10 | 0 |
| 12 | Generalization | 3 | 3 | 4 |
| 13 | Process yield and cost | 1 | 3 | 0 |
| 14 | Recurring bug classes | 5 | 12 | 0 |
| | **Total** | **41** | **129** | **20** |

Seats reported counts distinct finder seats in `reports.json` plus D3-s2 (reported on `origin/handoff/audit-r9-find-B2`, not in `reports.json`). D3-s3 has not reported and is listed separately; it is not counted in D3's seats-reported figure. Findings accepted and rejected at intake include both finder findings and the leads seats' converted findings, keyed by each finding's `scope`.

### Rejected at intake

20 findings failed validation against `tools/audit/finding.schema.json` (`#/definitions/finding`) and are rejected at intake, with the validator's message:

| id | seat | source | validator message |
|---|---|---|---|
| D2-s3-01 | D2-s3 | accepted | metric_definition: 'Per profile, the count of the 96 quarters (clock frozen 7 minutes into each) where _current_spot_price() differs from the price of the entry whose [start, start+15 min) contains now; keyed on the value the seam returns.' is too long; perturbation/expected_direction: "The quarter-entry arms fall to 0 mismatches and the hourly-entries null control rises from 0 to 273. The span is the mechanism; an honest fix takes each entry's end from the next entry's start, as _known_prices_for does, and must read 0 on all three arms." is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D2-s3-02 | D2-s3 | accepted | metric_definition: "Per (price profile, export price) cell, the count of the 96 steps where the production cost closure's price of a 3 kW single-step draw differs by more than 1e-9 from export·min(P,s)+import·max(P−s,0)·dt with a clear-sky 6 kWp surplus; keyed on the closure's returned value." is too long; perturbation/expected_direction: "Breach steps fall to 0 in every cell, the solve's predicted_cost − identity goes from −0.609 to 0.000, and surplus kWh in negative-price steps goes from 5.07 to 2.27." is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D5-s1-03 | D5-s1 | accepted | title: 'dashboard-card.md upgrade troubleshooting says the card version lags the integration; the stamp makes them equal on every release' is too long |
| D5-s1-04 | D5-s1 | accepted | title: 'configuration.md has 9 lines that a GFM renderer puts in the wrong block: 3 table rows as raw-pipe text, 6 prose lines as table rows' is too long |
| D7-s1-01 | D7-s1 | accepted | title: 'Structural ratchet does not price coordinator state reached via module-level _helper(self, ...), rewarding the refused move' is too long |
| D7-s2-01 | D7-s2 | accepted | title: 'sysid two-state fit rolls the candidate with one Euler step per 30-min sample: UA 17-25% low on an exact continuous plant, 0/3 presets adopt' is too long |
| D7-s2-02 | D7-s2 | accepted | title: 'Defrost derate fallback folds meter ratios that _cop_fold_blocked refuses to the COP learner (immersion, backup heater, capacity cap)' is too long |
| D7-s3-02 | D7-s3 | accepted | title: 'structure.py dead_methods reads 0 while 9 members are dead: properties are skipped and bare-name loads count as references' is too long |
| D8-s2-01 | D8-s2 | accepted | perturbation/expected_direction: 'climate_unavailable_with_payload 5 -> 0 and climate_attrs_hidden 112 -> 0 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip']; title: 'Climate entity is permanently unavailable on an install without an indoor thermometer, taking the thermostat control with it' is too long |
| D8-s2-02 | D8-s2 | accepted | perturbation/expected_direction: 'hvac_action_vs_plan 14 -> 0 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D8-s2-03 | D8-s2 | accepted | metric_definition: 'Number of immediate state writes made by climate.async_set_hvac_mode or OptimizerEnableSwitch.async_turn_off in which the live-mode field (hvac_mode or is_on) disagrees with a payload-mode field in the same write (hvac_action OFF-ness or the switch attribute mode).' is too long; perturbation/expected_direction: 'mode_split_after_action 2 -> 0 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D9-s2-01 | D9-s2 | accepted | title: 'sensor_advisor ranking re-simulated on the event loop at every plan-sensor state write: 1152 simulate steps, ~32% of loop CPU per cycle' is too long |
| D9-s2-02 | D9-s2 | accepted | title: "No budgeted check can see a 2x of the coordinator's loop-thread work; nightly replay needs ~x5, stress.py reaches none of it" is too long |
| D12-s2-01 | D12-s2 | accepted | evidence/cpu_or_wall: 'neither (counts and ratios)' is not one of ['cpu', 'wall', 'count', 'bytes', 'ratio', 'n/a']; evidence/load1: '1.38' is not of type 'number'; evidence/thread_factor: '1.000' is not of type 'number'; metric_definition: "withheld_frac = planned space+DHW kWh in steps whose production heat_pump_on_schedule is False, divided by the plan's total planned kWh; a cell fails above 0.10; e2e counts switch.turn_off calls from _apply_action on steps with planned power > 0.1 kW" is too long; perturbation/expected_direction: 'down: onoff_failing_cells 4 -> 0, e2e turn_off-with-planned-heat 30 -> 0 (both measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D12-s2-02 | D12-s2 | accepted | evidence/cpu_or_wall: 'neither (counts)' is not one of ['cpu', 'wall', 'count', 'bytes', 'ratio', 'n/a']; evidence/load1: '1.14' is not of type 'number'; evidence/thread_factor: '1.000' is not of type 'number'; metric_definition: "misrouted_mode_writes = mode-slot service calls from pump_arbiter.apply whose service domain differs from the target entity's domain, over 9 ticks 7 min apart on a space/space/DHW/space plan, with HA entity-service routing modelled explicitly (select.select_option acts only on select.*, input_select.select_option only on input_select.*, and there is no sensor.select_option)" is too long; perturbation/expected_direction: 'down: input_select misrouted 5 -> 0, ticks_mode_wrong 9 -> 0, repair 1 -> 0 (measured). The sensor cell keeps 9 wrong ticks, which is the read-only half of the property.' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D12-s2-03 | D12-s2 | accepted | evidence/cpu_or_wall: 'neither (counts)' is not one of ['cpu', 'wall', 'count', 'bytes', 'ratio', 'n/a']; evidence/load1: '1.30' is not of type 'number'; evidence/thread_factor: '1.000' is not of type 'number'; perturbation/expected_direction: 'down: onoff_full_power_mislabelled 149 -> 0 and power_normalized minimum -60 -> -5 (measured)' is not one of ['up', 'down', 'to_zero', 'sign_flip'] |
| D12-s3-01 | D12-s3 | accepted | metric_definition: "Initial-flow completion paths (DFS over menus, forms untouched, quick-setup plant answers 'no') whose entry's first _async_update_data publishes dhw_enabled with a dhw_plan tank trajectory, or two_zone_enabled, with no affirming answer." is too long |
| D1-s2-54 | D1-s2 | lead_findings | title: 'apply_manual_plan accepts expires_at past the horizon: the override owns all 96 steps, the invariant it states is unenforced' is too long |
| D1-s5-51 | D1-s5 | lead_findings | title: 'A report-on-change indoor thermometer silent over 60 min turns Indoor Temperature unavailable while HA holds its valid reading' is too long |
| D1-s5-52 | D1-s5 | lead_findings | title: 'InputReader has no plausibility window: -127 and 85 degC sensor sentinels are delivered as ok on 6 of 6 temperature inputs' is too long |

### Findings register — round 9 (intake, unjudged)

One table per dimension. Columns: id, scope, step, severity, class_guess, title, status, provisional. `status` is `reported` for every row: this is the intake register, before clustering, dedup or judge verification. No finding is provisional under the driver's rule, except D9-s1-71 and D9-s2-71 (both lead findings), marked provisional because their CPU ratios were taken on a shared box.

#### D0 — Price optimality

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D0-s1-01 | D0-s1 | D0.M2 | low | P4 | The two-zone 0.20x deep anchor is built only in _optimize_space_only; the DHW path's _solve_space never gets it | reported |  |
| D0-s2-01 | D0-s2 | D0.M2 | low | P4 | L-BFGS-B ftol=1e-6 stops the solve and its in-loop restart short of their own fixed point | reported |  |
| D0-s2-02 | D0-s2 | D0.M2 | low | P4 | Multi-start seed set misses lower basins on shoulder prices, above the flat-price null | reported |  |

#### D1 — Robustness and stability

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D1-s1-01 | D1-s1 | D1.M2 | medium | P1 | A tz-naive persisted timestamp raises on every cycle at three sibling loader seams (snapshots, curve, comfort) | reported |  |
| D1-s1-02 | D1-s1 | D1.M2 | medium | P1 | A non-numeric snapshot temperature_bias makes best_restore raise and suppresses the accuracy_drift issue for good | reported |  |
| D1-s1-03 | D1-s1 | D1.M6 | medium | new | One out-of-range DHW thermometer sample is booked as a physically impossible draw and inflates the published p90 | reported |  |
| D1-s1-04 | D1-s1 | D1.M3 | low | new | A timestamp stored while the clock ran ahead is trusted verbatim and stretches stale timeouts by the clock error | reported |  |
| D1-s1-51 | D1-s1 | D1.M2 | low | P11 | hastub Store decodes with stdlib json: 6 of 6 hostile number tokens load where HA's orjson Store drops the file *[from lead (L1)]* | reported |  |
| D1-s1-52 | D1-s1 | D1.M3 | low | P11 | hastub dt_util.now() is naive by default: the naive-vs-aware verdict of 6 of 6 stored-timestamp cells is inverted *[from lead (L1)]* | reported |  |
| D1-s2-01 | D1-s2 | D1.M6 | high | new | A malformed weather-forecast response wedges every later cycle until restart | reported |  |
| D1-s2-02 | D1-s2 | D1.M6 | medium | new | Finite-but-absurd weather forecast values reach the solve unbounded: failed plans and a runaway solve | reported |  |
| D1-s2-03 | D1-s2 | D1.M2 | medium | P1 | A sample count past 2**64 in the thermal-learning store fails every cycle, across restarts | reported |  |
| D1-s2-04 | D1-s2 | D1.M5 | medium | new | Five cycle-path guards swallow a persistent failure at DEBUG, including pump and frequency actuation | reported |  |
| D1-s2-05 | D1-s2 | D1.M1 | medium | new | Home Assistant stop waits out an in-flight solve before reaping the solve worker | reported |  |
| D1-s2-51 | D1-s2 | D1.M5 | medium | new | A learner or arbiter raise on the cycle path fails the solve or the whole cycle and skips actuation and saves *[from lead (L1)]* | reported |  |
| D1-s2-52 | D1-s2 | D1.M1 | medium | new | Five store writers do not wait for the startup read: a save in that window replaces persisted learned state *[from lead (L1)]* | reported |  |
| D1-s2-53 | D1-s2 | D1.M1 | medium | new | set_thermal_parameters changes are silently lost at the next restart (24 of 26 fields) *[from lead (L1)]* | reported |  |
| D1-s2-55 | D1-s2 | D1.M5 | medium | new | A solve worker that cannot start (Popen OSError) skips the in-process fallback: no plan, no fallback notice *[from lead (L1)]* | reported |  |
| D1-s2-71 | D1-s2 | D1.M1 | low | P11 | hastub DataUpdateCoordinator drops update_interval: the coordinator's cadence is unreadable in 4 of 4 cells *[from lead (L3)]* | reported |  |
| D1-s3-01 | D1-s3 | D1.M6 | high | P2 | A tz-less return_time (card datetime-local) or a naive stored datetime wedges every cycle with TypeError | reported |  |
| D1-s3-02 | D1-s3 | D1.M1 | high | new | Pump-duty arbiter re-registers its timer and state listener on an unloaded coordinator and keeps writing the pump | reported |  |
| D1-s3-03 | D1-s3 | D1.M2 | medium | P1 | pump_arbiter._load installs non-numeric set-point values that raise TypeError on every apply | reported |  |
| D1-s3-04 | D1-s3 | D1.M4 | medium | new | Climate entity publishes the away setback as the user's target while the solve is in the executor | reported |  |
| D1-s3-05 | D1-s3 | D1.M3 | medium | new | Boost 'two-hour maximum' is an absolute instant: a clock step back or a far-future store extends it without bound | reported |  |
| D1-s3-06 | D1-s3 | D1.M2 | medium | P1 | FrequencyMap.from_dict admits an unbounded ratio or out-of-range decile that pins recommend() at hz_min for days | reported |  |
| D1-s4-01 | D1-s4 | D1.M2 | medium | P1 | DefrostDerate.from_dict admits non-finite/out-of-range duty; the bucket pins at DERATE_MIN and never recovers | reported |  |
| D1-s4-02 | D1-s4 | D1.M5 | medium | P2 | A failed solve is returned as a plan with status 'failed (...)', so the coordinator counts it a success | reported |  |
| D1-s4-03 | D1-s4 | D1.M2 | low | P1 | One unreadable cell in a v2 defrost store voids all 12 measured buckets and is labelled a pre-v5.3.0 upgrade | reported |  |
| D1-s5-01 | D1-s5 | D1.M3 | medium | P2 | inputs.age_of ignores last_reported and accepts future stamps, diverging from InputReader's freshness rule | reported |  |
| D1-s5-02 | D1-s5 | D1.M2 | medium | P1 | Learner-store loaders check finiteness but not the domain their own update path enforces (price shape, peak tracker) | reported |  |
| D1-s5-03 | D1-s5 | D1.M6 | low | P2 | One huge JSON integer drops a whole price fetch (entity and Tibber) or Open-Meteo refresh instead of one row | reported |  |
| D1-s5-04 | D1-s5 | D1.M6 | low | new | One off-grid timestamp collapses Open-Meteo's inferred resolution and erases the whole solar horizon | reported |  |

#### D2 — Mathematical and physical sanity

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D2-s1-01 | D2-s1 | D2.M1 | medium | new | Euler sub-step guard judges each store's diagonal ratio only, so coupled stores in accepted configs diverge | reported |  |
| D2-s1-02 | D2-s1 | D2.M1 | low | new | DHW refill coil debits the wood tank the full coil heat but spares the DHW tank only its scaled share | reported |  |
| D2-s1-51 | D2-s1 | D2.M2 | low | P6 | DHW setpoint advisor prices candidates at the 5.0 degC ThermalState default when no outdoor thermometer is mapped *[from lead (L1)]* | reported |  |
| D2-s2-01 | D2-s2 | D2.M3 | high | P2 | Settlement caps (slab_settlement_cap, hold_demand_kw) ignore the learned house_heat_loss_scale the dynamics apply | reported |  |
| D2-s2-02 | D2-s2 | D2.M2 | medium | new | #1067 flow-lift bias clamp (15 K) cannot reach real supply: model curve tops out at 27.9 C, COP overstated up to 37% | reported |  |
| D2-s2-03 | D2-s2 | D2.M3 | low | P2 | DHW-path savings settle-up replays space schedule without the DHW coil: end state differs from published trajectory | reported |  |
| D2-s2-81 | D2-s2 | D2.M3 | medium | P3 | Two-zone comfort penalty halves each zone's floor price; shipped plans sit up to 0.46 K below min_temp *[from lead (L4)]* | reported |  |
| D2-s4-01 | D2-s4 | D2.M5 | medium | P5 | sysid adoption interval misses the true UA on 14 of 22 fits it admits; admitted fits biased high | reported |  |
| D2-s4-02 | D2-s4 | D2.M5 | medium | new | sysid step sized to exactly the abort bound: sensor noise aborts 100 of 294 experiments, light_new 81 of 96 | reported |  |
| D2-s4-81 | D2-s4 | D2.M5 | medium | P5 | sysid cannot adopt its own exact noise-free fit on 43 of 80 preset houses, yet arms on all 80 *[from lead (L4)]* | reported |  |

#### D3 — Test-suite gaps

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D3-s1-01 | D3-s1 | D3.M2 | low | I1 | No closure script fails when _dhw_inlet_c's lower plausibility bound moves (-5.0 <= value -> -5.0 < value) | reported |  |
| D3-s2-01 | D3-s2 | D3.M2 | medium | I1 | Store-parser non-finite guards in flow_lift, tariff, price_model survive deletion: no gate driver notices *[catch-up batch]* | reported |  |
| D3-s2-02 | D3-s2 | D3.M2 | low | I1 | PriceShapeModel residual_var restore can discard every stored variance with the gate green *[catch-up batch]* | reported |  |

#### D4 — UI/UX

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D4-s1-01 | D4-s1 | D4.M3 | medium | P9 | Status text coloured by HA's --success/--error/--warning-color fails WCAG AA on the default themes | reported |  |
| D4-s1-02 | D4-s1 | D4.M1 | medium | P2 | Lane slot menu is placed at the tap point unclamped; near the right edge it spills past its chart and the viewport | reported |  |
| D4-s1-03 | D4-s1 | D4.M1 | medium | new | Setup picker: two identically named sensors render as identical options at 375 and 768 px | reported |  |
| D4-s1-04 | D4-s1 | D4.M1 | medium | new | Setup layout editor: removing a pipe, drawing a pipe and moving a box have no keyboard route | reported |  |
| D4-s1-05 | D4-s1 | D4.M1 | high | P2 | Now-marker label prints over the measured-now reading on the live default view | reported |  |
| D4-s2-01 | D4-s2 | D4.M2 | medium | P6 | Setup wizard's device pre-fill page shows raw keys: 3 unlabelled fields and 1 untranslated error | reported |  |
| D4-s2-02 | D4-s2 | D4.M2 | medium | P8 | Wood price field shows 'SEK/m³' to a non-SEK install while its sibling money fields follow the instance currency | reported |  |
| D4-s2-03 | D4-s2 | D4.M3 | medium | new | The hot-water minimum error text shows literal '\u00b0C' (en) and 9 escaped letters (sv) | reported |  |
| D4-s2-04 | D4-s2 | D4.M2 | high | P2 | Expert setup: the zones page says 'leave defaults if you don't need two-zone' and leaving them turns two-zone on | reported |  |
| D4-s2-05 | D4-s2 | D4.M1 | low | new | 12 number fields start off their own step grid: native validity flags them, one spinner click gives 5.1 not 5.5 | reported |  |
| D4-s2-06 | D4-s2 | D4.M2 | low | P2 | The zones page computes the derivation-overwrite warning but never shows it for its 6 derived fields | reported |  |
| D4-s2-07 | D4-s2 | D4.M2 | low | new | After 'Quick setup (recommended)' the wizard returns to the identical menu, offering quick setup again | reported |  |
| D4-s2-08 | D4-s2 | D4.M3 | low | new | None of the 12 registered services has an icon in icons.json | reported |  |
| D4-s2-09 | D4-s2 | D4.M3 | low | new | 8 help texts per language write '45 C' / 'W/m2' beside selectors that say °C and m² | reported |  |
| D4-s2-81 | D4-s2 | D4.M2 | medium | new | Setup overview page and setup diagram publish English slot text on a Swedish install *[from lead (L4)]* | reported |  |

#### D5 — Docs structure, flow and content; code comments

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D5-s1-01 | D5-s1 | D5.M1 | medium | I5 | configuration.md 'Initial setup' documents the pre-v6.6.5 flow: no finish menu, Tibber token required, 74 entities | reported |  |
| D5-s1-02 | D5-s1 | D5.M3 | medium | I5 | setup.md Quick setup promises buffer storage and two-tank physics that the quick-setup answers cannot produce | reported |  |
| D5-s1-05 | D5-s1 | D5.M1 | low | I5 | Docs name 5 option fields by labels the options forms do not show | reported |  |
| D5-s1-06 | D5-s1 | D5.M1 | low | I5 | simulate_plan accepts 5 wood fields that no doc names; configuration.md's table says 16 fields and its prose lists 11 | reported |  |
| D5-s2-01 | D5-s2 | D5.M4 | low | I5 | Card comments cite 12 private members the card no longer has (17 mentions) | reported |  |
| D5-s2-02 | D5-s2 | D5.M4 | low | I5 | Three comments cite a number the code beside them does not deliver | reported |  |
| D5-s2-03 | D5-s2 | D5.M4 | low | I5 | DHW_COLD_WATER_TEMP comment claims the draw model heats from it; the draw reads the configured inlet | reported |  |
| D5-s2-51 | D5-s2 | D5.M4 | low | I5 | Two optimizer comments describe a data flow the code does not have (warm-start alignment, buffer-series stash) *[from lead (L1)]* | reported |  |

#### D6 — README and documentation claim verification

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D6-s1-01 | D6-s1 | D6.M2 | low | I5 | README's Heat Pump Action state list omits idle and system_identification, which the sensor publishes | reported |  |
| D6-s1-02 | D6-s1 | D6.M2 | low | I5 | README puts the two-zone split and the orientation factor on the wrong options pages | reported |  |
| D6-s1-03 | D6-s1 | D6.M2 | low | I5 | README's disabled-by-default census omits six hot-water sensors that the no-hot-water install disables | reported |  |
| D6-s1-04 | D6-s1 | D6.M2 | low | I5 | README says apply_manual_plan pins 'up to 20 hours'; an explicit expires_at pins the whole horizon | reported |  |
| D6-s1-81 | D6-s1 | D6.M1 | low | P11 | README's SEK currency fallback is unreachable under Home Assistant core, which defaults Config.currency to EUR *[from lead (L4)]* | reported |  |
| D6-s2-01 | D6-s2 | D6.M2 | low | I5 | configuration.md says 'All 74 entities'; the six platforms create 75 | reported |  |
| D6-s2-02 | D6-s2 | D6.M2 | low | I5 | configuration.md: the weather page does not create the entry; the setup flowchart omits the menu and overview | reported |  |
| D6-s2-03 | D6-s2 | D6.M2 | low | I5 | Curve-bias 'at most 0.5 K per week' is false: 0.6 K in a 7-day window | reported |  |
| D6-s2-04 | D6-s2 | D6.M2 | low | I5 | how-it-works.md: space solve 'from two starting points'; it runs four, each refined and polished | reported |  |
| D6-s2-05 | D6-s2 | D6.M2 | low | I5 | configuration.md simulate_plan field list omits the five wood fields | reported |  |

#### D7 — Architecture and maintainability

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D7-s1-02 | D7-s1 | D7.M5 | medium | I1 | Drift-gate comparison and stress per-scenario budget verdict are deletable with every runnable check green | reported |  |
| D7-s1-71 | D7-s1 | D7.M1 | low | new | Cold-water inlet default held three times: 3 of 5 sites ignore DEFAULT_DHW_INLET_TEMP when it moves *[from lead (L3)]* | reported |  |
| D7-s3-01 | D7-s3 | D7.M6 | low | new | 10 class members are reached by no production code; 9 are kept only by tests that pin them | reported |  |
| D7-s3-51 | D7-s3 | D7.M6 | low | new | nightly_ha._async_check_a4 returns inside finally: an in-flight CancelledError or KeyboardInterrupt is swallowed *[from lead (L1)]* | reported |  |
| D7-s3-72 | D7-s3 | D7.M6 | low | new | 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer *[from lead (L3)]* | reported |  |

#### D8 — Sensor verification and ordering

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D8-s1-01 | D8-s1 | D8.M2 | high | P2 | Current Electricity Price publishes an earlier quarter's price when prices are quarter-hourly | reported |  |
| D8-s1-02 | D8-s1 | D8.M2 | low | P2 | DHW Heating Schedule counts 15-minute steps as 'heating periods', disagreeing with DHW Heating Plan's slot count | reported |  |
| D8-s1-03 | D8-s1 | D8.M2 | low | P2 | Recommended Power publishes a sub-threshold draw at steps Heat Pump Action reports 'off' | reported |  |
| D8-s3-01 | D8-s3 | D8.M3 | low | new | Accuracy and Energy-dashboard meter families split in both English and Swedish name sort | reported |  |
| D8-s3-02 | D8-s3 | D8.M3 | low | I5 | Swedish name of Sensor-Gap Advisor reads 'sensor gap in the currency' and drops the advisor role | reported |  |
| D8-s3-03 | D8-s3 | D8.M4 | low | new | Upper Floor Temperature, a byte duplicate of Indoor Temperature, is enabled by default on every install | reported |  |
| D8-s3-61 | D8-s3 | D8.M4 | low | P2 | Valve Target Recommendation ships disabled where a mixing valve is set, and available-but-unknown where none is *[from lead (L2)]* | reported |  |

#### D9 — CPU and memory efficiency, Raspberry-Pi-class target

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D9-s1-01 | D9-s1 | D9.M1 | medium | new | Per-row Python loop in _comfort_terms_batch costs 13-32% of every solve; a row-vectorized twin is bit-identical here | reported |  |
| D9-s1-02 | D9-s1 | D9.M1 | medium | new | L-BFGS-B asks the scalar objective for f(x) every iterate at ~19-26x a batched row: 9-19% of the solve | reported |  |
| D9-s1-03 | D9-s1 | D9.M1 | low | P10 | The sysid two-state fit runs inside one event-loop callback: 43-228 ms here (1.1-6x a reference solve) | reported |  |
| D9-s1-04 | D9-s1 | D9.M1 | low | new | DHW min-run repair: a full-suffix re-simulation per refused weak slot, 12-23% of a single-zone DHW solve | reported |  |
| D9-s1-71 | D9-s1 | D9.M1 | low | new | Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU *[from lead (L3)]* | reported | yes |
| D9-s2-03 | D9-s2 | D9.M2 | medium | new | stress.py misses a 2x solve regression in one scenario when the extra work is outside the simulate seams | reported |  |
| D9-s2-71 | D9-s2 | D9.M2 | medium | I1 | stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees *[from lead (L3)]* | reported | yes |

#### D10 — Home Assistant integration quality scale

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D10-s1-01 | D10-s1 | D10.M1 | medium | P2 | Entry unique id is not re-derived after reauth or an options edit, so the same plant can be set up twice | reported |  |
| D10-s1-02 | D10-s1 | D10.M1 | medium | P2 | Optimize-now button press returns normally when the solve did not run; the run_optimization action raises | reported |  |
| D10-s1-03 | D10-s1 | D10.M1 | low | P11 | Tibber auth refusal reaches HA as ConfigEntryNotReady/UpdateFailed, never ConfigEntryAuthFailed | reported |  |
| D10-s2-01 | D10-s2 | D10.M1 | medium | I5 | Climate presets auto and economy are non-standard and have no translation or icon in any language | reported |  |

#### D11 — Governance mechanisms and policy

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D11-s1-01 | D11-s1 | D11.M1 | high | I3 | A code-owned change pushed after the owner approval merges on that stale approval (dismiss_stale_reviews=false) | reported |  |
| D11-s1-02 | D11-s1 | D11.M4 | high | I3 | A non-stamp direct push to main over the DeployKey bypass is reported by no enumerator | reported |  |
| D11-s1-03 | D11-s1 | D11.M2 | medium | I3 | Three pull_request jobs execute the PR's own code-owned scripts while holding contents:write + actions:write | reported |  |
| D11-s1-04 | D11-s1 | D11.M2 | medium | new | Owner approvals given by the orchestrator are indistinguishable from the owner's in GitHub's record | reported |  |
| D11-s1-71 | D11-s1 | D11.M3 | low | I4 | Two parsers of a rule's paths: frontmatter disagree on 2 of 6 legal shapes (rules_sync vs policy_lint) *[from lead (L3)]* | reported |  |
| D11-s1-72 | D11-s1 | D11.M3 | low | I4 | entities.py GOV pin reads governance.yml only: a new governance job in 3 of 3 other workflow files passes *[from lead (L3)]* | reported |  |
| D11-s2-01 | D11-s2 | D11.M3 | medium | I3 | Per-file policy caps count lines, so a capped rule file grows in prose with its per-file budget check green | reported |  |
| D11-s2-02 | D11-s2 | D11.M1 | medium | I3 | policy_lint --hooks never reads a hook's matcher: a PreToolUse matcher naming no edit tool passes as wired | reported |  |
| D11-s2-03 | D11-s2 | D11.M2 | medium | new | The owner-approval predicate keys on the tvofi account, and 6 of 6 sampled owner approvals at head were seat-given | reported |  |
| D11-s2-04 | D11-s2 | D11.M3 | low | I5 | CLAUDE.md rule 1 quotes a mode line the gate does not print, and says FULL prints a zero it does not | reported |  |

#### D12 — Generalization

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D12-s1-01 | D12-s1 | D12.M2 | high | P6 | Hot water without a tank probe: every solve starts from the 55 C ThermalState default, never advanced | reported |  |
| D12-s1-02 | D12-s1 | D12.M2 | high | P2 | Untouched Hot water / Hot water tank options page turns hot-water planning on for an install with no tank | reported |  |
| D12-s3-81 | D12-s3 | D12.M4 | medium | P8 | Grid-fee bounds are SEK numbers: a 0.05 EUR/kWh fee is unenterable in HUF, ISK, JPY and KRW *[from lead (L4)]* | reported |  |

#### D13 — Process yield and cost

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D13-s1-01 | D13-s1 | D13.M1 | medium | I4 | --stats API-mode enumerator silently drops 52 of 253 window merges whose /commits/<sha>/pulls answers [] | reported |  |
| D13-s1-02 | D13-s1 | D13.M1 | high | new | 22 re-verification rounds after a moved head caught 0 defects; 12 heads moved only by merges or ci: commits | reported |  |
| D13-s1-03 | D13-s1 | D13.M3 | high | new | Body-answer blocks (8) exceed every engineering block class (max 1); record-and-body 12 vs engineering 7 | reported |  |

#### D14 — Recurring bug classes

| id | scope | step | severity | class_guess | title | status | provisional |
|---|---|---|---|---|---|---|---|
| D14-s1-01 | D14-s1 | D14.M3 | medium | P1 | P1: a malformed store leaf raises out of a loader or consumer; a naive legionella timestamp wedges every refresh | reported |  |
| D14-s1-02 | D14-s1 | D14.M3 | low | P6 | P6: horizon_hours read from coordinator.data but never written; boost probes a field only a test double defines | reported |  |
| D14-s2-01 | D14-s2 | D14.M4 | medium | P2 | P2: the two-zone and wood-furnace facts are re-derived from a proxy key at three seams beside their canonical predicate | reported |  |
| D14-s2-02 | D14-s2 | D14.M4 | medium | P8 | P8: a money figure's currency comes from the label source, never from the price feed that denominates it | reported |  |
| D14-s2-03 | D14-s2 | D14.M4 | low | I4 | I4: class roster and finding grammar have disagreeing readers (P11 on no D14 seat; intake admits schema-refused ids) | reported |  |
| D14-s3-01 | D14-s3 | D14.M4 | low | P3 | P3: 22 quantities are read through a positive floor at one seam and raw at a sibling; no check enumerates them | reported |  |
| D14-s3-02 | D14-s3 | D14.M4 | low | P4 | P4: both multi-start seams stop at non-stationary points; 12 of 30 seam calls ship >0.1 % above reachable | reported |  |
| D14-s3-03 | D14-s3 | D14.M4 | medium | P5 | P5: sysid adoption gate keys on the UA half-width, which barely moves while unmodelled free heat biases UA to -21 % | reported |  |
| D14-s4-01 | D14-s4 | D14.M4 | high | P7 | Eight production seams still do wall-clock datetime arithmetic across DST; the forecast grid lands 60 min off | reported |  |
| D14-s4-02 | D14-s4 | D14.M3 | medium | P7 | The replay lane freezes a fixed-offset clock, so a DST-day replay reports zero P7 seams | reported |  |
| D14-s5-01 | D14-s5 | D14.M3 | medium | I2 | Python closures miss every file a spawned child process reads; select() skips the script on a change to it | reported |  |
| D14-s5-02 | D14-s5 | D14.M3 | medium | I1 | Mutation ratchet inventory cannot see 528 of 2313 production guard seams; a new guard of those shapes raises it by 0 | reported |  |

**D3 findings rest on the seats' pre-screen evidence.** D3's method (`tools/audit/briefs/D3.md`) turns a pre-screened survivor into a finding only after the quiet-window `GATE_SCOPE=full GOLDEN_MODE=drift` gate confirms it; that quiet window was **not run** this round, by tvofi's rule of 2026-09-26 (no heavy D3 re-runs). D3-s1's and D3-s2's findings above are registered as reported on the strength of the pre-screen closures alone, and the judge inherits that gap rather than a re-measured one.

### Leads — round 9

What the finder seats noticed outside their own cells, routed to the four leads seats (L1-L4). A lead is **converted** into a finding only with an executed number (rows above, marked *from lead*), or **closed** with a reason. Taken from `leads_result.json`, `leads_result_L2.json`, `leads_result_L3.json` and `leads_result_L4.json`.

| raised by | owner seat | file | symbol | converted to / closed because |
|---|---|---|---|---|
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator.async_run_optimization (:5096 _record_quiet_comfort_period) | converted to D1-s2-51 |
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | _async_save_ledger / _async_save_thermal_learning / _async_save_price_model / _async_save_energy_totals | converted to D1-s2-52 |
| D1-s3 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._apply_action | converted to D1-s2-51 |
| D6-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/services.py | handle_apply_manual_plan | converted to D1-s2-54 |
| D14-s4 | D1-s2 (L1) | custom_components/heatpump_optimizer/coordinator.py | _run_in_process / _ensure_worker | converted to D1-s2-55 |
| D1-s1 | D1-s5 (L1) | custom_components/heatpump_optimizer/inputs.py | input reader (problem codes) | converted to D1-s5-52 |
| D8-s1 | D2-s1 (L1) | custom_components/heatpump_optimizer/coordinator.py | _dhw_setpoint_sweep | converted to D2-s1-51 |
| D7-s2 | D5-s2 (L1) | custom_components/heatpump_optimizer/optimizer.py | OptimizationResult.buffer_temp_trajectory | converted to D5-s2-51 |
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/ | set_thermal_parameters | converted to D1-s2-53 |
| D1-s1 | D1-s2 (L1) | custom_components/heatpump_optimizer/ | async_reset_comfort_weight and the cycle-end save | converted to D1-s2-52 |
| orchestrator (#110) | D1-s5 (L1) | custom_components/heatpump_optimizer/inputs.py | INPUT_MAX_AGE_MINUTES age gate (Indoor Temperature unavailable after 60 min) | converted to D1-s5-51 |
| D1-s1 | D1-s1 (L1) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | converted to D1-s1-51 (outside L1's own dimension) |
| D1-s2 | D1-s1 (L1) | tests/hastub/homeassistant/helpers/storage.py | Store.async_load | converted to D1-s1-51 (outside L1's own dimension) |
| D1-s4 | D1-s1 (L1) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | converted to D1-s1-51 (outside L1's own dimension) |
| D1-s3 | D1-s1 (L1) | tests/hastub/homeassistant/util/dt.py | now | converted to D1-s1-52 (outside L1's own dimension) |
| D14-s1 | D1-s1 (L1) | tests/hastub/homeassistant/util/dt.py | now | converted to D1-s1-52 (outside L1's own dimension) |
| D7-s3 | D7-s3 (L1) | tests/nightly_ha.py | line 1274 (return inside finally, A4 recovery block) | converted to D7-s3-51 (outside L1's own dimension) |
| D0-s3 | D5-s2 (L1) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._warm_start_starts docstring / coordinator._warm_seeded | converted to D5-s2-51 (outside L1's own dimension) |
| D0-s1 | (L1, closed) | tests/optimality.py | score_plan / pin_result | closed: owner deferred to catch-up batch; re-route then (owner D3-s3) |
| D0-s1 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._solve_space / _co_optimize | closed: closed by D0-s3 non-finding (M6/M7 measured by the owner: step 0 moves 1.197->1.200 kW in the largest cell, none in the other two); D0-s1 non-finding (horizon not reachable) |
| D0-s2 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize | closed: closed by D0-s3 non-finding M6/M7 (receding-horizon realisation measured by the owner) and D0-s2-01/02, which carry the step-0 change |
| D0-s2 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._terminal_cost | closed: closed by D0-s3 non-finding M7 (terminal-credit share at 6 h measured by the owner) |
| D0-s3 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize / HeatPumpOptimizer._solve_space seed set | closed: closed by D0-s1 non-finding: two-zone winter grid gap within 0.54 %, step 0 unchanged |
| D0-s3 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize seed set | closed: closed by D0-s2-02 (same seed-set gap on shoulder/summer_negative cells) |
| D1-s1 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _async_update_data (:4677 _async_watch_learning_drift guard); _async_load_accuracy (:7270-7283) | closed: closed by D1-s2 non-finding M2 (owner measured the from_dict chain: no sibling store lost at this baseline); the DEBUG heartbeat log is the documented guard level |
| D1-s3 | (L1, closed) | custom_components/heatpump_optimizer/services.py | SERVICE_SCHEMA_SET_AWAY | closed: closed by D1-s3-01 (tz-less return_time reaching the coordinator is that finding's mechanism) |
| D1-s4 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | thermal-learning load of internal_gains_profile (~3018-3023) and _learn_internal_gains (~8550) | closed: non-finding by measurement: gains_nan_probe.py nonfinite=0/4 (QuarantiningStore._sanitize scrubs "nan"/"inf" strings before float()); --raw bypass control 4/4 |
| D1-s4 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _shutdown_process_pool / _run_in_process | closed: closed by D1-s2-05 (shutdown waits on _PROCESS_LOCK held across the solve) |
| D1-s4 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _forecast_arrays | closed: non-finding by measurement: forecast_nonfinite.py failed_arms=0/7 at the coordinator boundary; positive control -1e308 fails (finite-absurd class is D1-s4-owned) |
| D1-s5 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator (price_sensor attributes at ~6992, peak_threshold_kw) | closed: closed by D1-s5-02 (negative threshold from a corrupt peak store is that finding's producer; publishing is its downstream) |
| D1-s5 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | solar_radiation horizon build from OpenMeteoSolar.irradiance_for | closed: closed by D1-s5-04: all-None irradiance falls back to the weather entity, else 0.0 (coordinator.py:6159), logged at DEBUG |
| D4-s2 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | dhw_legionella_above_setpoint repair (config_flow._dhw_legionella_warning judgement) | closed: non-finding: the shipped 55/60 default pair is excluded as "stock" in legionella.py, so a fresh default install raises no repair |
| D8-s1 | (L1, closed) | custom_components/heatpump_optimizer/coordinator.py | _get_current_price / _current_spot_price | closed: closed by D2-s3-01 (hour-window pricing under quarter-hour prices) |
| D1-s1 | (L1, closed) | custom_components/heatpump_optimizer/dhw_draws.py | DrawStats.fold / from_dict | closed: closed by D1-s1-03 (unbounded DrawStats energy is that finding) |
| D1-s2 | (L1, closed) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel._stability_substeps | closed: closed by D1-s2-02 (runaway wind-driven substeps) |
| D1-s2 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.optimize | closed: closed by D1-s2-02 (non-physical finite forecast accepted); owner-side D1-s4 guard scope |
| D1-s5 | (L1, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._stash_price_horizon | closed: inf sigma unreachable: QuarantiningStore._sanitize scrubs non-finite residual_var before from_dict; finite-absurd variance is D1-s5-02; price_risk_lambda defaults to 0 |
| D1-s2 | (L1, closed) | custom_components/heatpump_optimizer/store.py | QuarantiningStore._sanitize | closed: closed by D1-s2-03 (>= 2**64 counts through the loader int()) |
| D2-s1 | (L1, closed) | custom_components/heatpump_optimizer/sysid.py | identify / heat-loss learner (house_heat_loss_scale) | closed: closed as seam of D2-s1-01: the learned scale enters the same diagonal the substep count already includes |
| D2-s4 | (L1, closed) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel.simulate_step | closed: closed by D2-s1 non-finding (dt invariance measured by the owner) |
| D8-s1 | (L1, closed) | custom_components/heatpump_optimizer/battery.py | VirtualBattery / label_measured | closed: closed by D12-s1-01 (unmodelled constant tank default) and the #282 disclosure decision |
| D6-s2 | (L1, closed) | docs/configuration.md | lines 181-187 (setup hot-water table) | closed: closed by D5-s1-02 (configuration.md table split) |
| orchestrator (#110, D4 framing) | (L1, closed) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | IndoorTempSensor source-id attribute / card _entityIds indoor derivation | closed: D4 (card): route to D4 owner. The D4 side stands structurally: IndoorTempSensor publishes no source-entity attribute (sensor.py:636-661 defines no extra_state_attributes) and the card derives its indoor trace only from *_indoor_temperature_optimizer (card.js:4749-4775), so it cannot draw the raw thermometer through the stale gap; not measured by L1 |
| D1-s2 | (L1, closed) | tests/harness.py | ha_unload_entry | closed: non-finding by measurement: unload_coroutines.py dropped=1, raised_when_run=0 (the dropped async_shutdown coroutine has no effect the harness can observe) |
| D8-s1 | D8-s3 (L2) | custom_components/heatpump_optimizer/sensor.py | ValveTargetRecommendationSensor | converted to D8-s3-61 |
| D1-s3 | (L2, closed) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | away-strip data-away-return change handler | closed: Same phenomenon as D1-s3-01, which names the card's datetime-local value as a seam (tz-less return_time; every later cycle raises until away is switched off). Card side (owner D4-s1 by check_scopes) is a seam of that finding, not a second one. |
| D4-s1 | (L2, closed) | custom_components/heatpump_optimizer (plan narrative sensor) | plan_narrative attributes.language | closed: Owner D8-s1 by check_scopes (sensor.py, D8.M2 attributes). Measured, holds: narrative_language_mismatch=0 of 4 hass.config.language arms (l2_d8_leads.py --only E; perturbation -> 2). The backend follows HA's configured language; a single-state sensor cannot follow each viewer's UI language. |
| D8-s3 | (L2, closed) | README.md | Entities > temperatures table, Upper Floor Temperature row | closed: Owner D6-s1 (README.md). Seam of D8-s3-03, which measured Upper Floor Temperature = Indoor Temperature on all 5 topologies including single-zone installs with no upper floor; README:503's 'The radiator zone' is true only under the two-zone convention the sensor docstring states. The README row is carried with that finding's fix. |
| D10-s2 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | SolarIrradianceSensor.extra_state_attributes / open_meteo.OpenMeteoSolar.diagnostics | closed: Owner D8-s1 by check_scopes (sensor.py attributes). Measured: 5 dp recorded vs diagnostics' 1 dp (l2_d8_leads.py --only F). Not a defect: the value is hass.config's own home coordinate inside the instance; diagnostics coarsens because that file leaves it. |
| D10-s2 | (L2, closed) | custom_components/heatpump_optimizer/icons.json | services section | closed: Owner D4-s2 by check_scopes (icons.json); measured by D4-s2-08 (12 of 12 services without an icon). |
| D11-s1 | (L2, closed) | docs/decisions/0011-app-authored-identity.md | Context: 'about eleven of its merged pull requests now return 404' | closed: No seat owns it: check_scopes --seat for every D11/D5/D6 seat lists no docs/decisions/** cell (D11's universe is .github/.claude/.cursor/tools/CLAUDE.md/AGENTS.md; D5/D6 name specific docs files), although D11.md M3 names 'status lines in docs/decisions/'. Scope gap for the orchestrator to route; the executed 52-of-253 count is D11-s1's (its exposure line). Not measured here: it needs GitHub API reads. |
| D11-s1 | (L2, closed) | docs/decisions/0008-a-seat-identity-distinct-from-the-owner.md | step 3(d) dismiss_stale_reviews_on_push: true | closed: Measured by D11-s1-01, whose claim names decisions 0008 3(d) and 0009 step 6 against live ruleset 23698884 (dismiss_stale_reviews_on_push=false). |
| D4-s2 | (L2, closed) | custom_components/heatpump_optimizer/wood_fuel.py | wood_fuel_ready / cheaper_hour_count (CONF_WOOD_PRICE_SEK_M3) | closed: Owner D12-s1. Measured (l2_wood_currency.py): the comparison is currency-agnostic, factors_changing_count=0 of 6. The harm is D4-s2-02's form label: a EUR install typing the price in SEK as the unit asks gets 0 cheaper steps vs 60. Seam evidence for D4-s2-02; the SEK-named keys price_sek_m3/sek_per_kwh belong to the same fix. |
| D5-s1 | (L2, closed) | custom_components/heatpump_optimizer/translations/en.json | config.step.quick_setup.data_description.buffer_tank / wood_buffer_tank | closed: Seam of D5-s1-02 (same mechanism: quick_setup.derive never sets a throttling mixing valve, so buffer_is_store and two_tank_modelled stay off). The form text at translations/en.json:312/:315 (strings.json same keys) is a second place the claim shows; carry it to that finding's seams. |
| D6-s2 | (L2, closed) | custom_components/heatpump_optimizer/strings.json | options ... data_description.curve_learning_enabled (line 1333) | closed: Seam of D6-s2-03 (curve bias moves 0.6 K in 7 days against 'at most 0.5 K per week'); strings.json/en.json:1333 carries the same figure as 'at most half a degree per week'. |
| D12-s1 | (L2, closed) | custom_components/heatpump_optimizer/config_flow.py | HeatPumpOptimizerConfigFlow.async_step_dhw | closed: Seam of D12-s1-02 (an untouched hot-water page stores dhw_windows/dhw_tank_volume and turns DHW planning on); its harness phantom_dhw.py already drives the wizard_dhw_step seam (HeatPumpOptimizerConfigFlow.async_step_dhw). The missing 'no tank' answer is that finding's fix surface. |
| D5-s1 | (L2, closed) | README.md | Entities: 'Nineteen entities (eighteen sensors and the wood binary sensor) are disabled by default' | closed: Owner D6-s1 measured it: D6-s1-03 (26 disabled on a no-hot-water install, six DHW sensors unlisted) and NF C08/C09 (19 on a hot-water install, list matches); D8-s3's NF agrees (19 + 7 DHW-gated). |
| D6-s2 | (L2, closed) | README.md | line 44 | closed: Owner D6-s1 measured it as a non-finding (claims.py C27-C48, 'curve 0.5 K/week' equal to the constant). That check reads the constant; D6-s2-03 measures the behaviour at 0.6 K in 7 days. The judge reconciles the two; README:44 is a seam of D6-s2-03's phenomenon. |
| D5-s1 | (L2, closed) | docs/setup.md | 'the original eleven-page wizard'; 'Quick setup arrived in v6.6.5' | closed: Owner D6-s2; measured here, holds: 10 screens at v6.6.4 on either building route (8 forms + 2 menus), 11 with the opt-in device pre-fill page; #1251 under the v6.6.5 heading (l2_wizard_pages.py; --with-offer -> 11). |
| D5-s1 | (L2, closed) | docs/ecl110.md | ## Sensors: 'on an install whose topics were configured at setup they are enabled' | closed: Owner D6-s2. Stale wording, not a false instruction: no initial-flow page offers an ECL110 topic (D6-s1 NF C49/C50), and ecl110.md:113-114 prescribes the only reachable route (topics added in Options, enable from the device page); 'configured at setup' describes only pre-v4.1.0 entries, which the same doc states at :88. README:549-550 is the same wording. |
| D5-s1 | (L2, closed) | docs/configuration.md | Services table: simulate_plan '16 optional comfort and wood fields' | closed: Owner D6-s2 measured it as D6-s2-05 (the paragraph lists 11 of the schema's 16 fields); D5-s1-06 carries the structure half. |
| D8-s1 | (L2, closed) | custom_components/heatpump_optimizer/entity.py | commanded_power_kw (climate recommended_power_kw) | closed: Seam of D8-s1-03: climate.py:232 publishes recommended_power_kw from entity.commanded_power_kw, the symbol D8-s1-03 instruments (whose docstring lists the climate among its four readers). |
| D8-s2 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | IndoorTempSensor.available | closed: Owner D8-s1; measured, holds: non_measured_hidden=0 over 5 topologies; the 20 hidden entities are the thermometer's own and the thermal-battery 'store sensed' gate (l2_d8_leads.py --only B; perturbation gate -> 5). |
| D8-s2 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | Heat Pump Action / operating-state sensors | closed: Owner D8-s1; measured, holds: boost_off_mismatch=0 of 7 mode-off boost arms, control 0; Heat Pump Action reads the actuated action's mode (boost / hot_water) (l2_d8_leads.py --only A; perturbation label -> 7). |
| D8-s3 | (L2, closed) | custom_components/heatpump_optimizer/sensor.py | DHWHeavyDaySensor | closed: Owner D8-s1; measured, holds: heavy_day_on_no_dhw=0 of 3 no-DHW topologies, and tests/entities.py _DHW_GATE_EXCEPTIONS names it with its reason (l2_d8_leads.py --only C). |
| D10-s1 | (L2, closed) | custom_components/heatpump_optimizer/config_flow.py | config-flow-test-coverage / test-coverage rows | closed: Owner D10-s2 measured D10.M3 as a non-finding: every module above 95 % statement coverage (min 95.12 %), which decides both coverage rows. |
| D10-s1 | (L2, closed) | custom_components/heatpump_optimizer/strings.json | exceptions section | closed: Owner D10-s2 NF exception-translations: raise_without_key=0 at baseline. The keys owed by fixes of D10-s1-02/-03 are a constraint on those fixers, not a baseline defect. |
| D10-s1 | (L2, closed) | custom_components/heatpump_optimizer/quality_scale.yaml | manifest quality_scale: platinum | closed: Not a separate mechanism: the declared tier stands or falls with D10-s1's Bronze/Silver findings; D10-s2's gold/platinum rows are non-findings except D10-s2-01. |
| D14-s4 | (L2, closed) | custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js | slot-hit rect (TARGET_MIN_PX_COARSE) | closed: Owner D4-s1 NF: every HTML control clears 24 px (44 px coarse); lane slot targets are recorded there as the boxed-in residue by design. |
| D5-s2 | D1-s2 (L3) | tests/hastub/homeassistant/helpers/update_coordinator.py | DataUpdateCoordinator.__init__ | converted to D1-s2-71 |
| D5-s2 | D7-s1 (L3) | custom_components/heatpump_optimizer/thermal_model.py | ThermalParameters.dhw_inlet_temp | converted to D7-s1-71 |
| D7-s2 | D7-s3 (L3) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel._step_dhw_refused/_step_dhw_floor_injected/_step_dhw_draw_kw/_step_wood_refused | converted to D7-s3-72 |
| D9-s2 | D9-s1 (L3) | custom_components/heatpump_optimizer/thermal_model.py | ThermalModel.effective_dhw_draw_pattern / dhw_tank_heat_loss_coefficient / dhw_inlet_reference | converted to D9-s1-71 |
| D12-s1 | D9-s2 (L3) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.optimize | converted to D9-s2-71 |
| D11-s2 | D11-s1 (L3) | .claude/workflows/rules_sync.mjs | parse | converted to D11-s1-71 |
| D13-s1 | D11-s1 (L3) | tools/audit/round4/D11/governance_cost.py | GOV | converted to D11-s1-72 |
| D1-s1 | (L3, closed) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | closed: done by L1: D1-s1-51 |
| D1-s2 | (L3, closed) | tests/hastub/homeassistant/helpers/storage.py | Store.async_load | closed: done by L1: D1-s1-51 |
| D1-s2 | (L3, closed) | tests/harness.py | ha_unload_entry | closed: done by L1: non-finding (unload_coroutines.py dropped=1, raised_when_run=0) |
| D1-s3 | (L3, closed) | tests/hastub/homeassistant/util/dt.py | now | closed: done by L1: D1-s1-52 |
| D1-s4 | (L3, closed) | tests/hastub/homeassistant/helpers/storage.py | Store.async_save/async_load | closed: done by L1: D1-s1-51 |
| D3-s1 | (L3, closed) | tests/golden/coord_dhw.json | data.dhw_advisor | closed: closed by D3-s1's own M2 prescreen entry: dhw_advisor is produced in coordinator.py (D3-s1's cells, check_scopes --seat D3-s1), and mutant C0086 (_dhw_setpoint_sweep) was KILLED by features.py, so the gate is not blind to the advisor's cover/ranking logic; the golden's degeneracy is redundancy, not a gap. Not re-run (tvofi 2026-09-26: no heavy D3 scripts). |
| D3-s1 | (L3, closed) | tools/audit/round3..round8 | (tracked files) | closed: by design, measured: r9-strip-rounds.sh (prepare_baseline strip_earlier_rounds) run on this seat's export printed RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 -- the same 498; it keeps every tools/audit/round* file named in tests/closures.json or by a literal path in tests/*.py\|*.mjs\|*.sh, so no file the gate reads is removed. Export-only; the tracked tree is untouched. |
| D4-s1 | (L3, closed) | tests/card_rig.mjs | planStates | closed: closed by D4-s1-05 (now-marker label over the measured-now reading on the live default view): that the card lanes' default-view states come from planStates() without withActuals is why the gate missed it -- the failing lane test that finding's fix owes (fixer.md step 1) and the escape's process cause under defect-root-cause.md, not a second mechanism. Owner D4-s1 (www/**; tests/*.mjs sit in no seat's cells, check_scopes). |
| D4-s1 | (L3, closed) | tests/card_browser.mjs | contrastOf / REQUIRED | closed: closed by D4-s1-01 (status-token text below WCAG AA): the contrast lane measuring four fixed sites on fixtures with no status outcome is why the gate missed it -- the failing lane test that fix owes and its root-cause seat's process cause, not a second mechanism. Owner D4-s1. |
| D6-s2 | (L3, closed) | tests/entities.py | README count pins (~lines 566-886) | closed: closed by D6-s2-01 (configuration.md 'All 74 entities' vs 75): the missing pin is the failing test that finding's fix owes under fixer.md step 1, not a second mechanism. D6-s2's cells hold docs/configuration.md (check_scopes --seat D6-s2). |
| D7-s3 | (L3, closed) | tests/nightly_ha.py | line 1274 (return inside finally, A4 recovery block) | closed: done by L1: D7-s3-51 |
| D11-s1 | (L3, closed) | tests/delivery_status.py | collect | closed: same phenomenon and seam as D11-s1-02 (single-parent direct pushes to main reported by no enumerator); its proposed_fix_scope already names delivery_status.collect. The docstring is that seam's prose; no separate mechanism. |
| D12-s1 | (L3, closed) | tools/audit/round9/D12/s1/ | REPORT.md | closed: not a defect of the baseline: a report-rendering matter for the orchestrator (the seat's JSON is its report). Nothing to measure. |
| D12-s3 | (L3, closed) | tests/entities.py | _walk_flow_untouched / check 'and turns hot water on anyway, with the 200 L tank the page pre-fills' | closed: owner deferred to catch-up batch; re-route then (a test-suite gap on config_flow.py is a D3 cell; check_scopes --seat D3-s3 lists config_flow.py) |
| D14-s1 | (L3, closed) | tests/hastub/homeassistant/util/dt.py | now | closed: done by L1: D1-s1-52 |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._run_system_identification | closed: closed by D9-s1-03, one finding per mechanism: its claim already names the synchronous call of SystemIdentification.step in coordinator._async_update_data; the call-site fix is that finding's fix scope. |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | _maybe_run_fuse_advisor / _await_optimize | closed: closed by D9-s2's non-finding 'A coordinator cycle runs exactly one full solve by default': solves_per_cycle_mean=1.0000 (main 48/48), 2.0000 with price tiles, fuse advisor 0 solves/day (weekly rate limit). |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | _solve_snapshot | closed: closed by D9-s2's non-finding on the default cycle's loop-thread work: loop_update_cpu_ms=9.03 per cycle (0.617 reference solves including the entity read), which bounds everything _async_update_data runs on the loop, _solve_snapshot included. |
| D9-s1 | (L3, closed) | custom_components/heatpump_optimizer/coordinator.py | _await_optimize (in-process fallback) | closed: closed by D9-s1's non-finding (in-process fallback starvation share 0.91-0.94, documented degraded path capped by WORKER_FALLBACK_CAP with a repair issue); what remains is a design choice about N, not a falsifiable defect. |
| D9-s2 | (L3, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._build_dhw_requirements / _apply_dhw_min_run / _plan_dhw_min_cost | closed: closed by D9-s1-04 and D9-s1's DHW-planner non-finding: _build_dhw_requirements is the parent of every DHW planner (optimizer.py:4712; it calls _plan_dhw_min_cost, _plan_dhw_cheapest_first, _apply_dhw_min_run, _clamp_dhw_to_capacity, _repair_dhw_floor), D9-s1 decomposed that parent (0.526 of the single-zone DHW solve, 0.287 of it _apply_dhw_min_run = D9-s1-04; each other planner 0.001-0.124). The replay's 58 % is the same parent under cProfile. |
| D11-s2 | (L3, closed) | .github (ruleset on main) | pull_request rule: require_last_push_approval / dismiss_stale_reviews_on_push | closed: closed by D11-s1-01 (ruleset dismiss_stale_reviews_on_push=false, require_last_push_approval=false; #1621 and #1623 merged on a stale owner approval). |
| D11-s2 | (L3, closed) | .claude/workflows/policy_lint.mjs | cmdHooks | closed: closed by D11-s2-02 (cmdHooks never reads a hook's matcher, 4 of 4 wrong matchers pass): the missing policy-rot/hooks fixture is the failing test that fix owes, not a second mechanism. |
| D11-s2 | (L3, closed) | .claude/workflows/budget_raise_gate.py | approval | closed: closed by D11-s1-04 (budget_raise_gate.py:approval accepts orchestrator-given approvals as the owner's, 27/27) and D11-s2-03; the lead names a fix constraint, not a defect. |
| D13-s1 | (L3, closed) | .github/workflows/governance.yml | instrument-self-tests | closed: not measured by this seat: the lead needs GitHub Actions run history and logs for governance.yml's instrument-self-tests on main, and this seat's GitHub API read was refused by the permission system (no gh, per brief). D13-s1's count (18 of 201 main merges, one 11.69 h episode) stands unconverted; re-route to a seat with GitHub read (D11-s1's d11lib cache) in the catch-up batch. |
| D13-s1 | (L3, closed) | .claude/workflows/web-fix-wave.js | verdict poster identity | closed: same phenomenon as D11-s1-04 (seat actions are recorded under the owner account, so the record cannot show the owner's own act); D13-s1's count 166 of 239 'Fix review:' lines under tvofi is a further seam of it, carried here for that finding's fix. No GitHub read from this seat. |
| D0-s1 | D2-s2 (L4) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._comfort_terms | converted to D2-s2-81 |
| D4-s1 | D4-s2 (L4) | custom_components/heatpump_optimizer/topology.py | describe_setup slots / rank_sensor_advisor labels | converted to D4-s2-81 |
| D14-s3 | D2-s4 (L4) | custom_components/heatpump_optimizer/sysid.py | SystemIdentification (light_new preset) | converted to D2-s4-81 |
| D14-s2 | D12-s3 (L4) | custom_components/heatpump_optimizer/grid_fee.py | grid_fee:IMPLAUSIBLE_FEE_SEK_PER_KWH | converted to D12-s3-81 |
| D14-s2 | D6-s1 (L4) | custom_components/heatpump_optimizer/currency.py | currency:FALLBACK_CURRENCY | converted to D6-s1-81 |
| D0-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._comfort_terms | closed: owner D2-s2 (objective shape, D2.M3). Measured, non-finding: the constant costs nothing -- polish gap 0.0000 % in 12 summer_warm cells (see non_findings). |
| D0-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._terminal_cost | closed: owner D2-s2 already measured the terminal credit's sign and magnitude against a re-simulated continuation: ratio 0.997-1.123 over 6 cells including shoulder, 0 sign disagreements (D2-s2 non-finding, terminal_continuation.py). |
| D0-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._warm_start_starts docstring / coordinator._warm_seeded | closed: done by L1: D5-s2-51 |
| D0-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | OptimizationResult.predicted_cost | closed: owner D2-s2 measured predicted_cost == sum(price*(P_space+P_dhw)*dt) on all 50 golden scenarios (cost_err 0, D2-s2 non-finding); README.md:488 claims only 'Cost of the optimized 24 h plan', which that identity verifies, not the executed day. The 23.28 vs 38.61 SEK day gap is receding-horizon realisation (D0-s3's own M6 non-finding: the loop buys 0.6-1.0 K of warmth the objective values). |
| D1-s2 | (L4, closed) | custom_components/heatpump_optimizer/coordinator.py | async_diagnose_interval / _diagnose_payload | closed: owner D5-s2 (comment accuracy). Measured, non-finding: the worker does get copies on the production transport, leaked_writes=0 (see non_findings). |
| D2-s1 | (L4, closed) | custom_components/heatpump_optimizer/external_heat.py | ExternalHeatDetector.forecast_free_heat / optimizer.py HeatPumpOptimizer.optimize (np.clip of external_heat_kw) | closed: owner D1-s5 (external-input parsers). Measured, non-finding: nonfinite_forecast_cells=0 of 27; InputReader delivers no non-finite value (D1-s5 non-finding) (see non_findings). |
| D8-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | Optimizer._idle_action | closed: owner D8-s2 (climate recommended_power_kw via entity.commanded_power_kw). Covered by D8-s1-03: its property ('No entity attributes a power draw to the pump at a step the same action declares off') and fix scope (commanded_power_kw gates on heat_pump_on, shared with the climate attribute) include the idle action's power=min_electrical_power with heat_pump_on False; the fixer should add this seam to that finding's enumeration. |
| D9-s2 | (L4, closed) | custom_components/heatpump_optimizer/entity.py | HeatPumpOptimizerSensorBase.__init_subclass__ scrub (_finite) | closed: owner D9-s2, who bounds it already: its non-findings put loop-thread work outside the advisor at entity_read 5.89 ms per read and 0.617 reference solves per cycle, and the retained series the scrub walks are bounded (accuracy deque maxlen 672); the scrub is a subset of that bounded read, so no cost finding exists above the owner's bound. |
| D12-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer.get_current_action | closed: owner D12-s2. Covered by D12-s2-03: its property ('power_normalized stay in [0,1] ... on every compressor kind') and fix scope (clamp to [0,1]) include the modulating -0.2, which its own null arm measured (minimum -0.2). |
| D12-s2 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | HeatPumpOptimizer._idle_action | closed: owner D1-s2 (coordinator consumers). Not converted: the idle branch is reachable in production only when the wall clock steps back more than one step between _solve_anchor (now floored to the forecast grid) and get_current_action's only caller (coordinator.py:5074, right after the solve); the entity side of the same fact is D8-s1-03's property. Not measured here. |
| D12-s3 | (L4, closed) | custom_components/heatpump_optimizer/coordinator.py | HeatPumpOptimizerCoordinator._build_data_dict | closed: owner D1-s2. Not converted: every published surface of these three keys gates on reading_ok (the dhw/buffer/slab sensors' _reading_key, climate._measured, battery.label_measured #282), reading_ok is published in the same data dict, and the card reads entity states only; the lead names no reader that shows them unflagged. Not measured here. |
| D14-s2 | (L4, closed) | custom_components/heatpump_optimizer/quick_setup.py | quick_setup:stored_answers | closed: owner D4-s2. Measured, non-finding: derive/stored_answers round-trip mismatch 0 of 32 (see non_findings). |
| D14-s3 | (L4, closed) | custom_components/heatpump_optimizer/optimizer.py | _multi_start_minimize / _lbfgsb_restart | closed: owner D0-s1. Not a production claim: the ABNORMAL terminations are a challenger's at ftol 1e-12; production runs ftol 1e-6, whose stop-rule residue is D0-s2-01's finding and D0-s1's stoprule_ab non-finding (not price-attributable in aggregate). |

### Judge flags

Verbatim, `judge_flags.txt`:

```
Round-9 exposure flags for the judge (orchestrator, 2026-09-26).
(1) Driver Prepare step 1 copied tools/audit/round3..round8 into every finder tree. The boxes ran handoff/round9/r9-strip-rounds.sh (498 removed, 235 gate-read kept). Seats that ran partly BEFORE the strip: B1 D0-s1 and D3-s1; B8 D14-s1..s3; B10 D4-s1; the B4 seats (strip about 12 min into the fan-out); the B6 seats.
(2) B8 D14-s3 read docs/audit-2026-09.md rows (rounds 1, 2, 4, 6, 7) to locate fixes, and recorded it under exposure.
(3) B9 D14-s4 read, but did not cite, the docstrings of round3/D2/dst_window_factors.py, round5/D1/seat-b/h5_dst_age_seams.py and 80 lines of harnesses/j5_gil.py before the strip. This bears on D14-s4-01 and D14-s4-02.
(4) B3 D13-s1 imports the brief-named instruments tools/audit/round4/D11/{dora_keys,governance_cost}.py (gate-read, kept by the strip). It read their headers only.
(5) B2 D0-s2 listed round8/ directory names before the strip and opened no file. B3 D11-s1 ran ls on round8/D11 once.
(6) Several REPORT.md files were rendered by the box host from the seat's JSON. reports-Bn.json is authoritative.
(7) D3 quiet window NOT run, by tvofi's rule of 2026-09-26: no heavy D3 re-runs. D3 findings rest on the seats' pre-screen evidence.
(8) Catch-up batch: D3-s2 is in (registered with the lead findings); D3-s3 is still to come.
```
