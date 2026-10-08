Fix review: blocked 6b1d0c466311cdd810bb85db0994d3b146aef196 skip-abusable: --recarry skips prepr for a parent 2 that is an ancestor of origin/main but on no main tree (side-branch commit), and instrument-self-tests is red at this head with the body's Red checks saying none

bus-nonce: dd7507415946f68cd7049cc1420f9f9e
seat: review-2069 (round 1)
head measured: 6b1d0c466311cdd810bb85db0994d3b146aef196 (PR body ## Head names it; live head re-read before posting)

## RESULT lines (reviewer's own harness, evidence/attack_p2_side.sh, driving the production recarry_verdict extracted from tools/pr/app_push.sh at this head against real git)

RESULT attack=p2-side-branch rc=0 -> prepr SKIPPED, and HEAD carries evil.py, which no origin/main tree has (main tree evil.py: 0; EVIL on first-parent chain: 0; EVIL ancestor of origin/main: yes)
RESULT control=honest-main-merge rc=0 -> SKIPPED (correct)
RESULT attack=extra-commit-under-p1 rc=1 (parent 1 not the live head)
RESULT attack=swapped-parents rc=1
RESULT attack=strategy-ours (evil merge) rc=1 (tree != merge-tree)
RESULT attack=body-trailing-space rc=1; body-leading-newline rc=1
RESULT attack=body-crlf rc=0 -- harmless: (c) and the PATCH both read the file in universal-newline mode, so the bytes sent equal the bytes compared
RESULT attack=listing-empty / [] / error-json / no-body-key rc=1 (fail closed, prepr runs)
RESULT attack=fetch-fails rc=1 (fail closed)
Perturbation: replacing the merge-base --is-ancestor test with first-parent membership (evidence/app_push.firstparent.sh) flips p2-side-branch to rc=1 and leaves the honest control at rc=0 (evidence/attack_perturbed.txt). The harness moves under its own perturbation.

## Blocking 1: (a) is weaker than the owner's decision

Decision 6070202495: "the new commit is a merge whose parents are the live PR head and origin/main". The code tests `merge-base --is-ancestor p2 origin/main`. This repository merges with merge commits: origin/main reaches 5015 commits, only 1332 on its first-parent chain, so about 3683 side-branch commits (intermediate commits of merged PRs, including reverted mutation-proof commits) pass (a). Merging one of them into a live head whose base predates it lands its content, which was never a main state, with prepr skipped, and the RECARRY line then calls it "origin/main's <sha>". Fix: require p2 on origin/main's first-parent chain (`git rev-list --first-parent origin/main | grep -qx p2`), or p2 == the freshly fetched origin/main (a race then fails closed into prepr). Add a real-git self-test case for a side-branch p2.

## Blocking 2: step 11, a red gate check unanswered

instrument-self-tests completed failure at this head (job 113578428882): `throwaway_git: 1 raw git init or clone site(s) refused`, at tools/pr/app_push.sh:644 -- the new real-git fixture's rgit() init/clone. The body's Red checks says "none". (nightly-status is red too; not this PR's.) pr-contract was still queued when read.

## Checked and holding

- Parent-1 spoof, extra commits, swapped parents, evil merge (-s ours), conflicted-then-resolved merge: all refuse (my harness plus the PR's own real-git cases).
- Race on the PR head: the push is a plain non-force `git push <url> <br>`; a head moved or force-pushed after the listing read makes M non-fast-forward, so the push is refused.
- API read failure: the listing gh call dies before anything is minted; empty, error-shaped or body-less listings refuse the skip and run prepr.
- update_pr.sh, open_pr.sh, handoff_push.sh call app_push without --recarry; only remerge_main.sh passes it. A fix seat that types --recarry by hand gets prepr unless its HEAD is a pure merge -- the guard is the verdict, not the caller, which is the right design once (a) is tightened.
- Self-tests at head (local): app_push 86 checks 0 failed; merge_train 83 checks 0 failed.

## The (c) departure

Keeps (c)'s intent in the skip path: the only body difference is the script's note, H is HEAD and pr-contract re-checks that ## Head names it. Two defects in the note, non-blocking alone, fix with the above:
1. M is `rev-parse --short refs/remotes/origin/main` read BEFORE the verdict's fetch, not p2; the worktree shares refs with sibling seats, so M can name a main the merge does not contain, and pr-contract checks only H. Build M from p2.
2. On the RUNS path the note is still written, asserting "no resolution ... The reviewed code is unchanged" for a head the verdict has just found carries a resolution or extra commits. Write that sentence only on the SKIPPED path (or a neutral note on RUNS).
Also minor: the verdict reads HEAD, the note and the push re-read it; pin the verified sha and refuse if HEAD differs at push time.

Not run here (heavy, CI's): full suite, mutation table. No production line is removed by this diff for step 1; the mutation proof is my perturbation above.
Evidence: /Users/timmalmstrom/hpo-seats/review-2069/evidence
