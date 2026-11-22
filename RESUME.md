Repair of review round 1 (blocked mutation-vacuous at 6ef32c22f3, C1).
Code head aeced5ecfe3604b5c0a010d7db2d75d262d2fd30 on handoff/r11-outside-rooms-3b.
Delta for the reviewer: git diff 6ef32c22f3 aeced5ecfe = the origin/main merge f9ce3efe2a, the merge of the bot head 84ae6ce8aa,
(budgets only conflicted: driver-resolved, no row raised) plus ffb12a9319 (tests/features.py only).
Evidence stays in the fixer's local seat directory (fix-3838-mut/evidence): the C1, C1a and C1b
diffs, the block driver, the prelude (emitted plus `import asyncio as _asyncio`) and block outputs.
Overlay note for round-end triage: proto/features_block-prelude-swallowed-nameerror.md (orchestrator's r11 dir).
