Design review: approve 080231bbfd580815e13811e5a2abcaf3e71952d2

Round 3. I read design.md at 080231bbfd in a detached worktree. I checked the code at 030a4d377f, the payload base. The note's base 824a016f75 is an ancestor of 030a4d377f, 112 commits back. Between the two, draw_range.py, sensor.py, store.py, pump_arbiter.py, coordinator.py and tests/golden/ have no diff. Group credited: outside pull request 3529 by Bankaifan.

## Round-2 revise point 1 (golden-unclaimed): answered

- The set is right. At 030a4d377f, `git grep -l '"pump_max_power_source"' -- tests/golden/` returns exactly coord_all_features, coord_dhw, coord_grid_fee, coord_minimal and coord_two_zone.
- The mechanism is right. `_pump_max_power` (sensor.py:2093-2105) writes its source and reason as `b.get(...)` even when there is no band, so three new keys land as null in every coord capture. Today's three sit at tests/golden/coord_minimal.json:1903-1905. tests/golden.py:1488 reports a key missing from the fixture as "new field". `data.pump_max_power` (coord_minimal.json:465) carries no floor key, so it stays null.
- The write follows R10-COP-GATE-D (claimed_drift.txt:744-753): the five committed files are spliced in those paths alone and claimed ADDED under the live `claims-for:`, with no `--record` run. claims-for is 10.0.2 at the base, equal to VERSION; the note leaves both untouched. card_claimed_drift.txt stays byte-identical.
- Null control (a) is restated: each fixture's diff is only the three added null keys.
- The note supersedes the parent note's "moves no golden" sentence for group C.
- Correction to my round-2 verdict: the parent branch does not claim coord_all_features. fix/r11-outside-honest-starts-runs, re-read at 1c3417a151, claims only cycling_cost and everything_on, as the note says. The claimnotes-driver sentence stays as the merge order.

## Notes v2a, v2b, v2c: folded

- v2a: the "unexceeded" code reads "does not clearly exceed it", which is true on both sides of configured. Test 7 reaches it from a statistic within tol and from one below (1 - tol) x configured. The "measured" text holds because the update rule gives F set only when F > (1 + tol) x configured.
- v2b: the two min codes join `_cpd_codes` (tests/features.py:87854). Its loop runs over strings.json plus SHIPPED_CATALOGUES, so de is covered.
- v2c: the D6 register is rerun at the head.

## Convergence claim (carry 1): attacked a third time, held

The shape is unchanged since round 2: E taken at the floor in force, n reset on every move, no age lapse, moves only by more than a factor 1 +- tol, applied as min(F, top). The argument from rounds 1 and 2 stands: a monotone sequence, bounded, moving by fixed ratios, and g_f(f) = m through `_band_kw` mapping on `planned_min_kw` (pump_arbiter.py:702). The alignment paths are tested in test 6. The golden splice touches neither E nor its statistic.

## Decision still routed (not a revise point)

- decision: orchestrator. Whether C also raises a notice through issues.py (brief bindings 1 and 4). The note designs none and gives a fallback shape; ruling c2 moved the plan-moving arm into scope and leaves the notice to the orchestrator.

## Notes for the fixer (carried observations)

- The carry-6 check's label text (tests/features.py:87868, "in strings.json, en and sv") under-describes a loop that also covers de. When test 7 extends it to the min codes, make the label name the four files it checks. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item v3a)
- Group C claims the five coord fixtures, and any other group that adds a key to the model status entity before C lands moves the same five. Before the handoff, re-run `git grep -l '"pump_max_power_source"' -- tests/golden/` and env_drift --all at the fixer's own merge base. Splice and claim whatever set that returns, not the note's list. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item v3b)

## Checked and clean

- Seam: draw_range.py is still the one owner. The update and the store reader are module-level, `_run_asked` gains keyword bounds whose defaults are today's, and there is no second sample store.
- Siblings: archive/design/R10-DRAW-MAP-EVIDENCE is not on main; the seam is textual only.
- Cited lines re-measured at 030a4d377f: sensor.py:2093-2105, the four `learning_model_status` blocks at line 2154, and tests/entities.py:13063-13066.
- Size: still M. The design adds the five golden splices and one claim block, with no new code file.

Token count: not reported by this harness.
