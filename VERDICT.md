Fix review: blocked 3d8f7c37815f78f5eee3718848bbd1b47057d786 carry-missing: six carries this batch appends land on groups the same batch leaves done -- P227 R10-FLY-OPENPR-ATOMIC, P228 R10-FLOW-MAIN-GATE, P229 R10-ORCH-REVIEW-PACKET, P231 R10-TRAIN-OVERLAP-GRADE, P234 R10-PREPR-CAP were reopened to the derivable stage `fixing` and roster_sync 8c57b43dd re-derived all five to `done` from their old merged PRs; V149's RCA carry on R10-FLOW-BOARD was set done by roster_sync d9f81f5c5 one commit after it landed

bus-nonce: 5c813002eb52bd6bd3f0e9edc8eede3a
reviewer: local-reviewer-s10
round: 1
measured: 3d8f7c37815f78f5eee3718848bbd1b47057d786 (detached worktree; head re-read before post, unchanged); base origin/main eab04d0eb

## Blocking: carries stranded on done groups

`ev/trace.txt` (python3 ev/trace.py, first-parent eab04d0eb..69b1ac245) shows the sequence for each:
set-stage <G> fixing -> append-carry <G> -> roster_sync 8c57b43dd sets <G> done (resume.pr is the old merged PR).
The triage rulings route each as "a carry of <G> (resume.stage done ...) ... The group is reopened first (the P196 route)"
(s6-batch45.md P227/P228/P229/P231, s6-batch46.md P234 on main). The net at the head is the five groups done with the new ACCEPT carry on them,
so no fixer is dispatched for any: the reopen the ruling required is undone in the same batch. The FLOW-BOARD carry
(root-cause owed for #2883's 2nd red check) is stranded the same way (6f074ab57 append, d9f81f5c5 done).
`tools/audit/seat/roster_sync.py` protects `carries-open` (PROTECTED_STAGES, self-test :999-1010) but derives `fixing`, so the op that survives a sync is
`set-stage <G> carries-open` -- the shape this same batch uses correctly for R10-ORCH-ROSTER-SCHEMA (728e1d80c).
Remedy: six roster_edit set-stage ops to `carries-open` (or a fresh stage with a non-merged resume.pr) on R10-FLY-OPENPR-ATOMIC, R10-FLOW-MAIN-GATE,
R10-ORCH-REVIEW-PACKET, R10-TRAIN-OVERLAP-GRADE, R10-PREPR-CAP, R10-FLOW-BOARD; re-lint; re-request review.
This is the stranding class R10-ORCH-ROSTER-SCHEMA's new carry (item 3: roster_sync never emits carries-open) describes; no CI check catches it today.

## Checks that pass

- brief_lint at the head (head already merges main eab04d0eb; `git merge-tree --write-tree origin/main HEAD` rc 0, tree 0b5cafa80): rc 0, `TOTAL: 0 error(s) across 1 file(s)`, no error lines (ev/brief_lint.txt).
- Every done group's resume.commit is an ancestor of origin/main: 144 done groups, 0 NOT-ON-MAIN (ev/done_check.txt; 11 done groups without a commit are unchanged from main). The 8 resume.pr values this batch writes (2909 2883 2853 2882 2894 2876 2905 2900) are MERGED with mergeCommit equal to resume.commit (ev/prs.txt); R10-FLOW-ROSTER-FREEZE's 71fe1f7fc is #2903's merge.
- Proposal carries cite ACCEPT rulings on main: P223 (s6-batch44), P227 P228 P229 P231 (s6-batch45), P233 P234 (s6-batch46), P236 (s6-batch48) -- each "Verdict: ACCEPT narrowed" on origin/main (ev/carry_triage.txt).
  Not on main: R10-FLOW-BOARD's V149 carry cites "ruled DEFER to this route in s6-batch47"; s6-batch47.md exists only on open PR #2906 (head verdict line: DEFER, owned by the red-check root-cause route on #2883). It is a DEFER, not an ACCEPT, and unmerged; batches 49-51 none cited here.
- Two live destinations: no issue gains a second live group from this diff except umbrella #2505 (adds R10-ORCH-ROSTER-SCHEMA by its reopen; #2505 already spans 5 live groups on main); #2389, #2428, #2715 each lose live groups (ev/dup.txt vs ev/dup_main.txt). #2895 and #2907 have one group each.
  Cross-PR hazard, not this PR's to fix: #2896 at its head 73b1b4048 still adds dev/programme/carries/carry-2733.json with the two items this batch moves into R10-ORCH-ROSTER-SCHEMA; if #2896 merges without dropping it, #2733's two items have two destinations. #2896's reviewer owns that.
- R10-FRICTION-FIXER-MD and R10-FRICTION-CLAIM-FALSE briefs resolve: dev/governance/roles/fixer.md, dev/audit/rca/, tools/policy/policy_lint.mjs, tools/policy/rules_sync.mjs, dev/governance/config/policy_budgets.json, .claude/hooks/stop-selfcheck.sh (which does name tools/audit/briefs/fixer.md once), tools/ci/gate.py all exist; #2895 and #2907 OPEN with the stated titles.
- Body figure `212 215 3 0 25` re-derived against origin/main at the head (ev/groupdiff.txt).

## Advisories

- R10-TRIAGE-S6 is set done (05c60458a) while its own carry says resume.pr tracks the currently open batch PR; #2906 (batch 47) is open now, so it is unwired again -- the gap the group was registered to close. Its next_step text ("review the re-cut head of #2900") is stale.
- Draft: the PR is a draft (isDraft true); it is not ready -- the six set-stage ops above are owed first.
- CI at the head: prelude in_progress, 2 success, 1 skipped (ev/checkruns.txt); no red to answer. Not a merge verdict, so the CI wait is moot.
- No mutation proof / finder's harness applies (roster state only); VERSION, manifest and notes heading untouched (diff touches the roster and delivery/2914.md only).
