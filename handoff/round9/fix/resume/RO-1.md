# R9-RO-1 resume note

Branch: `handoff/r9-ro-1-v2`, which supersedes `handoff/r9-ro-1` (review round 1 of #1789 blocked at ca6d2368, and a code fix cannot go above a transport commit). Base: origin/main `830f84ad`. Stage: **handed off, review round 2 owed**. The code head is `ea3f85c0`, and this note and `handoff/round9/fix/RO-1-body.md` ride in one transport commit above it.

Code commits (the first four are v1's, cherry-picked with identical trees):
- `3935cb9d` (v1 `f26077a6`): tests/layout.py and tests/layout.json, wired into run.sh (run_always) and derive_closures.sh; closure recorded with `--single` on Linux; a CODEOWNERS line for the manifest.
- `3bec2ce1` (v1 `04191f80`): an independent ls-files count, one historical filter, and three more self-test cases.
- `d5074f0f` (v1 `5d9b3666`): the #1218 pair-count note in deployment_shape.py.
- `bc683e87` (v1 `19f75625`): layout.py's own comments cite no retired path.
- `ea3f85c0`: review round 1's fix, with self-test cases for N (a moved path re-added after `since` is set), M (a single `*` must not cross directories) and C (a directory citation ending in a full stop), plus `verdict()`, whose `--enforce` exit status every case checks (G).

Evidence: /mnt/project-files/audit-r9/fix/evidence/RO-1/ holds the full gate at `f26077a6` (same tree as `3935cb9d`), entities at `ea3f85c0` (ALL 1990 PASSED), the stress re-run, `mutants_ea3f85c0.txt` (28 mutants, 24 killed; H, J, K and L survive, as review round 1 judged non-blocking), `prepr_ea3f85c0.txt` (`PRE-PR: ea3f85c0… 00000000000000000`), the layout report, the retired-list regeneration, and codeowners_gap at the base and the head.

Owner gate: tests/run.sh, tests/derive_closures.sh and .github/CODEOWNERS are code-owned, so tvofi's approving review is needed. No workflow file changes.

Review blocker 2 (carry-missing) is the orchestrator's: apply the text below to the R9-RO-2..9 entries on handoff/audit-r9-fixplan.

## Forward-carry text for the roster (orchestrator applies it on handoff/audit-r9-fixplan)

- **R9-RO-2..9, append to each brief:** "tests/layout.py (R9-RO-1) reads the git index, so stage your moves (`git mv`/`git add`) before reading its meter; an unstaged edit is invisible to it. Every planned move is already listed in tests/layout.json `retired` with `since: null`. For each entry your PR lands, set `since` to your PR number; do not add entries. `python3 tests/layout.py --gen-retired <inventory.tsv>` regenerates the list and keeps `since`. Put the per-arm counts before and after in the body (`python3 tests/layout.py`)."
- **R9-RO-4, append:** "carry-1743.json and carry-1747.json landed after the inventory (754d2319), so they have no row, and layout.py's category arm reports them. Re-derive every carry's open or closed state at your merge base, add rows, and regenerate `retired`."
- **R9-RO-5, append:** "`.claude/rules/` is not in `retired`: the target admits it as D1's generated copy, and --gen-retired skips admitted paths. The lift is metered by the dev/governance/rules/*.md glob leaving the dead arm."
- **R9-RO-9, append:** "Enforce means `run_always \"$PYTHON\" tests/layout.py --enforce` in tests/run.sh (it prints `MODE: ENFORCE`), plus the `fast` wiring and the required contexts from plan section 7. Any PR that adds a recorded closure must also update tests/deployment_shape.py's #1218 pair count (entities.py checks it)."
