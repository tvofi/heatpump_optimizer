Fix review: blocked f8694ba2d73595da723f0de3ed78c3e05df78b3d ci-red: instrument-self-tests is red on this diff (ref_privacy --check refuses the new push site at tools/audit/seat/pr_args.sh:353) and pr-contract is red (carry_audit: both Forward-carry items unrouted), while the body says Red checks: none

Round 1 for this head. Group: none (no roster entry for topic r10-openpr-row-push); reviewed against the PR body.
Measured at head f8694ba2d73595da723f0de3ed78c3e05df78b3d (ev/HEAD.txt); refs/pull/2560/head still f8694ba2d73595da723f0de3ed78c3e05df78b3d when this verdict was written. Merge base 03b49e152 = origin/main; dev/governance/roles/ is unchanged between the base and origin/main.

## Blocking

1. **instrument-self-tests: failure** (check-run 119202734228, step 23 "Refuse a push that names the host, and an unregistered pusher"). Re-run locally at the head: `python3 -I tools/audit/seat/ref_privacy.py --check` prints
   `ref_privacy: REFUSE tools/audit/seat/pr_args.sh:353: a push site in a file PUSHERS does not name: guard it ... and register it, or register why not` and
   `ref_privacy --check at HEAD: 19 file(s) with a push site, 9 guarded, 111 line(s) added since 03b49e1521a2 judged, 1 refused` (ev/ref-privacy-head.txt).
   At the base worktree the same command prints `0 refused`. Line 353 is the stub `app_push.sh` heredoc this diff adds to the self-test (`git -C "$wt" push -q origin "$br"`). The fix is the fixer's: register `pr_args.sh` in `PUSHERS` with its reason (a self-test stub pushing to a scratch origin), or reshape the fixture so it is not a push site.
2. **pr-contract: failure** (both runs, 119202272281 and 119202779945): `carry_audit.py check --body` prints `UNROUTED body item 058090a8 (## Forward-carry)` and `UNROUTED body item 11c47230 (## Forward-carry)`, `CARRY-AUDIT: 2 finding item(s): 0 routed, 2 unrouted`. Reproduced locally (ev/carry-audit.txt, rc=1). `Carry: orchestrator` and `Carry: none` are not destinations the audit accepts (GROUP | #issue | O<n> | dismissed: <reason>). Step 10 also: the first item (#2547/#2548 rows unrepaired) has no stage it was written to.
3. **## Red checks says "none"** while the head has both reds above (step 11). Not posted as root-cause-unanswered because the head's workflows had not all concluded (Analyze, browser, closures, env-matrix, fast, coverage-ratchet, graders-head-copy still running at 11:52Z; ev/check-runs-final.tsv); the ci-red block stands on its own, and the re-pushed body owes the answer for whatever is red then.
   nightly-status is red too; it grades main and this diff does not reach what it reads -- not this PR's.

## What holds (verified, carries forward if only the above changes)

RESULT selftest-head: `pr_args self-test: 62 checks, 0 failed`, `delivery_row self-test: 5 checks, 0 failed` (ev/selftest-head.txt) -- matches the body.
RESULT selftest-main(03b49e152): `pr_args self-test: 56 checks, 0 failed` (ev/selftest-main.txt) -- matches the body's "56 on origin/main".
RESULT null-control (43f79c08b + head pr_args.sh): `62 checks, 4 failed`, the four exactly the ones the body names (ev/null-control.txt). The oplock+unpushed arm passes against the old scripts, i.e. the "is not the committed tip" defect reproduces there.
RESULT my mutants on production lines, full self-test each (ev/mutant-*.diff, ev/mutant-*.txt):
  A delete open_pr.sh mut:oplock line -> 1 failed (race arm)
  B delete update_pr.sh mut:unpushed line -> 2 failed (oplock arm, unpushed arm)
  C both -> 3 failed
  D open_pr takes a differently named lock (open-<br>.lock, not shared with update_pr) -> 1 failed (race arm)
  E unpushed check direction inverted (is-ancestor origin/BR HEAD) -> 2 failed
  All killed; no vacuous arm found.
RESULT lock path: open_pr's `$(dirname $D)/upd-${BR//\//-}.lock` = $STATE/pr/upd-<br>.lock = update_pr's $WT.lock, taken after the -pr rename of BR; open_pr has no EXIT trap of its own for pr_branch_lock's to clobber.
RESULT structure: `STRUCTURE RATCHET PASSED` (ev/structure.txt). archscore: `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). Both match the body.
RESULT VERSION / manifest / notes heading / claim files / budgets / closures.json untouched (ev/untouched.txt; CI pr-contract also prints "no version edit").
RESULT merge: `git merge-tree --write-tree origin/main f8694ba2d73595da723f0de3ed78c3e05df78b3d` exit 0, no conflict (ev/merge-tree.txt).
RESULT class search: the body's grep returns 43 lines (ev/class-search.txt). Beyond the body's dispositions (update_pr closed; handoff_push, remerge_main, cloud_relay fixtures) it returns: app_push.sh:827 and prepr.sh:1877/1984/2098 (self-test throwaway clones, inside the body's stated self-test exclusion), app_approve.sh fixtures (excluded), and tools/audit/seat/ci_predict_replay.sh:47, which the body does not disposition. My disposition, stated as mine: it removes a detached worktree it created itself one loop iteration earlier under its own scratch dir at a commit already on origin; it holds no branch and cannot drop another instrument's work, so it is outside the class. The re-pushed body should name it.
Harness: no committed finder harness; the finding's evidence is the reflogs and lock files in the body. The race arm in pr_args.sh's self-test is the fixer's own instrument (disclosed as such); I measured with it plus my own mutants above.
Not checked: entities.py locally (needs the CI python; tree file classification left to CI's closure-scope/entities, closure-scope green).

bus-nonce: 60c0cd20873ffadd8b9124823443ac67
