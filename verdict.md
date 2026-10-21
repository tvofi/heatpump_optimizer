Fix review: merge 31ce1c0cbb552095177d3ef733f88d9515b65d7c

bus-nonce: 798cdc485ee4e4b8d556162234ddef10

Round: third review of #2525 (the second returned merge at eda11668; this head adds one merge of origin/main). Measured head: 31ce1c0cbb552095177d3ef733f88d9515b65d7c, still the PR head when this was written (refs/pull/2525/head and fix/r10-wip-cap). I worked in a detached worktree at that head. dev/governance/roles/ does not differ between the merge base and origin/main, so this review ran under the current contract. The prior verdict (probe/rev-2525-45db6e37) was read as one argument, and every figure below was re-taken at this head.

RESULT head=31ce1c0cbb552095177d3ef733f88d9515b65d7c base=origin/main 03b49e152 merge_tree=clean tree=7317cf669035 exit=0 (ev/merge_tree.txt)
RESULT main_merge_delta: the head tree equals git merge-tree eda11668 03b49e15, so this is an automatic merge with no resolution delta. All 9 PR files are blob-identical to eda11668 (ev/pr_files_vs_prior_head.txt). The merge brought in only main's dev/programme/delivery rows 2526/2543/2546/2550-2552 and 22 mutation-ledger killed_by JSONs. The fix and its self-tests read none of these (the tick's self-tests use faked delivery paths).
RESULT pr_cap_selftest="21 checks, 0 failed" pr_args_selftest="54 checks, 0 failed" tick_selftest="152 checks, 0 failed" selftest_wiring="37 self-testing, 37 wired, 0 unwired" (ev/selftests.txt)
RESULT dispatch_gate_live: rc=1, "REFUSE: WIP cap: 6/6 at the cap" naming six in-progress groups, at origin/main (ev/dispatch_gate_live.txt)
RESULT structure=PASSED layout_guard="0 refusal(s) against 03b49e1521a2" policy_lint="TOTAL: 0 error(s) across 41 policy file(s); FIXTURE ok" rules_sync=ok orchestrator.md=317 lines
RESULT mutation (a) main's pr_cap.py: pr_args "54 checks, 6 failed", the six arms the body names: KILLED
RESULT mutation (b) n<cap -> n<=cap: pr_cap "21 checks, 1 failed": KILLED
RESULT mutation (c) tick n=len(prs): tick "152 checks, 2 failed", the two arms the body names: KILLED
RESULT mutation (d) unreadable roster treated as an empty roster: pr_cap "21 checks, 3 failed", the three arms the body names: KILLED
RESULT own mutants: WIP_STAGE=fixing KILLED(6); mut:overcap line deleted KILLED(1); empty-reason arm deleted KILLED(1) (ev/mutations.txt)
RESULT ci at head: 46 check runs, all completed: 29 success, 16 skipped, 1 failure (nightly-status) (ev/check_runs.tsv)

Findings, by step:
1/3 Mutation proof and null control: (a) to (d) each reproduce the body's exact tallies at this head. For (d) I planted `roster = {}` on the refusal line instead of the body's `{"groups": []}`; the same three arms failed. The null-control arms are present and pass: 0 WIP passes, 20 open PRs is information only, and an unreadable roster refuses.
2/9 Harness: the finding is the owner's ruling and has no numeric finder harness, so the mutants and self-test arms are the measurement. I built none.
4/5 The diff touches no claim file, golden, budget, VERSION, manifest or RELEASE_NOTES.
6 Class: the body names no enumeration rule, so I used my own: grep for pr_cap, open-PR cap and soft cap over tools/, .github/, .claude/ and tests/ (ev/class_enum.txt). It returns the five seat files and governance.yml, all in the diff, plus tools/plan/replan.py. replan.py bounds groups in flight at wave open. That is dispatch, which the ruling allows, and it never refuses opening a PR, so it is outside the class. This agrees with the prior review.
7 The body's ## Head names 31ce1c0cbb552095177d3ef733f88d9515b65d7c and describes it as an automatic merge of origin/main 03b49e152 onto the previous head. Verified above.
8 Every figure in the body re-derives at this head. Not re-derived by me: the ci_predict.py and closure.py select outputs. CI's closures and mutation runs at this head are green.
10 Forward-carry: "none". The change binds orchestrator.md §5 directly. The roster group R10-OPENPR-SILENT is stage done, with a note naming #2525 as its follow-up, and its listed carry (the carry_audit sweep) is not this PR's.
11 Red checks: nightly-status is red. Its inputs (tests/nightly_status.py, .github/workflows/tests.yml) are untouched by the diff, so it grades main, and the body names it. The previous head's policy-docs, env-matrix and pr-contract reds are named with a cheaper detector. policy-docs, env-matrix, pr-contract, closures, fast, coverage, coverage-ratchet, mutation and CodeQL are all green at this head.
13 merge-tree against origin/main 03b49e15 is clean, exit 0; nothing conflicts.
14/15 The main merge moves no number. The PR's own instruments are unchanged from the prior review: no budget moves, and orchestrator.md was paid down by cutting prose. Architecture: the WIP count reuses roster_lib through pr_cap.wip_groups, with no breach.

Approval still owed, not by this verdict: orchestrator.md is policy, and pr_cap.py, open_pr.sh and orchestrator_tick.py are code-owned paths, so tvofi's approving review at this head is still required.
