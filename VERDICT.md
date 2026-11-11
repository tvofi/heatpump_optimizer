Fix review: merge cd13fd1f345086d79eefe4f968f646b55a00d84d

bus-nonce: 997f41b6b6098de5f621c34c0a0b5a6e
pending-ci: gate

Round 2 of review for #3419 (R10-HOTFIX-PREPR-READSET). This is a delta re-review of `245ddf7876bf..cd13fd1f345086d79eefe4f968f646b55a00d84d`. Measured head: cd13fd1f345086d79eefe4f968f646b55a00d84d. It is still `refs/pull/3419/head` at verdict time (`ev/head-at-verdict.txt`).

## Evidence

- Round-1 block answered. Both round-1 survivors are now killed. I applied each by hand to the live files in a worktree at the head:
  - Deleting the `python3 -I tools/ci/selftest_scope.py settle` line from `.github/workflows/governance.yml` fails the self-test (rc 1, `FAIL the live job settles the index in an untraced step before its first traced one`). `static` also fails (rc 1, `UNSETTLED job`, 1 problem). See `ev/mut-ci-settle-line-deleted.txt`.
  - Replacing `return settle_index(root)` with `return 0` fails the self-test (rc 1, `FAIL the \`settle\` command settles that racy index`). See `ev/mut-cli-settle-noop.txt`.
- In-tree harness: `sh tools/ci/selftest_scope_mutants.sh --self-test` at the head ends `SELFTEST-SCOPE MUTANTS: every mutant refused`, rc 0 (`ev/mutants-harness.txt`). The body's per-mutant counts re-derive: `settle_gaps reads no job` 5 failed, `settle never rewrites the index` 10 failed, the other new mutants 1 failed each.
- Reviewer mutants on `settle_gaps`:
  - `s.gated or s.id == "launch"` → `s.gated`: killed (`ev/mut-launch-not-boundary.txt`).
  - `settle$` → `settle` (regex unanchored): killed by the `|| true` fixture (`ev/mut-regex-unanchored.txt`).
  - Dropping the `s.id in UNGATED and` conjunct: survives (`ev/mut-ungated-dropped.txt`). This is equivalent in composition. `wiring_gaps` refuses every run-step that is neither gated nor in UNGATED, and the live check and `static_check` both run `wiring_gaps` alongside `settle_gaps`. So a step before `first` with a run line is already in UNGATED. Listed under Findings as a dismissed residual.
- Self-test at the head, untraced with strace on PATH: `117 checks, 0 failed` (`ev/selftest-head.txt`). `static`: `111 gated step(s), 0 problem(s)` (`ev/static-head.txt`). Both match the body.
- Re-recorded table (main-red repair). The step-by-step file deltas are in `ev/steps-changed.txt` and match the body's account. prepr drops `.gitattributes`, `tests/env_drift.py` and `tools/merge/ledger_merge.py`, and adds the disclosed `required-contexts.json`, which agrees with my round-1 head records.
- Independent re-record of three of the 20 steps:
  - Steps: `verdict-bus`, `handover-prompt` and `field-coverage`.
  - Tree: a fresh worktree of the head merged with current origin/main dbd1ab5b07, which is 66 commits past the body's d08ed31049 (`ev/merged.txt`).
  - Record: `0 failed [], 0 broken trace(s)` (`ev/rec-merged.log`).
  - Comparison against the committed entries (files, dirs, probes): identical for all three, with no extra and no unread entry (`ev/rec-compare.txt`).
- Not re-derived: the body's full-replay refusal counts (12, 34, 3, 0). Its driver is a scratch script that is not in the tree, and the full replay is CI's heavy run. I re-took a 3-step sample instead.
- Merge with main: `git merge-tree --write-tree origin/main cd13fd1f345086d79eefe4f968f646b55a00d84d` rc 0, clean at dbd1ab5b07 (`ev/merge-tree.txt`).
- Role-file currency: main's `fix-review.md` diff since the merge base only rewords steps 7 and 11 (the owed-reds set). I applied main's wording.
- CI: `merge_train.py classify` has printed `WAIT … pending: gate red: none` from 04:01 to 04:38 UTC (`ev/classify.log`), so `pending-ci: gate` is set above. No red at this head, so `## Red checks: none` stands for now. The relay re-checks it.
- The body's head is cd13fd1f345086d79eefe4f968f646b55a00d84d, the head measured. `VERSION`, the manifest and the notes heading are not in the diff (three-dot diff empty for those paths).
- Forward-carry: both body items carry `dismissed:` markers, and the packet's carry_audit routes them (2 routed).

## Findings

- Residual: the `s.id in UNGATED` conjunct in `settle_gaps` survives deletion. It is equivalent, because `wiring_gaps` (run beside it in both callers) refuses any untraced run-step outside UNGATED. Carry: dismissed: equivalent mutant under wiring_gaps in every caller, no behaviour to pin
