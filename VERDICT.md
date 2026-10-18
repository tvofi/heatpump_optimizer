Fix review: blocked 354c84a963cb04cb68141cb394c0c4415a85b250 mutation-vacuous: each half of the item-ref guard survives alone; the self-test kills only the two reverted together (M12)

bus-nonce: ad2798604bc28247b08a9d5f788b884b
Round: second review of #2404. Round 1 blocked 5cf5786b9 (review/2404 dd663f18c) on the item-ref over-fire. This round judges the delta 5cf5786b9..354c84a96: commits 71a7b6294 and 269a8dfd4, plus two main merges that touch delivery rows only.
Reviewed head: 354c84a963cb04cb68141cb394c0c4415a85b250 (still the head when posted). Role contract current.
Evidence: ~/hpo-seats/r10s3/review-2404/ev2

## Block

The round-1 finding is fixed: all three of my probes now read `0 routed, 1 unrouted`. The repair has two independent guards. The body states both: an id counts "only as `(item <id>)` inside that marker's own segment". The self-test pins only their conjunction. M12 reverts both guards at once (the pre-review parser), so it is killed. Remove either guard alone and all 39 checks still pass, while a planted body misroutes (`ev2/mutants-354c84a9....txt`):

- Mutant A, the paren form dropped (`ITEM_REF` back to `\bitem\s+([0-9a-f]{8})\b`) with segment scope kept: 39 checks, 0 failed. `ev2/p-segbare.md` (a marker line `Carry: R10-TICK-DRIVERS, see the quoted UNROUTED line: body item <id> stays owed.`) goes to `1 routed`. At the head it is `0 routed`.
- Mutant B, segment scope dropped (`ITEM_REF.findall(text)` in `carry_refs`) with the paren form kept: 39 checks, 0 failed. `ev2/p-parenprose.md` (prose `the refusal named (item <id>) and is owed here ... Carry: R10-TICK-DRIVERS`) goes to `1 routed`. At the head it is `0 routed`.

Each guard covers a case the other does not. Neither is pinned on its own, so either can be lost in a later edit without a red. Repair: add two self-test arms built on these two probes, one per guard, each with its null control (`Carry: R10-LIVE (item <id>)` still routes). Then name them as mutants beside M12 and M13. M13 (code-span skip) is killed as claimed: with the skip removed, 1 check fails.

## Verified

RESULT carry_audit_selftest=39 failed=0 (head)
RESULT queue_pre_flight_selftest=37 failed=0; merge_train_selftest=180 failed=0
RESULT round1_probes probe-unrouted=0/1 probe-quoted=0/1 probe-backtick=0/1 (routed/items)
RESULT body_check="5 routed, 0 unrouted, 0 bad" (live body; its Red-checks quote of cb97c3b2 no longer routes anything)
RESULT mutant_M13_span_skip_removed=killed (`a backticked example Carry: ... does not route it`)
RESULT mutant_A_paren_form_dropped=survived; mutant_B_segment_scope_dropped=survived
RESULT rows39 rows_caught=33 of=33
RESULT last20 rows_caught=34 of=35; last20_hits=76 on_a_row=46 on_no_row=30 (unchanged from round 1)
RESULT merge_tree_vs_origin_main=clean
RESULT check_runs_head=45 completed, 0 failure/cancelled (closures 117708987163, pr-contract 117706700576 and 117706605865, instrument-self-tests 117706607247 all success)

- Step 11: the delta's commits 71a7b6294, 58be98660 and 269a8dfd4 have no check-runs of their own, and the head has no red. Nothing in this round owes a root-cause answer.
- Step 5 and 14: no VERSION or manifest change. The delta's only metric-adjacent files are two `dev/programme/delivery/` rows, both from main merges.
- Note, not a block: the code-span skip fails closed. The PR template shows the marker as a code span (`` `Carry: <dest>` ``, and line 38 puts the whole Friction line in one span). A fixer who copies that shape literally writes a backticked marker, which is now refused as unrouted. The refusal is loud, so nothing passes wrongly. It can be cheaper to say so in the template or the refusal text. This is the same file the body's Friction line routes to its cap item (O10-policy-fixer-md). Carry: O10-policy-fixer-md
