Fix review: blocked 4b91c2f9f705b76db9e041e1c88ad12bb79147f8 class-open: op_host_refusal guards 1 of the 59 self-test inputs, so a head breaking one of the other 58 is left open as the host's

bus-nonce: a10e31cf0b33e9452575cf4a118a56b5

Round 1 (handoff review, no pull request yet).

## Block

- **class-open: the predicate's unguarded domain is the whole case it fires on.** prepr.sh step 3h runs `self-test` only when `selftest_owed` holds, i.e. the branch's diff touches a self-test input (`tools/pr/prepr.sh:1762`, `:4467-4477`): prepr.sh itself, every tracked `tools|tests|.claude/workflows` script it names, `counts.mjs`/`render_md.mjs` and the fixtures directory. At this head that enumeration (`selftest_inputs`'s grep, re-run: `ev/selftest-inputs-at-head.txt`) returns 57 named scripts, 56 of them not prepr.sh, plus the two .mjs modules and the fixtures prefix. `op_host_refusal` exempts only `tools/(pr|audit)/prepr\.sh`. So every `REFUSE self-test` row a head can provoke through any other input (e.g. `tools/policy/policy_lint.mjs`, the #1811 shape `selftest_owed` exists for) is classified as the host's and the PR is left open. Measured with the head's function verbatim (`ev/probe.sh`, `ev/fn.sh`, output `ev/probe-classifier.txt`): a branch changing `tools/pr/prepr.sh` → closed; a branch changing `tools/policy/policy_lint.mjs` → **left open**. The body names no enumeration rule and dispositions none of these seams.
- **The classifier decides by message text and a path proxy, not by measurement.** Nothing in the diff runs prepr's self-test at origin/main on the refusing host; "the host's" is inferred from the REFUSE row's step name plus the diff guard above. The dispatch's acceptance condition is that a host refusal is decided by measurement at origin/main on that host (e.g. re-run `prepr.sh --self-test` in a worktree at origin/main and treat the refusal as the host's only when it also fails there, with the same FAIL rows), never by matching message text. A re-cut that measures would also close the class above without a path list.
- **Surviving reviewer mutant (mutdiffread):** changing `git diff ... origin/main...HEAD) || return 1  # an unread diff is the branch's own` to `|| return 0` (an unread diff counts as the host's) → `pr_args.sh --self-test` 211 checks, 0 failed (`ev/selftest-mutdiffread.log`). The comment's stated rule has no arm pinning it.

## Evidence

- HEAD reviewed: 4b91c2f9f705b76db9e041e1c88ad12bb79147f8 (`ev/HEAD.txt`); body `handoff-body/r10-hotfix-openpr-host-refusal` at 6b8ddac9 names that head under `## Head` (step 7: matches).
- No pull request, no review packet and no CI exist before the PR opens; no check runs were read and no red is owed an answer (no check run exists on this head, so nothing in the `merge_train.py owed-reds` set is red).
- Merge: `git merge-tree --write-tree origin/main 4b91c2f9f705b76db9e041e1c88ad12bb79147f8` rc=0, tree b4b88cf6 (`ev/merge-tree.txt`), which equals the body's `Prepr:` trailer tree; origin/main 8c10361e is the merge base, so the head is not behind.
- VERSION, manifest version, RELEASE_NOTES.md: untouched (three-dot diff empty). No golden/claim files touched, so env_drift has nothing to compare; no budget file moved.
- RESULT selftest-head: `pr_args.sh --self-test` at the head: 211 checks, 0 failed, rc=0, 4m20s (`ev/selftest-head.log`) — body's figure re-derived.
- RESULT null-control: head's pr_args.sh with origin/main's open_pr.sh: 211 checks, 3 failed (the new open arm, mut:hostother, mut:hostguard) (`ev/selftest-nullmain.log`) — body's "3 failed" re-derived.
- RESULT mutants (fixer's): mut:hostother and mut:hostguard arms pass at the head, i.e. the suite's deletion of each line is killed (`ev/selftest-head.log`).
- RESULT reviewer mutant mutrows (delete `[ "${rows:-0}" -gt 0 ] || return 1`): 3 failed — killed by the existing refused-row-push/errexit close arms (`ev/selftest-mutrows.log`).
- RESULT reviewer mutant mutdiffread: survived, 0 failed (see Block).
- Harness: the finding (#3508's close) has no committed finder's harness; the probe in `ev/` is this reviewer's, not the finder's (step 9).
- `tools/audit/prepr.sh` does not exist at the head; the guard's `audit` alternative mirrors prepr.sh's own fallback at `:4473` and is not a defect.
- Logs in `ev/` are each cut to their last 20 kB.

## Findings

none
