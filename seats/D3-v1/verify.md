# Round 11 D3 verify (seat D3-v1, box V6)

One finding: D3-s2-01. Tree: D3-s2 is not a planted scope, so measured in git
worktrees. The finder's harness reads `tests/closures.json` and the cell
sources from the cwd, so the register tip (28b864af6d) and the baseline give
different numbers; the baseline is the finder's tree, and the numbers below
come from a detached worktree at 92d38ecb6 with round11/D3 copied in.
load1 0.32-0.98, thread_factor 1.00, no other seat running on this box.

## D3-s2-01: vote **weaken** (severity low; class I2, not new)

**V1 reproduce.** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s2/m5_reach.py dev/audit/rounds/round11/D3/s2/run/reach`
- baseline worktree: clean_pairs=170, over_approximated_pairs=**29**, over_seconds[payload.py]=525.7 s of 3051.3 s (9 of 27 scripts): exact match.
- register-tip worktree: 27 pairs, payload 535.5 of 3887.4 s. That tree's closures.json moved, so the claim is tied to the baseline.
- Perturbation `--claim-only tests/boost_drift_replay.py:payload.py`: 29 -> 28, payload 525.7 -> 184.6 s. The number moves in the stated direction, so the finding is not void.
- Leave-one-out on the payload aggregate: boost_drift_replay alone is 341.1 of the 525.7 s (65 %).

**Attack: the payload.py pairs are vacuous.** `ast.walk` over the baseline
`custom_components/heatpump_optimizer/payload.py` finds **0** FunctionDef or
AsyncFunctionDef nodes (1032 lines, all TypedDicts and module constants), so
`body_lines()` is empty. As a result, body_hits=0 holds for every importer by
construction, and no "function-body-only edit" of payload.py exists. Any edit
to it is module-level code that runs at import, and the finding's own
proposed_fix_scope says such edits must still select every importer.
All 9 payload pairs and the whole 525.7 s headline are therefore an artefact
of the metric. The other cells do have bodies: store 26 functions,
ledger 32, snapshots 10, inputs 68, accuracy 45.

**V2 independent** (`v2_bodyraise.py`, written by this seat). Metric: insert
`raise RuntimeError` as the first statement of every function body in a cell
(module code untouched), run each claimed-over script, and count the scripts
that still exit 0 while `closure.py select --files CELL` still selects them.
- Null control: the 6 scripts exit 0 unmutated.
- Positive control: inputs.py bodies raised. guard_pins and manual_plan, whose inputs pairs are not over, exit 1.
- Result: **20 of 20** non-payload over pairs survive the all-bodies raise and are still selected. That covers snapshots 6/6, ledger 4/4, store 2/2, accuracy 4/4 (incl. optimality, validate) and inputs 4/4 (incl. optimality, validate).
- Independent value: 20 genuinely over-approximated pairs, against the claimed 29. Over-selected recorded seconds per body-only edit are inputs 167.2 s, accuracy 166.6 s, snapshots 30.4 s, ledger 22.1 s and store 3.2 s; payload is 0 s, not 525.7 s.

**V3 reach and class.**
- Reach: this is CI gate selection, not a Home Assistant runtime path. It is reachable on every scoped branch gate. The consequence is gate seconds only: no wrong verdict is possible, because over-selection runs more scripts rather than fewer. Severity is low.
- seam_rule: it is the same harness. It enumerates only the 22 scripts that have traced reach rows, over en.CELLS. arch_score, backtest, card.mjs, card_drift.mjs, edge, golden, harness_headers, ha_contract, layout, md_tables.mjs and stress (11 scripts) are not traced, so the rule covers the demonstrated subset, not every seam.
- class: I2 ("A measured closure or scope diverges from the real dependency graph") fits; "new" is corrected to I2.

**Why weaken.** The mechanism is real (20 pairs, about 390 s of recorded
seconds across cells). The headline cell and its 525.7 s, plus 9 of the 29
pairs, rest on a cell that has no function bodies.
