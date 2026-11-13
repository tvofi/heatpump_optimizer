R10-USER-TEXT-VERIFY-CARD (production, user-facing text; the owner's ruling of 2026-11-13, "Do 1 in round 10": verify all user-facing text in production against the code's behaviour, not its comments). This pull request covers the dashboard card's text: every string in the card's language table and every unkeyed literal it renders. It judges each one against the code that decides it, corrects the false and stale ones in en, sv and de, and pins the claims a script can read back. strings.json and translations are the sibling groups' and are not edited.

What the diff does:

- `dev/audit/harnesses/r10_card_user_text.mjs` is the enumerator. It lists every key of `STRINGS.en`, with its sv and de texts and whether a reader reaches it. A key counts as reached when it is quoted outside the table, or when it starts with the literal head of a run-time key, such as `` `health.p_${...}` `` or `"health.input_" + id`. It also lists every unkeyed literal reaching the DOM: a template's `>text<` run, a `title`, `aria-label`, `placeholder` or `alt` value, or a quoted `textContent`/`innerText` assignment.
- `dev/audit/rounds/round10/user-text-card.md` is the record. It is a claim table per string, with verdict and `file:line` evidence at the merge base, built on the method of #3513's record (page text against the deciding symbol). Every string was read against the code that decides it: where the card renders it, under what condition, and which value fills each placeholder, followed into the Python. The reading was split across nine read-only reader subagents. Every `false` and `stale` verdict was then re-read by this seat at the quoted lines before any text changed (Figures).
- Corrected in all three languages:
  - `health.cop_reason_tracking_gate`: the gate compares the pump's draw-to-plan ratio with its own average, `abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE` in `accuracy.py`. The house is not involved.
  - `health.cop_reason_modelled_cop`: the refusal fires when `modelled_cop <= 0.1` (`coordinator.py`), an unusable reference. It does not fire because a measurement was missing.
  - `health.metric_gains`: with no profile, `internal_gains_at` returns the configured `internal_gains` constant. The plan counts that constant, not "none".
  - `health.metric_tank` and `health.model_default`: the seed is `params().dhw_cooling_rate`, the option's value. It is not necessarily the default.
  - `health.metric_lower` and `health.model_share`: the lower floor's U is `lower_floor_heat_loss * _house_heat_loss_scale` times the ratio. The ratio is therefore relative to the house-wide estimate, not to the settings' value.
  - `health.learn_savings_why`: the sensor waits only while `_rows()` is empty, and the open month books a row. It does not wait for a settled month.
  - `whatif.no_windows_hint`: with no windows, `dhw_planner` derives them from the learned draw pattern. With the schedule off it uses `FULL_DAY`. Hot water is never "never required".
  - `whatif.quiet_frac_note`: `measured_ceiling_kw` sets the silent cap before the fraction is read, so the cap can apply while the fraction is still 1.0.
  - `advisor.basis_history` and `advisor.basis_config`: the replay power is the mean of measured electrical power, else `max_electrical_power * _ADVISOR_DUTY_FRACTION`. The de text "Wärmeabgabe" said heat output.
  - `advisor.step_grid`: the fuse size is `CONF_MAIN_FUSE_A`, on Advanced settings → Fuse and peak guards. The text now names both pages.
  - `score.part_overall`: `compose_scores` averages machine and operation only. No reader renders this key today, but its text was false.
  - `score.reason_cop_unmeasurable`: the grade calls `cop_measured(False)`, so hot-water coverage is not required.
  - `slots.released_one` and `slots.released_other`: `n` counts released plan steps (`{"step": i, ...}` per step and channel), not slots.
  - `errors.invalid_window_time`: the save and simulate checks also read `quietWindows`, so the error no longer calls every invalid window a hot-water one.
  - `plan.space_blocked`: `space_blocked` is `not mode.space_heat`, which pure cooling also sets. The banner no longer says "DHW only".
  - `receipt.covers`: savings are priced at `spot + fee_per_kwh` (`ledger.py`). The text no longer says "spot cost only".
  - `advisor.refit_detail`: the refit publishes one band, `band_percent` (`REFIT_BAND_PERCENT`, 10, `accuracy.py`'s `heat_loss_refit`), and `_refit_disagrees` (`coordinator.py`) judges the refit against it alone. The "7" of "±7-10 %" stood only in the `#:` comment over the constant. The row now renders `±{band} %` from `attrs.refit.band_percent` (`restartRows`), so the text follows the published value.
  - The wood, fuse and frequency opt-in rows (`advisor.optin_sensor_off`, new in en, sv and de): each named only an options page, but no options step turns these advisors on. Each is a sensor created disabled (`_attr_entity_registry_enabled_default = False` in `WoodBurnAdvisorSensor`, `MonthlyPeakSensor`, `FrequencyAdvisorSensor`), and the card never reads it. The row now also says to enable its sensor. The degree row is unchanged: its page's `price_tiles_enabled` switch does turn it on. The comment over `ADVISOR_OPT_IN_STEP` said the step "turns each opt-in on", and is corrected.
- Corrected in de only: `setup.page_building`, `advisor.step_tuning` and the grid page in `advisor.step_grid` now carry the de options menu's own labels. en and sv already matched theirs.
- Never rendered, so removed from all three languages: `health.learn_score_why` (`healthWaitingWhy` returns the score sensor's reason first), and `advisor.act_schedule`, `series.wood_slots` and `menu.add_slot_wood`, which have no reader.
- Unverifiable, recorded with the reason and left as written:
  - `reasons.dhw_preheat`: "while electricity is cheap" is the classifier's fall-through, with no price test.
  - `series.dhw_band_note` and `series.dhw_band_note_floored`: "widens further ahead" is not enforced by `sigma(lead)`.
  - `setup.dhw_coil_none_why`: en "wood heat only" has no subject, and sv and de read it differently.
  - `advisor.waiting`: none of the four sensors it reads publishes `waiting_for`, so the row cannot render.
  - `health.check_insight`: that Home Assistant's entity table lists disabled entities is decided by Home Assistant's frontend, outside this repository.
- Pinned in `tests/card.mjs`, in every card language (the languages are `STRINGS`' own keys):
  - (1) every `setup.page_*` equals its options-flow step's menu label in `translations/<lang>.json`. Every comma clause of every `advisor.step_*` is a menu path (an init page, or the init menu's advanced entry and then an advanced page), and one clause ends on the step's own page when the step is a page. This extends the en-only Configure-chip check, which the de drift passed.
  - (2) the COP refusal reasons quote `COP_TRACKING_ERROR_GATE` (read from `const.py`) and the modelled-COP floor (read from `coordinator.py`'s refusal line).
  - (3) the invalid-window error names no channel. Both handlers that refuse an invalid window, Save (`onSaveSchedule`) and Simulate (`run`), are driven with a valid hot-water window and an invalid quiet one: each must print `errors.invalid_window_time` for the quiet window and call no service. This replaces the source regex, which one of the two sites satisfied.
  - (4) the refit row renders the `band_percent` the advice publishes, read from `accuracy.py`'s `REFIT_BAND_PERCENT`, and a probe band of 13, which the constant does not name. The probe shows the row reads the attribute, not a literal.
  - (5) each `ADVISOR_OPT_IN` row carries `advisor.optin_sensor_off`, and the degree row does not. The fixture has price tiles off, so the degree row renders. Each of the three classes is read from `sensor.py` as disabled by default.
  - The existing restart-row pins (en and sv) now expect `±10 %`, the fixture's `band_percent`.
  - The existing pins on `receipt.covers` (UX-6), the advisor basis line, the space-blocked banner and the Health learning row follow the corrected text.
  - Prose-only: the rest of the corrected list above. Each states a code path, such as the derived DHW windows, the measured silent cap, the house-scaled lower floor or the counted steps, that no string comparison reads.
- `tests/golden/card_claimed_drift.txt` claims the 21 card states the corrected text moves (`claim-files.md`).
- `docs/img/card/health-light.png` and `health-dark.png` are re-taken from the head's card. The learning row's corrected text is the one change on the page; `pages.json` is byte-identical.
- `dev/audit/harnesses/r10_card_evidence_kinds.py` is the evidence sweep. It classifies every `file:line` a row of the record cites, at the merge base, as code, comment, docstring (by `ast`) or blank, and prints each row with a citation that is not code. The record's new section, "Comment and docstring evidence, swept", lists every row it returned at f11bdd4d4 with its disposition. Two rows were re-judged false or incomplete on code: `advisor.refit_detail` and the opt-in rows above. Five more were re-judged true on code, where the citation had been a comment or docstring: `savings.wood_note`, `setup.dhw_coil_preheats`, `receipt.saved`, `score.evidence_empty`, `status.stale_title`. The rest were line drift, a reversed range or a redundant docstring citation beside deciding code, and each is re-anchored in its row. The record's verdict counts move by one row, `advisor.refit_detail`, from true to false. Two absolute `/home/user/wt-card/` paths in the record are made relative.
- `tests/closures.json` gains the INERT READS entries for `tests/harness_headers.py` of both harnesses (`ci_predict.py --apply-inert`).

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Head

741f378bfd9a45b640c399670ad3d854b39bc0b6, merge base 90c6bc3b0756475e28d4ace8d8e31c4788474933 (origin/main #3511). origin/main was read at e23124ff6e45bac1d48b4a775dad555a37965355, 2026-11-13T20:32Z. `git merge-tree --write-tree origin/main HEAD` exits 0 with a single tree, so there was no re-merge. Round 2: the repair of `Fix review: blocked f11bdd4d48`, at `probe/revt-r10-user-text-verify-card-c1e04704`. It fast-forwards from f11bdd4d4 through the BLOCKED.md commit c86500999a on `handoff-wip`, and BLOCKED.md is deleted.

## Mutation proof

The card at the merge base was put in place of the head's (`git show 90c6bc3b0:<card> > <card>`) in a detached worktree at the head, with the head's `tests/card.mjs`. `node tests/card.mjs` exits 1, with 11 failing checks:

- `UX-6: the note names what the total covers`
- `the page names what drove the replay`
- `a drift alarm offers the refit with its band, and the restore point`
- `the restart rows speak Swedish`
- `a space-blocked plan shows the no-space-heating banner`
- `still learning lists unavailable waiting sensors with a reason in words`
- `user text: every setup.page_* and advisor.step_* names the options flow's own menu path, in every card language`
- `user text: the COP refusal reasons quote COP_TRACKING_ERROR_GATE and the modelled-COP floor, in every card language`
- `user text: the invalid-window error names no channel, in every card language`
- `user text: the refit row states the band_percent the refit publishes, in every card language`
- `user text: an opt-in advisor whose sensor is off by default says to enable it, in every card language`

`user text: Save and Simulate both refuse an invalid quiet window with the channel-neutral error` passes on the base card. Both handlers read `quietWindows` at the base, and only the error's text was wrong. That check pins the behaviour the corrected text states, and the mutants below are its proof. With the head's card restored, the result is `ALL CARD CHECKS PASSED`, exit 0. No `.py` line is added outside `dev/`, so `prepr.sh`'s mutant draw is empty.

Mutants: the review's nine, rebuilt from the verdict's descriptions, plus six for this round, each applied to a detached worktree at the head and run with `node tests/card.mjs`. Driver: `mutants.py` in scratch, one source edit per mutant, restored after each.

| mutant | edit | rc | failing check |
|---|---|---|---|
| `gate-const-0.25` | `const.py` `COP_TRACKING_ERROR_GATE` 0.3 to 0.25 | 1 | COP refusal reasons |
| `sv-gate-40` | sv tracking-gate text 30 % to 40 % | 1 | COP refusal reasons |
| `sv-window-hotwater` | "Varmvatten: " prefixed to the sv window error | 1 | invalid-window error names no channel |
| `drop-quiet-find-both` | both `(draft.quietWindows \|\| []).find(` to `[].find(` | 1 | Save and Simulate both refuse an invalid quiet window |
| `drop-quiet-find-first` | the first site (`onSaveSchedule`) reads `dhwWindows` | 1 | Save and Simulate both refuse an invalid quiet window |
| `de-page-building-old` | de `setup.page_building` back to "Wärmespeicherung" | 1 | menu path |
| `sv-step-grid-badpage` | the sv `advisor.step_grid` loses its last word | 1 | menu path |
| `de-json-menu-grid` | de.json `menu_options.grid` to "Netz-Spitzentarif" | 1 | menu path |
| `modelled-floor-0.2` | `coordinator.py` `modelled_cop <= 0.1` to `<= 0.2` | 1 | COP refusal reasons |
| `band-literal` | `restartRows` passes `band: "10"` | 1 | refit row states the band_percent |
| `band-wrong-attr` | `restartRows` reads `refit.band` | 1 | refit row; the two restart-row pins |
| `band-text-old-en` | en text back to "±7-10 %" | 1 | refit row; the placeholder parity checks |
| `optin-note-dropped` | the opt-in note removed from the row | 1 | opt-in advisor says to enable it |
| `optin-note-on-all` | the note on every opt-in row, degree included | 1 | opt-in advisor says to enable it |
| `NULL` | a trailing comment appended to the card | 0 | none (`ALL CARD CHECKS PASSED`) |

`drop-quiet-find-first` survived at f11bdd4d4. `optin-note-on-all` survived the first cut of check (5), whose fixture had price tiles on, so no degree row rendered. The fixture now turns them off, and the check fails on a missing row.

## Null control

- The evidence sweep: `python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py <record>` prints `rows 360 flagged 29` on the record at f11bdd4d4. That run includes `advisor.refit_detail` (the `coordinator.py:1363` docstring) and `slots.lane_aria`'s reversed range. At the head it prints `rows 360 flagged 0`. It stops at the record's own sweep section, whose table quotes the replaced citations.
- The refit band's Python source: with `REFIT_BAND_PERCENT = 12` in `accuracy.py`, the card check still passes, by design: the row reads the published value, and only `band-literal` and `band-wrong-attr` above, which cut that read, fail it. The Python pin fails, so a changed constant is not silent: `tests/features.py` exits 1 with `1 of 5571 FEATURE CHECKS FAILED`, `FAIL #1936: the refit states its own band and the evidence behind it`. Restored, it passes (gate table).
- Enumerator: a scratch copy of the merge-base card, with one table key and two unkeyed literals planted, prints `table 649 (unreached 4)` and `literal 6` and lists all three planted strings. The unplanted base prints `table 648 (unreached 3)` and `literal 4`.

## Figures

- Strings: `node dev/audit/harnesses/r10_card_user_text.mjs` at the merge base gives `table 648 (unreached 3)`, `literal 4`. At the head it gives `table 645 (unreached 0)`, `literal 4`: four keys removed and `advisor.optin_sensor_off` added.
- Verdicts, recorded per row in `dev/audit/rounds/round10/user-text-card.md`: true 330, false 23, stale 1, unverifiable 6, n/a 292, totalling 652. Against f11bdd4d4, `advisor.refit_detail` moves from true to false. The true, false, stale and unverifiable rows are the record's per-row tables: `python3 -I dev/audit/harnesses/r10_card_evidence_kinds.py` counts them as `rows 360`, and 330 + 23 + 1 + 6 = 360. The n/a count comes from the nine reader tables, which are not in the tree. That is the residue the review named.
- Gate at 9eb771be1 against 90c6bc3b0. 741f378bf changes only `tests/card.mjs`, which was re-run at that head. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 11 script(s) run, 22 scoped out`. Each script was run with `PYTHONPATH=tests/hastub`:

  | script | rc | result |
  |---|---|---|
  | `node tests/card.mjs` | 0 | `ALL CARD CHECKS PASSED` (at 741f378bf too) |
  | `GOLDEN_MODE=drift node tests/card_drift.mjs` | 0 | `card_drift: 21 state(s) moved and claimed, 24 identical`. No new state moves, so the claim file is unchanged this round |
  | `tests/features.py` | 0 | `ALL 5571 FEATURE CHECKS PASSED` |
  | `env -u BASH_ENV python3 tests/entities.py` | 0 | `ALL 2711 ENTITY CHECKS PASSED` |
  | `tests/doc_claims.py` | 0 | `ALL 348 checks PASSED` |
  | `tests/harness_headers.py` | 0 | `ALL 115 HARNESS HEADER CHECKS PASSED` |
  | `tests/arch_score_head.py` | 0 | `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED` |
  | `tests/deployment_shape.py` | 0 | `ALL DEPLOYMENT SHAPE CHECKS PASSED` |
  | `tests/plan_view.py` | 0 | `plan reason codes, price provenance and slot energy OK` |
  | `tests/env_drift.py` | 0 | `NO STALE FIXTURE: 5` |
  | `GOLDEN_MODE=drift tests/golden.py` | 0 | `NO STALE FIXTURE: 56` |

  The run_always lines: `tests/layout.py` rc 0; `tests/closure.py selftest` rc 0, `ALL 118 closure shrink pins PASSED`; `tests/env_drift.py --claims-only 90c6bc3b0` rc 0. `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`. `python3 tools/pr/ci_predict.py --apply-inert` applied the new harness's entry and then predicted no closures, fast, governance or instrument red.
- Browser: `HPO_PAGES_OUT=<scratch> node tests/card_browser.mjs` at 741f378bf exits 0 with `ALL BROWSER CHECKS PASSED`. `cmp` against the committed `docs/img/card/*.png` finds health, plan, plan-why and tile identical (light and dark), and advisor, savings and setup different. `pages.json` is identical. Advisor, savings and setup already differed at the merge base on this host in round 1, so they are not re-taken here (Forward-carry, which now also covers the opt-in note on the advisor page). The health pair committed in round 1 still matches.
- VERSION, the manifest and RELEASE_NOTES.md are absent from the three-dot diff. `tests/golden/claimed_drift.txt` is untouched.

## Red checks

- none: no CI run exists at this head, because no pull request exists yet. Carry: dismissed: no red to answer

## Forward-carry

- `docs/dashboard-card.md` (Savings receipt paragraph) still says the savings figure "compares spot cost only". `ledger.py` prices both sides at `spot + fee_per_kwh`, the fact `receipt.covers` now states. Re-measure: `git grep -n 'spot cost only' docs`. Carry: R11-INTAKE-R10-RESIDUE
- `docs/dashboard-card.md` (Advisor page) says the replay uses "your install's measured delivery". `topology.py` replays the mean measured electrical power, else half the configured maximum. Re-measure: `git grep -n 'measured delivery' docs`. Carry: R11-INTAKE-R10-RESIDUE
- `docs/dashboard-card.md`'s Health picture alt text says "waiting for the first settled month", and the re-taken picture now shows "the first month with a booked saving". Re-measure: `git grep -n 'first settled month' docs`. Carry: R11-INTAKE-R10-RESIDUE
- `docs/img/card/advisor-*.png` show the old basis line and fuse step. This host's render of the merge base already differs from the committed advisor, savings and setup figures, so they need a re-take on the host that recorded them. Re-measure: `cmp` of a `card_browser.mjs` `HPO_PAGES_OUT` render at the base against the committed PNGs. Carry: R11-INTAKE-R10-RESIDUE
- `translations/de.json`'s `grid` options page is titled "Netz-Spitzentarif", but its menu entry is "Lastspitzentarif des Netzes". The card now names the menu entry, the label a user clicks. One page should have one de name. Re-measure: compare `options.step.init.menu_options.grid` with `options.step.grid.title` in de.json. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
