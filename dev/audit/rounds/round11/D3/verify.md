# D3 verify, round 11 (one verifier, three lenses)

Tree: git worktree at handoff/audit-r11-register 28b864af6d (D3-s2 is not a planted-tree seat). load1 4.25-6.31, thread_factor 1.00; all numbers are counts, contention-immune.

## D3-s2-01 — vote: weaken

V1 reproduce (finder harness, header command, python3 since $HOME/venv-ci absent):
- with closures.json at the register head: claimed 296, clean 170, over 27; payload.py 535.5 s of 3887.4 s (9 of 27 scripts).
- with closures.json from baseline 92d38ecb (restored afterwards): clean 170, over 27; payload.py 525.7 s of 3051.3 s (9 of 27). The seconds reproduce exactly; the pair count is 27, not the claimed 29.
- Perturbation `--claim-only tests/plan_view.py:payload.py`: over 27 -> 26, payload 9 -> 8 scripts, 535.5 -> 533.7 s. Moves in the stated direction.
- Null control: cells with no over-pairs (sensor, climate, const, ...) report 0.0 s; arch_score_head-type scripts that read the file are not counted (read=True, OVER=False).
V2 independent: own script parsing payload.py's function spans with ast and checking each reach JSON's hit lines for any line strictly inside a function span: all 9 named scripts (boost_drift_replay, debug_collect, guard_pins, manual_plan, optimality, plan_view, solar_alignment, validate, wood_advisor) have 0 body-line hits while claiming payload.py. Independent value: 9 scripts, agrees.
V3: reach — test-gate cost only (closure.py select on a branch diff), not a Home Assistant runtime path; severity low (CI seconds, ~535 s per payload body edit, no correctness loss: over-approximation is the safe direction). Seam rule: the harness enumerates all 23 cells and all scripts, so it enumerates the seams, not only payload. Class: new (no bugclasses.json entry for closure over-approximation) — confirmed.
Weaken because: count 29 does not reproduce (27 of 170), and the over-selection is safe-direction cost, not a defect in gate correctness.
