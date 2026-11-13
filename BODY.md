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
  - (3) the invalid-window error names no channel, and the card's check reads `quietWindows`.
  - The existing pins on `receipt.covers` (UX-6), the advisor basis line, the space-blocked banner and the Health learning row follow the corrected text.
  - Prose-only: the rest of the corrected list above. Each states a code path, such as the derived DHW windows, the measured silent cap, the house-scaled lower floor or the counted steps, that no string comparison reads.
- `tests/golden/card_claimed_drift.txt` claims the 21 card states the corrected text moves (`claim-files.md`).
- `docs/img/card/health-light.png` and `health-dark.png` are re-taken from the head's card. The learning row's corrected text is the one change on the page; `pages.json` is byte-identical.
- `tests/closures.json` gains the enumerator's INERT READS entry for `tests/harness_headers.py` (`ci_predict.py --apply-inert`).

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Head

f11bdd4d483c0509ad108b0e00112aaae8f1368d, merge base 90c6bc3b0756475e28d4ace8d8e31c4788474933 (origin/main #3511). origin/main was read at e23124ff6e45bac1d48b4a775dad555a37965355, 2026-11-13T18:08Z. `git merge-tree --write-tree origin/main HEAD` exits 0, a single tree, so there was no re-merge. The same check also exits 0 against `handoff/r10-config-flow-text-verify` and `handoff/r10-hotfix-flow-setpoint-stuck`. `handoff/r10-hotfix-boost-flow-ceiling` does not exist.

## Mutation proof

The card at the merge base was put in place of the head's (`git show origin/main:custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js > <card>`), with the head's `tests/card.mjs`. `node tests/card.mjs` exits 1, with these failing checks:

- `UX-6: the note names what the total covers`
- `the page names what drove the replay`
- `a space-blocked plan shows the no-space-heating banner`
- `still learning lists unavailable waiting sensors with a reason in words`
- `user text: every setup.page_* and advisor.step_* names the options flow's own menu path, in every card language`, detail `de advisor.step_tuning: ["Einsparungen vs. Komfort"] is no menu path; ... de advisor.step_grid: ["Netz-Spitzentarif"] is no menu path; ... de setup.page_building: "Heizsystem und Wärmespeicherung" vs "Heizsystem und Wärmespeicher"`
- `user text: the COP refusal reasons quote COP_TRACKING_ERROR_GATE and the modelled-COP floor, in every card language`, detail `gate 0.3, modelled floor 0.1; wrong in: en,sv,de`
- `user text: the invalid-window error names no channel, in every card language`

With the head's card restored, the result is `ALL CARD CHECKS PASSED`, exit 0. No `.py` line is added, so `prepr.sh`'s mutant draw is empty and `mutant_run.py --diff` has nothing to draw.

## Null control

- Enumerator: a scratch copy of the merge-base card, with one table key (`header.zz_planted`) and two unkeyed literals (a `<span>` text run and a `title=` value) planted, prints `table 649 (unreached 4)` and `literal 6` and lists all three planted strings. The unplanted card prints `table 648 (unreached 3)` and `literal 4`. At the head: `table 644 (unreached 0)`, `literal 4`.
- The nav check's own control is the merge-base card's de drift above. The en-only Configure-chip check passed on that same card.

## Figures

- Strings: `node dev/audit/harnesses/r10_card_user_text.mjs` at the merge base gives `table 648 (unreached 3)`, `literal 4`, so 652 rows. At the head it gives `table 644 (unreached 0)`, `literal 4`.
- Verdicts, from `cut -f4` over the nine verdict tables and recorded per row in `dev/audit/rounds/round10/user-text-card.md`: true 331, false 22, stale 1, unverifiable 6, n/a 292, totalling 652. Every false and stale row was re-read at its quoted lines by this seat. The re-read used `sed -n` over `accuracy.py`, `coordinator.py`, `thermal_model.py`, `dhw_learning.py`, `pump_signals.py`, `ledger.py`, `topology.py`, `dhw_planner.py`, `quiet_windows.py` and the card, and `translations/de.json`'s `menu_options` for the de rows.
- Applied corrections: a script compared each edited key's en, sv and de text in `node dev/audit/harnesses/r10_card_user_text.mjs --tsv` with the intended text, giving `mismatches []` over 22 keys.
- Gate at cf15484e5 against 90c6bc3b0 (f11bdd4d4 adds only the two Health PNGs, and the scope it prints is the same 11 scripts): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 11 script(s) run, 22 scoped out`. Each script was run with `PYTHONPATH=tests/hastub`:

  | script | rc | result |
  |---|---|---|
  | `node tests/card.mjs` | 0 | `ALL CARD CHECKS PASSED` |
  | `GOLDEN_MODE=drift node tests/card_drift.mjs` | 0 | 21 claimed states; rc 1 with `21 problem(s)` unclaimed before the claim |
  | `tests/features.py` | 0 | `ALL 5571 FEATURE CHECKS PASSED` |
  | `env -u BASH_ENV python3 tests/entities.py` | 0 | `ALL 2711 ENTITY CHECKS PASSED` |
  | `tests/doc_claims.py` | 0 | `ALL 348 checks PASSED` |
  | `tests/harness_headers.py` | 0 | `ALL 115 HARNESS HEADER CHECKS PASSED` |
  | `tests/arch_score_head.py` | 0 | `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED` |
  | `tests/deployment_shape.py` | 0 | `ALL DEPLOYMENT SHAPE CHECKS PASSED` |
  | `tests/plan_view.py` | 0 | passed |
  | `tests/env_drift.py` | 0 | `NO STALE FIXTURE: 5` |
  | `GOLDEN_MODE=drift tests/golden.py` | 0 | `NO STALE FIXTURE: 56` |

  The run_always lines: `tests/layout.py` rc 0; `tests/closure.py selftest` rc 0, `ALL 118 closure shrink pins PASSED`; `tests/env_drift.py --claims-only 90c6bc3b0` rc 0. `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`. `python3 tools/pr/ci_predict.py` after `--apply-inert` predicts no closures, fast, governance or instrument red.
- Browser: `HPO_PAGES_OUT=<scratch> node tests/card_browser.mjs` at the head exits 0 with `ALL BROWSER CHECKS PASSED`. The same command at the merge base (worktree at 90c6bc3b0) exits 0 too. `cmp` was run against the committed `docs/img/card/*.png`:
  - At the base, advisor, savings and setup (light and dark) already differ on this host, and the other eight figures match.
  - Base against head: only advisor and health differ.
  - `pages.json` is identical to the committed one at both ends.
  - So the health pair moves by this diff alone and is re-taken. Advisor moves too, but this host does not reproduce the committed advisor figure even at the base, so it is not re-taken here (Forward-carry).
- VERSION, the manifest and RELEASE_NOTES.md are absent from the three-dot diff. `tests/golden/claimed_drift.txt` is untouched.

## Red checks

none yet at this head (CI not run).

## Forward-carry

- `docs/dashboard-card.md` (Savings receipt paragraph) still says the savings figure "compares spot cost only". `ledger.py` prices both sides at `spot + fee_per_kwh`, the fact `receipt.covers` now states. Re-measure: `git grep -n 'spot cost only' docs`. Carry: R11-INTAKE-R10-RESIDUE
- `docs/dashboard-card.md` (Advisor page) says the replay uses "your install's measured delivery". `topology.py` replays the mean measured electrical power, else half the configured maximum. Re-measure: `git grep -n 'measured delivery' docs`. Carry: R11-INTAKE-R10-RESIDUE
- `docs/dashboard-card.md`'s Health picture alt text says "waiting for the first settled month", and the re-taken picture now shows "the first month with a booked saving". Re-measure: `git grep -n 'first settled month' docs`. Carry: R11-INTAKE-R10-RESIDUE
- `docs/img/card/advisor-*.png` show the old basis line and fuse step. This host's render of the merge base already differs from the committed advisor, savings and setup figures, so they need a re-take on the host that recorded them. Re-measure: `cmp` of a `card_browser.mjs` `HPO_PAGES_OUT` render at the base against the committed PNGs. Carry: R11-INTAKE-R10-RESIDUE
- `translations/de.json`'s `grid` options page is titled "Netz-Spitzentarif", but its menu entry is "Lastspitzentarif des Netzes". The card now names the menu entry, the label a user clicks. One page should have one de name. Re-measure: compare `options.step.init.menu_options.grid` with `options.step.grid.title` in de.json. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
