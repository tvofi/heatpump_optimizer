Fix review: blocked 3d31fc52565e96b08a330ba55b8c0027e2c42a5b harness: class-open tools/audit/harnesses/r9_fr3_family_consumer.mjs:43

bus-nonce: 933bbfca5aa7663fd6e21b00e0aec849
Reviewer: r9c-rev-2014, round 1, detached worktree at 3d31fc52565e96b08a330ba55b8c0027e2c42a5b (live PR head re-read at posting time: same SHA). Merge base 59b5ac6e4594b42cd5579cca182a743c25f4c48d. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2014-evidence

## The block (step 6, open the class)

The body and dev/audit/rca/R9-RCA-2004.md section 4 name the class "moved program paths executed at the old spelling (d)" and say the search found three executed-and-broken seams (friction_issues.mjs STATS_TOOL, preflight.sh corpus_filter, the env-matrix base driver) plus two frozen round harnesses. The class reaches one more live seam that is neither in the diff nor dispositioned:

- `tools/audit/harnesses/r9_fr3_family_consumer.mjs:43` reads `path.join(ROOT, '.claude/workflows/friction_issues.mjs')` and imports a stripped copy of it. That is the R9-FR-3 consumer harness for the file this PR edits. It is not under a frozen `tools/audit/round*/` directory.
- RESULT fr3_consumer head: rc=1, `ENOENT ... .claude/workflows/friction_issues.mjs` (fr3_consumer_head.txt). The same line is present at the merge base, so this is pre-existing since #1919 and was not introduced by the diff.
- No gate catches it. tests/closures.json lists it only as an `inert_reads` entry of tests/harness_headers.py, which checks the header and does not run the file.
- The body's enumeration rule misses it. That rule covers string constants matching `^(export )?const [A-Z_]+ *= *'` and spawn/exec/node/python3 lines; this line is a `readFileSync` + dynamic import inside a `const src =` expression. I re-ran the rule over the 140 tests/layout.json retired-old paths absent at HEAD, and it tags this line NEITHER (body_rule_enumeration.txt). The rule is narrower than the class it claims to enumerate, so the RCA's "executed and broken: three" cannot be re-derived as complete (step 8).
- The forward-carry does not cover it. The R9-RO-8 roster entry on handoff/audit-r9-fixplan carries (a) since-null and (b) old-path launches "for every unit this group moves". RO-8 is the audit-evidence move, and friction_issues.mjs was moved by RO-6 (#1919).

Remedy (any one): repoint line 43 to the sibling path the way this diff does for STATS_TOOL (one line, beside the file it reads); or disposition it by name in the body and the RCA section 4 with an owner; and widen the stated rule to cover read/import of an old path, or say why it does not.

## Everything else checked, and it passes

- Step 1 mutation, friction_issues.mjs: STATS_TOOL_PATH resolved back to `.claude/workflows/policy_lint.mjs` gives self-test rc=1 with `FAIL the stats tool this lane spawns and quotes is a file`, `100 passed, 1 failed`. Restored gives rc=0, `101 passed, 0 failed` (selftest_mut.txt, selftest_head.txt).
- Step 1 mutation, preflight.sh: corpus_filter's lint path reverted to `.claude/workflows/` gives `check policy corpus -- NOT compared`. Head gives `ok policy corpus -- current with origin/main` (preflight_mut.txt, preflight_head.txt). The tests/entities.py arm 5 was not run, because load was about 250 against the 80 gate; I cite CI's run.
- Step 2, the finder's harness (#2004: policy_lint --stats plus the filer dry-run), same stats file at both ends:
  - stats: `harness` 6 / 8 over 59 merged PRs. The body says 5 / 7 over 57; the window gained 2 merges since, so this is not a contradiction (stats.txt).
  - base filer (59b5ac6e's friction_issues.mjs): rc=1, `refusing: .claude/workflows/policy_lint.mjs --normalize-friction-keys did not answer` (dryrun_base.txt).
  - head filer: rc=0, would update #1985 / #1990 / #2004 and file `other` and `conflict` (dryrun_head.txt).
- Step 4: no claim file is in the diff. Step 5: VERSION, the manifest and the notes heading are untouched.
- Step 7: the body's Head names 3d31fc52..., the head I measured.
- Step 10: the R9-RO-8 roster entry carries since-null and old-path launches, with a null control.
- Step 11: check-runs at head (checkruns_head.tsv, 36 runs). Red: nightly-status and delivery-status, both named and answered in the body as main's (the diff reaches only its own delivery row). budget-raise-gate is **cancelled**, not red; the orchestrator should rerun the cancelled twin before merge. coverage and CodeQL Analyze (python) were still in progress at review time. Earlier heads had no failed runs.
- Step 13: `git merge-tree --write-tree origin/main HEAD` rc=0.
- Policy edit: defect-root-cause.md now names dev/audit/rca/, which matches fold_ledger RCA_DIR, and the generated copies match it.
