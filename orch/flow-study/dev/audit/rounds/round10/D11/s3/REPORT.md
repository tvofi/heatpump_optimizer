# D11-s3 — round 10, step D11.M4 (perturbation), baseline 17f1c55fad1b

## Method
M4 asks that each mechanism move under a one-line change. I drove two kinds of perturbation:
the existing mutation lane (`node tools/policy/policy_lint_mutants.mjs`, which empties each
wired check and demands a red acceptance), and a hand perturbation of the `.claude/hooks`
mechanisms, which no mutation lane covers.

## Findings
### D11-s3-01 (low, bug): pre-edit hook's RELEASE_NOTES heading refusal does not reach MultiEdit
The `PreToolUse` matcher in `.claude/settings.json` names `MultiEdit`. The hook's program only
joins top-level `new_string`/`content`/`new_source`. A MultiEdit carries its text in
`edits[].new_string`, so a branch MultiEdit that adds `## v9.9.9` gets through.
Harness: `dev/audit/rounds/round10/D11/s3/pre_edit_multiedit.py`. Result: refused_heading_payloads=2 of 3,
multiedit_refused=0, null_refused=0. With `--perturb` (a one-line join over `edits`) the counts are 3, 1 and 0.
The self-test has no MultiEdit case (16 passed). `stamp.py` remains a backstop after the merge.
Property: each text-bearing key of every matched tool's `tool_input` reaches the content checks.
Seams: `grep -n 'matcher' .claude/settings.json` crossed with the keys read in `HPO_PRE_EDIT_PY`.

## Non-findings
- `policy_lint_mutants.mjs`: MUTANTS ok. All 11 corpus checks and all 12 record checks turn
  the acceptance red when they are emptied.
- `bash .claude/hooks/pre-edit.sh --self-test`: 16 passed, 0 failed.
- `bash .claude/hooks/stop-selfcheck.sh --self-test`: 26 passed, 0 failed.

## Unfinished
M4 was not applied to the ruleset on `main` (that needs a live API read with both arms), to `tests/structure.py` budgets,
to `brief_lint.mjs`, to the claim files or to `prepr.sh`.

## Exposure
Read tree files only. I read no GitHub API and no git history.
