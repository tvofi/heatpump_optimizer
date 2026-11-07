# Proposal triage, session s12, batch 129 (P400)

The rolling batch after batch 128. Facts were read at origin/main `355d9965a` and on the seat's host at 2026-11-07 03:56Z (`date -u`). The temp directory and process table are host-local, so another seat re-runs these commands only on that host.

## P400: s12-ci-predict-tree-leak, ci_predict.py temp trees left under TMPDIR

Verdict: REJECT. The proposed fix is already in the tree, and the remaining gap is too small to pay for itself. `tools/pr/ci_predict.py` already removes its tree in a `try`/`finally`. A tree survives only when the process is killed by a signal, and SIGKILL can never be cleaned up. The leak found is two trees in about three days, roughly 0.55 GB, and it moves none of the four measures the bar counts.

Source: the orchestrator's queue line `s12-ci-predict-tree-leak`, 2026-11-07 (last line of the s7 triage queue).

Instances:
- **The cleanup exists:** `git show origin/main:tools/pr/ci_predict.py`, lines 601 to 624. Line 601 makes `tmp = Path(tempfile.mkdtemp(prefix="hpo-ci-predict-tree-"))`, line 603 opens `try:`, and lines 623 and 624 run `finally: shutil.rmtree(tmp, ignore_errors=True)`. The other two mkdtemp sites follow the same pattern: `hpo-ci-predict-graders-` (lines 1337 and 1359-1360) and `hpo-ci-predict-plant-` (lines 1632 and 1688-1689). Every other temp dir in the file is a `TemporaryDirectory()` context.
  - So the proposed "cleanup on exit (try/finally)" is already in place. The only gap left is a signal handler. Python's default SIGTERM and SIGHUP handling skips `finally`, and SIGKILL cannot be handled at all.
- **The trees now:** `ls -d $TMPDIR/hpo-ci-predict-*` shows one tree, `hpo-ci-predict-tree-2hykmqqn`, and `du -sh` gives 603M.
  - It is not a leak. `lsof +D` shows it held by node pids 38030 and 45256. `ps` shows 38030 is `policy_lint_envmatrix.mjs`, a child of pid 37457, which is `ci_predict.py --record-self-tests` under a live `prepr.sh`, 14 min elapsed.
  - That is the queue line's "one live, growing" tree. It is a normal run in progress.
- **The leaked trees:** the queue line counts two trees from 11-04 that no pid held, and says they were already removed. They were gone when this seat looked, so their size (the queue line's 1.0 GB less the live tree, about 0.55 GB) and their cause are the queue line's figures, not re-measured.
  - No log records what killed their runs, so it is unknown whether a SIGTERM handler would have saved either one.
- **Disk:** `df -h /System/Volumes/Data` gives 15 GiB free of 228 GiB. Both leaked trees together are about 3.7 % of that free space, and about 18 % of the 3 GiB margin above the queue line's 12 GiB worktree_gc trigger. That rate is one hand `rm` every few days.

Cost:
- A SIGTERM/SIGHUP handler in `ci_predict.py` that turns the signal into `SystemExit`, so the `finally` blocks run. It also needs a self-test that signals a run partway through and checks no `hpo-ci-predict-*` tree is left. That is about 15 lines of code and about 30 lines of test, with one fix seat and its review.
- `tools/pr/ci_predict.py` is a hot file: `git log --since=2026-10-24 --oneline origin/main -- tools/pr/ci_predict.py | wc -l` gives 30 commits. It is 1693 lines, it is not code-owned (no CODEOWNERS row), and it has no `tests/structure_budgets.json` row.
  - Also, a handler installed by a library function changes how every caller of `prepr.sh` handles signals.
- Benefit: a one-line `rm` every few days. This adds no CI time, completion time, right-first-time or tokens, which are the measures the 2026-11-05 bar counts. A disk-only gain from about 0.18 GB a day is at best a marginal trade.

Binding:
- The binding cost is a fix seat, a review and a change to a hot file, spent to save a one-line `rm` every few days. The proposed form already exists, and the residue cannot be fully closed because SIGKILL cannot be caught.
- What would reopen it: either of these, each measured and with its command.
  - A leaked `hpo-ci-predict-*` tree that pushed free disk below the worktree_gc trigger and cost seat time.
  - A leak rate above one tree per day.
  Either would also have to show that the killing signal was one a handler can catch (SIGTERM or SIGHUP, not SIGKILL).
- No carry. Until then, an unheld tree, meaning one that `lsof +D` shows no process holding, is removed by hand.
