R10-CONFIGFLOW-PAGES (Product UX, L), arms C and C2, the third of the group's pull requests in the approved design's order (`design/R10-CONFIGFLOW-PAGES` `32892dc67`, `dev/programme/designs/R10-CONFIGFLOW-PAGES.md`; approve verdict `design-verdict/R10-CONFIGFLOW-PAGES` `3af84d776`). Finding ARCH2-s5-F1 of #2238's group, fixed here. Arms A and B are their own pull requests, and arm D (the carried tripwires) follows, so this one closes nothing.

**The finding (ARCH2-s5-F1).** The setup wizard and the options flow ask about the same settings, and the wizard built each widget a second time instead of taking the one `_OPTION_FIELDS` declares. The finder's harness reads `wizard_fields=46 in_registry=44 spelled_twice=44` at the base. Its `--all` arm adds `other_spelled_twice=20` on the first screens (user 4, user_sensors 14, quick_setup's wood probes 2). Every copy agrees today (`disagree=0`), but nothing keeps them agreeing: `--bump heat_pump_cop_nominal` (the registry's max doubled) gives `disagree=2`, because building_extras and thermal keep their own copy.

**The fix.**
- **Arm C** (the finder's F1). `_wizard_fields(marker, defaults)` returns `{marker(key, default=d): _prefill_row(key).widget}`, and building_extras and thermal share `_NAMEPLATE_DEFAULTS`. The six wizard pages take all 44 widgets from their rows. Defaults and markers stay the wizard's own.
- **Arm C2.** The same move on the 20 first-screen widgets (`_user_credentials_fields`, `_user_sensors_fields`, `_quick_setup_schema`'s two wood probes), as a value swap to `_prefill_row(KEY).widget`, with markers and defaults untouched. The design's spike spelled the lookup `_registry_widget(K)`, a second helper over the same `_OPTION_FIELDS` scan. This diff uses the existing `_prefill_row(K).widget`, which the design's C2 text names, so no lookup is duplicated.

One setting now has one selector object in both flows, which the identity test checks.

**Conflict with arm B, for the merge.** Arm B (`handoff/r10-configflow-b`) rewrites the marker side of `_quick_setup_schema`'s two wood probes (`_suggested_entity(K, current)` -> `_suggested_optional(current, K)`), while this diff rewrites their value side. The design's resolution keeps both sides: `_suggested_optional(current, K): _prefill_row(K).widget`, for `CONF_WOOD_TANK_TOP_ENTITY` and `CONF_WOOD_TANK_BOTTOM_ENTITY`. That is the tree the design reviewer measured at dS +3.3700 (A+B+C+C2). Whichever of the two merges second takes that resolution, and the quick-setup and `_field_marker` checks plus `wizard_widgets.py --all` (`other_spelled_twice=0`) are re-run on the merged tree.

## Head

`d520361663649dc2772f5c9be666c857da62a0b2`, branch `handoff/r10-configflow-c`, merge base `6d86acc909f7fc465e5736771daf8fa45c1373a4` (origin/main tip at 2026-10-28T10:23Z). Everything below was measured on this branch over that base, three-dot, with the seat interpreter (Python 3.14.7, `~/.local/state/hpo/venv-ci`, first on `PATH`).

## Mutation proof

The test came first. `setup_widgets_are_the_registry_rows` in `tests/config_flow_steps.py` drives the ten setup form steps through the production handlers. Every field whose key has an `_OPTION_FIELDS` row must deliver that row's widget object (`is`), and the census asserts its own reach (`>= 64` registry-backed fields). With this head's tests over the base's `config_flow.py`: `1 of 507 checks FAILED`, `no setup field spells a second widget for a setting the options registry declares` with `64 spelled twice` (44 wizard fields plus the 20 first-screen ones), rc 1.

- `_wizard_fields`' widget lookup, `_prefill_row(key).widget` -> `copy.copy(_prefill_row(key).widget)` (an equal widget, built a second time): `1 of 507 checks FAILED`, the same check with `44 spelled twice` (the 20 C2 sites take the row's widget directly), at `f20b8ecc2`, whose `config_flow.py` is this head's. The golden still reads equal under that mutant (`wizard_widgets.py` `golden_equal` on the mutant tree: `golden_equal=1`), so only the identity check sees a second construction. That is the defect's shape.

## Unpinned sites

none: `python3 tools/pr/ci_predict.py --base origin/main` lists no unpinned site the diff adds.

## Null control

- `golden.capture_config_flow()` equals `tests/golden/config_flow.json` on both trees: `wizard_widgets.py` reads `golden_equal=1` at the base and at this head. No golden moves, and `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to the base, so nothing is claimed.
- `wizard_widgets.py` `disagree=0` at both ends. The fix changes which object renders, never what it is.

## Figures

- the finder's harness `wizard_widgets.py` from `3930b421a` (`$EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py`, sha1 `66b390554c0aa54c8960eacb532b04ff827ca8cf`), copied into a `git archive` of each tree: `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s5/wizard_widgets.py [--all | --bump heat_pump_cop_nominal]`, with `$EXPORT` the archived tree.
  - base: `wizard_fields=46 in_registry=44 spelled_twice=44 disagree=0 golden_equal=1`; `--all` adds `other_spelled_twice=20 other_disagree=0`; `--bump heat_pump_cop_nominal` reads `disagree=2`.
  - this head: `spelled_twice=0 disagree=0 golden_equal=1`; `--all` reads `other_spelled_twice=0`; `--bump heat_pump_cop_nominal` reads `spelled_twice=0 disagree=0`, because the second copy no longer exists (the finder's perturbation, read at both ends).
  - the `copy.copy` mutant: `spelled_twice=44 golden_equal=1`, `other_spelled_twice=0`.
- `tests/config_flow_steps.py` at this head: `ALL 507 checks PASSED`, rc 0, at `f20b8ecc2` (this head adds only the structure re-record): `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py`.
- architecture score: `Architecture score: dS +0.5850 IMPROVES`, `literal_clone_copies 185 -> 123 +0.5850`: `python3 tools/audit/archscore/score.py --diff 6d86acc909f7fc465e5736771daf8fa45c1373a4`. The design's rows are C +0.4731 (literal_clone_copies 185 -> 133) and C2 +0.1119 more (133 -> 123).
- structural ratchet: `STRUCTURE RATCHET PASSED` after re-recording `class_excess_loc` 18038 -> 17922 (`python3 tests/structure.py --record`; the reason is in commit `d52036166`'s message). Arm A re-records the same row at its own head (17992), so the second of the two to merge re-measures that row on the merged tree: `python3 tests/structure.py`.
- the gate: `PRE-PR: d520361663649dc2772f5c9be666c857da62a0b2 00000000000000000000000000`, `clean no refusal`: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`.
- three-dot diffstat: 3 files changed, 169 insertions(+), 210 deletions(-): `git diff --stat 6d86acc909f7fc465e5736771daf8fa45c1373a4...HEAD`.
- the mutation ledger: no `killed_by` or `survivor_triage` row names a site this diff removes. The stale-row probe (`mutation_table.dispositions` against `mutation_table.inventory` over `config_flow.py`) returns none, so the design's five wizard rows keep their anchors, which this diff leaves in place.
- the branch touches none of `VERSION`, `RELEASE_NOTES.md`, the manifest, `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`: `git diff --name-only 6d86acc90...HEAD -- <those five> | wc -l` prints 0.

**#2238's findings, each dispositioned** (no closing keyword here; the group's last pull request carries #2238's): D10-s1-51 fixed by #2290; D2-s2-01 by #2365 and #2368; D7-s2-01 by #2527; D7-s2-51 (weakened), D7-s2-52, D7-s2-53 and D7-s2-54 by #2379; D7-s2-55 by this group's arm-B pull request; D7-s2-56 by its arm-A pull request; D7-s2-57 by #2819; D7-s2-59 by #2282; D8-s1-01 by #2819.

## Red checks

none: no check has run on this head yet. `ci_predict.py --base origin/main` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 6d86acc909f7`.

## Forward-carry

- Arm D: drop `device_registry as dr` from the `homeassistant.helpers` import, lower `archscore.unused_boundary_imports` 1 -> 0, and re-record `archscore.literal_clone_copies` at the measured value once A, B and C/C2 are merged, with the merge-base figure, the head figure and the drop in the commit message. It lands in `dev/programme/rosters/wave-r10-groups.json`, group R10-CONFIGFLOW-PAGES. Carry: R10-CONFIGFLOW-PAGES

## Friction

none
