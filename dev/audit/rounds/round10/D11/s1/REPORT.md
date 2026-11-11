# D11-s1 (step D11.M1) — round 10, baseline 17f1c55fad1b

Method: M1 mechanism inventory, partial; deep probe on the `.claude/settings.json` hooks.

## Findings
- D11-s1-01 (low, hygiene/bug): `.claude/hooks/pre-edit.sh` reads only top-level
  `new_string`/`content`/`new_source`; a MultiEdit payload (`edits[*].new_string`) that writes a
  `## v9.9.9` heading into RELEASE_NOTES.md off main exits 0. Edit control exits 2.
  Harness `pre_edit_multiedit.py`: escaped=1; `--perturb` (also read `edits`) -> 0.
  Seam rule: `grep -n 'k in ("new_string"' .claude/hooks/pre-edit.sh`.

## Non-findings
- `bash .claude/hooks/pre-edit.sh --self-test` -> 16 passed, 0 failed.

## Unfinished
- M1 rows for the ruleset, required checks, policy_lint classes, brief_lint, structure.py, claim files, prepr.sh: not inventoried.

## Exposure
- None read from GitHub; local tree only.
