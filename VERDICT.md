Fix review: merge d144a5917737bc7d9ecc713308e4faa30387c1cf
bus-nonce: 5adf24ae2785b19f1c35e26a355b6ee3

Round 1, full scope. Head moved to 70ca147447d5c2095ddc475518a79a3476569cf1 (`ci: merge main`); `review_carry.py d144a591 70ca1474` prints CARRY (ev/review_carry.txt), and at 70ca1474 all 285 rows this PR adds still exist with their anchor in the inventory.

RESULT pin-reproduction: 6 sampled rows (seed 3938, one per killer: block_duty, manual_plan, plan_view, finite_boundary, env_drift, solar_alignment) re-driven with `mutation_table.py --anchor <a> --scripts <killer>` at the head: `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced` each, null control survived each driver (ev/spot.log).
RESULT mutation-proof: `pin_harvest.py --self-test` rc=0; three hand mutants of `narrowed` (no filter, args dropped, filter inverted) each rc=1 (ev/selftest-mutants.txt). No production line changes.
RESULT figures: unpinned sites 1739 at ef797d79 and 1446 at the head, re-derived with the body's command; DISPOSITIONS.tsv totals equal the body's; every candidate has one disposition; the family-B and S2 identities outside the enumerated set are exactly the 18 dropped-anchor-gone. I did not re-derive family A (box refs not fetched).
RESULT drive-evidence: 17 batch heads b987439d, 1 head 34867f49; every report records its null control surviving.
RESULT untouched: VERSION, manifest, release notes and both claim files are not in the diff. `git merge-tree --write-tree origin/main d144a591` exit 0.
Note: figure: the body says main had pinned 13 of the 306 anchors, but 21 pinned anchors already had a killed_by row at ef797d79 (13 add/add conflicts plus 8 identical rows), so the branch adds 285 rows. The site fall of 293 is correct. Carry: dismissed: a figure correction to this PR's own body, made before merge
Note: root-cause-unanswered: tests / closures: red at 394bfe18 (UNDER-SCOPED, repaired by the closures-autofix commit d144a591). `## Red checks` reads none, so the required `pr-contract` is red at d144a591 and `gate` fails on that alone. Naming UNDER-SCOPED in the body is enough. Carry: dismissed: a body edit on this PR, the orchestrator's to make before merge
Note: head-stale-in-body: `## Head` names 394bfe18; the head is now 70ca1474. Carry: dismissed: a body edit on this PR, made with the note above
