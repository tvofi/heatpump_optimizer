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

`8b8b0f2a3caec204474c9799ef73b01065d6b34b`, branch `handoff/r10-configflow-c`. It is one merge commit of `origin/main` at `0265f524e9d4810ee179a58d7f5471151ba1cd22` into the round-2 reviewed code head `fc17b2560857a7da6ce11986c979e314180b56f2`. That repairs the `verdict/2915` `e9eb5259a` block, merge-conflict in `tests/config_flow_steps.py` after arm A (#2912, `ba19d13c4`) merged. The merge base with `origin/main` is now `0265f524e`, and at 2026-10-29T01:51Z `origin/main` is still `0265f524e`. Every figure below was re-taken on this merged head, three-dot against `0265f524e`, with `/opt/hpo/venv-ci/bin/python3` (Python 3.14) first on `PATH` and `PYTHONPATH=tests/hastub`. Figures from earlier rounds are named as such.

**The resolution (orchestrator.md section 6, union).** Both sides of each conflicted hunk are kept whole:
- After this PR's `setup_widgets_are_the_registry_rows` (with `NON_FORM_SETUP_STEPS` and `_schema_leaves`), the merged file carries arm A's `PAGE_REJECTIONS`, `_page_stored_entities`, `options_rejected_page_rerenders_the_clear` and `options_cleared_price_entity_is_refused`.
- `main()` awaits all three checks, in this order: `setup_widgets_are_the_registry_rows`, `options_rejected_page_rerenders_the_clear`, `options_cleared_price_entity_is_refused`.
- Read-back of the merged file: `diff <(git show origin/main:tests/config_flow_steps.py) tests/config_flow_steps.py | grep -c '^<'` prints `0`, so no main line is lost. Against `fc17b2560`'s file it prints `3`. Those 3 are the lines arm A rewrote in the non-conflicting `stored_price_entry` check ("an untouched stored price sensor satisfies the entity source and is kept"). The branch never touched those lines: `diff b0b2d7697 fc17b2560` over the file changes only lines 7330-7408 and 7454. Git took main's side there automatically.
- `tests/structure_budgets.json` was merged by the ledger driver. This PR merges second of arms A and C, so it owes the merged-tree measurement: `python3 tests/structure.py` on this head reads `RESULT class_excess_loc=17875`, `ok class_excess_loc 17875 <= 17875`, `STRUCTURE RATCHET PASSED`. The merge commit's message quotes the same figure.
- `config_flow.py` merged without conflict.

## Mutation proof

The failing test came first, in round 2. At `f74f6cbb2`, the repaired census read `1 of 508 checks FAILED` (`2 spelled twice: ['reauth:tibber_token', 'reauth_confirm:tibber_token']`), and it read `ALL 508 checks PASSED` after the production change. That is the round-2 record, not re-taken here.

Re-executed on this merged head, where the unmutated baseline is `ALL 534 checks PASSED` with rc 0 (508 from this branch, plus arm A's checks). Each mutant was applied in a separate worktree at this head and run with `python3 tests/config_flow_steps.py`. The file was then restored with `git checkout`, and `git diff --quiet` confirmed it was clean:
- M1, the blocked site. `reauth_confirm`'s widget goes back to its own `selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))`. Result: rc 1, `1 of 534 checks FAILED`, `no setup field spells a second widget ... [2 spelled twice: ['reauth:tibber_token', 'reauth_confirm:tibber_token']]`. Killed.
- M2, the census precondition. `reauth_confirm` returns `async_abort(reason="mutant")` before its form. Result: rc 1, `7 of 534 checks FAILED`. These include `the setup-widget census renders every step but the declared non-form ones [unrendered=['reauth:no form', 'reauth_confirm:no form'] steps=18]` and `the setup-widget census reaches every registry-backed setup field [registry-backed setup fields=64]`. Killed.
- M3, the whole fix. `config_flow.py` is replaced by `origin/main`'s (`0265f524e`: arm A in, this PR out) under this head's tests. Result: rc 1, `1 of 534 checks FAILED`, `66 spelled twice`. Killed.

## Unpinned sites

none: `python3 tools/pr/ci_predict.py --base origin/main` lists no unpinned site the diff adds.

## Null control

- M1 under main's tests. The M1 mutant was run with `origin/main`'s `tests/config_flow_steps.py`, which has arm A's checks but not this PR's census. Result: rc 0, `ALL 531 checks PASSED`. Main's file has none of the census's 3 checks (534 - 3 = 531), and the second reauth widget is invisible to it, so the kill above comes from this PR's census, not from the run itself.
- The finder's harness at `origin/main` reads the defect (`spelled_twice=44`, below), and at this head it reads 0. The difference comes from this diff, not from the harness.
- `disagree=0` and `golden_equal=1` at this head (harness, below). No golden moves, and both claim files are byte-identical to the merge base.

## Figures

All figures in this section were re-taken on this merged head unless they are marked as from round 2.

- **The class rule** (fixer.md step 8): `sorted(n for n in dir(HeatPumpOptimizerConfigFlow) if n.startswith("async_step_"))`. It returns 18 steps (`steps=18` in M2's detail). That is the census's domain:
  - 15 steps render a form and are checked.
  - `building` and `finish_setup` are menus.
  - `reconfigure` aborts without a sourced entry, and its form is `user`'s, which is checked.
  - `reauth` and `reauth_confirm` were missing from the old hand-kept list. Both were closed in round 2, and M1 confirms they stay closed at this head.
  - The options flow renders from `_OPTION_FIELDS` itself. The merge brings in arm A's options-page checks, but no new `async_step_*` on `HeatPumpOptimizerConfigFlow` (still 18).
- **The finder's harness**, `wizard_widgets.py` from `3930b421a` (`$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`, sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`). It was copied into a `git archive` of each tree and run as `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py [--all | --bump heat_pump_cop_nominal]`:

  | arm | this head | `origin/main` `0265f524e` (the merge base) |
  |---|---|---|
  | plain | `wizard_fields=46 in_registry=44 spelled_twice=0 disagree=0 golden_equal=1` | `spelled_twice=44 disagree=0` |
  | `--all` | `other_wizard_fields=38 other_in_registry=20 other_spelled_twice=0 other_disagree=0` | `other_spelled_twice=20` |
  | `--bump heat_pump_cop_nominal` | `spelled_twice=0 disagree=0` | `spelled_twice=44 disagree=2` |

- **`tests/config_flow_steps.py`** at this head: `ALL 534 checks PASSED`, rc 0. That includes `the setup-widget census renders every step but the declared non-form ones`, `... reaches every registry-backed setup field`, `no setup field spells a second widget for a setting the options registry declares`, arm A's nine `a rejected <page> submit re-renders each cleared stored entity empty` checks, and `switching to Tibber with a token saves it and nulls the cleared price entity`.
- **The scoped gate.** `python3 tests/closure.py select --diff 0265f524e --workdir $D` prints `MODE: SCOPED -- 13 script(s) run, 20 scoped out.` over 4 changed files:
  - `custom_components/heatpump_optimizer/config_flow.py`
  - `dev/programme/delivery/2915.md`
  - `tests/config_flow_steps.py`
  - `tests/structure_budgets.json`

  Every script `scope.run` names exits rc 0, run with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`: `arch_score_head`, `config_flow_steps`, `deployment_shape`, `doc_claims`, `entities`, `env_drift`, `features`, `finite_boundary`, `golden`, `harness_headers`, `manual_plan`, `structure`, `typing_ruler`. So do the `run_always` lines: `env_drift.py --claims-only 0265f524e`, `closure.py selftest` and `layout.py`.
- **Structural ratchet:** `python3 tests/structure.py` reads `STRUCTURE RATCHET PASSED`. `class_excess_loc` reads 17875 against the budget 17875. That is the ledger driver's resolution of arm A's re-record (18038 -> 17992) and this PR's (18037 -> 17921), now measured on the merged tree.
- **Architecture score:**
  - `python3 tools/audit/archscore/score.py --diff origin/main` reads `Architecture score: dS +0.5850 IMPROVES`, `literal_clone_copies 185 -> 123`. That is the same delta as at round 2, against the new base.
  - `--diff fc17b2560` reads `dS +2.3483 IMPROVES`, `duplication_copies 35 -> 29`. That delta is main's own content (arm A and the rest) arriving through the merge, not a change this PR authors.
- **CI prediction:** `python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 0265f524e9d4 (a data-file read is not seen)`.
- **Diffstat:** the three-dot `git diff --stat 0265f524e...HEAD` reads `4 files changed, 195 insertions(+), 218 deletions(-)`.
- **Release files:** the branch touches none of `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt`. `git diff --name-only origin/main...HEAD -- <those five> | wc -l` prints 0.

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

none. No check has run on `8b8b0f2a3` yet, and `ci_predict.py --base origin/main` predicts no red. On `196a75a9f` the one red was `governance / delivery-status` (`DELIVERY STATUS OVERDUE` on rows #2921, #2910, #2873 and #2909, none of them this PR's). `verdict/2915` `e9eb5259a` ev/ci_state.txt records it, and the review found it is not this pull request's.

## Forward-carry

- Arm D: drop `device_registry as dr` from the `homeassistant.helpers` import and lower `archscore.unused_boundary_imports` 1 -> 0. Once A, B and C/C2 are merged, re-record `archscore.literal_clone_copies` at the measured value, with the merge-base figure, the head figure and the drop in the commit message. It lands in `dev/programme/rosters/wave-r10-groups.json`, group R10-CONFIGFLOW-PAGES. Carry: R10-CONFIGFLOW-PAGES
- The finder's harness (sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`) exists only at `3930b421a`. It should land under `dev/audit/rounds/round10/D7/arch2-s5/` for arm B's merge resolution and for arm D. This is the review's carry (`verdict/2915`), routed to the same group, and is not landed in this repair, which is scoped to the blocked class. Carry: R10-CONFIGFLOW-PAGES

## Friction

none
