Fix review: blocked c24be17f8cd37cfd46f7fd2cad354c15db74d15a ruling-unsound: the handoff_push.sh detach site breaks handoff_push.sh's own update arm, which reuses that worktree and pushes from it

bus-nonce: 419b36e8e7d1804e7e6b59f6574efc6e

Round 2 (round 1 blocked ruling-unsound on the detach inside app_push.sh). A detach is still a re-cut of the ruling, not of code; round 3 would still be a repair.

## Block

The re-cut fixes round 1's defect for the two-push open sequence: "the detach is the opener's, once, after its last push". But it judges "last push" only inside one run, and handoff_push.sh's worktree is used again by later runs. origin/main `tools/audit/seat/handoff_push.sh` line 166 (`if [ -d "$WT" ] && gh pr view "$BR" ...`) is the update arm. It reuses the same sibling `$WT` the ruling detaches after line 212. It runs `git reset -q --hard "origin/$BR"`, then merges the new code head and main, then `ensure_row`, then `push_app 2` (line 179, `mut:push-update`). On a detached worktree, `reset --hard` moves only HEAD, so those merge commits land on a detached HEAD while `refs/heads/$BR` stays at the old pushed sha. app_push.sh lines 482-484 then die: "worktree HEAD ... is not the committed tip". This is the same mechanism the ruling's own Binding paragraph uses to rule out a detach after p1. Repro in `ev/repro_update_after_detach.txt`: `RESULT update-after-detach app_push-gate=REFUSE`. So carrying the ruling as written turns every handoff_push.sh update of an open PR into a refusal. The ruling must name the update arm, either as reattaching first (`git -C "$WT" checkout -q -B "$BR" "origin/$BR"` before the reset) or as a site with its own detach-after-push, plus a self-test arm for update-after-open. The same question has to be answered for each named site's next run. update_pr.sh and open_pr.sh are safe, because update_pr.sh removes and re-adds its `$WT` with `-B`, and open_pr.sh adds a fresh worktree with `-b`. The ruling should say so.

## Findings

- The ruling's "Why not --free-holders" says detaching a worktree outside `$HPO_STATE_DIR/pr/` is unsafe because another seat may be using it. It does not mention that origin/main `merge_train.py` already has `--free-holders` (`free_holder`/`freeable`, lines 805-824). That code detaches any holder that is clean and at origin/<br>, with no prefix restriction. Either that existing mechanism is unsafe by the ruling's own argument, or the argument is overstated. The re-cut should engage with it (reuse its `freeable` predicate as the shared helper, or say why not). Carry: R10-FLY-OPENPR-ATOMIC
- The update_pr.sh site says its `upd-<branch>` worktree "is the holder detached by hand for #2735 and #2738". The cited ledger lines (99, 102) name triage worktree holders for #2734/#2735, not an update_pr.sh holder for #2738. That clause has no citation, and I could not re-derive it from the tree. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence

- Head reviewed: c24be17f8cd37cfd46f7fd2cad354c15db74d15a (`ev/HEAD.txt`). It matches the body's `## Head`. Merge base e97f5749b. The diff touches 2 files, 18 lines, all under `dev/programme/` (INERT): `delivery/2738.md` and `triage/s6-batch6.md`.
- `git merge-tree --write-tree origin/main <head>` exits 0, tree c3c76836b8 (clean, no claim files touched).
- These figures re-derived at origin/main (`ev/figures.txt`): update_pr.sh line 50 "checked out elsewhere", sweep lines 45-48, final push line 77, `$WT` under `$P` = state/pr; open_pr.sh `_push` lines 55, 58, 70, 71; handoff_push.sh push_app open line 198, commit_row line 204, row push line 212; app_push.sh committed-tip gate lines 482-484 (the ruling cites 481-484; 481 is the `head=` read, which is fine).
- The site census omits handoff_push.sh line 179 (`push_app 2`, the update arm), which `git grep 'push_app'` returns. That omission is the Block.
- I could not re-derive the instances. seat-ledger.md lines 99/102 and proposals.md line 89 live out of tree on the orchestrator's machine.
- Policy wording: the file is a triage ruling record and quotes no owner words. No tvofi quote was cited, so there was nothing to check against.
- CI at this head, from the check-runs API: no run is red. fast, typing, closures, coverage and browser are queued, and instrument-self-tests and prelude are in progress. All others that have concluded are success or skipped. No red check is owed an answer.
- No mutation proof applies (no code lines). The null control (`ruling_verdict` on P99) is not re-run; it does not bear on the block.
