# R9-RO-1 resume note

Branch: `handoff/r9-ro-1`. Base: origin/main `830f84ad`. Stage: **handed off**. The code head is `19f75625`, and this note and `handoff/round9/fix/RO-1-body.md` ride in one transport commit above it.

Code commits:
- `f26077a6`: tests/layout.py and tests/layout.json. Wired into run.sh (run_always) and derive_closures.sh; closure recorded with `--single` on Linux; CODEOWNERS line for the manifest.
- `04191f80`: an independent ls-files count, one historical filter, and three more self-test cases (these kill the surviving mutants M3b, M8 and M11).
- `5d9b3666`: tests/deployment_shape.py's #1218 note now counts 378 pairs (28 choose 2) and names tests/layout.py (entities.py was red on it).
- `19f75625`: layout.py's own comments cite no retired path.

Evidence: /mnt/project-files/audit-r9/fix/evidence/RO-1/ holds the full gate log at `f26077a6`, entities at `5d9b3666`, the stress re-run, the mutants at `19f75625`, the layout report, the retired-list regeneration, and codeowners_gap at the base and the head.

Owner gate: tests/run.sh, tests/derive_closures.sh and .github/CODEOWNERS are code-owned, so this needs tvofi's approving review. No workflow file is touched.

## Forward-carry text for the roster (orchestrator applies it on handoff/audit-r9-fixplan)

- **R9-RO-2..9, append to each brief:** "tests/layout.py (R9-RO-1) reads the git index, so stage your moves (`git mv`/`git add`) before reading its meter; an unstaged edit is invisible to it. Every planned move is already listed in tests/layout.json `retired` with `since: null`. For each entry your PR lands, set `since` to your PR number; do not add entries. `python3 tests/layout.py --gen-retired <inventory.tsv>` regenerates the list and keeps `since`. Put the per-arm counts before and after in the body (`python3 tests/layout.py`)."
- **R9-RO-4, append:** "carry-1743.json and carry-1747.json landed after the inventory (754d2319), so they have no row, and layout.py's category arm reports them. Re-derive every carry's open or closed state at your merge base, add rows, and regenerate `retired`."
- **R9-RO-5, append:** "`.claude/rules/` is not in `retired`: the target admits it as D1's generated copy, and --gen-retired skips admitted paths. The lift is metered by the dev/governance/rules/*.md glob leaving the dead arm."
- **R9-RO-9, append:** "Enforce means `run_always \"$PYTHON\" tests/layout.py --enforce` in tests/run.sh (it prints `MODE: ENFORCE`), plus the `fast` wiring and the required contexts from plan section 7. Any PR that adds a recorded closure must also update tests/deployment_shape.py's #1218 pair count (entities.py checks it)."
