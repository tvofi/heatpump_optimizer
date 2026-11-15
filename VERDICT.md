Fix review: merge d0704b6718b5eeb7127aa2017cbaa844326fb512
bus-nonce: b3b5307399e683f2fc9b3fadc9ec7e7d
pending-ci: `merge_train.py classify d0704b6718b5eeb7127aa2017cbaa844326fb512 --pr 3611` printed `WAIT d0704b6718b5eeb7127aa2017cbaa844326fb512 pending: gate red: none` at review time (ev/classify.txt); this verdict holds once the required checks conclude green.

Round 2, a delta review (tvofi 2026-11-09): `git diff f460c3a2b320cf594736d301fa464a46b87cc2e3 d0704b6718b5eeb7127aa2017cbaa844326fb512`, read from a detached worktree at the new head. The delta has two files. The ledger is renamed from dev/audit/yardstick/round10/ to dev/audit/rounds/round10/objective/ with three lines changed, and OBJECTIVE.json has its ledger paths and `injected` changed. d0704b67 has two parents, f460c3a2 and the authored 119b5cb851, and brings in no main change. No production, instrument or policy file is in the delta, and check_scopes.py is untouched. Nothing widens the review.

## RESULT lines

RESULT self-test: `python3 tools/audit/check_scopes.py --repo . --self-test` at the head -> `yardstick records: covered=True, refused without the exclusion=True`, `SELF-TEST passed`, rc 0 (ev/check_scopes_selftest_head.txt). dev/audit/yardstick/round10/ now holds only OBJECTIVE.json.
RESULT citations: `git grep "yardstick/round10/escapes_hand"` at the head prints nothing. All four ledger paths in OBJECTIVE.json, and its count_command, name dev/audit/rounds/round10/objective/escapes_hand.tsv.
RESULT injected: the record's count_command (`awk -F'\t' '!/^#/ && $1 != "group" && $9 != "-"' <ledger> | wc -l`) selects 4 rows: R10-SAVINGS-NEGATIVE 2411, R10-HOTFIX-SAV-ESTIMATE 2411 2887, R10-HOTFIX-FLOW-SETPOINT-STUCK 3404, R10-HOTFIX-REFERENCE-BASIS 3587. 4/155 = 2.58 per 100, as recorded.
RESULT ledger counts: in 26, day0 6, unreleased 1, out 65. Unowned stays 7 and the window 155.
RESULT layout: `python3 tests/layout.py` -> rc 0, `GUARD: 0 refusal(s)`, `layout self-test: ok` (ev/layout_head.txt). The moved ledger falls under the existing `dev/audit/rounds/**` glob. The `dev/audit/yardstick/**` glob is still needed for OBJECTIVE.json.
RESULT closure: `tests/closure.py select --diff <merge-base>` -> `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
RESULT round check: on a throwaway merge 0b8b0f849a of this head with origin/eval-review/r11-4 f6d35cf73f, `check_scopes.py --repo . --ref HEAD --round 11` -> rc 1 with `FAIL start evaluation round=11: 48 gap(s)` (ev/check_scopes_round11_merge.txt). The gaps are 43 of `card ... is accepted and not merged at this ref` and 5 of `accepted for ... which dev/audit/config/objective.json still leaves unset`: criteria D4, D5, D9 and D10, and threshold product_green_floor. There is no missing round-10 record gap and no other kind.
RESULT evaluation: eval-review/r11-4 reads escapes in_window 26, unowned 7 and production merges 155. These agree with this record.

## Prior findings

- Block introduced-red (instrument-self-tests): resolved. The ledger moved out of dev/audit/yardstick/, and the self-test passes at the head. The body's `## Red checks` names the red and answers it with the cheaper detector (`check_scopes.py --self-test`) and its standing cost. Carry: dismissed: resolved at d0704b67
- Note root-cause-detectable: answered in the body. Carry: dismissed: resolved at d0704b67
- Note on the evaluation's window of 162: corrected in eval/r11 9de7c2bd, which reads 155. Carry: dismissed: resolved in the evaluation
- Note on the evaluation's escapes 31 and unowned 9: corrected to 26 and 7. Carry: dismissed: resolved in the evaluation
- Note on the record's `injected` undercount: resolved, 4 bugs, 2.58 per 100. Carry: dismissed: resolved at d0704b67
- Note on the two attribution differences: the body now names both (lines 17-18). R10-MIN-POWER-FLOOR stays D2 here and D8 in the evaluation, each with a stated reason; no term's value moves. Carry: dismissed: disclosed in both artifacts

## Findings

- Note: figure: residual in the evaluation, not this pull request. eval-review/r11-4's `terms.unowned.by_hand` reads value 7 but still lists 9 cards, among them E11-U10 for R10-OUTSIDE-DHW-START-HYSTERESIS, which is no escape by the ruling the evaluation adopted. The unowned card for R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE may be the ninth. Two cards then rest on no escape; each is a dimension-gap argument and no longer an `unowned` item. Carry: R11-INTAKE-R10-RESIDUE
