Fix review: merge 2e97faf4c1d23d6ab0dd1013efa6d68d1a7dbf0d
bus-nonce: d6f71e60a67231328b61fb6ae7d302aa

Round 1, full review from a detached worktree at the head; merge base e84856520d.
RESULT part-B-block head: ALL 70 FEATURES BLOCK PASSED (features_block.py, prelude emitted at the head; ev/block-head.log).
RESULT mutation proof: the body's mutant (draw_range.py:1070 `elif not sweep:` -> `else:`) exit 1, 6 FAIL lines. Reviewer's own mutants, all killed by the same block: pump_arbiter.py:1380 sweep-floor release dropped (4 FAIL), pump_arbiter.py:1491 tank-cold stand-down off (3 FAIL), sysid.py:1621 dear-hour level-boundary end off (3 FAIL). Tree restored. Driver: ev/mutants.sh.
RESULT m5_tankfall: booked_kwh_unplanned_max=3.0160, long_max=0, short_max=0 at both ends; at the head draw_then_charge_max=3.0160 and unplanned_inputs_equal_draw_then_charge=True, as the body states.
RESULT draw_map_sweep night arm at the head: routing window=4 idle=0 ceiling=1 sources=['sweep'] probe_since=None plan_night_window=9; r17 ceiling_sample_kw=[3.2] against row_drawn_mean_kw=[3.2000000000000006].
RESULT structure.py: module_excess_loc 21627 -> 21992, class_excess_loc 17218 -> 17198, max_class_loc 7762 -> 7748, every row ok at the head. archscore --diff origin/main: dS +0.0006 IMPROVES (coord_footprint 2533 -> 2532).
RESULT VERSION, manifest, RELEASE_NOTES, tests/golden and both claim files: untouched. git merge-tree origin/main head: rc 0 (LEDGER-MERGE resolved tests/closures.json).
Step 16 (actuator): the sweep adds no refusal of a planned write. The held floor clears on any pass whose action is not a sweep's (mutant above). The sweep ends on its step hours, an excursion abort, a dear hour or the night's end at a level boundary. In-flight sysid state is not persisted, so a restart drops the sweep and the arbiter's sweep_floor_c too.
Step 14 (raise): checked under mandate 6893738184 (scope all). I found no missed payment. Moving the pure sweep_levels_kw / cheap_night_cycles into draw_range.py (under the limit) would cut the count without improving cohesion, so it does not count as a payment.
Note: harness: draw_map_sweep.py and m5_tankfall's draw_then_charge arm are the fixer's instruments, not a finder's (the packet names no finder harness; this is a port of part B). Carry: dismissed: evidence, not a finding
Note: red-at-head: at review time tests / mutation was red on ADDED UNPINNED sites, with the 12 mutation-pins shards still queued or running and the gate red behind it. The body answers this as red by construction, pinned by mutation-autofix (ci-autofix.md). The post gate (C8) holds this verdict until the head is green. Survivors that the pins report are mutation-autofix's lane. Carry: dismissed: owed red answered in the body; C8 enforces at post
Note: carry 5 is on handoff/audit-r11-roster under R11-OUTSIDE-HONEST-DHW-RUNS, with its draw_then_charge null control stated as the precondition. Carry: dismissed: evidence, not a finding
