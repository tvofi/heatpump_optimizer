Question: CI's `briefs` job runs main's tools/policy/brief_lint.mjs over this head's data and refuses it either way (BOOTSTRAP, fixer.md step 5). Will the orchestrator land p1 = this branch's tools/policy/brief_lint.mjs hunk alone (8 lines, `git diff 154dbb4c61..78325190f8 -- tools/policy/brief_lint.mjs`) as its own pull request, so that p2 (this head) hands off once p1 is on main? A seat may open no pull request, and no data-only edit passes main's grader.

# BLOCKED: r10-closeout-prep-p2 repair round 4

## Done and verified at 78325190f8 (this note's parent)

- BLOCKED.md from round 3 is removed. origin/main 154dbb4c61 is merged as a plain merge commit (626601a933).
- The closures table is repaired. tests/closures.json lists dev/programme/rosters/wave-r10-groups.json in tests/entities.py's closure. That entry came from `./tests/derive_closures.sh --single tests/entities.py` on Linux: a record-only pass merged `--partial --allow-failures`, because the only failure was the F2 check itself. A second `--single` run then recorded rc 0. `closure.select(['dev/programme/rosters/wave-r10-groups.json'])['run']` is `['tests/doc_claims.py', 'tests/entities.py']`; before the repair it was `['tests/doc_claims.py']`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2711 ENTITY CHECKS PASSED`. codeowners_gap.py is cited by `wave-r10-groups.json#R11-INTAKE-R10-RESIDUE[83]`.
- Mutation: `_SP_REMEASURES += _SP_ROSTER_CARRIES` replaced with `pass` gives `2 of 2711 ENTITY CHECKS FAILED` (#2227 with `cited 2`, and the cited-program arm).
- Head copies: `node tools/policy/brief_lint.mjs` exits 0, ci_predict's under-scoped and left-inert arms report no red, `STRUCTURE RATCHET PASSED`, and `git merge-tree --write-tree origin/main HEAD` prints one tree.

## The block (prepr.sh at 78325190f8: `REFUSE ci predict ... 1 BOOTSTRAP`)

In both runs below, main's brief_lint.mjs was swapped into this head's worktree, run, and restored:
- With this head's data (carry-201.json delisted from tools/policy/legacy_control_files.json), rc 1: `CONTROL VACUOUS: carry control: a legacy carry file is refused (the narrowing): names no path ...`. Main's `assertCarryControl` names carry-201.json literally.
- With main's legacy_control_files.json restored (carry-201.json listed), rc 1: `LEGACY-CONTROL VACUOUS: carry-201.json: its controls lint clean without the exemption: remove it from LEGACY_CONTROL_FILES`. carry-201.json now holds only its live entry 22.
- Deleting carry-201.json as well is refused by main's copy too (`in no carry directory: remove it`, the red at b560375dbd).
- Control for p1: the brief_lint.mjs hunk applied to a worktree of origin/main, run with the head's grader on main's data, gives rc 0 and no VACUOUS line. Main's own copy on main is rc 0.

Not done pending the ruling: body_push.sh. The re-cut body is drafted; its `## Forward-carry` must read a bare `none`, which prepr's carry audit asks for.
