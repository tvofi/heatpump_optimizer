Design review: revise c9aa2294772a4a2d5be672f3f1df52894903dc12 harness

Reviewed: `dev/programme/designs/R10-CONFIGFLOW-PAGES.md` and its `-probes/` at `design/R10-CONFIGFLOW-PAGES` c9aa22947, round 1 of 3, from a detached worktree at that SHA (main aaf8af512 plus the note and probes). No earlier design verdict exists on `design-verdict/R10-CONFIGFLOW-PAGES`: the killed seat posted none. Token count: not reported by this harness.

## Re-measured, holding (`evidence/probes.cfp.out`, `evidence/probes.p08.out`)

- **`rejected_rerender.py`:** 27 of 30 cleared rows are stale at main and 0 with patches 08+04+08t+F1b applied. The `--null` row reads shown_stored 19 = 19 on both trees.
- **`clear_required.py` at main:** `type=menu errors=None stored_price_entity=None`, so the A3' defect is reproduced. It is unchanged under patch 08.
- **Finder's `wizard_widgets.py` (3930b421a):**
  - spelled_twice: 44 -> 0;
  - other_spelled_twice: 20 -> 0;
  - `--bump heat_pump_cop_nominal` disagree: 2 -> 0.
- **Archscore:**
  - The combined A+B+C+C2 tree reads dS **+3.3700** (duplication_copies 35 -> 28, literal_clone_copies 185 -> 123) against the note's "about +3.37" (`evidence/archscore_combined.out`).
  - The per-move figures in `archscore.out` are consistent with it.
- **Goldens:** `golden.capture_config_flow()` is byte-identical between main and the combined tree (`evidence/golden_capture_sha.txt`), so no golden moves.
  - `golden_equal` reads 0 on both trees in this seat's mixed venv. That is environment drift against the committed file, the same on both sides.
  - The canonical environment's `golden_equal 1` stays the fixer's to show.
- **Seam:** `config_flow.py` only (`_page`, `_OPTION_FIELDS`). No other open `design/*` ref touches `config_flow.py`; R10-HEAT-METER's ref is merged as #2854.
- **Sibling grep of the A3' class** (a required check that falls back to stored data, so a cleared `_STORED` slot still reads as stored): `or current.get(` appears twice in the options flow (config_flow.py:3405, 3411).
  - The tibber token's row default is `''`, not `_STORED` (config_flow.py:1563), so `_clear_absent` never nulls it. The only live site is `CONF_PRICE_ENTITY` (row at :1564).
  - metering (:3445), hot_water_tank (:3540-3547) and building (:3585-3603) do not judge a cleared `_STORED` entity over stored data.
  - The note's class is closed by A3' alone.
- **Mutation-ledger re-key (15 entries) and no claim-file change:** these hold as written.

## Revise point (one, an addition only)

1. **harness / evidence plan: arm A3' is in scope by the orchestrator's ruling, and the note designs it in one sentence.** The note's "Decisions routed" section offers A3' as a recommendation, with the fix in one line and "its own failing test" unspecified. Add an **Arm A3'** section after Arm A that states all of the following.
   - **Fix:** `_entities_errors(cleaned, current)` judges both the source and the entity over `view = {**current, **cleaned}`:
     - `source = view.get(CONF_PRICE_SOURCE, DEFAULT_PRICE_SOURCE)`;
     - when `source == PRICE_SOURCE_ENTITY` and `not view.get(CONF_PRICE_ENTITY)`, the result is `price_entity_required`.

     This works because `_clear_absent` writes a cleared `_STORED` slot back as `None` (config_flow.py:2264-2267), so the view reads the clear. It is the same rule `async_step_hot_water_tank` already uses (:3540-3544). The tibber branch stays as it is: its row is not `_STORED`.
   - **Failing test** (`tests/config_flow_steps.py`, beside the existing `price_entity_required` cases at :742 and :3335):
     - **Setup:** stored `price_source: entity` and `price_entity: sensor.price`, then submit the entities page with `price_source: entity` and the price entity cleared (absent).
     - **Assert:** `type == "form"`, `errors == {CONF_PRICE_ENTITY: "price_entity_required"}`, and the stored options unchanged, with `price_entity` still `sensor.price`.
     - At main it fails: menu, and `None` saved.
     - **Null control:** the same submit with `price_entity: sensor.other` saves `sensor.other`.
     - **Second control:** a switch to tibber with a token clears nothing and raises no error.
   - **Mutants:**
     - judge over `{**current, **flat}`, which is the pre-clear view;
     - restore `submit or current`.

     The test must kill both.
   - **Harness:** port `clear_required.py` into `dev/audit/harnesses/r10_configflow_pages.py` beside the re-render arm. It reads `type=menu stored_price_entity=None` at base and `type=form errors=price_entity_required` at head.
   - **Invariants amended.** Arm A states that an accepted submit saves byte-identical options and that every error key is unchanged. A3' is the one deliberate exception: this submit changes from accepted to refused. A3's record-at-main comparison must exclude exactly that case and name it, or A3 will flag the fix as a regression.
   - **The behaviour change is user-visible:** a submit that used to save is now refused. Name it in the PR body's behaviour section. The translation key `price_entity_required` already exists, so no string moves.

## Notes for the fixer (carries)

- Patch 04 (arm B) and `F1_plus_F1b_spike.patch` (arm C2) conflict textually at `_quick_setup_schema`'s two wood probes (config_flow.py about :1221 on the 08+04 tree). The note's "apply clean together" holds for 04, 08 and F1, not for F1b. The resolution `_suggested_optional(current, K): _registry_widget(K)` is the one measured at dS +3.3700 above. Carry: R10-CONFIGFLOW-PAGES (item dr1-b-c2-conflict)
- Per the ruling, every other #2238 finding is dispositioned in the PR body before any closing keyword is written. This is the note's own `close-2238` carry, restated so the fix reviewer checks it. Carry: R10-CONFIGFLOW-PAGES (item dr1-close-2238-disposition)
