Fix review: merge 4f3aa7edb38f9818e7ddb5ce2d411c67a35fe8db

bus-nonce: ebb3c580669be45df1dd4b15fcf60a64

## Round

First round (no earlier reviewed head). Reviewed from detached worktrees at 4f3aa7edb38f9818e7ddb5ce2d411c67a35fe8db, which is still `refs/pull/3664/head` (ev/HEAD.txt). The role contract has no change between the merge base and origin/main (the three-dot diff over dev/governance/roles/ is empty).

## Evidence

- CI: `merge_train.py classify 4f3aa7edb38f9818e7ddb5ce2d411c67a35fe8db --pr 3664` printed `GREEN 4f3aa7edb38f9818e7ddb5ce2d411c67a35fe8db pending: none red: none`, rc 0 (ev/classify.txt). The only red in the packet digest is `tests / nightly-status`. It is not in the `owed-reds` set (ev/owed-reds.txt), so it needs no answer and blocks nothing.
- Merge: `git merge-tree --write-tree origin/main <head>` exited 0 with tree c25fc1a9e0 and no conflict (ev/merge-tree.txt).
- Mutation proof (step 1), each mutant in its own worktree at the head:
  - `mut:dupkey` with the base key restored: `roster_sync self-test: 98 checks, 2 failed`. Same two rows as the body (ev/mut-dupkey.txt).
  - id arm deleted: 1 failed, the reworded-landing row (ev/mut-idarm.txt).
  - core arm deleted: 3 failed, the queued row and both markup rows (ev/mut-corearm.txt).
  - `mut:readers`: FAIL on the recorded-closure row and on the `tools/lib/**` row (ev/mut-readers.txt).
  - `mut:roundfetch` (the call replaced by `stale = None`): FAIL `predict with a body refreshes the round rosters and notes a failed refresh` (ev/mut-roundfetch.txt).
  - All five match the body.
- Unmutated head:
  - `ci_predict self-test: 0 failed`.
  - `roster_sync self-test: 98 checks, 0 failed`.
  - `roster_edit self-test: 311 checks, 0 failed`. Carry 3's control is the P409 row, which passes with the `update-ref` removed.
  - Logs: ev/head-*.txt.
- Carry 3's premise: every caller of `write_roster` runs `fetch_origin` immediately before it. The callers are `roster_edit.main` (roster_edit.py:1602 then 1610), `roster_queue.py`'s batch (:335 then :339) and `roster_sync` (:646 then :740). The race loop re-fetches at roster_edit.py:1364. `state_docs.py`'s `write_roster` is a separate local function.
- Carry 0, end to end (ev/carry0-*.txt), with the r10 roster ref set to f20f8b13a7 and a body carrying one item to `R11-OUTSIDE-SELF-SETTING-PUMP`:
  - main's `ci_predict.py`: `CARRY BAD ... is not a group of the roster`, rc 1, ref left at f20f8b13a7.
  - the head's: `no closures, fast, governance or instrument red predicted`, rc 0, ref moved to origin's tip 5e4fdcb7cd.
- Carry 4 census (ev/census.txt):
  - `wave-r10-groups.json`: `2466 0 58`, the same as the body.
  - `wave-r11-groups.json` at roster tip 5e4fdcb7cd: `471 0 9`. The body's `429 0 8` was taken at 0350a63e82, before the roster gained carries. The result has the same shape: 0 repeats under the base's key, some under the head's.
- Carry 2 reader counts at this head (ev/carry2-counts.txt): four of the five rows match the body. `roster_lib.py` gives 43 / 9 / 37 against the body's 42 / 9 / 36. The difference comes from main's merge (047ea3fddf to 4f3aa7edb3), which adds a `selftest_closures.json` entry that reads `roster_lib.py`. The fix does not cause it.
- Not re-derived: the 674 s / 1226 s step-replay wall times. They are heavy, host-dependent runs, and the forward-carry that cites them carries its own re-measure instruction.
- Forward-carry (step 10): body item 79b11b82 is on `R11-PRE-PARALLEL-PIPELINE` in `origin/handoff/audit-r10-roster` at 5e4fdcb7cd. It keeps its re-measure-at-own-merge-base precondition.
- Step 5: the diff touches five files. None of them is `VERSION`, the manifest or `RELEASE_NOTES.md`, and neither claim file is touched.
- Step 6: the carries are instrument fixes, each with a named enumerator or a single site. `finding_words` has no other caller doing comparisons, so no further dedup seam was found. Step 9: no finder's harness is named. The finding is the roster carry itself, and the self-test rows the PR adds are the fixer's instruments.
- Closing self-audit: `carry_audit.py check` over this verdict returned rc 0 with no item flagged. The PR body's own audit at the head is the packet's: `17 routed, 0 unrouted, 0 bad destination(s)`.

## Findings

none
