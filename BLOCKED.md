# BLOCKED: r11-seam-solver (fixer seat)

Question: The brief says "Do your work inline, with no subagents: this replaces the Agent-subagent routing line above for this seat", but the frugal routing PreToolUse hook (command hook 3, frugal@synced) refuses every further inline Read/Bash discovery op past 5 per prompt ("inline search op 7 this prompt exceeds budget of 5 ... the budget resets when you delegate"). The brief forbids FRUGAL_ALLOW_INLINE and editing .claude/settings.json, and forbids working around a refusal. Which governs for this seat: may it delegate discovery reads to a haiku/sonnet Agent subagent despite the "no subagents" line, or will the seat environment be re-dispatched with the inline guard lifted?

State at stop (base bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f, no code written):
- D1-s1-51 harness (`$EXPORT/dev/audit/rounds/round11/D1/leads/slot_reason_hashseed.py`, plan/r11 819aa2e3): distinct_tie=2, distinct_null=1 at base -- reproduces at main.
- D2-s3-01 harness (`$EXPORT/dev/audit/rounds/round11/D2/s3/m3_risk.py`): savings_inflation_lambda1_price_risk=10.2015, null (lambda 0) 0.0000 at base -- reproduces at main.
- D0-s2-01 (wood_seeds.py --census/--race) and D0-s3-02 (offstart.py) base runs started, not read.
- Fix shapes read so far: plan_slots.close's `max(set(codes), key=codes.count)`; `_Horizon.prices` is the risk-adjusted series from `_stash_price_horizon` and feeds `energy_cost_of` money figures and `_build_result`'s published prices; the space-only seed set scales by `_wood_covered_share` and neither start set carries the lower bound.
