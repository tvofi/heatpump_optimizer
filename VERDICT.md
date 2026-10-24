Fix review: merge e5ad7315184614c824690094bb77943bba947a0b

bus-nonce: 27edb48521acd45fe34a71b8bd68b304

## Scope

PR #2695, record-class (`record: delivery rows for #2694 (autofix)`), round 1 of review. Head measured: `e5ad7315184614c824690094bb77943bba947a0b`, base and merge base `145bfe197b9e7c09eb90bedadec44c6bc19d679d` (the current origin/main). The `dev/governance/roles/` contract on main is identical to the copy at the merge base (empty diff).

## Findings

none

## Evidence

- Diff (three-dot from the merge base): two files, both `dev/programme/delivery/<N>.md` row files. `2694.md` goes from `**open**` to ``**merged `145bfe1`**, record: delivery rows for #2687, #2690 (autofix).``, and `2695.md` is new, carrying an `**open**` self-row. Each is one line anchoring its own PR number. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (ev/merge_tree.txt).
- Row facts checked against the REST API: #2694 is merged, merged_at 2026-10-24T10:07:09Z, its merge commit is `145bfe197b9e` ("Merge pull request #2694 from tvofi/record/autofix") and its title matches the row text.
- Steps 1 and 3 (mutation proof, null control): the body's n/a holds, since the diff writes no production, test or check line. Targeted mutants on the instrument the body names, `tests/delivery_status.py` (ev/mutants.txt): at the head it prints `75 rowed, 0 pending, 0 overdue`. Reverting `2694.md` to the base, or deleting it, moves that to `74 rowed, 1 pending` with #2694 pending, so the figure is earned by the row. That script exits 0 when a row is pending, by design: it is not a required context.
- Body figures re-derived at the head: `python3 tests/delivery_status.py` gives `DELIVERY STATUS OK — 75 rowed, 0 pending, 0 overdue` (ev/delivery_status.txt). `node tools/policy/policy_lint.mjs --record --since 145bfe1` gives `TOTAL: 0 error(s) over 0 merged pull request(s)` (ev/policy_lint_record.txt). `record_row.py --automerge-check --pr 2695 --head e5ad731…` gives `AUTOMERGE OK #2695 at e5ad7315184614c824690094bb77943bba947a0b`, exit 0 (ev/automerge_check.txt).
- Step 4 (claims): neither claim file is touched, and no fixture is in the diff.
- Step 6 (class): one seam, the record rows for one merged PR. The body names no multi-seam issue.
- Step 7: the `## Head` SHA in the body equals the measured head.
- Step 11 (CI): I read the head's check-runs API, 52 runs. Every run is `success` or `skipped`, and none is red, so no root-cause answer is owed. `pr-contract` ran green twice (runs 40084762235 and 40084761080). `delivery-status`, `nightly-status`, `mutation` and `gate` are all success. `governance / record` was skipped.
- Step 13: `git merge-tree --write-tree origin/main e5ad731…` exits 0 with tree `7e2973d8d228…`, so there are no conflicting paths.
- Step 14: the only number the diff moves is the delivery ledger's rowed count, which the row earns (shown by the mutants above).
- Step 12: just before writing this verdict, `git ls-remote` showed `record/autofix` still at `e5ad7315184614c824690094bb77943bba947a0b` and main still at `145bfe1`.
- Instruments are all in-tree. I built none of my own.
