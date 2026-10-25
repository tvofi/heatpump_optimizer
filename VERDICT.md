Fix review: merge c4b83673c90896606c365bce779e4b5bfb51a571

bus-nonce: bbaff4f7904955a0fb4fd370faf6e7c8

## Round

Round 1 of review for #2789 (record lane, no group).

## Evidence

- Head reviewed: `c4b83673c90896606c365bce779e4b5bfb51a571`, which is the PR's live head and the head named under the body's `## Head`. The roles contract is current (the merge-base...origin/main diff under `dev/governance/roles/` is empty).
- Three-dot diff against origin/main (merge base `973618e`): exactly three files, all under `dev/programme/delivery/`: `2765.md` and `2788.md` modified, `2789.md` added. No other file. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. Both commits are authored by `hpo-author[bot]`, which is correct.
- `2765.md`: open -> `merged 8a11b8b`. `8a11b8bdd6bf` is "Merge pull request #2765 from tvofi/fix/r10-fly-yield-guard" and is an ancestor of origin/main, so the row is correct.
- `2788.md`: open -> `merged 973618e`. `973618e6f941` is "Merge pull request #2788 from tvofi/record/autofix" and is an ancestor of origin/main. Its subject line, "delivery rows for #2756, #2758, #2779, #2782, #2786", matches the merge commit's title and the five row files it touched, so the row is correct.
- `2789.md`: a new row, present and **open**, which matches the PR's state (open, not merged). Each file is one line and anchors its own PR number.
- Merge with origin/main (`1aa765f`): `git merge-tree --write-tree` exits 0 (tree `0e1fe3e`), so there is no conflict. Main's only delivery change since the base is the new `2787.md`, which does not overlap these files.
- `python3 tests/delivery_status.py` at the head: `DELIVERY STATUS OK — 139 rowed, 1 pending, 0 overdue`, which re-derives the body's one figure (ev/delivery_status.txt).
- Mutation proof: n/a, as the body says. The diff has no production, test or check line, so it draws no mutant. Null control and class rule: n/a, because the diff is record-only with a single seam.
- CI at the head, from the check-runs API (57 runs): no run concluded red. Every completed run is success or skipped, including `governance / delivery-status`, `tests / nightly-status`, `pr-contract` (push-time), `tests / mutation`, `arch-score` and `budget-raise-gate`. Still in progress when read: `gate`, a second `pr-contract` and one `prelude`. Because no check went red, step 11 owes no answer.
- Not re-derived: `record_row.py --automerge-check` could not reach the API from this seat (HTTP 404). Its result is the beat's gate, not this review's.
- Claim files and fixtures: untouched, so nothing drifts and nothing is claimed.

## Findings

- The delivery row for #2787 (merged at `1aa765f` after this PR's base) is still open on main. delivery-status reports it as pending (0 commits since), not overdue. It is not this PR's to fix, because it merged after the beat was computed. Carry: dismissed: the next record beat's ordinary batch drains it; delivery-status grades it pending, not overdue.
