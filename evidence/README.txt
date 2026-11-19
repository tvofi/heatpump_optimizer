PR 3801 review evidence, head 5e10f99bc84d7ecef0d5dbdc4e3451ed27cc2c4c (detached worktree /Users/timmalmstrom/hpo-seats/r11/rev-3801/wt).
Finder's harness: selftest_scope.drift() (the CI step "Refuse a self-test read set the committed table misses")
over red main push run 44408012370's own selftest-closures artifact (1723f9fdc9), with the workflow's steps.
- harness-base.txt     table at main 1723f9fd (unchanged at ed7025dc): 4 UNDER-SCOPED, the four CI printed
- harness-head.txt     table at head: 0 refusals
- harness-perturb.txt  each of the 4 added items dropped alone: 1 UNDER-SCOPED each (harness moves under perturbation)
- class-enum.txt       every survivor_triage/* directory (39) at head and main is in all three dirs steps and its .gitattributes in the probe step
- static-selftest.txt  selftest_scope static 127/0; --self-test 118/0
- check-runs-5e10f99b.txt  head check runs: all success/skipped/neutral, gate success
