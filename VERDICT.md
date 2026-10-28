Fix review: merge 0303eae447bf7a12fc52ef03d66df50cb573e4f3

bus-nonce: aeedca3b22af848522ddc29294e13b15

Round: second review of #2753 (R10-THERMAL-POWER-OPTION), a re-review after round 1 (origin/review/2753, `blocked ba02b95fc carry-missing`). Measured head: `0303eae447bf7a12fc52ef03d66df50cb573e4f3` (`ev/HEAD.txt`). The role contract is current: the roles diff from the merge base to origin/main is empty (`ev/claims_version.txt`).

Head moved during the review. At 01:06:39Z, after I had measured, `github-actions[bot]` pushed `e6455b8fe617ec28d6916977778e7499a6d2fd27` ("ci: merge main"), with parents 0303eae44 and main 662a3809c. The fixer did not move it. That delta touches `tests/closures.json` and `tests/structure_budgets.json`, both in the branch's own diff, so under orchestrator.md section 11 this verdict cannot carry to the new head. I judged the resolution delta myself (Evidence, last bullet) and found it sound. The verdict still names the head I measured. The orchestrator needs to dispatch at `e6455b8fe` before it publishes there (orchestrator.md section 7).

## Findings

- none: all four round-1 items are paid and verified below; this review raises no new defect, survivor or deferral. Carry: dismissed: no finding to carry

## Evidence

- Round-1 item 1, the forward-carry, is paid and landed on main. Both carries are in the `carry` lists of their groups in `dev/programme/rosters/wave-r10-groups.json` on origin/main, by roster_edit `append-carry` commits 6a57b0a79 (R10-HEAT-METER) and 78f195461 (R10-COP-GATE), merged to main by #2771 (`0d1385e2f`). 0d1385e2f is an ancestor of origin/main and of the head (`ev/roster_carries_origin_main.txt` has the full text). Each carry states its control as a precondition, per finding-propagation.md:
  - HEAT-METER: M1's check, "a configured heat meter answers in kW, and outranks the flow meter's estimate".
  - COP-GATE: "a thermal-power-metered install is never given the not-measurable state, and its fold still moves `cop_scale`".
- Round-1 item 2, the closing contract, is paid. The live body carries `Part of #2507`. The closing-keyword regex pr-contract uses finds no closing reference in the body (`ev/body_checks.txt`); #1955 is named only in prose. pr-contract at this head passed (`ev/ci_pr_contract.txt`).
- Round-1 item 3, the (c) freeze lift booking undeclared hot-water heat as space heat, is carried, not fixed in code. The HEAT-METER carry above says that `replay_freeze` decides space against hot water only from `_commanded_split`. It requires that group's mode split to apply to the thermal power entity's reading and to this replay. The carry is landed on main, as item 1 shows. No code change was claimed, so no failing-test-first was owed.
- Round-1 item 4, the stale docstring, is paid. Commit bab39f395 rewrites the opening of `_interval_measured_heat_kw` ("#2016, #2507: the measured heat kW ... The thermal meter's reading or the flow meter's estimate"). It also names the source precedence that `read_heat_output_kw` implements. The commit changes no code line.
- RESULT harness: `dev/audit/harnesses/r10_thermal_power_option.py` (the fixer's own; the finding had no committed finder harness, as round 1 recorded), run by me at the head against the PR base `c6ef25a65` and against the body's merge base `4a00a3f05` (`ev/harness_c6ef25a.txt`, `ev/harness_4a00a3f.txt`).
  - Head `metered`: spread 0.0000, every scale within 5.2e-7 of 0.9.
  - Base `metered`: spread 0.1321 (0.6356 at -15 to 0.7677 at 12).
  - `commanded`: spread 0.1321, bitwise equal at head and base. This is the null control.
  - `first_fold`: 0.997 on the head's first step.
  - `clamp`: 1.6 at every point on both trees.
  - The head's four arms are byte-identical to round 1's run at ba02b95fc (PRIOR-MATCH), as a docstring-and-merge delta should leave them. Every figure in the body's harness bullet reproduces.
- RESULT features at the head: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/features.py` gives ALL 4374 FEATURE CHECKS PASSED, rc=0 (`ev/features_head.txt`).
- RESULT mutants M1 to M10: each is round 1's one-line patch, re-applied unchanged to a fresh detached worktree at this head with full `tests/features.py`. All 10 are killed, each with the same count as round 1 (`ev/mut_M*.txt`, which hold the diffs):
  - M1, the heat-meter branch off: 7 failing.
  - M2, the target drops `cop_scale`: 2.
  - M3, partial-load samples decay the bucket: 1.
  - M4, partial-load samples count: 1.
  - M5, a zero heat reading refused: 1.
  - M6, the freeze lifted without a reading: 1.
  - M7, the reference ignores the heat reading: 9.
  - M8, the on-change `math.inf` dropped: 2.
  - M9, the polling age limit dropped: 4.
  - M10, the flow meter as fallback: 1.
- RESULT mutation lane (CI job 121023048704, read from its log, not its conclusion; `ev/ci_mutation_lane.txt`):
  - 6 mutants over 5 files.
  - Null control `coordinator.py:511 NULL_COMMENT` survived every driver.
  - Baselines `env_drift.py`, `features.py` and `entities.py` all rc=0.
  - "PIN RE-VERIFICATION: 6 reproduced, 0 not reproduced", "0 survivor(s) of 6 evaluated", MUTATION TABLE PASSED. The pass comes from evaluated mutants, not an inconclusive run.
- CI at the measured head (`ev/ci_state.txt`): none of the 42 check runs is red. pr-contract passed at 01:07:15Z, and its range line says "every failure conclusion across them: none". So step 11 owes nothing. Still running at my last read: `gate`, and the `prelude` job of run 40144548358 ("CI edit"), which had sat in its derive step since 23:53Z. Neither had concluded, so neither is cited as green; §11 requires `gate` at the merged head anyway.
- Merge: `git merge-tree --write-tree origin/main 0303eae44` (origin/main 5c0ee1093) gives rc=0, tree 693982d28. The ledger driver printed `LEDGER-MERGE: resolved` for `tests/structure_budgets.json` and `tests/closures.json`. Neither claim file conflicts (`ev/merge_tree.txt`).
- Claims: `claims-for: 7.0.4` equals `VERSION` 7.0.4 at the head and in the merged tree. The only claim the PR adds is `config_flow` (the float-free capture, keys added). No coord_* claim was lost:
  - Every claim line at main c6ef25a is still present at the head.
  - The merged tree's coord_* claims equal origin/main's.
  - `env_drift.py --claims-only` prints "claims hygiene: origin/main ok".
  Evidence in `ev/claims_version.txt` and `ev/env_drift_claims_only.txt`. I did not re-run the full `--all` capture; per step 11 I cite CI `tests / fast (3.14)`, green at this head.
- `VERSION`, the manifest version and the RELEASE_NOTES heading are untouched (empty three-dot stat, `ev/claims_version.txt`).
- Structure: STRUCTURE RATCHET PASSED at the head (`ev/structure.txt`). Against base c6ef25a the budgets only move down: `class_excess_loc` 18209 -> 18202 and `max_class_loc` 8449 -> 8442. No budget is raised.
- Body head (step 7): the body's `## Head` names 0303eae447bf7a12fc52ef03d66df50cb573e4f3 (`ev/body_checks.txt`).
- Resolution delta to e6455b8fe (`ev/head_moved.txt`). I re-ran the cheap checks on this delta; the heavy runs at the new head are CI's.
  - `git merge-tree --write-tree` of its two parents reproduces its tree exactly (4c49a5c01), so the resolution delta is empty.
  - `tests/closures.json` differs from main 662a3809c only by the PR's own added line (`r10_thermal_power_option.py`).
  - `tests/structure_budgets.json` keeps the PR's 18202/8442 beside main's re-recorded `seam_cut_total` 420.
  - `tests/structure.py` at e6455b8fe prints STRUCTURE RATCHET PASSED (seam_cut_total 420 <= 420).
  - The claim files differ from main only by the PR's `config_flow` line.
