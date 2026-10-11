Fix review: merge 5c3fda5e6d25382202adff5345b38fe162c5b6fc

bus-nonce: c89fd1856ec27ddabc84bf04b49e8bb2

Resolution-delta review (step 12, second main merge): the recarry of main
`6918cb4b2` into previous head `cce999733` (merge base `969c3a5c8`). Rounds 1-3
measured the substance; this verdict covers the delta alone.

RESULT carry-201-union = PASS: parses; 12 entries (mb 10, prev 11, main 11);
the branch's BLAS-kernel/D0 entry and main's #2111 row-stale entry are BOTH
present, each intact with all of from/effect/control/remeasure/brief; 0 base
entries dropped; no duplicates; order = base + branch + main. The top-level
`_comment`/`stage` take the branch's versions, which loses nothing: main
changed neither against the merge base (verified field-by-field).

RESULT closures-union = PASS: parses; the merged file is main's version plus
exactly one added line -- the branch's `inert_reads` entry
`dev/audit/harnesses/r9_rc_blas_kernel_red_f21_p3.py` (line 3152); main/#2125's
`dev/audit/rounds/round9/prestudy/boost_drift_refit.py` (line 3662) is present
and identical on both parents, so no duplicate; main's two `seconds` updates
are carried; nothing else changed.

RESULT delta-scope = PASS: `git diff cce999733 5c3fda5e6` names 14 files; 12 of
them are byte-identical to main `6918cb4b2` (main's own files: audit-find.js,
debugger.py, bugclasses.json, finding.schema.json, R9-RC-POSTREVIEW-MERGE.md,
delivery/2110|2111|2124|2125.md, docs/configuration.md, debug_collect.py,
record_row.py) and the remaining ones are this branch's own three (the harness,
delivery/2114.md, tests/features.py) plus the two resolution files. No third
thing changed.

RESULT production-tree = PASS: `tests/features.py` blob
db5db5c6134617811620dde150218c7a8a7f64e9 and `optimizer.py` blob
523eb5d0b5cfd794140597361f779feb36f18197 are identical to `cce999733`.
`custom_components/heatpump_optimizer/debugger.py` differs from `cce999733`
because main itself changed it; the merged blob is byte-identical to main's
(152d8d174...), so the resolution authored nothing there. Rerun at the head:
`PYTHONPATH=tests/hastub python3 tests/features.py` rc=0,
`ALL 3986 FEATURE CHECKS PASSED`, `RESULT f21_p3_two_zone=1 j_plain=110.436632
j_continuation_off=111.267093 continuation_gain=+0.830461
j_seeded_half_price=110.129674` and the single-zone null
`continuation_gain=+0.000000` -- the reviewed head's figures, unchanged.

RESULT red-checks = PASS: the body's `## Red checks` names `closures` and
`fast (3.14)`, both answered. The check-runs API at
5c3fda5e6d25382202adff5345b38fe162c5b6fc shows ZERO red conclusions:
`closures` success, `fast (3.14)` success, coverage, arch-score, mutation,
briefs, pr-contract, delivery-status, nightly-status, typing all success.

RESULT local-cheap-checks = PASS at the head: `python3 tests/layout.py` rc=0,
`layout: GUARD: 0 refusal(s) against 6918cb4b213`; `node
tools/policy/brief_lint.mjs dev/programme/carries/carry-201.json` rc=0,
0 errors 0 warnings -- so the union file is lint-clean under the linter the
`briefs` job runs.

Round: 4 (resolution delta of the second main merge; the substance was
measured at rounds 1-3 and stands).

Head measured and still the branch head at posting:
5c3fda5e6d25382202adff5345b38fe162c5b6fc.

Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2114d/evidence/
(head.txt, delta-files.txt, head-vs-main-files.txt, carry201-union.txt,
closures-union.txt, checkruns-head.txt, features_head.log, layout_head.log,
brieflint_head.log)
