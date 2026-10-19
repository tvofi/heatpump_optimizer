Fix review: blocked 01e08685f4e454e17dc16c467a5e5e3c7ad8be5f regression: the automatic merge of origin/main dd27e7c1b (#2406 O17 removed roster_lib.DEFAULT_ROSTER_REF) breaks fold 7; orchestrator_tick.py --self-test crashes with AttributeError at carry_sweep line 1782, so the body's "142 checks, 0 failed" is false at this head

bus-nonce: ee543287c3950c1e2f824fd400ff7257

Round 1: the PR has no earlier `Fix review:` comments. Measured head: 01e08685f4e454e17dc16c467a5e5e3c7ad8be5f (ev/HEAD). Role contract current (diff of dev/governance/roles/ vs origin/main is empty).

## Blocking
- `python3 tools/audit/seat/orchestrator_tick.py --self-test` at 01e08685f4e454e17dc16c467a5e5e3c7ad8be5f: rc=1, traceback
  `carry_sweep: default = rl.DEFAULT_ROSTER_REF ... AttributeError: module 'roster_lib_tick' has no attribute 'DEFAULT_ROSTER_REF'` (ev/tick_selftest_head.txt).
  At the code head 0b5c9b24 (git archive) it prints `orchestrator_tick self-test: 142 checks, 0 failed` (ev/tick_selftest_codehead.txt).
- Cause: 6ad3b1bb7 merges origin/main dd27e7c1b, which carries a5de742c0 (#2406, O17): `-DEFAULT_ROSTER_REF = "origin/main"`, replaced by `default_roster_ref(git)` returning the round's roster branch. The merge was textually clean (its tree equals `git merge-tree 0b5c9b24 dd27e7c1b`, f4f34267) but broke the build. The body says "any resolution inside the code head is described below" and quotes every figure as "measured at this head". The tick figure was not re-run after the merge.
- Live effect: `--only CARRY` at this head does not crash only because carry_audit.py is absent and the section returns early (ev/only_carry_head.txt). Once #2404 lands, every `--only CARRY` run without `--roster-ref` raises. That is the weekly and closure sweep fold 7 delivers. The fix also has to follow O17's semantics: the default ref is now `default_roster_ref(...)`, not origin/main, so a plain rename is not obviously right.
- CI could not catch this: no workflow runs orchestrator_tick.py (grep of .github/workflows is empty). The body's own forward-carry names that gap. The pre-handoff gate does not re-run the instrument self-tests after the orchestrator's main merge, which is the cheaper detector.

## Checked and holding
- `git merge-tree --write-tree origin/main 01e08685f4e454e17dc16c467a5e5e3c7ad8be5f`: rc=0, tree cab603fb.
- Head structure: 7635793e2's tree equals 0b5c9b24's tree (32773194). 6ad3b1bb is the automatic merge with dd27e7c1b. 01e08685 adds only dev/programme/delivery/2422.md.
- VERSION, the manifest version, RELEASE_NOTES.md and goldens are untouched (pr-contract log: "no version edit").
- Self-tests at the head (ev/selftests.txt): pr_args 46/0, pr_cap 12/0, tick_loop 4/0, bus 70/0, proof_watch 34/0, delivery_row via open_pr. These match the body.
- CI on the head (check-runs API, 03:36Z run): red arch-score x2, env-matrix, validate-hacs, nightly-status and pr-contract x2. coverage and Analyze (python) were still in progress. I did not read each infrastructure red's log, because the block above is independent of them. pr-contract's red needs re-reading after the reruns.

## Not done
- Hand mutants M1-M7, C1-C7 and U1-U2 not re-run. The tick self-test that kills them crashes at this head, so none of them is verified here.
