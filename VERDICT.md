Fix review: blocked 92e3712af8e5ca935f5a404539c402b403fe7aa9 ci-red: required gate red at this head; the only failing checks are main's tests/features.py freeze, not this diff

bus-nonce: 4cccbfc3e98cc2f46f4adcd65dce9e99

Round: first (no prior verdict on #3945).

## Block

- `merge_train.py classify 92e3712af8e5ca935f5a404539c402b403fe7aa9 --pr 3945` exits 1: `RED 92e3712af8e5ca935f5a404539c402b403fe7aa9 pending: none red: gate` (ev/classify.txt). A head that is still red cannot take a `merge` verdict (C8).
- The red comes from `tests / fast (3.14, 1/4)` (job 141070987221): `3 of 2806 ENTITY CHECKS FAILED`. All three failures are the `tests/features.py` freeze checks: "tests/features.py keeps the freeze ...", "null control (span ids) ..." and "null control (seam home) ...". The log reads `tests/features.py has 104990 lines, above the 104695 tests/features_frozen_budgets.json records`.
- These failures are inherited from main. The diff touches neither `tests/features.py` nor `tests/features_frozen_budgets.json`. The same 104990 > 104695 holds at the merge base a59a1b0d9a (the #3940 merge that added the freeze) and at origin/main fa284cd457 (ev/tree_checks.txt). My local `tests/entities.py` run at the head fails exactly those three checks and no others (ev/ent_head.summary.txt).
- Re-dispatch this review, or carry it, once main's freeze manifest and `tests/features.py` agree and the gate is green at a head with this same diff. Apart from this red I found no code, test or harness defect that blocks.

## Findings

- Follow-up: the no-prices pin reads the step count only from the English message in `strings.json`. Mutant m7 changed the sv `fyra` to `tre` and the de `vier` to `drei`, and `tests/entities.py` reported only the three inherited failures, so the mutant survives (ev/m7.diff, ev/m7.summary.txt). The rain pin, by contrast, reads every shipped translation. The carried item named only "four price steps", so this does not block; the fixer can extend `_ptp_msg` to every translation if this PR gets a new head. Carry: dismissed: outside the carried item's English text; offered to the fixer with this block, no later stage depends on it

## Evidence

- Head reviewed: 92e3712af8e5ca935f5a404539c402b403fe7aa9 (ev/HEAD.txt). The PR branch is still at this head per `git ls-remote`. Its body names 92e3712 as the head and 077b3afcf5 as the authored code head.
- Merge with main: `git merge-tree --write-tree origin/main 92e3712af8` exits 0 (tree 948f3cc604), so there is no conflict.
- `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are untouched: 0 diff lines over the three-dot range.
- Mutation proof, re-run at the head, one detached worktree per mutant, `PYTHONPATH=tests/hastub`:
  - m1, the dabc6d30af narrative revert: fails "no dhw_preheat sentence claims a price ..." with all six claiming; 4 of 2806 (3 inherited + 1). Killed.
  - m3, `precipitation > 0.1` changed to `> 0.0`: fails "every rain-multiplier description states ..." and "the rain-rate check refuses a text that names other rates"; 5 of 2806 (3 + 2). Killed.
  - m5, `len(prices) < 4` changed to `< 3`: fails "the no-prices message's step count ..." with `need=4 uncut=[96, 96] runs={3: None, 4: None}`; 4 of 2806. Killed.
  - m6, the device_prefill preview changed to `_prefill_schema(...)`: `tests/config_flow_steps.py` 9 of 731 failed, including "the wizard's pre-fill page renders no after-save choice and its schema refuses one". Killed; matches the body.
  - m7 (my own; see Findings): survives.
- Unmutated head: `tests/config_flow_steps.py` ALL 731 checks PASSED. `tests/entities.py` 3 of 2806 failed, all three the inherited freeze checks.
- Note: figure-stale: the body's "ALL 2800 ENTITY CHECKS PASSED" was measured at 6a53fe2094 on base ac9045c223. At this head the count is 2806 with the 3 inherited failures. Carry: dismissed: evidence, not a finding
- Structure: `tests/structure.py` at the head prints STRUCTURE RATCHET PASSED, with class_excess_loc=17190 and module_excess_loc=21597; the merge base a59a1b0d9a gives 17191 and 21598. The only `custom_components/` line-count change is in thermal_model.py (docstring +1 line, comment -2 lines), so each down-by-one is earned by the change.
- Production delta: docstrings and one comment only, with no executable line. I checked the setpoint_check.py docstring against pump_arbiter.py's write table (space set-point column) and the presets.py docstring against `preset_from_config`'s `answers.get` reads (structure, era, foundation, heated area, upper and lower emitter). Both match.
- Finder's harness: none was named (the packet says so). The carried items are prose pins whose control is the revert; mutants m1/m3/m5/m6 are that control.
- Red checks: `tests / fast (3.14)` is in the owed-reds set, and its red is the inherited main freeze above, a cause outside this diff (#3940's manifest). `tests / nightly-status` is red too but is not in the owed-reds set.
- I did not re-run the gate or the mutation table; I cite CI.
- Carry audit: `carry_audit.py check` over this verdict exits 0 (2 routed, 0 unrouted). For the PR body I used the packet's own head run (0 items), and a stand-in file holding the body's Red checks, Forward-carry and Friction sections, because this seat has no gh to fetch the full body to a file.
