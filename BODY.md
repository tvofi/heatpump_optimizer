R10-LIVE-BUNDLE-READS (issue #3120). Fixes `tools/replay/debug_ingest.py` against a real Home Assistant download (D15-s1-03, D15-s1-01) and does the live-bundle reads that round 10 could not do for want of the owner's bundle. The bundle is owner data, read locally and never committed or quoted; only derived numbers and reason words appear below. Privacy gate (D15 step 2) run first: `tests/replay.py` `leak_probes()` 46 arms, 0 failing; `export.violations` catches a planted credential in the bundle (+2 violations over the unplanted count) and passes the derived-figure document this body is made from (0 violations; a planted street address in the same shape is caught, 1 violation).

The fix: `load_bundle` unwraps `data.debug` when the top level is a download (`unwrap_download`); stage 4 compares the store window and the rows over the samples both hold, each stamp once. Design choice, said so a reader does not take it for a bug: the comparison is now over the intersection, and it still fails (not vacuous) when the intersection is empty.

Carry dispositions (roster carries of R10-LIVE-BUNDLE-READS, numbered from 1):
- Carry 1 (R10-HEAT-METER, L9 `unhealthy_input`): done, see Figures; outdoor limit unchanged.
- Carry 2 (R10-REPLAY-REAL-DAY carry 4): dismissed as the duplicate of Carry 1 the roster marks; same reading.
- Carry 3 (L6, 238 min house meter): done, see Figures; no code change, the rule already keys on report time.
- Carry 4 (R10-SCORES `--bundle` scale drift): done, see Figures.
- Carry 5 (D15-s1-01, D15-s1-03, L-a, L-b): fix landed, L-a dismissed with its reading, L-b reproduced and explained.
- Carry 6 (coordinator lane note): honoured, no coordinator.py edit.

Handed to the orchestrator, not landed by this seat (a local seat does not write the roster): Three items are owed to R10-ROUND-PLAYBOOK and are handed to the orchestrator to land as roster ops before merge: (1) a version change across a gap is a restart whatever the gap's length (the `d15_restart_gaps.py` rule read 0 at a 43.6 min upgrade gap); (2) its carry beginning "Round-11 D15 inputs, re-homed from R10-REPLAY-REAL-DAY" is done here and can be closed; (3) only 1 of 8 ring snapshots carries `unhealthy_input`, so the next live bundle re-reads it with `d15_bundle_reads.py`.

## Head

0623400819922e51443917996f49de671f138d34

## Mutation proof

Failing test first: the three new arms of `debug_ingest.gate_checks()` (driven by `tests/entities.py`) fail on the unfixed file. Wrapped download at origin/main (c3a279e32): 6 of 12 stages fail (schema, manifest-cycles, manifest-version, rows-match, stores-present, bias-rederived); tail-repeat bundle: bias-rederived fails; both pass at the head.
Mutants, each run through `gate_checks()`:
- `return unwrap_download(json.loads(raw))` to `return json.loads(raw)`: the wrapped-download arm goes red (6 stages).
- `by_time.setdefault(parsed.when, parsed)` to a key unique per row (no de-duplication): the clean arm, the wrapped arm and the tail-repeat arm go red on bias-rederived.
- `shared = sorted(set(held) & set(by_time))` to `sorted(held)`: the run raises KeyError (a kill by crash, not by a named check).
Restored after each; `git diff` shows only the fix.

## Null control

`debug_ingest`'s own self-test bundle (unwrapped, one sample): the pre-existing arms read the same before and after (clean 12 of 12; `--corrupt accuracy` still refused by the loader, `corruption-refused` ok). New negative arms: a shared sample whose row disagrees with the store still fails bias-rederived; rows sharing no sample with the store fail it too. The flat control for the reads is below: a week with every heartbeat reporting names none.

## Figures

All commands from the repository root with `PYTHONPATH=tests/hastub:custom_components` (add `tests` for debug_ingest) and the bundle path from the seat; bundle at 7.1.1, exported 2026-11-04T07:22Z.

Fix, `tools/replay/debug_ingest.py --bundle B`: at origin/main the download as handed reads 6 of 12 stages; at the head 12 of 12. Store window 192 samples, rows hold 300 distinct sample stamps in 327 rows, 191 shared; store bias and rows bias over the shared samples are equal (delta 0.0 C). D15-s1-01 does not reproduce on this bundle: with only the unwrap applied at origin/main, delta is 0.013 C (< 0.05), so the carry's 0.109 belonged to an older bundle; the fixed comparison is the correct rule regardless. `live_deque_bias` (0.339) differs from the store window (0.245): the diagnostics figure is taken at export time, the store at its last save; not a defect, a timing difference. `replay` is null (the manifest says one entity id was not masked), so stage 2 `replay-clean` is vacuous on this bundle; no replay-half step ran.

`dev/audit/harnesses/d15_bundle_reads.py --bundle B` (new; instrument for the next bundle):
- L9 `unhealthy_input`: the ring holds 8 weekly snapshots; 6 are unhealthy, 1 carries the field (the newest, taken 2026-10-28), the 7 earlier ones predate #2261 and carry no key, so the 5 unhealthy ones among them are unattributable, not healthy. The newest names `external_heat_source`: a plant-wide freeze reason from the external-heat detector (this install has a wood tank), not an indoor, outdoor or power input. 0 snapshots name outdoor. Decision: outdoor's 180 min on-change limit is not implicated by any evidence and stays; no change. Controls (real `SnapshotRing`): every heartbeat reporting gives `unhealthy_input=None`; one input silent gives `stale:outdoor_temp_entity`. The two healthy weeks (2026-10-14, 2026-10-21) name none, consistent with the null.
- L6 age rule: `inputs.age_limit_for` plus `inputs.state_age`, all three meters 240 min since the last write: a meter reporting on change is not flagged (its limit is infinite for the house-power key); a polling meter re-reporting an unchanged value is not flagged (age is read from `last_reported`); a polling meter that went silent is flagged. Mutant `--mutant last_changed`: the re-reporting meter turns flagged, so the control moves. The sensors self-test (`debugger.sensor_sanity`) has no age rule at all: it reports missing counts, range and longest flat run, and the live health view. The 238 min flag of the lead came from the freshness rule, and #2234 (R10 N-staleness) already keys it on the report time and the source's reporting kind. The bundle's `self_tests` is null (collection not final), so the original flag is not re-readable. No change.
- L-a: not reproduced at 7.1.x. Rows 327, distinct samples 300, longest run of rows repeating one sample 9 (lead: 446), longest gap between distinct samples 0.84 h (lead: 115 h), largest row-stamp lead over its own sample 0.79 h. Perturbation `--plant-stall`: the same bundle with the tracker stopped at the midpoint reads longest repeat 164 rows and row lag 40.99 h, so the measure sees a stall. Dismissed with the reading.
- L-b: reproduced, 3 of 327 rows lack `action_mode`, `action_kw` and `heat_pump_on`. They are the first row after a start: row 133 follows a 43.6 min gap and is the first 7.1.1 row (the upgrade restart), the other two (rows 1 and 194) are each followed by a row within 1.0 min. `debugger.cycle_row` omits a key whose value is None, and `current_action` is empty until the first plan of a start is solved; the docstring says absent fields are omitted. By design, not a defect; a row scan that treats absent as a failure would be wrong. Side finding: `d15_restart_gaps.py` reads 0 gaps because the 43.6 min gap is under its 3-interval rule (2700 s at the 900 s interval) although the version changed across it..

`dev/audit/harnesses/r10_scores_envelope.py --bundle B` (scale drift, the re-homed read): stored scale 1.065, split 0.936, 10 samples (the learner restarted counting after the newest ring snapshot), two-zone. Time constants: configured 19.7 h (grade 0), effective 13.6 h (grade 0 on the 20-100 h band; the tree's `house_grade` reads 7.6). The 2.6x drift lead is visible in the ring, not in the live scale: the scale walked 0.876 (2026-09-09) to 2.182 (2026-10-21), a ratio of 2.49, then re-anchored (anchor 0.191 to 0.507 at 2026-10-28, scale 1.039) and the samples count reset below 50 by the time of the bundle. No live drift at this bundle; the walk itself is a historical, pre-7.1 observation. Null control: ratio of the unplanted ring entries 2026-09-09 and 2026-09-16 is 1.00.

No coordinator.py edit was needed or made.

Restart gaps (`d15_restart_gaps.py --bundle B`): restart_gaps=0 at 327 rows, max spacing 2613.9 s against the 2700 s rule.

Seams for the class (fixer.md step 8; rule: `git grep -n "json.loads(raw)" tools/replay` and `git grep -n "load_bundle" tools tests dev`): `load_bundle` is the one loader; its other callers are `debug_replay.py` (gains the unwrap) and `dbg_bundle_gen.py` (bare bundles, unchanged). `d15_restart_gaps.unwrap` and `r10_scores_envelope.arm_bundle` already unwrap.

Not run: `tests/entities.py` aborts before the new arms on this macOS box (a PermissionError from the stall sampler at line 18578 of tests/entities.py, `Cannot get task port`), a Linux-only path; the scoped gate selects only that script, so CI is its first full run. The arms were run directly through `debug_ingest.gate_checks()`: 7 of 7 ok. `tests/harness_headers.py`: 112 checks passed. `tests/structure.py`: passed. `ci_predict.py --base origin/main`: no red predicted after `--apply-inert`.

## Red checks

none

## Forward-carry

none

## Friction

none
