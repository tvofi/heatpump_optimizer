# BLOCKED: R11-PRE-PRODUCT-READS (part 1) -- body_push.sh exit 4, REFUSED CARRY-LANDED

Question: the relay folds the carries below onto the round's roster branch (this seat may not write it) and re-runs `bash tools/audit/seat/body_push.sh r11-pre-product-reads <body>` with the body kept at handoff-wip/r11-pre-product-reads-body 0d1781ccbe.

Code head: handoff/r11-pre-product-reads at ede3434ae196bc16171a6ac25fa1b8a8354452c1 (prepr.sh clean, body check included, at that head; no conflict with origin/main b94425b94f).

```
fill-red: the diff adds no unpinned mutation site; nothing written
figure_block: refreshed 1 block(s) at ede3434ae196
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R11-PRE-PRODUCT-READS at ede3434ae196, 1 live, 1 dispatched carries, 0 refused
CARRY-STATUS R11-PRE-PRODUCT-READS body item 31b27b88: a status line on its own carry, lands nothing: '- n6, the interface of design 3.5 (one command printing each escape in the window with id, released '
CARRY-MISSING R11-PRE-PRODUCT-READS body item 6ceaaf5d: not in its brief or carries: '- Part 2 of the approved plan: the regret oracle script under `tools/audit/` and its guide (design 3'
CARRY-MISSING R11-PRE-PRODUCT-READS body item d65f4c4c: not in its brief or carries: '- n8, measured above (`ATTRIBUTE_KEYS` holds no forecast): D15 step 9 asks a seat for `C_same` per i'
CARRY-MISSING R11-PRE-PRODUCT-READS body item 94f5e481: not in its brief or carries: '- n11: `dev/audit/rounds/round10/objective/escapes_hand.tsv` is a hand-read escapes ledger with owne'
CARRY-LANDED: 3 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
body_push: refused body kept at handoff-wip/r11-pre-product-reads-body 0d1781ccbe426e49ab0e45f2bf68bb2c635f93c7
```
