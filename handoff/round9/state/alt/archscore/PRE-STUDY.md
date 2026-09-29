# Architecture score: pre-study, metric review, calibrated prototype, and a 2× plan

Status: pre-study for tvofi, 2026-09-29. Measured at origin/main `7952d8f9`, and re-based to `f88e6af8`.

- #1771 (register tranche 2) touches no production file.
- #1767 (R9-F1.6) touches six production files, but the score vector, the counters and every per-file figure the briefs cite are identical at `f88e6af8`.
- #1767 is the first live PR scored: **ΔS 0, NULL**. Only the retired `coordinator_loc` moved (−1).

Nothing here is policy. Everything under `handoff/round9/state/alt/archscore/` is a proposal and its evidence.

The question was whether the ratchet budget numbers can be combined into a weighted score such that raising it necessarily improves the architecture.

## 1. The answer

**No, not from the ratchet budgets, and no score can be "necessarily" right.** What can be built is narrower, and it is calibrated:

- **It catches defect introductions.** Planted defects score as a regression in 27 of 28 cases. Real bad commits from main's history score as a regression in 11 of 14. **No bad change in either set scores as an improvement.** Weight sensitivity is flat: halving, doubling or equalising any weight changes no verdict.
- **It is weak at crediting improvements.** It credits 11 of 15 planted good moves, but only 10 of 24 real good commits. The corpus is the holdout: v1's definitions were fixed on planted cases only. On the holdout, 6 good commits are *invisible* (verdict NULL). 8 are refused because one gated metric rises by 1–3 while the score still counts a gain, or because the change is priced wrongly.
- **The 24 structure metrics are mostly unfit for an architecture score.** On the historical corpus they track size, not the defect shapes (§3). The perturbation review retires 11, merges 7 into 2 rows, and finds 11 new metric defects (§2).

- **It is easy to game** (§7). The red team raised S with 13 of 16 moves that make the architecture no better, from +0.5 to +160. The worst is a 5-line class rename worth +101, which is half the 2× target. v1 scores EG-B1's and EG-B3's honest steps exactly as it scores their evasions.
  - Eight prototyped counters close all but one game: feature deletion, which only the behaviour suite can see.
  - The counters change no GOOD verdict on the holdout.

So the property that holds is one-sided, and **only with the counters**:

- An increase of S under the gate means no measured defect shape was introduced, and none of the known evasions was used.
- It does *not* mean the architecture improved in every way a reviewer would judge.
- Any evasion the red team did not try is still open.

**Goodhart's law is measured here, not assumed.** The honest role for S is a **report-only review trigger with a calibration self-check and the red-team attempts as regression cases** (§9). It is **never a target a seat is rewarded for moving.** The 2× plan (§8) is a plan of real changes whose deltas S *reports*. It is not a mandate to raise S. This changes in round 10 only if one wave of report-only data, with the counters in place, supports it.

## 2. The 24 structure metrics: soundness by perturbation (A1)

**Method** (`a1/metric_review.md`):
- 30 deterministic perturbations of `7952d8f9`: 6 good moves, 17 bad moves, 6 nulls, plus 1 control.
- Each one compiles, imports under `tests/hastub`, and adds no new ruff F finding (B8 excepted, by design).
- Each is measured with `tests/structure.py`'s own `measure()`.
- The harness is stable: N1, a rename at 18 sites, moves 0 of 24 metrics.

| verdict | metrics |
|---|---|
| **retire** | `attrbag_classes_over_30`, `classes_over_300`, `internal_call_edges`, `local_imports` (→ `import_cycle_modules`), `coordinator_methods` (→ footprint) |
| **retire from the architecture score** (keep as quality ratchets) | `const_modules_over_50`, `functions_cc_over_15`/`_25`, `max_cc`, `max_method_loc`, `methods_over_150`/`_200` |
| **merge** | `coordinator_loc` into `max_class_loc` (identical in 30/30); `cross_seam_edges` and the five `cut_*` rows into one `seam_cut_total` |
| **keep + modify** | `coordinator_attrs`, `coordinator_multiassigned_attrs` (count writers outside the class), `max_class_loc` (as a footprint in logical statements), `duplication_blocks` (AST windows, package-wide), `dead_methods` and `dead_top_level_symbols` (quality, not architecture; resolve by receiver and through `import *`), `seam_cut_total` (charge `f(coord)` functions to their seam; compute against the base's seam map) |

**Metric defects verified by perturbation with a null.** None of these is #1738 a/b/c or the known blindness to dead properties:

1. **Ranking inversion.** B7 moves a cluster out as free functions of `coord` and adds 37 private reaches. It outscores G3, the real extraction, on 6 metrics (cross_seam −7 vs −3, cut_learning −13 vs −8, and so on).
2. **Writes from outside the class vanish from the attribute census** (B7 −1; B4c 0 vs B4b +1).
3. **In-place mutation of a long-lived shared object is invisible** (B4a: every row reads 0).
4. **`duplication_blocks` depends on formatting.** An AST-identical re-wrap reads −2, and 8 of its 14 baseline rows are parameter lists.
5. **The line-span metrics move on nulls.** A reformat gives `max_method_loc` +38; a docstring gives +4 and +5.
6. **`const_modules_over_50` measures import spelling.** The null reads −1; a star import, a bad move, is rewarded −1.
7. **A seam-map relabel alone lowers the cut table.** `cut_learning` −21; 100 of 1,120 single relabels lower it.
8. **Meaningless pass-through chains are rewarded.** `max_cc` 48 → 34; `methods_over_200` −2.
9. **Good local refactors are penalised.** Extract Method, a dedupe and a new public accessor each read +1 on method and edge counts.
10. **`dead_top_level_symbols` reports 42 live constants dead** under `import *`.
11. **No metric sees an import cycle.** The package's first module-level cycle reads 0 everywhere.

**The four other ratchets** (coverage, typing, mutation, stress) are test-adequacy, annotation, test-strength and performance constraints. They stay constraints and stay out of an architecture score.

## 3. What the ratchet actually tracks: a historical corpus (A2)

`a2/corpus.tsv` holds 45 commits from main's history: 14 BAD, 24 GOOD, 7 NEUTRAL. Each is labelled from a source that does not use a metric: an RCA, a probe-confirmed screen verdict, an issue, a PR body or an owner decision. The quote is in the row.

The measurer is the current `structure.py`, applied to both sides of each commit with one seam assignment. It reproduces the before/after figures quoted in #506, #551, #750, #1751 and #1765 row for row.

- **The ratchet fails 11 of 14 BAD commits, but for growth.** 9 of those 11 are features of 255–1,665 lines. On the defect-sized BAD commits, every structure row is flat or moves the wrong way:
  - #1752's introduction (`07bdc557`, sev:high) moves no row up;
  - `a1bdb11c` and `546b4924` move nothing.
- **`duplication_blocks` never moved on any of the 38 labelled GOOD and BAD commits.** That includes every duplication introduction and every deduplication.
- **The best separator, `coordinator_loc` (+.55), comes from how the commits were chosen**, not from seeing defects: GOOD is mostly coordinator-shrinking stages, BAD mostly coordinator-growing features.
- **The round-9 enumerators do respond to their classes.** m3 (reach) fires on both reach-through BAD commits; m2 fires on the payload key with no producer; m1 on hub-writing introductions. Each sees one class only.

## 4. New metrics (A3) and the v1 fixes

A3 built nine stdlib-only AST metrics (`a3/metrics/`). Each is deterministic under three hash seeds and runs in under 1.7 s (all nine in 2.4 s). Each rose on a planted control, fell on a planted fix and held on a null (`a3/controls.out`).

**At baseline:**

| metric | value |
|---|---|
| `hub_solve_writes` | 40 |
| `shared_inplace_writes` | 22; exactly the 12 + 4 sites the #1752/#1753 fix removed, measured at the fix's parent and at the fix |
| `private_reach` | 92 |
| `untyped_payload_keys` | 164; 0 TypedDicts, and one live read with no producer: `horizon_hours`, `sensor.py:1511`/`:1544` |
| cross-module duplication | 5 |
| import cycles | 0 |
| public surface | 515 (6 unused) |
| `dead_by_reachability` | 6 of 1,560 members; `structure.py` reads 0 |
| `family_splits` | 3; the three `tests/entities.py` allows |

**v0 calibration found four definition faults.** A1 and A3 had predicted each before the run, and each was fixed in `b/metrics_v1.py` using planted cases only:

1. **The coordinator footprint found `f(coord)` functions by parameter name.** Renaming `coord` to `owner` in `pump_arbiter.py` hid 232 statements. v1 finds them by role, using A3's role engine.
2. **The footprint counted plumbing.** A new call, an alias or a one-line accessor made an extraction read as growth. v1 counts logic statements only.
3. **`dup_pairs` depended on names.** A local rename and a `const.X` spelling both moved it. v1 alpha-renames a function's own names and reads `mod.X` as `X`.
4. **The two import-cycle prototypes disagreed.** v1 includes function-scope imports and excludes `TYPE_CHECKING` imports.

`a1_params_over_10` also enters the score, as A1's guard against fragment chains.

## 5. The score

- **Definition** (`b/arch_score.py`): S = Σ wᵢ · log₂((refᵢ + 1)/(curᵢ + 1)) over 12 metrics.
  - Halving any metric is worth wᵢ, whatever its scale.
  - The absolute form is a *log-debt*, D = Σ wᵢ · log₂(1 + xᵢ), and ΔS = D_before − D_after.
  - The index is AI = 100 · D_ref/D, with `7952d8f9` = 100.
- **Gate:** no score metric may rise. Every metric is a deterministic static count, so the tolerance is 0.

**Weights** (`b/weights.json`): wᵢ = log₂(1 + cost in hours) of the register-v2 class the metric guards, and floor 1.0 for a metric that guards no class.

- The cost is max(instance total × 5.4 h, the class RCA's h/month). 5.4 h is RCA-BULK-2's measured mean per instance; the rounds span 2026-09-01..29, so stock and monthly rates are on one scale.
- The file was frozen, and its sha256 recorded, **before the first calibration run**. Two amendments are recorded in the file, both made before that run:
  - **P2+P3 → `dup_pairs`:** the line-based cross-module count moves on a reformat.
  - **`dead_by_reachability` → the floor:** N-structure-blind's 150 h/month is the cost of the *instrument's* blindness, not of a dead member.

| metric | guards | w | baseline |
|---|---|---|---|
| `dup_pairs_v1` | P2+P3 (486 h) | 8.93 | 121 |
| `untyped_payload_keys` | P6 (119 h) | 6.90 | 164 |
| `hub_solve_writes`, `shared_inplace_writes` | N-shared-config (85 h/month, shared) | 5.44 each | 40, 22 |
| `family_splits` | N-name-sort (43 h) | 5.47 | 3 |
| `coord_footprint_v1`, `a1_coord_writers_multi`, `private_reach`, `import_cycle_modules_v1`, `public_unused`, `dead_by_reachability`, `a1_params_over_10` | the floor | 1.0 | 2512, 130, 92, 0, 6, 6, 28 |

**Log-debt at `7952d8f9`:** D = 212.8. Most of it sits in four metrics:

| metric | share of D |
|---|---|
| duplication | 61.9 |
| untyped payload | 50.9 |
| hub writes | 29.2 |
| shared in-place writes | 24.6 |

## 6. Calibration results

The acceptance bar was that every case classifies correctly. **v1 does not meet it, and nothing is hidden.** The complete per-case table is `b/calibrate_v1.out`; v0's is `b/calibrate_v0.out`.

| set / label | v0 | v1 | v1 misses: blind / wrong-way |
|---|---|---|---|
| planted GOOD | 9/15 | 11/15 | 3 / 1 |
| planted BAD | 27/28 | 27/28 | 1 / 0 |
| planted NULL | 12/15 | 14/15 | 0 / 1 |
| corpus GOOD (holdout) | 12/24 | 10/24 | 6 / 8 |
| corpus BAD (holdout) | 11/14 | 11/14 | 3 / 0 |
| corpus NEUTRAL (holdout) | 6/7 | 6/7 | 0 / 1 |
| **total** | 77/103 | 79/103 | |

**Reading the misses:**

- **BAD blind (3 corpus, 1 planted).** All three corpus misses are classes the static set does not reach:
  - a duplicated input-stamp rule, below the clone window (`a1bdb11c`);
  - a module-global fallback streak, where `shared_inplace_writes` does not follow module globals (`546b4924`);
  - a family split whose production family declaration did not yet exist, so `family_splits` is NA on that tree (`ca711b56`).
- **GOOD blind (6).** These are decompositions outside the coordinator (the optimizer's DHW builder, a table in `ThermalParameters`), complexity-only extractions (the retired rows), and centralisations the clone window does not see. **The footprint prices only the coordinator; the optimizer class is invisible.** EG-B5 will read ΔS ≈ 0.
- **GOOD wrong-way (8).** Two carry a positive ΔS but fail the gate on a +1 incidental rise: EG-B9's fix (#1765) at +4.14 with `private_reach` +1, and W4-G2 at +0.42 with `dup_pairs` +1 and footprint +28. The largest miss is #597, the settings registry: `dup_pairs_v1` 98 → 124. The registry made the option pages' step functions identical, and pair counting is quadratic in cluster size. The rest are +1 to +3 rises on `params_over_10`, `dead_by_reachability` or the footprint.
- **NEUTRAL wrong-way (1).** The compare-and-restore repair of the away envelope (#1563) lowers the hub-write site count. RCA-1736 says it left the pattern in place.
- **Planted residue:**
  - N4 still moves `dup_pairs_v1` +1: a `const.X` window forms one new pair;
  - G4b's new accessor is counted as a logic statement;
  - B3b's chain inside the coordinator uses fewer than 11 parameters;
  - G1 and A3's public-surface fix are NULL, by the retirements;
  - A3's cross-module fix is below the clone window.

**Gate variants** (`b/gate_variants.out`). These are reported, not chosen by fit:

| gate | corpus GOOD | corpus BAD | BAD credited as improvement |
|---|---|---|---|
| strict (all metrics) | 10/24 | 11/14 | 0 |
| class metrics only | 11/24 | 11/14 | 0 |
| none (sign of ΔS) | 12/24 | 10/14 | **1** |

Dropping the gate starts crediting a BAD change. That is the case for keeping a gate, but as a **review trigger that asks for a stated reason**, the way a budget raise does, rather than an automatic refusal.

**Weight sensitivity** (`b/sensitivity_v1.out`): every weight at ×0.5 and ×2, and all weights equal, gives 79/103 with the identical misclassified set. Classification is decided by the gate and the signs; the weights only set magnitude.

**Trajectory of the last 20 merges** (`b/trajectory_v1.out`):

- `cdbca706` raised `family_splits` 3 → 5 (ΔS −3.20). The same trees show `3defa2d5` (F7.4) brought it back to 3, with `public_unused` +1.
- #1765 (EG-B9) is ΔS +4.14, with `private_reach` 91 → 92.
- Net over the 20 merges: S −3.90 → 0.00.

## 7. Red team (`redteam/redteam.md`)

One seat made 16 scripted attempts, plus a null, on scratch trees of `7952d8f9`, each trying to raise S while making the architecture no better. Every edited tree compiles and imports. **13 attempts succeeded, 3 were stopped by the gate, and the null scored 0.** For scale:
- the best real GOOD merge in the corpus scores +0.795 under v1;
- the games score +0.47 to +160.

| # | move | metric moved | ΔS |
|---|---|---|---|
| 05d | **rename the coordinator class and append an empty subclass (+5/−1 lines)** | payload, hub, shared, footprint, writers | **+101.1** |
| 01 | a `total=False` TypedDict with every value `Any` | untyped_payload_keys 164 → 0 | +50.9 |
| 04 | a no-op `id(N)` inside every clone window | dup_pairs_v1 121 → 7 | +35.1 |
| 02 | hub writes re-spelled `object.__setattr__(hub, "f", v)` | hub_solve_writes 40 → 0 | +29.2 |
| 03 | in-place writes via `type(X).__setitem__` and a string-dispatch helper | shared_inplace_writes 22 → 0 | +24.7 |
| 07 | stragglers declared as one-member families | family_splits 3 → 0 | +10.9 |
| 08 | a keep-alive lambda that touches the dead members | dead 6 → 0, public_unused 6 → 0 | +5.6 |
| 06 | public `raw_<x>` passthrough properties | private_reach 92 → 13 | +2.7 |
| 09 | delete a working feature | hub 40 → 31 | +1.9 (`features.py` fails 5 checks) |
| 10 | `self.X = v` → `setattr(self, "X", v)` | writers 130 → 59 | +1.2 |
| 11 | keyword parameters → `**kw` | params_over_10 28 → 20 | +0.5 |
| 12 | 01+02+03+04+06+07+08+10+11 in one change | 11 of 12 metrics | **+160.7** |
| 05, 05b, 13 | move the methods into a mixin; route the hub through an accessor | — | stopped, **but only by another metric's side effect** |

**The consequence for the 2× plan is direct.** Its two largest steps score exactly what their evasions score:
- **EG-B1's hub-write removal:** 02 scores +29.2;
- **EG-B3's typed payload:** 01 scores +50.9.

v1 cannot tell the honest step from the evasion.

**The four holes:**
- **Name-keyed identity:** the coordinator class name.
- **Spelling-keyed write detection.** v1's plumbing rule even *credits* `setattr` as non-logic.
- **Declaration-keyed metrics** that never check the declaration constrains anything.
- **The log-to-zero payoff:** evasion is exactly the move that reaches zero.

**Counters, prototyped in `redteam/counters/`** (identical on the baseline and the null):

| counter | closes |
|---|---|
| C1 `untyped_payload_keys_v2`: `Any`/`object` is not typed | 01 |
| C2 `reflective_writes`, C2b `computed_attr_access` (gate-only tripwires) | 02, 03, 10, 13 |
| C3 `dup_pairs_v2`: drop effect-free statements before comparing | 04 |
| C4: measure the coordinator as its whole package class hierarchy | 05c, 05d |
| C5 `private_reach_v2`: a trivial passthrough property counts as a read of its private | 06 |
| C6 `family_orphan_overrides` | 07 |
| C7 `unread_private_globals` | 08 |
| C11 `params_over_10_v2`: literal keys read from its own `**kw` count as parameters | 11 |

**With all counters,** every game except 09 becomes NULL or inadmissible, and the combination (12) is inadmissible.
- **Holdout:** one corpus verdict changes, and it is a correction. #1563's partial repair goes from IMPROVES to WORSENS on `reflective_writes`.
- **No GOOD case is newly blocked.**
- **The tripwires are a stopgap.** The principled fix reads reflective spellings as the writes they are, in a3's `write_sites`, and evaluates method return values in its role engine. W4-G2 (`67e1cf33`) also raises both tripwires.

**No structural counter exists for 09**, deleting a feature. The behaviour suite catches it. So a score is only reported for a change whose behaviour suite stays green and whose check count does not fall.


## 8. A 2× improvement plan, from real improvements only

**Target:** AI 100 → 200, that is, D halved, 212.8 → 106.4. Arithmetic: `b/plan2x.py` → `b/plan2x.out`.

| step | group | metric targets (from the brief) | ΔS | AI after |
|---|---|---|---|---|
| 1 | R9-EG-B1 per-solve input record (planned) | `hub_solve_writes` 40 → 0; `optimize` takes the record keyword-only (params_over_10 28 → 22) | +29.5 | 116 |
| 2 | R9-EG-B3 typed payload contract (planned) | `untyped_payload_keys` 164 → 0, **real value types, not `Any`** | +50.9 | 161 |
| 3 | R9-EG-B6 collaborator interfaces (planned) | `private_reach` 92 → 13 (pump_arbiter 37, boost 9, diagnostics 8, `__init__` 7, away 7, wood_fuel 7, services 2, setpoint_check 2); collaborator in-place writes −4 | +4.2 | 166 |
| 4 | R9-EG-B2 surface accessors (planned) | `private_reach` 13 → 0 | +3.8 | 171 |
| 5 | R9-EG-B7 two coordinator seams (planned, conditional) | footprint 2512 → 1900, writers 130 → 90, shared in-place 18 → 10 | +5.2 | 179 |
| 6 | R9-F10.4 dead members and unused publics (planned + carry) | 6 → 0 and 6 → 0 | +5.6 | 187 |
| 7 | **new R9-EG-A2** one copy per formula and helper | `dup_pairs_v1` 121 → 40: the scalar and batch physics steps in `thermal_model` (a P3 risk), `_finite` in `freq_control`/`inputs`, the store-load prelude, the sysid r², and the option-flow step factory | +14.1 | 214 |
| 8 | **new R9-F7.5** the three recorded family splits (owner-gated, user-visible names) | 3 → 0 | +10.9 | 240 |
| 9 | **new R9-EG-A3** parameter objects | params_over_10 22 → 14 | +0.6 | 242 |

**Robustness of the 2×:**

| weights | final AI |
|---|---|
| frozen | 242 |
| dominant weight (payload) halved | 213 |
| all weights 1.0 | 204 |
| frozen, without F7.5 | 215 |
| frozen, without EG-B3 | 153 |

EG-B3 is indispensable. Steps 1–6 are all already planned and reach AI 187 on their own. The 2× needs one new group (EG-A2) on top.

**What makes an improvement count.** These are review obligations, stated in each brief:

1. It removes an instance of a register class or a measured defect shape, named in the PR body with its per-metric deltas.
2. Behaviour holds: the goldens stay byte-identical for every refactor step.
3. None of the red-team moves in §7 appears in the diff. The reviewer checks the list, and the ΔS is measured **with the counters** (`redteam/counters/`, and in-tree once EG-A1 lands). A step whose ΔS appears only without the counters did not happen.
4. A gate rise is explained in the PR body, like a budget raise.
5. **Honest does not mean at zero.** A target is met where the defect is gone, not where the count is. A payload key typed `Any` is not a contract; a public passthrough property over a private is not an interface.

## 9. Implementation: combined with round 9, not after it

**Why combined:**
- 80 of the 106 points sit in EG-B1 and EG-B3, which round 9 already plans.
- Waiting until after round 9 loses the measurement of exactly those PRs.
- Running it staggered as a separate programme would re-open files EG-B1/B3/B6/B7 own.

**The plan:**

1. **R9-F10.4 (planned, ratchet truth) absorbs the metric changes** from §2 and §4:
   - retire the rows listed, merge coordinator_loc and the cut table, and add the v1 fixes, `import_cycle_modules_v1`, `dead_by_reachability` and `family_splits` as ratcheted metrics;
   - each at its measured baseline, as a *re-record with a reason*, not a raise;
   - with the 11 metric defects carried into its brief.
2. **New R9-EG-A1, "architecture score, report-only"**, after R9-F10.4:
   - lands `arch_score.py`, the metric modules and the calibration corpus under `tools/audit/archscore/`;
   - prints ΔS and the per-metric deltas as a report line in CI and the PR body;
   - lands the §7 counters first: C1, C3, C4, C5, C6, C7 and C11 as metric fixes, and C2/C2b as tripwires until `write_sites` reads reflective writes;
   - fails only its own self-check (a regression test on the instrument, not a gate on PRs):
     - the corpus and planted cases must classify as §6 records, amended by the counters' one correction;
     - **every red-team attempt must stay NULL or inadmissible**;
   - no budget raise, no policy.
3. **The planned groups state their expected ΔS** in their briefs (the step table above). The reviewer compares the measured value. That applies to EG-B1, B2, B3, B6, B7 and F10.4.
4. **New R9-EG-A2 (clone consolidation)** follows EG-B5 and EG-B3, which own `optimizer.py` and the payload. **R9-F7.5** and **R9-EG-A3** are owner-gated and small.
5. **Round 10:** after one wave of report-only data, tvofi decides whether "ΔS ≥ 0, or an explained gate rise" becomes a required check. That is policy (0013-style owner approval). The v2 metric fixes (§10) are evaluated then, on a fresh holdout: round-9 merges labelled from their RCAs and reviews.

**Duration.** This is measured from the 33 round-9 merges, 2026-09-26T23:08Z to 2026-09-29T10:59Z:
- **Throughput:** 1.9 h per merge across the lanes.
- **The serial F1 lane:** 5.6, 7.9, 8.3 and 11.1 h per step.
- **The critical path from here** (F1.6 merged as #1767) is 12 serial PRs: F2.4 → F1.7 … F1.11 → F10.4 → F10.5 → F10.6 → EG-B1 → EG-B6 → EG-B7.
  - That is about 67–133 h, or **about 4 days at the mean** of continuous operation.
  - 5–7 days is realistic: the remaining chain is heavier, and throughput has already slowed. F1.6 took about 17 h from dispatch (05:23Z) to merge (22:46Z) and two review rounds, against the 8.2 h mean.
  - Owner-gated waits come on top.
- **The rev-3 groups add no serial time** and about 7 h of parallel capacity.
- **When AI passes 200:** when EG-A2 merges, at depth 11 of 13.

## 10. Known limits, and the v2 queue (not applied: the corpus holdout is spent)

- **Coordinator-only size.** Charge every class over a threshold, the optimizer included, or EG-B5 stays invisible.
- **Pair counting is quadratic.** Count redundant copies (members − 1 per window), which fixes #597's +26. Blank a framework's step-function idiom only if a null shows it is idiom, not logic.
- **Site counts credit partial repairs** (#1563). Count the *shape* (a hub write reachable from a solve at all), not the sites.
- **`shared_inplace_writes` does not follow module globals** (`546b4924`).
- **Deleting a feature raises S** (red team §7). The score cannot see functionality. Tests, coverage and "never delete working functionality to fit" stay the constraints.
- **Unknown evasions.** The counters close the 16 moves tried. A new spelling is a new red-team case, added to EG-A1's self-check when found.
- **The zero-target bonus.** Log-ratio to +1 makes the last few instances of a class worth as much as the first many. It is intended (a class at zero is a class closed), but it makes EG-B3 carry 48 % of the 2×.
