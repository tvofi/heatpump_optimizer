R10-SCORES: the owner's plan-score items 1-3 (tvofi, 2026-10-14) and
ARCH2-s5-C3's reading rule, on the approved design (`design/r10-scores`,
`Design review: approve f01e06d24`). Part of #2238 and part of #2258: the
roster's `fixes` is empty for this group, so neither closes here; the
orchestrator verifies each after the merge.

What the owner reported, and what answers it:

- **Item 1: the heat-pump score reads 0 with too little COP data.** The
  coordinator already published `machine: None`; the card's `finiteScore`
  read it through `Number(null)`, which is 0, and printed `0/100` in the
  hover and the breakdown. The card now reads every score through C3's
  `readNumber` (ported verbatim from `3930b421a`), and a null renders as
  "—" and the reason the coordinator names. **One rule for every score:**
  `Scores` gains `reasons`, exactly one code per score that is `None`
  (`no_house_model`, `heat_loss_learning`, `heat_loss_refit_disagrees`,
  `cop_watch_learning`, `no_scored_day`, `free_price_reset`,
  `first_scored_day`), and none for a score with a value.
- **Item 2: the house score reads 0 on an averagely insulated house.** The
  grade is now a pure `envelope_score(params, samples, advice)`:
  - its loss is `_effective_house_heat_loss` -- both zones with the learned
    lower-floor split, the figure the Health tab publishes as
    `heat_loss_w_per_k` -- not `heat_loss_coefficient x scale` (the
    RATIO-SITES carry);
  - it is a dash (`heat_loss_learning`) until the heat-loss learner has
    converged: `house_loss_converged(samples)`, one EWMA time constant
    (`round(1 / HOUSE_LOSS_ALPHA)` = 50 samples, confidence about
    `1 - 1/e`), derived from the learner's own constant. The learning
    view's `house_heat_loss_learned` -- the Health tab's "learned" --
    reads the same predicate, so the two cannot disagree;
  - it is a dash (`heat_loss_refit_disagrees`) while the drift advisor's
    refit sits outside its own `band_percent` of the learned scale;
  - precedence is one chain: `no_house_model` > `heat_loss_learning` >
    `heat_loss_refit_disagrees`.
  The 20-100 h band is unchanged; see the new finding under Forward-carry.
- **Item 3: one message everywhere.** The advice is taken once a cycle in
  `_insight_view` and published as `insight.model_restart`; the advisor
  sensor republishes it (zero recomputations per state write, from two)
  and the envelope grade reads the same take. The adopt and restore
  services now `async_request_refresh()` -- the tree's existing mechanism --
  so the next cycle re-plans on the moved scale and re-takes the advice,
  instead of notifying listeners over a payload that no longer matches it.
  A card census walks every score input (a grade, or null with each code)
  through the headline, the hover and the breakdown and requires one
  number or one reason; a backend sweep requires `ModelStatusSensor`'s
  `learned` and the score's `heat_loss_learning` to be one predicate.

**Availability (the design verdict's carry).** `OptimizationScoreSensor`
drops its `available` override: with no overall grade its state is
`unknown`, not `unavailable`. This departs from `_WaitsForEvidenceMixin`'s
rule (sensor.py), which makes a waiting sensor unavailable because Home
Assistant renders `unknown` like a thrown integration. The departure is
deliberate: Home Assistant drops an unavailable entity's attributes, and
this sensor's `reasons` are the answer the owner asked for in exactly the
no-evidence state. `waiting_for` -- now the coordinator's
`reasons["overall"]`, never a code spelled in the sensor -- says "not
measured yet" in the attributes, which answers the mixin's concern; the
card already reads `unknown` + `waiting_for` as waiting (`advisorRow`). The
Health tab's comment above `HEALTH_WAITING` is rewritten and its filter
(`healthWaiting`) admits an `unknown` sensor that names what it waits for,
so the score row stays listed.

**Architecture.** `envelope_score`, `house_loss_converged`,
`_refit_disagrees`, `_watched_cop_buckets` and `restart_advice` are pure
module-level functions taking their inputs; `model_restart_advice(coord)`
is now a six-line adapter over `restart_advice`. `_watched_cop_buckets`
replaces the two inline counts, which disagreed on `np.isfinite`.
Alternatives, and why each lost:
- a new `scores.py` module: rejected in the design (a new tracked file and
  churn outside the seam while R10-LIVESTATE follows on `coordinator.py`);
- keeping the configured coefficient and adding only a confidence dash:
  leaves the measured two-zone inflation;
- dashing on `_snapshot_ring.alarmed` directly: it fires on solar, COP and
  sensor causes the refit does not attribute to UA;
- re-publishing `data["insight"]` in place after adopt/restore (round 1 of
  this seat): `archscore` read `shared_inplace_writes 17->18` (WORSENS);
  assigning a new `coord.data` instead moved `coordinator_attrs`; the
  existing `async_request_refresh` moves neither and also re-plans.

The `max(scale, 0.1)` floor stays: the learner's writers
(`_apply_house_heat_loss_scale`, the snapshot restore) clamp to
`[HOUSE_HEAT_LOSS_SCALE_MIN, _MAX]`, but `ThermalParameters` does not clamp
the field on construction (`clamp()` covers the masses, `inter_zone_transfer`
and `window_area`), so a configured or service-written value reaches the
grade unclamped.

## Head

`9b6423818873f3eb888bb6c22568e1cac311b663` is the measured code head.
- Cut from `origin/main` `86425b9ad` (the dispatch base). `origin/main` was
  merged in twice before the handoff: `de69745ff` (merge `01b55d546`,
  bringing R10-SOLVER #2612; the ledger driver resolved
  `tests/structure_budgets.json`) and `fc7173fe7` (merge `d88061f89`; it
  touches `tests/entities.py` and `tests/closures.json` here, both merged
  without conflict, `closures.json` by its ledger driver).
- Merge base: `fc7173fe7876e9973a170675d25337a810a40c59`, origin/main's tip
  at 2026-10-22T23:52Z (`date -u`).
- Where a figure was taken at an earlier commit of this branch it names it;
  steps 2-8 were re-run after each merge where the merge reached them:
  `tests/entities.py` (`ALL 2399 ENTITY CHECKS PASSED` at `d88061f89`),
  `tests/structure.py` and `tests/closure.py selftest` and
  `tools/pr/ci_predict.py` at `d88061f89`, and `tests/features.py` at
  `9b6423818` (the M0 null run below). Neither merge touched the card,
  `coordinator.py`, `sensor.py`, `payload.py` or `tests/features.py`'s
  score blocks.

## Mutation proof

Each mutant replaces one production text, exactly one occurrence, in its own
detached worktree at `38d7452b8` (M1-M13), `ad0df8395` (M14, M15) or
`9b6423818` (M16, M17) (`git worktree add --detach`), driven by a scratch
driver that is not committed (worktree, replace, run the script, collect its
`FAIL` lines). A named check is one that went red; the unmutated head is green on
the same scripts (`## Null control`).

| mutant | production text replaced | script | red checks |
|---|---|---|---|
| M1 | `readNumber`'s null/undefined/"" return deleted | `node tests/card.mjs` | `a heat pump with no COP evidence is never 0/100 in the hover`; `nor in the breakdown: a dash and the reason the coordinator named`; `score input envelope=no_house_model …` and the other five null-input walk rows (8 checks) |
| M2 | `loss = _effective_house_heat_loss(params, scale)` -> `params.heat_loss_coefficient * scale` | `tests/features.py` | `#2258: a two-zone house is graded on the Health tab's heat loss, learned split included` |
| M3 | `house_loss_converged`'s `>=` -> `>` | `tests/features.py` | `#2258: the grade dashes exactly while the Health tab reads the learner as learning`; `#2258: converged is one EWMA time constant, 1/alpha samples, from the prior` |
| M4 | `_refit_disagrees`'s `>` -> `<` | `tests/features.py` | `#2258: a converged learner the refit disagrees with is dashed, not graded`; `#2258: a refit inside its own band does not dash the grade` |
| M5 | `reasons["machine"] = "cop_watch_learning"` -> `pass` (the invariant) | `tests/features.py` | `a fresh install grades nothing, and says why for each part (#2258)` and four more `#2258` checks, then a `KeyError` |
| M6 | `np.isfinite(entry[1]) and` dropped from `_watched_cop_buckets` | `tests/features.py` | `a non-finite aperture n does not wedge _learning_view` (`ValueError: cannot convert float NaN to integer`) |
| M7 | the `heat_loss_learning` and `heat_loss_refit_disagrees` arms swapped (precedence) | `tests/features.py` | `#2258: an unconverged learner with a refit outside the band reads learning alone` |
| M8 | the `available` override restored (`overall is not None`) | `tests/entities.py` | `the score sensor reads unknown, not unavailable, before any grade has evidence: its reasons stay readable (#2258)`; `the optimization score is unknown, still available, before any sub-score has evidence (#1335, #2258)` |
| M9 | `house_heat_loss_learned` back to `samples > 0` | `tests/features.py` | `#2258: the grade dashes exactly while the Health tab reads the learner as learning`; `#2258: Health's learned and the score's heat_loss_learning are one predicate, …` |
| M10 | `"model_restart": advice` dropped from `_insight_view` (the holder) | `tests/features.py` | `#1936: the advisor sensor reads the recommended scale and both options`; `#1936: with no alarm the sensor reads the scale in use (nothing to change)` |
| M11 | the adopt's `await coord.async_request_refresh()` -> `coord.async_update_listeners()` | `tests/features.py` | `#2258: an adopt asks for a cycle, and that cycle's advice offers no refit and grades the house on the adopted scale` |
| M12 | `healthWaiting` back to `state === "unavailable"` | `node tests/card.mjs` | `still learning lists unavailable waiting sensors with a reason in words` |
| M14 | `envelope_score`'s `max(params.house_heat_loss_scale, 0.1)` floor dropped | `tests/features.py` | `#2258: a configured scale under the learner's clamp is floored at 0.1, not read as a house with no loss` |
| M15 | the band's `np.clip(…, 0.0, 1.0)` dropped | `tests/features.py` | `#2258: a house past 100 hours grades 100, not more`; `#2258: a house under 20 hours grades 0, not less` (and the floor check) |
| M16 | `params.room_thermal_mass <= 0` -> `< 0` | `tests/features.py` | `#2258: a converged learner on a massless house, or one at the loss floor, has no house model -- not a grade of 0` |
| M17 | `free >= SCORE_FREE_SPAN_RESET` -> `>` | `tests/features.py` | `#2258: after a free-price reset the operation part says so` |
| M13 | `waiting_for` spelled `"first_scored_day"` in the sensor | `tests/features.py` | none -- **survives, equivalent**: `reasons["overall"]` has exactly one code (`_scores_view` writes only `first_scored_day`), so the spelled code and the read one agree in every reachable state; the read stands because a second overall code would otherwise be silently mis-named |

Failing tests first: the head's `tests/card.mjs`, `tests/features.py` and
`tests/entities.py` run against the merge base's production files
(a worktree at `86425b9ad` with the three test files of `38d7452b8` copied
in): `node tests/card.mjs` prints `12 CARD CHECK(S) FAILED`
(including `a heat pump with no COP evidence is never 0/100 in the hover`);
`tests/features.py` fails `#2258: before a cycle publishes the advice the
sensor reads the scale in use, no refit` and stops at `KeyError:
'model_restart'`.

Moved mutation pins, re-anchored to the scopes their lines moved into, and
re-verified with `tests/mutation_table.py --anchor <anchor> --scripts
tests/features.py` (each `PIN RE-VERIFICATION: 1 reproduced`, null control
`NULL_COMMENT` survived):
- `_scores_view BOOLOP 4902d2e0` (`if loss > 1e-6 and …`): the guard is now
  `envelope_score`'s `if loss <= 1e-6 or params.room_thermal_mass <= 0:`,
  where the inventory generates a GUARD_OFF site and no BOOLOP site; pinned
  as `envelope_score GUARD_OFF 0805c971`, reproduced;
- `sensor.py:ModelRestartAdvisorSensor.native_value RETURN_DEL b9a14709`
  (`return None if scale is None else float(scale)`): the line is now the
  payload-number read `return refit if refit is not None else
  _as_float(…)`; pinned as `RETURN_DEL c79284c9`, reproduced;
- `model_restart_advice GUARD_OFF 1f3cb02f`, `GUARD_OFF b22d4a99` and
  `RETURN_DEL 8ac0f475`: the same lines, now in `restart_advice`; the first
  two reproduced, and `RETURN_DEL 8ac0f475` reproduced too (killed by `tests/features.py` at
`restart_advice`'s final `return advice`).

## Unpinned sites

Each line is a site `tools/pr/ci_predict.py --base origin/main` lists as
added and unpinned at `d88061f89`, with its disposition. "Pinned by
`mutation-autofix`" names the check this branch shows killing it.
- `coordinator.py` `house_loss_converged` CMP_BOUND (`>=`): pinned by `mutation-autofix` (M3).
- `coordinator.py` `house_loss_converged` RETURN_DEL: pinned by `mutation-autofix` (the convergence sweep reads `None` as unconverged everywhere and fails at 50 samples).
- `coordinator.py` `_refit_disagrees` GUARD_OFF `if fitted is None:`: pinned by `mutation-autofix` (`float(None)` raises on the fresh-install view, whose advice has no refit).
- `coordinator.py` `_refit_disagrees` CMP_BOUND: written triage, **equivalent** -- `>` against `>=` differ only when the refit sits exactly `band x scale` from the scale; no check pins that edge and none should, since the band itself is a measured ±7-10 %.
- `coordinator.py` `_refit_disagrees` RETURN_DEL: pinned by `mutation-autofix` (M4's checks read the `None` return as "agrees").
- `coordinator.py` `envelope_score` CLAMP_DROP (the 0.1 floor): pinned by `mutation-autofix` (M14).
- `coordinator.py` `envelope_score` CMP_BOUND x2 (`loss <= 1e-6`, `mass <= 0`): the mass bound is pinned by `mutation-autofix` (M16); the loss bound is written triage, **equivalent** -- `_effective_house_heat_loss` rounds to 1e-4 kW/K, so the loss is never exactly 1e-6.
- `coordinator.py` `envelope_score` GUARD_OFF `if not house_loss_converged`: pinned by `mutation-autofix` (the convergence sweep).
- `coordinator.py` `envelope_score` GUARD_OFF `if _refit_disagrees`: pinned by `mutation-autofix` (`a converged learner the refit disagrees with is dashed`).
- `coordinator.py` `envelope_score` CLAMP_DROP and RETURN_DEL on the band's return: pinned by `mutation-autofix` (M15; a deleted return unpacks `None`).
- `coordinator.py` `_scores_view` GUARD_OFF `if why is not None` / `if _watched_cop_buckets` / `if operation is None` / `if not available`: pinned by `mutation-autofix` (the fresh-install reasons check and the invariant census).
- `coordinator.py` `_scores_view` CMP_BOUND `free >= SCORE_FREE_SPAN_RESET`: pinned by `mutation-autofix` (M17).
- `sensor.py` `ModelRestartAdvisorSensor._advice` GUARD_OFF `if advice:`: pinned by `mutation-autofix` (`#1936: the advisor sensor reads the recommended scale and both options` reads the fallback's no-refit state).

## Null control

- The unmutated head: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`
  at `01b55d546` printed `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`
  and failed one script, `tests/entities.py`, on the mutation ledger's
  refusal of the advisor sensor's moved pin; that pin was re-anchored in
  `e07f41fed` and `tests/entities.py` reads `ALL 2397 ENTITY CHECKS PASSED`
  there and `ALL 2399` at `d88061f89`. Every other script in scope passed,
  including `tests/stress.py`, `tests/card.mjs`, `tests/card_drift.mjs`,
  `tests/env_drift.py --all`, `tests/optimality.py` and
  `tests/typing_ruler.py`. The M0 null mutant (a comment-only edit) at
  `9b6423818`: `tests/features.py` rc=0.
- The finder's instance (item 1) at the merge base: `finiteScore(null)` is
  `Number(null)` = 0 -- the base card under the head's card tests prints the
  `0/100` checks red (above); at the head they are green.
- Item 2's harness, `dev/audit/harnesses/r10_scores_envelope.py`
  (`--ratio-override 1.0`): every split forced to 1.0, where the configured
  total and the model's figure are one number; it reads
  `split_max_abs_gap=0.0` at the merge base and at the head, so the base's
  gap is the split's and not a scale-only drift.

## Figures

Every figure below was taken at FIG_`9b6423818873f3eb888bb6c22568e1cac311b663` is the measured code head.
- Cut from `origin/main` `86425b9ad` (the dispatch base). `origin/main` was
  merged in twice before the handoff: `de69745ff` (merge `01b55d546`,
  bringing R10-SOLVER #2612; the ledger driver resolved
  `tests/structure_budgets.json`) and `fc7173fe7` (merge `d88061f89`; it
  touches `tests/entities.py` and `tests/closures.json` here, both merged
  without conflict, `closures.json` by its ledger driver).
- Merge base: `fc7173fe7876e9973a170675d25337a810a40c59`, origin/main's tip
  at 2026-10-22T23:52Z (`date -u`).
- Where a figure was taken at an earlier commit of this branch it names it;
  steps 2-8 were re-run after each merge where the merge reached them:
  `tests/entities.py` (`ALL 2399 ENTITY CHECKS PASSED` at `d88061f89`),
  `tests/structure.py` and `tests/closure.py selftest` and
  `tools/pr/ci_predict.py` at `d88061f89`, and `tests/features.py` at
  `9b6423818` (the M0 null run below). Neither merge touched the card,
  `coordinator.py`, `sensor.py`, `payload.py` or `tests/features.py`'s
  score blocks. unless it names another commit.

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py`
  (rule: |published envelope − the 20-100 h grade of
  `room_thermal_mass / house_heat_loss_effective`| over a two-zone preset at
  splits {0.5, 0.8, 1.0, 1.25, 2.0} x scales {1.0, 2.6}, converged learner,
  no alarm): `split_max_abs_gap=10.5` at the merge base `86425b9ad` (split
  0.5, scale 1.0: envelope 6.2 against Health's 16.7), `0.0` at the head.
  Null control: `--ratio-override 1.0`, `0.0` at both.
- Same harness, `ends` arm (the learner at both ends of its input range):
  zero samples reads `envelope=None reason=heat_loss_learning` at the clamp
  floor (0.3) and ceiling (3.0); 2000 samples grades 79.2 and 0.0. At the
  merge base zero samples graded 79.2 and 0.0 -- the prior presented as the
  house.
- Same harness, `band` arm (rule: each `presets.derive` structure x era at
  140 m², time constant `house_thermal_mass / house_heat_loss_coefficient`
  and its 20-100 h grade; identical at both ends): the default preset
  (`timber_slab`, `1980_2005`) is 25.0 h, grade 6.2; `timber_slab`
  `post_2005` is 36.4 h, grade 20.5; every timber `pre_1960` and
  `1960_1980` preset grades 0.0. A drift of the scale to 2.6 grades 0 on
  every split of the default preset (split arm).
- `python3 tools/audit/archscore/score.py --diff origin/main`:
  `Architecture score: dS +0.0023 IMPROVES` (`coord_footprint 2489 -> 2485`), at `e07f41fed` against `de69745ff`.
- `python3 tests/structure.py`: before the re-record,
  `class_excess_loc 18286 > 18272 (+14)`, `max_class_loc 8518 > 8514 (+4)`,
  `seam_cut_total 714 > 708 (+6)` (at `eb90c6de6`); re-recorded in
  `8495a8d51` with the reason in its commit message; after merging
  `origin/main` the ledger driver resolved `class_excess_loc` to 18282 and
  the ratchet reads `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main`
  (at `eb90c6de6`, against `86425b9ad`):
  exactly the five `coord_*` fixtures move, 5 leaves each
  (`insight.model_restart` added, `insight.scores.envelope` 58.3 -> null,
  `insight.scores.reasons` added, and the same two on the score sensor's
  attributes); claimed in `tests/golden/claimed_drift.txt`. The committed
  files were patched in exactly the 17 structural paths `STALE` named, from
  a head recording (`tests/golden.py --record --only coord_` in a scratch
  worktree); the re-run reads `NO UNCLAIMED DRIFT: 56 scenario(s)` and
  `NO STALE FIXTURE: 56 committed fixture(s)`.
- `node tests/card_drift.mjs origin/main`: one state moves, `score_open`
  (the "Driving" row and hover segment gain the leading dash); the other 39
  identical; claimed in `tests/golden/card_claimed_drift.txt`.
- Class census, null read as 0 in the card (rule:
  `grep -nE 'Number\([A-Za-z_.]*attr[A-Za-z_]*(\.[A-Za-z_]+|\[[^]]+\])\)' custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`,
  plus `finiteScore\(attrs` at the base). At the base: 3 `finiteScore`
  sites (closed here: `readNumber`) and 4 `Number(attrs.*)` sites; at the
  head the 4 remain, each dispositioned under Forward-carry (R10-ADVISOR's
  seam, a distinct finding): `restartRows`' `Number(attrs.current_scale)`,
  the hot-water row's `Number(attrs.current_setpoint)` and
  `Number(attrs.recommended_setpoint)`, the valve row's
  `Number(attrs.configured_target)`. The last three can turn a null into
  0 °C, and `recommended_setpoint` is what the hot-water row writes.
- Class census, UA without the learned split (rule:
  `grep -rnE "heat_loss_coefficient\s*\*|\*\s*[a-z_.]*house_heat_loss_scale" custom_components/heatpump_optimizer/*.py`):
  the envelope grade's site is gone; the remaining house-loss sites are
  `battery.py` (single-zone branch), `optimizer.py` (single-zone `else`),
  `sysid.py` `_held_state` (guarded by `two_zone_enabled`),
  `coordinator.py` `_space_demand_kw` (learned split, RATIO-SITES),
  `sysid.py` `HousePlant.of_params` (out of scope, refuted D2-s3-73); the
  tank and mixing-valve matches are not house loss.
- Advice recomputation: `ModelRestartAdvisorSensor` called
  `model_restart_advice` twice per state write; at the head it calls it 0
  times per write and the cycle once (`#2258: one advice per cycle, none
  per advisor-sensor write`, counted by patching the module function).

## Raise justification

Mandate 6175172275 (#201, scope `all`, until 2026-10-28T18:14Z), read from
`dev/programme/HANDOVER.md`; the approver reads it and any revocation from
the API at use. Rows raised in `tests/structure_budgets.json`:
`class_excess_loc` +14 (now 18282 after main's -4), `max_class_loc` +4,
`seam_cut_total` +6. What remains is the feature itself: `_insight_view`
hands the coordinator to `model_restart_advice` once a cycle (the design's
holder), which makes that adapter a charged helper (+10) and reads
learning-owned state from the views seam; the class keeps four lines of
`reasons`.

Payments tried: (1) the envelope grade moved out of the class into the pure
`envelope_score` -- taken, -15 class lines; (2) `model_restart_advice`'s
42-line body made the pure `restart_advice` behind a six-line adapter --
taken, -32 helper lines; (3) a `republish_restart_advice` helper, then an
in-place `data["insight"]` write, then a `coord.data` reassignment, each
replaced by the existing `async_request_refresh` -- taken (the in-place
write was archscore-inadmissible, the reassignment moved
`coordinator_attrs`); (4) reformatting the machine grade's twelve-line
expression -- not taken, it moves lines without improving code; (5) calling
`restart_advice` directly from `_insight_view` to avoid charging the
adapter -- not taken, it duplicates the adapter's argument extraction.

Architecture score: dS +0.0023 IMPROVES

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main`: no gate metric
rises; `coord_footprint 2489 -> 2485`.

## Red checks

- `budget-raise-gate` is red until an approving review at the head: this
  branch raises three rows of `tests/structure_budgets.json`
  (`class_excess_loc`, `max_class_loc`, `seam_cut_total`). It is the gate
  working as designed, not a defect; the answer is `## Raise justification`
  (mandate 6175172275, scope `all`), which the approver judges. No cheaper
  detector applies.
Two scripts went red on this branch's own first gate (at `8495a8d51`,
against the moved `de69745ff`), both caught locally before any push:
- `tests/finite_boundary.py`, `every number state publishes None, never the
  bool or the text, from a bool or text payload (#2242)`:
  `ModelRestartAdvisorSensor.native_value` cast a text advice leaf with
  `float()`. Fixed in `9ed756d3f` (the payload-number read). The cheaper
  detector is the census itself, which ran here; no cheaper one exists.
- `tests/harness_headers.py`, `the executed harnesses leave their committed
  output byte-identical`: the README's score row no longer says
  "Unavailable", so `dev/audit/rounds/round4/D6/claims.py` counts 20 notes,
  not 21; its output is regenerated in `9ed756d3f`. The cheaper detector is
  running that generator with any README edit; none is wired, and the gate
  caught it.
- `tests/stress.py`'s production-call check read 1.192x on `summer/2z/space`
  against `de69745ff` before this branch had merged it (thermal_model.py
  +13956 calls, R10-SOLVER's code); after the merge it passed. Not this
  diff's: a branch-vs-moved-main comparison.

## Forward-carry

- **R10-LEARNER-ETA**: `house_loss_converged(samples)` (and
  `_HOUSE_LOSS_CONVERGED_CONFIDENCE`) in `coordinator.py` is the one
  convergence predicate for the heat-loss learner: the learning view's
  `house_heat_loss_learned` and the envelope dash read it. Learner
  progress, phase and ETA for the heat-loss learner must read it, never a
  second threshold. Carry: R10-LEARNER-ETA.
- **R10-UX-HEALTH**: the score sensor is `unknown` (available) while it
  waits, with `waiting_for` and `reasons`; `healthWaiting` lists it. The
  card ships `score.reason_*` strings (en, sv) for every code; UX-HEALTH
  renders `reasons` on the Health `score` row and owns its copy. The Health
  tab's heat-loss "learned" now means converged (50 samples), not one
  sample. Carry: R10-UX-HEALTH.
- **R10-SENSOR-PAYLOAD**: `OptimizationScoreSensor` has no `available`
  override any more; `ModelRestartAdvisorSensor` reads
  `insight.model_restart` through `_advice()`, falling back to the
  payload's `house_heat_loss_scale` before the first cycle. Carry:
  R10-SENSOR-PAYLOAD.
- **R10-ARCH-DOCS**: `docs/architecture.md`'s `[target: R10-SCORES]` line
  claims "one view model behind the scores, Savings, Advisor and Health".
  Landed: one rule and one view model for the scores and the advisor's
  restart advice, and one convergence predicate shared with Health; not
  landed: no score reads or recomputes a Savings figure (SAV-BASELINE's
  figures are untouched, carry 2), and Health's own copy is UX-HEALTH's.
  Carry: R10-ARCH-DOCS.
- **New finding, the card's null-as-0 siblings in the Advisor rows** (the
  four `Number(attrs.*)` sites in Figures; R10-ADVISOR is done): the
  hot-water row writes `recommended_setpoint` when `Number(...)` is finite,
  and `Number(null)` is 0. `readNumber` is now in the card for the fix.
  Carry: orchestrator (R10-ADVISOR's seam; next card group R10-UX-HEALTH).
- **New finding, the envelope band and mass basis (reported, not shipped,
  per the design note):** on the tree's own presets the 20-100 h band
  grades the default preset 6.2 and a post-2005 timber house 20.5 at the
  configured prior, and every timber house before 1980 0; the time
  constant reads `room_thermal_mass`, which on a floor-heated house
  excludes the slow mass `presets.derive` puts in `slab_thermal_mass`, and
  on a two-zone house is not the zone masses the dynamics use. A band or
  mass-basis change is a behaviour no finding names yet. Carry:
  orchestrator (owner decision).
- **Blocked, not designed around:** the owner's bundle is not in this
  container, so the suspected 2.6x scale drift and the band on the owner's
  own house are unmeasured. The harness takes `--bundle PATH` and prints
  the stored scale, split and samples and the grade on both bases. Carry:
  orchestrator (a seat with the bundle).

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01LDiRr7xuyKtzhvXAeBMKfY
