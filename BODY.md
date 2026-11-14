R10-CLOSEOUT-CLEANUP: `.claude/hooks/pre-bash.sh` line 321, a comment in the hook's self-test block, cited `verdict/3294` bare. `tools/audit/seat/closeout.py --apply` step 1 refuses while a policy or tool path cites, bare, a ref that closeout archives and deletes, and this was the one such citation outside the rosters (RETARGET.md section 4 of the closeout dry run). The comment now reads `PR 3294's fix review`: it names no ref and keeps its sentence true. Nothing else changes. The file is code-owned (`/.claude/hooks/ @tvofi`), so the merge needs the owner's approving review (or the declared mandate approval). The change is comment-only, with no behaviour change and no budget touched.

## Head

36e4fd30689af5eae682e0e28ba49c33c7d23b22

## Mutation proof

n/a: comment-only change, no executable line moved, so there is nothing to break. `bash -n .claude/hooks/pre-bash.sh` is clean and the hook's own `--self-test` prints `46 passed, 0 failed` both before and after the edit.

## Null control

n/a: the unmodified tree prints the same `46 passed, 0 failed` from `.claude/hooks/pre-bash.sh --self-test`; the only difference is line 321 matching the closeout citation pattern (`verdict/3294`), which the edited line no longer does.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
