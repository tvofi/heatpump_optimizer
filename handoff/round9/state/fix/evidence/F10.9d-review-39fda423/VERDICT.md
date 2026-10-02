Fix review: blocked 39fda4233ca66a933d3539a9bcd05847672ec3e3 mutation: closure.py check()'s INERT READS UNDER-APPROXIMATED refusal, _fold_inert_reads and _exec_record's audit-hook inert_reads line each survive every committed check

PR #1837 (R9-F10.9d), round 1. Measured head 39fda423 (merge base with main 3bd6f122). Briefs current (no briefs diff vs main). merge-tree vs origin/main: clean.

## What holds (verified by me)
- RESULT recording: `closure.py record tests/harness_headers.py` (py3.13 + requirements-ci, strace) -> inert_reads = DISCLAIMER.md, LICENSE, docs/audit-2026-08.md, docs/audit-2026-09.md, docs/backlog.md; equals the committed table. `closure.py check --partial` on it: rc 0.
- RESULT census: `N=120 INJECT=0|1 tools/audit/fastpath_census.py` at origin/main 3bd6f122 -> ELIGIBLE 0 of 120 both; 50 moved pairs; unrecorded 50 -> 30; class counts full 43, claim 29, grader 27, workflow 17, overlap 7 (plus budget 3, unmentioned); every moved pair carries one of those five; no pair has unrecorded alone; --files list identical to the body. Per-merge lines match the fixer's m120_*.txt (whitespace only). cen0.txt, cen1.txt here.
- RESULT predicate mutants (merge_fastpath --self-test, mut.py): reads->None kills 2 (the body's red-first pair, confirmed); drop sibling clause kills 1; drop is_inert kills 1; any->all kills; ignore `always` kills 3. Drop `f in reads[0]` survives but is EQUIVALENT (reads[1] is the parents of reads[0]).
- RESULT recorder mutant in _union_strace (drop the inert_reads union): entities.py rc 1, killed.
- Soundness reasoning on the predicate: any change that alters what harness_headers.py concludes about links must edit a file it opens (refused) or a non-INERT file (refused); I found no pair that escapes.

## Why blocked (mutc.py, mutc.log; each run: entities.py, closure.py selftest, merge_fastpath --self-test, py3.13 with tests/hastub)
- C4: `if missed:` -> `if False:` in check() (the new INERT READS UNDER-APPROXIMATED refusal): all three rc 0. SURVIVES.
- C3: _fold_inert_reads iterates nothing (merge writes no inert_reads): all rc 0. SURVIVES.
- C1: _exec_record's `"inert_reads": [...]` -> `[]` (the audit-hook path, the only one where strace is absent): all rc 0. SURVIVES.

The table the fast path now trusts is guarded only by check()'s new block, and deleting it fails nothing; with C3 or C1 (no-strace recording) a merge writes a table that omits DISCLAIMER.md, which turns a DISCLAIMER.md edit ELIGIBLE -- the exact #1823 false-claim pair. The body's "Table mutant" was a hand run of `closure.py check`, not a committed pin, and its "all five [seams] are covered by the checks above" is not true for check, _fold_inert_reads or _exec_record.

## Owed for merge
Committed checks that fail under C1, C3 and C4: e.g. an entities.py (or closure selftest) case that runs `merge` on a synthetic records dir with inert_reads and reads them back (full and --partial), one that runs `check` against a committed-table fixture missing a read and wants the refusal, and an audit-hook-only record (no strace) that wants the INERT read filed. Re-run these three mutants at the new head and quote the kills.

## Not re-run (cited)
Gate and mutation table: CI's, per fix-review.md step 11. CI on the new head was still running when I wrote this; the head has moved past 39fda423 (author seat's delivery row), which does not affect this finding.
