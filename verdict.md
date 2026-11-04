Fix review: blocked b195da4715d4b160e9e638d648e73603c7df59a4 class-open: worktree_gc.sh class B removes a detached worktree whose HEAD moved after the read, losing the commit

bus-nonce: f0e4e8db0594c9ed9d7338ff33a2a285

## Round

Round 3 (delta review, started from scratch) of #3085 at head b195da4715d4b160e9e638d648e73603c7df59a4. Rounds 1 and 2 blocked class-open; a fourth round owes a re-cut under `fixer.md`, not a repair. `dev/governance/roles/` has no diff between the merge base and origin/main, so the contract is current.

## Block

The class this PR names is "a delete with no lease removes something that moved after the read, so a commit made after the read is lost". It is still open at a site in `tools/audit/worktree_gc.sh`, a file this PR modifies (carry 4 adds the `on-remote` arm on this path):

- `classify()` class B (detached worktrees: the merged-ancestor path and the new `on-remote` path) calls `remove_worktree` -> `git worktree remove --force "$1"` after the read of `$head`, with no lease. A detached worktree's HEAD is the only ref holding a commit made on it. A seat that commits there between the read and the remove loses that commit, because nothing references it any more.
- The body's class enumeration covers this site wrongly. It says `worktree_gc.sh remove_worktree's worktree remove --force: no ref is deleted. The branch ref and its commits survive the removal`. That holds for class A only. Class B has no branch ref, and the worktree's own HEAD is deleted with it.
- Measured with my own harness, `ev/wtgc-detached-race.sh`. It is the round-2 finder's `wtgc-race.sh` (sha1 0fe381af) with the worktree detached at a strict ancestor of origin/main, its mtimes aged past every age guard, and the same `worktree remove` git-stub race. At the head: race arm `RESULT race=1 detached-moved-head-lost=1`, null arm `RESULT race=0 detached-moved-head-lost=0`. At the merge base c3a279e3 the result is the same (pre-existing, as class A's `branch -D` was in round 2). Output: `ev/wtgc-detached-race.txt`.
- The same shape, read from the code and not separately measured: `closeout.py step_local` checks `_unpushed` and then runs `worktree remove --force` on every worktree under the seat roots. For a detached worktree, that is the same unleased removal.
- A repair that closes the race, not one that only narrows it: before removing, delete the worktree's HEAD with its old value, `git -C "$wt" update-ref --no-deref -d HEAD "$head"`, which is atomic in git's ref transaction just as class A's lease is. A HEAD that moved refuses, and the worktree is kept. Re-reading HEAD just before the remove only narrows the window. The fixer chooses the mechanism; the block is the open site.

## Findings

- The PR body carries a duplicated block. The `## Head` section repeats the round-1/round-2 repair paragraphs after a broken heading (``## Mutation proof`), and carry 7 is the line above.``), and a second `92b159d7...` paragraph follows that block. pr-contract passed on it (run 126491555702), but a reader sees two `## Head` accounts. Repair it in the next body. Carry: R10-CLOSEOUT-CLEANUP

## Evidence

- Head reviewed: b195da4715d4b160e9e638d648e73603c7df59a4. The live PR head and `refs/heads/fix/r10-closeout-cleanup` were still this SHA when the verdict was written (`ev/merge.txt`).
- Round-2 finder's harness (`ev/finder-r2-wtgc-race.sh`, sha1 0fe381af81201c7b2d86a7b0ed28e14a5b5cf748) at both ends (`ev/wtgc-race.txt`). At 7813b422: race `RESULT race=1 moved-tip-deleted-unpushed=1`, null `=0`. At the head: race `FAILED to delete branch fix/merged`, branch kept at the moved tip, `RESULT race=1 moved-tip-deleted-unpushed=0`; null `=0`, with the branch deleted. Class A is closed.
- Round-1 finder's harness (`ev/finder-r1-lease-race.py`, sha1 1bd5a9518656b7b017cc6860da51efbaf2457aa6, from verdict/3085 at 4c0fc0af), in `ev/lease-race.txt`. At 7f95f908: `RESULT moved-tip-deleted-untagged=1`. At the head: `delete-FAILED` (atomic lease refused), `fix/x` survives at its moved tip, `RESULT moved-tip-deleted-untagged=0`. The push arm's concurrent-move case is refused and the ref is left intact.
- The scout's enumeration of every production delete site in prune_refs.py, closeout.py, worktree_gc.sh and ref_privacy.py at the head matches the body's list. The leased sites are `apply_plan_push` (lease plus `--atomic`), `apply_plan` (read-and-compare before the REST DELETE, which narrows the race but cannot close it, as the body says), `closeout.delete_local_branch` (`update-ref -d <ref> <sha>`) and worktree_gc class A (`update-ref -d ... "$head"`). The enumeration missed `worktree remove --force` on detached worktrees, which is the block above. `git fetch --prune` and the `+refs/heads/*` fetch rewrite remote-tracking mirrors only, so they are out of class.
- Mutation proof, re-run at the head with the body's command (`ev/mutants.txt`): M0 `0 seat step(s) red`. All 18 mutants are KILLED, including `worktree_gc-4` (`95 checks, 3 failed`), `prune_refs-7..10` and `closeout-3`. `RESULT survivors=0`, rc 0, and the worktree is clean afterwards. None of the mutants touches class B, so this proof says nothing about the block.
- CI: `merge_train.py classify b195da47... --pr 3085` returned `GREEN b195da4715d4b160e9e638d648e73603c7df59a4 pending: none red: none`, rc 0 (`ev/classify.txt`). Check-runs read through the API, every page, 68 runs (`ev/checks.tsv`). Concluded reds:
  - `pr-contract` at 08:55 and 08:57: superseded by the 09:12 success, which ran after the last red concluded.
  - `tests / nightly-status`: main's nightly CPU-ratio failure, named and answered in `## Red checks`.
  - All three `gate` runs are success.
- Merge: `git merge-tree --write-tree origin/main(fad43b04) <head>` gives rc 0, with `LEDGER-MERGE: resolved tests/closures.json`.
- Protected files: VERSION, the manifest, RELEASE_NOTES.md, both claim files and every `*_budgets.json` are untouched in the three-dot diff.
- `python3 tests/structure.py` passes (`STRUCTURE RATCHET PASSED`, rc 0) with no budget raise.
- Packet `carry_audit` at the head: 1 routed (#2727). Delivery row `dev/programme/delivery/3085.md` is in the three-dot diff.
- Not re-derived: the self-test counts (95/74/26) and the scoped-gate MODE line. CI's `instrument-self-tests` and `gate` are green at this head and are cited instead.
