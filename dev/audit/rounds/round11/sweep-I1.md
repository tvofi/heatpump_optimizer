# Round 11 class sweep: I1

Class I1 (instrument): *a mutation kill miscounted, or a guard whose deletion
leaves the gate green.* Status in `dev/audit/config/bugclasses.json`: open,
with instances in rounds 1-10. The seven round-11 findings are D10-s1-05,
D11-s1-03, D11-s1-04, D11-s3-03, D11-s3-04, D9-s3-01 and D9-s3-02.

## Enumerator (D14 step 3)

`python3 dev/audit/rounds/round11/D14/sweep-I1/enumerate_i1.py` scans every
`.github/workflows/*.yml` step and `.claude/settings.json`, and lists the seams
in four families:

- **ST**: a CI step runs `<script> --self-test` and passes on the exit status
  alone, with no tally grep in the step.
- **CHECK**: a `--check` drift gate.
- **HOOK**: a wired hook that `policy_lint.mjs --hooks` judges.
- **JUDGED**: the five finding sites that a workflow scan cannot derive.

The dynamic arm (`probes.out`) runs two probes. `probe_empty_selftest.sh`
empties a script: it inserts an exit 0 after the shebang or the last
`from __future__` line, then runs `--self-test` under the CI step shell.
`probe_hook.sh` inserts `exit 0` as line 2 of a hook, then runs
`policy_lint --hooks`. Exit 1 means the gate stays green, so the seam is an
instance. Both probes restore the file, and they refuse a path that is absent.

- **Positive control:** the enumerator finds D11-s3-03 again (all 4 hooks:
  instance) and D11-s1-03 (`rules_sync.mjs`: instance). D11-s3-04, D11-s1-04,
  D10-s1-05, D9-s3-01 and D9-s3-02 are listed only by inclusion, because their
  seams (a line-level self-test blind spot, a mutant driver's copied tree, and
  coverage of test scenarios and per-cycle cost) are not workflow-derivable.
  This is a stated limit of the detector.
- **Null control:** `--fixture null` (a step that greps the tally) gives
  `instances=0`.
- **Perturbation:** `--fixture perturb` removes that one grep line and gives
  `instances=1`.

## Dispositions (D14 step 4)

168 seams: 68 instance, 93 guarded, 7 not applicable.

- **Guarded (93):** each is an ST step whose run greps the self-test's tally,
  so an emptied script prints no tally and the step goes red. This is static
  evidence and was not probed.
- **Not applicable (7):** every one is a workflow path absent from the tree,
  where the step falls back to a `dev/` copy or skips: the 4 seat scripts
  (`tools/audit/push.sh`, `app_push.sh`, `app_approve.sh`, `app_comment.sh`),
  `tools/audit/record-predicate/sweep.mjs`, and
  `tools/audit/round6/D11/fix/codeowners_gap.py` (one ST seam and one CHECK
  seam).
- **Instances judged (10):** `rules_sync.mjs` (D11-s1-03), the 4 hooks
  (D11-s3-03), `tests/config_flow_steps.py` (D10-s1-05),
  `claim_merge_mutants.py` (D11-s1-04), `prepr.sh` (D11-s3-04), the memory
  pass (D9-s3-01) and the stress gate (D9-s3-02).
- **Instances beyond the findings (58):** each probe exits 1, because the step
  stays green with the script emptied:

- CHECK `tools/audit/machinery_ratchet.py` Refuse a window of merges past the machinery caps --check
- ST `tools/policy/fragments_sync.mjs` fragment-check
- ST `tools/audit/seat/probe_bridge.py` probe-bridge
- ST `tools/audit/seat/plan_public.py` plan-public
- ST `tools/audit/seat/outside_intake.py` outside-intake
- ST `tools/audit/seat/bottleneck_check.py` bottleneck-alert
- ST `tools/audit/seat/scorecard.py` scorecard
- ST `tools/audit/seat/toolchain.py` toolchain
- ST `tools/audit/seat/round_metrics.py` round-metrics
- ST `tools/audit/seat/plant_recall.py` plant-recall
- ST `tools/audit/seat/finder_overlap.py` finder-overlap
- ST `tools/audit/seat/loop_ledger.py` loop-ledger
- ST `tools/policy/field_coverage.mjs` field-coverage
- ST `tools/site/day_chart.mjs` day-chart
- ST `tools/pr/merge_main_bot.py` merge-main-bot
- ST `tools/pr/cancel_superseded.py` superseded-run-canceller
- ST `tools/pr/dependabot_merge.py` dependabot-merge-decision
- ST `tools/pr/depgraph.py` dependency-graph-census
- ST `tools/audit/seat/bus.sh` verdict-bus
- ST `tools/audit/machinery_ratchet.py` machinery-ratchet
- ST `tools/audit/seat/tmp_paths.py` temp-or-machine-path
- CHECK `tools/audit/seat/tmp_paths.py` temp-or-machine-path --check
- ST `tools/audit/seat/bare_array.py` bare-array-expansion
- ST `tools/audit/seat/shell_hazard.py` bare-array-expansion
- CHECK `tools/audit/seat/bare_array.py` bare-array-expansion --check
- ST `tools/audit/seat/ref_privacy.py` push-names-the-host
- CHECK `tools/audit/seat/ref_privacy.py` push-names-the-host --check
- ST `tools/audit/seat/selftest_wiring.py` selftest-wiring
- CHECK `tools/audit/seat/selftest_wiring.py` selftest-wiring --check
- ST `tools/audit/regret_oracle.py` regret-oracle
- ST `tools/audit/archscore/gate.py` self-tests-outside-seat
- ST `tools/audit/check_scopes.py` self-tests-outside-seat
- ST `tools/audit/enumerate.py` self-tests-outside-seat
- ST `tools/audit/product_reads.py` self-tests-outside-seat
- ST `tools/audit/text_ledger.py` self-tests-outside-seat
- ST `tools/audit/merge_throughput.py` self-tests-outside-seat
- ST `tools/audit/worktree_gc.sh` self-tests-outside-seat
- ST `tools/coverage/partition.py` self-tests-outside-seat
- ST `tools/merge/ledger_merge.py` self-tests-outside-seat
- ST `tools/plan/replan.py` self-tests-outside-seat
- ST `tools/plan/size_durations.py` self-tests-outside-seat
- ST `tools/policy/policy_lint.mjs` self-tests-outside-seat
- ST `tools/policy/record-predicate/row_files_replay.py` self-tests-outside-seat
- ST `tools/pr/approve_held_runs.sh` self-tests-outside-seat
- ST `tools/pr/gate_priority.py` self-tests-outside-seat
- ST `tools/pr/head_note.py` self-tests-outside-seat
- ST `tools/release/stamp.py` self-tests-outside-seat
- ST `tools/policy/agreement_py.py` self-tests-outside-seat
- ST `tools/policy/role_pack.py` self-tests-outside-seat
- ST `tests/throwaway_git.py` throwaway-git-helper
- CHECK `tests/throwaway_git.py` throwaway-git-helper --check
- ST `tools/audit/seat/train.sh` train-launcher
- ST `tools/policy/figure_lint.mjs` figure-check
- ST `tools/policy/figure_census.mjs` figure-census
- ST `tools/policy/agreement.mjs` Show the agreement lane refusing each shape it exists to refuse
- ST `tools/audit/fold_ledger.py` Check the bug-class register against the rounds in the tree
- ST `tools/policy/friction_issues.mjs` filer_selftest
- ST `tests/ci_ratchet.py` Self-test the window fetch and parse

## Proposed barrier (D14 step 4)

One seam carries the 52 RC-only ST instances and the 6 CHECK instances beyond
the findings: `tools/ci/selftest_step.sh`. The barrier is that each step
requires a non-zero `N passed` / `RESULT` tally line from its self-test, so an
emptied or `exit 0`-shortcut script fails. It costs about 0 gate seconds, as a
grep on output already produced. For the hooks, `policy_lint --hooks` would run
each hook's `--self-test` and require its tally. This is an instrument change,
so it is a round-end proposal (tooling freeze), not built here.
`barriered: false`.
