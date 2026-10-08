Fix review: blocked d30236a5a1a2ca3ee258908994690d63a5fb621d head-moved: measured d30236a5, head is b78e5810 (bot "ci: pin killed mutants")

bus-nonce: 69a3261bb7b12b4961445c0fe874bcf2

Reason: head moved to b78e58109ce293e87693955ce75b4d82b99e1c93 (github-actions[bot] "ci: pin killed mutants", 31 files, 186 insertions, killed_by pins only) while the review was open; mutation red at d30236a5 was the expected ADDED UNPINNED set the bot then pinned. Re-review b78e5810 as a bot-only delta.

Checked at d30236a5 (all pass): (a) no non-bot code commits since dc4e3f13; own commits c75b7770, c79b4bdd were already in dc4e3f13. (b) all 8 merges reproduce by git merge-tree; head merge's tests/closures.json is resolved by the ledger driver (tree 27563ad9 == HEAD tree), set of inert_reads preserved, only ux5_idle_codes.py added. (c) three-dot diff differs from dc4e3f13's only in tests/closures.json inert_reads ordering from main's own change. 
Open for b78e5810: body NOT refreshed (still base e2a4f7c6/head a5379d67, "this head has no run yet", cites optimizer.py:4035 not :1028; closures paragraph not fixed) - must name and answer reds delivery-status (non-required), budget-raise-gate cancelled twin (rerun needed; no budgets in diff), mutation; confirm closures/coverage/fast/mutation-pins green at the new head.
