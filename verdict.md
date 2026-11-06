Design review: approve aead688d446317fbbb8b478a47bdfe19725db1c2

Group R10-CLONE-2238, note design.md at design/r10-clone-2238 (aead688d4), the third note (205c766b7 revised 2026-11-04; 51884d31f unreviewed). The note cites base b88684a2. The seat's base is origin/main 28482ece, 1449 commits later. In that range `git diff b88684a2 28482ece` touches only manifest.json and the card JS under custom_components/. It does not touch tests/structure_budgets.json, the sweep-P2 directory or bugclasses.json. So every line the note cites holds unchanged at 28482ece.

## Prior revise point and carries

- Revise 1 (class-open, P3's fourth site) is answered. `optimizer.py:4477-4482` (`_safety_release_steps`, the `space_pins` loop) is P3's fourth caller and a named mutation target. The sibling command is widened to a plain `rg -n 'upper_temp_trajectory' custom_components/`. I re-ran it at 28482ece and it gives 15 lines at 11 sites, as stated. Each excluded reader carries a reason: 1902 is the field, 3096 the producer, 2362 the min over zones, 2922 the ungated ut column, and 4665-4667 needs both zones.
- Carry golden-check is answered. The note names `tests/golden.py` drift mode via `env_drift.py`, plus the coord_* fixtures and the capacity/peak/two-zone fixtures.
- Carry bugclasses-json is answered. The P2 entry's `sw:` instances sit at bugclasses.json:280-290, inside the list at 195-296, and the entry has a single `status` ("barriered", line 314). Leaving the file untouched with a stated reason is sound.

## Checked and holding

- Seams (step 1): I checked these at 28482ece.
  - P1 at coordinator.py:1219 and 10153-10154.
  - P2 at 5633 and 5756. The 1331 argument is a separate fact.
  - P3 at coordinator.py:10067 and 10116, and optimizer.py:4103 and 4477.
  - P4 at tariff.py:876, tariff.py:1169 and optimizer.py:4932-4934. The slice before the pad is as stated.
  - P5 at optimizer.py:3377 and 3396, inside `_peak_window_factors`:3352 and `_peak_day_kwargs`:3382.
  - P6 has the mixin at sensor.py:376, the classes at 1872 and 2369, and the attrs at 1913 and 2409.
  - P7 at tariff.py:332 and 413.
  - P8 at tariff.py:557 and 1077.
  - P9 at tariff.py:609 and 670. Sites 261 and 306 are a separate fact.
  - Every owner is new and sits in the module that holds the copies. None of them opens a new write path.
- Shape (step 2): the change is bit-identical, and each move maps to one enumerator pair. Dropping the two pairs that are gone from F5 is correct.
- Siblings (step 3): every command in section 4 reproduces at 28482ece with the counts stated.
- Evidence (step 4): each pair gets a sentinel-owner test that drives both production callers. It fails at base because the owner is absent. Restoring any inline copy is a killed mutant.
  - Controls: the enumerator `--fixture` null, the per-commit F5 delta, and archscore before and after.
  - Probe re-extraction: probes_p2.py:99 uses the needle `target_kw <=`. `grep -rn 'target_kw <=' custom_components/` is empty, so the stated LookupError holds, and the re-extraction plus inverted FIXES null arm is the right repair.
  - I did not check probe 5's needle at line 111 against `_async_learn_buffer_cooling`. I took the note's "unchanged" and its 6/6 spike reading as given, because there was no code to rerun.
  - Zero headroom: `class_excess_loc` 17585, `duplication_copies` 14 and `max_class_loc` 7955 match the budget file. The plan to stop for the owner rather than raise matches CLAUDE.md rule 2.
- Consistency (step 5): I read every open design/* note for the hot symbols. No design claims any of these nine facts as its seam.
  - R10-HEAT-METER (approved 21f4fbfe) edits the `_accumulate_energy` and `_settle_interval_diag` call sites. It passes on the pending split it reads today and does not own the read.
  - R10-LIVESTATE (approved f589cc0c) touches `_file_lead_predictions` for the lead_pending void. That is a different fact from P3's trajectory.
  - R10-COP-GATE (approved 72902290) adds a field to `OptimizationResult`. That is a different concern on the same dataclass, as WHY-NOW's `space_drivers` was.
  - Overlaps are textual only (see carries).
- Cost (step 6): four production files, tests added to existing scripts, one budget re-record and the probe repair, in nine commits. That fits size L.

## Notes for the fixer (carries, not revise points)

- Carry: R10-CLONE-2238 (item heat-meter-overlap). R10-HEAT-METER rewrites the attribution call at coordinator.py:1219 and the ledger split at 10153-10154, the same lines P1 owns. Whichever lands second routes its split through `_planned_split(pending)` and does not re-inline the read. Re-run P1's two-caller test after that rebase.
- Carry: R10-CLONE-2238 (item livestate-overlap). R10-LIVESTATE edits `_file_lead_predictions` near P3's coordinator.py:10067 caller. On rebase, keep P3's `sensor_trajectory(two_zone)` call as the only trajectory selection there.
- Carry: R10-CLONE-2238 (item budget-rerecord-order). All three zero-headroom rows are shared with every in-flight group. Re-record tests/structure_budgets.json only after the final rebase, and name the rows that moved in the commit message, as section 5 states.
