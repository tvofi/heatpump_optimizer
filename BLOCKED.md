# BLOCKED: r11-owner-card-external-heat

Question: R11-OWNER-CARD-EXTERNAL-HEAT is already delivered on main; may the orchestrator move its roster resume to merged and close the dispatch, so no seat re-does it?

Facts at origin/main fd93aa3e9b:
- PR #3871 merged as 34c7a3f610 (the roster's resume.commit); handoff/r11-owner-card-external-heat (044f90d048) and handoff-wip/r11-owner-card-external-heat (f7202d2bf2) are both ancestors of main.
- statusPill in custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js (line 9833) returns the external_heat key only when the twin is on and attributes.block_ignored !== true, and otherwise falls through to heating/idle, which is the carry from R11-OWNER-EXTHEAT-OVERRIDE.
- en, sv and de strings for status.external_heat, status.external_heat_title, status.heating_space and status.heating_dhw are present (lines 923-927, 1779-1783, 2459-2463).
- tests/card.mjs lines 12330-12334 test block_ignored true (falls through) and block_ignored false (external heat).
- No earlier BLOCKED.md exists on handoff-wip, dispatch or wip-sync refs for this topic.

No code was written and no handoff, body or PR was pushed. Under the reconciliation brief this counts as "next part already live on another ref".
