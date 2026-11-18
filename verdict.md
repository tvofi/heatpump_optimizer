Design review: revise 9fe9f13b63f8e17f7fd7bee37befe9e90d004ebf class-open

Reviewed design/R11-SEAM-cycle-solve at 9fe9f13b63f8e17f7fd7bee37befe9e90d004ebf (round 1) from a detached worktree. Code read at the note's base origin/main bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f. Plan read at plan/r11 819aa2e354b4e5baaf824b8568fd72bea8168a75 (PLAN.md S14/T14 and the owed-design row, SCENARIOS.md, JUDGE.json, ISSUES.json). Roster row read on handoff/audit-r10-roster (size L, no after edge, 8 findings).

Revise point:
1. class-open. design.md:133 and :74 (section E). debugger.py:325 `_solver_smoke` calls `coordinator.async_simulate({}, limited=False)`. That is a third background what-if (the debug collection's finalize self-test, debugger.py:585), and the section 5 grep misses it because it reads only coordinator.py and services.py. Fix: widen the grep to `custom_components/heatpump_optimizer/*.py`, and dispose the site in E. Either it asks `admit_background`, or it is exempt with a stated reason (for example: one solve per finalize, and the self-test must answer rather than be denied). Add the matching test line in section 6. Also re-derive design.md:124: that grep returns 18 lines at bc658f9, not 22.

Checked with no point raised:
- Seam. The cycle owns when a solve runs. solve_gate.py is a per-coordinator side table, which is the discipline whatif.py, boost.py and price_tiles.py already follow. It moves `_optimization_running` and `_optimization_rerun_requested` (coordinator.py:3757-3759, 6362-6527) into one guard together with the new fields. That is one owner per concern, so it is not a score-only move. There is no new write path into state another module owns.
- Shape. Each section from A to H names its finding. The strings.json and release-note text follow C.
- Evidence plan. The harnesses are the finders' (m4_race.py, f01_run_optimization.py, h_*.py, peer_wait.py, m1_stop_midsolve.py). The null controls move under the named perturbations. No golden moves, and both claim files stay byte-identical.
- Sibling designs. Of the coordinator-touching designs in flight, design/R11-SEAM-money, R11-SEAM-plant-model, R11-SEAM-comments-production and R11-ARCH-OBJECTIVE claim no part of the guard, the what-if path, the worker arms or the run-now path.
- Cost. One new module plus coordinator, services, whatif, button and strings, with tests, fits L. No split.

Rulings on the designer's open points:
1. D1-s1-01 is not read-0 at main. On this seat, m1_stop_midsolve.py --arm stop_midsolve read 1 and --arm stop_idle read 0 at 8f39313a44, whose worker path (coordinator.py) is identical to bc658f9's. So the 2026-11-18 precedent (not reproduced at main, pinned) does not apply. H stays a fix, and the fixer still re-takes the harness at both ends. If the fixer's own base read is 0, H's D1-s1-01 parts (`_WORKER_STOPPING`, the restored-notice delete) become regression pins and nothing more.
2. D9-s1-02 (weakened). The stacking reproduced at main and only the B1 breach did not, so the budget is the count E designs. It is not a pin-only case.
3. The D14 probes are absent from plan/r11 and the register. The greps in section 5 stand in for them. This group owes no probe.
4. Item button-1641. C may make the press await the refresh. #1641's reason was that an awaiting press held the PARALLEL_UPDATES slot, and 6c1834977a set PARALLEL_UPDATES to 0. Keep it at 0, pin that a reset pressed during an awaiting optimize-now press is not queued, and update off_the_action's docstring. Report back only if a test shows that cancelling the press cancels the cycle mid-actuation.
5. D9-s1-03 to at most 6 jobs instead of the finder's 3 is accepted: newest-supersedes answers the last draft fresh (T14). The fixer's after-end reads the design's figure.
6. Item fallback-flap: the dismissal is accepted.

Seat token count: not reported by this harness.
