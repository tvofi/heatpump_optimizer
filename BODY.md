Fix review: blocked 19dff27fe599c934aa0441ae5c5f98035fc30914 correctness: _apportion_by_steady_demand never terminates when capping cascades

## Block
The cap-and-redistribute loop in HeatPumpOptimizer._apportion_by_steady_demand replaces the held set each pass (`held = over`, optimizer.py:) instead of accumulating it (`held = held | over`). When redistributing the excess pushes a second step past the pump, the first held step is released, re-exceeds the cap, and the two sets alternate forever. The `while` has no other exit, so the solve hangs (no iteration bound).

## Findings
- custom_components/heatpump_optimizer/optimizer.py: `held = over` drops previously held steps; it must be `held |= over`. Reproduced on the production method (fake self, patched _floor_demand_at_target): 7 steps, steady demand [1.69, 9.70, 5.21, 1.25, 6.27, 7.79, 6.17], pump cap 3.0, horizon energy 18.34 -> infinite loop (SIGALRM after 10 s, rc 142). With `held = held | over` it returns [1.92, 3, 3, 1.42, 3, 3, 3], energy conserved, max == cap.
- Randomised model of the loop (20000 draws, 3-7 steps): 3386 cases loop forever with replace semantics that terminate correctly with accumulation.
- tests/features.py (new spread checks, ~44270-44320) only exercise one-pass cases (one step over the cap), so no test reaches the cascade; the fix's own tests pass the defect. A cascading-cap case (two or more passes) is missing.

## Evidence
- git diff 661d26a5...19dff27f reviewed (optimizer.py, tests/features.py, ledger files).
- Repro script run at head: Alarm clock, rc=142 (hang). Same script with held = held | over: rc=0, output above.
- Full tests/features.py not completed in my budget; I stopped it and reverted the mutation (git status clean).
