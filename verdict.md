Fix review: merge 0e200f4995c2b708c75b5c2ba4307ef3e124a9ca

bus-nonce: 8110544170007c223912014b10cd1fc9
pending-ci: gate

## Review

This is round 2, a delta review over the blocked head cde73e8b72fc563d515fd5ab66a6a12eec85698e. The delta is one authored commit, 4df50c054e4228f6f4e2b204a40d973e7f039fde, merged at the head, and it touches only `tools/audit/seat/pr_args.sh`, `open_pr.sh` and `update_pr.sh` (ev/delta_stat.txt). It touches no production code (custom_components/), so the scope does not widen (fix-review.md step 12).

Round 1's class-open is closed. Round 1 found that `mut:opreg` compared the logical `$WT` with git's physical worktree path, and that the same logical-against-physical comparison sat in `op_clear_leftover` and `update_pr.sh` `mut:elsewhere`. `pr_state_root` now resolves the state root once with `cd -P && pwd -P`. `open_pr.sh` builds `D`/`WT` on it and `update_pr.sh` builds `P`/`WT` on it, so every site that compares against `git worktree list` uses the physical spelling. The perturbation round 1 asked for, a state dir passed through a symlink, is now a self-test arm (`dualrun - link`), and so are the trailing-slash and `/./` spellings. The update_pr.sh side has its own symlink arm.

## Evidence

- Head reviewed: 0e200f4995c2b708c75b5c2ba4307ef3e124a9ca (ev/HEAD.txt). Merge with main: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict (ev/merge_tree.txt).
- RESULT figure: `bash tools/audit/seat/open_pr.sh --self-test` at the head ends `pr_args self-test: 253 checks, 0 failed`, rc 0 (ev/selftest_head.txt). This matches the body's 253 (247 plus 6 round-2 arms).
- My own mutants, independent of the in-harness `mut:` mechanism (ev/mutant_*.diff, ev/selftest_m*.txt):
  - `mopen`: `open_pr.sh` `D` set back to `${HPO_STATE_DIR...}`. The link, slash and dot arms all FAIL: 3 failed, rc 1. Killed.
  - `mupd`: `update_pr.sh` `P` set back to the logical path. `update_pr: through a symlinked state dir ...` FAILs: 1 failed, rc 1. Killed.
  - `mlogical`: `pr_state_root` with `cd`/`pwd` in place of `cd -P`/`pwd -P`. The open_pr and update_pr symlink arms FAIL: 2 failed, rc 1. Killed. The slash and dot arms still pass under this mutant, as they should: logical `cd` already normalises those spellings, and only the symlink needs `-P`.
- The body's class enumeration was checked against the diff. `$WT` and `$P` derive only from `$PR_STATE` in both scripts. I did not re-derive the sibling-file claim (`closeout.py`, `worktree_gc.sh` resolve both sides). Those files are outside this delta, and round 1 did not name them.
- VERSION, the manifest, RELEASE_NOTES.md, the golden and claim files, the budgets and closures.json are untouched: the three-dot diff against the merge base is empty (ev/untouched.txt).
- CI: `merge_train.py classify` printed `WAIT 0e200f4995c2b708c75b5c2ba4307ef3e124a9ca pending: gate red: none` on every poll from 13:14 to 13:40 UTC (24 polls, ev/classify_poll.txt). No red has been read, so no `## Red checks` answer is owed. review_packet refused `introduced-red: unreadable` because instrument-self-tests was in progress at render time. classify decides, and it reported WAIT.

## Friction

- The Stop hook's policy_lint flagged 6 pre-existing citation errors in `tools/audit/README.md` (lines 288-296). This seat edited no file, and the working tree was clean.
- `git ls-remote` once returned a transient 502 ("session scope unavailable").
