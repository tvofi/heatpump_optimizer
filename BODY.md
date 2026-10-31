Part 3 of R10-UX-HEALTH: the carries neither #2976 nor #2997 answered. Part of #2253, Part of #2260, Part of #2263, Part of #2499, Part of #2809, Part of #2815 (the group's `fixes` is empty, so no closing keyword is used. Carry 20 assigns #2499's last residual, its Health line, to this group, and whether the issue is then done is the orchestrator's call after the merge).

What lands:

- **#2499's Health residual (carries 11, 20).** #2976 (559134e96) made the heat-loss row read "Not observable without a power meter." with no power meter. It still drew the row's learned bar full when the learner had converged, so the row still looked like a trusted learned scale. The bar is now empty (`healthModelHtml`, one condition on the share the row already computes). A metered install's learned row keeps its full bar.
- **udf-strings-history (carry 21).** UI text describes current behaviour only. `price_prior_enabled` ("used to be a flat repeat") now says what the option does and what switching it off does. `price_risk_lambda` drops ", as before". The census (Figures) found one more phrase of the same kind: `heat_pump_mode_entity`'s "exactly as before", in three places per file (the setup page, its plant section, and the options pump page). It is dropped too. The Swedish text is rewritten in step: "som tidigare", "precis som förut", and "Dessförinnan var resten av horisonten ...".
- **A check that keeps it so.** `tests/entities.py` refuses any leaf in strings.json, en.json or sv.json that carries a change-history phrase.
- **The control for carry 22, which stays open**: `dev/audit/harnesses/r10_two_zone_hhl_inert.py`. See below.

What does not land, and why:

- **Carry 22 (two-zone `house_heat_loss_coefficient`), not built.** The carry rests on the live probe's finding that the field is inert in two-zone mode. That holds for the solve but not for system identification. `sysid.HousePlant.of_params` builds the step sizer's plant from `heat_loss_coefficient` with no two-zone branch, and the coordinator's sysid tick passes it whenever an experiment runs, on single- and two-zone plants alike. On the probe's two-zone config, the sized step is 1.738 kW at 0.1 kW/K, 3.386 kW at 0.4, and no step at 1.0 (Figures). Hiding the field would hide a setting that still changes what the integration does, and labelling it "unused" would be false. A first cut hid the field through the registry's `when=` with a shared `two_zone_from_config` predicate. That cut was withdrawn before the handoff once the sizer arm read non-zero. The sound order is to make the sizer read the zone loss first: `_slab_prior` in the same class already does, through `_zone_heat_loss`. The hide is then one `when=` row. That is a sysid change outside this group's seam (architect note: the Health tab renderer), so it is routed rather than made. Forward-carry. Carry: R10-UX-HEALTH
- **Carry 14 (the "driving scale") and carry 17 (the P9 storage reset)** stay where #2997 left them: each waits on an orchestrator decision (the widget's confirmation; an after-edge for the chart ink at 375 px). Nothing here changes either. Carry: R10-UX-HEALTH

Design choices:

- **The history check is a phrase list, and says so.** Tense has no syntactic shape. The markers are the change-history phrasings the catalogues held: en `as before`, `used to be`; sv `som tidigare`, `som förut`, `dessförinnan var`. "Used to <verb>" as an instrument ("Used to read your hourly electricity prices") is current behaviour and is not matched. So is a repair's runtime history ("until now the plan was still being held ...", "no longer measured"). The census in Figures lists every remaining hit of the wider net and its kind.
- **The bar, not the value.** The W/K figure stays. It is the value the model plans with, and the row says it is not observable. The bar is the row's "how far learned" signal, so only the bar changes.

## Head

bbbce602dc4b3374cbb079f3b067ac82365a1ca7, on merge base 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3. origin/main was at a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 at 2026-10-31T19:47Z, and `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so main is not merged in (`fixer.md` step 6).

Commits: 22626a277f5bb957d4f22357c242758b1d984f8f (the failing checks), 03fec96c13b50e83484413f55177bf0af4242e6b (the fix), fe5cdef51921638028f7a4b1c0776c6a561f6911 (the harness), bbbce602dc4b3374cbb079f3b067ac82365a1ca7 (its INERT READS entry, written by `tools/pr/ci_predict.py --apply-inert`).

Host note: macOS. `tests/entities.py`'s heartbeat arm cannot get a task port for its own child here (`PermissionError: Cannot get task port`). Each local `entities.py` run below therefore hid `_remote_debugging` from `importlib.util.find_spec` through a scratch wrapper, the same as #2997's runs, so that arm skips exactly as it does on an interpreter without the module. No tree file changes. CI (Linux) runs the arm.

## Mutation proof

Each mutant is one production edit in a detached worktree at bbbce602d (`git worktree add --detach`), run through the closure that owns the check, then discarded.

- Card: `healthModelHtml`'s heat-loss share `!observable ? 0 : hl.learned ? 1 : house ? house.share : 0` back to `hl.learned ? 1 : house ? house.share : 0`. `node tests/card.mjs` (after `tests/plan_view.py`) prints `1 CARD CHECK(S) FAILED`: `UX-HEALTH D: with no power meter the learned heat loss draws no learned bar (#2499)`, detail `bar 100%`. The null control `a metered install's learned heat loss still draws a full bar` stays ok.
- Strings: ", as before" restored in strings.json's `price_risk_lambda`, and ", som tidigare" restored in sv.json's. `PYTHONPATH=tests/hastub python3 tests/entities.py` (through the host wrapper, Head) prints `2 of 2496 ENTITY CHECKS FAILED`: `strings.json: no UI text describes how the integration used to behave [1: options.step.tuning.sections.risk.data_description.price_risk_lambda]` and the same for `sv.json`. `en.json`'s check, whose file the mutant left alone, stays ok. Each check reads only its own catalogue.

Test first: both commits' checks ran at the merge base's production files with the new tests (22626a277's tests, the production tree at 7539d1675). `node tests/card.mjs` printed the bar check FAIL with `bar 100%` and its null control ok. `entities.py` printed the three history checks FAIL, each `[5: config.step.user_sensors.data_description.heat_pump_mode_entity, config.step.user_sensors.sections.plant.data_description.heat_pump_mode_entity, options.step.tuning.sections.risk.data_description.price_risk_lambda, options.step.learning.data_description.price_prior_enabled, options.step.entities_pump.data_description.heat_pump_mode_entity]`. That base run was cut by its 900 s timeout under load average 38, after those checks printed.

## Null control

- The unmodified merge base fails the three new history checks (5 leaves per catalogue, listed under Mutation proof) and the bar check (`bar 100%`). The metered null control (`bar 100`, "Learned from 21 samples") passes at the base and at the head.
- `node tests/card_drift.mjs origin/main` prints "card_drift: identical in all 45 states". No committed card state has an unmetered learned heat-loss row, so nothing is claimed, and both claim files are byte-identical to the merge base.
- Carry 22's harness at the head: the solve sweep reads `two_zone_max_dkw=0.000000` and `two_zone_max_dcost=0.000000` against `single_zone_max_dkw=4.999993`. So the solve ignores the field in two zones, and the harness is not blind. The sizer reads `two_zone_sysid_steps=1.738,3.386,None`, identical to `single_zone_sysid_steps=1.738,3.386,None`. So sysid uses the field in two-zone mode exactly as it does in single-zone mode, and the carry's premise is false there.

## Figures

Measured at the head named under `## Head` (bbbce602dc4b3374cbb079f3b067ac82365a1ca7), against the merge base 7539d1675.

- Structure: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3` prints `Architecture score: dS +0.0000 NULL`.
- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 12 script(s) run, 21 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh` ran those twelve and the run_always lines; it printed `1 TEST SCRIPT(S) FAILED`, and that one was `tests/entities.py` on the host's `PermissionError: Cannot get task port` in `_hb_stdlib_reads` (Head's host note). Every other script it ran passed: features (`ALL 4660 FEATURE CHECKS PASSED`), config_flow_steps (`ALL 534 checks PASSED`), doc_claims (`ALL 255 checks PASSED`), card (`ALL CARD CHECKS PASSED`), card_drift (`identical in all 45 states`), harness_headers (`ALL 112 HARNESS HEADER CHECKS PASSED`), arch_score_head (`ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`), deployment_shape, layout, plan_view, env_drift `--all` (`NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`), and `claims hygiene: origin/main ok`. `tests/entities.py` re-run through the host wrapper at the head: `ALL 2496 ENTITY CHECKS PASSED`.
- Browser: `node tests/card_browser.mjs` (playwright 1.64.1, macOS) at the head prints `2 BROWSER CHECK(S) FAILED`: `P9 grid: no two text runs share ink` (`20: text "2" x text "3" 2 px of shared ink`) and `P40 every committed card page figure has the size and structure of the page this card draws` (`setup-dark.png: height 714 committed, 720 drawn; setup-light.png: ...`). The same run at the merge base 7539d1675 (a detached worktree) prints both with the same detail: the 20 pairs and the two 714/720 heights. It also prints a third, `P9 grid: every cell mounted ...` (`threw 3: page.screenshot: Timeout 30000ms exceeded.`), at load average above 50. So both head reds are the base's. Neither involves the Health renderer: the P9 pairs are digit ink, and P40 is the Setup page's committed picture on this host's fonts. CI's browser job decides both. Every UX-HEALTH browser check passes at the head.
- The history census (the class rule, wider than the check): `python3 hist.py`, a scratch probe with sha1 b90a1d15e93266bef6269ef48a9bf5863749124c, run from the tree root, walks every string leaf of strings.json, en.json and sv.json for en `used to|as before|no longer|previously|until now|formerly|anymore|any more` and sv `som tidigare|tidigare var|brukade|inte längre|hittills|förut|var resten`. At the merge base it prints 63 hits: 34 `used to`, 10 `no longer`, 8 `as before`, 3 `förut`, 3 `inte längre`, 2 `until now`, 1 each `brukade`, `som tidigare`, `var resten`. At the head it prints 48: the 15 removed are every history hit (the 8 `as before`, the 2 `used to be`, the 3 `förut`, 1 `som tidigare`, 1 `var resten`). Each of the 48 left is disposed as current behaviour. 30 are `used to <verb>` as instrument ("Used to read your hourly electricity prices", the pump switch, the floor return, the wood tank, window area, PV peak, daily consumption, shower flow). 2 are `cop_degradation`'s "than it used to under the same conditions", and its sv `brukade` is 1: a measured comparison the repair reports. 10 `no longer` and 3 `inte längre` are repairs' runtime states. 2 `until now` are `pump_mode_unreadable`'s runtime history.
- Carry 22's census, of every production reader of the field: `grep -nE "\.heat_loss_coefficient\b" custom_components/heatpump_optimizer/*.py` prints 17 sites (battery 1, coordinator 3, optimizer 5, sysid 4, thermal_model 4). 15 are guarded single-zone branches: battery.py:274; coordinator.py:1221, 4875 and 5200; optimizer.py:361, 2126 and 2265; sysid.py:179 and 1242; thermal_model.py:572, 1852, 3257 and 3729. optimizer.py:3440 and 3443 form `forecast_heat_loss_factors` as `effective(u)/u`, which does not depend on u. sysid.py:1355's value is overwritten under `plant.two_zone_enabled`. **sysid.py:338** (`HousePlant.of_params`) has no branch and is live on two zones, which is what the harness's sizer arm measures. Carry 22: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_two_zone_hhl_inert.py` prints the five RESULT lines under Null control.
- Demand-overbook (carries 11, 20): `dev/audit/harnesses/r10_demand_overbook.py` measures the learner, and this diff changes no Python file under `custom_components/` (`git diff --name-only 7539d1675...HEAD -- 'custom_components/*.py'` prints nothing). The harness therefore reads flat at both ends by construction and was not re-run. The companion applying the card's rule to the same input class is `card.mjs`'s bar check and its metered null.

## Unpinned sites

none

## Red checks

none

## Forward-carry

- **Carry 22 needs the sysid sizer first.** `HousePlant.of_params` (`sysid.py`) sets `ua=p.heat_loss_coefficient * p.house_heat_loss_scale` and `capacity=p.room_thermal_mass` with no two-zone branch. Two-zone installs therefore size the step from the whole-house coefficient, which every other reader treats as unused there (the census in Figures). The step's own prior (`_slab_prior`, under `plant.two_zone_enabled`) uses `_zone_heat_loss` and the zone masses, so the sizer and the prior describe two different houses. The fix: the sizer reads the zone loss (and, to be checked, the zone masses) on a two-zone plant. After that the options flow hides `house_heat_loss_coefficient` in two-zone mode through a `when=` row. `ThermalParameters.from_config`'s two-zone rule moves to a module function that both read, so the page and the model cannot disagree. Control: `dev/audit/harnesses/r10_two_zone_hhl_inert.py` must print one distinct value in `two_zone_sysid_steps` (it prints 1.738,3.386,None here), with `single_zone_sysid_steps` still moving (the null). `room_thermal_mass` through the same constructor may be the same shape for `house_thermal_mass`; that is not measured here. Destination: the orchestrator, for a group owning `sysid.py` with an after-edge into R10-UX-HEALTH's carry 22 (no open group in this seat's roster owns the sysid sizer). Carry: R10-UX-HEALTH
- **The docs copy of the same phrase.** `docs/configuration.md`, the "Heat pump operating mode" row, ends "exactly as before". That is the same history phrase this diff drops from `heat_pump_mode_entity`, and it is outside this group's files. The two price rows there already describe current behaviour. Destination: R10-USER-DOCS-FINAL, whose design (be9f30ec9) raised udf-strings-history. Carry: R10-USER-DOCS-FINAL

## Friction

- `carry-audit: unenforced`: the brief names `tools/audit/seat/carry_audit.py`. No ref holds it (`git log --all -- tools/audit/seat/carry_audit.py` is empty), so the carries were audited by hand against the #2976 and #2997 bodies and diffs, carry by carry (Carries below). Carry: R10-UX-HEALTH
- `finding-propagation: unenforced`: #2997's Forward-carry names a `null_for` pre-check for `tools/pr/ci_predict.py`, with "Destination: the R10-UX-HEALTH group's `carry` list ... which does not hold it yet; the orchestrator writes it". The group's carry list at handoff/audit-r10-roster 2fd6806cfa1abe88cd078d11e8fb1f0f744182c1 has 22 entries and none of them names `null_for`. So it reached no brief. It is not this part's to build, because no carry asks it, and it is recorded here so it is not lost. Carry: R10-UX-HEALTH

## Carries

Each of the roster group's 22 carries (handoff/audit-r10-roster 2fd6806cfa1abe88cd078d11e8fb1f0f744182c1, the same 22 as at 3bf1b487e when the work began), by number. "#2976" is 559134e96942999722526c92bde663ce04a324fe, "#2997" is 05be22881b1e63221da6ccec9604c0371969c9c0.

- Carry 1 (item 6, gains at 03:00): a lead to D2 and D15, not owed here (#2976).
- Carry 2 (reviewer with browser screenshots): the reviewer's. `tests/card_browser.mjs` result in Figures.
- Carry 3 (no URL into an options step; PENDING rows): answered by #2976.
- Carry 4 (no disabled-only filter): answered by #2976 (copy narrowed, Show links the entry's entities).
- Carry 5 (P08, P41 card test gaps): answered by #2976 and #2997.
- Carry 6 (reuse `open_options`): disposed by #2976 (not taken; the design rules item 4 wins).
- Carry 7 (pipelined design): satisfied; design/R10-UX-HEALTH e6797ca9d.
- Carry 8 (null-as-0 Advisor rows): answered by #2976.
- Carry 9 (the waiting score's reasons): answered by #2976.
- Carry 10 (learner_progress): answered by #2976.
- Carry 11 (no power meter: unobservable, not a trusted learned scale): the text by #2976; the full learned bar beside it, here.
- Carry 12 (#2809): answered by #2976 and #2997 (`debug_collect_start`).
- Carry 13 (#2815): answered by #2976 (Start on the Health row).
- Carry 14 (hover spec; the "driving scale"): the hover spec by #2976 and #2997. The "driving scale" stays open on the orchestrator's confirmation (#2997). Carry: R10-UX-HEALTH
- Carry 15 (HEAT-METER rows, `unaligned_meters`): answered by #2976.
- Carry 16 (span codes): answered by #2976.
- Carry 17 (P9 storage reset): open, waiting on an after-edge for the chart ink (#2997). Carry: R10-UX-HEALTH
- Carry 18 (span strings, restated): as carry 16.
- Carry 19 (sv.json wood labels): answered by #2976.
- Carry 20 (#2499's residual Health line): as carry 11; the line and its bar now both say unobservable.
- Carry 21 (udf-strings-history): answered here, with the `heat_pump_mode_entity` sibling.
- Carry 22 (two-zone `house_heat_loss_coefficient`): open; the field is not inert (sysid's sizer reads it), see Forward-carry. Carry: R10-UX-HEALTH
