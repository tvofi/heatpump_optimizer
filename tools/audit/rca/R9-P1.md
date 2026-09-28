# Round-9 RCA, class P1: a non-finite or malformed value crosses a persisted-store boundary with no guard

Seat: round-9 RCA seat for P1 (slug `p1`). Contract: `tools/audit/briefs/root-cause.md`,
policy `.claude/rules/defect-root-cause.md`. Baseline `1936d5ca` (v6.7.1); main measured at
`db878b29`. Prototype branch `handoff/r9-rca-p1`: barrier `0ade2456`, demo-only instance fixes
`99118d35` (evidence, not the fix). Evidence files: `rca/p1/evidence/`. Interpreter: CPython
3.11.15, numpy 2.4.6, scipy 1.17.1 (CI pins), box 4 cores, shared (load noted per run).

## Root cause

### Cause, reproduced

Every instance was reproduced at `1936d5ca` and at `db878b29`: the S3 probes
(`tools/audit/round9/D14/sweep/P1/probes.py`) give `failing_probes=14` of 14 at both, each for its
stated reason. With `voluptuous` missing, all 14 also "fail", but with `ModuleNotFoundError`. A
seat without the runtime deps gets 14 of 14 that measure nothing. The finder's detector
(`tools/audit/round9/D14/s1/p1_store.py --barrier`) reproduces its own numbers exactly at
`1936d5ca`: `p1_escaping_mutants=11`, `p1_escape_seams=7`, `p1_poison_mutants=0` of 4027,
`p1_wedged_seams=2`, `barrier_driven_escape_seams=0`.

**Cause.** The class has one structural barrier: `QuarantiningStore`, round 6, #1425 (`e299cd72`).
It covers one sub-property: **nothing non-finite reaches a loader**. `store.py` says it "closes the
class by construction". Its standing check, `tests/finite_boundary.py`, measures that
sub-property only. Every other way a stored leaf can be malformed is still decided per seam, by
hand, in each loader. That is the mechanism `store.py`'s own docstring names as the cause of the
non-finite escapes: "finiteness was enforced **per demonstrated field**". The four sub-shapes left
per-seam are:

- a naive instant;
- a wrong type installed live;
- an unbounded magnitude (a value, or a dict key);
- a wrong container.

At `1936d5ca` the check was green (`ALL 41 FINITE BOUNDARY CHECKS PASSED`) while every judged
instance reproduced. It was blind in three measured ways:

1. **Substitution.** It substitutes numeric leaves only
   (`if not isinstance(val, (int, float)) ...: continue`). No instant or container is ever
   corrupted.
2. **Seeding.** Its seeding leaves most sections empty. `p1_store --barrier` counts its
   substitutable leaves per store: manual_plan 0, boost 0, away 0, snapshots 1, pump_duty 1. Its
   own healthy legionella payload holds naive instants (`_dt.datetime(2026, 1, 1, 12)`), which
   is the D14-s1-01 shape.
3. **Oracle.** It reads only `coord._thermal_params` and `_build_data_dict()`, and applies type
   drift to `_thermal_params` alone. The comfort, curve and snapshot learners, the arbiter's
   `_STATES`, and legionella are never scanned.

**Which side moved.** The seams predate the check. `snapshots.due`, `ComfortLearner._decay` and
legionella's `parse_datetime` all exist at `e299cd72`, where the check landed. The narrow
substitution and narrow oracle both date from that same commit (`8e5d1ace`, `git log -S`).
`pump_arbiter.py` came after (`3b320405`, 2026-09-24). Arm 1's loader-count equality forced its
wiring into the sweep the same day (#1588, `f842cfda`). The wired sweep then ran green over
D1-s3-03.

**Class search: what else the cause reaches.** The prototype arm (below) was run at `db878b29`
before the magnitude scrub. It gives `class_seams=101` (`evidence/early_arm_no_scrub_on_main_db878b29.txt`).

- **84 are magnitude-only.** Every one of the 13 stores has at least one numeric leaf that loads
  `1e300` or `2**64` verbatim. Examples: every `*_samples` counter, `solar_aperture`, both CUSUM
  stats, `energy` totals, ledger lines, `peaks/*`, `price_model` shapes and variances,
  `dhw_draws`, `legionella/last_attempt_peak`, the arbiter set-point, and the freq-map and
  capacity-envelope keys.
- **The rest are the known instance seams.**

With the accuracy samples, immersion events and fuse advisor also seeded, three further seams
appear. All are **latent**: no current consumer raises.

- `accuracy:accuracy/samples/#/t` and `accuracy:dhw_accuracy/samples/#/t`.
  `AccuracySample.from_dict` keeps a naive `when`. This confirms S3's lead.
- `thermal_learning:immersion_events/#`. The naive string is kept. Its one consumer
  (`coordinator.py` ~8385) normalises it.

**The sweep's two new instances are not store-reachable.** P1-sw1/sw2 are the NaN
`configured_weight`, `learned_weight` and `evidence`. The NaN arm of D14-s1-01's probe
(legionella `attempt_peak`), and the D1-s4-01 duty and D1-s5-02 `residual_var` NaN probes, have
the same flaw. Each calls `from_dict` directly, bypassing `QuarantiningStore`. Through the real
store the NaN leaf becomes `None`: the arm's non-finite substitutes on `accuracy:comfort/*` give
no non-finite seam, and `p1_store` gives `p1_poison_mutants=0` of 4027. The same comfort leaves
**are** reachable at `1e300`, which is a magnitude seam.

### Process state: (c), the process was followed and did not produce the intended result

- **The process existed.** `store.py` (#1425):
  > "The rule that a store must be this type is enforced, not remembered: the standing sweep
  > `tests/finite_boundary.py` derives the boundary set from the tree ... and drives a non-finite
  > leaf through each boundary."
- **It was followed.**
  - All 13 stores are `QuarantiningStore` (`raw_store_calls=0`).
  - The sweep runs in every gate (`tests/run.sh`: `run "$PYTHON" tests/finite_boundary.py`).
  - Arm 1 forced the arbiter's wiring (#1588).
  - Round 8 extended it (#1518: `WRONG_TYPE` substitutes, `_type_drift`).
- **It was green over 11 instances**, because its property was narrower than the class. The
  ledger mechanism is "non-finite **or malformed**". The check's docstring re-scopes that to "a
  non-finite (invalid) value". The #1518 extension repeated the per-demonstrated-field pattern at
  the detector level: its type-drift reader covers `_thermal_params` only, which is where the
  round-8 instance lived. `tools/audit/bugclasses.json` still records P1 as `detector: null`,
  `barrier: null`, `status: open`.
- **Why not (b):** nothing was skipped. **Why not (d):** the instance seams predate the check. A
  firmer instruction would not help; the countermeasure is to measure the class property itself.

### Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**Left side, measured.** The arm adds **25.2–26.4 s CPU** to each `tests/finite_boundary.py`
run: arm 4 25.2 s and 26.4 s against arms 1–3 11.3–11.6 s, measured with `process_time`, load
6.6–6.9 on 4 cores. The old script is 12.7 s CPU at `1936d5ca`. Runs per round are an estimate,
not a measurement. The script's closure includes the coordinator, so nearly every production PR
runs it, and every push to main runs it (FULL). At 41 PRs × about 3 runs each, that is about 123
runs × 26 s, or **about 53 min** of serial gate time per round.

**Right side, measured.** The branch spans (first commit to merge, `git log`) of the last three
P1 class fix PRs are:

| PR | round | span |
|---|---|---|
| #1345 | 5 | 4.8 h |
| #1425 | 6 | 5.7 h |
| #1569 | 8 | 16.8 h |

The mean is **9.1 h** per round. This is a lower bound: it excludes finding, verifying, judging,
sweeping and RCA. P1 had instances in 8 of 9 rounds: rounds 1–6 (12 in the ledger), round 8
(#1569) and round 9 (11). So P ≈ **0.89 per round**, and the expected defect cost is ≥ **8.1 h per
round**. That is about **9 times** the countermeasure's standing cost. **Passes.**

**The production half is free at runtime.** The magnitude scrub is one comparison per leaf, in a
walk `_sanitize` already does once per store load.

### Countermeasure: the class-eliminating barrier

The barrier addresses state (c): it widens the instrument to the class property, and it closes
by construction the sub-shape that has one boundary.

1. **Structural, in `store.py`.** `_sanitize` quarantines a leaf, a numeric string or a dict key
   of magnitude ≥ `ABSURD` (1e15), exactly as it quarantines a non-finite one. The new
   `_poisoned()` predicate keeps `functions_cc_over_15` at 34 ≤ 34.
   - Null control: the populated seed round-trips unchanged (`_sanitize(v) == v` for every store).
   - An int of `10**400` is handled; `math.isfinite` would raise on it.
2. **Detector, Arm 4 in `tests/finite_boundary.py`:**
   - **Seeding.** Every store is written by its real saver at an **aware** frozen clock, with
     snapshot, freq map, envelope, defrost duty, curve and comfort instants, accuracy samples,
     immersion event, fuse advisor, legionella, boost, away and arbiter populated.
   - **Substitution.** Every leaf and container by kind, with numbers adding `1e300`, `-1e300`
     and `2**64`. An aware ISO instant also gets its naive twin. Every int-like dict key is
     renamed to `10**15`.
   - **Oracle.** It runs after the real loaders, `best_restore`, `async_restore_learned_snapshot`
     and `_build_data_dict`. There must be no raise, and nothing new that is non-finite, naive,
     of magnitude ≥ 1e15, or text/container where the healthy load held a number. The scan
     covers everything the coordinator owns, plus module-level per-coordinator registries
     (derived: any package mapping keyed by the coordinator).
   - **Controls.** A self-test on planted labels. A no-skip check (`mutants > 0`, stores ==
     `LOADERS`). A healthy-load null control. `UNSEEDED` lines print the sections the seed
     leaves empty (23).
3. **Instants.** The naive sub-shape is fixed by F3.1's shared stored-instant parser, as planned.
   The arm is what holds every loader to it.

**Demonstration** (`evidence/evidence.out`):

| run | tree | result |
|---|---|---|
| old check | `1936d5ca` | `ALL 41 ... PASSED`, over 14 failing probes |
| barrier on main, no fixes | `0ade2456` | **exit 1**, `class_seams=18`: every store-reachable judged seam plus the 3 latent ones |
| barrier + demo instance fixes | `99118d35` | **exit 0**, `class_seams=0`, `ALL 46 ... PASSED` |
| perturbation: arbiter fix reverted | `99118d35` | exit 1, `class_seams=4` |
| perturbation: magnitude scrub reverted | `99118d35` | exit 1, `class_seams=105` |
| structure ratchet | `0ade2456` | exit 0 |

**What it does not cover, stated so a zero is not over-read. This needs a tvofi ruling.**

- **Out-of-domain but bounded values.** Examples: a decile of 12–99, `window_factor` 1e12, duty
  1.5. This is part of D1-s3-06, D1-s4-01 and D1-s5-02. A field's domain is known only to its
  writer, so a generic detector would need a declared domain table for about 150 stored fields,
  which is carried and large.
- **Blast radius (D1-s4-03).** A loader discarding a whole valid grid for one bad cell is data
  loss, not poison or a raise. Many loaders discard a section on purpose, so a generic oracle
  would fire on intended designs.

These stay per-seam in their instance PRs, pinned by their probes. **Ask tvofi:** accept this
residue as per-seam, or commission a declared-domain barrier. I recommend accepting it: no form
of that barrier fits within the bound.

The sweep's proposal (a `load_finite_field(..., lo, hi)` helper) was examined and not taken as
the barrier:

- its finiteness check duplicates `QuarantiningStore`;
- its bound is optional per call, so leaving it out is the defect again;
- nothing forces a loader to use it;
- it does not reach instants, keys, containers or wrong types, the shapes of D1-s1-01, D1-s1-02,
  D1-s3-03, D1-s4-03 and D14-s1-01, and the key half of D1-s3-06.

A fixer may still use such a helper inside the instance fixes.

## Plan fold

- **Landing PR:** F1.6 as planned. No change to the PR set or the `after` edges. F1.6 already
  waits on F1.5, F3.3, F4.1 and F9.1, so every P1 instance PR precedes it: F3.1, F3.2, F3.3 and
  F1.4. The arm reads zero only when all of them have merged.
- **Files.** None is code-owned or policy.

  | file | owner lane | status in F1.6 |
  |---|---|---|
  | `custom_components/heatpump_optimizer/store.py` | F1 | owned |
  | `tests/finite_boundary.py` | F9 | already a Borrow in F1.6 |
  | `accuracy.py` (latent seam) | F1 | owned |
  | `coordinator.py` (immersion events) | F1 | owned |

  `tests/run.sh` is untouched, and no new tracked file is added.
- **Lines, from the prototype diff `db878b29..0ade2456`:**
  - production: `store.py` +33/−19;
  - tests: `finite_boundary.py` +402/−4;
  - the two latent seams: `accuracy.py` +3/−3 and `coordinator.py` +6/−1 in the demo, less once
    F3.1's parser exists.
- **Re-disposition, for the orchestrator.** P1-sw1 and P1-sw2 are not store-reachable (see
  Cause). Record them as defence-in-depth, not instances; the class N falls from 11 to 9. Their
  two slots in F1.6 go to the two latent class-search seams (accuracy sample `t`, and
  `immersion_events`), both F1-owned, so F1.6 stays at five.
  - This also applies to the NaN-arm probes of D14-s1-01 (`attempt_peak`), D1-s4-01 and D1-s5-02.
    Each fixer should take its failing test from the arm, or a store-path probe, not from a
    direct `from_dict` call.
  - **Carry this into F1.6's and F3.3's briefs** (`finding-propagation.md`). This seat did not
    edit them.
- **Constraint for F3.1.** The shared stored-instant parser must make every stored instant aware,
  or drop it, at load. That covers `AccuracySample.from_dict`, `immersion_events` and the
  snapshot `taken_at`. Arm 4 refuses a naive instant held live even where no consumer diffs it
  yet. Which zone a naive value is read in is F3.1's decision (the demo uses UTC).
- **Cherry-pick `0ade2456` only**; `99118d35` is demo. Before merging, the fixer re-derives
  `tests/closures.json` for `finite_boundary.py` with `derive_closures.sh --single` on Linux.
- **Budgets:** no raise needed.
- **Optional cost cut, not measured.** 42% of the arm's 4706 mutants are the snapshot `learners`
  subtree and 29% are `accuracy` (the defrost grids). Sampling nested grid rows first and last,
  as scalar lists already are, would cut both. The fixer re-measures if taken.

## Figures

Every figure above comes from the runs in `rca/p1/evidence/`. Commands, from a tree root, with
the CI-pinned deps:

- `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` gives `class_seams`,
  `class_mutants` and `class_unseeded_sections`.
- `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/s1/p1_store.py --barrier` is the
  finder's detector.
- `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P1/probes.py` runs the S3 probes.
