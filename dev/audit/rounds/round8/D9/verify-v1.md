# D9 round 8, verifier v1 (the only verifier on this panel)

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree `/home/claude/audit-r8/seats/D9-v1` is a git worktree. The machine is the shared 4-vCPU container. load1 was 6.6 to 15.7 during my runs; the finders ran at 13 to 25. Counts and same-session ratios are final. Every wall, CPU and gap figure is provisional.

Both finder seats' evidence is copied in, and every finder harness was re-run from this tree. `s2_gate_blind.py` hard-codes `TMP_ROOT=/home/claude/audit-r8/tmp/D9-s2`. I ran a copy with that path rewritten to `/home/claude/audit-r8/tmp/D9-v1`; nothing else in it changed. `s2_cycle.py` defaults `TMPDIR` to D9-s2's directory, but I ran it with `TMPDIR` set to mine. My own harnesses are the `v1_*` files. Raw outputs are in `v1_out/`.

When I finished, `git diff -- custom_components tests` in this tree was empty. The mutation runs were made on copies under `/home/claude/audit-r8/tmp/D9-v1/`.

## D9-s1-01: discarded per-candidate polishes (vote: verify, low)

**Re-run of the finder's harness** (`s1_polish.py`, three arms run concurrently; they are counts):
- real: 0.0633. 149 of 206 polishes discarded, taking 1200 of 18967 njev. 24 polishes ended ABNORMAL at nit 0, using 501 njev.
- flat: 0.0783.
- maxls 5: 0.0406. Discarded njev went from 1200 to 679, and adopted njev from 3441 to 1715.

Every value matches the report exactly. thread_factor was 1.000 and load1 13.7.

**My own harness:** `v1_polish_kernel.py`.
- Metric: kernel step-equivalents (the `SolverWork` convention) run while `_lbfgsb_restart` was on the stack and whose polished `OptimizeResult` was not returned, over all kernel steps, pooled across the 51 sweep scenarios.
- It hooks a different point from the finder: scipy's `minimize` in the optimizer's namespace, and the kernel rather than njev.

| arm | dropped-polish kernel share | also not shipped (dropped, or adopted then beaten across candidates) | ABNORMAL nit 0 |
|---|---|---|---|
| real | **0.0631** (11.17 M of 176.9 M) | 0.2168 (194 of 206 polishes) | 0.0264 |
| flat | 0.0781 | 0.1911 | 0.0361 |
| maxls 5 | 0.0405 | 0.1246 | 0.0208 |
| no polish | 0 (kernel total 133.7 M) | 0 | 0 |

- My metric agrees with the finder's njev metric to 0.0002. The two are one quantity, because every gradient is one 96x97 batch.
- All polishing together is 24.4% of kernel work: (176.9 M − 133.7 M) / 176.9 M.

**Attacks:**
- **Contention:** counts, so none applies.
- **Gate mode:** not applicable.
- **Grid artefact:**
  - Per-scenario shares run from 0 to 0.414, with a median of 0.131. Only 1 of 51 scenarios has zero.
  - The pooled 0.063 sits below the per-scenario median because the expensive scenarios have lower shares. So the effect is broad, not carried by a single cell.
  - The finder's `leave_one_out.drop_most_favourable` (0.1258) is mislabelled. The code computes the mean of the per-scenario shares with the highest one removed. It is not the pooled share with a cell dropped, as the harness header says.
- **Null control:** the share persists at flat prices (0.078). That is expected for a waste claim, so the flat arm does not discriminate. The perturbation arm does discriminate: it moves in the stated direction under both metrics.
- **Reachability:** `_lbfgsb_restart` runs on every production solve (`_multi_start_minimize`, optimizer.py:626). It runs on the process-worker route, so it costs host CPU but not loop time.
- **Severity by consequence:**
  - "Discarded" is known only in hindsight. The keep rule is decided after the polish has run.
  - The finder's own remedy has a D0 cost. With maxls 5, **9 of 51 scenarios end with a worse shipped objective, by up to +1.06%**, and 1 ends better. Removing the polish makes 12 worse, by up to +1.20%.
  - So no free saving has been shown. The finding is a correct accounting of what the owner-chosen unbounded polish (#1208, override 2026-09-20) costs. Low is the right severity. The one cleanly separable piece is the ABNORMAL-at-nit-0 polishes, at 2.6% of kernel work.

Same mechanism as another finding? None. D9-s1-02 shares the batched gradient but is a different claim.

## D9-s1-02: in-process fallback starves the loop (vote: refute, severity none as a defect; the judge must re-take the timing)

**Re-run of the finder's harness** (`s1_cycle.py`, sequential, two sessions, load1 6.6 to 6.8). Starvation share while the executor was busy:

| session | idle | process route | inline | inline, no yield |
|---|---|---|---|---|
| 1 | 0 (no executor work) | 0.083 | 0.354 | **0.210** |
| 2 | 0 (no executor work) | 0.078 | 0.370 | **0.323** |

- The inline value is 0.35 to 0.37, not 0.65 to 0.90.
- Removing `_gil_yield` **lowered** the share in 2 of 2 sessions. The finder's stated direction is up.
- The inline arms returned `thread_factor` values of 1.055, 1.090, 1.136 and 1.119. Every one is above the README's 1.05 rejection bar, so these runs are formally void. The finder quoted 1.043.
- Maximum gap on the inline route was 13.5 to 25.4 ms, against the finder's 30 to 46.

**My own harness:** `v1_gil.py`.
- Metric: on a real loop with a 1 ms heartbeat, the share of executor-busy wall time spent in gaps longer than 5, 10 and 20 ms, while one real `optimize()` runs on a real `ThreadPoolExecutor` thread in this interpreter.
- The arms are interleaved in one session.
- The null control is a pure-Python arithmetic loop (`pybusy`) of the same wall duration. It stands for any CPU-bound executor job.
- load1 was 7.2 to 7.4. thread_factor was 1.029, and 1.045 in the switch-interval arm.

| arm (median of 4) | >5 ms | >10 ms | >20 ms | max gap |
|---|---|---|---|---|
| idle | 0.035 | 0 | 0 | 6.6 ms |
| **pybusy (null)** | **0.994** | 0.28 | 0 | 17.5 ms |
| solve | 0.483 | 0.12 | 0 | 17.0 ms |
| solve, no yield | 0.606 | 0.13 | 0 | 14.8 ms |
| second perturbation, `sys.setswitchinterval(0.001)`: solve / pybusy | 0.233 / 0.188 | 0.03 / 0.04 | 0 / 0 | 12.5 / 11.8 ms |

**Attacks:**
- **Contention:** the finder's 0.645 and 0.904 were taken at load1 23. At load1 7 the same harness reads 0.35 to 0.37. The magnitude is box load, not code.
- **The metric sits on a structural boundary:** CPython's switch interval is 5 ms. Any CPU-bound Python thread holds a waiting loop out for about 5 ms per hand-off.
  - The pure-Python null starves the loop at 0.99 above the 5 ms cut. The real solve starves it *less*, at 0.48, in 4 of 4 rounds.
  - Above 20 ms, every arm reads 0. The max gap is the same about 17 ms for the solve and the null.
  - `setswitchinterval(0.001)` lowers the solve and the null together.
  - So the batched gradient creates no hold beyond the interpreter's own. The claimed cause ("the batched gradient contains no yield, so `_gil_yield` does not bound the hold") is not what the numbers show.
  - The factual premise is also inexact. The jac calls `memoized(x)` for `f0`, and `memoized` runs `_gil_yield()`, so every gradient call does yield once, just before its batch.
- **The yield does help, a little, in my harness:** 0.61 without it and 0.48 with it. In the finder's own harness today the direction was reversed. Either way this is the existing mitigation working at the margin, not a defect.
- **Reachability and consequence:**
  - The inline route runs only when the process worker is unusable. It is accepted by design (#511: "a slow plan beats none").
  - It raises a persistent repair issue (`solve_worker_fallback`).
  - It is capped at `WORKER_FALLBACK_CAP = 3` consecutive cycles, after which the solve is skipped (#783, coordinator.py:637 and :1209).
  - Real HA does run executor jobs on real threads, so the path is reachable. What it costs is the documented, bounded price of the fallback.
- **Vote:** refute. The refute rests on the same-session null (a ratio between arms under one load), not on the timing mismatch alone. The absolute gap and share numbers are still provisional, and the judge should re-take the null-versus-solve ordering on the quiet box.

## D9-s2-01: no cost-budgeted gate reaches the coordinator cycle (vote: weaken, medium to low)

**Re-run of the finder's harness** (`s2_gate_blind.py`, path-rewritten copy):
- `coordinator`, `sensor`, `process_worker`, `price_model` and `narrative` each read 0. The `optimizer` control reads 1.
- `closure.py select` prints `SKIP tests/stress.py` for coordinator.py.
- `--make-perturbed` moves coordinator from 0 to 1.
- Exact match.

**Re-run of the companion arm** (`s2_cycle.py --cycles 30 --no-rss`, interleaved, two rounds, load1 7.2 to 7.4, thread_factor 1.003):
- inject 1: 0.2906 and 0.2691 of a reference solve (43.6 and 42.4 ms per cycle).
- inject 2: 0.3555 and 0.3577 (52.9 and 53.3 ms).
- The ratio rises 22 to 33%, and loop ms 21 to 26%. The direction reproduces.

**My own harness:** `v1_suite_blind.sh`.
- Metric: the number of Python gate scripts selected for coordinator.py whose exit status or FAIL-line set differs between an unmutated copy and a copy carrying a one-line production mutation.
- The mutation is at `custom_components/heatpump_optimizer/coordinator.py:4569`, the success return of `_async_update_data`. It changes `return self._build_data_dict()` to `return [self._build_data_dict() for _i in (0, 1)][-1]`. That doubles the per-cycle `_build_data_dict` work.
- It runs 13 selected Python scripts. `env_drift.py` and the two Node card scripts are not run: the copies have no .git, and the mutation changes no published value, which is all those three compare.

Results:
- The default (list-comprehension) spelling changed **0** of 13 scripts. The result is `v1_out/v1_suite_blind.txt`.
- The `--tuple` spelling, `(self._build_data_dict(), self._build_data_dict())[1]`, changed **1** of 13: `tests/structure.py` failed on `cross_seam_edges`, `cut_views` and `internal_call_edges` (each +1).
- So the structural ratchet sees a second call *site*, not the cost. The same doubling written without a new call site passes the whole selected suite.
- `deployment_shape`, `entities`, `features` and `golden` fail identically in both copies. Those are no-.git copy artefacts, and their FAIL lines are identical.
- My first default-spelling run flagged `entities.py`. The only differences were the copy's directory name inside FAIL messages, and the order of an `extra=[...]` set in the failing check `a8:register_once`, which fails in both copies. The final run sets `PYTHONHASHSEED=0` and normalises the tree name, and it reads 0. The first run is kept as `v1_out/v1_suite_blind_unnormalised.txt`.

**Attacks:**
- **Contention:** the gate-blindness count is exact. The finder's "+41%" is inflated by a shift in the denominator between two separate sessions: the reference solve was 169.8 ms in one and 155.3 ms in the other. Loop CPU itself rose 29% (43.69 to 56.38 ms). In same-session interleaving I measure +22 to +33%.
- **The title overstates the perturbation:** it says "a 2x loop-thread regression". The perturbation doubles one component (`_build_data_dict`, about 2.3 ms uncontended) and raises the cycle's loop work by 21 to 33%. It is not 2x the loop work.
- **Perturbation (a) is tautological:** it appends coordinator.py to a table and then reads the same table. Only arm (b), plus my suite mutation, shows the blindness in behaviour.
- **Instrument classification:** the harness decides "budgeted" by regex. It misses `tests/features.py`'s `_g525_ticks`, a loop-tick timing check that uses `time.monotonic` (features.py:30559-30575). That check covers shutdown, not the cycle, so the conclusion stands. `tests/nightly_ha.py` has a 240 s wall-clock plan budget in real HA. It is nightly, not in the gate, and far too coarse to see a 2x change.
- **Reachability:** the cycle path runs on every install. The blind spot is real under both SCOPED and FULL, because stress.py never loads coordinator.py.
- **Severity by consequence:**
  - The loop work is a few milliseconds per 15-minute cycle when uncontended. The finder's figure is about 9 to 12 ms, and their Pi 4 extrapolation (an assumption) is 30 to 50 ms.
  - A regression would need to be orders of magnitude larger to matter on a Pi. No such regression, and no leak, is shown: the finder's own retained-bytes and RSS measurements are bounded.
  - This is a real instrument gap with no demonstrated harm. I rate it low, not medium.

Same mechanism as another finding? No. It is independent of D9-s1-01 and D9-s1-02.

## Harness gaps met

- `s2_gate_blind.py` and `s2_cycle.py` hard-code D9-s2's temp root. In `s2_cycle.py` it is only a default.
- `s1_cycle.py`'s inline arms exceed the 1.05 thread_factor bar even after the subtraction the README prescribes.
