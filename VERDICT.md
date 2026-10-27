Fix review: blocked b0920b94abd9bfcb62611c05e04afda797a39518 body-stale: the body is PR #2866's (batch 22) text verbatim, only its Head section patched: it enumerates 95 commits over 6fe5170..1e9180dc9, all of them already on main (1e9180dc9 is an ancestor of origin/main), so it enumerates zero of the 27 commits this pull request lands and omits all 26 authored roster commits (a9c7555..3b78b44a0); it states this PR flips five delivery rows and adds #2866's row when this PR's only record commit is dev/programme/delivery/2878.md; and its Forward-carry says P199/P200/P203 "could not be appended", ordering three append-carry ops, while all three are already in the head roster and on main from 82db76ffe/d052b8d78/2f63ddb60 (merge 72da5ffa1), so following it duplicates them. The roster state itself is sound: no group, carry, issue, after, file or top-level field main carries is lost (superset PASS), every listed op is in the tree, the five flipped rows equal record_row.row_line from the API facts, and each stated figure re-derives from the refs it names.

## Head

Reviewed b0920b94abd9bfcb62611c05e04afda797a39518 from a detached worktree at that SHA; origin/main 524c1896b at measurement. The head did not move.

RESULT superset: PASS — main 208 groups, head 208; 0 only-on-main; 0 only-on-head; no carry entry lost; no resume key lost. Four groups gained carries (R10-ARCH-SHAPES-CLASSIFIER 4->6, R10-FLOW-DESIGN-STAGES 20->21, R10-FLOW-TOOLKIT-MODEL 8->9, R10-FLOW-WIP 8->9). R10-DIAG-AGES resume.stage reads main `fixing` -> head `in-progress`, the roster_sync-derived field excluded from the loss comparison.

RESULT ops-exist: PASS — all 95 commits in 6fe5170..1e9180dc9 change a file; the 13 append/drop-carry, 6 wire, 6 append-group, 8 set-after and 3 set-stage ops were checked against the resulting head roster, not the subjects.

RESULT flips: PASS — 2834/2858/2862/2864/2865 are MERGED at 0137c4cb052e/3b4180dcc680/149ce54a36bc/6fe5170cd7ce/bfc4a1e297fb and each row equals record_row.row_line from those facts; #2856 and #2863 are record-class (`stamp.merge_is_record_class` True for 1f82fee49add and f46bb2728641), so leaving them open is the generator's stated exemption.

RESULT figures: PASS as stated — 95; 6/6/60/27/6/2; blob hashes 53414799/0886357f/852ec7bd; 461/62 and the five 1/1 plus 1/0; merge-tree 8a25ac66 exit 0; self-test 55 checks 0 failed; brief_lint TOTAL 0 error(s); null control 199->208, added 9, removed 0, changed 27 with the body's key list. These reproduce against 1e9180dc9, not the PR head (whose roster blob is cc64745e).

## What blocks

The record, not the tree. `git log --no-merges --format=%H origin/main..HEAD` is 27 commits (26 authored + 1 record); `comm -12` of that set with `git log 6fe5170..1e9180dc9` is 0. A body diff against PR #2866 shows only the Head first paragraph replaced and one merge paragraph added; the op lists, record beat, Figures, Null control, Red checks, Forward-carry and Friction are #2866's. Also: the head is 19 commits behind `origin/handoff/audit-r10-roster` (b589d2b09), which carries this PR's own registration R10-ROSTER-BATCH24 (14268fb54) while the row `dev/programme/delivery/2878.md` names `(R10-ORCH-ROSTER)`, a group the roster does not contain.

## Checks

55 check runs at this head, all success or skipped; the reds the body names (instrument-self-tests, pr-contract, gate) belong to ancestor 6f42fc12b and are named with their cause.

## Not established

No `bus-nonce:` line in the review brief and no dispatch record for #2878 at this head in `$HOME/.zcode/bus/dispatched`; `bus.sh push-verdict` refuses the publish, so this verdict is returned to the dispatcher unposted.

bus-nonce: bb7c247e5bca5efe189fd220a582fd23
