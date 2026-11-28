# BLOCKED: R11-SEAM-wallclock-dst (fixer-r11-seam-wallclock-dst)

Question: R11-SEAM-wallclock-dst already merged on main as #3914 (merge cb2026c3b5, an ancestor of the dispatched head ac9045c223), but the roster still shows `resume.stage: not-started`. Should this dispatch be withdrawn and the roster row set to done, or is there a residual scope beyond #3914 that you want fixed?

## Evidence, measured at ac9045c223721608e684c8a2213831aa34c1fa4f

Harness: `dev/audit/harnesses/r11_wallclock_dst.py`, which #3914 landed. Each run was
`PYTHONPATH=tests/hastub:<tree>/custom_components python3 dev/audit/harnesses/r11_wallclock_dst.py <instance> --day <day>`,
with its exit code read directly (1 = disagrees with the zone's real clock, 0 = agrees).

- At the head ac9045c223, all 15 runs exit 0: the instances `hours_until_next_window`, `simulate_trajectory`, `simulate_trajectory_batch`, `simulate_trajectory_with_dhw` and `next_window_census`, each on the spring, autumn and plain days.
- Null control at 265e061f65, the first parent of #3914's merge, with `custom_components/` taken from `git archive`: `hours_until_next_window`, `simulate_trajectory` and `simulate_trajectory_batch` each exit 1 on the spring and autumn days and 0 on the plain day. This is the reproduction the brief describes. The probe does detect the defect, and the merge removed it.
- D15-s2-04 stays `unreproduced` in `dev/audit/rounds/round11/ISSUES.json` (class P7, issue 3786). Running its bundle harness `m5_zone.py` needs a diagnostics bundle, and this tree does not have one. I did not run it.

I made no code change. Nothing was pushed to `handoff/r11-seam-wallclock-dst`.

This ref's earlier tip, 1404098d53, was the previous seat's 2026-11-26 `body_push: REFUSED CARRY-LANDED` block. The relay re-ran body_push, #3914 merged, and this step ref was never deleted. I stacked this commit on top of it so the push stays fast-forward-only.
