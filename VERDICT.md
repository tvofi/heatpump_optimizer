Fix review: merge 70ef3055363512123e9e6f8e5632831830d31dbb

bus-nonce: 12e9aeddc3b15d25a9b99d0fee04ac13
pending-ci: gate

Round 3 of the review. It is a delta review over the reviewed head d712c2ba4a834afcb5d722468676d52ce3762681, whose verdict (verdict/3481, 1417dd0b1) blocked `ci-red` for one reason: main's tests/features.py charge-start-dip check. I measured head 70ef3055363512123e9e6f8e5632831830d31dbb, and it was still `refs/pull/3481/head` at 03:39Z.

## Evidence

- Setup:
  - `cloud-setup.sh --check` printed OK.
  - The role pack was rendered.
  - `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
  - The review packet was rendered (ev/review-packet.md). It refused only `introduced-red: unreadable` because instrument-self-tests was in progress at render time. Its `## Review scope` is delta. carry_audit at the head: 5 routed, 0 unrouted, 0 bad. figure_lint: 28 resolved, 0 not verified.
- The delta is main's content only:
  - 70ef30553 is one merge commit with parents d712c2ba and c987209cc, which is origin/main.
  - `git merge-tree --write-tree d712c2ba c987209c` gives tree 1e4713c4a0a1. That equals `70ef3055^{tree}`, so the merge was automatic and carries no branch-authored change (ev/review_carry.txt).
  - `tools/audit/seat/review_carry.py d712c2ba 70ef3055` prints `CARRY`: 0 of 1 branch-only commits are non-merge.
  - `git diff d712c2ba 70ef3055` touches 12 files (ev/delta-files.txt, ev/delta-stat.txt), the same 12 files and line counts as `git diff merge-base(d712c2ba,c987209c) c987209c`.
  - The production part is the v7.1.16 stamp's version strings: the manifest and the card's CARD_VERSION. VERSION, RELEASE_NOTES.md and the claim files' `claims-for` lines also came from main's stamp. None was authored by this branch. Nothing widens the review.
- Merge with main: `git merge-tree --write-tree origin/main 70ef3055` exits 0, and origin/main is c987209cc.
- The prior round's one finding is resolved:
  - main's charge-start-dip check in tests/features.py was repaired on main (#3578, c987209c) and is merged in.
  - `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/features.py` on a worktree at this head printed `1 of 5618 FEATURE CHECKS FAILED` (ev/features_head_summary.txt). The charge-start-dip check passes.
  - The one red is `_bootstrap drops the package directory so datetime is stdlib`. That is the copy/worktree path artifact the previous verdict recorded on every copy, including main's.
  - CI's `tests / fast (3.14)` was still in progress at 03:39Z.
- Every earlier code finding stays resolved as verdict/3481's Evidence recorded:
  - the own-group carries, now routed to R11-INTAKE-R10-RESIDUE;
  - the `## Head` statement;
  - the mutation proof w1, w2, t1, t2, with no survivor;
  - the seams-harness figures.
  No line of custom_components/ that this branch wrote changed in the delta, so those measurements hold at this head.
- Step 5: the three-dot diff `origin/main...70ef3055` leaves VERSION, the manifest version and the RELEASE_NOTES.md heading untouched. Their two-dot movement is main's stamp.
- CI at the head (step 11). `merge_train.py classify 70ef3055... --pr 3481` printed `WAIT ... pending: gate red: none` from 03:08Z to 03:39Z (ev/classify.log), so this verdict carries `pending-ci: gate`.
  - Success: arch-score, budget-raise-gate, typing, browser, briefs, closure-scope, env-matrix, policy-docs, wave-script, delivery-status, hassfest, validate-hacs and the three codeql lanes.
  - Still running: fast (3.14), replay, closures, coverage, arch-instrument, instrument-self-tests, mutation-pins (1) and (2).
- `tests / mutation` (job 132308321907) concluded failure, and it is in the `owed-reds` set (ev/owed-reds.txt).
  - Its log reads `MUTATION TABLE REFUSED -- 2306 unpinned site(s) against 2309 at the ratchet base c987209cc..., 7 of them added by this diff`.
  - The sites are coordinator.py:10703 GUARD_OFF, price_tiles.py:130 RETURN_DEL, price_tiles.py:146 GUARD_OFF, price_tiles.py:148 CMP_BOUND*2 and GUARD_OFF, and whatif.py:149 RETURN_DEL.
  - I reproduced it on this head's worktree: `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3`, rc 1, the same 6 lines (ev/mutation_table_head.txt).
  - That is this branch's code, from rounds 4–6 (`Rotation`, `whatif.state_for`). The delta did not add it: the same lane was red at d712c2ba.
  - So the body's statement that every site this diff adds is pinned, and that `ci_predict.py` lists no unpinned site, does not re-derive at this head. I did not re-derive it at the commits the body names.
  - By ci-autofix.md, the `mutation-pins` shards are the job that repairs this. Both were in progress at 03:39Z, so a bot commit pinning the killed sites, or a red naming survivors, is still to come.
  - No `root-cause-*` call is made: the head's workflows have not all concluded.
  - The relay posts this verdict only once classify reads GREEN at this exact head. It refuses on a red, which includes a pins shard naming a survivor, and on a moved head, which includes a bot pin commit.
- Not re-run, by CI citation: the gate, the mutation table's driver run, replay, the card checks.
