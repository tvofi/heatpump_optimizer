Fix review: blocked 09c0bc5ce99c4ed0b27e780d08aa6be28bf06bbd mutant-committed: check_scopes.py's "static and in the universe" refusal is replaced by `pass` (ff9b385bcd), so its own self-test fails at the head

bus-nonce: fc1ede121a04a26556310bff7f4d1471

Round 2 (delta review). Reviewed head ac1607ad7344f75d619dd5f0b2f2c66d12663a3f, head measured 09c0bc5ce99c4ed0b27e780d08aa6be28bf06bbd (ev/HEAD.txt). Scope: delta. The branch's own commits are 3b7b45197a, afcb73580d, ff9b385bcd and 38f90d9be7, plus the hand-resolved merge 02d55e28 and the delivery row. The delta touches no production (custom_components/) code, so the review is not widened.

## Block

Commit ff9b385bcd ("D5.md: the scope line fits the brief's line cap") changes one line in `tools/audit/check_scopes.py` `classify_errors`, and that change has nothing to do with D5.md. The line that refused it went (ev/ff9b385bcd_check_scopes.diff):

    -    errs += [f"static and in the universe: {f}" for f in sorted(stat & uni)]
    +    pass

At the head, a path that is both in a ledger dimension's universe and in its `static` map is no longer refused, which removes half of the line this PR exists to draw. The instrument's own self-test catches it. At the head, `python3 -I tools/audit/check_scopes.py --self-test --repo .` prints `ledger arms: ... line refused True/False/True/True` and `SELF-TEST FAILED`, with the arm `'a static path in the universe is refused': False`, rc=1 (ev/check_scopes_selftest_head.txt).

The body's `## Figures` says the same self-test prints `SELF-TEST passed`, which is false at this head. So is its claim that the line refuses "a path in both".

The fix is to restore the deleted line and re-run the self-test. The figure_lint `ok` for this command means only that the command resolves, not that it passed.

## Findings

none

## Evidence

- (a) The class-open block at ac1607ad is resolved (ev/class_open_plants.txt). I committed each plant on the head and ran `check_scopes.py --repo . --ref HEAD`:
  - The verdict's plant `.claude/workflows/zz-planted.js` is now a D5 unit. It prints `ok D5 ... universe=854`, one more than the unplanted 853, and rc=0.
  - The same comment at `.claude/zz-planted.js` gives `FAIL D5`, rc=1.
  - The D6 null `dev/zz-planted.md` gives `FAIL D6` and `unclassified=1`, rc=1.
  - The self-test's six D5 comment-line arms all print True.
- (b) Hand-resolved merge 02d55e28, `tools/policy/check-wave-script.mjs`: I re-ran the planted cases in `.claude/workflows/audit-find.js` at the head (ev/cadence_plants_head.txt).
  - Null: `227 passed, 0 failed`, rc 0.
  - D5 off-round (`activeIn` true for D5 at any round): `226 passed, 1 failed` on the cadence arm.
  - D11 off-cadence: `226 passed, 1 failed`.
  - D13 off-cadence: `226 passed, 1 failed`.
  - Extra plants, for what main's assertion refused and `byRound` alone would not, because `byRound` filters on `D.CADENCE[d]`:
    - D11 dropped from CADENCE fails 4+ other arms (round-9 every-dimension, dispatch, box B7).
    - D13 dropped from CADENCE fails the same way.
    - D11 never active fails the cadence arm and 4+ others.
  - Every plant main's six lines refused is still refused, so the resolution loses nothing measured. The `(probe, expected)` FAIL line is the checker's uncounted self-probe and appears in the null too.
- Main's own copy of check-wave-script.mjs (origin/main 513a07dfdc) run over the head tree prints `227 passed, 0 failed` (ev/main_checker_over_head.txt), so the base-copy wave-script job should pass.
- Merge: `git merge-tree --write-tree origin/main 09c0bc5c` (origin/main 513a07dfdc0daf09a054826974dbb64bfea9de27) printed one tree, rc 0, with no conflict (ev/merge_tree.txt).
- `text_ledger.py --self-test` at the head: `17 checks, 0 failed`.
- Figures: the D5 line at the head reads `seats=10 universe=853`; the body says 851. The difference is consistent with main's merge adding files. I have not attributed it further, and it is not a block.
- Still at the head: `CADENCE` holds `D5: 2, D6: 2`, as the body states, with p2 carried. That was already reviewed at ac1607ad and is outside this delta.
- CI: `merge_train.py classify 09c0bc5c --pr 3571` printed `WAIT 09c0bc5ce99c4ed0b27e780d08aa6be28bf06bbd pending: gate red: none`. I did not wait longer, because the block stands on a measured local failure. `## Red checks` was not assessed, since no red is reported yet.
