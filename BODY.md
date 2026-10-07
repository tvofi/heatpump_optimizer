R9-UX-7 (lane UX, model status and diagnostics), part of #201; the lane's feature issue is #1795, which stays open for its other groups.

**Stacked base.** This head is built on R9-EG-B11's handoff head `d81907ad` (PR #2025, approved, not yet merged; it carries `origin/main` `8d7903e6`). Until #2025 merges, every three-dot comparison here is against `d81907ad`, not `origin/main`. Once #2025 merges, this branch takes `origin/main` by merge (never rebase), and the figures below get re-measured. R9-UX-5 (#2010), another after-edge, is also not merged; this branch does not touch its functions (see Overlap).

What it adds, per DESIGN-UX.md section UX-7:

1. **Learning Model Status** (`sensor.py`, `ModelStatusSensor`). It reads the learning view the coordinator already publishes. The state is an ENUM: `learning`, `learned` (the heat-loss learner has evidence) or `attention` (the COP health alarm). The attributes have one compact row per learner, and the recorder keeps them: heat loss in W/K with scale, samples and learned; lower floor; solar aperture with the learner's own `SOLAR_APERTURE_MIN_SAMPLES`; tank cooling (only on a plant with hot water); COP. The hourly internal gains, the capacity envelope and system identification are `_unrecorded_attributes`. It adds no coordinator line.
2. **Indoor Temperature (Predicted)** (`PredictedIndoorTempSensor`). A recorded `MEASUREMENT` of the plan's next-interval room prediction. A module-level `coordinator.predicted_next_room_temp(coord)` calls the existing `_predicted_next_room_temp`, so the sensor reports exactly the figure the accuracy tracker files. It is unavailable while no plan governs the room, and `waiting_for` says why: `first_plan` or `plan_not_in_control`.
3. **Diagnostics** (`diagnostics.py`). The download now also carries `last_diagnosis`, `inputs` (the input watchdog's published keys), `plan` (counts and totals, no per-step series) and `learning` (the published `LearningView` keys). Every `person.*` and `calendar.*` entity id is redacted at any depth, including inside message strings and inside main's opt-in debug bundle. The token, the name and coarsened location are unchanged.
4. **Card, Health tab: "What the model has learned"**. One row per learner shows its value, its evidence in words and an evidence bar. Heat loss is compared with the settings' estimate. Solar shows "Learning: n of about N samples". Lower floor appears once learned, the tank only with a tank. A COP alarm shows in the warn tone. A 24-bar internal-gains strip in the accent colour names its peak hour.

New entities: README 81 entities / 62 sensors (`docs/architecture.md`, `docs/configuration.md` alike), and the `tests/entities.py` rosters (Diagnostic, published attributes, count). The names follow the family rule: `learning_model_status` sorts in the `learning` run (en "Learning Model Status", sv "Inlärning modellstatus"), and `indoor_temperature_predicted` in the `indoor` run (en "Indoor Temperature (Predicted)", sv "Inomhustemperatur (prognos)").

Alternatives considered for (2): (a) publish a new `predicted_next_room_temp` payload key from `_learning_view`, rejected because it adds a key to the five `tests/golden/coord_*.json` payload goldens that capture the learning view, which this brief keeps byte-identical; (b) re-derive the prediction in `sensor.py` from the published `space_plan.forecast`, `mode` and the interval, rejected because it is a second copy of the coordinator's selection and boost gate that can drift from what is scored. The module function reads the one rule.

Budgets: no raise. `max_class_loc` went down by 4. That is the `_learning_view` comment saying the heat-loss figure can be "~2x wrong after an options edit": `_thermal_learning_payload` records that defect as resolved by `_reanchor_house_heat_loss_scale` (#110), so the comment was false and is deleted (fixer step 9). It was re-recorded at the stacked base, and after the merge of `d81907ad` the ledger driver's value is what the merged tree measures.

Overlap with parallel work on the same base: `sensor.py`, `strings.json`, `translations/{en,sv}.json`, `icons.json`, the card JS, `tests/card.mjs`, `tests/entities.py`, `README.md`, `docs/dashboard-card.md`, `docs/architecture.md`, `docs/configuration.md` (entity counts), `tests/golden/card_claimed_drift.txt` and `dev/audit/rounds/round4/D6/claims.{json,md}` (the counts). UX-5 (#2010) and UX-6 also touch most of these, in different functions and hunks. The entity counts, the claim list and the D6 output will conflict mechanically with any sibling that adds entities or card CSS, and get re-derived after that merge.

## Head

`226e6fc241a7fd0d62f037fddd1e7d949ca63e18`, on base `d81907ad872378051cab14f0145487eb1cdd47a4` (R9-EG-B11 handoff head).

## Mutation proof

These production lines were deleted at the head, in a detached worktree, and `PYTHONPATH=tests/hastub python tests/entities.py` was run: `diagnostics.py`'s `_without_private_ids(` wrapper, `ModelStatusSensor`'s COP-alarm guard (`if ... alarm: return "attention"`), and `predicted_next_room_temp`'s `return predict() ...` (replaced with `return None`). The run printed `6 of 2227 ENTITY CHECKS FAILED`:
- `UX-7: the status is learned, still learning, or needs attention on a COP alarm`
- `UX-7: the predicted indoor temperature is the plan's next-interval prediction, recorded`
- `UX-7: waiting_for names why: no plan yet, or a plan that does not run the room`
- `every entity is available against a payload that satisfies every gate`
- `UX-7: no person or calendar id leaves the instance, from the entry or an input problem`
- `UX-7: the over-redaction control -- an ordinary sensor id survives beside them`

The same file, unmutated, printed `ALL 2227 ENTITY CHECKS PASSED` at `6931952` and `ALL 2231 ENTITY CHECKS PASSED` at the head (the merge brought main's checks). This mutation run was taken before the merge of `d81907ad` and is owed again at the post-#2025 head.

## Null control

The failing tests ran at the tests-only commit `f36d466a`, on the stacked base with no implementation. `entities.py` printed `19 of 2226 ENTITY CHECKS FAILED`: every UX-7 check, the Diagnostic roster, the attribute roster and surface, and the sensor count; the diagnostics block's leak check listed `person.anna_lindqvist` and `calendar.familjen_lindqvist` leaked. `node tests/card.mjs` printed `10 CARD CHECK(S) FAILED`, all of them UX-7 checks. The three absence checks (no sensor, unavailable sensor, no tank or profile) pass at the base by construction, and they are the controls for the presence checks.

The card drift's null control: the four new CSS rules were deleted and `node tests/card_drift.mjs` was run; it printed `card_drift: identical in all 40 states`. So the 39 claimed states move by the stylesheet alone.

## Figures

Every command below ran at the head or at the commit named, on Darwin with the seat venv (`tools/audit/seat/seat_venv.sh`). These are local results. CI's check-runs at the pushed head are the authority.
- `python3 tests/closure.py select --diff d81907ad --workdir <dir>`: `MODE: SCOPED -- 22 script(s) run, 11 scoped out`.
- Ran locally at the head, each green: `debug_collect.py`, `card.mjs`, `card_drift.mjs` (`39 state(s) moved and claimed, 1 identical`), `md_tables.mjs`, `doc_claims.py`, `typing_ruler.py`, `config_flow_steps.py`, `deployment_shape.py`, `env_drift.py`, `finite_boundary.py`, `manual_plan.py`, `wood_advisor.py`, `block_duty.py`, `solar_alignment.py`, `structure.py` (`STRUCTURE RATCHET PASSED`), `harness_headers.py`, `entities.py` (`ALL 2231 ENTITY CHECKS PASSED`).
- Left to CI (heavy, per SEAT-BLOCK): `features.py`, `golden.py`, `boost_drift_replay.py`, `arch_score_head.py`, and the mutation drive.
- `python3 tools/pr/ci_predict.py --base d81907ad` (from `origin/fix/r9-ro-11-pr`): `no closures or fast red predicted`, 11 unpinned sites (below).

## Unpinned sites

The rule is the `ADDED UNPINNED` lines `ci_predict.py --base d81907ad` prints. Each site, and the check expected to kill it, for `mutation-autofix` to pin:
- `coordinator.py` `predicted_next_room_temp` RETURN_DEL: killed in the mutation proof above (`UX-7: the predicted indoor temperature ...`).
- `diagnostics.py` `_without_private_ids` GUARD_OFF on `str` and on `list`: a regex substitution on a dict raises, and a list pass over a dict yields keys, so the diagnostics block's checks fail. Expected killed; not run per site.
- `diagnostics.py` `_coarsen` GUARD_OFF on `Mapping` and RETURN_DEL: pre-existing lines this diff only shifted; the existing #509 coordinate checks cover them.
- `sensor.py` `PredictedIndoorTempSensor._waiting_for` GUARD_OFF and RETURN_DEL, and `native_value` RETURN_DEL: the waiting_for and value checks. The value deletion is killed in the proof above.
- `sensor.py` `ModelStatusSensor.native_value` GUARD_OFF (no data), GUARD_OFF (alarm) and RETURN_DEL: the status-state checks. The alarm guard is killed in the proof above.

## Red checks

none yet: nothing has been pushed to CI. After the push, any red goes here with its answer.

## Forward-carry

none: no finding changes how a later stage must work. The carry in `dev/programme/carries/carry-1795.json` (third entry, from R9-UX-3) is honoured: the new Health block reads only an always-available, enabled-by-default sensor, and nothing is added to `HEALTH_WAITING`.

## Friction

- `fixer.md`: cost: `entities.py` fails at the end in a `git archive` copy (the handover checks need a repository), which hid the diagnostics block's red. The null-control run was taken again from a detached worktree.
- `gate-scoping.md`: cost: an untracked seat-claim file in the worktree forced `MODE: FULL` until it was removed.

## Remaining (owed after #2025 merges)

- Merge `origin/main` into this branch, then re-run `structure.py` (re-record if `max_class_loc` moved), `entities.py`, `card.mjs`, `card_drift.mjs` and `harness_headers.py` (the D6 counts), re-take the mutation proof and this body, and re-run `ci_predict.py --base origin/main`.
- U5 screenshots. `tests/card_browser.mjs`'s Health fixture now carries the model-status sensor. `HPO_PAGES_OUT=docs/img/card node tests/card_browser.mjs` must regenerate `health-light.png` and `health-dark.png`, and the `docs/dashboard-card.md` alt text then needs to name the new block. That run needs Playwright and Chromium, which this seat did not have and did not download. The product page's gallery slot for the Health page (DESIGN-SITE.md) takes the regenerated picture with its caption quoted from `docs/dashboard-card.md`.
- `tests/card_browser.mjs` is code-owned: this PR merges on tvofi's approving review at the head.

_Requested by **tvofi**_

🤖 Generated with [Claude Code](https://claude.com/claude-code)
