Fix review: merge 3230ac7113e513864159360d16a6fd35828997ad

bus-nonce: 9abb01b20734a599925774bf1fa1b3a3
pending-ci: gate

Round 3, a delta review. The reviewed head was 09c0bc5ce99c4ed0b27e780d08aa6be28bf06bbd (blocked `mutant-committed`), and the head measured here is 3230ac7113e513864159360d16a6fd35828997ad (ev/HEAD.txt). Scope: delta, as the packet's `## Review scope` line gives it. `git diff 09c0bc5c 3230ac71` is one line in `tools/audit/check_scopes.py` and touches no production (custom_components/) code, so the review is not widened.

## Evidence

- (1) The refusal is restored. The delta replaces `pass` with `errs += [f"static and in the universe: {f}" for f in sorted(stat & uni)]` in `classify_errors`. `git diff ff9b385bcd^ HEAD -- tools/audit/check_scopes.py` prints nothing (0 lines, ev/restore_vs_premutant.txt), so the file is byte-identical to its text before the mutant.
- (2) At the head, `python3 -I tools/audit/check_scopes.py --self-test --repo .` prints `SELF-TEST passed (every perturbed scope refused)`, rc=0, in 63 s (ev/check_scopes_selftest_head.txt).
  - Mutation control, run in a separate detached worktree: putting ff9b385bcd's `pass` back gives `SELF-TEST FAILED` with the arm `'a static path in the universe is refused': False`, rc=1, and every other arm True (ev/mutant_selftest.txt). The worktree was restored afterwards, with 0 dirty paths.
- (3) I re-took the body's figures at the head (ev/figures_head.txt). Each one matches:
  - `text_ledger.py --self-test` prints `17 checks, 0 failed`.
  - `check-wave-script.mjs` prints `227 passed, 0 failed`, with the cadence line `off at 11: D5, D6, D11, D13`.
  - `selftest_wiring: 0 index gap(s)`.
  - `selftest_scope self-test: 120 checks, 0 failed`.
  - `check_scopes.py --repo . --ref HEAD` exits 0:
    - `ok D5 ... seats=10 universe=853`, with s1 0u, s7 3809u and s10 `312f/0loc/1704u`.
    - `ok D6 ... seats=7 universe=344`, from s6 2246u to s2 4005u.
    - `unclassified=0`.
  - The round-10 sentence counts 1 of 2250 strings.json units.
  - `git grep` over the round 9/10 D6 outputs exits 1.
  - `STRUCTURE RATCHET PASSED`.
  - The sweep's "13 files, 849+/65-" is `git diff --shortstat c987209cc7...c2508883c4`, which I reproduced. At the head the same three-dot diff is 14 files, 850+/65-, and the extra file is the 1-line delivery row `dev/programme/delivery/3571.md`, as the body's `## Head` states (ev/threedot.txt).
- (4) The fixer's account of how the mutant was committed is in the body, under `## Re-cut` "How the mutant got committed":
  - Cause: a hand mutation in the branch worktree with no `mutant_guard`, swept into ff9b385bcd.
  - Process state: (b).
  - Cheaper detector: a local self-test run, 50 s. I measured 63 s here.
  - The cost test is given, and the tree-wide countermeasure is routed to the root-cause seat with a `Carry:`. `## Red checks` answers the `gate` / `governance / instrument-self-tests` red at 09c0bc5c.
- (5) I re-ran the leftover-mutant sweep (ev/leftover_sweep.txt) over the 10 non-merge commits in `c987209cc7..HEAD`, grepping each commit's added code lines for a bare `pass` / `return` / `continue` / `break` / `exit 0` / `|| true`.
  - It returns exactly the body's list: ff9b385bcd's `pass`, which is reverted at the head, and e130ee97a4's `return None` (x2), `continue` (x3), `break`, `except ValueError: pass` and `return 1`, all new code in `text_ledger.py`.
  - Every removed code line in the three-dot diff is the import, `check`/`verdict` signatures, `status`, `sizes`, `live = verdict(...)`, the final `sys.exit` and the cadence assertion, as the body lists. No other mutant was found.
- Merge: `git merge-tree --write-tree origin/main 3230ac71` against origin/main f7e7a0244a3d5f7763c4ec15d193d03ef4bb3274 prints one tree, rc=0, with no conflict (ev/merge_tree.txt).
- The delta commits' messages carry no attribution trailer.
- CI: `merge_train.py classify 3230ac71 --pr 3571` printed `WAIT 3230ac7113e513864159360d16a6fd35828997ad pending: gate red: none` on each of 31 runs, about 60 s apart, from 04:58 to 05:28 UTC (ev/classify.log). No red has been reported, so no `## Red checks` answer is owed. The relay posts this verdict once `gate` is green at this head.
