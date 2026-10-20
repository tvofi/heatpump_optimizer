Fix review: blocked 84326c5ca1ec93168480f5a0e091bebeef753349 body-figures-stale: #2471's body describes the #2467 roster diff (17 new groups, 72 to 89, 8 stage changes, 38 carries), not this head's diff

bus-nonce: 603aea6ed5704aea750f669bfab90ad5

Round: not stated in the brief; first review seen by this seat.

Measured at head 84326c5ca1ec93168480f5a0e091bebeef753349 (origin/main 2bd48adfa), evidence in ev/.

Diff (ev/stat-main.txt, ev/diff.txt): origin/main...HEAD touches exactly dev/programme/delivery/2471.md and dev/programme/rosters/wave-r10-groups.json. Content is only the three claimed changes: group R10-UPDATE-PR-LOCK added (wave 1), R10-SAVINGS-NEGATIVE stage done with commit 73a6ca86 (#2463), and one carry paragraph appended to R10-CEILING-PROBE. OK.

Carry text (ev/2465body.txt): each of the three items (floor-only mapping and set-point-to-draw gain, reaching the real maximum, idle draw absorbing compressor draw) has every sentence verbatim in #2465's body. OK.

Merge: git merge-tree --write-tree origin/main HEAD exits 0, no conflicts, no MERGE-CLAIM lines (ev/mt.out, ev/mt.err). OK.

Recount of roster (python over the file at origin/main and at HEAD):
- groups 89 -> 90 (+1)
- stage done 42 -> 43; not-started 37, in-progress 6, queued 3, planned 1 unchanged at both
- carries total 196 -> 197 (+1)

Body figures, all wrong for this head: the body says "New groups (17, taking the roster from 72 to 89)", names 17 groups, "Stage changes to done (8)", a 7/6/1/3 stage split of the new groups, "38 carries across 9 groups", edited brief/owner-gate text on three groups, and that head d4f8914e adds 2467.md. None of it is this PR's diff. It is the #2467 body with only the Head paragraph rewritten. It also never mentions R10-UPDATE-PR-LOCK, the SAVINGS-NEGATIVE done flip or the CEILING-PROBE carry, and says "closes nothing" without stating the carry that the diff adds. Item 7/8: the quoted counts do not re-derive. The correct figures are +1 group (89 -> 90), 1 stage flip to done (42 -> 43), 1 carry (196 -> 197).

CI (ev/checks.tsv, check-runs API at this head): 23 success, 17 skipped, 1 neutral, and 2 still in_progress (closures, fast (3.14)); no red. Not a block by itself, but no merge verdict can rest on an incomplete set.

Fix: re-take the whole body from this diff (counts above), then re-dispatch review once the head's workflows conclude. The code diff itself is clean and needs no change.
