Fix review: blocked 0e2ee62bca778503d16b718d69deb7cc8d4d9374 root-cause-unanswered: budget-raise-gate went red at head and ## Red checks never names it

Measured at head 0e2ee62bca778503d16b718d69deb7cc8d4d9374 (merge base 7865ba9060a49aecf8f113bcaf7cb6c4ab58bd84):

1. Diff scope clean: CLAUDE.md (+10 lines, one ### Instruments section) and policy_budgets.json (exactly three caps raised). No rules/*.md, no .mdc, no production code, no VERSION/claims.
2. Budget exactness holds. CLAUDE.md at head: 14360 bytes, 14360/4 = 3590 tokens; 221 lines. roles.policy measured 9958 by policy_lint --budgets. All three written caps equal their measured values exactly; the opens list is unchanged; no other key moved. `node .claude/workflows/policy_lint.mjs` rc 0, 0 errors across 40 files.
3. Instruments real: merge_train.py, bus.sh, update_pr.sh, wt_sync.sh (the 15-minute crash-safety snapshot per HANDOVER), seat_venv.sh all exist in tools/audit/seat/ and none appears in base CLAUDE.md; archscore/, harnesses/, round9/ exist. Obligation sentence matches decision 0013 (HANDOVER #1879: instruments live in tools/audit/seat/, never /tmp).
4. Body contract: first line, headings, Figures (FIGURES: 1 resolved, 0 refused), ## Approval present, no armed closing keyword. But `budget-raise-gate` is red at head (it found exactly the 3 raises and refuses pending tvofi's decisive review — the designed pre-approval state), and the body's ## Red checks describes "budgets refusals" without naming the check; pr-contract exits 1 on precisely that (`check 'budget-raise-gate' is red and '## Red checks' does not name it`). One body line naming and answering budget-raise-gate clears it; nightly-status is green and answered.

Fix round 1. Re-review on the body re-take.
