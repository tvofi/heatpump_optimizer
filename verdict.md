Fix review: merge 197f7e344b585b96ed04af8c9d494ee130e97765

bus-nonce: 0fdf8147eb456200d040018bde36984c

## Scope

First round, full review of the three-dot diff f269ecccb5...197f7e344b (27 files). Reviewed from a detached worktree at the head; the head read back from `refs/pull/3846/head` before writing this verdict is unchanged.

## Evidence

- CI: `merge_train.py classify 197f7e344b585b96ed04af8c9d494ee130e97765 --pr 3846` from a clean worktree at the head: `GREEN 197f7e344b585b96ed04af8c9d494ee130e97765 pending: none red: none`, rc 0 (ev/classify-clean.txt). The earlier poll's GREEN at 07:09Z (ev/classify-log.txt) ran while one of my mutants was applied to that worktree, so I re-took it clean and cite only the clean run.
- Owed reds: none. The packet's check digest shows no red, and the classify result above agrees (ev/owed-reds.txt holds the set).
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 with one tree (ev/merge-tree.txt).
- `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden/` and both claim files are untouched in the three-dot diff. No fixture moved, so `env_drift` has nothing to compare.
- Self-tests and figures re-derived at the head (ev/selftests-head.txt):
  - merge_train: 843 checks, 0 failed.
  - review_packet: 131 checks, 0 failed.
  - ci_rerun: 16 checks, 0 failed.
  - ci_supersede: 6 checks, 0 failed.
  - selftest_wiring: 153/153 wired, 0 index gaps.
  - rules_sync: ok.
  - selftest_scope static: 127 gated, 0 problems.
  - structure ratchet: passed.
  - tmp_paths: 0 refused.
  - policy_lint `--budgets`: `.claude/rules/defect-root-cause.md` is 151/151 lines and 1885/1885 tokens, no cap raised.
- bus self-test at the head on this host: `240 checks, 0 failed` (ev/bus-selftest-head.txt). The body reports 28 host failures on its own host; there are none here, and the REPAIR-OWED arm the diff touches passes.
- Finder's harness (the body's: `merge_train.py introduced <head>` over live PR heads). The packet names none committed; I re-ran it myself.
  - Base side: from a checkout of origin/main 40e513eea4, which is newer than the body's 6fdc15354f.
  - Head side: from a worktree at this head.
  - Both runs cover #3824 (f93aa6456b) and #3822 (45a7397ecf).
  - Both trees read `introduced: 6`. The base tree read a base job (137032369357); the head tree read `scope leaves 84 step(s) out` and no base job.
  - `diff` of the INTRODUCED names is empty (ev/harness-base.txt, ev/harness-head.txt).
  - I did not re-run the other eleven heads.
- Mutation, targeted mutants of my own (ev/mutant-driver.py, ev/mutants.txt). Each was applied in place and run against the merge_train, review_packet and ci_rerun self-tests.
  - Killed:
    - B: ungated steps counted as unreached.
    - C: the push-only step no longer subtracted.
    - D: a two-dot diff.
    - F: an unreadable diff read as an empty set.
    - G: a FULL selection read as scoped.
    - J: review_packet ignores the scope.
    - K: the timeout is never added.
    - L: the ci_rerun cap is off by one.
  - Equivalent:
    - E: a missing merge base giving `set()` instead of `None`. Both count every red; only the how-text differs.
    - H: the workflow and table read from the base tree instead of the head's. Both files are in `selftest_scope.GATE_FILES`, so any difference between the two trees forces FULL, which reads `None` either way.
  - Not applied: I, because the target text occurs twice in review_packet.py. J covers that wiring.
  - Survivor A: see Findings.
- Class: the claim is one rule, `selftest_scope.select` reached through `selftest_unreached`, with both callers (`Train.introduced` and `review_packet.introduced_reading`) routed through it. The deleted base reader `_selftest_runs` has no remaining caller. I found no third reader of the base job.
- Policy: `CLAUDE.md` rule 1 and `defect-root-cause.md` change. Per the body, they merge on the owner's approving review at this head (the code-owner rule). That review is not this seat's, and it does not block this verdict.

## Findings

- Survivor A: in `merge_train.introduced_at`, deleting `hung and` from the timeout guard (`not (hung and hung <= set(unreached or ()))`) survives every self-test. With the deletion, a `timed_out` job with no cancelled step and a read scope would drop JOB_TIMED_OUT. I did not block on it: the module's own model (merge_train.py:776) says a job that times out always cancels its running step, so the entry state is not one GitHub produces, and the guard is a defensive fail-closed line. Carry: dismissed: the entry state is not one GitHub produces (merge_train.py:776), so the guard is defensive and not a reachable gap

## Notes

- Note: self-audit: `carry_audit.py check` on this verdict printed rc 0 and `0 finding item(s)`. A control comment holding an unrouted `## Findings` bullet also printed 0 items, so the audit's rc 0 does not show that this verdict's one Carry was read (ev/carry-audit.txt). Carry: dismissed: evidence, not a finding
