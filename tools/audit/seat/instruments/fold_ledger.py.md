# `fold_ledger.py`

- `fold_ledger.py` — folds a round's JUDGE.json and sweeps into
  `bugclasses.json`, and checks the register against the judges. When: after a
  judge lands, and before quoting the bugclass register as current state;
  `sync` after any hand edit of `finding.schema.json`, which rewrites
  `audit-find.js`'s generated CLASS_GUESS and FINDING_REPORT (fold runs it).
  `yield` prints, per rule, the instances of the classes naming it (`rules`)
  recorded before and after the rule's first add, every date derived from git
  at `--ref` and none stored; `no-class` for a rule no class names. When: a
  round's evaluator scores a rule object (decision 0018 section 3).
  Refusal: `check` refuses a register that drifted from its judges — re-quote
  the register, not a memory of it.
