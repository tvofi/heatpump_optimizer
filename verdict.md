Fix review: merge 9b9c4ffc7d168af9dc7007f361e9402ad32065db

bus-nonce: abc27e13f0f31cfbad52434308f66f44

## Evidence
- Head measured: 9b9c4ffc7d168af9dc7007f361e9402ad32065db (ev/HEAD.txt). Round: first review by this seat. Head is a merge of 41d98b8e9 with an identical tree (git diff empty); origin/main `425b85849` (re-checked at the end) merges cleanly (merge-tree rc=0, no MERGE-CLAIM line).
- CI: `merge_train.py classify` -> GREEN, pending none, red none (rc=0). Packet digest green; carry_audit 0 findings; figure_lint 19 resolved, 0 unverified.
- Key gap re-derived (own script, flattened dotted leaves): strings.json vs de.json 0 missing / 0 extra; en vs de 0/0.
- Mutation: deleted selector.compressor_modulation.options.on_off from de.json at head -> entities.py "1 of 2703 ENTITY CHECKS FAILED", rc=1 (ev/entities_mutant.log). Unmutated head: "ALL 2703 ENTITY CHECKS PASSED", rc=0 (null control).
- claims.py at head: claims_true=123, claims_false=0, tree left byte-identical. harness_headers.py: ALL 112 PASSED. card.mjs: ran only after plan payload existed in the body author's flow; my standalone run lacked the payload, so I cite CI's green `tests / fast (3.14)` and `tests / browser` for it rather than my own run.
- Class enumeration: per-language production tables with an sv entry (narrative.TEMPLATES, topology._TRANSLATIONS, config_flow.PRESET_WARNING, card STRINGS) each have de; no sv-only production seam remains. Historical dev/audit/rounds scripts that hard-code en/sv are audit instruments, not shipped UI.
- VERSION/manifest/RELEASE_NOTES/claim files/budgets: untouched in the three-dot diff. Red checks: body answers the earlier fast/pr-contract/mutation reds; none red at this head.
- Not re-derived: the stress.py memory-peak red on the author's container (CI passes stress); I did not run the full scoped gate or mutation table, citing CI.

## Findings
none
