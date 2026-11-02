Fix review: merge a9541f2f83649630ffbe20405d4334db693bcbef

bus-nonce: 2919a89cebb30e3e077d3f02e9348777

This is round 3, a past-three minimal re-cut under the orchestrator ruling of 08:40Z. It is a delta review of repair commit 3de2926c6, judged at head a9541f2f83649630ffbe20405d4334db693bcbef from a detached worktree.

## Head

The head is a9541f2f83649630ffbe20405d4334db693bcbef. It merges eb17067c3 (the previous head cee9f6f44 plus code head 3de2926c6) with origin/main 8fcaf47e1, and 8fcaf47e1 is the merge base. `git merge-tree --write-tree origin/main a9541f2f8` exits 0 (tree 78b556546), with no conflict. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current. The body's `## Head` names this head and the code head 3de2926c6. `## Re-cut` names round 3, and `## Red checks` is present.

## Findings

- A reap-side stem site survives the self-test: line 240 of open_driver.py, the failure path's `reason(d / (stem(t) + ".log"))`. It is one of the two reap-log sites (232 and 240) that verdict/3164 named. The repair pins 232 (M-reap-log) but not 240. My mutant R-fail-log-nostem reverts it to `t + ".log"`, and the self-test stays green at `68 checks, 0 failed`. With it, a refused slash-topic open prints `OWED ... open-refused a/b 44444444 rc=3 no log` instead of `... rc=3 REFUSE no-row`. My probe ev/reap_fail_probe.py shows this (ev/reap_probes.txt, ev/reviewer_mutants_head.txt). The rc, backoff and retry stay correct, so only the OWED reason is lost. I judged that too small to block a past-three re-cut. Repair: a self-test row in which a slash topic's open fails and the OWED line carries the log's reason, plus an M-fail-log mutant. Carry: R10-OPENER-REUSE
- Two findings from verdict/3164 are not in the roster entry yet, and the body defers both to the orchestrator's roster op: stem() does not escape `%` (and a topic named `open-driver` would overwrite the driver's own log), and the hostile-topic `log written` read is unguarded. Carry: R10-OPENER-REUSE

## Evidence

- The blocked finding is closed. With round 2's mutant R-reap-nostem planted again (`rcf = d / f"{t}.rc"`), the self-test goes red with rc=1 and 2 failed: `slash topic reaped: RESULT a/b rc=0 with its log's reason` and `slash topic reaped: seen, not reopened`. With the fix in place, the null M0 run is green at `open_driver self-test: 68 checks, 0 failed` (ev/selftest.txt, ev/reviewer_mutants_head.txt).
- The finder's harness is verdict/3164's evidence/reap_probe.py, re-run unchanged against this head (ev/finder_reap_probe.py). At the head it prints `ok   a/b RESULT a/b 44444444 rc=0 opened | SKIP a/b 44444444 seen | SKIP a/b 44444444 seen` and `RESULT reap_probe failed=0`, so the slash topic is reaped and then held seen, not backed off. Under R-reap-nostem it prints `FAIL a/b SKIP a/b 44444444 live`, `RESULT reap_probe failed=1` (ev/reap_probes.txt).
- Open side (World.launch positional arguments, hostile-topic fixtures), each with the self-test, the finder's reap_probe and launch_probe, and my reap_fail_probe. old-launch: self-test rc=1, launch_probe failed=30. R-open-rc-nostem: 3 failed. R-open-log-nostem: 2 failed. R-stem-noop: 2 failed. R-shift1: 4 failed. R-unquoted-log: 2 failed. R-argv-swap (topic and sha swapped): 4 failed. All are killed, and M0 is green on all four instruments (ev/reviewer_mutants_head.txt, built by ev/mk3.py and ev/run_mutants.sh).
- Reap side. R-reap-nostem: 2 failed. R-reap-log-ok (line 232): 1 failed. R-reap-alive-dead: 2 failed. R-reap-rc-empty: 3 failed. All are killed. R-fail-log-nostem (line 240) SURVIVED; see Findings.
- The fixer's harness at this head (`python3 dev/audit/harnesses/r10_open_driver_mutants.py`) gives `RESULT mutant=M0 failed=0 verdict=null-ok`, `RESULT mutants=19`, `RESULT survived=0`. M-open-stem failed=3, M-reap-stem failed=2 and M-reap-log failed=1, as the body's table says. M-launch gives failed=2, killed, matching the corrected figure (ev/fixer_mutants.txt).
- Previous-head figures, re-derived at cee9f6f44: M0 gives `66 checks, 0 failed`. M-open-stem gives rc=1, 1 failed (`launch 'a/b': rc file written with 0`). M-reap-stem and M-reap-log give rc=0, `66 checks, 0 failed`. This matches the body (ev/prev_head_mutants.txt).
- 3de2926c6, read line by line, adds only the self-test `Slash` row: real World.launch and alive, a dummy opener, a state directory containing a space, a wait of at most 10 s for the stemmed rc, then reap and seen. It also adds the three harness plants. The PR's three-dot interdiff against the round-2 head touches only open_driver_selftest.py (+31) and r10_open_driver_mutants.py (+8). open_driver.py is byte-identical, so no other production change was made, and the workflow change in the three-dot diff is still only the self-test step in governance.yml.
- Standing checks (ev/standing.txt, ev/structure.txt, ev/gate_mode.txt). The delivery row dev/programme/delivery/3164.md is in the three-dot diff. No claim file, VERSION, manifest, RELEASE_NOTES or `*_budgets.json` is touched. No host path appears in any added line. `tests/structure.py` prints STRUCTURE RATCHET PASSED with rc=0. `tests/closure.py select` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, as the body says.
- The forward-carry points to the roster entry for R10-OPENER-REUSE part 2. The round-2 findings in it are recorded under Findings above.
- CI: `python3 tools/audit/seat/merge_train.py classify a9541f2f83649630ffbe20405d4334db693bcbef --pr 3164` exited 0 at 10:08:39Z with `GREEN a9541f2f83649630ffbe20405d4334db693bcbef pending: none red: none` (ev/classify.txt, ev/classify.rc). Before posting, I re-read the PR head and it is still a9541f2f83649630ffbe20405d4334db693bcbef.

## Red checks

None. I read every check-run at this head from the commit's check-runs API, with every page, and each one concluded success, skipped or neutral (ev/check_runs.txt). The body's `## Red checks: none` is accurate, so step 11 owes nothing.
