# `check_scopes.py`

- `check_scopes.py` — proves the finder scopes are disjoint and complete
  within each dimension, from `scopes.json`. When: starting an audit round
  (`audit-find` runs it in Prepare and refuses the round on failure) or
  splitting one. Refusal: a cell owned twice, or owned by nobody — the
  perturbed-scope `--self-test` is the null control. D5 and D6 also: a seat
  over its `ledger.max_units` of `text_ledger.py` units, a D6 document or a
  D5 comment carrier (a suffix `text_ledger.D5_SUFFIXES` reads) neither
  measured nor named `static`, and a ledger dimension drawing no `classify`.
