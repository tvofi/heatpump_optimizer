Fix review: merge 278e28c1396fdb7f4d8361e525cf58130d1f6bf4

bus-nonce: add3bb6c9513cec3f8289f77090e9b30

Round 3 of this review (repair round 2 after the carry-missing block at b9ec7037). Scope: the delta b9ec7037..278e28c1 (instrument/RCA/doc only, no custom_components change, so no widening), the previous block, and live checks at the head.

## Evidence

- Previous block (carry-missing: carries 8-11 held the claims without their controls): resolved. The roster carry is on origin/handoff/audit-r10-roster a09a5c59b, group R10-PREPR-RESIDUE (ev/roster-a09a5c59b.json). Its carries 11-15 (From 3411, items 41176b97, 300fa7f0, fab9d1da, e0b30357, d1d75b8f) state each control as a precondition, matching the body: C1 failing cases plus both null controls (non-merge commit past the receipt keeps the trailer and reuse_verdict rc 1; a non-ancestor receipt writes no trailer) and a re-measure instruction; C2 four planted reasons plus the valid-receipt null control; C3 sleep-2s case plus no-op null control; C4 before/after on one host with predict_sha1 identity, including the scoped c19017d6 control; the "never" follow-up with its null control. Item 88c4f531 carries the roster-op friction.
- carry_audit at head (packet): 7 finding items, 7 routed, 0 unrouted, 0 bad destination.
- CI: merge_train.py classify at the head exits GREEN, pending none, red none (ev/classify.txt). owed-reds names the required set; none of it is red.
- Merge: git merge-tree --write-tree origin/main <head> exit 0 (ev/mergetree.txt). VERSION, manifest, RELEASE_NOTES, custom_components, goldens and closures are untouched by the three-dot diff. No production code, so no mutation proof is owed (body says n/a; the diff writes no production line).
- Figures re-derived at the head: `open_prepr_receipts.py --self-test` PASS, 0 failed; `tips` re-run prints exactly tips=149 result=12 code=137 trailer=57 no_trailer=80, same=5 merge-only=3 non-merge=24 never=48, tree_equal=2 of=27 (ev/tips-rerun.txt); prepr.sh `2734 123` at c09cf12010 and `4682 325` at b0762725099f, HEAVY_SLOTS = 4 at c09cf12010 (ev/cb.txt); fold_ledger check 0 violation(s), 146 rca entries. C1's 7 x (62.8 - 18.9) = 307 is arithmetic on the frozen opens snapshot. Not re-derived: the opens medians against a live corpus (refs move; the frozen tsv carries them), the 2.3 ms spawn cost, and the 1561 s / 40 s step-6d timings (a 26-minute cloud run; cited as the body's own measurement).
- Red checks: body says none; no required red at the head.

## Findings

- Residual: the stale round-1 copies remain in the roster beside the corrected ones: R10-PREPR-RESIDUE carries 7-10 ("From r10-rca-open-prepr-slow, items dfceecd3, 70f46ea9, ddee73ac, 8eec61f0") hold round-1 text with no controls and no note saying the 3411 items supersede them, and the group's `rca` is still []. The PR's own Friction names these roster ops as the orchestrator's. A seat reading the group sees two disagreeing copies (finding-propagation.md: say which is newer). Drop or mark carries 7-10 as superseded by 11-14, and set rca to R10-RCA-OPEN-PREPR-SLOW. Carry: R10-PREPR-RESIDUE
- Follow-up: the opens medians are a latency proxy that includes the relay wait for both grades; C1's reach (7 tips) is small against its 307 open-minute estimate, so the fixer should re-measure reach before building and note that most `never` rows are C2's to split. Carry: R10-PREPR-RESIDUE
