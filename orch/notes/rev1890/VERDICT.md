Fix review: merge d6877750729c95dc966c36522a8fe776135908d9

Round 1. Measured at d6877750729c95dc966c36522a8fe776135908d9, still the live head at posting. Diff = tests/run.sh, tests/derive_closures.sh, coverage_tree.sh only; every hunk maps to a body claim; no workflow file touched; VERSION, claim files, fixtures byte-identical. The dispatch's stated scope (workflows/*.yml + delivery row) is not the actual PR; the body states the real files, and no row rides this diff.

RESULT (b) fast job 111389523263: `lane count: nproc=1 ... nproc=4 ... lanes = min(that, 3)`; `TOTAL (3 lane(s))`; 32/32 ok, script set equal to base run 111330336480. Caveat: head job 38.0 min vs that base's 33.5 — stress, alone on the box, rose 302s→408s (slower runner, ~1.35x) and lanes compressed the head runner's serial sum 3247s→2252s; the body's stated base is the 42.9 min median, and 38.0 passes. No timing-sensitive red: drop-commit-(b) did not trigger.

RESULT (a) coverage job 111389523211: features interleaved with the rest, lane walls 720s vs 484s. The body's command vs base f4e8d911b prints 2, not 1 — but two serial main runs also print 2 on the same 28 leaves (freq_control.py:207 flap), and head is uniq=1 vs 4efc5b63: pre-existing serial nondeterminism, not lane interference. My control, disclosed.

RESULT (c) closures job 111389562651: 31 records across three lanes, equal to my dry run and base's (31=31); no UNDER-SCOPED; closures-autofix skipped, no re-record commit; 26 min.

Re-ran myself: (c) dry-run 31=31 and its mutant (30); (b) stand-in-nproc arms (1/3/2). (a)'s local mutant not re-run locally; its CI oracle held.

nightly-status failure is main's (mutation-ledger, run 37108891698, predates the branch); diff touches no REPORTER_INPUTS, exemption holds, pr-contract green.

Body contract: first line, headings, figures resolve, friction none, no closing keyword. merge-tree clean.
