Fix review: blocked de28f656ba17e2e381471d8d3a50dffdf2840cfc root-cause-unanswered: mutation went red, unanswered

bus-nonce: 9554be76dc935f8f96bf6f839c36ca2c

Measured the code head `4f2ac0cac5cfb97bee9fa34df590e20e32f658e3` and the final head
`de28f656ba17e2e381471d8d3a50dffdf2840cfc`; the only delta is `dev/programme/delivery/2527.md`.
All RESULT lines and logs are in the evidence directory (`RESULTS.txt`).

## Confirmed

- **Finder's harness, both ends** (`sha1 5b77f874…` at each): baseline `freq_map_clean_folds=8`,
  `freq_map_defrost_folds=8`; head `8` / `0`. `--perturb` reads `8 -> 0 -> 0` at the head exactly as
  disclosed — but deleting `or defrosting` from the fold guard moves the defrost arm `0 -> 8` (`clean`
  stays 8), so the finding is still measurable and the perturbation is only vacuous as written.
- **The two arm64 reds**: baseline `4e5801eb` optimality `1 of 84`, same check
  (`one|summer_negative|shoulder: a recorded claim still has a gap`, gap 0.0000%); baseline stress
  reproduces `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`. Neither is this diff's.
- **Structure rows**: `class_excess_loc 18301 -> 18299`, `max_class_loc 8543 -> 8541`,
  `seam_cut_total 719 -> 718`, all down, reason in `0be6047ca`. Reverting the two named payments while
  keeping the defrost fix reads `18306 / 8548 / 719`, so the movement is earned.
- **Unpinned sites**: all three kill under the lane's own mutations (`GUARD_OFF` = `if False:`,
  `RETURN_DEL` = `pass`). `coordinator.py:10555` -> `persistent divergence stands control down to observe
  and latches`; `freq_control.py:78` -> both defrost checks. `coordinator.py:10679` also kills, but by
  `a number install publishes source=number beside its unchanged keys` and `a frequency sensor alone
  observes…` — **not** the check the body names, and the body's "with it off the unconfigured view gains
  `source: None`" describes `GUARD_ON`, not `GUARD_OFF`.
- **P2 `defrost_standoff`**: driven with the matcher extracted verbatim from `tests/entities.py`:
  direct-if/bool/not/walrus all hit; a copy to a local (`d = signals.defrosting; if d:`) hits **0**.
  The gap is real, the body's quoted "decided only by its owner" over-states it, and the gap **is**
  carried as a precondition in `R10-ARCH-SHAPES` on `handoff/audit-r10-roster` (`aaf70eb2d`).
- `ALL 2360 ENTITY CHECKS PASSED`; `env_drift --all` `NO UNCLAIMED DRIFT` (56 scenarios);
  `carry_audit pr 2527` 1 routed / 0 unrouted; `figure_lint` 8 resolved / 0 refused; `merge-tree` rc=0;
  `VERSION`, the manifest and both claim files unchanged; features green in a real worktree (the one
  failure in my no-`.git` copies is `recorded_at = 'unknown'`, environmental).
- **Forward-carry**: `pump_offline` is stated plainly as measured, carried and **not** closed
  (`Carry: #2238`), and lands in `R10-ARCH-SHAPES`' carry list with its control.

## Blocked

- `mutation`, a **required** check, is `failure` at the final head: `MUTATION TABLE REFUSED -- … 5 of
  them added by this diff`. The body says "No check is expected to be red in CI at this head" and never
  names `mutation` under `## Red checks`, so the root-cause trigger is unanswered for it (the cheaper
  detector is `tools/pr/ci_predict.py --base origin/main`; standing cost about a minute).
- `nightly-status` is red but grades `main`; this diff touches none of what it reads.

## Could not establish

- The body's `9 of 110` baseline stress count: my run of the same export reads `8 of 110` (seven
  `origin/main does not resolve`, one shoulder); I did not reproduce the memory-record failure. The
  load-bearing shoulder check and its numbers do reproduce.
- The head's `1 of 113` stress figure (I measured the baseline export, not a `.git` head run).
- `mutation-pins (1)` and `fast (3.14)` were still running when this was prepared. If `mutation-autofix`
  pushes its pin commit the head moves, and the verdict becomes
  `blocked <de28f656b> head-moved: measured de28f656b, head is <bot head>` rather than the class above.
