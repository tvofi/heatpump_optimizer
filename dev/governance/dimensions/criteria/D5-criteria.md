# D5 acceptance criteria: docs structure and code comments

The owner's brief is quoted in `D5.md`. Claims in docs are D6's (`D6.md`).

Drafted by a fixer seat under mandate 6893738184 (scope all);
binding as the owner's words until the owner rewrites them.
A finding names the statement it fails.

Comment units: what `python3 tools/audit/text_ledger.py units --dim D5`
lists for the seat's cells.

## Comments: "concise but precise and easy to understand"

- **C1 precise: true.** Every unit is true of the code it sits on, shown by
  an executed check of that code (`D5.md` step 4). Fail: a unit the check
  contradicts.
- **C2 precise: resolvable.** Every identifier, path and issue a unit names
  exists (`git grep -n` at the ref, `git ls-files`), and every quantity
  carries its unit or names a dimensionless quantity. Fail: one that does not.
- **C3 concise: no restatement.** Delete the unit; if every fact it stated
  is readable from the identifiers and literals of the statement it sits on,
  it restated that statement. Fail: such a unit.
- **C4 concise: why over history.** Split a unit's sentences into those
  stating a reason, constraint or unit and those recounting history (who
  measured, which round, what the code used to do). Fail: history sentences
  are more than half of the unit and deleting them loses no reason or
  constraint.
- **C5 easy to understand.** No sentence over 40 words; a term the unit
  needs is defined in it, in the code it sits on, or in a document it names.
  Fail: a longer sentence, or an undefined term a reader of the code alone
  cannot resolve.

## "Docs structure, flow and content"

- **S1 reader paths.** The three paths of `D5.md` step 1 reach their goal.
  Fail: a dead end, a forward reference, or a needed fact found nowhere.
- **S2 links.** Every internal link and anchor resolves; every external link
  answers below HTTP 400. Fail: one that does not.
- **S3 one home per fact.** No paragraph appears twice across `README.md` and
  `docs/*.md` (hash of its whitespace-normalised text). Fail: a repeat.
