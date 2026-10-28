# `selftest_wiring.py`

- `selftest_wiring.py` — refuses a self-testing file under `tools/` (widened
  from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:`
  line, comments removed, invokes with its self-test (`--check`,
  `--self-test`). Runs first among the seat steps of
  `instrument-self-tests`. When: adding a tool with a `--self-test`; add its
  step in the same pull request. Refusal: each unwired file by path; a
  mention in a comment, a step name or a `--check` call does not wire it.
