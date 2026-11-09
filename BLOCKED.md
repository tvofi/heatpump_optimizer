# BLOCKED: r10-process-slim (carry re-route for #3245)

## Done

- Steps 1 and 2: the head is c09a9acb7a7d5806c5db8881404ebd808a23daf0, with no code change. BODY.md (this commit) moves item ada60feb's marker to `Carry: R10-CLOSEOUT-INSTRUMENTS`, and its `## Head` note says so. Nothing else in the body changed. The precondition holds at main f365ce75: `git grep -c -- '--require-rows' origin/main -- tools/release/stamp.py` prints 8.
- Step 3: `git merge-tree --write-tree origin/main HEAD` exits 0, so no merge was made.
- Step 4: `tools/pr/prepr.sh` exits 0 at c09a9acb, and the receipt is written. Its carry line reads `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster d9393b486`.
- Step 5, first half: c09a9acb was pushed to handoff/r10-process-slim (`b5ddb2a57..c09a9acb7`). The pull request head has therefore moved.

## The refusal (step 5, body_push.sh), verbatim

    ref_privacy: REFUSE: unnumbered-email in the author email of 343a05219ecf would publish this host or a tool's attribution; nothing pushed
    ref_privacy: pin the seat identity, then re-author the commits: `git -c user.name=tvofi -c user.email=70032254+tvofi@users.noreply.github.com commit ...`, or `git commit --author='tvofi <70032254+tvofi@users.noreply.github.com>'`, or for a worktree `git config extensions.worktreeConfig true && git config --worktree user.email 70032254+tvofi@users.noreply.github.com` (a plain `git config` there writes the shared repo config); then `git rebase --exec 'git commit --amend --no-edit --reset-author' <base>`.
    body_push: a commit of handoff/r10-process-slim fails the push guard (above); re-author it, push the code again, then the body

343a05219 (`Merge remote-tracking branch 'origin/main' into fix/r10-process-slim`) is authored `seat <seat@users.noreply.github.com>`. So are at least nine more commits in merge-base..c09a9acb: b64ad5417, bd7de9b50, e86929252, 4715c0867, 9f4ecd399, 0d59fc797, 90bba85ad, 59c39580c, 0108578bd. They are not new. Every earlier head already contains 343a05219: 491177c4, f5af5b51 (the head holding the merge verdict) and b5ddb2a5 (the previous handoff).

## Why this seat stopped

The remedy is to rebase and re-author those commits. That rewrites the PR's whole history, including the head the merge verdict carries from, and the addendum does not name this refusal. The orchestrator decides: re-author (a new history, so the merge verdict and the budget-raise approval have to be re-earned), or body_push the body by another route. The body to push is BODY.md on this commit.

Expected red at c09a9acb: budget-raise-gate, until the orchestrator approves at that head.
