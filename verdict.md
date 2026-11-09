Fix review: merge aff9f1393aec11bc0f5fc745d34a9161c09b695a

bus-nonce: 461575119b6131a79a5b3f5cbe2218ab

Round: first review by this seat of head aff9f1393aec11bc0f5fc745d34a9161c09b695a. The body's reviewed-head 43136fbc differs only by main merges (review_carry printed FRESH-REVIEW; I therefore re-reviewed the whole three-dot diff at aff9f1393aec11bc0f5fc745d34a9161c09b695a, and none of the PR's 12 files is in the 43136fbc..aff9f1393aec11bc0f5fc745d34a9161c09b695a delta other than through main's own changes, with no conflict).

## Evidence

- Head measured: aff9f1393aec11bc0f5fc745d34a9161c09b695a, still the live pull/3304/head (ev/livehead.txt). `merge_train.py classify`: GREEN, pending none, red none (ev/classify.txt). `owed-reds` set (ev/owed-reds.txt) is all green; no red check owed.
- `git merge-tree --write-tree origin/main aff9f1393aec11bc0f5fc745d34a9161c09b695a`: rc 0, clean (ev/merge-tree.txt).
- Self-tests at the head, all 0 failed: roster_lib 80 checks, gate_priority 15, open_driver 86, orchestrator_tick 295, plan_page 67, merge_train 577, replan self-test 0 failed (ev/selftests.txt). The body's older counts are lower because main added checks since; I did not rebuild its figures, which are per-head snapshots.
- Mutants I ran myself, each KILLED: merge_train drain-hotfix and drain-outside terms; roster_lib is_hotfix `kind == bug` arm; gate_priority `rank <= 1` band; orchestrator_tick `group_for_pr` fork fallback; open_driver outside class arm (4 failed), hotfix set arm (1 failed), FENCED 2 to 0 (2 failed) (ev/mutants.txt, ev/od_mutants.txt). A first open_driver run showed SURVIVED only because I invoked open_driver_selftest.py directly, which prints nothing and exits 0; through `open_driver.py --self-test` it is killed.
- Enumeration rule from the body re-run (ev/enum.txt): outside the six owner files the hits are comments or provenance strings (agreement.mjs, gh_comment.py, gate.py, sweep.py); agrees with the body.
- Three-dot diff touches no VERSION, manifest, RELEASE_NOTES, golden, claim file or budgets file (ev/prfiles.txt). No finder's harness named; the body discloses its one-off fixtures and tiers.py as its own. The live-roster count (9 open hotfix groups, 0 and 7 not-TIER_HOTFIX) I could not re-derive: tiers.py is not in the tree and the roster ref moves.
- Red checks: the three earlier-head reds in the body are answered; the head's required checks are all green.

## Findings

- Follow-up: merge_train.py:2383 and :3765 (`self.critical`) decide whether the record sweep waits for an entry; hotfix and outside entries take the drain-order rank but not the sweep skip, so they wait one record sweep a critical-path entry does not. Latency only, not an order; the body's enumeration rule did not cover it and the ruling speaks of priority in dispatch and merge order. Carry: dismissed: the sweep skip is P289's critical-path latency optimisation and no ordering changes, so extending it to hotfix and outside entries is a measured-wait question the owner has not raised
