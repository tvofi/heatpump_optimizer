<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: when a diff added a guard, clamp, removable return or constant with no ledger disposition, the `mutation` lane refused it with "N unpinned site(s) against M at the ratchet base". A seat then had to measure each site by hand and write its `killed_by` entry. That happened on pull requests and on pushes to `main`. The census is in the project's `ci-autofix/ANALYSIS.md`.

After: `python3 tests/mutation_table.py --pin-killed --base <ref>` drives exactly the sites the diff added unpinned. It records a `killed_by` entry for each one a driver kills, naming the driver and the two runs. The refusal message now names this command.

A kill is a measurement, so recording one asserts nothing the run did not see. A survivor is never written: it stays unpinned, and the ratchet stays red until a seat writes a killing check or a `survivor_triage` verdict.

A ledger entry covers every site under its anchor, and a clamp's `max(` and `min(` drops share one. So an anchor is pinned only when **every** site the inventory holds under it was driven and killed. A killed twin beside a surviving one pins neither.

How:
- **Which sites:** `base_unpinned` is split so `base_unpinned_sites` returns the base's unpinned list. `new_unpinned` takes the anchors unpinned here and not there, so a site the diff only moved is not re-measured.
- **Driving them:** the pool is those sites, driven through the sampled table's own baselines, null control, `drive_pool` and `killed()`. The kill's own run is kept (`kill_runs`), so each entry carries the rc and failed-check counts it was earned on.
- **Deciding the pins:** `pin_results` groups the results by anchor, pins an anchor only when every inventory site under it has a kept kill run, and returns exit 1 while anything is left.
- **Writing the ledger:** it goes through `normalize`, so it stays in canonical form.
- **Pins:** `tests/entities.py` pins `new_unpinned` and `pin_entry`, and pins `pin_results` by behaviour: a kill, `LIVES`, `SKIP-MOVED`, a mixed twin pair, a both-killed pair, an undriven twin, and a kill verdict with no run. It also pins the wiring.

This touches `tests/mutation_table.py`, a code-owned path.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`e416e14e5d01a23a1c085ece31a446d665133215`

The review fix is commit `e416e14e`. The handoff commit after it only carries this body.

## Mutation proof

Each of these turned `tests/entities.py` red with `FAIL --pin-killed pins an anchor only when every site under it was killed, and exits 1 with any left`. Restored, it printed `ALL 1869 ENTITY CHECKS PASSED`.
- the review's S1: a verdict with no kept run falls back to a baseline run, so a survivor is pinned;
- the review's S2: `pin_results` returns 0 with sites left;
- an anchor pinned when any one of its sites was killed;
- an anchor pinned without checking that every inventory site under it was driven.

The first round's proof still holds. I made `new_unpinned` return every unpinned site (`return list(unpinned)`). `tests/entities.py` then went red: `FAIL --pin-killed drives only the sites the diff added and records the measured kill`, with `1 of 1868 ENTITY CHECKS FAILED`. Restored, it printed `ALL 1868 ENTITY CHECKS PASSED`.

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
