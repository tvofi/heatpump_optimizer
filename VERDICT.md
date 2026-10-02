Fix review: blocked e5301f5e5a070ae3c691df72296a2122691b689e harness: class-open C3 is still an enumeration of junk spellings; `assert True`, `_ = None` and `(_ := 0)` interleaved in uncharged clones each read IMPROVES admissible +14.15

bus-nonce: e4e642c3c5b9d17e58bb81c3c072c08c

Round 2. PR #1851 (R9-EG-A1), head e5301f5e5a070ae3c691df72296a2122691b689e (live head re-read 2026-10-02T15:42:29Z, unchanged). Evidence: evidence/ev-e5301f5e/ (HEAD.txt names the head). The harness is the reviewer's (round-1 rt_14..16 plus round-2 rt_17*), not the finder's or the fixer's.

## Round-1 Blocking 1 (closure) -- RESOLVED

RESULT select(['tests/structure.py']) -> scoped, tests/arch_score.py run: True (round 1: False)   (select-probe.txt)
RESULT control: select(coordinator.py) -> arch_score.py False, arch_score_head.py True (the integration still does not select the calibration, as designed)
RESULT calibration re-run under tests/structure.py DUP_WINDOW_STATEMENTS 2->6 (the run the fixer did not do): a1_B1_copy_cross_module MOVED WORSENS->NULL and a1_G2_dedupe MOVED IMPROVES->NULL, so arch_score.py, now selected, refuses it   (calib-dup-mutant-window6.txt)
RESULT restored: a1_B1 WORSENS -0.2129, a1_G2 IMPROVES +0.2165, as recorded   (calib-r1-harness.txt)

## Round-1 Blocking 2 (C3, `pass`) -- the named spellings are closed, the class is not

RESULT rt_16 (pass, uncharged; round 1 IMPROVES +14.15) now NULL. rt_14 and rt_15 now WORSENS via coord_footprint, with delta-S -0.0029 and -0.0006 (round 1: +16.24 and +14.81). rt_04 NULL. Null rt_00 NULL.   (calib-r1-harness.txt)

The round-2 games are built from the fixer's own 04 script, with the junk chosen outside the widened `is_noop` and coordinator plus footprint-charged functions skipped (rt_17_rv_base.py and three wrappers in the evidence):

RESULT rt_17a_rv_assert_uncharged (`assert True`): IMPROVES, admissible, +14.1502, duplication_copies+14.150
RESULT rt_17a_rv_assign_uncharged (`_ = None`): IMPROVES, admissible, +14.1502, duplication_copies+14.150
RESULT rt_17w_rv_walrus_uncharged (`(_ := 0)`): IMPROVES, admissible, +14.1502, duplication_copies+14.150   (calib-r2-games.txt)

Each is junk with no observable effect, and each splits every clone window exactly as `id(N)` and `pass` did. The widened `is_noop` lists spellings (`pass`, constants, names, attributes, pure calls, `if <const>`), and every spelling it omits is an open game at the same +14.15. A fifth widening will lose to a sixth spelling, so this is class-open (fix-review step 6) and not a missing case. Two ways out, either acceptable:

1. Close it structurally. Make the clone comparison tolerate an interleaved statement: for example, match a window when its statements appear in order within the block, with at most g statements between them. Or drop dead statements by data flow: a statement with no call to a non-pure function and no store that is later loaded. Then add the three rt_17 spellings as cases.
2. Record it as a known limit of a report-only instrument. "no red-team attempt reads IMPROVES" then holds only for the listed attempts. ABOUT.md and the body would say that interleaved junk of any unlisted spelling reads as a dedupe, and the reviewer of a later EG stage would be told to look for it. That is tvofi's call, not mine. I would return merge on it once it is in ABOUT.md and in the A2 brief, which is where the clone target lives.

## Unchanged from round 1 (re-checked only where the delta reaches)

- The round-2 delta is `tests/arch_score.py` (smoke loads structure.py, red-team floor 17->23), `counters.py` C3, the 04 variants, `expected.json` (+36 lines: the six new cases), and `closures.json` (+structure.py, +6 scripts; it is the only entry that moved).
- The main merge brought optimizer.py, policy_lint, check-wave-script, structure_budgets and the mutation ledger. That is main's content with no hand resolution claimed, and it is not judged here.
- Gate edits, the template-sentence sources, forward-carry and untouched version files are as in round 1 and not re-taken.

## CI at this head

Check-runs at e5301f5e (check-runs.json, 15:42Z) are all success, neutral (CodeQL) or skipped. The cancelled pr-contract and budget-raise-gate runs were each superseded by a success, and Analyze (python) is still in progress. "Tests" run 37028348773 is `pending` with no jobs, so closures (whether Linux agrees with the Darwin --single recording of 86 files), fast, mutation and the calibration's CI runtime are UNVERIFIED this round as well. The fixer's ~9 min local figure is theirs, not re-taken.
