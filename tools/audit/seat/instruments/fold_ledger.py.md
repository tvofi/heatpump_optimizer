# `fold_ledger.py`

- `fold_ledger.py` — folds a round's JUDGE.json and sweeps into
  `bugclasses.json`, and checks the register against the judges. When: after a
  judge lands, and before quoting the bugclass register as current state;
  `sync` after any hand edit of `finding.schema.json`, which rewrites
  `audit-find.js`'s generated CLASS_GUESS and FINDING_REPORT (fold runs it).
  Refusal: `check` refuses a register that drifted from its judges — re-quote
  the register, not a memory of it.
