Fix review: blocked 43227286fc18822b7955e54aa5323cc61feab39e mutation-vacuous: running_signal.py:178 delay=0.0 survives both blocks, every blip shorter than EDGE_DEBOUNCE_S counts a start

bus-nonce: 1227229651502aae0b772dbd84cfc00c

## Block

- `custom_components/heatpump_optimizer/running_signal.py:178`, `delay = max(0.0, wear.EDGE_DEBOUNCE_S - utc_elapsed_seconds(dt_util.now(), pending[1]))`, mutated to `delay = 0.0` (spec name timer-delay-zero): SURVIVED. The build's features.py block and part A's block each report 0 failures (`ev/reviewer_mutants_driver.log`, driver `ev/reviewer_mutants.py`, the fixer's own `start_counter_edges_mutants.py` with a different mutant list). This is the only survivor my driver reported, 1 of 13.
- The mutant breaks real behaviour, and no check catches it. The timer fires at once and confirms with `due` (pending + 30 s), so the debounce passes before the reading can go back. Probe `ev/blip_probe.py`, built on the build's harness `replay`: a meter-only install with a 2.0 kW blip, compressor off. At the head the counts are blip 5 s/10 s/20 s/29 s = 0 and 31 s/45 s = 1, so the debounce works. With the mutant, all six count 1 (`ev/blip_probe.log`). The null control (31 s and 45 s count 1 at both) holds.
- So with the mutant, every meter spike books a start and a wear line. That is the debounce wear.py's docstring promises, and the sampled path's `START_HYSTERESIS_SAMPLES` pinned it before the build deleted it. No check in either block drives a change that reverts inside `EDGE_DEBOUNCE_S` while its timer is armed. Every existing trace reads at 60 s or longer, so the timer is always due before the next reading.
- The body's "Unpinned sites" lists `running_signal.py:178 CLAMP_DROP`, disposed as "pinned by mutation-autofix". That mutant only removes the `max(0.0, ...)`, which differs from the head only when elapsed > 30 s at arm time. It is close to equivalent and does not cover this debounce. The fix is cheap and in this group's seam: one check that a meter blip shorter than `EDGE_DEBOUNCE_S` counts nothing, with a blip longer than it counting one as the null control, red under `delay = 0.0`.

## Evidence

- Round: first review of the build at the handoff. No pull request exists yet, so there is no review packet and no CI to read. No check runs exist at this head, and `## Red checks` is judged on the body's account only. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs` (`ev/owed_reds.txt`). The body answers `mutation`, and `main-conflict` is answered by the merge.
- Head: the body's `## Head` names 43227286fc18822b7955e54aa5323cc61feab39e, the head I measured. handoff-body ref at cb83bffd79 (`ev/HEAD.txt`).
- Merge: `git merge-tree --write-tree origin/main 43227286fc` at origin/main 9acc181ca7 (ahead of the body's 4058469d79) gives rc 0, no conflict (`ev/HEAD.txt`).
- Roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- RESULT mutation (fixer's proof re-run at the head): `BASELINE [(0, False), (0, False)]`, 21 of 21 killed, `RESULT survived=0` (`ev/fixer_mutants_driver.log`). This matches the body's 21 killed.
- RESULT mutation (reviewer's own, 13 mutants, `ev/reviewer_mutants_driver.log`): 12 killed, 1 survived (the Block). Killed:
  - price gate `wear > 0` -> `wear >= 0` and -> unconditional; zero kWh `kwh=0.0` -> `kwh=1.0`. These are the brief's pinned edges. Each one is killed by "a counted start books money, never energy, and only at a nonzero price", as the body says.
  - wear line deleted; wear line stamped at `now` instead of the edge time.
  - `restore` ignoring the stored `running`; a `None` edge overwriting `running`; month key taken from now.
  - restore before the ledger read; `attach` idempotence removed; the immersion commanded-power term dropped; the reader source swapped to the meter.
- RESULT null control (the build's harness, `dev/audit/harnesses/start_counter_edges.py`). It is the fixer's instrument, not a finder's. The finder is an outside report, so no committed finder harness exists, as the body and design state.
  - base 4058469d79 (git archive): control=3 perturbed=3 restored=7 s7_60s=0 s7_30s=0.
  - head: control=3 perturbed=4 restored=8 s7_60s=5 s7_30s=5.
  - All five rows match the body (`ev/harness_base_4058469d79.log`, `ev/harness_head.log`). The perturbation moves the harness (3 -> 4) and the control stays flat (3 / 3).
- Structure: `tests/structure.py` passes at the head. The base reads class_excess_loc 17469, coordinator_multiassigned_attrs 108, max_class_loc 7916; the head reads 17462, 107, 7909, matching the body. `seam_cut_total` reads 420 at both ends. The body quotes "421 -> 421", taken at an older base. The flat claim holds, but the number differs at this merge base (`ev/structure_*.log`).
- Architecture vector: `coord_footprint` 2498 -> 2498. `layer_violations`, `private_cross_module`, `coordinator_private_reach`, `import_cycle_modules` and `dead_members` are flat (`ev/archscore_vector.log`). The body quotes 2504 -> 2504 at its earlier base; flat either way. I did not re-run `gate.py`'s dS figure.
- Untouched: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files have no diff from the merge base (`ev/untouched.txt`). I did not re-run the goldens drift check: no claim file is touched, and neither is any fixture.
- Forward-carry: both `## Forward-carry` items are on `handoff/audit-r10-roster` at 61b0e0ff1842779e009e177243848774a72e07c2. The running-now read is in R11-OUTSIDE-HONEST-STARTS-RUNS's carry (item 5a53c59f). S7 is in R10-START-COUNTER-EDGES's carry (item 6a12a74d). That one is an own-group carry naming a pending owner ruling, which is a `fixer.md` exception. Neither is on origin/main yet, which is expected for a roster carry.
- Figures I could not re-derive:
  - The body's "Whole script: `PYTHONPATH=tests/hastub python3 tests/features.py`: ." quotes no result at all.
  - I did not re-run the archscore gate dS, `ha_floor.py record`, `ci_predict.py`, closures or the scoped-gate line (`MODE: SCOPED -- 32 script(s) run`). They are CI's or heavy, and this verdict blocks before them.
- Design conformance (approved note at design/R10-START-COUNTER-EDGES):
  - attach in `__init__`, detach in `_release_registrations`;
  - the queue in the counter with restore in `finally`;
  - one owner of the over level in `thermal_model.immersion_over`;
  - the element callable built from the latch or the instant term, meter source only;
  - a per-refresh re-read after `_detect_immersion`;
  - `running_now` returning `None` while a change is pending.
  All as designed. The module's import set (`wear`, `drift`, `entry_config`, `freq_control`, `inputs`, `thermal_model`) is wider than the design's "wear, freq_control, thermal_model only". The body discloses this as design-review carry v2, and the archscore vector stays flat.

## Findings

None beyond the Block. The block's defect is in this group's seam and is fixed in this pull request, not carried.
