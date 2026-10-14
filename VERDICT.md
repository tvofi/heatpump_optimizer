Fix review: merge 66a33cab8db7fe1ce41ef2c8a88c05fd5da0eb4c
bus-nonce: c6c99ff49f14e52fedd2e57e9149d5d4
reviewer: r10-2205-reviewer (round 1)
evidence: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/r10-2205-reviewer/evidence

Measured at 66a33cab8 from a detached worktree; base = merge base 554e2ecfa. python 3.14.7 (seat venv). Contract roles/ diff vs origin/main empty.
The finder's instrument is the nightly lane, tests/replay.py; r10_2205_replay_cost_arms.py is the fixer's own harness (disclosed as such in its docstring). I ran both.

RESULT lane head (tests/replay.py): ALL 81 replay checks PASSED; clean cpu_ratio 1.9474; cpu arm 3.9512 injected_ratio 1.0; loop arm injected_ratio 1.0001; memory 3830.0 KiB
RESULT doubled arm burns >= 1.0 clean span: cpu injected_ratio 1.0/1.0/1.0 (harness, head), loop 1.0001 x3; base cpu arm hot/clean 1.756-1.871 (under 2), head 2.022-2.193
RESULT planted 0.9 arm (_spin(..., 0.9 * clean_span)): 2 of 81 FAILED, both "the <arm> arm doubles the whole span" (injected 0.9 / 0.9001); "cycle_cost sees a doubled cycle cpu" still PASSED at 3.6891, so short_doubling is the only check that catches it
RESULT M1 (fix line reverted to `if inject == "loop":`): 2 of 81 FAILED, cycle_cost sees a doubled cycle cpu (1.9104 vs 1.8925) and the cpu arm doubles (injected 0)
RESULT threshold mutant >= 0.9: control:cycle_cost:short_doubling FAILS (bad=[] good=[]); unmetered_doubling still passes, as designed
RESULT null control (memory arm hot/clean cpu_ratio): base 0.882-0.995, head 0.979-1.010; peak doubles at both ends (3824.7-3826.2 KiB)
RESULT CI figures re-derived from the six slow-job logs (10-09..10-14): clean 2.1955/2.5992/2.7689/2.1559/2.1758/1.8804, ref_ms 53.5/32.4/22.2/53.0/53.3/23.8, cpu arm hot/clean all < 2 -- match the body
RESULT budget: 2.332 = sqrt(2) x sqrt(1.4458 x 1.8804) re-derived; band (1.166, 2.332]; post-#2142 projection checked against the one measured CI point: the ref-22 class projects 1.857, measured 1.8804 (+1.3 %)
RESULT not a raise: cpu_ratio 3.576 -> 2.332 is a tightening; COST_BUDGETS lives in tests/replay.py, no *_budgets.json touched; budget-raise-gate success
RESULT claim files, VERSION, manifest, RELEASE_NOTES untouched (three-dot); merge-tree vs origin/main clean (rc 0)
RESULT check-runs at head (API, 37 runs): all completed; only red is nightly-status (main's schedule run 38530020347, not reachable by this diff, answered under ## Red checks); slow skipped on PRs, so my local lane is the only head measurement of replay
RESULT mutation lane green with no production line in the diff (tests-only change draws no mutant)

Judgement on the budget's headroom: honestly centred on the data available, but the post-#2142 spread rests on one measured CI point plus a projection that point corroborates. Headroom to the highest known class is 24 %, comparable to the old cap's 29 % over 2.769. Risk to carry: on this box under load1 75 (8 cores, ~9x oversubscribed) one base clean run read 2.3371, over 2.332, with its ref_ms falling to 42 -- denominator noise under heavy contention. CI runners have not shown that; if a nightly reds on the clean arm's over-budget line, re-record from the nightly series rather than read it as a regression.

Body nits, non-blocking: d7bfeb0dd at lines 19/21 is a legitimate historical reference (a commit in the list and the end of a diff range; the Head section names 66a33cab8, whose only change is the autofix delivery row). The body's "ALL 80 replay checks PASSED" I could not re-derive: at this head the lane summary reads 81. The body's runs used python3.13, not the seat venv.
