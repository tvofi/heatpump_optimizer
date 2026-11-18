# `selftest_wiring.py`

- `selftest_wiring.py` — refuses a self-testing file under `tools/` (widened
  from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:`
  line, comments removed, invokes with its self-test (`--check`,
  `--self-test`). Runs first among the seat steps of
  `instrument-self-tests`. When: adding a tool with a `--self-test`; add its
  step in the same pull request. Refusal: each unwired file by path; a
  mention in a comment, a step name or a `--check` call does not wire it.
  `--check` also refuses this guide's index and its `instruments/` files
  disagreeing: a line whose file is gone, a file linked twice or by no line,
  or a line naming another instrument than its file's entry. When: adding,
  renaming or removing an entry; its index line moves in the same pull
  request.
