Round 10's objective record, which decision 0018 section 6 has the closing round write and which round 10's close did not write, written now under tvofi's ruling on card E11-N-OBJECTIVE-RECORD ("Write it now (Recommended)"). Two record files under `dev/audit/yardstick/round10/`: `OBJECTIVE.json`, one row per term of `dev/audit/config/objective.json`, and `escapes_hand.tsv`, the by-hand escapes ledger that `escapes`, `injected` and `unowned` carry as `by_hand` beside a NO-READ. The third change is one glob in `tests/layout.json`. No production, instrument or policy file changes, and nothing is closed by keyword.

## Summary

- **Window.** v7.0.0 (`9cb735dfc6`, 2026-10-14T13:27:06Z, subject `v7.0.0: stamp Round-9 closure`) to v10.0.0 (`13cbe48de4`, 2026-11-15T05:22:47Z): 0018 section 2 reads "from the previous closeout stamp to its own". That is 1210 first-parent commits, of which 1139 are merges.
- **Roster pin.** `dev/programme/rosters/wave-r10-groups.json` at `c080e93403e69543564ee334f0772229a28331b3`, the tip of `handoff/audit-r10-roster` when read (548 groups). Every roster-derived command in the record names this sha. The builders named in the record (R11-INTAKE-R10-RESIDUE, R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER) are carry-receivable groups of the roster `check_scopes.py` reads at the ref.
- **Terms.** 1 of 13 has a value: `first_pass`, 0.5058 by `flow_metrics.py` and 0.5138 by `review_strength.py`. 0018 names both, and they count different populations, so the record carries both. The other 12 are `no_read`, each with `would_read` and `builder`. The table in 0018 section 2 gives `none` as the enumerator for `regret`, `operation`, `unowned`, `escapes`, `injected`, `coverage`, `unexamined`, `lead_time`, `closure_slip` and `tokens_per_change`. The examined count of `generality` has none either. `product_green`'s named enumerator prints `A_gate  unread (runs.json)`.
- **Escapes, by hand.** The matching rule, the two commands that print the 98 candidates, and the ruling classes are in the ledger's header. 26 escapes fall in the window: 15 from owner reports and 11 from outside reports. 6 more are owner reports dated the stamp's own day, 2026-10-14, which no tracked record gives an hour for (their issues were opened on 2026-10-15 by the orchestrator). 1 was caused and caught before a release (R10-HOTFIX-REFERENCE-BASIS). 65 candidates are ruled out, each with its reason. 7 escapes are owned by `none`, and that is `unowned.by_hand`. 3 named causes (pull requests 2411, 3404 and 3587) over 155 production merges give `injected.by_hand` 1.94 per 100.
- **Where this differs from the revised evaluation (`eval/r11` 7891b714f8, a lead, never copied).**
  - `escapes`: 26 against 30. The evaluation counts four rows this ledger rules out. R10-BUFFER-STORE, R10-LEARNED-STORE-LOAD and R10-COP-GATE-E were found by fixer seats. Such a report is neither a judged finding nor an outside report, so it is no objective bug by 0018 section 2's definition. R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE is classed `NEED` by its own feature triage.
  - Stamp-day rows: 6 against 7.
  - `injected`: its denominator is 155 production merges. The evaluation's 162 comes from `machinery_ratchet.py --window 1210`, but that flag counts merges, and the window holds 1139 of them. 1210 reaches 71 merges into round 9.
  - `unowned`: 7 against 8. R10-HOTFIX-FLOW-SETPOINT-STUCK is owned by D1, following the evaluation review's R6.
  - `first_pass` matches the evaluation to the rounding.
- **What `check_scopes.py --round 11` prints.**
  - On this branch alone: 1 gap, `dev/audit/yardstick/round11/EVALUATION.json is not in the tree`.
  - On a throwaway merge of this tip with `eval/r11` 7891b714f8: 48 gaps, 47 `card ... carries no owner decision` and 1 `review is not an approve verdict`.
  - The same evaluation without this record: 49 gaps, the extra one being `dev/audit/yardstick/round10/OBJECTIVE.json is not in the tree`. This record removes that gap and adds none.
- **Not followed as written.** 0018 section 5 says "The orchestrator writes two things and no others: a closing round's objective record, once", and section 6 says the record is one "which the orchestrator writes at closure". This record is written after the close, by a record seat working for the round-11 orchestrator. The orchestrator publishes it, and tvofi's approving review makes it his.
- **Layout.** `tests/layout.json` gains `dev/audit/yardstick/**` in its `dev/audit` category. Without it, prepr's CI predict printed `PREDICT tests / fast (3.14) LAYOUT placement: dev/audit/yardstick/round10/OBJECTIVE.json is in 0 categories of tests/layout.json` and the same for the ledger. `eval/r11`'s `round11/EVALUATION.json` sits under the same directory and needs the same line. The file is code-owned (`/tests/layout.json @tvofi`), as `dev/audit/yardstick/` is.
- **Privacy.** Nothing from tvofi's diagnostics download is in either file. Every brief sentence quoted in the ledger is roster text already tracked.

## Head

`7f0a55487c8fe9f4910f3c228bce3fb4b90844c3`, one commit on `origin/main` `26dbf7c43e`. Read the diff three-dot.

## Mutation proof

n/a: two record files under `dev/audit/yardstick/`, which `scopes.json` excludes from every universe, and one category glob in `tests/layout.json`, a manifest with no code. The glob's control is the layout check itself: without the line, prepr predicts the two `LAYOUT placement` reds quoted in Summary. With it, `python3 tests/layout.py --enforce` lists 9 category findings, all present on main, and none of them is under `dev/audit/yardstick/`.

## Null control

Without this record, `check_scopes.py --round 11` on the same evaluation prints the missing-record gap (49 gaps). With the record it prints 48 gaps and no line naming `round10/OBJECTIVE.json`. Any refusal of a term, a builder or an enumerator would print such a line. `check_scopes.py --repo . --ref HEAD` stays rc 0 with `unclassified=0`.

## Figures

- first_pass: `python3 tools/audit/seat/flow_metrics.py --repo . --window 2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --roster c080e93403e69543564ee334f0772229a28331b3:dev/programme/rosters/wave-r10-groups.json --prefix R10-` printed `first-pass yield 436/862 (0.51); merged with no bus verdict 18`
- first_pass: `python3 tools/audit/seat/review_strength.py --repo . --window r10=2026-10-14T13:27:06Z..2026-11-15T05:22:47Z --roster c080e93403e69543564ee334f0772229a28331b3:dev/programme/rosters/wave-r10-groups.json` printed `incidence 214/909 (0.24) first-pass 467/909`
- production merges in the window: `python3 tools/audit/machinery_ratchet.py --measure --repo . --head 13cbe48de4 --window 1139` printed `"production": 155`, `"window": 1139`
- merges in the window: `git rev-list --first-parent --merges --count v7.0.0..v10.0.0` printed 1139
- generality denominator: `python3 tools/audit/check_scopes.py --repo . --ref 13cbe48de4 --population` printed `LEVELS: 195`, `PAIRS: 18696`, `NO-READ AXES: 2`
- product_green: `python3 tools/audit/seat/scorecard.py report --dir <empty> --train-log <empty>` printed `A_gate  unread (runs.json)`
- releases in the window: `git tag --contains v7.0.0 --merged v10.0.0 -l 'v*' | grep -vx v7.0.0 | wc -l` printed 24
- escapes candidates: the two commands in the header of `dev/audit/yardstick/round10/escapes_hand.tsv` printed 98 groups
- classification: `python3 tests/closure.py select --diff origin/main` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py` and `tests/layout.py`, reached by `tests/layout.json`)
- record check: `python3 tools/audit/check_scopes.py --repo . --ref HEAD` exit 0, `unclassified=0`

## Red checks

none known at this head; the orchestrator reads the check-runs.

## Forward-carry

none

## Friction

none
