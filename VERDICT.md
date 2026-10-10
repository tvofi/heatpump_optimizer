Fix review: merge 6b21ba53028820a85af9ebde83d0fd310ce0a0e4

bus-nonce: 1c8d506e7bc628a06fa948da495a240e

Delta review, round 2. Prior round blocked `carry-missing`; the fix is
judged only on the delta from `3f82aba33` to `6b21ba530`.

## What the delta contains

`d57cd1e3d` ("carry the beat's window-reach to carry-201") adds 7 lines to
`dev/programme/carries/carry-201.json` and nothing else; `ce5068f5f` and
`6b21ba530` are merges (the branch's previous head, and `origin/main` at
`d3dbf2c3f`). Three-dot against main the branch changes exactly three files:
`carry-201.json` (+7), `dev/programme/delivery/2111.md` (+1, the lane's own
open row), `tools/audit/seat/record_row.py` (the fix, unchanged this round).

## RESULT lines

- RESULT carry-real: `carries[10]` of `carry-201.json` exists at the head
  with all five sibling fields; `brief_lint.mjs carry-201.json` prints
  `0 error(s), 0 warning(s)`. The entry names the destination a seat finds
  (the standing carry file at #201), states the owed action concretely
  (`record_row.py --enumerate --since v6.7.13`, then `--plan`/`--apply` at a
  worktree of origin/main), carries the measurement (18 planned in the
  v6.7.17 window vs 103 from v6.7.13) with its null control (a last tag at or
  before v6.7.13 equalizes the counts; a plan of 0 at v6.7.13 is the other
  arm) and a re-measurement instruction that refuses to carry the frozen
  18/85. The declining sentence is gone (`grep "needs a destination issue"`
  over the PR body: 0 matches), and the body's `## Forward-carry` finding 2
  now names the file and says the entry is in the diff to be opened.
- RESULT code-unchanged: `git rev-parse <sha>:tools/audit/seat/record_row.py`
  answers blob `585b51f264e6e7892e4864f991705f9dddb37e0c` at `3f82aba33`,
  `ce70213ae`, `d57cd1e3d` and `6b21ba530` — byte-identical; the diff on the
  file between the two review heads is empty. No behaviour change.
- RESULT mutant-M4: reproduced. My own driver, scratch copy, seat
  interpreter 3.14.7: the driver's exact M4 (`return want != now`, which
  drops the grant's None boundary *and* the direction clause) reddens 3 arms
  verbatim (`a merged row is never rewritten back to open`, `a seat's
  multi-line disposition is neither planned nor rewritten`, `a status a row
  writer never emits is outside the grant`); dropping the None boundary alone
  reddens 2 — the prior round's 2 was its own narrower mutant, and the body's
  3 is genuine. Both clauses are separately covered (M4a: direction alone,
  1 arm).
- RESULT mutant-M10: reproduced. `return now is not None` reddens 5 arms
  verbatim, matching the corrected 4 -> 5.
- RESULT mutant-M7: reproduced. The loosened status regex reddens 1 arm
  (`a status a row writer never emits is outside the grant`). The prior
  round's survivor was its own mis-built mutant.
- RESULT census: reproduced at the body's stated head. My own census over
  the production `line_status`/`rowed_line`: `d57cd1e3d` reads 503 = 248 +
  104 + 151 and `ce70213ae` reads 502 = 248 + 103 + 151, exactly as the body
  states. At the PR head `6b21ba530` the same rule reads 506 = 248 + 107 +
  151; the difference is exactly `dev/programme/delivery/2072.md`,
  `2075.md`, `2083.md` — main's own rows brought by the merge, not this
  branch's change. The body's sentence "the PR tree is that code head plus
  the row" is imprecise by those three main rows; no figure it quotes is
  moved by them.
- RESULT checks: no red conclusion on the head's check-runs (only
  in-progress `closures`/`Analyze (python)` and skipped lanes); nothing to
  answer. Claim files byte-identical to the merge base; VERSION, manifest,
  RELEASE_NOTES heading untouched by the branch diff.
- RESULT self-test null: unmutated `--self-test` at the head, seat
  interpreter: `record_row self-test: all checks passed`, rc=0.

## Unverified

The 18/103/85 window figures and the 161/18, 105 = 103+2 and re-plan-0
figures are the prior round's verified numbers restated; I did not re-derive
them this round (they were API-confirmed there and `record_row.py` is
byte-identical since). The `harness_headers` `ALL 109 PASSED` line I did not
re-run (CI's run_always lane covers it; it is green on the head).

## Verdict

The carry defect is cured in the tree, not promised; the code the prior
round verified is the code at this head, unchanged; both prior caveats
resolve as artefacts of that round's own mutants, and every re-taken figure I
could run reproduces. Merge.
