Fix review: merge fb1e1f785724e0b9aa82d60c8faa4dde04491b8b

bus-nonce: ed1030e290d4dd06a15a76470372dc0d
pending-ci: gate, tests / coverage

## Evidence

Round 1 (first round, full scope). Head fb1e1f785724e0b9aa82d60c8faa4dde04491b8b measured; rechecked as PR head before posting. CI: `merge_train.py classify` printed `WAIT fb1e1f785724e0b9aa82d60c8faa4dde04491b8b pending: gate red: none` for about 33 minutes; the only run not concluded at the last read was `tests / coverage` (every other non-skipped run, including `instrument-self-tests`, `closures`, `fast (3.14)`, `mutation`, `pr-contract`-set contexts, concluded success; an early `gate` run reads failure but classify decides and reads it pending, not red). No required context is red. Merge verdict is conditional on CI going green at this head (relay posts it only then).

1. Roster: `wave-r10-groups.json` and `wave-r9-groups.json` at the head equal the roster branch blob at 89acffb1ab once every `archive/` is stripped from both (byte-identical, `cmp`); `critical-path.json` identical. The four named citations (handoff/r10-cop-learner-draw-floor, handoff/r10-hotfix-main-selftest-scope-2, handoff/r10-hotfix-reference-basis, review/3481) each appear as `archive/...` at the head with no bare occurrence. Null control re-derived: 544 groups on main and head, 0 added, 0 removed, 6 differ. DROPPED lines re-derived element-wise: R10-REVIEW-DISPATCH-RESIDUE 33/33/33 carries, main's changes at indices 5,14,17,20,30,31 present verbatim at the head except 30 (the extra `archive/` on review/3481, the pass's own retarget); R11-INTAKE-R10-RESIDUE 183/183/185, main's changes at 66 and 72 present verbatim. I did not re-run `main_only_roster_delta.py` (not in this checkout); the figures were rebuilt with my own keying on the group field, and agree with the body. Note the head also differs from the blob by archive prefixes beyond the four (#3601/#3604's, which the body says the blob copy drops): all are prefix-only.
2. State docs: re-rendered with the body's command plus `--pr-state` from REST (gh GraphQL is refused here). PLAN-TABLE, FLOW-BOARD and NEXT-SESSION-PROMPT byte-identical to the head. RESUME-CURRENT differs only by one added row `#3607 | fix/r10-closure-record-3 | OPEN`, because this pull request was opened after the author rendered it; no other difference.
3. HANDOVER.md: updated-for 13cbe48de4 is an ancestor of the head, and is the v10.0.0 tag commit (2026-11-15T05:22Z). Checked against git and REST: #3599 merged as 57fa260451 (03:49:24Z); #3491 as 099d4fa3f2 (03:48:50Z); #3604 as 946eb6d255; #3605 as 2d0b1c7594; #3601 as 29b3e5a74c; #3600 as 2a257fce08; #3575 as 4eea986a62; 89acffb1ab and f8d3342d50 exist; #3451 open, dirty, head 7f4a9be89c, verdict/3451 present, handoff/r10-process-slim-p2 at c314960799 (a live head ref; a merge of main); #3593 carries 5cf3425240; open set #3602 #3598 #3593 #3521 #3551 #3566 #3606 all open. 20 facts, no mismatch.
4. Paths in the three-dot diff: HANDOVER.md, delivery/3607.md, wave-r10-groups.json, four files under round10/state. Nothing else: no production, test, instrument, VERSION or claim-file change. wave-r9-groups.json is not in the three-dot diff (main already had its prefixes).
5. `git merge-tree --write-tree origin/main fb1e1f785724e0b9aa82d60c8faa4dde04491b8b`: clean, rc 0. Mutation, golden and budget steps do not apply (record files only).

## Findings

none
