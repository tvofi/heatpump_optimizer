# `check_scopes.py`

- `check_scopes.py` — proves the finder scopes are disjoint and complete
  within each dimension, cover the tree, and hold each dimension's own
  `territory` inside the files its seats own, from `scopes.json`. When:
  starting an audit round (`audit-find` runs it in Prepare and refuses the
  round on failure), splitting one, or adding a file a dimension must read.
  Refusal: a cell owned twice or by nobody; a tracked path in no universe;
  a path a dimension's `territory` matches that no seat of that dimension
  owns. The perturbed-scope `--self-test` is the null control.
