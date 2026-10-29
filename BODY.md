R10-CONFIGFLOW-PAGES (Product UX, L), arms C and C2, the third of the group's pull requests in the approved design's order (`design/R10-CONFIGFLOW-PAGES` `32892dc67`, `dev/programme/designs/R10-CONFIGFLOW-PAGES.md`; approve verdict `design-verdict/R10-CONFIGFLOW-PAGES` `3af84d776`). Finding ARCH2-s5-F1 of #2238's group, fixed here. Arms A and B are their own pull requests, and arm D (the carried tripwires) follows, so this one closes nothing.

**The finding (ARCH2-s5-F1).** The setup wizard and the options flow ask about the same settings, and the wizard built each widget a second time instead of taking the one `_OPTION_FIELDS` declares. The finder's harness reads `wizard_fields=46 in_registry=44 spelled_twice=44` at the base. Its `--all` arm adds `other_spelled_twice=20` on the first screens (user 4, user_sensors 14, quick_setup's wood probes 2). Every copy agrees today (`disagree=0`), but nothing keeps them agreeing: `--bump heat_pump_cop_nominal` (the registry's max doubled) gives `disagree=2`, because building_extras and thermal keep their own copy.

**The fix.**
- **Arm C** (the finder's F1). `_wizard_fields(marker, defaults)` returns `{marker(key, default=d): _prefill_row(key).widget}`, and building_extras and thermal share `_NAMEPLATE_DEFAULTS`. The six wizard pages take all 44 widgets from their rows. Defaults and markers stay the wizard's own.
- **Arm C2.** The same move on the 20 first-screen widgets (`_user_credentials_fields`, `_user_sensors_fields`, `_quick_setup_schema`'s two wood probes), as a value swap to `_prefill_row(KEY).widget`, with markers and defaults untouched. The design's spike spelled the lookup `_registry_widget(K)`, a second helper over the same `_OPTION_FIELDS` scan. This diff uses the existing `_prefill_row(K).widget`, which the design's C2 text names, so no lookup is duplicated.

- **Repair after the fix review** (`verdict/2915` `4ccdc435b`, blocked at `f74f6cbb2`, class-open: `reauth_confirm`'s `tibber_token` spelled a second widget). `async_step_reauth_confirm` now renders `_prefill_row(CONF_TIBBER_TOKEN).widget`. The one-off `_tibber_token_selector()` factory is deleted and its `TextSelector(PASSWORD)` sits inline on the `CONF_TIBBER_TOKEN` registry row, so the row is the only place that can build that widget. The class was open because the test's domain was a hand-kept list, `SETUP_FORM_STEPS`, which left out `reauth` and `reauth_confirm`. That list is replaced by every `async_step_*` of `HeatPumpOptimizerConfigFlow`, minus a declared `NON_FORM_SETUP_STEPS` (`building` and `finish_setup` are menus; `reconfigure` needs a sourced entry and hands its form to `user`). The census asserts that every other step renders a form, so a step added later joins the census without being listed.
  - Alternatives considered: (a) add `reauth_confirm` to the hand list. It closes this instance and leaves the domain hand-kept, which is how this one escaped. (b) Keep `_tibber_token_selector()` and call it once, from the row. That keeps a factory a later form could call again for a second widget. Both lost.

One setting now has one selector object in both flows and in reauth, which the identity test checks.

**Conflict with arm B, for the merge.** Arm B (`handoff/r10-configflow-b`) rewrites the marker side of `_quick_setup_schema`'s two wood probes (`_suggested_entity(K, current)` -> `_suggested_optional(current, K)`), while this diff rewrites their value side. The design's resolution keeps both sides: `_suggested_optional(current, K): _prefill_row(K).widget`, for `CONF_WOOD_TANK_TOP_ENTITY` and `CONF_WOOD_TANK_BOTTOM_ENTITY`. That is the tree the design reviewer measured at dS +3.3700 (A+B+C+C2). Whichever of the two merges second takes that resolution, and the quick-setup and `_field_marker` checks plus `wizard_widgets.py --all` (`other_spelled_twice=0`) are re-run on the merged tree.

## Head

`fc17b2560857a7da6ce11986c979e314180b56f2`, branch `handoff/r10-configflow-c`. It is one repair commit on the reviewed head `f74f6cbb23649562bcc3db7f6415334707b1fd23`, whose merge base with `origin/main` is `b0b2d7697f8c5baaef2c082d9bf3242b57249e68`. At 2026-10-28T23:52Z `origin/main` is at `6493ea3625900f8361011e0c8f2a3c66885ce7b1`, and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged (fixer.md step 6). Every figure below was measured on this head, three-dot against `b0b2d7697`, with `/opt/hpo/venv-ci/bin/python3` (Python 3.14.7) first on `PATH` and `PYTHONPATH=tests/hastub`.

## Mutation proof

The failing test came first. At `f74f6cbb2`, with the repaired census in `tests/config_flow_steps.py` (`setup_widgets_are_the_registry_rows`, driving every `async_step_*`) and that head's `config_flow.py`, the run read `1 of 508 checks FAILED`: `no setup field spells a second widget for a setting the options registry declares [2 spelled twice: ['reauth:tibber_token', 'reauth_confirm:tibber_token']]`, rc 1. After the production change it reads `ALL 508 checks PASSED`, rc 0.

Each mutant below was applied to this head, run with `python3 tests/config_flow_steps.py`, and restored:
- M1, the blocked site. `reauth_confirm`'s widget goes back to its own `selector.TextSelector(selector.TextSelectorConfig(type=PASSWORD))`. Result: `1 of 508 checks FAILED`, `2 spelled twice: ['reauth:tibber_token', 'reauth_confirm:tibber_token']`. Killed.
- M2, the census precondition. `reauth_confirm` returns `async_abort` before its form. Result: `7 of 508 checks FAILED`, including `the setup-widget census renders every step but the declared non-form ones [unrendered=['reauth:no form', 'reauth_confirm:no form'] steps=18]` and `... reaches every registry-backed setup field [registry-backed setup fields=64]`. Killed. A step that stops rendering cannot pass the identity check vacuously.
- M3, the whole file. `config_flow.py` at the merge base `b0b2d7697`, run under this head's tests. Result: `1 of 508 checks FAILED`, `66 spelled twice`. That is 44 wizard fields, 20 first-screen fields and the 2 reauth fields. Killed.
- The round-1 mutants (`copy.copy` in `_wizard_fields`, the single `weather_entity`, wood-probe and `dhw_windows` sites) were killed at `f74f6cbb2` (`verdict/2915` ev/m1..m4). This repair leaves those lines alone, and the new census's domain is a superset of the old list's.

## Unpinned sites

none: `python3 tools/pr/ci_predict.py --base origin/main` lists no unpinned site the diff adds.

## Null control

- M1 under the old domain. The M1 mutant was run with `f74f6cbb2`'s `tests/config_flow_steps.py`, which still has the hand-kept `SETUP_FORM_STEPS`. Result: `ALL 507 checks PASSED`, rc 0. The second reauth widget is invisible to the old list and caught by the new one, so the kill comes from the domain change and not from the run itself.
- `golden_equal=1` from the finder's harness at this head, and `tests/golden.py` passes under `GOLDEN_MODE=drift` against `b0b2d7697`. No golden moves. Both claim files are byte-identical to the merge base, so nothing is claimed.
- `disagree=0` from the finder's harness at this head. The repair changes which object renders, not what the object is (`token_surfaces_agree`'s `the three tibber_token surfaces agree on the same mask` passes).

## Figures

- The class rule (fixer.md step 8): `sorted(n for n in dir(HeatPumpOptimizerConfigFlow) if n.startswith("async_step_"))`. It returns 18 steps, which are the census's domain (`steps=18` in M2's detail). Each step's disposition:
  - 15 render a form and are checked.
  - `building` and `finish_setup` are menus with no fields.
  - `reconfigure` aborts without a sourced entry, and its form is `user`'s, which is checked.
  - The reviewer's census (`verdict/2915` ev/census_all_steps.py, run unchanged at this head) reads `all_steps_registry_fields=66` and `all_steps_spelled_twice=0`. It read `2` at `f74f6cbb2` (`reauth:tibber_token`, `reauth_confirm:tibber_token`) and `66` at `b0b2d7697`.
  - Two `async_step_*` in `HeatPumpOptimizerConfigFlow` have registry-backed fields but were missing from the old list: `reauth` and `reauth_confirm`. Both are closed in this diff.
  - The options flow is out of this class's domain: its pages render from `_OPTION_FIELDS` itself.
- The finder's harness, `wizard_widgets.py` from `3930b421a` (`$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`, sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`). It was copied into a `git archive` of this head and run as `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py [--all | --bump heat_pump_cop_nominal]`.
  - This head: `wizard_fields=46 in_registry=44 spelled_twice=0 disagree=0 golden_equal=1`.
  - `--all`: `other_in_registry=20 other_spelled_twice=0 other_disagree=0`.
  - `--bump heat_pump_cop_nominal`: `spelled_twice=0 disagree=0`.
  - At the base `6d86acc90` and the merge base `b0b2d7697` (`verdict/2915` ev/finder_harness.txt): `spelled_twice=44`, `other_spelled_twice=20`, and `disagree=2` under `--bump`.
  - The harness does not drive `reauth`. Its `--all` arm reads the first screens only, which is why it read 0 at `f74f6cbb2` while that seam was open. The census above is the instrument for that seam.
- The scoped gate: `python3 tests/closure.py select --diff b0b2d7697 --workdir $D` prints `MODE: SCOPED -- 13 script(s) run, 20 scoped out.` Every script `scope.run` names exits rc 0 (`arch_score_head`, `config_flow_steps`, `deployment_shape`, `doc_claims`, `entities`, `env_drift`, `features`, `finite_boundary`, `golden`, `harness_headers`, `manual_plan`, `structure`, `typing_ruler`). So do `run.sh`'s `run_always` lines here: `env_drift.py --claims-only b0b2d7697`, `closure.py selftest` and `layout.py`.
- `tests/config_flow_steps.py` at this head: `ALL 508 checks PASSED`, rc 0 (507 at `f74f6cbb2`, plus the census-precondition check).
- Architecture score:
  - `python3 tools/audit/archscore/score.py --diff b0b2d7697` reads `Architecture score: dS +0.5850 IMPROVES`, `literal_clone_copies 185 -> 123 +0.5850`.
  - The repair alone, `--diff f74f6cbb2`, reads `dS +0.0000 NULL`. It deletes one function and moves no scored metric.
- Structural ratchet: `python3 tests/structure.py` reads `STRUCTURE RATCHET PASSED` at this head. The re-record in commit `d52036166` writes `class_excess_loc` 18037 -> 17921 in `tests/structure_budgets.json`. That is the file's value: the round-1 body's 18038 -> 17922 was one off at both ends. Arm A re-records the same row, so the second of the two to merge re-measures it on the merged tree and quotes the file's value.
- `python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against b0b2d7697f8c (a data-file read is not seen)`.
- Three-dot diffstat: `git diff --stat b0b2d7697...HEAD` reads 4 files changed, 196 insertions(+), 219 deletions(-). The fourth file is `dev/programme/delivery/2915.md`, the orchestrator's row commit.
- The mutation ledger: no file under `tests/`, `dev/` or `tools/` names `_tibber_token_selector` (`grep -rln _tibber_token_selector tests/ dev/ tools/` prints nothing), so its deletion strands no ledger row.
- The branch touches none of `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt`: `git diff --name-only b0b2d7697...HEAD -- <those five> | wc -l` prints 0.

**#2238's findings, each dispositioned.** There is no closing keyword here; the group's last pull request carries #2238's.
- D10-s1-51: fixed by #2290.
- D2-s2-01: fixed by #2365 and #2368.
- D7-s2-01: fixed by #2527.
- D7-s2-51 (weakened), D7-s2-52, D7-s2-53 and D7-s2-54: fixed by #2379.
- D7-s2-55: fixed by this group's arm-B pull request.
- D7-s2-56: fixed by its arm-A pull request.
- D7-s2-57: fixed by #2819.
- D7-s2-59: fixed by #2282.
- D8-s1-01: fixed by #2819.

## Red checks

none. No check has run on `fc17b2560` yet, and `ci_predict.py --base origin/main` predicts none red. On `f74f6cbb2` no check concluded red (`verdict/2915` ev/ci_state.txt).

## Forward-carry

- Arm D: drop `device_registry as dr` from the `homeassistant.helpers` import and lower `archscore.unused_boundary_imports` 1 -> 0. Once A, B and C/C2 are merged, re-record `archscore.literal_clone_copies` at the measured value, with the merge-base figure, the head figure and the drop in the commit message. It lands in `dev/programme/rosters/wave-r10-groups.json`, group R10-CONFIGFLOW-PAGES. Carry: R10-CONFIGFLOW-PAGES
- The finder's harness (sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`) exists only at `3930b421a`. It should land under `dev/audit/rounds/round10/D7/arch2-s5/` for arm B's merge resolution and for arm D. This is the review's carry (`verdict/2915`), routed to the same group, and is not landed in this repair, which is scoped to the blocked class. Carry: R10-CONFIGFLOW-PAGES

## Friction

none
