Fix review: blocked d6482b704bb11831c12001ffc0b0210a47c35483 mutation-vacuous: bg_wait's still-running poll survives every arm; a slow-failing prepr self-test reads green under it

bus-nonce: 5c5f6f5dd97a85992c401adb5eac7593

Round: first-round fix review of PR #3275 (R10-HOTFIX-SELFTEST-TIMEOUT), measured at head d6482b704bb11831c12001ffc0b0210a47c35483 from a detached worktree. The head is unchanged at verdict time (`refs/pull/3275/head` = d6482b704).

## Block

- Mutant X8 inserts `return 0` after `bg_wait`'s `sleep 5`, so `bg_wait` returns 0 once its first poll finds the test still running. It survives every arm of `dev/audit/harnesses/r10_selftest_timeout.py`. Every arm's command has either finished or been killed before its `bg_wait` runs (the arms `sleep 2` first), so the loop's still-running path is never exercised. The mutant is the same shape as the fixer's M1 and M2: a return replaced by 0, on a line this PR adds.
- The defect it admits is a false green. "Show the pre-PR self-check refusing its own fixtures" is `bg_wait prepr` alone, with no tally grep (prepr.sh prints none). Under X8 that step passes while prepr.sh's self-test is still running, or after it fails late. I added a slow arm (`bg_start slowbad bash -c 'sleep 8; echo partial; exit 5'`, then `bg_wait slowbad` with no grep, as the prepr step does):
  - committed library: `PASS refuse slow bad`, `PASS control slow ok`
  - X8: `FAIL refuse slow bad (prepr-shaped step passes)`, `PASS control slow ok`
  The other four waiter steps grep a tally, so a partial log fails them. The prepr step is the one this mutant reaches.
- The body itself says the job now lasts as long as the longer of the in-line steps and prepr.sh's self-test, so prepr can still be running when its waiter is read. In the head's CI run it had already finished (waiter at 0 s), which is why CI cannot show this.
- Cure, either one: add a still-running arm to the harness (a slow failing command waited on before it ends, refused with no grep; X8 then dies), or give the prepr waiter a terminal line to grep. Re-run M1, M2 and X8 afterwards.

## Findings

- Follow-up: pr_args.sh's `mut:unlock` arm is load-sensitive: per the body, 1 FAIL in 9 runs with all five self-tests at once, and 9 of 9 PASS chained. Chaining restores the base's order, but at this head the chain still runs alongside the in-line steps and a niced prepr.sh. That is more load than the base had (all serial). Nine passes bound the residual rate only loosely, as the body says. The body dismisses it to a comment at the launcher step, which leaves no owner for a flake this PR's concurrency can still trigger on main, where a red cancels a merge-train slot. The re-cut owes either a measured rate under the head's real CI load (more than one CI run's observation) or a roster carry to the group owning tools/audit/seat/pr_args.sh, for a deterministic `mut:unlock`. Carry: R10-HOTFIX-SELFTEST-TIMEOUT

## Evidence

- RESULT harness at head (fixer-built, disclosed as such; there is no finder harness, because the finder's enumerator is the orchestrator's `gh run view` job timing): M0 8/8 PASS, M1 KILLED by refuse chained bad and refuse bad, M2 KILLED by refuse chain killed and refuse killed, `RESULT survivors=0`, rc 0. File: ev/harness_head.txt.
- RESULT reviewer mutants on the library through the fixer's arms: X5 (bg_run always records 0) KILLED; X7 (bg_run writes no status) KILLED; X8 (bg_wait returns 0 after the first poll) SURVIVED. File: ev/reviewer_bgrun_mutant.txt.
- RESULT reviewer mutants on the launcher step, replayed with stub commands and the five committed waiter steps. X0, the null control, passes all five. Each of these fails exactly its own waiter: X1 (`bg_start prepr` deleted), X2 (`bg_start beatd` deleted), X4 (the pr-args link deleted). X3 (the chain's `bg_pid` deleted) passes only because the stubs finished before the waiters read them. With a missing pid file, `bg_wait` fails at once (shown by a trace: `kill -0 ''` fails, rc 1), so X3 can only fail closed. File: ev/reviewer_workflow_mutants.txt.
- Focus checks:
  - No check run is renamed: the five waiter steps keep their old names, and their grep lines are byte-identical to the base's in the three-dot diff.
  - The job id and `timeout-minutes: 30` are unchanged.
  - bg_wait refuses a missing status (M2 and X1).
  - `selftest_wiring.py --check`: `118 self-testing, 118 wired, 0 unwired` (ev/selftest_wiring.txt).
- CI at this head is a real run, not a replay: `governance / instrument-self-tests` job 128289649754 (run 42334641003, attempt 1) ran 03:40:04Z to 03:50:35Z, which is 631 s, a 65% margin under 1800 s (the brief asks for at least 30%). Step 104 (PR updater) waited 90 s on the chain, so the chain is the new critical path, not prepr. The log tail shows `pr_args self-test: 174 checks, 0 failed`. File: ev/ci_head_job.txt. The body's projected ~710 s is consistent with this.
- Not re-derived: the CI "before" per-step figures (runs 42297617709 and 42291959742) and the local replay figures (1870 s and 737/744/702 s). figure_lint resolves their commands (ev/review-packet.md), but I did not re-time them.
- `merge_train.py classify d6482b704... --pr 3275`: `GREEN d6482b704bb11831c12001ffc0b0210a47c35483 pending: none red: none`, rc 0 (ev/classify.txt). The packet's gate digest shows no concluded red, so `## Red checks: none` is accurate.
- `git merge-tree --write-tree origin/main HEAD` (origin/main 630bf533d) exits 0. Its stderr reads `LEDGER-MERGE: resolved tests/closures.json` (merged as a set). File: ev/merge-tree.txt.
- Hygiene: the three-dot diff touches .github/workflows/governance.yml, the new harness (classified INERT in tests/closures.json), the delivery row dev/programme/delivery/3275.md and tests/closures.json. No budget file, VERSION, manifest or RELEASE_NOTES.md is touched. `## Head` names d6482b704, the head reviewed. The roles directory is current against main (empty three-dot diff).
- Reviewer-built instruments: /tmp scratch scripts rev_mut.py and the inline slow arm. Their output is in ev/. The slow arm is the one the re-cut should land in the committed harness.
