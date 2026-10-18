Fix review: blocked 312f319238841bf545df92ba98777c93bbc5fde4 mutation-vacuous: the segment's two boundaries (cut at the next Carry:, cut at the line end) each survive alone; 43 checks pass while a planted body misroutes

bus-nonce: de1a6e03ea09bf800f463669f801a516
Round: third review of #2404. Round 1 blocked 5cf5786b9 (item-ref over-fire), round 2 blocked 354c84a96 (mutation-vacuous: paren form and segment scope each unpinned). This round judges the delta 354c84a96..312f31923: authored commit b3a121472 (two self-test arms plus null controls, M14 and M15) and the main merges cb398f3e3 and 312f31923. The main merge is a clean automatic merge: `git merge-tree --write-tree b3a121472 55dc8d9c2` gives the tree of cb398f3e3 exactly, and 312f31923's tree equals cb398f3e3's, so the resolution delta is empty.
Reviewed head: 312f319238841bf545df92ba98777c93bbc5fde4 (still the PR head when written). Role contract current (empty `git diff $(merge-base)...origin/main -- dev/governance/roles/`).
Next round is the fourth: by fix-review.md's last line, fixer.md owes a re-cut, not a repair.

## Block

Round 2's finding is fixed: M14 (paren form dropped) and M15 (`ITEM_REF.findall(text)`, segment scope dropped) are each killed by 1 check now. The same class is still open one level down, though. The body defines the guard as an id counting only "inside that marker's own segment". `carry_segments` bounds a segment in two ways: it cuts at the next `Carry:`, and it cuts at the line end. Neither cut is pinned on its own (`ev/mutants-312f3192.txt`):

- M15b, the line-end cut dropped (`.split("\n", 1)[0]` removed): 43 checks, 0 failed. `ev/p-nextline.md` has a marker line `Carry: R10-TICK-DRIVERS` and, on the next line of the same bullet, `The refusal it printed, (item f60b9acb), stays owed in this PR.` At the head it gives `0 routed, 1 unrouted`. Under the mutant it gives `1 routed`. Null control `ev/p-nextline-null.md` (the id inside the marker) gives `1 routed` at both.
- M16, the next-`Carry:` cut dropped (`text[at:]`, the line-end cut kept): 43 checks, 0 failed. `ev/p-twomarkers.md` (`Carry: R10-TICK-DRIVERS; the friction item is Carry: R10-INVENTED (item f60b9acb)`) gives `1 bad destination` at the head. Under the mutant the first segment swallows the second marker's id, so it gives `1 routed`: a bad destination is laundered through an unrelated marker. Round 1's "greedy" mutant was killed only because it also reverted the destination parse, so it never isolated this cut.

Repair: two self-test arms built on these two probes, each with its null control, named as mutants beside M14 and M15. Better, given that this is round 3 on one function: a single table-driven arm that perturbs each boundary of a segment (paren, segment start, next marker, line end, code span).

Not a block: M17 (`if ds else []` dropped) leaves `ev/p-nodest.md` and `ev/p-twomarkers.md` unchanged. An id under a marker with no destination maps to `[]`, which still reads unrouted. So I judge it an equivalent mutant.

## Verified

RESULT carry_audit_selftest=43 failed=0 (head)
RESULT queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0
RESULT mutant_M14_paren_dropped=killed (1 failed); mutant_M15_segment_scope_dropped=killed (1 failed); mutant_M12_both=killed (3 failed); mutant_M13_span_skip_removed=killed (1 failed)
RESULT mutant_M15b_line_cut_dropped=survived; mutant_M16_next_marker_cut_dropped=survived; mutant_M17_dests_guard_dropped=survived (equivalent on probes)
RESULT rows39 rows_caught=33 of=33
RESULT last20 rows_caught=34 of=35; last20_hits=76 on_a_row=46 on_no_row=30 (unchanged)
RESULT merge_tree_vs_origin_main=clean (exit 0; origin/main c8cc75ea9)
RESULT check_runs_head=46 completed: 31 success, 15 skipped, 0 failure
RESULT version_manifest_notes=untouched

- Step 11: b3a121472 and cb398f3e3 have no check-runs of their own, and the head has no red. Nothing in this round owes a root-cause answer.
- Step 9: `r10_carry_sweep_rows.py` is still the fixer's own instrument. The round-10 sweep has no committed harness, as rounds 1 and 2 recorded. I built the probes under `ev/` myself.
- Step 14: the delta moves no budget, closure or claim file. The only other files are main's (codeql, delivery rows).
- I did not re-run the figures the delta leaves untouched: policy_lint, field_coverage, agreement and structure. CI is green on them at this head.
