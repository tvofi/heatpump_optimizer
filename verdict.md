Fix review: merge 39910247950c509a4a22b649e23e34feeadd177c

bus-nonce: eaeb0343441bf6d3f0b4e6167a65c479

Note: figure: the body says 78 files were copied from the two box trees; at this head 49 were (`ev/box-copy-compare.txt`: 44 byte-identical to the boxes plus the 5 edited harnesses, out of the boxes' 29 + 22 files less the 2 `CHECK.txt`). The diff has 51 files: those 49, `dev/programme/delivery/3829.md` and `tests/closures.json`.
Note: stale-body: `## Head` names `01b007b91f` as this PR's head. The head is `3991024795` (`ci: re-record closures`, which only touches `tests/closures.json`). `review_carry.py 01b007b9 39910247` prints `CARRY` (`ev/review_carry.txt`), and `## Red checks` already names 3991024 as the head.

## Scope

Round 1 (first review of this PR). This is an evidence-landing PR: no `custom_components/` line changed, and no `VERSION`, manifest, `RELEASE_NOTES.md`, golden fixture or claim file is touched (three-dot diff against merge base `78d3b40221`). The only code is in five harnesses: each `parents[N]` root walk was replaced, four times by an inline copy of `tools/audit/repo_root.py`'s `repo_root` and once (`p1_seams.py`) by `d.parent.parent`.

## Evidence

- Head reviewed: `39910247950c509a4a22b649e23e34feeadd177c` (`ev/HEAD.txt`). The base is `78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f`, which is 0 commits behind origin/main.
- CI: `merge_train.py classify 39910247950c509a4a22b649e23e34feeadd177c --pr 3829` printed `GREEN 39910247950c509a4a22b649e23e34feeadd177c pending: none red: none` (`ev/classify.txt`). An earlier run had exited 2 (`REFUSE selftests`: job 136917292158 `governance / instrument-self-tests` concluded cancelled). The later run read GREEN. That job also concluded success in run 44907950621 at this head (job 136914081871).
- Merge with main: `git merge-tree --write-tree origin/main 39910247` exits 0 (`ev/merge-tree.txt`). The only driver line is `LEDGER-MERGE: resolved tests/closures.json`, and no conflict was reported.
- Copy fidelity: every box file except `CHECK.txt` is in the head. Each is byte-identical except the five harnesses the body names (`ev/box-copy-compare.txt`), and their whole delta is the root walk (`ev/landed-edits.diff`). The four inlined `repo_root` bodies match the canonical copy, which `tests/harness_headers.py`'s inline scan checks and which passes at the head.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at the head: `ALL 115 HARNESS HEADER CHECKS PASSED`, rc 0 (`ev/harness_headers_head.txt`).
- Mutation proof (`ev/mutants.txt`): I put back each box's original fixed parent count, one file at a time (P3 `enumerate.py`, P4 `enumerate.py`, P4 `probe_offstart_sites.py`, P5 `enumerate.py`, P1 `p1_seams.py`), and also planted a drift in P3's inlined walk. `harness_headers.py` exited 1 on all 6 of 6 and named the planted file each time (depth seams for the first 5, `python copies=221 differ=[P3 enumerate.py]` for the drift). The worktree was restored clean afterwards.
- Landed enumerators run at the landed path:
  - P3 `enumerate.py` and P5 `enumerate.py` resolve the root from a foreign cwd and print their RESULT lines (`ev/enumerators_landed.txt`).
  - `p1_seams.py` defaults `--root .`, so from the repo root it reproduces the committed `p1_seams.out` RESULT lines. The one difference is `bool-number seams=34` against the committed 33 (`seams_total` 75 against 74). `flagged` and the 7-of-7 judged-site lines are identical (`ev/p1_seams_landed.out`). The tree has moved since the box's baseline, so I read this as baseline drift, not a landing defect: the PR states it lands evidence as the boxes wrote it.
- `tests/closures.json`: the 13 added entries are exactly the 13 landed `.py` files, re-recorded by the closures autofix. `tests / closures` is success at the head.
- Not re-derived: the instance counts and barriered flags (P1 10, P3 1, P4 1, P5 2, P10 0, P11 3). They are the boxes' own judgements, and this PR neither judges nor registers them. They match the landed `REPORT.json` files.
- Finder's harness: none is named, and none is owed. This PR fixes no finding, so there is no mutation table or null control to run against a behaviour claim.
- Red checks: `tests / closures` and `pr-contract / pr-contract` were red at earlier runs, and both are in the owed-reds set. The body's `## Red checks` names both and answers each one (autofix repair, and a body-order failure). Both are success at this head.
- Forward-carry: none named, and none is owed. The body states the instances still go through the round's verify and judge steps.
