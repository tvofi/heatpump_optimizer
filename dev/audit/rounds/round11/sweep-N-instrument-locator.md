# Class sweep: N-instrument-locator (round 11, D14 steps 3-4)

Class: an audit instrument reports the wrong line/file for the units it counts. Finding: D5-s8-07 (`tools/audit/text_ledger.py:scan_c_like`). The class has no entry in `dev/audit/config/bugclasses.json` at `handoff/audit-r11-register` (28b864af6d); status is therefore unrecorded (treated as `open`).

## Enumerator
`python3 dev/audit/rounds/round11/D14/N-instrument-locator/enumerate.py tools` lists every function under `tools/` that hand-maintains a line counter (`+=` on a name containing `line`, or `ln`) instead of taking locations from ast/tokenize/enumerate.
- Positive control: lists `tools/audit/text_ledger.py:scan_c_like` (the finding). PASS.
- Null control: `--null` (enumerate-based clean fixture) prints COUNT 0. PASS.
- Perturbation: `--perturb` (fixture plus one `line += ...` line) prints COUNT 1. PASS.

Result on tools/: 10 seams.

## Dispositions
| seam | disposition | reason |
|---|---|---|
| tools/audit/text_ledger.py:scan_c_like | **instance** (judged site, D5-s8-07) | probe: escaped newline in a JS string; comment on line 3 reported at line 2 |
| tools/audit/seat/mutant_run.py:added_lines | guarded | counter is reset from each `@@ +N` hunk header of `git diff -U0`; with zero context only `+` lines advance the new-file line, which is what it does |
| tools/audit/check_scopes.py:population | not applicable | `lines +=` extends a list of output text, not a locator |
| tools/audit/judge_batch.py:render_table | not applicable | list of table rows |
| tools/audit/merge_throughput.py:render_board | not applicable | list of report lines |
| tools/audit/seat/beat_jobs.py:roster_drain | not applicable | list of report lines |
| tools/audit/seat/closeout.py:render_report | not applicable | list of report lines |
| tools/audit/seat/handover_prompt.py:pickup | not applicable | string concatenation of a prompt line |
| tools/audit/seat/review_strength.py:pr_facts | not applicable | sums added+deleted line counts (a size, not a location) |
| tools/pr/depgraph.py:check | not applicable | list of report lines |

Instances beyond the finding: 0. Barrier: none in place (`barriered: false`); proposed barrier is a tests/ check comparing `units_of` line fields against the file text for JS/shell fixtures with escaped and unterminated-string newlines (the s8 harness shape).
