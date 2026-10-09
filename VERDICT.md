Fix review: blocked 91b77d0cd3acbc1a5f13c400b6dd60a8910e86f4 other: carry-1922 names judge_batch.py and fold_ledger.py as moved, and they are not; new-reference refusals now get the file-placement hint

bus-nonce: a4e214a01e55fc7f96c82a051e3a0cfa
Seat: review-2072. Round 2, reviewing the delta 71f7a612..91b77d0cd (one commit: carry-1922.json +7, prepr.sh +13 -3). Merge base bd59a4af1b26, origin/main 47b083b03a9d. Live head re-read before posting: unchanged.

Round 1's three items are resolved. Two new defects came in with the delta, and each is a one-line fix.

## Blocking

1. **The new carry entry states something false to R9-RO-9.** Its `control` says the round-runner workflows "name the finding schema, judge_batch.py and fold_ledger.py at their retired paths". Its `brief` tells the stage to re-point "to ... the moved judge_batch.py and fold_ledger.py".
   - Neither script is moved or retired. `tools/audit/judge_batch.py` and `tools/audit/fold_ledger.py` are in the tree.
   - tests/layout.json has no `retired` entry for either.
   - judge_batch.py is named in the `tools` category's own glob (`tools/audit/{judge_batch.py,check_scopes.py,...}`), so its current path is its home.
   - Of the three instruments, only `finding.schema.json` is retired (to dev/audit/config/).

   A carry is read later as established fact, so the stage would go looking for moves that do not exist. The entry's closing "read the destination from tests/layout.json" does not repair a control that asserts the move. Fix: drop judge_batch.py and fold_ledger.py from `control` and `brief`.
2. **The new hint is wrong for the new-reference arm.** The `case` sends every refusal that lacks "it lives at" to "place it where tests/layout.json says". I planted a stale citation line in README.md and got: `new-reference: README.md cites retired path tools/audit/harnesses/: ... -- place it where tests/layout.json says`. A citation is fixed by re-pointing the line, not by placing a file. Round 1's note said only the zero-categories arm needed a different hint. The new self-test row pins that arm only, so this regression is unpinned. Fix: a third hint for `new-reference:` and `unswept:` lines (for example "re-point the citation"), plus a row.

## Verified (RESULT lines)

- RESULT round-1 item 1: resolved. The body gives three samples, each with its check-run id: 30m28s (113574473913), 30m48s (113577108665) and 29m50s (113595667988). These match the check-runs API. It states the local cost as 0.4 to 2.1 s, crediting the reviewer's runs.
- RESULT round-1 item 2: resolved. The step is labelled 6e in prepr.sh and the body. The first commit's message still says 6d (no force-push), and the new commit says to cite 6e; that is acceptable.
- RESULT round-1 item 3: resolved in substance. The body states the class search and carries it to R9-RO-9 in carry-1922.json, apart from item 1 above. brief_lint gives carry-1922.json 0 errors (TOTAL 0 across 44 files).
- RESULT label uniqueness: no duplicate step heading, indented ones included. Simulated merges onto origin/main, with #2067 at 09d2061b and #2073 at 3637f1c7:
  - P7, P3, H, P7+H, P3+H, P7+P3, P7+P3+H, H+P7+P3 and P3+H+P7 all merge with no conflict and pass `bash -n`.
  - The full three-way merge (8edf6ca919) has 22 headings: 6, 6a, 6b, 6d, 6c, 6e, 7.
- RESULT hint: a moved path gives "move it to the new path", rc 1. A zero-categories file gives "place it where tests/layout.json says", rc 1. Null at the head: rc 0, `GUARD: 0 refusal(s)`.
- RESULT self-test at 91b77d0cd: 218 passed, 0 failed (4m07s), including the two new rows.
- RESULT checks: 40 check-runs, all completed. The only failure is nightly-status, which this diff does not reach. CodeQL concluded neutral.
- RESULT diff: four files three-dot (CLAUDE.md, fixer.md, carry-1922.json, prepr.sh), +74 -2. VERSION, the manifest and the notes heading are untouched.

## Non-blocking

- The 6e step comment still says "~0.7 s", while the moved_line header now says 0.44 to 2.10 s.
- "Passes by three orders of magnitude": 1800 s against 2.1 s is about 860x, so at the high end of the cost it is not quite three orders.

Evidence: /Users/timmalmstrom/hpo-seats/review-2072/evidence-r2 (HEAD.txt names the head)
