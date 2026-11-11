Fix review: merge 7bcabb999f96e0c1e864b51ca4283c4a5a464857

bus-nonce: 5a1c8e70b4e6135b707f2a9ec3f2031d

Round: third review. This is a later round, scoped to the delta 4660c050..7bcabb99 under the owner ruling of 2026-11-09.

## Evidence
- RESULT head measured: 7bcabb999f96e0c1e864b51ca4283c4a5a464857 (ev/HEAD.txt). The PR API reports it as the head at verdict time.
- RESULT the delta is three merges of origin/main: 143b44af3, ed0900e33 and 7bcabb999. `review_carry.py 4660c050 7bcabb99` printed FRESH-REVIEW because 143b44af3 is not the automatic merge of its parents.
- RESULT ed0900e33 and 7bcabb999 are exact automatic merges. For each, `git merge-tree --write-tree <p1> <p2>` gives the commit's own tree: 11119f90 and 711d3c71.
- RESULT 143b44af3 (parents 4660c050 and main 04dfcafc): the automatic merge conflicts only in dev/governance/roles/fix-review.md. tools/audit/seat/bus.sh auto-merged. The commit's tree differs from the conflicted auto-merge tree only in that file.
- RESULT the resolution of fix-review.md is an exact union:
  - `git diff <main parent> 143b44af3 -- fix-review.md` is identical to the branch's own diff from the merge base: the header drops "(a script routes on it)", and item 7 gains the handoff-tip clause.
  - `git diff <branch parent> 143b44af3 -- fix-review.md` is identical to main's diff from the merge base: #3341's rewording of items 1, 2, 4, 6, 8, 9, 11 and 13.
  - Neither parent's change was lost. At the head, `handoff tip` and `class-open: <seams>` each occur once, and there are no conflict markers (ev/figures.txt).
  - The body's "## Resolution" account matches.
- RESULT the PR's own patch is unchanged by the delta. The +/- lines of `git diff <merge base> 4660c050` and `git diff fc022fd1 7bcabb99` are byte-identical (empty ev/patch-interdiff.txt). Both diffs cover 20 files, +578/-74.
- RESULT the PR's patch touches no production code: `git diff fc022fd1...7bcabb99 -- custom_components` is empty. The delta's custom_components changes (16 files) all come from main through automatic merges, so the review was not widened.
- RESULT `python3 tools/audit/seat/review_packet.py --self-test` at the head: 85 checks, 0 failed, exit 0 (ev/review_packet-selftest.txt). This matches the body.
- RESULT `bash tools/audit/seat/bus.sh --self-test` at the head: 173 checks, 0 failed, exit 0 (ev/bus-selftest.txt). This matches the body, whose figure was taken at 143b44af3.
- RESULT the other body figures, re-taken at the head (ev/figures.txt):
  - `tests/closure.py select`: "MODE: SCOPED -- 2 script(s) run", running tests/doc_claims.py and tests/entities.py.
  - STRUCTURE RATCHET PASSED.
  - `policy_lint.mjs --budgets`: rc 0.
  - RULES-SYNC ok.
  - Not re-run: the scoped gate pass counts (297 and 2707) and prepr.sh. I cite CI's `gate`, which is success at this head.
- RESULT merge with main: `git merge-tree --write-tree origin/main 7bcabb99` exits 0 at origin/main 45adb0c3, with no conflict.
- RESULT CI: `merge_train.py classify 7bcabb99 --pr 3366` exits 0 with `GREEN 7bcabb999f96e0c1e864b51ca4283c4a5a464857 pending: none red: none` (ev/classify.txt).
- RESULT required checks: `merge_train.py owed-reds` lists the required set (ev/owed-reds.txt). It takes no head or PR argument. Every context in that set is success or skipped at the head. The two intermediate merge commits show `red: none` (ev/classify-intermediate.txt). The body's `## Red checks: none` stands.
- RESULT the previous verdict (verdict/3366, merge at 4660c050) had no findings, so none is owed resolution. Its inherited red, `governance / instrument-self-tests`, is success at this head.
- VERSION, the manifest, RELEASE_NOTES, both claim files and every `*_budgets.json` are untouched by the PR's patch. The three-dot diff is empty.
- RESULT closing self-audit: `carry_audit.py check` over this verdict reports 0 finding items, rc 0 (ev/carry-audit.txt). It ran with an empty `--body`. The PR body was audited at this head by the review packet: 0 items, 0 unrouted.
- Policy approval: the patch carries policy files (fix-review.md, standing-dispatch.md). The owner's approving review is still required before merge, and it is not mine to give.

## Findings
none
