Fix review: blocked 6dd4630dafc3a614608051b29c0e0b7c31de1f8d mutation: three Health-tab sites survive their mutants, and one published problem code renders as a raw token

Round 1. PR #1840, R9-UX-3. Measured at code f512f826 (6dd4630d adds only docs/delivery/1840.md; code-identical). Contract current: empty briefs/rules diff against main 777c2318, which is the merge base.

RESULT card.mjs rc0 ALL CARD CHECKS PASSED
RESULT card_drift.mjs GOLDEN_REF=777c2318 rc0: 39 moved and claimed, 0 unclaimed, 0 claimed-but-identical; editor_schema identical (the control)
RESULT structure.py rc0; doc_claims.py rc0 (84)
RESULT entities.py rc1 locally: 2 checks on updated-for 4bcfcf20 ancestry; this clone is shallow, so not attributed to the PR (CI fast job decides)
RESULT VERSION, manifest version, notes heading untouched

Mutants (node tests/card.mjs, each restored):
- killed: the fixer's three (pill n===0 -> n<=1, waiting filter -> "unknown", n===1 -> n===2), confirmed independently
- killed: healthy-row skip, header pill removed, health signature, Health tab button, stale-input limit text, price step forced done, diagnostics action -> settings path
- SURVIVED M5: healthPlanHtml `const stale = age.minutes > age.limit` -> `false`. No check reaches a stale plan, so the plan row's warn pill is unpinned.
- SURVIVED M6: checklist power step `assigned("heat_pump_power_entity")` -> `false`. Only the unassigned path is checked; an assigned power meter is never shown done.
- SURVIVED M13a/b: drop the `unavailable`/`unknown` guard in healthPillHtml and in healthInputsHtml. With the Input Problem sensor unavailable, its attributes are empty, so the unguarded pill reads "All inputs fresh" (ok) over inputs nobody can see. That is the wrong answer the guard exists to prevent, and nothing pins it.

Defect: inputs.py:800 publishes problem "unknown_unit". STRINGS has health.p_* for seven codes but not this one, so the row prints the raw token "unknown_unit" in English and Swedish. The design asks for problems "in words". Enumeration rule: every `reading.problem = "..."` in inputs.py (9 codes; not_configured never reaches details() because its entity_id is None).

Owed for round 2:
1. card.mjs checks that fail under M5, M6, M13a and M13b.
2. health.p_unknown_unit in en and sv, with a check.
3. Re-run card_drift (expect the same 39 claims) and prepr.sh on the merged head.

Verified independently (not blocking):
- The four waiting sensors are enabled by default and go unavailable while waiting. HA drops the extra attributes of an unavailable entity, so waiting_for is unreadable from the card, as the body says. The COP sensor has two reasons (measured_power_entity, first_cop_sample), and the card's fixed text covers both.
- No published fallback input, no default-off insight count, and max_age_minutes only for a failing input: the carry's three facts hold.
- Forward-carry: present in .claude/workflows/carry-1795.json (third entry, stage R9-UX-7). The roster's R9-UX-7 brief on handoff/audit-r9-fixplan still has to receive the same text; that is the orchestrator's job.
- Body: "Part of #1795" is right; #1795 is the multi-item UX feature issue, so no closing keyword.
- tests/card_browser.mjs is code-owned, so tvofi's approving review is owed at the final head.
- Optional: the pill counts every problem, not just stale ones, and still says "N inputs stale" when an input is unavailable or not numeric.
- CI at 6dd4630d was still running when this was written; no red check yet.
