# D3-g02 per-key working notes (provisional until each key's gate is recorded)
Probe outcome per key, run from a scratch baseline worktree (never the gate tree), in-memory mutant:
- cd1d099ef87f3ab9 4525 GUARD_OFF: MOVES (pump turn_on->turn_off at step 5/6 of a 4-7 heat plan; off->on at step 10 of a step-0 plan). candidate if gate survives.
- 473508040d23cc21 4528 CLAMP_DROP: MOVES (same as cd1d). candidate if gate survives.
- ad8a02e5c07428ab 4538 GUARD_OFF: MOVES (two-zone cold floor under warm avg: turn_on->turn_off). candidate if gate survives.
- b3a8cff2e5c0a8cc 5654: MOVES at dt=0.15 h exactly (samples 1->0). candidate (boundary).
- 59027d3bdf2e7a0c 5656: MOVES at dt=3.0 h exactly (samples 1->0). candidate (boundary).
- 7d276b43052dbeb9 5658 CMP: 0/9 moved. equivalent-candidate (equal temps -> 0 C/h < positive floor).
- 953a106a1aa39cee 5658 GUARD_OFF: 0/9 moved. equivalent-candidate (warming -> negative/non-finite rate rejected later).
- 4b296fec48fc594f 5663 CMP: 0/6. equivalent-candidate (end guard / floor subsume).
- 58fe17a0726473a6 5663 GUARD_OFF: 0/8. equivalent-candidate (end guard subsumes; features.py says so).
- 2700e28d79c64bd8 5665: MOVES at end delta exactly 4 K (samples 1->0). candidate (boundary).
- 223ac303af04edde 5671 GUARD_OFF: moves 4/8 on direct non-finite calls, reach 0/4 via InputReader -> equivalent-candidate (unreachable).
- 9d324a1dc7a6aa82 5674 >=high: MOVES at observed==high bitwise (samples 1->0). candidate (boundary).
- bb1abbfc58114a17 5674 <=low: MOVES at observed==low bitwise (2 h tie). candidate (boundary).
- 74dbcc2eae2c24f5 5679: moves by 1-2 ulp on 3/9 exact ties; samples equal. candidate (float-rounding only, low).
- 355c3d7dd36a1b90 5782: MOVES at delta_t exactly 6 K (samples 1->0, scale 1.01->1.0). candidate (boundary).
- 206a570d8cc784e3 5800 GUARD_OFF: 0/9 moved though 6 non-finite residuals pass the guard. equivalent-candidate (Cusum + _loss_residual_rejected subsume).
