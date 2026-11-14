Fix review: merge 4d5b7e94d1807b987fac5323e9129f9359d6b7a9

bus-nonce: da23881d8714203424dcd885b21cd367
pending-ci: gate

## Findings

- The detection-lag and refused-opens-per-Darwin-red measures are owed at round end, as the body says. Carry: O1
- Out of scope: the stale-worktree remove before `worktree add` still survives deletion (mutant no_stale_wt_remove, rc=0 at this head). The line is unchanged since 8a05961b and outside this delta. It carries as in round 3. Carry: O1

## Evidence

- Round 4, delta review over a55158085ed8cd6517113af8b77af07492a6634e. Head measured: 4d5b7e94d1807b987fac5323e9129f9359d6b7a9 (ev/HEAD.txt). The authored delta is the single commit 5c7b8a82, which touches only tools/audit/seat/beat_jobs_selftest.py (+27: two cases and two MUTANTS rows). The other commit is the merge of origin/main c987209c. `git diff a5515808 4d5b7e94 -- tools/audit/seat/beat_jobs.py tools/audit/seat/instruments/` is empty, so no production line of beat_jobs.py changed, as the body states. There is no custom_components/ change, so the review does not widen. Three-dot against the merge-base, the PR is still the same 6 files (+305/-6).
- Prior block resolved: mutation-vacuous.
  - red_carried_to_next_cycle is now killed by "darwin-selftest: a new cycle starts with an empty red list after a cycle that had REDs". That is the in-file MUTANTS row, and also the round-3 reviewer's own mutant text re-applied independently (ev/mutants.txt).
  - no_per_run_remember is now killed by "darwin-selftest: a pass killed partway keeps the runs it finished". This holds both for the in-file row, which deletes the line, and for the round-3 reviewer's mutant, which replaces the call with `pass` (ev/mutants.txt).
  - The new red case reads the second cycle's digest and asserts that it is empty, which is what round 3 asked for. The new kill case raises from the second `ctx.run` and asserts on the persisted state: `done == [prepr.sh]`, `complete` False, tip A.
- Null control: the unmutated head with `--self-test --no-mutants` gives rc=0.
- Re-run of the round-3 mutant set at this head (ev/mutants.txt):
  - Killed: done_carried_to_next_cycle, complete_default_false and no_final_remember.
  - Surviving: no_stale_wt_remove (out of scope, under Findings) and budget_gt (the 900 s boundary is equivalent under the fixture, dismissed in round 3).
  - The worktree was clean afterwards (ev/wt-status-after.txt is empty).
- Body figures re-derived at this head. `python3 -I tools/audit/seat/beat_jobs.py --self-test` gives rc=0 and `beat_jobs self-test: 242 checks, 0 failed`, 31 s wall on Linux (ev/selftest.txt). The self-test prints 17 darwin-lane `ok mutant ... killed by:` lines, matching "Seventeen mutants" (10 + 5 + 2), and each names the case the body names. The figures from earlier rounds (M1 wall times, enumerator 80/81) were checked in round 3 and are unchanged in this body.
- Merge with main: `git merge-tree --write-tree origin/main 4d5b7e94` exits 0 with tree bcc2eccb, so it merges cleanly (ev/merge-tree.txt).
- Red checks: none answered. The owed-reds set is in ev/owed-reds.txt.
- CI: `merge_train.py classify` printed WAIT for every poll from 04:23Z to 04:58Z, about 35 min (ev/classify.log, last line `WAIT 4d5b7e94d1807b987fac5323e9129f9359d6b7a9 pending: gate red: none`). This verdict is a merge with pending-ci: gate.
