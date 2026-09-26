# D7 round 9 — verifier V1 (reproduce)

Box G4-V1. Unit D7: D7-s1-01, D7-s1-02, D7-s2-01, D7-s2-02, D7-s3-01 and D7-s3-02.

Tree: `handoff/audit-r9-evidence` at 6f51db2. `git diff 1936d5ca..HEAD -- custom_components tests` is empty, so production and tests are the baseline's. Every run used `/home/claude/venv/bin/python` (3.14.0rc2) with `PYTHONPATH=tests/hastub`. Load was load1 1.2–3.5 with thread_factor 1.000 throughout. Every number below is a count, so contention does not affect it.

Logs are under `tools/audit/round9/D7/verify-v1/`. One harness was written there, `headroom.py`, which prints budget minus measured for every `structure_budgets.json` row. Run it with `PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v1/headroom.py`.

The only on-disk mutation was made in a private `git worktree`, which was removed afterwards. Both stress.py runs went through `tests/gate_lock.py auto-lease --label g4v1-d7`.

## D7-s1-01: the ratchet does not price `_helper(self, ...)` (verify, low)

**Re-run** (`helper_escape.py`, log `s1_01_base.log`):
- helpers 11, state refs 30, coordinator calls 8.
- Inlining `_fold_flow_lift` raises 4 rows, cut delta 8.

**Perturbation** (`--helper _warm_seeded`, log `s1_01_perturb.log`): cut delta 0.

**Leave-one-out** (`--all`, log `s1_01_all.log`): 10 cells, sum 36, min 0, max 12. Dropping the largest cell leaves 24, and 8 of 10 cells are non-zero.

**Independent check** (`headroom.py`, log `s1_01_headroom.log`):
- The four seam rows the inlining raises all sit at zero headroom: cross_seam_edges 136, cut_learning 285, cut_grid 197, internal_call_edges 317.
- Caveat: all 25 rows are at zero headroom, including coordinator_methods and coordinator_loc. Inlining would therefore fail the ratchet on those rows too.
- What holds is that 30 state refs and 8 coordinator calls go unpriced, and the refused shape is rewarded by 8.

## D7-s1-02: the drift comparison and the stress per-scenario verdict are deletable with checks green (verify, medium)

**Re-run** (`train_mutations.py --only drift_leaf,drift,stress`, about 17 min, log `s1_02_arm.log`):
- Driver baselines are red because the copied tree has no `.git`: entities.py 13 failing, features.py 2 failing.
- The `drift` mutant survives both drivers, and so does the `stress` mutant.
- `drift_leaf` is killed by entities.py: failing checks go from 13 to 20, with fresh check names.
- Survivors: 2, as the finding states.
- Inconsistency for the judge: `train_mutations.py`'s own header expects `drift_leaf` to survive without `--pin-leaf` (3 survivors). The executed run and REPORT.md both say it is killed (2 survivors).

**Independent real-gate measurement** (private worktree):

| gate | production perturbation | pristine gate | gate with the mutant |
|---|---|---|---|
| drift (`env_drift.py 1936d5ca`, default 5 fixtures, private `DRIFT_CACHE_DIR`; logs `s1_02_gateA/B.log`) | `outdoor_temp -= 0.5` in `ThermalModel.simulate_step` | 5 UNCLAIMED DRIFT, rc=1 | "NO UNCLAIMED DRIFT: 5 scenario(s) checked", rc=0 |
| stress (under the lease, `GOLDEN_REF=1936d5ca`; logs `s1_02_stressA/B.log`) | `STRESS_SCENARIO_FACTOR=0.01` | per-scenario budget check FAILs, 51 scenarios listed | the same check reads ok |

The other FAILs in the stress arms are not the verdict under test:
- Two pins read the environment factor directly, and they fail in both arms.
- One kernel-timing check failed in arm B under contention.

**Attacks:**
- Gate mode: this used the default 5 fixtures, not `--all`. The mutant deletes the comparison for every scenario, so `--all` cannot differ.
- Real-HA reach: not applicable, since these are CI gate scripts.
- Severity: a deleted verdict lets the only behavioural gate on a scoped PR print green on a drifting branch, so medium holds.

## D7-s2-01: the sysid Euler rollout biases UA (verify, medium)

**Re-run** (`sysid_plant.py`, log `s2_01.log`), UA bias against truth integrated at 30 substeps:

| preset | UA bias |
|---|---|
| light_new | −16.8 % |
| heavy_old | −25.5 % |
| typical_slab | refused |

3 of 3 presets are biased by more than 5 % or refused, and none is adopted.

**Null control** (truth at the fit's own step): heavy_old and typical_slab come out at +0.00000 and are adopted. light_new is refused at this step as well. A free two-exponential fit stays within 0.6 % on all three.

**Perturbation** (`--substep-rollout`, log `s2_01_perturb.log`): 0 presets biased, 2 adopted.
- heavy_old −0.85 %.
- typical_slab −1.87 %.
- light_new is still refused, with a ±16 % interval.

**Dose-response:** the bias grows monotonically over sub2, sub6 and sub30.

**Leave-one-out:** only 3 cells, so fewer than the 5 COMMON.md asks for. Dropping any one preset leaves 2 of 2 biased or refused.

**Reach:** the biased UA is published in coordinator `data['system_identification']` (`heat_loss_kw_per_c`) even when adoption refuses it.

**Caveat:** light_new never adopts in either arm, so the headline is 2 of 3 adopting on each side, not 3.

## D7-s2-02: the defrost derate folds intervals that `_cop_fold_blocked` refuses (verify, medium)

**Re-run** (`learner_gates.py`, log `s2_02.log`): the derate ingests 3 of 3 distorting arms. The COP learner ingests 0 of 3.

Derate factor after 24 intervals:

| arm | baseline | `--gate-derate` (log `s2_02_perturb.log`) |
|---|---|---|
| immersion | 0.8738 | 1.0000 |
| backup | 0.8738 | 1.0000 |
| capacity (seeded 0.80) | 0.9769 | 0.9208 (raw 0.80) |
| clean control | folds, stays 1.0000 | still folds |

With `--gate-derate`, 0 of 3 distorting arms are ingested.

**Leave-one-out:** each arm is 1 on its own.

**Reach:** the path is coordinator logic. V3 owns the real-HA check.

## D7-s3-01: dead class members (verify, low)

**Re-run:**
- `reach.py --list` (log `s3_01_reach.log`): 9 dead members, 1 method and 8 properties.
- `reach.py --perturb-live next_optimization` (log `s3_01_reach_perturb.log`): 8.
- `sentinel.py` (log `s3_01_sentinel.log`): 0 of 10 dead members called from production. The live controls are all seen (6 of 6), over 12 update cycles, 450 entities and 2808 attribute reads.
- `sentinel.py --perturb` (log `s3_01_sentinel_perturb.log`): 1.

**Independent check:** a grep for these names across custom_components found them only as coordinator.data keys, entity key strings or snapshot keys. No production code reads any of them as a property.

## D7-s3-02: `dead_methods` reads 0 (verify, low)

**Re-run** (`screen.py`, logs `s3_02_*.log`):

| arm | dead_methods |
|---|---|
| baseline | 0 |
| `--no-property-exclusion` | 5 |
| `--attribute-only` | 1 |
| both | 11 |

- The two rules overlap, which is why 5 + 1 does not add up to 11.
- The 11 include climate `hvac_mode` and `preset_mode`, which HA reads. The finding says its fix must list them.
- `dead_methods` is budgeted at 0 with 0 headroom.

## Not run
- The `--pin-leaf` arm of `train_mutations.py`: not needed, because `drift_leaf` was already killed.
- `env_drift --all` on the drift mutant: it would add nothing, since the deletion covers every scenario.
