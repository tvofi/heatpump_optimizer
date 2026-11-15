Fix review: blocked 2aff0cc4fe1ea58c40c1113b300592211ee75d3f class-open: plan_phases.violations leaves the text fields' types unguarded, so a phases file that --check accepts crashes plan_page.render (plan_page.py:710), not only its section

bus-nonce: 6492ab05c3ffdd7a5d8ea630e17e7efb

Round: 1 (first review of #3622).

## Block

- The body claims the phases file cannot break the page. An invalid file "draws its section as PHASES UNAVAILABLE and the rest of the page still renders", and `--check` is the file's lint. But `plan_phases.violations` never checks the type of the free-text fields `note`, `entry`, `exit`, `forecast.basis`, and an item's `name` and `detail`. It only tests `str(x).strip()` for truthiness. `section()` then passes each of those fields to `html.escape`, which raises on a non-string. `plan_page.render` calls `plan_phases.section(*phases, ...)` at `tools/audit/seat/plan_page.py:710` with no guard, so the exception kills the whole page, which the plan beat publishes, not only the phases section.
- Reproduced at this head (ev/type-confusion.txt): `phases[0].entry=5`, `items[1].name=7`, `forecast.basis=3` and `note=1` each give `violations=0` (`plan_phases.py --check` rc 0), and `section` raises `AttributeError: 'int' object has no attribute 'replace'`. `plan_phases.py --phases F --html OUT` exits 1 with the traceback. Null control: the unmodified fixture gives `violations=0` and renders.
- Under step 6, this is the guard predicate's unguarded domain. The body says no gate script reads a real phases file, and the file is hand-edited on main. So nothing stops an edit that passes `--check` from taking down the beat's page.
- Fix shape, not prescribed: refuse a non-string in each text field inside `violations`, with a self-test arm and a mutant for it.
- The same predicate also accepts these, and the fix round should either refuse them or disposition them in the body: `started` later than `finished`; `forecast.start_from` later than `start_to`; `round` disagreeing with its `round<N>/` directory (discovery takes the directory, the page prints the field); `round: true`. Each passes `--check` and renders (measured: check_rc=0 html_rc=0).

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 2aff0cc4fe1ea58c40c1113b300592211ee75d3f` gives rc 0, with `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).
- CI: `merge_train.py classify 2aff0cc4fe1ea58c40c1113b300592211ee75d3f --pr 3622` printed `GREEN 2aff0cc4fe1ea58c40c1113b300592211ee75d3f pending: none red: none` (ev/classify.txt).
- Role contracts: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so my copy is current.
- VERSION, the manifest and RELEASE_NOTES.md are untouched. No golden or claim file moves.
- Mutation proof, re-run with the PR's driver: `r10_plan_page_mutants.py M0` plus all 23 `phases-*` mutants gives `RESULT survived=0` and M0 `rc=0 fails=0 verdict=null`. Every per-mutant line matches the body (ev/mutants.txt).
- Self-tests at this head: `plan_page self-test: 133 checks, 0 failed`. `plan_phases.py --check dev/programme/round11/phases.json` rc 0. `plan_public self-test: all checks passed`. `state_docs self-test: all checks passed`.
- Public page: `origin/handoff/audit-r10-plan:handoff/round10/state/PLAN.html` sha1 3d2752f7b784 matches the body. The inventory null control re-run gives `RESULT other=pub.html missing=0 added=0` (ev/inventory-null.txt).
- Not re-derived: the BYTE-IDENTICAL comparison and `missing=0 added=9`. Their plan.json (edc40ce32bfd) and GitHub snapshot (21875573ab86) are not in the tree or on the state ref. The self-test arm `both.replace(sec, "", 1) == groups_only` (mutant `phases-keep-groups-page` killed) covers the same property.
- Finder's harness: none named. This is an owner-directive feature, not an audit finding.
- Red checks: the body answers `governance / instrument-self-tests` and `tests / fast (3.14)` at earlier heads. Neither is red at this head.
