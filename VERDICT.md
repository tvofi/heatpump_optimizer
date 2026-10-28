Fix review: merge 1c3302acfc64e780f8c1cf9b3f3f6876132bdee1

bus-nonce: d8185da8367b8eae313140f31f239962

## Round
Round 4 of the #2738 lineage. This round is a re-cut (b2ab64317, merged as 1c3302acf with origin/main 806aa2ce8). I judged the whole P64 ruling at the live head, not only the delta.

## Findings
- The Binding line says "app_push.sh's committed-tip gate (`is not the committed tip`) refuses a detached HEAD". That is not what the gate does. `tools/pr/app_push.sh` line 484 compares the HEAD sha with `refs/heads/$br`, so a worktree detached exactly at the branch tip passes (`ev/repro_detach_gate.txt`: `RESULT detached-at-tip gate=PASS`). The gate refuses only after a commit lands on the detached HEAD (`RESULT detached-then-row-commit gate=REFUSE`). The ruling's prescription still holds, because each site it rules out (open_pr.sh p1, `mut:push-open`) commits a row before its next push. But the fixer must not count on the gate to catch a misplaced detach: a detach followed by a push with no commit in between would pass the gate without any warning. The helper's self-test arms should assert the sequence itself, not lean on the gate. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence
- Head reviewed: 1c3302acfc64e780f8c1cf9b3f3f6876132bdee1 (`ev/HEAD.txt`). Just before return, `refs/heads/triage/s6-batch6` and `refs/pull/2738/head` were both still at that sha. The body's `## Head` names it. Contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, and the merge base is origin/main 806aa2ce8.
- Diff (three-dot): `dev/programme/delivery/2738.md` (+1) and `dev/programme/triage/s6-batch6.md` (+17), both under `dev/programme/`. `VERSION`, the manifest and the `RELEASE_NOTES.md` diff are empty.
- Earlier blocks, each checked against the live text:
  - Round 1 (detach inside app_push.sh): answered. The carry says "Never inside app_push.sh", and the detach comes after each run's last push.
  - Round 2 (handoff_push.sh update arm reuses the detached worktree): answered. The update arm is named in Binding and Sites, with a re-attach before the reset.
  - Round 2 (`--free-holders` engagement): answered. The "Why not" paragraph cites merge_train.py `freeable` (empty porcelain and HEAD == origin/<br>, no prefix restriction). I verified this at lines 789-803 of the head.
  - Round 2 (uncited update_pr.sh holder clause): gone.
  - Round 3 (`checkout -B` drops the reset's discard): answered. The arm now uses `checkout -q -f -B "$BR" "origin/$BR"` and keeps `reset -q --hard`. Re-run: `RESULT ruling-update-arm sym=refs/heads/br porcelain=[] gate=PASS`, against `RESULT todays-update-arm sym=DETACHED` (`ev/repro_detach_gate.sh`, my own scratch instrument).
- Class rule re-run at this head: `git grep -nE 'bash "?\$_push"?|push_app [0-9]' -- tools ':!tools/pr/app_push.sh'` returns 8 lines (`ev/merge_tree_and_sites.txt`). They are handoff_push.sh 114 (push_app body), 179 (`mut:push-update`), 198 (`mut:push-open`) and 212 (`mut:push-row`); open_pr.sh 58 (p1) and 71 (p2); remerge_main.sh 29 (`--recarry`); and update_pr.sh 77. The Sites line disposes of each one. The class is closed.
- Next-run claims re-derived: open_pr.sh line 46 runs `git worktree add -q -b $BR $WT $C`. update_pr.sh line 51 runs `worktree remove --force` and line 52 re-adds with `-B` at `origin/$BR`. update_pr.sh line 50 holds the `checked out elsewhere` exit. All three of open_pr.sh, update_pr.sh and handoff_push.sh source pr_args.sh.
- Figures: `grep -c '^Verdict:'` prints 1. `roster_edit.ruling_verdict` gives `ACCEPT` for P64 and `None` for P99 (the null control re-run). `ref_privacy.py --check` prints `0 refused`.
- Not re-derivable here: the Instances figure (seat-ledger.md line 99, proposals.md line 89) lives in the orchestrator's out-of-tree record, so I did not verify it. s6-batch5.md (P63) is not on origin/main at this base, so the numbering continues from an unmerged record.
- Merge: `git merge-tree --write-tree origin/main 1c3302acf` exits 0 with tree c1ec950d05bed4d1dfd8fe78a78caa960409abe7 and no conflict. No claim file is touched.
- CI at this head, from the check-runs API (`ev/check_runs.txt`): no run is red. Every concluded run is success or skipped. Still in progress at review time: instrument-self-tests, prelude, browser, closures, coverage and fast (3.14). The reds at earlier heads (instrument-self-tests host-path refusal at c24be17f8, pr-contract body-contract and codescan_wait at c24be17f8/d1756ee44, and gate) are each named and answered in the body's `## Red checks`, with a cheaper detector named for the host-path one.
- Mutation proof: n/a. The diff writes no production or check line, so no mutant is drawn.
- No figure in the diff moves an instrument (no budget, closure, INERT or golden file).
