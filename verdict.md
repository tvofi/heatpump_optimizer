Fix review: merge 037611d5e6816893de290963f12ddba293cbace7

bus-nonce: 97ba1e43c64b78507d568e98f6976fee

Round 1. Record PR: dev/programme/triage/s6-batch108.md and dev/programme/delivery/3154.md, head 037611d5e6816893de290963f12ddba293cbace7, measured at that head (a detached worktree).

## Findings

None. The record settles its one ruling (P366, REJECT for code files) and leaves nothing owed after the merge.

## Evidence

- RESULT three-dot diff (`git diff $(git merge-base origin/main HEAD)...HEAD`, merge base 0166aefd7 = origin/main): exactly two files, the batch file (66 lines) and the delivery row. No VERSION, manifest, RELEASE_NOTES, tests/golden or claim-file change; no host path in the added lines. ev/diffstat.txt.
- RESULT `git merge-tree --write-tree origin/main <head>` exits 0 (ev/merge-tree.txt).
- RESULT classify: GREEN, pending none, red none (ev/classify.txt). The body's `## Red checks` says none, and no check concluded red at this head (all pages read).
- RESULT body `## Head` names 037611d5e6816893de290963f12ddba293cbace7 and the authored code head 6b7648651; the extra commit holds only the delivery row.
- RESULT cited facts re-derived: origin/main is 0166aefd7; roster branch is f2d9626b4; 5bb7710c1, dba968f8d, aa6148d4f, 404117b99 and f04b25a00 all resolve. `review_carry.py 5bb7710c1 dba968f8d --main origin/main` prints FRESH-REVIEW, 1 branch-only commit, "the branch's own diff differs". The normalised diffs differ in exactly one line, the `snapshots.py` context line `if not snap.get("healthy"):` against `... or "before_reset" in snap:`; the `-U0` +/- lines are equal. dba968f8d is a single main merge.
- RESULT bus.sh lines 503-516 refuse a second reviewer only on rc 0 (CARRY); app_approve.sh self-test arms at lines 1568 and 1580 and the context arm at 1607 exist as cited; `norm()` at line 390 drops `index` and `@@` lines and runs at -U3.
- RESULT P325 (s6-batch88.md) is as quoted: REJECT for code files, the 9 context-only PRs all before 2026-10-24, #3014 the tenth, and the re-open trigger of at least 5 delta reviews of context-only code heads with no defect in the adjacent lines. P366 cites none, so REJECT follows its own stated, testable reason. #3077 (head aa6148d4f) holds the `*.md` arm; its `norm()` text cites P17 and P325, so the carry-nothing ruling matches. The record's "built in #3077" means authored on that open PR, and no ruling here depends on it landing.
- RESULT mutation proof for the body's claim, run from the worktree: `ruling_verdict` reads P366 as REJECT and P367 as None; with the verdict flipped it reads ACCEPT; `triage_refusal` refuses a citing text ("is not an ACCEPT ruling (REJECT)"), and with the file absent refuses "is not on the roster branch or origin/main". The null control holds.
- RESULT carry text matches the ruling: "No carry, no roster op", and the body's Forward-carry is none. A REJECT with no carry owes no roster entry.
- Not re-derived: the seat-ledger line (22:51:54Z, nonce 8123b36a) and the owner's 19:50Z rule. Both are session-ledger or queue records outside the tree, so I take them as the record's sources and no ruling here is judged on them alone. The 19:50Z rule is cited the same way in batch 107's record.
- The record's own quantified claim (about one delta review a week, about 20 minutes) restates P325's count, which has its source table there.
