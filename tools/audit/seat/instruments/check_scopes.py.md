# `check_scopes.py`

- `check_scopes.py` — proves the finder scopes are disjoint and complete
  within each dimension, from `scopes.json`. When: starting an audit round
  (`audit-find` runs it in Prepare and refuses the round on failure) or
  splitting one. Refusal: a cell owned twice, or owned by nobody — the
  perturbed-scope `--self-test` is the null control. D5 and D6 also: a seat
  over its `ledger.max_units` of `text_ledger.py` units, a D6 document or a
  D5 comment carrier (a suffix `text_ledger.D5_SUFFIXES` reads) neither
  measured nor named `static`, and a ledger dimension drawing no `classify`.
  `--round N` adds decision 0018's start evaluation: an accepted card holds
  the start only if its `gates_finders` is true; one that gates no finder and
  is unmerged prints `PARALLEL <card>`. `--round N --open-cards` prints P3's
  input as JSON when the finders finish: those cards still open at `--ref`, and
  the roster's open groups whose `gates_finders` is not true; exit 1, with an
  `UNMARKED <card|group>` line, while an accepted card or open group carries
  no boolean.
