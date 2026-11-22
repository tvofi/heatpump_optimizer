# BLOCKED: r11-arch-fabric-learner (fixer), second fire

Question: The fabric cut still waits on R11-SEAM-learners, which is pull request #3835, open and a draft at 074f8741ca, not on `origin/main` (8ef450936a). Is this fixer re-fired when #3835 merges, as inbox command 1 says, or released to cut against #3835's head now?

This file names no `body_push: REFUSED` line and no kept body because none exists: no body was written and `body_push.sh` was not run. The block is the approved design's own ordering, not a refusal of a pushed result, so `cloud_relay.sh`'s carry-fold arm has nothing to fold.

## Why the block was not cleared

- Approved design 221c246ece section 7: "the fixer waits on `R11-SEAM-learners`", and its step-9 revalidation re-runs the arm "at the predecessor's merge"; its edits "are exact-text and stop on a moved anchor".
- Inbox command 1 (`refs/heads/inbox/r11-arch-fabric-learner` at 8c807cee91): "wait. ... You are re-fired from main after the learners PR merges; run the arm first."
- The dependency is in the code, not only the plan. #3835 changes lines inside two of the methods the design cuts, and replaces the freeze predicate the design says the coordinator asks "wherever ADR-008 puts the predicate". Rule: each `-` line of `git diff -U0 608c95decc 074f8741ca -- custom_components/heatpump_optimizer/coordinator.py` mapped to its innermost enclosing `def` at 608c95decc. It returns `_fold_internal_gains` (6 lines), `_async_learn_house_heat_loss` (1) and `_learning_frozen` (78) among nineteen functions. Null control: the same rule returns none of `_async_learn_buffer_cooling`, `_reanchor_house_heat_loss_scale`, `_heat_loss_anchors`, `_close_fabric_interval`, so it is not matching every learner method.
- `git merge-base --is-ancestor 074f8741ca origin/main` and the same for `handoff/r11-seam-learners` at 6a4b37067e both exit 1; that handoff head moved on 2026-11-22, so #3835's coordinator text is not final.

A cut built at 8ef450936a would move text #3835 rewrites, and its arm reading (design `## Figures`, F = 48) would describe a tree that does not survive the predecessor's merge.

## What this ref carries: the #3795 remainder, built and not handed off

`price_model.py` is in neither #3835's diff nor the fabric cut, so the carry was built here. It is not on `handoff/r11-arch-fabric-learner`: design fixer note 3 lands the group as one pull request, so no handoff or body ref was pushed.

- 29692afa83 the failing test (`tests/features.py`, six `#3795` checks). At 8ef450936a three fail: the constant, the window+N fold, the prune on load. Three pass there as controls: no day is re-folded, exactly a window is kept whole, a 90-day list from the previous release loads whole.
- 05e00fb4ce the fix: `_newest_days` bounds both sets to `DAYS_SEEN_RETENTION` after a fold that learned and on `restore`; `store_payload` reads the same function.
- Mutation, ten mutants of the fix's lines against the six checks run as a block extracted verbatim from `tests/features.py`: all ten killed (each prune in `fold`, the `if learned` predicate, each prune in `restore`, newest to oldest, the constant at 89 and at 91, `_newest_days` as the identity, the payload unbounded).
- Finder's probe `dev/audit/rounds/round11/sweep/N-unbounded-retention/D14/retention/probe_price_days.py` (sha1 929db15f6c): `retained_keys_slope` 2.00 keys/day at 8ef450936a, 0.00 at 05e00fb4ce; its `--null` arm (a restart per day) reads 0.00 at 8ef450936a.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget touched. `python3 tools/audit/archscore/score.py --diff 8ef450936a`: `Architecture score: dS +0.0000 NULL`.
- Not run: `tools/pr/prepr.sh` (the group gets one, at its whole head) and the fabric arm.

## Owed by the next fire

- Delete this file before the handoff: it is an unclassified tracked file.
- Residual of the carry, undecided: a complete day older than every retained day, offered to a full set, is folded, pruned at once and folded again on the next refresh. A price refresh carries today and tomorrow, so no production caller offers one; before this change the same day was folded once per restart. Carry: R11-ARCH-fabric-learner
- #3795 stays open after this group: its four `HistorySource` instances belong to R11-SEAM-card, so the body closes the remainder named here, not the issue.
