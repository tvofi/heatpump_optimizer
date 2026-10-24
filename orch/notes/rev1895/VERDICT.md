Fix review: merge 81cc117be09ca271f4f22fbbed23ed5157dc7359

First review, dispatched 2026-10-04. Head measured = head posted (81cc117be; re-checked at verdict time).

RESULT self-test at head: 175 passed, 0 failed.
RESULT mutants (restored, cmp-verified): PYTHON-not-passed 174/1; refusal-gutted 172/3; override-trusted 170/5 — the exact rows the body names.
RESULT F1 (origin/main 283eb22f0, ambient 3.11.5): ast.parse entities.py SyntaxError; derive_closures.sh --single wrapper rc 0, recording rc 1/files 1; main's closures_verdict (sourced verbatim) prints "failed while being recorded: tests/entities.py (exit 1) -- fix the script first; a re-derive would record the same truncation". Incident reproduced.
RESULT F2 (head): recorder_python rc 0 -> seat venv 3.14.7; recording rc 0/208 files; "scoped recordings are covered".
RESULT F3: none-parse refusal rc 1, names tools/audit/seat/seat_venv.sh.
RESULT F4: script/rc/how equal True; closures equal repo-relative True, count 208.
RESULT scope: diff is tools/audit/prepr.sh alone; derive_closures.sh, VERSION, claim files untouched; MODE: SCOPED -- 0 script(s) run, 30 scoped out; STRUCTURE RATCHET PASSED; recorder_parses domain = 41 + 70 = 111 files.
RESULT failing-first: 9a04d5e03 adds exactly 13 st rows, all requiring recorder_python absent at that commit.
CODEOWNERS: tools/audit/*.sh pinned/unowned — App approval suffices.
CI: nightly-status the only red, answered (grades main's schedule; prepr named in none of its inputs). pr-contract green at head; body contract, head SHA, no closing keyword — all checked.

Round: 1.

Evidence (absolute): /Users/timmalmstrom/hpo-orch/notes/rev1895/ — VERDICT.md naming measured head 81cc117be09ca271f4f22fbbed23ed5157dc7359 (carried to b8cabfb80db2ea5b627ac3cb2d9ebd4c707eb736 by automatic main merges only).
