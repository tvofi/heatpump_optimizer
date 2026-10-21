Fix review: blocked fe1365f0f992b1d53d79c8e0a1d94804a74f53d8 body-stale: Null control says every carry list is unchanged except R10-POLICY-FIXER-MD, but at this head R10-LIVESTATE (8 to 9) and R10-UX-HEALTH (5 to 6) changed too, and Head still names f424d993d as the authored code head

bus-nonce: 4e030b94445cb86f87f436bd597d7054

Round: delta re-verdict after my merge verdict at df70cb6bca69c7b1717abcc317233ff1bc994df3 (round 2 on this PR; this is not a re-cut round). Head measured: fe1365f0f992b1d53d79c8e0a1d94804a74f53d8; git rev-parse origin/fix/audit-r10-roster gave this same SHA. Base: origin/main f2fb1b0e950ecd047b7f08b3adef93776a622540, which is also the merge base.

## What I checked, and the result

- Roster delta. git diff df70cb6bca69c7b1717abcc317233ff1bc994df3 fe1365f0f992b1d53d79c8e0a1d94804a74f53d8 -- dev/programme/rosters/ (ev/delta_roster.diff) has exactly two appends to wave-r10-groups.json. R10-LIVESTATE gains the #2572 item 4c077302 note (price_tiles), and R10-UX-HEALTH gains the #2572 item 6ce59610 note (open_options). Each one matches #2572's Forward-carry section. Nothing else in the roster moved. RESULT delta_roster_hunks=2
- The rest of the delta is main's own merge. The three-dot file list at the head equals the list at df70cb6bca69c7b1717abcc317233ff1bc994df3 (6 files, ev/threedot_files.txt). Every file except the roster has the same blob at both heads, and main did not touch the roster between the two merge bases. RESULT threedot_new_outside_roster=0
- Lint gate at the head. node tools/policy/brief_lint.mjs printed TOTAL: 0 error(s) across 47 file(s) and exited 0 (ev/brief_lint.txt). carry_audit owners 6ce59610 4c077302 printed one owner each (R10-UX-HEALTH.carry and R10-LIVESTATE.carry) and exited 0, so nothing is orphaned (ev/carry_owners.txt). A sweep of origin/handoff/audit-r10-roster (23ef06dc6) against the head printed CARRY-AUDIT: 0 unrouted (ev/carry_sweep.txt). The handoff roster equals the head's roster.
- Carry controls as preconditions. LIVESTATE's control (no _price_tiles in coordinator.py) does not hold at main today: the grep finds 5. Neither does UX-HEALTH's (open_options is absent from main's card). Both targets follow R10-ADVISOR (#2572, still open) through after edges: LIVESTATE after R10-SCORES, and R10-SCORES after R10-ADVISOR; UX-HEALTH after R10-SCORES. So each control is a precondition of its stage once #2572 merges, not a claim about the tree today. Carry: dismissed: ordering already enforces it
- Merge. git merge-tree --write-tree origin/main fe1365f0f992b1d53d79c8e0a1d94804a74f53d8 printed tree 99bb43157 and exited 0, with no claim-file conflict (ev/merge_tree.txt).
- Figures re-derived at the head. Groups: 108 at both ends. Critical path from plan_table.py: 11 at origin/main and 8 at the head, on the same path the body names (ev/depth.txt). Carry lists that differ between main and head: R10-LIVESTATE 8 to 9, R10-UX-HEALTH 5 to 6, R10-POLICY-FIXER-MD 5 to 6 (ev/carry_lists.txt). RESULT critical_depth main=11 head=8; RESULT carry_lists_changed=3
- CI at this head, read once from the check-runs API (ev/check_runs.tsv). Still in progress: coverage and fast (3.14). Red: nightly-status. The body answers it, and the diff does not reach anything it reads. Every other check passed or was skipped, and both pr-contract runs passed.

## The blocker

- The body's Null control says "Every carry list is unchanged except R10-POLICY-FIXER-MD's (5 to 6)". At this head that is false. Two more carry lists changed, both through this branch's own commits 9dc08aac2 and 23ef06dc6 (ev/carry_lists.txt). Step 8 says a quoted number I cannot re-derive is not verified, and this one re-derives to a different answer. Carry: dismissed: body edit on this PR
- The Head section's first sentence calls 23ef06dc6 the authored code head. Its second paragraph says the authored code head is f424d993d (handoff/audit-r10-roster), but origin/handoff/audit-r10-roster is 23ef06dc6 (ev/handoff_ref.txt). Carry: dismissed: body edit on this PR
- The fix is a body edit only. Name the two carry appends in the Null control (and in the paragraph listing the roster branch's commits) and make the authored code head consistent. The head does not need to move, so the next verdict can be issued at this same SHA. Carry: dismissed: body edit on this PR

## Other observations

- The three-dot list has six files. The body lists five for f424d993d; the sixth is dev/programme/delivery/2576.md, the PR's own delivery row, which was unchanged between df70cb6bca69c7b1717abcc317233ff1bc994df3 and the head. Carry: dismissed: own delivery row convention
- Steps 1-6 and 14 do not apply. The diff writes no production or test code and moves no budget, golden fixture or closure. The body's Mutation proof is n/a, which is correct. Carry: dismissed: roster-only data diff
