Fix review: merge 981b31024e43a40a88552f08208809dcbbbf5512

bus-nonce: a44dfdbb6e3fb6905dddd2a8e6365291

## Evidence

Round 1 of fix review for #3372 (no earlier verdict on this head named in the dispatch). Measured at head 981b31024e43a40a88552f08208809dcbbbf5512, detached worktree; head re-read at origin before posting: unchanged. Merge base 806e952cadde68bec637a491b4646dd6fb5281d0; `git diff <mb>...origin/main -- dev/governance/roles/` empty (contract current).

- Merge with main: `git merge-tree --write-tree origin/main 981b31024e43` exit 0 (origin/main c668197a3721), no conflict, no claim-driver line.
- CI: `merge_train.py classify 981b31024e43 --pr 3372` exit 0: `GREEN 981b31024e43a40a88552f08208809dcbbbf5512 pending: none red: none` (ev/classify.txt; 17 WAIT polls before it, ev/classify-log.txt).
- Re-authoring (extra check 1): the dispatch's ee9138f1 range (057d4b39, deb339c1, c3ac6099) is not in the remote: `git cat-file -t` on each, after fetching every branch and the PR refs that name this group, says "Not a valid object name". I compared against `handoff-wip/r10-water-setpoint-lift` 8fb1858d75fc instead, the range the body measures at. Each of the five commits has a byte-identical tree to its predecessor, commit for commit: 1ec0c8ca=9fab06f0 tree 25381f4d, 753b9869=2d6b81d5 tree d8bea8ce, eaf01e72=ad3a1b4e tree 069eedf5, d49b1602=96ab870f tree 5851999f, ec2d173c=8fb1858d tree f785c4d4. All share parent ba6fd7e8. Mismatches: 0 (ev/tree-compare.txt). I could not verify the ee9138f1-to-8fb1858d step itself.
- Authorship (extra check 2): the four contributor commits on the head are authored `Bankaifan <476059+Bankaifan@users.noreply.github.com>`. At 8fb1858d the third of them (2d6b81d5) carried the assistant identity `noreply@anthropic.com`, as the body explains, and two carried the unnumbered `bankaifan@` address. The body credits the outside PR #3356 in its title and first line, keeps its fork head e9dc72be, and carries a Co-authored-by credit. A `git range-diff` of fork e9dc72be~4..e9dc72be against the adopted four shows only the dropped assistant trailers and the dropped stale `claimed_drift.txt` hunk, which is what the body says (ev/range-diff-fork.txt).
- RESULT features_head_unmutated: `ALL 5011 FEATURE CHECKS PASSED` rc=0, including `ok null control: with default options every set-point an indoor or flow unit writes, and every held FlowCommand, is main's, cell for cell`.
- RESULT null-control grid (extra check 3), re-recorded independently: I appended the head's `_nc_cells` block unchanged to origin/main c668197a's own `tests/features.py` (`ALL 4985 FEATURE CHECKS PASSED`) and dumped its cells on main's production tree. That is a newer main than the fixer's ba6fd7e8. `nc_main_rerecord_cells=2688 nc_main_rerecord_mismatches=0 identical=True` against the pinned `_NC_AT_MAIN` (ev/nc-compare.txt). The re-record harness is my own, built from the fixer's block.
- RESULT perturbed grid (null-control detector, `_return_unit` widened to `in SPACE_SETPOINT_WATER_UNITS`): `20 of 5011 FEATURE CHECKS FAILED`, null control `2688 cells, moved at [1344, 1347, 1348, 1349, 1352, 1353, ...]`. This equals the body's 20 and its first moved cell 1344.
- RESULT mutation proof, each mutant alone on the head, `PYTHONPATH=tests/hastub python3 tests/features.py`:
  - `_as_target` → `return supply_c`: 10 of 5011 failed (body: 10). The grid stays ok, as the body says.
  - `_full_draw_c` → `return ceiling_c`: 2 of 5011 failed (body: 2).
  - `_return_unit` widened: 20 of 5011 failed (body: 20).
  - My own mutant, `_heat_ceiling_c`'s gate guard dropped (`return ceiling`): 1 of 5011 failed, "D3: a stored ceiling at or below the gate reads as the default heating flow".
  - My own boundary mutant, `_full_draw_c` headroom `>=` → `>`: 2 of 5011 failed.
  - All five are killed; diffs and logs are in ev/mutant-*.
- Claims: VERSION, manifest and RELEASE_NOTES untouched (three-dot diff empty). `claimed_drift.txt` adds one `config_flow` line under `claims-for: 7.1.8`, which equals VERSION 7.1.8. `tests/golden/config_flow.json` moves 2 insertions and 2 deletions (the `space_setpoint_unit` options list in the plain and the seeded render), matching the claim. `env_drift.py --claims-only <mb>`: `claims hygiene: 806e952c... ok`. The full `env_drift --all` was cited from CI (`governance / env-matrix` success), not re-run.
- Figures: `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`, and no `*_budgets.json` is in the diff. `tools/audit/archscore/score.py --diff origin/main HEAD` gives `Architecture score: dS +0.0000 NULL`, as the body states. The 5011 check total matches. Not re-derived: `option_doc_coverage.py`'s 205/0 and `prepr.sh` rc=0; those are the fixer's figures.
- Class (step 6): every production site that reads `space_setpoint_unit` goes through `SPACE_SETPOINT_WATER_UNITS` (`pump_arbiter._flow_unit`, `thermal_model.flow_setpoint_driven`) or `_return_unit`, apart from the select's option list and `entry_config`'s validator. No production `== "flow"` comparison remains. The rule returns no unhandled seam. `configured_flow_heat_c` has a single caller (`pump_arbiter._heat_ceiling_c`), which passes `FLOW_HEAT_C` 55.0, so the changed absent-key default moves nothing, as the body says.
- Harness (step 9): no finder's harness exists. This is a feature adoption with no issue. The measurement is the fixer's own null-control grid, disclosed as theirs (commit ec2d173c), and I re-recorded it as above.
- Head SHA in body: names 981b31024e43, the head measured. Body `## Red checks: none`. The two red `gate` runs at this head (42603361927, 42604091899) logged `FAIL run(s) [42603361377] at this head are still being judged; their gate decides`. That is a deferral to the in-progress main run, not a check failure; the classifier line above is the conclusion.
- Forward-carry: the three fork proposals go to #201 (`carry-201.json`, owned by the orchestrator). carry_audit at the head reports 4 routed, 0 unrouted.

## Findings

- Follow-up: the fork's three unmeasured proposals (start-then-hold writes for a return target, measuring the 5 K full-draw headroom against a steady-state series, anchoring the modulation floor once per plan step) are not settled by this PR; the body routes them to the orchestrator. Carry: #201
- Follow-up: once this PR merges, #3356 is owed a close with thanks and its plan-page link for the outside-intake ruling; the orchestrator owns both. If R10-GENERIC-HEAT-CURVE (#3299) merges first with its own config_flow claim, the combined claim line must be restated on this branch. Carry: #201

## Friction

none
