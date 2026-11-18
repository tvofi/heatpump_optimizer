Fix review: merge 1c75332e983535262406473761d3b0eecce2f959

bus-nonce: d00576dbf8daaa05ee9c083922199aa9

Round 1 (first review of #3715). Reviewed from detached worktrees at the head `1c75332e983535262406473761d3b0eecce2f959`, the merge base `2c59b3d916` and the code head's base `7ae657e0e2`. The role contracts are current against origin/main: the three-dot diff over `dev/governance/roles/` is empty.

## Evidence

- Mutation proof (step 1), re-run on the features block `# -- the fold and its gates`..`# -- persistence is additive`: the unmutated head prints `ALL 11 FEATURES BLOCK PASSED`. M1 deletes the guard's two lines and fails `R11-VALVE-REFERENCE r1` (the single-zone manual/smart_read/smart_write arms fold 1 sample). M2, the plain `is_throttling` skip, fails it (the two-zone valved arms fold 0). A third mutant of my own, M3 (`and params.two_zone_enabled`), also fails it. The file was restored after each run, so no mutant survives. The ledger's BOOLOP/GUARD_OFF 808d9b0c counts across the whole of `tests/features.py` (failed=11 / failed=2) were not re-run; this cites CI's green `tests / mutation` lane.
- Null control (step 3): the head's `tests/features.py` run on the merge base's production code prints `1 of 11 FEATURES BLOCK FAILED`. Every arm folds 1 sample and `clamped held` is False, which matches the body.
- Two-zone bitwise control (ruling on carry 5; my own instrument, `ev/bitwise_snippet.py`, not the fixer's): I compared the full `_flow_bias.as_dict()` after two folds, for every zone × valve mode × seed (no seed, a bias seeded −50 K onto the clamp, a bias seeded +3 K), at the base and at the head. All 12 two-zone arms and all 3 single-zone no-valve arms are identical. Only the 9 single-zone throttling arms differ, and each holds its seeded bias, neither moved nor reset (`ev/bitwise_base.txt`, `ev/bitwise_head.txt`).
- Class (step 6): the body's rule (`git grep -n "_flow_bias.observe(" -- custom_components`) returns only `coordinator.py:988`, inside `_fold_flow_lift`. The broader `_flow_bias` grep also finds `observe_water` (coordinator.py:6773 → `flow_meter.observe_water` → `FlowBias.observe_temps`). That path writes only `last_supply_c`, `last_return_c` and `heat_output_kw`, never `bias_k` or `samples`. That leaves one fold site, and the diff closes it.
- Rulings: carry 3 is answered as moved to #3713, carry 4 as dismissed with the note's Alternatives reason, and carry 5 is built exactly as ruled, as a single-zone-only skip in `_fold_flow_lift`'s guard. The `supply is None` line is byte-identical. Carry 6 re-derives: `r10_advisor_steady_seams.py fields` at `7ae657e0e2` and at the head is byte-identical (`ev/carry6_*.txt`). `valve, one tank` reads `rows 72 missed 0`, `(a correct zero) 1`, `idle on every moved step ['night-1 21:00']`, and the other three fixtures read `missed 0`, `a correct zero` 0.
- Merge with main (step 13): `git merge-tree --write-tree origin/main 1c75332e98` exits 0, with no conflict.
- Version (step 5): `VERSION`, `manifest.json`, the `RELEASE_NOTES.md` heading and `tests/golden` are untouched. The diff touches no claim file and no golden fixture (step 4), and the gate is green at the head.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, and no budget file is in the diff.
- Architecture score (step 14): `coord_footprint` rises by 2, the ruled guard line. Re-derived: `score.py --diff 2c59b3d916 HEAD` prints `dS -0.0012 WORSENS (coord_footprint 2505->2507)`, and `--diff 7ae657e0e2 56a87b7795` prints `dS -0.0012 (2502->2504)`. The rise is explained under `## Architecture score`, and the `arch-score` check is green.
- Step 16 does not apply: the skip is a learner observation, not an actuator write.
- CI (step 11): `merge_train.py classify 1c75332e98 --pr 3715` prints `GREEN 1c75332e983535262406473761d3b0eecce2f959 pending: none red: none`, read twice, the second time just before return. The packet's `tests / nightly-status` and `tests / replay` failures are outside the `owed-reds` set, so they are neither answered nor a block.
- Head (steps 7, 12): `refs/heads/fix/r11-valve-reference-p2` is at `1c75332e98` on re-read, which matches the body's `## Head`.
- Not re-derived: the body's −2.411 / −4.286 / −6.161 K residual moves are quoted from #3685's r1 figure, and the packet names no finder's harness for them. The proof of this PR's behaviour rests on the fixer's features check plus my bitwise control above.

## Notes

- Note: figure: the body's `## Figures` line quotes `score.py --diff 7ae657e0e2 HEAD` as `dS +0.0000 NULL`. It re-derives as `dS -0.0029 WORSENS (coord_footprint 2502->2507)` at this head (main's own +3 included) and as `-0.0012` at the code head. `## Architecture score` and `## Red checks` already state the true `-0.0012`, so this is a stale figure, not a gamed one.
- Note: body: `## Red checks` opens with `none` and then lists the answered arch-score red.

## Findings

none
