# Round 4 — judge verdicts

- **worktree** `../audit-r4-judge`, detached at `cedec8b` (branch head of
  `claude/13-dimension-audit-920935`; `git diff 7dd68dd HEAD -- custom_components/`
  touches only the card's `CARD_VERSION` string, so every production file the
  findings hook is byte-identical to the baseline `7dd68dd`).
- **judge contract** `tools/audit/briefs/judge.md`, followed as written: re-run,
  perturb, compare metric definitions, leave-one-out, null control, assign
  `stop_rule_class` from the number.
- **box** 8-core Apple M1, load1 **1.80–4.39** across the session, quoted per
  harness below (the harnesses print it; it is quoted, never gated).
  `thread_factor=1.0` on every timing run. The gate lock (`judge-r4`) was taken
  for the two timing-sensitive re-measurements (`D9/h9_batch_cost_loop.py`,
  standalone `tests/golden.py`), renewed between commands, released at the end;
  process exclusivity confirmed before each (`ps aux | grep -E
  "[s]tress\.py|[t]ests/run\.sh"` → 0 every time; the harnesses' own
  `concurrent_gate_procs` counters read 0).
- **live GitHub state** measured 2026-09-12T22:25–23:10 local, fresh private
  cache `D11_CACHE=/tmp/d11-judge-cache` (the finder harnesses' pinned windows
  reproduce from `~/.cache/hpo-d11-round4`, the documented path; live
  re-measurements use the fresh cache plus my own direct `gh` arms).

## What this report decides

43 seated findings (the index's 39 rows plus the four `*-INST` instrument
findings the panels also voted on). Every verdict line carries: my number (or
the panel-sustained mark), the votes as counted, `stop_rule_class`, one line.

### The count in the ledger's summary is wrong, the JSON is right

`verify-tally.json`'s `_final` says "117 votes over 39 findings — 108 verify,
6 weaken, 3 refute". Recounting the JSON itself: **117 votes over 43
findings — 110 verify, 5 weaken, 2 refute**. The 39/108/6/3 figures match no
counting of the file they summarise. Separately, the D4, D7 and D8 seats marked
`pending` (usage-limit restart) all delivered reports — `verify-0-2.md` /
`verify-0-3.md` exist for all three dimensions — and those votes are **not**
in the JSON. Counting them: **123 votes over 43 findings — 114 verify, 5
weaken, 4 refute**. The kill arithmetic is unaffected: D4-02 is refute
3-of-3 either way (seat 1 in the JSON, seats 2 and 3 in their reports), and I
verified the kill's premise myself (below). The register should carry 43
findings, not 39.

## 1. The four splits, re-measured in full

### D11-04 — weakened(medium) — 2 verify-high vs 1 weaken-medium

My live number: `ruleset_probe.py` with a fresh cache → `required_contexts=16`
(both arms), `pull_request_rules=0`, **`tree_claim_mismatches=4`** at my head
(`governance.yml:354` claims 18; `docs/plan-2026-09-open-issues.md:714` claims
18 twice — count and `record`-required; `:1142` claims 18). My own whole-tree
grep (wider than the harness's nine-file `CLAIM_GLOBS`, which seat 3 showed
undercounts) finds a fifth site: `docs/decisions/0001-session-policy-merge-grant.md:11`.

Decision. The count moved 8 → 4/5 through main's own deletions and repairs
(`tests/record_status.py` deleted; `tests/entities.py:15394` and
`docs/HANDOVER.md:52` rewritten), and **every surviving contradiction is
prose** — a CI comment block, the plan of record, a decision document; no
executable assertion asserts the wrong number any more. The live ruleset is
authoritative and correct; `RELEASE_NOTES.md` records the drop. What keeps the
finding alive at medium: the workflow's own boundary account
(`governance.yml:354`, the stated justification for the `record-status` job)
still rests on the now-false premise, and the structural half holds — I
re-verified no tree file outside `tools/audit/round*` reads the rulesets or
`rules/branches` API, so `policy_lint`'s `counts` class keys on tree literals
and structurally cannot see ruleset drift. That is the brief's medium slot ("a
detector with no live control"), not its high slot. The perturbation
(`18`→`16` in governance.yml drops the count, direction correct) is invisible
to CI by construction. **stop_rule_class: hygiene** — what the number shows is
stale prose plus a blind detector, not a mechanism acting wrongly.

### D7-03 — weakened(medium) — 2 verify-high vs 1 weaken-medium

Re-ran both instruments at my head. Finder's `learner_freeze_r4.py`: exact —
`ingesting_cells_defrost=3` of `live_learner_cells=20`, external-heat /
open-window / pump-fault all 0, `positive_control_dead_learners=0`, and the
perturbation fires in-harness (`perturbed_ingesting_cells_defrost=0`). Seat
3's drift harness `verify3_own_D7-03.py`, my own execution:
`v3_sustained60h_light_new_final=0.9775`, `…typical_slab_final=0.9978`,
120/120 samples folded, vent CUSUM never trips, fix arm `1.0000`.

Decision. The mechanism is beyond dispute — the shared gate lacks the one
condition, three of four learners fold the flagged interval, `_learn_measured_cop`
is held only by its own bespoke block (stripping it moves the EWMA 1.200→1.220,
reproduced). The severity question was the magnitude the finder explicitly
left unmeasured. **My number: −2.25 % on `_house_heat_loss_scale` for the most
exposed shipped preset under a maximal regime (defrost every interval for 60 h),
−0.22 % on the typical preset, −0.07 % over one frosty night.** A ≤2.3 % UA
mis-scale is second-order in plan cost, on an opt-in flag path, requiring a
configured defrost entity. Real bug, clean one-line fix, persisted but bounded
bias: medium. Caveat carried forward (seat 3's, unclosed by me too): the
buffer-tank and DHW-learner magnitudes are unmeasured; if a defrost draws from
the indoor tank the relative signal there is larger. **stop_rule_class: bug.**

### D1-INST — weakened(low, hygiene) — 1 verify-low vs 2 weaken-low

Executed `verify2_d1inst.py` myself: `stub_refresh_cycles_run=0`,
`refresh_requests=3`, flag armed through setup (1), cleared by one direct call
(0). Both refuted consequences confirmed by my own reading:
`tests/features.py:16284-16299` sets `_skip_solve_once` and consumes it via a
direct `_async_update_data()` (asserting "the flag is consumed by the light
refresh"); `features.py:16660-16698` asserts the flag armed on the reloaded
coordinator and cleared after the handover consume; `tests/nightly_ha.py:1237,
1252, 2154` awaits `coordinator.async_refresh()` against the real base class,
and `tests/run.sh:289` excludes that lane from the gate.

Decision. The residual core survives as an instrument finding: the stub's
refresh entry points are counters, so **the gate suite never runs a cycle
through the coordinator base class** — the `UpdateFailed → last_update_success
False → entities unavailable` reaction chain, the debouncer and the listener
fan-out are unexercised anywhere the gate runs; the nightly container lane
owns them and the gate never invokes it. With both headline consequences
struck and two compensating controls in the tree, this is a low gate-lane
coverage hole. **stop_rule_class: hygiene.**

### D3-S3 — weakened(hygiene) — 2 weaken vs 1 refute

My own execution of `verify_equiv_v2.py`: `m22_max_abs_diff_int_k=0.000e+00`
over 1251 adversarial integer-k cases; the only divergence is fractional
0<k<1 (`1.497` at k=0.5), which no caller can pass — confirmed by my own read
of the call site: `peak_cost` at `tariff.py:593` computes
`k = max(1, min(int(peaks_averaged), excess.size))` **before** the only
production call at `:601`, i.e. the deleted line recomputes the identical
value on the identical array. M32 identically bit-identical (7 shapes).

Decision. All three seats and I agree the mutant is equivalent through every
reachable input. A survivor that no writable black-box test can kill is not
evidence of a suite gap, so the finding's bug/survivor classification is
refuted; the observation itself is true and measured, and its correct class is
the one D3-S4 already occupies in the register — **equivalent mutant,
hygiene** (redundant defensive hardening, dead through reachable inputs). The
provenance defect stands recorded: M22 has no `prescreen.json` record (the
finder never executed it; the quiet window, two seats and this judge did).
**stop_rule_class: hygiene.**

## 2. The kill, re-measured: D4-02 — refuted (3-of-3 + judge)

The kill's premise — *HA's stock dark theme never sets `--text-primary-color`
to `#212121`* — verified by me against `home-assistant/frontend` source, not
against any seat's note:

- **2025.2.0 era** (the card's minimum, `hacs.json`; tag `20250203.0`):
  `src/resources/ha-style.ts:24` — `--text-primary-color: #ffffff;` at html
  level. `src/resources/styles-data.ts`'s `darkStyles` (the complete variable
  set dark mode applies) contains **zero** key definitions of
  `text-primary-color` — grep for the definition form returns 0; the only
  occurrences reference it as a value. Dark mode therefore inherits `#ffffff`.
- **current dev** (Sept 2026): `src/resources/theme/color/color.globals.ts:10`
  — `--text-primary-color: #ffffff;` in the base globals.
- The **only** stock path to `#212121` is
  `src/common/dom/apply_themes_on_element.ts:79-80`
  (`rgbContrast(primaryColor, [33,33,33]) < 6 ? "#fff" : "#212121"`), which
  runs only when the user has customised the default theme's primary colour —
  and the branch is **not dark-gated**: it applies in both modes. My
  recomputation: the default picker blue `#03a9f4` measures 6.123 ≥ 6, so a
  customised-primary install gets `#212121` in light **and** dark.

My arithmetic (recomputed independently): `#212121` on `#026aa8` = 2.783 (the
finder's number is real for that pairing); `#ffffff` on `#026aa8` = **5.786,
passes AA** — which is what stock HA dark actually renders. My re-run of
`contrast_pixels.mjs` (private plan payload) reproduces both rows, including
the wi-save dark 2.783 that flows from the harness's hand-written dark table —
the table asserts a value stock HA never produces. **The kill is upheld.**

Residuals, dispositioned:

1. **Custom-primary exposure** — under a user-customised primary colour the
   pairing reaches 2.783:1 in **both** modes (not a dark-theme bug). Real,
   conditional, unmeasured prevalence. It is not the claim that was seated; I
   record it here as an unfiled candidate **low** for the next round or the
   D4 fix group, per the filing rule (a fresh seat files it with its own
   harness if it is wanted).
2. **The `.delta.dearer` rider (4.291 light / 3.972 dark)** — my arithmetic
   reproduces both against HA's stock `--error-color` `#db4437`. This number
   is premise-free and survives the kill untouched, but it was explicitly
   filed only as a rider, never as its own finding, so it dies with its host
   as a *filed* matter. Same disposition: recorded here as the strongest
   unfiled candidate low in D4; it needs a seat to file it properly.

## 3. The two criticals, re-measured live

### D11-01 — verified (critical)

`ruleset_probe.py`, fresh cache: `pull_request_rules=0` in the live ruleset
**and in all five history versions** (18→17→16 with the recorded timestamps);
`bypass_actors_always=1` (RepositoryRole 5), `bypass_applies_to_merger=1`
(authenticated identity `admin: true`); the two arms disagree on bypass by
construction, as filed. `merge_census.py` (pinned window, the documented
reproduction path): `merged_all=592, reviewed_by_non_author=0, approved_any=0,
merges_with_red_required=28, red_answered=10, disposition_rows=164` — every
line exact. My own fresh arms, live: search index `merged=602`,
`merged+review:approved=0`; REST `pulls/{n}/reviews` on an 11-PR spread sample
— every one `reviews=[]`, all authored by `tvofi`. Ten merges since baseline,
still zero approving reviews. Verified critical, bug.

### D11-02 — verified (critical)

`untrusted_text.py`, fresh cache: `seat_obey_sites=8, seat_guard_sites=0,
writer_population=public` (`shell_interpolations_freetext=0`,
`dangerous_triggers=0`). Live writer population re-read by me: public,
issues open, interaction-limits empty. The strongest sites re-read in source:
`web-triage.js:153` ("the comments carry judge verdicts, corrections and
claims that override the body") and the merge prompt's `Fix review:` comment
grammar with no authorship check. Perturbation executed by me on the tree and
reverted: one guard sentence in `COMMON.md` moves `seat_guard_sites` 0→1
(git-verified clean after restore). Verified critical, bug.

## 4. The remaining highs — harness re-run + perturbation each

- **D1-01** — `price_prior_zero.py`: `zero_priced_steps=4`, control 0, null 0,
  bins 14/24 reaching, per-bin 4–4, drop-most-favourable 52 — exact.
  `d1_own_D1-01.py` (seat 1's, deeper seams): `e2e_zero_priced_steps=4`,
  **fix arm `e2e_fixed_zero_priced_steps=0`** — perturbation fires. Verified
  high, bug.
- **D1-02** — `accuracy_wipe.py`: `fields_lost=3/3`, control 0, bool variant 3,
  `last_update_success_after=1`, zero warnings — exact. `d1_own_D1-02.py`
  through the real spawn path on a real loop: same, plus
  `spawned_task_raised_typeerror=1` and **fix arm `fixed_fields_lost=0`**.
  Verified high, bug.
- **D2-01** — `peak_topk_bracket.py`: `ratio_worst=5.0838` (reachable 12 kW),
  headline cell `cell_ratio_max=13.35` (needs the 48 h horizon — not
  options-settable, per all three seats), null flats 1.0,
  `break_excess_kw_1pc=5.84`, phantom money 49.85 SEK @6 kW / 1556.6 SEK @9 kW
  (the 3.13x catalog row is shipped-catalog reachable). `d2_own_D2-01.py`:
  the closed-form bracket-exit cross-check lands at 3.7e-16; jittered and
  partial-plateau arms hold (5.08 / 2.12). Verified high, bug, with the
  panel's reachability caveat carried on the headline.
- **D2-03** — `wood_share_jump.py`: share jumps 0.9985 across 0.002 °C at the
  curve; `d2_own_D2-03.py`: 400-cell dense sweep, `own_jump_max=0.99994`,
  analytic cross-check 3.5e-10, nulls at zero margin, one-sided direction
  confirmed. Verified high, bug.
- **D4-01** — `contrast_pixels.mjs`, private payload, real Chromium: spec
  1.014 ("Wood"), 1.794/2.393 ("Heating"/"Hot water", light), blended medians
  1.18–2.17 — all far under 4.5:1 (dark rows per the finder/seats 1.89–2.55;
  the lane metric keys on `--secondary-text-color`, whose table values are
  HA's real ones, so the D4-02 table defect does not touch it). Perturbation
  executed by me on the card source and reverted: the `font * 0.8` factor at
  `:6653`/`:6790` removed → `tiny_text_instances` **24 → 0** (plan_inline,
  375×812). The 8 px floor's `lane-*` exclusion confirmed in
  `tests/card_browser.mjs`. Verified high, bug.
- **D6-01** — `d6_own_D6-01.py`: `arch_ha_importers_static=21` = dynamic 21,
  against `docs/architecture.md:140`'s "Exactly ten" (read by me);
  `undocumented_ha_dependents=11`; module map 45 listed of 56 on disk.
  Verified high, hygiene.
- **D11-03** — `mechanism_inventory.py`, fresh cache: `mechanisms=73`,
  `controls_driven=9`, `controls_fired=9`, **`controls_inert_in_ci=1`**; no
  workflow passes `--red` (grep over `.github/workflows/`: zero hits; the
  pr-contract step at governance.yml:238 passes
  `--pr-body/--head/--title/--paths-file` only). The refusal re-driven by me
  on the corpus's own fixture with its own head SHA: **rc=1 with
  `--red 'fast (3.14)'`, rc=0 without** — and the census conformance
  (`merges_with_red_required=28`, `red_answered=10`) reproduced exactly.
  Verified high, bug.
- **D12-01** — `d12_own_01.py`: celsius null 0 misadopted / plan 4.752 kWh;
  imperial **10 slots misadopted**, indoor 21.4 → 70.5 "°C", **plan 0.0 kWh,
  95 of 96 steps zero-power**; fix arm `own_fix_imperial_slots_misadopted=1`
  (10 → 1; the residual slot is the double-read `wood_tank_top`/`dhw_inlet`
  family the seats named). Verified high, bug.
- **D3-S1** — my own in-process A/B of M06 (`grid_fee.py:106` guard →
  `if False:`): `Mar-Sep` 7→12 months, `Okt-Dec` 3→12, `Jun-Aug` 3→12,
  `Jan-Feb` 2→12; `Nov-Mar` and `Jul` unchanged — **not equivalent**, 4 of 6
  ranges become year-round. The quiet window already ran the full gate with
  M06 applied (survived, control-red subtracted), and the seats grepped the
  assertion set: the only range assertions use the wrapping case. Verified
  high (the panel's weight-5 reading; money behind it — a seasonal grid fee
  applies year-round), bug.

## 5. Mediums and lows — sample re-run + tally consistency

Re-measured by me (harness + number): D2-02 (`catalog_masks.py`: 4 rows,
`rows_writing_offpeak_factor=0`, ellevio `0/672` discounted vs 432 declared),
D5-01 (`d5_own_D5-01.py`: 65 of 200 fields without a row, 15 absent labels,
add-row perturbation arm drops 15→14), D5-02 (`d5_own_D5-02.py`: doc 48 vs
code 51, controls equal), D6-02 (`currency_unit.py`: 1 of 9 currency rows
without a unit), D7-01/02 (`sysid_plant_r4.py` exact; `HPO_D7_SLABK=100`
moves `adopted_cells` 0→9), D8-01 (`d8_own_D8-01.py`: 159 intruders, the two
zero-scoring families are exactly the two shared-prefix ones, LOO 99–159),
D8-02 (`d8_own_D8-02.py`: 4 no-icon entities, control 31-with/0-without),
D9-05 (`h9_batch_cost_loop.py` under the lock, exclusive:
`comfort_terms_calls_per_gradient=97.0197` exact, share 33.61 % within ±5 pp,
flat-null delta 0.55 pp — control holds), D9-06 (`h7_memory_gate.py`: 2.52905
/ 2.64294 exact, 51 scenarios pass a 2x, 45 never probed; plus the quiet
window's executed 2.03x injection passing the full 62-check gate), D10-01
(`qs_rules.py` plain: mismatch=1 with the two coverage rows unmeasured without
the toolchain JSONs — exactly as seat 1 documented; the committed full run and
two seats' independent coverage runs give the 3-of-54 with
`config_flow.py` 97.2 %, 21 missed vs the declared "100 %, 0 missed"),
D11-05 (`dora_keys.py`, pinned window: cfr 0.477/0.441/0.117 over 222 heads,
exact), D11-06 (live `--stats`: `blocked=4` over threshold 3, "WOULD OPEN: 1",
rc=0 under `|| true`; live `search/issues` "recurring friction" total_count=0),
D11-07 (live: last 5 releases all 0 assets; 9 distinct `uses:`, 7 mutable
tags, 2 SHA-pinned), D0-01/02 (`ftol_gap.py`: 34 of 70 priced cells above
0.01 pp, mean 0.118 %, flat null survives, LOO 0.108 %; `budget_knobs.py`:
maxiter×15 and gtol arms both gain 0 % — the cap is never binding), D4-03
(`target_size.mjs`: fine 2907 targets / 1548 undersized / 364 failing SC 2.5.8,
coarse 4/2 — exact), D3-INST (my deferred timing re-take, below).

**D3-INST's deferred number, re-taken.** Verifier 2 left the 201.2 s
standalone `golden.py` measurement to the judge on a quiet box. Under the
lock, exclusive: standalone `python3 tests/golden.py` = **160.9 s wall**
(finder: 201.2 s at load1 4.2–6.8 shared; same order); the stub invocation
`derive_closures.sh` records = **0.544 s**; `tests/closures.json` `recorded`
says **0.4 s** for both differential guards. The recorded table understates
the dearest script by ~400x (finder's shared-box ratio ~500x), nothing reads
`recorded[*].seconds` for a decision, and `tests/README.md`'s one-script list
double-charges a developer ~160 s + ~150 s for one answer. Verified low,
hygiene.

**Panel-sustained (three independent verifications, each with an executed
number; not re-measured by me):** D2-04 (COP below unity, 51 of 328 cells),
D2-05 (grid-fee decimal comma unreachable), D6-03 (headroom availability at
0.0 kW), D10-02 (0 docs-known-limitations headings), D10-03 (runtime_data Any
behind a bare ConfigEntry re-bind), D8-INST (six vacuous checks, seat 2's
strengthened count), D9-INST (four harnesses print no `thread_factor`, fifth
offender `h3_payload.py:243`; quiet-window §3 corroborates), D3-S2 (M01
survived the quiet window's full gate; seats' probes read `None` clean vs
`-312.0` mutant in the disabled-with-history state). Each dimension in which
I did not re-run a given finding still had at least one harness re-run by me
this session, listed above.

## 6. Verdict table

| id | verdict | my number | votes as counted | class | note |
|---|---|---|---|---|---|
| D0-01 | verified (low) | 34/70 cells >0.01 pp; mean 0.118 %; flat null holds | 3v | bug | ftol halts the space solve short; realised-money control still moves the wrong way |
| D0-02 | verified (low) | maxiter×15 gain 0 %; gtol gain 0 % | 3v | bug | the policed iteration budget is never binding; ftol ungated |
| D1-01 | verified (high) | 4/96 steps at 0.0 SEK/kWh; fix arm 0; null 0 | 3v | bug | non-finite shape bin prices the guessed tail free, silently |
| D1-02 | verified (high) | 3/3 fields lost; lus True; fix arm 0 | 3v | bug | one corrupt scalar wipes the accuracy store next cycle, zero log |
| D1-INST | weakened(low) | stub cycles 0; flag consumed at features.py:16284/16688; nightly real, gate-excluded | 1v/2w | hygiene | residual: base-class reaction chain unexercised by the gate suite |
| D2-01 | verified (high) | 5.08x reachable / 13.35x 48 h-horizon cell; null 1.0; closed form 3.7e-16 | 3v | bug | bracket not scaled by its own logistic temperature; headline needs unreachable horizon |
| D2-02 | verified (medium) | 0/4 rows write off-peak factor; 0/672 windows discounted | 3v | bug | every shipped DSO row's peak mask discounts nothing |
| D2-03 | verified (high) | jump 0.9985 over 0.002 degC; 400-cell max 0.99994 | 3v | bug | wood_share discontinuous where its docstring claims continuity |
| D2-04 | verified (medium) | panel-sustained (51/328 cells COP<1) | 3v | bug | Carnot/DHW factors apply after the curve's own floor |
| D2-05 | verified (low) | panel-sustained | 3v | bug | decimal-comma grid fees unparseable |
| D3-S1 | verified (high) | 4/6 ranges → 12 months; survived full gate (quiet window) | 3v | bug | non-wrapping seasonal range becomes year-round; money |
| D3-S2 | verified (low) | panel + quiet window (None vs −312.0 mutant) | 3v | bug | wrong published attribute on a disabled feature; nothing downstream acts |
| D3-S3 | weakened(hygiene) | 0.000e+00 over 1251 int-k cases; caller pre-clamps at :593 | 2w/1r | hygiene | equivalent mutant, reclassified to S4's class; provenance defect recorded |
| D3-S4 | verified (hygiene/low) | weights bit-identical, 7 shapes | 3v | hygiene | judged equivalent as filed |
| D3-INST | verified (low) | recorded 0.4 s vs real 160.9 s; stub 0.544 s | 3v | hygiene | accounting defect; README double-charges one answer |
| D4-01 | verified (high) | 1.014–2.393:1; 6.4 px; perturbation 24→0 tiny-text | 3v | bug | lane strip unreadable on phones; floor excludes lane-* |
| D4-02 | refuted | 5.786:1 stock dark (passes); 2.783 needs custom primary, both modes | 3r | — | premise false at HA source 2025.2/dev; residuals recorded in §2 |
| D4-03 | verified (low) | 20.22 px at 22.22 px; 364 failing fine, 2 coarse | 3v | bug | 24 px floor only under coarse pointer |
| D5-01 | verified (medium) | 65/200 fields rowless; 15 labels absent; arm 15→14 | 3v | hygiene | reference README does not document 15 fields |
| D5-02 | verified (low) | doc 48 vs code 51 | 3v | hygiene | stale sweep count |
| D6-01 | verified (high) | 21 modules import HA vs claimed 10 | 3v | hygiene | architecture.md stale in ten claims incl. its own boundary |
| D6-02 | verified (medium) | 1/9 currency rows without unit | 3v | bug | Euro Advisor publishes unitless currency-per-month |
| D6-03 | verified (low) | panel-sustained | 3v | hygiene | headroom precondition unenforced |
| D7-01 | verified (medium) | 0/18 adopted; slabk×100 → 9; null adopts 0.940 | 3v | bug | sysid fits one state to a two-state plant on every preset |
| D7-02 | verified (medium) | 6/18 breach; ratio 0.486–1.329; honest 0/1.000 | 3v | bug | sizer's plant leaves slab at defaults |
| D7-03 | weakened(medium) | ingest 3/4 exact; drift −2.25 % max / −0.22 % typical; fix 1.0000 | 2v/1w | bug | gate lacks the defrost condition; magnitude bounded |
| D8-01 | verified (low) | 159 intruders; 2 zero families = the 2 shared-prefix | 3v | hygiene | alphabetical ordering leaves foreign entities in spans |
| D8-02 | verified (low) | 4 no-icon; control 31/0 | 3v | hygiene | four entities missing icons.json |
| D8-INST | verified (low) | panel-sustained (6 vacuous, strengthened) | 3v | hygiene | instrument checks vacuous |
| D9-05 | verified (medium) | 97.0197 calls/grad; 33.61 % share; null 0.55 pp | 3v | bug | Python cost loop over batch rows, third of solve wall |
| D9-06 | verified (medium) | 2x passes all 51 scenarios; 2.529–2.643x to fail | 3v | bug | memory gate blind; executed 2.03x injection passed 62 checks |
| D9-INST | verified (low) | panel + quiet window (4+1 harnesses no thread_factor) | 3v | hygiene | contract telemetry gaps |
| D10-01 | verified (low) | 3/54 contradicted with coverage JSONs; 97.2 % vs declared 100 % | 3v | hygiene | register drift incl. config-flow coverage row |
| D10-02 | verified (low) | panel-sustained (0 headings/4075 lines) | 3v | hygiene | declared done, absent |
| D10-03 | verified (low) | panel-sustained | 3v | hygiene | Any in runtime_data behind 0-error strict mypy |
| D11-01 | verified (critical) | 0 pr-rules in 5 versions; 0/602 live (2 arms + REST sample); bypass→merger | 3v | bug | no review anywhere in the record; admin bypass always |
| D11-02 | verified (critical) | 8 obey / 0 guard / public; perturbation 0→1 | 3v | bug | seats obey world-writable text with merge grants |
| D11-03 | verified (high) | inert_in_ci=1; rc 1-with/0-without --red; 28 red, 10 answered | 3v | bug | the "enforced" trigger is enforced by nothing |
| D11-04 | weakened(medium) | 4 (probe) / 5 (whole-tree) live contradictions; set 16 | 2v/1w | hygiene | prose-only rot, self-repairing; detector structurally blind |
| D11-05 | verified (medium) | 44.1 % governance-red pushes; 222 heads | 3v | bug | disposition rule reddens main post-merge |
| D11-06 | verified (medium) | blocked=4 > threshold 3; opens nothing; search 0 | 3v | bug | improvement loop never acts |
| D11-07 | verified (low) | 0 assets ×5 releases; 7/9 mutable tags | 3v | hygiene | SLSA L0, no provenance |
| D12-01 | verified (high) | 10 slots misadopted; plan 0.0 kWh; fix arm 10→1 | 3v | bug | every temperature adopted as degC |

## 7. What is still open

- The two D4-02 residuals (custom-primary 2.783:1 mode-independent;
  `.delta.dearer` 4.291/3.972) are true, measured, and unfiled — a seat must
  file them properly if they are wanted (§2).
- D7-03's tank-learner magnitudes remain unmeasured by anyone.
- The register should correct the panel-phase summary line (43 findings, and
  either 110/5/2 from the JSON or 114/5/4 counting the delivered D4/D7/D8
  seat reports).
- The gate lock was released; the tree is clean (only this report is new).
