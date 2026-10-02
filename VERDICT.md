Fix review: merge 17e1ac3e4b780facd4962987331f9f5e41dcc233

Round 2, PR #1840, R9-UX-3 (Health tab). The PR head 17e1ac3e has code 03576be7 plus docs/delivery/1840.md only (`git diff --stat 03576be7 17e1ac3e`: 1 file). Its base is main 777c2318, which is still current main. The body's Head names 03576be7. Round 1, blocked at 6dd4630d (code f512f826), is in evidence UX-3-review-6dd4630d.

Delta f512f826..03576be7: two string-table lines in the card (health.p_unknown_unit, en and sv) and 54 lines of tests/card.mjs. No claim file, golden or budget changed.

RESULT card.mjs at 03576be7 rc0 ALL CARD CHECKS PASSED
RESULT card_drift.mjs GOLDEN_REF=777c2318 rc0: 39 moved and claimed, 1 identical (editor_schema, the control), unchanged from round 1
RESULT round-1 survivors, re-run by me against node tests/card.mjs, each restored, worktree clean afterwards:
- M5 stale -> false: KILLED ("a plan older than its limit shows a warn Stale pill on the plan row")
- M5b stale -> true: KILLED ("a fresh plan shows an ok Fresh pill on the plan row")
- M6 power step -> false: KILLED ("an assigned power meter shows the power step done, with no Assign action")
- M13a pill guard dropped: KILLED (unavailable and unknown header-pill checks)
- M13b inputs guard dropped: KILLED (unavailable and unknown inputs-block checks)
- M13c only the unknown arm dropped: KILLED
- S1 en unknown_unit removed: KILLED (the enumerated every-code check, and the unknown_unit check)
- S2 sv unknown_unit removed: KILLED (the unknown_unit check; the enumerated sv check alone would pass on the English fallback, so the specific check is the one that pins Swedish)
RESULT round-1 kills still hold (the fixer's 3 plus my 7); the round-2 code adds no logic
RESULT enumeration: the card.mjs check derives problem codes from inputs.py by `reading.problem = "..."`, which gives the 9 codes I enumerated in round 1, minus not_configured (it never reaches details()). The class is closed.

Carried from round 1 (code unchanged there):
- structure.py and doc_claims.py pass.
- VERSION, the manifest version and the notes heading are untouched.
- The facts the card relies on hold against the sensor code.
- Forward-carry: present in .claude/workflows/carry-1795.json (third entry, R9-UX-7). The orchestrator copies it into the roster's R9-UX-7 brief.
- Body: "Part of #1795" is right for a multi-item issue.

CI at 17e1ac3e at posting time: every completed check is green, and none is red. The two cancelled runs are superseded duplicates of pr-contract and budget-raise-gate, each with a green run. The Tests workflow had not reported, so the merge waits on CI green per the merge rule. I did not re-run the gate (fix-review step 11).

Owed before merge: tvofi's approving review at this head, because tests/card_browser.mjs is code-owned.
