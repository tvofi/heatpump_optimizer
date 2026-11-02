Fix review: merge 431bc33f1e73f04ddf9befd8ef98b20fa7e0b538

bus-nonce: 910474bd1d35ab843b3f1aa03a0f21f2

Round 1, full review.

## Head

431bc33f1e73f04ddf9befd8ef98b20fa7e0b538 (PR head, measured from a detached worktree; merge base 8f286293b = origin/main, so the diff is exactly 2 files: tools/policy/policy_lint.mjs +19, dev/programme/delivery/3165.md +1). Nothing else touched: no machinery_ratchet.py, budgets, governance.yml, entities.py, prepr.sh; no VERSION/manifest/RELEASE_NOTES change; claim files untouched; no host path in added lines.

## Red checks

None. Check-run set read at this head (45 runs, all pages): every concluded run is success, skipped or neutral(CodeQL, later success). merge_train classify: GREEN rc=0. policy-docs, graders-head-copy, instrument-self-tests, closures, coverage, mutation, pr-contract all success.

## Findings

- The brief expects a DECLARED entry for tools/audit/machinery_ratchet.py in field_coverage.mjs; this PR does not carry it, and the body says so. I confirmed the deferral is correct: with the entry added on this head, field_coverage.mjs reports "DEAD registry: DECLARED `pinned tools/audit/machinery_ratchet.py` is no longer in the derived set" (ev/fc_entry_present.txt), because the pinned set derives from codeowners_gap.py PINNED lines and nothing pins that file until part 2. Without the entry the head is clean (RESULT dead=0 refused=0, FIELD COVERAGE ok). So including it would deadlock part 1; it must ride part 2 together with the governance.yml pin, and become live once the file exists. Task owed after merge: part 2 lands the field_coverage entry and the pin in one PR. Carry: R10-MACHINERY-RATCHETS

## Evidence

- Mutation: dropped the regex line (1-line deletion) -> policy_lint.mjs "FIXTURE OVER-FIRES: checkCoverage reported the grader data dev/governance/config/machinery_budgets.json", rc=1 (ev/mutant_lint.txt). Head unmutated: "FIXTURE ok: 93 error(s) hold 260 pins", TOTAL 0 errors, rc=0; --self-test same.
- Non-widening: regex tested directly (ev/regex_controls.txt): machinery_budgets.json true; config/notes.md false; config/sub/x.json (nested) false; dev/governance/other/x.json false; config/X-y.json false. The acceptance's second pin requires notes.md to still report exactly once and it does.
- field_coverage.mjs at head: RESULT read=53 ignored=28 declared_none=36 blind=0 dead=0 refused=0; --self-test ok (undeclared/dead/missing-arm probes all ok). With the extra entry: dead=1.
- python3 tests/structure.py: STRUCTURE RATCHET PASSED; no budget file in the diff.
- Scoped gate: closure.py select --diff <merge-base> prints "MODE: FULL -- every test script runs" (ev/closure_select.txt); CI ran the full gate and it is green (cited, not re-run).
- policy-docs CI: it grades with the BASE copy of policy_lint.mjs and field_coverage.mjs. This PR adds no policy path (only exclusion + delivery row), so base graders accept it; green, consistent with the body.
- merge-tree: git merge-tree --write-tree origin/main 431bc33f1e73f04ddf9befd8ef98b20fa7e0b538 exits 0 (tree ef39cdb1c), no conflict.
- Body figures (260 pins, 258 on main, dead=1 control, rc values) re-derived at this head; the 258 baseline was not re-run on main.
- Forward-carry: body says none; the part-2 dependency above is the only handoff, stated in the body.
- Round 1.
