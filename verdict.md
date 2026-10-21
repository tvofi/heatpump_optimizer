Fix review: merge 1ebbae78756a3802009081f1fd5a1df4918e7ee5

Round: delta re-verdict (round 2 on this PR; predecessor blocked body-stale at fe1365f0f992b1d53d79c8e0a1d94804a74f53d8). Head re-read on origin before writing: still 1ebbae78756a3802009081f1fd5a1df4918e7ee5.

RESULT body-point-1 null-control: FIXED. The body names three carry lists differing from main; re-derived at the head (ev/carry_lists.txt): R10-LIVESTATE 8->9, R10-POLICY-FIXER-MD 5->6, R10-UX-HEALTH 5->6, and no fourth group. Carry: dismissed body point verified fixed
RESULT body-point-2 commits: FIXED. The commit paragraph names 9dc08aac2 (item 6ce59610, onto R10-UX-HEALTH) and 23ef06dc6 (item 4c077302, onto R10-LIVESTATE); carry_audit owners finds each item in exactly that group's carry at the head (ev/owners.txt). Carry: dismissed body point verified fixed
RESULT body-point-3 head: FIXED. The Head section names 1ebbae78756a3802009081f1fd5a1df4918e7ee5 as the PR head, 23ef06dc6 as the authored code head (it is the tip of origin/handoff/audit-r10-roster), and f424d993d as an earlier ancestor. Carry: dismissed body point verified fixed
RESULT groups: 108 at main and at head, same ids. Note/brief changed for exactly 12 groups; `after` changed for exactly the 10 the body lists. carry_audit sweep (main vs handoff) reports ROSTER-DRIFT for exactly those 12 (ev/sweep.txt). The roster at the head is byte-identical to origin/handoff/audit-r10-roster. Carry: dismissed figure re-derived, matches
RESULT critical-depth: plan_table.py prints 11 wave(s) at origin/main 57f0c9c77 and 8 wave(s) at the head; the critical path at the head matches the body's eight groups exactly (ev/plan_main.txt, ev/plan_head.txt). Carry: dismissed figure re-derived, matches
RESULT delta: git diff fe1365f0f..1ebbae787 is byte-identical to main's own f2fb1b0e9..57f0c9c77 (18 files, +170/-38: PR #2527 and #2581 with their delivery rows). Nothing under dev/programme/rosters/ moved. Three-dot diff vs main lists the same six files the body lists (ev/delta_stat.txt). Carry: dismissed main merge only, verified
RESULT lint: brief_lint from a fresh origin/main worktree over the head's roster prints `TOTAL: 0 error(s) across 1 file(s)` (ev/brief_lint.txt). carry_audit owners finds an owning group for the 6ce59610, 4c077302 and #2567 carries, no orphan. Carry: dismissed lint gate clean
RESULT merge-tree: `git merge-tree --write-tree origin/main 1ebbae787` exits 0, tree 3b3dec0e3, no conflict and no claim-file driver call (ev/merge_tree.txt). Carry: dismissed clean merge measured
RESULT ci: check-runs on the head, read once: 21 runs, none red. pr-contract (two runs, the later started 18:10:09) success, delivery-status, policy-docs, wave-script, budget-raise-gate, arch-score, scope, hassfest, validate-hacs, Analyze (actions/python) success; record, delivery-status-publish, kernel-points skipped. Pending at read time: Analyze (javascript-typescript), env-matrix, instrument-self-tests (ev/check_runs.txt). No red check, so step 11 owes nothing yet. Carry: dismissed no red check
RESULT mutation: n/a, roster state and evidence only, no production or test code line; the delta is main's own. Carry: dismissed no code changed
RESULT forward-carry: body says none; the PR's own carries landed in roster groups (verified above). Carry: dismissed nothing to propagate

Note: tests/layout.json is code-owned, so the PR still needs @tvofi's approving review. Carry: dismissed owner review already requested

bus-nonce: 4942e7460eab68db29c0ef60597171a3
