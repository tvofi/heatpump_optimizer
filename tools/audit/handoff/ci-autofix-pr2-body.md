<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: when a diff added a guard, clamp, removable return or constant with no ledger disposition, the `mutation` lane refused it with "N unpinned site(s) against M at the ratchet base". A seat then had to measure each site by hand and write its `killed_by` entry. That happened on pull requests and on pushes to `main`. The census is in the project's `ci-autofix/ANALYSIS.md`.

After: `python3 tests/mutation_table.py --pin-killed --base <ref>` drives exactly the sites the diff added unpinned. It records a `killed_by` entry for each one a driver kills, naming the driver and the two runs. The refusal message now names this command.

A kill is a measurement, so recording one asserts nothing the run did not see. A survivor is never written: it stays unpinned, and the ratchet stays red until a seat writes a killing check or a `survivor_triage` verdict.

How:
- **Which sites:** `base_unpinned` is split so `base_unpinned_sites` returns the base's unpinned list. `new_unpinned` takes the anchors unpinned here and not there, so a site the diff only moved is not re-measured.
- **Driving them:** the pool is those sites, driven through the sampled table's own baselines, null control, `drive_pool` and `killed()`. The kill's own run is kept (`kill_runs`), so each entry carries the rc and failed-check counts it was earned on.
- **Writing the ledger:** it goes through `normalize`, so it stays in canonical form.
- **Pins:** `tests/entities.py` pins `new_unpinned`, `pin_entry` and the wiring.

This touches `tests/mutation_table.py`, a code-owned path.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AJvUdyMZC5ztrV1UH5FmiH

## Head

`cdd3dd90fd0fbafe78deb4d6d9a7b7a11618a82e`

## Mutation proof

I made `new_unpinned` return every unpinned site (`return list(unpinned)`). `tests/entities.py` then went red: `FAIL --pin-killed drives only the sites the diff added and records the measured kill`, with `1 of 1868 ENTITY CHECKS FAILED`. Restored, it printed `ALL 1868 ENTITY CHECKS PASSED`.

## Null control

I built a probe in a scratch clone:
- a base commit that pins six `open_meteo.py` sites (lines 125, 129, 143, 149, 160, 162);
- a head that reverts those pins.

On that probe, `--pin-killed --base <probe base> --scripts tests/open_meteo.py` printed `PIN KILLED: 3 pinned, 3 left unpinned`.

I then checked each outcome by hand, outside the tool:
- **Line 149, pinned:** turned into `if False:`, it made `tests/open_meteo.py` print `1 CHECK(S) FAILED`.
- **Line 125, left unpinned:** turned into `if False:`, it left `ALL OPEN-METEO CHECKS PASSED`.

After the run, the plain table still refused the three survivors: `MUTATION TABLE REFUSED -- 3722 unpinned site(s) against 3719`. The tool closes the kills, not the ratchet.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
