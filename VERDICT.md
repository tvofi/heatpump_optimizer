Fix review: merge 4449ca654397321ff1a909704317d6eb174206b4

bus-nonce: f841ef18f3f24883d042cb70338a0436

## Evidence

Round 2, delta only, over the reviewed head 6bb827793e1fff355b73cc17dd267a46b6b2a254 (merge verdict at f14bb0aff7). Reviewed at 4449ca654397321ff1a909704317d6eb174206b4, merge base 99436a082c, from a detached worktree. dev/governance/roles/fix-review.md is unchanged between the two heads.

- Delta: two merges of origin/main (6c854c212d, 4449ca6543). No commit authored on the branch. review_carry.py prints FRESH-REVIEW only because of the merges (ev/review-carry.txt). The PR's own diff, three-dot, matches round 1 in 16 of its 17 files (ev/own-diff-compare.txt). The one that differs is .claude/workflows/audit-find.js. In it, the generated `CLASS_GUESS` and `FINDING_REPORT` class enum now carry main's new class ids. The branch's own change is the same `X0` alternative in each dimension/id/step/scope/harness pattern, and `DIMS` keeps `DX0`. The body's `## Head` section describes the conflict resolution the same way.
- Prior findings: round 1 blocked nothing; its one disclosed survivor (audit-verify.js:309 step-yield regex, equivalent) is in unchanged code.
- Checks at the head (ev/checks-head.txt): `fold_ledger.py check` 0 violations; `check_scopes.py --repo .` ok harness citations; `check-wave-script.mjs` 296 passed, 0 failed; `git merge-tree --write-tree` against origin/main e83a2c919f rc 0, only `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).
- CI: `merge_train.py classify 4449ca6543... --pr 3739` rc 4, APPROVAL-OWED only. The approval at 6bb827793e1f does not cover this head (ev/classify-log.txt). Packet digest: every other required context succeeded or was skipped. `gate` and `budget-raise-gate` are red only on the owed approval.
- Raises (0013), re-measured at the head (ev/budgets.txt): there are four. `corpus_tokens` 71212 -> 72206. `CLAUDE.md` files_tokens 3604 -> 3616. `tools/audit/briefs/COMMON.md` lines 114 -> 115. Its files_tokens 1691 -> 1715. `DX0.md` is a new entry (60 lines / 799 tokens), not a raise. Each per-file cap equals the head measurement exactly. The corpus measures ~72240 at the head against ~71405 at the base 99436a082c. The +835 is DX0.md 799 + CLAUDE.md 12 + COMMON.md 24, the same three files as round 1. Main's own +34 since then sits inside the 500 band.
- Raise justification judged: the body's `## Raise justification` names each row, the payments tried (brief 89/1241 -> 60/799, CLAUDE.md row cut from 24 to 12 tokens over the cap, COMMON.md sentence from two lines to one, a duplicated sentence replaced by a pointer) and `Architecture score: dS +0.0000 NULL`, in the form budget_raise_gate.py reads. The growth is a new owner-ruled dimension brief plus the index row CLAUDE.md's "named individually" rule requires and the COMMON.md owner-only sentence design P8 requires. Moving text elsewhere does not lower `corpus_tokens`. Cutting other rows would change other seats' obligations, outside this PR's scope. I found no architecture-improving payment the body missed.
- Steps 4/5: no golden fixture, claim file, VERSION, manifest or RELEASE_NOTES in the PR's own diff. Step 16: no custom_components/ in the PR's own diff.
- Head: live PR head = 4449ca654397321ff1a909704317d6eb174206b4 = the head this verdict names (ev/head-recheck.txt).

Note (paperwork): the body says each raised cap "is the measurement ... at the head". That still holds for every per-file cap. The corpus now measures 34 tokens above its new cap because of main's merges, inside the band.

## Red checks

- `budget-raise-gate / budget-raise-gate` and `gate` (owed reds): red only on the raise's owed approval at this head. classify reports APPROVAL-OWED; the approval follows this verdict.
