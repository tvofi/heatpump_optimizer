Fix review: merge 9b24795b242862ac8ea4f5f9f1c798cf087fbde7

bus-nonce: 3f6fed0339cdd6b5624e57c8bd491aee

Cloud reviewer seat, **round 4** of review for R10-COP-PARTLOAD. Rounds 1-3 blocked `ea4630ace`, `a7411d7ad` and `8ecde5f26`, and round 3 blocked again at this head on the body alone. Under `fixer.md` the fourth round owes a re-cut. The body now opens `## Re-cut` and describes one tree. The code head is unchanged since round 3: every commit on the branch after `8ecde5f26` that is not on main is a merge (0 non-merge commits). Head measured: `9b24795b242862ac8ea4f5f9f1c798cf087fbde7`. It was still `refs/pull/2872/head` when this verdict was written. This review did not re-open the design earlier rounds accepted, and nothing at this head is defective.

## Findings

- Carry 1 (body `## Forward-carry`): the inverse conversions still use `heat / cop`. These are `dhw_planner._plan_dhw_min_cost`, `_clamp_dhw_to_capacity`, `optimizer._compute_baseline_power` and `coordinator._dhw_setpoint_sweep`. With a non-zero derate they understate the power needed by up to the derate. They are exact at the default 0, which is the stated control precondition. The note is present in `dev/programme/rosters/wave-r10-groups.json` at origin/main, in this group's `carry` list. That entry is the group's own row, so the next owner of the inverse conversions still has to read it from there. Carry: R10-COP-PARTLOAD
- Carry 2 (body `## Forward-carry`): D2's brief, item 2, does not list compressor power among the inputs its COP step sweeps. The countermeasure is one sentence in `dev/governance/dimensions/D2.md`. That file is policy, so the owner approves the change, and this PR does not edit it. The note is present in the same roster `carry` list at origin/main. Carry: R10-COP-PARTLOAD

## Evidence

- RESULT head: `ev/HEAD.txt` = 9b24795b242862ac8ea4f5f9f1c798cf087fbde7. `git ls-remote origin refs/pull/2872/head` returned the same SHA after every measurement.
- RESULT roles: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` touches only `proposal-triage.md`. fix-review.md was read from origin/main.
- RESULT `## Head`:
  - `git rev-parse 3dbefe25f^{tree} cfe368316^{tree}` printed `f305e001415b...` twice.
  - `git diff --quiet 3dbefe25f cfe368316` exited 0.
  - `git diff --name-only cfe368316 9b24795b2 -- custom_components tests` printed 0 lines; over the whole tree it prints 18.
  - `git rev-list --no-merges 8ecde5f26..9b24795b2 ^origin/main` printed 0 commits.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main `ce5940c0d` (now newer than the PR's base `279578074`), tree `91f0f6a04` (`ev/merge-tree.txt`).
- RESULT `VERSION`, `RELEASE_NOTES.md` and `manifest.json` are untouched three-dot (`ev/version-diff.txt`, empty).
- RESULT claims: the three-dot `claimed_drift.txt` diff adds one line, `config_flow`, and nothing else; the card claim file is unchanged (`ev/claims-diff.txt`). `env_drift.py --all 279578074` read: `CLAIMED config_flow: 2 leaves moved`, `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`, rc 0 (`ev/env_drift.txt`).
- RESULT `## Round 3 delta`, failing first: at `5534a0ac9` `tests/features.py` read `2 of 4553 FEATURE CHECKS FAILED`, rc 1 (`ev/features-ff.txt`). The two failures are the reachability probe `[cop_partload_derate]` and the new pre-fill band check, as the body says. M3's restored lines are byte-identical to `5534a0ac9`'s `_prefill_errors` (`config_flow.py:2122-2123` there).
- RESULT mutants, each applied in its own detached worktree at the head by an exact single-hit replacement, one file changed (`ev/m3.diff`, `ev/m4.diff`, `ev/m5.diff`), run with `/opt/hpo/venv-ci` (Python 3.14.7):
  - M3, the fix deleted: `1 of 4593 FEATURE CHECKS FAILED`. The failing check is the pre-fill band check, `[max 5->2: {}]` (`ev/features-m3.txt`).
  - M4, `_partload_errors` dropped from the predicate: `1 of 4593 FEATURE CHECKS FAILED`, the same check, `[max 5->2: {}]` (`ev/features-m4.txt`).
  - M5, the guard written `if False:`: `tests/config_flow_steps.py` read `1 of 534 checks FAILED`, `a maximum power below the stored minimum is refused [errors=None ...]` (`ev/cfs-m5.txt`).
  - All three are killed, with the counts and names the body gives.
- RESULT null control, the unmutated head: `ALL 4593 FEATURE CHECKS PASSED` rc 0 and `ALL 534 checks PASSED` rc 0 (`ev/features-head.txt`, `ev/cfs-head.txt`).
- RESULT `## Band writers`: rules A, B and C, re-run verbatim at the head, return 22, 11 and 14 lines, and 24, 11 and 14 at `a7411d7ad`, matching the body (`ev/ruleA-*.txt`, `ev/ruleB-*.txt`, `ev/ruleC-*.txt`). Every line A and B return is one the body places. Every sink C returns has a table row. `config_flow.py:3120` is the `unique_id` write inside `_save`, covered by the `_save` row at `:3121`. Dispositions spot-checked:
  - `SERVICE_SCHEMA_SET_THERMAL_PARAMS` has 31 `vol.Optional` keys, none of them a band or derate key, and no `extra=` override.
  - `apply_schedule` builds `updates` from a fixed six-key tuple plus the windows (`services.py:939-964`).
  - `_save` and `_save_or_menu` write the page's `user_input` merged into the options.
  - The head's `_prefill_errors` (`config_flow.py:2175-2179`) runs `_power_errors or _partload_errors` on either band key.
  - No writer is open.
- RESULT harness: the finder named no harness (review packet: "none named"). Round 1 recorded that `dev/audit/harnesses/r10_cop_partload.py` is the fixer's own. Run at the head on this x86_64 host (`ev/harness-head.txt`, 59 s), it reproduces every line the body quotes:
  - `grid 27 plants; ratio at p_max >= 0.808, at p_min >= 0.985`
  - `central plant derate 0.112 term in tree True`
  - `spread term vs none ... min -0.0598 max +0.0293 cells cheaper 13 dearer 3`
  - `flat term vs none ... min -0.0810 max +0.1066 cells cheaper 11 dearer 1`
  - `spread d=0.0 ... heat short max 0.1093` and `spread d=0.112 ... 0.0822`
  - `failures 0`
- Not re-derived: the 32-of-32 `d=0` hash identity against origin/main `3042dcd4f`, and the `sysid_estimator_frontier.py` CPU figures (289.7 s and 287.7 s). This seat did not run the harness at main or time that script.
- RESULT ratchets and predictions at the head: `tests/structure.py` read `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). `ci_predict --base origin/main` read `no closures, fast, wave-script or instrument red predicted` (`ev/ci_predict.txt`). `archscore --diff origin/main` read `dS +0.0000 NULL` (`ev/archscore.txt`).
- RESULT CI on this head, from the check-runs API (95 runs, all completed):
  - Every run is success or skipped except `tests / nightly-status`, which is a failure.
  - The `gate` jobs and `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `tests / coverage`, `tests / typing`, `budget-raise-gate` and `arch-score` are all success.
  - `pr-contract / pr-contract` run 123672013104 started at 19:09:53 UTC, after every other run had concluded, and is success.
  - `tests / nightly-status` grades main's nightly record, and this diff does not reach what it reads. Per fix-review.md step 11 it is not this PR's. The body answers it under `## Red checks` anyway.
- Not re-run, per tvofi 2026-09-30: the full scoped gate and the mutation table. CI's runs above are cited instead.
- The review packet rendered at rc 0 with both of its refusal lists empty. `carry_audit` read `2 finding item(s): 2 routed, 0 unrouted` (`ev/review-packet.md`).
