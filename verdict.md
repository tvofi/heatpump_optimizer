Fix review: merge 2108fcb09ef16a53119dedb8b731bd89f0fea0ad

Round 3. Group: none (as rounds 1-2: no roster entry for r10-openpr-row-push); reviewed against the PR body.
Measured at head 2108fcb09ef16a53119dedb8b731bd89f0fea0ad (ev/HEAD.txt); the PR head was still that sha when this verdict was written (ev/head-recheck.txt). Merge base 22615537a = origin/main; dev/governance/roles/ is the same at the merge base and origin/main (empty diff).

## Round-2 blocking item: resolved

RESULT r2-item1 class-open: the body's rule returns 43 lines at this head (ev/class-search.txt: ci_predict_replay 1, cloud_relay 2, handoff_push 2, pr_args 6, remerge_main 1, update_pr 3, app_approve 24, app_push 1, prepr 3), the same per-file counts the body gives. The body now dispositions every line, `ci_predict_replay.sh:47` included (self-created detached scratch worktree `$scratch/wt-$sha`, holds no branch, moves no ref; outside the class). The line numbers it cites for update_pr.sh (:40 detach, :43 remove, :44 -B) and ci_predict_replay.sh:47 match the tree. I agree with the disposition; it is the body's now, not mine.
RESULT r2 non-blocking: the body quotes `113 line(s) added since ... judged`; at this head `ref_privacy --check` prints `19 file(s) with a push site, 9 guarded, 113 line(s) added since 22615537a497 judged, 0 refused`, rc 0 (ev/ref-privacy-head.txt). Matches.

## The head's main merge (resolution delta)

RESULT delta: the authored three-dot diff at this head (22615537a...2108fcb) has exactly the same +/- lines as round 2's (289426c1f...085a4caf): 0 differing lines (ev/delta-r2-r3.txt). 6 files, +136/-37 (ev/diffstat.txt).
RESULT INSTRUMENTS.md, both sides (ev/instruments-main-change.txt, ev/instruments-diff.txt): e958d53bc's resolution keeps main's advisory-cap text verbatim ("The soft cap gates only dispatching a new roster group, and never refuses opening or updating ... `pr_cap.py info` ... still opens"), and the PR's row-lock sentence follows it ("It holds the branch's `upd-<branch>.lock` from before its worktree to its second push, so a concurrent `update_pr.sh` is BUSY (75) ..."). main's other hunks (cloud_relay "which the soft cap never refuses", the WIP level line, pr_cap.py, proof_watch --mode owner) are untouched by the PR. The PR's own three hunks (cloud_relay BUSY wording, pr_args `pr_branch_lock`, update_pr's unpushed refusal) read correctly against main's text. No stale `HPO_OPEN_PR_CAP` refusal wording survives in the PR's lines.
RESULT merge: `git merge-tree --write-tree origin/main 2108fcb...` exit 0, tree 9b0322865 (ev/merge-tree.txt). No conflict.

## Measured at this head

RESULT selftest-head: `delivery_row self-test: 5 checks, 0 failed`, `pr_args self-test: 60 checks, 0 failed`, rc 0 (ev/selftest-head.txt).
RESULT selftest-main(22615537a): `pr_args self-test: 54 checks, 0 failed` (ev/selftest-22615537a.txt). The diff adds 6 arms, as the body says.
RESULT selftest-codehead(d901186ff): `62 checks, 0 failed` (ev/selftest-d901186ff.txt) -- matches the body's figure, which the body states was taken at d901186ff's tree with main at 3688cf259. The body's absolute 62/56 do not hold at this head (60/54): main's #2525 (wip-cap) removed 2 cap checks from the self-test. The diff-attributable +6, 0 failed, holds. Not blocking: the body names the tree its figures came from and the move is main's, not the authored diff's.
RESULT null-control (22615537a + head's pr_args.sh): `pr_args self-test: 60 checks, 4 failed`, the four FAILs exactly the ones the body names (ev/null-control.txt).
RESULT my mutants on production lines, full self-test each (ev/mutant-*.diff, ev/mutant-*.txt):
  A delete open_pr.sh:33 (`pr_branch_lock ... # mut:oplock`) -> 1 failed (race arm)
  B delete update_pr.sh:39 (`... # mut:unpushed`) -> 2 failed (oplock arm, unpushed arm)
  C both -> 3 failed
  All killed. Round 1's D (differently named lock) and E (inverted ancestry) carry: the authored diff is unchanged.
RESULT structure: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
RESULT carry: `carry_audit.py check --body` on the current body: `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry-audit.txt). Forward-carry none; nothing in the diff changes a later stage's brief.
RESULT untouched: VERSION, manifest, RELEASE_NOTES, claim files, *_budgets.json, closures.json absent from the three-dot diff (ev/untouched.txt).
RESULT head-in-body: the body names 2108fcb09ef16a53119dedb8b731bd89f0fea0ad as the head, code heads e958d53bc and d901186ff. Confirmed (git log).
RESULT CI (commit check-runs API, ev/check-runs.tsv): every concluded run is success/skipped/neutral except nightly-status (failure), which grades main; this diff (tools/audit/seat/* and delivery/2560.md) does not reach what it reads -- not this PR's. instrument-self-tests, pr-contract (both runs), closure-scope, mutation, structure-bearing fast (3.14), arch-score: success. Still running when read: Analyze (python), coverage. The body's ## Red checks answers both earlier reds (instrument-self-tests, pr-contract) with a cheaper detector and its cost.
Harness: no committed finder harness (as rounds 1-2); the finding's evidence is the reflogs and lock files. The race arm is the fixer's own instrument, disclosed; I measured with it plus my own production-line mutants.
Not re-run: archscore (authored diff unchanged since round 1, where it read dS +0.0000; CI arch-score green on this head), entities.py (closure-scope green).

bus-nonce: 6abf0de1f258dffa046f06ddd148adc0
