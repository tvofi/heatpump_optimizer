# R11-PREPR-STEP-TIMING: blocked, the group is already on main

Question: both countermeasures this dispatch carries (C3, C4 of dev/audit/rca/R10-RCA-OPEN-PREPR-SLOW.md) landed on main in PR #3908 (merge fd93aa3e9b, 2026-11-26), an ancestor of the dispatched head ac9045c223. Should the group be closed (resume.stage: done) rather than re-fixed?

Evidence, at ac9045c223 (origin/main at this run):
- `git merge-base --is-ancestor 0d8cac00c7 origin/main` (refs/heads/handoff/r11-prepr-step-timing) and `... afbc0bc485 origin/main` (this ref's previous tip) both return 0.
- C3: commit 0b3c31d80c. `step()` and `summary_end()` in tools/pr/prepr.sh carry `[Ns]` and `elapsed=${SECONDS}s`. Re-measured by extracting prepr.sh's block from `PREPR_LOG="" LOG_MARK=0 STEP_MARK=$SECONDS` up to `summary_end() {` and running `sleep 2; step slow 0 slept; step noop 0 nothing`: printed `[2s] slept` (failing case, at least 2) and `[0s] nothing` (null control, 0 or 1).
- C4: commit c232412f04. The comment over `predict_line` now reads "It costs seconds only on a diff keying none of them", and STEP REPLAY is bounded by `HPO_STEP_REPLAY_BUDGET_S` in tools/pr/ci_predict.py, with the rest left to CI by name. open_prepr_6d.sh was not re-run: the change is merged and was reviewed at its own head.

No code was written. Nothing was pushed to handoff/ or handoff-body/.
