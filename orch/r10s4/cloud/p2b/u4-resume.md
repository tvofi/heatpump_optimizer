# U4 resume: one defect to fix in your head f0e4a9d1d (same topic, same refs)

Your body flags it, and it is a defect, not a note. `record`'s `if:` (`github.event_name != 'pull_request' && != 'merge_group'`) runs on any `ci.yml` `workflow_dispatch` whose workset names `governance`. `prelude.derive` gives every dispatch kind `code`, and `CODE_UNITS` holds `governance`. After P2b, every bot dispatch of `ci.yml` on a PR branch (autofix `-f pr= -f base=`, merge-main) therefore runs `record`:
- `issues: write` (the friction-filing step) over code the PR branch carries;
- a full `<tag>..origin/main` window on the GITHUB_TOKEN bucket #2629 budgets.
main's governance.yml had a dispatch arm, but no bot dispatched governance on a PR branch, so the exposure is new with the umbrella.

Fix, failing test first (fixer.md):
1. A `tests/entities.py` pin over governance.yml: `record` runs only on `refs/heads/main` (push, schedule, or a dispatch at main).
   - Plant: a dispatch at a PR branch reaches `record` (the current `if:`) and is refused.
   - Null: push at main, and schedule, reach it.
   - Show the pin red on f0e4a9d1d first.
2. The guard: `if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request' && github.event_name != 'merge_group'` (or an equivalent you show). Keep #2629's `concurrency` and steps byte-identical.
3. Check `delivery-status-publish` (already `push && refs/heads/main`), and any other job holding a write grant, against the same rule, in the same pin.
4. Re-run `unitcheck.sh` (map gains the `record|` row as changed), entities, structure, and the R2d mutants. Push to the same handoff and body refs.
Set PREPR_SKIP_CLOSURES=1 for prepr and the scoped gate.
