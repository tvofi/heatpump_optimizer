Fix review: blocked 57eeaa6d40f55efe32463848a3812c79edd03d97 mutation: 3 hand mutants on new card code survive (mid-width flip, hover's dhw wiring, narrative order) and the plan-why alt text describes a footer the PR removed

Round 1. Code head 57eeaa6d (PR #1830 head 11335214 = clean main merge 48cfd6ff, tree == merge-tree 828d61c6, + delivery row).
Briefs current: git diff merge-base...origin/main -- tools/audit/briefs/ empty.

Confirmed
- node tests/card.mjs at head: ALL CARD CHECKS PASSED (card_head.log).
- card_drift vs 9ad66abc: 39 moved and claimed, 1 identical (card_drift_head.log).
- DOM-move claim re-derived: head with the 3 new CSS rules removed (nocss.py) moves exactly score_open, shared_steps_hover, tooltip_hover; other 36 report STALE, i.e. stylesheet-only (card_drift_nocss.log). Claims match.
- claims-for unchanged (6.7.12 = VERSION); VERSION/manifest/notes untouched.
- merge-tree origin/main 57eeaa6d: clean, rc 0.
- Brief scope: headline lists every line; idle tooltip says price rank, coast run, next run, tank vs published minimum, solar ahead; no floor/fuse (pinned); fitWhy omits, never clips; top 8px + cap h-16 keeps it inside.
- Screenshots plan-why light/dark and tile look right.
- Forward carry carry-1795.json present; roster R9-UX-5 brief at 18901fc8 does not carry it yet (body says sent to coordinator).
- CI on 11335214 at 19:45Z: no red; browser, fast, coverage, closures still running.

Hand mutants (mut.py, node tests/card.mjs, mut.txt)
- R1 no solar line: killed. R4 coast end without +step: killed. R5 rank > not >=: killed. R7 no coast line: killed. R8 headline first line only: killed.
- R6 flip at 0.6 instead of 0.5: SURVIVES. The pin hovers x=600 on a 900 px chart (67 %), so it cannot tell the PR's mid-width rule from main's 60 %.
- R3 hover passes the space forecast as `dhw`: SURVIVES. No test drives the real hover on a hot-water idle step.
- R2 hover reads `dhw_min_temp` not `dhw_min_temperature`: SURVIVES. Same gap: the tank line is only tested through a hand-built ctx.
- R9 narrative lines reversed: SURVIVES. The body claims "in its own order".
- R10 tank line on the space channel: equivalent (the space forecast has no dhw_temp).

Docs (D6)
- docs/dashboard-card.md plan-why alt text says "space heating is off" and "with the house and outdoor temperatures underneath". The picture says "Space heating and hot water off". The temperatures are value rows above the block, and the body says the footer was dropped.

To fix
- Pin the flip between 50 % and 60 % (e.g. x = 0.55 * width).
- Drive _onPointerMove on a hot-water idle step of the fixture with dhw_min_temperature published below its tank temperature, and assert the coast/next/tank lines.
- Pin the narrative order.
- Correct the alt text.
