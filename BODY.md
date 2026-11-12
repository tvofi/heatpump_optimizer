open_pr.sh pushed a body whose generated figure block names the code head, so lint refused p1 after a main merge and always p2 (the row commit moves the head). It now runs figure_block.py refresh at each head it pushes, and a re-run after an open closed past p2 clears the left-over local branch and detached worktree.

Not cured, for the reviewer: the self-test stubs figure_block.py and the pusher's head check, and its stub pusher uses push -f; a real re-run starts from the code head and merges main afresh, so its first push may be non-fast-forward against the first run's branch on origin (app_push.sh has no force). That is outside this one-script change.

## Head

`95bf04a83cf16aab992410968deea3aaa3ca58e1`

## Mutation proof

Deleting the p2 refresh line (mut:opfig2) is refused at the row push, naming "figure-block scope-line names another head", and the PR is closed. Deleting the p1 refresh (mut:opfig1) is refused at the code push with nothing pushed. Deleting the leftover clear (mut:opclear) fails the re-run at git worktree add -b. All three are arms of `tools/audit/seat/pr_args.sh --self-test`.

## Null control

A body with no figure block opens as before and its row push prints `ROW-ONLY: prepr SKIPPED` (arm in the same self-test). The unmodified tree fails the figure-block arm at p1.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
