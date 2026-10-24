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

**Architecture.** `envelope_score`, `machine_score`, `operation_reason`,
`compose_scores`, `house_loss_converged`, `_refit_disagrees`,
`_watched_cop_buckets` and `restart_advice` are pure module-level functions
taking their inputs. Each score part is a `(grade, why)` pair and
`compose_scores` is the one place the rule "one code per None, none for a
grade" is written; `_scores_view` is a thirteen-line adapter that reads the
coordinator's learners into it, and `model_restart_advice(coord)` is a
six-line adapter over `restart_advice`. `_watched_cop_buckets` replaces the
two inline counts, which disagreed on `np.isfinite`. Alternatives, and why
each lost:
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
grade unclamped. The no-loss test is `loss <= 0.0`, not `<= 1e-6`:
`_effective_house_heat_loss` rounds to 1e-4 kW/K, so a house with no loss
reads exactly 0.0 and the epsilon separated nothing.

## Head

`488cbef71b0ded138cd75b0f1ea0542350a6f52b` merges the authored code head `902acfe28c6045f27e9ed4966b400050b4fd2688` and then merges origin/main `a243a79f4` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`902acfe28c6045f27e9ed4966b400050b4fd2688` is the measured code head (round 3, from `19319cc135899015bfc34e8832580665e43a3b80`).
- Merge base: `a243a79f4b97776e25063bb18a4c4c3062aa61b8`, origin/main's tip at
  2026-10-23T06:26Z (`date -u`); `git merge origin/main` was clean (no
  conflict) and left `custom_components` byte-identical to the previous head.
- Round 3 adds one commit, test-only (`tests/features.py`, two checks; no
  production line, no budget file): the two pins the round-2 review found
  missing (`## Round 2's block`). The production diff against the previous
  head is empty: `git diff --quiet 19319cc13 HEAD -- custom_components`
  exits 0, and the commit's `--stat` names `tests/features.py` alone.
- Steps 2-8 re-run at this head: features, entities, structure, archscore,
  `ci_predict`; the pin drive is not re-run (no production site was added).

## Round 2's block

- **R7, restore re-plan**: `async_restore_learned_snapshot`'s
  `await self.async_request_refresh()` mutated to
  `self.async_update_listeners()` survived features, entities and
  finite_boundary. New check `#2258: a restore asks for a cycle, and that
  cycle's advice offers no refit and grades the house on the restored scale`
  (`tests/features.py`, after the adopt arm M11): a drift coordinator with a
  refit on offer at scale 1.4, restored to the ring's 1.0; it asserts one
  refresh request, `model_restart.refit.scale is None` and `current_scale ==
  1.0` from the cycle's `_insight_view()`. The ledger draws no site for an
  awaited expression statement, so this is a features check, not a ledger
  row, and `## Unpinned sites` cannot show it.
- **R13, one view**: `"scores": self._scores_view(advice)` mutated to
  `self._scores_view({})` survived all three. New check `#2258: one cycle
  view offers the refit and grades the house against it`: ONE
  `_insight_view()` on a converged coordinator (5000 samples) whose refit
  (1.16 against 1.0, band 10 %) sits outside its band; it asserts, from that
  same view, `model_restart.refit.scale` offered, `scores.reasons.envelope ==
  "heat_loss_refit_disagrees"` and `scores.envelope is None`. The cycle path,
  not a hand-built advice.
- Mutation proof, each planted alone in a copy of this head, `tests/features.py`
  (null control: the unmutated head, same script, `ALL 4330 FEATURE CHECKS
  PASSED`):
  - R7: `FAIL #2258: a restore asks for a cycle, and that cycle's advice
    offers no refit and grades the house on the restored scale` (the only
    new-check failure);
  - R13: `FAIL #2258: one cycle view offers the refit and grades the house
    against it`.
  Both are green at the head. The checks encode a design choice: restore is
  held to the adopt path's contract (the design verdict's "both must refresh").

## Mutation proof`), `tests/structure.py`, `tools/pr/ci_predict.py`,
  `tools/audit/archscore/score.py`, and the envelope harness. Figures taken
  at an earlier commit name it.

## Mutation proof

**At this head: `tests/mutation_table.py --pin-killed --base origin/main`**
(scripts: the default drivers less `tests/entities.py`, whose baseline is red
on `origin/main` itself; see `## Red checks`). Each site the diff adds is
mutated in a temp copy and driven by every script whose recorded closure
holds its file; a site is pinned only when a driver goes red on it, and the
null mutant `coordinator.py:509 NULL_COMMENT` must survive every driver.
- Run 1 (at `65d6f349c`, after `c79cb51a3`): `PIN KILLED: 16 pinned, 5 left unpinned`; the null
  control survived every driver; baselines green (`tests/features.py`,
  `tests/env_drift.py`, `tests/structure.py`, `tests/typing_ruler.py`,
  `tests/harness_headers.py` rc=0).
- The five survivors and what this seat did:
  - `_watched_cop_buckets` CMP_BOUND (`>=` -> `>`): new check `a COP bucket
    at exactly the minimum sample count is watched, and the machine is graded`;
  - `_refit_disagrees` CMP_BOUND (`>` -> `>=`): new check `a refit exactly on
    its own band edge agrees with the scale; only one past it disagrees`
    (scale 2.0, band 25 %: 2.5 agrees, 2.51 and 1.49 disagree; the edge is
    exact in binary, so the check reads the operator, not rounding);
  - `machine_score` CLAMP_DROP: new check `a machine past the alarm threshold
    still grades 0, never below` (Cusum at twice the threshold);
  - `envelope_score` CMP_BOUND x2 on one line (`loss <= 1e-6`, `mass <= 0`):
    the mass bound was killed, the loss bound lived because the rounded loss
    is never within (0, 1e-6]; the line now reads `loss <= 0.0`, where the
    strict mutant divides by zero on the existing lossless check.
- Run 2 (at `80043426f`, after dropping the retired line's pin
  `envelope_score GUARD_OFF 0805c971`, which the ledger refused as naming no
  generated site): `PIN KILLED: 6 pinned, 0 left unpinned`, every one by
  `tests/features.py`; the null control survived; `tests/features.py` and
  `tests/env_drift.py` baselines rc=0 -- the three new checks pass on the
  fix and each fails on its mutant.

**Recorded by the previous rounds of this seat** (each mutant one
production text in its own detached worktree; the commit it ran at is named;
`c79cb51a3` later moved M5's and M17's texts into `machine_score` and
`operation_reason` unchanged, and the pin drive above re-proves every added
site at this head):

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
| M11 (adopt arm) | the adopt's `await coord.async_request_refresh()` -> `coord.async_update_listeners()` | `tests/features.py` | `#2258: an adopt asks for a cycle, and that cycle's advice offers no refit and grades the house on the adopted scale` |
| R7 | the restore's `await self.async_request_refresh()` -> `self.async_update_listeners()` | `tests/features.py` | `#2258: a restore asks for a cycle, and that cycle's advice offers no refit and grades the house on the restored scale` |
| R13 | `_insight_view`'s `self._scores_view(advice)` -> `self._scores_view({})` | `tests/features.py` | `#2258: one cycle view offers the refit and grades the house against it` |
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
  as `envelope_score GUARD_OFF 0805c971`, reproduced; that line now reads
  `loss <= 0.0`, so `f464d3dfa` dropped the row and the drive re-pinned it
  as `envelope_score GUARD_OFF 88c2835d`;
- `sensor.py:ModelRestartAdvisorSensor.native_value RETURN_DEL b9a14709`
  (`return None if scale is None else float(scale)`): the line is now the
  payload-number read `return refit if refit is not None else
  _as_float(…)`; pinned as `RETURN_DEL c79284c9`, reproduced;
- `model_restart_advice GUARD_OFF 1f3cb02f`, `GUARD_OFF b22d4a99` and
  `RETURN_DEL 8ac0f475`: the same lines, now in `restart_advice`; the first
  two reproduced, and `RETURN_DEL 8ac0f475` reproduced too (killed by `tests/features.py` at
`restart_advice`'s final `return advice`).

## Unpinned sites

none -- `tests/mutation_table.py --pin-killed --base origin/main` at the
round-2 commits pinned every site the diff adds (16, then 6: `PIN KILLED: 6
pinned, 0 left unpinned`). Round 3 adds no production line, so it adds no
site and the drive was not re-run; `tools/pr/ci_predict.py --base origin/main`
at `902acfe28` prints `CI PREDICT: no closures or fast red predicted`. R7's
line is invisible to the ledger by construction (see `## Round 2's block`).

## Null control

- The pin drive's null mutant, `coordinator.py:509 NULL_COMMENT` (a
  comment-only edit), survived every driver in both runs at this head; a
  driver that killed it would have refused the run.
- The previous rounds' unmutated head: `GATE_SCOPE=auto GOLDEN_MODE=drift
  PYTHONPATH=tests/hastub bash tests/run.sh` at `01b55d546` printed `MODE:
  SCOPED -- 29 script(s) run, 4 scoped out.`, every script in scope green
  after the advisor pin's re-anchor (`e07f41fed`), including
  `tests/stress.py`, `tests/card.mjs`, `tests/card_drift.mjs`,
  `tests/env_drift.py --all`, `tests/optimality.py` and
  `tests/typing_ruler.py`.
- The finder's instance (item 1) at the merge base: `finiteScore(null)` is
  `Number(null)` = 0 -- the base card under the head's card tests prints the
  `0/100` checks red; at the head they are green. This seat did not touch
  the card.
- Item 2's harness, `dev/audit/harnesses/r10_scores_envelope.py`, is **this
  PR's instrument, not the finder's**: the finder's harness
  (`dev/audit/rounds/round10/study-reseed/live_store.py`) needs the owner's
  bundle, which stays carried to R10-PARAMS-OWNER (`c3711a1f0`). It runs with
  `--ratio-override 1.0`): every split forced to 1.0, where the configured
  total and the model's figure are one number; it reads
  `split_max_abs_gap=0.0` at the merge base and at this head, so the base's
  gap is the split's and not a scale-only drift.

## Figures

Every figure below was taken at `902acfe28c6045f27e9ed4966b400050b4fd2688`
(or at a seat commit whose production code it shares, named) unless it names
another commit.

- `python3 tools/audit/archscore/score.py --diff origin/main` at the head:
  `Architecture score: dS +0.0105 IMPROVES` (`coord_footprint 2489 -> 2471`).
  Before `c79cb51a3`, at `f9458e55c`: `dS +0.0023 IMPROVES`
  (`coord_footprint 2489 -> 2485`); `--diff HEAD` across `c79cb51a3` alone:
  `dS +0.0081 IMPROVES` (`2485 -> 2471`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. Against
  `origin/main`'s budgets (three-dot diff of `tests/structure_budgets.json`):
  `class_excess_loc 18268 -> 18244`, `max_class_loc 8514 -> 8480`,
  `seam_cut_total 708 -> 714`. Before `c79cb51a3` the branch read
  `18282`, `8518`, `714`; `c79cb51a3` re-recorded the two that fell (-38
  each) with the reason in its commit message.
- Seam table (`tests/structure.py`'s `coordinator seam table`, rule: per
  seam, attribute references and calls crossing it), a detached
  `origin/main` at `e45fc34fb` against this branch at `f9458e55c`: `learning 281 -> 283`, `grid 158
  -> 159`, `views 106 -> 109`, the other two equal; total `708 -> 714`.
  At `c79cb51a3`'s tree, with `coordinator.model_restart_advice` re-seated to `learning` in
  `tests/seam_map.json`: `learning 286`, `views 106`, total still `714`; `c79cb51a3` itself leaves the total at `714`.
- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py`
  re-run at `f464d3dfa` (production code identical to this head; harness
  sha1 `272d51759459b3bd7410f2224763fa197565602d`): `split_max_abs_gap=0.0`;
  `ends` arm `samples=0` at scales 0.3 and 3.0 `envelope=None
  reason=heat_loss_learning`, `samples=2000` grades 79.2 and 0.0; with
  `--ratio-override 1.0`, `split_max_abs_gap=0.0`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` at the head:
  `ALL 4330 FEATURE CHECKS PASSED` (4328 at the previous head plus the two
  round-3 checks).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: `ALL 2406
  ENTITY CHECKS PASSED`.

Taken by the previous rounds of this seat, at the commits they name (none of
these inputs moved since):

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
the API at use. One row stays raised in `tests/structure_budgets.json`:
`seam_cut_total` +6 (708 -> 714). The other two rows this branch raised are
paid and now sit under `origin/main`'s: `class_excess_loc` 18268 -> 18244 and
`max_class_loc` 8514 -> 8480. What remains is the feature itself: the cycle
takes the restart advice once (`_insight_view` hands the coordinator to
`model_restart_advice`, the design's holder), so the advisor's reads of the
learner's ring, scale and accuracy now cross from the views seam, and the
envelope grade reads the learner's sample count to know whether it has
converged.

Payments tried: (1) the envelope grade moved out of the class into the pure
`envelope_score` -- taken, -15 class lines; (2) `model_restart_advice`'s
42-line body made the pure `restart_advice` behind a six-line adapter --
taken, -32 helper lines; (3) a `republish_restart_advice` helper, then an
in-place `data["insight"]` write, then a `coord.data` reassignment, each
replaced by the existing `async_request_refresh` -- taken (the in-place
write was archscore-inadmissible, the reassignment moved
`coordinator_attrs`); (4) the score composition moved into the pure
`machine_score`, `operation_reason` and `compose_scores` (`c79cb51a3`) --
taken, -38 on `class_excess_loc` and `max_class_loc`, archscore
`dS +0.0081 IMPROVES` across it, seam cut unchanged at 714; (5) re-seating
`coordinator.model_restart_advice` from `views` to `learning` in
`tests/seam_map.json` -- not taken, the total stays 714 (`learning` +5,
`views` -3), so it buys nothing and would only move the charge; (6) calling
`restart_advice` directly from `_insight_view` -- not taken, the same three
learner reads then sit in `_insight_view` itself and the adapter's argument
extraction is duplicated for `async_adopt_heat_loss_refit`; (7) carrying the
sample count inside the advice so the grade reads no learner state -- not
taken, it hides the same read inside a dict to move a metric.

Round 3 touched no production code, so no payment changed: structure reads `seam_cut_total 714 <= 714` and archscore `dS +0.0105 IMPROVES` at the head (re-taken, `date -u` 2026-10-23T06:26Z). The round-2 review hunted a payment (advice taken in the learning seam and stored) and found it trades this raise for one on `coordinator_attrs`, which sits at its cap.

Architecture score: dS +0.0105 IMPROVES

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main` at this head, re-taken after round 3 (no production line moved):
`dS +0.0105 IMPROVES`; no gate metric rises; `coord_footprint 2489 -> 2471`.

## Red checks

- `budget-raise-gate` is red until main's mandate approval at the head (the one it answers; it stays red until then): this
  branch raises one row of `tests/structure_budgets.json`
  (`seam_cut_total`). It is the gate working as designed, not a defect; the
  answer is `## Raise justification` (mandate 6175172275, scope `all`),
  which the approver judges. No cheaper detector applies.
- `mutation` was the opener's predicted red at `04ab79356`: 17 sites the
  diff added had no pin. Own defect, fixed here: `tests/mutation_table.py
  --pin-killed --base origin/main` pinned 16, three new checks and the
  `loss <= 0.0` floor made the other five killable, and a second drive
  pinned them (`## Mutation proof`); `## Unpinned sites` is empty and
  `tools/pr/ci_predict.py` predicts no red. The cheaper detector is the
  same `--pin-killed` drive run before the handoff instead of after the
  opener refuses; it costs one drive of the changed files' drivers (two runs
  here, the longer over an hour on this loaded box).
- `tests/entities.py` reads `ALL 2406 ENTITY CHECKS PASSED` at this head on
  this seat's machine. Round 2 recorded a `hb:positive_control` py-spy retry
  arm failing on another machine; that arm depends on the environment, and
  CI `fast` is the arbiter. Nothing in this diff reaches `tests/nightly_ha.py`'s
  heartbeat control.
- `nightly-status` grades main's nightly run; this diff touches nothing it
  reads. Not this branch's.
- From the previous rounds, both caught locally before any push:
  `tests/finite_boundary.py`'s `every number state publishes None, never the
  bool or the text` (fixed in `9ed756d3f`; the census itself is the cheapest
  detector) and `tests/harness_headers.py`'s `the executed harnesses leave
  their committed output byte-identical` (regenerated in `9ed756d3f`; no
  cheaper detector is wired).

## Forward-carry

- **R10-LEARNER-ETA**: `house_loss_converged(samples)` (and
  `_HOUSE_LOSS_CONVERGED_CONFIDENCE`) in `coordinator.py` is the one
  convergence predicate for the heat-loss learner: the learning view's
  `house_heat_loss_learned` and the envelope dash read it. Learner
  progress, phase and ETA for the heat-loss learner must read it, never a
  second threshold. Landed on the roster at 59c2ebc0276decf74d29b81d1895687ba0b15c00 (`handoff/audit-r10-roster`). Carry: R10-LEARNER-ETA.
- **R10-UX-HEALTH**: the score sensor is `unknown` (available) while it
  waits, with `waiting_for` and `reasons`; `healthWaiting` lists it. The
  card ships `score.reason_*` strings (en, sv) for every code; UX-HEALTH
  renders `reasons` on the Health `score` row and owns its copy. The Health
  tab's heat-loss "learned" now means converged (50 samples), not one
  sample. Landed on the roster at 524d335a0a104d4972495acd37542286541db0c2 (`handoff/audit-r10-roster`). Carry: R10-UX-HEALTH.
- **R10-SENSOR-PAYLOAD**: `OptimizationScoreSensor` has no `available`
  override any more; `ModelRestartAdvisorSensor` reads
  `insight.model_restart` through `_advice()`, falling back to the
  payload's `house_heat_loss_scale` before the first cycle. Carry: dismissed: R10-SENSOR-PAYLOAD is done; this diff makes the change itself and records it here, nothing is owed
- **R10-ARCH-DOCS**: `docs/architecture.md`'s `[target: R10-SCORES]` line
  claims "one view model behind the scores, Savings, Advisor and Health".
  Landed: one rule and one view model for the scores and the advisor's
  restart advice, and one convergence predicate shared with Health; not
  landed: no score reads or recomputes a Savings figure (SAV-BASELINE's
  figures are untouched, carry 2), and Health's own copy is UX-HEALTH's.
  Landed on the roster at 1f27f9daf4da8798c5b796513348e7d2d0ea3cbf (`handoff/audit-r10-roster`). Carry: R10-ARCH-DOCS.
- **New finding, the card's null-as-0 siblings in the Advisor rows** (the four `Number(attrs.*)` sites in Figures; R10-ADVISOR is done): the hot-water row writes `recommended_setpoint` when `Number(...)` is finite, and `Number(null)` is 0. `readNumber` is now in the card for the fix. Landed on R10-UX-HEALTH at 9a4953627ba02add3175dd80cbd3c5b4d8c87af6. Carry: R10-UX-HEALTH
- **New finding, the envelope band and mass basis (reported, not shipped, per the design note):** on the tree's own presets the 20-100 h band grades the default preset 6.2 and a post-2005 timber house 20.5 at the configured prior, and every timber house before 1980 0; the time constant reads `room_thermal_mass`, which on a floor-heated house excludes the slow mass `presets.derive` puts in `slab_thermal_mass`, and on a two-zone house is not the zone masses the dynamics use. A band or mass-basis change is a behaviour no finding names yet. Main's decision under the mandate: R10-PARAMS-OWNER, the single owner of the thermal parameters, decides which mass the score's time constant reads (the dynamics' slab-inclusive and zone masses are recommended, so the score grades the house the model simulates), and re-grades the 20-100 h band on the presets at that basis. Landed on R10-PARAMS-OWNER at 75c891e28f19142fc44f550b792c1442bff89715. Carry: R10-PARAMS-OWNER
- **Blocked, not designed around:** the owner's bundle is not in this container, so the suspected 2.6x scale drift and the band on the owner's own house are unmeasured. The harness takes `--bundle PATH` and prints the stored scale, split and samples and the grade on both bases. A local seat with the bundle runs the harness with `--bundle PATH` as part of that group. Landed on R10-PARAMS-OWNER at c3711a1f09213ef1a5c072c5e77297c2b674bac7. Carry: R10-PARAMS-OWNER

## Friction

none


