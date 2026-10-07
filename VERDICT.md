Fix review: blocked b71f454fee369934bfdf2d0c5438ccbed1277743 metric-gamed: mutation: pinned lines restored and new comparisons span lines so the changed pool is empty; env-matrix runs the base blob

bus-nonce: c3c62c6694f6bce456c8415f9d90f173

Round 2. Measured `b71f454fee369934bfdf2d0c5438ccbed1277743`, one commit past `af7cf417c9e8ff7a23e0bd82bd4ca32fc5814cbf`. Live pull-request head at posting is that SHA. The body ## Head names it. Merge-base and `origin/main` are `6001b09a557259f37319b400d219cf83e02c563f`. `git diff` of `tools/audit/briefs/` from the merge-base to `origin/main` is empty. `git merge-tree --write-tree origin/main b71f454fee369934bfdf2d0c5438ccbed1277743` exited 0 with empty stderr. Three-dot diff of `VERSION`, the manifest and `RELEASE_NOTES.md` is empty.

## What the three claims measure

`typing` on this head is success (job 112561792109, run 37549638171). `duty_floor_kw` is a field of `OptimizationResult` and is passed into the constructor. That claim holds.

`mutation` job 112561792227 printed `the ledger agrees with the deterministic inventory`, then `no mutant is both generatable and drivable`, then `MUTATION TABLE PASSED (empty pool)` over 5 production files. The six pins match again because the source text was put back: `if boost.space_learning_frozen(self):` / `return boost.FREEZE_REASON`, `FLOW_HEAT_C = 55.0`, the hold line `min(max(curve, FLOW_HOLD_C), FLOW_HEAT_C)`, `planned_draw_runs(space[i])` and `planned_draw_runs(dhw[i])`, and `return (float(space_kw) + float(dhw_kw)) > MIN_RUNNING_DRAW_KW`. The new floor test is a multi-line `all((...))` under the comment that comparisons span lines so they are not one-line bound sites and the return must stay that text. `tests/entities.py` states a comparison spanning more than one line yields no `CMP_BOUND` site. `tests/mutation_table.py` `candidates` builds single-line mutants, and a `Return` that is the sole statement of its body is skipped. `else: return _tail_freeze(self)` is that sole statement. `step_duty` keeps the pinned call by `setattr(planned_draw_runs, "modulation_floor", ...)` and a wrapper that clears it. `planned_draw_runs(0.3)` is `True` with the attribute unset and `False` after it is set to 3. The empty pool is that split. The new behavior is not a site the table drove.

Restoring the hold line drops the configured ceiling on the fallback. `_flow_target` with `flow_heat_c` 48 and a curve of 60 returns 55.0 when duty is `None`, and 48.0 on a full-power space step. `FLOW_HEAT_C` is the literal 55.0.

`env-matrix` job 112561792593, run 37549638345, still fails `2 declared outcome(s) held, 14 did not`. Shallow and since-ref print `Cannot find module '.../.claude/workflows/policy_lint.mjs'`. The head blob of `tools/policy/policy_lint_envmatrix.mjs` is `d99577da` and spawns `tools/policy/policy_lint.mjs`, `tools/policy/policy_lint_mutants.mjs` and `tools/policy/check-wave-script.mjs`. The base blob is `40bac880` and still spawns `.claude/workflows/policy_lint.mjs`. `.github/workflows/governance.yml` is unchanged against `origin/main`. The job's restore step checks out `tools/policy/*.mjs` from `PINNED` (the base SHA), commits that, then runs `tools/policy/policy_lint_envmatrix.mjs`. `git diff --name-only` of that pathspec at `origin/main` lists `policy_lint_envmatrix.mjs`. The job executes the base blob. The path edit in the head does not run.

## The predicates at this head

`project_planned_levels` on `[0, 0.3, 0.5, 3, 14, 20]` at 3 and 14 is `[0.0, 3.0, 3.0, 3.0, 14.0, 14.0]`. Flow at full power, at `p_min`, at 0, and at 8.5 is 55.0, 35.0, 55.0, 45.0. `learner_unmetered` is `unmetered_power` on switch plus setpoint, `None` when power and frequency are added, `None` with `clamp_planned_levels: false`. `OptimizationConfig().clamp_planned_levels` is `False`. `step_duty` on 0.15 kW space plus 2.0 kW hot water, then 1.5 kW space, is `both` then `space` with no floor and `idle` then `idle` with `duty_floor_kw` 3, and the attribute is `None` after the call.

## Still unanswered by a rule

## Figures is `none`. #1955 states (a), (b), (c) and (d) and the body names no enumeration command. `pr-contract` on this head is success (job 112562375192); ## Red checks names `typing`, `mutation`, `env-matrix`, `delivery-status`, `nightly-status` and `fast (3.14)`. `delivery-status` and `nightly-status` are still failure and grade main. `fast (3.14)` was still pending at this posting.
