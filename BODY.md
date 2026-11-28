R11-WHATIF-PAIR-SCATTER, Carry 0, review item f9a20486 (carried from R11-SEAM-cycle-solve), is built here, both halves: a hot-water window, quiet-hours or wood-slot ask the card sends with no comfort target moved takes the steady pair (`whatif.schedule_days` returns None), and nothing measured its hour scatter. Arm `alone` of `dev/audit/harnesses/r11_advisor_measures.py` measures it; `docs/dashboard-card.md` named the hour scatter for the comfort weight and the floor only, and now names it for every two-plan figure, and lists those asks among the two-plan ones.

The arm could not run on main as it stood: 1c935b8d8a (D9-s1-04) made `schedule_days` take `whatif.reference_days`'s output, and the harness callers still handed it `(optimizer, inputs)` pairs, so it compared two optimizer objects. The `asks` arm and `r10_advisor_steady_seams.py pair` therefore raised AssertionError, and the `valve` arm raised TypeError, at the base. The three harness files (`r10_advisor_residue.py`, `r10_advisor_steady_seams.py`, `r11_advisor_measures.py`) now call `whatif.reference_days` first, the way `async_simulate` does.

Precondition the carry names: the card still sends these asks with the comfort fields unchanged. `overrides()` in `www/heatpump-optimizer-card.js` sends `target_temp`, `comfort_temp_day`, the day hours, `dhw_windows`, the quiet fields and `wood_slots` together, so an edit to a window, a quiet row or a slot alone moves no setpoint. Each row of the arm asserts the pair branch. The carry's control, the asks arm with these overrides added beside the pair asks, is arm `alone`, whose reference row is the `asks` arm's comfort-weight ask.

Alternatives: pricing these asks at several hours inside `whatif.py` (an average over asking hours) would remove the scatter rather than describe it. But it costs several extra solves for every ask, which the user slot (`SIMULATE_MIN_INTERVAL_SECONDS`) and the P10 budget the cycle-solve group settled do not cover, and it changes the figure the panel, the cap tile and the fuse advisor read. That makes it a design change outside an S group, and R11-SEAM-cycle-solve's design excluded it. This change measures and documents; it moves no production line.

## Head

1a9f4b04dadd85c315470df02aec58b9b4a1d083, on origin/main a59a1b0d9ac782fabbe01eb84f4d4ff5a17aee43, 2026-11-28T18:38Z.

## Mutation proof

No production line is added (`custom_components/` is untouched), so `prepr.sh`'s mutant draw has no site. Mutation of the harness fix: revert the `whatif.reference_days` wrap, which is the base's text. At a59a1b0d9a `python3 dev/audit/harnesses/r11_advisor_measures.py asks` exits 1 with AssertionError, `valve` exits 1 with TypeError, and `r10_advisor_steady_seams.py pair` exits 1 with AssertionError. At the head all three exit 0 with their RESULT lines. No in-tree check reads the card page's sentence: `tests/doc_claims.py` passes either way, so the doc correction is pinned by the arm's output, not by a check.

## Null control

Arm `alone`, row `null: dhw_windows 06-08:30,17-22 resent`: the live window spec sent back reads +0.0 or -0.0 at every one of the six hours. That is the pair's own resolution, against which the other rows' scatter is read. Reference row `comfort_weight 5 to 2.5` reproduces the scatter the page already named (both signs). At the base the arm does not exist (`KeyError: 'alone'`).

## Figures

Every command runs from the tree root with `PYTHONPATH=tests/hastub:tests:custom_components`, at the head unless named; the harness is the tracked file, sha1 dd889de43d00b9780f1f98cb0fa7545df2823577. Hours 01, 05, 09, 13, 17 and 21, tanked house, tank 52 °C, held start; a month's money in the fixture's price unit. "both signs" is `min < 0 < max` over the six hours; "largest over smallest" is `max|f| / min|f|`, printed as inf when `min|f| < 0.05`.

- `python3 dev/audit/harnesses/r11_advisor_measures.py alone`, reference `comfort_weight 5 to 2.5`: both signs True, range -53.7..+2.2
- same command, `dhw_windows 06-08:30,17-22 to 17-22`: both signs False, range +10.5..+61.6, largest over smallest 5.9
- same command, `dhw_windows to none`: both signs False, range -57.3..-6.9, largest over smallest 8.3
- same command, `quiet off 16-19`: both signs True, range -16.7..+8.8
- same command, `quiet silent 16-20 at half power`: both signs True, range -0.1..+18.5
- same command, `wood 40 l over 2 h, 3 h ahead`: both signs False, range +241.0..+351.7, largest over smallest 1.5
- same command, null `dhw_windows 06-08:30,17-22 resent`: range +0.0..+0.0
- `python3 dev/audit/harnesses/r11_advisor_measures.py asks`, `valve` and `python3 dev/audit/harnesses/r10_advisor_steady_seams.py pair`: exit 1 at a59a1b0d9a (AssertionError, TypeError, AssertionError), exit 0 at the head

A window narrowed to the evening reads as a cost at every hour. That is consistent with the model, not against the ask: `ThermalParameters._windowed_draw_pattern` puts the day's draw inside the windows, so dropping the morning window moves its draw into the evening.

Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED` and selects `tests/doc_claims.py`, `tests/harness_headers.py` and `tests/md_tables.mjs`; each passed at the head.

## Red checks

none

## Forward-carry

none

## Friction

none
