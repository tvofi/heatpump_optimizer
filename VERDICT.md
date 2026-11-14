Fix review: merge 897c777b23ca69cac35183ff1a88f1483a8ccdb1

bus-nonce: 392733a0b94b7430f3a82f186790f6a7
pending-ci: gate

## Findings

- Residual (non-blocking): the `open_pr.sh:48` mutant (the old `git worktree list --porcelain | awk '... exit'` line restored alone, `ev/mutant-m48.diff`) survives `pr_args.sh --self-test` on Linux: `262 checks, 0 failed` (`ev/st-m48-parallel.txt`). The cause is the host's awk, not the row. Here `awk` and `nawk` both resolve to mawk 1.3.4, which drains its input on `exit`. The writer therefore never takes SIGPIPE: `PIPESTATUS=0 0` against `141 0` for `head -1` on the same 260 KB producer, and the isolated old line survives under `set -Eeo pipefail` for a registered, a branch-holding and an absent worktree (`ev/probe48.txt`, `ev/probe48.sh`). So on a mawk host the old line was not defective, and the new row cannot pin it. It pins it only where awk leaves early (BSD awk on macOS, gawk). The body's macOS mutant run (`12 failed`) is plausible but I could not re-derive it here. CI's runner awk decides whether CI ever pins this line. The class lint owed under the body's Forward-carry should treat `| awk ... exit` as an early-exit reader whatever the host's awk does. Carry: R11-INTAKE-R10-RESIDUE
- Residual (non-blocking): the `pr_args.sh:448` mutant (`kind=$(printf '%s\n' "$PR_PUSHERS" | awk ... exit)` restored, `ev/mutant-m448.diff`) survives: `262 checks, 0 failed` in a serial run (`ev/st-m448-serial.txt`). The body does not claim a pin for it. It is a defensive rewrite, the same kind as round 1's unpinned `$bt`, bus re-cut, handoff_push and census rewrites. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Round 2. Reviewed head 897c777b23ca69cac35183ff1a88f1483a8ccdb1 (`ev/HEAD.txt`), which is still the branch tip at verdict time. The previous verdict was at cb803e9eed (probe/revt-r10-hotfix-carry-tip-sigpipe-a366776e, blocked class-open on open_pr.sh:125).
- Scope: the delta. The PR's own change since cb803e9eed is the one commit 7d186ed4a5, touching `open_pr.sh` and `pr_args.sh`. Commit 5c4a7a0fc6 is a main merge, and the three-dot diff at the head holds no `custom_components/` path, so nothing widens the scope. The packet printed `Review scope: full` only because the prior verdict lives on a probe ref and not on `verdict/3592`. The brief names the round.
- The prior block is resolved. `open_pr.sh:125` now reads a here-string.
  - The new row `open_pr: the same re-run with 3000 more worktrees listed after the left-over one still clears it and opens` prints `ok` at the head: `pr_args self-test: 262 checks, 0 failed` (`ev/st-head-parallel.txt`).
  - Mutant with line 125 restored: that row FAILs, `262 checks, 1 failed` in a serial run (`ev/st-m125-serial.txt`).
  - Both lines restored: the row FAILs, `1 failed` (`ev/st-mboth-parallel.txt`).
  - The neighbouring closed-after-p2 row stays `ok` in every run. It is the null control.
  - The parallel m125 run also FAILed row 211, and the parallel m448 run FAILed row 215. Neither recurs in a serial run, so both are load flakes from running five self-tests at once on this host. Neither is this PR's row.
- Class re-enumeration, done independently (`ev/class-enum.txt`).
  - The body's widened rule prints 232 lines at the head and at 7d186ed4, and 236 at 6858b4abc1, on Linux. That matches the body's figures.
  - Early-exit readers (`| head`, `| grep -q/-m/-l`, `| awk ... exit`, `| sed ... q`) in the `pr_trap` scripts (open_pr.sh, update_pr.sh), in sourced delivery_row.sh, and in pr_args.sh's production half (before its self-test at line 489) return exactly these sites:
    - `open_pr.sh:170`: grep -o over p1.log `| head -1`, a line or two in one write.
    - `update_pr.sh:69`: both upstream stages read to the end.
    - `pr_args.sh:459/462`: the upstream grep emits a few matched lines.
  - Each of these is dispositioned in the body with a reason that holds. Lines 48 and 125 are in the diff, and `pr_args.sh:448` is in the diff. No seam is open.
  - The `coverage_tree.sh:300` dismissal (executed, not sourced, sets no pipefail) holds.
- The body's macOS check counts (`260 checks`, `12/11 failed`, `353`) are host-specific. On Linux the counts are 262 checks and 0 failed at the head, so I could not re-derive them as quoted.
- `git merge-tree --write-tree origin/main 897c777b23` gives tree e22813b409, rc 0, over origin/main 4058469d79: it merges cleanly (`ev/merge-tree.txt`). The roles diff from the merge base to main is empty, so the contract is current. VERSION, the manifest, RELEASE_NOTES and tests/golden are untouched.
- The PR body's `## Head` names 897c777b23, which is the head measured here.
- CI: `merge_train.py classify 897c777b23 --pr 3592` printed `WAIT 897c777b23ca69cac35183ff1a88f1483a8ccdb1 pending: gate red: none` on every poll from 19:45:14 to 20:16:06 UTC (`ev/classify.log`). No required red has been seen, so no `## Red checks` answer is owed by this review. The packet's `introduced-red` refusal was on instrument-self-tests still `in_progress` at render, and classify decides. `tests / nightly-status` is red, but it is outside the `owed-reds` set and grades main.
- Forward-carry: unchanged since round 1 (R11-INTAKE-R10-RESIDUE, carry 151 on handoff/audit-r10-roster), which round 1 opened and confirmed.
