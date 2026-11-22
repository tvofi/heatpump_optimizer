Fix review: merge b0ee904f74393f05b4a2195bdef1c305f9b1dcc5

bus-nonce: b62336c7fe8ec4f2e5bcee1fb7f85aaf

Note: body-head: `## Head` still has a stale second line naming 49b07894306e as a merge of 7f2e1ee90c; the first line names this head correctly.
Note: ci-pending: no owed red at this head when read at 20:16Z. The only failure, `gate` (job 137337285687), reads "run(s) [45062271575, 45063111041] at this head are still being judged; their gate decides". `tests / fast`, `tests / mutation`, `closures` and the rest are queued or running. This verdict does not depend on them, but `bus.sh post` should wait until they are green.

Round 2, a delta review (owner ruling 2026-11-09): `git diff 8b127c6d85 b0ee904f74`. The round-1 verdict blocked at 8b127c6d85 (verdict/3841 c4be3d7b). No new nonce was dispatched for this round, so it carries round 1's nonce. `review_carry.py 8b127c6d85 b0ee904f74` prints FRESH-REVIEW. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract copy is current.

## The prior block is resolved

Round 1 blocked with class-open: axis the hot-water windows in force at an instant unenumerated (e.g. dhw_planner.DhwPlanner next_window_in_hours).

- Repaired. `dhw_planner._dhw_next_window_hours` takes today's windows from `_dhw_windows_at(.., 1, ..)`, the entry `in_window[0]` tests. It takes tomorrow's windows from the first step past midnight, or, when the horizon has no wrap, from the next weekday through `cyclic_span`. `_build_dhw_requirements` publishes that value. I re-ran the round-1 probe at the head (`ev/probe_planner_next_window.head.txt`) on "weekdays 06:00-08:30, weekend 08:00-09:30":
  - Saturday 07:00: 1.0 (was 0.0).
  - Saturday 05:00: 3.0 (was 1.0).
  - Monday 07:00: 0.0. Flat-spec control: 0.0.
  - New cross-midnight cells: Friday 23:00 is 9.0, Sunday 23:00 is 7.0, Saturday 10:00 is 22.0. Each matches `windows_in_force`'s answer.
- The axis is now enumerated. It has a rule and a census. The new `tests/entities.py` consumers census (`_fw_consumers`, `_P2_CENSUSES["dhw_window_flat_consumers"]`) follows every flat load through locals, returns (which become sources) and same-module parameters to the consuming call. Each consumer is either a resolver or dispositioned. The census also checks itself: it must find both sources. Its three null plants each fail it.
- I tried to open it further. My own probe (`ev/probe_fw_holes.py.txt`) runs the census's own code, extracted from `tests/entities.py`, on the head package and looks for flat values the walk drops without keying them: non-Name assign targets, tuple unpacks past element 0, AnnAssign/AugAssign, iteration, and `getattr(.., "dhw_*windows")`. It found 1 site: `windows, learned_windows = self._effective_dhw_windows()`. Element 1 there is a bool, so no window set is dropped. The census reports `stray=[]`.
- I also swept every instant reader by hand: `grep hour_in_windows( | hours_until_next_window(` over the package. Every hot-water reader goes through `windows_in_force` or the planner's per-step `_dhw_windows_at`: boost, the coordinator flag and next-window hours, the draw learner, `pump_schedule`, and the planner's `in_window`, `prev_in_window` and next window. The remaining callers (`grid_fee`, `tariff`, `quiet_windows`, `silent_mode`) read other window sets.

## Mutation proof (the reviewer's own, at the head)

Each mutant ran in its own detached worktree, through `features_block.py --through '_flata = _weekly_solve(...)'` (`ev/mut.M*.txt`). Each run fails only the named check: "the planner's published next window reads the day's windows ... in every census cell".
- M1: the call restored to the pre-fix `hours_until_next_window(.., windows)`. The check fails: 25 of 58 cells wrong. The census extract keys `_build_dhw_requirements -> hours_until_next_window` as stray.
- M2: `tomorrow = today`. The check fails: 10 of 58 cells wrong.
- M3: `today = windows` (the flat set). The check fails: 19 of 58 cells wrong. The census extract keys `_dhw_next_window_hours -> hours_until_next_window` as stray.
- I did not re-drive the body's `cyclic_span(.., + 2)` mutant or its survivor kills. CI's `mutation` lane is running at this head.

## The delta's other production change

`PayloadFlagMixin` now reads a key path. Five sensors (`MeasuredPowerSensor`, `CompressorStartsSensor`, `MonthlyPeakSensor`, `PVSurplusSensor`, `MixedHotWaterSensor`) drop their own `available` and declare `_available_flag = (<key>,)`.
- Each sensor's `available` owner chain is the same as before, with the mixin in the slot the sensor's own override held (`ev/probe_flag_mro.*`). For example, `MixedHotWaterSensor` reads PayloadFlagMixin -> DHWEntityMixin -> _MeasuredTemperatureMixin -> CoordinatorEntity, where it used to read MixedHotWaterSensor -> the same three. The one-key gate `(data or {}).get(key)` is the old `data.get(key)`.
- Every PayloadFlagMixin subclass in the package declares the flag (grep). The flag now has no default, which turns a missing declaration into an AttributeError, and `tests/entities.py` exercises that.
- This puts no reviewed functionality at a non-obvious risk, so the review does not widen.

## Evidence

- Finder harness `dev/audit/rounds/round11/D17/leads/dhw_window_weekday.py` (sha1 3747d12b7fca, matching the body) at the head: `cells_wrong` 0, `null_cells_wrong` 0 (`ev/finder.dhw_window_weekday.head.txt`). Round 1 measured it at the merge base as 18.
- Structure: `tests/structure.py` at the head prints STRUCTURE RATCHET PASSED, rc 0. In `git diff <mb>...HEAD -- '*_budgets.json'` every row moves down: `class_excess_loc` 17317 -> 17280, `dead_top_level_symbols` 1 -> 0, `duplication_copies` 5 -> 3, `max_class_loc` 7868 -> 7857, `module_excess_loc` 21779 -> 21778, `unloaded_package_imports` 14 -> 5, archscore `dead_members` 1 -> 0, `public_unused` 1 -> 0. No row is raised. The two-dot `8b127c6d..HEAD` shows `const_modules_over_50` 3 -> 4, but that is main's own row, brought in by the merge.
- Merge: `git merge-tree --write-tree origin/main(e3cb5c019b) b0ee904f74` exits 0 (`ev/merge-tree.txt`). VERSION, the manifest, RELEASE_NOTES.md and `tests/golden/` have no three-dot diff, so neither claim file is touched.
- Body: the `## Head` first line names b0ee904f74, a merge of the code head 7f2e1ee90c, whose tree is identical to b0ee904f74's. `## Red checks` names the ancestry reds and answers each one. At this head nothing is red apart from the pending `gate` (Note above).
- `carry_audit.py check` on the body's Forward-carry, Friction and Carry routing sections: 2 routed, 0 unrouted, rc 0 (`ev/carry_audit.txt`).
- Not re-derived here: the body's 3072-payload mixin census, `Architecture score: dS +3.8460` (CI `arch-score` is green at this head), and the D15/D10/D8/D14 harness figures, which this delta does not touch and which round 1 measured.
