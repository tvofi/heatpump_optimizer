Fix review: blocked aac8c5e80fdfe574597f7fad17f11a418ff3596f mutation-untriaged: 3 added sites survive every driver after mutation-autofix (climate.py:140 GUARD_OFF, entity.py:140 GUARD_OFF, sensor.py:2808 CMP_BOUND); mutation is red at 7e79b6762 and the body triages none of them

bus-nonce: 90bc7d55d34c947585c12e3edea95113

Review round 1. Measured head `aac8c5e80fdfe574597f7fad17f11a418ff3596f`, merge base `99cf51c1a73a5a1a44577021399b7f1cfcab898d`. The production code is byte-identical to 839b1b863 (`git diff 839b1b863 aac8c5e80 -- custom_components tests` is empty). During the review the head moved to `7e79b6762824e2df766d465518c8ba19106c7918`, which is mutation-autofix's `ci: pin killed mutants`. I judged that commit only as a delta (below). Evidence: `/Users/timmalmstrom/hpo-seats/r10s3/review-2379/evidence`.

## Why blocked

The body says each of the 26 unpinned sites is "pinned by mutation-autofix (CI's mutation job drives it; a survivor is triaged in this pull request, never auto-dispositioned)". CI drove all 26. Three survived every driver in play. mutation-pins jobs 117605275242, 117605275435 and 117605275215 each report `1 survived`. At 7e79b6762 the `mutation` lane is red again: check-run 117615880606 reads `MUTATION TABLE REFUSED -- ... 3 of them added by this diff`, and it names these sites:

- `climate.py:140 GUARD_OFF`, `if measured is not None:` in `current_temperature`;
- `entity.py:140 GUARD_OFF`, `if isinstance(value, np.generic):` in `payload_number`, the numpy-scalar unwrap. My own mutant R1 deletes the unwrap, and it also survives `tests/finite_boundary.py`. The docstring's claim that "a numpy.int64 [reads as] an int" is not tested by any driver;
- `sensor.py:2808 CMP_BOUND`, `if rate is None or rate <= 0.0:` in `_gap_energy_rate`.

The body has no survivor_triage and no killing check for any of the three. Each site needs one or the other. The fixer owns this work, under `ci-autofix.md`: "never automate survivor triage".

## Claims, each re-derived with the finder's harness at both ends

Each finder harness is a scratch copy of origin/main's file, and the only edits are `BASE` set to the end's SHA and `REPO` set to my worktree.

- `shape_payload_guard.py`: base `implementations=35 guard_families=4 driven_sites=26 distinct_answer_vectors=5 disagreeing_probes=3 (0,True,'21.5')`; head `implementations=6 guard_families=2 driven_sites=1 disagreeing_probes=0`. Confirmed. As the body says, the harness cannot see the mixin property (only 1 site is driven at the head). So I checked the mixin behaviourally myself, below.
- P6 `enumerate.py --tree` over `git archive` trees: base and fork `seams=56 instance=31 guarded=5 not_applicable=20`; head `seams=26 instance=0 guarded=6 not_applicable=20`. Its null control `--fixture clean` gives instance=0, and `--fixture reintro` gives instance=1. Confirmed, with the same blindness: the 30 mixin seams drop out of the enumerator instead of being guarded by it.
- `probe_scrub_mixin.py`: base `mixin_supplied=0 nan_published=1 nan_published_outside_pkg=0 nan_published_null=0`; head `nan_published=0 nan_published_outside_pkg=0 nan_published_null=0`. The carry requires outside-package to read 0 at both ends, and it does.
- `scrub_escapes.py`: `escapes=0` over `entity_classes=91` at both ends.
- D8-s1 `f1_active_now.py`: `heating_now_while_off=1 slot_steps_declared_off=4` at both ends. Flat by design, because `coordinator.py` is not in the diff.
- Number-state census (`tests/finite_boundary.py`, the fixer's instrument): head `number_states=50 number_state_escapes=0`. **I did not re-derive the body's fork figure, 31/36.** That figure was taken with the c896df781 copy of the test. I ran the head's copy of the test against base production and got `number_states=37 number_state_escapes=42`. The body's two ends were therefore measured with two different instruments. The direction (escapes go to 0) holds either way.
- My own probe (`my_mixin_probe.py`, mine, not the finder's): it drives native_value on all 35 concrete classes that inherit `_PayloadNumberMixin` (30 declarations: 29 sensors plus `_AccumulatingSensor`; the body's "30 sensors" counts declarations) at both ends, with 14 payload values. Across base and head, the only changed answers are for bool, `np.bool_` and text (now None) and `np.int64` (None -> int, on 14 classes). No legitimate numeric answer changed. At the head, every class publishes None for True, False, `np.bool_`, '21.5', nan, inf and np nan.
- `payload_number` refuses bools and text: confirmed by the probe and by the mutation pins. The finite scrub walks the MRO: confirmed by `probe_scrub_mixin`, `scrub_escapes` and my mutant R8. `effective_outdoor` and `zone_setpoint_attributes` are single owners: confirmed by the diff, which removes `sensor._effective_outdoor`, climate's `_effective_outdoor` and the three renamings.
- archscore `--diff 99cf51c1a HEAD`: `dS +5.6289 IMPROVES` (duplication_copies 64 -> 41, coord_footprint 2547 -> 2540). Confirmed.
- `tests/structure.py`: `duplication_copies=33` at the base (git archive) and `17` at the head, and the ratchet passes. The re-record is c15f92abf, and its commit message gives the reason. Earned: the drop is 30 per-sensor property bodies deleted, not a cosmetic split.
- Goldens: the PR does not touch `tests/golden/` or either claim file. CI's `fast (3.14)` at aac8c5e80 reads `NO UNCLAIMED DRIFT: 56` and `NO STALE FIXTURE: 56` against 99cf51c1a, and `env_drift.py --all` is ok. VERSION, the manifest version and the notes heading are untouched.
- Closing keywords: `closingIssuesReferences` is `[2242]`; #2238 is "Part of".
- Forward-carry: D8-s1-01 is in the R10-ARCH-SHAPES `carry` on origin/main ("From R10-SENSOR-PAYLOAD (#2238 D8-s1-01, left open there)"). It landed with #2380, merged 2026-10-18T06:43Z, and it carries the control (1 and 4) and a re-measure instruction. The body names the roster file but not the stage. It should name R10-ARCH-SHAPES and #2380.
- Red checks: the body names and answers `mutation`. pr-contract was red at 839b1b863 only because the body did not yet name mutation, and it is green at the head.

## mutation-autofix delta (aac8c5e80..7e79b6762)

There are 23 new files, all under `tests/mutation_ledger/killed_by/`, all with `Recorded by mutation_table.py --pin-killed`, and the commit adds no survivor_triage. The pins are kill-only. The 7 pins the branch deleted named lines this diff rewrote, and none of their `old` text remains in the tree.

## My mutants (each restored; the worktree is clean)

- R1, the numpy unwrap deleted: SURVIVED finite_boundary. This is CI's entity.py:140 survivor.
- R2, `_payload_types` ignored, so CompressorStarts accepts floats: SURVIVED finite_boundary and entities. This is an advisory gap.
- R3, mixin rounding dropped: SURVIVED finite_boundary and features. CI's entities pin kills it (a58846bd, 91e639fa).
- R4, a text DHW part read as 0: KILLED by finite_boundary.
- R5, the outdoor thermometer skipped: KILLED by finite_boundary; SURVIVED features.
- R6, the upper/lower names swapped in `zone_setpoint_attributes`: SURVIVED finite_boundary, features and entities. No check pins the values this owner publishes, only the P2 single-spelling fact. This is advisory and not a mutation-table kind, but it is worth a value check while the three survivors get triaged.
- R7, climate's indoor fallback read raw: KILLED by finite_boundary.
- R8, the scrub skipping every non-package owner (patch 00's rule): KILLED by finite_boundary (outside-package NaN).

## What clears it

Add a killing check or a survivor_triage verdict for each of the three survivors (and a value check for R6, preferably). Then re-run steps 2-8 and hand off again at the new head.
