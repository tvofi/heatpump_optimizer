Fix review: blocked 3e6bf423086464ee6207f98adab18861e81871d4 class-open: train_add's start path queues a stopped train's spool and the new entry without drain_order, so add --priority runs the HOTFIX last

bus-nonce: d3460427e8c751fe7feefb59499a03a3

## Round

This is round 2. Round 1 is `refs/heads/verdict/3090`, at 41790e2b8. I reviewed from detached worktrees at 3e6bf423086464ee6207f98adab18861e81871d4 (the head) and at 41790e2b8 (the round-1 head). The fixer's handoff, 3e91443e5, is merged into this head. `git diff merge-base...origin/main -- dev/governance/roles/` touches only main's own edit to `fix-review.md` step 12 (`review_carry` wording), which does not change any step I apply here.

## Block

**class-open: the P312 rule ("the train drains its spool into the next batch priority entries first, then critical-path entries, then arrival order"; train.sh's header and `--priority`'s help) is enforced at one of the two places that turn the spool into a batch.**

The spool is read into a batch at two sites (`grep -n "spool_read(" merge_train.py`, production lines only):

- `Train.queue_take` (merge_train.py:3048). It drains a live train's spool through `drain_order`. Round 2 fixed it, and it is pinned.
- `train_add`'s start path (merge_train.py:1044 → 1076). With no live train, `queue = [entry] + spooled if front else spooled + [entry]` builds the new train's first batch from whatever a stopped train left spooled ("spooled entries stay for the next train", `queue_close`) plus the new entry. It never calls `drain_order`.

My harness `ev/start_path.py` covers the start path. A stopped train left `[#3 critical, #1]` in the spool, there is no live train, and the harness adds #4. The train would be launched over these queues:

- `--priority`: `start_queue=[3, 1, 4]`. `drain_order` of the same entries gives `[4, 3, 1]`. The HOTFIX runs **last**, behind the entries a stopped train left, which are exactly the ones whose train stopped.
- `--front`: `[4, 3, 1]`, the same as `drain_order`. This path is correct at this head.
- Null control, a plain add: `[3, 1, 4]`, the same as `drain_order`.

The body does not name this seam, the diff does not change it, and no self-test arm covers it. The repair is one line on the seam the fixer already owns: order the start queue with `t.drain_order(...)`. A fronted entry carries `front` and stays first. The fix also needs a self-test arm on the start path with a leftover spool and `--priority`.

## Findings

- The start path of `train_add` builds the new train's queue from leftover spool entries plus the new entry without `drain_order`. As a result, `add --priority` runs a HOTFIX last whenever a stopped train left entries spooled, and critical-path leftovers keep arrival order (Block). Carry: R10-FLY-TRAIN-DEFAULTS

## Evidence

- Head. `ev/HEAD.txt` holds 3e6bf423086464ee6207f98adab18861e81871d4. The PR's live head (`pull_request_read get`) was the same when I read it before writing, and the body's `## Head` names it.
- Block 1 of round 1 (front against drain) is settled. I re-ran the finder's harness, round 1's `ev/front_vs_drain.py`, at both ends (`ev/front_vs_drain.txt`):
  - Old head 41790e2b8: `spool_after_front [1, 3, 2]` and `drained [3, 1, 2]`.
  - This head: `spool_after_front [1, 3, 2]` and `drained [1, 3, 2]`, so the drain now matches the read-back.
  - Null control: `null_drained [1, 3, 2]` at both ends, so it is unchanged.
- The rule the fixer states. A fronted entry is marked `front` (by `spool_edit_locked` and by `train_add` for a new entry) and ranks in the `--priority` tier, ahead of critical-path entries. Ties are broken by spool order. This is stated in the `drain_order` docstring and in `instruments/merge_train.py.md`. It is coherent with P112's "FIRST in the next batch" on the live path.
- Ordering shapes on a live train, read-back against drain (`ev/shapes.py`, `ev/shapes.txt`, my own harness):
  - Two fronted (1, then 2): read-back `[2, 1, 3]`, drain `[2, 1, 3]`.
  - New `--front --priority`: read-back `[5, 3, 1, 2]`, drain `[5, 3, 1, 2]`.
  - Front then remove: read-back `[3, 2]`, drain `[3, 2]`.
  - New `--front` then front another: read-back `[2, 5, 3, 1]`, drain `[2, 5, 3, 1]`.
  - Null: read-back `[3, 1, 2]`, drain `[3, 1, 2]`.
  - Front 1, then a plain `add #5 --priority`: drain `[1, 5, 3, 2]` against spool `[1, 3, 2, 5]`. This is P312's stated reordering of a HOTFIX. A non-front add prints no read-back, so nothing printed is contradicted.
  - The only divergence I found is the start path, which is under Block.
- Block 2 of round 1 (mutants) is settled. I ran each mutant single-occurrence in a detached worktree at the head and restored it afterwards; `git status` was clean after the run. The harness is `ev/mut2.py`, which is round 1's `ev/mut.py` with the drain-key anchor re-pointed at the round-2 key plus three new `--front` mutants. Results are in `ev/own_mutants.txt`:
  - R1 priority key dropped from item: KILLED, rc=1 | merge_train self-test: 418 checks, 1 failed
  - R2 front not passed to train_add: KILLED, rc=1 | merge_train self-test: 418 checks, 1 failed
  - R3 --remove arm made front: KILLED, rc=1 | merge_train self-test: 418 checks, 2 failed
  - R4 spool entry drops priority key: KILLED, rc=1 | merge_train self-test: 418 checks, 1 failed
  - B1 drain key 0: KILLED, rc=1 | merge_train self-test: 418 checks, 5 failed
  - R5 critical before priority/front: KILLED, rc=1 | merge_train self-test: 418 checks, 3 failed
  - R6 --priority flag ignored: KILLED, rc=1 | merge_train self-test: 418 checks, 1 failed
  - F1 drain ignores front (round-1 key): KILLED, rc=1 | merge_train self-test: 418 checks, 2 failed
  - F2 spool_edit front marking dropped: KILLED, rc=1 | merge_train self-test: 418 checks, 2 failed
  - F3 train_add new-entry front marking dropped: KILLED, rc=1 | merge_train self-test: 418 checks, 1 failed
  - All of round 1's R1, R2, R4 and R6 are now killed, and R3 and R5 are still killed. Every mutant is killed, so no survivors remain.
- Unmutated head: `merge_train self-test: 418 checks, 0 failed` (`ev/figures.txt`).
- The body's figures, which the body says were measured at 17b38f7d9, re-taken at this head (`ev/figures.txt`):
  - `merge_train.py --self-test`: 418 checks, 0 failed. The body's 396 is the 17b38f7d9 figure and is disclosed as such.
  - `merge_pr.sh --self-test`: 22 checks, 0 failed.
  - `postmerge.py --self-test`: 16 checks, 0 failed.
  - `record_beat.py --self-test`: 16 checks, 0 failed.
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `policy_lint.mjs --budgets`: rc 0. standing-merge.md is at 36 of 37 lines and 504 of 507 tokens. nudge.md is at 115 of 115 lines and 3758 of 3814 tokens; the budget table lists it as `tools/audit/briefs/nudge.md`. Both are within cap with no raise (`ev/policy_budgets.txt`).
  - I did not re-run `tests/entities.py` or `tests/harness_headers.py` locally. CI's `tests / fast (3.14)` at this head concluded success.
- Merge. `git merge-tree --write-tree origin/main 3e6bf423086464ee6207f98adab18861e81871d4`, with origin/main at a568a2e12, gives rc 0 and tree 469e8d28f. Its stderr has `LEDGER-MERGE: resolved tests/closures.json` and no `MERGE-CLAIM: refused` (`ev/standing.txt`).
- The claim files are byte-identical to the merge base 1d28de993, so the branch claims nothing. They differ from origin/main only by main's own later commits (78dd34354, v7.1.1). VERSION, RELEASE_NOTES.md and the manifest are untouched in the three-dot diff. The delivery row `dev/programme/delivery/3090.md` is in the three-dot diff (`ev/standing.txt`).
- CI. `merge_train.py classify 3e6bf423086464ee6207f98adab18861e81871d4 --pr 3090` gives `GREEN ... pending: none red: none`, rc 0. I ran it from the origin/main a568a2e12 checkout, because the head's own copy refuses `--pr` with rc 2 (`ev/classify.txt`, `ev/standing.txt`).
- Red checks. All 55 check runs fit on one page of 100, and every one concluded success or skipped. None failed, was cancelled, timed out or needs action. That matches the body's `## Red checks: none` (`ev/check_runs.txt`).
- Approval. The body's `## Approval` still says the policy files standing-merge.md and nudge.md merge only on tvofi's approving review at the head, or under mandate 6329234399 scoped `all`, and that the seat claims none. This verdict is not that review.
- Harnesses. The finder's harness is round 1's `ev/front_vs_drain.py` and `ev/mut.py`. `ev/mut2.py`, `ev/shapes.py` and `ev/start_path.py` are my own, built for this round.
